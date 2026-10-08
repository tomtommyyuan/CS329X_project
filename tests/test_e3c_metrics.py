"""Synthetic O / F / C students for vcd.analysis.e3c_metrics and scripts/20_e3c_gap.py.

World: three teachers (alpha, beta, gamma) whose majority sides differ on a known share of the (family, variant) cells
(relative to alpha, beta flips T1 and gamma flips T1 / T3 / T5), 5 seeds x {O, F, C} per teacher. O students copy their
teacher's side on 80% of the cells (seeded per cell); F students of alpha and beta copy 98% (their gap to the reference
other teacher rises by about 0.09); gamma's F is a copy of its O; every C run is a copy of the O run of the same seed
(difference exactly 0 -> TOST -> no effect). Expected references: alpha -> beta, beta -> alpha, gamma -> beta.
"""

from __future__ import annotations

import json
import subprocess
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from vcd.analysis import e1_metrics as M
from vcd.analysis import e3_metrics as E
from vcd.analysis import e3c_metrics as G
from vcd.data.framings import make_prompts
from vcd.io import write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse

V = ["T1", "T3", "T5", "T6"]
N_FAM = 60
TEACHERS = ("alpha", "beta", "gamma")
SEEDS = (1, 2, 3, 4, 5)
STUDENT = "qwen3-4b-e2c-paired"
FLIPS = {"alpha": (), "beta": ("T1",), "gamma": ("T1", "T3", "T5")}  # variants where the teacher takes the opposite side of the base judgment
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
    rows = []
    for p in prompts.values():
        px = float(np.clip(p_fn(p.family_id, p.variant, p.order), 0.01, 0.99))
        letter = next(l for l, a in p.letter_to_action.items() if a == ("x" if px >= 0.5 else "y"))
        pl = {letter: px if p.letter_to_action[letter] == "x" else 1 - px}
        pl[[l for l in ("A", "B") if l != letter][0]] = 1 - pl[letter]
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=who, model="m", mode="profile", temperature=0.0, raw=f"Answer: {letter}", category="answer", letter=letter, choice_action=p.letter_to_action[letter], p_letters=pl, p_x=px))
    return rows


def _u(tag: str, f: str, v: str) -> float:
    return float(np.random.default_rng([zlib.crc32(tag.encode()), zlib.crc32(f.encode()), V.index(v)]).uniform())


def build_world(fresh_c: bool = False) -> dict:
    """`fresh_c`: C students re-draw the O noise (same 80% copy rate, new per-cell draws) instead of copying the O run."""
    prompts = _prompts()
    rng = np.random.default_rng(0)
    fams = sorted({p.family_id for p in prompts.values()})
    base = {f: (rng.uniform(0.15, 0.4) if rng.uniform() < 0.5 else rng.uniform(0.6, 0.85)) for f in fams}  # away from 0.5: no ties

    def tp(t: str, f: str, v: str) -> float:
        return 1 - base[f] if v in FLIPS[t] else base[f]

    def student(t: str, eps: float, tag: str):
        return lambda f, v, o: tp(t, f, v) if _u(tag, f, v) >= eps else 1 - tp(t, f, v)

    teachers, students = [], []
    for t in TEACHERS:
        teachers += _rows(t, lambda f, v, o, t=t: tp(t, f, v), prompts)
        for s in SEEDS:
            o_fn = student(t, 0.2, f"O{t}{s}")
            f_fn = student(t, 0.02, f"F{t}{s}") if t != "gamma" else o_fn
            c_fn = student(t, 0.2, f"C{t}{s}") if fresh_c else o_fn
            students += _rows(f"{STUDENT}.{t}_O_s{s}", o_fn, prompts) + _rows(f"{STUDENT}.{t}_F_s{s}", f_fn, prompts) + _rows(f"{STUDENT}.{t}_C_s{s}", c_fn, prompts)
    return dict(prompts=prompts, teachers=teachers, students=students, sym_t=M.sym_table(teachers, prompts), sym_s=M.sym_table(students, prompts))


@pytest.fixture(scope="module")
def world():
    return build_world()


@pytest.fixture(scope="module")
def analysis(world):
    return G.analyze_gap(world["sym_s"], world["sym_t"], TEACHERS, V, n_boot=300, seed=0)


# --------------------------------------------------------------------------- (3) reference other teacher


def test_reference_other_selection(analysis):
    ref = analysis.reference.set_index("teacher")
    assert list(ref.index) == list(TEACHERS)
    assert ref.loc["alpha", "reference_other"] == "beta" and ref.loc["beta", "reference_other"] == "alpha" and ref.loc["gamma", "reference_other"] == "beta"
    assert (ref["n_O_runs"] == 5).all() and not ref["tie"].any()
    assert ref.loc["alpha", "agree__beta"] > ref.loc["alpha", "agree__gamma"] and ref.loc["alpha", "agree__alpha"] == pytest.approx(0.8, abs=0.05)
    assert ref.loc["alpha", "agree_ref"] == pytest.approx(0.65, abs=0.05) and ref.loc["gamma", "agree__alpha"] == pytest.approx(0.35, abs=0.05)
    assert ref.loc["alpha", "candidates"].startswith("beta=") and ";gamma=" in ref.loc["alpha", "candidates"]
    # the choice uses the O runs only and the e1_metrics.teacher_agreement values
    ag = analysis.agreement
    o_alpha = ag[ag["run_id"].str.contains("alpha_O_") & (ag["teacher"] == "beta")]["agreement"].mean()
    assert ref.loc["alpha", "agree__beta"] == pytest.approx(o_alpha)
    # every run of a teacher uses the same reference (O, F and C)
    assert (analysis.runs.groupby("teacher")["reference_other"].nunique() == 1).all()


def test_reference_other_tie_and_edge_cases():
    grid = E.run_grid(["s.alpha_O_s1", "s.alpha_O_s2", "s.alpha_F_s1", "s.beta_O_s1"])
    ag = pd.DataFrame([
        ("s.alpha_O_s1", "alpha", 0.9), ("s.alpha_O_s1", "beta", 0.6), ("s.alpha_O_s1", "gamma", 0.7),
        ("s.alpha_O_s2", "alpha", 0.9), ("s.alpha_O_s2", "beta", 0.8), ("s.alpha_O_s2", "gamma", 0.7),
        ("s.alpha_F_s1", "alpha", 0.9), ("s.alpha_F_s1", "beta", 0.1), ("s.alpha_F_s1", "gamma", 0.99),  # F runs never enter the choice
        ("s.alpha_O_s1", "delta", 0.99),  # a teacher outside the configured list is ignored
        ("s.beta_O_s1", "beta", 0.9),  # beta's O run has no row against another teacher
    ], columns=["run_id", "teacher", "agreement"])
    ref = G.reference_other(ag, grid, ["alpha", "beta", "gamma"]).set_index("teacher")
    assert ref.loc["alpha", "reference_other"] == "beta" and bool(ref.loc["alpha", "tie"]) and ref.loc["alpha", "agree_ref"] == pytest.approx(0.7) and ref.loc["alpha", "n_O_runs"] == 2  # beta 0.7 == gamma 0.7 -> alphabetical
    assert ref.loc["alpha", "candidates"] == "beta=0.700000;gamma=0.700000" and ref.loc["alpha", "agree__alpha"] == pytest.approx(0.9)
    assert pd.isna(ref.loc["beta", "reference_other"]) and ref.loc["beta", "n_O_runs"] == 0 and np.isnan(ref.loc["beta", "agree_ref"])
    assert pd.isna(ref.loc["gamma", "reference_other"])  # no O run at all
    empty = G.reference_other(pd.DataFrame(columns=["run_id", "teacher", "agreement"]), E.run_grid([]), ["alpha"])
    assert len(empty) == 1 and pd.isna(empty.iloc[0]["reference_other"]) and list(empty.columns) == G.REF_COLS + ["agree__alpha"]


# --------------------------------------------------------------------------- (1), (2), (4) per-family gap


def test_family_tables_match_teacher_agreement_cell_weighted(analysis):
    ag = analysis.agreement.set_index(["run_id", "teacher"])["agreement"]
    ref = dict(zip(analysis.reference["teacher"], analysis.reference["reference_other"]))
    assert len(analysis.tables) == 45
    for run, d in analysis.tables.items():
        k = M.parse_run_id(run)
        assert list(d.columns) == G.FAMILY_COLS and len(d) == N_FAM and (d["n_cells_own"] == 4).all() and (d["n_ties_own"] == 0).all()
        cw_own = float((d["agree_own"] * d["n_cells_own"]).sum() / d["n_cells_own"].sum())
        cw_oth = float((d["agree_other"] * d["n_cells_other"]).sum() / d["n_cells_other"].sum())
        assert cw_own == pytest.approx(ag[(run, k.teacher)], abs=1e-12) and cw_oth == pytest.approx(ag[(run, ref[k.teacher])], abs=1e-12)
        assert np.allclose(d["gap"], d["agree_own"] - d["agree_other"])
    # complete families with the same number of non-tie cells: the family-unit mean equals the cell-weighted run value
    runs = analysis.runs
    assert len(runs) == 45 and np.abs(runs["gap"] - runs["gap_cw"]).max() < 1e-12 and np.abs(runs["agree_own"] - runs["agree_own_cw"]).max() < 1e-12
    assert (runs["gap_e2c_cw"] <= runs["gap_cw"] + 1e-12).all()  # max over the others >= the reference other
    o = runs[runs["version"] == "O"]
    assert (o["other_argmax_cw"] == o["reference_other"]).mean() > 0.8  # the fixed reference is the per-run argmax almost always


def test_family_tables_tie_rule():
    piv_s = pd.DataFrame({"T1": [0.9, 0.5], "T3": [0.9, 0.8], "T5": [0.1, 0.2], "T6": [0.1, 0.2]}, index=["f0", "f1"])
    piv_t = pd.DataFrame({"T1": [0.9, 0.9], "T3": [0.1, 0.8], "T5": [0.1, 0.9], "T6": [0.1, 0.1]}, index=["f0", "f1"])
    piv_r = pd.DataFrame({"T1": [0.1, 0.1], "T3": [0.9, 0.2], "T5": [0.9, 0.2], "T6": [0.9, 0.9]}, index=["f0", "f1"])
    grid = E.run_grid(["s.t_O_s1", "s.u_O_s1"])
    tabs = G.family_tables({"s.t_O_s1": piv_s, "s.u_O_s1": piv_s}, {"t": piv_t, "r": piv_r}, grid, {"t": "r", "u": None})
    assert set(tabs) == {"s.t_O_s1"}  # u has no reference -> not scored
    d = tabs["s.t_O_s1"]
    assert d.loc["f0", "agree_own"] == pytest.approx(0.75) and d.loc["f0", "agree_other"] == pytest.approx(0.25) and d.loc["f0", "gap"] == pytest.approx(0.5) and d.loc["f0", "n_cells_own"] == 4
    assert d.loc["f1", "n_cells_own"] == 3 and d.loc["f1", "n_ties_own"] == 1 and d.loc["f1", "n_cells_other"] == 3  # the T1 tie is dropped on both sides
    assert d.loc["f1", "agree_own"] == pytest.approx(2 / 3) and d.loc["f1", "agree_other"] == pytest.approx(1 / 3) and d.loc["f1", "gap"] == pytest.approx(1 / 3)
    # an all-tie family has an undefined gap and is excluded from the teacher's family set
    piv_all = pd.DataFrame({"T1": [0.5], "T3": [0.5], "T5": [0.5], "T6": [0.5]}, index=["f0"])
    tabs2 = G.family_tables({"s.t_O_s1": pd.concat([piv_s, piv_all.rename(index={"f0": "f2"})])}, {"t": pd.concat([piv_t, piv_all.rename(index={"f0": "f2"})]), "r": pd.concat([piv_r, piv_all.rename(index={"f0": "f2"})])}, E.run_grid(["s.t_O_s1"]), {"t": "r"})
    assert np.isnan(tabs2["s.t_O_s1"].loc["f2", "gap"]) and G.gap_families(tabs2, E.run_grid(["s.t_O_s1"])) == {"t": ["f0", "f1"]}
    assert G.gap_families(tabs2, E.run_grid(["s.t_O_s1"]), base={"t": ["f1"]}) == {"t": ["f1"]}


# --------------------------------------------------------------------------- (4), (5) statistics and verdicts


def test_gap_delta_effect_and_tost_no_effect(analysis):
    vt = analysis.verdicts.set_index("metric")
    assert list(vt.index) == ["gap F - O", "gap C - O"] and list(analysis.verdicts.columns) == G.VERDICT_COLS
    f, c = vt.loc["gap F - O"], vt.loc["gap C - O"]
    assert f["verdict"] == "effect" and f["direction"] == "+" and f["n_pass"] >= 2 and bool(f["direction_consistent"]) and f["n_teachers"] == 3 and f["n_required"] == 3 and f["n_null"] == 30 and f["df"] == 12
    assert c["verdict"] == "no effect" and c["n_pass"] == 0 and c["n_tost"] == 3 and c["direction"] == "nan"  # e3_verdict's direction = sign of the PASSING teachers; none pass
    pt = analysis.per_teacher.set_index(["teacher", "version"])
    for t in ("alpha", "beta"):
        assert pt.loc[(t, "F"), "diff"] == pytest.approx(0.09, abs=0.03) and pt.loc[(t, "F"), "ci_lo"] > 0 and pt.loc[(t, "F"), "direction"] == "+"
    assert pt.loc[("gamma", "F"), "diff"] == 0 and (pt.xs("C", level="version")["diff"] == 0).all() and (pt.xs("C", level="version")["ci_lo"] == 0).all() and (pt.xs("C", level="version")["ci_hi"] == 0).all()
    assert (pt["n_seeds"] == 5).all() and (pt["n_families"] == N_FAM).all() and (pt["metric"] == "gap").all()
    # the statistic is the seed mean of the per-seed paired differences; the levels reproduce it
    ps = analysis.per_seed
    a = ps[(ps["teacher"] == "alpha") & (ps["version"] == "F")]
    assert len(a) == 5 and a["diff"].mean() == pytest.approx(pt.loc[("alpha", "F"), "diff"]) and all(M.parse_run_id(x).seed == M.parse_run_id(y).seed for x, y in zip(a["run_v"], a["run_o"]))
    lv = analysis.levels.set_index(["teacher", "version"])
    assert len(lv) == 9 and lv.loc[("alpha", "F"), "gap"] - lv.loc[("alpha", "O"), "gap"] == pytest.approx(pt.loc[("alpha", "F"), "diff"])
    assert lv.loc[("alpha", "O"), "agree_own"] == pytest.approx(0.8, abs=0.05) and lv.loc[("alpha", "O"), "agree_other"] == pytest.approx(0.65, abs=0.05) and lv.loc[("alpha", "F"), "agree_own"] > 0.95
    assert lv.loc[("alpha", "O"), "gap"] == pytest.approx(0.15, abs=0.05) and (lv["gap_ci_lo"] <= lv["gap"]).all() and (lv["gap"] <= lv["gap_ci_hi"]).all() and (lv["n_seeds"] == 5).all()
    assert lv.loc[("alpha", "C")].drop("seeds").astype(float).equals(lv.loc[("alpha", "O")].drop("seeds").astype(float)) or np.allclose(lv.loc[("alpha", "C"), ["agree_own", "agree_other", "gap"]].astype(float), lv.loc[("alpha", "O"), ["agree_own", "agree_other", "gap"]].astype(float))
    # the per-run gap of the levels / null equals the mean over the teacher's family set of the per-family gap
    runs = analysis.runs.set_index("run_id")
    r = f"{STUDENT}.alpha_O_s1"
    assert runs.loc[r, "gap"] == pytest.approx(analysis.tables[r]["gap"].reindex(analysis.families["alpha"]).mean()) and runs.loc[r, "n_families"] == N_FAM
    # null: 30 signed O-O differences (C(5, 2) per teacher), scale-matched to the 5-seed mean with t(0.975, 12)
    null = analysis.null
    assert len(null) == 30 and set(null["teacher"]) == set(TEACHERS) and (null["version"] == "O").all() and (null["metric"] == "gap").all() and (null["seed_a"] < null["seed_b"]).all()
    assert (null["diff"] != 0).any() and G.null_df(null) == 12
    sd1 = float(np.sqrt(np.mean(null["diff"] ** 2)))
    assert f["null_sd_single"] == pytest.approx(sd1) and f["null_sd"] == pytest.approx(sd1 / np.sqrt(5)) and f["null_q95"] == pytest.approx(2.1788 * sd1 / np.sqrt(5), rel=1e-3) and f["null_q95"] < f["null_q95_single"]
    assert all(d["effect_sd"] > 2 for t, d in analysis.raw["gap F - O"]["per_teacher"].items() if t != "gamma")
    vtt = analysis.verdict_teachers
    assert len(vtt) == 6 and list(vtt.columns) == G.VERDICT_TEACHER_COLS
    fr = vtt[vtt["metric"] == "gap F - O"].set_index("teacher")
    assert bool(fr.loc["alpha", "exceeds_q95"]) and bool(fr.loc["beta", "exceeds_q95"]) and not bool(fr.loc["gamma", "exceeds_q95"]) and fr.loc["alpha", "p_null"] < 0.01 and fr.loc["alpha", "p_holm"] >= fr.loc["alpha", "p_null"]
    assert fr.loc["alpha", "stat"] == pytest.approx(pt.loc[("alpha", "F"), "diff"]) and fr.loc["alpha", "ci_lo"] == pytest.approx(pt.loc[("alpha", "F"), "ci_lo"])
    assert (vtt[vtt["metric"] == "gap C - O"]["tost"] == True).all()  # noqa: E712
    assert 0 < f["p_row"] <= 1 and np.isfinite(f["min_p_holm"])


def test_fresh_noise_c_is_not_an_effect():
    """C runs that re-draw the O noise (same copy rate, new draws) are seed noise: never an effect, at most one teacher past q95, CIs of real width."""
    w = build_world(fresh_c=True)
    a = G.analyze_gap(w["sym_s"], w["sym_t"], TEACHERS, V, n_boot=200, seed=0)
    vt = a.verdicts.set_index("metric")
    assert vt.loc["gap F - O", "verdict"] == "effect" and vt.loc["gap C - O", "verdict"] in ("no effect", "inconclusive") and vt.loc["gap C - O", "n_pass"] <= 1
    c = a.per_teacher[a.per_teacher["version"] == "C"].set_index("teacher")
    ps = a.per_seed[a.per_seed["version"] == "C"]
    assert len(ps) == 15 and (ps["diff"] != 0).sum() >= 12  # fresh draws: the per-seed paired differences are not the exact zeros of the copy world (the seed MEAN may still hit 0 on its 1/1200 grid)
    assert (c["ci_lo"] < c["ci_hi"]).all() and (c["diff"].abs() < 3 * vt.loc["gap C - O", "null_q95"]).all()
    assert (c["diff"].abs() < a.per_teacher[(a.per_teacher["version"] == "F") & (a.per_teacher["teacher"] != "gamma")]["diff"].min()).all()  # well below the F effect
    lv = a.levels.set_index(["teacher", "version"])
    assert abs(lv.loc[("alpha", "C"), "gap"] - lv.loc[("alpha", "O"), "gap"]) < 0.05 and lv.loc[("alpha", "C"), "agree_own"] == pytest.approx(0.8, abs=0.05)


def test_pending_paths(world):
    sym_s, sym_t = world["sym_s"], world["sym_t"]
    # F missing for one teacher -> the F row is pending (n_teachers 2 < 3), the C row is unaffected
    a = G.analyze_gap(sym_s[~sym_s["teacher"].str.contains("gamma_F_")], sym_t, TEACHERS, V, n_boot=50)
    vt = a.verdicts.set_index("metric")
    assert vt.loc["gap F - O", "verdict"] == "pending (n_teachers 2 < 3)" and vt.loc["gap C - O", "verdict"] == "no effect"
    assert a.inventory.set_index("teacher").loc["gamma", "paired_F"] == 0 and a.inventory.set_index("teacher").loc["gamma", "n_C"] == 5
    long = a.verdict_teachers[a.verdict_teachers["metric"] == "gap F - O"]
    assert sorted(long["teacher"]) == ["alpha", "beta"] and long["stat"].notna().all() and long["null_sd"].isna().all() and "alpha" in vt.loc["gap F - O", "teachers"]
    # O only -> both rows pending (no paired runs); the null, the levels and the reference still exist
    a = G.analyze_gap(sym_s[sym_s["teacher"].str.contains("_O_")], sym_t, TEACHERS, V, n_boot=50)
    assert (a.verdicts["verdict"] == "pending (no paired runs)").all() and len(a.null) == 30 and len(a.levels) == 3 and a.per_teacher.empty and a.per_seed.empty
    assert a.reference.set_index("teacher").loc["alpha", "reference_other"] == "beta" and len(a.runs) == 15
    # a single O seed -> the seed-pair null is undefined
    a = G.analyze_gap(sym_s[sym_s["teacher"].str.endswith("_s1")], sym_t, TEACHERS, V, n_boot=50)
    assert a.verdicts["verdict"].str.startswith("pending (seed-pair").all() and a.null.empty and a.df is None and len(a.per_teacher) == 6
    # a teacher without a profile: its runs are not scored, the others keep their references, the rows are pending
    a = G.analyze_gap(sym_s, sym_t[sym_t["teacher"] != "gamma"], TEACHERS, V, n_boot=50)
    assert not any(M.parse_run_id(r).teacher == "gamma" for r in a.tables) and len(a.runs) == 30 and a.families["gamma"] == []
    ref = a.reference.set_index("teacher")
    assert ref.loc["alpha", "reference_other"] == "beta" and ref.loc["beta", "reference_other"] == "alpha"
    assert a.verdicts.set_index("metric").loc["gap F - O", "verdict"] == "pending (n_teachers 2 < 3)" and a.df == 8 and len(a.null) == 20
    # only two teachers configured: n_required follows the configuration
    a = G.analyze_gap(sym_s[~sym_s["teacher"].str.contains("gamma")], sym_t, ("alpha", "beta"), V, n_boot=50)
    assert a.verdicts.set_index("metric").loc["gap F - O", "verdict"] == "effect" and (a.verdicts["n_required"] == 2).all()
    # a version list without C -> one row only
    a = G.analyze_gap(sym_s, sym_t, TEACHERS, V, versions=("O", "F"), n_boot=50)
    assert list(a.verdicts["metric"]) == ["gap F - O"] and list(a.inventory.columns) == ["teacher", "n_O", "n_F", "seeds_O", "seeds_F", "paired_F"]
    # nothing at all
    a = G.analyze_gap(sym_s.iloc[0:0], sym_t, TEACHERS, V, n_boot=50)
    assert (a.verdicts["verdict"] == "pending (no paired runs)").all() and a.runs.empty and a.levels.empty and a.null.empty and a.tables == {}
    assert list(a.inventory["teacher"]) == list(TEACHERS) and (a.inventory["n_O"] == 0).all() and (a.inventory["paired_F"] == 0).all()
    assert list(a.runs.columns) == G.RUN_COLS + G.CW_COLS and list(a.levels.columns) == G.LEVEL_COLS
    with pytest.raises(ValueError):
        G.analyze_gap(sym_s, sym_t, TEACHERS, V, versions=("F", "C"))


def test_determinism_under_fixed_seed(world):
    a1 = G.analyze_gap(world["sym_s"], world["sym_t"], TEACHERS, V, n_boot=200, seed=0)
    a2 = G.analyze_gap(world["sym_s"], world["sym_t"], TEACHERS, V, n_boot=200, seed=0)
    pd.testing.assert_frame_equal(a1.per_teacher, a2.per_teacher)
    pd.testing.assert_frame_equal(a1.levels, a2.levels)
    pd.testing.assert_frame_equal(a1.verdicts, a2.verdicts)
    pd.testing.assert_frame_equal(a1.runs, a2.runs)
    a3 = G.analyze_gap(world["sym_s"], world["sym_t"], TEACHERS, V, n_boot=200, seed=1)
    f1 = a1.per_teacher[(a1.per_teacher["version"] == "F") & (a1.per_teacher["teacher"] != "gamma")]
    f3 = a3.per_teacher[(a3.per_teacher["version"] == "F") & (a3.per_teacher["teacher"] != "gamma")]
    assert np.allclose(f1["diff"], f3["diff"]) and not np.allclose(f1["ci_lo"], f3["ci_lo"])  # point estimates fixed, bootstrap draws differ


# --------------------------------------------------------------------------- CLI


def _write_tree(world, tmp_path: Path, drop: tuple[str, ...] = ()) -> tuple[Path, Path, Path]:
    runs = tmp_path / "runs"
    (runs / STUDENT).mkdir(parents=True)
    for run in sorted(world["sym_s"]["teacher"].unique()):
        if any(d in run for d in drop):
            continue
        d = runs / STUDENT / run.split(".", 1)[1] / "eval"
        d.mkdir(parents=True)
        write_jsonl(d / "dev_responses.jsonl", [r for r in world["students"] if r.teacher == run])
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in TEACHERS:
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    return runs, tdir, pp


def _run20(runs: Path, tdir: Path, pp: Path, out: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/20_e3c_gap.py"), "--split", "dev", "--runs-dir", str(runs), "--student", STUDENT, "--teacher-dir", str(tdir), "--teachers", ",".join(TEACHERS), "--prompts", str(pp),
         "--out", str(out), "--n-boot", "100", *extra],
        cwd=ROOT, capture_output=True, text=True, check=True)


OUTPUTS = ("e3c_gap_verdicts.csv", "e3c_gap_by_teacher.csv", "e3c_gap_runs.csv", "e3c_gap_null.csv", "e3c_reference_other.csv", "e3c_inventory.csv", "e3c_summary.md", "e3c_gap_verdicts.json", "e3c_gap_by_seed.csv", "e3c_gap_verdict_teachers.csv")


def test_cli_full_grid(world, tmp_path):
    runs, tdir, pp = _write_tree(world, tmp_path)
    smoke = runs / STUDENT / "_smoke_alpha_O_s1" / "eval"
    smoke.mkdir(parents=True)
    write_jsonl(smoke / "dev_responses.jsonl", [r.model_copy(update={"teacher": f"{STUDENT}._smoke_alpha_O_s1"}) for r in world["students"] if r.teacher == f"{STUDENT}.alpha_O_s1"])
    out = tmp_path / "e3c"
    res = _run20(runs, tdir, pp, out)
    assert "skipping 1 run id" in res.stderr
    for f in OUTPUTS:
        assert (out / f).exists(), f
    vt = pd.read_csv(out / "e3c_gap_verdicts.csv").set_index("metric")
    assert list(vt.index) == ["gap F - O", "gap C - O"] and vt.loc["gap F - O", "verdict"] == "effect" and vt.loc["gap C - O", "verdict"] == "no effect" and (vt["n_null"] == 30).all() and (vt["df"] == 12).all()
    md = (out / "e3c_summary.md").read_text()
    assert "not yet frozen" in md and "**gap F - O：effect**" in md and "**gap C - O：no effect**" in md and "dev = freeze split" in md and "效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致" in md
    assert "## 参照 other teacher" in md and "## 每 run" in md and "family 单位与 cell 加权之差" in md
    ref = pd.read_csv(out / "e3c_reference_other.csv").set_index("teacher")
    assert ref.loc["alpha", "reference_other"] == "beta" and ref.loc["gamma", "reference_other"] == "beta" and (ref["n_O_runs"] == 5).all()
    bt = pd.read_csv(out / "e3c_gap_by_teacher.csv")
    assert len(bt) == 9 and set(bt["version"]) == {"O", "F", "C"} and bt.loc[bt["version"] == "O", "diff"].isna().all() and bt.loc[bt["version"] != "O", "diff"].notna().all()
    assert list(bt["version"][:3]) == ["O", "F", "C"] and (bt["n_families"] == N_FAM).all()
    inv = pd.read_csv(out / "e3c_inventory.csv").set_index("teacher")
    assert (inv["n_O"] == 5).all() and (inv["paired_F"] == 5).all() and (inv["paired_C"] == 5).all()
    rt = pd.read_csv(out / "e3c_gap_runs.csv")
    assert len(rt) == 45 and {"gap", "gap_cw", "gap_e2c_cw", "other_argmax_cw", "reference_other"} <= set(rt.columns) and np.abs(rt["gap"] - rt["gap_cw"]).max() < 1e-12
    null = pd.read_csv(out / "e3c_gap_null.csv")
    assert len(null) == 30 and (null["metric"] == "gap").all() and (null["version"] == "O").all()
    vj = json.loads((out / "e3c_gap_verdicts.json").read_text())
    assert vj["confirmatory"] is False and vj["verdicts"]["gap F - O"]["verdict"] == "effect" and vj["df"] == 12 and vj["reference_other"]["alpha"] == "beta" and "not yet frozen" in vj["frozen"]
    bs = pd.read_csv(out / "e3c_gap_by_seed.csv")
    assert len(bs) == 30 and set(bs["version"]) == {"F", "C"}


def test_cli_partial_grid_is_pending_and_frozen_header(world, tmp_path):
    runs, tdir, pp = _write_tree(world, tmp_path, drop=("gamma_F_",))
    out = tmp_path / "e3c"
    res = _run20(runs, tdir, pp, out, "--frozen-commit", "abc1234")
    vt = pd.read_csv(out / "e3c_gap_verdicts.csv").set_index("metric")
    assert vt.loc["gap F - O", "verdict"] == "pending (n_teachers 2 < 3)" and vt.loc["gap C - O", "verdict"] == "no effect" and "effect" not in set(vt["verdict"]) - {"no effect"}
    md = (out / "e3c_summary.md").read_text()
    assert "frozen at commit abc1234" in md and "frozen at commit abc1234" in res.stdout and "not yet frozen" not in md
    inv = pd.read_csv(out / "e3c_inventory.csv").set_index("teacher")
    assert inv.loc["gamma", "paired_F"] == 0 and inv.loc["gamma", "n_F"] == 0 and inv.loc["alpha", "paired_F"] == 5
    bt = pd.read_csv(out / "e3c_gap_by_teacher.csv")
    assert len(bt) == 8 and bt[(bt["teacher"] == "gamma") & (bt["version"] == "F")].empty


def test_cli_no_runs_is_pending(world, tmp_path):
    runs, tdir, pp = _write_tree(world, tmp_path, drop=("_O_", "_F_", "_C_"))
    out = tmp_path / "e3c"
    res = _run20(runs, tdir, pp, out)
    assert "no student responses" in res.stderr
    for f in OUTPUTS:
        assert (out / f).exists(), f
    vt = pd.read_csv(out / "e3c_gap_verdicts.csv")
    assert len(vt) == 2 and (vt["verdict"] == "pending (no paired runs)").all()
    inv = pd.read_csv(out / "e3c_inventory.csv").set_index("teacher")
    assert list(inv.index) == list(TEACHERS) and (inv["n_O"] == 0).all()
    assert pd.read_csv(out / "e3c_gap_runs.csv").empty and pd.read_csv(out / "e3c_gap_null.csv").empty
    assert "pending (no paired runs)" in (out / "e3c_summary.md").read_text()
