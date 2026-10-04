"""Tests for the SFT template and the O / F / C / R training-file builders (docs/05 §8, row 1).

Data: pilot prompts + gpt4o teacher_v2 demos + rewrites_v9/gpt4o (the rewrites cover pilot items only).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from vcd.io import load_models, read_jsonl, write_jsonl
from vcd.schemas import Prompt, TeacherResponse
from vcd.train.data import (
    ASSISTANT_PREFIX,
    RANDOM_RATIONALE,
    TRAIN_VARIANTS,
    build_random_examples,
    build_sft_examples,
    canonical_target,
    family_permutation,
    item_order_choice,
    kept_rewrites,
    load_sft_rows,
    load_train_yaml,
    order_examples,
    pair_versions,
    prompt_ids_sha256,
    render_prompt,
    render_target,
    select_demo_targets,
    summarize_examples,
    validate_sft_row,
    version_examples,
)

ROOT = Path(__file__).resolve().parents[1]
PROMPTS = ROOT / "data/prompts/pilot_prompts_v2.jsonl"
DEMOS = ROOT / "data/teacher_v2/gpt4o_demo.jsonl"
REWRITES = ROOT / "data/rewrites_v9/gpt4o/rewrites.jsonl"
SCRIPT = ROOT / "scripts/10_build_sft_data.py"


@pytest.fixture(scope="module")
def pilot():
    prompts = {p.prompt_id: p for p in load_models(PROMPTS, Prompt)}
    demos = load_models(DEMOS, TeacherResponse)
    rewrites = list(read_jsonl(REWRITES))
    return prompts, demos, rewrites


# ----------------------------------------------------------------------------- template


def test_template_strings():
    tp = render_prompt("You are a helpful assistant.", "Situation.\n\nOptions:\nA. x\nB. y")
    assert tp == "You are a helpful assistant.\n\nSituation.\n\nOptions:\nA. x\nB. y\n\nAnswer:"
    assert tp.endswith(ASSISTANT_PREFIX) and not tp.endswith(" ")
    assert render_target("B", "  Because. ") == " B\nRationale: Because."


def test_canonical_target_strips_teacher_noise():
    assert canonical_target("Answer: B  \nRationale: It is safer.  ") == " B\nRationale: It is safer."
    assert canonical_target("**Answer: A**\nRATIONALE: Keep your word.") == " A\nRationale: Keep your word."
    assert canonical_target("Answer: A") is None  # no rationale line
    assert canonical_target("Answer: A\nRationale:   ") is None  # empty rationale
    assert canonical_target("I cannot choose between these options.") is None
    assert canonical_target(None) is None and canonical_target("") is None


def test_tokenizer_boundary_smollm2():
    """tok(prompt + target) == tok(prompt) + tok(target) and the first target token is a single letter token."""
    os.environ.setdefault("HF_HUB_OFFLINE", "1")
    transformers = pytest.importorskip("transformers")
    try:
        tok = transformers.AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M")
    except Exception as e:  # not cached on this machine
        pytest.skip(f"SmolLM2 tokenizer unavailable: {e}")
    tp = render_prompt("You are a helpful assistant.", "Pick one.\n\nOptions:\nA. x\nB. y")
    for letter in ("A", "B"):
        tt = render_target(letter, "Because it is better.")
        ids_p = tok(tp, add_special_tokens=False)["input_ids"]
        ids_t = tok(tt, add_special_tokens=False)["input_ids"]
        assert tok(tp + tt, add_special_tokens=False)["input_ids"] == ids_p + ids_t
        assert tok.decode([ids_t[0]]) == f" {letter}"
        assert len(tok(f" {letter}", add_special_tokens=False)["input_ids"]) == 1


# ----------------------------------------------------------------------------- filters and ordering


def test_item_order_choice_is_deterministic_and_mixed():
    picks = [item_order_choice(f"dd_{i:04d}", "T1") for i in range(200)]
    assert picks == [item_order_choice(f"dd_{i:04d}", "T1") for i in range(200)]
    assert set(picks) == {1, 2} and 60 < picks.count(1) < 140
    assert item_order_choice("dd_0001", "T1") != item_order_choice("dd_0001", "T1", order_seed=7) or item_order_choice("dd_0002", "T1") != item_order_choice("dd_0002", "T1", order_seed=7)


def test_select_demo_targets_stable_one(pilot):
    prompts, demos, _ = pilot
    kept, counts = select_demo_targets(prompts, demos)
    assert counts["n_prompts_variant"] == 800 and counts["n_demos_unmatched"] == 240  # T0 / VC dropped
    assert counts["n_items_stable"] + counts["n_dropped_order_unstable"] == counts["n_items_answered"] == 400
    assert len(kept) == counts["n_items_stable"] == counts["n_selected_O"]
    items = Counter((prompts[pid].family_id, prompts[pid].variant) for pid in kept)
    assert set(items.values()) == {1}  # exactly one order per kept item
    assert {prompts[pid].variant for pid in kept} <= set(TRAIN_VARIANTS)
    # every kept prompt belongs to an item whose two orders chose the same action
    by_pid = {d.prompt_id: d for d in demos}
    for pid in kept:
        p = prompts[pid]
        other = f"{p.family_id}.{p.variant}.o{3 - p.order}"
        assert by_pid[pid].choice_action == by_pid[other].choice_action
        assert p.order == item_order_choice(p.family_id, p.variant)
        assert kept[pid][1] == by_pid[pid].letter
    # the two other policies keep supersets
    both_stable, _ = select_demo_targets(prompts, demos, order_policy="stable_both")
    both, c_both = select_demo_targets(prompts, demos, order_policy="both")
    assert len(both_stable) == 2 * len(kept) and set(kept) <= set(both_stable) <= set(both)
    assert len(both) == 800 and c_both["n_dropped_order_unstable"] == 0
    with pytest.raises(ValueError):
        select_demo_targets(prompts, demos, order_policy="random")


def test_select_demo_targets_counts_drops():
    p1 = Prompt(prompt_id="f1.T1.o1", family_id="f1", variant="T1", order=1, letter_to_action={"A": "x", "B": "y"}, system="s", user="u")
    p2 = Prompt(prompt_id="f1.T1.o2", family_id="f1", variant="T1", order=2, letter_to_action={"A": "y", "B": "x"}, system="s", user="u")
    p3 = Prompt(prompt_id="f2.T3.o1", family_id="f2", variant="T3", order=1, letter_to_action={"A": "x", "B": "y"}, system="s", user="u")
    p4 = Prompt(prompt_id="f2.T3.o2", family_id="f2", variant="T3", order=2, letter_to_action={"A": "y", "B": "x"}, system="s", user="u")
    prompts = {p.prompt_id: p for p in (p1, p2, p3, p4)}

    def demo(pid, raw, category="answer"):
        cat, letter = ("answer", raw[8]) if category == "answer" else (category, None)
        return TeacherResponse(prompt_id=pid, teacher="t", model="m", mode="demo", temperature=0.0, raw=raw, category=cat, letter=letter)

    demos = [
        demo("f1.T1.o1", "Answer: A\nRationale: r"), demo("f1.T1.o2", "Answer: B\nRationale: r"),  # same action x -> stable
        demo("f2.T3.o1", "Answer: A\nRationale: r"), demo("f2.T3.o2", "Answer: A\nRationale: r"),  # x vs y -> unstable
        demo("f2.T3.o2", "Answer: B\nRationale: dup"),  # duplicate row ignored
    ]
    kept, c = select_demo_targets(prompts, demos)
    assert set(kept) == {f"f1.T1.o{item_order_choice('f1', 'T1')}"}
    assert c["n_dropped_order_unstable"] == 1 and c["n_demos_duplicate"] == 1 and c["order_stable_rate"] == 0.5
    demos2 = [demo("f1.T1.o1", "I refuse.", "refusal"), demo("f1.T1.o2", "Answer: B"), demo("f2.T3.o1", "Answer: A\nRationale: r")]
    kept2, c2 = select_demo_targets(prompts, demos2)
    assert kept2 == {} and c2["n_dropped_category"] == 1 and c2["n_dropped_format"] == 1 and c2["n_missing_demo"] == 1


def test_paired_versions_share_prompt_set_letters_and_family_order(pilot):
    prompts, demos, rewrites = pilot
    o_targets, _ = select_demo_targets(prompts, demos)
    by_version, counts = {}, {}
    for v in ("O", "F", "C"):
        by_version[v], counts[v] = version_examples(prompts, o_targets, v, "gpt4o", rewrites)
    assert len(by_version["O"]) == len(o_targets) > len(by_version["F"]) > 0
    assert counts["F"]["n_dropped_no_rewrite"] + len(by_version["F"]) == len(o_targets)
    paired = pair_versions(by_version)
    ids = {v: [e["prompt_id"] for e in exs] for v, exs in paired.items()}
    assert set(ids["O"]) == set(ids["F"]) == set(ids["C"]) and len(ids["O"]) == len(set(ids["O"])) > 50
    assert prompt_ids_sha256(paired["O"]) == prompt_ids_sha256(paired["F"]) == prompt_ids_sha256(paired["C"])
    rank = family_permutation((p.family_id for p in prompts.values()), seed=1)
    ordered = {v: order_examples(exs, rank) for v, exs in paired.items()}
    for v in ("F", "C"):
        for eo, ev in zip(ordered["O"], ordered[v]):
            assert eo["prompt_id"] == ev["prompt_id"] and eo["letter"] == ev["letter"] and eo["text_prompt"] == ev["text_prompt"]
            assert ev["text_target"].startswith(f" {eo['letter']}\nRationale: ")
            assert ev["version"] == v and eo["version"] == "O"
        assert any(eo["text_target"] != ev["text_target"] for eo, ev in zip(ordered["O"], ordered[v]))
    # family blocks are contiguous and follow the permutation; inside a family T1 < T3 < T5 < T6
    fams = [e["family_id"] for e in ordered["O"]]
    first_seen = list(dict.fromkeys(fams))
    assert [rank[f] for f in first_seen] == sorted(rank[f] for f in first_seen)
    assert len(first_seen) == len(set(fams))
    for i in range(1, len(ordered["O"])):
        a, b = ordered["O"][i - 1], ordered["O"][i]
        if a["family_id"] == b["family_id"]:
            assert TRAIN_VARIANTS.index(a["variant"]) <= TRAIN_VARIANTS.index(b["variant"])
    # another seed: same set, different order; same seed: identical order
    other = order_examples(paired["O"], family_permutation((p.family_id for p in prompts.values()), seed=2))
    assert [e["prompt_id"] for e in other] != ids["O"] and set(e["prompt_id"] for e in other) == set(ids["O"])
    assert [e["prompt_id"] for e in order_examples(paired["O"], family_permutation((p.family_id for p in prompts.values()), seed=1))] == [e["prompt_id"] for e in ordered["O"]]


def test_kept_rewrites_takes_last_kept_attempt_and_letter_mismatch_is_dropped():
    rows = [
        {"prompt_id": "p", "version": "F", "attempt": 0, "kept": False, "text": "Answer: A\nRationale: bad"},
        {"prompt_id": "p", "version": "F", "attempt": 1, "kept": True, "text": "Answer: A\nRationale: first kept"},
        {"prompt_id": "p", "version": "F", "attempt": 2, "kept": True, "text": "Answer: A\nRationale: last kept"},
        {"prompt_id": "p", "version": "C", "attempt": 0, "kept": True, "text": "Answer: B\nRationale: wrong letter"},
        {"prompt_id": "q", "version": "C", "attempt": 0, "kept": True, "text": "no answer here"},
    ]
    assert kept_rewrites(rows, "F") == {"p": "Answer: A\nRationale: last kept"}
    p = Prompt(prompt_id="p", family_id="f", variant="T1", order=1, letter_to_action={"A": "x", "B": "y"}, system="s", user="u")
    q = Prompt(prompt_id="q", family_id="g", variant="T1", order=1, letter_to_action={"A": "x", "B": "y"}, system="s", user="u")
    o = {"p": " A\nRationale: orig", "q": " A\nRationale: orig"}
    f, cf = version_examples({"p": p, "q": q}, o, "F", "t", rows)
    assert [e["text_target"] for e in f] == [" A\nRationale: last kept"] and cf["n_dropped_no_rewrite"] == 1
    c, cc = version_examples({"p": p, "q": q}, o, "C", "t", rows)
    assert c == [] and cc["n_dropped_choice_mismatch"] == 1 and cc["n_dropped_rewrite_format"] == 1
    with pytest.raises(ValueError):
        version_examples({"p": p}, o, "F", "t", None)


def test_build_sft_examples_wrapper(pilot):
    prompts, demos, rewrites = pilot
    o1, c1 = build_sft_examples(prompts, demos, version="O", teacher="gpt4o", seed=1)
    o2, _ = build_sft_examples(list(prompts.values()), demos, version="O", teacher="gpt4o", seed=1)
    assert [e["prompt_id"] for e in o1] == [e["prompt_id"] for e in o2] and c1["n_examples"] == len(o1) == c1["n_selected_O"]
    for e in o1:
        validate_sft_row(e)
    f1, cf = build_sft_examples(prompts, demos, rewrites, version="F", teacher="gpt4o", seed=1)
    assert 0 < len(f1) < len(o1) and cf["n_dropped_no_rewrite"] > 0
    # the worked example of docs/05 §1.2: target = teacher raw minus the two trailing spaces after the letter
    by_pid = {d.prompt_id: d for d in demos}
    e = o1[0]
    raw = by_pid[e["prompt_id"]].raw
    assert raw.startswith(f"Answer: {e['letter']}") and e["text_target"] == " " + raw.replace("  \n", "\n", 1).split("Answer: ", 1)[1].strip()


# ----------------------------------------------------------------------------- random-label control


def test_random_examples_balanced_and_deterministic(pilot):
    prompts, demos, _ = pilot
    ref, _ = build_sft_examples(prompts, demos, version="O", teacher="gpt4o", seed=3)
    r = build_random_examples(ref, seed=3)
    assert [e["prompt_id"] for e in r] == [e["prompt_id"] for e in ref]
    assert all(e["teacher"] == "random" and e["version"] == "R" and e["text_prompt"] == o["text_prompt"] for e, o in zip(r, ref))
    assert all(e["text_target"] == f" {e['letter']}\nRationale: {RANDOM_RATIONALE}" for e in r)
    for e in r:
        validate_sft_row(e)
    per_family = {}
    for e in r:
        per_family.setdefault(e["family_id"], Counter())[e["letter"]] += 1
    assert all(abs(c["A"] - c["B"]) <= 1 for c in per_family.values())
    total = Counter(e["letter"] for e in r)
    assert abs(total["A"] - total["B"]) <= len(per_family)
    assert sum(e["letter"] != o["letter"] for e, o in zip(r, ref)) > 0.25 * len(r)  # not a copy of the teacher
    assert build_random_examples(ref, seed=3) == r and [e["letter"] for e in build_random_examples(ref, seed=4)] != [e["letter"] for e in r]


# ----------------------------------------------------------------------------- file I/O and the script


def test_load_sft_rows_validates(tmp_path):
    good = {"prompt_id": "f.T1.o1", "family_id": "f", "variant": "T1", "order": 1, "teacher": "t", "version": "O",
            "text_prompt": render_prompt("s", "u"), "text_target": render_target("A", "r"), "letter": "A"}
    path = tmp_path / "x.jsonl"
    write_jsonl(path, [good])
    assert load_sft_rows(path) == [good]
    for bad in ({**good, "text_target": "A\nRationale: r"}, {**good, "text_prompt": good["text_prompt"] + " "}, {**good, "letter": "B"},
                {**good, "version": "X"}, {**good, "text_target": good["text_target"] + "\n"}, {k: v for k, v in good.items() if k != "family_id"}):
        write_jsonl(path, [bad])
        with pytest.raises(ValueError):
            load_sft_rows(path)
    s = summarize_examples([good])
    assert s["n_examples"] == 1 and s["letter_counts"] == {"A": 1} and s["variant_counts"] == {"T1": 1}


def _run(*args):
    env = {**os.environ, "HF_HUB_OFFLINE": "1"}
    return subprocess.run([sys.executable, str(SCRIPT), *map(str, args)], cwd=ROOT, env=env, capture_output=True, text=True, check=True).stdout


def test_script_end_to_end(tmp_path):
    out = _run("--teacher", "gpt4o", "--versions", "O,F,C", "--seeds", "1,2", "--prompts", PROMPTS, "--demos", DEMOS, "--out-dir", tmp_path)
    assert "paired across" in out
    rows = {name: load_sft_rows(tmp_path / f"gpt4o_{name}.jsonl") for name in ("O_s1", "O_s2", "F_s1", "C_s1")}
    assert len({len(r) for r in rows.values()}) == 1 and len(rows["O_s1"]) > 50
    assert [e["prompt_id"] for e in rows["O_s1"]] == [e["prompt_id"] for e in rows["F_s1"]] == [e["prompt_id"] for e in rows["C_s1"]]
    assert sorted(json.dumps(e, sort_keys=True) for e in rows["O_s1"]) == sorted(json.dumps(e, sort_keys=True) for e in rows["O_s2"])
    assert [e["prompt_id"] for e in rows["O_s1"]] != [e["prompt_id"] for e in rows["O_s2"]]
    metas = {name: json.loads((tmp_path / f"gpt4o_{name}.meta.json").read_text()) for name in rows}
    for name, m in metas.items():
        for k in ("sha256", "prompt_ids_sha256", "n_examples", "n_families", "n_dropped_order_unstable", "order_stable_rate", "paired",
                  "seed", "variant_counts", "prompts_path", "demos_path", "built_at"):
            assert k in m, (name, k)
        assert m["paired"] is True and m["n_examples"] == len(rows[name])
    assert len({m["prompt_ids_sha256"] for m in metas.values()}) == 1
    assert metas["O_s1"]["sha256"] != metas["O_s2"]["sha256"] and metas["F_s1"]["n_dropped_no_rewrite"] > 0
    # random-label control from the O_s1 reference
    out = _run("--random-label", "--ref-teacher", "gpt4o", "--seeds", "1", "--out-dir", tmp_path)
    r = load_sft_rows(tmp_path / "random_R_s1.jsonl")
    assert [e["prompt_id"] for e in r] == [e["prompt_id"] for e in rows["O_s1"]] and {e["teacher"] for e in r} == {"random"}
    rmeta = json.loads((tmp_path / "random_R_s1.meta.json").read_text())
    assert rmeta["ref_prompt_ids_sha256"] == metas["O_s1"]["prompt_ids_sha256"] == rmeta["prompt_ids_sha256"]
    # unpaired O alone keeps the full stable set; --list-prompt-ids writes the same set
    out = _run("--teacher", "gpt4o", "--versions", "O", "--seeds", "1", "--prompts", PROMPTS, "--demos", DEMOS, "--out-dir", tmp_path / "solo")
    solo = load_sft_rows(tmp_path / "solo/gpt4o_O_s1.jsonl")
    assert len(solo) > len(rows["O_s1"])
    _run("--teacher", "gpt4o", "--list-prompt-ids", "--prompts", PROMPTS, "--demos", DEMOS, "--out-dir", tmp_path / "solo")
    listed = (tmp_path / "solo/gpt4o_O_prompt_ids.txt").read_text().split()
    assert sorted(listed) == sorted(e["prompt_id"] for e in solo)
    # R without its reference file fails loudly
    with pytest.raises(subprocess.CalledProcessError):
        _run("--random-label", "--ref-teacher", "claude46", "--seeds", "9", "--out-dir", tmp_path)


def test_script_refuses_empty_versions_and_silent_overwrite(tmp_path):
    """A paired build whose rewrites do not cover the prompts must not write 0-row files over a good O file."""
    _run("--teacher", "gpt4o", "--versions", "O", "--seeds", "1", "--prompts", PROMPTS, "--demos", DEMOS, "--out-dir", tmp_path)
    good = (tmp_path / "gpt4o_O_s1.jsonl").read_bytes()
    assert good
    empty_rewrites = tmp_path / "rw" / "gpt4o"
    empty_rewrites.mkdir(parents=True)
    (empty_rewrites / "rewrites.jsonl").write_text("")
    with pytest.raises(subprocess.CalledProcessError) as e:
        _run("--teacher", "gpt4o", "--versions", "O,F", "--seeds", "1", "--prompts", PROMPTS, "--demos", DEMOS, "--rewrites-dir", tmp_path / "rw", "--out-dir", tmp_path)
    assert "0 examples" in e.value.stderr and not (tmp_path / "gpt4o_F_s1.jsonl").exists()
    assert (tmp_path / "gpt4o_O_s1.jsonl").read_bytes() == good, "the existing O file must be untouched"
    # same build again: refused without --overwrite, allowed with it
    with pytest.raises(subprocess.CalledProcessError) as e:
        _run("--teacher", "gpt4o", "--versions", "O", "--seeds", "1", "--prompts", PROMPTS, "--demos", DEMOS, "--out-dir", tmp_path)
    assert "--overwrite" in e.value.stderr
    _run("--teacher", "gpt4o", "--versions", "O", "--seeds", "1", "--prompts", PROMPTS, "--demos", DEMOS, "--out-dir", tmp_path, "--overwrite")
    assert (tmp_path / "gpt4o_O_s1.jsonl").read_bytes() == good


def test_load_train_yaml_has_no_env_side_effect(monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    cfg = load_train_yaml("configs/train.yaml")
    assert cfg["paths"]["sft_dir"].is_absolute() and cfg["profile"] == "default" and "tiny" not in cfg
    assert os.environ.get("OPENAI_API_KEY") is None, "the training stack must not load .env"
    tiny = load_train_yaml("configs/train.yaml", "tiny")
    assert tiny["student_model_short"] == "smollm2-135m" and tiny["train"]["num_epochs"] == 3
    with pytest.raises(ValueError):
        load_train_yaml("configs/train.yaml", "nope")
