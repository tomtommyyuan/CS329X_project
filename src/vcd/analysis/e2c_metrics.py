"""E2c metrics: does a student trained on CONTESTED families agree more with its own teacher than with the others?
(tasks/e2c_plan.md §0 and §6; written and tested before any E2c student was trained, §8 step 7.)

Quantities (tasks/e2c_plan.md §6, implemented as written):
  * agreement(run, teacher) is the symmetrized majority-action agreement of `e1_metrics.teacher_agreement` -- the same
    function behind E1's descriptive table (cell-weighted over the seen framings, cells where either p_sym is exactly
    0.5 excluded). It is called, never re-implemented; the per-family cell counts used by the bootstrap follow its
    tie rule and are checked against it at run time (`analyze_condition`).
  * gap(run) = agree_own - max over the other teachers of agree_other; gap_T(condition) = mean over the seeds of T.
  * seed-pair null of (teacher, condition) = |agree_own(seed a) - agree_own(seed b)| over the C(5, 2) = 10 seed pairs
    (`e1_metrics.seed_noise_null`, i.e. the `agree_own` rows of E1's seed_null.csv: dev SD 0.005-0.008, q95 <= 0.022);
    the rule compares gap_T with that q95 as written. The single-pair q95 is NOT rescaled to the seed mean, which
    makes the comparison conservative (cf. the scaling argument in e3_metrics); we do not change the frozen rule.
  * family bootstrap 95% CI of gap_T: families resampled with replacement (B = 2000, fixed seed), agreement recomputed
    for every run from per-family cell counts, per-run gap and seed mean recomputed, 2.5 / 97.5 percentiles. One
    weight matrix (`bootstrap_weights`) is shared by every condition, so gap_T(C) - gap_T(K) has a paired CI.
  * primary verdict (condition C): per teacher pass iff gap_T > q95 AND ci_lo > 0; >= 2/3 of the configured teachers
    -> PASS, 1/3 -> PARTIAL, 0/3 -> FAIL (`e1_metrics.e2_primary_verdict`). Attribution: gap_T(C) - gap_T(K) with
    ci_lo > 0 for >= 2/3 teachers -> the effect is attributed to contestedness rather than to the change of source.
Conditions: C = E2c contested-trained O students, K = E2c consensus control O students, E1 = the original E1 O students
(reference row). Every function is pure; `analyze_condition` runs the whole chain for one condition.
"""

from __future__ import annotations

import json
import warnings
from pathlib import Path
from typing import Iterable, Mapping, NamedTuple, Optional, Sequence

import numpy as np
import pandas as pd

from vcd.analysis import e1_metrics as M
from vcd.analysis.e1_metrics import SEEN_VARIANTS, is_run_id, parse_run_id
from vcd.schemas import Prompt, TeacherResponse
from vcd.teacher import profile as P

CONDITIONS: tuple[str, ...] = ("C", "K", "E1")
CONDITION_LABELS: dict[str, str] = {"C": "E2c-C (contested)", "K": "E2c-K (consensus control)", "E1": "E1 (original train, reference)"}
N_BOOT = 2000  # tasks/e2c_plan.md §6: family bootstrap B = 2000
BOOT_SEED = 0  # fixed seed of the shared family resampling
N_SEEDS_PLANNED = 5
GAP_VERSION = "O"  # E2c trains O students only; R / B runs never enter gaps or nulls
MIN_TEACHER_FRAC = 2 / 3
RULE = ("gap_T = seed mean over the teacher's O runs of [agree_own - max_other agree_other] (symmetrized majority action, e1_metrics.teacher_agreement); "
        "seed-pair null = |agree_own(a) - agree_own(b)| over the seed pairs of (teacher, condition), q95; family bootstrap 95% CI of gap_T (B resamples, fixed seed, "
        "shared across conditions). Primary (condition C): per teacher gap_T > q95 AND ci_lo > 0; >= 2/3 teachers PASS, 1/3 PARTIAL, 0/3 FAIL. "
        "Attribution: gap_T(C) - gap_T(K) with ci_lo > 0 for >= 2/3 teachers -> effect attributed to contestedness.")


def _nan(x) -> bool:
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


# --------------------------------------------------------------------------- per-run table


RUN_COLS = ["run_id", "student", "teacher", "version", "seed", "agree_own", "agree_other_max", "other_argmax", "gap", "n_cells_own", "n_ties_own"]


def run_table(sym_s: pd.DataFrame, sym_t: pd.DataFrame, teachers: Sequence[str], variants: Sequence[str] = SEEN_VARIANTS) -> pd.DataFrame:
    """One row per protocol run: agree__{teacher} for every teacher with a profile, agree_own, agree_other_max, other_argmax, gap.

    Agreement comes from `e1_metrics.teacher_agreement` (the E1 descriptive algorithm). `teachers` fixes the column
    order; teachers without profile rows in `sym_t` get no column. The max over the other teachers is taken over the
    present ones (NaNs ignored, order-independent). Runs whose id does not parse are dropped.
    """
    ag = M.teacher_agreement(sym_s, sym_t, variants) if len(sym_s) and len(sym_t) else pd.DataFrame(columns=["run_id", "teacher", "agreement", "n_ties", "n_cells"])
    present = [t for t in teachers if t in set(ag["teacher"])] if len(ag) else []
    cols = RUN_COLS[:5] + [f"agree__{t}" for t in present] + RUN_COLS[5:]
    keys = M.run_keys_table(sorted(sym_s["teacher"].unique())) if len(sym_s) else pd.DataFrame(columns=["run_id", "student", "teacher", "version", "seed"])
    if keys.empty:
        return pd.DataFrame(columns=cols)
    piv = ag.pivot_table(index="run_id", columns="teacher", values="agreement") if len(ag) else pd.DataFrame()
    cells = ag.set_index(["run_id", "teacher"]) if len(ag) else pd.DataFrame(columns=["n_cells", "n_ties"])
    rows = []
    for k in keys.itertuples(index=False):
        row: dict = dict(run_id=k.run_id, student=k.student, teacher=k.teacher, version=k.version, seed=int(k.seed))
        for t in present:
            row[f"agree__{t}"] = float(piv.at[k.run_id, t]) if (k.run_id in piv.index and t in piv.columns and not pd.isna(piv.at[k.run_id, t])) else np.nan
        own = row.get(f"agree__{k.teacher}", np.nan) if k.teacher in present else np.nan
        others = {t: row[f"agree__{t}"] for t in present if t != k.teacher and not _nan(row[f"agree__{t}"])}
        other_max = max(others.values()) if others else np.nan
        row.update(agree_own=own, agree_other_max=other_max, other_argmax=(max(others, key=others.get) if others else None),
                   gap=(own - other_max) if not (_nan(own) or _nan(other_max)) else np.nan,
                   n_cells_own=int(cells.at[(k.run_id, k.teacher), "n_cells"]) if (k.run_id, k.teacher) in cells.index else 0,
                   n_ties_own=int(cells.at[(k.run_id, k.teacher), "n_ties"]) if (k.run_id, k.teacher) in cells.index else 0)
        rows.append(row)
    return pd.DataFrame(rows, columns=cols)


# --------------------------------------------------------------------------- per-family cell counts and the family bootstrap


class FamilyCounts(NamedTuple):
    """Per (run_id, teacher) pair and family: the agreement numerator and denominator of `teacher_agreement`."""

    pairs: list[tuple[str, str]]  # (run_id, teacher), sorted
    agree: np.ndarray  # (n_pairs, n_families) int: non-tie cells whose majority act is the same on both sides
    valid: np.ndarray  # (n_pairs, n_families) int: non-tie cells (both p_sym present, neither exactly 0.5)
    families: list[str]


def family_counts(sym_s: pd.DataFrame, sym_t: pd.DataFrame, families: Sequence[str], variants: Sequence[str] = SEEN_VARIANTS) -> FamilyCounts:
    """Cell counts per (run, teacher, family) on the aligned cells of `e1_metrics._pairs`, with the tie rule of `_agreement`.

    sum over families of agree / sum of valid reproduces `teacher_agreement` exactly (`agreement_from_counts`); weighting
    the families by bootstrap counts gives the agreement on a resampled family set. Families outside `families` are
    ignored (they cannot occur when the sym tables come from the split's prompt file).
    """
    families = list(families)
    fam_idx = {f: i for i, f in enumerate(families)}
    m = M._pairs(sym_s, sym_t, variants) if len(sym_s) and len(sym_t) else pd.DataFrame(columns=["run_id", "teacher", "family_id", "variant", "p_s", "p_t"])
    m = m[m["family_id"].isin(fam_idx)]
    pairs = sorted(set(zip(m["run_id"], m["teacher"]))) if len(m) else []
    A = np.zeros((len(pairs), len(families)), dtype=np.int64)
    V = np.zeros_like(A)
    if len(m):
        a, b = m["p_s"].to_numpy(dtype=float), m["p_t"].to_numpy(dtype=float)
        tie = (a == 0.5) | (b == 0.5)  # identical to e1_metrics._agreement: the majority act is undefined at exactly 0.5
        same = (a > 0.5) == (b > 0.5)
        pair_idx = {p: i for i, p in enumerate(pairs)}
        pi = np.array([pair_idx[p] for p in zip(m["run_id"], m["teacher"])], dtype=np.int64)
        fi = m["family_id"].map(fam_idx).to_numpy(dtype=np.int64)
        np.add.at(V, (pi, fi), (~tie).astype(np.int64))
        np.add.at(A, (pi, fi), (same & ~tie).astype(np.int64))
    return FamilyCounts(pairs, A, V, families)


def agreement_from_counts(fc: FamilyCounts, W: Optional[np.ndarray] = None) -> np.ndarray:
    """Observed agreement per pair (W None, shape (n_pairs,)) or per pair x replicate (W = family counts, (B, F) -> (n_pairs, B)).

    NaN where a pair has no valid cell on the (resampled) families.
    """
    if W is None:
        num, den = fc.agree.sum(axis=1).astype(float), fc.valid.sum(axis=1).astype(float)
    else:
        Wt = np.asarray(W, dtype=float).T
        num, den = fc.agree.astype(float) @ Wt, fc.valid.astype(float) @ Wt
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def bootstrap_weights(n_families: int, n_boot: int = N_BOOT, seed: int = BOOT_SEED) -> np.ndarray:
    """(n_boot, n_families) multiplicity of every family in each with-replacement resample; deterministic in `seed`.

    Built once per analysis and shared by every condition, so the C - K difference is a paired bootstrap.
    """
    rng = np.random.default_rng(seed)
    W = np.zeros((n_boot, n_families), dtype=np.int64)
    if n_boot > 0 and n_families > 0:
        idx = rng.integers(0, n_families, size=(n_boot, n_families))
        np.add.at(W, (np.repeat(np.arange(n_boot), n_families), idx.ravel()), 1)
    return W


def gap_replicates(fc: FamilyCounts, agree_pb: np.ndarray, own: Mapping[str, str], teachers: Sequence[str]) -> tuple[list[str], np.ndarray]:
    """Per run (rows) and replicate (columns): agree_own - max over the other teachers, from a (n_pairs, B) agreement matrix.

    `own` maps run_id -> teacher; runs without an own-teacher pair or without any other teacher are skipped. An
    all-NaN set of other teachers in a replicate gives NaN for that replicate.
    """
    pb = np.asarray(agree_pb, dtype=float)
    pb = pb[:, None] if pb.ndim == 1 else pb
    idx = {p: i for i, p in enumerate(fc.pairs)}
    runs = sorted({r for r, _ in fc.pairs if r in own and (r, own[r]) in idx})
    G = np.full((len(runs), pb.shape[1]), np.nan)
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)  # all-NaN slices are legitimate NaN replicates
        for k, r in enumerate(runs):
            others = [idx[(r, t)] for t in teachers if t != own[r] and (r, t) in idx]
            if others:
                G[k] = pb[idx[(r, own[r])]] - np.nanmax(pb[others], axis=0)
    return runs, G


def seed_mean_gaps(runs: Sequence[str], G: np.ndarray, own: Mapping[str, str]) -> dict[str, np.ndarray]:
    """teacher -> (B,) mean over that teacher's runs of the per-run gap replicates (NaN replicates ignored per run)."""
    out: dict[str, np.ndarray] = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for t in sorted({own[r] for r in runs}):
            rows = [i for i, r in enumerate(runs) if own[r] == t]
            out[t] = np.nanmean(np.asarray(G, dtype=float)[rows], axis=0)
    return out


# --------------------------------------------------------------------------- seed-pair null, gap table, verdicts


NULL_COLS = ["teacher", "version", "metric", "n_pairs", "mean", "sd", "q95"]


def seed_pair_null(run_tab: pd.DataFrame, version: str = GAP_VERSION) -> pd.DataFrame:
    """|agree_own(seed a) - agree_own(seed b)| over the seed pairs of every teacher (`e1_metrics.seed_noise_null`), plus the pooled row."""
    if run_tab.empty:
        return pd.DataFrame(columns=NULL_COLS)
    t = run_tab[run_tab["version"] == version].dropna(subset=["agree_own"])
    if t.empty:
        return pd.DataFrame(columns=NULL_COLS)
    return M.seed_noise_null(t[["run_id", "teacher", "version", "seed", "agree_own"]], "agree_own")[NULL_COLS]


GAP_COLS = ["teacher", "n_seeds", "seeds", "agree_own", "agree_other_max", "gap", "ci_lo", "ci_hi", "n_boot", "n_boot_nan", "null_n_pairs", "null_mean", "null_sd", "null_q95",
            "exceeds_null", "ci_above_zero", "passed"]


def gap_table(run_tab: pd.DataFrame, boot: Mapping[str, np.ndarray], null: pd.DataFrame, teachers: Sequence[str], version: str = GAP_VERSION) -> pd.DataFrame:
    """Per configured teacher: gap_T (seed mean of the per-run gap), its family-bootstrap CI, the seed-pair q95 and the two pass flags.

    `exceeds_null` = gap_T > null_q95 (strict), `ci_above_zero` = ci_lo > 0 (strict), `passed` = both. A teacher without
    runs keeps a row with n_seeds 0 and passed False; a teacher without a defined q95 (one seed) or CI cannot pass.
    """
    t = run_tab[run_tab["version"] == version].dropna(subset=["gap"]) if len(run_tab) else run_tab
    nl = null[(null["version"] == version) & (null["teacher"] != "all")].set_index("teacher") if len(null) else pd.DataFrame(columns=NULL_COLS).set_index("teacher")
    rows = []
    for teacher in teachers:
        g = t[t["teacher"] == teacher].sort_values("seed") if len(t) else t
        row = dict(teacher=teacher, n_seeds=int(len(g)), seeds=",".join(str(int(s)) for s in g["seed"]) if len(g) else "", agree_own=np.nan, agree_other_max=np.nan, gap=np.nan,
                   ci_lo=np.nan, ci_hi=np.nan, n_boot=0, n_boot_nan=0, null_n_pairs=0, null_mean=np.nan, null_sd=np.nan, null_q95=np.nan, exceeds_null=False, ci_above_zero=False, passed=False)
        if len(g):
            row.update(agree_own=float(g["agree_own"].mean()), agree_other_max=float(g["agree_other_max"].mean()), gap=float(g["gap"].mean()))
            b = np.asarray(boot.get(teacher, []), dtype=float)
            if b.size and np.isfinite(b).any():
                lo, hi = np.nanquantile(b, [0.025, 0.975])
                row.update(ci_lo=float(lo), ci_hi=float(hi), n_boot=int(b.size), n_boot_nan=int(np.isnan(b).sum()))
            elif b.size:
                row.update(n_boot=int(b.size), n_boot_nan=int(b.size))
            if teacher in nl.index:
                row.update(null_n_pairs=int(nl.at[teacher, "n_pairs"]), null_mean=float(nl.at[teacher, "mean"]), null_sd=float(nl.at[teacher, "sd"]), null_q95=float(nl.at[teacher, "q95"]))
            row["exceeds_null"] = bool(row["gap"] > row["null_q95"]) if not _nan(row["null_q95"]) else False
            row["ci_above_zero"] = bool(row["ci_lo"] > 0) if not _nan(row["ci_lo"]) else False
            row["passed"] = bool(row["exceeds_null"] and row["ci_above_zero"])
        rows.append(row)
    return pd.DataFrame(rows, columns=GAP_COLS)


def primary_verdict(gaps: Optional[pd.DataFrame], teachers: Sequence[str]) -> dict:
    """E2c primary on condition C: PASS / PARTIAL / FAIL over the configured teachers, or pending when the rule cannot be applied.

    Pending when the condition has no runs or any configured teacher has fewer than 2 seeds (no seed-pair null).
    Teachers with a seed count other than the planned 5 are listed under `deviations` (the verdict is still issued).
    """
    out = {"verdict": "pending (no runs)", "n_pass": 0, "n_teachers": len(teachers), "passing": [], "missing": list(teachers), "deviations": [], "rule": RULE}
    if gaps is None or gaps.empty:
        return out
    g = gaps.set_index("teacher")
    n_seeds = {t: int(g.at[t, "n_seeds"]) if t in g.index else 0 for t in teachers}
    out["missing"] = [t for t in teachers if n_seeds[t] < 2]
    out["deviations"] = [f"{t}: {n_seeds[t]} seeds (planned {N_SEEDS_PLANNED})" for t in teachers if n_seeds[t] != N_SEEDS_PLANNED and n_seeds[t] >= 2]
    if out["missing"]:
        out["verdict"] = f"pending (fewer than 2 seeds for {', '.join(out['missing'])})"
        return out
    passing = [t for t in teachers if bool(g.at[t, "passed"])]
    out.update(n_pass=len(passing), passing=passing, verdict=M.e2_primary_verdict(len(passing), len(teachers)))
    return out


ATTR_COLS = ["teacher", "gap_C", "gap_K", "diff", "ci_lo", "ci_hi", "n_boot", "n_boot_nan", "ci_above_zero"]


def attribution_table(gaps_c: Optional[pd.DataFrame], gaps_k: Optional[pd.DataFrame], boot_c: Mapping[str, np.ndarray], boot_k: Mapping[str, np.ndarray], teachers: Sequence[str]) -> pd.DataFrame:
    """Per teacher: gap_T(C) - gap_T(K) with the paired family-bootstrap CI (same resampled families on both sides)."""
    gc = gaps_c.set_index("teacher")["gap"] if gaps_c is not None and len(gaps_c) else pd.Series(dtype=float)
    gk = gaps_k.set_index("teacher")["gap"] if gaps_k is not None and len(gaps_k) else pd.Series(dtype=float)
    rows = []
    for teacher in teachers:
        c, k = float(gc.get(teacher, np.nan)), float(gk.get(teacher, np.nan))
        row = dict(teacher=teacher, gap_C=c, gap_K=k, diff=(c - k) if not (_nan(c) or _nan(k)) else np.nan, ci_lo=np.nan, ci_hi=np.nan, n_boot=0, n_boot_nan=0, ci_above_zero=False)
        if teacher in boot_c and teacher in boot_k:
            d = np.asarray(boot_c[teacher], dtype=float) - np.asarray(boot_k[teacher], dtype=float)
            if d.size and np.isfinite(d).any():
                lo, hi = np.nanquantile(d, [0.025, 0.975])
                row.update(ci_lo=float(lo), ci_hi=float(hi), n_boot=int(d.size), n_boot_nan=int(np.isnan(d).sum()), ci_above_zero=bool(lo > 0))
        rows.append(row)
    return pd.DataFrame(rows, columns=ATTR_COLS)


def attribution_verdict(att: Optional[pd.DataFrame], teachers: Sequence[str], has_c: bool, has_k: bool) -> dict:
    """'attributed to contestedness' iff ci_lo(gap_C - gap_K) > 0 for >= 2/3 of the configured teachers; pending without C or K."""
    out = {"verdict": "pending", "n_pass": 0, "n_teachers": len(teachers), "passing": [], "missing": []}
    if not has_c or not has_k:
        out["verdict"] = "pending (no " + " and ".join(n for n, h in (("C", has_c), ("K", has_k)) if not h) + " runs)"
        return out
    a = att.set_index("teacher") if att is not None and len(att) else pd.DataFrame(columns=ATTR_COLS).set_index("teacher")
    out["missing"] = [t for t in teachers if t not in a.index or _nan(a.at[t, "ci_lo"])]
    if out["missing"]:
        out["verdict"] = f"pending (no paired bootstrap for {', '.join(out['missing'])})"
        return out
    passing = [t for t in teachers if bool(a.at[t, "ci_above_zero"])]
    out.update(n_pass=len(passing), passing=passing, verdict="attributed to contestedness" if len(passing) * 3 >= 2 * len(teachers) else "not attributed")
    return out


# --------------------------------------------------------------------------- one condition end to end


class ConditionResult(NamedTuple):
    name: str
    n_rows: int
    run_tab: pd.DataFrame
    agreement: pd.DataFrame
    jsd: pd.DataFrame
    consistency: pd.DataFrame
    category: pd.DataFrame
    suggestibility: pd.DataFrame
    counts: Optional[FamilyCounts]
    boot: dict[str, np.ndarray]
    null: pd.DataFrame
    gaps: pd.DataFrame
    skipped: list[str]


def analyze_condition(name: str, rows: Sequence[TeacherResponse], prompts: Mapping[str, Prompt], sym_t: pd.DataFrame, teachers: Sequence[str], variants: Sequence[str],
                      families: Sequence[str], W: np.ndarray) -> ConditionResult:
    """Run table, seed-pair null, family bootstrap and gap table for one condition's response rows; descriptive tables alongside.

    Only version-O runs whose teacher has a profile enter the gap, null and bootstrap; every protocol run enters the
    descriptive tables. Run ids that do not match the protocol pattern are listed in `skipped`. The observed agreement
    from the per-family counts must equal `teacher_agreement` (raises otherwise: the bootstrap would be off the rule).
    """
    fs = M.frame_table(rows, dict(prompts))
    sym_s = M.sym_table(fs) if len(fs) else pd.DataFrame(columns=["teacher", "family_id", "variant", "p_o1", "p_o2", "p_sym", "order_gap"])
    ids = sorted(sym_s["teacher"].unique()) if len(sym_s) else []
    skipped = [r for r in ids if not is_run_id(r)]
    sym_s = sym_s[~sym_s["teacher"].isin(skipped)]
    fs = fs[~fs["teacher"].isin(skipped)] if len(fs) else fs
    present = [t for t in teachers if len(sym_t) and t in set(sym_t["teacher"])]
    run_tab = run_table(sym_s, sym_t, teachers, variants)
    own = {r: parse_run_id(r).teacher for r in run_tab["run_id"] if parse_run_id(r).version == GAP_VERSION and parse_run_id(r).teacher in present}
    counts, boot = None, {}
    if own:
        counts = family_counts(sym_s[sym_s["teacher"].isin(own)], sym_t[sym_t["teacher"].isin(present)], families, variants)
        if counts.pairs:
            obs = agreement_from_counts(counts)
            ref = run_tab.set_index("run_id")
            for (r, t), v in zip(counts.pairs, obs):
                want = float(ref.at[r, f"agree__{t}"])
                if not (np.isnan(v) and np.isnan(want)) and not np.isclose(v, want, atol=1e-12, rtol=0):
                    raise ValueError(f"family counts disagree with teacher_agreement for ({r}, {t}): {v} vs {want}")
            runs, G = gap_replicates(counts, agreement_from_counts(counts, W), own, present)
            boot = seed_mean_gaps(runs, G, own)
    null = seed_pair_null(run_tab)
    gaps = gap_table(run_tab, boot, null, teachers)
    agreement = M.teacher_agreement(sym_s, sym_t, variants) if len(sym_s) and len(sym_t) else pd.DataFrame(columns=["run_id", "teacher", "agreement", "n_ties", "n_cells"])
    jsd = M.student_teacher_jsd(sym_s, sym_t, variants) if len(sym_s) and len(sym_t) else pd.DataFrame(columns=["run_id", "teacher", "jsd", "n_cells"])
    cons = M.consistency(sym_s, variants) if len(sym_s) else pd.DataFrame(columns=["teacher", "n_families", "share_uncertain", "flip_rate", "family_flip_share", "mean_jsd"])
    cat = M.category_rates(fs, by=("teacher",)) if len(fs) else pd.DataFrame(columns=["teacher", "answer", "malformed", "n"])
    shifts = P.framing_shifts(sym_s, list(variants)) if len(sym_s) else pd.DataFrame(columns=["teacher", "family_id", "variant", "p", "r"])
    sugg = M.suggestibility_by_run(shifts) if len(shifts) else pd.DataFrame(columns=["who", "delta_T5", "delta_T6", "s", "n_families"])
    return ConditionResult(name, len(rows), run_tab, agreement, jsd, cons, cat, sugg, counts, boot, null, gaps, skipped)


def run_descriptives(res: ConditionResult) -> pd.DataFrame:
    """Per run: the run table plus answer_rate, jsd_own, flip_rate, mean_jsd, family_flip_share and the suggestibility s = delta(T5) - delta(T6)."""
    tab = res.run_tab.copy()
    if tab.empty:
        return tab.assign(condition=res.name, answer_rate=np.nan, jsd_own=np.nan, flip_rate=np.nan, mean_jsd=np.nan, family_flip_share=np.nan, n_families=np.nan, s=np.nan)
    tab.insert(0, "condition", res.name)
    cat = res.category.set_index("teacher") if len(res.category) else pd.DataFrame(columns=["answer"])
    tab["answer_rate"] = tab["run_id"].map(cat["answer"]).astype(float) if "answer" in cat else np.nan
    js = res.jsd.set_index(["run_id", "teacher"])["jsd"] if len(res.jsd) else pd.Series(dtype=float)
    tab["jsd_own"] = [float(js.get((r, t), np.nan)) for r, t in zip(tab["run_id"], tab["teacher"])]
    cons = res.consistency.set_index("teacher") if len(res.consistency) else pd.DataFrame(columns=["flip_rate", "mean_jsd", "family_flip_share", "n_families"])
    for c in ("n_families", "flip_rate", "mean_jsd", "family_flip_share"):
        tab[c] = tab["run_id"].map(cons[c]).astype(float) if c in cons else np.nan
    tab["n_families"] = [int(v) if not _nan(v) else np.nan for v in tab["n_families"]]  # a count, printed without decimals
    sug = res.suggestibility.set_index("who")["s"] if len(res.suggestibility) else pd.Series(dtype=float)
    tab["s"] = tab["run_id"].map(sug).astype(float)
    return tab


# --------------------------------------------------------------------------- training-size inputs (optional)


MANIFEST_COLS = ["run_id", "n_examples", "n_target_tokens", "n_rows_in_file", "data_path", "data_sha256"]


def load_manifests(files: Iterable[str | Path]) -> pd.DataFrame:
    """n_examples / n_target_tokens of <run_dir>/train_manifest.json next to each eval response file (absent files skipped)."""
    rows = []
    for f in files:
        p = Path(f).parent.parent / "train_manifest.json"
        if not p.exists():
            continue
        m = json.loads(p.read_text(encoding="utf-8"))
        rows.append({c: m.get(c) for c in MANIFEST_COLS})
    return pd.DataFrame(rows, columns=MANIFEST_COLS)


META_COLS = ["teacher", "version", "seed", "n_examples", "n_families", "n_items_answered", "n_items_stable", "n_dropped_order_unstable", "order_stable_rate", "path"]


def load_sft_meta(sft_dir: str | Path, teachers: Sequence[str], version: str = GAP_VERSION) -> pd.DataFrame:
    """Per (teacher, seed): the {teacher}_{version}_s{seed}.meta.json fields of scripts/10 (n_examples, n_families, order stability); missing files skipped."""
    rows = []
    d = Path(sft_dir)
    for t in teachers:
        for p in sorted(d.glob(f"{t}_{version}_s*.meta.json")):
            m = json.loads(p.read_text(encoding="utf-8"))
            try:
                seed = int(p.stem.split("_s")[-1].split(".")[0])
            except ValueError:
                seed = -1
            rows.append(dict(teacher=t, version=version, seed=seed, **{c: m.get(c) for c in META_COLS[3:-1]}, path=str(p)))
    return pd.DataFrame(rows, columns=META_COLS)
