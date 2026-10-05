"""E1 / E2 metrics from student and teacher TeacherResponse rows (docs/04 groups B, C, D; docs/05 §6).

Every function starts from the existing profile pipeline
    responses_to_frame -> align_to_focus -> cell_estimates -> symmetrize -> framing_shifts
so a `sym` table has columns (teacher, family_id, variant, p_o1, p_o2, p_sym, order_gap) and a `shifts`
table has (teacher, family_id, variant, p, r). The `teacher` column holds either a teacher name
(gpt4o, claude46, ...) or a student run id (qwen3-4b.gpt4o_O_s1); functions do not distinguish them,
so the same code gives teacher-teacher, student-teacher and student-student comparisons.

Notation (docs/04 §0): p(i,j) symmetrized P(positive act); r(i,j) = p(i,j) - mean_j p(i,j) framing shift
(family-demeaned, so a shared average judgment cannot masquerade as a shared profile).

Revision frozen on dev 2026-10-05 (tasks/e2_plan.md §1-2, docs/05 §6): the untrained base's prior profile r_0
(`base_prior_shifts`, no answer-mass gate) is a covariate; inheritance is measured with partial correlations
given r_0 (`inheritance_partial`, `pooled_inheritance_partial`, `grid_permutation_partial`), suggestibility
inheritance with a dose-response regression (`suggestibility_by_run`, `dose_response`), and E1 on the training
items (`train_reproduction`, `contested_alignment`).
"""

from __future__ import annotations

import itertools
import math
import warnings
import zlib
from pathlib import Path
from typing import Iterable, Mapping, NamedTuple, Optional, Sequence

import numpy as np
import pandas as pd

from vcd.io import load_models
from vcd.schemas import Prompt, TeacherResponse
from vcd.stats import pearson, spearman
from vcd.teacher import profile as P
from vcd.train.data import RUN_ID_RE  # one definition for trainer, eval and analysis (docs/05 §3.3)

SEEN_VARIANTS: tuple[str, ...] = ("T1", "T3", "T5", "T6")


class RunKey(NamedTuple):
    student: str
    teacher: str
    version: str
    seed: int


def parse_run_id(run_id: str) -> RunKey:
    """'qwen3-4b.gpt4o_O_s1' -> RunKey(student='qwen3-4b', teacher='gpt4o', version='O', seed=1)."""
    m = RUN_ID_RE.match(run_id)
    if not m:
        raise ValueError(f"not a run id: {run_id!r}")
    return RunKey(m["student"], m["teacher"], m["version"], int(m["seed"]))


def is_run_id(s: str) -> bool:
    return RUN_ID_RE.match(s) is not None


def binary_jsd(p: np.ndarray | float, q: np.ndarray | float) -> np.ndarray:
    """Base-2 Jensen-Shannon divergence between Bernoulli(p) and Bernoulli(q); same clipping as profile._jsd."""
    return P._jsd(np.asarray(p, dtype=float), np.asarray(q, dtype=float))


# --------------------------------------------------------------------------- loading


def load_prompts(path: str | Path) -> dict[str, Prompt]:
    return {p.prompt_id: p for p in load_models(path, Prompt)}


def focus_map(prompts: dict[str, Prompt]) -> dict[str, str]:
    """family_id -> focus_action ('x'|'y') from the prompt rows (v2 framings carry it on every row)."""
    return {p.family_id: p.focus_action for p in prompts.values() if p.focus_action}


def load_run_responses(runs_dir: str | Path, split: str, student_short: Optional[str] = None, glob: Optional[str] = None) -> list[TeacherResponse]:
    """All rows from runs/{student}/{run}/eval/{split}_responses.jsonl (or a custom glob relative to runs_dir)."""
    runs_dir = Path(runs_dir)
    pattern = glob or f"{student_short or '*'}/*/eval/{split}_responses.jsonl"
    rows: list[TeacherResponse] = []
    for path in sorted(runs_dir.glob(pattern)):
        rows += load_models(path, TeacherResponse)
    return rows


def load_responses(paths: Iterable[str | Path], prompt_ids: Optional[set[str]] = None) -> list[TeacherResponse]:
    rows: list[TeacherResponse] = []
    for path in paths:
        rows += [r for r in load_models(path, TeacherResponse) if prompt_ids is None or r.prompt_id in prompt_ids]
    return rows


# --------------------------------------------------------------------------- tables


def frame_table(responses: Iterable[TeacherResponse], prompts: dict[str, Prompt], focus_by_family: Optional[dict[str, str]] = None) -> pd.DataFrame:
    """responses_to_frame + align_to_focus (rows whose prompt is unknown are dropped)."""
    rows = [r for r in responses if r.prompt_id in prompts]
    if not rows:
        return pd.DataFrame(columns=["teacher", "mode", "pass_idx", "sample_idx", "prompt_id", "family_id", "variant", "order", "category", "choice_action", "p_x"])
    df = P.responses_to_frame(rows, prompts)
    focus = focus_map(prompts) if focus_by_family is None else focus_by_family
    return P.align_to_focus(df, focus) if focus else df


def sym_table(responses: Iterable[TeacherResponse] | pd.DataFrame, prompts: Optional[dict[str, Prompt]] = None, focus_by_family: Optional[dict[str, str]] = None, mass_gate: bool = True) -> pd.DataFrame:
    """responses_to_frame -> align_to_focus -> cell_estimates -> symmetrize. Accepts an already-built frame.

    `mass_gate=False` also uses rows the readout marked `malformed` (letter mass below answer_mass_min) as long
    as they carry a renormalized p_x. This is NOT a readout of answers; it is only for the untrained base's prior
    profile used as a covariate (`base_prior_shifts`). The 0.9 rule itself is untouched.
    """
    df = responses if isinstance(responses, pd.DataFrame) else frame_table(responses, prompts or {}, focus_by_family)
    if df.empty:
        return pd.DataFrame(columns=["teacher", "family_id", "variant", "p_o1", "p_o2", "p_sym", "order_gap"])
    prof = df[df["mode"] == "profile"]
    if not mass_gate:
        prof = prof.copy()
        prof.loc[(prof["category"] == "malformed") & prof["p_x"].notna(), "category"] = "answer"
    return P.symmetrize(P.cell_estimates(prof))


def base_prior_shifts(rows: Iterable[TeacherResponse], prompts: dict[str, Prompt], variants: Sequence[str] = SEEN_VARIANTS) -> pd.DataFrame:
    """Framing-shift profile r_0 of the untrained base from its renormalized two-letter probabilities on EVERY cell.

    The 0.9 answer-mass gate is bypassed (`sym_table(mass_gate=False)`), so the base contributes a complete
    profile even though it rarely answers with a letter. The result is the "base prior profile": a covariate for
    the partial correlations of the revised E2, never a readout of S_0's answers. `teacher` keeps the run id.
    """
    sym = sym_table(rows, prompts, mass_gate=False)
    return P.framing_shifts(sym, list(variants))


def category_rates(frame: pd.DataFrame, by: Sequence[str] = ("teacher", "variant")) -> pd.DataFrame:
    """Share of answer / malformed / refusal / insufficient rows per group (all modes; students only have profile rows)."""
    if frame.empty:
        return pd.DataFrame(columns=[*by, "answer", "malformed", "n"])
    tab = frame.groupby(list(by))["category"].value_counts(normalize=True).unstack(fill_value=0.0)
    for c in ("answer", "malformed", "refusal", "insufficient"):
        if c not in tab:
            tab[c] = 0.0
    tab["n"] = frame.groupby(list(by)).size()
    return tab.reset_index()


def order_gap(sym: pd.DataFrame) -> pd.DataFrame:
    """Per teacher: mean |p_o1 - p_o2| and the share of cells whose majority act agrees across orders (docs/04 group A)."""
    out = []
    for teacher, g in sym.groupby("teacher", sort=True):
        g = g.dropna(subset=["p_o1", "p_o2"])
        out.append(dict(teacher=teacher, n_cells=len(g), order_gap_mean=float(g["order_gap"].mean()) if len(g) else np.nan, order_majority_agree=float(((g["p_o1"] > 0.5) == (g["p_o2"] > 0.5)).mean()) if len(g) else np.nan))
    return pd.DataFrame(out, columns=["teacher", "n_cells", "order_gap_mean", "order_majority_agree"])


def _pairs(sym_s: pd.DataFrame, sym_t: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Long table of aligned (run_id, teacher, family_id, variant, p_s, p_t) over cells where both have p_sym."""
    s = sym_s[sym_s["variant"].isin(variants)].dropna(subset=["p_sym"])[["teacher", "family_id", "variant", "p_sym"]].rename(columns={"teacher": "run_id", "p_sym": "p_s"})
    t = sym_t[sym_t["variant"].isin(variants)].dropna(subset=["p_sym"])[["teacher", "family_id", "variant", "p_sym"]].rename(columns={"p_sym": "p_t"})
    return s.merge(t, on=["family_id", "variant"], how="inner")


def _compare(sym_s: pd.DataFrame, sym_t: pd.DataFrame, variants: Sequence[str], by_variant: bool, value: str, fn, extra: Sequence[str] = ()) -> pd.DataFrame:
    """Apply fn(p_s, p_t) -> float | dict per (run_id, teacher[, variant]); a dict must hold `value` and the `extra` keys."""
    m = _pairs(sym_s, sym_t, variants)
    keys = ["run_id", "teacher"] + (["variant"] if by_variant else [])
    if m.empty:
        return pd.DataFrame(columns=keys + [value, "n_cells", *extra])
    out = []
    for key, g in m.groupby(keys, sort=True):
        res = fn(g["p_s"].to_numpy(), g["p_t"].to_numpy())
        res = res if isinstance(res, dict) else {value: res}
        out.append(dict(zip(keys, key if isinstance(key, tuple) else (key,))) | res | {"n_cells": len(g)})
    return pd.DataFrame(out)


def _agreement(a: np.ndarray, b: np.ndarray) -> dict:
    """Majority-act agreement over cells where neither side is exactly 0.5 (the majority act is undefined there).

    Ties are rare with float logits but systematic for a flat random-label student, which would otherwise be
    scored as 'chooses the negative act' and agree with every teacher below 0.5. `n_ties` reports the share.
    """
    tie = (a == 0.5) | (b == 0.5)
    ok = ~tie
    return {"agreement": float(((a[ok] > 0.5) == (b[ok] > 0.5)).mean()) if ok.any() else np.nan, "n_ties": int(tie.sum())}


def teacher_agreement(sym_s: pd.DataFrame, sym_t: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS, by_variant: bool = False) -> pd.DataFrame:
    """Majority-act agreement mean_{(i,j)} [(p_s > .5) == (p_t > .5)] for every (run_id, teacher) pair (group C).

    Cells where either p_sym is exactly 0.5 are excluded from the mean and counted in `n_ties`.
    """
    return _compare(sym_s, sym_t, variants, by_variant, "agreement", _agreement, extra=("n_ties",))


def student_teacher_jsd(sym_s: pd.DataFrame, sym_t: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS, by_variant: bool = False) -> pd.DataFrame:
    """mean_{(i,j)} JSD(p_s, p_t) for every (run_id, teacher) pair (group C)."""
    return _compare(sym_s, sym_t, variants, by_variant, "jsd", lambda a, b: float(binary_jsd(a, b).mean()))


def flip_rate(sym: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS) -> pd.DataFrame:
    """Per teacher and framing pair: share of families whose majority act differs (wraps profile.pairwise_flip_rates)."""
    return P.pairwise_flip_rates(sym, list(variants))


def cross_framing_jsd(sym: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS) -> pd.DataFrame:
    """Per teacher and framing pair: mean over families of JSD(p(i,a), p(i,b))."""
    out = []
    for teacher in sorted(sym["teacher"].unique()):
        s = sym[(sym["teacher"] == teacher) & (sym["variant"].isin(variants))]
        piv = s.pivot_table(index="family_id", columns="variant", values="p_sym").dropna()
        if len(piv) == 0 or any(v not in piv.columns for v in variants):
            continue
        for i, a in enumerate(variants):
            for b in variants[i + 1 :]:
                out.append(dict(teacher=teacher, pair=f"{a}-{b}", jsd=float(binary_jsd(piv[a].to_numpy(), piv[b].to_numpy()).mean()), n_families=len(piv)))
    return pd.DataFrame(out, columns=["teacher", "pair", "jsd", "n_families"])


def consistency(sym: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS) -> pd.DataFrame:
    """Group-B table: profile.teacher_consistency plus one flip_{a}-{b} column per framing pair."""
    base = P.teacher_consistency(sym, list(variants))
    pf = flip_rate(sym, variants)
    if not pf.empty:
        wide = pf.pivot_table(index="teacher", columns="pair", values="flip_rate")
        wide.columns = [f"flip_{c}" for c in wide.columns]
        base = base.merge(wide.reset_index(), on="teacher", how="left")
    return base


def seen_vs_unseen(sym: pd.DataFrame, seen: Sequence[str] = SEEN_VARIANTS, unseen: str = "T0") -> pd.DataFrame:
    """Flip rate / JSD inside the seen framings vs between (unseen, seen[0]). Empty when `unseen` is absent."""
    cols = ["teacher", "n_families", "flip_seen", "jsd_seen", "flip_unseen", "jsd_unseen"]
    if unseen not in set(sym["variant"]):
        return pd.DataFrame(columns=cols)
    out = []
    for teacher in sorted(sym["teacher"].unique()):
        s = sym[(sym["teacher"] == teacher) & (sym["variant"].isin([*seen, unseen]))]
        piv = s.pivot_table(index="family_id", columns="variant", values="p_sym").dropna()
        if len(piv) == 0 or any(v not in piv.columns for v in [*seen, unseen]):
            continue
        maj = piv > 0.5
        pairs = [(a, b) for i, a in enumerate(seen) for b in seen[i + 1 :]]
        out.append(dict(
            teacher=teacher, n_families=len(piv),
            flip_seen=float(np.mean([(maj[a] != maj[b]).mean() for a, b in pairs])),
            jsd_seen=float(np.mean([binary_jsd(piv[a].to_numpy(), piv[b].to_numpy()).mean() for a, b in pairs])),
            flip_unseen=float((maj[unseen] != maj[seen[0]]).mean()),
            jsd_unseen=float(binary_jsd(piv[unseen].to_numpy(), piv[seen[0]].to_numpy()).mean()),
        ))
    return pd.DataFrame(out, columns=cols)


# --------------------------------------------------------------------------- inheritance (E2)


def _shift_matrix(shifts: pd.DataFrame, who: str, families: Sequence[str], variants: Sequence[str]) -> np.ndarray:
    """(n_families x n_variants) matrix of r for one teacher / run, in the given family and variant order."""
    piv = shifts[shifts["teacher"] == who].pivot_table(index="family_id", columns="variant", values="r")
    return piv.reindex(index=list(families), columns=list(variants)).to_numpy(dtype=float)


def complete_families(shifts: pd.DataFrame, whos: Sequence[str], variants: Sequence[str]) -> list[str]:
    """Families for which every listed teacher / run in `shifts` has r on all `variants` (sorted).

    This is the cell set every E2 statistic is computed on: `inheritance` uses it per run (run, all teachers,
    r_0) and scripts/13 uses it once for P2 (all O runs, all teachers, r_0) so that s_run and s_T are measured on
    the same families (frozen on dev 2026-10-05).
    """
    sets = []
    for w in whos:
        g = shifts[(shifts["teacher"] == w) & (shifts["variant"].isin(variants))]
        sets.append(set(g.groupby("family_id")["variant"].nunique().pipe(lambda s: s[s == len(variants)]).index))
    return sorted(set.intersection(*sets)) if sets else []


_complete_families = complete_families


def _corr_with_fixed(x_rows: np.ndarray, t: np.ndarray) -> np.ndarray:
    """Pearson r between each row of x_rows (k x n) and the vector t (n,)."""
    xc = x_rows - x_rows.mean(axis=1, keepdims=True)
    tc = t - t.mean()
    denom = np.sqrt((xc**2).sum(axis=1)) * np.sqrt((tc**2).sum())
    with np.errstate(invalid="ignore", divide="ignore"):
        return (xc @ tc) / denom


def _rowwise_corr(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Pearson r between matching rows of a and b (both k x n)."""
    ac = a - a.mean(axis=1, keepdims=True)
    bc = b - b.mean(axis=1, keepdims=True)
    denom = np.sqrt((ac**2).sum(axis=1)) * np.sqrt((bc**2).sum(axis=1))
    with np.errstate(invalid="ignore", divide="ignore"):
        return (ac * bc).sum(axis=1) / denom


def _residualize_rows(x_rows: np.ndarray, z_rows: np.ndarray) -> np.ndarray:
    """Each row of x_rows (k x n) minus its mean and its OLS projection on the matching (or broadcast 1 x n) row of z_rows."""
    xc = x_rows - x_rows.mean(axis=1, keepdims=True)
    zc = z_rows - z_rows.mean(axis=1, keepdims=True)
    with np.errstate(invalid="ignore", divide="ignore"):
        beta = (xc * zc).sum(axis=1, keepdims=True) / (zc**2).sum(axis=1, keepdims=True)
    return xc - beta * zc


def _partial_corr_with_fixed(x_rows: np.ndarray, t: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Partial Pearson r(x, t | z) between each row of x_rows (k x n) and the vector t (n,), controlling for z (n,)."""
    xr = _residualize_rows(x_rows, z[None, :])
    tr = _residualize_rows(t[None, :], z[None, :])[0]
    return _corr_with_fixed(xr, tr)


def _rowwise_partial_corr(a: np.ndarray, b: np.ndarray, z: np.ndarray) -> np.ndarray:
    """Partial Pearson r between matching rows of a and b (k x n) given the matching rows of z (k x n)."""
    return _rowwise_corr(_residualize_rows(a, z), _residualize_rows(b, z))


def partial_corr(x: Sequence[float], y: Sequence[float], z: Sequence[float]) -> float:
    """Partial Pearson correlation r(x, y | z) = Pearson of the residuals of x and y after OLS on [1, z]. NaN below 4 points."""
    x, y, z = (np.asarray(v, dtype=float) for v in (x, y, z))
    ok = ~(np.isnan(x) | np.isnan(y) | np.isnan(z))
    if ok.sum() < 4:
        return float("nan")
    return float(_partial_corr_with_fixed(x[ok][None, :], y[ok], z[ok])[0])


def profile_rho_partial(shifts_s: pd.DataFrame, shifts_t: pd.DataFrame, control: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS, by_variant: bool = False) -> pd.DataFrame:
    """Partial rho(run, teacher | base): Pearson of r_s vs r_t after removing the base prior r_0 from both, on the common cells.

    `control` is a shifts table holding exactly one profile (the base prior, `base_prior_shifts`). `rho_base` is
    the raw Pearson of the run with the base on the same cells.
    """
    whos = control["teacher"].unique()
    if len(whos) != 1:
        raise ValueError(f"control must hold one profile, got {list(whos)}")
    z_all = control[control["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
    keys = ["run_id", "teacher"] + (["variant"] if by_variant else [])
    out = []
    for run in sorted(shifts_s["teacher"].unique()):
        s = shifts_s[(shifts_s["teacher"] == run) & shifts_s["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
        for teacher in sorted(shifts_t["teacher"].unique()):
            t = shifts_t[(shifts_t["teacher"] == teacher) & shifts_t["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
            idx = s.index.intersection(t.index).intersection(z_all.index)
            groups = {v: idx[idx.get_level_values("variant") == v] for v in variants} if by_variant else {None: idx}
            for v, ix in groups.items():
                row = dict(run_id=run, teacher=teacher)
                if by_variant:
                    row["variant"] = v
                pr, _ = pearson(s.loc[ix], t.loc[ix])
                rb, _ = pearson(s.loc[ix], z_all.loc[ix])
                out.append(row | dict(partial=partial_corr(s.loc[ix], t.loc[ix], z_all.loc[ix]), raw=pr, rho_base=rb, n_cells=len(ix)))
    return pd.DataFrame(out, columns=keys + ["partial", "raw", "rho_base", "n_cells"])


def profile_rho(shifts_s: pd.DataFrame, shifts_t: pd.DataFrame, variants: Sequence[str] = SEEN_VARIANTS, by_variant: bool = False) -> pd.DataFrame:
    """rho(run, teacher): Pearson and Spearman of r_s vs r_t on the (family, variant) cells both have."""
    keys = ["run_id", "teacher"] + (["variant"] if by_variant else [])
    out = []
    for run in sorted(shifts_s["teacher"].unique()):
        for teacher in sorted(shifts_t["teacher"].unique()):
            s = shifts_s[(shifts_s["teacher"] == run) & shifts_s["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
            t = shifts_t[(shifts_t["teacher"] == teacher) & shifts_t["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
            idx = s.index.intersection(t.index)
            groups = {v: idx[idx.get_level_values("variant") == v] for v in variants} if by_variant else {None: idx}
            for v, ix in groups.items():
                pr, _ = pearson(s.loc[ix], t.loc[ix])
                sr, _ = spearman(s.loc[ix], t.loc[ix])
                row = dict(run_id=run, teacher=teacher)
                if by_variant:
                    row["variant"] = v
                out.append(row | dict(pearson=pr, spearman=sr, n_cells=len(ix)))
    return pd.DataFrame(out, columns=keys + ["pearson", "spearman", "n_cells"])


def inheritance(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    own: dict[str, str],
    variants: Sequence[str] = SEEN_VARIANTS,
    n_perm: int = 10_000,
    n_boot: int = 10_000,
    seed: int = 0,
    by_variant: bool = False,
    control: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """Per run: rho_own, rho to each other teacher (rho__{teacher} columns), rho_other_max, delta_rho, family
    permutation p and family bootstrap CI (docs/03 §3, docs/04 group D).

    `own` maps run_id -> its teacher's name. All correlations for one run are computed on the same family
    set (families complete for the run and every teacher), so rho_own and rho_other are comparable.
    p_perm: the run's family labels are permuted as whole families (variant structure kept) n_perm times
    and delta_rho recomputed; p = share(perm >= observed). ci_lo / ci_hi: 2.5 / 97.5 % of delta_rho over
    n_boot family bootstraps. With by_variant, the same is done on each variant's cells (one row per variant).

    With `control` (a shifts table holding ONE profile, the base prior r_0 from `base_prior_shifts`), every rho
    is the partial correlation given r_0 on the same cells (`spearman_own` becomes the Spearman of the
    residuals), families must also be complete for the control, and the output gains `control` (its name) and
    `rho_base` (the run's raw Pearson with r_0). The permutation shuffles only the student's families; the
    control and the teachers stay aligned. This is the revised E2 statistic deltaRhoPartial (frozen on dev
    2026-10-05); `inheritance_partial` is the named entry point.
    """
    teachers = sorted(shifts_t["teacher"].unique())
    variant_groups = [(v, [v]) for v in variants] if by_variant else [("all", list(variants))]
    ctrl_name: Optional[str] = None
    if control is not None:
        names = control["teacher"].unique()
        if len(names) != 1:
            raise ValueError(f"control must hold exactly one profile, got {list(names)}")
        ctrl_name = str(names[0])
    out = []
    for run in sorted(shifts_s["teacher"].unique()):
        if run not in own or own[run] not in teachers:
            continue
        own_t = own[run]
        others = [t for t in teachers if t != own_t]
        tables = [shifts_s[shifts_s["teacher"] == run], shifts_t] + ([control] if control is not None else [])
        fams = _complete_families(pd.concat(tables), [run, *teachers] + ([ctrl_name] if ctrl_name else []), variants)
        if len(fams) < (4 if control is not None else 3):
            continue
        S_full = _shift_matrix(shifts_s[shifts_s["teacher"] == run], run, fams, variants)
        T_full = {t: _shift_matrix(shifts_t, t, fams, variants) for t in teachers}
        Z_full = _shift_matrix(control, ctrl_name, fams, variants) if control is not None else None
        rng = np.random.default_rng([seed, zlib.crc32(run.encode())])
        for vname, vcols in variant_groups:
            ci = [variants.index(v) for v in vcols]
            S = S_full[:, ci]
            T = {t: T_full[t][:, ci] for t in teachers}
            Z = Z_full[:, ci] if Z_full is not None else None
            n_f = len(fams)

            # observed
            x = S.ravel()
            if Z is None:
                rhos = {t: float(_corr_with_fixed(x[None, :], T[t].ravel())[0]) for t in teachers}
                sx, st = x, {t: T[t].ravel() for t in teachers}
                rho_base = np.nan
            else:
                z = Z.ravel()
                rhos = {t: float(_partial_corr_with_fixed(x[None, :], T[t].ravel(), z)[0]) for t in teachers}
                sx = _residualize_rows(x[None, :], z[None, :])[0]
                st = {t: _residualize_rows(T[t].ravel()[None, :], z[None, :])[0] for t in teachers}
                rho_base = float(_corr_with_fixed(x[None, :], z)[0])
            with warnings.catch_warnings():  # a constant r on one variant (e.g. an insensitive teacher) is legitimate
                warnings.simplefilter("ignore")
                spear = {t: spearman(sx, st[t])[0] for t in teachers}
            rho_own = rhos[own_t]
            other_vals = {t: rhos[t] for t in others}
            rho_other_max = max(other_vals.values()) if other_vals else np.nan
            other_argmax = max(other_vals, key=other_vals.get) if other_vals else None
            d_obs = rho_own - rho_other_max
            # permutation: shuffle family rows of the student matrix; teachers (and the control) fixed
            p_perm, null_sd = np.nan, np.nan
            if others and n_perm > 0:
                perms = np.stack([rng.permutation(n_f) for _ in range(n_perm)])  # (n_perm, n_f)
                Xp = S[perms].reshape(n_perm, -1)  # (n_perm, n_f * n_v)
                if Z is None:
                    r_by_t = {t: _corr_with_fixed(Xp, T[t].ravel()) for t in teachers}
                else:
                    r_by_t = {t: _partial_corr_with_fixed(Xp, T[t].ravel(), Z.ravel()) for t in teachers}
                d_null = r_by_t[own_t] - np.max(np.stack([r_by_t[t] for t in others]), axis=0)
                p_perm = float((np.sum(d_null >= d_obs) + 1) / (n_perm + 1))
                null_sd = float(np.nanstd(d_null))
            # family bootstrap
            ci_lo, ci_hi = np.nan, np.nan
            if others and n_boot > 0:
                d_boot = np.empty(n_boot)
                for start in range(0, n_boot, 1000):  # chunked family bootstrap: resample rows of S, every T (and Z) jointly
                    boots = rng.integers(0, n_f, size=(min(1000, n_boot - start), n_f))
                    Xb = S[boots].reshape(len(boots), -1)
                    if Z is None:
                        rb = {t: _rowwise_corr(Xb, T[t][boots].reshape(len(boots), -1)) for t in teachers}
                    else:
                        Zb = Z[boots].reshape(len(boots), -1)
                        rb = {t: _rowwise_partial_corr(Xb, T[t][boots].reshape(len(boots), -1), Zb) for t in teachers}
                    d_boot[start : start + len(boots)] = rb[own_t] - np.max(np.stack([rb[t] for t in others]), axis=0)
                ci_lo, ci_hi = (float(v) for v in np.nanquantile(d_boot, [0.025, 0.975]))
            row = dict(run_id=run, teacher=own_t, variant=vname, n_families=n_f, n_cells=n_f * len(vcols), rho_own=rho_own, spearman_own=spear[own_t], rho_other_max=rho_other_max, other_argmax=other_argmax, delta_rho=d_obs, p_perm=p_perm, perm_null_sd=null_sd, ci_lo=ci_lo, ci_hi=ci_hi)
            if control is not None:
                row["control"] = ctrl_name
                row["rho_base"] = rho_base
            for t in teachers:
                row[f"rho__{t}"] = rhos[t]
            out.append(row)
    cols = ["run_id", "teacher", "variant", "n_families", "n_cells", "rho_own", "spearman_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "perm_null_sd", "ci_lo", "ci_hi"]
    if control is not None:
        cols += ["control", "rho_base"]
    return pd.DataFrame(out, columns=cols + [f"rho__{t}" for t in teachers])


delta_rho = inheritance  # alias used in the task description


def inheritance_partial(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    control: pd.DataFrame,
    own: dict[str, str],
    variants: Sequence[str] = SEEN_VARIANTS,
    n_perm: int = 10_000,
    n_boot: int = 10_000,
    seed: int = 0,
    by_variant: bool = False,
) -> pd.DataFrame:
    """Per run deltaRhoPartial = partial rho(r_s, r_own | r_0) - max_other partial rho(r_s, r_other | r_0) (E2 revision, dev-frozen 2026-10-05).

    `control` is the base prior profile (`base_prior_shifts`). Columns are those of `inheritance` (every rho is
    partial given r_0) plus `control` and `rho_base`; family permutation p and family bootstrap CI as there.
    """
    return inheritance(shifts_s, shifts_t, own, variants, n_perm=n_perm, n_boot=n_boot, seed=seed, by_variant=by_variant, control=control)


def pooled_shifts(shifts_s: pd.DataFrame, runs: Sequence[str], name: str) -> pd.DataFrame:
    """One shifts table (teacher = `name`) whose r is the mean over `runs` on the (family, variant) cells all of them have.

    Averaging the seeds' framing-shift profiles before correlating is the pre-registered 'seed-mean' test of
    docs/03 §3: one Δρ and one family-permutation p per (teacher, version) instead of five per-seed verdicts.
    """
    piv = shifts_s[shifts_s["teacher"].isin(runs)].pivot_table(index=["family_id", "variant"], columns="teacher", values="r")
    piv = piv.reindex(columns=list(runs)).dropna()
    out = piv.mean(axis=1).rename("r").reset_index()
    out["teacher"] = name
    out["p"] = np.nan
    return out[["teacher", "family_id", "variant", "p", "r"]]


def pooled_inheritance(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    own: dict[str, str],
    variants: Sequence[str] = SEEN_VARIANTS,
    n_perm: int = 10_000,
    n_boot: int = 10_000,
    seed: int = 0,
    control: Optional[pd.DataFrame] = None,
) -> pd.DataFrame:
    """inheritance() on the seed-mean profile of every (student, teacher, version) group in `own`, plus Holm-adjusted p.

    Rows carry run_id = "{student}.{teacher}_{version}_pooled", `n_seeds`, `seeds`, `p_perm` and `p_holm`
    (Holm step-down over the groups of the same version, docs/04 §3). Groups whose run ids do not parse are skipped.
    With `control` every rho is partial given the base prior (see `inheritance`); `pooled_inheritance_partial`.
    """
    groups: dict[tuple[str, str, str], list[str]] = {}
    for run in sorted(own):
        try:
            k = parse_run_id(run)
        except ValueError:
            continue
        groups.setdefault((k.student, k.teacher, k.version), []).append(run)
    pooled, pooled_own, meta = [], {}, {}
    for (student, teacher, version), runs in groups.items():
        name = f"{student}.{teacher}_{version}_pooled"
        pooled.append(pooled_shifts(shifts_s, runs, name))
        pooled_own[name] = own[runs[0]]
        meta[name] = (version, len(runs), ",".join(str(parse_run_id(r).seed) for r in runs))
    cols = ["run_id", "teacher", "version", "n_seeds", "seeds", "variant", "n_families", "n_cells", "rho_own", "spearman_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "p_holm", "perm_null_sd", "ci_lo", "ci_hi"]
    if control is not None:
        cols += ["control", "rho_base"]
    if not pooled:
        return pd.DataFrame(columns=cols)
    inh = inheritance(pd.concat(pooled, ignore_index=True), shifts_t, pooled_own, variants, n_perm=n_perm, n_boot=n_boot, seed=seed, control=control)
    if inh.empty:
        return pd.DataFrame(columns=cols)
    inh["version"] = inh["run_id"].map(lambda r: meta[r][0])
    inh["n_seeds"] = inh["run_id"].map(lambda r: meta[r][1])
    inh["seeds"] = inh["run_id"].map(lambda r: meta[r][2])
    inh["p_holm"] = np.nan
    for _, idx in inh.groupby("version").groups.items():
        inh.loc[idx, "p_holm"] = holm(inh.loc[idx, "p_perm"].to_numpy(dtype=float))
    rho_cols = [c for c in inh.columns if c.startswith("rho__")]
    return inh[cols + rho_cols]


def pooled_inheritance_partial(
    shifts_s: pd.DataFrame,
    shifts_t: pd.DataFrame,
    control: pd.DataFrame,
    own: dict[str, str],
    variants: Sequence[str] = SEEN_VARIANTS,
    n_perm: int = 10_000,
    n_boot: int = 10_000,
    seed: int = 0,
) -> pd.DataFrame:
    """P3 of the revised E2: per (teacher, version) deltaRhoPartial of the seed-mean profile, family permutation p, Holm over teachers."""
    return pooled_inheritance(shifts_s, shifts_t, own, variants, n_perm=n_perm, n_boot=n_boot, seed=seed, control=control)


def holm(pvals: Sequence[float]) -> np.ndarray:
    """Holm step-down adjusted p-values (monotone, capped at 1); NaN inputs stay NaN and do not count."""
    p = np.asarray(pvals, dtype=float)
    out = np.full(p.shape, np.nan)
    ok = ~np.isnan(p)
    m = int(ok.sum())
    if m == 0:
        return out
    order = np.argsort(p[ok])
    adj = np.minimum(1.0, p[ok][order] * (m - np.arange(m)))
    out[np.flatnonzero(ok)[order]] = np.maximum.accumulate(adj)
    return out


def n_label_assignments(labels: Sequence[int]) -> int:
    """Number of distinct arrangements of the multiset `labels` (multinomial coefficient; 15 runs / 3 x 5 -> 756,756)."""
    counts = pd.Series(list(labels)).value_counts().to_numpy()
    out = math.factorial(int(counts.sum()))
    for c in counts:
        out //= math.factorial(int(c))
    return out


def label_assignments(labels: Sequence[int]) -> np.ndarray:
    """All distinct arrangements of the multiset `labels` as rows of an (n_assignments x n) int array.

    Built level by level with itertools.combinations and numpy indexing, so the 756,756 run -> teacher
    assignments of the 15-run grid take well under a second. The observed assignment is one of the rows.
    """
    labels = np.asarray(list(labels))
    uniq, counts = np.unique(labels, return_counts=True)
    n = len(labels)
    A = np.full((1, n), -1, dtype=np.int64)
    remaining = np.arange(n)[None, :]
    for lab_i, k in enumerate(counts[:-1]):
        r = remaining.shape[1]
        pats = np.array(list(itertools.combinations(range(r), int(k))), dtype=np.int64).reshape(-1, int(k))
        comp = np.array([sorted(set(range(r)) - set(p)) for p in pats], dtype=np.int64).reshape(len(pats), r - int(k))
        m, c = remaining.shape[0], len(pats)
        pos = remaining[:, pats]  # (m, c, k)
        A = np.repeat(A[:, None, :], c, axis=1)  # (m, c, n)
        np.put_along_axis(A, pos, lab_i, axis=2)
        A = A.reshape(m * c, n)
        remaining = remaining[:, comp].reshape(m * c, r - int(k))
    np.put_along_axis(A, remaining, len(counts) - 1, axis=1)
    return uniq[A]


def _assignment_null(own_idx: np.ndarray, stat, n_perm: int, seed: int, exact_max: int) -> tuple[np.ndarray, str]:
    """Null distribution of `stat(assignments)` over run -> teacher reassignments that keep the group sizes.

    Exact enumeration of every distinct assignment when their number is <= exact_max (0 disables it), else
    n_perm random label permutations. `stat` maps an (m x n_runs) int array of assignments to m floats.
    """
    if exact_max and n_label_assignments(own_idx) <= exact_max:
        A = label_assignments(own_idx)
        out = np.concatenate([stat(A[i : i + 50_000]) for i in range(0, len(A), 50_000)])
        return out, "exact"
    rng = np.random.default_rng(seed)
    A = np.stack([rng.permutation(own_idx) for _ in range(n_perm)]) if n_perm > 0 else own_idx[None, :]
    return np.concatenate([stat(A[i : i + 50_000]) for i in range(0, len(A), 50_000)]), "random"


def _p_from_null(null: np.ndarray, obs: float, method: str) -> float:
    """Exact: share of assignments (the observed one included) at or above obs; random: (count + 1) / (n + 1)."""
    if method == "exact":
        return float(np.mean(null >= obs - 1e-12))
    return float((np.sum(null >= obs) + 1) / (len(null) + 1))


def grid_permutation(table: pd.DataFrame, n_perm: int = 10_000, seed: int = 0, exact_max: int = 0) -> dict:
    """Shuffle the run -> teacher assignment across the grid and recompute mean delta_rho (docs/03 §3).

    `table` is an inheritance() output (variant == 'all' rows) with rho__{teacher} columns. Group sizes are kept
    (5 runs per teacher). exact_max > 0 enumerates every distinct assignment when there are at most that many
    (`grid_permutation_partial` does so by default); the pre-revision table keeps the random null.
    """
    t = table[table["variant"] == "all"] if "variant" in table else table
    rho_cols = [c for c in t.columns if c.startswith("rho__")]
    teachers = [c[len("rho__") :] for c in rho_cols]
    R = t[rho_cols].to_numpy(dtype=float)  # (n_runs, n_teachers)
    if len(t) == 0 or len(teachers) < 2:
        return {"observed": np.nan, "null_mean": np.nan, "null_sd": np.nan, "p": np.nan, "n_perm": 0, "n_runs": int(len(t)), "method": "none"}
    own_idx = np.array([teachers.index(x) for x in t["teacher"]])
    n = len(R)

    def mean_delta(A: np.ndarray) -> np.ndarray:
        own = R[np.arange(n)[None, :], A]  # (m, n)
        masked = np.broadcast_to(R, (len(A), n, len(teachers))).copy()
        masked[A[:, :, None] == np.arange(len(teachers))[None, None, :]] = -np.inf
        return (own - masked.max(axis=2)).mean(axis=1)

    obs = float(mean_delta(own_idx[None, :])[0])
    null, method = _assignment_null(own_idx, mean_delta, n_perm, seed, exact_max)
    return {"observed": obs, "null_mean": float(null.mean()), "null_sd": float(null.std()), "p": _p_from_null(null, obs, method),
            "n_perm": int(len(null)), "n_runs": int(n), "method": method, "per_run": {r: float(d) for r, d in zip(t["run_id"], t["delta_rho"])}}


def grid_permutation_partial(table: pd.DataFrame, n_perm: int = 10_000, seed: int = 0, exact_max: int = 1_000_000) -> dict:
    """P1 of the revised E2: mean deltaRhoPartial over the O runs vs the teacher-assignment null (dev-frozen 2026-10-05).

    `table` is an `inheritance_partial` output. The null reassigns the runs to teachers keeping the group sizes;
    all distinct assignments are enumerated when there are at most `exact_max` (756,756 for 3 x 5), else n_perm
    random ones. Pass iff p < 0.05.
    """
    if "control" not in table.columns:
        raise ValueError("grid_permutation_partial expects an inheritance_partial table (column `control`)")
    out = grid_permutation(table, n_perm=n_perm, seed=seed, exact_max=exact_max)
    out["control"] = str(table["control"].iloc[0]) if len(table) else None
    out["n_assignments"] = int(n_label_assignments([*table.loc[table["variant"] == "all", "teacher"]])) if len(table) else 0
    return out


# --------------------------------------------------------------------------- suggestibility dose-response (E2 P2)


def suggestibility_by_run(shifts: pd.DataFrame, pos: str = "T5", neg: str = "T6", families: Optional[Sequence[str]] = None) -> pd.DataFrame:
    """s = delta(pos) - delta(neg) for every profile in a shifts table: how much the directional framings pull the answer.

    delta(j) = mean_i r(i, j) (profile.type_effects) in positive-act coordinates; `who` is the run id or teacher name.
    With `families`, only those families are used (P2 passes the families complete for every O run, every
    teacher and r_0, see `complete_families`); `n_families` is the count actually available per profile.
    """
    cols = ["who", f"delta_{pos}", f"delta_{neg}", "s", "n_families"]
    if families is not None:
        shifts = shifts[shifts["family_id"].isin(set(families))]
    if shifts.empty:
        return pd.DataFrame(columns=cols)
    d = shifts.groupby(["teacher", "variant"])["r"].mean().unstack()
    nf = shifts.groupby("teacher")["family_id"].nunique()
    out = pd.DataFrame({"who": d.index, f"delta_{pos}": d.get(pos, np.nan), f"delta_{neg}": d.get(neg, np.nan)}).reset_index(drop=True)
    out["s"] = out[f"delta_{pos}"] - out[f"delta_{neg}"]
    out["n_families"] = nf.reindex(d.index).to_numpy()
    return out[cols]


def dose_response(s_runs: Mapping[str, float], s_teachers: Mapping[str, float], own: Mapping[str, str], n_perm: int = 10_000, seed: int = 0, exact_max: int = 1_000_000) -> dict:
    """P2 of the revised E2: OLS slope of the students' s on their own teacher's s_T, p from reassigning runs to teachers.

    Runs whose teacher is missing from `s_teachers` are ignored. The null reassigns the runs to the teachers
    keeping the group sizes (exact enumeration when <= exact_max assignments, else n_perm random); p is
    one-sided for slope > 0. Also reports Pearson r, the per-teacher mean / sd of the students' s, the pooled
    within-teacher sd (seed noise), and whether the ranking of the student means equals the teachers' ranking.
    """
    runs = sorted(r for r in s_runs if own.get(r) in s_teachers and not np.isnan(s_runs[r]))
    teachers = sorted({own[r] for r in runs})
    empty = {"slope": np.nan, "intercept": np.nan, "pearson": np.nan, "p": np.nan, "n_runs": len(runs), "n_teachers": len(teachers), "method": "none", "n_perm": 0,
             "seed_noise_sd": np.nan, "ordering_preserved": None, "teachers": {}}
    if len(runs) < 3 or len(teachers) < 2:
        return empty
    y = np.array([s_runs[r] for r in runs], dtype=float)
    s_t = np.array([s_teachers[t] for t in teachers], dtype=float)
    own_idx = np.array([teachers.index(own[r]) for r in runs])
    yc = y - y.mean()

    def slope_of(A: np.ndarray) -> np.ndarray:
        x = s_t[A]  # (m, n)
        xc = x - x.mean(axis=1, keepdims=True)
        with np.errstate(invalid="ignore", divide="ignore"):
            return (xc * yc[None, :]).sum(axis=1) / (xc**2).sum(axis=1)

    x = s_t[own_idx]
    slope = float(slope_of(own_idx[None, :])[0])
    intercept = float(y.mean() - slope * x.mean())
    null, method = _assignment_null(own_idx, slope_of, n_perm, seed, exact_max)
    per_t = {}
    for i, t in enumerate(teachers):
        v = y[own_idx == i]
        per_t[t] = {"s_teacher": float(s_t[i]), "s_student_mean": float(v.mean()), "s_student_sd": float(v.std(ddof=1)) if len(v) > 1 else np.nan, "n_runs": int(len(v))}
    within_var = [float(v["s_student_sd"]) ** 2 for v in per_t.values() if not np.isnan(v["s_student_sd"])]
    means = np.array([per_t[t]["s_student_mean"] for t in teachers])
    return {"slope": slope, "intercept": intercept, "pearson": pearson(x, y)[0], "p": _p_from_null(null, slope, method), "n_runs": len(runs), "n_teachers": len(teachers),
            "method": method, "n_perm": int(len(null)), "null_mean": float(null.mean()), "null_sd": float(null.std()),
            "seed_noise_sd": float(np.sqrt(np.mean(within_var))) if within_var else np.nan,
            "ordering_preserved": bool(np.array_equal(np.argsort(-means, kind="stable"), np.argsort(-s_t, kind="stable"))), "teachers": per_t}


# --------------------------------------------------------------------------- training-item E1 (E1a / E1b)


def letters_of(rows: Iterable[TeacherResponse]) -> dict[str, Optional[str]]:
    """prompt_id -> argmax letter (None when the readout had no letter mass); the first row per prompt wins."""
    out: dict[str, Optional[str]] = {}
    for r in rows:
        out.setdefault(r.prompt_id, r.letter)
    return out


def train_reproduction(letters: Mapping[str, Optional[str]], targets: Mapping[str, str]) -> dict:
    """E1a: share of the SFT targets whose prompt the student answers with the target letter.

    `letters` is the student's prompt_id -> argmax letter on its training prompts (`letters_of`), `targets` the
    SFT file's prompt_id -> letter. Prompts without a readout row count as missing (not scored); rows without a
    letter count as mismatches. The argmax letter is scored whatever the readout category (a `malformed` row
    with letter mass below 0.9 still has an argmax); scripts/13 reports the run's answer rate next to it. Gate
    (frozen on dev 2026-10-05): accuracy >= 0.95 with n_missing == 0 for every O run.
    """
    pids = [p for p in targets if p in letters]
    n_match = sum(letters[p] == targets[p] for p in pids)
    return {"n_targets": len(targets), "n_scored": len(pids), "n_missing": len(targets) - len(pids), "n_no_letter": sum(letters[p] is None for p in pids),
            "n_match": int(n_match), "accuracy": (n_match / len(pids)) if pids else float("nan")}


def contested_items(own_targets: Mapping[str, str], other_targets: Mapping[str, str]) -> list[str]:
    """Training prompts both teachers labelled with different letters (same prompt_id, hence the same option order)."""
    return sorted(p for p, l in own_targets.items() if p in other_targets and other_targets[p] != l)


def contested_alignment(
    letters_by_run: Mapping[str, Mapping[str, Optional[str]]],
    own_targets: Mapping[str, str],
    other_targets: Mapping[str, str],
    n_boot: int = 10_000,
    seed: int = 0,
    family_of: Optional[Mapping[str, str]] = None,
) -> dict:
    """E1b: on contested training items (own and other teacher disagree), the share of (item, run) pairs where the
    student gives its own teacher's letter, pooled over the runs, with a family-bootstrap 95% CI.

    `family_of` maps prompt_id -> family_id (default: the prompt_id prefix before ".{variant}.o{order}"). Items a
    run did not read out are skipped for that run. Gate (frozen on dev 2026-10-05): ci_lo > 0.5 for every other teacher.
    """
    items = contested_items(own_targets, other_targets)
    fam = (lambda p: family_of[p]) if family_of is not None else (lambda p: p.rsplit(".", 2)[0])
    hits: dict[str, list[int]] = {}
    n_pairs = 0
    for run, letters in letters_by_run.items():
        for p in items:
            if p in letters:
                hits.setdefault(fam(p), []).append(int(letters[p] == own_targets[p]))
                n_pairs += 1
    fams = sorted(hits)
    out = {"n_items": len(items), "n_families": len(fams), "n_runs": len(letters_by_run), "n_pairs": n_pairs, "share": float("nan"), "ci_lo": float("nan"), "ci_hi": float("nan")}
    if not n_pairs:
        return out
    sums = np.array([sum(hits[f]) for f in fams], dtype=float)
    cnts = np.array([len(hits[f]) for f in fams], dtype=float)
    out["share"] = float(sums.sum() / cnts.sum())
    if n_boot > 0 and len(fams) > 1:
        rng = np.random.default_rng(seed)
        boots = rng.integers(0, len(fams), size=(n_boot, len(fams)))
        share = sums[boots].sum(axis=1) / cnts[boots].sum(axis=1)
        out["ci_lo"], out["ci_hi"] = (float(v) for v in np.quantile(share, [0.025, 0.975]))
    return out


# --------------------------------------------------------------------------- seed noise null


def seed_noise_null(metric_table: pd.DataFrame, value: str) -> pd.DataFrame:
    """Distribution of |metric(seed a) - metric(seed b)| over seed pairs within each (teacher, version), plus a pooled row.

    `metric_table` needs columns run_id, teacher, version, seed and `value` (one row per run).
    """
    cols = ["teacher", "version", "metric", "n_pairs", "mean", "sd", "q95"]
    out = []
    pooled: list[float] = []
    for (teacher, version), g in metric_table.groupby(["teacher", "version"], sort=True):
        vals = g.sort_values("seed")[value].to_numpy(dtype=float)
        diffs = [abs(vals[i] - vals[j]) for i in range(len(vals)) for j in range(i + 1, len(vals))]
        pooled += diffs
        d = np.asarray(diffs, dtype=float)
        out.append(dict(teacher=teacher, version=version, metric=value, n_pairs=len(d), mean=float(d.mean()) if len(d) else np.nan, sd=float(d.std(ddof=1)) if len(d) > 1 else np.nan, q95=float(np.quantile(d, 0.95)) if len(d) else np.nan))
    d = np.asarray(pooled, dtype=float)
    out.append(dict(teacher="all", version="all", metric=value, n_pairs=len(d), mean=float(d.mean()) if len(d) else np.nan, sd=float(d.std(ddof=1)) if len(d) > 1 else np.nan, q95=float(np.quantile(d, 0.95)) if len(d) else np.nan))
    return pd.DataFrame(out, columns=cols)


def effect_in_null_sd(diff: float, null_row: pd.Series) -> float:
    """Effect size in units of the seed-noise null SD (docs/04 §3)."""
    sd = float(null_row["sd"])
    return float(diff) / sd if sd and not np.isnan(sd) else float("nan")


def shared_component_r2(shifts_s: pd.DataFrame, shifts_t: pd.DataFrame, own: str, others: Sequence[str], variants: Sequence[str] = SEEN_VARIANTS) -> float:
    """OLS R^2 of the student's r on [1, r_own, r_other...] over common cells (group D). `shifts_s` holds ONE run."""
    runs = shifts_s["teacher"].unique()
    if len(runs) != 1:
        raise ValueError(f"shifts_s must hold one run, got {list(runs)}")
    s = shifts_s[shifts_s["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
    cols = []
    idx = s.index
    for t in [own, *others]:
        tt = shifts_t[(shifts_t["teacher"] == t) & shifts_t["variant"].isin(variants)].set_index(["family_id", "variant"])["r"]
        idx = idx.intersection(tt.index)
        cols.append(tt)
    if len(idx) < len(cols) + 2:
        return float("nan")
    y = s.loc[idx].to_numpy(dtype=float)
    X = np.column_stack([np.ones(len(idx))] + [c.loc[idx].to_numpy(dtype=float) for c in cols])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    ss_res = float(((y - X @ beta) ** 2).sum())
    ss_tot = float(((y - y.mean()) ** 2).sum())
    return 1.0 - ss_res / ss_tot if ss_tot > 0 else float("nan")


# --------------------------------------------------------------------------- one-row-per-run table


def run_keys_table(run_ids: Iterable[str]) -> pd.DataFrame:
    rows = []
    for r in run_ids:
        try:
            k = parse_run_id(r)
        except ValueError:
            continue
        rows.append(dict(run_id=r, student=k.student, teacher=k.teacher, version=k.version, seed=k.seed))
    return pd.DataFrame(rows, columns=["run_id", "student", "teacher", "version", "seed"])


def e1_table(
    student_runs: dict[str, str | Path] | list[TeacherResponse] | pd.DataFrame,
    teacher_profiles: dict[str, str | Path] | list[TeacherResponse] | pd.DataFrame,
    prompts: dict[str, Prompt] | str | Path,
    variants: Sequence[str] = SEEN_VARIANTS,
    n_perm: int = 10_000,
    n_boot: int = 10_000,
    seed: int = 0,
) -> pd.DataFrame:
    """One row per student run: category rates, order gap, agreement / JSD to every teacher, consistency, inheritance.

    `student_runs` maps run_id -> responses path (or is a list of rows / a sym table); `teacher_profiles` maps
    teacher -> profile path (or rows / sym table). Teacher names come from the run id, so a run whose
    teacher has no profile gets agreement / JSD columns but no delta_rho.
    """
    prompts = load_prompts(prompts) if isinstance(prompts, (str, Path)) else prompts
    pid = set(prompts)

    def to_tables(x) -> tuple[pd.DataFrame, pd.DataFrame]:
        """-> (frame, sym). A DataFrame with p_sym is taken as a sym table (then the frame is empty)."""
        if isinstance(x, pd.DataFrame):
            return (pd.DataFrame(columns=["teacher", "category"]), x) if "p_sym" in x.columns else (x, sym_table(x))
        rows = load_responses(x.values(), pid) if isinstance(x, dict) else x
        fr = frame_table(rows, prompts)
        return fr, sym_table(fr)

    (fs, sym_s), (ft, sym_t) = to_tables(student_runs), to_tables(teacher_profiles)
    run_ids = sorted(sym_s["teacher"].unique())
    base = run_keys_table(run_ids).set_index("run_id")
    if base.empty:
        return base.reset_index()

    # category / order
    cat = category_rates(fs, by=("teacher",)).set_index("teacher") if len(fs) else pd.DataFrame(columns=["answer", "malformed"])
    base["answer_rate"] = cat["answer"].reindex(base.index).astype(float)
    base["malformed_rate"] = cat["malformed"].reindex(base.index).astype(float)
    og = order_gap(sym_s).set_index("teacher")
    base["order_gap_mean"] = og["order_gap_mean"].reindex(base.index)

    # agreement / jsd to every teacher
    ag = teacher_agreement(sym_s, sym_t, variants).pivot_table(index="run_id", columns="teacher", values="agreement")
    js = student_teacher_jsd(sym_s, sym_t, variants).pivot_table(index="run_id", columns="teacher", values="jsd")
    teachers = sorted(sym_t["teacher"].unique())
    for t in teachers:
        base[f"agree__{t}"] = ag[t].reindex(base.index) if t in ag else np.nan
        base[f"jsd__{t}"] = js[t].reindex(base.index) if t in js else np.nan
    own = base["teacher"]
    base["agree_own"] = [ag.loc[r, t] if (r in ag.index and t in ag.columns) else np.nan for r, t in own.items()]
    def _nanmax(vals: list[float]) -> float:
        vals = [v for v in vals if not (isinstance(v, float) and np.isnan(v))]
        return max(vals) if vals else np.nan  # order-independent, unlike builtin max over NaNs

    base["agree_other_max"] = [_nanmax([ag.loc[r, o] for o in teachers if o != t and r in ag.index and o in ag.columns]) for r, t in own.items()]
    base["jsd_own"] = [js.loc[r, t] if (r in js.index and t in js.columns) else np.nan for r, t in own.items()]

    # consistency
    cons = consistency(sym_s, variants).set_index("teacher")
    for c in ("n_families", "flip_rate", "mean_jsd", "family_flip_share", "share_uncertain"):
        base[c] = cons[c].reindex(base.index)

    # inheritance
    shifts_s = P.framing_shifts(sym_s, list(variants))
    shifts_t = P.framing_shifts(sym_t, list(variants))
    inh = inheritance(shifts_s, shifts_t, own.to_dict(), variants, n_perm=n_perm, n_boot=n_boot, seed=seed)
    if not inh.empty:
        inh = inh.set_index("run_id")
        for c in ("rho_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "ci_lo", "ci_hi"):
            base[c] = inh[c].reindex(base.index)
        for t in teachers:
            if f"rho__{t}" in inh:
                base[f"rho__{t}"] = inh[f"rho__{t}"].reindex(base.index)
    return base.reset_index()
