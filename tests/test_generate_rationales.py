"""scripts/25_generate_rationales.py: parsing units and a CPU smoke run with HuggingFaceTB/SmolLM2-135M (cached locally).

The untrained 135M model copies the "<A or B>" placeholder and then starts a new "Answer:" line, which exercises the
second-"Answer:" stop; the letter parse is checked on hand-written generations (a trained student writes " A\\nRationale: ...").
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from vcd.analysis import lexical_provenance as LP
from vcd.io import load_models, read_jsonl
from vcd.schemas import Prompt

TINY = "HuggingFaceTB/SmolLM2-135M"
ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/25_generate_rationales.py"
PILOT = ROOT / "data/prompts/pilot_prompts_v2.jsonl"

os.environ.setdefault("HF_HUB_OFFLINE", "1")  # the model is in the local cache; never download during tests


def _load_script():
    spec = importlib.util.spec_from_file_location("gen25", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_letter_and_rationale_parse():
    assert LP.split_generation("A\nRationale: Because it is kind.") == ("answer", "A", "Because it is kind.")
    assert LP.split_generation(" B\nRationale: Telling the truth matters.\n") == ("answer", "B", "Telling the truth matters.")
    assert LP.split_generation(" A\nRationale:  spaced  ") == ("answer", "A", "spaced")
    assert LP.split_generation(" (B)\nrationale: lower-case marker") == ("answer", "B", "lower-case marker")
    assert LP.split_generation("B. It is safer.\nMore text.") == ("answer", "B", "More text.")  # no marker: the text after the letter line
    assert LP.split_generation("I cannot choose between these.") == ("refusal", None, "")
    assert LP.split_generation(" <A or B>") == ("malformed", None, "")
    assert LP.split_generation("\n\n") == ("malformed", None, "")
    assert LP.split_generation("Rationale: no letter line") == ("malformed", None, "no letter line")
    # a second "Answer:" line is cut; a continuation starting with "Answer:" is not
    assert LP.truncate_at_second_answer(" A\nRationale: Fine.\n\nAnswer: B\nRationale: other") == (" A\nRationale: Fine.", True)
    assert LP.truncate_at_second_answer(" A\nRationale: Fine.") == (" A\nRationale: Fine.", False)
    assert LP.truncate_at_second_answer("Answer: A\nRationale: ok\n") == ("Answer: A\nRationale: ok", False)
    assert LP.truncate_at_second_answer(" <A or B>\n\nAnswer: <A or B>") == (" <A or B>", True)


def test_select_prompts_and_summary():
    mod = _load_script()
    prompts = load_models(PILOT, Prompt)
    sel = mod.select_prompts(prompts, ["T1", "T3", "T5", "T6"])
    assert sel and all(p.variant in ("T1", "T3", "T5", "T6") for p in sel) and {p.order for p in sel} == {1, 2}
    assert [p.prompt_id for p in mod.select_prompts(prompts, ["T1"], 3)] == [p.prompt_id for p in prompts if p.variant == "T1"][:3]
    rows = [dict(prompt_id="x", run_id="r", text=" A\nRationale: ok", letter="A", n_new_tokens=5, stop_reason="eos"),
            dict(prompt_id="y", run_id="r", text=" <A or B>", letter=None, n_new_tokens=9, stop_reason="answer_line")]
    s = mod.summarize(rows)
    assert s["n"] == 2 and s["letter_rate"] == 0.5 and s["mean_new_tokens"] == 7 and s["stop_reasons"] == {"eos": 1, "answer_line": 1} and s["rationale_rate"] == 0.5 and s["letter_counts"] == {"A": 1, "None": 1}


def test_cli_tiny_model_writes_generations(tmp_path):
    """4 pilot prompts on CPU with the tiny profile: row schema, a bounded token count, the summary, and the overwrite guard."""
    cmd = [sys.executable, str(SCRIPT), "--model", TINY, "--profile", "tiny", "--split", "pilot", "--limit", "4", "--max-new-tokens", "12", "--out", str(tmp_path)]
    res = subprocess.run(cmd, cwd=ROOT, env={**os.environ, "HF_HUB_OFFLINE": "1"}, capture_output=True, text=True)
    assert res.returncode == 0, res.stderr
    assert "run_id=smollm2-135m.base_B_s0" in res.stdout and "dtype=float32" in res.stdout and "device=cpu" in res.stdout
    rows = list(read_jsonl(tmp_path / "pilot_generations.jsonl"))
    assert len(rows) == 4
    prompts = [p.prompt_id for p in load_models(PILOT, Prompt) if p.variant in ("T1", "T3", "T5", "T6")][:4]
    assert [r["prompt_id"] for r in rows] == prompts
    for r in rows:
        assert set(LP.GEN_FIELDS) <= set(r) and set(r) == {*LP.GEN_FIELDS, "stop_reason"}
        assert r["run_id"] == "smollm2-135m.base_B_s0" and isinstance(r["text"], str) and r["letter"] in ("A", "B", None)
        assert 1 <= r["n_new_tokens"] <= 12 and r["stop_reason"] in ("eos", "answer_line", "max_new_tokens")
        assert "\nAnswer:" not in r["text"] and "<|endoftext|>" not in r["text"]  # the second-Answer tail and special tokens are gone
        assert LP.split_generation(r["text"])[1] == r["letter"]
    summary = json.loads((tmp_path / "pilot_generations_summary.json").read_text(encoding="utf-8"))
    assert summary["n"] == 4 and summary["max_new_tokens"] == 12 and summary["dtype"] == "float32" and summary["batch_size"] == 4 and summary["decoding"] == "greedy"
    assert summary["prompts_sha256"] and summary["variants"] == ["T1", "T3", "T5", "T6"] and sum(summary["stop_reasons"].values()) == 4
    # a second call without --overwrite refuses; with it, the rows are reproduced (greedy decoding)
    again = subprocess.run(cmd, cwd=ROOT, env={**os.environ, "HF_HUB_OFFLINE": "1"}, capture_output=True, text=True)
    assert again.returncode != 0 and "exists" in (again.stderr + again.stdout)
    redo = subprocess.run(cmd + ["--overwrite", "--batch-size", "2"], cwd=ROOT, env={**os.environ, "HF_HUB_OFFLINE": "1"}, capture_output=True, text=True)
    assert redo.returncode == 0, redo.stderr
    assert [r["text"] for r in read_jsonl(tmp_path / "pilot_generations.jsonl")] == [r["text"] for r in rows]


def test_generator_stops_at_second_answer_line_on_cpu():
    """The stopping criterion ends a sequence as soon as the continuation starts a new 'Answer:' line; the kept text is cut before it."""
    pytest.importorskip("torch")
    mod = _load_script()
    gen = mod.Generator(TINY, dtype="float32", device="cpu")
    prompts = [p for p in load_models(PILOT, Prompt) if p.variant == "T1"][:2]
    outs = gen.generate([mod.render_prompt(p.system, p.user) for p in prompts], max_new_tokens=40)
    assert len(outs) == 2
    for o in outs:
        assert set(o) == {"text", "n_new_tokens", "stop_reason"} and 1 <= o["n_new_tokens"] <= 40
        if o["stop_reason"] == "answer_line":
            assert o["n_new_tokens"] < 40 and "\nAnswer:" not in o["text"]  # stopped early, tail removed
