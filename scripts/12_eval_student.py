"""Step 12: student readout on a prompt split -> runs/.../eval/{split}_responses.jsonl (+ readout summary).

Examples
  # trained student (reads <run-dir>/checkpoint, run id from train_manifest.json or the directory names)
  python scripts/12_eval_student.py --run-dir runs/qwen3-4b/gpt4o_O_s1 --split test --backend vllm
  # untrained base model S_0; run id = "{student_model_short}.base_B_s0", written under runs/{short}/base_B_s0/
  python scripts/12_eval_student.py --model Qwen/Qwen3-4B-Base --split dev
  # CPU smoke with the tiny profile on the pilot prompts (expect category "malformed": the untrained 135M model copies the
  # "<A or B>" placeholder instead of answering; a trained checkpoint via --run-dir answers)
  python scripts/12_eval_student.py --model HuggingFaceTB/SmolLM2-135M --profile tiny --split pilot --limit 8 --out /tmp/smoke

Every variant and both option orders of the split are scored (order averaging happens in the analysis).
Rows are TeacherResponse with teacher = run id and mode "profile" (docs/05_training_stack.md §4-5).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from vcd.config import resolve
from vcd.io import load_models, write_jsonl
from vcd.schemas import Prompt
from vcd.student.readout import run_readout
from vcd.train.data import RUN_ID_RE, load_train_yaml


def resolve_run(args: argparse.Namespace, cfg: dict) -> tuple[str, str, Path]:
    """Return (model_path, run_id, out_dir) for --run-dir or --model mode."""
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
        print(f"warning: run id {run_id!r} does not match the contract regex; analysis may skip it", file=sys.stderr)
    return model_path, run_id, out_dir


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--run-dir", "--run", dest="run_dir", help="run directory runs/{student}/{teacher}_{version}_s{seed} (uses its checkpoint/)")
    src.add_argument("--model", help="HF model id or local path to evaluate directly (untrained base S_0)")
    ap.add_argument("--split", default="test", choices=["dev", "test", "pilot"], help="prompt split; selects paths.prompts_{split} unless --prompts is given")
    ap.add_argument("--prompts", help="prompt jsonl (default: config paths.prompts_{split})")
    ap.add_argument("--backend", default=None, choices=["auto", "vllm", "transformers"], help="default: config readout.backend")
    ap.add_argument("--batch-size", type=int, default=None, help="default: config readout.batch_size")
    ap.add_argument("--dtype", default=None, help="model dtype (default: config readout.dtype; CPU forces float32)")
    ap.add_argument("--limit", type=int, default=None, help="score only the first N prompts (smoke runs)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--profile", default=None, help="config profile overlay, e.g. tiny")
    ap.add_argument("--run-id", default=None, help="override the run id written to the `teacher` field")
    ap.add_argument("--out", default=None, help="output directory (default: <run-dir>/eval or runs/{short}/base_B_s0/eval)")
    ap.add_argument("--overwrite", action="store_true", help="re-score even if the responses file exists")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config, args.profile)  # profile overlay (tiny); no .env, this script calls no API
    rd_cfg = cfg.get("readout", {})
    backend = args.backend or rd_cfg.get("backend", "auto")
    batch_size = args.batch_size or int(rd_cfg.get("batch_size", 32))
    dtype = args.dtype or rd_cfg.get("dtype", "bfloat16")
    answer_mass_min = float(rd_cfg.get("answer_mass_min", 0.9))
    top_logprobs = int(rd_cfg.get("top_logprobs", 20))

    prompts_path = Path(args.prompts) if args.prompts else cfg["paths"].get(f"prompts_{args.split}")
    if prompts_path is None:
        raise SystemExit(f"no prompts path for split {args.split}; pass --prompts")
    prompts = load_models(resolve(prompts_path), Prompt)
    if args.limit:
        prompts = prompts[: args.limit]

    model_path, run_id, out_dir = resolve_run(args, cfg)
    out_dir.mkdir(parents=True, exist_ok=True)
    resp_path = out_dir / f"{args.split}_responses.jsonl"
    summ_path = out_dir / f"{args.split}_readout_summary.json"
    if resp_path.exists() and not args.overwrite:
        raise SystemExit(f"{resp_path} exists; pass --overwrite to redo")

    print(f"run_id={run_id} model={model_path} prompts={len(prompts)} backend={backend} -> {resp_path}")
    rows, summary = run_readout(model_path, prompts, run_id, backend=backend, batch_size=batch_size, dtype=dtype, top_logprobs=top_logprobs, answer_mass_min=answer_mass_min)
    summary.update({"run_id": run_id, "model": model_path, "split": args.split, "prompts_path": str(prompts_path), "answer_mass_min": answer_mass_min,
                    "dtype": dtype, "batch_size": batch_size})  # dtype as requested; the CPU path of the transformers backend upcasts half precision to fp32
    write_jsonl(resp_path, rows)
    summ_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({k: summary[k] for k in ("n", "category_rates", "mean_mass_AB", "backend", "seconds")}, ensure_ascii=False))
    print("top1:", ", ".join(f"{h['token']!r}x{h['count']}" for h in summary["top1_histogram"][:5]))


if __name__ == "__main__":
    main()
