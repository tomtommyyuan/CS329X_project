"""Synthetic teacher / student rows with known agreement and shift structure for vcd.analysis.e1_metrics."""

from __future__ import annotations

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
from vcd.schemas import Family, Prompt, TeacherResponse
from vcd.teacher import profile as P

V = ["T1", "T3", "T5", "T6"]
N_FAM = 40
ROOT = Path(__file__).resolve().parents[1]


def _prompts() -> dict[str, Prompt]:
    out = {}
    for i in range(N_FAM):
        f = Family(family_id=f"f{i:03d}", source="daily_dilemmas", source_id=str(i), topic_group="t", situation=f"You face situation {i}.", action_x="Do x.", action_y="Do not do x.", ambiguity="high")
        ps, _ = make_prompts(f, V)
        for p in ps:
            out[p.prompt_id] = p
    return out


def _rows(who: str, p_fn, prompts: dict[str, Prompt]) -> list[TeacherResponse]:
    """Logprob-style profile rows (one per prompt), p_x expressed in x coordinates."""
    rows = []
    for p in prompts.values():
        px = float(np.clip(p_fn(p.family_id, p.variant, p.order), 0.01, 0.99))
        letter = next(l for l, a in p.letter_to_action.items() if a == ("x" if px >= 0.5 else "y"))
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=who, model="m", mode="profile", temperature=0.0, raw=f"Answer: {letter}", category="answer", letter=letter, choice_action=p.letter_to_action[letter], p_letters=None, p_x=px))
    return rows


@pytest.fixture(scope="module")
def world():
    prompts = _prompts()
    rng = np.random.default_rng(0)
    fams = sorted({p.family_id for p in prompts.values()})
    base = {f: rng.uniform(0.2, 0.8) for f in fams}
    # teacher A: T5 pushes up, T6 pushes down, with a family-specific magnitude; teacher B: T3-sensitive, opposite sign
    mag = {f: rng.uniform(0.05, 0.3) for f in fams}
    tA = lambda f, v, o: base[f] + (mag[f] if v == "T5" else -mag[f] if v == "T6" else 0.0)
    tB = lambda f, v, o: base[f] + (-mag[f] if v == "T3" else mag[f] if v == "T1" else 0.0)
    # students: S_A copies A plus small noise (seeds 1, 2); S_B copies B; S_R is flat 0.5 everywhere (random-label control)
    noise = lambda s: (lambda f, v, o: np.random.default_rng([s, zlib.crc32(f.encode()), V.index(v)]).normal(0, 0.03))
    sA1 = lambda f, v, o: tA(f, v, o) + noise(1)(f, v, o)
    sA2 = lambda f, v, o: tA(f, v, o) + noise(2)(f, v, o)
    sB1 = lambda f, v, o: tB(f, v, o) + noise(3)(f, v, o)
    sR = lambda f, v, o: 0.5 + 0.001 * (1 if o == 1 else -1)
    teachers = _rows("alpha", tA, prompts) + _rows("beta", tB, prompts)
    students = _rows("qwen3-4b.alpha_O_s1", sA1, prompts) + _rows("qwen3-4b.alpha_O_s2", sA2, prompts) + _rows("qwen3-4b.beta_O_s1", sB1, prompts) + _rows("qwen3-4b.random_R_s1", sR, prompts)
    sym_t = M.sym_table(teachers, prompts)
    sym_s = M.sym_table(students, prompts)
    return dict(prompts=prompts, teachers=teachers, students=students, sym_t=sym_t, sym_s=sym_s)


def test_parse_run_id():
    k = M.parse_run_id("qwen3-4b.gpt4o_O_s1")
    assert k == M.RunKey("qwen3-4b", "gpt4o", "O", 1)
    assert M.parse_run_id("qwen3-4b.random_R_s3").teacher == "random"
    assert M.parse_run_id("smollm2-135m.base_B_s0").version == "B"
    with pytest.raises(ValueError):
        M.parse_run_id("gpt4o")


def test_binary_jsd_values():
    assert M.binary_jsd(0.5, 0.5) == pytest.approx(0.0, abs=1e-9)
    assert float(M.binary_jsd(np.array([0.0]), np.array([1.0]))[0]) == pytest.approx(1.0, abs=1e-6)
    assert M.binary_jsd(0.2, 0.8) == M.binary_jsd(0.8, 0.2)


def test_agreement_and_jsd(world):
    ag = M.teacher_agreement(world["sym_s"], world["sym_t"], V).set_index(["run_id", "teacher"])["agreement"]
    assert ag[("qwen3-4b.alpha_O_s1", "alpha")] >= 0.9 and ag[("qwen3-4b.alpha_O_s1", "alpha")] > ag[("qwen3-4b.alpha_O_s1", "beta")]
    assert ag[("qwen3-4b.beta_O_s1", "beta")] > ag[("qwen3-4b.beta_O_s1", "alpha")]
    js = M.student_teacher_jsd(world["sym_s"], world["sym_t"], V).set_index(["run_id", "teacher"])["jsd"]
    assert js[("qwen3-4b.alpha_O_s1", "alpha")] < js[("qwen3-4b.alpha_O_s1", "beta")]
    assert js[("qwen3-4b.alpha_O_s1", "alpha")] < 0.01
    # the flat random-label student has 0.5 everywhere: agreement is whatever the teacher's majority is, JSD is large
    assert js[("qwen3-4b.random_R_s1", "alpha")] > js[("qwen3-4b.alpha_O_s1", "alpha")]
    byv = M.teacher_agreement(world["sym_s"], world["sym_t"], V, by_variant=True)
    assert set(byv["variant"]) == set(V) and (byv["n_cells"] == N_FAM).all()


def test_consistency_and_flip(world):
    cons = M.consistency(world["sym_s"], V).set_index("teacher")
    assert "flip_T1-T3" in cons.columns and cons.loc["qwen3-4b.alpha_O_s1", "n_families"] == N_FAM
    # the flat student never flips and has zero cross-framing JSD; the A student flips on some T5/T6 cells
    assert cons.loc["qwen3-4b.random_R_s1", "flip_rate"] == 0.0 and cons.loc["qwen3-4b.random_R_s1", "mean_jsd"] < 1e-6
    assert cons.loc["qwen3-4b.alpha_O_s1", "flip_rate"] > 0
    cj = M.cross_framing_jsd(world["sym_t"], V)
    a = cj[cj.teacher == "alpha"].set_index("pair")["jsd"]
    assert a["T5-T6"] > a["T1-T3"] and a["T1-T3"] < 1e-9
    og = M.order_gap(world["sym_s"]).set_index("teacher")
    assert og.loc["qwen3-4b.alpha_O_s1", "order_gap_mean"] == pytest.approx(0.0, abs=1e-9)
    assert og.loc["qwen3-4b.random_R_s1", "order_gap_mean"] == pytest.approx(0.002, abs=1e-9)


def test_category_rates_and_seen_vs_unseen(world):
    fr = M.frame_table(world["students"], world["prompts"])
    cr = M.category_rates(fr, by=("teacher",)).set_index("teacher")
    assert (cr["answer"] == 1.0).all() and (cr["n"] == N_FAM * len(V) * 2).all()
    assert M.seen_vs_unseen(world["sym_s"], V, "T0").empty  # no T0 in this toy world


def test_inheritance_sign_and_permutation(world):
    shifts_s = P.framing_shifts(world["sym_s"], V)
    shifts_t = P.framing_shifts(world["sym_t"], V)
    own = {"qwen3-4b.alpha_O_s1": "alpha", "qwen3-4b.alpha_O_s2": "alpha", "qwen3-4b.beta_O_s1": "beta"}
    inh = M.inheritance(shifts_s, shifts_t, own, V, n_perm=500, n_boot=300, seed=0).set_index("run_id")
    assert set(inh.index) == set(own)  # the random-label run has no teacher profile -> excluded
    for run, t in own.items():
        assert inh.loc[run, "rho_own"] > 0.9, run
        assert inh.loc[run, "delta_rho"] > 0.5 and inh.loc[run, "p_perm"] < 0.02, run
        assert inh.loc[run, "ci_lo"] > 0 and inh.loc[run, "ci_lo"] <= inh.loc[run, "delta_rho"] <= inh.loc[run, "ci_hi"], run
        assert inh.loc[run, "other_argmax"] != t
    assert inh.loc["qwen3-4b.alpha_O_s1", "rho__alpha"] == inh.loc["qwen3-4b.alpha_O_s1", "rho_own"]
    # a student trained on A but labelled as B's student must get a negative delta_rho and a large p
    wrong = M.inheritance(shifts_s, shifts_t, {"qwen3-4b.alpha_O_s1": "beta"}, V, n_perm=300, n_boot=0, seed=0).iloc[0]
    assert wrong["delta_rho"] < 0 and wrong["p_perm"] > 0.5
    # determinism
    again = M.inheritance(shifts_s, shifts_t, own, V, n_perm=500, n_boot=300, seed=0).set_index("run_id")
    pd.testing.assert_frame_equal(inh, again)
    byv = M.inheritance(shifts_s, shifts_t, own, V, n_perm=0, n_boot=0, by_variant=True)
    assert set(byv["variant"]) == set(V)
    gp = M.grid_permutation(inh.reset_index(), n_perm=200, seed=0)
    assert gp["observed"] > 0 and gp["n_runs"] == 3 and 0 < gp["p"] <= 1
    rho = M.profile_rho(shifts_s, shifts_t, V).set_index(["run_id", "teacher"])["pearson"]
    assert rho[("qwen3-4b.alpha_O_s1", "alpha")] == pytest.approx(inh.loc["qwen3-4b.alpha_O_s1", "rho_own"], abs=1e-9)
    r2 = M.shared_component_r2(shifts_s[shifts_s.teacher == "qwen3-4b.alpha_O_s1"], shifts_t, "alpha", ["beta"], V)
    assert 0.8 < r2 <= 1.0


def test_agreement_excludes_exact_ties():
    cols = ["teacher", "family_id", "variant", "p_o1", "p_o2", "p_sym", "order_gap"]
    s = pd.DataFrame([["x.y_O_s1", "f1", "T1", .5, .5, .5, 0], ["x.y_O_s1", "f2", "T1", .9, .9, .9, 0], ["x.y_O_s1", "f3", "T1", .2, .2, .2, 0]], columns=cols)
    t = pd.DataFrame([["g", "f1", "T1", .4, .4, .4, 0], ["g", "f2", "T1", .9, .9, .9, 0], ["g", "f3", "T1", .8, .8, .8, 0]], columns=cols)
    row = M.teacher_agreement(s, t, ["T1"]).iloc[0]
    assert row["n_ties"] == 1 and row["n_cells"] == 3 and row["agreement"] == pytest.approx(0.5)  # f2 agrees, f3 disagrees, f1 is a tie
    assert np.isnan(M._agreement(np.array([0.5]), np.array([0.3]))["agreement"])


def test_holm_and_pooled_inheritance(world):
    assert M.holm([0.01, 0.04, 0.03]).tolist() == pytest.approx([0.03, 0.06, 0.06])
    h = M.holm([np.nan, 0.02])
    assert np.isnan(h[0]) and h[1] == pytest.approx(0.02)
    shifts_s = P.framing_shifts(world["sym_s"], V)
    shifts_t = P.framing_shifts(world["sym_t"], V)
    own = {"qwen3-4b.alpha_O_s1": "alpha", "qwen3-4b.alpha_O_s2": "alpha", "qwen3-4b.beta_O_s1": "beta", "qwen3-4b.random_R_s1": "random"}
    pooled = M.pooled_shifts(shifts_s, ["qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2"], "pool")
    one = shifts_s[shifts_s.teacher == "qwen3-4b.alpha_O_s1"].set_index(["family_id", "variant"])["r"]
    two = shifts_s[shifts_s.teacher == "qwen3-4b.alpha_O_s2"].set_index(["family_id", "variant"])["r"]
    got = pooled.set_index(["family_id", "variant"])["r"]
    assert len(got) == N_FAM * len(V) and np.allclose(got, ((one + two) / 2).reindex(got.index))
    inh = M.pooled_inheritance(shifts_s, shifts_t, own, V, n_perm=300, n_boot=100, seed=0).set_index("run_id")
    assert set(inh.index) == {"qwen3-4b.alpha_O_pooled", "qwen3-4b.beta_O_pooled"}  # the R group has no teacher profile
    a = inh.loc["qwen3-4b.alpha_O_pooled"]
    assert a["n_seeds"] == 2 and a["seeds"] == "1,2" and a["version"] == "O" and a["teacher"] == "alpha"
    assert a["delta_rho"] > 0.5 and a["p_perm"] < 0.02 and a["p_holm"] >= a["p_perm"] and a["p_holm"] < 0.05
    assert inh["p_holm"].max() == pytest.approx(M.holm(inh["p_perm"].to_numpy()).max())


def test_seed_noise_null_and_effect():
    tab = pd.DataFrame(dict(run_id=["r1", "r2", "r3", "q1", "q2"], teacher=["A", "A", "A", "B", "B"], version=["O"] * 5, seed=[1, 2, 3, 1, 2], agree=[0.80, 0.82, 0.86, 0.70, 0.75]))
    null = M.seed_noise_null(tab, "agree").set_index(["teacher", "version"])
    a = null.loc[("A", "O")]
    assert a["n_pairs"] == 3 and a["mean"] == pytest.approx((0.02 + 0.06 + 0.04) / 3)
    assert null.loc[("B", "O"), "n_pairs"] == 1 and np.isnan(null.loc[("B", "O"), "sd"])
    assert null.loc[("all", "all"), "n_pairs"] == 4
    assert M.effect_in_null_sd(0.04, null.loc[("A", "O")]) == pytest.approx(0.04 / a["sd"])


def test_e1_table_end_to_end(world, tmp_path):
    from vcd.io import write_jsonl

    runs = {}
    for run in ("qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2", "qwen3-4b.beta_O_s1", "qwen3-4b.random_R_s1"):
        p = tmp_path / f"{run}.jsonl"
        write_jsonl(p, [r for r in world["students"] if r.teacher == run])
        runs[run] = p
    tp = {}
    for t in ("alpha", "beta"):
        p = tmp_path / f"{t}_profile.jsonl"
        write_jsonl(p, [r for r in world["teachers"] if r.teacher == t])
        tp[t] = p
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    tab = M.e1_table(runs, tp, pp, V, n_perm=200, n_boot=100).set_index("run_id")
    assert len(tab) == 4 and {"agree__alpha", "agree__beta", "jsd__alpha", "delta_rho", "p_perm", "flip_rate"} <= set(tab.columns)
    assert (tab.loc["qwen3-4b.alpha_O_s1", "agree_own"] > tab.loc["qwen3-4b.alpha_O_s1", "agree_other_max"])
    assert tab.loc["qwen3-4b.alpha_O_s1", "delta_rho"] > 0 and np.isnan(tab.loc["qwen3-4b.random_R_s1", "delta_rho"])
    assert tab.loc["qwen3-4b.random_R_s1", "teacher"] == "random" and tab.loc["qwen3-4b.random_R_s1", "seed"] == 1
    # agree_other_max must not depend on NaN ordering: a teacher without profile rows gives NaN columns
    assert not np.isnan(tab.loc["qwen3-4b.alpha_O_s1", "agree_other_max"])


def test_analysis_script_cli(world, tmp_path):
    """scripts/13 end to end on a synthetic runs/ tree: populated summary, pooled E2 verdict, smoke dirs skipped."""
    from vcd.io import write_jsonl

    runs = tmp_path / "runs"
    for run in ("qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2", "qwen3-4b.beta_O_s1", "qwen3-4b.random_R_s1"):
        d = runs / "qwen3-4b" / run.split(".", 1)[1] / "eval"
        d.mkdir(parents=True)
        write_jsonl(d / "dev_responses.jsonl", [r for r in world["students"] if r.teacher == run])
    smoke = runs / "qwen3-4b" / "_smoke_alpha_O_s1" / "eval"  # must be ignored, not become a fourth teacher
    smoke.mkdir(parents=True)
    write_jsonl(smoke / "dev_responses.jsonl", [r.model_copy(update={"teacher": "qwen3-4b._smoke_alpha_O_s1"}) for r in world["students"] if r.teacher == "qwen3-4b.alpha_O_s1"])
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in ("alpha", "beta"):
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    out = tmp_path / "e1"
    res = subprocess.run(
        [sys.executable, str(ROOT / "scripts/13_e1_analysis.py"), "--runs-dir", str(runs), "--student", "qwen3-4b", "--split", "dev",
         "--teacher-dir", str(tdir), "--teachers", "alpha,beta", "--prompts", str(pp), "--out", str(out), "--n-perm", "200", "--n-boot", "100"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    assert "skipping 1 run id" in res.stderr
    md = (out / "summary.md").read_text()
    assert "No student runs found" not in md and "alpha (2 seeds pooled" in md and "E2 PASS" in md and "- alpha: 2/2 seeds pass -> ok" in md
    tab = pd.read_csv(out / "e1_table.csv")
    assert set(tab["run_id"]) == {"qwen3-4b.alpha_O_s1", "qwen3-4b.alpha_O_s2", "qwen3-4b.beta_O_s1", "qwen3-4b.random_R_s1"}
    pooled = pd.read_csv(out / "inheritance_pooled.csv").set_index("run_id")
    assert pooled.loc["qwen3-4b.alpha_O_pooled", "p_holm"] < 0.05 and pooled.loc["qwen3-4b.beta_O_pooled", "n_seeds"] == 1
    # the --teacher-files route reaches the same tables
    res2 = subprocess.run(
        [sys.executable, str(ROOT / "scripts/13_e1_analysis.py"), "--runs-dir", str(runs), "--student", "qwen3-4b", "--split", "dev",
         "--teacher-files", f"alpha={tdir / 'alpha_dev_profile.jsonl'},beta={tdir / 'beta_dev_profile.jsonl'}", "--prompts", str(pp),
         "--out", str(tmp_path / "e1b"), "--n-perm", "50", "--n-boot", "50"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    assert pd.read_csv(tmp_path / "e1b/agreement.csv").shape == pd.read_csv(out / "agreement.csv").shape


def test_analysis_script_cli_base_only(world, tmp_path):
    """scripts/13 with only the untrained base S_0 (no O runs yet) writes a summary instead of crashing."""
    from vcd.io import write_jsonl

    d = tmp_path / "runs" / "qwen3-4b" / "base_B_s0" / "eval"
    d.mkdir(parents=True)
    write_jsonl(d / "dev_responses.jsonl", [r.model_copy(update={"teacher": "qwen3-4b.base_B_s0"}) for r in world["students"] if r.teacher == "qwen3-4b.alpha_O_s1"])
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in ("alpha", "beta"):
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    out = tmp_path / "e1"
    subprocess.run(
        [sys.executable, str(ROOT / "scripts/13_e1_analysis.py"), "--runs-dir", str(tmp_path / "runs"), "--student", "qwen3-4b", "--split", "dev",
         "--teacher-dir", str(tdir), "--teachers", "alpha,beta", "--prompts", str(pp), "--out", str(out), "--n-perm", "50", "--n-boot", "50"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )
    md = (out / "summary.md").read_text()
    assert "qwen3-4b.base_B_s0" in md and "no O runs with a matching teacher profile yet" in md
