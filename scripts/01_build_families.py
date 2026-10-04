"""Step 01: raw datasets -> data/families/families.jsonl (no splits yet)."""

from __future__ import annotations

import argparse
from collections import Counter

from vcd.config import load_e0
from vcd.data.load_daily_dilemmas import load_daily_dilemmas
from vcd.data.load_moralchoice import load_moralchoice
from vcd.data.load_valueconsistency import load_valueconsistency
from vcd.io import write_jsonl


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    args = ap.parse_args()
    cfg = load_e0(args.config)
    raw = cfg["paths"]["raw"]

    fams = []
    fams += load_daily_dilemmas(raw / "daily_dilemmas" / "dilemma_to_action_to_values_aggregated.csv")
    fams += load_moralchoice(raw / "moralchoice" / "moralchoice_high_ambiguity.csv", raw / "moralchoice" / "moralchoice_low_ambiguity.csv")
    fams += load_valueconsistency(raw / "valueconsistency" / "valueconsistency.jsonl")

    n = write_jsonl(cfg["paths"]["families"], fams)
    print(f"wrote {n} families -> {cfg['paths']['families']}")
    print("by source:", dict(Counter(f.source for f in fams)))
    print("by ambiguity:", dict(Counter((f.source, f.ambiguity) for f in fams)))
    flags = Counter(fl for f in fams for fl in f.needs_review)
    print("review flags:", dict(flags))
    for src in ("daily_dilemmas", "moralchoice", "valueconsistency"):
        f = next(x for x in fams if x.source == src)
        print(f"\n--- example {src}: {f.family_id}\n  situation: {f.situation[:200]}\n  removed Q: {f.question_original[:120]}\n  x: {f.action_x}\n  y: {f.action_y}")


if __name__ == "__main__":
    main()
