"""Revised E1 / E2 rules (frozen on dev 2026-10-05, corrected the same day): base-prior covariate, partial-rho inheritance,
run-level assignment nulls (descriptive) with the teacher-level exact p, the family-level secondary statistic D, suggestibility
group CIs, the S_0 control row, training-item E1a / E1b, and scripts/12 --split train / scripts/13 end to end."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from vcd.analysis import e1_metrics as M
from vcd.data.framings import make_prompts
from vcd.io import write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse
from vcd.student import readout as R
from vcd.teacher import profile as P

V = ["T1", "T3", "T5", "T6"]
N_FAM = 60
ROOT = Path(__file__).resolve().parents[1]
os.environ.setdefault("HF_HUB_OFFLINE", "1")


def _prompts() -> dict[str, Prompt]:
    out = {}
    for i in range(N_FAM):
        f = Family(family_id=f"g{i:03d}", source="daily_dilemmas", source_id=str(i), topic_group="t", situation=f"Situation {i}.", action_x="Do x.", action_y="Do not do x.", ambiguity="high")
        ps, _ = make_prompts(f, V)
        for p in ps:
            out[p.prompt_id] = p
    return out


def _rows(who: str, p_fn, prompts: dict[str, Prompt], category: str = "answer") -> list[TeacherResponse]:
    rows = []
    for p in prompts.values():
        px = float(np.clip(p_fn(p.family_id, p.variant, p.order), 0.01, 0.99))
        letter = next(l for l, a in p.letter_to_action.items() if a == ("x" if px >= 0.5 else "y"))
        pl = {letter: px if p.letter_to_action[letter] == "x" else 1 - px}
        pl[next(l for l in "AB" if l != letter)] = 1 - pl[letter]
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=who, model="m", mode="profile", temperature=0.0, raw=f"Answer: {letter}", category=category, letter=letter, choice_action=p.letter_to_action[letter], p_letters=pl, p_x=px))
    return rows


def _comp(name: str, scale: float):
    """A deterministic family x variant component with zero family mean (a pure framing-shift pattern)."""
    def fn(f: str, v: str) -> float:
        rng = np.random.default_rng([zlib.crc32(name.encode()), zlib.crc32(f.encode())])
        vals = rng.normal(0, scale, size=len(V))
        return float(vals[V.index(v)] - vals.mean())
    return fn


@pytest.fixture(scope="module")
def world():
    """Teachers: alpha (its own pattern), beta = base-like pattern + its own. Students of alpha = alpha + base pattern:
    the raw closest teacher is beta (shared base component), the partial correlation given the base recovers alpha."""
    prompts = _prompts()
    A, Bse, Cu = _comp("alpha", 0.08), _comp("base", 0.12), _comp("beta_unique", 0.05)
    noise = lambda s: (lambda f, v: float(np.random.default_rng([s, zlib.crc32(f.encode()), V.index(v)]).normal(0, 0.01)))  # noqa: E731
    t_alpha = lambda f, v, o: 0.5 + A(f, v)  # noqa: E731
    t_beta = lambda f, v, o: 0.5 + 0.8 * Bse(f, v) + Cu(f, v)  # noqa: E731
    base = lambda f, v, o: 0.5 + Bse(f, v)  # noqa: E731
    stud = lambda s: (lambda f, v, o: 0.5 + 0.6 * A(f, v) + Bse(f, v) + noise(s)(f, v))  # noqa: E731
    stud_b = lambda f, v, o: 0.5 + 0.6 * (0.8 * Bse(f, v) + Cu(f, v)) + Bse(f, v) + noise(9)(f, v)  # noqa: E731
    teachers = _rows("alpha", t_alpha, prompts) + _rows("beta", t_beta, prompts)
    students = _rows("qwen3-4b.alpha_O_s1", stud(1), prompts) + _rows("qwen3-4b.alpha_O_s2", stud(2), prompts) + _rows("qwen3-4b.beta_O_s1", stud_b, prompts)
    base_rows = _rows("qwen3-4b.base_B_s0", base, prompts, category="malformed")  # the base rarely passes the mass gate but has p_x everywhere
    sym_t, sym_s = M.sym_table(teachers, prompts), M.sym_table(students, prompts)
    shifts_t, shifts_s = P.framing_shifts(sym_t, V), P.framing_shifts(sym_s, V)
    shifts_0 = M.base_prior_shifts(base_rows, prompts, V)
    return dict(prompts=prompts, teachers=teachers, students=students, base_rows=base_rows, sym_t=sym_t, sym_s=sym_s, shifts_t=shifts_t, shifts_s=shifts_s, shifts_0=shifts_0)


def test_mass_gate_flag_and_base_prior(world):
    gated = M.sym_table(world["base_rows"], world["prompts"])
    assert gated.empty or gated["p_sym"].isna().all()  # every base row is malformed: nothing passes the 0.9 rule
    ungated = M.sym_table(world["base_rows"], world["prompts"], mass_gate=False)
    assert len(ungated) == N_FAM * len(V) and ungated["p_sym"].notna().all()
    s0 = world["shifts_0"]
    assert s0["family_id"].nunique() == N_FAM and set(s0["teacher"]) == {"qwen3-4b.base_B_s0"}
    assert np.allclose(s0.groupby("family_id")["r"].sum(), 0, atol=1e-9)


def test_partial_corr_matches_closed_form():
    rng = np.random.default_rng(1)
    z = rng.normal(size=300)
    x, y = z + rng.normal(size=300), 0.5 * z + rng.normal(size=300)
    rxy, rxz, ryz = (np.corrcoef(a, b)[0, 1] for a, b in ((x, y), (x, z), (y, z)))
    expected = (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))
    assert M.partial_corr(x, y, z) == pytest.approx(expected, abs=1e-12)
    assert np.isnan(M.partial_corr([1, 2, 3], [1, 2, 3], [1, 2, 3]))
    # vectorised helpers agree with the scalar one
    X = np.stack([x, y])
    assert M._partial_corr_with_fixed(X, y, z)[0] == pytest.approx(expected, abs=1e-12)
    assert M._rowwise_partial_corr(X, np.stack([y, y]), np.stack([z, z]))[0] == pytest.approx(expected, abs=1e-12)


def test_partial_rho_recovers_own_teacher_when_raw_rho_does_not(world):
    own = {"qwen3-4b.alpha_O_s1": "alpha", "qwen3-4b.alpha_O_s2": "alpha", "qwen3-4b.beta_O_s1": "beta"}
    raw = M.inheritance(world["shifts_s"], world["shifts_t"], own, V, n_perm=0, n_boot=0).set_index("run_id")
    part = M.inheritance_partial(world["shifts_s"], world["shifts_t"], world["shifts_0"], own, V, n_perm=300, n_boot=300, seed=0).set_index("run_id")
    for run in ("qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"):
        assert raw.loc[run, "delta_rho"] < 0 and raw.loc[run, "other_argmax"] == "beta", run  # the shared base component wins raw
        assert part.loc[run, "delta_rho"] > 0.3 and part.loc[run, "p_perm"] < 0.02 and part.loc[run, "ci_lo"] > 0, run
        assert part.loc[run, "rho_base"] > 0.5 and part.loc[run, "control"] == "qwen3-4b.base_B_s0"
    assert part.loc["qwen3-4b.beta_O_s1", "delta_rho"] > 0  # beta's own unique part survives the control too
    pr = M.profile_rho_partial(world["shifts_s"], world["shifts_t"], world["shifts_0"], V).set_index(["run_id", "teacher"])
    assert pr.loc[("qwen3-4b.alpha_O_s1", "alpha"), "partial"] == pytest.approx(part.loc["qwen3-4b.alpha_O_s1", "rho_own"], abs=1e-9)
    assert pr.loc[("qwen3-4b.alpha_O_s1", "alpha"), "raw"] == pytest.approx(raw.loc["qwen3-4b.alpha_O_s1", "rho_own"], abs=1e-9)
    byv = M.inheritance_partial(world["shifts_s"], world["shifts_t"], world["shifts_0"], own, V, n_perm=0, n_boot=0, by_variant=True)
    assert set(byv["variant"]) == set(V) and (byv["n_cells"] == N_FAM).all()
    pooled = M.pooled_inheritance_partial(world["shifts_s"], world["shifts_t"], world["shifts_0"], own, V, n_perm=200, n_boot=100).set_index("run_id")
    assert pooled.loc["qwen3-4b.alpha_O_pooled", "delta_rho"] > 0.3 and pooled.loc["qwen3-4b.alpha_O_pooled", "n_seeds"] == 2 and "p_holm" in pooled
    with pytest.raises(ValueError):
        M.inheritance_partial(world["shifts_s"], world["shifts_t"], world["shifts_t"], own, V)  # control must hold one profile
    # determinism
    again = M.inheritance_partial(world["shifts_s"], world["shifts_t"], world["shifts_0"], own, V, n_perm=300, n_boot=300, seed=0).set_index("run_id")
    pd.testing.assert_frame_equal(part, again)


def test_label_assignments_and_exact_grid(world):
    A = M.label_assignments([0, 0, 1, 1])
    assert A.shape == (6, 4) and len({tuple(r) for r in A}) == 6 and (A.sum(axis=1) == 2).all()
    assert M.n_label_assignments([0] * 5 + [1] * 5 + [2] * 5) == 756_756
    assert M.label_assignments(["a", "b", "a"]).tolist() == [["a", "a", "b"], ["a", "b", "a"], ["b", "a", "a"]]
    own = {"qwen3-4b.alpha_O_s1": "alpha", "qwen3-4b.alpha_O_s2": "alpha", "qwen3-4b.beta_O_s1": "beta"}
    part = M.inheritance_partial(world["shifts_s"], world["shifts_t"], world["shifts_0"], own, V, n_perm=0, n_boot=0)
    g = M.grid_permutation_partial(part, n_perm=100, seed=0)
    assert g["method"] == "exact" and g["n_perm"] == 3 == g["n_assignments"] and g["observed"] > 0 and g["p"] == pytest.approx(1 / 3)
    assert g["control"] == "qwen3-4b.base_B_s0" and set(g["per_run"]) == set(own)
    g_rand = M.grid_permutation_partial(part, n_perm=100, seed=0, exact_max=0)
    assert g_rand["method"] == "random" and g_rand["n_perm"] == 100 and g_rand["observed"] == pytest.approx(g["observed"])
    with pytest.raises(ValueError):
        M.grid_permutation_partial(part.drop(columns=["control"]))
    # the pre-revision grid_permutation keeps its random null and its result keys
    raw = M.inheritance(world["shifts_s"], world["shifts_t"], own, V, n_perm=0, n_boot=0)
    g_old = M.grid_permutation(raw, n_perm=50, seed=0)
    assert g_old["method"] == "random" and g_old["n_perm"] == 50 and 0 < g_old["p"] <= 1


def test_dose_response_slope_and_permutation():
    s_t = {"a": 0.05, "b": 0.10, "c": 0.15}
    own = {f"q.{t}_O_s{s}": t for t in s_t for s in (1, 2, 3)}
    rng = np.random.default_rng(0)
    pos = {r: s_t[t] * 1.5 + rng.normal(0, 0.005) for r, t in own.items()}
    d = M.dose_response(pos, s_t, own, n_perm=100, seed=0)
    assert d["method"] == "exact" and d["n_perm"] == 1680 and d["n_runs"] == 9 and d["n_teachers"] == 3
    assert d["slope"] == pytest.approx(1.5, abs=0.2) and d["p"] == pytest.approx(1 / 1680) and d["ordering_preserved"] is True
    assert set(d["teachers"]) == set(s_t) and d["teachers"]["c"]["s_student_mean"] > d["teachers"]["a"]["s_student_mean"]
    assert 0 < d["seed_noise_sd"] < 0.02 and d["pearson"] > 0.95
    assert d["teacher_exact"]["n_assignments"] == 6 and d["teacher_exact"]["p"] == pytest.approx(1 / 6) and d["teacher_exact"]["rank"] == 1  # floor 1 / 3!
    neg = {r: -s_t[t] + rng.normal(0, 0.005) for r, t in own.items()}
    dn = M.dose_response(neg, s_t, own, n_perm=100, seed=0)
    assert dn["slope"] < 0 and dn["p"] > 0.9 and dn["ordering_preserved"] is False
    d_rand = M.dose_response(pos, s_t, own, n_perm=500, seed=0, exact_max=0)
    assert d_rand["method"] == "random" and d_rand["slope"] == pytest.approx(d["slope"]) and d_rand["p"] < 0.05
    # runs whose teacher has no s_T are ignored; too few runs -> empty result
    assert M.dose_response({"q.a_O_s1": 0.1, "q.z_O_s1": 0.2}, s_t, {"q.a_O_s1": "a", "q.z_O_s1": "z"})["n_runs"] == 1
    assert np.isnan(M.dose_response({}, s_t, {})["slope"])


def test_suggestibility_by_run(world):
    s = M.suggestibility_by_run(world["shifts_t"]).set_index("who")
    d = world["shifts_t"].groupby(["teacher", "variant"])["r"].mean()
    assert s.loc["alpha", "s"] == pytest.approx(d[("alpha", "T5")] - d[("alpha", "T6")])
    assert s.loc["alpha", "n_families"] == N_FAM and list(s.columns) == ["delta_T5", "delta_T6", "s", "n_families"]
    assert M.suggestibility_by_run(world["shifts_t"].iloc[0:0]).empty
    fams = sorted(world["shifts_t"]["family_id"].unique())[:10]
    sub = M.suggestibility_by_run(world["shifts_t"], families=fams).set_index("who")
    g = world["shifts_t"][world["shifts_t"]["family_id"].isin(fams) & (world["shifts_t"]["teacher"] == "alpha")].groupby("variant")["r"].mean()
    assert sub.loc["alpha", "n_families"] == 10 and sub.loc["alpha", "s"] == pytest.approx(g["T5"] - g["T6"])
    assert M.complete_families(world["shifts_t"], ["alpha", "beta"], V) == sorted(world["shifts_t"]["family_id"].unique())
    assert M.complete_families(world["shifts_t"], ["alpha", "nobody"], V) == []


def test_train_reproduction_and_contested_counting():
    letters = {"p1": "A", "p2": "B", "p3": None}
    targets = {"p1": "A", "p2": "A", "p3": "B", "p4": "A"}
    r = M.train_reproduction(letters, targets)
    assert r == {"n_targets": 4, "n_scored": 3, "n_missing": 1, "n_no_letter": 1, "n_match": 1, "accuracy": pytest.approx(1 / 3)}
    assert np.isnan(M.train_reproduction({}, targets)["accuracy"])
    own = {"f1.T1.o1": "A", "f1.T3.o1": "B", "f2.T1.o1": "A", "f3.T1.o1": "B"}
    other = {"f1.T1.o1": "B", "f1.T3.o1": "B", "f2.T1.o1": "B", "f3.T1.o1": "A", "f9.T1.o1": "A"}
    assert M.contested_items(own, other) == ["f1.T1.o1", "f2.T1.o1", "f3.T1.o1"]
    runs = {"r1": {p: "A" for p in own}, "r2": {p: "B" for p in own}}
    c = M.contested_alignment(runs, own, other, n_boot=500, seed=0)
    assert c["n_items"] == 3 and c["n_families"] == 3 and c["n_runs"] == 2 and c["n_pairs"] == 6 and c["share"] == pytest.approx(0.5)
    assert c["ci_lo"] <= 0.5 <= c["ci_hi"]
    perfect = M.contested_alignment({"r1": {p: own[p] for p in own}}, own, other, n_boot=200)
    assert perfect["share"] == 1.0 and perfect["ci_lo"] == 1.0
    assert np.isnan(M.contested_alignment({"r1": {}}, own, other)["share"])
    # family_of overrides the prompt_id prefix rule
    c2 = M.contested_alignment(runs, own, other, n_boot=0, family_of={p: "one" for p in own})
    assert c2["n_families"] == 1 and np.isnan(c2["ci_lo"])
    rows = [TeacherResponse(prompt_id="p1", teacher="x", model="m", mode="profile", temperature=0.0, raw="", category="answer", letter="B"),
            TeacherResponse(prompt_id="p1", teacher="x", model="m", mode="profile", temperature=0.0, raw="", category="answer", letter="A")]
    assert M.letters_of(rows) == {"p1": "B"}


def test_sft_prompts_order_and_validation(tmp_path):
    prompts = {p.prompt_id: p for p in _prompts().values()}
    ids = sorted(prompts)[:5][::-1]
    sft = tmp_path / "x_O_s1.jsonl"
    write_jsonl(sft, [{"prompt_id": i, "letter": "A"} for i in ids] + [{"prompt_id": ids[0], "letter": "A"}])
    got = R.sft_prompts(sft, prompts)
    assert [p.prompt_id for p in got] == ids  # file order, duplicates dropped, the other option order NOT added
    write_jsonl(sft, [{"prompt_id": "nope.T1.o1", "letter": "A"}])
    with pytest.raises(ValueError):
        R.sft_prompts(sft, prompts)


def test_eval_script_train_split(tmp_path):
    """scripts/12 --split train scores exactly the SFT prompts in file order and records the SFT sha256."""
    from vcd.io import load_models

    pilot = [p for p in load_models(ROOT / "data/prompts/pilot_prompts_v2.jsonl", Prompt) if p.variant in ("T1", "T5")][:6][::-1]
    sft = tmp_path / "gpt4o_O_s1.jsonl"
    write_jsonl(sft, [{"prompt_id": p.prompt_id, "letter": "A"} for p in pilot])
    res = subprocess.run([sys.executable, str(ROOT / "scripts/12_eval_student.py"), "--model", "HuggingFaceTB/SmolLM2-135M", "--profile", "tiny", "--split", "train",
                          "--prompts", str(ROOT / "data/prompts/pilot_prompts_v2.jsonl"), "--sft", str(sft), "--out", str(tmp_path / "eval")],
                         cwd=ROOT, capture_output=True, text=True, env={**os.environ, "HF_HUB_OFFLINE": "1"})
    assert res.returncode == 0, res.stderr[-2000:]
    rows = load_models(tmp_path / "eval/train_responses.jsonl", TeacherResponse)
    assert [r.prompt_id for r in rows] == [p.prompt_id for p in pilot] and all(r.teacher == "smollm2-135m.base_B_s0" for r in rows)
    summ = json.loads((tmp_path / "eval/train_readout_summary.json").read_text())
    assert summ["split"] == "train" and summ["sft_path"] == str(sft) and len(summ["sft_sha256"]) == 64
    bad = subprocess.run([sys.executable, str(ROOT / "scripts/12_eval_student.py"), "--model", "HuggingFaceTB/SmolLM2-135M", "--profile", "tiny", "--split", "train", "--out", str(tmp_path / "e2")],
                         cwd=ROOT, capture_output=True, text=True)
    assert bad.returncode != 0 and "--sft" in bad.stderr


def _write_tree(world, tmp_path: Path) -> tuple[Path, Path, Path]:
    runs = tmp_path / "runs"
    for run in ("qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2", "qwen3-4b.beta_O_s1"):
        d = runs / "qwen3-4b" / run.split(".", 1)[1] / "eval"
        d.mkdir(parents=True)
        write_jsonl(d / "dev_responses.jsonl", [r for r in world["students"] if r.teacher == run])
    d = runs / "qwen3-4b" / "base_B_s0" / "eval"
    d.mkdir(parents=True)
    write_jsonl(d / "dev_responses.jsonl", world["base_rows"])
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in ("alpha", "beta"):
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    return runs, tdir, pp


def _run13(runs: Path, tdir: Path, pp: Path, out: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/13_e1_analysis.py"), "--runs-dir", str(runs), "--student", "qwen3-4b", "--split", "dev", "--teacher-dir", str(tdir),
         "--teachers", "alpha,beta", "--prompts", str(pp), "--prompts-train", str(pp), "--out", str(out), "--n-perm", "100", "--n-boot", "100", *extra],
        cwd=ROOT, capture_output=True, text=True, check=True)


def test_analysis_script_without_train_readouts(world, tmp_path):
    runs, tdir, pp = _write_tree(world, tmp_path)
    out = tmp_path / "e1"
    _run13(runs, tdir, pp, out, "--sft-dir", str(tmp_path / "no_sft"))
    md = (out / "summary.md").read_text()
    assert "rules frozen on dev 2026-10-05" in md and "**pending (no train readouts)**" in md
    for f in ("inheritance_partial.csv", "inheritance_partial_by_variant.csv", "inheritance_partial_pooled.csv", "grid_permutation_partial.json",
              "suggestibility_runs.csv", "dose_response.json", "e1_train_reproduction.csv", "e1_contested.csv", "inheritance_pooled.csv", "grid_permutation.json",
              "e2_secondary_D.json", "suggestibility_groups.csv", "suggestibility_group_pairs.csv", "base_control.csv"):
        assert (out / f).exists(), f
    verdict_rows = [l for l in md.splitlines() if l.startswith("| ")][:8]
    assert any(l.startswith("| **E2 primary** |") for l in verdict_rows) and any(l.startswith("| **E2 secondary** |") for l in verdict_rows)
    assert not any(l.startswith("| P1 |") or l.startswith("| P2 |") for l in md.splitlines())  # run-level permutations are no longer verdict rows
    assert "pseudo-replicated" in md and "teacher-level exact p" in md and "Reliability ceilings" in md and "## Descriptive (no verdict)" in md
    sec = json.loads((out / "e2_secondary_D.json").read_text())
    assert sec["verdict"] == "pass" and sec["seen_partial"]["D"] > 0.3 and sec["seen_partial"]["ci_lo"] > 0 and sec["seen_partial"]["p_perm"] < 0.05
    assert sec["seen_partial"]["ci_specific_lo"] > 0 and sec["seen_partial"]["D"] == pytest.approx(sec["seen_partial"]["D_shared"] + sec["seen_partial"]["D_specific"])
    assert sec["ceiling_sqrt_spearman_brown"]["deepseek_v4"] == pytest.approx(M.reliability_ceiling(sec["reliability_split_half_r"]["deepseek_v4"])) and "D_specific" in sec["rule"]
    assert "D_specific" in md and "ceiling sqrt(2r/(1+r))" in md and "sqrt(2r / (1 + r))" in md and "version 5" in md
    assert "the gate does not fire" in md  # alpha / beta have no test-split r; the E2b / E3 / E4 / E5 sentence is for the real teachers
    pooled = pd.read_csv(out / "inheritance_pooled.csv")
    assert "perm_null_mean" in pooled.columns and pooled["perm_null_mean"].notna().all() and "perm_null_mean" in md
    assert set(sec["seen_partial"]["matrix"]) == {"qwen3-4b.alpha_O_pooled", "qwen3-4b.beta_O_pooled"} and sec["seen_raw"]["D"] < sec["seen_partial"]["D"]
    sg = pd.read_csv(out / "suggestibility_groups.csv")
    assert {"students:alpha", "students:beta", "teacher:alpha", "teacher:beta", "base_prior"} <= set(sg["group"]) and (sg["ci_lo"] <= sg["s"]).all() and (sg["s"] <= sg["ci_hi"]).all()
    bc = pd.read_csv(out / "base_control.csv").set_index("teacher")
    assert (bc["profile"] == "ungated covariate profile").all() and bc.loc["beta", "rank"] == 1 and bc.loc["beta", "margin_ci_lo"] > 0  # the base is beta-like by construction
    part = pd.read_csv(out / "inheritance_partial.csv").set_index("run_id")
    assert (part.loc[["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "delta_rho"] > 0).all() and (part["control"] == "qwen3-4b.base_B_s0").all()
    old = pd.read_csv(out / "inheritance.csv").set_index("run_id")
    assert (old.loc[["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "delta_rho"] < 0).all()  # the pre-revision rule is still written
    grid = json.loads((out / "grid_permutation_partial.json").read_text())
    assert grid["method"] == "exact" and grid["n_assignments"] == 3 and grid["observed"] > 0
    assert grid["teacher_exact"]["n_assignments"] == 2 and grid["teacher_exact"]["p"] == pytest.approx(0.5)  # 2 teachers -> floor 1/2
    dose = json.loads((out / "dose_response.json").read_text())
    assert dose["n_runs"] == 3 and dose["n_teachers"] == 2 and "base_prior" in dose["descriptive"]
    sug = pd.read_csv(out / "suggestibility_runs.csv")
    assert set(sug["kind"]) == {"teacher", "run", "base_prior"} and len(sug[sug["kind"] == "run"]) == 3  # the gated base has no complete family
    assert pd.read_csv(out / "e1_train_reproduction.csv").empty and pd.read_csv(out / "e1_contested.csv").empty
    assert "old rule, not the verdict" in md and "Pre-revision rule" in md and "withdrawn the same day" in md


def test_analysis_script_with_train_readouts(world, tmp_path):
    """E1a / E1b from eval/train_responses.jsonl + SFT files: the students copy their own teacher's letters exactly."""
    runs, tdir, pp = _write_tree(world, tmp_path)
    prompts = world["prompts"]
    sft_dir = tmp_path / "sft"
    sft_dir.mkdir()
    train_ids = sorted(prompts)[:120]
    # alpha and beta disagree on every third item
    letters = {"alpha": {pid: "A" for pid in train_ids}, "beta": {pid: ("B" if i % 3 == 0 else "A") for i, pid in enumerate(train_ids)}}
    for t in ("alpha", "beta"):
        write_jsonl(sft_dir / f"{t}_O_s1.jsonl", [{"prompt_id": pid, "family_id": prompts[pid].family_id, "letter": letters[t][pid]} for pid in train_ids])
    for run in ("qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2", "qwen3-4b.beta_O_s1"):
        t = M.parse_run_id(run).teacher
        rows = [TeacherResponse(prompt_id=pid, teacher=run, model="m", mode="profile", temperature=0.0, raw="", category="answer", letter=letters[t][pid]) for pid in train_ids]
        write_jsonl(runs / "qwen3-4b" / run.split(".", 1)[1] / "eval" / "train_responses.jsonl", rows)
    out = tmp_path / "e1"
    _run13(runs, tdir, pp, out, "--sft-dir", str(sft_dir))
    md = (out / "summary.md").read_text()
    assert "**PASS (E1a pass, E1b pass)**" in md and "| pass |" in md
    prim = [l for l in md.splitlines() if l.startswith("| **E2 primary** |")]
    assert len(prim) == 1 and prim[0].rstrip("| ").split("**")[-2] in {"PASS", "PARTIAL", "FAIL"}
    assert "rule-selection split" in md and "Conventions:" in md  # dev verdicts are labelled descriptive
    rep = pd.read_csv(out / "e1_train_reproduction.csv").set_index("run_id")
    assert len(rep) == 3 and (rep["accuracy"] == 1.0).all() and rep["passed"].all() and (rep["n_targets"] == 120).all()
    assert (rep["n_rows"] == 120).all() and (rep["answer_rate"] == 1.0).all() and (rep["n_missing"] == 0).all()
    dose = json.loads((out / "dose_response.json").read_text())
    assert dose["n_common_families"] == N_FAM
    con = pd.read_csv(out / "e1_contested.csv").set_index(["teacher", "other"])
    assert con.loc[("alpha", "beta"), "n_items"] == 40 and con.loc[("alpha", "beta"), "n_runs"] == 2 and con.loc[("alpha", "beta"), "n_pairs"] == 80
    assert con.loc[("alpha", "beta"), "share"] == 1.0 and con.loc[("alpha", "beta"), "ci_lo"] == 1.0 and con["passed"].all()
    # a student that fails E1a flips the verdict
    bad = [TeacherResponse(prompt_id=pid, teacher="qwen3-4b.beta_O_s1", model="m", mode="profile", temperature=0.0, raw="", category="answer", letter="B") for pid in train_ids]
    write_jsonl(runs / "qwen3-4b/beta_O_s1/eval/train_responses.jsonl", bad)
    _run13(runs, tdir, pp, tmp_path / "e1b", "--sft-dir", str(sft_dir))
    md2 = (tmp_path / "e1b/summary.md").read_text()
    assert "FAIL (E1a fail" in md2
    # a truncated readout (prompts missing) cannot pass E1a even at accuracy 1.0
    good_half = [TeacherResponse(prompt_id=pid, teacher="qwen3-4b.beta_O_s1", model="m", mode="profile", temperature=0.0, raw="", category="answer", letter=letters["beta"][pid]) for pid in train_ids[:60]]
    write_jsonl(runs / "qwen3-4b/beta_O_s1/eval/train_responses.jsonl", good_half)
    _run13(runs, tdir, pp, tmp_path / "e1c", "--sft-dir", str(sft_dir))
    rep3 = pd.read_csv(tmp_path / "e1c/e1_train_reproduction.csv").set_index("run_id")
    assert rep3.loc["qwen3-4b.beta_O_s1", "accuracy"] == 1.0 and rep3.loc["qwen3-4b.beta_O_s1", "n_missing"] == 60 and not rep3.loc["qwen3-4b.beta_O_s1", "passed"]
    assert "FAIL (E1a fail, E1b pass)" in (tmp_path / "e1c/summary.md").read_text()
    # only one teacher's runs read out: every E1 line is pending, no per-line "pass"
    (runs / "qwen3-4b/beta_O_s1/eval/train_responses.jsonl").unlink()
    _run13(runs, tdir, pp, tmp_path / "e1d", "--sft-dir", str(sft_dir))
    md4 = (tmp_path / "e1d/summary.md").read_text()
    verdict_rows = [l for l in md4.splitlines() if l.startswith("| E1a |") or l.startswith("| E1b |") or l.startswith("| **E1** |")]
    assert len(verdict_rows) == 3 and all(l.rstrip("| ").endswith("pending") or "pending (" in l for l in verdict_rows), verdict_rows
    assert "pending (train readouts or SFT targets missing for beta)" in md4


# --------------------------------------------------------------------------- corrected E2 (family-level inference, teacher-level exact p)


def test_e2_primary_verdict_categories():
    assert M.e2_primary_verdict(3, 3) == "PASS" and M.e2_primary_verdict(2, 3) == "PASS"
    assert M.e2_primary_verdict(1, 3) == "PARTIAL" and M.e2_primary_verdict(0, 3) == "FAIL" and M.e2_primary_verdict(0, 0) == "pending"
    assert M.e2_primary_verdict(1, 2) == "PARTIAL" and M.e2_primary_verdict(2, 2) == "PASS"


def _three_teacher_table(rng, own_bonus: float) -> pd.DataFrame:
    rows = []
    for t in ("a", "b", "c"):
        for s in range(1, 6):
            rho = {u: rng.normal(0.2, 0.02) for u in ("a", "b", "c")}
            rho[t] += own_bonus
            others = {u: v for u, v in rho.items() if u != t}
            rows.append(dict(run_id=f"q.{t}_O_s{s}", teacher=t, variant="all", rho_own=rho[t], rho_other_max=max(others.values()), delta_rho=rho[t] - max(others.values()), control="q.base_B_s0", **{f"rho__{u}": v for u, v in rho.items()}))
    return pd.DataFrame(rows)


def test_teacher_level_exact_p_floor_is_one_sixth():
    assert M.teacher_assignments(3).shape == (6, 3) and M.teacher_assignments(3)[0].tolist() == [0, 1, 2] and M.teacher_assignments(2).tolist() == [[0, 1], [1, 0]]
    rng = np.random.default_rng(0)
    good = _three_teacher_table(rng, own_bonus=0.1)
    te = M.teacher_level_exact_p(good)
    assert te["n_assignments"] == 6 and te["rank"] == 1 and te["p"] == pytest.approx(1 / 6) and te["floor"] == pytest.approx(1 / 6)
    assert te["observed"] == pytest.approx(good["delta_rho"].mean()) and len(te["null"]) == 6 and te["null"][0] == pytest.approx(te["observed"])
    # the run-level enumeration of the same table gives a far smaller (pseudo-replicated) p; the teacher-level one cannot go below 1/6
    g = M.grid_permutation_partial(good, n_perm=10, seed=0)
    assert g["method"] == "exact" and g["n_assignments"] == 756_756 and g["p"] < 1e-4 and g["teacher_exact"]["p"] == pytest.approx(1 / 6) and "pseudo-replicated" in g["unit_note"]
    bad = _three_teacher_table(rng, own_bonus=-0.1)
    assert M.teacher_level_exact_p(bad)["p"] == 1.0 and M.teacher_level_exact_p(bad)["rank"] == 6
    assert np.isnan(M.teacher_level_exact_p(good.iloc[0:0])["p"])


def test_joint_partial_D_recovers_inheritance(world):
    """Pooled alpha students (alpha + base pattern) vs the beta student: given the base, D is clearly positive with a small family-permutation p."""
    pooled = {"alpha": M.pooled_shifts(world["shifts_s"], ["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "qwen3-4b.alpha_O_pooled"),
              "beta": M.pooled_shifts(world["shifts_s"], ["qwen3-4b.beta_O_s1"], "qwen3-4b.beta_O_pooled")}
    d = M.joint_partial_D(pooled, world["shifts_t"], world["shifts_0"], V, n_perm=400, n_boot=400, seed=0)
    assert d["n_families"] == N_FAM and d["n_teachers"] == 2 and d["control"] == "qwen3-4b.base_B_s0" and d["cells"] == V
    assert d["D"] > 0.3 and d["ci_lo"] > 0 and d["p_perm"] == pytest.approx(1 / 401) and d["null_mean"] == pytest.approx(0, abs=0.05)
    m = d["matrix"]["qwen3-4b.alpha_O_pooled"]
    assert m["alpha"] > m["beta"] and d["per_teacher"]["alpha"]["contrast"] == pytest.approx(m["alpha"] - m["beta"])
    assert d["D"] == pytest.approx(np.mean([d["per_teacher"][t]["contrast"] for t in ("alpha", "beta")]))
    raw = M.joint_partial_D(pooled, world["shifts_t"], None, V, n_perm=0, n_boot=0, seed=0)
    assert raw["control"] is None and raw["D"] == pytest.approx(d["D_raw"]) and raw["D"] < d["D"]  # the shared base component hides alpha in the raw matrix
    assert np.isnan(raw["p_perm"]) and np.isnan(raw["ci_lo"]) and raw["n_perm"] == 0
    # cells subset: T5-only D uses the same families, 60 cells per profile
    d5 = M.joint_partial_D(pooled, world["shifts_t"], world["shifts_0"], V, cells=["T5"], n_perm=50, n_boot=50, seed=0)
    assert d5["cells"] == ["T5"] and d5["n_families"] == N_FAM and not np.isnan(d5["D"])
    with pytest.raises(ValueError):
        M.joint_partial_D({"alpha": world["shifts_s"], "beta": pooled["beta"]}, world["shifts_t"], world["shifts_0"], V)  # a pooled table must hold one profile
    assert np.isnan(M.joint_partial_D({"alpha": pooled["alpha"]}, world["shifts_t"], world["shifts_0"], V)["D"])  # fewer than 2 teachers
    again = M.joint_partial_D(pooled, world["shifts_t"], world["shifts_0"], V, n_perm=400, n_boot=400, seed=0)
    assert again == d


def test_joint_partial_D_null_for_random_students(world):
    """Students that carry only the base pattern plus noise: D ~ 0, the CI covers 0 and the family permutation p is large."""
    prompts = world["prompts"]
    Bse = _comp("base", 0.12)
    noise = lambda s: (lambda f, v: float(np.random.default_rng([s + 100, zlib.crc32(f.encode()), V.index(v)]).normal(0, 0.03)))  # noqa: E731
    rows = _rows("qwen3-4b.alpha_O_s7", lambda f, v, o: 0.5 + Bse(f, v) + noise(7)(f, v), prompts) + _rows("qwen3-4b.beta_O_s7", lambda f, v, o: 0.5 + Bse(f, v) + noise(8)(f, v), prompts)
    shifts = P.framing_shifts(M.sym_table(rows, prompts), V)
    pooled = {"alpha": M.pooled_shifts(shifts, ["qwen3-4b.alpha_O_s7"], "qwen3-4b.alpha_O_pooled"), "beta": M.pooled_shifts(shifts, ["qwen3-4b.beta_O_s7"], "qwen3-4b.beta_O_pooled")}
    d = M.joint_partial_D(pooled, world["shifts_t"], world["shifts_0"], V, n_perm=400, n_boot=400, seed=0)
    assert abs(d["D"]) < 0.1 and d["ci_lo"] < 0 < d["ci_hi"] and d["p_perm"] > 0.1


def test_suggestibility_groups_and_pairs(world):
    sh = pd.concat([world["shifts_t"], world["shifts_s"]])
    groups = {"students:alpha": ["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "teacher:alpha": ["alpha"], "teacher:beta": ["beta"], "nobody": ["ghost"]}
    g, pairs = M.suggestibility_groups(sh, groups, n_boot=300, seed=0)
    assert list(g["group"]) == ["students:alpha", "teacher:alpha", "teacher:beta"] and (g["n_families"] == N_FAM).all()  # a group with no profile is dropped
    by_run = M.suggestibility_by_run(sh).set_index("who")["s"]
    assert g.set_index("group").loc["teacher:alpha", "s"] == pytest.approx(by_run["alpha"])
    assert g.set_index("group").loc["students:alpha", "s"] == pytest.approx(by_run[["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"]].mean())
    assert (g["ci_lo"] <= g["s"]).all() and (g["s"] <= g["ci_hi"]).all() and g.set_index("group").loc["students:alpha", "n_profiles"] == 2
    assert len(pairs) == 3 and pairs.set_index(["a", "b"]).loc[("students:alpha", "teacher:beta"), "diff"] == pytest.approx(g.set_index("group").loc["students:alpha", "s"] - by_run["beta"])
    assert (pairs["ci_lo"] <= pairs["diff"]).all() and (pairs["diff"] <= pairs["ci_hi"]).all()
    fams = sorted(sh["family_id"].unique())[:10]
    g10, _ = M.suggestibility_groups(sh, groups, families=fams, n_boot=0)
    assert (g10["n_families"] == 10).all() and g10["ci_lo"].isna().all()
    e1, e2 = M.suggestibility_groups(sh.iloc[0:0], groups)
    assert e1.empty and e2.empty


def test_base_prior_control_row(world):
    """The base pattern is shared with beta (beta = 0.8 base + unique): the ungated covariate profile is closest to beta with a margin CI above 0."""
    bc = M.base_prior_control(world["shifts_0"], world["shifts_t"], V, n_boot=300, seed=0).set_index("teacher")
    assert list(bc.index) == ["alpha", "beta"] and (bc["profile"] == "ungated covariate profile").all() and (bc["who"] == "qwen3-4b.base_B_s0").all()
    assert bc.loc["beta", "rank"] == 1 and bc.loc["beta", "rho"] > bc.loc["alpha", "rho"] and bc.loc["beta", "margin"] == pytest.approx(bc.loc["beta", "rho"] - bc.loc["alpha", "rho"])
    assert bc.loc["beta", "margin_ci_lo"] > 0 and bc.loc["alpha", "margin"] == pytest.approx(-bc.loc["beta", "margin"])
    assert (bc["ci_lo"] <= bc["rho"]).all() and (bc["rho"] <= bc["ci_hi"]).all() and (bc["n_families"] == N_FAM).all()
    with pytest.raises(ValueError):
        M.base_prior_control(world["shifts_t"], world["shifts_t"], V)


def test_reliability_ceiling_is_sqrt_spearman_brown():
    """Split-half r -> reliability of the two-order mean 2r / (1 + r) -> attenuation ceiling sqrt of it (docs/E0 §13 test values)."""
    assert M.reliability_ceiling(0.329) == pytest.approx(0.704, abs=1e-3) and M.reliability_ceiling(0.466) == pytest.approx(0.797, abs=1e-3) and M.reliability_ceiling(0.691) == pytest.approx(0.904, abs=1e-3)
    assert M.reliability_ceiling(0.515) > 0.533  # the dev base prior reaches rho 0.533 with DeepSeek: the raw r 0.515 is not a bound, the ceiling is
    assert M.reliability_ceiling(1.0) == pytest.approx(1.0) and np.isnan(M.reliability_ceiling(0.0)) and np.isnan(M.reliability_ceiling(float("nan")))


def test_D_matrices_decomposition_and_scale_invariance():
    rng = np.random.default_rng(3)
    Tr = rng.normal(size=(1, 3, 200))
    shared = rng.normal(size=200)
    U = rng.normal(size=(3, 200)) * np.array([[0.3], [1.0], [3.0]])  # unequal row scales
    E = (shared[None, :] + U)[None]
    m = M._D_matrices(E, Tr)
    assert np.allclose(m["full"], m["shared"] + m["specific"])
    c = lambda k: float(M._contrast_D(m[k])[0])  # noqa: E731
    assert c("full") == pytest.approx(c("shared") + c("specific"))
    assert abs(c("shared")) > 1e-6  # unequal scales: the shared part does not cancel in D ...
    sc = shared - shared.mean()
    U_orth = U - U.mean(axis=1, keepdims=True)
    U_orth = U_orth - (U_orth @ sc)[:, None] / (sc @ sc) * sc[None, :]  # orthogonal to the shared part ...
    U_orth = U_orth / np.sqrt((U_orth**2).sum(axis=1, keepdims=True)) * 10  # ... and of equal norm, so |E_k| is equal across rows
    m_eq = M._D_matrices((sc[None, :] + U_orth)[None], Tr)
    assert float(M._contrast_D(m_eq["shared"])[0]) == pytest.approx(0, abs=1e-9)  # ... but cancels exactly for equal row scales
    m_u = M._D_matrices(U[None], Tr)
    s_bar = lambda X: float(np.sqrt(((X - X.mean(axis=1, keepdims=True)) ** 2).sum(axis=1).mean()))  # noqa: E731
    assert c("scalefree") * s_bar(E[0]) == pytest.approx(float(M._contrast_D(m_u["scalefree"])[0]) * s_bar(U))  # the shared component cancels exactly in the pooled-scale numerator
    # the correlation matrix is the usual Pearson one
    assert m["full"][0, 1, 2] == pytest.approx(np.corrcoef(E[0, 1], Tr[0, 2])[0, 1])


def test_joint_partial_D_specific_part_and_verdict(world):
    pooled = {"alpha": M.pooled_shifts(world["shifts_s"], ["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "qwen3-4b.alpha_O_pooled"),
              "beta": M.pooled_shifts(world["shifts_s"], ["qwen3-4b.beta_O_s1"], "qwen3-4b.beta_O_pooled")}
    d = M.joint_partial_D(pooled, world["shifts_t"], world["shifts_0"], V, n_perm=400, n_boot=400, seed=0)
    assert d["D"] == pytest.approx(d["D_shared"] + d["D_specific"]) and d["ci_specific_lo"] > 0 and d["p_perm_specific"] == pytest.approx(1 / 401)
    for a, row in d["matrix"].items():
        for t, v in row.items():
            assert v == pytest.approx(d["matrix_shared"][a][t] + d["matrix_specific"][a][t])
    assert set(d["row_scale"]) == {"qwen3-4b.alpha_O_pooled", "qwen3-4b.beta_O_pooled"} and d["ci_scalefree_lo"] < d["D_scalefree"] < d["ci_scalefree_hi"]
    assert d["per_teacher"]["alpha"]["contrast_specific"] + d["per_teacher"]["beta"]["contrast_specific"] == pytest.approx(2 * d["D_specific"])
    assert M.e2_secondary_verdict(d) == "pass"
    assert M.e2_secondary_verdict({}) .startswith("pending") and M.e2_secondary_verdict({"D": float("nan")}).startswith("pending")
    assert M.e2_secondary_verdict({**d, "ci_specific_lo": float("nan")}) == "pending (no resamples)"
    assert M.e2_secondary_verdict({**d, "ci_specific_lo": -0.01}) == "fail" and M.e2_secondary_verdict({**d, "ci_lo": -0.01}) == "fail" and M.e2_secondary_verdict({**d, "p_perm": 0.2}) == "fail"
    # a shared component with unequal noise scales and NO student-specific inheritance: D_specific ~ 0 and the guard refuses the pass
    prompts = world["prompts"]
    A, Bse = _comp("alpha", 0.08), _comp("base", 0.12)
    noise = lambda s, sd: (lambda f, v: float(np.random.default_rng([s + 300, zlib.crc32(f.encode()), V.index(v)]).normal(0, sd)))  # noqa: E731
    rows = _rows("qwen3-4b.alpha_O_s8", lambda f, v, o: 0.5 + Bse(f, v) + 0.5 * A(f, v) + noise(1, 0.01)(f, v), prompts) \
        + _rows("qwen3-4b.beta_O_s8", lambda f, v, o: 0.5 + Bse(f, v) + 0.5 * A(f, v) + noise(2, 0.08)(f, v), prompts)
    shifts = P.framing_shifts(M.sym_table(rows, prompts), V)
    pooled2 = {"alpha": M.pooled_shifts(shifts, ["qwen3-4b.alpha_O_s8"], "qwen3-4b.alpha_O_pooled"), "beta": M.pooled_shifts(shifts, ["qwen3-4b.beta_O_s8"], "qwen3-4b.beta_O_pooled")}
    d2 = M.joint_partial_D(pooled2, world["shifts_t"], world["shifts_0"], V, n_perm=400, n_boot=400, seed=0)
    assert abs(d2["D_shared"]) > 0.02 and abs(d2["D_specific"]) < 0.1 and d2["ci_specific_lo"] < 0 < d2["ci_specific_hi"]
    assert M.e2_secondary_verdict(d2) != "pass"


def test_inheritance_reports_permutation_null_mean(world):
    own = {"qwen3-4b.alpha_O_s1": "alpha", "qwen3-4b.beta_O_s1": "beta"}
    inh = M.inheritance(world["shifts_s"], world["shifts_t"], own, V, n_perm=200, n_boot=0, seed=0)
    assert list(inh.columns[:15]) == ["run_id", "teacher", "variant", "n_families", "n_cells", "rho_own", "spearman_own", "rho_other_max", "other_argmax", "delta_rho", "p_perm", "perm_null_mean", "perm_null_sd", "ci_lo", "ci_hi"]
    assert inh["perm_null_mean"].notna().all() and (inh["perm_null_sd"] > 0).all()
    pooled = M.pooled_inheritance(world["shifts_s"], world["shifts_t"], own, V, n_perm=200, n_boot=0, seed=0)
    assert "perm_null_mean" in pooled.columns and pooled["perm_null_mean"].notna().all()
    none = M.inheritance(world["shifts_s"], world["shifts_t"], own, V, n_perm=0, n_boot=0)
    assert none["perm_null_mean"].isna().all()
