"""From TeacherResponse rows to symmetrized probabilities, framing shifts, type effects, reliability.

Definitions follow docs/04_eval_metrics.md §0:
  p(i,j)      order-symmetrized P(choose x)
  r(i,j)      p(i,j) - mean_j p(i,j)            framing shift
  delta(j)    mean_i r(i,j)                      type effect
"""

from __future__ import annotations

from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from vcd.schemas import Prompt, TeacherResponse
from vcd.stats import bootstrap_ci, pearson, spearman, spearman_brown


def responses_to_frame(responses: Iterable[TeacherResponse], prompts: dict[str, Prompt]) -> pd.DataFrame:
    rows = []
    for r in responses:
        p = prompts[r.prompt_id]
        rows.append(
            dict(
                teacher=r.teacher,
                mode=r.mode,
                pass_idx=r.pass_idx,
                sample_idx=r.sample_idx,
                prompt_id=r.prompt_id,
                family_id=p.family_id,
                variant=p.variant,
                order=p.order,
                category=r.category,
                choice_action=r.choice_action,
                p_x=r.p_x,
            )
        )
    return pd.DataFrame(rows)


def align_to_focus(df: pd.DataFrame, focus_by_family: dict[str, str]) -> pd.DataFrame:
    """Re-express p_x and choice_action in the coordinates of each family's positive act.

    For families whose focus is "y", p_x -> 1 - p_x and choice x <-> y, for every variant, so that
    directional framings (T5 toward the act, T6 away) have one sign across families.
    """
    out = df.copy()
    flip = out["family_id"].map(lambda f: focus_by_family.get(f) == "y").fillna(False).astype(bool)
    px = out.loc[flip, "p_x"]
    out.loc[flip, "p_x"] = 1.0 - px
    out.loc[flip, "choice_action"] = out.loc[flip, "choice_action"].map({"x": "y", "y": "x"})
    return out


def cell_estimates(df: pd.DataFrame) -> pd.DataFrame:
    """Per (teacher, family, variant, order, pass): P(x) estimate.

    Rows with p_x (logprob readout) are averaged; otherwise P(x) = frequency of x among answers.
    """
    prof = df[df["mode"] == "profile"]
    out = []
    for key, g in prof.groupby(["teacher", "family_id", "variant", "order", "pass_idx"], sort=True):
        ans = g[g["category"] == "answer"]
        if len(ans) == 0:
            p = np.nan
        elif ans["p_x"].notna().any():
            p = float(ans["p_x"].mean())
        else:
            p = float((ans["choice_action"] == "x").mean())
        out.append(dict(zip(["teacher", "family_id", "variant", "order", "pass_idx"], key), p_x=p, n_answer=len(ans), n_total=len(g)))
    return pd.DataFrame(out)


def symmetrize(cells: pd.DataFrame) -> pd.DataFrame:
    """Average over passes, then over the two orders. p_sym is NaN unless both orders are present."""
    c = cells.groupby(["teacher", "family_id", "variant", "order"], as_index=False)["p_x"].mean()
    w = c.pivot_table(index=["teacher", "family_id", "variant"], columns="order", values="p_x", aggfunc="mean")
    w = w.rename(columns={1: "p_o1", 2: "p_o2"}).reset_index()
    for col in ("p_o1", "p_o2"):
        if col not in w:
            w[col] = np.nan
    w["p_sym"] = w[["p_o1", "p_o2"]].mean(axis=1, skipna=False)
    w["order_gap"] = (w["p_o1"] - w["p_o2"]).abs()
    return w


def framing_shifts(sym: pd.DataFrame, variants: Sequence[str], col: str = "p_sym") -> pd.DataFrame:
    """r(i,j) over the given variants; families missing any variant are dropped."""
    s = sym[sym["variant"].isin(variants)].copy()
    out = []
    for (teacher, fam), g in s.groupby(["teacher", "family_id"]):
        g = g.dropna(subset=[col])
        if len(g) != len(variants):
            continue
        mean_p = g[col].mean()
        for _, row in g.iterrows():
            out.append(dict(teacher=teacher, family_id=fam, variant=row["variant"], p=row[col], r=row[col] - mean_p))
    return pd.DataFrame(out, columns=["teacher", "family_id", "variant", "p", "r"])


def type_effects(shifts: pd.DataFrame, n_boot: int = 10_000, seed: int = 0) -> pd.DataFrame:
    out = []
    for (teacher, variant), g in shifts.groupby(["teacher", "variant"]):
        lo, hi = bootstrap_ci(g["r"].to_numpy(), n_boot=n_boot, seed=seed)
        out.append(dict(teacher=teacher, variant=variant, delta=float(g["r"].mean()), ci_lo=lo, ci_hi=hi, n_families=g["family_id"].nunique()))
    return pd.DataFrame(out)


def profile_vector(shifts: pd.DataFrame, teacher: str) -> pd.Series:
    s = shifts[shifts["teacher"] == teacher].set_index(["family_id", "variant"])["r"]
    return s.sort_index()


def reliability_by_order(sym: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Split-half by option order: corr of r computed from order-1 vs order-2 alone, Spearman-Brown corrected."""
    out = []
    for teacher in sorted(sym["teacher"].unique()):
        s = sym[sym["teacher"] == teacher]
        r1 = framing_shifts(s, variants, col="p_o1").set_index(["family_id", "variant"])["r"]
        r2 = framing_shifts(s, variants, col="p_o2").set_index(["family_id", "variant"])["r"]
        idx = r1.index.intersection(r2.index)
        rho, _ = pearson(r1.loc[idx], r2.loc[idx])
        out.append(dict(teacher=teacher, n_cells=len(idx), r_half=rho, reliability=spearman_brown(rho)))
    return pd.DataFrame(out)


def reliability_by_pass(cells: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Test-retest: profile from pass 0 vs pass 1 (sampling-readout teachers)."""
    out = []
    for teacher in sorted(cells["teacher"].unique()):
        c = cells[cells["teacher"] == teacher]
        passes = sorted(c["pass_idx"].unique())
        if len(passes) < 2:
            out.append(dict(teacher=teacher, n_cells=0, r_retest=np.nan))
            continue
        vecs = []
        for p in passes[:2]:
            sym_p = symmetrize(c[c["pass_idx"] == p])
            vecs.append(framing_shifts(sym_p, variants).set_index(["family_id", "variant"])["r"])
        idx = vecs[0].index.intersection(vecs[1].index)
        rho, _ = pearson(vecs[0].loc[idx], vecs[1].loc[idx])
        out.append(dict(teacher=teacher, n_cells=len(idx), r_retest=rho))
    return pd.DataFrame(out)


def residual_shifts(shifts: pd.DataFrame) -> pd.DataFrame:
    """r minus the teacher's own type effect delta(j): the family-specific part of the profile.

    With directional framings every teacher shares the sign of delta(T6), which inflates raw profile
    correlations; the residual asks whether teachers are fragile on the same families beyond that.
    """
    s = shifts.copy()
    s["r"] = s["r"] - s.groupby(["teacher", "variant"])["r"].transform("mean")
    return s


def cross_teacher(shifts: pd.DataFrame) -> pd.DataFrame:
    """Pairwise profile correlation (raw and residualized) and majority-judgment agreement between teachers."""
    teachers = sorted(shifts["teacher"].unique())
    resid = residual_shifts(shifts)
    out = []
    for i, a in enumerate(teachers):
        for b in teachers[i + 1 :]:
            va = profile_vector(shifts, a)
            vb = profile_vector(shifts, b)
            idx = va.index.intersection(vb.index)
            pr, _ = pearson(va.loc[idx], vb.loc[idx])
            sr, _ = spearman(va.loc[idx], vb.loc[idx])
            ra = profile_vector(resid, a).loc[idx]
            rb = profile_vector(resid, b).loc[idx]
            prr, _ = pearson(ra, rb)
            pa = shifts[shifts["teacher"] == a].set_index(["family_id", "variant"])["p"].loc[idx]
            pb = shifts[shifts["teacher"] == b].set_index(["family_id", "variant"])["p"].loc[idx]
            agree = float(((pa > 0.5) == (pb > 0.5)).mean()) if len(idx) else np.nan
            out.append(dict(teacher_a=a, teacher_b=b, n_cells=len(idx), profile_pearson=pr, profile_spearman=sr, residual_pearson=prr, majority_agreement=agree))
    return pd.DataFrame(out)


def _jsd(p: np.ndarray, q: np.ndarray) -> np.ndarray:
    p = np.clip(p, 1e-9, 1 - 1e-9)
    q = np.clip(q, 1e-9, 1 - 1e-9)
    m = (p + q) / 2

    def kl(a, b):
        return a * np.log2(a / b) + (1 - a) * np.log2((1 - a) / (1 - b))

    return (kl(p, m) + kl(q, m)) / 2


def teacher_consistency(sym: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Group-B consistency metrics applied to a teacher's symmetrized probabilities.

    share_uncertain: cells with 0.05 < p < 0.95 (how deterministic the teacher is);
    flip_rate: mean over variant pairs of the share of families whose majority action differs;
    family_flip_share: families whose majority action is not the same under every variant;
    mean_jsd: mean pairwise cross-framing JSD.
    """
    out = []
    for teacher in sorted(sym["teacher"].unique()):
        s = sym[(sym["teacher"] == teacher) & (sym["variant"].isin(variants))]
        piv = s.pivot_table(index="family_id", columns="variant", values="p_sym").dropna()
        if len(piv) == 0 or any(v not in piv.columns for v in variants):
            out.append(dict(teacher=teacher, n_families=0, share_uncertain=np.nan, flip_rate=np.nan, family_flip_share=np.nan, mean_jsd=np.nan))
            continue
        maj = piv[list(variants)] > 0.5
        pairs = [(a, b) for i, a in enumerate(variants) for b in variants[i + 1 :]]
        flip_rate = float(np.mean([(maj[a] != maj[b]).mean() for a, b in pairs]))
        mean_jsd = float(np.mean([_jsd(piv[a].to_numpy(), piv[b].to_numpy()).mean() for a, b in pairs]))
        vals = s["p_sym"].dropna()
        out.append(dict(
            teacher=teacher, n_families=len(piv),
            share_uncertain=float(((vals > 0.05) & (vals < 0.95)).mean()) if len(vals) else np.nan,
            flip_rate=flip_rate, family_flip_share=float((maj.nunique(axis=1) > 1).mean()), mean_jsd=mean_jsd,
        ))
    return pd.DataFrame(out)


def _majority_table(sym: pd.DataFrame, teacher: str, variants: Sequence[str]) -> pd.DataFrame:
    s = sym[(sym["teacher"] == teacher) & (sym["variant"].isin(variants))]
    piv = s.pivot_table(index="family_id", columns="variant", values="p_sym").dropna()
    if len(piv) == 0 or any(v not in piv.columns for v in variants):
        return pd.DataFrame()
    return piv[list(variants)] > 0.5


def pairwise_flip_rates(sym: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Share of families whose majority action differs between each pair of framings, per teacher."""
    out = []
    for teacher in sorted(sym["teacher"].unique()):
        maj = _majority_table(sym, teacher, variants)
        if maj.empty:
            continue
        for i, a in enumerate(variants):
            for b in variants[i + 1 :]:
                out.append(dict(teacher=teacher, pair=f"{a}-{b}", flip_rate=float((maj[a] != maj[b]).mean()), n_families=len(maj)))
    return pd.DataFrame(out, columns=["teacher", "pair", "flip_rate", "n_families"])


def flip_overlap(sym: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Do teachers flip on the same families? Jaccard overlap of the sets of flipping families."""
    sets: dict[str, set] = {}
    for teacher in sorted(sym["teacher"].unique()):
        maj = _majority_table(sym, teacher, variants)
        if not maj.empty:
            sets[teacher] = set(maj.index[maj.nunique(axis=1) > 1])
    out = []
    teachers = sorted(sets)
    for i, a in enumerate(teachers):
        for b in teachers[i + 1 :]:
            inter, union = sets[a] & sets[b], sets[a] | sets[b]
            out.append(dict(teacher_a=a, teacher_b=b, n_flip_a=len(sets[a]), n_flip_b=len(sets[b]), shared=len(inter), jaccard=(len(inter) / len(union)) if union else np.nan))
    return pd.DataFrame(out, columns=["teacher_a", "teacher_b", "n_flip_a", "n_flip_b", "shared", "jaccard"])


def order_stability(df: pd.DataFrame) -> pd.DataFrame:
    """Demo mode (T=0): share of (family, variant) where both orders yield the same action."""
    demo = df[(df["mode"] == "demo")]
    out = []
    for teacher, g in demo.groupby("teacher"):
        piv = g.pivot_table(index=["family_id", "variant"], columns="order", values="choice_action", aggfunc="first")
        if 1 not in piv.columns or 2 not in piv.columns:
            out.append(dict(teacher=teacher, n_items=len(piv), n_both_answered=0, order_stable_rate=np.nan))
            continue
        both = piv.dropna()
        stable = (both[1] == both[2]).mean() if len(both) else np.nan
        out.append(dict(teacher=teacher, n_items=len(piv), n_both_answered=len(both), order_stable_rate=float(stable)))
    return pd.DataFrame(out)


def answer_rates(df: pd.DataFrame, families: pd.DataFrame, by: Sequence[str] = ("teacher", "source", "variant")) -> pd.DataFrame:
    """Category shares in demo mode, grouped by the given columns (joins family source)."""
    demo = df[df["mode"] == "demo"].merge(families[["family_id", "source", "controversial"]], on="family_id", how="left")
    tab = demo.groupby(list(by))["category"].value_counts(normalize=True).unstack(fill_value=0.0)
    tab["n"] = demo.groupby(list(by)).size()
    return tab.reset_index()
