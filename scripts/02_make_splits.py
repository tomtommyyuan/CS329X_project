"""Step 02: dedup + assign splits in place; writes a summary json."""

from __future__ import annotations

import argparse
import json

from vcd.config import load_e0
from vcd.data.dedup_split import assign_splits, dedup_families, split_summary
from vcd.io import load_models, write_jsonl
from vcd.schemas import Family


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    args = ap.parse_args()
    cfg = load_e0(args.config)

    fams = load_models(cfg["paths"]["families"], Family)
    kept, dropped = dedup_families(fams, threshold=float(cfg["dedup_threshold"]))
    print(f"dedup: {len(fams)} -> {len(kept)} (dropped {len(dropped)})")
    for a, b in dropped[:10]:
        print(f"   dropped {a} ~ {b}")

    kept = assign_splits(kept, cfg["pilot"], cfg["splits"], seed=int(cfg["seed"]), exclude_flags=cfg.get("exclude_review_flags", []))
    write_jsonl(cfg["paths"]["families"], kept)
    summary = {"n_total": len(kept), "dropped_near_duplicates": dropped, "splits": split_summary(kept)}
    cfg["paths"]["splits_summary"].parent.mkdir(parents=True, exist_ok=True)
    with open(cfg["paths"]["splits_summary"], "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(json.dumps(summary["splits"], indent=2))


if __name__ == "__main__":
    main()
