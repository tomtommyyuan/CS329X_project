"""E0.7 readout validation for students (tasks/e1_plan.md §2 step 2b): first-token p(A) vs sampled letters.

The student readout (`vcd.student.readout`, scripts/12) reads the next-token distribution right after the
assistant prefix "Answer:" and renormalizes P(" A") + P("A") against P(" B") + P("B"). This module compares that
number with the letter frequency of k sampled continuations of the SAME prompt string (temperature 1, a few
tokens), each parsed with `vcd.teacher.parse.parse_answer` as E0.7 does for teachers
(`vcd.readout.logit_vs_sample`). The gate is `mean_abs_diff <= gates.readout_diff_max` (0.05, configs/e0.yaml).

With k samples the frequency itself is noisy: even a perfect readout has E|freq - p| > 0 (about 0.09 at p = 0.5
for k = 20). `binomial_noise_floor` gives that expectation so the reported difference can be read against it;
it does not change the gate.

Pure functions only; the vLLM sampling lives in scripts/14_readout_check.py.
"""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from vcd.readout.logit_vs_sample import summarize as e0_summarize
from vcd.teacher.parse import parse_answer
from vcd.train.data import ASSISTANT_PREFIX


def sample_letter_freq(completions: Sequence[str]) -> dict[str, float | int]:
    """k sampled continuations of a prompt ending in "Answer:" -> {n_samples, n_answer, freq_A}.

    Each continuation is parsed as `"Answer:" + text`, so " B\\nRationale: ..." counts as B. Samples without a
    letter do not enter the frequency; freq_A is NaN when none has one.
    """
    letters = [parse_answer(ASSISTANT_PREFIX + c)[1] for c in completions]
    n_ans = sum(letter is not None for letter in letters)
    freq = sum(letter == "A" for letter in letters) / n_ans if n_ans else float("nan")
    return {"n_samples": len(letters), "n_answer": n_ans, "freq_A": freq}


def binomial_noise_floor(p: Sequence[float] | np.ndarray, k: Sequence[int] | np.ndarray | int) -> np.ndarray:
    """E|X/k - p| for X ~ Binomial(k, p), elementwise: the mean |diff| that sampling noise alone produces."""
    from scipy.stats import binom

    p = np.asarray(p, dtype=float)
    k = np.broadcast_to(np.asarray(k, dtype=int), p.shape)
    out = np.full(p.shape, np.nan)
    for i, (pi, ki) in enumerate(zip(p, k)):
        if ki > 0 and np.isfinite(pi):
            x = np.arange(ki + 1)
            out[i] = float(np.sum(binom.pmf(x, ki, pi) * np.abs(x / ki - pi)))
    return out


def compare_readouts(p_logit_a: Mapping[str, float | None], samples: Mapping[str, Sequence[str]], meta: Mapping[str, dict] | None = None) -> pd.DataFrame:
    """One row per prompt_id in `samples`: p_logit_A (None -> NaN), n_answer, freq_A, abs_diff, noise_floor.

    `meta` adds per-prompt columns (variant, order, mass_AB, ...) when given.
    """
    rows = []
    for pid, comps in samples.items():
        p = p_logit_a.get(pid)
        s = sample_letter_freq(comps)
        rows.append({"prompt_id": pid, **(dict(meta[pid]) if meta and pid in meta else {}),
                     "p_logit_A": float(p) if p is not None else np.nan, **s})
    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["abs_diff"] = (df["p_logit_A"] - df["freq_A"]).abs()
    df["noise_floor"] = binomial_noise_floor(df["p_logit_A"].to_numpy(), df["n_answer"].to_numpy())
    return df


def summarize_check(df: pd.DataFrame, diff_max: float = 0.05) -> dict:
    """E0.7 summary (n, mean_abs_diff, pearson, share_no_logit) + the noise floor, the share of samples with a
    letter, and the gate verdict against `diff_max`."""
    s = e0_summarize(df)
    d = df.dropna(subset=["p_logit_A", "freq_A"])
    s["expected_abs_diff_from_sampling_noise"] = float(d["noise_floor"].mean()) if len(d) else float("nan")
    s["share_samples_with_letter"] = float(df["n_answer"].sum() / df["n_samples"].sum()) if len(df) and df["n_samples"].sum() else float("nan")
    s["share_prompts_no_sampled_letter"] = float((df["n_answer"] == 0).mean()) if len(df) else float("nan")
    s["diff_max"] = diff_max
    s["gate"] = "ok" if s["mean_abs_diff"] <= diff_max else "FAIL"
    return s
