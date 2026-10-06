"""Step 17 (E2c): prompts for a family file that is not families.jsonl (the contested pool or the selected set).

Default: the T1 screening prompts, both option orders, focus_action filled, for the wave-1 pool:
  python scripts/17_contested_prompts.py
      -> data/prompts/contested_pool_T1.jsonl   (families with meta.wave == 1)
Later waves:
  python scripts/17_contested_prompts.py --waves 2a,2b --out data/prompts/contested_pool_T1_wave2.jsonl
Training prompts for the selected set (T1 / T3 / T5 / T6, like train_prompts_v2.jsonl):
  python scripts/17_contested_prompts.py --families data/families/contested_selected.jsonl --variants T1,T3,T5,T6 \
      --waves all --out data/prompts/e2c_C_prompts.jsonl

Screening then runs on the Mac side with scripts/04_query_teachers.py --mode demo --variants T1 --prompts <out>.
"""

from __future__ import annotations

import argparse
from collections import Counter

from vcd.data.framings import make_prompts, positive_act
from vcd.io import load_models, write_jsonl
from vcd.schemas import Family


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--families", default="data/families/contested_pool.jsonl")
    ap.add_argument("--out", default="data/prompts/contested_pool_T1.jsonl")
    ap.add_argument("--variants", default="T1", help="comma list; T0 is not supported here")
    ap.add_argument("--waves", default="1", help="comma list of meta.wave values to include, or 'all'")
    ap.add_argument("--sources", default=None, help="optional comma list of Family.source values to include")
    args = ap.parse_args()
    variants = [v for v in args.variants.split(",") if v]
    if "T0" in variants:
        raise SystemExit("T0 needs judge-generated texts; use scripts/03_build_framings.py for dev / test")
    waves = None if args.waves == "all" else {w for w in args.waves.split(",") if w}
    sources = {s for s in args.sources.split(",") if s} if args.sources else None

    fams = load_models(args.families, Family)
    fams = [f for f in fams if f.item_form == "two_action" and (waves is None or str(f.meta.get("wave", "")) in waves) and (sources is None or f.source in sources)]
    prompts, flag_counts = [], Counter()
    for f in fams:
        ps, flags = make_prompts(f, variants)
        focus = positive_act(f)[0]
        for p in ps:
            if p.focus_action is None:
                p.focus_action = focus
        prompts += ps
        flag_counts.update(flags)
    n = write_jsonl(args.out, prompts)
    print(f"{len(fams)} families -> {n} prompts -> {args.out}")
    print("by source:", dict(Counter(f.source for f in fams)))
    print("variants:", dict(Counter(p.variant for p in prompts)))
    print("focus_action:", dict(Counter(p.focus_action for p in prompts)))
    print("flags:", dict(flag_counts))


if __name__ == "__main__":
    main()
