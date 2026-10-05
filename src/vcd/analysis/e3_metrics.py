"""E3 metrics: does rewriting the teacher's answer style (O -> F / C) change what the student learns?
(docs/03 §0 E3 row and §5; docs/04 groups B, C, D and §3; tasks/e3_plan.md.)

Design (frozen before any F / C run exists):
  * students are compared WITHIN teacher and PAIRED BY SEED: S_{T,V,s} vs S_{T,O,s} (same teacher T, same seed s,
    same family order in training), V in {F, C};
  * the inferential unit is the family: every per-teacher statistic is a mean over seeds of a per-family quantity,
    with a family bootstrap CI (families resampled jointly for all seeds of the teacher);
  * the noise reference is the SEED-PAIR NULL: the same quantity between two O seeds of the same teacher
    (S_{T,O,a} vs S_{T,O,b}), pooled over teachers (`seed_pair_null`, `seed_pair_disagreement`);
  * decision rule (docs/03 E3 row, verbatim: "效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致"): an effect
    counts when, in >= 2/3 of the (3 required) teachers, the seed-paired statistic exceeds the 95th percentile of
    the seed-pair null OF THAT STATISTIC and the direction is the same across those teachers (`e3_verdict`).
    The per-teacher statistic is a mean over n_seeds paired differences, so the single-pair null values are scaled
    to it: SD_stat = sqrt(mean(d^2) / n_seeds) (+ an extra variance term when the statistic is centred on the
    teacher's own O-O mean, metric 1), q95 = t_{1 - alpha/2, df} * SD_stat (one-sided: t_{1 - alpha, df}) with
    df = sum_T (n_O,T - 1). Assumptions, written in tasks/e3_plan.md §3: seed noise approximately normal and
    independent across seeds (the real same-seed pairs share init and data order, so the null is conservative).
    The raw single-pair q95 comparison is kept as a sensitivity column. p-values come from the t reference, so
    Holm over the teachers is meaningful; a "no effect" needs a TOST (docs/04 §3: every teacher's family-bootstrap
    CI inside +/- 1 SD_stat for >= 2/3 of the teachers), otherwise the verdict is "inconclusive".

Every function here is pure and starts from the e1_metrics tables: a `sym` table (teacher, family_id, variant,
p_sym, ...) whose `teacher` column holds run ids for students, `shifts` tables (teacher, family_id, variant, p, r),
and a run grid (`run_grid`) with one row per (student, teacher, seed) and one run-id column per version.

Metrics (numbers in parentheses = the list in tasks/e3_plan.md §2):
  (1) cross-student disagreement rate: `cross_student_disagreement`, null `seed_pair_disagreement`, centred
      statistic `excess_disagreement`
  (2) consistency change: `consistency_delta` (flip rate and cross-framing JSD, V minus O)
  (3) teacher agreement change and excess teacher drift: `drift_delta` (agree and JSD to the own teacher, V minus O)
  (4) homogenization index: `homogenization` (judgment JSD and 1 - corr(profile) between students of different teachers)
  (5) inheritance by form: `inheritance_by_form` (partial delta-rho given r_0, V minus O), `joint_D_by_version`,
      `suggestibility_by_version`
  (6) pre-training content check of the actual training files: `content_check`, `register_table`, `register_separation`
  (7) verdict: `e3_verdict`, with `seed_pair_null` / `null_summary`; `teacher_families` fixes one family set per
      teacher so the nulls and the paired statistics are computed on the same families
"""

from __future__ import annotations

import re
import zlib
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd
from scipy import stats as sps

from vcd.analysis import e1_metrics as M
from vcd.analysis.e1_metrics import SEEN_VARIANTS, binary_jsd, holm, is_run_id, parse_run_id
from vcd.io import read_jsonl

VERSIONS: tuple[str, ...] = ("O", "F", "C")
DISAGREEMENT_PAIRS: tuple[tuple[str, str], ...] = (("F", "C"), ("O", "F"), ("O", "C"))
MIN_TEACHER_FRAC = 2 / 3  # docs/03 E3 row: >= 2/3 teachers
N_TEACHERS_REQUIRED = 3  # docs/03 E3 row presupposes the 3 teachers; fewer paired teachers -> pending
REGISTER_MIN_ACC = 0.90  # frozen E3 choice (tasks/e3_plan.md §2): F vs C distinguishable by lexical register; docs/02 §4.3 only gives the lexical rules and the audit bar
CONFIDENT_MARGIN = 0.1  # |p - 0.5| >= this: a "confident" cell for the robustness columns of (1) and (4)


# --------------------------------------------------------------------------- run grid


def run_grid(run_ids: Iterable[str], versions: Sequence[str] = VERSIONS) -> pd.DataFrame:
    """One row per (student, teacher, seed) with a column per version holding that run's id (None when missing).

    Run ids that do not parse or whose version is not in `versions` (R, B) are ignored.
    """
    cells: dict[tuple[str, str, int], dict[str, str]] = {}
    for r in run_ids:
        if not is_run_id(r):
            continue
        k = parse_run_id(r)
        if k.version not in versions:
            continue
        cells.setdefault((k.student, k.teacher, k.seed), {})[k.version] = r
    rows = [dict(student=s, teacher=t, seed=sd, **{v: d.get(v) for v in versions}) for (s, t, sd), d in sorted(cells.items())]
    return pd.DataFrame(rows, columns=["student", "teacher", "seed", *versions])


def grid_inventory(grid: pd.DataFrame, versions: Sequence[str] = VERSIONS) -> pd.DataFrame:
    """Per teacher: number of seeds present for each version and the seeds paired with O (for the summary)."""
    rows = []
    for teacher, g in grid.groupby("teacher", sort=True):
        row: dict = {"teacher": teacher}
        for v in versions:
            have = g[g[v].notna()]
            row[f"n_{v}"] = int(len(have))
            row[f"seeds_{v}"] = ",".join(str(s) for s in sorted(have["seed"]))
        for v in versions:
            if v != "O":
                row[f"paired_{v}"] = int((g[v].notna() & g["O"].notna()).sum())
        rows.append(row)
    return pd.DataFrame(rows)


def seed_pairs(grid: pd.DataFrame, version: str, versions: Sequence[str] = VERSIONS) -> list[tuple[str, str, str, int]]:
    """(teacher, run_V, run_O, seed) for every seed where both S_{T,V,s} and S_{T,O,s} exist."""
    out = []
    for row in grid.itertuples(index=False):
        rv, ro = getattr(row, version), row.O
        if isinstance(rv, str) and isinstance(ro, str):
            out.append((row.teacher, rv, ro, int(row.seed)))
    return out


# --------------------------------------------------------------------------- per-family tables


def cell_matrices(sym: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS) -> dict[str, pd.DataFrame]:
    """profile name -> (family x variant) table of p_sym on the families complete for all `variants` (sorted index)."""
    out: dict[str, pd.DataFrame] = {}
    s = sym[sym["variant"].isin(variants)].dropna(subset=["p_sym"])
    for who, g in s.groupby("teacher", sort=True):
        piv = g.pivot_table(index="family_id", columns="variant", values="p_sym").reindex(columns=list(variants)).dropna().sort_index()
        out[who] = piv
    return out


def family_consistency(piv: pd.DataFrame) -> pd.DataFrame:
    """Per family (group B): `flip` = share of variant pairs whose majority act differs; `jsd` = mean pairwise JSD."""
    cols = list(piv.columns)
    pairs = [(a, b) for i, a in enumerate(cols) for b in cols[i + 1 :]]
    if piv.empty or not pairs:
        return pd.DataFrame(columns=["flip", "jsd"], index=piv.index, dtype=float)
    maj = piv > 0.5
    flip = np.mean([(maj[a] != maj[b]).to_numpy(dtype=float) for a, b in pairs], axis=0)
    jsd = np.mean([binary_jsd(piv[a].to_numpy(), piv[b].to_numpy()) for a, b in pairs], axis=0)
    return pd.DataFrame({"flip": flip, "jsd": jsd}, index=piv.index)


def family_compare(piv_a: pd.DataFrame, piv_b: pd.DataFrame, margin: float = CONFIDENT_MARGIN) -> pd.DataFrame:
    """Per common family: `disagree` = share of variants whose majority act differs (cells where either p is exactly
    0.5 are ties and excluded, as in e1_metrics.teacher_agreement; NaN when every variant is a tie), `agree` = 1 -
    disagree, `jsd` = mean over variants of JSD(p_a, p_b), `n_ties`, `disagree_conf` = the same share restricted to
    cells where both |p - 0.5| >= `margin` (NaN when none; robustness against readouts drifting towards 0.5),
    `n_conf` = number of such cells.

    Group-C quantities built from this table (agree_own, jsd_own in `run_scalars`, `drift_delta`) are family-unit means
    over complete families (docs/04 §3), so they differ slightly from the cell-weighted E1 tables
    (e1_metrics.teacher_agreement / student_teacher_jsd); flip and jsd of `family_consistency` match E1 exactly.
    """
    fams = piv_a.index.intersection(piv_b.index)
    cols = [c for c in piv_a.columns if c in piv_b.columns]
    A, B = piv_a.loc[fams, cols].to_numpy(dtype=float), piv_b.loc[fams, cols].to_numpy(dtype=float)
    if len(fams) == 0 or not cols:
        return pd.DataFrame(columns=["disagree", "agree", "jsd", "n_ties", "disagree_conf", "n_conf"], index=fams)
    tie = (A == 0.5) | (B == 0.5)
    diff = ((A > 0.5) != (B > 0.5)) & ~tie
    n_ok = (~tie).sum(axis=1)
    conf = (np.abs(A - 0.5) >= margin) & (np.abs(B - 0.5) >= margin)
    n_conf = conf.sum(axis=1)
    with np.errstate(invalid="ignore", divide="ignore"):
        disagree = np.where(n_ok > 0, diff.sum(axis=1) / np.maximum(n_ok, 1), np.nan)
        disagree_conf = np.where(n_conf > 0, (diff & conf).sum(axis=1) / np.maximum(n_conf, 1), np.nan)
    jsd = binary_jsd(A, B).mean(axis=1)
    return pd.DataFrame({"disagree": disagree, "agree": 1.0 - disagree, "jsd": jsd, "n_ties": tie.sum(axis=1), "disagree_conf": disagree_conf, "n_conf": n_conf}, index=fams)


def teacher_families(mats: Mapping[str, pd.DataFrame], grid: pd.DataFrame, versions: Sequence[str] = VERSIONS) -> dict[str, list[str]]:
    """teacher -> families complete for EVERY run of that teacher in the grid (all versions). One family set per
    teacher keeps the seed-pair null and the paired statistics on the same families (otherwise family-composition
    differences enter the null but not the statistic)."""
    out: dict[str, list[str]] = {}
    for teacher, g in grid.groupby("teacher", sort=True):
        runs = [r for v in versions if v in g.columns for r in g[v].dropna() if r in mats]
        out[teacher] = sorted(set.intersection(*[set(mats[r].index) for r in runs])) if runs else []
    return out


def _restrict(piv: pd.DataFrame, fams: Optional[Sequence[str]]) -> pd.DataFrame:
    return piv if fams is None else piv.loc[piv.index.intersection(list(fams))]


def run_scalars(mats_s: Mapping[str, pd.DataFrame], mats_t: Mapping[str, pd.DataFrame], families: Optional[Mapping[str, Sequence[str]]] = None) -> pd.DataFrame:
    """One row per student run: flip, jsd (own consistency), agree_own, jsd_own (vs the own teacher's profile), n_families.

    With `families` (teacher -> family list, cf. `teacher_families`) every run is scored on its teacher's set.
    This is the per-run table the seed-pair null is built from (`seed_pair_null`).
    """
    rows = []
    for run, piv in mats_s.items():
        if not is_run_id(run):
            continue
        k = parse_run_id(run)
        piv = _restrict(piv, families.get(k.teacher) if families else None)
        fc = family_consistency(piv)
        row = dict(run_id=run, student=k.student, teacher=k.teacher, version=k.version, seed=k.seed, flip=float(fc["flip"].mean()) if len(fc) else np.nan,
                   jsd=float(fc["jsd"].mean()) if len(fc) else np.nan, agree_own=np.nan, jsd_own=np.nan, n_families=int(len(piv)), n_families_own=0)
        if k.teacher in mats_t:
            cmp = family_compare(piv, mats_t[k.teacher])
            row.update(agree_own=float(cmp["agree"].mean()) if len(cmp) else np.nan, jsd_own=float(cmp["jsd"].mean()) if len(cmp) else np.nan, n_families_own=int(len(cmp)))
        rows.append(row)
    return pd.DataFrame(rows, columns=["run_id", "student", "teacher", "version", "seed", "flip", "jsd", "agree_own", "jsd_own", "n_families", "n_families_own"])


# --------------------------------------------------------------------------- family bootstrap helpers


def _boot_mean(mat: np.ndarray, n_boot: int, rng: np.random.Generator) -> tuple[float, float, float]:
    """mat (k x n_families): grand mean and the 2.5 / 97.5 percentiles of the grand mean over family bootstraps (columns
    resampled jointly for all k rows, so seeds / pairs stay paired)."""
    mat = np.asarray(mat, dtype=float)
    if mat.size == 0:
        return np.nan, np.nan, np.nan
    mean = float(np.nanmean(mat))
    n_f = mat.shape[1]
    if n_boot <= 0 or n_f < 2:
        return mean, np.nan, np.nan
    vals = np.empty(n_boot)
    for start in range(0, n_boot, 2000):
        m = min(2000, n_boot - start)
        boots = rng.integers(0, n_f, size=(m, n_f))
        vals[start : start + m] = np.nanmean(mat[:, boots], axis=(0, 2))
    lo, hi = np.nanquantile(vals, [0.025, 0.975])
    return mean, float(lo), float(hi)


def _sign(x: float) -> str:
    if x is None or np.isnan(x):
        return "nan"
    return "+" if x > 0 else ("-" if x < 0 else "0")


def _common_families(series: Sequence[pd.Series]) -> list[str]:
    sets = [set(s.dropna().index) for s in series]
    return sorted(set.intersection(*sets)) if sets else []


def paired_delta(values: Mapping[str, pd.Series], grid: pd.DataFrame, versions: Sequence[str] = ("F", "C"), n_boot: int = 10_000, seed: int = 0, label: str = "value",
                 families: Optional[Mapping[str, Sequence[str]]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Seed-paired difference V minus O of a per-family quantity (`values[run_id]` = Series indexed by family_id).

    Per (teacher, version): the families common to every paired run of that teacher (intersected with
    `families[teacher]` when given, cf. `teacher_families`); per seed, diff = mean over those families of
    value(S_{T,V,s}) - value(S_{T,O,s}); per teacher, the mean over seeds with a family-bootstrap CI (families
    resampled jointly across the seeds). Returns (per_seed, per_teacher) tables; `metric` = label.
    """
    rng = np.random.default_rng([seed, zlib.crc32(label.encode())])
    rows_s, rows_t = [], []
    for teacher in sorted(grid["teacher"].unique()):
        g = grid[grid["teacher"] == teacher]
        for v in versions:
            pairs = [(rv, ro, s) for _, rv, ro, s in seed_pairs(g, v) if rv in values and ro in values]
            if not pairs:
                continue
            fams = _common_families([values[r] for p in pairs for r in p[:2]])
            if families is not None and teacher in families:
                fams = sorted(set(fams) & set(families[teacher]))
            if not fams:
                continue
            D = np.stack([values[a].reindex(fams).to_numpy(dtype=float) - values[b].reindex(fams).to_numpy(dtype=float) for a, b, _ in pairs])
            for (a, b, s), d in zip(pairs, D):
                rows_s.append(dict(metric=label, teacher=teacher, version=v, seed=s, run_v=a, run_o=b, value_v=float(values[a].reindex(fams).mean()), value_o=float(values[b].reindex(fams).mean()), diff=float(d.mean()), n_families=len(fams)))
            mean, lo, hi = _boot_mean(D, n_boot, rng)
            rows_t.append(dict(metric=label, teacher=teacher, version=v, n_seeds=len(pairs), n_families=len(fams),
                               mean_v=float(np.mean([values[a].reindex(fams).mean() for a, _, _ in pairs])), mean_o=float(np.mean([values[b].reindex(fams).mean() for _, b, _ in pairs])),
                               diff=mean, ci_lo=lo, ci_hi=hi, direction=_sign(mean)))
    cols_s = ["metric", "teacher", "version", "seed", "run_v", "run_o", "value_v", "value_o", "diff", "n_families"]
    cols_t = ["metric", "teacher", "version", "n_seeds", "n_families", "mean_v", "mean_o", "diff", "ci_lo", "ci_hi", "direction"]
    return pd.DataFrame(rows_s, columns=cols_s), pd.DataFrame(rows_t, columns=cols_t)


# --------------------------------------------------------------------------- (1) cross-student disagreement


def cross_student_disagreement(mats: Mapping[str, pd.DataFrame], grid: pd.DataFrame, pairs: Sequence[tuple[str, str]] = DISAGREEMENT_PAIRS, n_boot: int = 10_000, seed: int = 0,
                               families: Optional[Mapping[str, Sequence[str]]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Share of (family, variant) cells where two students of the same teacher and seed have different majority acts.

    For every version pair (a, b) in `pairs` and every seed with both runs: per-family disagreement, JSD and the
    confident-cell disagreement (`family_compare`); per teacher the mean over seeds and families with a
    family-bootstrap CI (joint over seeds). `families` (teacher -> list) fixes the family set per teacher.
    Returns (per_seed, per_teacher). The reference is `seed_pair_disagreement` (O seed a vs O seed b); the
    centred statistic for the verdict is `excess_disagreement`.
    """
    rng = np.random.default_rng([seed, zlib.crc32(b"disagreement")])
    rows_s, rows_t = [], []
    for teacher in sorted(grid["teacher"].unique()):
        g = grid[grid["teacher"] == teacher]
        fams_t = families.get(teacher) if families else None
        for va, vb in pairs:
            trip = [(row[va], row[vb], int(row["seed"])) for _, row in g.iterrows() if isinstance(row[va], str) and isinstance(row[vb], str) and row[va] in mats and row[vb] in mats]
            if not trip:
                continue
            cmp = {(a, b): family_compare(_restrict(mats[a], fams_t), _restrict(mats[b], fams_t)) for a, b, _ in trip}
            fams = _common_families([c["disagree"] for c in cmp.values()])
            if not fams:
                continue
            Dd = np.stack([cmp[(a, b)]["disagree"].reindex(fams).to_numpy(dtype=float) for a, b, _ in trip])
            Dj = np.stack([cmp[(a, b)]["jsd"].reindex(fams).to_numpy(dtype=float) for a, b, _ in trip])
            Dc = np.stack([cmp[(a, b)]["disagree_conf"].reindex(fams).to_numpy(dtype=float) for a, b, _ in trip])
            for (a, b, s), d, j, c in zip(trip, Dd, Dj, Dc):
                rows_s.append(dict(teacher=teacher, pair=f"{va}-{vb}", seed=s, run_a=a, run_b=b, disagree=float(np.nanmean(d)), jsd=float(j.mean()), disagree_conf=float(np.nanmean(c)) if np.isfinite(c).any() else np.nan, n_families=len(fams)))
            m_d, lo_d, hi_d = _boot_mean(Dd, n_boot, rng)
            m_j, lo_j, hi_j = _boot_mean(Dj, n_boot, rng)
            m_c = float(np.nanmean(Dc)) if np.isfinite(Dc).any() else np.nan
            rows_t.append(dict(teacher=teacher, pair=f"{va}-{vb}", n_seeds=len(trip), n_families=len(fams), disagree=m_d, ci_lo=lo_d, ci_hi=hi_d, jsd=m_j, jsd_ci_lo=lo_j, jsd_ci_hi=hi_j, disagree_conf=m_c))
    return (pd.DataFrame(rows_s, columns=["teacher", "pair", "seed", "run_a", "run_b", "disagree", "jsd", "disagree_conf", "n_families"]),
            pd.DataFrame(rows_t, columns=["teacher", "pair", "n_seeds", "n_families", "disagree", "ci_lo", "ci_hi", "jsd", "jsd_ci_lo", "jsd_ci_hi", "disagree_conf"]))


def seed_pair_disagreement(mats: Mapping[str, pd.DataFrame], grid: pd.DataFrame, version: str = "O", families: Optional[Mapping[str, Sequence[str]]] = None) -> pd.DataFrame:
    """Seed-pair null of the disagreement rate: S_{T,V,a} vs S_{T,V,b} for every pair of seeds a < b of the same teacher
    (on `families[teacher]` when given)."""
    rows = []
    for teacher in sorted(grid["teacher"].unique()):
        g = grid[(grid["teacher"] == teacher) & grid[version].notna()].sort_values("seed")
        runs = [(int(s), r) for s, r in zip(g["seed"], g[version]) if r in mats]
        fams_t = families.get(teacher) if families else None
        for i in range(len(runs)):
            for j in range(i + 1, len(runs)):
                (sa, ra), (sb, rb) = runs[i], runs[j]
                cmp = family_compare(_restrict(mats[ra], fams_t), _restrict(mats[rb], fams_t))
                rows.append(dict(teacher=teacher, version=version, seed_a=sa, seed_b=sb, run_a=ra, run_b=rb, disagree=float(np.nanmean(cmp["disagree"])) if len(cmp) else np.nan, jsd=float(cmp["jsd"].mean()) if len(cmp) else np.nan,
                                 disagree_conf=float(np.nanmean(cmp["disagree_conf"])) if len(cmp) and cmp["disagree_conf"].notna().any() else np.nan, n_families=len(cmp)))
    return pd.DataFrame(rows, columns=["teacher", "version", "seed_a", "seed_b", "run_a", "run_b", "disagree", "jsd", "disagree_conf", "n_families"])


def excess_disagreement(dis_t: pd.DataFrame, spd: pd.DataFrame, value: str = "disagree") -> pd.DataFrame:
    """Centred statistic for metric 1: per (teacher, pair) the mean V-W disagreement minus the teacher's OWN mean O-O
    seed-pair disagreement (`oo_mean`), with `var_oo_mean` = delete-one-seed jackknife variance of that O-O mean
    (the O-O pairs share seeds, so their mean is a U-statistic whose variance a naive sd / sqrt(n) understates).
    Pooling the O-O null over teachers without centring would mix teacher-level offsets into the per-teacher test;
    `e3_verdict(..., extra_var=var_oo_mean)` adds this variance to the statistic's null SD. `n_oo_pairs` per teacher."""
    cols = ["teacher", "pair", "n_seeds", value, "oo_mean", "var_oo_mean", "n_oo_pairs", "excess", "ci_lo", "ci_hi"]
    if dis_t.empty:
        return pd.DataFrame(columns=cols)
    rows = []
    for _, r in dis_t.iterrows():
        g = spd[(spd["teacher"] == r["teacher"])].dropna(subset=[value]) if len(spd) else pd.DataFrame()
        mu, var_mu, n_pairs = np.nan, np.nan, 0
        if len(g):
            mu, n_pairs = float(g[value].mean()), int(len(g))
            seeds = sorted(set(g["seed_a"]) | set(g["seed_b"]))
            loo = np.array([g[(g["seed_a"] != s) & (g["seed_b"] != s)][value].mean() for s in seeds]) if len(seeds) >= 3 else np.array([])
            loo = loo[np.isfinite(loo)]
            var_mu = float((len(loo) - 1) / len(loo) * np.sum((loo - loo.mean()) ** 2)) if len(loo) >= 2 else np.nan
        ex = float(r[value] - mu) if np.isfinite(mu) else np.nan
        rows.append(dict(teacher=r["teacher"], pair=r["pair"], n_seeds=int(r["n_seeds"]), **{value: float(r[value])}, oo_mean=mu, var_oo_mean=var_mu, n_oo_pairs=n_pairs, excess=ex,
                         ci_lo=float(r["ci_lo"] - mu) if np.isfinite(mu) else np.nan, ci_hi=float(r["ci_hi"] - mu) if np.isfinite(mu) else np.nan))
    return pd.DataFrame(rows, columns=cols)


# --------------------------------------------------------------------------- (2) consistency change, (3) drift


def consistency_delta(mats: Mapping[str, pd.DataFrame], grid: pd.DataFrame, versions: Sequence[str] = ("F", "C"), n_boot: int = 10_000, seed: int = 0,
                      families: Optional[Mapping[str, Sequence[str]]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Flip rate and cross-framing JSD of S_{T,V,s} minus S_{T,O,s} (group B), via `paired_delta`; metric in {flip, jsd}."""
    fc = {r: family_consistency(p) for r, p in mats.items() if is_run_id(r)}
    out_s, out_t = [], []
    for metric in ("flip", "jsd"):
        s, t = paired_delta({r: d[metric] for r, d in fc.items()}, grid, versions, n_boot=n_boot, seed=seed, label=metric, families=families)
        out_s.append(s)
        out_t.append(t)
    return pd.concat(out_s, ignore_index=True), pd.concat(out_t, ignore_index=True)


def drift_delta(mats_s: Mapping[str, pd.DataFrame], mats_t: Mapping[str, pd.DataFrame], grid: pd.DataFrame, versions: Sequence[str] = ("F", "C"), n_boot: int = 10_000, seed: int = 0,
                families: Optional[Mapping[str, Sequence[str]]] = None) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Teacher-agreement change agree(S_{T,V,s}, T) - agree(S_{T,O,s}, T) and excess teacher drift JSD(S_{T,V,s}, T) -
    JSD(S_{T,O,s}, T), paired by seed (group C); metric in {agree, jsd}. Runs whose teacher has no profile are skipped.
    Family-unit means over complete families (see `family_compare`), not the cell-weighted E1 tables."""
    cmp: dict[str, pd.DataFrame] = {}
    for r, piv in mats_s.items():
        if is_run_id(r) and parse_run_id(r).teacher in mats_t:
            cmp[r] = family_compare(piv, mats_t[parse_run_id(r).teacher])
    out_s, out_t = [], []
    for metric in ("agree", "jsd"):
        s, t = paired_delta({r: d[metric] for r, d in cmp.items()}, grid, versions, n_boot=n_boot, seed=seed, label=metric, families=families)
        out_s.append(s)
        out_t.append(t)
    return pd.concat(out_s, ignore_index=True), pd.concat(out_t, ignore_index=True)


# --------------------------------------------------------------------------- seed-pair null and verdict


def seed_pair_null(run_table: pd.DataFrame, value: str, version: str = "O") -> pd.DataFrame:
    """Seed-pair null of a per-run scalar: value(S_{T,V,a}) - value(S_{T,V,b}) for every pair of seeds a < b of the same
    teacher (signed; the rule uses |diff|). `run_table` needs run_id, teacher, version, seed and `value`."""
    rows = []
    t = run_table[(run_table["version"] == version)].dropna(subset=[value])
    for teacher, g in t.groupby("teacher", sort=True):
        g = g.sort_values("seed")
        recs = list(zip(g["seed"], g["run_id"], g[value]))
        for i in range(len(recs)):
            for j in range(i + 1, len(recs)):
                (sa, ra, va), (sb, rb, vb) = recs[i], recs[j]
                rows.append(dict(metric=value, teacher=teacher, version=version, seed_a=int(sa), seed_b=int(sb), run_a=ra, run_b=rb, diff=float(va - vb), abs_diff=float(abs(va - vb))))
    return pd.DataFrame(rows, columns=["metric", "teacher", "version", "seed_a", "seed_b", "run_a", "run_b", "diff", "abs_diff"])


def null_summary(values: Sequence[float]) -> dict:
    """n, mean, sd, q95 of a null sample (NaNs dropped)."""
    v = np.asarray([x for x in values if not (isinstance(x, float) and np.isnan(x))], dtype=float)
    if len(v) == 0:
        return {"n": 0, "mean": np.nan, "sd": np.nan, "q95": np.nan}
    return {"n": int(len(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else np.nan, "q95": float(np.quantile(v, 0.95))}


def _clean(values: Sequence[float]) -> np.ndarray:
    return np.asarray([x for x in values if x is not None and not (isinstance(x, (float, np.floating)) and np.isnan(x))], dtype=float)


def e3_verdict(
    stats: Mapping[str, float],
    null: Sequence[float],
    one_sided: bool = False,
    n_seeds: int | Mapping[str, int] = 1,
    cis: Optional[Mapping[str, tuple[float, float]]] = None,
    extra_var: Optional[Mapping[str, float]] = None,
    null_groups: Optional[Sequence[str]] = None,
    df: Optional[int] = None,
    n_required: int = N_TEACHERS_REQUIRED,
    min_frac: float = MIN_TEACHER_FRAC,
    alpha: float = 0.05,
) -> dict:
    """Decision rule of docs/03 E3 row (frozen): an effect counts if in >= `min_frac` (2/3) of the `n_required` (3)
    teachers the seed-paired statistic exceeds the 95th percentile of the seed-pair null of that statistic and the
    direction is the same across those teachers.

    Inputs
      stats       teacher -> per-teacher statistic: the mean over `n_seeds` seed-paired differences V - O, or (with
                  one_sided=True) a centred disagreement excess (`excess_disagreement`).
      null        the pooled seed-pair null of the SINGLE-PAIR quantity: signed O_a - O_b differences (two-sided) or
                  single-pair O-O rates (one-sided, centred within teacher when `null_groups` gives the teacher of
                  each value).
      n_seeds     number of seed pairs averaged per teacher (int or per teacher).
      cis         teacher -> (lo, hi) family-bootstrap 95% CI of the statistic, for the TOST (docs/04 §3).
      extra_var   teacher -> extra variance of the statistic beyond seed noise / n_seeds (e.g. `var_oo_mean` of the
                  centring constant in `excess_disagreement`).
      df          degrees of freedom of the seed-noise estimate, sum_T (n_O,T - 1); None -> normal reference.
      n_required  teachers the rule presupposes; fewer teachers with a statistic -> "pending (n_teachers k < 3)".

    Scale matching: the single-pair null SD is sd_1 = sqrt(mean(d^2)) (two-sided: differences are symmetric about 0)
    or the within-teacher sd of the rates (one-sided); the statistic's null SD is
    SD_stat = sqrt(sd_1^2 / n_seeds + extra_var) and q95 = t_{1 - alpha/2, df} * SD_stat (one-sided: t_{1 - alpha, df}).
    Assumes seed noise approximately normal and independent across seeds; the real same-seed pairs share init and
    data order, so the null is conservative (tasks/e3_plan.md §3). The raw single-pair threshold `q95_single`
    (95th percentile of |d| or of the centred rates) and `exceeds_q95_single` are kept as a sensitivity column.

    Per teacher: stat, effect_sd = stat / SD_stat, exceeds_q95, sign, p (t reference), p_holm over the teachers,
    tost (CI inside +/- 1 SD_stat; None without a CI).
    verdict: "effect"; otherwise "no effect" when >= min_frac of the required teachers pass the TOST (equivalence
    bound 1 null SD, with a 95% CI, i.e. TOST at alpha 0.025), else "inconclusive"; "pending (...)" when the inputs
    do not allow the rule.
    """
    teachers = [t for t, s in stats.items() if s is not None and not np.isnan(s)]
    nv = _clean(null)
    need = int(np.ceil(min_frac * n_required - 1e-9))
    out = {"verdict": "pending", "n_teachers": len(teachers), "n_required": n_required, "n_need": need, "n_pass": 0, "n_tost": 0, "n_null": int(len(nv)), "q95": np.nan, "q95_single": np.nan,
           "null_sd_single": np.nan, "null_sd": np.nan, "null_mean": np.nan, "df": df, "one_sided": one_sided, "tost_bound": "1 null SD of the statistic (95% CI inside)",
           "direction": "nan", "direction_consistent": None, "passing": [], "per_teacher": {},
           "rule": f"effect iff >= {min_frac:.2f} of {n_required} teachers exceed the t-scaled seed-pair null q95 with the same direction; no effect iff the same share pass the TOST; else inconclusive"}
    if not teachers:
        out["verdict"] = "pending (no paired runs)"
        return out
    if len(teachers) < n_required:
        out["verdict"] = f"pending (n_teachers {len(teachers)} < {n_required})"
        return out
    if len(nv) < 2:
        out["verdict"] = "pending (seed-pair null needs >= 2 O seeds per teacher)"
        return out
    if one_sided:
        if null_groups is not None and len(null_groups) == len(list(null)):
            grp = np.asarray([g for g, x in zip(null_groups, null) if x is not None and not (isinstance(x, (float, np.floating)) and np.isnan(x))])
            centred = nv.copy()
            for g in set(grp):
                centred[grp == g] = nv[grp == g] - nv[grp == g].mean()
            k = len(set(grp))
            sd1 = float(np.sqrt(np.sum(centred**2) / max(1, len(nv) - k)))
        else:
            centred = nv - nv.mean()
            sd1 = float(nv.std(ddof=1))
        ref_single = centred
    else:
        sd1 = float(np.sqrt(np.mean(nv**2)))
        ref_single = np.abs(nv)
    q95_single = float(np.quantile(ref_single, 0.95))
    tq = float(sps.t.ppf(1 - alpha if one_sided else 1 - alpha / 2, df)) if df else float(sps.norm.ppf(1 - alpha if one_sided else 1 - alpha / 2))
    out.update(q95_single=q95_single, null_sd_single=sd1, null_mean=float(nv.mean()))
    pvals, sds = [], []
    for t in teachers:
        s = float(stats[t])
        n_s = int(n_seeds[t]) if isinstance(n_seeds, Mapping) else int(n_seeds)
        ev = float(extra_var.get(t, 0.0)) if extra_var else 0.0
        ev = 0.0 if not np.isfinite(ev) else ev
        sd_stat = float(np.sqrt(sd1**2 / max(1, n_s) + ev))
        sds.append(sd_stat)
        q95 = tq * sd_stat
        mag = s if one_sided else abs(s)
        z = mag / sd_stat if sd_stat > 0 else np.inf
        if df:
            p = float(sps.t.sf(z, df)) if one_sided else float(2 * sps.t.sf(abs(z), df))
        else:
            p = float(sps.norm.sf(z)) if one_sided else float(2 * sps.norm.sf(abs(z)))
        pvals.append(p)
        tost = None
        if cis and t in cis and all(np.isfinite(c) for c in cis[t]):
            tost = bool(cis[t][0] >= -sd_stat and cis[t][1] <= sd_stat and abs(s) <= sd_stat)
        out["per_teacher"][t] = {"stat": s, "n_seeds": n_s, "null_sd": sd_stat, "q95": q95, "effect_sd": (s / sd_stat) if sd_stat > 0 else np.nan, "exceeds_q95": bool(mag > q95),
                                 "exceeds_q95_single": bool(mag > q95_single), "sign": _sign(s), "p_null": p, "p_holm": np.nan, "tost": tost, "ci": tuple(cis[t]) if cis and t in cis else None}
    for t, ph in zip(teachers, holm(pvals)):
        out["per_teacher"][t]["p_holm"] = float(ph)
    out.update(q95=float(np.mean([d["q95"] for d in out["per_teacher"].values()])), null_sd=float(np.mean(sds)))
    passing = [t for t in teachers if out["per_teacher"][t]["exceeds_q95"]]
    signs = {out["per_teacher"][t]["sign"] for t in passing}
    consistent = len(signs) <= 1
    n_tost = sum(1 for t in teachers if out["per_teacher"][t]["tost"])
    out.update(n_pass=len(passing), n_tost=n_tost, passing=passing, direction_consistent=consistent, direction=(signs.pop() if len(signs) == 1 else ("mixed" if signs else "nan")))
    if len(passing) >= need and consistent:
        out["verdict"] = "effect"
    elif n_tost >= need:
        out["verdict"] = "no effect"
    else:
        out["verdict"] = "inconclusive"
    return out


# --------------------------------------------------------------------------- (4) homogenization


def homogenization(mats: Mapping[str, pd.DataFrame], grid: pd.DataFrame, versions: Sequence[str] = VERSIONS, n_boot: int = 10_000, seed: int = 0) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Homogenization index per version V: mean pairwise distance between students of DIFFERENT teachers, seed-matched.

    Distances per (version, seed, teacher pair): judgment JSD = mean over cells of JSD(p_A, p_B) and profile distance
    1 - corr(r_A, r_B) with r the family-demeaned shift over the cells (same families for every run: those complete
    for all runs of the grid). Per version the means over cells with family-bootstrap CIs, and the paired difference
    vs V = O over the (seed, pair) cells both versions have. A fix that works by homogenising shows a DROP vs O.

    Calibration guard: the judgment JSD between any two students shrinks mechanically when a version's readouts move
    towards 0.5, so per cell / version the table also gives `mean_abs_margin` (mean |p - 0.5| of the two runs),
    `share_low_margin` (cells with |p - 0.5| < CONFIDENT_MARGIN), the majority-act disagreement `maj_disagree` (ties
    excluded) and `maj_disagree_conf` (both runs confident). 1 - corr(profile) is scale-free and is the index to read
    first. Returns (per_cell, per_version).
    """
    runs = [r for v in versions for r in grid[v].dropna() if r in mats]
    cols_c = ["version", "seed", "teacher_a", "teacher_b", "run_a", "run_b", "jsd", "one_minus_corr", "maj_disagree", "maj_disagree_conf", "mean_abs_margin", "share_low_margin", "n_families"]
    cols_v = ["version", "n_cells", "n_seeds", "n_families", "jsd", "jsd_ci_lo", "jsd_ci_hi", "one_minus_corr", "omc_ci_lo", "omc_ci_hi", "maj_disagree", "maj_disagree_conf", "mean_abs_margin", "share_low_margin",
              "n_paired_cells", "d_jsd_vs_O", "d_jsd_ci_lo", "d_jsd_ci_hi", "d_omc_vs_O", "d_omc_ci_lo", "d_omc_ci_hi"]
    if len(runs) < 2:
        return pd.DataFrame(columns=cols_c), pd.DataFrame(columns=cols_v)
    fams = sorted(set.intersection(*[set(mats[r].index) for r in runs]))
    if len(fams) < 4:
        return pd.DataFrame(columns=cols_c), pd.DataFrame(columns=cols_v)
    Pm = {r: mats[r].reindex(fams).to_numpy(dtype=float) for r in runs}
    Rm = {r: p - p.mean(axis=1, keepdims=True) for r, p in Pm.items()}
    rng = np.random.default_rng([seed, zlib.crc32(b"homogenization")])
    n_f = len(fams)
    cells: dict[str, dict[tuple[int, str, str], tuple[str, str]]] = {}
    rows_c = []
    for v in versions:
        g = grid[grid[v].notna()]
        for s, gs in g.groupby("seed"):
            teachers = sorted(gs["teacher"])
            run_of = dict(zip(gs["teacher"], gs[v]))
            for i, a in enumerate(teachers):
                for b in teachers[i + 1 :]:
                    ra, rb = run_of[a], run_of[b]
                    if ra not in Pm or rb not in Pm:
                        continue
                    cells.setdefault(v, {})[(int(s), a, b)] = (ra, rb)
                    corr = float(M._corr_with_fixed(Rm[ra].ravel()[None, :], Rm[rb].ravel())[0])
                    A, B = Pm[ra], Pm[rb]
                    tie = (A == 0.5) | (B == 0.5)
                    dif = ((A > 0.5) != (B > 0.5)) & ~tie
                    conf = (np.abs(A - 0.5) >= CONFIDENT_MARGIN) & (np.abs(B - 0.5) >= CONFIDENT_MARGIN)
                    rows_c.append(dict(version=v, seed=int(s), teacher_a=a, teacher_b=b, run_a=ra, run_b=rb, jsd=float(binary_jsd(A, B).mean()), one_minus_corr=1.0 - corr,
                                       maj_disagree=float(dif.sum() / (~tie).sum()) if (~tie).any() else np.nan, maj_disagree_conf=float((dif & conf).sum() / conf.sum()) if conf.any() else np.nan,
                                       mean_abs_margin=float((np.abs(A - 0.5).mean() + np.abs(B - 0.5).mean()) / 2), share_low_margin=float(((np.abs(A - 0.5) < CONFIDENT_MARGIN).mean() + (np.abs(B - 0.5) < CONFIDENT_MARGIN).mean()) / 2),
                                       n_families=n_f))
    per_cell = pd.DataFrame(rows_c, columns=cols_c)

    def boot_stats(keys: Sequence[tuple[str, str]], ref_keys: Optional[Sequence[tuple[str, str]]] = None) -> dict:
        """Mean JSD and mean (1 - corr) over the cells with CIs; with ref_keys (same length, paired) the differences."""
        J = np.stack([binary_jsd(Pm[a], Pm[b]).mean(axis=1) for a, b in keys])  # (k, n_f)
        res: dict = {}
        if ref_keys is not None:
            Jr = np.stack([binary_jsd(Pm[a], Pm[b]).mean(axis=1) for a, b in ref_keys])
            res["d_jsd"], res["d_jsd_lo"], res["d_jsd_hi"] = _boot_mean(J - Jr, n_boot, rng)
        else:
            res["jsd"], res["jsd_lo"], res["jsd_hi"] = _boot_mean(J, n_boot, rng)
        omc = np.array([1.0 - float(M._corr_with_fixed(Rm[a].ravel()[None, :], Rm[b].ravel())[0]) for a, b in keys])
        if ref_keys is not None:
            omc_r = np.array([1.0 - float(M._corr_with_fixed(Rm[a].ravel()[None, :], Rm[b].ravel())[0]) for a, b in ref_keys])
            res["d_omc"] = float((omc - omc_r).mean())
        else:
            res["omc"] = float(omc.mean())
        if n_boot > 0:
            vals = np.empty(n_boot)
            for start in range(0, n_boot, 1000):
                m = min(1000, n_boot - start)
                boots = rng.integers(0, n_f, size=(m, n_f))
                acc = np.zeros(m)
                for idx, (a, b) in enumerate(keys):
                    c = M._rowwise_corr(Rm[a][boots].reshape(m, -1), Rm[b][boots].reshape(m, -1))
                    if ref_keys is not None:
                        ar, br = ref_keys[idx]
                        c = c - M._rowwise_corr(Rm[ar][boots].reshape(m, -1), Rm[br][boots].reshape(m, -1))
                        acc += -c  # (1 - c_v) - (1 - c_o) = c_o - c_v
                    else:
                        acc += 1.0 - c
                vals[start : start + m] = acc / len(keys)
            lo, hi = np.nanquantile(vals, [0.025, 0.975])
            if ref_keys is not None:
                res["d_omc_lo"], res["d_omc_hi"] = float(lo), float(hi)
            else:
                res["omc_lo"], res["omc_hi"] = float(lo), float(hi)
        return res

    rows_v = []
    for v in versions:
        cv = cells.get(v, {})
        if not cv:
            continue
        keys = list(cv.values())
        st = boot_stats(keys)
        pc = per_cell[per_cell["version"] == v]
        row = dict(version=v, n_cells=len(keys), n_seeds=len({k[0] for k in cv}), n_families=n_f, jsd=st["jsd"], jsd_ci_lo=st.get("jsd_lo", np.nan), jsd_ci_hi=st.get("jsd_hi", np.nan),
                   one_minus_corr=st["omc"], omc_ci_lo=st.get("omc_lo", np.nan), omc_ci_hi=st.get("omc_hi", np.nan),
                   maj_disagree=float(pc["maj_disagree"].mean()), maj_disagree_conf=float(pc["maj_disagree_conf"].mean()), mean_abs_margin=float(pc["mean_abs_margin"].mean()), share_low_margin=float(pc["share_low_margin"].mean()),
                   n_paired_cells=0, d_jsd_vs_O=np.nan, d_jsd_ci_lo=np.nan, d_jsd_ci_hi=np.nan, d_omc_vs_O=np.nan, d_omc_ci_lo=np.nan, d_omc_ci_hi=np.nan)
        co = cells.get("O", {})
        shared = sorted(set(cv) & set(co))
        if v != "O" and shared:
            d = boot_stats([cv[k] for k in shared], [co[k] for k in shared])
            row.update(n_paired_cells=len(shared), d_jsd_vs_O=d["d_jsd"], d_jsd_ci_lo=d.get("d_jsd_lo", np.nan), d_jsd_ci_hi=d.get("d_jsd_hi", np.nan), d_omc_vs_O=d["d_omc"], d_omc_ci_lo=d.get("d_omc_lo", np.nan), d_omc_ci_hi=d.get("d_omc_hi", np.nan))
        rows_v.append(row)
    return per_cell, pd.DataFrame(rows_v, columns=cols_v)


# --------------------------------------------------------------------------- (5) inheritance by form


def inheritance_by_form(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    control: Optional[pd.DataFrame],
    grid: pd.DataFrame,
    variants: Sequence[str] = SEEN_VARIANTS,
    versions: Sequence[str] = ("F", "C"),
    n_boot: int = 10_000,
    seed: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Per-run delta-rho (partial given the base prior r_0 when `control` is given, as e1_metrics.inheritance with
    control; raw Pearson otherwise) and its seed-paired change V minus O.

    For one teacher every run of the grid (O and the versions) is scored on ONE family set: the families complete
    for all of that teacher's runs, every teacher profile and r_0, so delta_rho_V - delta_rho_O is a within-cell
    difference. delta_rho = rho(own | r_0) - max_other rho(other | r_0). Per teacher and version the seed mean of the
    difference with a family-bootstrap CI (families resampled jointly for every run of the teacher).
    Returns (per_run, per_seed, per_teacher).
    """
    teachers = sorted(shifts_t["teacher"].unique())
    ctrl_name: Optional[str] = None
    if control is not None and len(control):
        names = control["teacher"].unique()
        if len(names) != 1:
            raise ValueError(f"control must hold exactly one profile, got {list(names)}")
        ctrl_name = str(names[0])
    cols_r = ["run_id", "teacher", "version", "seed", "n_families", "rho_own", "rho_other_max", "other_argmax", "delta_rho", "control", "rho_base"]
    cols_s = ["teacher", "version", "seed", "run_v", "run_o", "delta_rho_v", "delta_rho_o", "diff", "n_families", "control"]
    cols_t = ["teacher", "version", "n_seeds", "n_families", "mean_v", "mean_o", "diff", "ci_lo", "ci_hi", "direction", "control"]
    rows_r, rows_s, rows_t = [], [], []
    present = set(shifts_s["teacher"].unique())
    rng = np.random.default_rng([seed, zlib.crc32(b"inheritance_by_form")])
    for teacher in sorted(grid["teacher"].unique()):
        if teacher not in teachers or len(teachers) < 2:
            continue
        g = grid[grid["teacher"] == teacher]
        runs = [r for v in ("O", *versions) for r in g[v].dropna() if r in present]
        if not runs:
            continue
        tables = [shifts_s[shifts_s["teacher"].isin(runs)], shifts_t] + ([control] if ctrl_name else [])
        fams = M.complete_families(pd.concat(tables), [*runs, *teachers] + ([ctrl_name] if ctrl_name else []), variants)
        if len(fams) < 4:
            continue
        n_f = len(fams)
        S = {r: M._shift_matrix(shifts_s[shifts_s["teacher"] == r], r, fams, variants) for r in runs}
        T = {t: M._shift_matrix(shifts_t, t, fams, variants) for t in teachers}
        Z = M._shift_matrix(control, ctrl_name, fams, variants) if ctrl_name else None
        others = [t for t in teachers if t != teacher]

        def rho_obs(Sm: np.ndarray) -> dict[str, float]:
            x = Sm.ravel()
            if Z is None:
                return {t: float(M._corr_with_fixed(x[None, :], T[t].ravel())[0]) for t in teachers}
            return {t: float(M._partial_corr_with_fixed(x[None, :], T[t].ravel(), Z.ravel())[0]) for t in teachers}

        def delta_boot(Sm: np.ndarray, boots: np.ndarray) -> np.ndarray:
            m = len(boots)
            Xb = Sm[boots].reshape(m, -1)
            if Z is None:
                rb = {t: M._rowwise_corr(Xb, T[t][boots].reshape(m, -1)) for t in teachers}
            else:
                Zb = Z[boots].reshape(m, -1)
                rb = {t: M._rowwise_partial_corr(Xb, T[t][boots].reshape(m, -1), Zb) for t in teachers}
            return rb[teacher] - np.max(np.stack([rb[t] for t in others]), axis=0)

        d_run: dict[str, float] = {}
        for r in runs:
            rh = rho_obs(S[r])
            oth = {t: rh[t] for t in others}
            amax = max(oth, key=oth.get)
            d_run[r] = rh[teacher] - oth[amax]
            k = parse_run_id(r)
            rows_r.append(dict(run_id=r, teacher=teacher, version=k.version, seed=k.seed, n_families=n_f, rho_own=rh[teacher], rho_other_max=oth[amax], other_argmax=amax, delta_rho=d_run[r], control=ctrl_name,
                               rho_base=float(M._corr_with_fixed(S[r].ravel()[None, :], Z.ravel())[0]) if Z is not None else np.nan))
        for v in versions:
            pairs = [(rv, ro, s) for _, rv, ro, s in seed_pairs(g, v) if rv in S and ro in S]
            if not pairs:
                continue
            for rv, ro, s in pairs:
                rows_s.append(dict(teacher=teacher, version=v, seed=s, run_v=rv, run_o=ro, delta_rho_v=d_run[rv], delta_rho_o=d_run[ro], diff=d_run[rv] - d_run[ro], n_families=n_f, control=ctrl_name))
            diffs = np.array([d_run[rv] - d_run[ro] for rv, ro, _ in pairs])
            lo, hi = np.nan, np.nan
            if n_boot > 0:
                vals = np.empty(n_boot)
                for start in range(0, n_boot, 500):
                    m = min(500, n_boot - start)
                    boots = rng.integers(0, n_f, size=(m, n_f))
                    acc = np.zeros(m)
                    for rv, ro, _ in pairs:
                        acc += delta_boot(S[rv], boots) - delta_boot(S[ro], boots)
                    vals[start : start + m] = acc / len(pairs)
                lo, hi = (float(x) for x in np.nanquantile(vals, [0.025, 0.975]))
            rows_t.append(dict(teacher=teacher, version=v, n_seeds=len(pairs), n_families=n_f, mean_v=float(np.mean([d_run[rv] for rv, _, _ in pairs])), mean_o=float(np.mean([d_run[ro] for _, ro, _ in pairs])),
                               diff=float(diffs.mean()), ci_lo=lo, ci_hi=hi, direction=_sign(float(diffs.mean())), control=ctrl_name))
    return pd.DataFrame(rows_r, columns=cols_r), pd.DataFrame(rows_s, columns=cols_s), pd.DataFrame(rows_t, columns=cols_t)


def joint_D_by_version(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    control: Optional[pd.DataFrame],
    grid: pd.DataFrame,
    variants: Sequence[str] = SEEN_VARIANTS,
    versions: Sequence[str] = VERSIONS,
    n_perm: int = 10_000,
    n_boot: int = 10_000,
    seed: int = 0,
) -> tuple[pd.DataFrame, dict[str, dict]]:
    """e1_metrics.joint_partial_D per version: students of each teacher pooled over seeds within the version (one
    seed-mean profile per teacher), D = diagonal minus off-diagonal mean of the student x teacher partial-rho matrix
    given r_0 (raw when control is None), with its family bootstrap CI and permutation p. Returns (table, raw dicts)."""
    present = set(shifts_s["teacher"].unique())
    cols = ["version", "n_teachers", "n_families", "D", "ci_lo", "ci_hi", "p_perm", "null_mean", "null_sd", "D_specific", "ci_specific_lo", "ci_specific_hi", "p_perm_specific", "D_shared", "D_raw", "D_scalefree", "n_perm", "n_boot", "control", "e2_secondary_rule"]
    rows, raw = [], {}
    for v in versions:
        pooled: dict[str, pd.DataFrame] = {}
        for teacher, g in grid.groupby("teacher"):
            runs = [r for r in g[v].dropna() if r in present]
            if runs and teacher in set(shifts_t["teacher"]):
                student = parse_run_id(runs[0]).student
                pooled[teacher] = M.pooled_shifts(shifts_s, runs, f"{student}.{teacher}_{v}_pooled")
        if len(pooled) < 2:
            continue
        d = M.joint_partial_D(pooled, shifts_t, control if (control is not None and len(control)) else None, variants, n_perm=n_perm, n_boot=n_boot, seed=seed)
        raw[v] = d
        rows.append(dict(version=v, n_teachers=d["n_teachers"], n_families=d["n_families"], D=d["D"], ci_lo=d["ci_lo"], ci_hi=d["ci_hi"], p_perm=d["p_perm"], null_mean=d["null_mean"], null_sd=d["null_sd"],
                         D_specific=d["D_specific"], ci_specific_lo=d["ci_specific_lo"], ci_specific_hi=d["ci_specific_hi"], p_perm_specific=d["p_perm_specific"], D_shared=d["D_shared"], D_raw=d["D_raw"], D_scalefree=d["D_scalefree"],
                         n_perm=d["n_perm"], n_boot=d["n_boot"], control=d["control"], e2_secondary_rule=M.e2_secondary_verdict(d)))
    return pd.DataFrame(rows, columns=cols), raw


def suggestibility_by_version(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    grid: pd.DataFrame,
    versions: Sequence[str] = VERSIONS,
    families: Optional[Sequence[str]] = None,
    pos: str = "T5",
    neg: str = "T6",
    n_boot: int = 10_000,
    seed: int = 0,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """e1_metrics.suggestibility_groups with one group per (teacher, version) of students ("students:{T}:{V}") plus
    each teacher ("teacher:{T}"); returns (groups, diffs) where diffs holds s(students:T:V) - s(students:T:O) and
    s(students:T:V) - s(teacher:T) with the paired family-bootstrap CIs."""
    present = set(shifts_s["teacher"].unique())
    groups: dict[str, list[str]] = {}
    for teacher, g in grid.groupby("teacher", sort=True):
        for v in versions:
            runs = [r for r in g[v].dropna() if r in present]
            if runs:
                groups[f"students:{teacher}:{v}"] = runs
    for t in sorted(shifts_t["teacher"].unique()):
        groups[f"teacher:{t}"] = [t]
    gcols = ["group", "kind", "teacher", "version", "n_profiles", "n_families", "s", "ci_lo", "ci_hi"]
    dcols = ["teacher", "version", "contrast", "diff", "ci_lo", "ci_hi"]
    if not groups:
        return pd.DataFrame(columns=gcols), pd.DataFrame(columns=dcols)
    gt, pairs = M.suggestibility_groups(pd.concat([shifts_s, shifts_t]), groups, families=families, pos=pos, neg=neg, n_boot=n_boot, seed=seed)
    if gt.empty:
        return pd.DataFrame(columns=gcols), pd.DataFrame(columns=dcols)
    parts = gt["group"].str.split(":", expand=True)
    gt["kind"] = parts[0]
    gt["teacher"] = parts[1]
    gt["version"] = parts[2] if parts.shape[1] > 2 else None
    gt.loc[gt["kind"] == "teacher", "version"] = ""
    rows = []
    for _, r in pairs.iterrows():
        a, b = r["a"].split(":"), r["b"].split(":")
        if a[0] == "students" and b[0] == "students" and a[1] == b[1] and ("O" in (a[2], b[2])) and a[2] != b[2]:
            # (students:T:O, students:T:V) or (students:T:V, students:T:O) in whatever order `versions` lists them: orient as s_V - s_O
            sign = 1.0 if b[2] == "O" else -1.0
            v = a[2] if b[2] == "O" else b[2]
            lo, hi = (float(r["ci_lo"]), float(r["ci_hi"])) if sign > 0 else (-float(r["ci_hi"]), -float(r["ci_lo"]))
            rows.append(dict(teacher=a[1], version=v, contrast="students:V - students:O", diff=sign * float(r["diff"]), ci_lo=lo, ci_hi=hi))
        elif a[0] == "students" and b[0] == "teacher" and a[1] == b[1]:
            rows.append(dict(teacher=a[1], version=a[2], contrast="students:V - teacher", diff=float(r["diff"]), ci_lo=float(r["ci_lo"]), ci_hi=float(r["ci_hi"])))
    return gt[gcols], pd.DataFrame(rows, columns=dcols)


# --------------------------------------------------------------------------- (6) content check of the training files


CHECKS: tuple[str, ...] = ("choice", "reasons", "conditions", "strength", "style", "format")
_LETTER_RE = re.compile(r"^\s*Answer:\s*([AB])\b", re.I)


def load_sft_versions(sft_dir: str | Path, teacher: str, seed: int = 1, versions: Sequence[str] = VERSIONS) -> dict[str, list[dict]]:
    """{version: rows of {sft_dir}/{teacher}_{version}_s{seed}.jsonl} for the files that exist (paired files share the
    prompt set across versions and the seeds differ only in row order, so one seed suffices)."""
    out: dict[str, list[dict]] = {}
    for v in versions:
        p = Path(sft_dir) / f"{teacher}_{v}_s{seed}.jsonl"
        if p.exists():
            out[v] = list(read_jsonl(p))
    return out


def load_rewrites(path: str | Path) -> list[dict]:
    """Rows of a rewrites.jsonl (prompt_id, version, attempt, text, checks{...}, kept); [] when the file is missing."""
    p = Path(path)
    return list(read_jsonl(p)) if p.exists() else []


def kept_attempts(rewrites: Iterable[dict], version: str) -> dict[str, dict]:
    """prompt_id -> the last kept attempt row for `version` (the row scripts/10 uses, cf. vcd.train.data.kept_rewrites)."""
    best: dict[str, tuple[int, dict]] = {}
    for r in rewrites:
        if r.get("version") != version or not r.get("kept"):
            continue
        a = int(r.get("attempt", 0))
        if r["prompt_id"] not in best or a >= best[r["prompt_id"]][0]:
            best[r["prompt_id"]] = (a, r)
    return {pid: row for pid, (_, row) in best.items()}


def rewrite_yield(rewrites: Iterable[dict]) -> pd.DataFrame:
    """Per version: items attempted, items kept, kept share, mean attempts per item (from the rewrite log alone)."""
    rows = list(rewrites)
    out = []
    for v in sorted({r.get("version") for r in rows if r.get("version")}):
        rv = [r for r in rows if r.get("version") == v]
        items = {r["prompt_id"] for r in rv}
        kept = {r["prompt_id"] for r in rv if r.get("kept")}
        out.append(dict(version=v, n_attempted=len(items), n_kept=len(kept), kept_share=(len(kept) / len(items)) if items else np.nan, mean_attempts=(len(rv) / len(items)) if items else np.nan))
    return pd.DataFrame(out, columns=["version", "n_attempted", "n_kept", "kept_share", "mean_attempts"])


def rationale_of(text_target: str) -> str:
    """The rationale text of an SFT target ' X\\nRationale: ...' (whole text when no 'Rationale:' is present)."""
    m = re.search(r"rationale:\s*", text_target, flags=re.I)
    return text_target[m.end() :].strip() if m else text_target.strip()


def content_check(sft_by_version: Mapping[str, Sequence[dict]], rewrites: Iterable[dict], tokenizer=None, versions: Sequence[str] = VERSIONS) -> pd.DataFrame:
    """Stage-2 content check of docs/03 §5 on the ACTUAL training files of one teacher.

    Per version: n_items, n_families, same_prompt_set_as_O, letter_identity_with_O (share of prompts whose target letter
    equals O's; must be 1.0), letter_matches_rewrite (F / C: the SFT letter equals the kept rewrite text's letter),
    kept_attempt_found (share of F / C items with a kept attempt in the rewrite log), check_{choice,...,format} (share
    of items whose kept attempt passed each judge check), mean_attempts, n_attempted / n_kept / kept_share from the
    rewrite log, and lengths: mean_words / mean_chars of the rationale, mean_target_tokens (with a tokenizer; the
    whole text_target), n_target_tokens (sum). O rows have NaN for the rewrite-only columns.
    """
    rewrites = list(rewrites)
    yld = rewrite_yield(rewrites).set_index("version") if rewrites else pd.DataFrame()
    cols = ["version", "n_items", "n_families", "same_prompt_set_as_O", "letter_identity_with_O", "letter_matches_rewrite", "kept_attempt_found", *[f"check_{c}" for c in CHECKS], "mean_attempts", "n_attempted", "n_kept", "kept_share",
            "mean_words", "mean_chars", "mean_target_tokens", "n_target_tokens"]
    o_rows = {r["prompt_id"]: r for r in sft_by_version.get("O", [])}
    out = []
    for v in versions:
        rows = list(sft_by_version.get(v, []))
        if not rows:
            continue
        pids = [r["prompt_id"] for r in rows]
        rat = [rationale_of(r["text_target"]) for r in rows]
        row: dict = dict(version=v, n_items=len(rows), n_families=len({r["family_id"] for r in rows}), same_prompt_set_as_O=bool(set(pids) == set(o_rows)) if o_rows else None,
                         letter_identity_with_O=float(np.mean([o_rows[p]["letter"] == r["letter"] for p, r in zip(pids, rows) if p in o_rows])) if o_rows else np.nan,
                         letter_matches_rewrite=np.nan, kept_attempt_found=np.nan, mean_attempts=np.nan, n_attempted=np.nan, n_kept=np.nan, kept_share=np.nan,
                         mean_words=float(np.mean([len(t.split()) for t in rat])), mean_chars=float(np.mean([len(t) for t in rat])), mean_target_tokens=np.nan, n_target_tokens=np.nan)
        for c in CHECKS:
            row[f"check_{c}"] = np.nan
        if v != "O":
            kept = kept_attempts(rewrites, v)
            found = [kept.get(p) for p in pids]
            have = [k for k in found if k is not None]
            row["kept_attempt_found"] = len(have) / len(pids)
            if have:
                for c in CHECKS:
                    row[f"check_{c}"] = float(np.mean([bool((k.get("checks") or {}).get(c, False)) for k in have]))
                letters = [(r["letter"], _LETTER_RE.match(k["text"])) for r, k in zip(rows, found) if k is not None]
                row["letter_matches_rewrite"] = float(np.mean([m is not None and m.group(1).upper() == l for l, m in letters]))
                attempts = {}
                for r in rewrites:
                    if r.get("version") == v and r["prompt_id"] in set(pids):
                        attempts[r["prompt_id"]] = attempts.get(r["prompt_id"], 0) + 1
                row["mean_attempts"] = float(np.mean(list(attempts.values()))) if attempts else np.nan
            if len(yld) and v in yld.index:
                row.update(n_attempted=int(yld.loc[v, "n_attempted"]), n_kept=int(yld.loc[v, "n_kept"]), kept_share=float(yld.loc[v, "kept_share"]))
        if tokenizer is not None:
            n_tok = [len(tokenizer(r["text_target"], add_special_tokens=False)["input_ids"]) for r in rows]
            row.update(mean_target_tokens=float(np.mean(n_tok)), n_target_tokens=int(np.sum(n_tok)))
        out.append(row)
    return pd.DataFrame(out, columns=cols)


# --------------------------------------------------------------------------- (6) lexical register separation


_WORD_RE = re.compile(r"[A-Za-z]+(?:'[A-Za-z]+)?")
_SENT_RE = re.compile(r"[.!?]+(?:\s+|$)")
_CONTRACTION_RE = re.compile(r"\b(?:[a-z]+n't|[a-z]+'(?:re|ve|ll|d|m)|(?:it|that|there|here|he|she|what|who|let|where|how|one|everyone|someone)'s)\b", re.I)
FORMAL_CONNECTIVES: tuple[str, ...] = ("however", "therefore", "moreover", "furthermore", "thus", "hence", "consequently", "nevertheless", "nonetheless", "whereas", "additionally", "accordingly", "subsequently",
                                       "notwithstanding", "albeit", "in addition", "as a result", "in contrast", "for instance", "in order to", "with regard to", "regarding", "ultimately", "particularly")
FORMAL_WORDS: tuple[str, ...] = ("ensure", "ensures", "ensuring", "maintain", "maintains", "maintaining", "obtain", "assist", "individual", "individuals", "significant", "appropriate", "demonstrate", "demonstrates", "facilitate",
                                 "prioritize", "prioritizes", "prioritizing", "utilize", "essential", "potential", "potentially", "necessary", "uphold", "upholds", "adhere", "integrity", "responsibility", "consequences", "circumstances",
                                 "perspective", "fundamental", "crucial", "beneficial", "detrimental", "sufficient", "require", "requires", "approach", "foster", "fosters", "promote", "promotes", "preserve", "preserves", "undermine",
                                 "undermines", "address", "addresses", "commitment", "well-being", "wellbeing", "autonomy", "dignity", "compromise", "compromises", "prevent", "prevents", "constitutes", "regarding", "furthermore")
REGISTER_FEATURES: tuple[str, ...] = ("contraction_rate", "formal_connective_rate", "formal_word_rate", "mean_word_len", "words_per_sentence", "fk_grade")
_CONNECTIVE_RE = re.compile(r"\b(?:" + "|".join(re.escape(c) for c in sorted(FORMAL_CONNECTIVES, key=len, reverse=True)) + r")\b", re.I)
_FORMAL_WORDS = set(FORMAL_WORDS)
_VOWEL_GROUP_RE = re.compile(r"[aeiouy]+")


def _syllables(word: str) -> int:
    w = word.lower()
    n = len(_VOWEL_GROUP_RE.findall(w))
    if w.endswith("e") and not w.endswith(("le", "ee", "ye")) and n > 1:
        n -= 1
    return max(1, n)


def register_features(text: str) -> dict[str, float]:
    """Lexical register features of one rationale: contraction rate (contractions / word), formal-connective rate,
    formal-word rate (closed list), mean word length, words per sentence and a Flesch-Kincaid grade proxy
    0.39 * words/sentence + 11.8 * syllables/word - 15.59 (vowel-group syllable heuristic). No LLM, no model."""
    words = _WORD_RE.findall(text)
    n_w = max(1, len(words))
    n_s = max(1, len(_SENT_RE.findall(text)) or 1)
    syl = sum(_syllables(w) for w in words) / n_w
    return dict(n_words=len(words), n_sentences=n_s, contraction_rate=len(_CONTRACTION_RE.findall(text)) / n_w, formal_connective_rate=len(_CONNECTIVE_RE.findall(text)) / n_w,
                formal_word_rate=sum(w.lower() in _FORMAL_WORDS for w in words) / n_w, mean_word_len=float(np.mean([len(w) for w in words])) if words else 0.0,
                words_per_sentence=len(words) / n_s, fk_grade=0.39 * len(words) / n_s + 11.8 * syl - 15.59)


def register_table(sft_by_version: Mapping[str, Sequence[dict]], versions: Sequence[str] = VERSIONS) -> tuple[pd.DataFrame, pd.DataFrame]:
    """(per_item, per_version): register features of every rationale and their per-version means (+ n)."""
    rows = []
    for v in versions:
        for r in sft_by_version.get(v, []):
            rows.append(dict(version=v, prompt_id=r["prompt_id"], **register_features(rationale_of(r["text_target"]))))
    feats = ["n_words", "n_sentences", *REGISTER_FEATURES]
    per_item = pd.DataFrame(rows, columns=["version", "prompt_id", *feats])
    if per_item.empty:
        return per_item, pd.DataFrame(columns=["version", "n", *feats])
    per_version = per_item.groupby("version", sort=False)[feats].mean().reset_index()
    per_version.insert(1, "n", per_item.groupby("version", sort=False).size().to_numpy())
    return per_item, per_version


def _logistic_fit(X: np.ndarray, y: np.ndarray, l2: float = 1e-2, n_iter: int = 30) -> np.ndarray:
    """Ridge-regularised logistic regression by Newton / IRLS; returns [intercept, weights]."""
    n, d = X.shape
    Xb = np.column_stack([np.ones(n), X])
    w = np.zeros(d + 1)
    pen = np.full(d + 1, l2)
    pen[0] = 0.0
    for _ in range(n_iter):
        z = np.clip(Xb @ w, -30, 30)
        p = 1.0 / (1.0 + np.exp(-z))
        W = p * (1 - p)
        H = Xb.T @ (Xb * W[:, None]) + np.diag(pen)
        g = Xb.T @ (y - p) - pen * w
        step = np.linalg.solve(H, g)
        w = w + step
        if np.max(np.abs(step)) < 1e-8:
            break
    return w


def register_separation(per_item: pd.DataFrame, a: str = "F", b: str = "C", features: Sequence[str] = REGISTER_FEATURES, n_folds: int = 10, seed: int = 0) -> dict:
    """How separable are the rationales of versions a and b on the lexical features?

    Leave-one-out nearest-centroid accuracy (features standardised with the mean / sd of the n - 1 training items of
    each fold, each item scored against the centroids computed without it; no leakage of the held-out item) and
    k-fold logistic-regression accuracy (ridge IRLS, standardisation fitted on the training fold), Wilson 95% CIs of
    both accuracies (`*_ci_lo` / `*_ci_hi`), the per-feature standardised mean difference d = (mean_a - mean_b) /
    pooled sd, and `passes` = both accuracies >= REGISTER_MIN_ACC (frozen E3 choice, tasks/e3_plan.md §2: F vs C
    distinguishable). `pending (...)` when a version has < 2 items.
    """
    out: dict = {"a": a, "b": b, "n_a": 0, "n_b": 0, "nearest_centroid_loo_acc": np.nan, "nc_ci_lo": np.nan, "nc_ci_hi": np.nan, "logistic_cv_acc": np.nan, "lr_ci_lo": np.nan, "lr_ci_hi": np.nan,
                 "n_folds": n_folds, "passes": None, "min_acc": REGISTER_MIN_ACC, "feature_d": {}, "status": "pending (missing version)"}
    A = per_item[per_item["version"] == a][list(features)].to_numpy(dtype=float)
    B = per_item[per_item["version"] == b][list(features)].to_numpy(dtype=float)
    out["n_a"], out["n_b"] = int(len(A)), int(len(B))
    if len(A) < 2 or len(B) < 2:
        return out
    X = np.vstack([A, B])
    y = np.r_[np.ones(len(A)), np.zeros(len(B))]
    n = len(X)
    sd_pool = np.sqrt((A.var(axis=0, ddof=1) * (len(A) - 1) + B.var(axis=0, ddof=1) * (len(B) - 1)) / (len(A) + len(B) - 2))
    with np.errstate(invalid="ignore", divide="ignore"):
        out["feature_d"] = {f: float(v) for f, v in zip(features, (A.mean(axis=0) - B.mean(axis=0)) / sd_pool)}
    # LOO nearest centroid: standardisation and centroids both from the n - 1 training items (vectorised)
    S, SS = X.sum(axis=0), (X**2).sum(axis=0)
    mu_i = (S - X) / (n - 1)  # training mean without item i
    var_i = np.maximum((SS - X**2 - (n - 1) * mu_i**2) / max(1, n - 2), 0.0)  # training variance (ddof=1) without item i
    sd_i = np.sqrt(var_i)
    sd_i[sd_i == 0] = 1.0
    sums = {1.0: X[y == 1].sum(axis=0), 0.0: X[y == 0].sum(axis=0)}
    counts = {1.0: float(len(A)), 0.0: float(len(B))}
    own = y[:, None]
    c_own = (own * sums[1.0] + (1 - own) * sums[0.0] - X) / (own * counts[1.0] + (1 - own) * counts[0.0] - 1)
    c_other = (own * sums[0.0] + (1 - own) * sums[1.0]) / (own * counts[0.0] + (1 - own) * counts[1.0])
    d_own = np.sum(((X - c_own) / sd_i) ** 2, axis=1)
    d_other = np.sum(((X - c_other) / sd_i) ** 2, axis=1)
    correct = int(np.sum(d_own < d_other))
    out["nearest_centroid_loo_acc"] = correct / n
    out["nc_ci_lo"], out["nc_ci_hi"] = wilson_ci(correct, n)
    # k-fold logistic regression
    rng = np.random.default_rng([seed, zlib.crc32(b"register_separation")])
    idx = rng.permutation(len(X))
    k = min(n_folds, len(X))
    folds = np.array_split(idx, k)
    hits = 0
    for f in folds:
        tr = np.setdiff1d(idx, f)
        mu_t, sd_t = X[tr].mean(axis=0), X[tr].std(axis=0, ddof=1)
        sd_t[sd_t == 0] = 1.0
        w = _logistic_fit((X[tr] - mu_t) / sd_t, y[tr])
        z = np.column_stack([np.ones(len(f)), (X[f] - mu_t) / sd_t]) @ w
        hits += int(np.sum((z > 0) == (y[f] == 1)))
    out["logistic_cv_acc"] = hits / n
    out["lr_ci_lo"], out["lr_ci_hi"] = wilson_ci(hits, n)
    out["passes"] = bool(out["nearest_centroid_loo_acc"] >= REGISTER_MIN_ACC and out["logistic_cv_acc"] >= REGISTER_MIN_ACC)
    out["status"] = "pass" if out["passes"] else "fail"
    return out


def wilson_ci(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    """Wilson score interval for a binomial proportion k / n."""
    if n <= 0:
        return np.nan, np.nan
    p = k / n
    den = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / den
    half = z * np.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / den
    return (0.0 if k == 0 else float(max(0.0, centre - half))), (1.0 if k == n else float(min(1.0, centre + half)))
