"""Synthetic C / K / E1 students with known own-vs-other gaps for vcd.analysis.e2c_metrics and scripts/19_e2c_analysis.py.

World: three teachers (alpha, beta, gamma) whose judgments differ on a large share of cells (teacher-specific family
offsets). Condition C students copy their own teacher plus small seed noise (own agreement high, other agreement low:
a large positive gap); K and E1 students copy the three-teacher consensus plus seed noise (gap about 0). 5 seeds each.
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
from vcd.analysis import e2c_metrics as E
from vcd.data.framings import make_prompts
from vcd.io import write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse

V = ["T1", "T3", "T5", "T6"]
N_FAM = 40
TEACHERS = ("alpha", "beta", "gamma")
SEEDS = (1, 2, 3, 4, 5)
STUDENTS = {"C": "qwen3-4b-e2c", "K": "qwen3-4b-e2ck", "E1": "qwen3-4b"}
ROOT = Path(__file__).resolve().parents[1]
SYM_COLS = ["teacher", "family_id", "variant", "p_o1", "p_o2", "p_sym", "order_gap"]


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
        px = float(np.clip(p_fn(p.family_id, p.variant), 0.01, 0.99))
        letter = next(l for l, a in p.letter_to_action.items() if a == ("x" if px >= 0.5 else "y"))
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=who, model="m", mode="profile", temperature=0.0, raw=f"Answer: {letter}", category="answer", letter=letter, choice_action=p.letter_to_action[letter], p_x=px))
    return rows


def _noise(tag: str, sd: float):
    return lambda f, v: np.random.default_rng([zlib.crc32(tag.encode()), zlib.crc32(f.encode()), V.index(v)]).normal(0, sd)


def build_world() -> dict:
    prompts = _prompts()
    rng = np.random.default_rng(0)
    fams = sorted({p.family_id for p in prompts.values()})
    base = {f: rng.uniform(0.3, 0.7) for f in fams}
    off = {t: {f: rng.normal(0, 0.3) for f in fams} for t in TEACHERS}  # teacher-specific judgments: teachers disagree on many cells
    tfn = {t: (lambda t: (lambda f, v: base[f] + off[t][f] + (0.1 if v == "T5" else -0.1 if v == "T6" else 0.0)))(t) for t in TEACHERS}
    consensus = lambda f, v: float(np.mean([tfn[t](f, v) for t in TEACHERS]))  # noqa: E731
    teachers, students = [], {c: [] for c in STUDENTS}
    for t in TEACHERS:
        teachers += _rows(t, tfn[t], prompts)
        for s in SEEDS:
            students["C"] += _rows(f"{STUDENTS['C']}.{t}_O_s{s}", (lambda t=t, s=s: (lambda f, v: tfn[t](f, v) + _noise(f"C{t}{s}", 0.03)(f, v)))(), prompts)
            students["K"] += _rows(f"{STUDENTS['K']}.{t}_O_s{s}", (lambda t=t, s=s: (lambda f, v: consensus(f, v) + _noise(f"K{t}{s}", 0.03)(f, v)))(), prompts)
            students["E1"] += _rows(f"{STUDENTS['E1']}.{t}_O_s{s}", (lambda t=t, s=s: (lambda f, v: consensus(f, v) + _noise(f"E{t}{s}", 0.03)(f, v)))(), prompts)
    sym_t = M.sym_table(teachers, prompts)
    W = E.bootstrap_weights(len(fams), 200, 0)
    res = {c: E.analyze_condition(c, rows, prompts, sym_t, list(TEACHERS), V, fams, W) for c, rows in students.items()}
    return dict(prompts=prompts, families=fams, teachers=teachers, students=students, sym_t=sym_t, W=W, res=res)


@pytest.fixture(scope="module")
def world():
    return build_world()


# --------------------------------------------------------------------------- hand values


def _sym(rows: list[list]) -> pd.DataFrame:
    return pd.DataFrame([[t, f, "T1", p, p, p, 0.0] for t, f, p in rows], columns=SYM_COLS)


def test_hand_values_counts_gap_and_tie():
    """5 families, one variant: f3 is a tie for the student (excluded), own = 3/4, beta = 2/4 -> gap 0.25; weights [2,1,0,1,1] -> 0.8 - 0.4."""
    s = _sym([["x.alpha_O_s1", f, p] for f, p in (("f1", .9), ("f2", .2), ("f3", .5), ("f4", .8), ("f5", .9))])
    t = _sym([["alpha", f, p] for f, p in (("f1", .9), ("f2", .9), ("f3", .4), ("f4", .6), ("f5", .9))] + [["beta", f, p] for f, p in (("f1", .2), ("f2", .2), ("f3", .4), ("f4", .6), ("f5", .1))])
    tab = E.run_table(s, t, ["alpha", "beta"], ["T1"])
    r = tab.iloc[0]
    assert r["agree__alpha"] == pytest.approx(0.75) and r["agree__beta"] == pytest.approx(0.5) and r["gap"] == pytest.approx(0.25)
    assert r["agree_own"] == pytest.approx(0.75) and r["other_argmax"] == "beta" and r["n_cells_own"] == 5 and r["n_ties_own"] == 1
    fams = ["f1", "f2", "f3", "f4", "f5"]
    fc = E.family_counts(s, t, fams, ["T1"])
    assert fc.pairs == [("x.alpha_O_s1", "alpha"), ("x.alpha_O_s1", "beta")]
    assert fc.agree.tolist() == [[1, 0, 0, 1, 1], [0, 1, 0, 1, 0]] and fc.valid.tolist() == [[1, 1, 0, 1, 1], [1, 1, 0, 1, 1]]
    assert E.agreement_from_counts(fc).tolist() == pytest.approx([0.75, 0.5])
    W = np.array([[2, 1, 0, 1, 1]])
    assert E.agreement_from_counts(fc, W)[:, 0].tolist() == pytest.approx([0.8, 0.4])
    runs, G = E.gap_replicates(fc, E.agreement_from_counts(fc, W), {"x.alpha_O_s1": "alpha"}, ["alpha", "beta"])
    assert runs == ["x.alpha_O_s1"] and G[0, 0] == pytest.approx(0.4)
    # a replicate with no valid cell on either side is NaN, not 0
    W0 = np.array([[0, 0, 5, 0, 0]])
    assert np.isnan(E.agreement_from_counts(fc, W0)).all()


def test_run_table_matches_teacher_agreement(world):
    """Every agree__{teacher} is the e1_metrics.teacher_agreement value; gap = own - max other."""
    for c, res in world["res"].items():
        tab = res.run_tab.set_index("run_id")
        sym_s = M.sym_table(world["students"][c], world["prompts"])
        ag = M.teacher_agreement(sym_s, world["sym_t"], V).pivot_table(index="run_id", columns="teacher", values="agreement")
        for t in TEACHERS:
            assert np.allclose(tab[f"agree__{t}"], ag[t].reindex(tab.index)), (c, t)
        for run, r in tab.iterrows():
            own = M.parse_run_id(run).teacher
            assert r["agree_own"] == ag.at[run, own] and r["gap"] == pytest.approx(r["agree_own"] - max(ag.at[run, o] for o in TEACHERS if o != own))
        assert len(tab) == len(TEACHERS) * len(SEEDS) and set(tab["version"]) == {"O"}


def test_family_counts_reproduce_agreement_and_subsets(world):
    """Identity weights reproduce teacher_agreement exactly; 0/1 weights equal teacher_agreement on the restricted families."""
    res = world["res"]["C"]
    fc = res.counts
    assert fc is not None and len(fc.pairs) == len(TEACHERS) * len(SEEDS) * len(TEACHERS) and fc.families == world["families"]
    obs = E.agreement_from_counts(fc)
    ag = M.teacher_agreement(M.sym_table(world["students"]["C"], world["prompts"]), world["sym_t"], V).set_index(["run_id", "teacher"])["agreement"]
    assert np.allclose(obs, [ag[p] for p in fc.pairs])
    ones = np.ones((1, len(fc.families)), dtype=int)
    assert np.allclose(E.agreement_from_counts(fc, ones)[:, 0], obs)
    keep = world["families"][: N_FAM // 2]
    W = np.array([[1 if f in keep else 0 for f in fc.families]])
    sym_s = M.sym_table(world["students"]["C"], world["prompts"])
    ag_sub = M.teacher_agreement(sym_s[sym_s["family_id"].isin(keep)], world["sym_t"][world["sym_t"]["family_id"].isin(keep)], V).set_index(["run_id", "teacher"])["agreement"]
    assert np.allclose(E.agreement_from_counts(fc, W)[:, 0], [ag_sub[p] for p in fc.pairs])


# --------------------------------------------------------------------------- known gaps, null, bootstrap, verdicts


def test_known_gaps_null_and_verdicts(world):
    res = world["res"]
    gc, gk, ge = (res[c].gaps.set_index("teacher") for c in ("C", "K", "E1"))
    assert (gc["n_seeds"] == len(SEEDS)).all() and (gc["null_n_pairs"] == 10).all() and (gc["n_boot"] == 200).all() and (gc["n_boot_nan"] == 0).all()
    assert (gc["gap"] > 0.15).all() and (gc["ci_lo"] > 0).all() and (gc["ci_lo"] <= gc["gap"]).all() and (gc["gap"] <= gc["ci_hi"]).all()
    assert (gc["gap"] > gc["null_q95"]).all() and gc["passed"].all()
    for g in (gk, ge):  # consensus copies: own about equal to the others, inside the null
        assert (g["gap"].abs() < 0.08).all() and not g["passed"].any() and (g["ci_lo"] < 0).all()
    # the null is e1_metrics.seed_noise_null on agree_own
    ref = M.seed_noise_null(res["C"].run_tab[["run_id", "teacher", "version", "seed", "agree_own"]], "agree_own").set_index("teacher")
    assert np.allclose(gc["null_q95"], ref.loc[list(TEACHERS), "q95"]) and np.allclose(gc["null_sd"], ref.loc[list(TEACHERS), "sd"])
    assert (res["C"].null["teacher"] == "all").sum() == 1 and (ref.loc[list(TEACHERS), "n_pairs"] == 10).all() and ref.at["all", "n_pairs"] == 30
    pv = E.primary_verdict(res["C"].gaps, list(TEACHERS))
    assert pv["verdict"] == "PASS" and pv["n_pass"] == 3 and pv["deviations"] == [] and pv["missing"] == []
    assert E.primary_verdict(res["K"].gaps, list(TEACHERS))["verdict"] == "FAIL"
    att = E.attribution_table(res["C"].gaps, res["K"].gaps, res["C"].boot, res["K"].boot, list(TEACHERS)).set_index("teacher")
    assert np.allclose(att["diff"], gc["gap"] - gk["gap"]) and (att["ci_lo"] > 0).all() and (att["ci_lo"] <= att["diff"]).all() and (att["diff"] <= att["ci_hi"]).all()
    av = E.attribution_verdict(att.reset_index(), list(TEACHERS), True, True)
    assert av["verdict"] == "attributed to contestedness" and av["n_pass"] == 3
    # K vs E1: two consensus conditions, no attribution
    att2 = E.attribution_table(res["K"].gaps, res["E1"].gaps, res["K"].boot, res["E1"].boot, list(TEACHERS))
    assert E.attribution_verdict(att2, list(TEACHERS), True, True)["verdict"] == "not attributed"


def _fake_gaps(passed: list[bool], n_seeds: int = 5) -> pd.DataFrame:
    rows = [dict(teacher=t, n_seeds=n_seeds, seeds="1,2,3,4,5", agree_own=0.9, agree_other_max=0.8, gap=0.1, ci_lo=0.05, ci_hi=0.15, n_boot=10, n_boot_nan=0, null_n_pairs=10, null_mean=0.01, null_sd=0.005,
                 null_q95=0.02, exceeds_null=p, ci_above_zero=p, passed=p) for t, p in zip(TEACHERS, passed)]
    return pd.DataFrame(rows, columns=E.GAP_COLS)


def test_verdict_boundaries():
    T = list(TEACHERS)
    assert E.primary_verdict(_fake_gaps([True, True, True]), T)["verdict"] == "PASS"
    assert E.primary_verdict(_fake_gaps([True, False, True]), T)["verdict"] == "PASS"
    assert E.primary_verdict(_fake_gaps([False, True, False]), T)["verdict"] == "PARTIAL"
    assert E.primary_verdict(_fake_gaps([False, False, False]), T)["verdict"] == "FAIL"
    assert E.primary_verdict(None, T)["verdict"].startswith("pending") and E.primary_verdict(pd.DataFrame(columns=E.GAP_COLS), T)["verdict"].startswith("pending")
    one = _fake_gaps([True, True, True]).iloc[:2]  # gamma missing -> pending even though 2/3 pass
    assert E.primary_verdict(one, T)["verdict"] == "pending (fewer than 2 seeds for gamma)"
    four = _fake_gaps([True, True, True], n_seeds=4)
    pv = E.primary_verdict(four, T)
    assert pv["verdict"] == "PASS" and pv["deviations"] == [f"{t}: 4 seeds (planned 5)" for t in TEACHERS]
    # strict inequalities: gap == q95 does not exceed, ci_lo == 0 is not above zero (binary fractions, so the equality is exact)
    run_tab = pd.DataFrame([dict(run_id=f"s.alpha_O_s{s}", student="s", teacher="alpha", version="O", seed=s, agree__alpha=a, agree__beta=0.375, agree_own=a, agree_other_max=0.375, other_argmax="beta", gap=a - 0.375, n_cells_own=10, n_ties_own=0)
                            for s, a in ((1, 0.5), (2, 0.75))])
    null = E.seed_pair_null(run_tab)
    assert null.set_index("teacher").at["alpha", "q95"] == 0.25
    boot = {"alpha": np.array([0.0] * 2 + [0.1] * 38)}  # 2.5 % quantile exactly 0
    g = E.gap_table(run_tab, boot, null, ["alpha", "beta"]).set_index("teacher")
    assert g.at["alpha", "gap"] == 0.25 and g.at["alpha", "ci_lo"] == 0.0
    assert not g.at["alpha", "exceeds_null"] and not g.at["alpha", "ci_above_zero"] and not g.at["alpha", "passed"]
    assert g.at["beta", "n_seeds"] == 0 and not g.at["beta", "passed"] and np.isnan(g.at["beta", "gap"])
    g2 = E.gap_table(run_tab, {"alpha": np.array([0.01] * 40)}, null, ["alpha"]).set_index("teacher")
    assert g2.at["alpha", "ci_above_zero"] and not g2.at["alpha", "exceeds_null"]
    # attribution verdict thresholds and pending paths
    att = pd.DataFrame([dict(teacher=t, gap_C=0.2, gap_K=0.0, diff=0.2, ci_lo=lo, ci_hi=0.3, n_boot=10, n_boot_nan=0, ci_above_zero=lo > 0) for t, lo in zip(TEACHERS, (0.1, 0.1, -0.1))], columns=E.ATTR_COLS)
    assert E.attribution_verdict(att, T, True, True)["verdict"] == "attributed to contestedness"
    att.loc[1, ["ci_lo", "ci_above_zero"]] = [-0.05, False]
    assert E.attribution_verdict(att, T, True, True)["verdict"] == "not attributed"
    assert E.attribution_verdict(att, T, True, False)["verdict"] == "pending (no K runs)"
    assert E.attribution_verdict(att, T, False, False)["verdict"] == "pending (no C and K runs)"
    assert E.attribution_verdict(att.iloc[:2], T, True, True)["verdict"] == "pending (no paired bootstrap for gamma)"
    assert E.primary_verdict(_fake_gaps([True, True, False]), ["alpha", "beta"])["verdict"] == "PASS"  # 2/2 configured teachers


def test_bootstrap_reproducible_and_paired(world):
    W = E.bootstrap_weights(N_FAM, 200, 0)
    assert W.shape == (200, N_FAM) and (W.sum(axis=1) == N_FAM).all() and np.array_equal(W, world["W"])
    assert not np.array_equal(W, E.bootstrap_weights(N_FAM, 200, 1))
    assert E.bootstrap_weights(N_FAM, 0, 0).shape == (0, N_FAM)
    res = world["res"]["C"]
    again = E.analyze_condition("C", world["students"]["C"], world["prompts"], world["sym_t"], list(TEACHERS), V, world["families"], W)
    pd.testing.assert_frame_equal(res.gaps, again.gaps)
    for t in TEACHERS:
        assert np.array_equal(res.boot[t], again.boot[t]) and res.boot[t].shape == (200,)
    other = E.analyze_condition("C", world["students"]["C"], world["prompts"], world["sym_t"], list(TEACHERS), V, world["families"], E.bootstrap_weights(N_FAM, 200, 7))
    assert not np.allclose(other.gaps["ci_lo"], res.gaps["ci_lo"]) and np.allclose(other.gaps["gap"], res.gaps["gap"])  # the observed gap does not depend on the resampling
    # the same rows as C and K: a degenerate paired CI, difference exactly 0 in every replicate
    att = E.attribution_table(res.gaps, again.gaps, res.boot, again.boot, list(TEACHERS))
    assert (att["diff"] == 0).all() and (att["ci_lo"] == 0).all() and (att["ci_hi"] == 0).all() and not att["ci_above_zero"].any()
    assert E.attribution_verdict(att, list(TEACHERS), True, True)["verdict"] == "not attributed"


def test_empty_condition_and_descriptives(world):
    empty = E.analyze_condition("C", [], world["prompts"], world["sym_t"], list(TEACHERS), V, world["families"], world["W"])
    assert empty.run_tab.empty and empty.gaps["n_seeds"].tolist() == [0, 0, 0] and empty.counts is None and empty.boot == {} and empty.null.empty
    assert E.primary_verdict(empty.gaps, list(TEACHERS))["verdict"].startswith("pending")
    assert E.run_descriptives(empty).empty
    d = E.run_descriptives(world["res"]["C"])
    assert len(d) == len(TEACHERS) * len(SEEDS) and (d["condition"] == "C").all() and (d["answer_rate"] == 1.0).all() and (d["n_families"] == N_FAM).all()
    assert d["jsd_own"].notna().all() and d["flip_rate"].notna().all() and d["s"].notna().all() and (d["jsd_own"] < 0.05).all()
    # a run id outside the protocol is skipped, not turned into a run
    odd = [r.model_copy(update={"teacher": "qwen3-4b-e2c._smoke_alpha_O_s1"}) for r in world["students"]["C"] if r.teacher.endswith("alpha_O_s1")]
    res = E.analyze_condition("C", world["students"]["C"] + odd, world["prompts"], world["sym_t"], list(TEACHERS), V, world["families"], world["W"])
    assert res.skipped == ["qwen3-4b-e2c._smoke_alpha_O_s1"] and len(res.run_tab) == len(TEACHERS) * len(SEEDS)
    pd.testing.assert_frame_equal(res.gaps, world["res"]["C"].gaps)


def test_load_manifests_and_sft_meta(tmp_path):
    run = tmp_path / "runs" / "qwen3-4b-e2c" / "alpha_O_s1"
    (run / "eval").mkdir(parents=True)
    (run / "train_manifest.json").write_text(json.dumps({"run_id": "qwen3-4b-e2c.alpha_O_s1", "n_examples": 123, "n_target_tokens": 4567, "data_path": "x", "data_sha256": "abc"}))
    f = run / "eval" / "dev_responses.jsonl"
    f.write_text("")
    man = E.load_manifests([f, tmp_path / "nowhere" / "eval" / "dev_responses.jsonl"])
    assert len(man) == 1 and man.iloc[0]["n_examples"] == 123 and man.iloc[0]["n_target_tokens"] == 4567
    sft = tmp_path / "sft"
    sft.mkdir()
    (sft / "alpha_O_s1.meta.json").write_text(json.dumps({"n_examples": 123, "n_families": 40, "order_stable_rate": 0.9, "n_dropped_order_unstable": 4}))
    (sft / "alpha_O_s2.meta.json").write_text(json.dumps({"n_examples": 123, "n_families": 40, "order_stable_rate": 0.9, "n_dropped_order_unstable": 4}))
    meta = E.load_sft_meta(sft, ["alpha", "beta"])
    assert len(meta) == 2 and sorted(meta["seed"]) == [1, 2] and (meta["n_families"] == 40).all() and E.load_sft_meta(tmp_path / "none", ["alpha"]).empty


# --------------------------------------------------------------------------- scripts/19 end to end


def _write_tree(world, tmp_path: Path, conditions=("C", "K", "E1")) -> dict:
    runs = tmp_path / "runs"
    for c in conditions:
        for run in sorted({r.teacher for r in world["students"][c]}):
            d = runs / STUDENTS[c] / run.split(".", 1)[1]
            (d / "eval").mkdir(parents=True)
            write_jsonl(d / "eval" / "dev_responses.jsonl", [r for r in world["students"][c] if r.teacher == run])
            (d / "train_manifest.json").write_text(json.dumps({"run_id": run, "n_examples": 100 + len(run), "n_target_tokens": 5000, "data_path": "x", "data_sha256": "y"}))
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in TEACHERS:
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    return dict(runs=runs, tdir=tdir, prompts=pp)


def _cli(paths: dict, out: Path, **globs) -> subprocess.CompletedProcess:
    g = {c: str(paths["runs"] / STUDENTS[c] / "*_O_s*" / "eval" / "{split}_responses.jsonl") for c in STUDENTS}
    g.update(globs)
    return subprocess.run(
        [sys.executable, str(ROOT / "scripts/19_e2c_analysis.py"), "--split", "dev", "--c-glob", g["C"], "--k-glob", g["K"], "--e1-glob", g["E1"], "--teacher-dir", str(paths["tdir"]),
         "--teachers", ",".join(TEACHERS), "--prompts", str(paths["prompts"]), "--out", str(out), "--n-boot", "200", "--frozen-commit", "deadbee"],
        cwd=ROOT, capture_output=True, text=True, check=True,
    )


def test_analysis_script_cli(world, tmp_path):
    paths = _write_tree(world, tmp_path)
    smoke = paths["runs"] / STUDENTS["C"] / "_smoke_alpha_O_s1" / "eval"  # must be skipped, not become a run
    smoke.mkdir(parents=True)
    write_jsonl(smoke / "dev_responses.jsonl", [r.model_copy(update={"teacher": "qwen3-4b-e2c._smoke_alpha_O_s1"}) for r in world["students"]["C"] if r.teacher.endswith("alpha_O_s1")])
    out = tmp_path / "e2c"
    res = _cli(paths, out)
    assert "skipping 1 run id" in res.stderr
    for name in ("e2c_gaps.csv", "e2c_attribution.csv", "e2c_verdict.json", "e2c_runs.csv", "e2c_agreement.csv", "e2c_jsd.csv", "e2c_consistency.csv", "e2c_seed_null.csv", "e2c_summary.md"):
        assert (out / name).exists(), name
    v = json.loads((out / "e2c_verdict.json").read_text())
    assert v["primary"]["verdict"] == "PASS" and v["primary"]["n_pass"] == 3 and v["attribution"]["verdict"] == "attributed to contestedness" and v["missing_conditions"] == []
    assert v["reference_rows_under_the_same_rule"]["K"]["n_pass"] == 0 and v["descriptive_only"] is True and v["n_boot"] == 200 and "deadbee" in v["freeze"]
    gaps = pd.read_csv(out / "e2c_gaps.csv")
    assert set(gaps["condition"]) == {"C", "K", "E1"} and len(gaps) == 9 and gaps[gaps["condition"] == "C"]["passed"].all()
    runs = pd.read_csv(out / "e2c_runs.csv")
    assert len(runs) == 45 and runs["n_examples"].notna().all() and set(runs["condition"]) == {"C", "K", "E1"}
    md = (out / "e2c_summary.md").read_text()
    assert "**E2c primary（own > other，条件 C）：PASS**" in md and "attributed to contestedness" in md and "dev 只作描述" in md and "frozen at commit deadbee" in md
    att = pd.read_csv(out / "e2c_attribution.csv")
    assert (att["ci_above_zero"]).all() and len(att) == 3


def test_analysis_script_cli_missing_conditions(world, tmp_path):
    """Only E1 exists: C and K are reported missing, the verdicts are pending, the reference row is still computed."""
    paths = _write_tree(world, tmp_path, conditions=("E1",))
    out = tmp_path / "e2c"
    res = _cli(paths, out)
    assert "C: no files match" in res.stderr and "K: no files match" in res.stderr
    v = json.loads((out / "e2c_verdict.json").read_text())
    assert v["primary"]["verdict"] == "pending (no runs)" and v["attribution"]["verdict"] == "pending (no C and K runs)" and v["missing_conditions"] == ["C", "K"]
    gaps = pd.read_csv(out / "e2c_gaps.csv")
    assert set(gaps["condition"]) == {"E1"} and len(gaps) == 3 and not gaps["passed"].any()
    md = (out / "e2c_summary.md").read_text()
    assert "缺失条件" in md and "pending (no runs)" in md
    assert pd.read_csv(out / "e2c_attribution.csv").empty
