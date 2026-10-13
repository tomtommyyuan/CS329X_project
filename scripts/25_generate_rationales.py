r"""Step 25: generate a student's full answer (letter + rationale) for every prompt of a split -> {run}/eval/{split}_generations.jsonl.

E7 phase 3 (tasks/e7_plan.md §5): the lexical provenance baseline on STUDENT text (docs/03's original E7 design) needs the
students' own rationales, which the letter readout (scripts/12) never produces. Every prompt is rendered exactly as in training
and in the readout (vcd.train.data.render_prompt: system, blank line, user, blank line, "Answer:"; prompt file = the split's
prompt set restricted to the training variants T1 / T3 / T5 / T6, both option orders), decoded greedily with max_new_tokens 160,
stopped at EOS or when the model starts a new "Answer:" line (it moved on to another item). The text after the prefix is kept,
the letter is parsed from its first line (vcd.analysis.lexical_provenance.split_generation: the teacher pipeline's spelling
rules). The classifier side is `scripts/22_lexical_provenance.py classify-generations`.

Examples
  # one trained run (reads <run-dir>/checkpoint, run id from train_manifest.json); test = 300 families x 4 variants x 2 orders = 2,400 prompts
  python scripts/25_generate_rationales.py --run-dir runs/qwen3-4b-e2c/gpt4o_O_s1 --split test
  # the untrained base S_0 (run id {student_short}.base_B_s0, written under runs/{short}/base_B_s0/eval)
  python scripts/25_generate_rationales.py --model Qwen/Qwen3-4B-Base --split test
  # CPU smoke with the tiny profile (tests): the untrained SmolLM2-135M copies the "<A or B>" placeholder, so letters are mostly null
  python scripts/25_generate_rationales.py --model HuggingFaceTB/SmolLM2-135M --profile tiny --split pilot --limit 4 --max-new-tokens 16 --out /tmp/gen

Rows of {split}_generations.jsonl: {"prompt_id", "run_id", "text", "letter", "n_new_tokens", "stop_reason"}: text = the generated
continuation after "Answer:" (special tokens removed, a second "Answer:" line and everything after it cut off); letter = "A" /
"B" / null from the first line; n_new_tokens = tokens the model produced before EOS / the stop (so the kept text can be a few
tokens shorter when a new "Answer:" line was cut); stop_reason = eos | answer_line | max_new_tokens. Plus
{split}_generations_summary.json (n, letter rate, mean tokens, stop reasons, model, dtype, prompts path + sha256, seconds).
Decoding is greedy, so the output is deterministic up to floating-point noise of the batch padding; dtype follows the
readout (configs/train.yaml readout.dtype = float32; CPU always float32); transformers backend only (vLLM is not needed).

SLURM (HPC agent; per run, after training and the dev / test readouts and BEFORE deleting checkpoint/; one H100, fp32 like
the readout, 2,400 prompts x <= 160 tokens in batches of 32: a few minutes per run):

  mkdir -p logs
  for r in runs/qwen3-4b-e2c/{gpt4o,claude46,deepseek_v4}_O_s{1,2,3}; do
    sbatch --job-name=vcd-gen --account=ingrai --partition=hai --gres=gpu:h100:1 --cpus-per-task=8 --mem=64G --time=00:40:00 \
      --exclude=haic-hgx-2 --output=logs/%x-%j.out \
      --wrap "source .venv/bin/activate && export HF_HOME=/hai/scratch/\$USER/hf HF_HUB_OFFLINE=1 TOKENIZERS_PARALLELISM=false && \
              python scripts/25_generate_rationales.py --run-dir $r --split test"
  done
  # commit runs/*/*/eval/test_generations.jsonl (+ _summary.json) like the readouts; then, on the Mac:
  python scripts/22_lexical_provenance.py classify-generations --train-sft-dirs data/sft_paired,data/sft_e2c_paired \
      --generations "runs/*/*/eval/test_generations.jsonl" --behavioural results/e7/e7_runs.csv --out results/e7_lexical_students

Account / partition / exclude are the placeholders of slurm/eval.sbatch; verify them first with
`sacctmgr show user $USER withassoc format=user,account%20,qos%30`. No API key is needed or read.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Optional, Sequence

from vcd.analysis.lexical_provenance import split_generation, truncate_at_second_answer
from vcd.config import resolve
from vcd.io import load_models, write_jsonl
from vcd.schemas import Prompt
from vcd.train.data import RUN_ID_RE, file_sha256, load_train_yaml, render_prompt

DEFAULT_MAX_NEW_TOKENS = 160
_NEW_ANSWER_RE = re.compile(r"\n\s*answer\s*[:：]", re.IGNORECASE)


def resolve_run(args: argparse.Namespace, cfg: dict) -> tuple[str, str, Path]:
    """(model_path, run_id, out_dir) for --run-dir (checkpoint/, manifest run id) or --model (base S_0), as in scripts/12."""
    short = cfg["student_model_short"]
    if args.run_dir:
        run_dir = Path(args.run_dir)
        if not run_dir.exists():
            raise SystemExit(f"run dir {run_dir} does not exist")
        ckpt = run_dir / "checkpoint"
        model_path = str(ckpt if ckpt.exists() else run_dir)
        run_id = args.run_id
        manifest = run_dir / "train_manifest.json"
        if run_id is None and manifest.exists():
            run_id = json.loads(manifest.read_text(encoding="utf-8")).get("run_id")
        if run_id is None:
            run_id = f"{run_dir.parent.name}.{run_dir.name}"
        out_dir = Path(args.out) if args.out else run_dir / "eval"
    else:
        model_path = args.model
        run_id = args.run_id or f"{short}.base_B_s0"
        out_dir = Path(args.out) if args.out else cfg["paths"]["runs_dir"] / short / "base_B_s0" / "eval"
    if not RUN_ID_RE.match(run_id):
        print(f"warning: run id {run_id!r} does not match the contract regex; the analysis may skip it", file=sys.stderr)
    return model_path, run_id, out_dir


def select_prompts(prompts: Sequence[Prompt], variants: Sequence[str], limit: Optional[int] = None) -> list[Prompt]:
    """The split's prompts of the given variants (both option orders), in file order; optionally the first `limit`."""
    out = [p for p in prompts if p.variant in set(variants)]
    return out[:limit] if limit else out


def _torch_dtype(name: str):
    import torch

    return {"bfloat16": torch.bfloat16, "bf16": torch.bfloat16, "float16": torch.float16, "fp16": torch.float16, "float32": torch.float32, "fp32": torch.float32}[name]


class Generator:
    """Greedy batched generation with left padding; one sequence stops at EOS or at a new 'Answer:' line."""

    def __init__(self, model_path: str, dtype: str = "float32", device: Optional[str] = None):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.model_path = model_path
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        if self.device == "cpu" and dtype in ("bfloat16", "bf16", "float16", "fp16"):
            dtype = "float32"  # as in the readout backend: CPU half precision is slow or missing
        self.dtype = dtype
        self.tokenizer = AutoTokenizer.from_pretrained(model_path)
        if self.tokenizer.pad_token_id is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        self.tokenizer.padding_side = "left"  # generation reads the last position: pad on the left
        self.model = AutoModelForCausalLM.from_pretrained(model_path, dtype=_torch_dtype(dtype))
        self.model.to(self.device)
        self.model.eval()

    def _criteria(self, prompt_len: int):
        import torch
        from transformers import StoppingCriteria, StoppingCriteriaList

        tokenizer = self.tokenizer

        class NewAnswerLine(StoppingCriteria):
            """Per-sequence stop once the decoded continuation contains a new 'Answer:' line (the model moved on to another item)."""

            def __call__(self, input_ids, scores, **kwargs):
                cont = tokenizer.batch_decode(input_ids[:, prompt_len:], skip_special_tokens=True)
                return torch.tensor([_NEW_ANSWER_RE.search(c) is not None for c in cont], dtype=torch.bool, device=input_ids.device)

        return StoppingCriteriaList([NewAnswerLine()])

    def generate(self, texts: Sequence[str], max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS) -> list[dict]:
        """One batch -> per text {text, n_new_tokens, stop_reason} (text already cut at a second 'Answer:' line)."""
        import torch
        from transformers import GenerationConfig

        tok = self.tokenizer
        enc = tok(list(texts), add_special_tokens=False, padding=True, return_tensors="pt").to(self.device)
        prompt_len = enc["input_ids"].shape[1]
        gc = GenerationConfig(do_sample=False, num_beams=1, max_new_tokens=max_new_tokens, pad_token_id=tok.pad_token_id, eos_token_id=tok.eos_token_id)
        with torch.no_grad():
            out = self.model.generate(**enc, generation_config=gc, stopping_criteria=self._criteria(prompt_len))
        stops = {tok.eos_token_id, tok.pad_token_id}
        results = []
        for row in out[:, prompt_len:].tolist():
            ids, hit_eos = [], False
            for t in row:
                if t in stops:
                    hit_eos = t == tok.eos_token_id
                    break
                ids.append(t)
            text, cut = truncate_at_second_answer(tok.decode(ids, skip_special_tokens=True))
            results.append(dict(text=text, n_new_tokens=len(ids), stop_reason="answer_line" if cut else ("eos" if hit_eos else "max_new_tokens")))
        return results


def generate_rows(gen: Generator, prompts: Sequence[Prompt], run_id: str, batch_size: int = 32, max_new_tokens: int = DEFAULT_MAX_NEW_TOKENS, log=None) -> list[dict]:
    """Rows {prompt_id, run_id, text, letter, n_new_tokens, stop_reason} for every prompt, in prompt order."""
    rows: list[dict] = []
    t0 = time.time()
    for start in range(0, len(prompts), batch_size):
        chunk = list(prompts[start : start + batch_size])
        outs = gen.generate([render_prompt(p.system, p.user) for p in chunk], max_new_tokens)
        for p, o in zip(chunk, outs):
            _, letter, _ = split_generation(o["text"])
            rows.append(dict(prompt_id=p.prompt_id, run_id=run_id, text=o["text"], letter=letter, n_new_tokens=o["n_new_tokens"], stop_reason=o["stop_reason"]))
        if log:
            log(f"{len(rows)}/{len(prompts)} prompts ({time.time() - t0:.0f}s)")
    return rows


def summarize(rows: Sequence[dict]) -> dict:
    n = len(rows)
    letters = Counter(r["letter"] for r in rows)
    return dict(n=n, letter_rate=(sum(1 for r in rows if r["letter"]) / n) if n else None, letter_counts={str(k): v for k, v in sorted(letters.items(), key=lambda kv: str(kv[0]))},
                mean_new_tokens=(sum(r["n_new_tokens"] for r in rows) / n) if n else None, max_new_tokens_seen=max((r["n_new_tokens"] for r in rows), default=0),
                stop_reasons=dict(Counter(r["stop_reason"] for r in rows)), rationale_rate=(sum(1 for r in rows if split_generation(r["text"])[2]) / n) if n else None)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--run-dir", "--run", dest="run_dir", help="run directory runs/{student}/{teacher}_{version}_s{seed} (uses its checkpoint/)")
    src.add_argument("--model", help="HF model id or local path to generate from directly (untrained base S_0)")
    ap.add_argument("--split", default="test", choices=["dev", "test", "pilot"], help="prompt split; selects paths.prompts_{split} unless --prompts is given")
    ap.add_argument("--prompts", help="prompt jsonl (default: config paths.prompts_{split})")
    ap.add_argument("--variants", default=None, help="comma list of variants to generate for (default: config data.variants = T1,T3,T5,T6); both option orders always")
    ap.add_argument("--max-new-tokens", type=int, default=DEFAULT_MAX_NEW_TOKENS)
    ap.add_argument("--batch-size", type=int, default=None, help="default: config readout.batch_size")
    ap.add_argument("--dtype", default=None, help="model dtype (default: config readout.dtype; CPU forces float32)")
    ap.add_argument("--device", default=None, help="cuda | cpu (default: cuda if available)")
    ap.add_argument("--limit", type=int, default=None, help="generate for the first N selected prompts only (smoke runs)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--profile", default=None, help="config profile overlay, e.g. tiny")
    ap.add_argument("--run-id", default=None, help="override the run id written to the rows")
    ap.add_argument("--out", default=None, help="output directory (default: <run-dir>/eval or runs/{short}/base_B_s0/eval)")
    ap.add_argument("--overwrite", action="store_true", help="regenerate even if the generations file exists")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config, args.profile)  # no .env: this script calls no API
    rd_cfg = cfg.get("readout", {})
    batch_size = args.batch_size or int(rd_cfg.get("batch_size", 32))
    dtype = args.dtype or rd_cfg.get("dtype", "float32")
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    prompts_path = Path(args.prompts) if args.prompts else cfg["paths"].get(f"prompts_{args.split}")
    if prompts_path is None:
        raise SystemExit(f"no prompts path for split {args.split}; pass --prompts")
    prompts_path = resolve(prompts_path)
    prompts = select_prompts(load_models(prompts_path, Prompt), variants, args.limit)
    if not prompts:
        raise SystemExit(f"no prompts of variants {variants} in {prompts_path}")

    model_path, run_id, out_dir = resolve_run(args, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    gen_path = out_dir / f"{args.split}_generations.jsonl"
    summ_path = out_dir / f"{args.split}_generations_summary.json"
    if gen_path.exists() and not args.overwrite:
        raise SystemExit(f"{gen_path} exists; pass --overwrite to redo")

    t0 = time.time()
    gen = Generator(model_path, dtype=dtype, device=args.device)
    print(f"run_id={run_id} model={model_path} prompts={len(prompts)} variants={variants} device={gen.device} dtype={gen.dtype} batch={batch_size} max_new_tokens={args.max_new_tokens} -> {gen_path}")
    rows = generate_rows(gen, prompts, run_id, batch_size=batch_size, max_new_tokens=args.max_new_tokens, log=lambda m: print(m, flush=True))
    write_jsonl(gen_path, rows)
    summary = summarize(rows) | dict(run_id=run_id, model=model_path, split=args.split, variants=variants, prompts_path=str(prompts_path), prompts_sha256=file_sha256(prompts_path),
                                     n_prompts_selected=len(prompts), limit=args.limit, max_new_tokens=args.max_new_tokens, dtype=gen.dtype, device=gen.device, batch_size=batch_size,
                                     decoding="greedy", stop="eos or a new 'Answer:' line", seconds=time.time() - t0, timestamp=_dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"))
    summ_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("n", "letter_rate", "mean_new_tokens", "stop_reasons", "seconds")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
