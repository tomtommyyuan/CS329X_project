"""Student readout validation (E0.7 for students): sampled-letter parsing, binomial noise floor, summary / gate."""

from __future__ import annotations

import math

import numpy as np

from vcd.student.readout_check import binomial_noise_floor, compare_readouts, sample_letter_freq, summarize_check


def test_sample_letter_freq_parses_after_the_prefix():
    s = sample_letter_freq([" A\nRationale: safer.", " B\nRationale: kinder.", " <A or B>", "A", " (B)", " The"])
    assert s == {"n_samples": 6, "n_answer": 4, "freq_A": 0.5}
    none = sample_letter_freq([" The", " <A or B>"])
    assert none["n_answer"] == 0 and math.isnan(none["freq_A"])


def test_binomial_noise_floor_known_values():
    f = binomial_noise_floor([0.5, 0.9, 0.0, 1.0, 0.5], [20, 20, 20, 20, 0])
    assert abs(f[0] - 0.088099) < 1e-5 and abs(f[1] - 0.051332) < 1e-5
    assert f[2] == 0.0 and f[3] == 0.0 and math.isnan(f[4])
    assert np.allclose(binomial_noise_floor([0.5, 0.5], 20), f[0]), "scalar k broadcasts"


def test_compare_and_summarize_gate():
    p_logit = {"a": 1.0, "b": 0.0, "c": 0.5, "d": None}
    samples = {"a": [" A"] * 20, "b": [" B"] * 20, "c": [" A"] * 10 + [" B"] * 10, "d": [" A"] * 20}
    df = compare_readouts(p_logit, samples, {"a": {"variant": "T1"}})
    assert list(df["prompt_id"]) == ["a", "b", "c", "d"] and df.loc[0, "variant"] == "T1"
    assert np.allclose(df["abs_diff"].iloc[:3], 0.0) and math.isnan(df.loc[3, "p_logit_A"])
    s = summarize_check(df, diff_max=0.05)
    assert s["n"] == 3 and s["mean_abs_diff"] == 0.0 and s["gate"] == "ok" and s["share_no_logit"] == 0.25
    assert abs(s["expected_abs_diff_from_sampling_noise"] - 0.088099 / 3) < 1e-5
    assert s["share_samples_with_letter"] == 1.0 and s["share_prompts_no_sampled_letter"] == 0.0
    off = compare_readouts({"a": 0.9}, {"a": [" B"] * 20})
    assert summarize_check(off, diff_max=0.05)["gate"] == "FAIL"
