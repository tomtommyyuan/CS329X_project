"""E2c demo plumbing around scripts/04 and scripts/10 (tasks/e2c_plan.md §11 G-H).

Two subcommands:

  new-prompts   prompts that still need a teacher call: rows of the E2c prompt file (scripts/17 output for the
                selected C or K families) whose prompt_id has no demo yet -- tier-0 families already have every
                variant in data/teacher_phase1/{teacher}_train_demo.jsonl and every pool family has its T1 rows in
                data/teacher_e2c/{teacher}_pool_screen.jsonl, so only T3 / T5 / T6 of pool families remain.
                  python scripts/17b_e2c_demo_inputs.py new-prompts --prompts data/prompts/e2c_C_prompts.jsonl \
                      --existing data/prompts/train_prompts_v2.jsonl --out data/prompts/e2c_C_new_prompts.jsonl

  assemble      one TeacherResponse file per (teacher, condition) for scripts/10: concatenates the phase-1 train
                demos, the screening rows and the new demo rows, keeps exactly the rows whose prompt_id is in the
                condition's prompt file (first occurrence wins), and fails if any prompt is still missing.
                  python scripts/17b_e2c_demo_inputs.py assemble --prompts data/prompts/e2c_C_prompts.jsonl \
                      --sources data/teacher_phase1/gpt4o_train_demo.jsonl,data/teacher_e2c/gpt4o_pool_screen.jsonl,data/teacher_e2c/gpt4o_e2c_C_new_demo.jsonl \
                      --teacher gpt4o --out data/teacher_e2c/gpt4o_e2c_C_demo.jsonl
"""

from __future__ import annotations

import argparse
import collections
import json
import sys
from pathlib import Path


def read_jsonl(path: str | Path):
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def cmd_new_prompts(args: argparse.Namespace) -> int:
    existing = {r["prompt_id"] for r in read_jsonl(args.existing)}
    kept, by_variant, skipped = [], collections.Counter(), collections.Counter()
    for r in read_jsonl(args.prompts):
        if r["prompt_id"] in existing:
            skipped["tier0_has_demo"] += 1
        elif r["variant"] == "T1":
            skipped["pool_T1_screened"] += 1
        else:
            kept.append(r)
            by_variant[r["variant"]] += 1
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for r in kept:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"{args.prompts}: kept {len(kept)} prompts needing a call {dict(by_variant)}; skipped {dict(skipped)} -> {args.out}")
    return 0


def cmd_assemble(args: argparse.Namespace) -> int:
    prompts = {r["prompt_id"]: r for r in read_jsonl(args.prompts)}
    out_rows: dict[str, dict] = {}
    per_source = collections.Counter()
    for src in args.sources.split(","):
        p = Path(src)
        if not p.exists():
            print(f"warning: {src} does not exist, skipped", file=sys.stderr)
            continue
        for r in read_jsonl(p):
            pid = r["prompt_id"]
            if pid in prompts and pid not in out_rows:
                if args.teacher and r.get("teacher") not in (None, args.teacher):
                    raise SystemExit(f"{src}: row for {pid} is labelled teacher={r.get('teacher')!r}, expected {args.teacher!r}")
                out_rows[pid] = r
                per_source[p.name] += 1
    missing = [pid for pid in prompts if pid not in out_rows]
    miss_by_variant = collections.Counter(prompts[pid]["variant"] for pid in missing)
    Path(args.out).parent.mkdir(parents=True, exist_ok=True)
    with open(args.out, "w") as f:
        for pid in prompts:  # prompt-file order
            if pid in out_rows:
                f.write(json.dumps(out_rows[pid], ensure_ascii=False) + "\n")
    cats = collections.Counter(r.get("category") for r in out_rows.values())
    print(f"assembled {len(out_rows)} / {len(prompts)} demos from {dict(per_source)} -> {args.out}; categories {dict(cats)}; "
          f"missing {len(missing)} {dict(miss_by_variant)}")
    if missing and not args.allow_missing:
        print("first missing prompt_ids:", missing[:5], file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("new-prompts")
    a.add_argument("--prompts", required=True)
    a.add_argument("--existing", default="data/prompts/train_prompts_v2.jsonl", help="prompt file whose ids already have phase-1 demos")
    a.add_argument("--out", required=True)
    a.set_defaults(fn=cmd_new_prompts)
    b = sub.add_parser("assemble")
    b.add_argument("--prompts", required=True)
    b.add_argument("--sources", required=True, help="comma list of TeacherResponse jsonl files, earlier files win")
    b.add_argument("--teacher", default=None, help="assert every kept row carries this teacher label")
    b.add_argument("--out", required=True)
    b.add_argument("--allow-missing", action="store_true")
    b.set_defaults(fn=cmd_assemble)
    args = ap.parse_args()
    return args.fn(args)


if __name__ == "__main__":
    raise SystemExit(main())
