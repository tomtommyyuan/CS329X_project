import numpy as np

from vcd.stats import bootstrap_ci, cohen_kappa, pearson, spearman_brown, wilson_ci


def test_bootstrap_ci_contains_mean():
    x = np.random.default_rng(0).normal(0.5, 0.1, 200)
    lo, hi = bootstrap_ci(x, n_boot=2000)
    assert lo < x.mean() < hi and hi - lo < 0.1


def test_kappa():
    assert cohen_kappa([1, 1, 0, 0], [1, 1, 0, 0]) == 1.0
    assert abs(cohen_kappa([1, 1, 0, 0], [1, 0, 1, 0])) < 1e-9


def test_wilson():
    lo, hi = wilson_ci(45, 50)
    assert 0.78 < lo < 0.85 and 0.95 < hi < 0.97


def test_spearman_brown_and_pearson():
    assert abs(spearman_brown(0.5) - 2 / 3) < 1e-9
    r, _ = pearson([1, 2, 3, 4], [2, 4, 6, 8.5])
    assert r > 0.99
