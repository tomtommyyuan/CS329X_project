"""Synthetic world for vcd.analysis.provenance and scripts/21_provenance.py (E7 black-box provenance, tasks/e7_plan.md).

World: three teachers (alpha, beta, gamma) whose majority sides differ on about half of the (family, variant) cells; an
untrained base S_0 whose prior leans to beta (its side is beta's on 60% of the cells, alpha's and gamma's on 20% each) and
answers with a letter on only 30% of the prompts, like the real base; students that copy their own teacher's side on a
tunable share q of the cells and the base prior elsewhere (E2c_C / E3c: q = 0.95; E1 / E3: q = 0.2); consensus students K / K_n that mix the base prior and the
three-teacher majority (distilled, no specific teacher); random-label students R; O / F / C versions for the paired
grids. Ground truth and grid labels follow the real namespace layout, including the E3 namespace whose rows carry the
E1 prefix 'qwen3-4b.'.
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
from vcd.analysis import provenance as PV
from vcd.data.framings import make_prompts
from vcd.io import write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse

V = ["T1", "T3", "T5", "T6"]
N_FAM = 30
TEACHERS = ("alpha", "beta", "gamma")
ROOT = Path(__file__).resolve().parents[1]
# namespace -> (grid, versions, seeds, copy share q of the own teacher; None = consensus); the prefix inside the rows mimics the real files
LAYOUT = {
    "qwen3-4b": ("E1", ("O",), (1, 2, 3, 4, 5), 0.2, "qwen3-4b"),
    "qwen3-4b-e2c": ("E2c_C", ("O",), (1, 2, 3, 4, 5), 0.95, "qwen3-4b-e2c"),
    "qwen3-4b-e2ck": ("K", ("O",), (1, 2, 3, 4, 5), None, "qwen3-4b-e2ck"),
    "qwen3-4b-e2ckn": ("K_n", ("O",), (1, 2, 3, 4, 5), None, "qwen3-4b-e2ckn"),
    "qwen3-4b-paired": ("E3", ("O", "F", "C"), (1, 2, 3), 0.2, "qwen3-4b"),
    "qwen3-4b-e2c-paired": ("E3c", ("O", "F", "C"), (1, 2, 3), 0.95, "qwen3-4b-e2c-paired"),
}


def _prompts() -> dict[str, Prompt]:
    out = {}
    for i in range(N_FAM):
        f = Family(family_id=f"f{i:03d}", source="daily_dilemmas", source_id=str(i), topic_group="t", situation=f"You face situation {i}.", action_x="Do x.", action_y="Do not do x.", ambiguity="high")
        ps, _ = make_prompts(f, ["T0", *V], t0_text=f"You face situation {i}. What should you do?")
        for p in ps:
            out[p.prompt_id] = p
    return out


def _u(tag: str, f: str, v: str, o: int = 0) -> float:
    return float(np.random.default_rng([zlib.crc32(tag.encode()), zlib.crc32(f.encode()), zlib.crc32(v.encode()), o]).uniform())


def _rows(who: str, p_fn, prompts: dict[str, Prompt], malformed_share: float = 0.0, tag: str = "") -> list[TeacherResponse]:
    rows = []
    for p in prompts.values():
        px = float(np.clip(p_fn(p.family_id, p.variant, p.order), 0.01, 0.99))
        letter = next(l for l, a in p.letter_to_action.items() if a == ("x" if px >= 0.5 else "y"))
        pl = {letter: px if p.letter_to_action[letter] == "x" else 1 - px}
        pl[[l for l in ("A", "B") if l != letter][0]] = 1 - pl[letter]
        cat = "malformed" if (malformed_share and _u("malformed" + tag, p.family_id, p.variant, p.order) < malformed_share) else "answer"
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=who, model="m", mode="profile", temperature=0.0, raw=f"Answer: {letter}", category=cat, letter=letter, choice_action=p.letter_to_action[letter], p_letters=pl, p_x=px))
    return rows


class SynthWorld:
    """Sides and generators; `rows_for(split)` gives every run's rows for a split (the split only changes the noise tags)."""

    def __init__(self) -> None:
        self.prompts = _prompts()
        self.families = sorted({p.family_id for p in self.prompts.values()})
        variants = ["T0", *V]
        rng = np.random.default_rng(0)
        base_side = {(f, v): bool(rng.random() < 0.5) for f in self.families for v in variants}
        self.side = {"alpha": dict(base_side)}
        self.side["beta"] = {k: (s != (rng.random() < 0.5)) for k, s in base_side.items()}
        self.side["gamma"] = {k: (s != (rng.random() < 0.5)) for k, s in base_side.items()}
        self.s0_side = {}
        for k in base_side:
            u = rng.random()
            self.s0_side[k] = self.side["beta"][k] if u < 0.6 else (self.side["alpha"][k] if u < 0.8 else self.side["gamma"][k])
        self.consensus = {k: (sum(self.side[t][k] for t in TEACHERS) >= 2) for k in base_side}

    @staticmethod
    def _p(side: bool, tag: str, f: str, v: str, o: int, soft: float = 0.9) -> float:
        noise = (_u("noise" + tag, f, v, o) - 0.5) * 0.1
        return (soft if side else 1 - soft) + noise

    def teacher_fn(self, t: str):
        return lambda f, v, o: self._p(self.side[t][(f, v)], f"T{t}", f, v, o)

    def base_fn(self, split: str):
        return lambda f, v, o: self._p(self.s0_side[(f, v)], f"B{split}", f, v, o, soft=0.75)

    def student_fn(self, teacher: str, q: float, tag: str):
        def fn(f, v, o):
            side = self.side[teacher][(f, v)] if _u("copy" + tag, f, v) < q else self.s0_side[(f, v)]
            return self._p(side, tag, f, v, o)
        return fn

    def consensus_fn(self, tag: str):
        def fn(f, v, o):
            side = self.s0_side[(f, v)] if _u("mix" + tag, f, v) < 0.5 else self.consensus[(f, v)]
            return self._p(side, tag, f, v, o)
        return fn

    def random_fn(self, tag: str):
        return lambda f, v, o: 0.05 + 0.9 * _u("rand" + tag, f, v)

    def teacher_rows(self) -> list[TeacherResponse]:
        rows = []
        for t in TEACHERS:
            rows += _rows(t, self.teacher_fn(t), self.prompts)
        return rows

    def base_rows(self, split: str) -> list[TeacherResponse]:
        return _rows("qwen3-4b.base_B_s0", self.base_fn(split), self.prompts, malformed_share=0.7, tag=split)

    def runs(self, split: str, namespaces=tuple(LAYOUT)) -> list[tuple[str, str, str, list[TeacherResponse]]]:
        """(namespace, run_dir, row run id, rows) for every student run of the split."""
        out = []
        for ns in namespaces:
            grid, versions, seeds, q, prefix = LAYOUT[ns]
            for t in TEACHERS:
                for ver in versions:
                    for s in seeds:
                        name = f"{t}_{ver}_s{s}"
                        tag = f"{ns}{name}{split}"
                        fn = self.consensus_fn(tag) if q is None else self.student_fn(t, q, tag)
                        out.append((ns, name, f"{prefix}.{name}", _rows(f"{ns}.{name}", fn, self.prompts, tag=tag)))
            if ns == "qwen3-4b":
                for s in (1, 2, 3):
                    name = f"random_R_s{s}"
                    out.append((ns, name, f"{prefix}.{name}", _rows(f"{ns}.{name}", self.random_fn(f"{name}{split}"), self.prompts)))
        return out

    def inventory(self, runs) -> pd.DataFrame:
        inv = []
        for ns, name, _, rows in runs:
            k = M.parse_run_id(f"{ns}.{name}")
            inv.append(dict(run_id=f"{ns}.{name}", namespace=ns, run_dir=name, original_id=rows[0].teacher, grid=LAYOUT[ns][0], role="core", teacher=k.teacher, version=k.version, seed=k.seed,
                            truth=PV.truth_of(LAYOUT[ns][0], k.version, k.teacher), n_rows=len(rows), path=""))
        k = M.parse_run_id("qwen3-4b.base_B_s0")
        inv.append(dict(run_id="qwen3-4b.base_B_s0", namespace="qwen3-4b", run_dir="base_B_s0", original_id="qwen3-4b.base_B_s0", grid="E1", role="core", teacher=k.teacher, version="B", seed=0, truth=PV.NONE, n_rows=0, path=""))
        return pd.DataFrame(inv, columns=PV.RUN_COLS)

    def write_tree(self, root: Path, splits=("dev", "test")) -> dict:
        for split in splits:
            for ns, name, row_id, rows in self.runs(split):
                write_jsonl(root / "runs" / ns / name / "eval" / f"{split}_responses.jsonl", [r.model_copy(update={"teacher": row_id}) for r in rows])
            write_jsonl(root / "runs" / "qwen3-4b" / "base_B_s0" / "eval" / f"{split}_responses.jsonl", self.base_rows(split))
            write_jsonl(root / "runs" / "qwen3-4b-e2c" / "base_B_s0" / "eval" / f"{split}_responses.jsonl", self.base_rows(split))  # a base copy, must be skipped
            for t in TEACHERS:
                write_jsonl(root / "teachers" / f"{t}_{split}_profile.jsonl", [r for r in self.teacher_rows() if r.teacher == t])
        write_jsonl(root / "prompts.jsonl", list(self.prompts.values()))
        return dict(runs=root / "runs", teachers=root / "teachers", prompts=root / "prompts.jsonl", base=root / "runs" / "qwen3-4b" / "base_B_s0")


@pytest.fixture(scope="module")
def synth() -> SynthWorld:
    return SynthWorld()


@pytest.fixture(scope="module")
def world(synth: SynthWorld) -> PV.World:
    runs = synth.runs("dev")
    rows = [r for _, _, _, rs in runs for r in rs]
    return PV.build_world(rows, synth.base_rows("dev"), synth.teacher_rows(), synth.prompts, synth.inventory(runs), list(TEACHERS), V, base_reference="prior")


@pytest.fixture(scope="module")
def result(world: PV.World) -> PV.E7Result:
    return PV.analyze(world, n_rep=10, n_perm=300, n_perm_rep=50, seed=0, budgets=(10, 20, 300), sample_n=(1, 3, 25))


# --------------------------------------------------------------------------- hand values


def test_scores_margins_decide_by_hand():
    a = np.array([[0.8, 0.6, 0.5], [0.7, 0.7, 0.2], [np.nan, 0.5, 0.4], [np.nan, np.nan, 0.4]])
    a_base = np.array([[0.5, 0.5, 0.5]])
    s_known = PV.scores(a, "base_known", a_base)
    assert np.allclose(s_known[0], [0.3, 0.1, 0.0])
    s_unknown = PV.scores(a, "base_unknown")
    assert np.allclose(s_unknown[0], [0.8 - 0.6333333, 0.6 - 0.6333333, 0.5 - 0.6333333], atol=1e-6)
    assert np.allclose(s_unknown[2][1:], [0.05, -0.05]) and np.isnan(s_unknown[2][0])
    best, m = PV.margins(s_known)
    assert best.tolist() == [0, 0, 1, 2] and np.allclose(m[:3], [0.2, 0.0, 0.1]) and np.isnan(m[3])  # one finite score -> undefined margin
    dec, _ = PV.decide(s_known, 0.15)
    assert dec.tolist() == [0, -1, -1, -1]  # margin 0.2 > tau; exact tie 0.0 and 0.1 fall under tau; undefined -> unattributed
    dec0, _ = PV.decide(s_known, 0.0)
    assert dec0.tolist() == [0, -1, 1, -1]  # tau = 0 still needs a strictly positive margin
    with pytest.raises(ValueError):
        PV.scores(a, "base_known")


def test_calibrate_tau_rule_and_fallback():
    m = np.array([0.30, 0.25, 0.10, 0.05] + [0.01] * 36)  # 40 negatives: floor(0.05 * 40) = 2 may be attributed
    t = PV.calibrate_tau(m)
    assert t.tau == pytest.approx(0.10) and t.n_attributed == 2 and t.fpr <= 0.05 and not t.fallback
    assert np.mean(m > t.tau) <= 0.05 and np.mean(m > 0.0999) > 0.05  # smallest tau satisfying the bound
    t_nan = PV.calibrate_tau(np.concatenate([m, [np.nan] * 20]))  # NaN margins are never attributed and stay in the denominator
    assert t_nan.n_neg == 60 and t_nan.tau == pytest.approx(0.05) and t_nan.n_attributed == 3
    few = PV.calibrate_tau(np.linspace(0, 1, 19))
    assert few.fallback and few.tau == 0.0 and "19 negatives" in few.note
    assert PV.calibrate_tau(np.zeros(25)).tau == 0.0 and PV.calibrate_tau(np.zeros(25)).n_attributed == 0


def test_auroc_and_wilson_hand_cases():
    assert PV.auroc([0.9, 0.4, 0.5, 0.1], [True, True, False, False])[0] == pytest.approx(0.75)  # 3 of 4 pos-neg pairs ordered right
    assert PV.auroc([0.9, 0.8, 0.3, 0.1], [True, True, False, False])[0] == pytest.approx(1.0)
    assert PV.auroc([0.5, 0.5, 0.5], [True, False, False])[0] == pytest.approx(0.5)  # all ties
    au, n1, n0 = PV.auroc([0.9, np.nan, 0.2], [True, True, False])
    assert au == 1.0 and (n1, n0) == (1, 1)  # NaN score dropped
    assert np.isnan(PV.auroc([0.1, 0.2], [True, True])[0])
    from vcd.analysis.e3_metrics import wilson_ci
    lo, hi = wilson_ci(5, 5)
    assert lo == pytest.approx(0.5655, abs=1e-3) and hi == 1.0
    assert wilson_ci(0, 5)[0] == 0.0 and wilson_ci(0, 5)[1] == pytest.approx(0.4345, abs=1e-3)
    assert PV.chance_level(0.4, 3) == pytest.approx(0.2)


def test_unattributed_counts_as_wrong_and_permutation_p():
    truth = np.array(["alpha"] * 4 + ["beta"] * 4 + [PV.NONE] * 2, dtype=object)
    s = np.zeros((10, 2))
    dec = np.array([0, 0, -1, -1, 1, -1, -1, -1, -1, 0])  # alpha 2/4 (two unattributed), beta 1/4, one negative attributed
    g = PV.Group("G", "O", "core", np.arange(8))
    rows = PV.group_rows(truth, s, dec, [g], np.array([8, 9]), ["alpha", "beta"], 200, np.random.default_rng(0), {"table": "t"})
    by = {r["teacher"]: r for r in rows}
    assert by["alpha"]["recall"] == 0.5 and by["alpha"]["n_unattributed"] == 2 and by["beta"]["recall"] == 0.25
    assert by["macro"]["macro_recall"] == pytest.approx(0.375) and by["macro"]["unattributed_rate"] == pytest.approx(5 / 8)
    assert by["macro"]["chance"] == pytest.approx(0.5 * (1 - 5 / 8)) and by["macro"]["fpr"] == 0.5 and by["macro"]["n_neg"] == 2
    assert by["macro"]["wilson_lo"] is np.nan or np.isnan(by["macro"]["wilson_lo"]) if "wilson_lo" in by["macro"] else True
    # a perfect detector on 6 + 6 runs: the permutation p is small; a detector unrelated to the labels has p near 1
    tr = np.array([0] * 6 + [1] * 6)
    p_good, _, n = PV.permutation_p_macro(tr, tr.copy(), 2, 2000, np.random.default_rng(1))
    p_bad, _, _ = PV.permutation_p_macro(tr, np.array([0, 1] * 6), 2, 2000, np.random.default_rng(1))
    assert n == 2000 and p_good < 0.01 and p_bad > 0.3
    assert PV.macro_recall_batch(tr[None, :], np.full(12, -1), 2)[0] == 0.0  # everything unattributed -> macro recall 0


# --------------------------------------------------------------------------- engine against e1_metrics


def test_world_matches_teacher_agreement_and_truth(world: PV.World):
    """build_world checks the matrix engine against teacher_agreement; here the reference table is re-derived independently."""
    runs = world.runs
    assert len(runs) == 15 * 4 + 3 + 27 * 2 + 1 and runs["run_id"].is_unique
    assert set(runs.loc[runs["grid"].isin(["K", "K_n"]), "truth"]) == {PV.NONE} and set(runs.loc[runs["version"].isin(["R", "B"]), "truth"]) == {PV.NONE}
    assert (runs.loc[(runs["grid"] == "E3c") & (runs["version"] == "F"), "truth"] == runs.loc[(runs["grid"] == "E3c") & (runs["version"] == "F"), "teacher"]).all()
    a = PV.agreement_rate(*PV.agreement_counts(world.S.cells, world.T.cells))
    ref = world.agreement.pivot_table(index="run_id", columns="teacher", values="agreement").reindex(index=world.S.who, columns=world.teachers).to_numpy()
    assert np.allclose(a, ref, equal_nan=True)
    assert world.disagree.sum() > 0.3 * world.disagree.size  # teachers disagree on many cells
    assert world.base_ref_cells == len(world.families) * len(V)  # the prior profile covers every cell
    gated = world.runs.set_index("run_id").loc["qwen3-4b.base_B_s0", "n_cells_valid"]
    assert gated < 0.3 * world.base_ref_cells  # the gated base suspect has few cells (70% malformed prompts)
    assert len(PV.core_negatives(runs)) == 34


def test_sampled_readout_converges_to_probability_mode(world: PV.World):
    S = world.S
    rng = np.random.default_rng(0)
    p_prob = S.p
    conf = np.isfinite(p_prob) & (np.abs(p_prob - 0.5) > 0.2)
    p1 = PV.sample_sym(S.p_o1, S.p_o2, 1, rng)
    assert set(np.unique(p1[np.isfinite(p1)])) <= {0.0, 0.5, 1.0}
    assert np.isnan(p1[np.isnan(p_prob)]).all()  # missing orders stay missing
    agree1 = np.mean((p1[conf] > 0.5) == (p_prob[conf] > 0.5))
    p_big = PV.sample_sym(S.p_o1, S.p_o2, 101, np.random.default_rng(0))
    agree_big = np.mean((p_big[conf] > 0.5) == (p_prob[conf] > 0.5))
    assert agree_big > 0.999 and agree_big > agree1
    assert np.isnan(p_big[conf]).mean() < 0.005  # odd n: no ties; disagreeing orders are rare on confident cells
    p10 = PV.sample_sym(np.full((1, 2, 2), 0.5), np.full((1, 2, 2), 0.5), 10, np.random.default_rng(0))
    assert np.isnan(p10).any() or set(np.unique(p10[np.isfinite(p10)])) <= {0.0, 0.5, 1.0}  # even n can tie -> dropped order


def test_probe_masks_and_cell_weights():
    rng = np.random.default_rng(0)
    W = PV.probe_masks(30, 10, 5, rng)
    assert W.shape == (5, 30) and (W.sum(1) == 10).all()
    assert PV.probe_masks(30, 30, 5, rng).shape == (1, 30) and PV.probe_masks(30, 300, 5, rng).sum() == 30
    Wc = PV.family_cell_weights(np.array([[1, 0, 2]]), 2)
    assert Wc.tolist() == [[1, 1, 0, 0, 2, 2]]
    agree = np.ones((1, 1, 6), dtype=bool)
    valid = np.ones((1, 1, 6), dtype=bool)
    agree[0, 0, 4:] = False  # the third family disagrees
    assert PV.agreement_rate(agree, valid, Wc)[0, 0, 0] == pytest.approx(2 / 6)
    assert np.isnan(PV.agreement_rate(agree, valid, np.zeros((1, 6)))[0, 0, 0])


# --------------------------------------------------------------------------- behaviour of the whole detector on the synthetic world


def _main(res: PV.E7Result, detector: str, subset: str = "all", policy: str = "calibrated") -> pd.DataFrame:
    m = res.metrics
    return m[(m["table"] == "main") & (m["detector"] == detector) & (m["subset"] == subset) & (m["tau_policy"] == policy)]


def test_fpr_bound_recall_rises_with_copy_share_and_base_known_removes_bias(result: PV.E7Result, world: PV.World):
    cal = result.calibration["tau"]
    for det in PV.DETECTORS:
        c = cal[PV.cal_key("probability", "all", det)]
        assert c["n_neg"] == 34 and c["fpr_at_tau"] <= 0.05 and not c["fallback"]
        rows = _main(result, det)
        rows = rows[rows["teacher"] != PV.NONE]  # negative-group rows carry their own group FPR
        assert (rows["fpr"] <= 0.05).all() and (rows["n_neg"] == 34).all()
        e2c = rows[(rows["grid"] == "E2c_C") & (rows["teacher"] == "macro")]["macro_recall"].iloc[0]
        e1 = rows[(rows["grid"] == "E1") & (rows["teacher"] == "macro")]["macro_recall"].iloc[0]
        assert e2c > e1 and e2c > 0.8  # q = 0.95 students are recognised, q = 0.2 students much less
        e3c = rows[(rows["grid"] == "E3c") & (rows["teacher"] == "macro")]
        assert (e3c["macro_recall"] > 0.8).all() and set(e3c["version"]) == {"O", "F", "C"}
    # base-known removes the base bias: the beta score of the consensus students (beta-like prior) is large without the base, ~0 with it
    runs = result.runs
    k = runs[runs["grid"].isin(["K", "K_n"])]
    assert k["s_unknown__beta"].mean() > 0.03 and abs(k["s_known__beta"].mean()) < 0.06
    assert k["s_unknown__beta"].mean() > k["s_known__beta"].mean() + 0.04
    # the calibrated tau makes at most 1 of the 34 negatives attributed under either detector
    assert (~k["correct_unknown"]).sum() + (~runs[runs["truth"] == PV.NONE]["correct_known"]).sum() <= 2
    # per-teacher rows carry Wilson bounds and AUROC; AUROC of the q = 0.95 students is near 1
    e2c_t = _main(result, "base_known")
    e2c_t = e2c_t[(e2c_t["grid"] == "E2c_C") & e2c_t["teacher"].isin(TEACHERS)]
    assert (e2c_t["auroc"] > 0.95).all() and (e2c_t["wilson_lo"] <= e2c_t["recall"]).all() and (e2c_t["wilson_hi"] >= e2c_t["recall"]).all()
    assert result.verdict["verdict"] == "溯源可行（有条件）" and result.verdict["n_pass"] == 3 and result.verdict["fpr_ok"] is True
    # the chance reference and the permutation p are filled on macro rows
    mac = _main(result, "base_known")
    mac = mac[mac["teacher"] == "macro"]
    assert mac["chance"].between(0, 1 / 3).all() and mac["perm_p"].between(0, 1).all() and (mac["n_perm"] == 300).all()
    assert mac[mac["grid"] == "E2c_C"]["perm_p"].iloc[0] < 0.05


def test_tables_disagreement_sampled_probe_loso_logo(result: PV.E7Result, world: PV.World):
    m = result.metrics
    dis = m[(m["table"] == "main") & (m["subset"] == "disagreement") & (m["teacher"] != PV.NONE)]
    assert set(dis["tau_policy"]) == {"calibrated", "fixed_all_cells"} and (dis[dis["tau_policy"] == "calibrated"]["fpr"] <= 0.05).all()
    assert PV.cal_key("probability", "disagreement", "base_known") in result.calibration["tau"]
    # negative groups report their own false-attribution share
    neg = m[(m["table"] == "main") & (m["teacher"] == PV.NONE) & (m["subset"] == "all")]
    assert set(zip(neg["grid"], neg["version"])) == {("K", "O"), ("K_n", "O"), ("E1", "R"), ("E1", "B")}
    # sampled readout: more draws -> closer to the probability mode (higher recall on the q = 0.95 grid); taus pooled over the repetitions
    sm = result.sampled
    assert set(sm["n_draws"]) == {1, 3, 25} and (sm["n_rep"] == 10).all()
    e2c = sm[(sm["grid"] == "E2c_C") & (sm["teacher"] == "macro") & (sm["detector"] == "base_known")].set_index("n_draws")
    prob = _main(result, "base_known")
    prob_e2c = prob[(prob["grid"] == "E2c_C") & (prob["teacher"] == "macro")]["macro_recall"].iloc[0]
    assert e2c.loc[25, "macro_recall_mean"] >= e2c.loc[1, "macro_recall_mean"] - 0.05
    assert abs(e2c.loc[25, "macro_recall_mean"] - prob_e2c) <= 0.1
    assert (sm[sm["teacher"] == "macro"]["fpr_mean"] <= 0.08).all()  # tau pooled over reps keeps the average FPR near the 5% target
    assert result.calibration["tau"][PV.cal_key("sampled_n3", "all", "base_known")]["n_margins"] == 10 * 34
    # probe curve: budgets collapse to the family count; the all-families row equals the main table and reuses the all-cells tau (no separate entry)
    pc = result.probe_curve
    assert sorted(set(pc["budget"])) == [10, 20, 30] and pc[pc["budget"] == 30]["all_families"].all()
    assert PV.cal_key("probability", "budget10", "base_known") in result.calibration["tau"] and not any("budget30" in k or "budget300" in k for k in result.calibration["tau"])
    assert set(pc.loc[pc["budget"] == 30, "tau_source"]) == {"all_cells"} and set(pc.loc[(pc["budget"] == 10) & (pc["tau_policy"] == "calibrated"), "tau_source"]) == {"budget"}
    full = pc[(pc["budget"] == 30) & (pc["detector"] == "base_known") & (pc["tau_policy"] == "calibrated") & (pc["grid"] == "E2c_C") & (pc["teacher"] == "macro")]
    assert full["macro_recall_mean"].iloc[0] == pytest.approx(prob_e2c) and full["n_rep"].iloc[0] == 1
    small = pc[(pc["budget"] == 10) & (pc["detector"] == "base_known") & (pc["tau_policy"] == "calibrated") & (pc["grid"] == "E2c_C") & (pc["teacher"] == "macro")]
    assert small["n_rep"].iloc[0] == 10 and 0 <= small["macro_recall_mean"].iloc[0] <= 1
    # LOSO: tau from O / R / B only (= the main tau), rows are the F / C students
    lo = result.loso
    assert set(lo["version"]) == {"F", "C"} and set(lo["grid"]) == {"E3", "E3c"}
    for det in PV.DETECTORS:
        assert result.calibration["tau"][PV.cal_key("probability", "all", det, "loso")]["tau"] == result.calibration["tau"][PV.cal_key("probability", "all", det)]["tau"]
    e3c_fc = lo[(lo["grid"] == "E3c") & (lo["teacher"] == "macro") & (lo["detector"] == "base_known")]
    assert (e3c_fc["macro_recall"] > 0.8).all()
    # LOGO: calibrated on E1 + K + K_n (E1 students as rejects), evaluated on the other grids only
    lg = result.logo[result.logo["teacher"] != PV.NONE]  # the negative groups stay listed for their FPR
    assert "E1" not in set(lg["grid"]) and {"E2c_C", "E3", "E3c"} <= set(lg["grid"])
    c = result.calibration["tau"][PV.cal_key("probability", "all", "base_known", "logo")]
    assert c["n_population"] == 15 + 3 + 1 + 15 + 15 and c["note"].startswith("49 negatives") and np.isfinite(c["tau"])


def test_populations_loso_only_o_and_logo_includes_e1_students(world: PV.World):
    runs = world.runs.copy()
    neg = PV.core_negatives(runs)
    assert np.array_equal(PV.loso_population(runs), neg)
    fake = runs.iloc[:1].copy()
    fake["run_id"], fake["version"], fake["truth"], fake["grid"] = "x.alpha_F_s9", "F", PV.NONE, "K"
    runs2 = pd.concat([runs, fake], ignore_index=True)
    assert len(PV.core_negatives(runs2)) == len(neg) + 1 and len(PV.loso_population(runs2)) == len(neg)  # the F run is a negative but never a LOSO calibration point
    logo = PV.logo_population(runs)
    assert set(runs.loc[logo, "grid"]) == {"E1", "K", "K_n"} and (runs.loc[logo, "truth"] != PV.NONE).sum() == 15
    desc = runs.copy()
    desc.loc[desc["grid"] == "K", "role"] = "descriptive"
    assert len(PV.core_negatives(desc)) == 34 - 15  # descriptive runs never enter a calibration


def test_determinism_and_test_mode_reuses_tau(world: PV.World, result: PV.E7Result):
    again = PV.analyze(world, n_rep=10, n_perm=300, n_perm_rep=50, seed=0, budgets=(10, 20, 300), sample_n=(1, 3, 25))
    pd.testing.assert_frame_equal(result.metrics, again.metrics)
    pd.testing.assert_frame_equal(result.sampled, again.sampled)
    pd.testing.assert_frame_equal(result.probe_curve, again.probe_curve)
    assert result.calibration["tau"] == again.calibration["tau"]
    other = PV.analyze(world, n_rep=10, n_perm=300, n_perm_rep=50, seed=1, budgets=(10, 20, 300), sample_n=(1, 3, 25))
    assert not result.sampled["recall_mean"].equals(other.sampled["recall_mean"])  # the seed matters for the sampled readout
    # test mode: every tau comes from the calibration dict, nothing is recalibrated
    cal = json.loads(json.dumps(result.calibration))
    for k in cal["tau"]:
        cal["tau"][k]["tau"] = 0.5
    reused = PV.analyze(world, calibration=cal, n_rep=10, n_perm=300, n_perm_rep=50, seed=0, budgets=(10, 20, 300), sample_n=(1, 3, 25), split="test")
    assert (reused.metrics["tau"] == 0.5).all() and (reused.loso["tau"] == 0.5).all() and (reused.probe_curve["tau"] == 0.5).all()
    assert reused.verdict["calibration_reused"] and not reused.verdict["descriptive_only"] and not reused.notes
    # a budget the calibration split could not calibrate (its family count) falls back to the all-cells tau and says so
    cal2 = {k: v for k, v in cal.items() if k != "tau"} | {"tau": {k: v for k, v in cal["tau"].items() if "budget20" not in k}}
    fb = PV.analyze(world, calibration=cal2, n_rep=3, n_perm=20, n_perm_rep=5, seed=0, budgets=(10, 20), sample_n=(1,), split="test")
    assert len([n for n in fb.notes if n.startswith("probe budget 20")]) == 2
    assert set(fb.probe_curve.loc[(fb.probe_curve["budget"] == 20) & (fb.probe_curve["tau_policy"] == "calibrated"), "tau_source"]) == {"all_cells_fallback"}
    assert (fb.probe_curve.loc[fb.probe_curve["budget"] == 20, "tau"] == 0.5).all()
    with pytest.raises(KeyError):
        PV.analyze(world, calibration={"tau": {}, "teachers": list(TEACHERS)}, n_rep=2, n_perm=10, n_perm_rep=5, budgets=(300,), sample_n=(1,))


# --------------------------------------------------------------------------- loading and the CLI


def test_truth_grid_map_and_loading(synth: SynthWorld, tmp_path: Path):
    assert PV.truth_of("E2c_C", "O", "gpt4o") == "gpt4o" and PV.truth_of("K", "O", "gpt4o") == PV.NONE
    assert PV.truth_of("E1", "R", "random") == PV.NONE and PV.truth_of("E1", "B", "base") == PV.NONE and PV.truth_of("E3c", "C", "claude46") == "claude46"
    gm = PV.parse_grid_map("qwen3-4b-x=X, qwen3-4b=E1b")
    assert gm["qwen3-4b-x"] == "X" and gm["qwen3-4b"] == "E1b" and gm["qwen3-4b-e2c"] == "E2c_C"
    paths = synth.write_tree(tmp_path, splits=("dev",))
    pid = set(synth.prompts)
    rows, inv, notes = PV.load_student_runs(paths["runs"], "dev", ["qwen3-4b", "qwen3-4b-paired", "qwen3-4b-e2c"], PV.GRID_BY_NAMESPACE, pid, {"qwen3-4b": "core", "qwen3-4b-paired": "core", "qwen3-4b-e2c": "core"})
    assert len(inv) == 18 + 27 + 15 and inv["run_id"].is_unique
    paired = inv[inv["namespace"] == "qwen3-4b-paired"]
    assert (paired["original_id"].str.startswith("qwen3-4b.")).all() and (paired["run_id"].str.startswith("qwen3-4b-paired.")).all() and set(paired["grid"]) == {"E3"}
    assert all(r.teacher.startswith(("qwen3-4b.", "qwen3-4b-paired.", "qwen3-4b-e2c.")) for r in rows) and not any(r.teacher.startswith("qwen3-4b.") and "paired" in r.teacher for r in rows)
    assert sum("version-B copies skipped" in n for n in notes) == 1 and "qwen3-4b-e2c/base_B_s0" in notes[-1] and not any("directory wins" in n for n in notes)  # the E3 prefix is accepted silently
    assert PV._rel(Path.cwd() / "scripts" / "21_provenance.py") == "scripts/21_provenance.py" and PV._rel(Path("/nowhere/x.jsonl")) == "/nowhere/x.jsonl"  # relative only inside the cwd
    base_rows, base_row = PV.load_base(paths["base"], "dev", pid, PV.GRID_BY_NAMESPACE)
    assert base_row["run_id"] == "qwen3-4b.base_B_s0" and base_row["truth"] == PV.NONE and base_row["grid"] == "E1" and len(base_rows) == len(pid)
    with pytest.raises(ValueError):
        PV.load_student_runs(paths["runs"], "dev", ["unknown-ns"], PV.GRID_BY_NAMESPACE, pid, {})
    with pytest.raises(FileNotFoundError):
        PV.load_teachers(paths["teachers"], "dev", ["alpha", "delta"], pid)


def _cli(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(ROOT / "scripts/21_provenance.py"), *args], capture_output=True, text=True, cwd=ROOT)


def test_cli_dev_calibrates_then_test_reuses_and_refuses_without_calibration(synth: SynthWorld, tmp_path: Path):
    paths = synth.write_tree(tmp_path)
    common = ["--runs-dir", str(paths["runs"]), "--namespaces", ",".join(LAYOUT), "--descriptive-namespaces", "none", "--teacher-dir", str(paths["teachers"]), "--teachers", ",".join(TEACHERS),
              "--prompts", str(paths["prompts"]), "--base-run", str(paths["base"]), "--n-rep", "4", "--n-perm", "50", "--n-perm-rep", "10", "--budgets", "10,300", "--sample-n", "1,3"]
    out_dev = tmp_path / "e7_dev"
    r = _cli(["--split", "dev", "--out", str(out_dev), *common])
    assert r.returncode == 0, r.stderr
    for f in ("e7_runs.csv", "e7_metrics.csv", "e7_probe_curve.csv", "e7_sampled.csv", "e7_loso.csv", "e7_logo.csv", "e7_verdict.json", "e7_summary.md", "calibration.json"):
        assert (out_dev / f).exists(), f
    cal = json.loads((out_dev / "calibration.json").read_text(encoding="utf-8"))
    assert cal["negatives"]["n"] == 34 and PV.cal_key("probability", "all", "base_known") in cal["tau"] and cal["split"] == "dev"
    verdict = json.loads((out_dev / "e7_verdict.json").read_text(encoding="utf-8"))
    assert verdict["descriptive_only"] and not verdict["confirmatory"] and verdict["n_negatives"] == 34 and "not yet frozen" in verdict["frozen"]
    summary = (out_dev / "e7_summary.md").read_text(encoding="utf-8")
    assert "主判定" in summary and "标定 split" in summary and "not yet frozen" in summary
    runs = pd.read_csv(out_dev / "e7_runs.csv")
    assert len(runs) == 15 * 4 + 3 + 27 * 2 + 1 and (runs["namespace"] == "qwen3-4b-paired").sum() == 27 and "a_T0__alpha" in runs.columns
    # test split without a calibration file is refused
    r_bad = _cli(["--split", "test", "--out", str(tmp_path / "e7_bad"), *common])
    assert r_bad.returncode == 2 and "requires --calibration" in r_bad.stderr and not (tmp_path / "e7_bad").exists()
    # test split with the dev calibration: every tau is reused verbatim, calibration_used.json records the source
    out_test = tmp_path / "e7"
    r_test = _cli(["--split", "test", "--out", str(out_test), "--calibration", str(out_dev / "calibration.json"), "--frozen-commit", "abc123", *common])
    assert r_test.returncode == 0, r_test.stderr
    used = json.loads((out_test / "calibration_used.json").read_text(encoding="utf-8"))
    assert not (out_test / "calibration.json").exists() and used["calibration_file"].endswith("calibration.json")
    mt = pd.read_csv(out_test / "e7_metrics.csv")
    for det in PV.DETECTORS:
        assert mt[(mt["subset"] == "all") & (mt["detector"] == det) & (mt["tau_policy"] == "calibrated")]["tau"].iloc[0] == pytest.approx(cal["tau"][PV.cal_key("probability", "all", det)]["tau"])
    vt = json.loads((out_test / "e7_verdict.json").read_text(encoding="utf-8"))
    assert vt["confirmatory"] and vt["calibration_reused"] and "frozen at commit abc123" in vt["frozen"]
    assert "frozen at commit abc123" in (out_test / "e7_summary.md").read_text(encoding="utf-8")
