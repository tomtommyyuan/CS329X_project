"""Step 19: E2c own-vs-other agreement gap, seed-pair null, family-bootstrap CI and the C - K attribution -> {out}/e2c_*.

Examples
  python scripts/19_e2c_analysis.py --split dev                      # -> results/e2c_dev (descriptive)
  python scripts/19_e2c_analysis.py --split test                     # -> results/e2c (once, after the dev look)
  # stand-in smoke on the E1 runs: every condition = the same 15 O runs, so every gap_T(C) - gap_T(K) is exactly 0
  python scripts/19_e2c_analysis.py --split dev --c-glob "runs/qwen3-4b/*_O_s*/eval/dev_responses.jsonl" \
      --k-glob "runs/qwen3-4b/*_O_s*/eval/dev_responses.jsonl" --out /tmp/e2c_smoke
  # synthetic tree (tests): explicit teachers and prompts
  python scripts/19_e2c_analysis.py --split dev --c-glob "/tmp/runs/qwen3-4b-e2c/*/eval/dev_responses.jsonl" \
      --teacher-dir /tmp/teachers --teachers alpha,beta,gamma --prompts /tmp/prompts.jsonl --out /tmp/e2c --n-boot 200

Inputs: the eval response files of three conditions (TeacherResponse rows, teacher = run id; `{split}` in a glob is
replaced): C = E2c contested-trained students (default runs/qwen3-4b-e2c/*_O_s*/eval/{split}_responses.jsonl), K = the
consensus control (runs/qwen3-4b-e2ck/...), E1 = the original E1 O students (runs/qwen3-4b/...); the teacher profiles
{teacher_dir}/{teacher}_{split}_profile.jsonl; the split's prompt file (config paths.prompts_{split}). A condition whose
glob matches nothing is reported as missing and its rows are skipped. Optional: <run_dir>/train_manifest.json next to
each response file (n_examples, n_target_tokens) and --sft-meta C=dir,K=dir (scripts/10 meta files) for n_families and
order stability per teacher; both are skipped silently when absent.

Outputs (all prefixed e2c_ so that scripts/13 pointed at the same --out keeps its own summary.md and CSVs):
e2c_gaps.csv (per condition x teacher: gap_T, CI, seed-pair q95, flags), e2c_attribution.csv (gap_C - gap_K with the
paired CI), e2c_verdict.json, e2c_runs.csv (per run: agreement with every teacher, gap, JSD, flip rate, s, n_examples),
e2c_agreement.csv / e2c_jsd.csv / e2c_consistency.csv (the e1_metrics tables with a condition column), e2c_seed_null.csv,
e2c_sft_meta.csv (when meta files exist) and e2c_summary.md. No figures.

Decision rule (tasks/e2c_plan.md §6, frozen before any E2c run; implemented in vcd.analysis.e2c_metrics):
  gap_T = seed mean over the teacher's 5 O runs of [agree_own - max_other agree_other], agreement = symmetrized
  majority-action agreement of e1_metrics.teacher_agreement (the E1 descriptive algorithm). Seed-pair null of
  (teacher, condition) = |agree_own(a) - agree_own(b)| over the 10 seed pairs, q95 (not rescaled to the seed mean).
  Family bootstrap 95% CI of gap_T: B = 2000 resamples of the split's families, fixed seed, the SAME resampled families
  for every condition (paired C - K). E2c primary on C: per teacher gap_T > q95 AND ci_lo > 0; >= 2/3 teachers PASS,
  1/3 PARTIAL, 0/3 FAIL. Attribution: gap_T(C) - gap_T(K) ci_lo > 0 for >= 2/3 teachers -> effect attributed to
  contestedness rather than to the change of training source. E1 is the reference row. The E2c-E1 gate (E1a / E1b)
  comes from scripts/13 on the same runs and is not repeated here. dev is descriptive; test is evaluated once.
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
from vcd.analysis import e2c_metrics as E
from vcd.config import resolve
from vcd.train.data import load_train_yaml

DEFAULT_GLOBS = {"C": "runs/qwen3-4b-e2c/*_O_s*/eval/{split}_responses.jsonl", "K": "runs/qwen3-4b-e2ck/*_O_s*/eval/{split}_responses.jsonl", "E1": "runs/qwen3-4b/*_O_s*/eval/{split}_responses.jsonl"}
PRESPECIFIED = "rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed"


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


def glob_files(pattern: str) -> list[Path]:
    """Files matching a glob relative to the working directory (absolute patterns are honoured)."""
    if Path(pattern).is_absolute():
        return sorted(Path("/").glob(pattern.lstrip("/")))
    return sorted(Path(".").glob(pattern))


# --------------------------------------------------------------------------- summary


def summary_md(ctx: dict) -> str:
    split, teachers, conds = ctx["split"], ctx["teachers"], ctx["conds"]
    prim, attr = ctx["primary"], ctx["attribution"]
    lines = [f"# E2c 分析（{split}，variants {', '.join(ctx['variants'])}；{ctx['freeze']}；auto-generated）", ""]
    lines += [f"**E2c primary（own > other，条件 C）：{prim['verdict']}**（{prim['n_pass']}/{prim['n_teachers']} teacher 过）；**归因（C − K）：{attr['verdict']}**（{attr['n_pass']}/{attr['n_teachers']}）。", ""]
    if split != "test":
        lines += [f"**{split} 只作描述**（tasks/e2c_plan.md §5：test 每条件只跑一次，看 test 后不改任何量）；只有 results/e2c（test）是确认性的。", ""]
    if prim.get("deviations"):
        lines += ["偏离预注册 seed 数：" + "；".join(prim["deviations"]) + "。", ""]
    lines += ["规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，"
              "与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，"
              f"`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = {ctx['n_boot']}（seed {ctx['seed']}），每个 run 重算 agreement，取 seed 均值，"
              "2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。"
              "归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。", ""]

    lines += ["## 判定表（e2c_gaps.csv）", ""]
    gaps = ctx["gaps"]
    if len(gaps):
        g = gaps.copy()
        g["CI"] = [_ci(lo, hi) for lo, hi in zip(g["ci_lo"], g["ci_hi"])]
        g["role"] = g["condition"].map({"C": "primary", "K": "reference", "E1": "reference"})
        lines += _md_table(g, ["condition", "role", "teacher", "n_seeds", "agree_own", "agree_other_max", "gap", "CI", "null_q95", "null_sd", "null_n_pairs", "exceeds_null", "ci_above_zero", "passed"])
    else:
        lines += ["(no condition has runs)", ""]
    lines += ["## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）", ""]
    att = ctx["att"]
    if len(att):
        a = att.copy()
        a["CI"] = [_ci(lo, hi) for lo, hi in zip(a["ci_lo"], a["ci_hi"])]
        lines += _md_table(a, ["teacher", "gap_C", "gap_K", "diff", "CI", "ci_above_zero"])
    else:
        lines += [f"{attr['verdict']}", ""]

    lines += ["## 输入", ""]
    inv = ctx["inventory"]
    lines += _md_table(inv, ["condition", "label", "glob", "n_files", "n_runs", "n_rows", "seeds_per_teacher", "skipped_run_ids"])
    if ctx["missing"]:
        lines += ["缺失条件（glob 无匹配，行已跳过）：" + "、".join(f"{c}（{ctx['globs'][c]}）" for c in ctx["missing"]) + "。", ""]
    if ctx["missing_profiles"]:
        lines += ["缺失 teacher profile：" + "、".join(ctx["missing_profiles"]) + "。", ""]

    lines += ["## 描述", ""]
    runs = ctx["runs"]
    if len(runs):
        lines += ["### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）", ""]
        cols = ["condition", "run_id", "answer_rate", "n_families"] + [f"agree__{t}" for t in teachers] + ["agree_own", "agree_other_max", "other_argmax", "gap", "jsd_own", "flip_rate", "mean_jsd", "s", "n_examples", "n_target_tokens"]
        lines += _md_table(runs.sort_values(["condition", "teacher", "seed"]), cols)
    null = ctx["null"]
    if len(null):
        lines += ["### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）", ""]
        lines += _md_table(null, ["condition", "teacher", "version", "n_pairs", "mean", "sd", "q95"])
    size = ctx["size"]
    if len(size):
        lines += ["### 按 teacher 的训练规模（train_manifest.json 与 --sft-meta；O seed 共享同一 prompt 集）", ""]
        lines += _md_table(size, ["condition", "teacher", "n_runs", "n_examples", "n_target_tokens", "n_families", "order_stable_rate", "n_dropped_order_unstable"])
    lines += ["注：JSD 受 teacher 校准混淆，只与 agreement 同报；flip rate 与 mean_jsd 不单独解读。", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["dev", "test"], help="prompt split; dev is descriptive, test is evaluated once (tasks/e2c_plan.md §5)")
    ap.add_argument("--c-glob", default=DEFAULT_GLOBS["C"], help="E2c-C response files ({split} is substituted)")
    ap.add_argument("--k-glob", default=DEFAULT_GLOBS["K"], help="E2c-K response files ({split} is substituted)")
    ap.add_argument("--e1-glob", default=DEFAULT_GLOBS["E1"], help="E1 O-student response files, the reference row ({split} is substituted)")
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl; default: config paths.teacher_dir")
    ap.add_argument("--teacher-files", default=None, help="explicit profiles 'gpt4o=path,claude46=path' (overrides --teacher-dir/--teachers)")
    ap.add_argument("--teachers", default=None, help="comma list; default: config teachers")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--variants", default=None, help="comma list of framings (default: config data.variants = T1,T3,T5,T6)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default=None, help="default: results/e2c_dev for dev, results/e2c for test")
    ap.add_argument("--n-boot", type=int, default=E.N_BOOT, help=f"family bootstrap resamples (pre-registered {E.N_BOOT})")
    ap.add_argument("--seed", type=int, default=E.BOOT_SEED, help="seed of the shared family resampling")
    ap.add_argument("--sft-meta", default=None, help="optional 'C=data/sft_e2c,K=data/sft_e2ck[,E1=data/sft]': scripts/10 meta files for n_families / order stability per teacher")
    ap.add_argument("--frozen-commit", default=None, help="hash of the commit that froze tasks/e2c_plan.md §6 (printed in the summary header)")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    teacher_files = dict(kv.split("=", 1) for kv in args.teacher_files.split(",")) if args.teacher_files else None
    teachers = list(teacher_files) if teacher_files else (args.teachers.split(",") if args.teachers else list(cfg["teachers"]))
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    families = sorted({p.family_id for p in prompts.values()})
    out = Path(args.out) if args.out else Path("results/e2c" if args.split == "test" else f"results/e2c_{args.split}")
    freeze = f"{PRESPECIFIED}; frozen at commit {args.frozen_commit}" if args.frozen_commit else f"{PRESPECIFIED}; freeze commit not given (tasks/e2c_plan.md §9)"

    teacher_dir = Path(args.teacher_dir) if args.teacher_dir else cfg["paths"]["teacher_dir"]
    tfiles = {t: Path(teacher_files[t]) for t in teachers} if teacher_files else {t: teacher_dir / f"{t}_{args.split}_profile.jsonl" for t in teachers}
    missing_profiles = [str(p) for p in tfiles.values() if not p.exists()]
    if missing_profiles:
        print("warning: missing teacher profiles:", ", ".join(missing_profiles), file=sys.stderr)
    teacher_rows = M.load_responses([p for p in tfiles.values() if p.exists()], pid)
    sym_t = M.sym_table(M.frame_table(teacher_rows, prompts)) if teacher_rows else pd.DataFrame(columns=["teacher", "family_id", "variant", "p_o1", "p_o2", "p_sym", "order_gap"])
    if sym_t.empty:
        raise SystemExit("no teacher profile rows; pass --teacher-dir or --teacher-files")

    W = E.bootstrap_weights(len(families), args.n_boot, args.seed)  # one resampling for every condition (paired C - K)
    globs = {"C": args.c_glob.format(split=args.split), "K": args.k_glob.format(split=args.split), "E1": args.e1_glob.format(split=args.split)}
    results: dict[str, E.ConditionResult] = {}
    files_by: dict[str, list[Path]] = {}
    missing: list[str] = []
    for cond in E.CONDITIONS:
        files = glob_files(globs[cond])
        files_by[cond] = files
        if not files:
            missing.append(cond)
            print(f"{cond}: no files match {globs[cond]!r}; condition skipped", file=sys.stderr)
            continue
        rows = M.load_responses(files, pid)
        res = E.analyze_condition(cond, rows, prompts, sym_t, teachers, variants, families, W)
        if res.skipped:
            print(f"warning: {cond}: skipping {len(res.skipped)} run id(s) that do not match the protocol pattern: {res.skipped}", file=sys.stderr)
        results[cond] = res
        print(f"{cond}: {len(files)} files, {len(rows)} rows, {len(res.run_tab)} runs; gap rows {int((res.gaps['n_seeds'] > 0).sum())}")
    if not results:
        print("warning: no condition has response files; writing an empty summary", file=sys.stderr)

    out.mkdir(parents=True, exist_ok=True)
    gaps = pd.concat([r.gaps.assign(condition=c) for c, r in results.items()], ignore_index=True) if results else pd.DataFrame(columns=["condition", *E.GAP_COLS])
    gaps = gaps[["condition", *E.GAP_COLS]] if len(gaps) else gaps
    gaps.to_csv(out / "e2c_gaps.csv", index=False)
    primary = E.primary_verdict(results["C"].gaps if "C" in results else None, teachers)
    has_c, has_k = "C" in results, "K" in results
    att = E.attribution_table(results["C"].gaps if has_c else None, results["K"].gaps if has_k else None, results["C"].boot if has_c else {}, results["K"].boot if has_k else {}, teachers) if (has_c and has_k) else pd.DataFrame(columns=E.ATTR_COLS)
    att.to_csv(out / "e2c_attribution.csv", index=False)
    attribution = E.attribution_verdict(att, teachers, has_c, has_k)
    reference = {c: {"n_pass": int(results[c].gaps["passed"].sum()), "n_teachers": len(teachers)} for c in ("K", "E1") if c in results}

    # descriptive tables with a condition column
    def _cat(attr: str, cols: list[str]) -> pd.DataFrame:
        parts = [getattr(r, attr).assign(condition=c) for c, r in results.items() if len(getattr(r, attr))]
        df = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=["condition", *cols])
        return df[["condition", *[c for c in cols if c in df.columns]]]

    _cat("agreement", ["run_id", "teacher", "agreement", "n_ties", "n_cells"]).to_csv(out / "e2c_agreement.csv", index=False)
    _cat("jsd", ["run_id", "teacher", "jsd", "n_cells"]).to_csv(out / "e2c_jsd.csv", index=False)
    _cat("consistency", ["teacher", "n_families", "share_uncertain", "flip_rate", "family_flip_share", "mean_jsd"]).to_csv(out / "e2c_consistency.csv", index=False)
    null = _cat("null", E.NULL_COLS)
    null.to_csv(out / "e2c_seed_null.csv", index=False)
    runs_parts = [E.run_descriptives(r) for r in results.values()]
    runs = pd.concat(runs_parts, ignore_index=True) if runs_parts else pd.DataFrame(columns=["condition", *E.RUN_COLS])
    man_parts = [E.load_manifests(files_by[c]).assign(condition=c) for c in results]
    man = pd.concat(man_parts, ignore_index=True) if man_parts else pd.DataFrame(columns=["condition", *E.MANIFEST_COLS])
    if len(runs):
        if len(man):
            runs = runs.merge(man[["condition", "run_id", "n_examples", "n_target_tokens"]], on=["condition", "run_id"], how="left")
        else:
            runs["n_examples"], runs["n_target_tokens"] = np.nan, np.nan
    runs.to_csv(out / "e2c_runs.csv", index=False)
    meta_parts = []
    if args.sft_meta:
        for kv in args.sft_meta.split(","):
            cond, d = kv.split("=", 1)
            if Path(d).exists():
                m = E.load_sft_meta(d, teachers)
                if len(m):
                    meta_parts.append(m.assign(condition=cond.strip()))
            else:
                print(f"warning: --sft-meta {cond}={d}: directory missing, skipped", file=sys.stderr)
    meta = pd.concat(meta_parts, ignore_index=True) if meta_parts else pd.DataFrame(columns=["condition", *E.META_COLS])
    if len(meta):
        meta.to_csv(out / "e2c_sft_meta.csv", index=False)
    def _count(series: pd.Series):
        """Mean of a count column over the seeds (identical across O seeds), printed as an int when it is one."""
        v = float(pd.to_numeric(series, errors="coerce").mean()) if len(series) else np.nan
        return int(round(v)) if np.isfinite(v) and abs(v - round(v)) < 1e-9 else v

    size_rows = []
    for cond, r in results.items():
        rt = runs[(runs["condition"] == cond) & (runs["version"] == E.GAP_VERSION)] if len(runs) else runs
        mt = meta[meta["condition"] == cond] if len(meta) else meta
        for t in teachers:
            g = rt[rt["teacher"] == t] if len(rt) else rt
            mg = mt[mt["teacher"] == t] if len(mt) else mt
            size_rows.append(dict(condition=cond, teacher=t, n_runs=int(len(g)), n_examples=_count(g["n_examples"]) if len(g) and "n_examples" in g else np.nan,
                                  n_target_tokens=_count(g["n_target_tokens"]) if len(g) and "n_target_tokens" in g else np.nan,
                                  n_families=_count(mg["n_families"]) if len(mg) else np.nan, order_stable_rate=float(mg["order_stable_rate"].mean()) if len(mg) else np.nan,
                                  n_dropped_order_unstable=_count(mg["n_dropped_order_unstable"]) if len(mg) else np.nan))
    size = pd.DataFrame(size_rows, columns=["condition", "teacher", "n_runs", "n_examples", "n_target_tokens", "n_families", "order_stable_rate", "n_dropped_order_unstable"], dtype=object)  # ints stay ints next to NaN

    inv_rows = []
    for cond in E.CONDITIONS:
        r = results.get(cond)
        per_t = ""
        if r is not None and len(r.run_tab):
            o = r.run_tab[r.run_tab["version"] == E.GAP_VERSION]
            per_t = "; ".join(f"{t}: {','.join(str(int(s)) for s in sorted(o[o['teacher'] == t]['seed']))}" for t in teachers if (o["teacher"] == t).any())
        inv_rows.append(dict(condition=cond, label=E.CONDITION_LABELS[cond], glob=globs[cond], n_files=len(files_by.get(cond, [])), n_runs=len(r.run_tab) if r is not None else 0,
                             n_rows=r.n_rows if r is not None else 0, seeds_per_teacher=per_t or "(missing)", skipped_run_ids=", ".join(r.skipped) if r is not None and r.skipped else ""))
    inventory = pd.DataFrame(inv_rows)

    verdict = {"split": args.split, "freeze": freeze, "rule": E.RULE, "primary": primary, "attribution": attribution, "reference_rows_under_the_same_rule": reference,
               "teachers": teachers, "variants": variants, "n_boot": args.n_boot, "seed": args.seed, "n_families": len(families), "globs": globs,
               "n_files": {c: len(f) for c, f in files_by.items()}, "missing_conditions": missing, "missing_profiles": missing_profiles,
               "gaps": gaps.to_dict(orient="records"), "attribution_table": att.to_dict(orient="records"), "descriptive_only": args.split != "test"}
    (out / "e2c_verdict.json").write_text(json.dumps(verdict, indent=2, default=_dump, ensure_ascii=False), encoding="utf-8")
    ctx = dict(split=args.split, variants=variants, teachers=teachers, conds=list(results), primary=primary, attribution=attribution, gaps=gaps, att=att, inventory=inventory, missing=missing,
               globs=globs, missing_profiles=missing_profiles, runs=runs, null=null, size=size, n_boot=args.n_boot, seed=args.seed, freeze=freeze)
    (out / "e2c_summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote {len(list(out.glob('e2c_*.csv')))} CSVs + e2c_verdict.json + e2c_summary.md to {out}")
    print((out / "e2c_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
