"""E3c metric: does register rewriting of the CONTESTED-set demonstrations (O -> F / C) change how much a student inherits
its OWN teacher's judgments? One pre-registered quantity, the E2c "gap" (tasks/e2c_plan.md §6: agreement with the own
teacher minus agreement with another teacher), measured per family and put through the frozen E3 statistics of
tasks/e3_plan.md §2-3 (seed-paired V - O differences, family bootstrap, t-scaled seed-pair null, TOST, `e3_verdict`).

Definition (frozen by the Mac side before any E3c F / C run exists; implemented as written):
  1. For every student run and every teacher the symmetrized majority action per (family, variant) cell on the split's
     prompts (variants T1, T3, T5, T6 by default), as in `e1_metrics.sym_table`; the majority is undefined when
     p_sym == 0.5 and that cell is dropped from the comparison (`e3_metrics.family_compare`, the E1 tie rule).
  2. Per run and family f: agree_own_f = share of the family's cells (defined majorities on both sides) where the
     student's majority equals its OWN teacher's; agree_other_f likewise against the REFERENCE OTHER teacher of the
     student's teacher.
  3. Reference other teacher of T (`reference_other`): the other configured teacher with the highest seed-mean
     run-level agreement (`e1_metrics.teacher_agreement`, cell-weighted) with T's O students of this grid on the same
     split; fixed per teacher (used for the O, F and C runs) and recorded; exact ties -> alphabetically first.
  4. d_f = agree_own_f - agree_other_f (`family_tables`); the run value is mean_f d_f over ONE family set per teacher
     (`gap_families`: families complete for every run of the teacher, `e3_metrics.teacher_families`, with a defined
     gap in every run), so the null, the levels and the paired statistics share their families. Statistic per
     (teacher, V in {F, C}) = `e3_metrics.paired_delta`: seed mean of mean_f d_f(S_{T,V,s}) - mean_f d_f(S_{T,O,s})
     with a family-bootstrap CI (families resampled jointly across the seeds).
  5. Null (`gap_null` = `e3_metrics.seed_pair_null`): signed O-O seed-pair differences of mean_f d_f, all C(n_O, 2)
     pairs, pooled over teachers; verdict rows "gap F - O" and "gap C - O" (`gap_verdicts` = `e3_metrics.e3_verdict`,
     two-sided, n_seeds per teacher, df = sum_T (n_O,T - 1); SD_stat = sqrt(mean(d^2) / n_seeds), q95 = t(0.975, df)
     x SD_stat; effect / no effect (TOST) / inconclusive / pending exactly as e3_verdict returns them).
  6. Descriptive: per (teacher, version) seed-mean agree_own / agree_other / gap with family-bootstrap CIs
     (`gap_levels`), per-run values next to the cell-weighted E2c-style numbers (`run_table`), the grid inventory
     (`e3_metrics.grid_inventory`, `inventory_with_missing`) and the reference table.

Nothing here re-implements an E3 statistic: the grid, the per-family comparison, the paired delta, the null and the
verdict are the e3_metrics functions; the agreement behind the reference choice is e1_metrics.teacher_agreement.
`analyze_gap` runs the whole chain from the two sym tables.
"""

from __future__ import annotations

import zlib
from typing import Mapping, NamedTuple, Optional, Sequence

import numpy as np
import pandas as pd

from vcd.analysis import e1_metrics as M
from vcd.analysis import e3_metrics as E
from vcd.analysis.e1_metrics import SEEN_VARIANTS, is_run_id, parse_run_id

GAP_LABEL = "gap"
VERSIONS: tuple[str, ...] = E.VERSIONS
_META_COLS = ("student", "teacher", "seed")

REF_COLS = ["teacher", "reference_other", "n_O_runs", "agree_ref", "tie", "candidates"]
FAMILY_COLS = ["agree_own", "agree_other", "gap", "n_cells_own", "n_ties_own", "n_cells_other", "n_ties_other"]
RUN_COLS = ["run_id", "student", "teacher", "version", "seed", "reference_other", "n_families", "agree_own", "agree_other", "gap"]
CW_COLS = ["agree_own_cw", "agree_other_cw", "gap_cw", "agree_other_max_cw", "other_argmax_cw", "gap_e2c_cw", "n_cells_own_cw", "n_ties_own_cw"]
LEVEL_COLS = ["teacher", "version", "n_seeds", "seeds", "n_families", "agree_own", "agree_own_ci_lo", "agree_own_ci_hi", "agree_other", "agree_other_ci_lo", "agree_other_ci_hi", "gap", "gap_ci_lo", "gap_ci_hi"]
VERDICT_COLS = ["metric", "version", "one_sided", "teachers", "null_q95", "null_q95_single", "null_sd", "null_sd_single", "n_null", "df", "n_pass", "n_pass_single", "n_tost", "n_teachers", "n_required",
                "direction", "direction_consistent", "min_p_holm", "p_row", "verdict"]
VERDICT_TEACHER_COLS = ["metric", "version", "teacher", "stat", "ci_lo", "ci_hi", "n_seeds", "null_sd", "q95", "effect_sd", "exceeds_q95", "exceeds_q95_single", "sign", "p_null", "p_holm", "tost"]
_AGREEMENT_COLS = ["run_id", "teacher", "agreement", "n_ties", "n_cells"]


def _version_cols(grid: pd.DataFrame) -> list[str]:
    return [c for c in grid.columns if c not in _META_COLS]


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


def _ci(ci) -> str:
    lo, hi = ci if ci else (np.nan, np.nan)
    return f"[{_fmt(lo)}, {_fmt(hi)}]"


# --------------------------------------------------------------------------- (3) reference other teacher


def reference_other(agreement: pd.DataFrame, grid: pd.DataFrame, teachers: Sequence[str]) -> pd.DataFrame:
    """Per configured teacher T: the reference other teacher = the other configured teacher whose seed-mean run-level
    agreement (`e1_metrics.teacher_agreement` rows: run_id, teacher, agreement) with T's O students of `grid` is the
    highest. Exact ties go to the alphabetically first teacher (`tie` = True). `reference_other` is None when T has no
    O run with an agreement row against another configured teacher, or no other configured teacher has one.

    Columns: teacher, reference_other, n_O_runs (O runs that entered the means), agree_ref (the winning mean), tie,
    candidates ("beta=0.650000;gamma=0.350000", best first) and agree__{t} for every configured teacher t (the seed
    mean of T's O students' agreement with t; agree__{T} itself is the cell-weighted E2c agree_own of the O students).
    The choice is fixed per teacher and reused for the O, F and C runs (definition 3).
    """
    cols = REF_COLS + [f"agree__{t}" for t in teachers]
    ag = agreement.dropna(subset=["agreement"]) if len(agreement) else pd.DataFrame(columns=_AGREEMENT_COLS)
    rows = []
    for t in teachers:
        o_runs = list(grid.loc[(grid["teacher"] == t) & grid["O"].notna(), "O"]) if len(grid) and "O" in grid.columns else []
        sub = ag[ag["run_id"].isin(o_runs) & ag["teacher"].isin(list(teachers))]
        means = sub.groupby("teacher")["agreement"].mean() if len(sub) else pd.Series(dtype=float)
        others = means.drop(index=t, errors="ignore")
        row: dict = dict(teacher=t, reference_other=None, n_O_runs=int(sub.loc[sub["teacher"] != t, "run_id"].nunique()) if len(sub) else 0, agree_ref=np.nan, tie=False, candidates="")
        row.update({f"agree__{o}": float(means[o]) if o in means.index else np.nan for o in teachers})
        if len(others):
            best = float(others.max())
            top = sorted(o for o, v in others.items() if float(v) == best)
            order = sorted(others.index, key=lambda o: (-float(others[o]), o))
            row.update(reference_other=top[0], agree_ref=best, tie=len(top) > 1, candidates=";".join(f"{o}={float(others[o]):.6f}" for o in order))
        rows.append(row)
    return pd.DataFrame(rows, columns=cols)


# --------------------------------------------------------------------------- (1), (2), (4) per-family gap


def family_tables(mats_s: Mapping[str, pd.DataFrame], mats_t: Mapping[str, pd.DataFrame], grid: pd.DataFrame, reference: Mapping[str, Optional[str]]) -> dict[str, pd.DataFrame]:
    """run_id -> per-family table (index family_id, columns FAMILY_COLS) for every run of the grid whose teacher T and
    reference other R both have a profile in `mats_t` (`e3_metrics.cell_matrices` tables).

    agree_own / agree_other = `e3_metrics.family_compare(student, T / R)["agree"]`: the share of the family's non-tie
    cells (neither p_sym exactly 0.5) whose majority act matches, NaN when every cell of the family is a tie;
    gap = agree_own - agree_other (NaN when either side is undefined); n_cells_* = non-tie cells, n_ties_* = ties.
    Families = those complete (all variants) for the student and both teachers.
    """
    out: dict[str, pd.DataFrame] = {}
    if grid.empty:
        return out
    for row in grid.itertuples(index=False):
        t = row.teacher
        r_t = reference.get(t)
        if t not in mats_t or not isinstance(r_t, str) or r_t not in mats_t:
            continue
        for v in _version_cols(grid):
            run = getattr(row, v)
            if not isinstance(run, str) or run not in mats_s:
                continue
            own, oth = E.family_compare(mats_s[run], mats_t[t]), E.family_compare(mats_s[run], mats_t[r_t])
            fams = own.index.intersection(oth.index)
            n_own = len([c for c in mats_s[run].columns if c in mats_t[t].columns])
            n_oth = len([c for c in mats_s[run].columns if c in mats_t[r_t].columns])
            df = pd.DataFrame(index=fams)
            df["agree_own"] = own.loc[fams, "agree"].to_numpy(dtype=float)
            df["agree_other"] = oth.loc[fams, "agree"].to_numpy(dtype=float)
            df["gap"] = df["agree_own"] - df["agree_other"]
            df["n_ties_own"] = own.loc[fams, "n_ties"].to_numpy(dtype=int)
            df["n_cells_own"] = n_own - df["n_ties_own"]
            df["n_ties_other"] = oth.loc[fams, "n_ties"].to_numpy(dtype=int)
            df["n_cells_other"] = n_oth - df["n_ties_other"]
            out[run] = df[FAMILY_COLS].sort_index()
    return out


def gap_families(tables: Mapping[str, pd.DataFrame], grid: pd.DataFrame, base: Optional[Mapping[str, Sequence[str]]] = None) -> dict[str, list[str]]:
    """teacher -> sorted families with a defined gap in EVERY scored run of the teacher in the grid, intersected with
    `base[teacher]` when given (`e3_metrics.teacher_families`: families complete for every run of the teacher). One
    family set per teacher keeps the O-O null, the levels and the paired statistics on the same families (the E3
    convention, scripts/15). Teachers without a scored run get []."""
    out: dict[str, list[str]] = {}
    if grid.empty:
        return out
    for teacher, g in grid.groupby("teacher", sort=True):
        runs = [r for v in _version_cols(grid) for r in g[v].dropna() if r in tables]
        fams = set.intersection(*[set(tables[r]["gap"].dropna().index) for r in runs]) if runs else set()
        if base is not None and teacher in base:
            fams &= set(base[teacher])
        out[teacher] = sorted(fams)
    return out


def run_table(tables: Mapping[str, pd.DataFrame], families: Mapping[str, Sequence[str]], reference: Mapping[str, Optional[str]], agreement: Optional[pd.DataFrame] = None,
              teachers: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """One row per scored run (RUN_COLS + CW_COLS): the family-unit means over `families[teacher]` of agree_own,
    agree_other and gap (gap = mean_f d_f, the quantity of the null and the statistics) and, when `agreement`
    (`e1_metrics.teacher_agreement`) is given, the cell-weighted run-level values for cross-reference: agree_own_cw,
    agree_other_cw (against the reference other), gap_cw = their difference, and the E2c definition agree_other_max_cw /
    other_argmax_cw (max over the other configured teachers, ties alphabetical) / gap_e2c_cw = agree_own_cw -
    agree_other_max_cw, with n_cells_own_cw / n_ties_own_cw. The family-unit and cell-weighted numbers differ slightly
    on real data (families with ties or incomplete variants weigh differently); they coincide when every family has the
    same number of non-tie cells."""
    piv = agreement.pivot_table(index="run_id", columns="teacher", values="agreement") if agreement is not None and len(agreement) else None
    cells = agreement.set_index(["run_id", "teacher"]) if agreement is not None and len(agreement) else None
    rows = []
    for run in sorted(tables):
        k = parse_run_id(run)
        fams = list(families.get(k.teacher, []))
        d = tables[run].reindex(fams)
        row: dict = dict(run_id=run, student=k.student, teacher=k.teacher, version=k.version, seed=k.seed, reference_other=reference.get(k.teacher), n_families=len(fams),
                         agree_own=float(d["agree_own"].mean()) if fams else np.nan, agree_other=float(d["agree_other"].mean()) if fams else np.nan, gap=float(d["gap"].mean()) if fams else np.nan)
        row.update({c: np.nan for c in CW_COLS})
        row["other_argmax_cw"] = None
        if piv is not None and run in piv.index:
            cand = [t for t in (teachers if teachers is not None else piv.columns) if t in piv.columns]
            vals = {t: float(piv.at[run, t]) for t in cand if not pd.isna(piv.at[run, t])}
            own = vals.get(k.teacher, np.nan)
            ref = reference.get(k.teacher)
            a_ref = vals.get(ref, np.nan) if isinstance(ref, str) else np.nan
            others = {t: v for t, v in vals.items() if t != k.teacher}
            omax = max(others.values()) if others else np.nan
            row.update(agree_own_cw=own, agree_other_cw=a_ref, gap_cw=own - a_ref, agree_other_max_cw=omax, other_argmax_cw=(min(t for t, v in others.items() if v == omax) if others else None), gap_e2c_cw=own - omax,
                       n_cells_own_cw=int(cells.at[(run, k.teacher), "n_cells"]) if (run, k.teacher) in cells.index else np.nan, n_ties_own_cw=int(cells.at[(run, k.teacher), "n_ties"]) if (run, k.teacher) in cells.index else np.nan)
        rows.append(row)
    return pd.DataFrame(rows, columns=RUN_COLS + CW_COLS)


# --------------------------------------------------------------------------- (6) levels per (teacher, version)


def gap_levels(tables: Mapping[str, pd.DataFrame], grid: pd.DataFrame, versions: Sequence[str] = VERSIONS, families: Optional[Mapping[str, Sequence[str]]] = None, n_boot: int = 10_000, seed: int = 0) -> pd.DataFrame:
    """Per (teacher, version) with >= 1 scored run: n_seeds, seeds, n_families and the seed-mean agree_own, agree_other
    and gap over `families[teacher]` with family-bootstrap 95% CIs (families resampled jointly across the seeds of the
    teacher, `e3_metrics._boot_mean`; the three columns use consecutive draws of one generator, so they are
    deterministic under `seed` but not paired with each other). Descriptive (definition 6)."""
    rng = np.random.default_rng([seed, zlib.crc32(b"e3c_levels")])
    rows = []
    if grid.empty:
        return pd.DataFrame(columns=LEVEL_COLS)
    for teacher, g in grid.groupby("teacher", sort=True):
        fams = list(families.get(teacher, [])) if families is not None else None
        for v in versions:
            if v not in g.columns:
                continue
            runs = sorted((int(s), r) for s, r in zip(g["seed"], g[v]) if isinstance(r, str) and r in tables)
            if not runs:
                continue
            if fams is None:
                fams = sorted(set.intersection(*[set(tables[r]["gap"].dropna().index) for _, r in runs]))
            if not fams:
                continue
            row: dict = dict(teacher=teacher, version=v, n_seeds=len(runs), seeds=",".join(str(s) for s, _ in runs), n_families=len(fams))
            for col in ("agree_own", "agree_other", "gap"):
                mat = np.stack([tables[r][col].reindex(fams).to_numpy(dtype=float) for _, r in runs])
                mean, lo, hi = E._boot_mean(mat, n_boot, rng)
                row.update({col: mean, f"{col}_ci_lo": lo, f"{col}_ci_hi": hi})
            rows.append(row)
    return pd.DataFrame(rows, columns=LEVEL_COLS)


# --------------------------------------------------------------------------- (4), (5) paired delta, null, verdicts


def gap_delta(values: Mapping[str, pd.Series], grid: pd.DataFrame, versions: Sequence[str] = ("F", "C"), n_boot: int = 10_000, seed: int = 0,
              families: Optional[Mapping[str, Sequence[str]]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """`e3_metrics.paired_delta` of the per-family gap (label "gap"): per (teacher, V) the seed mean of mean_f d_f(V) -
    mean_f d_f(O) over the families common to every paired run (intersected with `families[teacher]`), family-bootstrap
    CI joint over the seeds. Returns (per_seed, per_teacher)."""
    return E.paired_delta(values, grid, versions, n_boot=n_boot, seed=seed, label=GAP_LABEL, families=families)


def gap_null(runs: pd.DataFrame) -> pd.DataFrame:
    """Signed O-O seed-pair differences of the per-run gap (`e3_metrics.seed_pair_null`, metric "gap", all C(n_O, 2)
    pairs per teacher; the caller pools them over teachers). `runs` = `run_table` output (run_id, teacher, version,
    seed, gap)."""
    if runs.empty:
        return E.seed_pair_null(pd.DataFrame(columns=["run_id", "teacher", "version", "seed", GAP_LABEL]), GAP_LABEL, "O")
    return E.seed_pair_null(runs, GAP_LABEL, "O")


def null_df(null: pd.DataFrame) -> Optional[int]:
    """Degrees of freedom of the seed-noise estimate: sum over the teachers with null pairs of (n_O,T - 1), n_O,T = the
    distinct O runs of T among the pairs (tasks/e3_plan.md §3: 3 x (5 - 1) = 12); None without pairs (e3_verdict then
    uses the normal reference)."""
    if null.empty:
        return None
    df = sum(max(0, len(set(g["run_a"]) | set(g["run_b"])) - 1) for _, g in null.groupby("teacher"))
    return int(df) or None


def gap_verdicts(per_teacher: pd.DataFrame, null: pd.DataFrame, versions: Sequence[str] = VERSIONS, n_required: int = E.N_TEACHERS_REQUIRED, df: Optional[int] = None) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    """One verdict row per non-O version in `versions` ("gap V - O") from `e3_metrics.e3_verdict` (two-sided; n_seeds per
    teacher; the family-bootstrap CIs of `per_teacher` for the TOST; `null` = the signed O-O differences of `gap_null`).

    Returns (rows: VERDICT_COLS, per-teacher long table: VERDICT_TEACHER_COLS, raw e3_verdict dicts by row name).
    `teachers` in the row is the per-teacher detail string of scripts/15 (stat [CI] (effect in null sd, p, Holm, TOST),
    * = exceeds q95); `p_row` = second-smallest per-teacher p (the level at which ">= 2 of 3 exceed" just holds).
    A version without paired runs gives "pending (no paired runs)"; fewer than `n_required` teachers with a statistic
    gives "pending (n_teachers k < n)"; never an error. For pending rows the long table still lists the available
    per-teacher statistics (with NaN null columns).
    """
    nv = null["diff"].to_numpy(dtype=float) if len(null) else np.array([], dtype=float)
    rows, long, raw = [], [], {}
    for v in [x for x in versions if x != "O"]:
        g = per_teacher[per_teacher["version"] == v] if len(per_teacher) else per_teacher
        stats = {str(t): float(d) for t, d in zip(g["teacher"], g["diff"])} if len(g) else {}
        n_seeds: int | dict = {str(t): int(n) for t, n in zip(g["teacher"], g["n_seeds"])} if len(g) else 1
        cis = {str(r.teacher): (float(r.ci_lo), float(r.ci_hi)) for r in g.itertuples()} if len(g) else None
        name = f"{GAP_LABEL} {v} - O"
        vd = E.e3_verdict(stats, nv, one_sided=False, n_seeds=n_seeds, cis=cis, df=df, n_required=n_required)
        raw[name] = vd
        per_t = vd["per_teacher"]
        detail = "; ".join(f"{t} {_fmt(d['stat'])} {_ci(d['ci'])} ({_fmt(d['effect_sd'])} null sd, p {_fmt(d['p_null'])}, Holm {_fmt(d['p_holm'])}, TOST {d['tost']}){'*' if d['exceeds_q95'] else ''}" for t, d in per_t.items())
        if not detail:
            detail = "; ".join(f"{t} {_fmt(s)} {_ci(cis.get(t) if cis else None)}" for t, s in stats.items()) or "nan"
        ps = sorted(d["p_null"] for d in per_t.values() if np.isfinite(d["p_null"]))
        rows.append(dict(metric=name, version=v, one_sided=False, teachers=detail, null_q95=vd["q95"], null_q95_single=vd["q95_single"], null_sd=vd["null_sd"], null_sd_single=vd["null_sd_single"], n_null=vd["n_null"], df=df,
                         n_pass=vd["n_pass"], n_pass_single=sum(1 for d in per_t.values() if d["exceeds_q95_single"]), n_tost=vd["n_tost"], n_teachers=vd["n_teachers"], n_required=vd["n_required"], direction=vd["direction"],
                         direction_consistent=vd["direction_consistent"], min_p_holm=min([d["p_holm"] for d in per_t.values()], default=np.nan), p_row=ps[1] if len(ps) >= 2 else np.nan, verdict=vd["verdict"]))
        for t, s in stats.items():
            d = per_t.get(t)
            ci = cis.get(t) if cis else None
            long.append(dict(metric=name, version=v, teacher=t, stat=s, ci_lo=ci[0] if ci else np.nan, ci_hi=ci[1] if ci else np.nan, n_seeds=n_seeds[t] if isinstance(n_seeds, dict) else n_seeds,
                             null_sd=d["null_sd"] if d else np.nan, q95=d["q95"] if d else np.nan, effect_sd=d["effect_sd"] if d else np.nan, exceeds_q95=d["exceeds_q95"] if d else None,
                             exceeds_q95_single=d["exceeds_q95_single"] if d else None, sign=d["sign"] if d else E._sign(s), p_null=d["p_null"] if d else np.nan, p_holm=d["p_holm"] if d else np.nan, tost=d["tost"] if d else None))
    return pd.DataFrame(rows, columns=VERDICT_COLS), pd.DataFrame(long, columns=VERDICT_TEACHER_COLS), raw


# --------------------------------------------------------------------------- inventory and the whole chain


def inventory_with_missing(inventory: pd.DataFrame, teachers: Sequence[str], versions: Sequence[str] = VERSIONS) -> pd.DataFrame:
    """`e3_metrics.grid_inventory` plus a zero row for every configured teacher without any run (so a missing teacher is
    visible in the summary instead of silently absent)."""
    cols = ["teacher", *[f"n_{v}" for v in versions], *[f"seeds_{v}" for v in versions], *[f"paired_{v}" for v in versions if v != "O"]]
    have = set(inventory["teacher"]) if len(inventory) and "teacher" in inventory.columns else set()
    extra = [dict(teacher=t, **{f"n_{v}": 0 for v in versions}, **{f"seeds_{v}": "" for v in versions}, **{f"paired_{v}": 0 for v in versions if v != "O"}) for t in teachers if t not in have]
    parts = [p for p in (inventory if len(inventory) else None, pd.DataFrame(extra, columns=cols) if extra else None) if p is not None]
    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=cols)
    return out.reindex(columns=cols).sort_values("teacher").reset_index(drop=True)


class GapAnalysis(NamedTuple):
    grid: pd.DataFrame
    inventory: pd.DataFrame
    agreement: pd.DataFrame
    reference: pd.DataFrame
    tables: dict[str, pd.DataFrame]
    families: dict[str, list[str]]
    runs: pd.DataFrame
    levels: pd.DataFrame
    per_seed: pd.DataFrame
    per_teacher: pd.DataFrame
    null: pd.DataFrame
    df: Optional[int]
    verdicts: pd.DataFrame
    verdict_teachers: pd.DataFrame
    raw: dict


def analyze_gap(sym_s: pd.DataFrame, sym_t: pd.DataFrame, teachers: Sequence[str], variants: Sequence[str] = SEEN_VARIANTS, versions: Sequence[str] = VERSIONS, n_boot: int = 10_000, seed: int = 0) -> GapAnalysis:
    """The whole E3c gap chain from the student and teacher sym tables (`e1_metrics.sym_table`; student `teacher` column =
    run ids): grid and inventory (`e3_metrics.run_grid`, `grid_inventory` + missing teachers), cell-weighted agreement
    (`e1_metrics.teacher_agreement`) -> `reference_other`, per-family tables -> one family set per teacher
    (`e3_metrics.teacher_families` ∩ defined gaps) -> `run_table`, `gap_levels`, `gap_delta`, `gap_null`, `null_df`,
    `gap_verdicts` (n_required = len(teachers)). Every stage degrades to empty tables / pending rows when runs,
    versions or teachers are missing."""
    if "O" not in versions:
        raise ValueError("versions must include O (the reference version)")
    mats_s, mats_t = E.cell_matrices(sym_s, variants), E.cell_matrices(sym_t, variants)
    run_ids = sorted(r for r in sym_s["teacher"].unique() if is_run_id(str(r))) if len(sym_s) else []
    grid = E.run_grid(run_ids, versions)
    inventory = inventory_with_missing(E.grid_inventory(grid, versions), teachers, versions)
    agreement = M.teacher_agreement(sym_s, sym_t, variants) if len(sym_s) and len(sym_t) else pd.DataFrame(columns=_AGREEMENT_COLS)
    reference = reference_other(agreement, grid, teachers)
    ref = {str(t): (r if isinstance(r, str) else None) for t, r in zip(reference["teacher"], reference["reference_other"])}
    tables = family_tables(mats_s, mats_t, grid, ref)
    base = E.teacher_families(mats_s, grid, versions) if len(grid) else {}
    families = gap_families(tables, grid, base)
    runs = run_table(tables, families, ref, agreement, teachers)
    levels = gap_levels(tables, grid, versions, families, n_boot=n_boot, seed=seed)
    per_seed, per_teacher = gap_delta({r: d["gap"] for r, d in tables.items()}, grid, [v for v in versions if v != "O"], n_boot=n_boot, seed=seed, families=families)
    null = gap_null(runs)
    df = null_df(null)
    verdicts, verdict_teachers, raw = gap_verdicts(per_teacher, null, versions, n_required=len(teachers), df=df)
    return GapAnalysis(grid, inventory, agreement, reference, tables, families, runs, levels, per_seed, per_teacher, null, df, verdicts, verdict_teachers, raw)
