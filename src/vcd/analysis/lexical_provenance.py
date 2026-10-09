"""Lexical-provenance baseline of E7 (tasks/e7_plan.md §1 last row, §4 last paragraph).

Question: can a purely lexical / stylistic classifier tell WHICH TEACHER wrote a demonstration, and does that cue survive
the F / C register rewriting? The behavioural detector (vcd.analysis.provenance) works on the students' answers; this
baseline works on the TRAINING TEXTS (the rationale of each SFT target), because the student checkpoints were deleted and
cannot generate text (disclosed in e7_plan §1 / §6). The contrast is qualitative: lexical cues are expected to be destroyed
by the rewriter while behavioural cues survive.

Data: {sft_dir}/{teacher}_{O|F|C}_s1.jsonl (seed 1 only; other seeds differ in row order). O / F / C of one teacher are
paired (same prompt_id set and letters). Text = rationale part of `text_target` (e3_metrics.rationale_of).

Features (fixed before any result; no tuning on test folds):
  * hashed character 3-5-grams of the lower-cased, whitespace-normalised text (padded with one space on each side) and
    hashed word unigrams + bigrams (tokens = [a-z0-9']+ runs and single punctuation marks); TF counts, each block
    L2-normalised separately, 2**hash_bits buckets per block (default 2**18), deterministic hashing (numpy polynomial
    hash for characters, zlib.crc32 for words; no Python hash randomisation);
  * length-only control: n_words, n_sentences, mean_word_len (e3_metrics.register_features), standardised on the
    training fold;
  * PoS n-grams only if a tagger is importable offline (`pos_tagger_available`); none is in this venv, so they are skipped.

Classifier: multinomial logistic regression with L2 (C = 1.0, balanced class weights, lbfgs, max_iter 1000); scikit-learn
when importable, otherwise the scipy L-BFGS fit `fit_logreg(..., backend="numpy")` of the same objective.

Evaluations (`run_evaluations`), each reported per teacher with Wilson 95% CIs, macro (= balanced) accuracy and pooled
accuracy; chance = 1/3:
  1. within-style 5-fold CV on O (folds grouped by family_id so a held-out family is never seen in training);
  2. leave-one-style-out: train on all O, test on F and on C of the SAME prompts (the brief's design) and, in addition,
     family-disjoint (the fold models of 1 applied to the F / C texts of the held-out families; no content memorisation);
  3. reverse: train on F + C, test on O (same prompts and family-disjoint), descriptive;
  4. within-style CV on F and on C (any teacher-specific lexical signature left by the rewriter);
  5. the length-only control on the same grid;
  6. nearest O-style centroid (cosine) of every F / C text: share whose nearest centroid is its own teacher.
`top_word_features` lists the most teacher-discriminative word features of the O (and F / C) models with their rates per
1,000 tokens in the teacher's O / F / C texts and in the other teachers' O texts; `cue_survival` counts how many of the top
O cues keep at least half their rate after rewriting.
"""

from __future__ import annotations

import json
import re
import time
import zlib
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import numpy as np
import pandas as pd
import scipy.sparse as sp

from vcd.analysis.e3_metrics import rationale_of, register_features, wilson_ci

TEACHERS: tuple[str, ...] = ("gpt4o", "claude46", "deepseek_v4")
STYLES: tuple[str, ...] = ("O", "F", "C")
CHANCE = 1.0 / 3.0
LENGTH_FEATURES: tuple[str, ...] = ("n_words", "n_sentences", "mean_word_len")
DEFAULT_C = 1.0
DEFAULT_MAX_ITER = 1000
DEFAULT_TOL = 1e-4  # sklearn's default lbfgs tolerance; fixed, not tuned

_TOKEN_RE = re.compile(r"[a-z0-9]+(?:'[a-z]+)?|[^\sa-z0-9]")
_WS_RE = re.compile(r"\s+")
_MIX = np.uint32(0x9E3779B1)
_BASE = np.uint32(257)


# --------------------------------------------------------------------------- data


def load_sft_texts(sft_dir: Path | str, teachers: Sequence[str] = TEACHERS, styles: Sequence[str] = STYLES, seed: int = 1) -> pd.DataFrame:
    """Rationale texts of {sft_dir}/{teacher}_{style}_s{seed}.jsonl: columns teacher, style, prompt_id, family_id, letter, text."""
    sft_dir = Path(sft_dir)
    rows = []
    for t in teachers:
        for s in styles:
            path = sft_dir / f"{t}_{s}_s{seed}.jsonl"
            if not path.exists():
                raise FileNotFoundError(f"missing SFT file {path}")
            with path.open(encoding="utf-8") as fh:
                for line in fh:
                    if not line.strip():
                        continue
                    r = json.loads(line)
                    rows.append(dict(teacher=t, style=s, prompt_id=r["prompt_id"], family_id=r.get("family_id", r["prompt_id"].split(".")[0]), letter=r.get("letter"), text=rationale_of(r["text_target"])))
    return pd.DataFrame(rows, columns=["teacher", "style", "prompt_id", "family_id", "letter", "text"])


def inventory(df: pd.DataFrame, teachers: Sequence[str] = TEACHERS, styles: Sequence[str] = STYLES) -> pd.DataFrame:
    """Per teacher: n per style, paired (same prompt_id set and same letters across styles), n_families, share of its
    prompts answered by every other teacher (`prompt_overlap_all`), source mix of its family_ids, mean words per style."""
    out = []
    pid_sets = {t: set(df[(df.teacher == t) & (df["style"] == styles[0])].prompt_id) for t in teachers}
    for t in teachers:
        d = df[df.teacher == t]
        base = d[d["style"] == styles[0]].set_index("prompt_id")
        paired = True
        for s in styles[1:]:
            ds = d[d["style"] == s].set_index("prompt_id")
            paired &= set(ds.index) == set(base.index) and (len(base) > 0) and bool((ds.loc[base.index, "letter"] == base["letter"]).all())
        others = [pid_sets[u] for u in teachers if u != t]
        common = set.intersection(pid_sets[t], *others) if others else pid_sets[t]
        src = Counter(f.split("_")[0] for f in base.family_id) if len(base) else Counter()
        row = dict(teacher=t, **{f"n_{s}": int((d["style"] == s).sum()) for s in styles}, paired=bool(paired), n_families=int(base.family_id.nunique()),
                   prompt_overlap_all=(len(common) / len(pid_sets[t])) if pid_sets[t] else np.nan, sources=" ".join(f"{k}:{v}" for k, v in sorted(src.items())),
                   **{f"mean_words_{s}": float(np.mean([len(x.split()) for x in d[d["style"] == s].text])) if (d["style"] == s).any() else np.nan for s in styles})
        out.append(row)
    return pd.DataFrame(out)


def family_folds(family_ids: Sequence[str], n_folds: int = 5, seed: int = 0) -> np.ndarray:
    """Fold id (0..n_folds-1) of every item, grouped by family: families are shuffled with `seed` and dealt round-robin,
    so one family is always in one fold (for every teacher and style that contains it)."""
    fams = sorted(set(map(str, family_ids)))
    rng = np.random.default_rng([seed, zlib.crc32(b"lexical_provenance_folds")])
    perm = rng.permutation(len(fams))
    fold_of = {fams[i]: k % n_folds for k, i in enumerate(perm)}
    return np.array([fold_of[str(f)] for f in family_ids], dtype=int)


def pos_tagger_available() -> Optional[str]:
    """Name of an importable offline PoS tagger with its model present, else None (nothing is downloaded)."""
    try:  # nltk needs the averaged_perceptron_tagger data on disk
        import nltk  # type: ignore

        nltk.data.find("taggers/averaged_perceptron_tagger_eng")
        return "nltk"
    except Exception:
        pass
    try:
        import spacy  # type: ignore

        spacy.load("en_core_web_sm")
        return "spacy"
    except Exception:
        return None


# --------------------------------------------------------------------------- features


def normalise_text(text: str) -> str:
    return _WS_RE.sub(" ", text.lower()).strip()


def word_tokens(text: str) -> list[str]:
    """Lower-cased word tokens ([a-z0-9']+ runs) and single punctuation marks."""
    return _TOKEN_RE.findall(normalise_text(text))


def word_ngrams(tokens: Sequence[str], n_max: int = 2) -> list[str]:
    out = list(tokens)
    for n in range(2, n_max + 1):
        out += [" ".join(tokens[i : i + n]) for i in range(len(tokens) - n + 1)]
    return out


def _char_buckets(text: str, n_min: int, n_max: int, bits: int, seed: int) -> np.ndarray:
    """Hash buckets of every character n-gram (bytes of the padded normalised text), n_min <= n <= n_max."""
    b = np.frombuffer((" " + normalise_text(text) + " ").encode("utf-8"), dtype=np.uint8).astype(np.uint32)
    shift = np.uint32(32 - bits)
    out = []
    for n in range(n_min, n_max + 1):
        m = len(b) - n + 1
        if m <= 0:
            continue
        salt = np.uint32((seed + n * 0x51ED270B) & 0xFFFFFFFF)  # per-length salt, computed in Python ints (no uint32 scalar overflow)
        h = np.zeros(m, dtype=np.uint32)
        for k in range(n):
            h = h * _BASE + b[k : k + m]
        h = (h ^ salt) * _MIX
        out.append(h >> shift)
    return np.concatenate(out) if out else np.zeros(0, dtype=np.uint32)


@dataclass
class HashedFeaturizer:
    """Hashed character 3-5-grams + word uni / bigrams, TF, each block L2-normalised; 2**hash_bits buckets per block."""

    hash_bits: int = 18
    seed: int = 0
    char_range: tuple[int, int] = (3, 5)
    word_nmax: int = 2
    _word_memo: dict[str, int] = field(default_factory=dict, repr=False)

    @property
    def n_buckets(self) -> int:
        return 1 << self.hash_bits

    @property
    def n_features(self) -> int:
        return 2 * self.n_buckets

    def word_bucket(self, token: str) -> int:
        b = self._word_memo.get(token)
        if b is None:
            b = zlib.crc32(token.encode("utf-8"), self.seed & 0xFFFFFFFF) & (self.n_buckets - 1)
            self._word_memo[token] = b
        return b

    def transform(self, texts: Sequence[str]) -> sp.csr_matrix:
        """CSR matrix (n_texts, 2 * n_buckets): columns [0, n_buckets) = characters, [n_buckets, 2 n_buckets) = words."""
        nb = self.n_buckets
        indptr = [0]
        indices: list[np.ndarray] = []
        data: list[np.ndarray] = []
        for text in texts:
            cb = _char_buckets(text, self.char_range[0], self.char_range[1], self.hash_bits, self.seed)
            parts_i, parts_d = [], []
            if cb.size:
                u, c = np.unique(cb, return_counts=True)
                c = c.astype(float)
                parts_i.append(u.astype(np.int64))
                parts_d.append(c / np.sqrt((c**2).sum()))
            wb = Counter(self.word_bucket(g) for g in word_ngrams(word_tokens(text), self.word_nmax))
            if wb:
                u = np.fromiter(wb.keys(), dtype=np.int64, count=len(wb)) + nb
                c = np.fromiter(wb.values(), dtype=float, count=len(wb))
                order = np.argsort(u)
                parts_i.append(u[order])
                parts_d.append(c[order] / np.sqrt((c**2).sum()))
            if parts_i:
                indices.append(np.concatenate(parts_i))
                data.append(np.concatenate(parts_d))
            indptr.append(indptr[-1] + (len(indices[-1]) if parts_i else 0))
        ind = np.concatenate(indices) if indices else np.zeros(0, dtype=np.int64)
        dat = np.concatenate(data) if data else np.zeros(0, dtype=float)
        return sp.csr_matrix((dat, ind, np.asarray(indptr, dtype=np.int64)), shape=(len(texts), 2 * nb))


def length_features(texts: Sequence[str]) -> np.ndarray:
    """Dense (n, 3): n_words, n_sentences, mean_word_len (e3_metrics.register_features)."""
    return np.array([[register_features(t)[f] for f in LENGTH_FEATURES] for t in texts], dtype=float)


# --------------------------------------------------------------------------- classifier


@dataclass
class LogRegModel:
    """Multinomial logistic regression: scores = X @ coef.T + intercept, predict = classes[argmax]."""

    classes: np.ndarray
    coef: np.ndarray  # (K, d)
    intercept: np.ndarray  # (K,)
    mean: Optional[np.ndarray] = None  # dense standardisation (length control)
    scale: Optional[np.ndarray] = None
    backend: str = ""

    def _prep(self, X):
        if self.mean is not None:
            return (np.asarray(X, dtype=float) - self.mean) / self.scale
        return X

    def decision(self, X) -> np.ndarray:
        Xp = self._prep(X)
        return np.asarray(Xp @ self.coef.T) + self.intercept

    def predict(self, X) -> np.ndarray:
        return self.classes[np.argmax(self.decision(X), axis=1)]


def _balanced_weights(y_idx: np.ndarray, K: int) -> np.ndarray:
    counts = np.bincount(y_idx, minlength=K).astype(float)
    return (len(y_idx) / (K * counts))[y_idx]


def _fit_numpy(X, y_idx: np.ndarray, K: int, C: float, sw: np.ndarray, max_iter: int, tol: float = DEFAULT_TOL) -> tuple[np.ndarray, np.ndarray]:
    """Multinomial logistic regression, objective sum_i sw_i * nll_i + ||W||^2 / (2 C) (sklearn's scaling), scipy L-BFGS."""
    from scipy.optimize import minimize

    n, d = X.shape
    Y = np.zeros((n, K))
    Y[np.arange(n), y_idx] = 1.0
    Xs = sp.csr_matrix(X) if sp.issparse(X) else np.asarray(X, dtype=float)

    def f(theta: np.ndarray) -> tuple[float, np.ndarray]:
        W = theta[: K * d].reshape(K, d)
        b = theta[K * d :]
        S = np.asarray(Xs @ W.T) + b
        S -= S.max(axis=1, keepdims=True)
        logZ = np.log(np.exp(S).sum(axis=1))
        logp = S - logZ[:, None]
        loss = -float((sw * logp[np.arange(n), y_idx]).sum()) + 0.5 / C * float((W**2).sum())
        R = (np.exp(logp) - Y) * sw[:, None]
        gW = np.asarray(Xs.T @ R).T + W / C
        gb = R.sum(axis=0)
        return loss, np.concatenate([gW.ravel(), gb])

    res = minimize(f, np.zeros(K * d + K), jac=True, method="L-BFGS-B", options=dict(maxiter=max_iter, maxfun=max_iter * 2, ftol=1e-12, gtol=tol))
    return res.x[: K * d].reshape(K, d), res.x[K * d :]


def fit_logreg(X, y: Sequence[str], C: float = DEFAULT_C, backend: str = "auto", max_iter: int = DEFAULT_MAX_ITER, standardise: bool = False, classes: Optional[Sequence[str]] = None, tol: float = DEFAULT_TOL) -> LogRegModel:
    """L2 multinomial logistic regression with balanced class weights. backend: auto (sklearn if importable) | sklearn | numpy.
    standardise=True (dense features only) fits mean / sd on X and applies them at prediction time. `tol` is the solver's
    stopping tolerance (sklearn's lbfgs tol; the numpy backend's projected-gradient tolerance)."""
    y = np.asarray(y)
    cls = np.asarray(sorted(set(y)) if classes is None else list(classes))
    idx = {c: i for i, c in enumerate(cls)}
    y_idx = np.array([idx[v] for v in y])
    K = len(cls)
    mean = scale = None
    if standardise:
        X = np.asarray(X, dtype=float)
        mean = X.mean(axis=0)
        scale = X.std(axis=0, ddof=1) if len(X) > 1 else np.ones(X.shape[1])
        scale = np.where(scale > 0, scale, 1.0)
        X = (X - mean) / scale
    if backend == "auto":
        try:
            import sklearn  # noqa: F401

            backend = "sklearn"
        except ImportError:
            backend = "numpy"
    d = X.shape[1]
    present = np.unique(y_idx)  # classes with training examples; absent classes get an intercept of -1e9 (never predicted)
    coef, intercept = np.zeros((K, d)), np.full(K, -1e9)
    if len(present) == 1:
        intercept[present[0]] = 0.0
    elif backend == "sklearn":
        from sklearn.linear_model import LogisticRegression

        clf = LogisticRegression(C=C, solver="lbfgs", max_iter=max_iter, class_weight="balanced", tol=tol)  # L2 is the default penalty
        clf.fit(X, y_idx)
        rows, ints = np.asarray(clf.coef_, dtype=float), np.asarray(clf.intercept_, dtype=float)
        if len(clf.classes_) == 2 and rows.shape[0] == 1:  # sklearn's binary parametrisation -> two symmetric rows
            rows, ints = np.vstack([-rows[0] / 2, rows[0] / 2]), np.array([-ints[0] / 2, ints[0] / 2])
        coef[clf.classes_], intercept[clf.classes_] = rows, ints
    elif backend == "numpy":
        remap = {c: i for i, c in enumerate(present)}
        sub = np.array([remap[v] for v in y_idx])
        rows, ints = _fit_numpy(X, sub, len(present), C, _balanced_weights(sub, len(present)), max_iter, tol)
        coef[present], intercept[present] = rows, ints
    else:
        raise ValueError(f"unknown backend {backend!r}")
    return LogRegModel(classes=cls, coef=coef, intercept=intercept, mean=mean, scale=scale, backend=backend)


# --------------------------------------------------------------------------- accuracy tables


def accuracy_rows(y_true: Sequence[str], y_pred: Sequence[str], teachers: Sequence[str] = TEACHERS, **tags) -> list[dict]:
    """Per-teacher accuracy (Wilson 95% CI), macro (mean of per-teacher accuracies; normal-approximation CI from the
    independent binomials) and pooled accuracy (Wilson); `tags` are copied into every row."""
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    rows, accs, vars_ = [], [], []
    for t in teachers:
        m = y_true == t
        n, k = int(m.sum()), int((y_pred[m] == t).sum())
        lo, hi = wilson_ci(k, n) if n else (np.nan, np.nan)
        acc = k / n if n else np.nan
        rows.append(dict(**tags, teacher=t, n=n, n_correct=k, acc=acc, ci_lo=lo, ci_hi=hi))
        if n:
            accs.append(acc)
            vars_.append(acc * (1 - acc) / n)
    if accs:
        macro = float(np.mean(accs))
        se = float(np.sqrt(np.sum(vars_)) / len(accs))
        rows.append(dict(**tags, teacher="macro", n=int(len(y_true)), n_correct=int((y_true == y_pred).sum()), acc=macro, ci_lo=max(0.0, macro - 1.959964 * se), ci_hi=min(1.0, macro + 1.959964 * se)))
    n, k = int(len(y_true)), int((y_true == y_pred).sum())
    lo, hi = wilson_ci(k, n) if n else (np.nan, np.nan)
    rows.append(dict(**tags, teacher="pooled", n=n, n_correct=k, acc=k / n if n else np.nan, ci_lo=lo, ci_hi=hi))
    return rows


def confusion_rows(y_true: Sequence[str], y_pred: Sequence[str], teachers: Sequence[str] = TEACHERS, **tags) -> list[dict]:
    y_true, y_pred = np.asarray(y_true), np.asarray(y_pred)
    out = []
    for t in teachers:
        m = y_true == t
        out.append(dict(**tags, true_teacher=t, n=int(m.sum()), **{f"pred_{u}": int((y_pred[m] == u).sum()) for u in teachers}))
    return out


# --------------------------------------------------------------------------- evaluation grid


@dataclass
class EvalResult:
    accuracy: pd.DataFrame
    confusion: pd.DataFrame
    models: dict[str, LogRegModel]  # "O_full", "F_full", "C_full", "FC_full" (n-gram models on every text of the style)
    folds: np.ndarray
    info: dict


def _predict_rows(name: str, feats: str, train: str, test: str, overlap: str, y_true, y_pred, teachers, set_name: str) -> tuple[list[dict], list[dict]]:
    tags = dict(set=set_name, evaluation=name, features=feats, train=train, test=test, overlap=overlap)
    return accuracy_rows(y_true, y_pred, teachers, **tags), confusion_rows(y_true, y_pred, teachers, **tags)


def run_evaluations(df: pd.DataFrame, set_name: str, featurizer: Optional[HashedFeaturizer] = None, n_folds: int = 5, seed: int = 0, C: float = DEFAULT_C, backend: str = "auto",
                    max_iter: int = DEFAULT_MAX_ITER, teachers: Sequence[str] = TEACHERS, styles: Sequence[str] = STYLES, log=None) -> EvalResult:
    """The whole grid of the module docstring on one set (df from load_sft_texts). Evaluations:
    within_O / within_F / within_C (family-grouped CV), O->F / O->C (same_prompts and family_disjoint), F+C->O (both),
    each for features = ngram and length; nearest_centroid (ngram space) for F / C (both overlaps) and O (family_disjoint)."""
    t0 = time.time()
    featurizer = featurizer or HashedFeaturizer(hash_bits=18, seed=seed)
    o_style, rew = styles[0], list(styles[1:])
    df = df.reset_index(drop=True)
    folds = family_folds(df.family_id.to_numpy(), n_folds=n_folds, seed=seed)
    y = df.teacher.to_numpy()
    sty = df["style"].to_numpy()
    say = log or (lambda *_: None)
    say(f"[{set_name}] featurising {len(df)} texts ...")
    X_ng = featurizer.transform(df.text.tolist())
    X_len = length_features(df.text.tolist())
    say(f"[{set_name}] features done in {time.time() - t0:.1f}s; nnz {X_ng.nnz}")
    acc_rows: list[dict] = []
    conf_rows: list[dict] = []
    models: dict[str, LogRegModel] = {}

    def fit(mask: np.ndarray, feats: str) -> LogRegModel:
        if feats == "ngram":
            return fit_logreg(X_ng[mask], y[mask], C=C, backend=backend, max_iter=max_iter, classes=teachers)
        return fit_logreg(X_len[mask], y[mask], C=C, backend=backend, max_iter=max_iter, standardise=True, classes=teachers)

    def predict(model: LogRegModel, mask: np.ndarray, feats: str) -> np.ndarray:
        return model.predict(X_ng[mask] if feats == "ngram" else X_len[mask])

    idx_style = {s: sty == s for s in styles}
    for feats in ("ngram", "length"):
        # (1) within-style CV on O, with the fold models reused for family-disjoint O -> F / C  (2b)
        for s in styles:
            pred = np.full(len(df), "", dtype=object)
            pred_other = {u: np.full(len(df), "", dtype=object) for u in (rew if s == o_style else [])}
            for k in range(n_folds):
                tr = idx_style[s] & (folds != k)
                te = idx_style[s] & (folds == k)
                if tr.sum() == 0 or te.sum() == 0:
                    continue
                m = fit(tr, feats)
                pred[te] = predict(m, te, feats)
                for u in pred_other:
                    te_u = idx_style[u] & (folds == k)
                    if te_u.sum():
                        pred_other[u][te_u] = predict(m, te_u, feats)
            m_te = idx_style[s] & (pred != "")
            a, c = _predict_rows(f"within_{s}", feats, s, s, "family_disjoint_cv", y[m_te], pred[m_te], teachers, set_name)
            acc_rows += a
            conf_rows += c
            for u, p in pred_other.items():
                m_u = idx_style[u] & (p != "")
                a, c = _predict_rows(f"{o_style}->{u}", feats, o_style, u, "family_disjoint", y[m_u], p[m_u], teachers, set_name)
                acc_rows += a
                conf_rows += c
            say(f"[{set_name}] {feats} within_{s} done ({time.time() - t0:.1f}s)")
        # (2a) train on ALL O, test on F / C of the same prompts
        m_o = fit(idx_style[o_style], feats)
        if feats == "ngram":
            models[f"{o_style}_full"] = m_o
        for u in rew:
            a, c = _predict_rows(f"{o_style}->{u}", feats, o_style, u, "same_prompts", y[idx_style[u]], predict(m_o, idx_style[u], feats), teachers, set_name)
            acc_rows += a
            conf_rows += c
        # (3) reverse: F + C -> O, same prompts and family-disjoint
        if rew:
            m_fc_mask = np.zeros(len(df), dtype=bool)
            for u in rew:
                m_fc_mask |= idx_style[u]
            m_fc = fit(m_fc_mask, feats)
            if feats == "ngram":
                models["+".join(rew) + "_full"] = m_fc
            a, c = _predict_rows("+".join(rew) + f"->{o_style}", feats, "+".join(rew), o_style, "same_prompts", y[idx_style[o_style]], predict(m_fc, idx_style[o_style], feats), teachers, set_name)
            acc_rows += a
            conf_rows += c
            pred = np.full(len(df), "", dtype=object)
            for k in range(n_folds):
                tr = m_fc_mask & (folds != k)
                te = idx_style[o_style] & (folds == k)
                if tr.sum() == 0 or te.sum() == 0:
                    continue
                pred[te] = predict(fit(tr, feats), te, feats)
            m_te = idx_style[o_style] & (pred != "")
            a, c = _predict_rows("+".join(rew) + f"->{o_style}", feats, "+".join(rew), o_style, "family_disjoint", y[m_te], pred[m_te], teachers, set_name)
            acc_rows += a
            conf_rows += c
        if feats == "ngram":  # full F / C models for the feature tables
            for u in rew:
                models[f"{u}_full"] = fit(idx_style[u], feats)
        say(f"[{set_name}] {feats} transfer rows done ({time.time() - t0:.1f}s)")

    # (6) nearest O-style centroid in the n-gram space (cosine)
    def centroids(mask: np.ndarray) -> np.ndarray:
        M = np.zeros((len(teachers), X_ng.shape[1]))
        for i, t in enumerate(teachers):
            mt = mask & (y == t)
            if mt.sum():
                v = np.asarray(X_ng[mt].mean(axis=0)).ravel()
                M[i] = v / (np.linalg.norm(v) or 1.0)
        return M

    def nearest(mask: np.ndarray, M: np.ndarray) -> np.ndarray:
        return np.asarray(teachers)[np.argmax(np.asarray(X_ng[mask] @ M.T), axis=1)]

    M_all = centroids(idx_style[o_style])
    for u in rew:
        a, c = _predict_rows(f"{o_style}->{u}", "ngram_centroid", o_style, u, "same_prompts", y[idx_style[u]], nearest(idx_style[u], M_all), teachers, set_name)
        acc_rows += a
        conf_rows += c
    for u in styles:
        pred = np.full(len(df), "", dtype=object)
        for k in range(n_folds):
            tr = idx_style[o_style] & (folds != k)
            te = idx_style[u] & (folds == k)
            if tr.sum() and te.sum():
                pred[te] = nearest(te, centroids(tr))
        m_te = idx_style[u] & (pred != "")
        name = f"within_{u}" if u == o_style else f"{o_style}->{u}"
        a, c = _predict_rows(name, "ngram_centroid", o_style, u, "family_disjoint_cv" if u == o_style else "family_disjoint", y[m_te], pred[m_te], teachers, set_name)
        acc_rows += a
        conf_rows += c
    info = dict(set=set_name, n_texts=int(len(df)), n_families=int(df.family_id.nunique()), n_folds=n_folds, seed=seed, C=C, hash_bits=featurizer.hash_bits, n_features=featurizer.n_features, nnz=int(X_ng.nnz),
                backend=next(iter(models.values())).backend if models else backend, runtime_s=time.time() - t0)
    return EvalResult(accuracy=pd.DataFrame(acc_rows), confusion=pd.DataFrame(conf_rows), models=models, folds=folds, info=info)


# --------------------------------------------------------------------------- discriminative word features


def top_word_features(model: LogRegModel, featurizer: HashedFeaturizer, df: pd.DataFrame, model_style: str, set_name: str, k: int = 20, min_df: int = 20,
                      teachers: Sequence[str] = TEACHERS, styles: Sequence[str] = STYLES) -> pd.DataFrame:
    """Top-k word features (uni / bigrams) per teacher of a hashed n-gram model: the word-block buckets with the largest
    coefficient for that class, named by the tokens observed in >= min_df of the model style's texts that hash there
    (`collision` when several such tokens share the bucket), with rates per 1,000 word tokens in the teacher's own
    O / F / C texts and in the OTHER teachers' texts of the model style."""
    nb = featurizer.n_buckets
    ms = df[df["style"] == model_style]
    # document frequency (model style, all teachers) and token counts per (teacher, style)
    df_count: Counter = Counter()
    counts: dict[tuple[str, str], Counter] = {}
    totals: dict[tuple[str, str], int] = {}
    for (t, s), g in df.groupby(["teacher", "style"], sort=False):
        c: Counter = Counter()
        tot = 0
        for text in g.text:
            toks = word_tokens(text)
            tot += len(toks)
            grams = word_ngrams(toks, featurizer.word_nmax)
            c.update(grams)
            if s == model_style:
                df_count.update(set(grams))
        counts[(t, s)] = c
        totals[(t, s)] = tot
    bucket_tokens: dict[int, list[str]] = {}
    for tok, n in df_count.items():
        if n >= min_df:
            bucket_tokens.setdefault(featurizer.word_bucket(tok), []).append(tok)
    w = model.coef[:, nb:]
    rows = []
    for i, t in enumerate(model.classes):
        if t not in teachers:
            continue
        order = np.argsort(-w[i])
        rank = 0
        for j in order:
            toks = bucket_tokens.get(int(j))
            if not toks or w[i, j] <= 0:
                continue
            rank += 1
            tok = max(toks, key=lambda x: df_count[x])
            others = [u for u in teachers if u != t]
            tot_others = sum(totals.get((u, model_style), 0) for u in others)
            row = dict(set=set_name, model_style=model_style, teacher=t, rank=rank, feature="|".join(sorted(toks, key=lambda x: -df_count[x])), kind="bigram" if " " in tok else "word", collision=len(toks) > 1,
                       coef=float(w[i, j]), df_model_style=int(df_count[tok]))
            for s in styles:
                row[f"rate_{s}_own"] = 1000.0 * counts.get((t, s), Counter())[tok] / max(1, totals.get((t, s), 0))
            row[f"rate_{model_style}_others"] = 1000.0 * sum(counts.get((u, model_style), Counter())[tok] for u in others) / max(1, tot_others)
            rows.append(row)
            if rank >= k:
                break
    return pd.DataFrame(rows)


def cue_survival(feats: pd.DataFrame, o: str = "O", rewrites: Sequence[str] = ("F", "C"), k: int = 20) -> pd.DataFrame:
    """Per set x teacher: of the top-k word features of the O model (top_word_features), how many keep at least half of
    their O rate in the teacher's F / C texts (`kept_F`, `kept_C`) and which ones lose more than half (`removed_F`,
    `removed_C`; the rewriter erased them)."""
    rows = []
    for (set_name, t), g in feats[feats.model_style == o].groupby(["set", "teacher"], sort=False):
        g = g.sort_values("rank").head(k)
        row: dict = dict(set=set_name, teacher=t, n=int(len(g)))
        for u in rewrites:
            kept = g[f"rate_{u}_own"] >= 0.5 * g[f"rate_{o}_own"]
            row[f"kept_{u}"] = int(kept.sum())
            row[f"removed_{u}"] = ", ".join(g.loc[~kept, "feature"].tolist()) or "—"
        rows.append(row)
    return pd.DataFrame(rows, columns=["set", "teacher", "n", *[c for u in rewrites for c in (f"kept_{u}", f"removed_{u}")]])


# --------------------------------------------------------------------------- summary helpers


def fmt_acc(row: Mapping) -> str:
    if row is None or pd.isna(row.get("acc", np.nan)):
        return "—"
    return f"{row['acc']:.3f} [{row['ci_lo']:.3f}, {row['ci_hi']:.3f}]"


def accuracy_table(acc: pd.DataFrame, teachers: Sequence[str] = TEACHERS) -> pd.DataFrame:
    """Wide table: one row per (set, features, evaluation, overlap) with 'acc [lo, hi]' per teacher, macro and pooled."""
    keys = ["set", "features", "evaluation", "train", "test", "overlap"]
    out = []
    for key, g in acc.groupby(keys, sort=False):
        d = dict(zip(keys, key))
        gi = g.set_index("teacher")
        for t in [*teachers, "macro", "pooled"]:
            d[t] = fmt_acc(gi.loc[t].to_dict()) if t in gi.index else "—"
        d["n"] = int(gi.loc["pooled", "n"]) if "pooled" in gi.index else 0
        d["macro_acc"] = float(gi.loc["macro", "acc"]) if "macro" in gi.index else np.nan
        d["macro_ci_lo"] = float(gi.loc["macro", "ci_lo"]) if "macro" in gi.index else np.nan
        out.append(d)
    return pd.DataFrame(out)
