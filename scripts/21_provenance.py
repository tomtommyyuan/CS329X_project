"""Step 21: E7 black-box provenance detector (tasks/e7_plan.md §2-§4) -> {out}/e7_* (CSVs, calibration.json, e7_verdict.json, e7_summary.md).

Examples
  python scripts/21_provenance.py --split dev                                   # calibrate tau on dev -> results/e7_dev/calibration.json (+ dev descriptives)
  python scripts/21_provenance.py --split test --calibration results/e7_dev/calibration.json --frozen-commit <hash>   # once, after the freeze
  # synthetic tree (tests): explicit namespaces / teachers / prompts / base run
  python scripts/21_provenance.py --split dev --runs-dir /tmp/runs --namespaces qwen3-4b,qwen3-4b-e2c,qwen3-4b-e2ck --descriptive-namespaces none \
      --teacher-dir /tmp/teachers --teachers alpha,beta,gamma --prompts /tmp/prompts.jsonl --base-run /tmp/runs/qwen3-4b/base_B_s0 --out /tmp/e7 --n-rep 20 --n-perm 200

Inputs: runs/{namespace}/{run}/eval/{split}_responses.jsonl for every namespace (TeacherResponse rows; the run id inside a
row may carry another namespace's prefix, so teacher / version / seed come from the directory name and the GRID label from
the namespace: qwen3-4b -> E1, qwen3-4b-paired -> E3, qwen3-4b-e2c -> E2c_C, qwen3-4b-e2ck -> K, qwen3-4b-e2ckn -> K_n,
qwen3-4b-e2cnf -> Cnf, qwen3-4b-e2c-paired -> E3c; override with --grid-map ns=GRID,...), {base_run}/eval/{split}_responses.jsonl
(S_0: a suspect like any other run under the gated readout AND, for the base-known detector, the reference profile; version-B
copies inside the namespaces are skipped), {teacher_dir}/{teacher}_{split}_profile.jsonl and the split's prompt file.
Ground truth: O / F / C runs of E1, E3, E2c_C, Cnf, E3c -> their teacher; K, K_n (consensus-trained), R and S_0 -> "none".

Outputs: e7_runs.csv (per run: grid, truth, a_t per teacher, both scores, decisions, margins), e7_metrics.csv (main and
descriptive tables: per grid x subset x detector x teacher recall with Wilson CI, macro recall, open-set FPR, AUROC, chance,
permutation p), e7_probe_curve.csv, e7_sampled.csv, e7_loso.csv, e7_logo.csv, e7_verdict.json, e7_summary.md and, on dev,
calibration.json (tau per detector configuration). --split test REQUIRES --calibration and never recalibrates. No figures.

Rule (tasks/e7_plan.md §3-§4, frozen before any provenance result; implemented in vcd.analysis.provenance): see the module
docstring and RULE. dev = calibration split (descriptive); test is evaluated once with the dev calibration.
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
from vcd.analysis import provenance as PV
from vcd.config import resolve
from vcd.train.data import load_train_yaml

PRESPECIFIED = "E7 detector, tau rule, metrics and verdict pre-registered in tasks/e7_plan.md §3-§4 before any provenance result"


def freeze_label(frozen_commit: Optional[str]) -> str:
    return f"{PRESPECIFIED}; frozen at commit {frozen_commit}" if frozen_commit else f"{PRESPECIFIED}; not yet frozen (freeze commit pending)"


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
    if isinstance(x, (Path,)):
        return str(x)
    return str(x)


def _with_ci(df: pd.DataFrame) -> pd.DataFrame:
    d = df.copy()
    if "wilson_lo" in d:
        d["CI"] = [_ci(lo, hi) for lo, hi in zip(d["wilson_lo"], d["wilson_hi"])]
    return d


def _agg_view(df: pd.DataFrame, value: str) -> pd.Series:
    return pd.Series([f"{_fmt(m)} [{_fmt(lo)}, {_fmt(hi)}]" for m, lo, hi in zip(df[f"{value}_mean"], df[f"{value}_lo"], df[f"{value}_hi"])], index=df.index)


def _pivot_lines(df: pd.DataFrame, index: list[str], column: str, text: pd.Series) -> list[str]:
    """Markdown table with one row per `index` tuple and one column per value of `column`, cells = the preformatted `text`."""
    if df.empty:
        return ["(empty)", ""]
    d = df.assign(_txt=text).pivot_table(index=index, columns=column, values="_txt", aggfunc="first", sort=False)
    d.columns = [str(c) for c in d.columns]
    return _md_table(d.reset_index(), [*index, *d.columns])


# --------------------------------------------------------------------------- summary


def summary_md(ctx: dict) -> str:
    res: PV.E7Result = ctx["res"]
    split, teachers = ctx["split"], ctx["teachers"]
    v = res.verdict
    lines = [f"# E7 黑盒溯源（{split}，variants {', '.join(ctx['variants'])}；{ctx['freeze']}；auto-generated）", ""]
    fpr_txt = f"开集 FPR {_fmt(v['fpr'])}（{'≤' if v.get('fpr_ok') else '>'} 10%）" if not PV._nan(v.get("fpr")) else "开集 FPR nan"
    lines += [f"**主判定（E2c-C 的 O 学生，基座已知，字母概率 readout，全部探针）：{v['verdict']}**（{v['n_pass']}/{v['n_teachers']} 个 teacher 的召回 Wilson 下界 > 1/3：{', '.join(v['passing']) or '无'}；{fpr_txt}；τ = {_fmt(v.get('tau'))}）。", ""]
    if split != "test":
        lines += [f"**{split} = 标定 split，以下全部只作描述**（tasks/e7_plan.md §4：阈值只在 dev 定，test 冻结后只跑一次，`--calibration` 复用本次写出的 calibration.json）。", ""]
    elif v.get("calibration_reused"):
        lines += ["**test：τ 全部来自 dev 的 calibration.json，本次没有任何标定**。", ""]
    lines += ["规则（tasks/e7_plan.md §3–4 原文，`vcd.analysis.provenance`）：a_t = run 与 teacher t 的 symmetrized 多数行动一致率（`e1_metrics.teacher_agreement`，p_sym = 0.5 的 cell 不计）；"
              "基座已知 s_t = a_t − a_t(S_0)，基座未知 s_t = a_t − mean_t' a_t'；t* = argmax s_t，margin = s_t* − 第二大，margin > τ 判为 t*，否则不判定；"
              "τ = 使 dev 负例（K、K_n、R、S_0）被判为任一 teacher 的比例 ≤ 5% 的最小值（负例 < 20 时 τ = 0），每个检测器配置（变体 × readout × 探针子集 × 预算）各一个，test 原样复用；"
              "召回 Wilson 95% CI（不判定计错），macro 召回，开集 FPR，一对多 AUROC（以 s_t 为分数，负类含 none），随机参照 (1/3)(1 − 不判定率)，teacher 标签在该网格可判定 run 间置换 10,000 次的 p（seed 为近复本，p 只作描述）。"
              f"主判定：E2c-C 的 15 个 O 学生，基座已知，字母概率，全部探针：召回 Wilson 下界 > 1/3 的 teacher ≥ 2/3 → 溯源可行（有条件），1/3 → 部分，0/3 → 不可行，并报开集 FPR 是否 ≤ 10%。", ""]

    cal = res.calibration
    lines += [f"## 标定（{'calibration.json，本次写出' if not v.get('calibration_reused') else '复用 dev 的 calibration.json'}）", ""]
    lines += [f"负例 {cal['negatives']['n']} 个（{', '.join(cal['negatives']['grids'])}）；基座参照 = {cal['base_reference']}（{cal['base_reference_cells']} 个有效 cell / {cal['n_cells']}）；teacher 分歧 cell {cal['disagreement_cells']} / {cal['n_cells']}；"
              f"family {cal['n_families']}；重复 {cal['n_rep']}；seed {cal['seed']}。", ""]
    ct = pd.DataFrame([{"configuration": k} | dict(v_) for k, v_ in cal["tau"].items()])
    lines += _md_table(ct, ["configuration", "tau", "n_neg", "n_margins", "n_attributed", "fpr_at_tau", "fallback", "note"])

    met = res.metrics
    main = met[(met["table"] == "main") & (met["subset"] == "all") & (met["tau_policy"] == "calibrated")] if len(met) else met
    for det in PV.DETECTORS:
        lines += [f"## 主表：{'基座已知' if det == 'base_known' else '基座未知'}，字母概率 readout，全部 cell（e7_metrics.csv，table = main）", ""]
        d = _with_ci(main[main["detector"] == det])
        lines += _md_table(d, ["grid", "version", "teacher", "n", "n_correct", "recall", "CI", "unattributed_rate", "auroc", "macro_recall", "chance", "perm_p", "fpr", "n_neg", "tau"])
    dis = met[(met["table"] == "main") & (met["subset"] == "disagreement") & (met["teacher"] != PV.NONE)] if len(met) else met
    lines += [f"## 分歧探针（三家多数行动不全同的 cell，{cal['disagreement_cells']} / {cal['n_cells']}；τ = 该配置自标定（calibrated）；全 cell 的 τ 作灵敏度（fixed_all_cells，只列 macro 行））", ""]
    lines += _md_table(_with_ci(dis[dis["tau_policy"] == "calibrated"]), ["detector", "tau", "grid", "version", "teacher", "n", "recall", "CI", "unattributed_rate", "auroc", "macro_recall", "chance", "perm_p", "fpr"])
    lines += _md_table(dis[(dis["tau_policy"] == "fixed_all_cells") & (dis["teacher"] == "macro")], ["detector", "tau_policy", "tau", "grid", "version", "n", "macro_recall", "unattributed_rate", "chance", "perm_p", "fpr"])

    lines += ["## 采样 readout：n = 1 / 3 / 10 个答案取多数（每 cell 两序各抽；均值 [2.5, 97.5] 分位，e7_sampled.csv）", ""]
    sm = res.sampled
    if len(sm):
        mac = sm[sm["teacher"] == "macro"]
        lines += ["macro 召回（行 = 检测器 × 网格，列 = n）：", ""]
        lines += _pivot_lines(mac, ["detector", "grid", "version"], "n_draws", _agg_view(mac, "macro_recall"))
        prim = sm[(sm["grid"] == PV.PRIMARY["grid"]) & (sm["version"] == PV.PRIMARY["version"]) & sm["teacher"].isin(teachers)]
        lines += [f"{PV.PRIMARY['grid']} {PV.PRIMARY['version']} 学生的每 teacher 召回与 AUROC：", ""]
        lines += _pivot_lines(prim, ["detector", "teacher"], "n_draws", _agg_view(prim, "recall") + " / AUROC " + prim["auroc_mean"].map(_fmt))
        one = mac[(mac["grid"] == PV.PRIMARY["grid"]) & (mac["version"] == PV.PRIMARY["version"])]
        lines += ["开集 FPR（各重复均值）与 τ：", ""]
        lines += _pivot_lines(one, ["detector"], "n_draws", "FPR " + _agg_view(one, "fpr") + "; τ " + one["tau"].map(_fmt))
    else:
        lines += ["(empty)", ""]

    lines += ["## 探针预算曲线：随机 k 个 family × 重复（基座参照取同一批 family；均值 [2.5, 97.5]，e7_probe_curve.csv）", ""]
    pc = res.probe_curve
    if len(pc):
        mac = pc[pc["teacher"] == "macro"]
        lines += ["macro 召回（行 = 检测器 × τ 策略 × 网格，列 = family 预算 k；calibrated = 该预算自标定的 τ_k，fixed_all_cells = 全 cell 的 τ）：", ""]
        lines += _pivot_lines(mac, ["detector", "tau_policy", "grid", "version"], "budget", _agg_view(mac, "macro_recall"))
        one = mac[(mac["grid"] == PV.PRIMARY["grid"]) & (mac["version"] == PV.PRIMARY["version"])]
        lines += ["开集 FPR（各重复均值）与 τ：", ""]
        lines += _pivot_lines(one, ["detector", "tau_policy"], "budget", "FPR " + _agg_view(one, "fpr") + "; τ " + one["tau"].map(_fmt))
        prim = pc[(pc["grid"] == PV.PRIMARY["grid"]) & (pc["version"] == PV.PRIMARY["version"]) & pc["teacher"].isin(teachers)]
        lines += [f"{PV.PRIMARY['grid']} {PV.PRIMARY['version']} 学生的每 teacher 召回：", ""]
        lines += _pivot_lines(prim, ["detector", "tau_policy", "teacher"], "budget", _agg_view(prim, "recall"))
    else:
        lines += ["(empty)", ""]

    lines += ["## leave-one-style-out：τ 只用 O / R / B 的负例标定（与主 τ 相同），认 E3 / E3c 的 F / C 学生（e7_loso.csv）", ""]
    lines += _md_table(_with_ci(res.loso), ["detector", "tau", "grid", "version", "teacher", "n", "recall", "CI", "unattributed_rate", "auroc", "macro_recall", "chance", "perm_p", "fpr"])
    lines += [f"## leave-one-grid-out：τ 在网格 {', '.join(cal['logo_grids'])} 上标定（E1 的学生一并视为应拒判的总体），用到其余网格（e7_logo.csv）", ""]
    lines += _md_table(_with_ci(res.logo[res.logo["teacher"] != PV.NONE]), ["detector", "tau", "grid", "version", "teacher", "n", "recall", "CI", "unattributed_rate", "auroc", "macro_recall", "chance", "perm_p", "fpr"])

    lines += ["## 描述：负例按类型的误判率（K / K_n / R / S_0）；归档 run；T0", ""]
    negs = met[(met["teacher"] == PV.NONE) & (met["subset"] == "all") & (met["tau_policy"] == "calibrated")] if len(met) else met
    lines += _md_table(negs, ["table", "detector", "grid", "version", "n", "n_neg_attributed", "fpr", "tau"])
    desc = met[(met["table"] == "descriptive") & (met["subset"] == "all") & (met["tau_policy"] == "calibrated")] if len(met) else met
    if len(desc):
        lines += ["归档配方（只有 dev readout；不进标定）：", ""]
        lines += _md_table(_with_ci(desc), ["detector", "grid", "version", "teacher", "n", "recall", "CI", "auroc", "macro_recall", "fpr"])
    runs = res.runs
    t0_cols = [c for c in runs.columns if c.startswith("a_T0__")]
    if t0_cols:
        g = runs.groupby(["grid", "version"], sort=False)[t0_cols + [f"a__{t}" for t in teachers]].mean().reset_index()
        lines += ["T0（训练未见的无框架变体，不进分数）：各网格 run 均值的 a_t；对照 seen variants 的 a_t：", ""]
        lines += _md_table(g, ["grid", "version", *t0_cols, *[f"a__{t}" for t in teachers]])

    lines += ["## 每 run（e7_runs.csv 节选：grid、真值、a_t、两种分数的判定）", ""]
    cols = ["run_id", "grid", "version", "truth", "n_cells_valid", *[f"a__{t}" for t in teachers], "decision_known", "margin_known", "decision_unknown", "margin_unknown"]
    lines += _md_table(runs[runs["role"] == "core"].sort_values(["grid", "version", "teacher", "seed"], kind="stable"), cols)

    lines += ["## 输入", ""]
    inv = runs.groupby(["namespace", "grid", "role", "version"], sort=False).agg(n_runs=("run_id", "size"), truths=("truth", lambda s: ",".join(sorted(set(s))))).reset_index()
    lines += _md_table(inv, ["namespace", "grid", "role", "version", "n_runs", "truths"])
    if ctx["notes"]:
        lines += ["说明：", ""] + [f"- {n}" for n in ctx["notes"]] + [""]
    lines += ["## 预注册之外的实现决定（披露）", ""]
    lines += ["- 基座已知的参照 a_t(S_0) 默认用 S_0 的**未门控**两字母概率（`sym_table(mass_gate=False)`，与 E2 的协变量 r_0 同一对象）：门控 readout 下未训练基座只有约 1/6 的 cell 有答案；S_0 作为**被测**负例时仍用门控 readout。`--base-reference gated` 可切换。",
              "- τ 按检测器配置各标一个（变体 × readout × 探针子集 × 预算），全部写入 calibration.json 并在 test 复用；分歧探针与预算曲线同时报自标定 τ 与全 cell τ（tau_policy）。",
              "- 采样 readout 只作用于被测模型；teacher 参照与基座参照保持概率 readout。τ 在 200 次重复的负例 margin 合并后标定。",
              "- leave-one-grid-out 的标定总体 = E1 网格的全部 run（15 个 O 学生一并视为应拒判）+ K / K_n 负例；评估其余网格。",
              "- 置换 p 以 run 为单位（同 teacher 的 seed 为近复本，只作描述）；采样与预算曲线各重复内用 --n-perm-rep 次置换后取均值。",
              "- 不足两个有限分数的 run 记为不判定（margin nan）；AUROC 的负类 = 该网格其余 run + 全部 none 负例。", ""]
    return "\n".join(lines)


# --------------------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", required=True, choices=["dev", "test"], help="dev calibrates tau and writes calibration.json; test requires --calibration and never recalibrates")
    ap.add_argument("--runs-dir", default=None, help="default: config paths.runs_dir")
    ap.add_argument("--namespaces", default=",".join(PV.CORE_NAMESPACES), help="comma list of run namespaces under --runs-dir (core: enter calibration and the inferential tables)")
    ap.add_argument("--descriptive-namespaces", default=",".join(PV.ARCHIVED_NAMESPACES), help="comma list of namespaces scored but kept out of every calibration ('none' to disable); missing dirs are skipped")
    ap.add_argument("--grid-map", default=None, help="'ns=GRID,...' overrides / extends the default namespace -> grid map")
    ap.add_argument("--negative-grids", default=",".join(PV.NEGATIVE_GRIDS), help="grids whose O runs have no specific teacher (truth none)")
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl; default: config paths.teacher_dir")
    ap.add_argument("--teachers", default=None, help="comma list of candidate teachers; default: config teachers")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--variants", default=None, help="comma list of scored framings (default: config data.variants = T1,T3,T5,T6; T0 is reported descriptively)")
    ap.add_argument("--base-run", default="runs/qwen3-4b/base_B_s0", help="untrained base S_0 run dir with eval/{split}_responses.jsonl")
    ap.add_argument("--base-reference", default="prior", choices=["prior", "gated"], help="base-known reference profile: ungated two-letter prior (default) or the gated readout")
    ap.add_argument("--calibration", default=None, help="calibration.json of the dev run; REQUIRED for --split test, optional on dev (then reused, not rewritten)")
    ap.add_argument("--n-rep", type=int, default=PV.N_REP, help="repetitions of the sampled readout and of each probe budget")
    ap.add_argument("--n-perm", type=int, default=10_000, help="teacher-label permutations for the probability-readout rows")
    ap.add_argument("--n-perm-rep", type=int, default=1000, help="permutations per repetition in the sampled / probe-curve rows")
    ap.add_argument("--budgets", default=",".join(str(b) for b in PV.BUDGETS), help="probe budgets in families (values >= the split's family count collapse to 'all')")
    ap.add_argument("--sample-n", default=",".join(str(n) for n in PV.SAMPLE_N), help="answers drawn per order in the sampled readout")
    ap.add_argument("--logo-grids", default=",".join(PV.LOGO_GRIDS), help="grids forming the leave-one-grid-out calibration population")
    ap.add_argument("--fpr-max", type=float, default=PV.FPR_MAX, help="calibration target: share of negatives attributed to any teacher")
    ap.add_argument("--n-neg-min", type=int, default=PV.N_NEG_MIN, help="fewer negatives than this -> tau = 0 fallback")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default=None, help="default results/e7_dev for dev, results/e7 for test")
    ap.add_argument("--frozen-commit", default=None, help="hash of the commit that froze the plan and the dev calibration (printed in the summary header)")
    args = ap.parse_args()

    if args.split == "test" and not args.calibration:
        print("error: --split test requires --calibration <dev calibration.json>; refusing to calibrate tau on the test split (tasks/e7_plan.md §3)", file=sys.stderr)
        raise SystemExit(2)
    calibration = None
    if args.calibration:
        calibration = json.loads(Path(args.calibration).read_text(encoding="utf-8"))
        if "tau" not in calibration:
            raise SystemExit(f"error: {args.calibration} is not an E7 calibration file (no 'tau' section)")

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    teachers = args.teachers.split(",") if args.teachers else list(cfg["teachers"])
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    runs_dir = Path(args.runs_dir) if args.runs_dir else Path(cfg["paths"]["runs_dir"])
    teacher_dir = Path(args.teacher_dir) if args.teacher_dir else Path(cfg["paths"]["teacher_dir"])
    out = Path(args.out) if args.out else Path("results/e7" if args.split == "test" else f"results/e7_{args.split}")
    grid_map = PV.parse_grid_map(args.grid_map)
    negative_grids = [g for g in args.negative_grids.split(",") if g]
    core = [n for n in args.namespaces.split(",") if n]
    desc = [] if args.descriptive_namespaces.strip().lower() in ("", "none") else [n for n in args.descriptive_namespaces.split(",") if n and (runs_dir / n).exists()]
    roles = {n: "core" for n in core} | {n: "descriptive" for n in desc if n not in core}

    student_rows, inventory, notes = PV.load_student_runs(runs_dir, args.split, core + [n for n in desc if n not in core], grid_map, pid, roles, negative_grids)
    if inventory.empty:
        raise SystemExit(f"no {args.split} response files under {runs_dir} for namespaces {core}")
    base_rows, base_row = PV.load_base(args.base_run, args.split, pid, grid_map)
    inventory = pd.concat([inventory, pd.DataFrame([base_row])], ignore_index=True)
    teacher_rows = PV.load_teachers(teacher_dir, args.split, teachers, pid)
    print(f"{args.split}: {len(inventory)} runs ({int((inventory['role'] == 'core').sum())} core) from {len(core) + len(desc)} namespaces, {len(student_rows) + len(base_rows)} rows; teachers {teachers}")
    for n in notes:
        print("note:", n, file=sys.stderr)

    world = PV.build_world(student_rows, base_rows, teacher_rows, prompts, inventory, teachers, variants, base_reference=args.base_reference)
    print(f"cells {world.S.cells.shape[1]} ({len(world.families)} families x {len(world.variants)} variants); disagreement cells {int(world.disagree.sum())}; base reference '{world.base_ref_label}' with {world.base_ref_cells} valid cells")
    res = PV.analyze(world, calibration=calibration, n_rep=args.n_rep, n_perm=args.n_perm, n_perm_rep=args.n_perm_rep, seed=args.seed, budgets=[int(b) for b in args.budgets.split(",") if b],
                     sample_n=[int(n) for n in args.sample_n.split(",") if n], fpr_max=args.fpr_max, n_min=args.n_neg_min, logo_grids=[g for g in args.logo_grids.split(",") if g], split=args.split)
    notes += res.notes

    out.mkdir(parents=True, exist_ok=True)
    res.runs.to_csv(out / "e7_runs.csv", index=False)
    res.metrics.to_csv(out / "e7_metrics.csv", index=False)
    res.probe_curve.to_csv(out / "e7_probe_curve.csv", index=False)
    res.sampled.to_csv(out / "e7_sampled.csv", index=False)
    res.loso.to_csv(out / "e7_loso.csv", index=False)
    res.logo.to_csv(out / "e7_logo.csv", index=False)
    freeze = freeze_label(args.frozen_commit)
    cal_out = dict(res.calibration) | {"frozen": freeze, "runs_dir": str(runs_dir), "namespaces": core, "descriptive_namespaces": desc, "grid_map": {n: grid_map[n] for n in core + desc}}
    if calibration is None:
        (out / "calibration.json").write_text(json.dumps(cal_out, indent=2, default=_dump, ensure_ascii=False), encoding="utf-8")
    else:
        cal_out["calibration_file"] = str(args.calibration)
        (out / "calibration_used.json").write_text(json.dumps(cal_out, indent=2, default=_dump, ensure_ascii=False), encoding="utf-8")
    verdict = dict(res.verdict) | {"split": args.split, "frozen": freeze, "confirmatory": args.split == "test", "calibration_file": args.calibration, "seed": args.seed, "n_rep": args.n_rep,
                                   "n_perm": args.n_perm, "teachers": teachers, "variants": variants, "n_runs": int(len(res.runs)), "n_negatives": res.calibration["negatives"]["n"], "notes": notes}
    (out / "e7_verdict.json").write_text(json.dumps(verdict, indent=2, default=_dump, ensure_ascii=False), encoding="utf-8")
    ctx = dict(res=res, split=args.split, teachers=teachers, variants=variants, freeze=freeze, notes=notes)
    (out / "e7_summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote {len(list(out.glob('e7_*.csv')))} CSVs + e7_verdict.json + {'calibration.json' if calibration is None else 'calibration_used.json'} + e7_summary.md to {out}")
    print((out / "e7_summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
