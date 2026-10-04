"""Step 09: assemble results/e0/report.md from whatever E0 outputs exist."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from vcd.config import load_e0


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    args = ap.parse_args()
    cfg = load_e0(args.config)
    res: Path = cfg["paths"]["results"]
    parts = ["# E0 pilot report", ""]

    summary = res / "e0_summary.md"
    if summary.exists():
        parts += [summary.read_text(encoding="utf-8").replace("# E0 summary (auto-generated)", "## E0.1-E0.4 teachers"), ""]
    else:
        parts += ["## E0.1-E0.4 teachers", "", "_not run yet (scripts/04, 05)_", ""]

    rw_root = cfg["paths"]["teacher_dir"].parent / "rewrites"
    parts += ["## E0.6 rewrite preservation (automatic checks)", ""]
    if rw_root.exists() and any(rw_root.glob("*/rewrites.jsonl")):
        parts += ["| teacher | version | attempts | kept | choice | reasons | conditions | strength | style |", "|---|---|---|---|---|---|---|---|---|"]
        for d in sorted(rw_root.glob("*")):
            f = d / "rewrites.jsonl"
            if not f.exists():
                continue
            rows = [json.loads(l) for l in open(f, encoding="utf-8")]
            df = pd.DataFrame([{"version": r["version"], "kept": r["kept"], **{k: v for k, v in r["checks"].items() if k != "kept"}} for r in rows])
            for v, g in df.groupby("version"):
                parts.append(f"| {d.name} | {v} | {len(g)} | {g['kept'].mean():.2f} | " + " | ".join(f"{g[c].mean():.2f}" for c in ("choice", "reasons", "conditions", "strength", "style")) + " |")
        parts.append("")
    else:
        parts += ["_not run yet (scripts/06, needs B and J endpoints)_", ""]

    parts += ["## E0.7 readout check", ""]
    rc = sorted(res.glob("readout_check_*.csv"))
    if rc:
        for f in rc:
            df = pd.read_csv(f).dropna(subset=["p_logit_A", "freq_A"])
            parts.append(f"- {f.stem}: n={len(df)}, mean |p_logit - freq| = {(df['p_logit_A'] - df['freq_A']).abs().mean():.3f}")
        parts.append("")
    else:
        parts += ["_not run yet (scripts/07, needs vLLM)_", ""]

    parts += ["## E0.5 / E0.6 human annotation", "", "_score with scripts/08_annotation.py once two annotators have filled the sheets_", ""]
    (res / "report.md").write_text("\n".join(parts), encoding="utf-8")
    print((res / "report.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
