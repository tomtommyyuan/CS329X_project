"""Student readout on CPU with HuggingFaceTB/SmolLM2-135M (cached locally) and hand-made distributions."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from vcd.io import load_models
from vcd.schemas import Prompt, TeacherResponse
from vcd.student import readout as R
from vcd.teacher import profile as P

TINY = "HuggingFaceTB/SmolLM2-135M"
ROOT = Path(__file__).resolve().parents[1]
PILOT = ROOT / "data/prompts/pilot_prompts_v2.jsonl"  # absolute: the suite must pass from any cwd

os.environ.setdefault("HF_HUB_OFFLINE", "1")  # the model is in the local cache; never download during tests


@pytest.fixture(scope="module")
def tokenizer():
    from transformers import AutoTokenizer

    return AutoTokenizer.from_pretrained(TINY)


@pytest.fixture(scope="module")
def four_prompts() -> list[Prompt]:
    """One family, T1 and T5, both option orders -> 4 prompts."""
    ps = [p for p in load_models(PILOT, Prompt) if p.variant in ("T1", "T5")]
    fam = ps[0].family_id
    out = sorted([p for p in ps if p.family_id == fam], key=lambda p: p.prompt_id)
    assert len(out) == 4
    return out


def test_template_matches_contract():
    assert R.ASSISTANT_PREFIX == "Answer:"
    assert R.render_prompt("S", "U") == "S\n\nU\n\nAnswer:"
    assert not R.render_prompt("S", "U").endswith(" ")


def test_letter_token_ids_smollm(tokenizer):
    ids = R.letter_token_ids(tokenizer)
    assert ids == {"A": [330, 49], "B": [389, 50]}


def test_readout_rows_from_handmade_distribution(tokenizer, four_prompts):
    ids = R.letter_token_ids(tokenizer)
    vocab = len(tokenizer)
    q = np.zeros((4, vocab))
    q[0, 330] = 0.6; q[0, 389] = 0.3; q[0, 49] = 0.05; q[0, 50] = 0.05           # full mass on letters, A wins 0.65 / 0.35
    q[1, 389] = 0.8; q[1, 330] = 0.1; q[1, 100] = 0.1                             # B wins, mass 0.9 -> still "answer"
    q[2, 100] = 0.95; q[2, 330] = 0.03; q[2, 389] = 0.02                          # malformed, p_letters still defined
    q[3, 100] = 1.0                                                               # no letter mass at all
    rows = R.readout_rows(four_prompts, q, ids, tokenizer, "smollm2-135m.test_O_s1", TINY, "unit", answer_mass_min=0.9, n_prompt_tokens=[10, 11, 12, 13])
    assert all(isinstance(r, TeacherResponse) for r in rows)
    r0, r1, r2, r3 = rows
    assert r0.category == "answer" and r0.letter == "A" and r0.p_letters["A"] == pytest.approx(0.65) and r0.p_letters["B"] == pytest.approx(0.35)
    assert r0.usage["top1"] == tokenizer.decode([330]) == " A" and r0.usage["mass_AB"] == pytest.approx(1.0) and r0.usage["n_prompt_tokens"] == 10
    assert r0.choice_action == four_prompts[0].letter_to_action["A"] and r0.p_x == pytest.approx(0.65 if four_prompts[0].letter_to_action["A"] == "x" else 0.35)
    assert r1.category == "answer" and r1.letter == "B" and r1.p_letters["B"] == pytest.approx(0.8 / 0.9)
    assert r2.category == "malformed" and r2.letter == "A" and r2.usage["top1_id"] == 100 and r2.usage["mass_AB"] == pytest.approx(0.05)
    assert r3.category == "malformed" and r3.p_letters is None and r3.letter is None and r3.p_x is None
    assert all(r.teacher == "smollm2-135m.test_O_s1" and r.mode == "profile" and r.temperature == 0.0 for r in rows)
    assert r0.raw == "Answer: A"
    # sparse-dict input gives the same answer as the dense vector
    sparse = [{int(i): float(q[k, i]) for i in np.nonzero(q[k])[0]} for k in range(4)]
    rows2 = R.readout_rows(four_prompts, sparse, ids, tokenizer, "x.y_O_s1", TINY, "unit")
    assert [r.p_letters for r in rows2] == [r.p_letters for r in rows] and [r.category for r in rows2] == [r.category for r in rows]


def test_transformers_backend_end_to_end(four_prompts):
    rows, summary = R.run_readout(TINY, four_prompts, "smollm2-135m.base_B_s0", backend="transformers", batch_size=2, dtype="float32", answer_mass_min=0.0)
    assert len(rows) == 4 and summary["n"] == 4 and summary["backend"] == "transformers"
    for r in rows:
        TeacherResponse.model_validate(r.model_dump())
        assert r.p_letters is not None and sum(r.p_letters.values()) == pytest.approx(1.0)
        assert r.letter in ("A", "B") and r.choice_action in ("x", "y") and 0.0 <= r.p_x <= 1.0
        assert r.usage["backend"] == "transformers" and r.usage["n_prompt_tokens"] > 50 and 0 < r.usage["mass_AB"] <= 1
        assert r.raw.startswith("Answer:")
    assert {p.order for p in four_prompts} == {1, 2}
    # consumable by the existing profile pipeline: one symmetrized cell per (family, variant)
    prompts = {p.prompt_id: p for p in four_prompts}
    df = P.responses_to_frame(rows, prompts)
    sym = P.symmetrize(P.cell_estimates(df))
    assert len(sym) == 2 and sym["p_sym"].notna().all() and set(sym["variant"]) == {"T1", "T5"}
    # batch size must not change the numbers (right padding handled by the attention mask)
    rows_b1, _ = R.run_readout(TINY, four_prompts, "smollm2-135m.base_B_s0", backend="transformers", batch_size=1, dtype="float32", answer_mass_min=0.0)
    for a, b in zip(rows, rows_b1):
        assert a.p_letters["A"] == pytest.approx(b.p_letters["A"], abs=1e-4)
        assert a.usage["top1_id"] == b.usage["top1_id"]


def test_training_target_token_is_a_readout_letter_token(tokenizer, four_prompts):
    """Cross-module boundary: the first loss token of a training example is one of the ids the readout sums."""
    from vcd.train.data import render_prompt, render_target
    from vcd.train.sft import tokenize_example

    ids = R.letter_token_ids(tokenizer)
    for p in four_prompts:
        for letter in ("A", "B"):
            ex = tokenize_example(tokenizer, render_prompt(p.system, p.user), render_target(letter, "Because."), 1024)
            assert ex["input_ids"][ex["n_prompt_tokens"]] == ids[letter][0]  # " X" spelling, the one the target uses


def test_eval_script_cli_untrained_base_is_malformed(tmp_path):
    """scripts/12 end to end on the tiny base model: rows validate, and the untrained model is flagged malformed."""
    out = subprocess.run(
        [sys.executable, str(ROOT / "scripts/12_eval_student.py"), "--model", TINY, "--profile", "tiny", "--split", "pilot",
         "--limit", "8", "--backend", "transformers", "--out", str(tmp_path)],
        cwd=ROOT, env={**os.environ, "HF_HUB_OFFLINE": "1"}, capture_output=True, text=True, check=True,
    ).stdout
    assert "run_id=smollm2-135m.base_B_s0" in out
    rows = load_models(tmp_path / "pilot_responses.jsonl", TeacherResponse)
    assert len(rows) == 8 and all(r.teacher == "smollm2-135m.base_B_s0" and r.mode == "profile" for r in rows)
    summary = json.loads((tmp_path / "pilot_readout_summary.json").read_text())
    assert summary["n"] == 8 and summary["category_rates"].get("malformed", 0) > 0.5, "the untrained 135M model copies the placeholder, not a letter"
    assert all(r.category == "malformed" and r.usage["mass_AB"] < 0.9 for r in rows if r.usage["top1"] != " A" and r.usage["top1"] != " B")
    # a second call without --overwrite refuses
    res = subprocess.run([sys.executable, str(ROOT / "scripts/12_eval_student.py"), "--model", TINY, "--profile", "tiny", "--split", "pilot", "--limit", "8", "--out", str(tmp_path)],
                         cwd=ROOT, env={**os.environ, "HF_HUB_OFFLINE": "1"}, capture_output=True, text=True)
    assert res.returncode != 0 and "exists" in (res.stderr + res.stdout)


def test_vllm_matches_transformers_if_available(four_prompts):
    pytest.importorskip("vllm")
    import torch

    if not torch.cuda.is_available():
        pytest.skip("vLLM backend needs a GPU")
    rows_t, _ = R.run_readout(TINY, four_prompts, "smollm2-135m.base_B_s0", backend="transformers", dtype="float32", answer_mass_min=0.0)
    rows_v, _ = R.run_readout(TINY, four_prompts, "smollm2-135m.base_B_s0", backend="vllm", dtype="float32", answer_mass_min=0.0)
    for a, b in zip(rows_t, rows_v):
        assert abs(a.p_letters["A"] - b.p_letters["A"]) < 1e-3
