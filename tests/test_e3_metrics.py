"""Synthetic O / F / C students for vcd.analysis.e3_metrics and scripts/15_e3_analysis.py.

World: three teachers (alpha, beta, gamma) with distinct framing profiles; per teacher 3 seeds x {O, F, C}.
O copies the teacher plus small seed noise; F adds a large per-cell perturbation (it changes consistency, agreement
and inheritance); C copies the teacher with other seed noise (no change). A base run B has a beta-like prior.
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
from vcd.data.framings import make_prompts
from vcd.io import write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse
from vcd.teacher import profile as P

V = ["T1", "T3", "T5", "T6"]
N_FAM = 40
TEACHERS = ("alpha", "beta", "gamma")
SEEDS = (1, 2, 3)
STUDENT = "qwen3-4b-paired"
ROOT = Path(__file__).resolve().parents[1]


def _prompts() -> dict[str, Prompt]:
    out = {}
    for i in range(N_FAM):
        f = Family(family_id=f"f{i:03d}", source="daily_dilemmas", source_id=str(i), topic_group="t", situation=f"You face situation {i}.", action_x="Do x.", action_y="Do not do x.", ambiguity="high")
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
        pl[[l for l in ("A", "B") if l != letter][0]] = 1 - pl[letter]
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=who, model="m", mode="profile", temperature=0.0, raw=f"Answer: {letter}", category=category, letter=letter, choice_action=p.letter_to_action[letter], p_letters=pl, p_x=px))
    return rows


def _noise(tag: str, sd: float):
    return lambda f, v, o: np.random.default_rng([zlib.crc32(tag.encode()), zlib.crc32(f.encode()), V.index(v)]).normal(0, sd)


def build_world(homogenize_c: bool = False) -> dict:
    prompts = _prompts()
    rng = np.random.default_rng(0)
    fams = sorted({p.family_id for p in prompts.values()})
    base = {f: rng.uniform(0.25, 0.75) for f in fams}
    mag = {f: rng.uniform(0.08, 0.3) for f in fams}
    mag2 = {f: rng.uniform(0.05, 0.25) for f in fams}
    tfn = {
        "alpha": lambda f, v, o: base[f] + (mag[f] if v == "T5" else -mag[f] if v == "T6" else 0.0),
        "beta": lambda f, v, o: base[f] + (-mag2[f] if v == "T3" else mag2[f] if v == "T1" else 0.0),
        "gamma": lambda f, v, o: base[f] + (mag[f] * 0.6 if v == "T1" else -mag2[f] if v == "T5" else 0.0),
    }
    mean_t = lambda f, v, o: np.mean([tfn[t](f, v, o) for t in TEACHERS])  # noqa: E731
    teachers, students = [], []
    for t in TEACHERS:
        teachers += _rows(t, tfn[t], prompts)
        for s in SEEDS:
            o_fn = (lambda t=t, s=s: (lambda f, v, o: tfn[t](f, v, o) + _noise(f"O{t}{s}", 0.03)(f, v, o)))()
            f_fn = (lambda t=t, s=s: (lambda f, v, o: tfn[t](f, v, o) + _noise(f"F{t}{s}", 0.3)(f, v, o)))()
            if homogenize_c:
                c_fn = (lambda t=t, s=s: (lambda f, v, o: mean_t(f, v, o) + _noise(f"C{t}{s}", 0.03)(f, v, o)))()
            else:
                c_fn = (lambda t=t, s=s: (lambda f, v, o: tfn[t](f, v, o) + _noise(f"C{t}{s}", 0.03)(f, v, o)))()
            students += _rows(f"{STUDENT}.{t}_O_s{s}", o_fn, prompts) + _rows(f"{STUDENT}.{t}_F_s{s}", f_fn, prompts) + _rows(f"{STUDENT}.{t}_C_s{s}", c_fn, prompts)
    base_rows = _rows("qwen3-4b.base_B_s0", lambda f, v, o: 0.6 * tfn["beta"](f, v, o) + 0.4 * 0.5 + _noise("B", 0.03)(f, v, o), prompts, category="malformed")
    sym_t, sym_s = M.sym_table(teachers, prompts), M.sym_table(students, prompts)
    return dict(prompts=prompts, teachers=teachers, students=students, base_rows=base_rows, sym_t=sym_t, sym_s=sym_s,
                mats_s=E.cell_matrices(sym_s, V), mats_t=E.cell_matrices(sym_t, V), shifts_s=P.framing_shifts(sym_s, V), shifts_t=P.framing_shifts(sym_t, V),
                shifts_0=M.base_prior_shifts(base_rows, prompts, V), grid=E.run_grid(sorted(sym_s["teacher"].unique())))


@pytest.fixture(scope="module")
def world():
    return build_world()


@pytest.fixture(scope="module")
def homog_world():
    return build_world(homogenize_c=True)


# --------------------------------------------------------------------------- grid and per-family tables


def test_run_grid_and_pairs(world):
    g = world["grid"]
    assert len(g) == len(TEACHERS) * len(SEEDS) and set(g.columns) == {"student", "teacher", "seed", "O", "F", "C"}
    assert g["F"].notna().all() and (g["student"] == STUDENT).all()
    inv = E.grid_inventory(g).set_index("teacher")
    assert inv.loc["alpha", "n_O"] == 3 and inv.loc["alpha", "paired_F"] == 3 and inv.loc["alpha", "seeds_C"] == "1,2,3"
    pairs = E.seed_pairs(g, "F")
    assert len(pairs) == 9 and pairs[0][1].endswith("_F_s1") and pairs[0][2].endswith("_O_s1")
    g2 = E.run_grid([f"{STUDENT}.alpha_O_s1", f"{STUDENT}.alpha_F_s2", "qwen3-4b.random_R_s1", "qwen3-4b.base_B_s0", "junk"])
    assert len(g2) == 2 and g2.loc[g2["seed"] == 2, "O"].isna().all() and E.seed_pairs(g2, "F") == []


def test_family_consistency_and_compare_values():
    piv_a = pd.DataFrame({"T1": [0.9, 0.2], "T3": [0.9, 0.8], "T5": [0.1, 0.5]}, index=["f0", "f1"])
    fc = E.family_consistency(piv_a)
    assert fc.loc["f0", "flip"] == pytest.approx(2 / 3) and fc.loc["f1", "flip"] == pytest.approx(2 / 3)  # f1: (0.2,0.8) flip, (0.2,0.5) flip (0.5 counts as not > 0.5), (0.8,0.5) flip
    assert fc.loc["f0", "jsd"] > fc.loc["f1", "jsd"] * 0  # finite
    piv_b = pd.DataFrame({"T1": [0.9, 0.7], "T3": [0.1, 0.8], "T5": [0.1, 0.9]}, index=["f0", "f1"])
    cmp = E.family_compare(piv_a, piv_b)
    assert cmp.loc["f0", "disagree"] == pytest.approx(1 / 3) and cmp.loc["f0", "n_ties"] == 0
    assert cmp.loc["f1", "n_ties"] == 1 and cmp.loc["f1", "disagree"] == pytest.approx(0.5)  # T5 tie excluded; T1 differs, T3 agrees
    assert (cmp["agree"] == 1 - cmp["disagree"]).all() and cmp.loc["f0", "jsd"] > 0
    # all-tie family -> NaN disagreement, not 0
    tie = E.family_compare(pd.DataFrame({"T1": [0.5]}, index=["f"]), pd.DataFrame({"T1": [0.9]}, index=["f"]))
    assert np.isnan(tie.loc["f", "disagree"])


def test_run_scalars_and_seed_pair_null(world):
    scal = E.run_scalars(world["mats_s"], world["mats_t"])
    assert len(scal) == 27 and (scal["n_families"] == N_FAM).all() and scal["agree_own"].notna().all()
    o = scal[scal["version"] == "O"].set_index("run_id")
    f = scal[scal["version"] == "F"].set_index("run_id")
    assert o["agree_own"].min() > 0.9 and f["agree_own"].max() < o["agree_own"].min()
    null = E.seed_pair_null(scal, "flip", "O")
    assert len(null) == len(TEACHERS) * 3 and (null["abs_diff"] >= 0).all() and set(null["metric"]) == {"flip"}  # C(3,2) = 3 pairs per teacher
    assert E.null_summary(null["abs_diff"])["n"] == 9 and np.isnan(E.null_summary([])["q95"])
    spd = E.seed_pair_disagreement(world["mats_s"], world["grid"], "O")
    assert len(spd) == 9 and spd["disagree"].max() < 0.2 and (spd["seed_a"] < spd["seed_b"]).all()


# --------------------------------------------------------------------------- (1) - (3) with the verdict


def _verdict_kwargs(g: pd.DataFrame, n_seeds: int = len(SEEDS), df: int = len(TEACHERS) * (len(SEEDS) - 1)) -> dict:
    return dict(n_seeds=n_seeds, cis={r.teacher: (float(r.ci_lo), float(r.ci_hi)) for r in g.itertuples()}, df=df)


def test_disagreement_f_vs_c_exceeds_seed_pair_null(world):
    fams = E.teacher_families(world["mats_s"], world["grid"])
    assert set(fams) == set(TEACHERS) and all(len(f) == N_FAM for f in fams.values())
    dis_s, dis_t = E.cross_student_disagreement(world["mats_s"], world["grid"], n_boot=300, seed=0, families=fams)
    assert set(dis_t["pair"]) == {"F-C", "O-F", "O-C"} and len(dis_s) == 27 and (dis_t["n_seeds"] == 3).all() and dis_t["disagree_conf"].notna().all()
    spd = E.seed_pair_disagreement(world["mats_s"], world["grid"], "O", families=fams)
    ex = E.excess_disagreement(dis_t, spd)
    assert len(ex) == 9 and (ex["n_oo_pairs"] == 3).all() and ex["var_oo_mean"].notna().all() and (ex["var_oo_mean"] >= 0).all()
    a = ex[(ex["teacher"] == "alpha") & (ex["pair"] == "F-C")].iloc[0]
    assert a["oo_mean"] == pytest.approx(spd[spd["teacher"] == "alpha"]["disagree"].mean()) and a["excess"] == pytest.approx(a["disagree"] - a["oo_mean"])
    fc, oc = ex[ex["pair"] == "F-C"], ex[ex["pair"] == "O-C"]
    kw = dict(extra_var=dict(zip(ex["teacher"], ex["var_oo_mean"])), null_groups=list(spd["teacher"]), one_sided=True)
    v_fc = E.e3_verdict(dict(zip(fc["teacher"], fc["excess"])), spd["disagree"], **kw, **_verdict_kwargs(fc))
    v_oc = E.e3_verdict(dict(zip(oc["teacher"], oc["excess"])), spd["disagree"], **kw, **_verdict_kwargs(oc))
    assert v_fc["verdict"] == "effect" and v_fc["n_pass"] == 3 and (fc["ci_lo"] > v_fc["q95"]).all()
    assert v_oc["verdict"] in ("no effect", "inconclusive") and v_oc["n_pass"] == 0  # C vs O is seed noise
    assert all(0 < d["p_null"] <= 1 for d in v_fc["per_teacher"].values()) and v_fc["per_teacher"]["alpha"]["p_holm"] >= v_fc["per_teacher"]["alpha"]["p_null"]
    # the extra variance of the centring constant widens the statistic's null SD beyond sd_1 / sqrt(n_seeds)
    assert all(d["null_sd"] > v_fc["null_sd_single"] / np.sqrt(3) for d in v_fc["per_teacher"].values())
    # the family restriction keeps the null and the statistic on the same families
    assert (spd["n_families"] == N_FAM).all() and (dis_t["n_families"] == N_FAM).all()


def test_consistency_delta_f_changes_c_does_not(world):
    fams = E.teacher_families(world["mats_s"], world["grid"])
    cons_s, cons_t = E.consistency_delta(world["mats_s"], world["grid"], ("F", "C"), n_boot=300, seed=0, families=fams)
    assert set(cons_t["metric"]) == {"flip", "jsd"} and len(cons_t) == 12 and len(cons_s) == 36
    scal = E.run_scalars(world["mats_s"], world["mats_t"], families=fams)
    for metric in ("flip", "jsd"):
        null = E.seed_pair_null(scal, metric, "O")["diff"]
        f = cons_t[(cons_t["metric"] == metric) & (cons_t["version"] == "F")]
        c = cons_t[(cons_t["metric"] == metric) & (cons_t["version"] == "C")]
        vf = E.e3_verdict(dict(zip(f["teacher"], f["diff"])), null, **_verdict_kwargs(f))
        vc = E.e3_verdict(dict(zip(c["teacher"], c["diff"])), null, **_verdict_kwargs(c))
        assert vf["verdict"] == "effect" and vf["direction"] == "+" and (f["ci_lo"] > 0).all(), metric
        assert vc["verdict"] in ("no effect", "inconclusive") and vc["n_pass"] == 0 and (c["diff"].abs() < 0.25 * f["diff"].min()).all(), metric  # C - O is seed noise, well below F - O
        assert all(d["effect_sd"] > 2 for d in vf["per_teacher"].values())
        # scale matching: the statistic's null SD is the single-pair RMS / sqrt(n_seeds); q95 = t(0.975, df) * SD
        sd1 = float(np.sqrt(np.mean(np.asarray(null) ** 2)))
        assert vf["null_sd_single"] == pytest.approx(sd1) and vf["null_sd"] == pytest.approx(sd1 / np.sqrt(3)) and vf["q95"] == pytest.approx(2.4469 * sd1 / np.sqrt(3), rel=1e-3)
        assert vf["q95"] < vf["q95_single"]  # the old single-pair threshold was ~sqrt(n_seeds) too high for a seed mean
    # per-seed rows are paired by seed and the teacher rows average them
    s = cons_s[(cons_s["metric"] == "flip") & (cons_s["version"] == "F") & (cons_s["teacher"] == "alpha")]
    assert sorted(s["seed"]) == list(SEEDS) and all(M.parse_run_id(a).seed == M.parse_run_id(b).seed for a, b in zip(s["run_v"], s["run_o"]))
    t = cons_t[(cons_t["metric"] == "flip") & (cons_t["version"] == "F") & (cons_t["teacher"] == "alpha")].iloc[0]
    assert t["diff"] == pytest.approx(s["diff"].mean()) and t["n_seeds"] == 3


def test_drift_delta_direction(world):
    drift_s, drift_t = E.drift_delta(world["mats_s"], world["mats_t"], world["grid"], ("F", "C"), n_boot=300, seed=0)
    f_ag = drift_t[(drift_t["metric"] == "agree") & (drift_t["version"] == "F")]
    f_js = drift_t[(drift_t["metric"] == "jsd") & (drift_t["version"] == "F")]
    c_ag = drift_t[(drift_t["metric"] == "agree") & (drift_t["version"] == "C")]
    assert (f_ag["diff"] < 0).all() and (f_ag["ci_hi"] < 0).all() and (f_js["diff"] > 0).all() and (f_js["ci_lo"] > 0).all()
    assert (c_ag["ci_lo"] <= 0).all() and (c_ag["ci_hi"] >= 0).all()
    assert (drift_t["direction"].isin(["+", "-", "0"])).all()


def test_e3_verdict_rule_cases():
    rng = np.random.default_rng(0)
    null = list(rng.normal(0, 0.02, 30))  # single-pair O-O differences; RMS ~ 0.02 -> SD of a 5-seed mean ~ 0.009, q95 (t 12 df) ~ 0.0195
    kw = dict(n_seeds=5, df=12)
    v = E.e3_verdict({"a": 0.2, "b": 0.3, "c": 0.0}, null, **kw)
    assert v["verdict"] == "effect" and v["n_pass"] == 2 and v["direction"] == "+" and v["n_required"] == 3 and v["n_need"] == 2  # 2/3 exceed, same sign
    assert v["q95"] == pytest.approx(2.1788 * np.sqrt(np.mean(np.square(null)) / 5), rel=1e-3) and v["per_teacher"]["a"]["p_null"] < 1e-6 and v["per_teacher"]["c"]["p_null"] == pytest.approx(1.0)
    v = E.e3_verdict({"a": 0.2, "b": -0.3, "c": 0.0}, null, **kw)
    assert v["verdict"] == "inconclusive" and v["direction"] == "mixed" and v["n_pass"] == 2  # opposite signs, no CI -> cannot claim equivalence
    assert E.e3_verdict({"a": 0.2, "b": 0.0, "c": 0.0}, null, **kw)["verdict"] == "inconclusive"  # 1/3 and no CIs
    # TOST: no effect only when >= 2/3 teachers' CIs lie inside +/- 1 null SD of the statistic
    sd = E.e3_verdict({"a": 0.0, "b": 0.0, "c": 0.0}, null, **kw)["null_sd"]
    tight = {t: (-0.5 * sd, 0.5 * sd) for t in "abc"}
    wide = {t: (-2 * sd, 2 * sd) for t in "abc"}
    assert E.e3_verdict({"a": 0.001, "b": -0.001, "c": 0.0}, null, cis=tight, **kw)["verdict"] == "no effect"
    assert E.e3_verdict({"a": 0.001, "b": -0.001, "c": 0.0}, null, cis=wide, **kw)["verdict"] == "inconclusive"
    assert E.e3_verdict({"a": 0.001, "b": -0.001, "c": 0.0}, null, cis={"a": tight["a"], "b": tight["b"], "c": wide["c"]}, **kw)["verdict"] == "no effect"  # 2/3 pass the TOST
    mixed = E.e3_verdict({"a": 0.2, "b": -0.3, "c": 0.0}, null, cis=tight, **kw)
    assert mixed["verdict"] == "inconclusive" and mixed["per_teacher"]["a"]["tost"] is False  # the CI must contain the point estimate to be a TOST pass -> a: stat 0.2 outside
    # partial grids are pending, never a verdict (rule 7 presupposes the 3 teachers)
    assert E.e3_verdict({"a": 0.2}, null, **kw)["verdict"] == "pending (n_teachers 1 < 3)"
    assert E.e3_verdict({"a": 0.2, "b": 0.3}, null, **kw)["verdict"] == "pending (n_teachers 2 < 3)"
    assert E.e3_verdict({"a": 0.2, "b": 0.3}, null, n_required=2, **kw)["verdict"] == "effect"
    assert E.e3_verdict({}, null)["verdict"] == "pending (no paired runs)" and E.e3_verdict({"a": 0.2, "b": 0.1, "c": 0.0}, [0.1])["verdict"].startswith("pending (seed-pair")
    # one-sided (centred disagreement excess): negative never exceeds; q95 uses t(0.95) and the within-teacher sd of the rates
    rates = [0.05, 0.06, 0.07, 0.05, 0.08, 0.06] * 5
    groups = ["x", "x", "x", "y", "y", "y"] * 5
    one = E.e3_verdict({"a": 0.2, "b": 0.3, "c": 0.3}, rates, one_sided=True, null_groups=groups, **kw)
    assert one["verdict"] == "effect" and one["n_pass"] == 3 and one["q95"] == pytest.approx(1.7823 * one["null_sd"], rel=1e-3) and one["null_sd_single"] < np.std(rates, ddof=1) * 1.01
    assert E.e3_verdict({"a": -0.5, "b": -0.5, "c": -0.5}, rates, one_sided=True, **kw)["n_pass"] == 0
    assert E.e3_verdict({"a": -0.2, "b": -0.3, "c": -0.1}, null, **kw)["direction"] == "-"
    # extra_var widens the null SD of that teacher only
    ev = E.e3_verdict({"a": 0.0, "b": 0.0, "c": 0.0}, null, extra_var={"a": 1.0}, **kw)
    assert ev["per_teacher"]["a"]["null_sd"] > 1.0 > ev["per_teacher"]["b"]["null_sd"]
    # sensitivity column: the raw single-pair q95
    assert v["q95_single"] == pytest.approx(np.quantile(np.abs(null), 0.95)) and all("exceeds_q95_single" in d for d in v["per_teacher"].values())


def test_e3_verdict_calibrated_under_h0():
    """i.i.d. H0 world: V runs are copies of O runs' distribution; the per-teacher exceed rate of the t-scaled seed-pair null is ~5%
    (the single-pair q95 rule the review flagged gives ~0.3%)."""
    rng = np.random.default_rng(123)
    n_rep, hit, hit_single, n = 400, 0, 0, 0
    for _ in range(n_rep):
        O, Vv = rng.normal(size=(3, 5)), rng.normal(size=(3, 5))
        tab = pd.DataFrame([dict(run_id=f"s.t{t}_O_s{s}", teacher=f"t{t}", version="O", seed=s, x=O[t, s]) for t in range(3) for s in range(5)])
        null = E.seed_pair_null(tab, "x", "O")["diff"]
        v = E.e3_verdict({f"t{t}": float((Vv[t] - O[t]).mean()) for t in range(3)}, null, n_seeds=5, df=12)
        hit += v["n_pass"]
        hit_single += sum(d["exceeds_q95_single"] for d in v["per_teacher"].values())
        n += 3
    assert 0.03 <= hit / n <= 0.08, hit / n
    assert hit_single / n < 0.015


# --------------------------------------------------------------------------- (4) homogenization


def test_homogenization_drops_when_students_converge(homog_world):
    cells, per_v = E.homogenization(homog_world["mats_s"], homog_world["grid"], ("O", "F", "C"), n_boot=300, seed=0)
    pv = per_v.set_index("version")
    assert set(pv.index) == {"O", "F", "C"} and (pv["n_cells"] == 9).all() and pv.loc["O", "n_paired_cells"] == 0 and pv.loc["C", "n_paired_cells"] == 9
    assert pv.loc["C", "one_minus_corr"] < pv.loc["O", "one_minus_corr"] and pv.loc["C", "d_omc_vs_O"] < 0 and pv.loc["C", "d_omc_ci_hi"] < 0
    assert pv.loc["C", "jsd"] < pv.loc["O", "jsd"] and pv.loc["C", "d_jsd_ci_hi"] < 0
    assert pv.loc["F", "d_jsd_vs_O"] > 0 and pv.loc["F", "d_jsd_ci_lo"] > 0  # noisy students judge further apart, no drop
    assert len(cells) == 27 and (cells["n_families"] == N_FAM).all()
    assert {"maj_disagree", "maj_disagree_conf", "mean_abs_margin", "share_low_margin"} <= set(pv.columns) and pv["mean_abs_margin"].between(0, 0.5).all() and pv.loc["C", "maj_disagree"] < pv.loc["O", "maj_disagree"]


def test_homogenization_unchanged_for_clean_copy(world):
    _, per_v = E.homogenization(world["mats_s"], world["grid"], ("O", "C"), n_boot=200, seed=0)
    c = per_v.set_index("version").loc["C"]
    assert abs(c["d_omc_vs_O"]) < 0.1 and abs(c["d_jsd_vs_O"]) < 0.005  # seed noise; the homogenised world drops by ~0.9 / 0.03


# --------------------------------------------------------------------------- (5) inheritance by form


def test_inheritance_by_form_partial(world):
    runs, per_seed, per_t = E.inheritance_by_form(world["shifts_s"], world["shifts_t"], world["shifts_0"], world["grid"], V, ("F", "C"), n_boot=200, seed=0)
    assert len(runs) == 27 and (runs["control"] == "qwen3-4b.base_B_s0").all() and runs["rho_base"].notna().all()
    o = runs[runs["version"] == "O"]
    assert (o["delta_rho"] > 0).all() and (o["other_argmax"] != o["teacher"]).all()
    f = per_t[per_t["version"] == "F"]
    c = per_t[per_t["version"] == "C"]
    assert len(per_t) == 6 and (f["diff"] < 0).all() and (f["ci_hi"] < 0).all()  # a noisier student inherits less
    assert (c["ci_lo"] <= 0).all() and (c["ci_hi"] >= 0).all()
    assert len(per_seed) == 18 and per_seed["diff"].equals(per_seed["delta_rho_v"] - per_seed["delta_rho_o"])
    null = E.seed_pair_null(runs, "delta_rho", "O")
    assert len(null) == 9
    vf = E.e3_verdict(dict(zip(f["teacher"], f["diff"])), null["diff"], **_verdict_kwargs(f))
    assert vf["verdict"] == "effect" and vf["direction"] == "-"
    raw_runs, _, raw_t = E.inheritance_by_form(world["shifts_s"], world["shifts_t"], None, world["grid"], V, ("F",), n_boot=0, seed=0)
    assert raw_runs["control"].isna().all() and raw_runs["rho_base"].isna().all() and raw_t["ci_lo"].isna().all() and len(raw_t) == 3


def test_joint_D_and_suggestibility_by_version(world):
    jd, raw = E.joint_D_by_version(world["shifts_s"], world["shifts_t"], world["shifts_0"], world["grid"], V, ("O", "F", "C"), n_perm=100, n_boot=100, seed=0)
    assert list(jd["version"]) == ["O", "F", "C"] and (jd["n_teachers"] == 3).all() and jd.set_index("version").loc["O", "D"] > 0.3
    assert set(raw) == {"O", "F", "C"} and jd.set_index("version").loc["C", "ci_lo"] > 0
    sg, diffs = E.suggestibility_by_version(world["shifts_s"], world["shifts_t"], world["grid"], ("O", "F", "C"), n_boot=100, seed=0)
    assert {"students:alpha:O", "students:alpha:F", "students:alpha:C", "teacher:alpha"} <= set(sg["group"]) and (sg["ci_lo"] <= sg["s"]).all()
    d = diffs.set_index(["teacher", "version", "contrast"])
    assert len(diffs) == 6 + 9  # 3 teachers x 2 version diffs + 3 teachers x 3 versions vs teacher
    c_alpha = d.loc[("alpha", "C", "students:V - students:O")]
    assert c_alpha["ci_lo"] <= c_alpha["diff"] <= c_alpha["ci_hi"] and abs(c_alpha["diff"]) < 0.05
    s_alpha = sg.set_index("group")
    assert c_alpha["diff"] == pytest.approx(s_alpha.loc["students:alpha:C", "s"] - s_alpha.loc["students:alpha:O", "s"])
    assert d.loc[("alpha", "O", "students:V - teacher"), "diff"] == pytest.approx(s_alpha.loc["students:alpha:O", "s"] - s_alpha.loc["teacher:alpha", "s"])
    # a version listed before O still gets its s(V) - s(O) contrast, with the same sign
    _, diffs2 = E.suggestibility_by_version(world["shifts_s"], world["shifts_t"], world["grid"], ("F", "O", "C"), n_boot=50, seed=0)
    d2 = diffs2.set_index(["teacher", "version", "contrast"])
    assert len(diffs2) == 6 + 9 and d2.loc[("alpha", "F", "students:V - students:O"), "diff"] == pytest.approx(d.loc[("alpha", "F", "students:V - students:O"), "diff"])


# --------------------------------------------------------------------------- (6) content and register checks


FORMAL = ["It is important to maintain fairness; therefore, reporting the colleague ensures that company policies are upheld.",
          "Honesty is essential in this situation. Moreover, the individual should obtain consent before proceeding.",
          "Furthermore, prioritizing safety demonstrates responsibility and preserves the integrity of the team.",
          "The appropriate course of action is to assist the neighbour, as this fosters trust and sustains the community.",
          "Consequently, one should decline the offer; accepting it would undermine the commitment made previously.",
          "Respecting the agreement is necessary; nevertheless, a candid conversation regarding expectations is advisable."]
CASUAL = ["It's only fair, so you've got to tell on him. That's how the rules stay the same for everyone.",
          "Just be honest here. And ask first, it's their call, isn't it?",
          "Keep people safe first. It's your job and it keeps the team's trust.",
          "Help the neighbour out. It's the kind thing and folks will trust you more.",
          "So don't take it. You said you wouldn't, and that's that.",
          "Stick to the deal. But hey, it's fine to talk about what you both want."]


def _write_sft_tree(tmp_path: Path, prompts: dict[str, Prompt]) -> tuple[Path, Path]:
    sft, rw = tmp_path / "sft", tmp_path / "rewrites"
    sft.mkdir()
    (rw / "alpha").mkdir(parents=True)
    pids = sorted(prompts)[:12]
    letters = ["A" if i % 2 else "B" for i in range(len(pids))]
    rows = {v: [] for v in ("O", "F", "C")}
    rewrites = []
    for i, (pid, l) in enumerate(zip(pids, letters)):
        p = prompts[pid]
        o_text = f" {l}\nRationale: Reporting the colleague is important to keep things fair and uphold company policies, item {i}."
        f_text, c_text = f" {l}\nRationale: {FORMAL[i % 6]}", f" {l}\nRationale: {CASUAL[i % 6]}"
        for v, txt in (("O", o_text), ("F", f_text), ("C", c_text)):
            rows[v].append(dict(prompt_id=pid, family_id=p.family_id, variant=p.variant, order=p.order, teacher="alpha", version=v, text_prompt="x\n\nAnswer:", text_target=txt, letter=l))
        for v, txt in (("F", f_text), ("C", c_text)):
            checks = {c: True for c in E.CHECKS}
            if v == "C" and i % 4 == 0:  # a rejected first attempt, then a kept second one
                rewrites.append(dict(prompt_id=pid, teacher="alpha", version=v, attempt=0, text="Answer: " + l + "\nRationale: nope", checks={**checks, "strength": False}, kept=False))
                rewrites.append(dict(prompt_id=pid, teacher="alpha", version=v, attempt=1, text="Answer: " + l + "\n" + txt.split("\n", 1)[1], checks=checks, kept=True))
            else:
                rewrites.append(dict(prompt_id=pid, teacher="alpha", version=v, attempt=0, text="Answer: " + l + "\n" + txt.split("\n", 1)[1], checks=checks, kept=True))
    rewrites.append(dict(prompt_id="f999.T1.o1", teacher="alpha", version="F", attempt=0, text="Answer: A\nRationale: dropped", checks={c: True for c in E.CHECKS} | {"reasons": False}, kept=False))  # attempted, never kept
    for v in rows:
        write_jsonl(sft / f"alpha_{v}_s1.jsonl", rows[v])
    write_jsonl(rw / "alpha" / "rewrites.jsonl", rewrites)
    return sft, rw


def test_content_check_and_register(world, tmp_path):
    sft, rw = _write_sft_tree(tmp_path, world["prompts"])
    by_v = E.load_sft_versions(sft, "alpha", 1)
    assert set(by_v) == {"O", "F", "C"} and len(by_v["F"]) == 12 and E.load_sft_versions(sft, "beta", 1) == {}
    rewrites = E.load_rewrites(rw / "alpha" / "rewrites.jsonl")
    cc = E.content_check(by_v, rewrites).set_index("version")
    assert list(cc.index) == ["O", "F", "C"] and (cc["n_items"] == 12).all() and cc["same_prompt_set_as_O"].all()
    assert cc.loc[["F", "C"], "letter_identity_with_O"].eq(1.0).all() and cc.loc[["F", "C"], "letter_matches_rewrite"].eq(1.0).all() and cc.loc[["F", "C"], "kept_attempt_found"].eq(1.0).all()
    assert all(cc.loc[["F", "C"], f"check_{c}"].eq(1.0).all() for c in E.CHECKS) and np.isnan(cc.loc["O", "check_choice"])
    assert cc.loc["C", "mean_attempts"] == pytest.approx(1.25) and cc.loc["F", "mean_attempts"] == 1.0
    assert cc.loc["F", "n_attempted"] == 13 and cc.loc["F", "n_kept"] == 12 and cc.loc["F", "kept_share"] == pytest.approx(12 / 13)
    assert cc.loc["F", "mean_words"] > cc.loc["C", "mean_words"] * 0.8 and np.isnan(cc.loc["O", "mean_target_tokens"])
    assert E.rationale_of(" A\nRationale: hi there") == "hi there" and E.kept_attempts(rewrites, "C")[sorted(world["prompts"])[0]]["attempt"] == 1
    items, per_v = E.register_table(by_v)
    pv = per_v.set_index("version")
    assert pv.loc["F", "contraction_rate"] == 0.0 and pv.loc["C", "contraction_rate"] > 0.05
    assert pv.loc["F", "formal_connective_rate"] > pv.loc["C", "formal_connective_rate"] and pv.loc["F", "mean_word_len"] > pv.loc["C", "mean_word_len"] and pv.loc["F", "fk_grade"] > pv.loc["C", "fk_grade"]
    sep = E.register_separation(items, "F", "C", seed=0)
    assert sep["n_a"] == sep["n_b"] == 12 and sep["nearest_centroid_loo_acc"] >= 0.9 and sep["logistic_cv_acc"] >= 0.9 and sep["passes"] and sep["status"] == "pass"
    assert sep["feature_d"]["contraction_rate"] < 0 and sep["feature_d"]["formal_connective_rate"] > 0
    assert sep["nc_ci_lo"] <= sep["nearest_centroid_loo_acc"] <= sep["nc_ci_hi"] and sep["lr_ci_lo"] <= sep["logistic_cv_acc"] <= sep["lr_ci_hi"]
    # the vectorised LOO equals a brute-force loop that refits mean / sd and centroids without item i (no leakage of the held-out item)
    Xf = items[items["version"] == "F"][list(E.REGISTER_FEATURES)].to_numpy(float)
    Xc = items[items["version"] == "C"][list(E.REGISTER_FEATURES)].to_numpy(float)
    X, y = np.vstack([Xf, Xc]), np.r_[np.ones(len(Xf)), np.zeros(len(Xc))]
    hits = 0
    for i in range(len(X)):
        tr = np.arange(len(X)) != i
        mu, sd = X[tr].mean(0), X[tr].std(0, ddof=1)
        sd[sd == 0] = 1
        z = (X - mu) / sd
        c1, c0 = z[tr & (y == 1)].mean(0), z[tr & (y == 0)].mean(0)
        pred = 1.0 if np.sum((z[i] - c1) ** 2) < np.sum((z[i] - c0) ** 2) else 0.0
        hits += pred == y[i]
    assert sep["nearest_centroid_loo_acc"] == pytest.approx(hits / len(X))
    assert E.wilson_ci(9, 10) == pytest.approx((0.5958, 0.9821), abs=1e-3) and E.wilson_ci(0, 0) == (E.wilson_ci(0, 0)[0], E.wilson_ci(0, 0)[1])
    pend = E.register_separation(items[items["version"] != "C"], "F", "C")
    assert pend["status"].startswith("pending") and pend["passes"] is None
    f = E.register_features("Don't do it. It's wrong, isn't it?")
    assert f["n_sentences"] == 2 and f["n_words"] == 7 and f["contraction_rate"] == pytest.approx(3 / 7) and f["words_per_sentence"] == 3.5
    # a letter mismatch is caught
    bad = {**by_v, "C": [{**r, "letter": "A" if r["letter"] == "B" else "B"} for r in by_v["C"]]}
    assert E.content_check(bad, rewrites).set_index("version").loc["C", "letter_identity_with_O"] == 0.0


# --------------------------------------------------------------------------- CLI


def _write_runs(world, tmp_path: Path, versions=("O", "F", "C")) -> tuple[Path, Path, Path, Path]:
    runs = tmp_path / "runs"
    for run in sorted(world["sym_s"]["teacher"].unique()):
        if M.parse_run_id(run).version not in versions:
            continue
        d = runs / STUDENT / run.split(".", 1)[1] / "eval"
        d.mkdir(parents=True)
        write_jsonl(d / "dev_responses.jsonl", [r for r in world["students"] if r.teacher == run])
    smoke = runs / STUDENT / "_smoke_alpha_O_s1" / "eval"
    smoke.mkdir(parents=True)
    write_jsonl(smoke / "dev_responses.jsonl", [r.model_copy(update={"teacher": f"{STUDENT}._smoke_alpha_O_s1"}) for r in world["students"] if r.teacher == f"{STUDENT}.alpha_O_s1"])
    base = runs / "qwen3-4b" / "base_B_s0"
    (base / "eval").mkdir(parents=True)
    write_jsonl(base / "eval" / "dev_responses.jsonl", world["base_rows"])
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in TEACHERS:
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    return runs, tdir, pp, base


def _run15(runs: Path, tdir: Path, pp: Path, base: Path, out: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/15_e3_analysis.py"), "--runs-dir", str(runs), "--student", STUDENT, "--split", "dev", "--teacher-dir", str(tdir), "--teachers", ",".join(TEACHERS),
         "--prompts", str(pp), "--base-run", str(base), "--tokenizer", "none", "--out", str(out), "--n-boot", "100", "--n-perm", "50", *extra],
        cwd=ROOT, capture_output=True, text=True, check=True)


OUTPUTS = ("disagreement.csv", "consistency_delta.csv", "drift.csv", "homogenization.csv", "inheritance_by_form.csv", "joint_D_by_version.csv", "suggestibility_by_version.csv",
           "content_check.csv", "register_check.csv", "seed_pair_null.csv", "verdicts.csv", "run_inventory.csv", "summary.md")


def test_cli_full_grid(world, tmp_path):
    runs, tdir, pp, base = _write_runs(world, tmp_path)
    sft, rw = _write_sft_tree(tmp_path, world["prompts"])
    out = tmp_path / "e3"
    res = _run15(runs, tdir, pp, base, out, "--sft-dir", str(sft), "--rewrites-dir", str(rw))
    assert "skipping 1 run id" in res.stderr
    for f in OUTPUTS:
        assert (out / f).exists(), f
    md = (out / "summary.md").read_text()
    assert "## Verdicts (rule 7; descriptive on dev)" in md and RULE_ZH_IN(md) and "freeze split" in md and "qwen3-4b.base_B_s0" in md
    vt = pd.read_csv(out / "verdicts.csv").set_index("metric")
    null_result = ("no effect", "inconclusive")
    assert vt.loc["disagreement F vs C", "verdict"] == "effect" and vt.loc["disagreement O vs C", "verdict"] in null_result and vt.loc["disagreement O vs C", "n_pass"] == 0
    assert vt.loc["consistency change: flip rate F - O", "verdict"] == "effect" and vt.loc["consistency change: flip rate C - O", "verdict"] in null_result
    assert vt.loc["excess teacher drift (JSD to own teacher) F - O", "verdict"] == "effect" and vt.loc["inheritance by form: partial delta_rho F - O", "verdict"] == "effect"
    assert vt.loc["inheritance by form: partial delta_rho F - O", "direction"] == "-" and vt.loc["inheritance by form: partial delta_rho C - O", "verdict"] in null_result
    assert (vt["n_teachers"] == 3).all() and (vt["n_null"] == 9).all() and (vt["df"] == 6).all() and (vt["n_required"] == 3).all()
    assert len(vt) == 13 and (vt["tier"] == "primary").sum() == 9 and set(vt.loc[vt["tier"] == "secondary"].index) == {"disagreement O vs F", "disagreement O vs C", "teacher agreement change F - O", "teacher agreement change C - O"}
    assert vt.loc[vt["tier"] == "primary", "p_row_holm_primary"].notna().all() and vt.loc[vt["tier"] == "secondary", "p_row_holm_primary"].isna().all()
    assert (vt.loc[~vt["one_sided"], "null_q95"] < vt.loc[~vt["one_sided"], "null_q95_single"]).all() and "TOST" in vt.loc["disagreement F vs C", "teachers"]  # two-sided rows: seed-mean scaling lowers the threshold
    vj = json.loads((out / "verdicts.json").read_text())
    assert vj["confirmatory"] is False and vj["verdicts"]["disagreement F vs C"]["one_sided"] is True and vj["df"] == 6 and "not yet frozen" in vj["frozen"]
    assert (out / "disagreement_excess.csv").exists() and len(pd.read_csv(out / "disagreement_excess.csv")) == 9
    inv = pd.read_csv(out / "run_inventory.csv").set_index("teacher")
    assert (inv["n_F"] == 3).all() and (inv["paired_C"] == 3).all()
    null = pd.read_csv(out / "seed_pair_null.csv")
    assert set(null["metric"]) == {"flip", "jsd", "agree_own", "jsd_own", "disagree_O-O", "jsd_between_O-O", "delta_rho"} and (null.groupby("metric").size() == 9).all()
    hom = pd.read_csv(out / "homogenization.csv").set_index("version")
    assert list(hom.index) == ["O", "F", "C"] and hom.loc["F", "n_paired_cells"] == 9
    jd = pd.read_csv(out / "joint_D_by_version.csv").set_index("version")
    assert (jd["control"] == "qwen3-4b.base_B_s0").all() and jd.loc["O", "D"] > 0
    cc = pd.read_csv(out / "content_check.csv")
    assert set(cc["teacher"]) == {"alpha"} and (cc.loc[cc["version"] != "O", "letter_identity_with_O"] == 1.0).all() and "Letter identity with O: 100%" in md
    sep = pd.read_csv(out / "register_separation.csv").set_index(["teacher", "a", "b"])
    assert sep.loc[("alpha", "F", "C"), "status"] == "pass" and sep.loc[("alpha", "F", "C"), "nearest_centroid_loo_acc"] >= 0.9 and sep.loc[("alpha", "F", "C"), "nc_ci_lo"] <= 0.9
    assert "pending" not in " ".join(vt["verdict"])
    hom = pd.read_csv(out / "homogenization.csv")
    assert {"maj_disagree_conf", "share_low_margin"} <= set(hom.columns)


def test_cli_partial_grid_is_pending(world, tmp_path):
    """F / C runs for one teacher only: every F / C verdict row is pending (n_teachers 1 < 3), never 'effect'."""
    runs, tdir, pp, base = _write_runs(world, tmp_path)
    for run_dir in (runs / STUDENT).iterdir():
        if run_dir.name.startswith(("beta_", "gamma_")) and ("_F_" in run_dir.name or "_C_" in run_dir.name):
            for f in run_dir.rglob("*"):
                if f.is_file():
                    f.unlink()
            import shutil

            shutil.rmtree(run_dir)
    out = tmp_path / "e3"
    res = _run15(runs, tdir, pp, base, out, "--sft-dir", str(tmp_path / "no_sft"), "--rewrites-dir", str(tmp_path / "no_rw"), "--frozen-commit", "abc1234")
    vt = pd.read_csv(out / "verdicts.csv")
    assert len(vt) == 13 and vt["verdict"].str.startswith("pending (n_teachers 1 < 3)").all() and "effect" not in set(vt["verdict"])
    inv = pd.read_csv(out / "run_inventory.csv").set_index("teacher")
    assert inv.loc["alpha", "paired_F"] == 3 and inv.loc["beta", "paired_F"] == 0
    assert "frozen at commit abc1234" in (out / "summary.md").read_text() and "frozen at commit abc1234" in res.stdout


def RULE_ZH_IN(md: str) -> bool:
    return "效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致" in md


def test_cli_o_only_is_pending(world, tmp_path):
    runs, tdir, pp, base = _write_runs(world, tmp_path, versions=("O",))
    out = tmp_path / "e3"
    _run15(runs, tdir, pp, base, out, "--sft-dir", str(tmp_path / "no_sft"), "--rewrites-dir", str(tmp_path / "no_rw"))
    for f in OUTPUTS:
        assert (out / f).exists(), f
    md = (out / "summary.md").read_text()
    vt = pd.read_csv(out / "verdicts.csv")
    assert len(vt) and vt["verdict"].str.startswith("pending").all() and "pending (no paired runs)" in md
    assert pd.read_csv(out / "disagreement.csv").empty and pd.read_csv(out / "consistency_delta.csv").empty and pd.read_csv(out / "inheritance_by_form.csv").empty
    null = pd.read_csv(out / "seed_pair_null.csv")  # the O-vs-O noise reference exists without any F / C run
    assert len(null) and set(null["metric"]) >= {"flip", "agree_own", "disagree_O-O", "delta_rho"}
    hom = pd.read_csv(out / "homogenization.csv")
    assert list(hom["version"]) == ["O"] and hom["d_omc_vs_O"].isna().all()
    assert pd.read_csv(out / "content_check.csv").empty and "pending (no" in md and "rebuild with scripts/10_build_sft_data.py" in md
    inv = pd.read_csv(out / "run_inventory.csv").set_index("teacher")
    assert (inv["n_F"] == 0).all() and (inv["n_O"] == 3).all()
