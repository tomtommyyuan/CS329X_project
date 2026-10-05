"""Step 15: E3 tables (form effects of the O / F / C rewrites on the paired students) -> results/e3_{split}/ (CSVs + summary.md).

Examples
  python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev --out results/e3_dev
  python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split test --out results/e3 --frozen-commit <hash>   # once, after the dev freeze line
  # smoke on the E1 namespace (O and R only: every F / C line is pending, the O-vs-O seed-pair null is real)
  python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b --split dev --sft-dir /tmp/sft_paired --out /tmp/e3_smoke --n-boot 500 --n-perm 500
  # synthetic tree (tests): explicit teachers / prompts / base run, no tokenizer
  python scripts/15_e3_analysis.py --runs-dir /tmp/runs --student qwen3-4b-paired --split dev --teacher-dir /tmp/teachers --teachers alpha,beta,gamma \
      --prompts /tmp/prompts.jsonl --base-run /tmp/runs/qwen3-4b/base_B_s0 --sft-dir /tmp/sft --rewrites-dir /tmp/rewrites --tokenizer none --out /tmp/e3

Inputs: runs/{student}/{teacher}_{O|F|C}_s{seed}/eval/{split}_responses.jsonl (TeacherResponse rows, teacher = run id),
{base_run}/eval/{split}_responses.jsonl (untrained base: its ungated prior profile r_0 is the covariate of the partial delta_rho),
{teacher_dir}/{teacher}_{split}_profile.jsonl, {sft_dir}/{teacher}_{O|F|C}_s{seed}.jsonl (the ACTUAL paired training files) and
{rewrites_dir}/{teacher}/rewrites.jsonl (per-item judge checks). Everything degrades to "pending" when a version is missing.

Outputs (docs/05 §6b): disagreement.csv (+ disagreement_by_seed.csv, disagreement_excess.csv), consistency_delta.csv (+ _by_seed), drift.csv (+ _by_seed),
homogenization.csv (+ homogenization_cells.csv), inheritance_by_form.csv (+ inheritance_by_form_runs.csv, _by_seed), joint_D_by_version.csv
(+ joint_D_by_version.json), suggestibility_by_version.csv (+ suggestibility_version_diffs.csv), content_check.csv, register_check.csv
(+ register_separation.csv), seed_pair_null.csv (+ seed_pair_null_summary.csv), run_scalars.csv, run_inventory.csv, verdicts.csv / .json, summary.md.

Decision rule (docs/03 E3 row, pre-specified before any F / C run was trained; tasks/e3_plan.md §3):
  an effect counts if in >= 2/3 of the 3 teachers the seed-paired statistic (seed mean of S_{T,V,s} - S_{T,O,s}, or the F-vs-C
  disagreement excess over the teacher's own O-O level) exceeds the 95th percentile of the seed-pair null OF THAT STATISTIC
  (single O-O seed-pair differences pooled over teachers, scaled to the seed mean: SD / sqrt(n_seeds), t reference with
  df = sum (n_O - 1)) and the direction is the same across those teachers. "no effect" needs a TOST (every teacher's
  family-bootstrap CI inside +/- 1 null SD for >= 2/3 teachers), otherwise "inconclusive". Fewer than 3 teachers with paired
  runs -> pending. Primary rows: disagreement F vs C, consistency change (flip, JSD), excess teacher drift, inheritance by
  form (partial delta_rho), each x {F, C}; secondary rows: disagreement O vs F / O vs C and the teacher-agreement change.
  Homogenization, joint D per version, suggestibility per version and the content / register checks are descriptive.
  On any split other than test the Verdicts table is labelled descriptive (dev is the freeze split; test is evaluated once).
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
from vcd.analysis import e3_metrics as E
from vcd.config import resolve
from vcd.schemas import TeacherResponse
from vcd.teacher import profile as P
from vcd.train.data import load_train_yaml

PRESPECIFIED = "E3 rule pre-specified 2026-10-05 (docs/03 E3 row, tasks/e3_plan.md §3) before any F / C run existed"
RULE_ZH = "效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；R 有而 F / C 无则归因于隐性内容变化"
ALPHA = 0.05
PRIMARY = ("disagreement F vs C", "consistency change: flip rate", "consistency change: cross-framing JSD", "excess teacher drift (JSD to own teacher)", "inheritance by form: partial delta_rho")


def freeze_label(frozen_commit: Optional[str]) -> str:
    return f"{PRESPECIFIED}; frozen at commit {frozen_commit} (tasks/hpc_log.md)" if frozen_commit else f"{PRESPECIFIED}; not yet frozen (freeze line pending in tasks/hpc_log.md)"


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


# --------------------------------------------------------------------------- loading


def load_tokenizer(name: str):
    """AutoTokenizer for the target-token lengths; None (with a warning) when unavailable or name == 'none'."""
    if not name or name.lower() == "none":
        return None
    try:
        from transformers import AutoTokenizer  # optional: the `train` extra

        return AutoTokenizer.from_pretrained(name)
    except Exception as e:  # noqa: BLE001  (offline cache miss, missing extra)
        print(f"warning: tokenizer {name!r} unavailable ({type(e).__name__}); target-token lengths are NaN", file=sys.stderr)
        return None


def load_base_rows(base_run: Optional[str], split: str, student_rows: list[TeacherResponse], pid: set[str]) -> tuple[list[TeacherResponse], Optional[str]]:
    """Rows of the untrained base: {base_run}/eval/{split}_responses.jsonl, else a version-B run inside the student namespace."""
    if base_run:
        p = Path(base_run) / "eval" / f"{split}_responses.jsonl"
        if p.exists():
            rows = [r for r in M.load_responses([p], pid) if M.is_run_id(r.teacher)]
            names = sorted({r.teacher for r in rows})
            if names:
                return [r for r in rows if r.teacher == names[0]], names[0]
        print(f"warning: no base readout at {p}; the partial delta_rho falls back to the raw one", file=sys.stderr)
    b = sorted({r.teacher for r in student_rows if M.is_run_id(r.teacher) and M.parse_run_id(r.teacher).version == "B"})
    if b:
        return [r for r in student_rows if r.teacher == b[0]], b[0]
    return [], None


# --------------------------------------------------------------------------- verdicts


VERDICT_COLS = ["metric", "family", "tier", "one_sided", "teachers", "null_q95", "null_q95_single", "null_sd", "n_null", "df", "n_pass", "n_pass_single", "n_tost", "n_teachers", "n_required", "direction", "direction_consistent",
                "min_p_holm", "p_row", "p_row_holm_primary", "verdict"]


def verdict_rows(dis_t: pd.DataFrame, excess: pd.DataFrame, cons_t: pd.DataFrame, drift_t: pd.DataFrame, inh_t: pd.DataFrame, nulls: dict[str, np.ndarray], null_groups: dict[str, np.ndarray],
                 versions: list[str], n_required: int, df: Optional[int]) -> tuple[pd.DataFrame, dict]:
    """One verdict per metric (rule 7): the per-teacher seed-mean statistic against the t-scaled pooled seed-pair null.

    Disagreement rows use the centred excess (`excess_disagreement`: V-W disagreement minus the teacher's own O-O mean,
    plus the jackknife variance of that mean) one-sided; the other rows the seed-paired V - O difference two-sided.
    `p_row` = second-smallest per-teacher p (the level at which ">= 2 of 3 exceed" would just hold, sign ignored);
    `p_row_holm_primary` = Holm over the primary rows of p_row (descriptive: the q95 rule itself has a per-row false
    positive rate of about 3 * alpha^2 / 2 = 0.004 under H0, i.e. <= 0.05 family-wise over the 13 rows by Bonferroni).
    """
    specs = []  # (name, family, tier, stats, null, one_sided, table, extra_var, null_groups)
    for a, b in E.DISAGREEMENT_PAIRS:
        if a in versions and b in versions:
            g = excess[excess["pair"] == f"{a}-{b}"] if len(excess) else excess
            name = f"disagreement {a} vs {b}"
            specs.append((name, "disagreement", "primary" if name in PRIMARY else "secondary", dict(zip(g["teacher"], g["excess"])) if len(g) else {}, nulls.get("disagree_O-O", np.array([])), True, g,
                          dict(zip(g["teacher"], g["var_oo_mean"])) if len(g) else {}, null_groups.get("disagree_O-O")))
    for v in [x for x in versions if x != "O"]:
        for metric, label in (("flip", "consistency change: flip rate"), ("jsd", "consistency change: cross-framing JSD")):
            g = cons_t[(cons_t["metric"] == metric) & (cons_t["version"] == v)]
            specs.append((f"{label} {v} - O", "consistency", "primary" if label in PRIMARY else "secondary", dict(zip(g["teacher"], g["diff"])), nulls.get(metric, np.array([])), False, g, {}, None))
        for metric, label, key in (("agree", "teacher agreement change", "agree_own"), ("jsd", "excess teacher drift (JSD to own teacher)", "jsd_own")):
            g = drift_t[(drift_t["metric"] == metric) & (drift_t["version"] == v)]
            specs.append((f"{label} {v} - O", "drift", "primary" if label in PRIMARY else "secondary", dict(zip(g["teacher"], g["diff"])), nulls.get(key, np.array([])), False, g, {}, None))
        g = inh_t[inh_t["version"] == v]
        specs.append((f"inheritance by form: partial delta_rho {v} - O", "inheritance", "primary", dict(zip(g["teacher"], g["diff"])), nulls.get("delta_rho", np.array([])), False, g, {}, None))
    rows, raw = [], {}
    for name, fam, tier, stats, null, one_sided, g, extra_var, groups in specs:
        n_seeds = dict(zip(g["teacher"], g["n_seeds"].astype(int))) if len(g) else 1
        cis = {r["teacher"]: (float(r["ci_lo"]), float(r["ci_hi"])) for _, r in g.iterrows()} if len(g) else None
        vd = E.e3_verdict(stats, null, one_sided=one_sided, n_seeds=n_seeds, cis=cis, extra_var=extra_var, null_groups=list(groups) if groups is not None else None, df=df, n_required=n_required)
        raw[name] = vd
        per_t = vd["per_teacher"]
        detail = "; ".join(f"{t} {_fmt(d['stat'])} {_ci(*(d['ci'] or (np.nan, np.nan)))} ({_fmt(d['effect_sd'])} null sd, p {_fmt(d['p_null'])}, Holm {_fmt(d['p_holm'])}, TOST {d['tost']}){'*' if d['exceeds_q95'] else ''}"
                           for t, d in per_t.items()) or "nan"
        ps = sorted(d["p_null"] for d in per_t.values() if np.isfinite(d["p_null"]))
        rows.append(dict(metric=name, family=fam, tier=tier, one_sided=one_sided, teachers=detail, null_q95=vd["q95"], null_q95_single=vd["q95_single"], null_sd=vd["null_sd"], n_null=vd["n_null"], df=df, n_pass=vd["n_pass"],
                         n_pass_single=sum(1 for d in per_t.values() if d["exceeds_q95_single"]), n_tost=vd["n_tost"], n_teachers=vd["n_teachers"], n_required=vd["n_required"], direction=vd["direction"],
                         direction_consistent=vd["direction_consistent"], min_p_holm=min([d["p_holm"] for d in per_t.values()], default=np.nan), p_row=ps[1] if len(ps) >= 2 else np.nan, p_row_holm_primary=np.nan, verdict=vd["verdict"]))
    vt = pd.DataFrame(rows, columns=VERDICT_COLS)
    prim = vt["tier"] == "primary"
    if prim.any():
        vt.loc[prim, "p_row_holm_primary"] = M.holm(vt.loc[prim, "p_row"].to_numpy(dtype=float))
    return vt, raw


# --------------------------------------------------------------------------- summary


def summary_md(ctx: dict) -> str:
    split, student, versions = ctx["split"], ctx["student"], ctx["versions"]
    lines = [f"# E3 summary ({split}, student {student}, variants {', '.join(ctx['variants'])}; {ctx['freeze']}; auto-generated)", ""]
    lines += [f"Rule (docs/03 E3 row, verbatim): {RULE_ZH}. Operationalised (tasks/e3_plan.md §3): per metric, the per-teacher statistic is the seed mean of the paired difference S_{{T,V,s}} - S_{{T,O,s}} "
              "(disagreement: the mean V-W disagreement minus the teacher's own O-O seed-pair mean); the seed-pair null is the same single-pair quantity between two O seeds of the same teacher, pooled over "
              f"teachers, and scaled to the statistic: SD_stat = sqrt(mean(d^2) / n_seeds [+ jackknife var of the O-O mean]), q95 = t(0.975, df = sum(n_O - 1) = {ctx['df']}) x SD_stat (disagreement: t(0.95)); "
              f"a teacher exceeds when |stat| > q95; effect iff >= 2/3 of the {ctx['n_required']} teachers exceed with the same sign. p from the t reference with Holm over the teachers; `no effect` only when "
              ">= 2/3 teachers pass the TOST (family-bootstrap 95% CI inside +/- 1 SD_stat; docs/04 §3), otherwise `inconclusive`. The raw single-pair q95 (`null_q95_single`, `n_pass_single`) is a sensitivity "
              "column. Primary rows: disagreement F vs C, consistency change, excess drift, inheritance by form; the other rows are secondary. Under H0 the q95 rule has a per-row false-positive rate of about 0.004, "
              "<= 0.05 family-wise over the 13 rows (Bonferroni); `p_row_holm_primary` is descriptive. CIs are family-bootstrap 2.5 / 97.5 percentiles with families resampled jointly for every seed of a teacher. "
              "Assumptions: seed noise approximately normal and independent across seeds (same-seed F / O pairs share init and data order, so the null is conservative).", ""]
    if split != "test":
        lines += [f"**{split} = freeze split**: the verdicts below are descriptive; only results/e3 (test, evaluated once after the dev freeze line in tasks/hpc_log.md) is confirmatory.", ""]
    inv = ctx["inventory"]
    lines += ["## Run inventory (runs with a readout on this split)", ""]
    lines += _md_table(inv, ["teacher", *[f"n_{v}" for v in versions], *[f"seeds_{v}" for v in versions], *[f"paired_{v}" for v in versions if v != "O"]]) if len(inv) else ["(no protocol runs found)", ""]
    if ctx["base_name"]:
        lines += [f"Base prior covariate r_0: {ctx['base_name']} ({ctx['n_base_families']} complete families without the mass gate).", ""]
    else:
        lines += ["Base prior covariate r_0: absent (partial delta_rho falls back to the raw delta_rho).", ""]

    lines += [f"## Verdicts (rule 7; {'descriptive on ' + split if split != 'test' else 'confirmatory'})", ""]
    vt = ctx["verdicts"]
    if len(vt):
        lines += ["| metric | tier | teachers: stat [CI] (effect in null sd, p, Holm, TOST) * = exceeds q95 | null q95 of the stat (single-pair q95; n) | pass | TOST pass | direction | verdict |", "|---|---|---|---|---|---|---|---|"]
        for _, r in vt.iterrows():
            lines.append(f"| {r['metric']} | {r['tier']} | {r['teachers']} | {_fmt(r['null_q95'])} ({_fmt(r['null_q95_single'])}; {r['n_null']}) | {r['n_pass']}/{r['n_teachers']} | {r['n_tost']}/{r['n_teachers']} | {r['direction']} | **{r['verdict']}** |")
        lines.append("")
    else:
        lines += ["pending: no student runs", ""]
    lines += ["Descriptive (no verdict): homogenization index, joint partial D per version, suggestibility per version, content and register checks of the training files.", ""]

    lines += ["## Seed-pair null: the same quantity between two O seeds of one teacher, pooled over teachers (seed_pair_null.csv)", ""]
    lines += _md_table(ctx["null_summary"], ["metric", "n", "mean", "sd", "q95"])

    lines += ["## (1) Cross-student disagreement: share of (family, variant) cells with different majority acts, same teacher and seed (disagreement.csv; disagree_conf = cells where both |p - 0.5| >= 0.1, robustness)", ""]
    lines += _md_table(ctx["dis_t"], ["teacher", "pair", "n_seeds", "n_families", "disagree", "ci_lo", "ci_hi", "disagree_conf", "jsd", "jsd_ci_lo", "jsd_ci_hi"]) if len(ctx["dis_t"]) else ["pending (needs two versions of the same teacher and seed)", ""]
    if len(ctx["excess"]):
        lines += ["Excess over the teacher's own O-O seed-pair mean (disagreement_excess.csv; the verdict statistic; var_oo_mean = delete-one-seed jackknife variance of the O-O mean):", ""]
        lines += _md_table(ctx["excess"], ["teacher", "pair", "n_seeds", "disagree", "oo_mean", "n_oo_pairs", "var_oo_mean", "excess", "ci_lo", "ci_hi"])
    lines += ["## (2) Consistency change V - O, paired by seed (consistency_delta.csv; flip = flip rate, jsd = cross-framing JSD)", ""]
    lines += _md_table(ctx["cons_t"], ["metric", "teacher", "version", "n_seeds", "n_families", "mean_v", "mean_o", "diff", "ci_lo", "ci_hi", "direction"]) if len(ctx["cons_t"]) else ["pending (no F / C run paired with an O run)", ""]
    lines += ["## (3) Teacher agreement change and excess teacher drift V - O, paired by seed (drift.csv; agree = majority-act agreement with the own teacher, jsd = JSD to the own teacher)", ""]
    lines += _md_table(ctx["drift_t"], ["metric", "teacher", "version", "n_seeds", "n_families", "mean_v", "mean_o", "diff", "ci_lo", "ci_hi", "direction"]) if len(ctx["drift_t"]) else ["pending", ""]
    lines += ["## (4) Homogenization index per version: distance between students of different teachers, seed-matched (homogenization.csv; a fix that homogenises shows a drop vs O; 1 - corr is scale-free and is the index to read first)", ""]
    lines += _md_table(ctx["homog"], ["version", "n_cells", "n_seeds", "n_families", "one_minus_corr", "omc_ci_lo", "omc_ci_hi", "jsd", "jsd_ci_lo", "jsd_ci_hi", "n_paired_cells", "d_omc_vs_O", "d_omc_ci_lo", "d_omc_ci_hi", "d_jsd_vs_O", "d_jsd_ci_lo", "d_jsd_ci_hi"]) if len(ctx["homog"]) else ["pending (needs >= 2 teachers at the same seed)", ""]
    if len(ctx["homog"]):
        lines += ["Calibration guard (judgment JSD and majority disagreement shrink / grow mechanically when readouts move towards 0.5): mean |p - 0.5|, share of cells with |p - 0.5| < 0.1, cross-teacher majority disagreement (all cells / confident cells).", ""]
        lines += _md_table(ctx["homog"], ["version", "mean_abs_margin", "share_low_margin", "maj_disagree", "maj_disagree_conf"])
    lines += [f"## (5) Inheritance by form: delta_rho{' partial given r_0' if ctx['base_name'] else ''} of V minus O, paired by seed (inheritance_by_form.csv)", ""]
    lines += _md_table(ctx["inh_t"], ["teacher", "version", "n_seeds", "n_families", "mean_v", "mean_o", "diff", "ci_lo", "ci_hi", "direction", "control"]) if len(ctx["inh_t"]) else ["pending", ""]
    runs = ctx["inh_runs"]
    if len(runs):
        g = runs.groupby(["teacher", "version"])["delta_rho"].agg(["mean", "std", "count"]).reset_index()
        lines += ["Per-run delta_rho seed means by version (inheritance_by_form_runs.csv):", ""] + _md_table(g, ["teacher", "version", "mean", "std", "count"])
    lines += ["### Joint partial D per version (joint_D_by_version.csv; e2 secondary statistic computed on each version's seed-pooled students)", ""]
    lines += _md_table(ctx["jointD"], ["version", "n_teachers", "n_families", "D", "ci_lo", "ci_hi", "p_perm", "D_specific", "ci_specific_lo", "ci_specific_hi", "D_shared", "D_raw", "e2_secondary_rule"]) if len(ctx["jointD"]) else ["pending (needs >= 2 teachers with runs of the version)", ""]
    lines += ["### Suggestibility s = delta(T5) - delta(T6) per (teacher, version) group with family-bootstrap CI (suggestibility_by_version.csv) and version differences (suggestibility_version_diffs.csv)", ""]
    lines += _md_table(ctx["sugg"], ["group", "n_profiles", "n_families", "s", "ci_lo", "ci_hi"]) if len(ctx["sugg"]) else ["pending", ""]
    lines += _md_table(ctx["sugg_diffs"], ["teacher", "version", "contrast", "diff", "ci_lo", "ci_hi"]) if len(ctx["sugg_diffs"]) else []

    lines += ["## (6) Stage-2 content check of the ACTUAL training files (content_check.csv; docs/03 §5: a change here = content drift, not form)", ""]
    cc = ctx["content"]
    if len(cc):
        lines += _md_table(cc, ["teacher", "version", "n_items", "n_families", "same_prompt_set_as_O", "letter_identity_with_O", "letter_matches_rewrite", "kept_attempt_found", *[f"check_{c}" for c in E.CHECKS], "mean_attempts", "kept_share", "mean_words", "mean_chars", "mean_target_tokens"])
        fc = cc[cc["version"] != "O"]
        bad = fc[fc["letter_identity_with_O"] < 1.0]
        lines += [("Letter identity with O: 100% for every F / C file." if bad.empty else f"**Letter identity with O below 100% for {len(bad)} file(s)**: " + ", ".join(f"{r['teacher']} {r['version']} {_fmt(r['letter_identity_with_O'])}" for _, r in bad.iterrows())), ""]
        for col, what in (("letter_matches_rewrite", "SFT letter differs from the kept rewrite text's leading 'Answer: X' (format leak in the rewrite, letter itself still equals O)"), ("kept_attempt_found", "no kept attempt in the rewrite log")):
            odd = fc[fc[col].notna() & (fc[col] < 1.0)]
            if len(odd):
                lines += [f"**{col} < 1 for {len(odd)} file(s)** ({what}): " + ", ".join(f"{r['teacher']} {r['version']} {r[col]:.5f} (~{round((1 - r[col]) * r['n_items'])} item(s))" for _, r in odd.iterrows()), ""]
    else:
        lines += [f"pending (no {ctx['sft_dir']}/{{teacher}}_{{O,F,C}}_s{ctx['sft_seed']}.jsonl; rebuild with scripts/10_build_sft_data.py --versions O,F,C --rewrites-dir {ctx['rewrites_dir']} --out-dir {ctx['sft_dir']})", ""]
    lines += ["### Lexical register per version (register_check.csv; rates per word; fk_grade = Flesch-Kincaid proxy) and F vs C separability (register_separation.csv; frozen bar >= 0.90, e3_plan §2; Wilson 95% CIs)", ""]
    lines += _md_table(ctx["register"], ["teacher", "version", "n", "n_words", "n_sentences", *E.REGISTER_FEATURES]) if len(ctx["register"]) else ["pending", ""]
    lines += _md_table(ctx["separation"], ["teacher", "a", "b", "n_a", "n_b", "nearest_centroid_loo_acc", "nc_ci_lo", "nc_ci_hi", "logistic_cv_acc", "lr_ci_lo", "lr_ci_hi", "min_acc", "status", "top_feature"]) if len(ctx["separation"]) else []
    if len(ctx["separation"]):
        lines += ["The >= 0.90 bar applies to F vs C (pass / fail); O vs F and O vs C are descriptive (O is already a formal register, so O vs F near chance is expected and O vs C mirrors F vs C).", ""]
    lines += ["Notes: students are compared within teacher and paired by seed; the paired O students (runs/qwen3-4b-paired) are trained on the prompt intersection of O / F / C, not on the full O set of E1. ",
              "Consistency is never read alone: every consistency row sits next to the agreement / JSD rows of the same runs. R students and the base are not E3 cells."]
    return "\n".join(lines)


# --------------------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", default=None, help="default: config paths.runs_dir")
    ap.add_argument("--student", default="qwen3-4b-paired", help="student namespace runs/{student}/* (default qwen3-4b-paired; qwen3-4b for the E1 smoke)")
    ap.add_argument("--split", default="dev", choices=["dev", "test", "pilot"])
    ap.add_argument("--base-run", default="runs/qwen3-4b/base_B_s0", help="untrained base run dir with eval/{split}_responses.jsonl (covariate r_0); falls back to a B run in the student namespace")
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl; default: config paths.teacher_dir")
    ap.add_argument("--teachers", default=None, help="comma list; default: config teachers")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--versions", default="O,F,C")
    ap.add_argument("--variants", default=None, help="comma list of framings for the metrics (default: config data.variants = T1,T3,T5,T6)")
    ap.add_argument("--sft-dir", default="data/sft_paired", help="paired training files {teacher}_{O,F,C}_s{seed}.jsonl for the content check")
    ap.add_argument("--sft-seed", type=int, default=1, help="which seed's SFT files to check (versions share the prompt set; seeds differ in row order only)")
    ap.add_argument("--rewrites-dir", default="data/rewrites_train", help="{teacher}/rewrites.jsonl with per-item judge checks")
    ap.add_argument("--tokenizer", default="Qwen/Qwen3-4B-Base", help="tokenizer for target-token lengths ('none' to skip)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default=None, help="default results/e3_{split} (results/e3 for test)")
    ap.add_argument("--n-boot", type=int, default=10_000)
    ap.add_argument("--n-perm", type=int, default=10_000, help="family permutations of the joint D per version")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--frozen-commit", default=None, help="commit hash of the freeze line in tasks/hpc_log.md (printed in summary.md); omitted -> 'not yet frozen'")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    versions = [v for v in args.versions.split(",") if v]
    if "O" not in versions:
        raise SystemExit("--versions must include O (the reference version)")
    teachers = args.teachers.split(",") if args.teachers else list(cfg["teachers"])
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    out = Path(args.out) if args.out else Path("results") / ("e3" if args.split == "test" else f"e3_{args.split}")
    out.mkdir(parents=True, exist_ok=True)

    # students
    runs_dir = Path(args.runs_dir) if args.runs_dir else Path(cfg["paths"]["runs_dir"])
    student_rows = [r for r in M.load_run_responses(runs_dir, args.split, args.student) if r.prompt_id in pid]
    bad_ids = sorted({r.teacher for r in student_rows if not M.is_run_id(r.teacher)})
    if bad_ids:
        print(f"warning: skipping {len(bad_ids)} run id(s) that do not match the protocol pattern (smoke runs?): {bad_ids}", file=sys.stderr)
        student_rows = [r for r in student_rows if r.teacher not in bad_ids]
    base_rows, base_name = load_base_rows(args.base_run, args.split, student_rows, pid)
    # teachers
    teacher_dir = Path(args.teacher_dir) if args.teacher_dir else Path(cfg["paths"]["teacher_dir"])
    tfiles = [teacher_dir / f"{t}_{args.split}_profile.jsonl" for t in teachers]
    missing = [str(p) for p in tfiles if not p.exists()]
    if missing:
        print("warning: missing teacher profiles:", ", ".join(missing), file=sys.stderr)
    teacher_rows = M.load_responses([p for p in tfiles if p.exists()], pid)
    run_ids = sorted({r.teacher for r in student_rows})
    print(f"students: {len(student_rows)} rows, {len(run_ids)} runs; teachers: {len(teacher_rows)} rows, {len({r.teacher for r in teacher_rows})} profiles; base: {base_name or 'absent'}")
    if not student_rows:
        print("warning: no student responses found; only the content / register checks are computed", file=sys.stderr)

    fs, ft = M.frame_table(student_rows, prompts), M.frame_table(teacher_rows, prompts)
    sym_s, sym_t = M.sym_table(fs), M.sym_table(ft)
    mats_s, mats_t = E.cell_matrices(sym_s, variants), E.cell_matrices(sym_t, variants)
    shifts_s, shifts_t = P.framing_shifts(sym_s, variants), P.framing_shifts(sym_t, variants)
    grid = E.run_grid(run_ids, versions)
    inventory = E.grid_inventory(grid, versions)
    inventory.to_csv(out / "run_inventory.csv", index=False)
    shifts_0 = M.base_prior_shifts(base_rows, prompts, variants) if base_rows else pd.DataFrame(columns=["teacher", "family_id", "variant", "p", "r"])
    control = shifts_0 if len(shifts_0) else None
    n_base_fams = int(shifts_0["family_id"].nunique()) if len(shifts_0) else 0

    # one family set per teacher (all runs of the teacher): nulls and paired statistics on the same families
    fams_by_teacher = E.teacher_families(mats_s, grid, versions) if len(grid) else {}
    # per-run scalars and the seed-pair nulls
    scal = E.run_scalars(mats_s, mats_t, families=fams_by_teacher)
    scal.to_csv(out / "run_scalars.csv", index=False)
    nulls: dict[str, np.ndarray] = {}
    null_groups: dict[str, np.ndarray] = {}
    null_tables = []
    for metric in ("flip", "jsd", "agree_own", "jsd_own"):
        t = E.seed_pair_null(scal, metric, "O") if len(scal) else pd.DataFrame()
        if len(t):
            null_tables.append(t)
            nulls[metric] = t["diff"].to_numpy(dtype=float)
            null_groups[metric] = t["teacher"].to_numpy()
    spd = E.seed_pair_disagreement(mats_s, grid, "O", families=fams_by_teacher) if len(grid) else pd.DataFrame()
    if len(spd):
        nulls["disagree_O-O"] = spd["disagree"].to_numpy(dtype=float)
        nulls["jsd_between_O-O"] = spd["jsd"].to_numpy(dtype=float)
        null_groups["disagree_O-O"] = null_groups["jsd_between_O-O"] = spd["teacher"].to_numpy()
        null_tables.append(pd.DataFrame(dict(metric="disagree_O-O", teacher=spd["teacher"], version="O", seed_a=spd["seed_a"], seed_b=spd["seed_b"], run_a=spd["run_a"], run_b=spd["run_b"], diff=spd["disagree"], abs_diff=spd["disagree"])))
        null_tables.append(pd.DataFrame(dict(metric="jsd_between_O-O", teacher=spd["teacher"], version="O", seed_a=spd["seed_a"], seed_b=spd["seed_b"], run_a=spd["run_a"], run_b=spd["run_b"], diff=spd["jsd"], abs_diff=spd["jsd"])))
    n_o = grid["O"].notna().groupby(grid["teacher"]).sum() if len(grid) else pd.Series(dtype=int)
    df_null = int(sum(max(0, int(k) - 1) for k in n_o)) or None  # sum_T (n_O,T - 1); None -> normal reference

    # (1) - (3)
    dis_s, dis_t = E.cross_student_disagreement(mats_s, grid, [p for p in E.DISAGREEMENT_PAIRS if p[0] in versions and p[1] in versions], n_boot=args.n_boot, seed=args.seed, families=fams_by_teacher) if len(grid) else (pd.DataFrame(), pd.DataFrame())
    dis_t.to_csv(out / "disagreement.csv", index=False)
    dis_s.to_csv(out / "disagreement_by_seed.csv", index=False)
    excess = E.excess_disagreement(dis_t, spd) if len(dis_t) else pd.DataFrame()
    excess.to_csv(out / "disagreement_excess.csv", index=False)
    non_o = [v for v in versions if v != "O"]
    cons_s, cons_t = E.consistency_delta(mats_s, grid, non_o, n_boot=args.n_boot, seed=args.seed, families=fams_by_teacher) if len(grid) else (pd.DataFrame(), pd.DataFrame())
    cons_t.to_csv(out / "consistency_delta.csv", index=False)
    cons_s.to_csv(out / "consistency_delta_by_seed.csv", index=False)
    drift_s, drift_t = E.drift_delta(mats_s, mats_t, grid, non_o, n_boot=args.n_boot, seed=args.seed, families=fams_by_teacher) if len(grid) else (pd.DataFrame(), pd.DataFrame())
    drift_t.to_csv(out / "drift.csv", index=False)
    drift_s.to_csv(out / "drift_by_seed.csv", index=False)
    # (4)
    hom_c, hom_v = E.homogenization(mats_s, grid, versions, n_boot=args.n_boot, seed=args.seed) if len(grid) else (pd.DataFrame(), pd.DataFrame())
    hom_v.to_csv(out / "homogenization.csv", index=False)
    hom_c.to_csv(out / "homogenization_cells.csv", index=False)
    # (5)
    inh_r, inh_s, inh_t = E.inheritance_by_form(shifts_s, shifts_t, control, grid, variants, non_o, n_boot=args.n_boot, seed=args.seed) if len(grid) and len(shifts_t) else (pd.DataFrame(), pd.DataFrame(), pd.DataFrame())
    inh_t.to_csv(out / "inheritance_by_form.csv", index=False)
    inh_s.to_csv(out / "inheritance_by_form_by_seed.csv", index=False)
    inh_r.to_csv(out / "inheritance_by_form_runs.csv", index=False)
    if len(inh_r):
        t = E.seed_pair_null(inh_r.rename(columns={"delta_rho": "delta_rho"}), "delta_rho", "O")
        if len(t):
            null_tables.append(t)
            nulls["delta_rho"] = t["diff"].to_numpy(dtype=float)
    jd_t, jd_raw = E.joint_D_by_version(shifts_s, shifts_t, control, grid, variants, versions, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed) if len(grid) and len(shifts_t) else (pd.DataFrame(), {})
    jd_t.to_csv(out / "joint_D_by_version.csv", index=False)
    (out / "joint_D_by_version.json").write_text(json.dumps(jd_raw, indent=2, default=_dump), encoding="utf-8")
    sg, sg_d = E.suggestibility_by_version(shifts_s, shifts_t, grid, versions, n_boot=args.n_boot, seed=args.seed) if len(grid) else (pd.DataFrame(), pd.DataFrame())
    sg.to_csv(out / "suggestibility_by_version.csv", index=False)
    sg_d.to_csv(out / "suggestibility_version_diffs.csv", index=False)
    # nulls out
    null = pd.concat(null_tables, ignore_index=True) if null_tables else pd.DataFrame(columns=["metric", "teacher", "version", "seed_a", "seed_b", "run_a", "run_b", "diff", "abs_diff"])
    null.to_csv(out / "seed_pair_null.csv", index=False)
    ns = pd.DataFrame([{"metric": k, **E.null_summary(np.abs(v) if not k.endswith("O-O") else v)} for k, v in nulls.items()], columns=["metric", "n", "mean", "sd", "q95"])
    ns.to_csv(out / "seed_pair_null_summary.csv", index=False)
    # verdicts
    freeze = freeze_label(args.frozen_commit)
    vt, vraw = verdict_rows(dis_t, excess, cons_t, drift_t, inh_t, nulls, null_groups, versions, n_required=len(teachers), df=df_null) if len(grid) else (pd.DataFrame(columns=VERDICT_COLS), {})
    vt.to_csv(out / "verdicts.csv", index=False)
    (out / "verdicts.json").write_text(json.dumps({"rule_zh": RULE_ZH, "frozen": freeze, "split": args.split, "confirmatory": args.split == "test", "alpha": ALPHA, "df": df_null, "n_required": len(teachers), "primary_rows": list(PRIMARY), "verdicts": vraw},
                                                  indent=2, default=_dump), encoding="utf-8")

    # (6) content and register checks of the actual training files
    tok = load_tokenizer(args.tokenizer)
    cc_rows, reg_rows, sep_rows = [], [], []
    for t in teachers:
        sft = E.load_sft_versions(args.sft_dir, t, args.sft_seed, versions)
        if not sft:
            continue
        rw = E.load_rewrites(Path(args.rewrites_dir) / t / "rewrites.jsonl")
        cc = E.content_check(sft, rw, tokenizer=tok, versions=versions)
        cc.insert(0, "teacher", t)
        cc_rows.append(cc)
        items, per_v = E.register_table(sft, versions)
        per_v.insert(0, "teacher", t)
        reg_rows.append(per_v)
        for a, b in (("F", "C"), ("O", "F"), ("O", "C")):
            if a in sft and b in sft:
                s = E.register_separation(items, a, b, seed=args.seed)
                top = max(s["feature_d"], key=lambda f: abs(s["feature_d"][f])) if s["feature_d"] else None
                status = s["status"] if (a, b) == ("F", "C") else "descriptive"  # the >= 0.90 bar of docs/02 is for F vs C; O is itself formal, so O vs F is expected near chance
                sep_rows.append(dict(teacher=t, a=a, b=b, n_a=s["n_a"], n_b=s["n_b"], nearest_centroid_loo_acc=s["nearest_centroid_loo_acc"], nc_ci_lo=s["nc_ci_lo"], nc_ci_hi=s["nc_ci_hi"], logistic_cv_acc=s["logistic_cv_acc"],
                                     lr_ci_lo=s["lr_ci_lo"], lr_ci_hi=s["lr_ci_hi"], min_acc=s["min_acc"], status=status, top_feature=f"{top} d={s['feature_d'][top]:.2f}" if top else None, **{f"d_{f}": v for f, v in s["feature_d"].items()}))
    content = pd.concat(cc_rows, ignore_index=True) if cc_rows else E.content_check({}, []).assign(teacher=pd.Series(dtype=str))
    register = pd.concat(reg_rows, ignore_index=True) if reg_rows else E.register_table({})[1].assign(teacher=pd.Series(dtype=str))
    separation = pd.DataFrame(sep_rows, columns=["teacher", "a", "b", "n_a", "n_b", "nearest_centroid_loo_acc", "nc_ci_lo", "nc_ci_hi", "logistic_cv_acc", "lr_ci_lo", "lr_ci_hi", "min_acc", "status", "top_feature", *[f"d_{f}" for f in E.REGISTER_FEATURES]])
    content.to_csv(out / "content_check.csv", index=False)
    register.to_csv(out / "register_check.csv", index=False)
    separation.to_csv(out / "register_separation.csv", index=False)

    ctx = dict(split=args.split, student=args.student, versions=versions, variants=variants, inventory=inventory, base_name=base_name, n_base_families=n_base_fams, verdicts=vt, null_summary=ns, freeze=freeze, df=df_null, n_required=len(teachers),
               dis_t=dis_t, excess=excess, cons_t=cons_t, drift_t=drift_t, homog=hom_v, inh_t=inh_t, inh_runs=inh_r, jointD=jd_t, sugg=sg, sugg_diffs=sg_d, content=content, register=register, separation=separation,
               sft_dir=args.sft_dir, sft_seed=args.sft_seed, rewrites_dir=args.rewrites_dir)
    (out / "summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote {len(list(out.glob('*.csv')))} CSVs + summary.md to {out}")
    print((out / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
