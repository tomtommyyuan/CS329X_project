"""Revised E1 / E2 rules (frozen on dev 2026-10-05): base-prior covariate, partial-rho inheritance, exact teacher-assignment
null, suggestibility dose-response, training-item E1a / E1b, and scripts/12 --split train / scripts/13 end to end."""

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
              "suggestibility_runs.csv", "dose_response.json", "e1_train_reproduction.csv", "e1_contested.csv", "inheritance_pooled.csv", "grid_permutation.json"):
        assert (out / f).exists(), f
    part = pd.read_csv(out / "inheritance_partial.csv").set_index("run_id")
    assert (part.loc[["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "delta_rho"] > 0).all() and (part["control"] == "qwen3-4b.base_B_s0").all()
    old = pd.read_csv(out / "inheritance.csv").set_index("run_id")
    assert (old.loc[["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "delta_rho"] < 0).all()  # the pre-revision rule is still written
    grid = json.loads((out / "grid_permutation_partial.json").read_text())
    assert grid["method"] == "exact" and grid["n_assignments"] == 3 and grid["observed"] > 0
    dose = json.loads((out / "dose_response.json").read_text())
    assert dose["n_runs"] == 3 and dose["n_teachers"] == 2 and "base_prior" in dose["descriptive"]
    sug = pd.read_csv(out / "suggestibility_runs.csv")
    assert set(sug["kind"]) == {"teacher", "run", "base_prior"} and len(sug[sug["kind"] == "run"]) == 3  # the gated base has no complete family
    assert pd.read_csv(out / "e1_train_reproduction.csv").empty and pd.read_csv(out / "e1_contested.csv").empty
    assert "old rule, not the verdict" in md and "Pre-revision rule" in md


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
