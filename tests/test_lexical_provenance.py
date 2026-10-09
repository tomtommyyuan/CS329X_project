"""Synthetic teachers for vcd.analysis.lexical_provenance and scripts/22_lexical_provenance.py.

World: three teachers (alpha, beta, gamma) write rationales from one shared neutral vocabulary; each teacher's O text always
contains its marker word (alpha "indeed", beta "basically", gamma "frankly"). The "rewrites" F and C drop the marker
(F also capitalises, C appends a filler), so a lexical classifier should be near-perfect within O and near chance on F / C.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
import scipy.sparse as sp

from vcd.analysis import lexical_provenance as LP

ROOT = Path(__file__).resolve().parents[1]
TEACHERS = ("alpha", "beta", "gamma")
MARKERS = {"alpha": "indeed", "beta": "basically", "gamma": "frankly"}
VOCAB = ["the", "person", "should", "help", "because", "harm", "trust", "family", "honest", "promise", "care", "fair", "right", "wrong", "money", "friend", "work", "time", "other", "choose", "keep", "tell", "truth", "safe", "kind"]


def make_world(n_fam: int = 60, seed: int = 0, min_len: int = 12, max_len: int = 26) -> pd.DataFrame:
    """Long frame (teacher, style, prompt_id, family_id, letter, text) like load_sft_texts; one family = 2 prompts per teacher."""
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n_fam):
        fam = f"f{i:03d}"
        for v in ("T1", "T3"):
            pid = f"{fam}.{v}.o1"
            for t in TEACHERS:
                words = list(rng.choice(VOCAB, size=int(rng.integers(min_len, max_len))))
                plain = " ".join(words)
                marked = words.copy()
                marked.insert(int(rng.integers(0, len(words) + 1)), MARKERS[t])
                o_text = " ".join(marked) + "."
                f_text = plain.capitalize() + "."
                c_text = plain + ", you know."
                letter = "A" if rng.random() < 0.5 else "B"
                for s, txt in (("O", o_text), ("F", f_text), ("C", c_text)):
                    rows.append(dict(teacher=t, style=s, prompt_id=pid, family_id=fam, letter=letter, text=txt))
    return pd.DataFrame(rows)


def write_sft(df: pd.DataFrame, out: Path) -> None:
    out.mkdir(parents=True, exist_ok=True)
    for (t, s), g in df.groupby(["teacher", "style"], sort=False):
        with (out / f"{t}_{s}_s1.jsonl").open("w", encoding="utf-8") as fh:
            for r in g.itertuples():
                pid = r.prompt_id
                fh.write(json.dumps(dict(prompt_id=pid, family_id=r.family_id, variant=pid.split(".")[1], order=1, teacher=t, version=s, text_prompt="Q", text_target=f" {r.letter}\nRationale: {r.text}", letter=r.letter)) + "\n")


@pytest.fixture(scope="module")
def world() -> pd.DataFrame:
    return make_world()


@pytest.fixture(scope="module")
def result(world) -> LP.EvalResult:
    return LP.run_evaluations(world, "synth", LP.HashedFeaturizer(hash_bits=12, seed=0), n_folds=3, seed=0, teachers=TEACHERS)


def _macro(acc: pd.DataFrame, features: str, evaluation: str, overlap: str) -> float:
    m = acc[(acc.features == features) & (acc.evaluation == evaluation) & (acc.overlap == overlap) & (acc.teacher == "macro")]
    assert len(m) == 1, (features, evaluation, overlap)
    return float(m.acc.iloc[0])


# --------------------------------------------------------------------------- loading and folds


def test_load_sft_texts_strips_letter_line(tmp_path, world):
    write_sft(world, tmp_path)
    df = LP.load_sft_texts(tmp_path, teachers=TEACHERS)
    assert len(df) == len(world)
    assert not df.text.str.contains("Rationale:").any()
    assert not df.text.str.match(r"^[AB]\n").any()
    inv = LP.inventory(df, teachers=TEACHERS)
    assert inv.paired.all() and (inv.n_O == 120).all() and (inv.prompt_overlap_all == 1.0).all()
    with pytest.raises(FileNotFoundError):
        LP.load_sft_texts(tmp_path, teachers=("delta",))


def test_family_folds_group_and_balance(world):
    folds = LP.family_folds(world.family_id.to_numpy(), n_folds=5, seed=0)
    per_fam = pd.Series(folds).groupby(world.family_id.to_numpy()).nunique()
    assert (per_fam == 1).all(), "a family must sit in exactly one fold"
    sizes = np.bincount(pd.Series(folds).groupby(world.family_id.to_numpy()).first().to_numpy(), minlength=5)
    assert sizes.max() - sizes.min() <= 1
    assert np.array_equal(folds, LP.family_folds(world.family_id.to_numpy(), n_folds=5, seed=0))
    assert not np.array_equal(folds, LP.family_folds(world.family_id.to_numpy(), n_folds=5, seed=1))


# --------------------------------------------------------------------------- features


def test_featurizer_deterministic_and_normalised():
    texts = ["Indeed, the person should help.", "Basically it's fine — trust them; really.", "x"]
    fz1, fz2 = LP.HashedFeaturizer(hash_bits=12, seed=0), LP.HashedFeaturizer(hash_bits=12, seed=0)
    X1, X2 = fz1.transform(texts), fz2.transform(texts)
    assert sp.issparse(X1) and X1.shape == (3, 2 * 4096)
    assert (X1 != X2).nnz == 0
    nb = fz1.n_buckets
    for i in range(2):  # each block has unit L2 norm
        row = X1[i].toarray().ravel()
        assert np.isclose(np.linalg.norm(row[:nb]), 1.0) and np.isclose(np.linalg.norm(row[nb:]), 1.0)
    X3 = LP.HashedFeaturizer(hash_bits=12, seed=1).transform(texts)
    assert (X1 != X3).nnz > 0, "the seed must change the hashing"
    assert fz1.word_bucket("indeed") == fz2.word_bucket("indeed") < nb
    assert LP.word_tokens("It's a test, really — yes.") == ["it's", "a", "test", ",", "really", "—", "yes", "."]
    assert LP.word_ngrams(["a", "b", "c"]) == ["a", "b", "c", "a b", "b c"]


def test_length_features_shape():
    X = LP.length_features(["One two three. Four five.", "Six"])
    assert X.shape == (2, 3)
    assert X[0, 0] == 5 and X[0, 1] == 2 and X[1, 0] == 1


# --------------------------------------------------------------------------- classifier


def test_backends_agree_and_handle_missing_class():
    rng = np.random.default_rng(0)
    X = rng.normal(size=(300, 5))
    y = np.where(X[:, 0] + 0.5 * X[:, 1] > 0.5, "a", np.where(X[:, 2] > 0, "b", "c"))
    m_sk = LP.fit_logreg(X, y, backend="sklearn", standardise=True)
    m_np = LP.fit_logreg(X, y, backend="numpy", standardise=True)
    assert m_sk.backend == "sklearn" and m_np.backend == "numpy"
    agree = np.mean(m_sk.predict(X) == m_np.predict(X))
    assert agree >= 0.97, agree
    assert np.allclose(m_sk.coef, m_np.coef, atol=0.05)
    # a class absent from training is never predicted; classes keep the declared order
    m = LP.fit_logreg(X[y != "c"], y[y != "c"], backend="numpy", classes=("a", "b", "c"))
    assert list(m.classes) == ["a", "b", "c"] and "c" not in set(m.predict(X))
    m1 = LP.fit_logreg(X[y == "a"], y[y == "a"], backend="sklearn", classes=("a", "b", "c"))
    assert set(m1.predict(X)) == {"a"}
    with pytest.raises(ValueError):
        LP.fit_logreg(X, y, backend="nope")


def test_wilson_and_accuracy_rows():
    lo, hi = LP.wilson_ci(50, 100)
    assert abs(lo - 0.4038) < 1e-3 and abs(hi - 0.5962) < 1e-3
    assert LP.wilson_ci(0, 10)[0] == 0.0 and LP.wilson_ci(10, 10)[1] == 1.0
    y = np.array(["a"] * 4 + ["b"] * 4 + ["c"] * 4)
    p = np.array(["a"] * 4 + ["b", "b", "c", "c"] + ["a"] * 4)
    rows = pd.DataFrame(LP.accuracy_rows(y, p, teachers=("a", "b", "c"), tag=1)).set_index("teacher")
    assert rows.loc["a", "acc"] == 1.0 and rows.loc["b", "acc"] == 0.5 and rows.loc["c", "acc"] == 0.0
    assert np.isclose(rows.loc["macro", "acc"], 0.5) and np.isclose(rows.loc["pooled", "acc"], 6 / 12)
    assert rows.loc["pooled", "ci_lo"] < 0.5 < rows.loc["pooled", "ci_hi"] and (rows.tag == 1).all()
    conf = pd.DataFrame(LP.confusion_rows(y, p, teachers=("a", "b", "c"))).set_index("true_teacher")
    assert conf.loc["c", "pred_a"] == 4 and conf.loc["b", "pred_b"] == 2


# --------------------------------------------------------------------------- the grid on the synthetic world


def test_marker_identifies_teacher_within_style(result):
    acc = result.accuracy
    assert _macro(acc, "ngram", "within_O", "family_disjoint_cv") >= 0.95
    per = acc[(acc.features == "ngram") & (acc.evaluation == "within_O") & (acc.teacher.isin(TEACHERS))]
    assert (per.ci_lo > LP.CHANCE).all() and (per.n == 120).all()


def test_removing_marker_drops_to_chance(result):
    acc = result.accuracy
    for u in ("F", "C"):
        disjoint = _macro(acc, "ngram", f"O->{u}", "family_disjoint")
        assert 0.20 <= disjoint <= 0.48, (u, disjoint)
        # same prompts: the all-O model has seen the very word sequence of every F / C text (minus the marker), so content
        # memorisation lifts it above the family-disjoint value (the reason both overlaps are reported on the real data)
        assert _macro(acc, "ngram", f"O->{u}", "same_prompts") >= disjoint - 0.05
        assert 0.20 <= _macro(acc, "ngram", f"within_{u}", "family_disjoint_cv") <= 0.48
    # the reverse direction (F + C -> O) has no marker to learn either
    assert _macro(acc, "ngram", "F+C->O", "family_disjoint") <= 0.48
    # lengths are identically distributed across teachers -> the length control is at chance everywhere
    ln = acc[(acc.features == "length") & (acc.teacher == "macro")]
    assert ((ln.acc >= 0.20) & (ln.acc <= 0.48)).all(), ln[["evaluation", "overlap", "acc"]]
    # nearest-centroid rows exist for F / C (both overlaps) and O (cross-fold)
    nc = acc[(acc.features == "ngram_centroid") & (acc.teacher == "macro")]
    assert set(zip(nc.evaluation, nc.overlap)) == {("O->F", "same_prompts"), ("O->C", "same_prompts"), ("within_O", "family_disjoint_cv"), ("O->F", "family_disjoint"), ("O->C", "family_disjoint")}
    assert _macro(acc, "ngram_centroid", "within_O", "family_disjoint_cv") >= 0.8


def test_grid_is_deterministic(world, result):
    again = LP.run_evaluations(world, "synth", LP.HashedFeaturizer(hash_bits=12, seed=0), n_folds=3, seed=0, teachers=TEACHERS)
    pd.testing.assert_frame_equal(result.accuracy, again.accuracy)
    pd.testing.assert_frame_equal(result.confusion, again.confusion)
    assert np.array_equal(result.folds, again.folds)
    assert set(result.models) == {"O_full", "F_full", "C_full", "F+C_full"}
    wide = LP.accuracy_table(result.accuracy, TEACHERS)
    assert {"features", "evaluation", "overlap", "macro", "pooled", "n"} <= set(wide.columns)
    assert wide.n.eq(360).all()


def test_top_features_name_the_marker(world, result):
    fz = LP.HashedFeaturizer(hash_bits=12, seed=0)
    feats = LP.top_word_features(result.models["O_full"], fz, world, "O", "synth", k=5, min_df=5, teachers=TEACHERS)
    assert set(feats.teacher) == set(TEACHERS)
    for t, marker in MARKERS.items():
        top = feats[(feats.teacher == t) & (feats["rank"] == 1)].iloc[0]
        assert marker in top.feature.split("|"), (t, top.feature)
        assert top.rate_O_own > 20 and top.rate_F_own == 0 and top.rate_C_own == 0 and top.rate_O_others == 0
        assert top.coef > 0 and top.df_model_style == 120
    assert (feats.groupby("teacher").size() == 5).all()
    assert list(feats.columns[:4]) == ["set", "model_style", "teacher", "rank"]
    surv = LP.cue_survival(feats, "O", ("F", "C"), k=5).set_index("teacher")
    for t, marker in MARKERS.items():  # the marker is erased by both rewrites; the other top words are plain vocabulary and stay
        assert marker in surv.loc[t, "removed_F"] and marker in surv.loc[t, "removed_C"]
        assert surv.loc[t, "kept_F"] <= 4 and surv.loc[t, "n"] == 5


# --------------------------------------------------------------------------- script


def test_script_end_to_end(tmp_path, world):
    sft = tmp_path / "sft"
    write_sft(world, sft)
    out = tmp_path / "out"
    cmd = [sys.executable, str(ROOT / "scripts/22_lexical_provenance.py"), "--sets", "synth", "--sft-dirs", str(sft), "--teachers", ",".join(TEACHERS), "--out", str(out), "--n-folds", "3", "--hash-bits", "12", "--min-df", "5", "--top-k", "5"]
    subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, check=True)
    for name in ("lexical_accuracy.csv", "lexical_confusion.csv", "lexical_features.csv", "lexical_cue_survival.csv", "lexical_inventory.csv", "lexical_run_info.json", "lexical_summary.md"):
        assert (out / name).exists(), name
    acc = pd.read_csv(out / "lexical_accuracy.csv")
    assert set(acc.columns) == {"set", "evaluation", "features", "train", "test", "overlap", "teacher", "n", "n_correct", "acc", "ci_lo", "ci_hi"}
    assert (acc["set"] == "synth").all()
    assert _macro(acc, "ngram", "within_O", "family_disjoint_cv") >= 0.95
    assert _macro(acc, "ngram", "O->F", "family_disjoint") <= 0.48
    md = (out / "lexical_summary.md").read_text(encoding="utf-8")
    assert "## 结论" in md and "词汇" in md and "| synth | within_O |" in md
    info = json.loads((out / "lexical_run_info.json").read_text())
    assert info["pos_tagger"] is None and info["sets"]["synth"]["n_texts"] == 1080 and len(info["sets"]["synth"]["files_sha256"]) == 9
    feats = pd.read_csv(out / "lexical_features.csv")
    assert set(feats.model_style) == {"O", "F", "C"} and (feats[(feats.model_style == "O") & (feats["rank"] == 1)].set_index("teacher").feature.loc["alpha"] == "indeed")
    # a second run writes byte-identical tables
    out2 = tmp_path / "out2"
    subprocess.run(cmd[:cmd.index("--out") + 1] + [str(out2)] + cmd[cmd.index("--out") + 2 :], cwd=ROOT, capture_output=True, text=True, check=True)
    assert (out / "lexical_accuracy.csv").read_bytes() == (out2 / "lexical_accuracy.csv").read_bytes()
    assert (out / "lexical_features.csv").read_bytes() == (out2 / "lexical_features.csv").read_bytes()
    bad = subprocess.run(cmd[:2] + ["--sets", "a,b", "--sft-dirs", str(sft), "--out", str(tmp_path / "x")], cwd=ROOT, capture_output=True, text=True)
    assert bad.returncode != 0 and "same length" in bad.stderr
