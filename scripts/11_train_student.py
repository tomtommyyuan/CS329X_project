#!/usr/bin/env python
"""Train one student on one SFT file (docs/05_training_stack.md §3).

Examples
  # one core-grid run on a GPU node (hyperparameters all come from configs/train.yaml)
  python scripts/11_train_student.py --data data/sft/gpt4o_O_s1.jsonl --out runs/qwen3-4b/gpt4o_O_s1 --seed 1

  # CPU smoke test with the tiny profile (SmolLM2-135M, 2 optimizer steps)
  python scripts/11_train_student.py --data data/sft/gpt4o_O_s1.jsonl --out runs/smoke --seed 1 --profile tiny --max-steps 2

The run directory name should be "{teacher}_{version}_s{seed}" so the run id "{student_short}.{dir}" matches the
protocol regex and the EVAL scripts can parse it; other names are allowed for smoke runs. A directory that
already holds train_manifest.json is refused unless --overwrite is given (double submission protection).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from vcd.train.sft import load_train_config, train_sft  # noqa: E402


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--data", required=True, help="SFT jsonl built by scripts/10_build_sft_data.py (file order = training order)")
    ap.add_argument("--out", "--run-dir", dest="out", required=True, help="run directory, e.g. runs/qwen3-4b/gpt4o_O_s1")
    ap.add_argument("--config", default="configs/train.yaml", help="hyperparameter YAML (default configs/train.yaml)")
    ap.add_argument("--profile", choices=["default", "tiny"], default="default", help="tiny = SmolLM2-135M CPU smoke overrides")
    ap.add_argument("--seed", type=int, required=True, help="run seed (torch/numpy/random); must match the _s{seed} in --out")
    ap.add_argument("--model", default=None, help="override student_model (HF name or local path)")
    ap.add_argument("--epochs", type=int, default=None, help="override train.num_epochs (protocol: 3)")
    ap.add_argument("--lr", type=float, default=None, help="override train.learning_rate (protocol: 1e-5)")
    ap.add_argument("--max-steps", type=int, default=None, help="cap optimizer steps (smoke runs only)")
    ap.add_argument("--overwrite", action="store_true", help="retrain even if --out already has train_manifest.json")
    args = ap.parse_args()

    run_dir = Path(args.out)
    if (run_dir / "train_manifest.json").exists() and not args.overwrite:
        print(f"[11] {run_dir} already has train_manifest.json; skipping (use --overwrite to retrain)")
        return
    cfg = load_train_config(args.config, profile=args.profile)
    if args.profile == "default" and (args.epochs is not None or args.lr is not None or args.model is not None or args.max_steps is not None):
        print("[11] WARNING: overriding protocol hyperparameters; this run is NOT a core-grid run")
    train_sft(
        args.data,
        run_dir,
        cfg,
        seed=args.seed,
        model_name=args.model,
        epochs=args.epochs,
        learning_rate=args.lr,
        max_steps=args.max_steps,
    )


if __name__ == "__main__":
    main()
