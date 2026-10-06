"""Leakage and duplicate checks for the contested pool (tasks/e2c_plan.md §2).

All similarities use the same TF-IDF char_wb(3, 5) cosine as `vcd.data.dedup_split`, computed in chunks so a
pool of ~10k situations against ~3k existing families fits in memory.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Iterable, Optional

import numpy as np
from scipy import sparse
from sklearn.feature_extraction.text import TfidfVectorizer

from vcd.schemas import Family

NEW_SOURCES = ("scruples", "aita_berkeley", "moral_stories", "hendrycks_ethics")


def char_vectorizer() -> TfidfVectorizer:
    return TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)


def max_cosine(query: sparse.csr_matrix, ref: sparse.csr_matrix, chunk: int = 1000, exclude_self: bool = False) -> tuple[np.ndarray, np.ndarray]:
    """Per query row: (max cosine against ref rows, argmax index). With `exclude_self`, query and ref are the
    same matrix and the diagonal is ignored."""
    n = query.shape[0]
    best = np.zeros(n)
    arg = np.full(n, -1, dtype=int)
    ref_t = ref.T.tocsc()
    for start in range(0, n, chunk):
        stop = min(n, start + chunk)
        sims = (query[start:stop] @ ref_t).toarray()
        if exclude_self:
            idx = np.arange(start, stop)
            sims[np.arange(stop - start), idx] = -1.0
        if sims.shape[1] == 0:
            continue
        a = sims.argmax(axis=1)
        best[start:stop] = sims[np.arange(stop - start), a]
        arg[start:stop] = a
    return best, arg


@dataclass
class LeakageReport:
    drop: dict[str, tuple[str, str, float]] = field(default_factory=dict)  # family_id -> (reason, matched_id, sim)
    review: list[tuple[str, str, float]] = field(default_factory=list)  # (family_id, matched_id, sim) in [review, drop)
    reused: set[str] = field(default_factory=set)  # pool rows that are existing families on purpose (same id)
    max_sim: dict[str, float] = field(default_factory=dict)  # family_id -> max situation cosine vs existing
    max_sim_eval: dict[str, float] = field(default_factory=dict)  # family_id -> max situation cosine vs dev / test only
    max_sim_joint: dict[str, float] = field(default_factory=dict)  # per space, for the report
    max_sim_reference: dict[str, float] = field(default_factory=dict)
    action_review: list[tuple[str, str, float, float]] = field(default_factory=list)  # (pool, dev/test id, action cosine >= thr, situation cosine)
    source_item_conflicts: list[str] = field(default_factory=list)
    fit_corpus: str = ""

    def eval_histogram(self, edges: Iterable[float] = (0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 1.01)) -> list[tuple[str, int]]:
        edges = list(edges)
        vals = np.array([v for k, v in self.max_sim_eval.items()])
        return [(f"[{lo:.1f}, {min(hi, 1.0):.1f}{']' if hi > 1 else ')'}", int(((vals >= lo) & (vals < hi)).sum())) for lo, hi in zip(edges[:-1], edges[1:])]

    def sim_histogram(self, edges: Iterable[float] = (0.0, 0.3, 0.5, 0.7, 0.8, 0.9, 1.01)) -> list[tuple[str, int]]:
        edges = list(edges)
        vals = np.array([v for k, v in self.max_sim.items() if k not in self.reused])
        out = []
        for lo, hi in zip(edges[:-1], edges[1:]):
            out.append((f"[{lo:.1f}, {min(hi, 1.0):.1f}{']' if hi > 1 else ')'}", int(((vals >= lo) & (vals < hi)).sum())))
        return out


def check_leakage(
    pool: list[Family],
    existing: list[Family],
    sit_threshold: float = 0.9,
    review_threshold: float = 0.7,
    action_threshold: float = 0.9,
    action_sit_threshold: float = 0.7,
    reference_fit: bool = True,
) -> LeakageReport:
    """Mark pool rows that would leak from the existing families (every split, dev / test included).

    Rules: situation cosine >= sit_threshold -> drop; action pair cosine >= action_threshold AND situation cosine
    >= action_sit_threshold (checked against EVERY existing family above that situation cosine, not only the
    nearest) -> drop; situation cosine in [review_threshold, sit_threshold) -> listed for a human. Pool rows whose
    action pair matches a dev / test pair at >= action_threshold are listed (`action_review`) whatever the situation
    cosine.

    Metric: the TF-IDF cosine is computed in two spaces and the LARGER value is used everywhere -- the joint space
    (vectorizer fitted on existing + pool, the implementer's original) and, with `reference_fit`, the reference
    space of `dedup_split` (fitted on the existing families only; pool rows are transformed into it, which can only
    raise their cosine because n-grams unknown to the reference drop out). Both maxima are kept per row.

    A pool row whose family_id is an existing family with the same source is a deliberate re-use (MoralChoice
    low) and is exempt; a pool row from a NEW source whose (source, source_id) exists already is a conflict.
    """
    rep = LeakageReport()
    rep.fit_corpus = "max over the joint space (existing + pool) and the reference space (existing only)" if reference_fit else "joint space (existing + pool)"
    ex_ids = {f.family_id: f for f in existing}
    ex_items = {(f.source, f.source_id) for f in existing}
    for f in pool:
        if f.family_id in ex_ids and ex_ids[f.family_id].source == f.source:
            rep.reused.add(f.family_id)
        if f.source in NEW_SOURCES and (f.source, f.source_id) in ex_items:
            rep.source_item_conflicts.append(f.family_id)
    ex_two = [f for f in existing if f.item_form == "two_action" and f.situation]
    if not ex_two or not pool:
        return rep
    ex_texts = [f.situation for f in ex_two]
    pool_texts = [f.situation for f in pool]
    ex_acts = [f"{f.action_x} {f.action_y}" for f in ex_two]
    pool_acts = [f"{f.action_x} {f.action_y}" for f in pool]
    eval_idx = np.array([k for k, f in enumerate(ex_two) if f.split in ("dev", "test")], dtype=int)

    spaces: list[tuple[sparse.csr_matrix, sparse.csr_matrix, sparse.csr_matrix, sparse.csr_matrix]] = []
    vec = char_vectorizer()
    x = vec.fit_transform(ex_texts + pool_texts)
    vec_a = char_vectorizer()
    xa = vec_a.fit_transform(ex_acts + pool_acts)
    spaces.append((x[: len(ex_two)], x[len(ex_two) :], xa[: len(ex_two)], xa[len(ex_two) :]))
    if reference_fit:
        vec_r = char_vectorizer()
        ex_r = vec_r.fit_transform(ex_texts)
        vec_ra = char_vectorizer()
        ex_ra = vec_ra.fit_transform(ex_acts)
        spaces.append((ex_r, vec_r.transform(pool_texts), ex_ra, vec_ra.transform(pool_acts)))

    n = len(pool)
    best = np.zeros(n)
    arg = np.full(n, -1, dtype=int)
    best_eval = np.zeros(n)
    best_eval_a = np.zeros(n)
    arg_eval_a = np.full(n, -1, dtype=int)
    per_space: list[np.ndarray] = []
    for ex_x, pool_x, ex_a, pool_a in spaces:
        b, a = max_cosine(pool_x, ex_x)
        per_space.append(b)
        upd = b > best
        best[upd], arg[upd] = b[upd], a[upd]
        if len(eval_idx):
            be, _ = max_cosine(pool_x, ex_x[eval_idx])
            best_eval = np.maximum(best_eval, be)
            ba, aa = max_cosine(pool_a, ex_a[eval_idx])
            upd = ba > best_eval_a
            best_eval_a[upd], arg_eval_a[upd] = ba[upd], aa[upd]
    rep.max_sim_joint = {f.family_id: float(per_space[0][i]) for i, f in enumerate(pool)}
    if reference_fit:
        rep.max_sim_reference = {f.family_id: float(per_space[1][i]) for i, f in enumerate(pool)}

    def sit_row(i: int) -> np.ndarray:
        out = None
        for ex_x, pool_x, _, _ in spaces:
            r = (pool_x[i] @ ex_x.T).toarray()[0]
            out = r if out is None else np.maximum(out, r)
        return out

    def act_sims(i: int, idx: np.ndarray) -> np.ndarray:
        out = None
        for _, _, ex_a, pool_a in spaces:
            r = (pool_a[i] @ ex_a[idx].T).toarray()[0]
            out = r if out is None else np.maximum(out, r)
        return out

    for i, f in enumerate(pool):
        rep.max_sim[f.family_id] = float(best[i])
        if len(eval_idx):
            rep.max_sim_eval[f.family_id] = float(best_eval[i])
        if f.family_id in rep.reused:
            continue
        if len(eval_idx) and best_eval_a[i] >= action_threshold:
            j = int(eval_idx[int(arg_eval_a[i])])
            rep.action_review.append((f.family_id, ex_two[j].family_id, float(best_eval_a[i]), float(sit_row(i)[j])))
        match = ex_two[int(arg[i])]
        if best[i] >= sit_threshold:
            rep.drop[f.family_id] = ("situation_near_duplicate", match.family_id, float(best[i]))
            continue
        if best[i] >= action_sit_threshold:
            sims = sit_row(i)
            near = np.where(sims >= action_sit_threshold)[0]
            a_sims = act_sims(i, near)
            hit = [(float(a_sims[k]), int(near[k])) for k in range(len(near)) if a_sims[k] >= action_threshold]
            if hit:
                _, j = max(hit)
                rep.drop[f.family_id] = ("action_pair_and_situation_similar", ex_two[j].family_id, float(sims[j]))
                continue
        if best[i] >= review_threshold:
            rep.review.append((f.family_id, match.family_id, float(best[i])))
    return rep


def dedup_within_pool(pool: list[Family], threshold: float = 0.9) -> tuple[list[Family], list[tuple[str, str, float]]]:
    """Drop the later of any two pool rows whose situations have cosine >= threshold (chunked; order-stable).
    The vectorizer is fitted on the pool itself (its own reference space), so a pair of re-used sanity families
    can fall above the threshold here although it survived dedup_split on the smaller families.jsonl corpus."""
    if len(pool) < 2:
        return list(pool), []
    vec = char_vectorizer()
    x = vec.fit_transform([f.situation for f in pool])
    xt = x.T.tocsc()
    dropped: list[tuple[str, str, float]] = []
    drop_idx: set[int] = set()
    chunk = 1000
    for start in range(0, len(pool), chunk):
        stop = min(len(pool), start + chunk)
        sims = (x[start:stop] @ xt).toarray()
        for r in range(stop - start):
            j = start + r
            if j in drop_idx:
                continue
            row = sims[r, :j]
            cands = np.where(row >= threshold)[0]
            cands = [int(i) for i in cands if int(i) not in drop_idx]
            if cands:
                i = max(cands, key=lambda k: row[k])
                drop_idx.add(j)
                dropped.append((pool[j].family_id, pool[i].family_id, float(row[i])))
    kept = [f for k, f in enumerate(pool) if k not in drop_idx]
    return kept, dropped


def dedup_aita_titles(pool: list[Family], threshold: float = 0.9) -> tuple[list[Family], list[tuple[str, str, float]]]:
    """Scruples and Berkeley are both r/AITA: drop later rows sharing a Reddit post id or a title with cosine >=
    threshold (the two corpora cover 2018-19 and 2022-23, so this is expected to be empty)."""
    aita = [(k, f) for k, f in enumerate(pool) if f.source in ("scruples", "aita_berkeley")]
    dropped: list[tuple[str, str, float]] = []
    drop_idx: set[int] = set()
    seen_post: dict[str, str] = {}
    for k, f in aita:
        pid = str(f.meta.get("post_id") or f.meta.get("submission_id") or "")
        if pid and pid in seen_post:
            drop_idx.add(k)
            dropped.append((f.family_id, seen_post[pid], 1.0))
        elif pid:
            seen_post[pid] = f.family_id
    rest = [(k, f) for k, f in aita if k not in drop_idx and f.meta.get("title")]
    if len(rest) >= 2:
        vec = char_vectorizer()
        x = vec.fit_transform([str(f.meta["title"]) for _, f in rest])
        best, arg = max_cosine(x, x, exclude_self=True)
        for n, (k, f) in enumerate(rest):
            if best[n] >= threshold and int(arg[n]) < n:
                drop_idx.add(k)
                dropped.append((f.family_id, rest[int(arg[n])][1].family_id, float(best[n])))
    kept = [f for k, f in enumerate(pool) if k not in drop_idx]
    return kept, dropped


def flag_counts(fams: Iterable[Family]) -> dict[str, Counter]:
    out: dict[str, Counter] = defaultdict(Counter)
    for f in fams:
        for fl in f.needs_review:
            out[f.source][fl] += 1
    return out


def md_table(header: list[str], rows: list[list]) -> str:
    def fmt(v) -> str:
        if isinstance(v, float):
            return f"{v:.3f}"
        return str(v)

    lines = ["| " + " | ".join(header) + " |", "|" + "---|" * len(header)]
    lines += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in rows]
    return "\n".join(lines)
