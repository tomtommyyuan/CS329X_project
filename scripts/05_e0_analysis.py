"""Step 05: E0.1-E0.4 tables and gate summary from data/teacher/*.jsonl -> results/e0/."""

from __future__ import annotations

import argparse

from vcd.analysis.e0_profiles import run
from vcd.config import load_e0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    args = ap.parse_args()
    cfg = load_e0(args.config)
    tables = run(cfg)
    print("tables:", ", ".join(sorted(tables)))
    print((cfg["paths"]["results"] / "e0_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
