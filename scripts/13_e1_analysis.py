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
{teacher_dir}/{teacher}_{split}_profile.jsonl for the teachers in the config (or explicit --teacher-files). For E1a / E1b
also runs/{student}/{run}/eval/train_responses.jsonl (scripts/12 --split train) and the SFT files in --sft-dir (an O
file that is missing locally is rebuilt in memory from {teacher_dir}/{teacher}_train_demo.jsonl).
Outputs (docs/05 §6): category_rates.csv, order_gap.csv, agreement.csv, agreement_by_variant.csv, jsd.csv,
consistency.csv, seen_vs_unseen.csv, e1_table.csv, inheritance.csv, inheritance_by_variant.csv, inheritance_pooled.csv
(E2 primary), seed_null.csv, grid_permutation.json, e2_secondary_D.json (E2 secondary), inheritance_partial.csv,
inheritance_partial_by_variant.csv, inheritance_partial_pooled.csv, grid_permutation_partial.json, suggestibility_runs.csv,
suggestibility_groups.csv, suggestibility_group_pairs.csv, dose_response.json, base_control.csv, e1_train_reproduction.csv,
e1_contested.csv and summary.md. No figures.

Decision rules (frozen on dev 2026-10-05, corrected the same day after the HPC agent's critique; tasks/e1_plan.md §0, tasks/e2_plan.md §2):
  E1  E1a every O run reproduces >= 95% of its own SFT target letters on its training prompts (every prompt read out);
      E1b on contested training items (own teacher's label != another teacher's) the seed-pooled share of items where the
      student gives its own teacher's letter has a family-bootstrap 95% CI lower bound > 0.5 against each other teacher.
      Verdict = E1a and E1b for all three teachers; "pending (no train readouts)" until eval/train_responses.jsonl exist.
  E2 primary (the pre-registered rule, unchanged): per teacher, the seed-mean student profile's delta_rho = rho(own) -
      max rho(other) > 0 with family-permutation p (Holm over teachers) < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3.
  E2 secondary (pre-declared): D = diagonal minus off-diagonal mean of the seed-pooled student x teacher partial-correlation
      matrix given r_0 (the untrained base's prior profile WITHOUT the 0.9 mass gate), seen framings only; family bootstrap
      95% CI excludes 0, family permutation p < 0.05, AND the student-specific part D_specific (D = D_shared + D_specific,
      D_shared = mean student residual x unequal row scales, no own-teacher information) has a family-bootstrap CI above 0.
      D on T0 only, the raw (non-partial) D and the scale-free D (pooled row scale) are exploratory.
  Descriptive only (no verdict): the run-level mean deltaRhoPartial and the suggestibility dose-response slope with the
      teacher-level exact p (3! = 6 relabellings, floor 1/6; the run-level 756,756-assignment p is pseudo-replicated because
      the seeds of one teacher are near-replicates), per-teacher partial delta_rho (P3), suggestibility per group with
      family-bootstrap CIs and pairwise differences, the S_0 control row from the ungated covariate profile.
  Every rho is printed next to its teacher's attenuation ceiling sqrt(2r / (1 + r)) (Spearman-Brown reliability of the
      two-order symmetrized profile from the order split-half r of docs/E0_results.md §13); the raw r is the E0 gate quantity:
      with two or more test-split r below 0.5 docs/03 §1 makes RQ1 / E2 / E7 exploratory and the main line E2b / E3 / E4 / E5
      (of which this project runs E3).
  On any split other than test the Verdicts table is labelled descriptive (dev is the rule-selection split).
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
from vcd.config import resolve
from vcd.io import load_models, read_jsonl
from vcd.schemas import TeacherResponse
from vcd.teacher import profile as P
from vcd.train.data import load_train_yaml, select_demo_targets, target_letter

E1A_MIN = 0.95  # frozen on dev 2026-10-05
E1B_MIN_CI_LO = 0.5
ALPHA = 0.05
FROZEN = "rules frozen on dev 2026-10-05"
# Teacher order split-half reliability r of the framing profile (docs/E0_results.md §13). The E0 gate reads r itself; the
# printed ceiling of a student-teacher rho is M.reliability_ceiling(r) = sqrt(2r / (1 + r)) (the symmetrized profile averages
# the two orders, so the raw r is not a bound: the base prior reaches 0.533 against DeepSeek's dev r of 0.515).
RELIABILITY = {"dev": {"gpt4o": 0.675, "claude46": 0.383, "deepseek_v4": 0.515}, "test": {"gpt4o": 0.691, "claude46": 0.329, "deepseek_v4": 0.466}}
RELIABILITY_GATE = 0.5  # docs/03 §1: >= 2 teachers below -> E0 P2 fails -> RQ1 / E2 / E7 exploratory, main line E2b / E3 / E4 / E5 (E3 here)


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
    if not cols:
        return ["(empty)", ""]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        lines.append("| " + " | ".join(_fmt(r[c]) for c in cols) + " |")
    return lines + [""]


def _kv_table(d: dict, keys: list[str]) -> list[str]:
    return ["| " + " | ".join(keys) + " |", "|" + "---|" * len(keys), "| " + " | ".join(_fmt(d.get(k)) for k in keys) + " |", ""]


def _ci(lo, hi) -> str:
    return f"[{_fmt(lo)}, {_fmt(hi)}]"


def _with_ceiling(df: pd.DataFrame, ceilings: dict[str, float], teacher_col: str = "teacher", rho_col: str = "rho_own") -> pd.DataFrame:
    """Add the own teacher's attenuation ceiling sqrt(2r / (1 + r)) and rho / ceiling next to a rho column."""
    df = df.copy()
    df["ceiling"] = df[teacher_col].map(ceilings).astype(float)
    if rho_col in df:
        df["rho_over_ceiling"] = df[rho_col] / df["ceiling"]
    return df


def _ceiling_row(df: pd.DataFrame, ceilings: dict[str, float], prefix: str, label_col: str, label: str = "ceiling sqrt(2r/(1+r))") -> pd.DataFrame:
    """Append a row holding every teacher column's ceiling (`{prefix}{teacher}` columns) so the column ceilings sit under the rhos."""
    row = {c: np.nan for c in df.columns}
    row[label_col] = label
    for c in df.columns:
        if c.startswith(prefix) and c[len(prefix):] in ceilings:
            row[c] = ceilings[c[len(prefix):]]
    return pd.concat([df, pd.DataFrame([row])], ignore_index=True)


# --------------------------------------------------------------------------- E1a / E1b inputs


def sft_letters(teacher: str, version: str, seed: int, sft_dir: Path, teacher_dir: Path, prompts_train: dict, variants: list[str], cfg: dict, cache: dict) -> tuple[Optional[dict[str, str]], str]:
    """prompt_id -> target letter of data/sft/{teacher}_{version}_s{seed}.jsonl; an absent O file is rebuilt from the train demos."""
    key = (teacher, version)  # O seeds share one prompt_id set and one label per prompt
    if key in cache:
        return cache[key]
    path = sft_dir / f"{teacher}_{version}_s{seed}.jsonl"
    if path.exists():
        out = ({r["prompt_id"]: r["letter"] for r in read_jsonl(path)}, str(path))
    elif version == "O" and (teacher_dir / f"{teacher}_train_demo.jsonl").exists():
        demos = load_models(teacher_dir / f"{teacher}_train_demo.jsonl", TeacherResponse)
        targets, _ = select_demo_targets(prompts_train, demos, variants, cfg["data"].get("order_policy", "stable_one"))
        out = ({pid: target_letter(t) for pid, t in targets.items()}, f"rebuilt from {teacher_dir / f'{teacher}_train_demo.jsonl'}")
    else:
        out = (None, f"missing {path}")
    if version == "O":
        cache[key] = out
    return out


def e1_train_tables(train_rows: list[TeacherResponse], teachers: list[str], sft_dir: Path, teacher_dir: Path, prompts_train: dict, variants: list[str], cfg: dict, n_boot: int, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, dict[str, str]]:
    """E1a per run, E1b per (teacher, other) pooled over the O seeds, and the E1 states {e1a, e1b, e1}.

    e1a / e1b are "pass" / "fail" only when every teacher's O runs are read out and scored; otherwise "pending",
    so a half-finished set of train readouts never shows a per-line pass. The E1a gate needs n_missing == 0
    (every SFT prompt read out) besides accuracy >= E1A_MIN; `answer_rate` (share of rows with letter mass >= 0.9)
    is reported next to the accuracy, which scores the argmax letter whatever the category.
    """
    by_run: dict[str, dict] = {}
    n_rows: dict[str, int] = {}
    n_answer: dict[str, int] = {}
    for r in train_rows:
        if M.is_run_id(r.teacher):
            by_run.setdefault(r.teacher, {}).setdefault(r.prompt_id, r.letter)
            n_rows[r.teacher] = n_rows.get(r.teacher, 0) + 1
            n_answer[r.teacher] = n_answer.get(r.teacher, 0) + int(r.category == "answer")
    cache: dict = {}
    rep_rows: list[dict] = []
    letters_o: dict[str, dict[str, dict]] = {t: {} for t in teachers}
    targets_o: dict[str, dict[str, str]] = {}
    for run in sorted(by_run):
        k = M.parse_run_id(run)
        targets, source = sft_letters(k.teacher, k.version, k.seed, sft_dir, teacher_dir, prompts_train, variants, cfg, cache)
        row = dict(run_id=run, teacher=k.teacher, version=k.version, seed=k.seed, n_rows=n_rows[run], answer_rate=n_answer[run] / n_rows[run], sft_source=source)
        if targets is None:
            row.update(n_targets=0, n_scored=0, n_missing=0, n_no_letter=0, n_match=0, accuracy=np.nan, passed=None)
        else:
            row.update(M.train_reproduction(by_run[run], targets))
            row["passed"] = bool(row["n_missing"] == 0 and row["accuracy"] >= E1A_MIN) if k.version == "O" else None
            if k.version == "O" and k.teacher in teachers:
                letters_o[k.teacher][run] = by_run[run]
                targets_o[k.teacher] = targets
        rep_rows.append(row)
    rep = pd.DataFrame(rep_rows, columns=["run_id", "teacher", "version", "seed", "n_rows", "answer_rate", "n_targets", "n_scored", "n_missing", "n_no_letter", "n_match", "accuracy", "passed", "sft_source"])
    fam_of = {pid: p.family_id for pid, p in prompts_train.items()}
    con_rows = []
    for t in teachers:
        if t not in targets_o:
            continue
        for o in teachers:
            if o == t:
                continue
            if o not in targets_o:
                tgt_o, _ = sft_letters(o, "O", 1, sft_dir, teacher_dir, prompts_train, variants, cfg, cache)
                if tgt_o is None:
                    continue
                targets_o[o] = tgt_o
            res = M.contested_alignment(letters_o[t], targets_o[t], targets_o[o], n_boot=n_boot, seed=seed, family_of=fam_of)
            con_rows.append(dict(teacher=t, other=o, **res, passed=bool(res["ci_lo"] > E1B_MIN_CI_LO) if not np.isnan(res["ci_lo"]) else None))
    con = pd.DataFrame(con_rows, columns=["teacher", "other", "n_items", "n_families", "n_runs", "n_pairs", "share", "ci_lo", "ci_hi", "passed"])
    # verdict
    pending = {"e1a": "pending", "e1b": "pending"}
    if not by_run:
        return rep, con, {**pending, "e1": "pending (no train readouts)"}
    o_rep = rep[rep["version"] == "O"]
    missing_t = [t for t in teachers if t not in set(o_rep["teacher"])]
    if missing_t or o_rep["accuracy"].isna().any():
        return rep, con, {**pending, "e1": f"pending (train readouts or SFT targets missing for {', '.join(missing_t) or 'some O runs'})"}
    e1a = "pass" if bool(o_rep["passed"].all()) else "fail"
    if len(con) < len(teachers) * (len(teachers) - 1) or con["passed"].isna().any():
        return rep, con, {"e1a": e1a, "e1b": "pending", "e1": "pending (contested-item targets missing for some teacher pair)"}
    e1b = "pass" if bool(con["passed"].all()) else "fail"
    return rep, con, {"e1a": e1a, "e1b": e1b, "e1": f"{'PASS' if e1a == e1b == 'pass' else 'FAIL'} (E1a {e1a}, E1b {e1b})"}


# --------------------------------------------------------------------------- verdicts


def e2_primary(pooled: pd.DataFrame, teachers: list[str]) -> tuple[str, pd.DataFrame]:
    """Pre-registered E2: per-teacher seed-mean delta_rho > 0 with Holm p < ALPHA; PASS / PARTIAL / FAIL over the teachers."""
    po = pooled[pooled["version"] == "O"].copy() if pooled is not None and not pooled.empty else pd.DataFrame()
    if po.empty:
        return "pending (no pooled O profiles)", po
    po["passed"] = (po["delta_rho"] > 0) & (po["p_holm"] < ALPHA)
    return M.e2_primary_verdict(int(po["passed"].sum()), len(teachers)), po


def e2_secondary(d: dict) -> str:
    return M.e2_secondary_verdict(d, ALPHA)


def reliability_lines(rel: dict[str, float], ceilings: dict[str, float], teachers: list[str], split: str) -> list[str]:
    test_r = RELIABILITY["test"]
    below = [t for t in teachers if test_r.get(t, np.nan) < RELIABILITY_GATE]
    fmt_pair = lambda t, r: f"{t} r {_fmt(r)} -> ceiling {_fmt(M.reliability_ceiling(r))}"  # noqa: E731
    lines = [f"Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its "
             "reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own "
             "teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings "
             f"apply to every entry of that column). This split ({split}): " + ", ".join(fmt_pair(t, rel.get(t, np.nan)) for t in teachers)
             + "; test split: " + ", ".join(fmt_pair(t, test_r.get(t, np.nan)) for t in teachers) + "."]
    if len(below) >= 2:
        lines.append(f"E0 gate (docs/03 §1, on the raw split-half r): {len(below)} of {len(teachers)} teachers ({', '.join(below)}) are below {RELIABILITY_GATE} on the test split, so E0's P2 fails: "
                     "per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the "
                     "pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).")
    else:
        lines.append(f"E0 gate (docs/03 §1): fewer than 2 teachers below {RELIABILITY_GATE} on the test split; the gate does not fire.")
    return lines + [""]


# --------------------------------------------------------------------------- summary


def summary_md(ctx: dict) -> str:
    tab, null, teachers, split, variants = ctx["tab"], ctx["null"], ctx["teachers"], ctx["split"], ctx["variants"]
    ceilings: dict[str, float] = ctx["ceilings"]
    rel: dict[str, float] = ctx["reliability"]
    lines = [f"# E1 / E2 summary ({split}, variants {', '.join(variants)}; {FROZEN}, corrected 2026-10-05: family-level inference; auto-generated)", ""]
    if tab.empty:
        cat_rates, n_rows = ctx.get("cat_rates"), ctx.get("n_student_rows", 0)
        if n_rows and cat_rates is not None and not cat_rates.empty:
            lines += [f"{n_rows} student rows were loaded but NO cell passed the readout (every row is `malformed`, "
                      "i.e. P(' A')+P('A')+P(' B')+P('B') < answer_mass_min): the students do not answer with a letter. "
                      "Per-run answer rates (category_rates.csv):", ""]
            lines += _md_table(cat_rates, ["teacher", "variant", "answer", "malformed", "n"])
            return "\n".join(lines)
        return "\n".join(lines + ["No student runs found."])

    grid_p, dose, pooled_p, inh_p = ctx["grid_partial"], ctx["dose"], ctx["pooled_partial"], ctx["inh_partial"]
    e1_states = ctx["e1_states"]
    e1_verdict, e1a, e1b = e1_states["e1"], e1_states["e1a"], e1_states["e1b"]
    has_base = ctx["base_name"] is not None and not inh_p.empty
    prim_verdict, po = e2_primary(ctx["pooled"], teachers)
    D, D_t0, D_raw = ctx["D"], ctx["D_t0"], ctx["D_raw"]
    sec_verdict = e2_secondary(D)
    rep_o = ctx["rep"][ctx["rep"]["version"] == "O"] if len(ctx["rep"]) else ctx["rep"]
    con = ctx["con"]

    lines += ["## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)", ""]
    if split != "test":
        lines += [f"**{split} = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): "
                  "the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.", ""]
    prim_val = "; ".join(f"{r['teacher']} {_fmt(r['delta_rho'])} {_ci(r['ci_lo'], r['ci_hi'])} p_perm {_fmt(r['p_perm'])} (null mean {_fmt(r['perm_null_mean'])}) p_holm {_fmt(r['p_holm'])}" for _, r in po.sort_values("teacher").iterrows()) if len(po) else "nan"
    n_prim = int(po["passed"].sum()) if len(po) else 0
    lines += ["| test | rule | value | verdict |", "|---|---|---|---|",
              f"| E1a | every O run reproduces >= {E1A_MIN:.2f} of its SFT target letters (all prompts read out) | min accuracy {_fmt(rep_o['accuracy'].min()) if len(rep_o) else 'nan'}, min answer rate {_fmt(rep_o['answer_rate'].min()) if len(rep_o) else 'nan'} | {e1a} |",
              f"| E1b | contested training items: ci_lo of the own-teacher share > {E1B_MIN_CI_LO} vs every other teacher | min ci_lo {_fmt(con['ci_lo'].min()) if len(con) else 'nan'} | {e1b} |",
              f"| **E1** | E1a and E1b for all teachers | | **{e1_verdict}** |",
              f"| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < {ALPHA}; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | {prim_val}; {n_prim}/{len(teachers)} pass | **{prim_verdict}** |",
              f"| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < {ALPHA}, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D {_fmt(D.get('D'))} {_ci(D.get('ci_lo'), D.get('ci_hi'))}, p {_fmt(D.get('p_perm'))}; D_specific {_fmt(D.get('D_specific'))} {_ci(D.get('ci_specific_lo'), D.get('ci_specific_hi'))}, D_shared {_fmt(D.get('D_shared'))} ({D.get('n_families', 0)} families, {D.get('n_perm', 0)} perm / {D.get('n_boot', 0)} boot) | **{sec_verdict}** |", ""]
    lines += reliability_lines(rel, ceilings, teachers, split)
    lines += ["Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, "
              "teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level "
              f"reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the {ctx.get('n_common_families', 'nan')} families complete for every O run, every teacher and r_0.", ""]

    # ---- descriptive table
    lines += ["## Descriptive (no verdict)", ""]
    te_grid = grid_p.get("teacher_exact", {}) if grid_p else {}
    te_dose = dose.get("teacher_exact", {}) if dose else {}
    bc = ctx["base_control"]
    if len(bc):
        top = bc.sort_values("rank").iloc[0]
        bc_val = f"closest teacher {top['teacher']}: rho {_fmt(top['rho'])} {_ci(top['ci_lo'], top['ci_hi'])}, margin over the next {_fmt(top['margin'])} {_ci(top['margin_ci_lo'], top['margin_ci_hi'])} ({int(top['n_families'])} families)"
        bc_note = "control holds (no teacher preferred before training)" if top["margin_ci_lo"] <= 0 else f"S_0 is systematically closest to {top['teacher']} before training: the confound the partial rho controls for"
    else:
        bc_val, bc_note = "nan", "pending (no base readout)"
    po_p = pooled_p[pooled_p["version"] == "O"] if not pooled_p.empty else pooled_p
    p3_val = "; ".join(f"{r['teacher']} {_fmt(r['delta_rho'])} {_ci(r['ci_lo'], r['ci_hi'])} p_holm {_fmt(r['p_holm'])}" for _, r in po_p.sort_values("teacher").iterrows()) if len(po_p) else "nan"
    lines += ["| item | value | note |", "|---|---|---|",
              f"| mean deltaRhoPartial over the O runs (r_0 = {ctx['base_name'] or 'absent'}) | {_fmt(grid_p.get('observed'))} | teacher-level exact p {_fmt(te_grid.get('p'))} (rank {te_grid.get('rank')} of {te_grid.get('n_assignments', 0)} relabellings, floor {_fmt(te_grid.get('floor'))}); the run-level null (mean {_fmt(grid_p.get('null_mean'))}, sd {_fmt(grid_p.get('null_sd'))}, p {_fmt(grid_p.get('p'))}, {grid_p.get('n_perm', 0)} assignments) is pseudo-replicated |",
              f"| suggestibility dose-response: slope of s_run on own s_T | {_fmt(dose.get('slope'))} (pearson {_fmt(dose.get('pearson'))}, seed-noise sd {_fmt(dose.get('seed_noise_sd'))}, ordering preserved {dose.get('ordering_preserved')}) | teacher-level exact p {_fmt(te_dose.get('p'))} (rank {te_dose.get('rank')} of {te_dose.get('n_assignments', 0)}, floor {_fmt(te_dose.get('floor'))}); run-level p {_fmt(dose.get('p'))} is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |",
              f"| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | {p3_val} | supportive only |",
              f"| D on T0 only (unseen framing; r demeaned over T0 + seen) | {_fmt(D_t0.get('D'))} {_ci(D_t0.get('ci_lo'), D_t0.get('ci_hi'))}, p {_fmt(D_t0.get('p_perm'))} ({D_t0.get('n_families', 0)} families) | exploratory |",
              f"| raw D (no r_0 control), seen framings | {_fmt(D_raw.get('D'))} {_ci(D_raw.get('ci_lo'), D_raw.get('ci_hi'))}, p {_fmt(D_raw.get('p_perm'))} | exploratory; the partial D above is the pre-declared one |",
              f"| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | {_fmt(D.get('D_scalefree'))} {_ci(D.get('ci_scalefree_lo'), D.get('ci_scalefree_hi'))} | exploratory alternative to the D_specific guard |",
              f"| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | {bc_val} | {bc_note} |", ""]

    # ---- E2 primary table
    lines += ["## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)", ""]
    if len(po):
        lines += _md_table(_with_ceiling(po.sort_values("teacher"), ceilings), ["teacher", "n_seeds", "n_families", "rho_own", "ceiling", "rho_over_ceiling", "rho_other_max", "other_argmax", "delta_rho", "ci_lo", "ci_hi", "p_perm", "perm_null_mean", "perm_null_sd", "p_holm", "passed"])
        lines += ["The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.", ""]
        lines += ["Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):", ""]
        lines += _kv_table(ctx["grid"], ["observed", "null_mean", "null_sd", "p", "method", "n_perm", "n_runs"])
    else:
        lines += ["pending: no O runs with a matching teacher profile yet", ""]

    # ---- E2 secondary
    lines += [f"## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = {ctx['base_name'] or 'absent'}, seen framings (e2_secondary_D.json)", ""]
    if D and D.get("matrix"):
        lines += _kv_table(D, ["D", "ci_lo", "ci_hi", "p_perm", "null_mean", "null_sd", "D_raw", "n_families", "n_perm", "n_boot"])
        lines += ["Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher "
                  "information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):", ""]
        lines += _kv_table(D, ["D_shared", "D_specific", "ci_specific_lo", "ci_specific_hi", "p_perm_specific", "null_mean_specific", "null_sd_specific", "D_scalefree", "ci_scalefree_lo", "ci_scalefree_hi"])
        lines += ["Row scales (sd of each pooled student's residual given r_0): " + ", ".join(f"{a} {_fmt(v)}" for a, v in D.get("row_scale", {}).items()) + ".", ""]
        rows = []
        teacher_of = {v["student"]: t for t, v in D["per_teacher"].items()}
        for a, r in D["matrix"].items():
            own_t = teacher_of.get(a)
            pt = D["per_teacher"].get(own_t, {})
            rows.append({"student": a, **{f"partial__{t}": v for t, v in r.items()}, "ceiling_own": ceilings.get(own_t, np.nan), "contrast": pt.get("contrast", np.nan), "contrast_specific": pt.get("contrast_specific", np.nan)})
        lines += ["Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):", ""]
        lines += _md_table(_ceiling_row(pd.DataFrame(rows), ceilings, "partial__", "student"), ["student"] + [f"partial__{t}" for t in D["teachers"]] + ["ceiling_own", "contrast", "contrast_specific"])
        rows = [{"student": a, **{f"specific__{t}": v for t, v in r.items()}} for a, r in D["matrix_specific"].items()]
        lines += ["Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):", ""] + _md_table(pd.DataFrame(rows), ["student"] + [f"specific__{t}" for t in D["teachers"]])
        rows = [{"student": a, **{f"raw__{t}": v for t, v in r.items()}} for a, r in D["matrix_raw"].items()]
        lines += ["Raw (non-partial) matrix on the same cells (last row = column ceilings):", ""] + _md_table(_ceiling_row(pd.DataFrame(rows), ceilings, "raw__", "student"), ["student"] + [f"raw__{t}" for t in D["teachers"]])
        if D_t0 and D_t0.get("matrix"):
            rows = [{"student": a, **{f"partial__{t}": v for t, v in r.items()}} for a, r in D_t0["matrix"].items()]
            lines += ["T0-only matrix (exploratory; last row = column ceilings):", ""] + _md_table(_ceiling_row(pd.DataFrame(rows), ceilings, "partial__", "student"), ["student"] + [f"partial__{t}" for t in D_t0["teachers"]])
    else:
        lines += ["pending: no base run (version B) with a prior profile, or fewer than 2 teachers with O runs", ""]

    # ---- suggestibility groups
    lines += [f"## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; {ctx.get('n_common_families', 'nan')} common families)", ""]
    sg, sgp = ctx["sugg_groups"], ctx["sugg_pairs"]
    if len(sg):
        lines += _md_table(sg, ["group", "n_profiles", "n_families", "s", "ci_lo", "ci_hi"])
        lines += ["Pairwise differences (students of A - students of B; students - own teacher; students - base prior):", ""]
        if len(sgp):
            is_stud = sgp["a"].str.startswith("students:")
            own_pair = pd.Series([_is_own_pair(a, b) for a, b in zip(sgp["a"], sgp["b"])], index=sgp.index)
            keep = sgp[(is_stud & sgp["b"].str.startswith("students:")) | own_pair | (is_stud & sgp["b"].eq("base_prior"))]
            lines += _md_table(keep, ["a", "b", "diff", "ci_lo", "ci_hi"])
    else:
        lines += ["pending", ""]
    sug = ctx["sugg"]
    other = sug[~sug["kind"].isin(["teacher"]) & ~((sug["kind"] == "run") & (sug["version"] == "O"))]
    if len(other):
        lines += ["Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):", ""]
        lines += _md_table(other, ["who", "kind", "delta_T5", "delta_T6", "s", "n_families"])
    if dose.get("teachers"):
        dt = pd.DataFrame([{"teacher": t, **v} for t, v in dose["teachers"].items()])
        lines += ["Dose-response inputs per teacher (dose_response.json):", ""] + _md_table(dt, ["teacher", "s_teacher", "s_student_mean", "s_student_sd", "n_runs"])

    # ---- E1 tables
    lines += ["## E1a: training-label reproduction (e1_train_reproduction.csv)", ""]
    if len(ctx["rep"]):
        lines += _md_table(ctx["rep"].sort_values(["teacher", "version", "seed"]), ["run_id", "n_rows", "answer_rate", "n_targets", "n_scored", "n_missing", "n_no_letter", "accuracy", "passed", "sft_source"])
    else:
        lines += ["pending: no eval/train_responses.jsonl (run `scripts/12_eval_student.py --run-dir <run> --split train` for every O and R run)", ""]
    lines += ["## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)", ""]
    if len(ctx["con"]):
        lines += _md_table(ctx["con"], ["teacher", "other", "n_items", "n_families", "n_runs", "n_pairs", "share", "ci_lo", "ci_hi", "passed"])
    else:
        lines += ["pending (needs the train readouts and the SFT files or train demos)", ""]

    lines += ["## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)", ""]
    cols = ["run_id", "answer_rate", "order_gap_mean", "n_families", "agree_own", "agree_other_max", "jsd_own", "flip_rate", "mean_jsd"]
    lines += _md_table(tab.sort_values(["teacher", "version", "seed"]), cols)
    lines += _md_table(tab.sort_values(["teacher", "version", "seed"]), ["run_id"] + [f"agree__{t}" for t in teachers] + [f"jsd__{t}" for t in teachers])
    agg_cols = [c for c in ("answer_rate", "agree_own", "agree_other_max", "jsd_own", "flip_rate", "mean_jsd") if c in tab]
    g = tab.groupby(["teacher", "version"])[agg_cols].mean().reset_index()
    g["n_seeds"] = tab.groupby(["teacher", "version"]).size().values
    lines += ["### Seed means", ""] + _md_table(g, ["teacher", "version", "n_seeds"] + agg_cols)

    # ---- per-run inheritance (descriptive)
    lines += [f"## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = {ctx['base_name'] or 'absent'} (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)", ""]
    if has_base:
        core = inh_p[inh_p["run_id"].map(lambda r: M.parse_run_id(r).version == "O")]
        lines += _md_table(_ceiling_row(_with_ceiling(core.sort_values(["teacher", "run_id"]), ceilings), ceilings, "rho__", "run_id"), ["run_id", "n_families", "rho_base", "rho_own", "ceiling", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "perm_null_mean", "ci_lo", "ci_hi"] + [f"rho__{t}" for t in teachers])
        gm = core.groupby("teacher")["delta_rho"].agg(["mean", "std", "count"]).reset_index()
        lines += ["Seed means of deltaRhoPartial per teacher:", ""] + _md_table(gm, ["teacher", "mean", "std", "count"])
        lines += ["Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):", ""]
        lines += _kv_table(te_grid, ["observed", "p", "rank", "n_assignments", "floor"])
    else:
        lines += ["pending: no base run (version B) with a prior profile; evaluate S_0 on this split first", ""]
    if "delta_rho" in tab and tab["delta_rho"].notna().any():
        lines += ["Uncontrolled delta_rho per run (inheritance.csv):", ""]
        lines += _md_table(_with_ceiling(tab.sort_values(["teacher", "version", "seed"]).dropna(subset=["delta_rho"]), ceilings), ["run_id", "rho_own", "ceiling", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "perm_null_mean", "ci_lo", "ci_hi"])
    byv = ctx["inh_partial_by_variant"]
    if len(byv):
        bv = byv[byv["run_id"].map(lambda r: M.parse_run_id(r).version == "O")].groupby(["teacher", "variant"])["delta_rho"].agg(["mean", "std", "count"]).reset_index()
        lines += ["### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)", ""]
        lines += _md_table(bv, ["teacher", "variant", "mean", "std", "count"])
    if len(po_p):
        lines += ["### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)", ""]
        lines += _md_table(_with_ceiling(po_p.sort_values("teacher"), ceilings), ["teacher", "n_seeds", "n_families", "rho_base", "rho_own", "ceiling", "rho_other_max", "other_argmax", "delta_rho", "ci_lo", "ci_hi", "p_perm", "perm_null_mean", "p_holm"])
    if len(bc):
        lines += ["### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)", ""]
        lines += _md_table(_with_ceiling(bc, ceilings, rho_col="rho"), ["who", "profile", "teacher", "n_families", "rho", "ceiling", "ci_lo", "ci_hi", "rank", "margin", "margin_ci_lo", "margin_ci_hi"])

    # ---- disclosure of superseded rule versions
    lines += ["## Pre-revision rule versions (disclosure; none of these is the verdict)", ""]
    lines += ["### E1 (old): every O seed agree_own > agree_other_max", ""]
    core = tab[tab["version"] == "O"].dropna(subset=["agree_own"])
    if core.empty:
        lines.append("no O runs with a matching teacher profile yet")
    for t, gt in core.groupby("teacher"):
        ok = int((gt["agree_own"] > gt["agree_other_max"]).sum())
        lines.append(f"- {t}: {ok}/{len(gt)} seeds pass -> {'ok' if ok == len(gt) else ('partial' if ok else 'fail')} (old rule, not the verdict)")
    lines.append("")
    lines += ["### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)", ""]
    lines += [f"- P1 mean deltaRhoPartial {_fmt(grid_p.get('observed'))} vs run-reassignment null mean {_fmt(grid_p.get('null_mean'))} sd {_fmt(grid_p.get('null_sd'))}, p {_fmt(grid_p.get('p'))} ({grid_p.get('method', 'none')}, {grid_p.get('n_perm', 0)} assignments) -> not a test; teacher-level exact p {_fmt(te_grid.get('p'))}",
              f"- P2 slope {_fmt(dose.get('slope'))}, run-reassignment p {_fmt(dose.get('p'))} ({dose.get('method', 'none')}, {dose.get('n_perm', 0)} assignments) -> not a test; teacher-level exact p {_fmt(te_dose.get('p'))}", ""]
    lines += ["### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)", ""]
    lines += [f"- D {_fmt(D.get('D'))} {_ci(D.get('ci_lo'), D.get('ci_hi'))} p {_fmt(D.get('p_perm'))} alone would read {'pass' if D and not np.isnan(D.get('ci_lo', np.nan)) and D['D'] > 0 and D['ci_lo'] > 0 and D['p_perm'] < ALPHA else 'fail / pending'}; "
              f"the frozen rule (version 5) also needs D_specific {_fmt(D.get('D_specific'))} {_ci(D.get('ci_specific_lo'), D.get('ci_specific_hi'))} above 0 -> {sec_verdict}", ""]

    lines += ["## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)", ""]
    lines += _md_table(null, ["metric", "teacher", "version", "n_pairs", "mean", "sd", "q95"])
    lines += ["Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. ",
              "Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). ",
              "The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate."]
    return "\n".join(lines)


def _is_own_pair(a: str, b: str) -> bool:
    return a.startswith("students:") and b == "teacher:" + a[len("students:") :]


# --------------------------------------------------------------------------- main


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--runs-dir", default=None, help="default: config paths.runs_dir")
    ap.add_argument("--student", default=None, help="student_model_short to select runs/{student}/*; default: config value")
    ap.add_argument("--runs-glob", default=None, help="explicit glob of response files (overrides --runs-dir/--student)")
    ap.add_argument("--split", default="test", choices=["dev", "test", "pilot"])
    ap.add_argument("--teacher-dir", default=None, help="dir with {teacher}_{split}_profile.jsonl and {teacher}_train_demo.jsonl; default: config paths.teacher_dir")
    ap.add_argument("--teacher-files", default=None, help="explicit profiles, 'gpt4o=path,claude46=path' (overrides --teacher-dir/--teachers)")
    ap.add_argument("--teachers", default=None, help="comma list; default: config teachers")
    ap.add_argument("--prompts", default=None, help="default: config paths.prompts_{split}")
    ap.add_argument("--prompts-train", default=None, help="train prompts for E1a / E1b; default: config paths.prompts_train")
    ap.add_argument("--sft-dir", default=None, help="SFT files for E1a / E1b targets; default: config paths.sft_dir (O files absent there are rebuilt from the train demos)")
    ap.add_argument("--variants", default=None, help="comma list of framings for the metrics (default: config data.variants = T1,T3,T5,T6)")
    ap.add_argument("--reliability", default=None, help="teacher order split-half reliability r for this split, 'gpt4o=0.69,claude46=0.33' (default: docs/E0_results §13 values for dev / test); the printed ceiling is sqrt(2r / (1 + r))")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default="results/e1")
    ap.add_argument("--n-perm", type=int, default=10_000)
    ap.add_argument("--n-boot", type=int, default=10_000)
    ap.add_argument("--exact-max", type=int, default=1_000_000, help="enumerate every run -> teacher assignment for the descriptive P1 / P2 numbers when there are at most this many (0 = random n_perm)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    teacher_files = dict(kv.split("=", 1) for kv in args.teacher_files.split(",")) if args.teacher_files else None
    teachers = list(teacher_files) if teacher_files else (args.teachers.split(",") if args.teachers else list(cfg["teachers"]))
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    student = args.student or cfg["student_model_short"]
    reliability = {k: float(v) for k, v in (kv.split("=", 1) for kv in args.reliability.split(","))} if args.reliability else dict(RELIABILITY.get(args.split, {}))
    ceilings = {t: M.reliability_ceiling(r) for t, r in reliability.items()}  # sqrt(2r / (1 + r)); the raw r stays the E0 gate quantity

    # students
    if args.runs_glob:
        files = sorted(Path(".").glob(args.runs_glob)) if not Path(args.runs_glob).is_absolute() else sorted(Path("/").glob(args.runs_glob.lstrip("/")))
        student_rows = M.load_responses(files, pid)
        train_files = sorted({Path(str(f).replace(f"{args.split}_responses.jsonl", "train_responses.jsonl")) for f in files})
        train_rows = M.load_responses([f for f in train_files if f.exists() and f.name == "train_responses.jsonl"])
    else:
        runs_dir = Path(args.runs_dir) if args.runs_dir else cfg["paths"]["runs_dir"]
        student_rows = [r for r in M.load_run_responses(runs_dir, args.split, student) if r.prompt_id in pid]
        train_rows = M.load_run_responses(runs_dir, "train", student)
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
    print(f"students: {len(student_rows)} rows, {len({r.teacher for r in student_rows})} runs; teachers: {len(teacher_rows)} rows, {len({r.teacher for r in teacher_rows})} profiles; "
          f"train readouts: {len({r.teacher for r in train_rows})} runs")
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

    # E2 primary (pre-registered, uncontrolled): per run, per variant, seed-mean per teacher with Holm
    shifts_s, shifts_t = P.framing_shifts(sym_s, variants), P.framing_shifts(sym_t, variants)
    own = {r: M.parse_run_id(r).teacher for r in sym_s["teacher"].unique() if M.is_run_id(r)}
    inh = M.inheritance(shifts_s, shifts_t, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
    inh.to_csv(out / "inheritance.csv", index=False)
    M.inheritance(shifts_s, shifts_t, own, variants, n_perm=0, n_boot=0, by_variant=True).to_csv(out / "inheritance_by_variant.csv", index=False)
    pooled = M.pooled_inheritance(shifts_s, shifts_t, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
    pooled.to_csv(out / "inheritance_pooled.csv", index=False)
    is_o = lambda r: M.parse_run_id(r).version == "O"  # noqa: E731
    core = inh[inh["run_id"].map(is_o)] if not inh.empty else inh
    grid = M.grid_permutation(core, n_perm=args.n_perm, seed=args.seed) if len(core) else {}
    (out / "grid_permutation.json").write_text(json.dumps(grid, indent=2), encoding="utf-8")

    # base prior covariate r_0 (no mass gate): partial correlations (descriptive P1 / P3) and the S_0 control row
    base_runs = sorted(r for r in {x.teacher for x in student_rows} if M.is_run_id(r) and M.parse_run_id(r).version == "B")
    base_name: Optional[str] = None
    shifts_0 = pd.DataFrame(columns=["teacher", "family_id", "variant", "p", "r"])
    if base_runs:
        base_name = base_runs[0]
        base_rows = [r for r in student_rows if r.teacher == base_name]
        shifts_0 = M.base_prior_shifts(base_rows, prompts, variants)
        if len(base_runs) > 1:
            print(f"warning: several base runs {base_runs}; using {base_name} as the covariate", file=sys.stderr)
        print(f"base prior profile {base_name}: {shifts_0['family_id'].nunique()} complete families without the mass gate")
    empty_p = pd.DataFrame(columns=list(inh.columns) + ["control", "rho_base"])
    inh_p, inh_p_byv, pooled_p, grid_p = empty_p, empty_p, pd.DataFrame(columns=list(pooled.columns) + ["control", "rho_base"]), {}
    o_runs = sorted(r for r in own if is_o(r))
    pooled_by_t = {t: M.pooled_shifts(shifts_s, [r for r in o_runs if own[r] == t], f"{student}.{t}_O_pooled") for t in present if any(own[r] == t for r in o_runs)}
    D, D_t0, D_raw = {}, {}, {}
    base_control = pd.DataFrame()
    if not shifts_0.empty:
        inh_p = M.inheritance_partial(shifts_s, shifts_t, shifts_0, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
        inh_p_byv = M.inheritance_partial(shifts_s, shifts_t, shifts_0, own, variants, n_perm=0, n_boot=0, by_variant=True)
        if "T0" in set(sym_s["variant"]) and "T0" in set(sym_t["variant"]):  # unseen framing: r demeaned over T0 + seen variants, T0 cells only
            v0 = ["T0", *variants]
            s0, t0 = P.framing_shifts(sym_s, v0), P.framing_shifts(sym_t, v0)
            z0 = M.base_prior_shifts([r for r in student_rows if r.teacher == base_name], prompts, v0)
            if not z0.empty and not s0.empty and not t0.empty:
                u = M.inheritance_partial(s0, t0, z0, own, v0, n_perm=0, n_boot=0, by_variant=True)
                inh_p_byv = pd.concat([inh_p_byv, u[u["variant"] == "T0"]], ignore_index=True)
                pooled_t0 = {t: M.pooled_shifts(s0, [r for r in o_runs if own[r] == t], f"{student}.{t}_O_pooled") for t in pooled_by_t}
                D_t0 = M.joint_partial_D(pooled_t0, t0, z0, v0, cells=["T0"], n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
        pooled_p = M.pooled_inheritance_partial(shifts_s, shifts_t, shifts_0, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
        core_p = inh_p[inh_p["run_id"].map(is_o)] if not inh_p.empty else inh_p
        grid_p = M.grid_permutation_partial(core_p, n_perm=args.n_perm, seed=args.seed, exact_max=args.exact_max) if len(core_p) else {}
        if len(pooled_by_t) >= 2:
            D = M.joint_partial_D(pooled_by_t, shifts_t, shifts_0, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
            D_raw = M.joint_partial_D(pooled_by_t, shifts_t, None, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
        base_control = M.base_prior_control(shifts_0, shifts_t, variants, n_boot=args.n_boot, seed=args.seed)
    inh_p.to_csv(out / "inheritance_partial.csv", index=False)
    inh_p_byv.to_csv(out / "inheritance_partial_by_variant.csv", index=False)
    pooled_p.to_csv(out / "inheritance_partial_pooled.csv", index=False)
    (out / "grid_permutation_partial.json").write_text(json.dumps(grid_p, indent=2), encoding="utf-8")
    base_control.to_csv(out / "base_control.csv", index=False)
    _dump = lambda x: x.item() if isinstance(x, np.generic) else (None if isinstance(x, float) and np.isnan(x) else str(x))  # noqa: E731  (json default)
    (out / "e2_secondary_D.json").write_text(json.dumps({"seen_partial": D, "T0_partial": D_t0, "seen_raw": D_raw, "verdict": e2_secondary(D), "alpha": ALPHA,
                                                         "rule": "pre-declared secondary: D > 0, family-bootstrap 95% CI of D excludes 0, family-permutation p < alpha, and the student-specific part D_specific (D = D_shared + D_specific) has a family-bootstrap CI above 0 (seen framings, partial given r_0)",
                                                         "reliability_split_half_r": reliability, "ceiling_sqrt_spearman_brown": ceilings},
                                                        indent=2, default=_dump), encoding="utf-8")

    # suggestibility (descriptive): per profile on ONE family set (complete for every O run, every teacher and r_0), per group with CIs
    fam_common = M.complete_families(pd.concat([shifts_s, shifts_t, shifts_0]), [*o_runs, *present] + ([base_name] if not shifts_0.empty else []), variants) if o_runs else []
    print(f"suggestibility family set: {len(fam_common)} families complete for {len(o_runs)} O runs, {len(present)} teachers and r_0")
    sug_t = M.suggestibility_by_run(shifts_t, families=fam_common).assign(kind="teacher", teacher=lambda d: d["who"], version="", seed=np.nan)
    sug_s = M.suggestibility_by_run(shifts_s, families=fam_common)
    keys = M.run_keys_table(sug_s["who"]).set_index("run_id") if len(sug_s) else pd.DataFrame(columns=["teacher", "version", "seed"])
    sug_s = sug_s.assign(kind="run", teacher=sug_s["who"].map(keys["teacher"]), version=sug_s["who"].map(keys["version"]), seed=sug_s["who"].map(keys["seed"]))
    sug_0 = M.suggestibility_by_run(shifts_0, families=fam_common).assign(kind="base_prior", teacher="base", version="B", seed=0)
    sugg = pd.concat([sug_t, sug_s, sug_0], ignore_index=True)[["who", "kind", "teacher", "version", "seed", "delta_T5", "delta_T6", "s", "n_families"]]
    sugg.to_csv(out / "suggestibility_runs.csv", index=False)
    s_runs = {r: float(s) for r, s, v in zip(sug_s["who"], sug_s["s"], sug_s["version"]) if v == "O"}
    s_teachers = {t: float(s) for t, s in zip(sug_t["who"], sug_t["s"])}
    dose = M.dose_response(s_runs, s_teachers, own, n_perm=args.n_perm, seed=args.seed, exact_max=args.exact_max)
    dose["n_common_families"] = len(fam_common)
    dose["descriptive"] = {"R_runs": {r: float(s) for r, s, v in zip(sug_s["who"], sug_s["s"], sug_s["version"]) if v == "R"},
                           "base_gated": {r: float(s) for r, s, v in zip(sug_s["who"], sug_s["s"], sug_s["version"]) if v == "B"},
                           "base_prior": {r: float(s) for r, s in zip(sug_0["who"], sug_0["s"])}}
    (out / "dose_response.json").write_text(json.dumps(dose, indent=2, default=_dump), encoding="utf-8")
    groups = {f"students:{t}": [r for r in o_runs if own[r] == t] for t in present if any(own[r] == t for r in o_runs)}
    groups |= {f"teacher:{t}": [t] for t in present}
    r_runs = sorted(r for r in own if M.parse_run_id(r).version == "R")
    if r_runs:
        groups["students:R"] = r_runs
    prior_name = f"{base_name}:prior" if base_name else None
    shifts_prior = shifts_0.assign(teacher=prior_name) if not shifts_0.empty else shifts_0
    if base_name:
        groups["base_prior"] = [prior_name]
    sugg_groups, sugg_pairs = M.suggestibility_groups(pd.concat([shifts_s, shifts_t, shifts_prior]), groups, families=fam_common, n_boot=args.n_boot, seed=args.seed)
    sugg_groups.to_csv(out / "suggestibility_groups.csv", index=False)
    sugg_pairs.to_csv(out / "suggestibility_group_pairs.csv", index=False)

    # revised E1: training-label reproduction and contested items
    prompts_train = M.load_prompts(resolve(args.prompts_train) if args.prompts_train else cfg["paths"]["prompts_train"]) if train_rows else {}
    sft_dir = Path(args.sft_dir) if args.sft_dir else cfg["paths"]["sft_dir"]
    rep, con, e1_states = e1_train_tables(train_rows, present, sft_dir, teacher_dir, prompts_train, variants, cfg, n_boot=args.n_boot, seed=args.seed)
    rep.to_csv(out / "e1_train_reproduction.csv", index=False)
    con.to_csv(out / "e1_contested.csv", index=False)

    nulls = []
    if not tab.empty:
        for metric in ("agree_own", "jsd_own", "flip_rate", "mean_jsd", "delta_rho"):
            if metric in tab and tab[metric].notna().any():
                nulls.append(M.seed_noise_null(tab.dropna(subset=[metric]), metric))
        if len(inh_p):
            t2 = inh_p.merge(M.run_keys_table(inh_p["run_id"]), on=["run_id", "teacher"]).rename(columns={"delta_rho": "delta_rho_partial"})
            nulls.append(M.seed_noise_null(t2, "delta_rho_partial"))
    null = pd.concat(nulls, ignore_index=True) if nulls else pd.DataFrame(columns=["teacher", "version", "metric", "n_pairs", "mean", "sd", "q95"])
    null.to_csv(out / "seed_null.csv", index=False)

    ctx = dict(tab=tab, null=null, grid=grid, teachers=present, split=args.split, variants=variants, pooled=pooled, cat_rates=cat_rates, n_student_rows=len(student_rows),
               base_name=base_name, inh_partial=inh_p, inh_partial_by_variant=inh_p_byv, pooled_partial=pooled_p, grid_partial=grid_p, dose=dose, sugg=sugg,
               sugg_groups=sugg_groups, sugg_pairs=sugg_pairs, D=D, D_t0=D_t0, D_raw=D_raw, base_control=base_control, ceilings=ceilings, reliability=reliability,
               rep=rep, con=con, e1_states=e1_states, n_common_families=len(fam_common))
    (out / "summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote {len(list(out.glob('*.csv')))} CSVs + summary.md to {out}")
    print((out / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
