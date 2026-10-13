"""Dose-response supplement (docs/supplemental_experiments.md §3 row 1): does the teacher-specific inheritance gap of
tasks/e2c_plan.md §6 grow with the share p of CONTESTED demonstrations in the training set?

Conditions are the shares p in {0, 0.25, 0.5, 1}: p = 0 is K_n (size-matched consensus control, scripts/10b), p = 0.25 /
0.5 the C + K mixtures of scripts/10c (size- and variant-matched to C), p = 1 is E2c-C. Every per-condition quantity
comes from `vcd.analysis.e2c_metrics.analyze_condition`, unchanged -- gap_T, seed-pair null, family bootstrap with ONE
weight matrix shared by every condition -- so the p = 0 and p = 1 rows reproduce scripts/19 exactly. This module adds
only the trend statistic across conditions (pre-registered before any mixture student was trained):

  * slope(T): least-squares slope of the per-run gap (agree_own - max_other agree_other) on the run's share p over all
    O runs of teacher T (planned 4 shares x 5 seeds = 20 runs). With balanced seeds it equals the slope through the
    seed-mean gaps; with the two shares 0 and 1 only it equals gap_T(C) - gap_T(K_n), the e2c attribution difference.
  * family-bootstrap 95% CI of slope(T): for every resample of the split's families (`e2c_metrics.bootstrap_weights`)
    every run's gap is recomputed from its per-family cell counts (`e2c_metrics.gap_replicates`, the same replicates
    behind the per-condition CIs) and the slope refitted; 2.5 / 97.5 percentiles. A run whose gap is undefined in a
    replicate is dropped from that replicate's fit.
  * Spearman rho between share and seed-mean gap over the shares (4 points; descriptive, no p-value reported).
  * verdict: per teacher pass iff ci_lo(slope) > 0 (strict); >= 2/3 of the configured teachers -> "dose-response
    supported", 1/3 -> "partial", 0/3 -> "not supported". Issued only when every configured teacher has O runs at every
    planned share; otherwise "pending (curve incomplete ...)" and the slopes over the present shares are descriptive.
  * the same slope (point estimate and Spearman only; no CI, no verdict) for the cost quantities flip_rate and
    suggestibility s = delta(T5) - delta(T6) of `e2c_metrics.run_descriptives`.
Every function is pure; scripts/24_dose_response.py runs the chain and writes the tables.
"""

from __future__ import annotations

import warnings
from pathlib import Path
from typing import Mapping, Optional, Sequence

import numpy as np
import pandas as pd

from vcd.analysis import e2c_metrics as E
from vcd.analysis.e1_metrics import parse_run_id
from vcd.stats import spearman

SHARES_PLANNED: tuple[float, ...] = (0.0, 0.25, 0.5, 1.0)
DEFAULT_CONDITIONS = ("0=runs/qwen3-4b-e2ckn/*_O_s*/eval/{split}_responses.jsonl,0.25=runs/qwen3-4b-e2cmix25/*_O_s*/eval/{split}_responses.jsonl,"
                      "0.5=runs/qwen3-4b-e2cmix50/*_O_s*/eval/{split}_responses.jsonl,1=runs/qwen3-4b-e2c/*_O_s*/eval/{split}_responses.jsonl")
COST_METRICS: tuple[str, ...] = ("flip_rate", "s")
METRICS: tuple[str, ...] = ("gap", *COST_METRICS)
N_SEEDS_PLANNED = E.N_SEEDS_PLANNED
MIN_TEACHER_FRAC = 2 / 3
RULE = ("slope(T) = least-squares slope of the per-run gap (agree_own - max_other agree_other, e2c_metrics) on the contested share p over the O runs of T "
        "(4 shares x 5 seeds); family-bootstrap 95% CI: resample the split's families (the e2c weight matrix, shared by every condition), recompute every "
        "run's gap, refit the slope, 2.5 / 97.5 percentiles. Per teacher pass iff ci_lo(slope) > 0; >= 2/3 teachers 'dose-response supported', 1/3 'partial', "
        "0/3 'not supported'; pending while any configured teacher lacks runs at a planned share. Spearman(share, seed-mean gap) over the 4 points is descriptive; "
        "the slopes of flip_rate and suggestibility s are descriptive (no CI, no verdict).")


def share_key(share: float) -> str:
    """'0', '0.25', '0.5', '1': the condition name used in every table."""
    return f"{float(share):g}"


def condition_label(share: float) -> str:
    p = float(share)
    if p == 0.0:
        return "K_n (p = 0, size-matched consensus control)"
    if p == 1.0:
        return "C (p = 1, contested)"
    return f"mix (p = {p:g}, C + K size-matched to C)"


def parse_conditions(text: str, split: str) -> dict[float, str]:
    """'0=glob,0.25=glob,...' -> {share: glob with {split} substituted}, sorted by share; duplicate shares are an error."""
    out: dict[float, str] = {}
    for item in text.split(","):
        item = item.strip()
        if not item:
            continue
        if "=" not in item:
            raise ValueError(f"condition {item!r} is not share=glob")
        key, pattern = item.split("=", 1)
        share = float(key)
        if not 0.0 <= share <= 1.0:
            raise ValueError(f"share {key!r} must be in [0, 1]")
        if share in out:
            raise ValueError(f"share {key!r} given twice")
        out[share] = pattern.format(split=split)
    return dict(sorted(out.items()))


def glob_files(pattern: str) -> list[Path]:
    """Files matching a glob relative to the working directory (absolute patterns are honoured)."""
    if Path(pattern).is_absolute():
        return sorted(Path("/").glob(pattern.lstrip("/")))
    return sorted(Path(".").glob(pattern))


# --------------------------------------------------------------------------- slope


def ols_slope(x: Sequence[float], Y: np.ndarray) -> np.ndarray:
    """Least-squares slope of every column of Y (n, B) on x (n,), NaN-aware per column.

    Rows whose y is NaN are dropped from that column's fit; a column with fewer than two distinct x values left is NaN.
    """
    x = np.asarray(x, dtype=float)
    Y = np.asarray(Y, dtype=float)
    Y = Y[:, None] if Y.ndim == 1 else Y
    if Y.shape[0] != x.shape[0]:
        raise ValueError(f"x has {x.shape[0]} rows, Y {Y.shape[0]}")
    M = np.isfinite(Y).astype(float)
    Yz = np.where(M > 0, Y, 0.0)
    n = M.sum(axis=0)
    with np.errstate(invalid="ignore", divide="ignore"):
        xbar = (M * x[:, None]).sum(axis=0) / n
        ybar = Yz.sum(axis=0) / n
        xc = M * (x[:, None] - xbar)
        sxx = (xc**2).sum(axis=0)
        sxy = (xc * (Yz - ybar)).sum(axis=0)
        return np.where(sxx > 0, sxy / sxx, np.nan)


def run_gap_replicates(res: E.ConditionResult, W: np.ndarray, teachers: Sequence[str]) -> tuple[list[str], np.ndarray]:
    """Per O run of one condition: the (B,) family-bootstrap replicates of its gap -- the same replicates behind `res.boot`.

    Recomputed from `res.counts` with `e2c_metrics.gap_replicates`; their seed means must reproduce `res.boot` (raises
    otherwise). Conditions without counts give no runs.
    """
    B = int(np.asarray(W).shape[0])
    if res.counts is None or not res.counts.pairs:
        return [], np.zeros((0, B))
    present = [t for t in teachers if t in {t for _, t in res.counts.pairs}]
    own = {r: parse_run_id(r).teacher for r in res.run_tab["run_id"] if parse_run_id(r).version == E.GAP_VERSION and parse_run_id(r).teacher in present}
    runs, G = E.gap_replicates(res.counts, E.agreement_from_counts(res.counts, W), own, present)
    for t, b in E.seed_mean_gaps(runs, G, own).items():
        if t in res.boot and not np.allclose(b, res.boot[t], equal_nan=True, atol=1e-12, rtol=0):
            raise ValueError(f"per-run gap replicates do not reproduce the condition bootstrap for {t}")
    return runs, G


SLOPE_COLS = ["teacher", "metric", "n_runs", "n_shares", "shares", "complete", "slope", "intercept", "ci_lo", "ci_hi", "n_boot", "n_boot_nan", "ci_above_zero", "spearman_rho", "seed_means"]


def slope_table(runs: pd.DataFrame, reps: Mapping[float, tuple[Sequence[str], np.ndarray]], teachers: Sequence[str], shares_planned: Sequence[float] = SHARES_PLANNED,
                metrics: Sequence[str] = METRICS) -> pd.DataFrame:
    """Per configured teacher and metric: the slope on the share, its family-bootstrap CI (gap only) and Spearman(share, seed mean).

    `runs` is the per-run table with columns share, run_id, teacher, version, seed and the metrics (e2c_metrics.run_descriptives
    plus a `share` column); `reps` maps share -> (run ids, (n_runs, B) gap replicates) from `run_gap_replicates`. Only O
    runs enter. `complete` = the teacher has runs at every planned share; `seed_means` lists 'share:mean' per share.
    """
    t = runs[runs["version"] == E.GAP_VERSION] if len(runs) else runs
    rows = []
    for teacher in teachers:
        g_all = t[t["teacher"] == teacher] if len(t) else t
        for metric in metrics:
            g = g_all.dropna(subset=[metric]) if len(g_all) and metric in g_all else g_all.iloc[0:0]
            shares = sorted(set(float(s) for s in g["share"])) if len(g) else []
            row = dict(teacher=teacher, metric=metric, n_runs=int(len(g)), n_shares=len(shares), shares=",".join(share_key(s) for s in shares),
                       complete=bool(len(g)) and all(any(np.isclose(p, s) for s in shares) for p in shares_planned),
                       slope=np.nan, intercept=np.nan, ci_lo=np.nan, ci_hi=np.nan, n_boot=0, n_boot_nan=0, ci_above_zero=False, spearman_rho=np.nan, seed_means="")
            if len(g):
                x = g["share"].to_numpy(dtype=float)
                y = g[metric].to_numpy(dtype=float)
                means = g.groupby("share")[metric].mean().sort_index()
                row["seed_means"] = "; ".join(f"{share_key(s)}:{m:.4f}" for s, m in means.items())
                if len(shares) >= 2:
                    slope = float(ols_slope(x, y)[0])
                    row.update(slope=slope, intercept=float(y.mean() - slope * x.mean()))
                if len(shares) >= 3:
                    row["spearman_rho"] = spearman(list(means.index.astype(float)), list(means.to_numpy(dtype=float)))[0]
                if metric == "gap" and len(shares) >= 2:
                    blocks = []
                    for rid, s in zip(g["run_id"], g["share"]):
                        ids, G = reps.get(float(s), ([], np.zeros((0, 0))))
                        ids = list(ids)
                        blocks.append(np.asarray(G, dtype=float)[ids.index(rid)] if rid in ids else None)
                    if blocks and all(b is not None for b in blocks) and len({b.shape[0] for b in blocks}) == 1 and blocks[0].shape[0] > 0:
                        sb = ols_slope(x, np.vstack(blocks))
                        row.update(n_boot=int(sb.size), n_boot_nan=int(np.isnan(sb).sum()))
                        if np.isfinite(sb).any():
                            lo, hi = np.nanquantile(sb, [0.025, 0.975])
                            row.update(ci_lo=float(lo), ci_hi=float(hi), ci_above_zero=bool(lo > 0))
            rows.append(row)
    return pd.DataFrame(rows, columns=SLOPE_COLS)


# --------------------------------------------------------------------------- curve table and verdict


CURVE_COLS = ["share", "condition", "label", *E.GAP_COLS, *COST_METRICS]


def curve_table(gaps_by_share: Mapping[float, pd.DataFrame], runs: pd.DataFrame) -> pd.DataFrame:
    """dose_gaps: per share x configured teacher the e2c gap row (gap_table columns, unchanged) plus the seed-mean flip_rate and s."""
    parts = []
    for share, gaps in sorted(gaps_by_share.items()):
        g = gaps.copy()
        g.insert(0, "label", condition_label(share))
        g.insert(0, "condition", share_key(share))
        g.insert(0, "share", float(share))
        r = runs[(runs["share"] == float(share)) & (runs["version"] == E.GAP_VERSION)] if len(runs) else runs
        for m in COST_METRICS:
            means = r.groupby("teacher")[m].mean() if len(r) and m in r else pd.Series(dtype=float)
            g[m] = g["teacher"].map(means).astype(float)
        parts.append(g)
    out = pd.concat(parts, ignore_index=True) if parts else pd.DataFrame(columns=CURVE_COLS)
    return out[CURVE_COLS]


def dose_verdict(slopes: pd.DataFrame, teachers: Sequence[str], shares_present: Sequence[float], shares_planned: Sequence[float] = SHARES_PLANNED,
                 runs: Optional[pd.DataFrame] = None) -> dict:
    """'dose-response supported' / 'partial' / 'not supported' over the configured teachers, or pending while the curve is incomplete.

    Pending when a planned share has no runs at all or any configured teacher lacks O runs at a planned share (its `complete`
    flag). Teachers with a seed count other than the planned 5 at some share are listed under `deviations` (verdict still issued).
    """
    present = sorted(float(s) for s in shares_present)
    missing = [p for p in shares_planned if not any(np.isclose(p, s) for s in present)]
    out = {"verdict": "pending", "n_pass": 0, "n_teachers": len(teachers), "passing": [], "shares_planned": [share_key(p) for p in shares_planned],
           "shares_present": [share_key(p) for p in present], "shares_missing": [share_key(p) for p in missing], "incomplete_teachers": [], "deviations": [], "rule": RULE}
    g = slopes[slopes["metric"] == "gap"].set_index("teacher") if len(slopes) else pd.DataFrame(columns=SLOPE_COLS).set_index("teacher")
    out["incomplete_teachers"] = [t for t in teachers if t not in g.index or not bool(g.at[t, "complete"])]
    if runs is not None and len(runs):
        o = runs[runs["version"] == E.GAP_VERSION]
        for t in teachers:
            for s, grp in o[o["teacher"] == t].groupby("share"):
                if len(grp) != N_SEEDS_PLANNED:
                    out["deviations"].append(f"{t} @ p={share_key(s)}: {len(grp)} seeds (planned {N_SEEDS_PLANNED})")
    if missing or out["incomplete_teachers"]:
        out["verdict"] = (f"pending (curve incomplete: shares present {', '.join(out['shares_present']) or 'none'}; missing {', '.join(out['shares_missing']) or 'none'}"
                          + (f"; teachers without a full curve: {', '.join(out['incomplete_teachers'])}" if out["incomplete_teachers"] else "") + ")")
        return out
    passing = [t for t in teachers if bool(g.at[t, "ci_above_zero"])]
    n = len(passing)
    out.update(n_pass=n, passing=passing, verdict="dose-response supported" if n * 3 >= 2 * len(teachers) else ("partial" if n >= 1 else "not supported"))
    return out
