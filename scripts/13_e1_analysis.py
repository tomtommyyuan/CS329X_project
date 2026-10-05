"""Step 13: E1 / E2 tables from student readouts + teacher profiles -> results/e1/ (CSVs + summary.md).

Examples
  python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split test
  python scripts/13_e1_analysis.py --runs-glob "runs/qwen3-4b/*_O_s*/eval/test_responses.jsonl" --teacher-dir data/teacher_phase1 --split test
  # quick look with fewer resamples
  python scripts/13_e1_analysis.py --split dev --n-perm 1000 --n-boot 1000 --out results/e1_dev
  # CPU smoke against the pilot profiles in data/teacher_v2 (file names there have no split infix)
  python scripts/13_e1_analysis.py --runs-dir /tmp/runs --student smollm2-135m --split pilot \
      --teacher-files gpt4o=data/teacher_v2/gpt4o_profile.jsonl,deepseek_v4=data/teacher_v2/deepseek_v4_profile.jsonl \
      --n-perm 200 --n-boot 200 --out /tmp/e1_smoke

Inputs: every runs/{student}/{run}/eval/{split}_responses.jsonl (TeacherResponse rows, teacher = run id) and
{teacher_dir}/{teacher}_{split}_profile.jsonl for the teachers in the config (or explicit --teacher-files).
Outputs (docs/05 §6): category_rates.csv, order_gap.csv, agreement.csv, agreement_by_variant.csv, jsd.csv,
consistency.csv, seen_vs_unseen.csv, inheritance.csv, inheritance_by_variant.csv, inheritance_pooled.csv,
seed_null.csv, grid_permutation.json, e1_table.csv and summary.md. No figures.

Decision rules (frozen before any test-split evaluation, docs/03 §8):
  E1  per teacher, every O seed must have agree_own > agree_other_max.
  E2  per teacher, the SEED-MEAN framing-shift profile of the O students (pooled_inheritance) must have
      delta_rho > 0 with Holm-adjusted family-permutation p < 0.05 (Holm over the teachers); pass iff >= 2/3
      teachers pass. The per-seed verdicts are printed next to it for transparency only.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from vcd.analysis import e1_metrics as M
from vcd.config import resolve
from vcd.teacher import profile as P
from vcd.train.data import load_train_yaml


def _fmt(x) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
        return "nan"
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, (float, np.floating)):
        return f"{x:.3f}"
    return str(x)


def _md_table(df: pd.DataFrame, cols: list[str]) -> list[str]:
    cols = [c for c in cols if c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_fmt(r[c]) for c in cols) + " |")
    return lines + [""]


def summary_md(tab: pd.DataFrame, null: pd.DataFrame, grid: dict, teachers: list[str], split: str, variants: list[str],
               pooled: pd.DataFrame | None = None, cat_rates: pd.DataFrame | None = None, n_student_rows: int = 0) -> str:
    lines = [f"# E1 / E2 summary ({split}, variants {', '.join(variants)}; auto-generated)", ""]
    if tab.empty:
        if n_student_rows and cat_rates is not None and not cat_rates.empty:
            lines += [f"{n_student_rows} student rows were loaded but NO cell passed the readout (every row is `malformed`, "
                      "i.e. P(' A')+P('A')+P(' B')+P('B') < answer_mass_min): the students do not answer with a letter. "
                      "Per-run answer rates (category_rates.csv):", ""]
            lines += _md_table(cat_rates, ["teacher", "variant", "answer", "malformed", "n"])
            return "\n".join(lines)
        return "\n".join(lines + ["No student runs found."])
    lines += ["## Per run", ""]
    cols = ["run_id", "answer_rate", "order_gap_mean", "n_families", "agree_own", "agree_other_max", "jsd_own", "flip_rate", "mean_jsd", "rho_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "ci_lo", "ci_hi"]
    lines += _md_table(tab.sort_values(["teacher", "version", "seed"]), cols)

    lines += ["## Agreement / JSD to every teacher (rows = runs; R students included for calibration)", ""]
    lines += _md_table(tab.sort_values(["teacher", "version", "seed"]), ["run_id"] + [f"agree__{t}" for t in teachers] + [f"jsd__{t}" for t in teachers])

    lines += ["## Per (teacher, version): seed means", ""]
    agg_cols = [c for c in ("answer_rate", "agree_own", "agree_other_max", "jsd_own", "flip_rate", "mean_jsd", "rho_own", "delta_rho") if c in tab]
    g = tab.groupby(["teacher", "version"])[agg_cols].mean().reset_index()
    g["n_seeds"] = tab.groupby(["teacher", "version"]).size().values
    lines += _md_table(g, ["teacher", "version", "n_seeds"] + agg_cols)

    lines += ["## E1 decision (docs/03 §0): agreement with own teacher > max agreement with another teacher", ""]
    core = tab[tab["version"] == "O"].dropna(subset=["agree_own"])
    if core.empty:
        lines.append("no O runs with a matching teacher profile yet\n")
    for t, gt in core.groupby("teacher"):
        ok = int((gt["agree_own"] > gt["agree_other_max"]).sum())
        verdict = "ok" if ok == len(gt) else ("partial" if ok else "FAIL: fix training first")
        lines.append(f"- {t}: {ok}/{len(gt)} seeds pass -> {verdict}")
    lines.append("")

    lines += ["## E2 decision (pre-registered): seed-mean profile per teacher, delta_rho > 0 and Holm-adjusted p_perm < 0.05 on >= 2/3 teachers", ""]
    n_pass = 0
    po = pooled[pooled["version"] == "O"] if pooled is not None and not pooled.empty else pd.DataFrame()
    for _, r in (po.sort_values("teacher") if len(po) else po).iterrows():  # no O runs yet (e.g. only S_0): empty, no columns
        passed = bool(r["delta_rho"] > 0 and r["p_holm"] < 0.05)
        n_pass += int(passed)
        lines.append(f"- {r['teacher']} ({r['n_seeds']} seeds pooled, {r['n_families']} families): delta_rho {_fmt(r['delta_rho'])} "
                     f"[{_fmt(r['ci_lo'])}, {_fmt(r['ci_hi'])}], p_perm {_fmt(r['p_perm'])}, p_holm {_fmt(r['p_holm'])} -> {'pass' if passed else 'fail'}")
    if len(po):
        lines.append(f"- teachers passing: {n_pass}/{len(teachers)} -> E2 {'PASS' if n_pass * 3 >= 2 * max(len(teachers), 1) else 'FAIL'}; "
                     f"grid permutation (teacher assignment shuffled across runs): mean delta_rho {_fmt(grid.get('observed'))}, null sd {_fmt(grid.get('null_sd'))}, p {_fmt(grid.get('p'))}")
    else:
        lines.append("no O runs with a matching teacher profile yet")
    lines.append("")
    lines += ["### Per-seed view (transparency only, not the decision rule)", ""]
    core2 = core.dropna(subset=["delta_rho"]) if "delta_rho" in core else core.iloc[0:0]
    for t, gt in core2.groupby("teacher"):
        ok = int(((gt["delta_rho"] > 0) & (gt["p_perm"] < 0.05)).sum())
        lines.append(f"- {t}: mean delta_rho {_fmt(gt['delta_rho'].mean())} (sd {_fmt(gt['delta_rho'].std())}), {ok}/{len(gt)} seeds individually with delta_rho > 0 and p < 0.05")
    lines.append("")

    lines += ["## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)", ""]
    lines += _md_table(null, ["metric", "teacher", "version", "n_pairs", "mean", "sd", "q95"])
    lines += ["Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. ", "Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id)."]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", default=None, help="default: config paths.runs_dir")
    ap.add_argument("--student", default=None, help="student_model_short to select runs/{student}/*; default: config value")
    ap.add_argument("--runs-glob", default=None, help="explicit glob of response files (overrides --runs-dir/--student)")
    ap.add_argument("--split", default="test", choices=["dev", "test", "pilot"])
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl; default: config paths.teacher_dir")
    ap.add_argument("--teacher-files", default=None, help="explicit profiles, 'gpt4o=path,claude46=path' (overrides --teacher-dir/--teachers)")
    ap.add_argument("--teachers", default=None, help="comma list; default: config teachers")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--variants", default=None, help="comma list of framings for the metrics (default: config data.variants = T1,T3,T5,T6)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default="results/e1")
    ap.add_argument("--n-perm", type=int, default=10_000)
    ap.add_argument("--n-boot", type=int, default=10_000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    teacher_files = dict(kv.split("=", 1) for kv in args.teacher_files.split(",")) if args.teacher_files else None
    teachers = list(teacher_files) if teacher_files else (args.teachers.split(",") if args.teachers else list(cfg["teachers"]))
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)

    # students
    if args.runs_glob:
        files = sorted(Path(".").glob(args.runs_glob)) if not Path(args.runs_glob).is_absolute() else sorted(Path("/").glob(args.runs_glob.lstrip("/")))
        student_rows = M.load_responses(files, pid)
    else:
        runs_dir = Path(args.runs_dir) if args.runs_dir else cfg["paths"]["runs_dir"]
        student_rows = [r for r in M.load_run_responses(runs_dir, args.split, args.student or cfg["student_model_short"]) if r.prompt_id in pid]
    bad_ids = sorted({r.teacher for r in student_rows if not M.is_run_id(r.teacher)})
    if bad_ids:
        print(f"warning: skipping {len(bad_ids)} run id(s) that do not match the protocol pattern (smoke runs?): {bad_ids}", file=sys.stderr)
        student_rows = [r for r in student_rows if r.teacher not in bad_ids]
    # teachers
    teacher_dir = Path(args.teacher_dir) if args.teacher_dir else cfg["paths"]["teacher_dir"]
    tfiles = [Path(teacher_files[t]) for t in teachers] if teacher_files else [teacher_dir / f"{t}_{args.split}_profile.jsonl" for t in teachers]
    missing = [str(p) for p in tfiles if not p.exists()]
    if missing:
        print("warning: missing teacher profiles:", ", ".join(missing))
    teacher_rows = M.load_responses([p for p in tfiles if p.exists()], pid)
    print(f"students: {len(student_rows)} rows, {len({r.teacher for r in student_rows})} runs; teachers: {len(teacher_rows)} rows, {len({r.teacher for r in teacher_rows})} profiles")
    if not student_rows:
        raise SystemExit("no student responses found; run scripts/12_eval_student.py first")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    fs, ft = M.frame_table(student_rows, prompts), M.frame_table(teacher_rows, prompts)
    sym_s, sym_t = M.sym_table(fs), M.sym_table(ft)
    present = sorted(sym_t["teacher"].unique()) if not sym_t.empty else []

    cat_rates = M.category_rates(fs, by=("teacher", "variant"))
    cat_rates.to_csv(out / "category_rates.csv", index=False)
    M.order_gap(pd.concat([sym_s, sym_t])).to_csv(out / "order_gap.csv", index=False)
    M.teacher_agreement(sym_s, sym_t, variants).to_csv(out / "agreement.csv", index=False)
    M.teacher_agreement(sym_s, sym_t, variants, by_variant=True).to_csv(out / "agreement_by_variant.csv", index=False)
    M.student_teacher_jsd(sym_s, sym_t, variants).to_csv(out / "jsd.csv", index=False)
    M.consistency(pd.concat([sym_s, sym_t]), variants).to_csv(out / "consistency.csv", index=False)
    M.seen_vs_unseen(pd.concat([sym_s, sym_t]), variants, "T0").to_csv(out / "seen_vs_unseen.csv", index=False)

    tab = M.e1_table(fs, ft, prompts, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
    tab.to_csv(out / "e1_table.csv", index=False)

    shifts_s, shifts_t = P.framing_shifts(sym_s, variants), P.framing_shifts(sym_t, variants)
    own = {r: M.parse_run_id(r).teacher for r in sym_s["teacher"].unique() if M.is_run_id(r)}
    inh = M.inheritance(shifts_s, shifts_t, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
    inh.to_csv(out / "inheritance.csv", index=False)
    M.inheritance(shifts_s, shifts_t, own, variants, n_perm=0, n_boot=0, by_variant=True).to_csv(out / "inheritance_by_variant.csv", index=False)
    pooled = M.pooled_inheritance(shifts_s, shifts_t, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
    pooled.to_csv(out / "inheritance_pooled.csv", index=False)
    core = inh[inh["run_id"].map(lambda r: M.parse_run_id(r).version == "O")] if not inh.empty else inh
    grid = M.grid_permutation(core, n_perm=args.n_perm, seed=args.seed) if len(core) else {}
    (out / "grid_permutation.json").write_text(json.dumps(grid, indent=2), encoding="utf-8")

    nulls = []
    if not tab.empty:
        for metric in ("agree_own", "jsd_own", "flip_rate", "mean_jsd", "delta_rho"):
            if metric in tab and tab[metric].notna().any():
                nulls.append(M.seed_noise_null(tab.dropna(subset=[metric]), metric))
    null = pd.concat(nulls, ignore_index=True) if nulls else pd.DataFrame(columns=["teacher", "version", "metric", "n_pairs", "mean", "sd", "q95"])
    null.to_csv(out / "seed_null.csv", index=False)

    (out / "summary.md").write_text(summary_md(tab, null, grid, present, args.split, variants, pooled, cat_rates, len(student_rows)), encoding="utf-8")
    print(f"wrote {len(list(out.glob('*.csv')))} CSVs + summary.md to {out}")
    print((out / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
