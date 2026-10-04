"""TRAIN tests: collator / label mask units (fast) and a 2-step CPU smoke run with SmolLM2-135M (slow, ~30 s).

Data: 8 SFT examples built from data/prompts/pilot_prompts_v2.jsonl + data/teacher_v2/gpt4o_demo.jsonl in the
documented format (docs/05 §1). canonical_target from vcd.train.data is used when that module exists; otherwise
the test renders the boundary itself exactly as the contract states.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

from vcd.io import read_jsonl, write_jsonl
from vcd.teacher.parse import parse_answer
from vcd.train.sft import (
    IGNORE_INDEX,
    SftCollator,
    accumulation_group_sizes,
    load_train_config,
    read_sft_rows,
    resolve_run_identity,
    tokenize_example,
    tokenize_rows,
    train_sft,
)

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "data/prompts/pilot_prompts_v2.jsonl"
DEMOS = ROOT / "data/teacher_v2/gpt4o_demo.jsonl"
TINY_MODEL = "HuggingFaceTB/SmolLM2-135M"
_RATIONALE_RE = re.compile(r"rationale\s*:", re.IGNORECASE)


def _render_prompt(system: str, user: str) -> str:
    try:
        from vcd.train.data import render_prompt

        return render_prompt(system, user)
    except ImportError:
        return f"{system}\n\n{user}\n\nAnswer:"


def _canonical_target(raw: str):
    try:
        from vcd.train.data import canonical_target

        return canonical_target(raw)
    except ImportError:
        cat, letter = parse_answer(raw)
        m = _RATIONALE_RE.search(raw)
        if cat != "answer" or letter is None or m is None:
            return None
        return f" {letter}\nRationale: {raw[m.end():].strip()}"


def build_sft_rows(n: int = 8) -> list[dict]:
    """First n answered T1/T3/T5/T6 pilot demos as SFT rows."""
    prompts = {p["prompt_id"]: p for p in read_jsonl(PROMPTS)}
    rows = []
    for d in read_jsonl(DEMOS):
        p = prompts.get(d["prompt_id"])
        if p is None or p["variant"] not in ("T1", "T3", "T5", "T6") or d["category"] != "answer":
            continue
        target = _canonical_target(d["raw"])
        if target is None:
            continue
        rows.append({
            "prompt_id": p["prompt_id"], "family_id": p["family_id"], "variant": p["variant"], "order": p["order"],
            "teacher": d["teacher"], "version": "O", "text_prompt": _render_prompt(p["system"], p["user"]),
            "text_target": target, "letter": d["letter"],
        })
        if len(rows) == n:
            break
    assert len(rows) == n
    return rows


@pytest.fixture(scope="module")
def tokenizer():
    from transformers import AutoTokenizer

    tok = AutoTokenizer.from_pretrained(TINY_MODEL)
    if tok.pad_token_id is None:
        tok.pad_token = tok.eos_token
    return tok


@pytest.fixture(scope="module")
def sft_rows() -> list[dict]:
    return build_sft_rows(8)


def test_tokenize_example_boundary_and_mask(tokenizer):
    prompt = "You are a helpful assistant.\n\nPick one.\n\nOptions:\nA. Go.\nB. Stay.\n\nAnswer:"
    target = " B\nRationale: Staying is safer."
    ex = tokenize_example(tokenizer, prompt, target, max_seq_len=256)
    assert ex is not None
    n_p = ex["n_prompt_tokens"]
    joined = tokenizer(prompt + target, add_special_tokens=False)["input_ids"]
    assert ex["input_ids"] == joined + [tokenizer.eos_token_id], "split tokenization must equal joined tokenization"
    assert ex["input_ids"][n_p] == 389, "first target token must be ' B' (id 389 on SmolLM2)"
    assert ex["labels"][:n_p] == [IGNORE_INDEX] * n_p
    assert ex["labels"][n_p:] == ex["input_ids"][n_p:]
    assert ex["labels"][-1] == tokenizer.eos_token_id
    assert ex["n_target_tokens"] == len(ex["input_ids"]) - n_p
    assert tokenize_example(tokenizer, prompt, target, max_seq_len=10) is None


def test_collator_pads_and_masks(tokenizer):
    import torch

    a = tokenize_example(tokenizer, "Hello there.\n\nAnswer:", " A\nRationale: short.", 256)
    b = tokenize_example(tokenizer, "A much longer prompt with more words in it.\n\nAnswer:", " B\nRationale: a longer rationale here.", 256)
    batch = SftCollator(pad_id=tokenizer.pad_token_id)([a, b])
    width = max(len(a["input_ids"]), len(b["input_ids"]))
    assert batch["input_ids"].shape == (2, width) == batch["labels"].shape == batch["attention_mask"].shape
    for i, ex in enumerate((a, b)):
        n, n_p = len(ex["input_ids"]), ex["n_prompt_tokens"]
        assert torch.all(batch["labels"][i, :n_p] == IGNORE_INDEX), "prompt tokens must carry no loss"
        assert torch.equal(batch["labels"][i, n_p:n], torch.tensor(ex["input_ids"][n_p:]))
        assert torch.all(batch["labels"][i, n:] == IGNORE_INDEX), "padding must carry no loss"
        assert torch.all(batch["input_ids"][i, n:] == tokenizer.pad_token_id)
        assert batch["attention_mask"][i].sum().item() == n
    n_loss = (batch["labels"] != IGNORE_INDEX).sum().item()
    assert n_loss == a["n_target_tokens"] + b["n_target_tokens"]


def test_tokenize_rows_counts_and_order(tokenizer, sft_rows):
    data = tokenize_rows(tokenizer, sft_rows, max_seq_len=256)
    assert data.n_examples == 8 and data.n_dropped_too_long == 0
    assert data.n_target_tokens == sum(ex["n_target_tokens"] for ex in data.examples) > 0
    assert data.n_total_tokens > data.n_target_tokens
    # file order preserved: first example's prompt tokens are the first row's prompt
    first = tokenizer(sft_rows[0]["text_prompt"], add_special_tokens=False)["input_ids"]
    assert data.examples[0]["input_ids"][: len(first)] == first
    tiny = tokenize_rows(tokenizer, sft_rows, max_seq_len=50)
    assert tiny.n_dropped_too_long == 8 and tiny.n_examples == 0


def test_read_sft_rows_validates(tmp_path, sft_rows):
    path = tmp_path / "ok.jsonl"
    write_jsonl(path, sft_rows)
    assert len(read_sft_rows(path)) == 8
    bad = dict(sft_rows[0], text_target="B\nRationale: no leading space")
    write_jsonl(tmp_path / "bad.jsonl", [bad])
    with pytest.raises(ValueError):
        read_sft_rows(tmp_path / "bad.jsonl")


def test_accumulation_group_sizes():
    """The partial last group of an epoch must be scaled by its own size, not by `accum` (703 micro-batches, accum 4 -> 175 x 4 + 3)."""
    g = accumulation_group_sizes(703, 4)
    assert len(g) == 176 and g[-1] == 3 and set(g[:-1]) == {4} and sum(g) == 703
    assert accumulation_group_sizes(8, 4) == [4, 4] and accumulation_group_sizes(5, 8) == [5] and accumulation_group_sizes(0, 4) == []


def test_run_identity():
    ident = resolve_run_identity(Path("runs/qwen3-4b/gpt4o_O_s3"), "qwen3-4b", [], seed=3)
    assert ident == {"run_id": "qwen3-4b.gpt4o_O_s3", "teacher": "gpt4o", "version": "O", "seed": 3, "protocol_run_id": True}
    with pytest.raises(ValueError):
        resolve_run_identity(Path("runs/qwen3-4b/gpt4o_O_s3"), "qwen3-4b", [], seed=1)
    smoke = resolve_run_identity(Path("runs/smoke"), "smollm2-135m", [{"teacher": "gpt4o", "version": "O"}], seed=1)
    assert smoke["run_id"] == "smollm2-135m.smoke" and smoke["protocol_run_id"] is False and smoke["teacher"] == "gpt4o"
    gate = resolve_run_identity(Path("runs/qwen3-4b/_smoke_gpt4o_O_s1"), "qwen3-4b", [{"teacher": "gpt4o", "version": "O"}], seed=1)
    assert gate["protocol_run_id"] is False, "a leading underscore must not parse as a protocol run"


def test_tiny_profile_overrides():
    cfg = load_train_config("configs/train.yaml", profile="tiny")
    assert cfg["student_model"] == TINY_MODEL and cfg["student_model_short"] == "smollm2-135m"
    assert cfg["train"]["precision"] == "fp32" and cfg["train"]["max_seq_len"] == 256
    assert cfg["train"]["learning_rate"] == 1e-5, "keys not in tiny: keep the protocol value"
    assert "tiny" not in cfg
    base = load_train_config("configs/train.yaml")
    assert base["student_model"] == "Qwen/Qwen3-4B-Base" and base["train"]["num_epochs"] == 3


@pytest.mark.slow
def test_smoke_train_tiny(tmp_path, sft_rows):
    """2 optimizer steps of SmolLM2-135M on CPU; manifest, log and reloadable checkpoint must exist."""
    from transformers import AutoModelForCausalLM

    data_path = tmp_path / "gpt4o_O_s1.jsonl"
    write_jsonl(data_path, sft_rows)
    run_dir = tmp_path / "runs" / "smollm2-135m" / "gpt4o_O_s1"
    cfg = load_train_config("configs/train.yaml", profile="tiny")
    manifest = train_sft(data_path, run_dir, cfg, seed=1, max_steps=2, log=lambda *_: None)

    on_disk = json.loads((run_dir / "train_manifest.json").read_text())
    assert on_disk["run_id"] == manifest["run_id"] == "smollm2-135m.gpt4o_O_s1"
    assert on_disk["n_examples"] == 8 and on_disk["n_dropped_too_long"] == 0
    assert on_disk["n_target_tokens"] > 0 and on_disk["n_total_tokens"] > on_disk["n_target_tokens"]
    assert on_disk["steps"] == 2 and on_disk["epochs"] == 3 and on_disk["effective_batch"] == 4
    assert on_disk["precision"] == "fp32" and on_disk["final_loss"] > 0
    assert on_disk["checkpoint_dtype"] == "float32" and on_disk["peak_memory_gib"] is None and on_disk["accumulation_group_sizes"] == [1]
    assert on_disk["optimizer_fused"] is False
    for key in ("data_sha256", "learning_rate", "lr_scheduler", "warmup_ratio", "max_seq_len", "optimizer",
                "gradient_checkpointing", "wall_time_sec", "torch_version", "transformers_version", "hostname",
                "started_at", "finished_at", "seed", "teacher", "version"):
        assert key in on_disk, key
    assert "git_commit" in on_disk  # may be null
    log_rows = [json.loads(l) for l in (run_dir / "train_log.jsonl").read_text().splitlines()]
    assert [r["step"] for r in log_rows] == [1, 2] and all(r["loss"] > 0 for r in log_rows)
    assert (run_dir / "checkpoint" / "model.safetensors").exists()
    assert (run_dir / "checkpoint" / "tokenizer_config.json").exists()
    reloaded = AutoModelForCausalLM.from_pretrained(run_dir / "checkpoint")
    assert reloaded.config.model_type == "llama" and reloaded.config.use_cache is True
    import torch
    from safetensors import safe_open

    with safe_open(run_dir / "checkpoint" / "model.safetensors", "pt") as f:
        assert f.get_tensor(next(iter(f.keys()))).dtype == torch.float32  # CPU / fp32 profile keeps fp32; bf16 runs save bf16
