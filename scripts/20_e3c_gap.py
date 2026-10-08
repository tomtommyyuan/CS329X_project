"""Step 20: E3c gap analysis (does register rewriting of the contested-set demonstrations change how much a student inherits
its OWN teacher's judgments?) -> {out}/e3c_* (CSVs + e3c_summary.md).

Examples
  python scripts/20_e3c_gap.py --split dev                                   # -> results/e3c_dev (descriptive, the freeze split)
  python scripts/20_e3c_gap.py --split test --frozen-commit <hash>           # -> results/e3c (once, after the freeze line in tasks/hpc_log.md)
  # stand-in smoke on the E3 paired grid (45 runs of the full train set): same statistics, different students
  python scripts/20_e3c_gap.py --split dev --student qwen3-4b-paired --out /tmp/e3c_smoke/dev
  # synthetic tree (tests): explicit teachers and prompts
  python scripts/20_e3c_gap.py --split dev --runs-dir /tmp/runs --student qwen3-4b-e2c-paired --teacher-dir /tmp/teachers \
      --teachers alpha,beta,gamma --prompts /tmp/prompts.jsonl --out /tmp/e3c --n-boot 200

Inputs: runs/{student}/{teacher}_{O|F|C}_s{seed}/eval/{split}_responses.jsonl (TeacherResponse rows, teacher = run id; the
E3c namespace is runs/qwen3-4b-e2c-paired), {teacher_dir}/{teacher}_{split}_profile.jsonl and the split's prompt file.
Everything degrades to pending rows when a version or a teacher is missing; nothing here calls an API.

Outputs (all prefixed e3c_): e3c_gap_verdicts.csv (+ .json with the raw e3_verdict dicts, + e3c_gap_verdict_teachers.csv per
teacher), e3c_gap_by_teacher.csv (per teacher x version: seed-mean agree_own / agree_other / gap with family-bootstrap CIs, and
for F / C the seed-paired difference vs O with its CI; e3c_gap_by_seed.csv per seed), e3c_gap_runs.csv (per run: family-unit
values and the cell-weighted E2c-style values), e3c_gap_null.csv (signed O-O seed-pair differences), e3c_reference_other.csv,
e3c_inventory.csv, e3c_summary.md. No figures.

Quantity and rule (pre-specified before any E3c F / C run; vcd.analysis.e3c_metrics):
  gap of a run = agreement with the own teacher minus agreement with the REFERENCE other teacher (the E2c gap of
  tasks/e2c_plan.md §6 with a fixed comparison teacher), symmetrized majority action per (family, variant) cell, cells
  with p_sym = 0.5 dropped; unit = family: d_f = agree_own_f - agree_other_f, run value = mean_f d_f over one family set
  per teacher. Reference other of T = the other teacher with the highest seed-mean cell-weighted agreement
  (e1_metrics.teacher_agreement) with T's O students of this grid (ties alphabetical), reused for F and C.
  Statistics = the frozen E3 rules (tasks/e3_plan.md §2-3): per teacher the seed mean of the paired difference
  mean_f d_f(S_{T,V,s}) - mean_f d_f(S_{T,O,s}) with a family-bootstrap CI; null = signed O-O seed-pair differences of
  mean_f d_f pooled over teachers, scaled to the seed mean (SD_stat = sqrt(mean(d^2) / n_seeds), q95 = t(0.975, df = sum
  (n_O - 1)) x SD_stat); effect iff >= 2/3 teachers exceed with the same sign; no effect iff >= 2/3 teachers pass the TOST
  (CI inside +/- 1 SD_stat); else inconclusive; fewer than 3 teachers with paired runs -> pending. Two rows: gap F - O and
  gap C - O. dev is the freeze split (descriptive); test is evaluated once.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

import numpy as np
import pandas as pd

from vcd.analysis import e1_metrics as M
from vcd.analysis import e3c_metrics as G
from vcd.config import resolve
from vcd.train.data import load_train_yaml

PRESPECIFIED = "E3c gap rule pre-specified (tasks/e3c_plan.md; statistics = the frozen E3 rules of tasks/e3_plan.md §2-3) before any E3c F / C run existed"
RULE_ZH = "效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致"


def freeze_label(frozen_commit: Optional[str]) -> str:
    return f"{PRESPECIFIED}; frozen at commit {frozen_commit} (tasks/hpc_log.md)" if frozen_commit else f"{PRESPECIFIED}; not yet frozen (freeze line pending in tasks/hpc_log.md)"


def _fmt(x) -> str:
    if x is None or (isinstance(x, (float, np.floating)) and np.isnan(x)):
        return "nan"
    if isinstance(x, (bool, np.bool_)):
        return str(bool(x))
    if isinstance(x, (int, np.integer)):
        return str(int(x))
    if isinstance(x, (float, np.floating)):
        return f"{x:.3f}" if abs(x) >= 1e-3 or x == 0 else f"{x:.1e}"
    return str(x)


def _md_table(df: pd.DataFrame, cols: list[str]) -> list[str]:
    cols = [c for c in cols if c in df.columns]
    if not cols or df.empty:
        return ["(empty)", ""]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_fmt(r[c]) for c in cols) + " |")
    return lines + [""]


def _ci(lo, hi) -> str:
    return f"[{_fmt(lo)}, {_fmt(hi)}]"


def _dump(x):
    if isinstance(x, np.generic):
        return x.item()
    if isinstance(x, float) and np.isnan(x):
        return None
    return str(x)


# --------------------------------------------------------------------------- tables


def by_teacher_table(a: G.GapAnalysis) -> pd.DataFrame:
    """Levels per (teacher, version) joined with the seed-paired difference vs O (NaN on the O rows)."""
    lv = a.levels.copy()
    cols = ["teacher", "version", "n_pairs", "n_families_paired", "diff", "diff_ci_lo", "diff_ci_hi", "direction"]
    if len(a.per_teacher):
        pt = a.per_teacher.rename(columns={"n_seeds": "n_pairs", "n_families": "n_families_paired", "ci_lo": "diff_ci_lo", "ci_hi": "diff_ci_hi"})[cols]
        lv = lv.merge(pt, on=["teacher", "version"], how="left")
    else:
        for c in cols[2:]:
            lv[c] = np.nan
    for c in ("n_pairs", "n_families_paired"):
        lv[c] = lv[c].astype("Int64")  # whole numbers next to the NaN of the O rows (no "5.0" in the CSV)
    lv["direction"] = lv["direction"].where(lv["direction"].notna(), "")
    order = {v: i for i, v in enumerate(["O", "F", "C"])}
    return lv.sort_values(["teacher", "version"], key=lambda s: s.map(order) if s.name == "version" else s).reset_index(drop=True)


def cw_check(runs: pd.DataFrame) -> pd.DataFrame:
    """Family-unit gap vs the cell-weighted gap of the same runs (|gap - gap_cw|): mean and max per version and overall."""
    cols = ["version", "n_runs", "mean_abs_diff", "max_abs_diff", "mean_gap", "mean_gap_cw", "mean_gap_e2c_cw"]
    if runs.empty or runs["gap_cw"].isna().all():
        return pd.DataFrame(columns=cols)
    rows = []
    for v, g in [*runs.groupby("version", sort=True), ("all", runs)]:
        d = (g["gap"] - g["gap_cw"]).abs()
        rows.append(dict(version=v, n_runs=int(len(g)), mean_abs_diff=float(d.mean()), max_abs_diff=float(d.max()), mean_gap=float(g["gap"].mean()), mean_gap_cw=float(g["gap_cw"].mean()), mean_gap_e2c_cw=float(g["gap_e2c_cw"].mean())))
    return pd.DataFrame(rows, columns=cols)


# --------------------------------------------------------------------------- summary


def summary_md(ctx: dict) -> str:
    a: G.GapAnalysis = ctx["a"]
    split, student = ctx["split"], ctx["student"]
    lines = [f"# E3c gap 分析（{split}，student {student}，variants {', '.join(ctx['variants'])}；{ctx['freeze']}；auto-generated）", ""]
    vt = a.verdicts
    if len(vt):
        lines += ["；".join(f"**{r['metric']}：{r['verdict']}**（{r['n_pass']}/{r['n_teachers']} 过 q95，{r['n_tost']}/{r['n_teachers']} 过 TOST，方向 {r['direction']}）" for _, r in vt.iterrows()) + "。", ""]
    else:
        lines += ["**pending**：没有 F / C 版本可判。", ""]
    if split != "test":
        lines += [f"**{split} = freeze split**：以下判定只作描述；只有 results/e3c（test，冻结后只跑一次）是确认性的。", ""]
    lines += [f"问题：contested-set 示范的文风改写（O → F / C）是否改变学生对**自己** teacher 判断的继承量。量 = E2c 的 gap（tasks/e2c_plan.md §6）按 family 计：每 run 每 family f 的 d_f = agree_own_f − agree_other_f，"
              "agree = 该 family 内有定义多数的 (family, variant) cell 上学生多数行动与 teacher 多数行动相同的份额（symmetrized，p_sym = 0.5 的 cell 不计，`e3_metrics.family_compare`）；run 值 = mean_f d_f，"
              "同 teacher 的所有 run 共用一个 family 集（对每个 run 都完整且 gap 有定义的 family），null、水平与配对统计量在同一组 family 上。参照 other teacher 按 teacher 固定：与该 teacher 的 O 学生 run 级 agreement"
              "（`e1_metrics.teacher_agreement`，cell 加权）seed 均值最高的其他 teacher（并列取字母序最前），O / F / C 共用，见下表。", ""]
    lines += [f"规则（docs/03 E3 行原文：{RULE_ZH}；tasks/e3_plan.md §2–3 的冻结统计，`e3_metrics.paired_delta` / `seed_pair_null` / `e3_verdict`）：每 teacher 统计量 = {ctx['n_seeds_text']} 个 seed 配对差 "
              f"mean_f d_f(S_T,V,s) − mean_f d_f(S_T,O,s) 的均值，family bootstrap 95% CI（B = {ctx['n_boot']}，seed {ctx['seed']}，同 teacher 各 seed 联动重抽）；null = 同 teacher 两个 O seed 的 mean_f d_f 之差"
              f"（带符号，C(n_O, 2) 对，跨 teacher 合并，n = {ctx['n_null']}），尺度匹配到 seed 均值：SD_stat = sqrt(mean(d²) / n_seeds)，q95 = t(0.975, df = Σ(n_O − 1) = {ctx['df']}) × SD_stat；teacher 过 ⇔ |stat| > q95；"
              f"effect ⇔ ≥ 2/3 的 {ctx['n_required']} 个 teacher 过且同号；no effect ⇔ ≥ 2/3 teacher 过 TOST（CI 与点估计落在 ± 1 SD_stat 内）；否则 inconclusive；无配对 run 或 teacher < 3 → pending。"
              "单对 q95（`null_q95_single`、`n_pass_single`）只作敏感性列。假设：seed 噪声近似正态、跨 seed 独立（同 seed 的 F / O 对共享初始化与数据顺序，null 偏保守）。", ""]

    lines += [f"## 判定（e3c_gap_verdicts.csv；{'descriptive on ' + split if split != 'test' else 'confirmatory'}）", ""]
    if len(vt):
        lines += ["| metric | teachers: stat [CI] (effect in null sd, p, Holm, TOST) * = exceeds q95 | null q95 of the stat (single-pair q95; n) | pass | TOST pass | direction | verdict |", "|---|---|---|---|---|---|---|"]
        for _, r in vt.iterrows():
            lines.append(f"| {r['metric']} | {r['teachers']} | {_fmt(r['null_q95'])} ({_fmt(r['null_q95_single'])}; {r['n_null']}) | {r['n_pass']}/{r['n_teachers']} | {r['n_tost']}/{r['n_teachers']} | {r['direction']} | **{r['verdict']}** |")
        lines.append("")
    else:
        lines += ["pending: no F / C version configured", ""]
    vtt = a.verdict_teachers
    if len(vtt):
        lines += ["每 teacher 的统计量（e3c_gap_verdict_teachers.csv）：", ""]
        lines += _md_table(vtt, ["metric", "teacher", "n_seeds", "stat", "ci_lo", "ci_hi", "null_sd", "q95", "effect_sd", "exceeds_q95", "exceeds_q95_single", "p_null", "p_holm", "tost"])

    lines += ["## 每 (teacher, version) 的水平与配对差（e3c_gap_by_teacher.csv；agree_own / agree_other / gap = family 单位的 seed 均值，CI = family bootstrap；diff = 与 O 按 seed 配对的差，e3c_gap_by_seed.csv 为每 seed）", ""]
    bt = ctx["by_teacher"]
    if len(bt):
        b = bt.copy()
        b["agree_own [CI]"] = [f"{_fmt(x)} {_ci(lo, hi)}" for x, lo, hi in zip(b["agree_own"], b["agree_own_ci_lo"], b["agree_own_ci_hi"])]
        b["agree_other [CI]"] = [f"{_fmt(x)} {_ci(lo, hi)}" for x, lo, hi in zip(b["agree_other"], b["agree_other_ci_lo"], b["agree_other_ci_hi"])]
        b["gap [CI]"] = [f"{_fmt(x)} {_ci(lo, hi)}" for x, lo, hi in zip(b["gap"], b["gap_ci_lo"], b["gap_ci_hi"])]
        b["diff vs O [CI]"] = [("" if pd.isna(d) else f"{_fmt(d)} {_ci(lo, hi)}") for d, lo, hi in zip(b["diff"], b["diff_ci_lo"], b["diff_ci_hi"])]
        for c in ("n_pairs", "n_families_paired"):
            b[c] = ["" if pd.isna(x) else str(int(x)) for x in b[c]]
        lines += _md_table(b, ["teacher", "version", "n_seeds", "n_families", "agree_own [CI]", "agree_other [CI]", "gap [CI]", "n_pairs", "n_families_paired", "diff vs O [CI]", "direction"])
    else:
        lines += ["pending (no scored run: a run needs its teacher's profile and a reference other teacher)", ""]

    lines += ["## 参照 other teacher（e3c_reference_other.csv；由该 teacher 的 O 学生的 cell 加权 run 级 agreement 的 seed 均值选出，并列取字母序最前）", ""]
    lines += _md_table(a.reference, ["teacher", "reference_other", "n_O_runs", "agree_ref", "tie", "candidates", *[f"agree__{t}" for t in ctx["teachers"]]])
    ties = a.reference[a.reference["tie"] == True]  # noqa: E712
    if len(ties):
        lines += ["**并列**（取字母序最前）：" + "、".join(ties["teacher"]) + "。", ""]

    lines += ["## seed-pair null：同 teacher 两个 O seed 的 mean_f d_f 之差（e3c_gap_null.csv）", ""]
    null = a.null
    if len(null):
        ns = pd.DataFrame([dict(teacher=t, **{"n": int(len(g)), "mean_diff": float(g["diff"].mean()), "rms": float(np.sqrt(np.mean(g["diff"] ** 2))), "mean_abs": float(g["abs_diff"].mean()), "q95_abs": float(np.quantile(g["abs_diff"], 0.95))})
                           for t, g in [*null.groupby("teacher", sort=True), ("all", null)]])
        lines += _md_table(ns, ["teacher", "n", "mean_diff", "rms", "mean_abs", "q95_abs"])
        if len(vt) and np.isfinite(vt["null_sd"]).any():
            r0 = vt.iloc[0]
            lines += [f"尺度匹配后统计量的 null SD = {_fmt(r0['null_sd'])}，q95 = {_fmt(r0['null_q95'])}（单对 RMS {_fmt(r0['null_sd_single'])}，单对 q95 {_fmt(r0['null_q95_single'])}；df = {ctx['df']}）。", ""]
    else:
        lines += ["pending (needs >= 2 O seeds of one teacher)", ""]

    lines += ["## Run inventory（e3c_inventory.csv；本 split 有 readout 的 run）", ""]
    lines += _md_table(a.inventory, ["teacher", *[f"n_{v}" for v in ctx["versions"]], *[f"seeds_{v}" for v in ctx["versions"]], *[f"paired_{v}" for v in ctx["versions"] if v != "O"]])
    if ctx["missing_profiles"]:
        lines += ["缺失 teacher profile：" + "、".join(ctx["missing_profiles"]) + "。", ""]
    if ctx["bad_ids"]:
        lines += [f"跳过 {len(ctx['bad_ids'])} 个不合协议模式的 run id：" + ", ".join(ctx["bad_ids"]) + "。", ""]

    lines += ["## 每 run（e3c_gap_runs.csv；gap = family 单位 mean_f d_f；*_cw = 同一 run 的 cell 加权 run 级值，`e1_metrics.teacher_agreement`：gap_cw 对参照 other，gap_e2c_cw = own − max_other 即 E2c 原定义）", ""]
    runs = a.runs
    lines += _md_table(runs.sort_values(["teacher", "version", "seed"]) if len(runs) else runs, ["run_id", "reference_other", "n_families", "agree_own", "agree_other", "gap", "agree_own_cw", "agree_other_cw", "gap_cw", "other_argmax_cw", "gap_e2c_cw", "n_ties_own_cw"]) if len(runs) else ["(no scored run)", ""]
    cw = ctx["cw_check"]
    if len(cw):
        lines += ["family 单位与 cell 加权之差 |gap − gap_cw|（预期不为 0：d_f 是 family 均值，不按 cell 加权；单位 = family 是 e3_metrics.family_compare 的约定）：", ""]
        lines += _md_table(cw, ["version", "n_runs", "mean_abs_diff", "max_abs_diff", "mean_gap", "mean_gap_cw", "mean_gap_e2c_cw"])
    lines += ["注：学生在 teacher 内按 seed 配对比较；gap 不单独解读，与 e3c 的 agreement / JSD 表（scripts/15 在同一 run 上）同报；R 学生与基座不是 E3c 的 cell。"]
    return "\n".join(lines)


# --------------------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["dev", "test"], help="prompt split; dev is the freeze split (descriptive), test is evaluated once")
    ap.add_argument("--runs-dir", default=None, help="default: config paths.runs_dir (runs)")
    ap.add_argument("--student", default="qwen3-4b-e2c-paired", help="student namespace runs/{student}/* (default qwen3-4b-e2c-paired; qwen3-4b-paired for the E3 stand-in smoke)")
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl; default: config paths.teacher_dir (data/teacher_phase1)")
    ap.add_argument("--teachers", default=None, help="comma list; default: config teachers (gpt4o,claude46,deepseek_v4); n_required of the rule = its length")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--variants", default=None, help="comma list of framings for the cells (default: config data.variants = T1,T3,T5,T6)")
    ap.add_argument("--versions", default="O,F,C", help="versions in the grid; must include O; one verdict row per other version")
    ap.add_argument("--n-boot", type=int, default=10_000, help="family bootstrap resamples")
    ap.add_argument("--seed", type=int, default=0, help="seed of the bootstrap")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default=None, help="default results/e3c_dev (dev) or results/e3c (test)")
    ap.add_argument("--frozen-commit", default=None, help="commit hash of the freeze line in tasks/hpc_log.md (printed in the summary header); omitted -> 'not yet frozen'")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    versions = [v for v in args.versions.split(",") if v]
    if "O" not in versions:
        raise SystemExit("--versions must include O (the reference version)")
    teachers = args.teachers.split(",") if args.teachers else list(cfg["teachers"])
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    out = Path(args.out) if args.out else Path("results") / ("e3c" if args.split == "test" else f"e3c_{args.split}")

    runs_dir = Path(args.runs_dir) if args.runs_dir else Path(cfg["paths"]["runs_dir"])
    student_rows = [r for r in M.load_run_responses(runs_dir, args.split, args.student) if r.prompt_id in pid]
    bad_ids = sorted({r.teacher for r in student_rows if not M.is_run_id(r.teacher)})
    if bad_ids:
        print(f"warning: skipping {len(bad_ids)} run id(s) that do not match the protocol pattern (smoke runs?): {bad_ids}", file=sys.stderr)
        student_rows = [r for r in student_rows if r.teacher not in bad_ids]
    teacher_dir = Path(args.teacher_dir) if args.teacher_dir else Path(cfg["paths"]["teacher_dir"])
    tfiles = [teacher_dir / f"{t}_{args.split}_profile.jsonl" for t in teachers]
    missing_profiles = [str(p) for p in tfiles if not p.exists()]
    if missing_profiles:
        print("warning: missing teacher profiles:", ", ".join(missing_profiles), file=sys.stderr)
    teacher_rows = M.load_responses([p for p in tfiles if p.exists()], pid)
    print(f"students: {len(student_rows)} rows, {len({r.teacher for r in student_rows})} runs under {runs_dir / args.student}; teachers: {len(teacher_rows)} rows, {len({r.teacher for r in teacher_rows})} profiles")
    if not student_rows:
        print("warning: no student responses found; every verdict is pending", file=sys.stderr)

    sym_s, sym_t = M.sym_table(M.frame_table(student_rows, prompts)), M.sym_table(M.frame_table(teacher_rows, prompts))
    a = G.analyze_gap(sym_s, sym_t, teachers, variants, versions, n_boot=args.n_boot, seed=args.seed)

    out.mkdir(parents=True, exist_ok=True)
    freeze = freeze_label(args.frozen_commit)
    by_teacher = by_teacher_table(a)
    cw = cw_check(a.runs)
    a.verdicts.to_csv(out / "e3c_gap_verdicts.csv", index=False)
    a.verdict_teachers.to_csv(out / "e3c_gap_verdict_teachers.csv", index=False)
    (out / "e3c_gap_verdicts.json").write_text(json.dumps({"rule_zh": RULE_ZH, "frozen": freeze, "split": args.split, "confirmatory": args.split == "test", "df": a.df, "n_required": len(teachers), "n_boot": args.n_boot, "seed": args.seed,
                                                            "reference_other": {r["teacher"]: r["reference_other"] for _, r in a.reference.iterrows()}, "verdicts": a.raw}, indent=2, default=_dump), encoding="utf-8")
    by_teacher.to_csv(out / "e3c_gap_by_teacher.csv", index=False)
    a.per_seed.to_csv(out / "e3c_gap_by_seed.csv", index=False)
    a.runs.to_csv(out / "e3c_gap_runs.csv", index=False)
    a.null.to_csv(out / "e3c_gap_null.csv", index=False)
    a.reference.to_csv(out / "e3c_reference_other.csv", index=False)
    a.inventory.to_csv(out / "e3c_inventory.csv", index=False)
    n_seeds = sorted(set(a.per_teacher["n_seeds"].astype(int))) if len(a.per_teacher) else []
    ctx = dict(a=a, split=args.split, student=args.student, variants=variants, versions=versions, teachers=teachers, freeze=freeze, n_boot=args.n_boot, seed=args.seed, df=a.df, n_required=len(teachers),
               n_null=int(len(a.null)), n_seeds_text=("/".join(str(n) for n in n_seeds) if n_seeds else "n"), by_teacher=by_teacher, cw_check=cw, missing_profiles=missing_profiles, bad_ids=bad_ids)
    (out / "e3c_summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote {len(list(out.glob('e3c_*.csv')))} CSVs + e3c_summary.md to {out}")
    print((out / "e3c_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
