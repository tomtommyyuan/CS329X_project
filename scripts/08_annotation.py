"""Step 08: human annotation sheets.
  export-framing                      -> data/annotation/framing_equivalence_pilot.csv (copy once per annotator)
  score-framing  A.csv B.csv          -> pass rate and kappa per variant
  export-rewrite --teacher gpt41      -> data/annotation/rewrite_audit_gpt41.csv
  score-rewrite  A.csv B.csv          -> pass rate and kappa per version
"""

from __future__ import annotations

import argparse

import pandas as pd

from vcd.analysis.annotation_sheets import export_framing_sheet, export_rewrite_sheet, score_framing, score_rewrite
from vcd.config import load_e0
from vcd.io import load_models, read_jsonl
from vcd.schemas import Family, Prompt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["export-framing", "score-framing", "export-rewrite", "export-rewrite-blind", "score-rewrite", "score-single"])
    ap.add_argument("files", nargs="*")
    ap.add_argument("--teacher", default=None)
    ap.add_argument("--teachers", default="gpt4o,claude46,deepseek_v4", help="for export-rewrite-blind")
    ap.add_argument("--n-per-version", type=int, default=300)
    ap.add_argument("--n-per-cell", type=int, default=50, help="blind sheet: items per teacher x version")
    ap.add_argument("--key", default=None, help="score-rewrite: key csv of a blind sheet")
    ap.add_argument("--name", default=None, help="export-rewrite-blind: output base name (default rewrite_audit_blind)")
    ap.add_argument("--tag", default=None, help="export-rewrite-blind: read rewrites from data/rewrites_<tag>/")
    ap.add_argument("--config", default="configs/e0.yaml")
    args = ap.parse_args()
    cfg = load_e0(args.config)
    ann = cfg["paths"]["annotation_dir"]

    if args.cmd == "export-framing":
        prompts = load_models(cfg["paths"]["prompts"], Prompt)
        fams = {f.family_id: f for f in load_models(cfg["paths"]["families"], Family)}
        n = export_framing_sheet(prompts, fams, ann / "framing_equivalence_pilot.csv")
        print(f"{n} rows -> {ann / 'framing_equivalence_pilot.csv'}")
    elif args.cmd == "score-framing":
        print(score_framing(*map(__import__("pathlib").Path, args.files[:2])).to_string(index=False))
    elif args.cmd == "export-rewrite":
        assert args.teacher, "--teacher required"
        d = cfg["paths"]["teacher_dir"].parent / "rewrites" / args.teacher
        rewrites = pd.DataFrame(list(read_jsonl(d / "rewrites.jsonl")))
        records = pd.DataFrame(list(read_jsonl(d / "records.jsonl")))
        n = export_rewrite_sheet(rewrites, records, args.n_per_version, ann / f"rewrite_audit_{args.teacher}.csv", int(cfg["seed"]))
        print(f"{n} rows -> {ann / f'rewrite_audit_{args.teacher}.csv'}")
    elif args.cmd == "export-rewrite-blind":
        from vcd.analysis.annotation_sheets import export_blind_rewrite_sheet

        per_teacher = {}
        for t in args.teachers.split(","):
            d = cfg["paths"]["teacher_dir"].parent / ("rewrites" + (f"_{args.tag}" if args.tag else "")) / t
            per_teacher[t] = (pd.DataFrame(list(read_jsonl(d / "rewrites.jsonl"))), pd.DataFrame(list(read_jsonl(d / "records.jsonl"))))
        name = args.name or "rewrite_audit_blind"
        n = export_blind_rewrite_sheet(per_teacher, args.n_per_cell, ann / f"{name}.csv", ann / f"{name}_KEY.csv", int(cfg["seed"]))
        print(f"{n} rows -> {ann / (name + '.csv')} (key: {name}_KEY.csv, keep it away from annotators)")
    elif args.cmd == "score-rewrite":
        from pathlib import Path as _P

        print(score_rewrite(_P(args.files[0]), _P(args.files[1]), _P(args.key) if args.key else None).to_string(index=False))
    elif args.cmd == "score-single":
        import csv as _csv

        key = {r["item_id"]: r for r in _csv.DictReader(open(args.key, encoding="utf-8"))} if args.key else {}
        rows = list(_csv.DictReader(open(args.files[0], encoding="utf-8")))
        bit = lambda s: 1 if str(s).strip() in ("1", "1.0", "yes", "y", "true") else 0
        fields = ["same_choice(1/0)", "same_reasons(1/0)", "same_conditions(1/0)", "same_strength(1/0)"]
        df = pd.DataFrame([{"version": key.get(r["item_id"], {}).get("version", r.get("version", "")), "teacher": key.get(r["item_id"], {}).get("teacher", r.get("teacher", "")),
                            **{f: bit(r[f]) for f in fields}, "pass": all(bit(r[f]) for f in fields),
                            "register_ok": r["register(F/C)"].strip().upper()[:1] == key.get(r["item_id"], {}).get("version", r.get("version", ""))} for r in rows])
        print(df.groupby("version").agg(n=("pass", "size"), pass_all4=("pass", "mean"), **{f.split("(")[0]: (f, "mean") for f in fields}, register_ok=("register_ok", "mean")).round(3).to_string())
        print()
        print(df.groupby(["teacher", "version"]).agg(n=("pass", "size"), pass_all4=("pass", "mean")).round(3).to_string())


if __name__ == "__main__":
    main()
