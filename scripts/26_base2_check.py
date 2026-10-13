#!/usr/bin/env python
"""Step 26: tokenizer / template / readout / memory pre-flight for a NEW student base (no weights, no training, no API).

Before a second base family enters the grid (docs/supplemental_experiments.md §2 row 1), prove on its tokenizer and config
alone that the frozen stack needs no change: (a) the SFT template boundary ("Answer:" | " X\\nRationale: ...") tokenizes the
same split and joined and the first target token is the letter token the readout reads; (b) " A", "A", " B", "B" are single
tokens, `vcd.student.readout.letter_token_ids` finds them, and no other vocabulary entry spells those four strings (the
readout sums exactly two spellings per letter); (c) train.max_seq_len holds the longest SFT row of the local SFT dirs;
(d) eos / pad / bos handling matches what sft.py and the readout assume (pad = eos when missing, no BOS); (e) a memory
and wall-time estimate for full-parameter SFT with the stack's optimizer (fp32 master + fp32 grads + AdamW m, v =
16 bytes / param), scaled from the reference base's measured peaks in runs/*/train_manifest.json.

Only the tokenizer and config.json are fetched (huggingface_hub snapshot_download with allow_patterns; a few MB). With
HF_HUB_OFFLINE=1 (the cluster) everything must already be in the cache. The reference model is read from the cache only.

Examples
  python scripts/26_base2_check.py                                   # SmolLM3-3B-Base from configs/train_smollm3_3b.yaml, Qwen as reference
  python scripts/26_base2_check.py --out /tmp/base2_check.md         # also save the Markdown report
  python scripts/26_base2_check.py --model meta-llama/Llama-3.2-3B --student-short llama32-3b --offline   # gated: pre-downloaded
  python scripts/26_base2_check.py --sft-dirs data/sft_e2c,data/sft_e2ck --limit-rows 500                  # quick run

Exit status 1 when any check of the candidate FAILS, so the HPC gate can call it before the first sbatch.
"""

from __future__ import annotations

import argparse
import glob
import json
import logging
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path
from typing import Any, Optional

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vcd.io import read_jsonl  # noqa: E402
from vcd.student.readout import LETTERS, letter_token_ids  # noqa: E402
from vcd.train.data import ASSISTANT_PREFIX, RUN_ID_RE, load_train_yaml, render_prompt, render_target  # noqa: E402

log = logging.getLogger("base2_check")

TOKENIZER_FILES = ["config.json", "generation_config.json", "tokenizer.json", "tokenizer_config.json", "special_tokens_map.json",
                   "vocab.json", "merges.txt", "tokenizer.model", "added_tokens.json", "chat_template*"]
SAMPLE_PROMPT_USER = ("You're driving to the vet with your cat loose in the car.\n\nOptions:\nA. Cancel the appointment and reschedule.\n"
                      "B. Drive on carefully.\n\nShould you cancel?\n\nAnswer with the letter of your choice, then give a brief rationale "
                      "(1 to 3 sentences). Use exactly this format:\nAnswer: <A or B>\nRationale: <your rationale>")
BYTES_PER_PARAM_RESIDENT = 16  # fp32 master 4 + fp32 grad 4 + AdamW m 4 + v 4 (sft.py: fp32 weights, bf16 autocast, adamw_torch fused)
BYTES_PER_PARAM_BF16_CACHE = 2  # autocast keeps a bf16 copy of every weight it casts during the forward / backward
GIB = 2**30


# --------------------------------------------------------------------------- report rows


class Report:
    """Ordered PASS / FAIL / INFO rows per section, rendered as Markdown tables."""

    def __init__(self, title: str):
        self.title = title
        self.sections: dict[str, list[tuple[str, str, str]]] = {}
        self.order: list[str] = []

    def add(self, section: str, check: str, status: str, detail: str) -> None:
        if section not in self.sections:
            self.sections[section] = []
            self.order.append(section)
        self.sections[section].append((check, status, detail))

    def n_fail(self) -> int:
        return sum(1 for rows in self.sections.values() for _, s, _ in rows if s == "FAIL")

    def markdown(self) -> str:
        lines = [f"### {self.title}", ""]
        for sec in self.order:
            lines += [f"**{sec}**", "", "| check | status | detail |", "|---|---|---|"]
            lines += [f"| {c} | {s} | {_md(d)} |" for c, s, d in self.sections[sec]]
            lines.append("")
        return "\n".join(lines)


def _md(s: Any) -> str:
    return str(s).replace("|", "\\|").replace("\n", " ")


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


# --------------------------------------------------------------------------- loading


def fetch_tokenizer_files(model: str, offline: bool) -> Optional[str]:
    """Local snapshot dir holding the tokenizer + config.json of `model` (downloads only those files unless offline)."""
    if Path(model).is_dir():
        return model
    from huggingface_hub import snapshot_download

    try:
        return snapshot_download(model, allow_patterns=TOKENIZER_FILES, local_files_only=True)
    except Exception:
        if offline or os.environ.get("HF_HUB_OFFLINE") == "1":
            return None
    try:
        return snapshot_download(model, allow_patterns=TOKENIZER_FILES)
    except Exception as e:  # gated, typo, no network
        log.warning("cannot fetch %s: %s", model, e)
        return None


def load_tokenizer_and_config(snapshot: str):
    from transformers import AutoConfig, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(snapshot)
    cfg = AutoConfig.from_pretrained(snapshot)
    raw = json.loads((Path(snapshot) / "config.json").read_text(encoding="utf-8")) if (Path(snapshot) / "config.json").exists() else {}
    gen_path = Path(snapshot) / "generation_config.json"
    gen = json.loads(gen_path.read_text(encoding="utf-8")) if gen_path.exists() else {}
    return tok, cfg, raw, gen


# --------------------------------------------------------------------------- parameter count from config


def estimate_params(cfg) -> Optional[dict[str, int]]:
    """Analytic parameter count of a Llama / Qwen / SmolLM-style decoder from its config (no weights needed).

    embeddings + L x (q, k, v, o projections [+ biases] + gated MLP [+ biases] + 2 RMSNorms [+ q_norm, k_norm]) + final norm
    [+ untied lm_head]. Returns None for architectures without these fields (then the caller falls back to --params).
    """
    g = lambda k, d=None: getattr(cfg, k, d)  # noqa: E731
    need = ("hidden_size", "intermediate_size", "num_hidden_layers", "num_attention_heads", "vocab_size")
    if any(g(k) is None for k in need):
        return None
    h, inter, L, heads, vocab = (int(g(k)) for k in need)
    kv = int(g("num_key_value_heads", heads) or heads)
    head_dim = int(g("head_dim") or h // heads)
    attn_bias = bool(g("attention_bias", False))
    mlp_bias = bool(g("mlp_bias", False))
    qk_norm = g("model_type") in ("qwen3", "qwen3_moe", "olmo2")  # per-head RMSNorm on q and k
    embed = vocab * h
    attn = h * heads * head_dim * 2 + h * kv * head_dim * 2 + (attn_bias * (heads * head_dim + 2 * kv * head_dim))
    mlp = 3 * h * inter + (mlp_bias * (2 * inter + h))
    norms = 2 * h + (2 * head_dim if qk_norm else 0)
    per_layer = attn + mlp + norms
    lm_head = 0 if bool(g("tie_word_embeddings", False)) else vocab * h
    total = embed + L * per_layer + h + lm_head
    return {"total": total, "embed": embed, "per_layer": per_layer, "layers": L, "lm_head_untied": lm_head, "vocab": vocab, "hidden": h,
            "intermediate": inter, "heads": heads, "kv_heads": kv, "head_dim": head_dim}


def reference_manifests(pattern: str, model: str) -> list[dict]:
    out = []
    for f in sorted(glob.glob(pattern)):
        try:
            m = json.loads(Path(f).read_text(encoding="utf-8"))
        except Exception:
            continue
        if m.get("student_model") == model and m.get("peak_memory_gib"):
            out.append({"path": f, **{k: m.get(k) for k in ("peak_memory_gib", "n_params", "wall_time_sec", "steps", "n_total_tokens", "epochs", "per_device_batch_size", "max_seq_len", "config_path")}})
    return out


# --------------------------------------------------------------------------- checks


def check_template(rep: Report, tok, sft_rows: list[dict], ids: dict[str, list[int]]) -> None:
    """(a) boundary: tok(prompt) + tok(target) == tok(prompt + target); first target token == id(' X'); prompt ends in [Answer][:]."""
    prompt = render_prompt("You are a helpful assistant.", SAMPLE_PROMPT_USER)
    p_ids = tok.encode(prompt, add_special_tokens=False)
    tail = [tok.decode([i]) for i in p_ids[-2:]]
    rep.add("(a) template boundary", "prompt ends with the tokens [Answer][:]", _status(tail == ["Answer", ":"]), f"last prompt tokens {tail!r}; `{ASSISTANT_PREFIX}` -> {tok.encode(ASSISTANT_PREFIX, add_special_tokens=False)}")
    for letter in LETTERS:
        target = render_target(letter, "Because it is safer.")
        t_ids = tok.encode(target, add_special_tokens=False)
        joined = tok.encode(prompt + target, add_special_tokens=False)
        same = p_ids + t_ids == joined
        first_ok = t_ids[0] == ids[letter][0]
        rep.add("(a) template boundary", f"synthetic row, letter {letter}: split == joined and first target token is id(' {letter}')", _status(same and first_ok),
                f"split==joined {same}; first target token {t_ids[0]} {tok.decode([t_ids[0]])!r} (readout id(' {letter}') = {ids[letter][0]}); target tokens {[tok.decode([i]) for i in t_ids[:5]]}")
    # the documented wrong split ("Answer: " | "B") must still be wrong for this tokenizer, i.e. the no-trailing-space rule matters
    p2 = tok.encode(prompt + " ", add_special_tokens=False) + tok.encode("B\nRationale: x", add_special_tokens=False)
    j2 = tok.encode(prompt + " B\nRationale: x", add_special_tokens=False)
    rep.add("(a) template boundary", "counter-example 'Answer: ' | 'B' (docs/05 §1.3) differs split vs joined", "INFO", f"split==joined {p2 == j2} (expected False: the stack's no-trailing-space prefix is the only consistent cut)")
    if sft_rows:
        bad_boundary = bad_first = 0
        for r in sft_rows:
            p = tok.encode(r["text_prompt"], add_special_tokens=False)
            t = tok.encode(r["text_target"], add_special_tokens=False)
            if p + t != tok.encode(r["text_prompt"] + r["text_target"], add_special_tokens=False):
                bad_boundary += 1
            if not t or t[0] != ids[r["letter"]][0]:
                bad_first += 1
        rep.add("(a) template boundary", f"real SFT rows (sample of {len(sft_rows)}): split == joined", _status(bad_boundary == 0), f"{bad_boundary} rows differ")
        rep.add("(a) template boundary", f"real SFT rows (sample of {len(sft_rows)}): first target token == id(' letter')", _status(bad_first == 0), f"{bad_first} rows differ")


def check_letters(rep: Report, tok, ids: dict[str, list[int]]) -> None:
    """(b) single-token spellings, the readout lookup, and the exhaustive vocabulary scan."""
    all_single = True
    for letter in LETTERS:
        for spelling in (f" {letter}", letter):
            enc = tok.encode(spelling, add_special_tokens=False)
            single = len(enc) == 1
            all_single &= single
            rep.add("(b) letter tokens", f"{spelling!r} is one token", _status(single), f"ids {enc}; decode {[tok.decode([i]) for i in enc]!r}")
    flat = [i for v in ids.values() for i in v]
    rep.add("(b) letter tokens", "readout.letter_token_ids(tokenizer)", _status(all(len(v) == 2 for v in ids.values()) and len(set(flat)) == 4),
            f"{ids} (two distinct ids per letter: the ' X' spelling first, as the training target uses it)")
    # every vocabulary entry that spells one of the four strings must be one of the ids the readout sums
    spellings = {f" {l}" for l in LETTERS} | set(LETTERS)
    hits: dict[str, list[int]] = defaultdict(list)
    for tok_str, tid in tok.get_vocab().items():
        try:
            s = tok.convert_tokens_to_string([tok_str])
        except Exception:
            continue
        if s in spellings:
            hits[s].append(int(tid))
    extra = {s: sorted(set(v) - set(flat)) for s, v in hits.items() if set(v) - set(flat)}
    rep.add("(b) letter tokens", "no other vocabulary entry decodes to ' A' / 'A' / ' B' / 'B'", _status(not extra and len(hits) == 4),
            f"vocab scan ({len(tok.get_vocab())} entries): {dict(sorted((k, sorted(v)) for k, v in hits.items()))}" + (f"; EXTRA ids not summed by the readout: {extra}" if extra else ""))
    rep.add("(b) letter tokens", "' A' / 'A' and ' B' / 'B' are distinct ids", _status(len(set(flat)) == 4), str(flat))


def iter_sft_files(dirs: list[str]) -> list[Path]:
    files: list[Path] = []
    for d in dirs:
        p = Path(d)
        if p.is_dir():
            files += sorted(p.glob("*.jsonl"))
    return [f for f in files if f.name != "runs.txt"]


def check_lengths(rep: Report, tok, files: list[Path], max_seq_len: int, limit_rows: Optional[int], batch: int = 512) -> dict[str, Any]:
    """(c) prompt + target + EOS token counts per row for every SFT file (what tokenize_rows does), vs max_seq_len."""
    per_file = []
    g_max = 0
    g_over = 0
    g_rows = 0
    longest: tuple[int, str, str] = (0, "", "")
    for f in files:
        rows = list(read_jsonl(f))
        if limit_rows:
            rows = rows[:limit_rows]
        if not rows:
            continue
        n_p = n_t = 0
        f_max = 0
        f_over = 0
        for s in range(0, len(rows), batch):
            chunk = rows[s : s + batch]
            lp = [len(x) for x in tok([r["text_prompt"] for r in chunk], add_special_tokens=False)["input_ids"]]
            lt = [len(x) + 1 for x in tok([r["text_target"] for r in chunk], add_special_tokens=False)["input_ids"]]  # + EOS, as sft.py
            for r, a, b in zip(chunk, lp, lt):
                n_p += a
                n_t += b
                tot = a + b
                f_max = max(f_max, tot)
                f_over += tot > max_seq_len
                if tot > longest[0]:
                    longest = (tot, f.name, r["prompt_id"])
        per_file.append({"file": f"{f.parent.name}/{f.name}", "rows": len(rows), "mean_prompt_tok": n_p / len(rows), "mean_target_tok_incl_eos": n_t / len(rows),
                         "max_total_tok": f_max, "n_over_max_seq_len": f_over, "target_tok_per_epoch": n_t})
        g_max = max(g_max, f_max)
        g_over += f_over
        g_rows += len(rows)
    if per_file:
        rep.add("(c) sequence length", f"longest row (prompt + target + EOS) <= max_seq_len {max_seq_len}", _status(g_over == 0),
                f"{g_rows} rows in {len(per_file)} files; max {g_max} tokens ({longest[1]} {longest[2]}); {g_over} rows over the limit (sft.py drops, never truncates); headroom {max_seq_len - g_max} tokens")
    else:
        rep.add("(c) sequence length", "SFT files", "INFO", "no SFT jsonl found in the given dirs (data/sft* are not in git; rebuild with scripts/10 on the cluster and rerun)")
    return {"per_file": per_file, "max_total_tok": g_max, "n_over": g_over, "n_rows": g_rows}


def check_special_tokens(rep: Report, tok, cfg, raw_cfg: dict, gen_cfg: dict) -> None:
    """(d) eos present (sft.py appends it), pad handling, BOS behaviour, config vs tokenizer disagreements."""
    eos_ok = tok.eos_token_id is not None
    rep.add("(d) special tokens", "tokenizer has an eos token (sft.py appends eos_token_id to every target)", _status(eos_ok), f"eos {tok.eos_token!r} id {tok.eos_token_id}")
    if tok.pad_token_id is None:
        rep.add("(d) special tokens", "pad token", "INFO", f"tokenizer has no pad token: sft.py and readout.TransformersBackend set pad = eos ({tok.eos_token!r} {tok.eos_token_id}); pad positions are masked (labels -100, attention 0), so the id is immaterial")
    else:
        rep.add("(d) special tokens", "pad token", "INFO", f"pad {tok.pad_token!r} id {tok.pad_token_id}" + (" (= eos)" if tok.pad_token_id == tok.eos_token_id else " (distinct from eos; fine, pad is masked)"))
    cfg_pad = raw_cfg.get("pad_token_id")
    if cfg_pad is not None and cfg_pad != tok.pad_token_id:
        rep.add("(d) special tokens", "config.json pad_token_id vs tokenizer pad", "INFO", f"config.json pad_token_id {cfg_pad} ({_safe_decode(tok, cfg_pad)}) differs from the tokenizer's {tok.pad_token_id}; the stack never reads config.pad_token_id (collator uses tokenizer.pad_token_id)")
    with_special = tok("hi", add_special_tokens=True)["input_ids"]
    without = tok("hi", add_special_tokens=False)["input_ids"]
    adds = [i for i in with_special if i not in without]
    rep.add("(d) special tokens", "add_special_tokens=True would prepend / append", "INFO",
            f"{[tok.decode([i]) for i in adds] or 'nothing'}; the stack tokenizes with add_special_tokens=False everywhere (sft.tokenize_example, readout, vLLM prompt_token_ids), so BOS never enters train or readout")
    rep.add("(d) special tokens", "bos", "INFO", f"tokenizer bos {tok.bos_token!r} id {tok.bos_token_id}; config.json bos_token_id {raw_cfg.get('bos_token_id')}; generation_config bos_token_id {gen_cfg.get('bos_token_id')}")
    cfg_eos = raw_cfg.get("eos_token_id")
    if cfg_eos is not None and cfg_eos != tok.eos_token_id:
        rep.add("(d) special tokens", "config.json eos_token_id vs tokenizer eos", "INFO", f"config {cfg_eos} vs tokenizer {tok.eos_token_id}; sft.py uses the tokenizer's")
    rep.add("(d) special tokens", "chat template", "INFO", f"{'present' if getattr(tok, 'chat_template', None) else 'absent'} (unused: the stack renders the plain-text template, never apply_chat_template)")


def _safe_decode(tok, tid: int) -> str:
    try:
        return repr(tok.decode([tid]))
    except Exception:
        return "?"


def check_model_class(rep: Report, cfg, raw_cfg: dict) -> None:
    """Does the installed transformers know the architecture, and does the class support sdpa + gradient checkpointing?"""
    import transformers
    from transformers import AutoModelForCausalLM

    try:
        cls = AutoModelForCausalLM._model_mapping[type(cfg)]
        rep.add("(e) model / memory", f"transformers {transformers.__version__} maps model_type {cfg.model_type!r}", "PASS",
                f"{cls.__name__}; _supports_sdpa {getattr(cls, '_supports_sdpa', '?')}, supports_gradient_checkpointing {getattr(cls, 'supports_gradient_checkpointing', '?')}")
    except Exception as e:
        rep.add("(e) model / memory", f"transformers {transformers.__version__} maps model_type {cfg.model_type!r}", "FAIL", f"{type(e).__name__}: {e}")
    saved_with = raw_cfg.get("transformers_version")
    rep.add("(e) model / memory", "config.json transformers_version (minimum version that knows the architecture)", "INFO",
            f"{saved_with}; the cluster's .venv-vllm pins transformers 4.51.3 / vllm 0.8.5.post1 (slurm/README.md §0): a model type newer than that is NOT loadable there, "
            "so scripts/14_readout_check.py (vLLM sampling) is unavailable for it until that venv is rebuilt; the protocol readout (transformers backend in .venv) is unaffected")
    rope = {k: raw_cfg.get(k) for k in ("rope_theta", "rope_scaling", "rope_parameters", "no_rope_layer_interval", "no_rope_layers", "sliding_window", "use_sliding_window") if k in raw_cfg}
    rep.add("(e) model / memory", "position / attention keys (write_legacy_compat copies rope_theta for transformers-4 readers)", "INFO", json.dumps(rope))


def check_memory(rep: Report, cfg, params: Optional[dict], ref: list[dict], ref_model: str, lengths: dict, train_cfg: dict, params_override: Optional[float],
                 is_reference: bool = False) -> None:
    """(e) resident optimizer state + bf16 cache + logits, and a scaling from the reference base's measured peaks."""
    n = float(params_override) if params_override else (params["total"] if params else None)
    if n is None:
        rep.add("(e) model / memory", "parameter count", "FAIL", "cannot estimate from config; pass --params")
        return
    src = "--params" if params_override else "analytic from config.json"
    detail = f"{n/1e9:.3f} B ({src})"
    if params:
        detail += f": vocab {params['vocab']} x hidden {params['hidden']} embed {params['embed']/1e6:.0f} M (tied lm_head: {params['lm_head_untied'] == 0}), {params['layers']} layers x {params['per_layer']/1e6:.1f} M"
    rep.add("(e) model / memory", "parameter count", "INFO", detail)
    resident = n * BYTES_PER_PARAM_RESIDENT / GIB
    bf16_cache = n * BYTES_PER_PARAM_BF16_CACHE / GIB
    per_device = int(train_cfg.get("per_device_batch_size", 4))
    seq = max(int(lengths.get("max_total_tok") or 0), 300)
    vocab = int(getattr(cfg, "vocab_size", 0) or 0)
    logits = per_device * seq * vocab * 4 * 3 / GIB  # fp32 logits + log-softmax + grad, longest micro-batch
    est_low = resident + bf16_cache + logits
    est_high = est_low + 3.0  # activations with checkpointing, allocator slack
    rep.add("(e) model / memory", "resident optimizer state (fp32 weights + grads + AdamW m, v = 16 B/param)", "INFO", f"{resident:.1f} GiB")
    rep.add("(e) model / memory", "bf16 autocast weight cache (2 B/param) + fp32 logits of the longest micro-batch", "INFO",
            f"{bf16_cache:.1f} GiB + {logits:.1f} GiB (batch {per_device} x {seq} tokens x vocab {vocab})")
    rep.add("(e) model / memory", "estimated peak GPU memory, bottom-up", "INFO", f"{est_low:.0f}-{est_high:.0f} GiB (gate rule: peak_memory_gib <= 70 on an 80 GB H100, else adamw_8bit for the WHOLE grid)")
    if ref:
        peaks = [r["peak_memory_gib"] for r in ref]
        ref_params = next((r["n_params"] for r in ref if r.get("n_params")), None)
        worst = max(ref, key=lambda r: r["peak_memory_gib"])
        if ref_params and params and is_reference:
            rel = abs(params["total"] - ref_params) / ref_params
            rep.add("(e) model / memory", "analytic parameter count vs manifest n_params (estimator self-check on the reference)", _status(rel < 0.01),
                    f"analytic {params['total']:,} vs manifest {ref_params:,} ({rel * 100:.2f}% off)")
        if ref_params:
            scaled = max(peaks) * n / ref_params
            rep.add("(e) model / memory", f"scaled from {ref_model} measured peaks ({len(ref)} manifests)", "INFO" if is_reference else _status(scaled <= 70.0),
                    f"reference peak max {max(peaks):.2f} GiB (min {min(peaks):.2f}; worst run {Path(worst['path']).parent.name}, config {worst.get('config_path')}) x {n/ref_params:.3f} = {scaled:.1f} GiB")
        # wall time includes model load + save, so pool over full-length runs (>= 100 steps) instead of taking a per-run max
        times = [(r["wall_time_sec"], r["steps"]) for r in ref if r.get("wall_time_sec") and (r.get("steps") or 0) >= 100]
        if times and ref_params:
            sec_per_step = sum(t for t, _ in times) / sum(s for _, s in times)
            slowest = max(t / s for t, s in times)
            rep.add("(e) model / memory", "wall time per optimizer step, scaled by parameter count", "INFO",
                    f"reference pooled {sec_per_step:.2f} s/step over {len(times)} runs (slowest run {slowest:.2f}) -> ~{sec_per_step * n / ref_params:.2f} s/step; "
                    f"a 760-step E2c run ~{sec_per_step * n / ref_params * 760 / 60:.0f} min, 528-step E1 run ~{sec_per_step * n / ref_params * 528 / 60:.0f} min (train.sbatch --time 02:00:00)")
    else:
        rep.add("(e) model / memory", "scaled from reference manifests", "INFO", f"no manifests for {ref_model} matched; bottom-up estimate only")
    ckpt = n * 2 / GIB
    rep.add("(e) model / memory", "bf16 checkpoint on disk per run", "INFO", f"~{ckpt:.1f} GiB (delete checkpoint/ after dev + test readouts, slurm/README.md §3)")
    rep.add("(e) model / memory", "hyperparameters", "INFO", f"keep IDENTICAL to the parent config (per_device {per_device} x accum {train_cfg.get('gradient_accumulation_steps')}, attn {train_cfg.get('attn_implementation')}, "
            f"optimizer {train_cfg.get('optimizer')}); nothing here suggests a change")


# --------------------------------------------------------------------------- driver


def run_model(model: str, short: Optional[str], train_cfg: dict, max_seq_len: int, files: list[Path], limit_rows: Optional[int], sample_rows: int,
              offline: bool, ref_glob: str, ref_model: str, params_override: Optional[float]) -> tuple[Report, dict]:
    rep = Report(f"{model}" + (f" (student_model_short `{short}`)" if short else ""))
    snap = fetch_tokenizer_files(model, offline)
    if snap is None:
        rep.add("load", "tokenizer + config.json", "SKIP" if model == ref_model else "FAIL",
                "not in the HF cache and not downloadable here (offline, gated or no network): download on a node with internet, e.g. `hf download MODEL --include 'tokenizer*' config.json`")
        return rep, {}
    tok, cfg, raw_cfg, gen_cfg = load_tokenizer_and_config(snap)
    rep.add("load", "tokenizer", "PASS", f"{type(tok).__name__}, vocab {len(tok)} (config vocab_size {getattr(cfg, 'vocab_size', '?')}); snapshot {snap}")
    rep.add("load", "config.json", "PASS", f"model_type {cfg.model_type!r}, architectures {raw_cfg.get('architectures')}, torch_dtype {raw_cfg.get('torch_dtype')}, max_position_embeddings {raw_cfg.get('max_position_embeddings')}")
    if short:
        rid = f"{short}.gpt4o_O_s1"
        rep.add("load", "student_model_short is a legal run-id prefix", _status(RUN_ID_RE.match(rid) is not None), f"{rid!r} vs RUN_ID_RE (no '.' allowed before the first dot)")
    ids = letter_token_ids(tok)
    sample = []
    for f in files[:3]:
        sample += list(read_jsonl(f))[:sample_rows]
    check_letters(rep, tok, ids)
    check_template(rep, tok, sample, ids)
    lengths = check_lengths(rep, tok, files, max_seq_len, limit_rows)
    check_special_tokens(rep, tok, cfg, raw_cfg, gen_cfg)
    check_model_class(rep, cfg, raw_cfg)
    params = estimate_params(cfg)
    ref = reference_manifests(ref_glob, ref_model)
    check_memory(rep, cfg, params, ref, ref_model, lengths, train_cfg, params_override, is_reference=(model == ref_model))
    return rep, {"ids": ids, "lengths": lengths, "params": params, "eos": (tok.eos_token, tok.eos_token_id), "pad": (tok.pad_token, tok.pad_token_id), "vocab": len(tok)}


def lengths_table(results: dict[str, dict]) -> str:
    rows = []
    for model, r in results.items():
        for pf in (r.get("lengths") or {}).get("per_file", []):
            rows.append((model.split("/")[-1], pf))
    if not rows:
        return ""
    lines = ["**(c) per-file token statistics (prompt + target + EOS, as sft.tokenize_rows counts them)**", "",
             "| tokenizer | file | rows | mean prompt tok | mean target tok (+EOS) | max total tok | over max_seq_len | target tok / epoch |", "|---|---|---|---|---|---|---|---|"]
    for m, pf in rows:
        lines.append(f"| {m} | {pf['file']} | {pf['rows']} | {pf['mean_prompt_tok']:.1f} | {pf['mean_target_tok_incl_eos']:.1f} | {pf['max_total_tok']} | {pf['n_over_max_seq_len']} | {pf['target_tok_per_epoch']} |")
    return "\n".join(lines) + "\n"


def overrides_section(model: str, short: str, config: str, e2c_config: Optional[str]) -> str:
    lines = ["### Overrides the HPC agent must pass for this base (nothing in the code defaults to it)", "",
             "| where | override |", "|---|---|",
             f"| login node, once (compute nodes run with HF_HUB_OFFLINE=1) | `HF_HOME=/hai/scratch/$USER/hf hf download {model} --exclude \"onnx/*\"` (or huggingface-cli; the SmolLM3 repo carries ~34 GB of ONNX exports next to the 5.9 GB safetensors) |",
             f"| gate run (slurm/README.md §1 (b), 30 steps, throwaway dir) | `python scripts/11_train_student.py --config {config} --data <sft> --out runs/_smoke/{short}_gate --seed 1 --max-steps 30`; then `12 --run-dir ... --backend transformers`; check manifest peak_memory_gib <= 70, precision bf16, n_dropped_too_long 0 |",
             f"| S_0 base readout (12 --model mode takes the run id AND out dir from the config) | `MODEL={model} EXTRA_ARGS=\"--config {config}\" sbatch slurm/eval.sbatch - dev` -> runs/{short}/base_B_s0/eval/; then copy that eval/ into runs/{short}-e2c/base_B_s0/ and runs/{short}-e2ck/base_B_s0/ (13 looks for version B under runs/{{student}}/) |",
             f"| training (train.sbatch defaults STUDENT_SHORT=qwen3-4b, CONFIG=configs/train.yaml) | `STUDENT_SHORT={short}-e2c CONFIG={e2c_config or config} DATA_LIST=data/sft_e2c/runs.txt sbatch --array=0-14%8 slurm/train.sbatch`; K: `STUDENT_SHORT={short}-e2ck ... DATA_LIST=data/sft_e2ck/runs.txt`; E1 O: `STUDENT_SHORT={short} CONFIG={config} sbatch --array=0-4,15-19,30-34%8 slurm/train.sbatch` |",
             f"| readout of trained runs (eval.sbatch) | no override: `sbatch slurm/eval.sbatch runs/{short}-e2c/<run> train|dev|test` (run id from the manifest, model from checkpoint/) |",
             f"| scripts/13 (default --student = config student_model_short) | `--student {short}-e2c --config {e2c_config or config} --sft-dir data/sft_e2c --prompts-train data/prompts/e2c_C_prompts.jsonl` (K: `{short}-e2ck`, data/sft_e2ck, e2c_K_prompts.jsonl) |",
             f"| scripts/19 (DEFAULT_GLOBS are the qwen3-4b namespaces) | `--c-glob \"runs/{short}-e2c/*_O_s*/eval/{{split}}_responses.jsonl\" --k-glob \"runs/{short}-e2ck/*_O_s*/eval/{{split}}_responses.jsonl\" --e1-glob \"runs/{short}/*_O_s*/eval/{{split}}_responses.jsonl\"` (a glob with no files is reported as missing and skipped) |",
             f"| scripts/14 / 15 / 20 / 21 | 14 needs a vLLM that knows the architecture (see (e)); 15 `--tokenizer {model}`; 21 (provenance) maps namespaces in src/vcd/analysis/provenance.py NAMESPACE_CONDITION and would need the new namespaces registered |",
             ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/train_smollm3_3b.yaml", help="training config of the candidate (student_model, student_model_short, train.max_seq_len)")
    ap.add_argument("--e2c-config", default="configs/train_smollm3_3b_e2c.yaml", help="the candidate's E2c config, named in the override checklist only")
    ap.add_argument("--model", default=None, help="candidate HF id or local dir (default: config student_model)")
    ap.add_argument("--student-short", default=None, help="run-id prefix to validate (default: config student_model_short)")
    ap.add_argument("--compare", default="Qwen/Qwen3-4B-Base", help="reference base, read from the HF cache only ('none' to skip)")
    ap.add_argument("--sft-dirs", default="data/sft_e2c,data/sft_e2ck,data/sft", help="comma list of SFT dirs; missing dirs are skipped")
    ap.add_argument("--limit-rows", type=int, default=None, help="tokenize only the first N rows of each SFT file (quick run)")
    ap.add_argument("--sample-rows", type=int, default=200, help="rows per file (first 3 files) for the split-vs-joined boundary check")
    ap.add_argument("--reference-manifests", default="runs/qwen3-4b*/*/train_manifest.json", help="glob of manifests whose peak_memory_gib / n_params scale the memory estimate")
    ap.add_argument("--params", type=float, default=None, help="override the candidate's parameter count (e.g. 3.08e9) if the config is not Llama-like")
    ap.add_argument("--offline", action="store_true", help="never download; equivalent to HF_HUB_OFFLINE=1")
    ap.add_argument("--out", default=None, help="write the Markdown report here as well as printing it")
    args = ap.parse_args()

    logging.basicConfig(level=logging.WARNING, format="%(levelname)s %(name)s: %(message)s")
    cfg = load_train_yaml(args.config)
    model = args.model or cfg["student_model"]
    short = args.student_short or cfg["student_model_short"]
    max_seq_len = int(cfg["train"]["max_seq_len"])
    files = iter_sft_files(args.sft_dirs.split(","))
    t0 = time.time()

    reports: list[Report] = []
    results: dict[str, dict] = {}
    rep, res = run_model(model, short, cfg["train"], max_seq_len, files, args.limit_rows, args.sample_rows, args.offline, args.reference_manifests, args.compare if args.compare != "none" else "Qwen/Qwen3-4B-Base", args.params)
    reports.append(rep)
    results[model] = res
    if args.compare and args.compare != "none" and args.compare != model:
        rep_c, res_c = run_model(args.compare, None, cfg["train"], max_seq_len, files, args.limit_rows, args.sample_rows, True, args.reference_manifests, args.compare, None)
        rep_c.title += " (reference, cache only)"
        reports.append(rep_c)
        results[args.compare] = res_c

    head = [f"# Second-base pre-flight: {model}", "",
            f"config `{args.config}` (max_seq_len {max_seq_len}, per_device {cfg['train']['per_device_batch_size']} x accum {cfg['train']['gradient_accumulation_steps']}); "
            f"SFT dirs {args.sft_dirs} ({len(files)} files{', first ' + str(args.limit_rows) + ' rows each' if args.limit_rows else ''}); "
            f"transformers {__import__('transformers').__version__}; {time.strftime('%Y-%m-%d %H:%M UTC', time.gmtime())}", ""]
    verdict = reports[0].n_fail()
    head += [f"**Candidate verdict: {'PASS' if verdict == 0 else f'{verdict} FAIL'}** (every PASS/FAIL row of the candidate below)", ""]
    body = "\n".join(r.markdown() for r in reports)
    if len(results) == 2 and all(results.values()):
        a, b = results[model], results[args.compare]
        head += ["| | " + model + " | " + args.compare + " |", "|---|---|---|",
                 f"| vocab | {a['vocab']} | {b['vocab']} |",
                 f"| letter ids A / B | {a['ids']['A']} / {a['ids']['B']} | {b['ids']['A']} / {b['ids']['B']} |",
                 f"| eos / pad | {a['eos']} / {a['pad']} | {b['eos']} / {b['pad']} |",
                 f"| params (analytic) | {a['params']['total']/1e9:.3f} B | {b['params']['total']/1e9:.3f} B |" if a.get("params") and b.get("params") else "| params | ? | ? |",
                 f"| longest SFT row (tok) / rows over {max_seq_len} | {a['lengths'].get('max_total_tok')} / {a['lengths'].get('n_over')} | {b['lengths'].get('max_total_tok')} / {b['lengths'].get('n_over')} |", ""]
    text = "\n".join(head) + "\n" + body + "\n" + lengths_table(results) + "\n" + overrides_section(model, short, args.config, args.e2c_config) + f"\n_{time.time() - t0:.0f} s_\n"
    print(text)
    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out).write_text(text, encoding="utf-8")
        print(f"wrote {args.out}", file=sys.stderr)
    sys.exit(1 if verdict else 0)


if __name__ == "__main__":
    main()
