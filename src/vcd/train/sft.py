"""Full-parameter SFT of a student on one SFT jsonl (docs/05_training_stack.md §3).

Design (deliberately plain, one file, no Trainer subclassing):
- Every row is `text_prompt` (ends with "Answer:") + `text_target` (starts with " X"). The two halves are
  tokenized SEPARATELY and concatenated, then one EOS is appended, so the first target token is exactly the
  letter token the readout reads (docs/05 §1.3).
- Labels are -100 on every prompt token and on padding; loss is on the target + EOS only.
- Examples longer than `max_seq_len` are DROPPED and counted (never truncated).
- No shuffling anywhere: the file order is the training order in every epoch (the file is already the
  seed permutation; docs/03 §8).
- bf16 autocast on CUDA (fp32 master weights, as HF Trainer `bf16=True`), fp32 on CPU/tiny profile.
- Gradient accumulation: every micro-batch loss (mean over its loss tokens) is divided by the number of
  micro-batches in ITS optimizer step, so the last, partial group of an epoch is not down-weighted.
- AdamW uses the fused CUDA kernel (no param-sized temporaries; the default foreach path needs ~15 GiB more
  for Qwen3-4B at step time). Peak GPU memory is recorded in the manifest (`peak_memory_gib`).
- The checkpoint is saved in bf16 when training ran in bf16 (vLLM / the readout load bf16 anyway; the fp32
  master copy carries nothing the evaluation uses and would double the 8 GB per run). CPU / fp32 runs save fp32.
- The saved config / tokenizer files also get their transformers-4.x spellings (`write_legacy_compat`) because
  the vLLM venv runs transformers 4.51 and would otherwise read the wrong rope_theta or fail on the tokenizer.
- Outputs: `{run_dir}/checkpoint/` (save_pretrained + tokenizer), `train_log.jsonl`, `train_manifest.json`.

Nothing here runs on import; the heavy imports (torch, transformers) happen inside functions so that the
rest of the `vcd` package stays importable without the "train" extra.
"""

from __future__ import annotations

import copy
import hashlib
import json
import math
import os
import platform
import random
import subprocess
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, Optional, Sequence

from vcd.config import PROJECT_ROOT
from vcd.train.data import RUN_ID_RE, RUN_NAME_RE, load_sft_rows, load_train_yaml

IGNORE_INDEX = -100


# --------------------------------------------------------------------------------------------- config


def load_train_config(config_path: str | Path = "configs/train.yaml", profile: str = "default") -> dict[str, Any]:
    """configs/train.yaml with the `tiny` profile merged in when asked (vcd.train.data.load_train_yaml; no .env)."""
    return load_train_yaml(config_path, profile)


# --------------------------------------------------------------------------------------------- data


def read_sft_rows(path: str | Path) -> list[dict]:
    """Read and validate one SFT jsonl in file order (docs/05 §1.2) via vcd.train.data.load_sft_rows."""
    return load_sft_rows(path)


def accumulation_group_sizes(n_micro: int, accum: int) -> list[int]:
    """Number of micro-batches in each optimizer step of one epoch: [accum, ..., accum, remainder]."""
    if n_micro <= 0:
        return []
    full, rest = divmod(n_micro, accum)
    return [accum] * full + ([rest] if rest else [])


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def tokenize_example(tokenizer, text_prompt: str, text_target: str, max_seq_len: int) -> Optional[dict[str, list[int]]]:
    """prompt ids + target ids + [eos]; labels -100 on the prompt. None when the sequence exceeds max_seq_len.

    No BOS, add_special_tokens=False on both halves (docs/05 §1.3): the concatenation equals the tokenization
    of the joined text for the "Answer:" | " X" split, so the readout boundary matches training.
    """
    p_ids = tokenizer(text_prompt, add_special_tokens=False)["input_ids"]
    t_ids = tokenizer(text_target, add_special_tokens=False)["input_ids"] + [tokenizer.eos_token_id]
    ids = p_ids + t_ids
    if len(ids) > max_seq_len:
        return None
    labels = [IGNORE_INDEX] * len(p_ids) + t_ids
    return {"input_ids": ids, "labels": labels, "n_prompt_tokens": len(p_ids), "n_target_tokens": len(t_ids)}


@dataclass
class TokenizedData:
    """All examples of one SFT file in file order plus the counts the manifest needs."""

    examples: list[dict[str, list[int]]]
    n_examples: int
    n_dropped_too_long: int
    n_target_tokens: int  # target + EOS, one epoch
    n_total_tokens: int  # prompt + target + EOS, one epoch
    dropped_prompt_ids: list[str] = field(default_factory=list)


def tokenize_rows(tokenizer, rows: Sequence[dict], max_seq_len: int) -> TokenizedData:
    """Tokenize every row in order (order is the protocol: never sort or shuffle here)."""
    examples: list[dict] = []
    dropped: list[str] = []
    n_tgt = n_tot = 0
    for r in rows:
        ex = tokenize_example(tokenizer, r["text_prompt"], r["text_target"], max_seq_len)
        if ex is None:
            dropped.append(r.get("prompt_id", "?"))
            continue
        n_tgt += ex["n_target_tokens"]
        n_tot += len(ex["input_ids"])
        examples.append(ex)
    return TokenizedData(examples, len(examples), len(dropped), n_tgt, n_tot, dropped)


@dataclass
class SftCollator:
    """Right-pad a list of tokenized examples; pad ids get `pad_id`, pad labels get -100."""

    pad_id: int

    def __call__(self, batch: Sequence[dict[str, list[int]]]) -> dict:
        import torch

        width = max(len(ex["input_ids"]) for ex in batch)
        input_ids = torch.full((len(batch), width), self.pad_id, dtype=torch.long)
        labels = torch.full((len(batch), width), IGNORE_INDEX, dtype=torch.long)
        attention = torch.zeros((len(batch), width), dtype=torch.long)
        for i, ex in enumerate(batch):
            n = len(ex["input_ids"])
            input_ids[i, :n] = torch.tensor(ex["input_ids"], dtype=torch.long)
            labels[i, :n] = torch.tensor(ex["labels"], dtype=torch.long)
            attention[i, :n] = 1
        return {"input_ids": input_ids, "labels": labels, "attention_mask": attention}


# --------------------------------------------------------------------------------------------- helpers


def set_all_seeds(seed: int) -> None:
    """random / numpy / torch (+ CUDA) seeds. Data order is NOT seeded here: it is the file order."""
    import numpy as np
    import torch

    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def git_commit() -> Optional[str]:
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=PROJECT_ROOT, capture_output=True, text=True, timeout=10)
        if out.returncode != 0:
            return None
        return out.stdout.strip() or None
    except Exception:  # git missing, not a repo, timeout
        return None


def resolve_run_identity(run_dir: Path, student_short: str, rows: Sequence[dict], seed: int) -> dict[str, Any]:
    """run_id = "{student_short}.{run_dir.name}"; teacher/version/seed from the dir name when it matches the
    protocol pattern, else from the data rows (teacher, version) and the --seed flag (smoke runs)."""
    m = RUN_NAME_RE.match(run_dir.name)
    if m:
        teacher, version, dir_seed = m["teacher"], m["version"], int(m["seed"])
        if dir_seed != seed:
            raise ValueError(f"run dir {run_dir.name!r} encodes seed {dir_seed} but --seed is {seed}")
    else:
        teachers = {r["teacher"] for r in rows}
        versions = {r["version"] for r in rows}
        teacher = teachers.pop() if len(teachers) == 1 else "mixed"
        version = versions.pop() if len(versions) == 1 else "X"
    run_id = f"{student_short}.{run_dir.name}"
    return {"run_id": run_id, "teacher": teacher, "version": version, "seed": seed, "protocol_run_id": bool(RUN_ID_RE.match(run_id))}


def write_legacy_compat(ckpt: str | Path) -> dict[str, Any]:
    """Add the transformers-4.x spellings to a checkpoint saved by transformers 5, in place; returns what changed.

    The vLLM venv (vllm 0.8.5.post1 pins transformers 4.51, slurm/README.md §0) must read a student checkpoint
    exactly like the base model, whose own files use these spellings (and transformers 5 reads them too):
    - config.json: `rope_theta` / `rope_scaling` from `rope_parameters`. Without them transformers 4.x silently
      falls back to rope_theta = 10000 (Qwen3 uses 1e6) and vLLM serves a model with the wrong positions.
      `torch_dtype` from `dtype`.
    - tokenizer_config.json: a list-valued `extra_special_tokens` becomes `additional_special_tokens`
      (transformers 4.x expects a dict under that key and fails to load the tokenizer).
    Keys that already exist are never overwritten, so the function is idempotent.
    """
    ckpt = Path(ckpt)
    changed: dict[str, Any] = {}
    cfg_path = ckpt / "config.json"
    if cfg_path.exists():
        cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
        rp = cfg.get("rope_parameters")
        if isinstance(rp, dict) and "rope_theta" in rp and "rope_theta" not in cfg:
            cfg["rope_theta"] = rp["rope_theta"]
            changed["rope_theta"] = rp["rope_theta"]
            if "rope_scaling" not in cfg:
                extra = {k: v for k, v in rp.items() if k != "rope_theta"}
                cfg["rope_scaling"] = None if extra.get("rope_type", "default") == "default" else extra
                changed["rope_scaling"] = cfg["rope_scaling"]
        if "dtype" in cfg and "torch_dtype" not in cfg:
            cfg["torch_dtype"] = changed["torch_dtype"] = cfg["dtype"]
        if changed:
            cfg_path.write_text(json.dumps(cfg, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    tok_path = ckpt / "tokenizer_config.json"
    if tok_path.exists():
        tok = json.loads(tok_path.read_text(encoding="utf-8"))
        extra = tok.get("extra_special_tokens")
        if isinstance(extra, list):
            del tok["extra_special_tokens"]
            tok.setdefault("additional_special_tokens", extra)
            changed["additional_special_tokens"] = len(extra)
            tok_path.write_text(json.dumps(tok, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return changed


def _load_model(name: str, dtype, attn_implementation: str):
    """AutoModelForCausalLM.from_pretrained with the transformers-5 `dtype` kwarg, falling back to `torch_dtype`."""
    from transformers import AutoModelForCausalLM

    try:
        return AutoModelForCausalLM.from_pretrained(name, dtype=dtype, attn_implementation=attn_implementation)
    except TypeError:
        return AutoModelForCausalLM.from_pretrained(name, torch_dtype=dtype, attn_implementation=attn_implementation)


def _build_optimizer(name: str, params: Iterable, lr: float, weight_decay: float, fused: bool = False):
    """adamw_torch (fused CUDA kernel when `fused`: in-place update, no param-sized temporaries) or adamw_8bit."""
    import torch

    if name == "adamw_torch":
        return torch.optim.AdamW(params, lr=lr, weight_decay=weight_decay, betas=(0.9, 0.999), eps=1e-8, fused=fused or None)
    if name == "adamw_8bit":
        import bitsandbytes as bnb  # optional: Linux + CUDA only

        return bnb.optim.AdamW8bit(params, lr=lr, weight_decay=weight_decay, betas=(0.9, 0.999), eps=1e-8)
    raise ValueError(f"unknown optimizer {name!r}; expected adamw_torch or adamw_8bit")


# --------------------------------------------------------------------------------------------- training


def train_sft(
    data_path: str | Path,
    run_dir: str | Path,
    cfg: dict[str, Any],
    seed: int,
    *,
    model_name: Optional[str] = None,
    epochs: Optional[int] = None,
    learning_rate: Optional[float] = None,
    max_steps: Optional[int] = None,
    student_short: Optional[str] = None,
    log=print,
) -> dict[str, Any]:
    """Train one student on one SFT file and return the manifest (also written to run_dir/train_manifest.json).

    `cfg` is `load_train_config(...)`; `model_name`, `epochs`, `learning_rate`, `max_steps` override it. `student_short`
    overrides cfg["student_model_short"] in the run id only (E2c: "qwen3-4b-e2c" / "qwen3-4b-e2ck" so those runs never share
    a run id with the E1 grid); it changes no hyperparameter.
    `max_steps` caps the number of optimizer steps (smoke runs); the cosine schedule is then computed over
    that cap so the smoke run is a shrunk copy of a real run.
    """
    import numpy as np
    import torch
    from torch.utils.data import DataLoader
    from transformers import AutoTokenizer, get_cosine_schedule_with_warmup

    t_cfg = cfg["train"]
    data_path, run_dir = Path(data_path), Path(run_dir)
    model_name = model_name or cfg["student_model"]
    student_short = student_short or cfg["student_model_short"]
    epochs = int(epochs if epochs is not None else t_cfg["num_epochs"])
    lr = float(learning_rate if learning_rate is not None else t_cfg["learning_rate"])
    max_steps = max_steps if max_steps is not None else cfg.get("max_steps")
    per_device = int(t_cfg["per_device_batch_size"])
    accum = int(t_cfg["gradient_accumulation_steps"])
    max_seq_len = int(t_cfg["max_seq_len"])
    precision = str(t_cfg.get("precision", "bf16"))
    optimizer_name = str(t_cfg.get("optimizer", "adamw_torch"))
    logging_steps = int(t_cfg.get("logging_steps", 10))

    started = datetime.now(timezone.utc)
    t0 = time.time()
    set_all_seeds(seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    use_bf16 = precision == "bf16" and device.type == "cuda"
    if precision == "bf16" and device.type != "cuda":
        log("[sft] bf16 requested but no CUDA device: training in fp32")
    run_dir.mkdir(parents=True, exist_ok=True)

    # ---- data (file order == training order)
    rows = read_sft_rows(data_path)
    identity = resolve_run_identity(run_dir, student_short, rows, seed)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    data = tokenize_rows(tokenizer, rows, max_seq_len)
    if data.n_examples == 0:
        raise ValueError(f"no trainable examples in {data_path} (all {len(rows)} rows dropped as too long?)")
    log(f"[sft] {identity['run_id']}: {data.n_examples} examples ({data.n_dropped_too_long} dropped > {max_seq_len} tokens), "
        f"{data.n_target_tokens} target tokens / {data.n_total_tokens} total per epoch")
    collator = SftCollator(pad_id=tokenizer.pad_token_id)
    loader = DataLoader(data.examples, batch_size=per_device, shuffle=False, collate_fn=collator, drop_last=False)

    micro_per_epoch = len(loader)
    steps_per_epoch = math.ceil(micro_per_epoch / accum)
    total_steps = steps_per_epoch * epochs
    if max_steps is not None:
        total_steps = min(total_steps, int(max_steps))
    warmup_steps = math.ceil(float(t_cfg.get("warmup_ratio", 0.0)) * total_steps)

    # ---- model
    model = _load_model(model_name, torch.float32, str(t_cfg.get("attn_implementation", "sdpa")))
    model.config.use_cache = False
    if t_cfg.get("gradient_checkpointing", False):
        model.gradient_checkpointing_enable(gradient_checkpointing_kwargs={"use_reentrant": False})
    model.to(device)
    model.train()
    n_params = sum(p.numel() for p in model.parameters())
    optimizer = _build_optimizer(optimizer_name, model.parameters(), lr, float(t_cfg.get("weight_decay", 0.0)), fused=device.type == "cuda")
    if device.type == "cuda":
        torch.cuda.reset_peak_memory_stats()
    scheduler = get_cosine_schedule_with_warmup(optimizer, warmup_steps, total_steps)
    max_grad_norm = float(t_cfg.get("max_grad_norm", 1.0))

    # ---- loop
    log_path = run_dir / "train_log.jsonl"
    log_f = open(log_path, "w", encoding="utf-8")
    step = 0
    final_loss: Optional[float] = None
    running: list[float] = []
    n_target_trained = 0  # loss tokens actually seen (all epochs), exact even when max_steps cuts the run
    group_sizes = accumulation_group_sizes(micro_per_epoch, accum)  # last group of an epoch may be partial
    done = False
    for epoch in range(epochs):
        micro_idx = 0
        for batch in loader:
            batch = {k: v.to(device) for k, v in batch.items()}
            with torch.autocast(device_type="cuda", dtype=torch.bfloat16, enabled=use_bf16):
                out = model(**batch)
            loss = out.loss / group_sizes[micro_idx // accum]  # mean over the micro-batches of THIS step
            loss.backward()
            running.append(float(out.loss.detach()))
            n_target_trained += int((batch["labels"] != IGNORE_INDEX).sum())
            micro_idx += 1
            is_last_micro = micro_idx == micro_per_epoch
            if micro_idx % accum == 0 or is_last_micro:
                torch.nn.utils.clip_grad_norm_(model.parameters(), max_grad_norm)
                optimizer.step()
                scheduler.step()
                optimizer.zero_grad(set_to_none=True)
                step += 1
                final_loss = float(np.mean(running))
                if step % logging_steps == 0 or step == total_steps or step == 1:
                    rec = {"step": step, "loss": final_loss, "lr": scheduler.get_last_lr()[0],
                           "epoch": round(epoch + micro_idx / micro_per_epoch, 4), "elapsed_s": round(time.time() - t0, 1)}
                    log_f.write(json.dumps(rec) + "\n")
                    log_f.flush()
                    log(f"[sft] step {step}/{total_steps} loss {final_loss:.4f} lr {rec['lr']:.2e} epoch {rec['epoch']}")
                running = []
                if step >= total_steps:
                    done = True
                    break
        if done:
            break
    log_f.close()

    peak_gib = round(torch.cuda.max_memory_allocated() / 2**30, 2) if device.type == "cuda" else None

    # ---- save (bf16 when trained in bf16: halves the 16 GB fp32 checkpoint of a 4B model; eval loads bf16 anyway)
    ckpt = run_dir / "checkpoint"
    checkpoint_dtype = "bfloat16" if use_bf16 else "float32"
    if use_bf16:
        model.to(torch.bfloat16)
    model.config.use_cache = True  # restore the inference default for vLLM / transformers loading
    model.save_pretrained(ckpt, safe_serialization=True)
    tokenizer.save_pretrained(ckpt)
    compat = write_legacy_compat(ckpt)  # the vLLM venv runs transformers 4.51
    finished = datetime.now(timezone.utc)

    manifest = {
        **identity,
        "student_model": model_name,
        "student_model_short": student_short,
        "data_path": str(data_path),
        "data_sha256": sha256_file(data_path),
        "n_rows_in_file": len(rows),
        "n_examples": data.n_examples,
        "n_dropped_too_long": data.n_dropped_too_long,
        "dropped_prompt_ids": data.dropped_prompt_ids[:50],
        "n_target_tokens": data.n_target_tokens,
        "n_total_tokens": data.n_total_tokens,
        "n_target_tokens_trained": n_target_trained,
        "epochs": epochs,
        "steps": step,
        "steps_planned": total_steps,
        "steps_per_epoch": steps_per_epoch,
        "max_steps": max_steps,
        "effective_batch": per_device * accum,
        "per_device_batch_size": per_device,
        "gradient_accumulation_steps": accum,
        "learning_rate": lr,
        "lr_scheduler": t_cfg.get("lr_scheduler", "cosine"),
        "warmup_ratio": t_cfg.get("warmup_ratio", 0.0),
        "warmup_steps": warmup_steps,
        "weight_decay": t_cfg.get("weight_decay", 0.0),
        "max_grad_norm": max_grad_norm,
        "max_seq_len": max_seq_len,
        "precision": "bf16" if use_bf16 else "fp32",
        "precision_requested": precision,
        "checkpoint_dtype": checkpoint_dtype,
        "peak_memory_gib": peak_gib,
        "accumulation_group_sizes": sorted(set(group_sizes)),
        "optimizer": optimizer_name,
        "gradient_checkpointing": bool(t_cfg.get("gradient_checkpointing", False)),
        "attn_implementation": t_cfg.get("attn_implementation", "sdpa"),
        "loss_on": "assistant",
        "shuffle": False,
        "n_params": n_params,
        "device": str(device),
        "device_name": torch.cuda.get_device_name(0) if device.type == "cuda" else platform.processor() or "cpu",
        "optimizer_fused": device.type == "cuda" and optimizer_name == "adamw_torch",
        "profile": cfg.get("profile", "default"),
        "config_path": cfg.get("config_path"),
        "hyperparameters": copy.deepcopy(t_cfg),
        "wall_time_sec": round(time.time() - t0, 2),
        "git_commit": git_commit(),
        "torch_version": torch.__version__,
        "transformers_version": __import__("transformers").__version__,
        "python_version": platform.python_version(),
        "hostname": platform.node(),
        "slurm_job_id": os.environ.get("SLURM_JOB_ID"),
        "started_at": started.isoformat(),
        "finished_at": finished.isoformat(),
        "final_loss": final_loss,
        "checkpoint": str(ckpt),
        "checkpoint_legacy_compat": compat,
    }
    with open(run_dir / "train_manifest.json", "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
    log(f"[sft] done in {manifest['wall_time_sec']} s; checkpoint ({checkpoint_dtype}) at {ckpt}" + (f"; peak GPU memory {peak_gib} GiB" if peak_gib is not None else ""))
    return manifest
