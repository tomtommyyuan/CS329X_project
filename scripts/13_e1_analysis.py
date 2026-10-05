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
consistency.csv, seen_vs_unseen.csv, e1_table.csv, inheritance.csv, inheritance_by_variant.csv, inheritance_pooled.csv,
seed_null.csv, grid_permutation.json (pre-revision rule), inheritance_partial.csv, inheritance_partial_by_variant.csv,
inheritance_partial_pooled.csv, grid_permutation_partial.json, suggestibility_runs.csv, dose_response.json,
e1_train_reproduction.csv, e1_contested.csv and summary.md. No figures.

Decision rules (frozen on dev 2026-10-05, replacing the rules that failed on dev; tasks/e1_plan.md §0, tasks/e2_plan.md §2):
  E1  E1a every O run reproduces >= 95% of its own SFT target letters on its training prompts (every prompt read out);
      E1b on contested training items (own teacher's label != another teacher's) the seed-pooled share of items where the
      student gives its own teacher's letter has a family-bootstrap 95% CI lower bound > 0.5 against each other teacher.
      Verdict = E1a and E1b for all three teachers; "pending (no train readouts)" until eval/train_responses.jsonl exist.
  E2  r_0 = the untrained base's prior profile (two-letter probabilities WITHOUT the 0.9 mass gate) is a covariate.
      P1 mean over the O runs of deltaRhoPartial = partial rho(r_s, r_own | r_0) - max_other partial rho(r_s, r_other | r_0),
         null = reassigning the runs to teachers keeping 5 per teacher (all 756,756 assignments), pass iff p < 0.05;
      P2 dose-response: slope of s_run = delta(T5) - delta(T6) on the own teacher's s_T across the O runs, both on the
         families complete for every O run, every teacher and r_0; p from the same reassignment null, pass iff slope > 0 and p < 0.05;
      P3 supportive: per-teacher deltaRhoPartial of the seed-mean profile, family permutation + Holm, >= 2/3 positive.
      Verdict = P1 and P2 both p < 0.05. The pre-revision pooled delta_rho tables are kept for transparency.
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


# --------------------------------------------------------------------------- summary


def summary_md(ctx: dict) -> str:
    tab, null, teachers, split, variants = ctx["tab"], ctx["null"], ctx["teachers"], ctx["split"], ctx["variants"]
    lines = [f"# E1 / E2 summary ({split}, variants {', '.join(variants)}; {FROZEN}; auto-generated)", ""]
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
    p1 = grid_p.get("p", np.nan)
    p2 = dose.get("p", np.nan)
    has_base = ctx["base_name"] is not None and not inh_p.empty
    po = pooled_p[pooled_p["version"] == "O"] if not pooled_p.empty else pooled_p
    n_p3 = int((po["delta_rho"] > 0).sum()) if len(po) else 0
    n_p3_sig = int(((po["delta_rho"] > 0) & (po["p_holm"] < ALPHA)).sum()) if len(po) else 0
    if not has_base:
        e2_verdict = "pending (no base readout for the covariate r_0)"
    elif np.isnan(p1) or np.isnan(p2):
        e2_verdict = "pending (fewer than 2 teachers with O runs)"
    else:
        e2_verdict = "PASS" if (p1 < ALPHA and dose["slope"] > 0 and p2 < ALPHA) else "FAIL"

    rep_o = ctx["rep"][ctx["rep"]["version"] == "O"] if len(ctx["rep"]) else ctx["rep"]
    con = ctx["con"]
    v_p1 = ("pass" if p1 < ALPHA else "fail") if not np.isnan(p1) else "pending"
    v_p2 = ("pass" if (dose["slope"] > 0 and p2 < ALPHA) else "fail") if not np.isnan(p2) else "pending"
    v_p3 = ("supportive" if n_p3 * 3 >= 2 * len(teachers) else "not supportive") if len(po) else "pending"
    lines += ["## Verdicts (rules frozen on dev 2026-10-05; test is evaluated once)", ""]
    if split != "test":
        lines += [f"**{split} = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): "
                  "the verdicts on this split are descriptive and PASS is expected by construction; only results/e1 (test) is confirmatory.", ""]
    lines += ["| test | rule | value | verdict |", "|---|---|---|---|",
              f"| E1a | every O run reproduces >= {E1A_MIN:.2f} of its SFT target letters (all prompts read out) | min accuracy {_fmt(rep_o['accuracy'].min()) if len(rep_o) else 'nan'}, min answer rate {_fmt(rep_o['answer_rate'].min()) if len(rep_o) else 'nan'} | {e1a} |",
              f"| E1b | contested training items: ci_lo of the own-teacher share > {E1B_MIN_CI_LO} vs every other teacher | min ci_lo {_fmt(con['ci_lo'].min()) if len(con) else 'nan'} | {e1b} |",
              f"| **E1** | E1a and E1b for all teachers | | **{e1_verdict}** |",
              f"| P1 | mean deltaRhoPartial over O runs vs teacher-assignment null, p < {ALPHA} | mean {_fmt(grid_p.get('observed'))}, p {_fmt(p1)} ({grid_p.get('method', 'none')}, {grid_p.get('n_perm', 0)} assignments) | {v_p1} |",
              f"| P2 | slope of s_run on own s_T > 0, assignment-permutation p < {ALPHA} | slope {_fmt(dose.get('slope'))}, p {_fmt(p2)} ({dose.get('method', 'none')}) | {v_p2} |",
              f"| P3 (supportive) | per-teacher pooled deltaRhoPartial > 0 (Holm p in table) on >= 2/3 teachers | {n_p3}/{len(teachers)} positive, {n_p3_sig}/{len(teachers)} with p_holm < {ALPHA} | {v_p3} |",
              f"| **E2** | P1 and P2 both p < {ALPHA} | | **{e2_verdict}** |", ""]
    lines += ["Conventions: exact p = share of all distinct run -> teacher assignments (the observed one included) with statistic >= observed "
              "(floor 1 / n_assignments); random-assignment and family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 "
              f"percentiles of the family bootstrap; P2's s_run and s_T are computed on the {ctx.get('n_common_families', 'nan')} families complete for every O run, every teacher and r_0.", ""]

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

    lines += [f"## E2 P1: deltaRhoPartial per O run, base prior r_0 = {ctx['base_name'] or 'absent'} (inheritance_partial.csv, grid_permutation_partial.json)", ""]
    if has_base:
        core = inh_p[inh_p["run_id"].map(lambda r: M.parse_run_id(r).version == "O")]
        lines += _md_table(core.sort_values(["teacher", "run_id"]), ["run_id", "n_families", "rho_base", "rho_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "ci_lo", "ci_hi"] + [f"rho__{t}" for t in teachers])
        lines += ["Teacher-assignment null (runs reassigned to teachers, 5 per teacher):", ""]
        lines += _kv_table(grid_p, ["observed", "null_mean", "null_sd", "p", "method", "n_perm", "n_runs"])
        gm = core.groupby("teacher")["delta_rho"].agg(["mean", "std", "count"]).reset_index()
        lines += ["Seed means of deltaRhoPartial per teacher:", ""] + _md_table(gm, ["teacher", "mean", "std", "count"])
    else:
        lines += ["pending: no base run (version B) with a prior profile; evaluate S_0 on this split first", ""]

    lines += [f"## E2 P2: suggestibility dose-response, s = delta(T5) - delta(T6) on the {ctx.get('n_common_families', 'nan')} common families (suggestibility_runs.csv, dose_response.json)", ""]
    if dose.get("teachers"):
        dt = pd.DataFrame([{"teacher": t, **v} for t, v in dose["teachers"].items()])
        lines += _md_table(dt, ["teacher", "s_teacher", "s_student_mean", "s_student_sd", "n_runs"])
        lines += _kv_table(dose, ["slope", "intercept", "pearson", "p", "method", "n_perm", "seed_noise_sd", "ordering_preserved"])
    else:
        lines += ["pending: fewer than 2 teachers with O runs", ""]
    sug = ctx["sugg"]
    other = sug[~sug["kind"].isin(["teacher"]) & ~((sug["kind"] == "run") & (sug["version"] == "O"))]
    if len(other):
        lines += ["Descriptive: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):", ""]
        lines += _md_table(other, ["who", "kind", "delta_T5", "delta_T6", "s", "n_families"])

    lines += ["## E2 P3 (supportive): seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)", ""]
    if len(po):
        lines += _md_table(po.sort_values("teacher"), ["teacher", "n_seeds", "n_families", "rho_base", "rho_own", "rho_other_max", "other_argmax", "delta_rho", "ci_lo", "ci_hi", "p_perm", "p_holm"])
    else:
        lines += ["pending", ""]
    byv = ctx["inh_partial_by_variant"]
    if len(byv):
        bv = byv[byv["run_id"].map(lambda r: M.parse_run_id(r).version == "O")].groupby(["teacher", "variant"])["delta_rho"].agg(["mean", "std", "count"]).reset_index()
        lines += ["### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)", ""]
        lines += _md_table(bv, ["teacher", "variant", "mean", "std", "count"])

    lines += ["## Pre-revision rule (original pre-registration; failed on dev 2026-10-04 and replaced 2026-10-05; kept for transparency)", ""]
    lines += ["### E1 (old): every O seed agree_own > agree_other_max", ""]
    core = tab[tab["version"] == "O"].dropna(subset=["agree_own"])
    if core.empty:
        lines.append("no O runs with a matching teacher profile yet")
    for t, gt in core.groupby("teacher"):
        ok = int((gt["agree_own"] > gt["agree_other_max"]).sum())
        lines.append(f"- {t}: {ok}/{len(gt)} seeds pass -> {'ok' if ok == len(gt) else ('partial' if ok else 'fail')} (old rule, not the verdict)")
    lines.append("")
    lines += ["### E2 (old): uncontrolled pooled delta_rho = rho(own) - max rho(other), Holm over teachers (inheritance_pooled.csv, grid_permutation.json)", ""]
    pooled = ctx["pooled"]
    po_old = pooled[pooled["version"] == "O"] if pooled is not None and not pooled.empty else pd.DataFrame()
    if len(po_old):
        n_pass = 0
        for _, r in po_old.sort_values("teacher").iterrows():
            passed = bool(r["delta_rho"] > 0 and r["p_holm"] < ALPHA)
            n_pass += int(passed)
            lines.append(f"- {r['teacher']} ({r['n_seeds']} seeds pooled, {r['n_families']} families): delta_rho {_fmt(r['delta_rho'])} "
                         f"[{_fmt(r['ci_lo'])}, {_fmt(r['ci_hi'])}], p_perm {_fmt(r['p_perm'])}, p_holm {_fmt(r['p_holm'])} -> {'pass' if passed else 'fail'}")
        lines.append(f"- teachers passing: {n_pass}/{len(teachers)} -> old rule: E2 {'PASS' if n_pass * 3 >= 2 * max(len(teachers), 1) else 'FAIL'} (not the verdict)")
        lines += ["", "Uncontrolled grid permutation (random label shuffles, as pre-registered):", ""]
        lines += _kv_table(ctx["grid"], ["observed", "null_mean", "null_sd", "p", "method", "n_perm", "n_runs"])
        lines += _md_table(tab.sort_values(["teacher", "version", "seed"]).dropna(subset=["delta_rho"]), ["run_id", "rho_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "ci_lo", "ci_hi"])
    else:
        lines += ["no O runs with a matching teacher profile yet", ""]

    lines += ["## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)", ""]
    lines += _md_table(null, ["metric", "teacher", "version", "n_pairs", "mean", "sd", "q95"])
    lines += ["Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. ",
              "Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). ",
              "The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate; S_0's answers are still read out with the gate."]
    return "\n".join(lines)


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
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", default="results/e1")
    ap.add_argument("--n-perm", type=int, default=10_000)
    ap.add_argument("--n-boot", type=int, default=10_000)
    ap.add_argument("--exact-max", type=int, default=1_000_000, help="enumerate every teacher assignment for P1 / P2 when there are at most this many (0 = random n_perm)")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    variants = args.variants.split(",") if args.variants else list(cfg["data"]["variants"])
    teacher_files = dict(kv.split("=", 1) for kv in args.teacher_files.split(",")) if args.teacher_files else None
    teachers = list(teacher_files) if teacher_files else (args.teachers.split(",") if args.teachers else list(cfg["teachers"]))
    prompts = M.load_prompts(resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"])
    pid = set(prompts)
    student = args.student or cfg["student_model_short"]

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

    # pre-revision inheritance (uncontrolled), kept for transparency
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

    # revised E2: base prior covariate r_0 (no mass gate), partial correlations
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
        pooled_p = M.pooled_inheritance_partial(shifts_s, shifts_t, shifts_0, own, variants, n_perm=args.n_perm, n_boot=args.n_boot, seed=args.seed)
        core_p = inh_p[inh_p["run_id"].map(is_o)] if not inh_p.empty else inh_p
        grid_p = M.grid_permutation_partial(core_p, n_perm=args.n_perm, seed=args.seed, exact_max=args.exact_max) if len(core_p) else {}
    inh_p.to_csv(out / "inheritance_partial.csv", index=False)
    inh_p_byv.to_csv(out / "inheritance_partial_by_variant.csv", index=False)
    pooled_p.to_csv(out / "inheritance_partial_pooled.csv", index=False)
    (out / "grid_permutation_partial.json").write_text(json.dumps(grid_p, indent=2), encoding="utf-8")

    # revised E2 P2: suggestibility dose-response on ONE family set: complete for every O run, every teacher and r_0
    o_runs = sorted(r for r in own if M.parse_run_id(r).version == "O")
    fam_common = M.complete_families(pd.concat([shifts_s, shifts_t, shifts_0]), [*o_runs, *present] + ([base_name] if not shifts_0.empty else []), variants) if o_runs else []
    print(f"P2 family set: {len(fam_common)} families complete for {len(o_runs)} O runs, {len(present)} teachers and r_0")
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
    (out / "dose_response.json").write_text(json.dumps(dose, indent=2, default=lambda x: None if isinstance(x, float) and np.isnan(x) else x), encoding="utf-8")

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
               rep=rep, con=con, e1_states=e1_states, n_common_families=len(fam_common))
    (out / "summary.md").write_text(summary_md(ctx), encoding="utf-8")
    print(f"wrote {len(list(out.glob('*.csv')))} CSVs + summary.md to {out}")
    print((out / "summary.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
