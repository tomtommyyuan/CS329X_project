"""Near-duplicate removal and family-level, topic-stratified splitting."""

from __future__ import annotations

import random
from collections import defaultdict
from typing import Iterable

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from vcd.schemas import Family


def find_near_duplicates(texts: list[str], threshold: float = 0.9) -> set[int]:
    """Indices to drop: for each pair with cosine >= threshold, the later index is dropped."""
    if len(texts) < 2:
        return set()
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
    x = vec.fit_transform(texts)
    sims = (x @ x.T).toarray()
    np.fill_diagonal(sims, 0.0)
    drop: set[int] = set()
    for i in range(len(texts)):
        if i in drop:
            continue
        for j in np.where(sims[i] >= threshold)[0]:
            if j > i:
                drop.add(int(j))
    return drop


def dedup_families(fams: list[Family], threshold: float = 0.9) -> tuple[list[Family], list[tuple[str, str]]]:
    """Dedup within two_action families by situation text. Returns (kept, dropped_pairs)."""
    two = [f for f in fams if f.item_form == "two_action"]
    others = [f for f in fams if f.item_form != "two_action"]
    texts = [f.situation for f in two]
    drop_idx = find_near_duplicates(texts, threshold)
    dropped: list[tuple[str, str]] = []
    if drop_idx:
        vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5), min_df=1)
        x = vec.fit_transform(texts)
        sims = (x @ x.T).toarray()
        for j in sorted(drop_idx):
            i = int(np.argmax(np.where(np.arange(len(texts)) < j, sims[j], -1)))
            dropped.append((two[j].family_id, two[i].family_id))
    kept = [f for k, f in enumerate(two) if k not in drop_idx] + others
    return kept, dropped


def _stratified_take(fams: list[Family], n: int, rng: random.Random) -> list[Family]:
    """Round-robin over topic_group so every group is represented."""
    by_topic: dict[str, list[Family]] = defaultdict(list)
    for f in fams:
        by_topic[f.topic_group].append(f)
    for lst in by_topic.values():
        rng.shuffle(lst)
    groups = sorted(by_topic)
    rng.shuffle(groups)
    out: list[Family] = []
    while len(out) < n and any(by_topic[g] for g in groups):
        for g in groups:
            if by_topic[g] and len(out) < n:
                out.append(by_topic[g].pop())
    return out


def assign_splits(
    fams: list[Family], pilot_cfg: dict, split_cfg: dict, seed: int, exclude_flags: Iterable[str] = ()
) -> list[Family]:
    """Mutates and returns `fams` with split labels.

    pilot_cfg: {daily_dilemmas, moralchoice_high, moralchoice_low, valueconsistency}
    split_cfg: {dev, test}; everything else among high-ambiguity two_action families is train.
    moralchoice_low not in pilot -> "sanity"; valueconsistency not in pilot -> "pool".
    Families carrying any flag in `exclude_flags` (e.g. third-person situations) -> "excluded".
    """
    rng = random.Random(seed)
    excl = set(exclude_flags)
    excluded = [f for f in fams if excl & set(f.needs_review)]
    for f in excluded:
        f.split = "excluded"
    fams_in = [f for f in fams if f.split != "excluded"]
    pools = {
        "daily_dilemmas": [f for f in fams_in if f.source == "daily_dilemmas"],
        "moralchoice_high": [f for f in fams_in if f.source == "moralchoice" and f.ambiguity == "high"],
        "moralchoice_low": [f for f in fams_in if f.source == "moralchoice" and f.ambiguity == "low"],
        "valueconsistency": [f for f in fams_in if f.source == "valueconsistency"],
    }
    chosen: set[str] = set()
    for key, n in pilot_cfg.items():
        for f in _stratified_take(pools.get(key, []), int(n), rng):
            f.split = "pilot"
            chosen.add(f.family_id)
    rest_main = [f for f in pools["daily_dilemmas"] + pools["moralchoice_high"] if f.family_id not in chosen]
    test = _stratified_take(rest_main, int(split_cfg["test"]), rng)
    for f in test:
        f.split = "test"
        chosen.add(f.family_id)
    rest_main = [f for f in rest_main if f.family_id not in chosen]
    dev = _stratified_take(rest_main, int(split_cfg["dev"]), rng)
    for f in dev:
        f.split = "dev"
        chosen.add(f.family_id)
    for f in rest_main:
        if f.family_id not in chosen:
            f.split = "train"
    for f in pools["moralchoice_low"]:
        if f.family_id not in chosen:
            f.split = "sanity"
    for f in pools["valueconsistency"]:
        if f.family_id not in chosen:
            f.split = "pool"
    return fams


def split_summary(fams: Iterable[Family]) -> dict:
    counts: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for f in fams:
        counts[f.split][f.source] += 1
    return {s: dict(v) for s, v in counts.items()}
