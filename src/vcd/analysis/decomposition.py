"""Cell-structure decomposition of student-teacher agreement (docs/paper_narrative.md figure 4).

Every test cell (family x framing) is classified by how the candidate teachers' symmetrized majority actions relate:
`all_agree`, or `unique_<t>` when exactly one teacher t dissents from the other two. For a student trained on teacher
t, cells are then grouped as `all_agree`, `own_unique` (only t holds that answer) and `own_with_one_other` (another
teacher is the dissenter). `follow_own` is the share of cells where the student's majority action equals its teacher's;
`follow_other_max` the largest such share for any other teacher. The run-level inheritance gap is driven almost
entirely by the `own_unique` cells, which is why GPT-4o (fewest unique cells, lowest follow rate) shows no gap.
Pure functions over pandas frames; loading lives in scripts/23_cell_decomposition.py.
"""

from __future__ import annotations

from typing import Sequence

import numpy as np
import pandas as pd


def majority_frame(sym: pd.DataFrame, variants: Sequence[str]) -> pd.DataFrame:
    """Rows (teacher, family_id, variant, maj) with maj in {'x','y'}; cells at p_sym == 0.5 are dropped."""
    s = sym[sym["variant"].isin(list(variants))].copy()
    s["maj"] = np.where(s["p_sym"] > 0.5, "x", np.where(s["p_sym"] < 0.5, "y", None))
    return s.dropna(subset=["maj"])[["teacher", "family_id", "variant", "maj"]]


def cell_structure(teacher_maj: pd.DataFrame, teachers: Sequence[str]) -> pd.DataFrame:
    """One row per cell where every teacher has a majority: columns = teachers' actions + `structure`."""
    piv = teacher_maj.pivot_table(index=["family_id", "variant"], columns="teacher", values="maj", aggfunc="first")
    piv = piv.reindex(columns=list(teachers)).dropna()

    def _label(row) -> str:
        labs = row.to_dict()
        if len(set(labs.values())) == 1:
            return "all_agree"
        odd = [t for t in teachers if sum(labs[o] == labs[t] for o in teachers) == 1]
        return f"unique_{odd[0]}" if len(odd) == 1 else "split"

    piv["structure"] = piv.apply(_label, axis=1)
    return piv.reset_index()


def teacher_pairwise(structure: pd.DataFrame, teachers: Sequence[str]) -> pd.DataFrame:
    rows = []
    for i, a in enumerate(teachers):
        for b in list(teachers)[i + 1:]:
            rows.append({"a": a, "b": b, "agreement": float((structure[a] == structure[b]).mean()), "n_cells": len(structure)})
    return pd.DataFrame(rows)


def own_category(structure_label: str, own: str) -> str:
    if structure_label == "all_agree":
        return "all_agree"
    if structure_label == f"unique_{own}":
        return "own_unique"
    return "own_with_one_other"


def follow_rates(student_maj: pd.DataFrame, structure: pd.DataFrame, teachers: Sequence[str], own: str,
                 by: Sequence[str] = ()) -> pd.DataFrame:
    """For one run's majority frame: follow_own / follow_other_max per own-category (optionally also per `by` columns)."""
    m = student_maj.merge(structure, on=["family_id", "variant"], how="inner")
    m["category"] = m["structure"].map(lambda s: own_category(s, own))
    others = [t for t in teachers if t != own]
    rows = []
    for keys, g in m.groupby(["category", *by]):
        keys = (keys,) if not isinstance(keys, tuple) else keys
        rows.append({"category": keys[0], **dict(zip(by, keys[1:])), "n_cells": len(g),
                     "follow_own": float((g["maj"] == g[own]).mean()),
                     "follow_other_max": float(max((g["maj"] == g[o]).mean() for o in others)) if others else np.nan})
    return pd.DataFrame(rows)


def seed_mean(table: pd.DataFrame, keys: Sequence[str], values: Sequence[str] = ("follow_own", "follow_other_max")) -> pd.DataFrame:
    """Mean and sd over runs (seeds) of the follow rates, plus the per-run cell count (identical across seeds)."""
    agg = {v: ["mean", "std"] for v in values}
    agg["n_cells"] = ["first"]
    agg["run_id"] = ["nunique"]
    out = table.groupby(list(keys)).agg(agg)
    out.columns = ["_".join(c) if c[1] not in ("first", "nunique") else {"first": c[0], "nunique": "n_runs"}[c[1]] for c in out.columns]
    return out.reset_index()
