"""Small statistics helpers used across E0 analyses."""

from __future__ import annotations

import math
from typing import Callable, Sequence

import numpy as np
from scipy import stats as sps


def bootstrap_ci(
    x: Sequence[float], stat: Callable = np.mean, n_boot: int = 10_000, alpha: float = 0.05, seed: int = 0
) -> tuple[float, float]:
    arr = np.asarray([v for v in x if v is not None and not (isinstance(v, float) and math.isnan(v))], dtype=float)
    if arr.size == 0:
        return (float("nan"), float("nan"))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, arr.size, size=(n_boot, arr.size))
    boots = stat(arr[idx], axis=1)
    return (float(np.quantile(boots, alpha / 2)), float(np.quantile(boots, 1 - alpha / 2)))


def _paired(a: Sequence[float], b: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    a = np.asarray(a, dtype=float)
    b = np.asarray(b, dtype=float)
    m = ~(np.isnan(a) | np.isnan(b))
    return a[m], b[m]


def pearson(a: Sequence[float], b: Sequence[float]) -> tuple[float, float]:
    a, b = _paired(a, b)
    if a.size < 3 or np.std(a) == 0 or np.std(b) == 0:
        return (float("nan"), float("nan"))
    r, p = sps.pearsonr(a, b)
    return (float(r), float(p))


def spearman(a: Sequence[float], b: Sequence[float]) -> tuple[float, float]:
    a, b = _paired(a, b)
    if a.size < 3:
        return (float("nan"), float("nan"))
    r, p = sps.spearmanr(a, b)
    return (float(r), float(p))


def spearman_brown(r_half: float) -> float:
    """Reliability of the full-length measure from a split-half correlation."""
    if math.isnan(r_half) or r_half <= -1:
        return float("nan")
    return 2 * r_half / (1 + r_half)


def cohen_kappa(a: Sequence, b: Sequence) -> float:
    a = list(a)
    b = list(b)
    assert len(a) == len(b) and len(a) > 0
    labels = sorted(set(a) | set(b))
    n = len(a)
    po = sum(x == y for x, y in zip(a, b)) / n
    pe = sum((a.count(l) / n) * (b.count(l) / n) for l in labels)
    return float("nan") if pe == 1 else (po - pe) / (1 - pe)


def wilson_ci(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    if n == 0:
        return (float("nan"), float("nan"))
    p = k / n
    denom = 1 + z**2 / n
    centre = (p + z**2 / (2 * n)) / denom
    half = z * math.sqrt(p * (1 - p) / n + z**2 / (4 * n**2)) / denom
    return (max(0.0, centre - half), min(1.0, centre + half))
