"""Step 24: dose-response curve of teacher-specific inheritance vs the share p of contested demonstrations -> {out}/dose_*.

Examples
  python scripts/24_dose_response.py --split dev                      # -> results/dose_dev (descriptive)
  python scripts/24_dose_response.py --split test --frozen-commit abc1234   # -> results/dose (once, after the dev look)
  # synthetic tree (tests): explicit conditions, teachers and prompts
  python scripts/24_dose_response.py --split dev --conditions "0=/tmp/runs/kn/*/eval/{split}_responses.jsonl,1=/tmp/runs/c/*/eval/{split}_responses.jsonl" \
      --teacher-dir /tmp/teachers --teachers alpha,beta,gamma --prompts /tmp/prompts.jsonl --out /tmp/dose --n-boot 200

Inputs: --conditions "share=glob,..." (default: the four pre-registered conditions p = 0 K_n runs/qwen3-4b-e2ckn, p = 0.25 / 0.5
the scripts/10c mixtures runs/qwen3-4b-e2cmix25 / -e2cmix50, p = 1 E2c-C runs/qwen3-4b-e2c; `{split}` is replaced), the teacher
profiles {teacher_dir}/{teacher}_{split}_profile.jsonl, the split's prompt file. A condition whose glob matches nothing is
reported as missing and skipped (never a crash): with only p = 0 and p = 1 present the script runs, computes the two-point
slope (= the e2c attribution difference) and says the curve is incomplete. <run_dir>/train_manifest.json next to each
response file supplies n_examples / n_target_tokens when present.

Per condition everything is vcd.analysis.e2c_metrics.analyze_condition (gap_T, seed-pair null, family bootstrap with ONE
weight matrix shared by all conditions), so the p = 0 / p = 1 rows equal scripts/19's K_n / C rows exactly. The trend
statistic, its family-bootstrap CI, the Spearman over the shares and the verdict rule are in vcd.analysis.dose_metrics
(module docstring = the pre-registered rule, repeated in the summary header).

Outputs: dose_gaps.csv (share x teacher: gap, CI, null, flags, seed-mean flip_rate and s), dose_slopes.csv (teacher x metric:
slope, CI for gap, Spearman), dose_runs.csv (per run), dose_verdict.json, dose_summary.md (Chinese headline + tables; header
says "frozen at commit X" or "not yet frozen"). No figures.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from vcd.analysis import dose_metrics as D
from vcd.analysis import e1_metrics as M
from vcd.analysis import e2c_metrics as E
from vcd.config import resolve
from vcd.train.data import load_train_yaml

PRESPECIFIED = "trend rule pre-registered in vcd.analysis.dose_metrics before any mixture student was trained"


def _fmt(x) -> str:
    if x is None or (isinstance(x, float) and np.isnan(x)):
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


def summary_md(ctx: dict) -> str:
    split, teachers, verdict = ctx["split"], ctx["teachers"], ctx["verdict"]
    lines = [f"# 剂量反应分析（{split}，variants {', '.join(ctx['variants'])}；{ctx['freeze']}；auto-generated）", ""]
    lines += [f"**剂量反应判定：{verdict['verdict']}**（slope CI 下界 > 0 的 teacher {verdict['n_pass']}/{verdict['n_teachers']}；曲线点 p ∈ {{{', '.join(verdict['shares_present']) or '—'}}}"
              + (f"，缺 {{{', '.join(verdict['shares_missing'])}}}" if verdict["shares_missing"] else "") + "）。", ""]
    if verdict["shares_missing"] or verdict["incomplete_teachers"]:
        lines += ["**曲线不完整**：缺失条件只报告、不插补；下面的斜率只用现有的点（两点时斜率 = gap(p=1) − gap(p=0)，即 e2c 的归因差），不出判定。", ""]
    if split != "test":
        lines += [f"**{split} 只作描述**（tasks/e2c_plan.md §5：test 每条件只跑一次，看 test 后不改任何量）；只有 results/dose（test）是确认性的。", ""]
    if verdict.get("deviations"):
        lines += ["偏离预注册 seed 数：" + "；".join(verdict["deviations"]) + "。", ""]
    lines += ["规则（`vcd.analysis.dose_metrics`，预注册）：条件 = 争议示范比例 p ∈ {0（K_n，规模匹配共识）, 0.25, 0.5（C + K 混合，规模与 variant 匹配 C）, 1（C）}；每条件的 gap_T、seed-pair null 与 family bootstrap 完全沿用 "
              "`e2c_metrics.analyze_condition`（同一组重抽 family，所以各条件配对；p = 0 / 1 行与 scripts/19 的 K_n / C 行相同）。趋势统计：每 teacher 以其全部 O run（4 份 × 5 seed = 20）的 per-run gap 对 p 做最小二乘斜率；"
              f"family bootstrap 95% CI：每次重抽 family 后重算所有 run 的 gap、重拟合斜率（B = {ctx['n_boot']}，seed {ctx['seed']}），取 2.5 / 97.5 分位。**判定：slope 的 CI 下界 > 0 的 teacher ≥ 2/3 → \"dose-response supported\"，1/3 → \"partial\"，0/3 → \"not supported\"**；"
              "任一 teacher 在任一预定 p 上没有 run 则 pending。Spearman(p, seed-mean gap) 只有 4 个点，描述用；flip_rate 与 suggestibility s = δ(T5) − δ(T6) 的斜率为代价量，描述用，无 CI 无判定。", ""]

    lines += ["## 曲线：gap 随争议比例（dose_gaps.csv）", ""]
    curve = ctx["curve"]
    if len(curve):
        c = curve.copy()
        c["CI"] = [_ci(lo, hi) for lo, hi in zip(c["ci_lo"], c["ci_hi"])]
        lines += _md_table(c.sort_values(["teacher", "share"], key=lambda s: s.map({t: i for i, t in enumerate(teachers)}) if s.name == "teacher" else s),
                           ["teacher", "share", "label", "n_seeds", "agree_own", "agree_other_max", "gap", "CI", "null_q95", "exceeds_null", "ci_above_zero", "flip_rate", "s"])
    else:
        lines += ["(no condition has runs)", ""]

    lines += ["## 斜率（dose_slopes.csv；gap 行有 family-bootstrap CI，代价量只有点估计）", ""]
    slopes = ctx["slopes"]
    if len(slopes):
        s = slopes.copy()
        s["CI"] = [_ci(lo, hi) if not np.isnan(lo) else "—" for lo, hi in zip(s["ci_lo"], s["ci_hi"])]
        lines += _md_table(s, ["teacher", "metric", "n_runs", "shares", "complete", "slope", "CI", "ci_above_zero", "spearman_rho", "seed_means"])
    else:
        lines += ["(empty)", ""]

    lines += ["## 输入", ""]
    lines += _md_table(ctx["inventory"], ["share", "label", "glob", "n_files", "n_runs", "n_rows", "seeds_per_teacher", "skipped_run_ids"])
    if ctx["missing"]:
        lines += ["缺失条件（glob 无匹配，已跳过）：" + "、".join(f"p = {D.share_key(p)}（{ctx['globs'][p]}）" for p in ctx["missing"]) + "。", ""]
    if ctx["missing_profiles"]:
        lines += ["缺失 teacher profile：" + "、".join(ctx["missing_profiles"]) + "。", ""]

    runs = ctx["runs"]
    if len(runs):
        lines += ["## 每 run（dose_runs.csv）：与每个 teacher 的 agreement、gap、JSD、翻转率、suggestibility s、训练规模", ""]
        cols = ["share", "run_id", "answer_rate"] + [f"agree__{t}" for t in teachers] + ["agree_own", "agree_other_max", "other_argmax", "gap", "jsd_own", "flip_rate", "mean_jsd", "s", "n_examples", "n_target_tokens"]
        lines += _md_table(runs.sort_values(["share", "teacher", "seed"]), cols)
    lines += ["注：JSD 受 teacher 校准混淆，只与 agreement 同报；flip_rate 与 s 是争议训练的代价量，不单独解读。", ""]
    return "\n".join(lines)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["dev", "test"], help="prompt split; dev is descriptive, test is evaluated once")
    ap.add_argument("--conditions", default=D.DEFAULT_CONDITIONS, help="'share=glob,...' ({split} is substituted); default: the four pre-registered conditions")
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl; default: config paths.teacher_dir")
    ap.add_argument("--teachers", default=None, help="comma list; default: config teachers")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--variants", default=None, help="comma list of framings (default: config data.variants = T1,T3,T5,T6)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default=None, help="default: results/dose_dev for dev, results/dose for test")
    ap.add_argument("--n-boot", type=int, default=E.N_BOOT, help=f"family bootstrap resamples (pre-registered {E.N_BOOT})")
    ap.add_argument("--seed", type=int, default=E.BOOT_SEED, help="seed of the shared family resampling")
    ap.add_argument("--frozen-commit", default=None, help="hash of the commit that froze the rule (printed in the summary header)")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    teachers = args.teachers.split(",") if args.teachers else list(cfg["teachers"])
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    families = sorted({p.family_id for p in prompts.values()})
    out = Path(args.out) if args.out else Path("results/dose" if args.split == "test" else f"results/dose_{args.split}")
    freeze = f"{PRESPECIFIED}; frozen at commit {args.frozen_commit}" if args.frozen_commit else f"{PRESPECIFIED}; not yet frozen"
    globs = D.parse_conditions(args.conditions, args.split)

    teacher_dir = Path(args.teacher_dir) if args.teacher_dir else cfg["paths"]["teacher_dir"]
    tfiles = {t: teacher_dir / f"{t}_{args.split}_profile.jsonl" for t in teachers}
    missing_profiles = [str(p) for p in tfiles.values() if not p.exists()]
    if missing_profiles:
        print("warning: missing teacher profiles:", ", ".join(missing_profiles), file=sys.stderr)
    teacher_rows = M.load_responses([p for p in tfiles.values() if p.exists()], pid)
    sym_t = M.sym_table(M.frame_table(teacher_rows, prompts)) if teacher_rows else pd.DataFrame()
    if sym_t.empty:
        raise SystemExit("no teacher profile rows; pass --teacher-dir")

    W = E.bootstrap_weights(len(families), args.n_boot, args.seed)  # one resampling for every condition (paired across shares)
    results: dict[float, E.ConditionResult] = {}
    reps: dict[float, tuple[list[str], np.ndarray]] = {}
    files_by: dict[float, list[Path]] = {}
    missing: list[float] = []
    for share, pattern in globs.items():
        files = D.glob_files(pattern)
        files_by[share] = files
        if not files:
            missing.append(share)
            print(f"p = {D.share_key(share)}: no files match {pattern!r}; condition skipped", file=sys.stderr)
            continue
        rows = M.load_responses(files, pid)
        res = E.analyze_condition(D.share_key(share), rows, prompts, sym_t, teachers, variants, families, W)
        if res.skipped:
            print(f"warning: p = {D.share_key(share)}: skipping {len(res.skipped)} run id(s) that do not match the protocol pattern: {res.skipped}", file=sys.stderr)
        results[share] = res
        reps[share] = D.run_gap_replicates(res, W, teachers)
        print(f"p = {D.share_key(share)}: {len(files)} files, {len(rows)} rows, {len(res.run_tab)} runs; gap rows {int((res.gaps['n_seeds'] > 0).sum())}")
    if not results:
        print("warning: no condition has response files; writing an empty summary", file=sys.stderr)

    out.mkdir(parents=True, exist_ok=True)
    runs_parts = []
    for share, res in results.items():
        d = E.run_descriptives(res)
        if len(d):
            d.insert(0, "share", float(share))
            man = E.load_manifests(files_by[share])
            d = d.merge(man[["run_id", "n_examples", "n_target_tokens"]], on="run_id", how="left") if len(man) else d.assign(n_examples=np.nan, n_target_tokens=np.nan)
            runs_parts.append(d)
    runs = pd.concat(runs_parts, ignore_index=True) if runs_parts else pd.DataFrame(columns=["share", "condition", *E.RUN_COLS, "flip_rate", "s", "n_examples", "n_target_tokens"])
    runs.to_csv(out / "dose_runs.csv", index=False)
    curve = D.curve_table({s: r.gaps for s, r in results.items()}, runs)
    curve.to_csv(out / "dose_gaps.csv", index=False)
    slopes = D.slope_table(runs, reps, teachers)
    slopes.to_csv(out / "dose_slopes.csv", index=False)
    verdict = D.dose_verdict(slopes, teachers, list(results), runs=runs)

    inv_rows = []
    for share, pattern in globs.items():
        r = results.get(share)
        per_t = ""
        if r is not None and len(r.run_tab):
            o = r.run_tab[r.run_tab["version"] == E.GAP_VERSION]
            per_t = "; ".join(f"{t}: {','.join(str(int(s)) for s in sorted(o[o['teacher'] == t]['seed']))}" for t in teachers if (o["teacher"] == t).any())
        inv_rows.append(dict(share=D.share_key(share), label=D.condition_label(share), glob=pattern, n_files=len(files_by.get(share, [])), n_runs=len(r.run_tab) if r is not None else 0,
                             n_rows=r.n_rows if r is not None else 0, seeds_per_teacher=per_t or "(missing)", skipped_run_ids=", ".join(r.skipped) if r is not None and r.skipped else ""))
    inventory = pd.DataFrame(inv_rows)

    payload = {"split": args.split, "freeze": freeze, "rule": D.RULE, "verdict": verdict, "teachers": teachers, "variants": variants, "n_boot": args.n_boot, "seed": args.seed,
               "n_families": len(families), "conditions": {D.share_key(s): g for s, g in globs.items()}, "n_files": {D.share_key(s): len(f) for s, f in files_by.items()},
               "missing_conditions": [D.share_key(s) for s in missing], "missing_profiles": missing_profiles, "gaps": curve.to_dict(orient="records"),
               "slopes": slopes.to_dict(orient="records"), "descriptive_only": args.split != "test"}
    (out / "dose_verdict.json").write_text(json.dumps(payload, indent=2, default=_dump, ensure_ascii=False), encoding="utf-8")
    ctx = dict(split=args.split, variants=variants, teachers=teachers, verdict=verdict, curve=curve, slopes=slopes, inventory=inventory, missing=missing, globs=globs,
               missing_profiles=missing_profiles, runs=runs, n_boot=args.n_boot, seed=args.seed, freeze=freeze)
    (out / "dose_summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote dose_gaps.csv, dose_slopes.csv, dose_runs.csv, dose_verdict.json, dose_summary.md to {out}")
    print((out / "dose_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
