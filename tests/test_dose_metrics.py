"""Synthetic 4-share worlds for vcd.analysis.dose_metrics and scripts/24_dose_response.py.

Dose world: three teachers (alpha, beta, gamma) with teacher-specific family offsets; the student trained at contested share p
copies its own teacher on the first round(p * N) families and the three-teacher consensus on the rest (+ seed noise), so the
own-vs-other gap grows linearly with p. Flat world: every student copies the consensus (+ noise), gap about 0 at every p.
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

from vcd.analysis import dose_metrics as D
from vcd.analysis import e1_metrics as M
from vcd.analysis import e2c_metrics as E
from vcd.data.framings import make_prompts
from vcd.io import write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse

V = ["T1", "T3", "T5", "T6"]
N_FAM = 40
TEACHERS = ("alpha", "beta", "gamma")
SEEDS = (1, 2, 3, 4, 5)
SHARES = (0.0, 0.25, 0.5, 1.0)
STUDENTS = {0.0: "qwen3-4b-e2ckn", 0.25: "qwen3-4b-e2cmix25", 0.5: "qwen3-4b-e2cmix50", 1.0: "qwen3-4b-e2c"}
ROOT = Path(__file__).resolve().parents[1]
N_BOOT = 200


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


def build_world(mode: str) -> dict:
    prompts = _prompts()
    rng = np.random.default_rng(0)
    fams = sorted({p.family_id for p in prompts.values()})
    base = {f: rng.uniform(0.3, 0.7) for f in fams}
    off = {t: {f: rng.normal(0, 0.3) for f in fams} for t in TEACHERS}
    tfn = {t: (lambda t: (lambda f, v: base[f] + off[t][f] + (0.1 if v == "T5" else -0.1 if v == "T6" else 0.0)))(t) for t in TEACHERS}
    consensus = lambda f, v: float(np.mean([tfn[t](f, v) for t in TEACHERS]))  # noqa: E731
    teachers, students = [], {p: [] for p in SHARES}
    for t in TEACHERS:
        teachers += _rows(t, tfn[t], prompts)
        for p in SHARES:
            own_set = set(fams[: round(p * N_FAM)]) if mode == "dose" else set()
            for s in SEEDS:
                fn = (lambda t=t, s=s, p=p, own_set=own_set: (lambda f, v: (tfn[t](f, v) if f in own_set else consensus(f, v)) + _noise(f"{mode}{t}{s}{p}", 0.03)(f, v)))()
                students[p] += _rows(f"{STUDENTS[p]}.{t}_O_s{s}", fn, prompts)
    sym_t = M.sym_table(teachers, prompts)
    W = E.bootstrap_weights(len(fams), N_BOOT, 0)
    res = {p: E.analyze_condition(D.share_key(p), rows, prompts, sym_t, list(TEACHERS), V, fams, W) for p, rows in students.items()}
    reps = {p: D.run_gap_replicates(r, W, list(TEACHERS)) for p, r in res.items()}
    runs = pd.concat([E.run_descriptives(r).assign(share=p) for p, r in res.items()], ignore_index=True)
    runs.insert(0, "share", runs.pop("share"))
    return dict(prompts=prompts, families=fams, teachers=teachers, students=students, sym_t=sym_t, W=W, res=res, reps=reps, runs=runs)


@pytest.fixture(scope="module")
def dose():
    return build_world("dose")


@pytest.fixture(scope="module")
def flat():
    return build_world("flat")


# --------------------------------------------------------------------------- pure functions


def test_ols_slope_hand_values():
    x = [0.0, 0.0, 1.0, 1.0]
    Y = np.array([[0.0, 1.0, 0.0, 2.0], [0.0, 1.0, np.nan, 2.0], [1.0, 1.0, 1.0, 3.0], [1.0, 1.0, 1.0, 5.0]])
    s = D.ols_slope(x, Y)
    assert s.tolist() == pytest.approx([1.0, 0.0, 1.0, 2.0])  # column 3: the NaN row is dropped, slope still 1; column 4: means 1.5 -> 4
    assert np.isnan(D.ols_slope([0.0, 0.0, 1.0], np.array([[1.0], [2.0], [np.nan]]))[0])  # one distinct x left
    assert np.isnan(D.ols_slope([0.0, 0.0], [1.0, 2.0])[0])
    # balanced seeds: the per-run slope equals the slope through the share means
    x4 = np.repeat(SHARES, 5)
    y = np.array([p * 0.3 + 0.01 * ((i % 5) - 2) for p in SHARES for i in range(5)])
    means = [y[x4 == p].mean() for p in SHARES]
    assert D.ols_slope(x4, y)[0] == pytest.approx(D.ols_slope(list(SHARES), np.array(means))[0]) == pytest.approx(0.3)
    with pytest.raises(ValueError):
        D.ols_slope([0.0, 1.0], np.zeros((3, 1)))


def test_parse_conditions_and_labels():
    g = D.parse_conditions(D.DEFAULT_CONDITIONS, "dev")
    assert list(g) == [0.0, 0.25, 0.5, 1.0]
    assert g[0.0] == "runs/qwen3-4b-e2ckn/*_O_s*/eval/dev_responses.jsonl" and g[1.0] == "runs/qwen3-4b-e2c/*_O_s*/eval/dev_responses.jsonl"
    assert g[0.25] == "runs/qwen3-4b-e2cmix25/*_O_s*/eval/dev_responses.jsonl" and g[0.5] == "runs/qwen3-4b-e2cmix50/*_O_s*/eval/dev_responses.jsonl"
    assert D.parse_conditions("1=b/{split}.jsonl, 0=a", "test") == {0.0: "a", 1.0: "b/test.jsonl"}
    for bad in ("0=a,0=b", "2=a", "noequals"):
        with pytest.raises(ValueError):
            D.parse_conditions(bad, "dev")
    assert [D.share_key(p) for p in SHARES] == ["0", "0.25", "0.5", "1"]
    assert D.condition_label(0.0).startswith("K_n") and D.condition_label(1.0).startswith("C (p = 1") and D.condition_label(0.5).startswith("mix (p = 0.5")


# --------------------------------------------------------------------------- known worlds


def test_dose_world_supported(dose):
    res, runs = dose["res"], dose["runs"]
    gaps = {p: r.gaps.set_index("teacher")["gap"] for p, r in res.items()}
    for t in TEACHERS:  # the gap rises with p
        assert gaps[0.0][t] < gaps[0.25][t] < gaps[0.5][t] < gaps[1.0][t] and gaps[1.0][t] > 0.15
    slopes = D.slope_table(runs, dose["reps"], list(TEACHERS))
    assert len(slopes) == 9 and set(slopes["metric"]) == set(D.METRICS)
    g = slopes[slopes["metric"] == "gap"].set_index("teacher")
    assert (g["n_runs"] == 20).all() and (g["n_shares"] == 4).all() and (g["shares"] == "0,0.25,0.5,1").all() and g["complete"].all()
    assert (g["slope"] > 0.15).all() and (g["ci_lo"] > 0).all() and (g["ci_lo"] <= g["slope"]).all() and (g["slope"] <= g["ci_hi"]).all()
    assert (g["n_boot"] == N_BOOT).all() and (g["n_boot_nan"] == 0).all() and g["ci_above_zero"].all() and (g["spearman_rho"] == 1.0).all()
    for t in TEACHERS:  # balanced seeds: slope through the seed-mean gaps, intercept consistent
        x = np.array(SHARES)
        y = np.array([gaps[p][t] for p in SHARES])
        assert g.at[t, "slope"] == pytest.approx(D.ols_slope(x, y)[0]) and g.at[t, "intercept"] == pytest.approx(y.mean() - g.at[t, "slope"] * x.mean())
        assert g.at[t, "seed_means"] == "; ".join(f"{D.share_key(p)}:{gaps[p][t]:.4f}" for p in SHARES)
    cost = slopes[slopes["metric"] != "gap"]
    assert cost["slope"].notna().all() and cost["ci_lo"].isna().all() and (cost["n_boot"] == 0).all() and not cost["ci_above_zero"].any()
    v = D.dose_verdict(slopes, list(TEACHERS), list(res), runs=runs)
    assert v["verdict"] == "dose-response supported" and v["n_pass"] == 3 and v["passing"] == list(TEACHERS)
    assert v["shares_present"] == ["0", "0.25", "0.5", "1"] and v["shares_missing"] == [] and v["incomplete_teachers"] == [] and v["deviations"] == []
    # curve table: the e2c gap rows unchanged plus seed-mean flip_rate and s
    curve = D.curve_table({p: r.gaps for p, r in res.items()}, runs)
    assert len(curve) == 12 and list(curve["share"].unique()) == list(SHARES) and curve["flip_rate"].notna().all() and curve["s"].notna().all()
    for p, r in res.items():
        c = curve[curve["share"] == p].reset_index(drop=True)
        pd.testing.assert_frame_equal(c[E.GAP_COLS], r.gaps[E.GAP_COLS])
        o = runs[(runs["share"] == p)]
        for t in TEACHERS:
            assert c.set_index("teacher").at[t, "s"] == pytest.approx(o[o["teacher"] == t]["s"].mean())


def test_run_gap_replicates_match_condition_bootstrap(dose):
    for p, r in dose["res"].items():
        runs, G = dose["reps"][p]
        assert len(runs) == 15 and G.shape == (15, N_BOOT) and np.isfinite(G).all()
        own = {rid: M.parse_run_id(rid).teacher for rid in runs}
        for t in TEACHERS:
            rows = [i for i, rid in enumerate(runs) if own[rid] == t]
            assert np.allclose(G[rows].mean(axis=0), r.boot[t])
        obs = r.run_tab.set_index("run_id")["gap"]  # identity weights reproduce the observed per-run gap
        ones = np.ones((1, N_FAM), dtype=int)
        _, G1 = E.gap_replicates(r.counts, E.agreement_from_counts(r.counts, ones), own, list(TEACHERS))
        assert np.allclose(G1[:, 0], [obs[rid] for rid in runs])
    empty = E.analyze_condition("0", [], dose["prompts"], dose["sym_t"], list(TEACHERS), V, dose["families"], dose["W"])
    runs, G = D.run_gap_replicates(empty, dose["W"], list(TEACHERS))
    assert runs == [] and G.shape == (0, N_BOOT)


def test_flat_world_not_supported(flat):
    slopes = D.slope_table(flat["runs"], flat["reps"], list(TEACHERS))
    g = slopes[slopes["metric"] == "gap"].set_index("teacher")
    assert (g["slope"].abs() < 0.05).all() and (g["ci_lo"] < 0).all() and (g["ci_hi"] > 0).all() and not g["ci_above_zero"].any()
    v = D.dose_verdict(slopes, list(TEACHERS), list(flat["res"]), runs=flat["runs"])
    assert v["verdict"] == "not supported" and v["n_pass"] == 0


def test_incomplete_curve_pending(dose):
    """Only p = 0 and p = 1: slopes are descriptive two-point differences (= the e2c attribution), the verdict is pending."""
    res, runs = dose["res"], dose["runs"]
    two = runs[runs["share"].isin([0.0, 1.0])]
    slopes = D.slope_table(two, {p: dose["reps"][p] for p in (0.0, 1.0)}, list(TEACHERS))
    g = slopes[slopes["metric"] == "gap"].set_index("teacher")
    assert (g["n_runs"] == 10).all() and (g["shares"] == "0,1").all() and not g["complete"].any() and g["spearman_rho"].isna().all()
    att = E.attribution_table(res[1.0].gaps, res[0.0].gaps, res[1.0].boot, res[0.0].boot, list(TEACHERS)).set_index("teacher")
    for t in TEACHERS:
        assert g.at[t, "slope"] == pytest.approx(att.at[t, "diff"]) and g.at[t, "ci_lo"] == pytest.approx(att.at[t, "ci_lo"]) and g.at[t, "ci_hi"] == pytest.approx(att.at[t, "ci_hi"])
    v = D.dose_verdict(slopes, list(TEACHERS), [0.0, 1.0], runs=two)
    assert v["verdict"] == "pending (curve incomplete: shares present 0, 1; missing 0.25, 0.5; teachers without a full curve: alpha, beta, gamma)"
    assert v["shares_missing"] == ["0.25", "0.5"] and v["n_pass"] == 0
    # a teacher missing from one present share is also incomplete; a 4-seed share is a deviation, not a block
    partial = runs[~((runs["teacher"] == "gamma") & (runs["share"] == 0.5))]
    v2 = D.dose_verdict(D.slope_table(partial, dose["reps"], list(TEACHERS)), list(TEACHERS), list(res), runs=partial)
    assert v2["verdict"].startswith("pending (curve incomplete") and v2["incomplete_teachers"] == ["gamma"] and v2["shares_missing"] == []
    four = runs[~((runs["teacher"] == "alpha") & (runs["share"] == 0.25) & (runs["seed"] == 5))]
    v3 = D.dose_verdict(D.slope_table(four, dose["reps"], list(TEACHERS)), list(TEACHERS), list(res), runs=four)
    assert v3["verdict"] == "dose-response supported" and v3["deviations"] == ["alpha @ p=0.25: 4 seeds (planned 5)"]


def _fake_slopes(ci_lo: list[float]) -> pd.DataFrame:
    rows = [dict(teacher=t, metric="gap", n_runs=20, n_shares=4, shares="0,0.25,0.5,1", complete=True, slope=0.1, intercept=0.0, ci_lo=lo, ci_hi=0.2, n_boot=10, n_boot_nan=0,
                 ci_above_zero=lo > 0, spearman_rho=1.0, seed_means="") for t, lo in zip(TEACHERS, ci_lo)]
    return pd.DataFrame(rows, columns=D.SLOPE_COLS)


def test_verdict_thresholds():
    T = list(TEACHERS)
    assert D.dose_verdict(_fake_slopes([0.1, 0.1, 0.1]), T, SHARES)["verdict"] == "dose-response supported"
    assert D.dose_verdict(_fake_slopes([0.1, -0.1, 0.1]), T, SHARES)["verdict"] == "dose-response supported"
    assert D.dose_verdict(_fake_slopes([-0.1, 0.1, -0.1]), T, SHARES)["verdict"] == "partial"
    assert D.dose_verdict(_fake_slopes([-0.1, -0.1, -0.1]), T, SHARES)["verdict"] == "not supported"
    assert D.dose_verdict(_fake_slopes([0.0, 0.1, 0.1]), T, SHARES)["n_pass"] == 2  # strict: ci_lo == 0 does not pass
    assert D.dose_verdict(_fake_slopes([0.1, 0.1, 0.1]).iloc[:2], T, SHARES)["verdict"].startswith("pending (curve incomplete")  # gamma has no row
    assert D.dose_verdict(_fake_slopes([0.1, 0.1, 0.1]), T, [0.0, 0.5, 1.0])["shares_missing"] == ["0.25"]
    assert D.dose_verdict(pd.DataFrame(columns=D.SLOPE_COLS), T, [])["verdict"] == "pending (curve incomplete: shares present none; missing 0, 0.25, 0.5, 1; teachers without a full curve: alpha, beta, gamma)"


# --------------------------------------------------------------------------- scripts/24 end to end


def _write_tree(world, tmp_path: Path) -> dict:
    runs = tmp_path / "runs"
    for p, rows in world["students"].items():
        for run in sorted({r.teacher for r in rows}):
            d = runs / STUDENTS[p] / run.split(".", 1)[1]
            (d / "eval").mkdir(parents=True)
            write_jsonl(d / "eval" / "dev_responses.jsonl", [r for r in rows if r.teacher == run])
            (d / "train_manifest.json").write_text(json.dumps({"run_id": run, "n_examples": 1000, "n_target_tokens": 5000, "data_path": "x", "data_sha256": "y"}))
    tdir = tmp_path / "teachers"
    tdir.mkdir()
    for t in TEACHERS:
        write_jsonl(tdir / f"{t}_dev_profile.jsonl", [r for r in world["teachers"] if r.teacher == t])
    pp = tmp_path / "prompts.jsonl"
    write_jsonl(pp, world["prompts"].values())
    return dict(runs=runs, tdir=tdir, prompts=pp)


def _cli(paths: dict, out: Path, shares=SHARES, *extra) -> subprocess.CompletedProcess:
    conds = ",".join(f"{D.share_key(p)}={paths['runs'] / STUDENTS[p] / '*_O_s*' / 'eval' / '{split}_responses.jsonl'}" for p in shares)
    return subprocess.run([sys.executable, str(ROOT / "scripts/24_dose_response.py"), "--split", "dev", "--conditions", conds, "--teacher-dir", str(paths["tdir"]),
                           "--teachers", ",".join(TEACHERS), "--prompts", str(paths["prompts"]), "--out", str(out), "--n-boot", str(N_BOOT), *extra],
                          cwd=ROOT, capture_output=True, text=True, check=True)


def test_analysis_script_cli(dose, tmp_path):
    paths = _write_tree(dose, tmp_path)
    out = tmp_path / "dose"
    _cli(paths, out, SHARES, "--frozen-commit", "deadbee")
    for name in ("dose_gaps.csv", "dose_slopes.csv", "dose_runs.csv", "dose_verdict.json", "dose_summary.md"):
        assert (out / name).exists(), name
    v = json.loads((out / "dose_verdict.json").read_text())
    assert v["verdict"]["verdict"] == "dose-response supported" and v["verdict"]["n_pass"] == 3 and v["missing_conditions"] == [] and v["n_boot"] == N_BOOT
    assert "frozen at commit deadbee" in v["freeze"] and v["descriptive_only"] is True and list(v["conditions"]) == ["0", "0.25", "0.5", "1"]
    gaps = pd.read_csv(out / "dose_gaps.csv")
    assert len(gaps) == 12 and gaps["share"].tolist() == sorted(gaps["share"]) and gaps["flip_rate"].notna().all()
    for p, r in dose["res"].items():  # the per-share rows are the e2c gap rows (same W)
        g = gaps[gaps["share"] == p].set_index("teacher")
        ref = r.gaps.set_index("teacher")
        for t in TEACHERS:
            assert g.at[t, "gap"] == pytest.approx(ref.at[t, "gap"], abs=1e-12) and g.at[t, "ci_lo"] == pytest.approx(ref.at[t, "ci_lo"], abs=1e-12)
    slopes = pd.read_csv(out / "dose_slopes.csv")
    assert len(slopes) == 9 and slopes[slopes["metric"] == "gap"]["ci_above_zero"].all()
    runs = pd.read_csv(out / "dose_runs.csv")
    assert len(runs) == 60 and (runs["n_examples"] == 1000).all() and set(runs["share"]) == set(SHARES)
    md = (out / "dose_summary.md").read_text()
    assert "**剂量反应判定：dose-response supported**" in md and "frozen at commit deadbee" in md and "dev 只作描述" in md and "曲线不完整" not in md


def test_analysis_script_cli_incomplete(dose, tmp_path):
    """Only p = 0 and p = 1 exist (the situation today): missing conditions are reported, the verdict pending, nothing crashes."""
    paths = _write_tree(dose, tmp_path)
    out = tmp_path / "dose"
    res = _cli(paths, out)
    conds = ",".join([f"0={paths['runs'] / STUDENTS[0.0] / '*_O_s*' / 'eval' / '{split}_responses.jsonl'}", f"0.25={tmp_path / 'nowhere25' / '*' / '{split}.jsonl'}",
                      f"0.5={tmp_path / 'nowhere50' / '*' / '{split}.jsonl'}", f"1={paths['runs'] / STUDENTS[1.0] / '*_O_s*' / 'eval' / '{split}_responses.jsonl'}"])
    res = subprocess.run([sys.executable, str(ROOT / "scripts/24_dose_response.py"), "--split", "dev", "--conditions", conds, "--teacher-dir", str(paths["tdir"]), "--teachers", ",".join(TEACHERS),
                          "--prompts", str(paths["prompts"]), "--out", str(out), "--n-boot", str(N_BOOT)], cwd=ROOT, capture_output=True, text=True, check=True)
    assert "p = 0.25: no files match" in res.stderr and "p = 0.5: no files match" in res.stderr
    v = json.loads((out / "dose_verdict.json").read_text())
    assert v["verdict"]["verdict"].startswith("pending (curve incomplete: shares present 0, 1; missing 0.25, 0.5") and v["missing_conditions"] == ["0.25", "0.5"]
    assert "not yet frozen" in v["freeze"]
    gaps = pd.read_csv(out / "dose_gaps.csv")
    assert set(gaps["share"]) == {0.0, 1.0} and len(gaps) == 6
    slopes = pd.read_csv(out / "dose_slopes.csv").set_index(["teacher", "metric"])
    att = E.attribution_table(dose["res"][1.0].gaps, dose["res"][0.0].gaps, dose["res"][1.0].boot, dose["res"][0.0].boot, list(TEACHERS)).set_index("teacher")
    for t in TEACHERS:
        assert slopes.at[(t, "gap"), "slope"] == pytest.approx(att.at[t, "diff"]) and slopes.at[(t, "gap"), "ci_lo"] == pytest.approx(att.at[t, "ci_lo"])
        assert np.isnan(slopes.at[(t, "gap"), "spearman_rho"]) and not slopes.at[(t, "gap"), "complete"]
    md = (out / "dose_summary.md").read_text()
    assert "曲线不完整" in md and "缺失条件" in md and "not yet frozen" in md and "pending (curve incomplete" in md
