"""E7: black-box provenance of a distilled student (tasks/e7_plan.md §2-§4; pre-registered 2026-10-08 before any provenance result).

Question (RQ4): from the BEHAVIOUR of one suspect model alone, can a detector tell which candidate teacher it was
distilled from, and does that survive register rewriting (F / C)? Everything here is a pure function of the students'
eval response files, the teacher profiles and the split's prompt file; nothing calls an API or a GPU, and the test
split is read only by the script, once, with a dev calibration file.

Detector (plan §3, implemented literally):
  * fingerprint a_t(run) = cell-weighted majority-action agreement with candidate teacher t over the seen framings
    (`e1_metrics.teacher_agreement`: cells where either p_sym is exactly 0.5 are excluded). The observed values in the
    run table come from that function; the matrix engine used for probe subsets, budgets and the sampled readout is
    checked against it at run time (`build_world` raises on any mismatch).
  * scores: base-known s_t = a_t(run) - a_t(S_0); base-unknown s_t = a_t(run) - mean over candidates of a_t'(run).
  * decision: t* = argmax_t s_t, margin = s_{t*} - second largest; attributed to t* iff margin > tau, else "unattributed"
    (a run with fewer than two finite scores is unattributed with a NaN margin).
  * tau: calibrated on dev so that the share of dev negatives (K, K_n, R, S_0) attributed to ANY teacher is <= 5%
    (the smallest tau that satisfies it; fewer than 20 negatives -> tau = 0, flagged). One tau per detector
    configuration (variant x readout x probe subset x budget), all written to calibration.json by the dev run and
    REUSED on test (`taus_from_calibration`); the script refuses to recalibrate on test.
  * sampled-answer readout: per cell and option order, n Bernoulli draws from the stored probability of the focus act,
    majority (a tie drops that order), symmetrized exactly like `sym_table` (p_sym = mean of the two order majorities,
    so disagreeing orders give 0.5 and fall under the tie rule); n in {1, 3, 10}, 200 repetitions with a fixed seed.
    The teacher references and the base reference stay probability-based (the detector owns the candidates' profiles
    and, when the base is known, the base).
  * probes: all cells; teacher-disagreement cells (every candidate has a defined majority and they are not all equal,
    computed from the teacher profiles only); random k families x 200 repetitions for the budget curve.
  * leave-one-style-out: calibration from O / R / B runs only (the negatives are all O / R / B, so this is the main
    tau by construction; `loso_population` makes the restriction explicit), evaluated on the F / C students.
    Leave-one-grid-out: calibration on the E1 grid (ALL its runs, the 15 O students included, treated as the reject
    population) plus the K / K_n negatives, evaluated on the other grids.
Metrics (plan §4): per-teacher recall with Wilson 95% CI (unattributed counts as wrong), macro recall, open-set FPR on
the negatives, one-vs-rest AUROC on s_t (positives = runs truly from t, negatives = every other run incl. "none"),
chance = (1/K)(1 - unattributed rate), and a run-label permutation p for the macro recall (seeds of one teacher are
near-replicates, so that p is descriptive, as in e1_metrics).
"""

from __future__ import annotations

import json
import math
import warnings
import zlib
from pathlib import Path
from typing import Iterable, Mapping, NamedTuple, Optional, Sequence

import numpy as np
import pandas as pd
from scipy.stats import rankdata

from vcd.analysis import e1_metrics as M
from vcd.analysis.e1_metrics import SEEN_VARIANTS, is_run_id, parse_run_id
from vcd.analysis.e3_metrics import wilson_ci
from vcd.io import load_models
from vcd.schemas import Prompt, TeacherResponse

# --------------------------------------------------------------------------- protocol constants (tasks/e7_plan.md §2-§4)

GRID_BY_NAMESPACE: dict[str, str] = {
    "qwen3-4b": "E1",
    "qwen3-4b-paired": "E3",
    "qwen3-4b-e2c": "E2c_C",
    "qwen3-4b-e2ck": "K",
    "qwen3-4b-e2ckn": "K_n",
    "qwen3-4b-e2cnf": "Cnf",
    "qwen3-4b-e2c-paired": "E3c",
    # archived recipes (dev readouts only): descriptive, never in a calibration or an inferential row
    "qwen3-4b-e2c-3ep": "E2c_C_3ep",
    "qwen3-4b-e2ck-3ep": "K_3ep",
    "qwen3-4b-e2cnf-5ep": "Cnf_5ep",
}
CORE_NAMESPACES: tuple[str, ...] = ("qwen3-4b", "qwen3-4b-paired", "qwen3-4b-e2c", "qwen3-4b-e2ck", "qwen3-4b-e2ckn", "qwen3-4b-e2cnf", "qwen3-4b-e2c-paired")
ARCHIVED_NAMESPACES: tuple[str, ...] = ("qwen3-4b-e2c-3ep", "qwen3-4b-e2ck-3ep", "qwen3-4b-e2cnf-5ep")
NEGATIVE_GRIDS: tuple[str, ...] = ("K", "K_n", "K_3ep")  # consensus-trained students: distilled, but from no specific teacher
POSITIVE_VERSIONS: tuple[str, ...] = ("O", "F", "C")
NONE = "none"
DETECTORS: tuple[str, ...] = ("base_known", "base_unknown")
FPR_MAX = 0.05
N_NEG_MIN = 20
N_REP = 200
BUDGETS: tuple[int, ...] = (30, 60, 100, 150, 300)
SAMPLE_N: tuple[int, ...] = (1, 3, 10)
LOGO_GRIDS: tuple[str, ...] = ("E1", "K", "K_n")
LOSO_VERSIONS: tuple[str, ...] = ("O", "R", "B")
GRID_ORDER: tuple[str, ...] = ("E2c_C", "E1", "E3", "E3c", "Cnf", "K", "K_n")
PRIMARY = {"grid": "E2c_C", "version": "O", "detector": "base_known", "readout": "probability", "subset": "all"}
RECALL_FLOOR = 1 / 3  # primary verdict: Wilson lower bound of the per-teacher recall must exceed this
FPR_VERDICT_MAX = 0.10
RULE = (
    "a_t = symmetrized majority-action agreement with teacher t (e1_metrics.teacher_agreement, p_sym = 0.5 cells excluded); "
    "base-known s_t = a_t - a_t(S_0), base-unknown s_t = a_t - mean_t' a_t'; t* = argmax s_t, margin = s_t* - second; attributed iff margin > tau; "
    "tau = smallest value with <= 5% of the dev negatives (K, K_n, R, S_0) attributed (fewer than 20 negatives -> tau = 0), one per detector "
    "configuration, reused on test. Primary (E2c-C O students, base-known, probability readout, all probes): teachers whose recall Wilson lower "
    "bound > 1/3: >= 2/3 -> feasible (conditional), 1/3 -> partial, 0/3 -> not feasible; and open-set FPR <= 10%."
)

RUN_COLS = ["run_id", "namespace", "run_dir", "original_id", "grid", "role", "teacher", "version", "seed", "truth", "n_rows", "path"]
METRIC_COLS = ["table", "calibration", "grid", "version", "role", "subset", "readout", "detector", "tau_policy", "tau", "teacher", "n", "n_correct", "recall", "wilson_lo", "wilson_hi",
               "n_unattributed", "unattributed_rate", "macro_recall", "chance", "perm_p", "perm_null_mean", "n_perm", "auroc", "n_auroc_pos", "n_auroc_neg", "fpr", "n_neg", "n_neg_attributed"]


def _nan(x) -> bool:
    return x is None or (isinstance(x, (float, np.floating)) and np.isnan(x))


# --------------------------------------------------------------------------- ground truth and loading


def truth_of(grid: str, version: str, teacher: str, negative_grids: Sequence[str] = NEGATIVE_GRIDS) -> str:
    """Teacher name for O / F / C runs of a teacher-specific grid; "none" for consensus grids (K, K_n), R and B runs."""
    if version not in POSITIVE_VERSIONS or grid in set(negative_grids):
        return NONE
    return teacher


def parse_grid_map(spec: Optional[str], base: Mapping[str, str] = GRID_BY_NAMESPACE) -> dict[str, str]:
    """'ns=GRID,ns2=GRID2' overrides / extends the default namespace -> grid map."""
    out = dict(base)
    if spec:
        for kv in spec.split(","):
            if not kv.strip():
                continue
            ns, grid = kv.split("=", 1)
            out[ns.strip()] = grid.strip()
    return out


def _rel(path: Path) -> str:
    """Path relative to the working directory when it lies inside it (keeps committed outputs free of machine-specific prefixes)."""
    try:
        return str(path.resolve().relative_to(Path.cwd().resolve()))
    except ValueError:
        return str(path)


def load_student_runs(runs_dir: str | Path, split: str, namespaces: Sequence[str], grid_map: Mapping[str, str], prompt_ids: set[str], roles: Mapping[str, str],
                      negative_grids: Sequence[str] = NEGATIVE_GRIDS) -> tuple[list[TeacherResponse], pd.DataFrame, list[str]]:
    """Rows of runs/{namespace}/{run}/eval/{split}_responses.jsonl for every namespace, re-keyed as '{namespace}.{run}'.

    The run id stored in a row's `teacher` field may carry another namespace's prefix (the E3 namespace reuses
    'qwen3-4b.'), so teacher / version / seed come from the run directory name parsed with the protocol pattern and the
    grid label from the namespace. Version-B directories (copies of S_0) are skipped: the base enters once via
    `load_base`. `roles` maps namespace -> 'core' | 'descriptive'. Returns rows, the inventory (RUN_COLS) and notes.
    """
    runs_dir = Path(runs_dir)
    rows: list[TeacherResponse] = []
    inv: list[dict] = []
    notes: list[str] = []
    base_copies: list[str] = []
    for ns in namespaces:
        if ns not in grid_map:
            raise ValueError(f"namespace {ns!r} has no grid label; pass --grid-map {ns}=LABEL")
        grid = grid_map[ns]
        ns_dir = runs_dir / ns
        if not ns_dir.exists():
            notes.append(f"namespace {ns}: directory {ns_dir} missing, skipped")
            continue
        for d in sorted(p for p in ns_dir.iterdir() if p.is_dir()):
            f = d / "eval" / f"{split}_responses.jsonl"
            if not f.exists():
                continue
            rid = f"{ns}.{d.name}"
            if not is_run_id(rid):
                notes.append(f"{_rel(f)}: '{d.name}' is not a protocol run name, skipped")
                continue
            k = parse_run_id(rid)
            if k.version == "B":
                base_copies.append(f"{ns}/{d.name}")
                continue
            loaded = load_models(f, TeacherResponse)
            orig = sorted({r.teacher for r in loaded})
            if any(o.split(".", 1)[-1] != d.name for o in orig):
                notes.append(f"{_rel(f)}: run id inside the file is {orig}, directory is {d.name}; the directory wins")
            kept = [r.model_copy(update={"teacher": rid}) for r in loaded if r.prompt_id in prompt_ids]
            rows += kept
            inv.append(dict(run_id=rid, namespace=ns, run_dir=d.name, original_id=",".join(orig), grid=grid, role=roles.get(ns, "core"), teacher=k.teacher, version=k.version,
                            seed=k.seed, truth=truth_of(grid, k.version, k.teacher, negative_grids), n_rows=len(kept), path=_rel(f)))
    if base_copies:
        notes.append(f"version-B copies skipped (S_0 is read once from --base-run): {', '.join(base_copies)}")
    return rows, pd.DataFrame(inv, columns=RUN_COLS), notes


def load_base(base_run: str | Path, split: str, prompt_ids: set[str], grid_map: Mapping[str, str]) -> tuple[list[TeacherResponse], dict]:
    """Rows of {base_run}/eval/{split}_responses.jsonl re-keyed as '{parent}.{name}' (qwen3-4b.base_B_s0), plus its inventory row (truth none)."""
    base_run = Path(base_run)
    f = base_run / "eval" / f"{split}_responses.jsonl"
    if not f.exists():
        raise FileNotFoundError(f"base run has no {split} readout: {f}")
    rid = f"{base_run.parent.name}.{base_run.name}"
    if not is_run_id(rid) or parse_run_id(rid).version != "B":
        raise ValueError(f"--base-run must be a version-B run directory, got {base_run}")
    k = parse_run_id(rid)
    loaded = load_models(f, TeacherResponse)
    kept = [r.model_copy(update={"teacher": rid}) for r in loaded if r.prompt_id in prompt_ids]
    row = dict(run_id=rid, namespace=base_run.parent.name, run_dir=base_run.name, original_id=",".join(sorted({r.teacher for r in loaded})), grid=grid_map.get(base_run.parent.name, "E1"),
               role="core", teacher=k.teacher, version=k.version, seed=k.seed, truth=NONE, n_rows=len(kept), path=_rel(f))
    return kept, row


def load_teachers(teacher_dir: str | Path, split: str, teachers: Sequence[str], prompt_ids: set[str]) -> list[TeacherResponse]:
    """{teacher_dir}/{teacher}_{split}_profile.jsonl for every candidate; every candidate must exist (the detector needs its full candidate set)."""
    paths = [Path(teacher_dir) / f"{t}_{split}_profile.jsonl" for t in teachers]
    missing = [str(p) for p in paths if not p.exists()]
    if missing:
        raise FileNotFoundError("missing teacher profiles: " + ", ".join(missing))
    return M.load_responses(paths, prompt_ids)


# --------------------------------------------------------------------------- profiles as matrices


class Profiles(NamedTuple):
    """p_sym and the two order probabilities of several profiles on one (family x variant) cell grid."""

    who: list[str]
    families: list[str]
    variants: list[str]
    p: np.ndarray  # (n_who, F, V) symmetrized P(focus act); NaN where the cell is missing
    p_o1: np.ndarray  # (n_who, F, V)
    p_o2: np.ndarray

    @property
    def cells(self) -> np.ndarray:
        """(n_who, F * V) view of p; cell index = family index * V + variant index."""
        return self.p.reshape(len(self.who), -1)


def profiles_from_sym(sym: pd.DataFrame, who: Sequence[str], families: Sequence[str], variants: Sequence[str]) -> Profiles:
    """Pivot a `sym_table` output (teacher, family_id, variant, p_o1, p_o2, p_sym) into (n_who, F, V) matrices."""
    who, families, variants = list(who), list(families), list(variants)
    cols = pd.MultiIndex.from_product([families, variants])
    mats = []
    s = sym[sym["variant"].isin(variants)] if len(sym) else sym
    for col in ("p_sym", "p_o1", "p_o2"):
        if len(s):
            piv = s.pivot_table(index="teacher", columns=["family_id", "variant"], values=col, aggfunc="mean")
            piv = piv.reindex(index=who, columns=cols)
            mats.append(piv.to_numpy(dtype=float).reshape(len(who), len(families), len(variants)))
        else:
            mats.append(np.full((len(who), len(families), len(variants)), np.nan))
    return Profiles(who, families, variants, mats[0], mats[1], mats[2])


def majority(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Majority act (p > 0.5) and validity (finite and not exactly 0.5): the tie rule of e1_metrics._agreement."""
    valid = np.isfinite(p) & (p != 0.5)
    return p > 0.5, valid


def agreement_counts(S: np.ndarray, T: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """S (R, C) and T (K, C) cell probabilities -> agree (R, K, C) and valid (R, K, C) booleans."""
    ms, vs = majority(S)
    mt, vt = majority(T)
    valid = vs[:, None, :] & vt[None, :, :]
    agree = (ms[:, None, :] == mt[None, :, :]) & valid
    return agree, valid


def agreement_rate(agree: np.ndarray, valid: np.ndarray, cell_weights: Optional[np.ndarray] = None) -> np.ndarray:
    """Cell-weighted agreement: (R, K) without weights, (B, R, K) with cell_weights (B, C); NaN where no valid cell."""
    if cell_weights is None:
        num, den = agree.sum(-1).astype(float), valid.sum(-1).astype(float)
    else:
        W = np.asarray(cell_weights, dtype=float)
        num = np.einsum("rkc,bc->brk", agree.astype(float), W)
        den = np.einsum("rkc,bc->brk", valid.astype(float), W)
    with np.errstate(invalid="ignore", divide="ignore"):
        return np.where(den > 0, num / den, np.nan)


def disagreement_cells(T: np.ndarray) -> np.ndarray:
    """(C,) mask of cells where every candidate teacher has a defined majority and the majorities are not all equal (teacher profiles only)."""
    mt, vt = majority(T)
    all_valid = vt.all(axis=0)
    return all_valid & ~(np.all(mt == mt[:1], axis=0))


def family_cell_weights(fam_weights: np.ndarray, n_variants: int) -> np.ndarray:
    """(B, F) family weights -> (B, F * V) cell weights (every variant of a family gets the family's weight)."""
    return np.repeat(np.asarray(fam_weights, dtype=float), n_variants, axis=1)


def probe_masks(n_families: int, k: int, n_rep: int, rng: np.random.Generator) -> np.ndarray:
    """(n_rep, F) 0/1 masks selecting k random families each; k >= F gives one all-ones row (the deterministic 'all' probe)."""
    if k >= n_families:
        return np.ones((1, n_families), dtype=float)
    W = np.zeros((n_rep, n_families), dtype=float)
    for b in range(n_rep):
        W[b, rng.choice(n_families, size=k, replace=False)] = 1.0
    return W


def sample_sym(p_o1: np.ndarray, p_o2: np.ndarray, n: int, rng: np.random.Generator) -> np.ndarray:
    """Sampled-answer readout: n Bernoulli draws per order, majority (ties drop the order), then the sym_table symmetrization.

    Returns p_sym in {0, 0.5, 1} (NaN where an order is missing or tied). 0.5 = the two orders disagree, which the
    agreement's tie rule then excludes, exactly as a probability-mode p_sym of 0.5 would be.
    """

    def side(p: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
        ok = np.isfinite(p)
        draws = rng.binomial(n, np.clip(np.where(ok, p, 0.5), 0.0, 1.0))
        return (draws * 2 > n).astype(float), ok & (draws * 2 != n)

    m1, v1 = side(p_o1)
    m2, v2 = side(p_o2)
    return np.where(v1 & v2, (m1 + m2) / 2, np.nan)


# --------------------------------------------------------------------------- scores, decisions, tau


def scores(a: np.ndarray, detector: str, a_base: Optional[np.ndarray] = None) -> np.ndarray:
    """a (..., K) -> s (..., K): base-known subtracts a_base (broadcastable), base-unknown subtracts the run's candidate mean."""
    if detector == "base_known":
        if a_base is None:
            raise ValueError("base_known needs the base agreement a_t(S_0)")
        return a - a_base
    if detector == "base_unknown":
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", category=RuntimeWarning)
            return a - np.nanmean(a, axis=-1, keepdims=True)
    raise ValueError(f"unknown detector {detector!r}")


def margins(s: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """s (..., K) -> (argmax index, margin = top - second largest); NaN margin when fewer than two scores are finite."""
    if s.shape[-1] < 2:
        raise ValueError("the detector needs at least two candidate teachers")
    x = np.where(np.isfinite(s), s, -np.inf)
    order = np.argsort(-x, axis=-1, kind="stable")
    top = np.take_along_axis(x, order[..., :1], -1)[..., 0]
    second = np.take_along_axis(x, order[..., 1:2], -1)[..., 0]
    n_fin = np.isfinite(s).sum(-1)
    with np.errstate(invalid="ignore"):
        m = np.where(n_fin >= 2, top - second, np.nan)
    return order[..., 0], m


def decide(s: np.ndarray, tau: float) -> tuple[np.ndarray, np.ndarray]:
    """s (..., K) -> (decision index, margin); decision -1 = unattributed (margin <= tau or undefined)."""
    best, m = margins(s)
    with np.errstate(invalid="ignore"):
        attributed = np.isfinite(m) & (m > tau)
    return np.where(attributed, best, -1), m


class Tau(NamedTuple):
    tau: float
    n_neg: int
    n_attributed: int
    fpr: float
    fallback: bool
    note: str


def calibrate_tau(neg_margins: Iterable[float], fpr_max: float = FPR_MAX, n_min: int = N_NEG_MIN) -> Tau:
    """Smallest tau such that the share of negative margins strictly above it is <= fpr_max (plan §3).

    NaN margins (undefined decisions) are never attributed and stay in the denominator. With fewer than `n_min`
    negatives the rule cannot be applied and tau falls back to 0 (every positive margin attributes), flagged.
    """
    m = np.asarray(list(neg_margins), dtype=float).ravel()
    n = int(m.size)
    if n < n_min:
        tau, fallback = 0.0, True
        note = f"only {n} negatives (< {n_min}): tau = 0 fallback"
    else:
        fin = np.sort(m[np.isfinite(m)])[::-1]
        k_allowed = int(math.floor(fpr_max * n + 1e-9))
        tau = float(fin[k_allowed]) if k_allowed < len(fin) else 0.0
        tau, fallback = max(tau, 0.0), False
        note = f"{n} negatives, at most {k_allowed} may be attributed"
    with np.errstate(invalid="ignore"):
        n_att = int(np.sum(m > tau))
    return Tau(tau, n, n_att, (n_att / n) if n else float("nan"), fallback, note)


def cal_key(readout: str, subset: str, detector: str, calibration: str = "main") -> str:
    """Key of one detector configuration in calibration.json: '{calibration}|{readout}|{subset}|{detector}'."""
    return f"{calibration}|{readout}|{subset}|{detector}"


def taus_from_calibration(cal: Mapping) -> dict[str, float]:
    """tau per configuration key from a calibration.json dict (dev run output); used verbatim on test."""
    return {k: float(v["tau"]) for k, v in cal["tau"].items()}


# --------------------------------------------------------------------------- metrics


def auroc(score: Sequence[float], positive: Sequence[bool]) -> tuple[float, int, int]:
    """Rank-based (Mann-Whitney) AUROC of `score` for `positive`; NaN scores dropped; (auroc, n_pos, n_neg)."""
    s = np.asarray(score, dtype=float)
    y = np.asarray(positive, dtype=bool)
    ok = np.isfinite(s)
    s, y = s[ok], y[ok]
    n1, n0 = int(y.sum()), int((~y).sum())
    if n1 == 0 or n0 == 0:
        return float("nan"), n1, n0
    r = rankdata(s, method="average")
    return float((r[y].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)), n1, n0


def chance_level(unattributed_rate: float, n_teachers: int) -> float:
    """Expected recall of a detector that attributes uniformly at random whenever it attributes: (1/K)(1 - unattributed rate)."""
    return (1.0 / n_teachers) * (1.0 - unattributed_rate) if n_teachers else float("nan")


def macro_recall_batch(truth_idx: np.ndarray, dec: np.ndarray, n_teachers: int) -> np.ndarray:
    """truth_idx (P, G) labels and dec (G,) decisions (-1 unattributed) -> (P,) macro recall over the teachers present in the labels."""
    T = np.asarray(truth_idx)
    present = [t for t in range(n_teachers) if np.any(T[0] == t)]
    if not present:
        return np.full(T.shape[0], np.nan)
    rec = []
    for t in present:
        pos = T == t
        with np.errstate(invalid="ignore", divide="ignore"):
            rec.append((pos & (dec == t)[None, :]).sum(1) / pos.sum(1))
    return np.nanmean(np.stack(rec), axis=0)


def permutation_p_macro(truth_idx: np.ndarray, dec: np.ndarray, n_teachers: int, n_perm: int, rng: np.random.Generator) -> tuple[float, float, int]:
    """Permute the teacher labels of the group's runs n_perm times; p = (#(null >= observed) + 1) / (n_perm + 1) for the macro recall."""
    truth_idx = np.asarray(truth_idx)
    obs = float(macro_recall_batch(truth_idx[None, :], dec, n_teachers)[0])
    if n_perm <= 0 or len(truth_idx) < 2 or np.isnan(obs):
        return float("nan"), float("nan"), 0
    perms = truth_idx[np.argsort(rng.random((n_perm, len(truth_idx))), axis=1)]
    null = macro_recall_batch(perms, dec, n_teachers)
    return float((np.sum(null >= obs - 1e-12) + 1) / (n_perm + 1)), float(np.nanmean(null)), int(n_perm)


class Group(NamedTuple):
    grid: str
    version: str
    role: str
    idx: np.ndarray  # row indices into the run table


def eval_groups(runs: pd.DataFrame, order: Sequence[str] = GRID_ORDER) -> tuple[list[Group], list[Group]]:
    """Positive groups (grid, version) with a teacher truth and negative groups (truth none), both in a fixed order."""
    rank = {g: i for i, g in enumerate(order)}
    pos, neg = [], []
    for (grid, version, role), g in runs.groupby(["grid", "version", "role"], sort=False):
        grp = Group(str(grid), str(version), str(role), g.index.to_numpy())
        (pos if (g["truth"] != NONE).any() else neg).append(grp)
    key = lambda x: (0 if x.role == "core" else 1, rank.get(x.grid, len(rank)), x.grid, POSITIVE_VERSIONS.index(x.version) if x.version in POSITIVE_VERSIONS else 9)  # noqa: E731
    return sorted(pos, key=key), sorted(neg, key=key)


def group_rows(truth: np.ndarray, s: np.ndarray, dec: np.ndarray, groups: Sequence[Group], neg_idx: np.ndarray, teachers: Sequence[str], n_perm: int, rng: np.random.Generator,
               meta: Mapping, neg_groups: Sequence[Group] = ()) -> list[dict]:
    """Metric rows for one detector configuration: per group a row per teacher plus a 'macro' row; per negative group a 'none' row.

    truth (R,) strings, s (R, K) scores, dec (R,) decision indices. The open-set FPR (on `neg_idx`) is repeated on
    every row of the configuration; AUROC_t is one-vs-rest over the group's runs plus the negatives.
    """
    teachers = list(teachers)
    K = len(teachers)
    t_idx = {t: i for i, t in enumerate(teachers)}
    with np.errstate(invalid="ignore"):
        fpr = float(np.mean(dec[neg_idx] >= 0)) if len(neg_idx) else float("nan")
    n_neg_att = int(np.sum(dec[neg_idx] >= 0)) if len(neg_idx) else 0
    base = dict(meta) | {"fpr": fpr, "n_neg": int(len(neg_idx)), "n_neg_attributed": n_neg_att}
    rows: list[dict] = []
    for g in groups:
        idx = g.idx
        tr = truth[idx]
        d = dec[idx]
        union = np.concatenate([idx, neg_idx[~np.isin(neg_idx, idx)]]) if len(neg_idx) else idx
        n_unatt = int(np.sum(d < 0))
        unatt_rate = n_unatt / len(idx) if len(idx) else float("nan")
        present = [t for t in teachers if np.any(tr == t)]
        recalls = []
        for t in present:
            pos = tr == t
            n, k = int(pos.sum()), int(np.sum(pos & (d == t_idx[t])))
            lo, hi = wilson_ci(k, n)
            au, n1, n0 = auroc(s[union, t_idx[t]], truth[union] == t)
            recalls.append(k / n)
            rows.append(base | dict(grid=g.grid, version=g.version, role=g.role, teacher=t, n=n, n_correct=k, recall=k / n, wilson_lo=lo, wilson_hi=hi,
                                    n_unattributed=int(np.sum(pos & (d < 0))), unattributed_rate=float(np.mean(d[pos] < 0)), auroc=au, n_auroc_pos=n1, n_auroc_neg=n0))
        tri = np.array([t_idx.get(t, -1) for t in tr])
        p, null_mean, n_done = permutation_p_macro(tri, d, K, n_perm, rng) if present else (float("nan"), float("nan"), 0)
        rows.append(base | dict(grid=g.grid, version=g.version, role=g.role, teacher="macro", n=int(len(idx)), n_correct=int(np.sum((d >= 0) & (tri == d))),
                                recall=float(np.mean(recalls)) if recalls else float("nan"), n_unattributed=n_unatt, unattributed_rate=unatt_rate,
                                macro_recall=float(np.mean(recalls)) if recalls else float("nan"), chance=chance_level(unatt_rate, K), perm_p=p, perm_null_mean=null_mean, n_perm=n_done))
    for g in neg_groups:
        d = dec[g.idx]
        rows.append(base | dict(grid=g.grid, version=g.version, role=g.role, teacher=NONE, n=int(len(g.idx)), n_correct=int(np.sum(d < 0)), recall=float(np.mean(d < 0)),
                                n_unattributed=int(np.sum(d < 0)), unattributed_rate=float(np.mean(d < 0)), macro_recall=float("nan"), chance=float("nan"),
                                fpr=float(np.mean(d >= 0)), n_neg=int(len(g.idx)), n_neg_attributed=int(np.sum(d >= 0))))
    return rows


def aggregate_reps(df: pd.DataFrame, keys: Sequence[str], values: Sequence[str]) -> pd.DataFrame:
    """Mean and 2.5 / 97.5 percentiles over the repetitions (column `rep`) of every value column, per key."""
    if df.empty:
        return pd.DataFrame(columns=[*keys, "n_rep", *[f"{v}_{s}" for v in values for s in ("mean", "lo", "hi")]])
    out = []
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)
        for key, g in df.groupby(list(keys), sort=False, dropna=False):
            row = dict(zip(keys, key if isinstance(key, tuple) else (key,)))
            row["n_rep"] = int(g["rep"].nunique())
            for v in values:
                x = pd.to_numeric(g[v], errors="coerce").to_numpy(dtype=float)
                if np.isfinite(x).any():
                    row[f"{v}_mean"], row[f"{v}_lo"], row[f"{v}_hi"] = float(np.nanmean(x)), *(float(q) for q in np.nanpercentile(x, [2.5, 97.5]))
                else:
                    row[f"{v}_mean"] = row[f"{v}_lo"] = row[f"{v}_hi"] = float("nan")
            out.append(row)
    return pd.DataFrame(out)


# --------------------------------------------------------------------------- the world: everything loaded, as matrices


class World(NamedTuple):
    runs: pd.DataFrame  # inventory (RUN_COLS + answer_rate, n_cells_valid); row order = rows of S
    teachers: list[str]
    families: list[str]
    variants: list[str]
    S: Profiles  # suspects on the seen variants (gated readout; S_0 included as a suspect)
    T: Profiles  # candidate teachers
    S_t0: Optional[Profiles]  # suspects on T0 (descriptive only); None when the prompt file has no T0
    T_t0: Optional[Profiles]
    base_ref: np.ndarray  # (F, V) p_sym of the base reference profile (prior = ungated two-letter probabilities, or gated)
    base_ref_label: str
    base_ref_cells: int
    disagree: np.ndarray  # (C,) teacher-disagreement cells
    agreement: pd.DataFrame  # the e1_metrics.teacher_agreement table on the seen variants (reference values)


def build_world(student_rows: Sequence[TeacherResponse], base_rows: Sequence[TeacherResponse], teacher_rows: Sequence[TeacherResponse], prompts: Mapping[str, Prompt],
                inventory: pd.DataFrame, teachers: Sequence[str], variants: Sequence[str] = SEEN_VARIANTS, base_reference: str = "prior", t0: str = "T0") -> World:
    """sym tables -> cell matrices; checks the matrix agreement against `e1_metrics.teacher_agreement` and raises on any mismatch.

    `base_reference` = 'prior': the base-known reference is S_0's ungated two-letter profile on EVERY cell
    (`sym_table(mass_gate=False)`, the same object as E2's covariate r_0: the detector owns the base and reads its
    probabilities); 'gated': the ordinary 0.9-gated readout (few cells for an untrained base). As a SUSPECT S_0 always
    gets the gated readout like every other run.
    """
    prompts = dict(prompts)
    teachers, variants = list(teachers), list(variants)
    families = sorted({p.family_id for p in prompts.values()})
    inv = inventory.reset_index(drop=True).copy()
    fs = M.frame_table(list(student_rows) + list(base_rows), prompts)
    sym_s = M.sym_table(fs) if len(fs) else pd.DataFrame(columns=["teacher", "family_id", "variant", "p_o1", "p_o2", "p_sym", "order_gap"])
    ft = M.frame_table(list(teacher_rows), prompts)
    sym_t = M.sym_table(ft)
    missing = [t for t in teachers if t not in set(sym_t["teacher"])]
    if missing:
        raise ValueError(f"teacher profiles without rows on this split: {missing}")
    who = list(inv["run_id"])
    S = profiles_from_sym(sym_s, who, families, variants)
    T = profiles_from_sym(sym_t, teachers, families, variants)
    has_t0 = any(p.variant == t0 for p in prompts.values())
    S_t0 = profiles_from_sym(sym_s, who, families, [t0]) if has_t0 else None
    T_t0 = profiles_from_sym(sym_t, teachers, families, [t0]) if has_t0 else None
    # base reference
    fb = M.frame_table(list(base_rows), prompts)
    if base_reference == "prior":
        sym_b = M.sym_table(fb, mass_gate=False)
    elif base_reference == "gated":
        sym_b = M.sym_table(fb)
    else:
        raise ValueError(f"base_reference must be 'prior' or 'gated', got {base_reference!r}")
    base_ids = sorted(sym_b["teacher"].unique()) if len(sym_b) else []
    if len(base_ids) != 1:
        raise ValueError(f"the base reference must hold exactly one profile, got {base_ids}")
    B = profiles_from_sym(sym_b, base_ids, families, variants)
    base_ref = B.p[0]
    # descriptive per-run columns
    cat = M.category_rates(fs, by=("teacher",)).set_index("teacher") if len(fs) else pd.DataFrame(columns=["answer"])
    inv["answer_rate"] = inv["run_id"].map(cat["answer"]).astype(float) if "answer" in cat else np.nan
    inv["n_cells_valid"] = majority(S.p)[1].reshape(len(who), -1).sum(1)
    # reference values and the engine check
    ag = M.teacher_agreement(sym_s, sym_t, variants) if len(sym_s) else pd.DataFrame(columns=["run_id", "teacher", "agreement", "n_ties", "n_cells"])
    a = agreement_rate(*agreement_counts(S.cells, T.cells))
    ref = ag.pivot_table(index="run_id", columns="teacher", values="agreement").reindex(index=who, columns=teachers).to_numpy(dtype=float) if len(ag) else np.full(a.shape, np.nan)
    bad = ~(np.isclose(a, ref, atol=1e-12, rtol=0) | (np.isnan(a) & np.isnan(ref)))
    if bad.any():
        r, k = np.argwhere(bad)[0]
        raise ValueError(f"matrix agreement disagrees with e1_metrics.teacher_agreement for ({who[r]}, {teachers[k]}): {a[r, k]} vs {ref[r, k]}")
    return World(inv, teachers, families, variants, S, T, S_t0, T_t0, base_ref, base_reference, int(majority(base_ref)[1].sum()), disagreement_cells(T.cells), ag)


# --------------------------------------------------------------------------- the analysis


class E7Result(NamedTuple):
    runs: pd.DataFrame
    metrics: pd.DataFrame
    probe_curve: pd.DataFrame
    sampled: pd.DataFrame
    loso: pd.DataFrame
    logo: pd.DataFrame
    verdict: dict
    calibration: dict
    notes: list[str]


def _rng(seed: int, *tags) -> np.random.Generator:
    return np.random.default_rng([int(seed)] + [zlib.crc32(str(t).encode()) for t in tags])


def loso_population(runs: pd.DataFrame, versions: Sequence[str] = LOSO_VERSIONS) -> np.ndarray:
    """Row indices of the leave-one-style-out calibration population: core negatives whose version is O / R / B (never F / C)."""
    m = (runs["role"] == "core") & (runs["truth"] == NONE) & runs["version"].isin(list(versions))
    return np.flatnonzero(m.to_numpy())


def logo_population(runs: pd.DataFrame, grids: Sequence[str] = LOGO_GRIDS) -> np.ndarray:
    """Row indices of the leave-one-grid-out calibration population: every core run of the calibration grids (E1 students included as rejects)."""
    m = (runs["role"] == "core") & runs["grid"].isin(list(grids))
    return np.flatnonzero(m.to_numpy())


def core_negatives(runs: pd.DataFrame) -> np.ndarray:
    """Row indices of the open-set negatives: core runs whose truth is none (K, K_n, R, S_0)."""
    return np.flatnonzero(((runs["role"] == "core") & (runs["truth"] == NONE)).to_numpy())


def _tau_for(key: str, neg_margins: np.ndarray, taus: Optional[Mapping[str, float]], cal: dict, fpr_max: float, n_min: int, extra: Optional[dict] = None) -> float:
    """Dev: calibrate and record; test: look the key up in the given taus (missing -> error, never recalibrated)."""
    if taus is not None:
        if key not in taus:
            raise KeyError(f"calibration file has no tau for configuration {key!r}; refusing to calibrate on this split")
        return float(taus[key])
    t = calibrate_tau(neg_margins, fpr_max, n_min)
    cal["tau"][key] = {"tau": t.tau, "n_neg": t.n_neg, "n_margins": int(np.asarray(neg_margins).size), "n_attributed": t.n_attributed, "fpr_at_tau": t.fpr, "fallback": t.fallback, "note": t.note} | (extra or {})
    return t.tau


def _eval_config(a: np.ndarray, a_base: np.ndarray, detector: str, tau: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """a (..., R, K), a_base (..., 1, K) -> (s, dec, margin) for one detector."""
    s = scores(a, detector, a_base if detector == "base_known" else None)
    dec, m = decide(s, tau)
    return s, dec, m


def analyze(world: World, *, calibration: Optional[Mapping] = None, n_rep: int = N_REP, n_perm: int = 10_000, n_perm_rep: int = 1000, seed: int = 0, budgets: Sequence[int] = BUDGETS,
            sample_n: Sequence[int] = SAMPLE_N, fpr_max: float = FPR_MAX, n_min: int = N_NEG_MIN, logo_grids: Sequence[str] = LOGO_GRIDS, split: str = "dev") -> E7Result:
    """The whole E7 table set for one split. With `calibration` (the dev calibration.json dict) every tau is taken from it; otherwise taus are calibrated here."""
    runs = world.runs
    teachers, K = world.teachers, len(world.teachers)
    R = len(runs)
    truth = runs["truth"].to_numpy(dtype=object)
    S, T, B0 = world.S.cells, world.T.cells, world.base_ref.reshape(1, -1)
    n_fam, n_var = len(world.families), len(world.variants)
    taus = taus_from_calibration(calibration) if calibration is not None else None
    cal: dict = {"split": split, "seed": seed, "fpr_max": fpr_max, "n_neg_min": n_min, "teachers": teachers, "variants": world.variants, "n_families": n_fam, "n_rep": n_rep,
                 "base_reference": world.base_ref_label, "base_reference_cells": world.base_ref_cells, "disagreement_cells": int(world.disagree.sum()), "n_cells": int(S.shape[1]),
                 "logo_grids": list(logo_grids), "loso_versions": list(LOSO_VERSIONS), "negatives": {}, "tau": {}}
    if calibration is not None:
        cal["reused_from"] = {k: calibration.get(k) for k in ("split", "seed", "fpr_max", "n_neg_min", "teachers", "variants")}
        if list(calibration.get("teachers", teachers)) != teachers:
            raise ValueError(f"calibration teachers {calibration.get('teachers')} differ from {teachers}")
    notes: list[str] = []
    neg_idx = core_negatives(runs)
    cal["negatives"] = {"n": int(len(neg_idx)), "run_ids": list(runs.loc[neg_idx, "run_id"]), "grids": sorted(set(runs.loc[neg_idx, "grid"]))}
    pos_groups, neg_groups = eval_groups(runs)
    core_pos = [g for g in pos_groups if g.role == "core"]
    desc_pos = [g for g in pos_groups if g.role != "core"]
    core_neg_groups = [g for g in neg_groups if g.role == "core"]
    desc_neg_groups = [g for g in neg_groups if g.role != "core"]

    # observed agreement (all cells, probability readout) and the base reference
    agree, valid = agreement_counts(S, T)
    a_all = agreement_rate(agree, valid)  # (R, K)
    a_base_all = agreement_rate(*agreement_counts(B0, T))  # (1, K)
    dis_w = world.disagree.astype(float)[None, :]
    a_dis = agreement_rate(agree, valid, dis_w)[0]  # (R, K)
    a_base_dis = agreement_rate(*agreement_counts(B0, T), dis_w)[0]  # (1, K)

    metric_rows: list[dict] = []
    run_tab = runs.copy()
    for k, t in enumerate(teachers):
        run_tab[f"a__{t}"] = a_all[:, k]
    run_tab["a_base_label"] = world.base_ref_label
    for k, t in enumerate(teachers):
        run_tab[f"a_base__{t}"] = a_base_all[0, k]
    if world.S_t0 is not None and world.T_t0 is not None:
        a_t0 = agreement_rate(*agreement_counts(world.S_t0.cells, world.T_t0.cells))
        for k, t in enumerate(teachers):
            run_tab[f"a_T0__{t}"] = a_t0[:, k]
    main_tau: dict[str, float] = {}
    for subset, a, a_b in (("all", a_all, a_base_all), ("disagreement", a_dis, a_base_dis)):
        for det in DETECTORS:
            s = scores(a, det, a_b if det == "base_known" else None)
            _, m = margins(s)
            key = cal_key("probability", subset, det)
            tau = _tau_for(key, m[neg_idx], taus, cal, fpr_max, n_min)
            policies = [("calibrated", tau)] if subset == "all" else [("calibrated", tau), ("fixed_all_cells", main_tau[det])]
            if subset == "all":
                main_tau[det] = tau
            for policy, tau_p in policies:
                dec, _ = decide(s, tau_p)
                meta = dict(table="main", calibration="main", subset=subset, readout="probability", detector=det, tau_policy=policy, tau=tau_p)
                metric_rows += group_rows(truth, s, dec, core_pos, neg_idx, teachers, n_perm, _rng(seed, "perm", key, policy), meta, core_neg_groups)
                if desc_pos or desc_neg_groups:
                    metric_rows += group_rows(truth, s, dec, desc_pos, neg_idx, teachers, n_perm, _rng(seed, "perm-desc", key, policy), meta | {"table": "descriptive"}, desc_neg_groups)
                if subset == "all" and policy == "calibrated":
                    tag = "known" if det == "base_known" else "unknown"
                    for k, t in enumerate(teachers):
                        run_tab[f"s_{tag}__{t}"] = s[:, k]
                    run_tab[f"decision_{tag}"] = [teachers[d] if d >= 0 else "unattributed" for d in dec]
                    run_tab[f"margin_{tag}"] = m
                    run_tab[f"correct_{tag}"] = [(teachers[d] == tr) if d >= 0 else (tr == NONE) for d, tr in zip(dec, truth)]
                    run_tab[f"tau_{tag}"] = tau
    metrics = pd.DataFrame(metric_rows, columns=METRIC_COLS)

    # leave-one-style-out: calibration population restricted to O / R / B (explicit), evaluated on F / C students
    loso_rows: list[dict] = []
    loso_idx = loso_population(runs)
    if set(loso_idx) != set(neg_idx):
        notes.append("leave-one-style-out population differs from the core negatives (an F / C run is labelled none?)")
    fc_groups = [g for g in core_pos if g.version in ("F", "C")]
    for det in DETECTORS:
        s = scores(a_all, det, a_base_all if det == "base_known" else None)
        _, m = margins(s)
        key = cal_key("probability", "all", det, "loso")
        tau = _tau_for(key, m[loso_idx], taus, cal, fpr_max, n_min, {"population": "core negatives with version in O/R/B", "n_population": int(len(loso_idx))})
        dec, _ = decide(s, tau)
        meta = dict(table="loso", calibration="loso", subset="all", readout="probability", detector=det, tau_policy="calibrated", tau=tau)
        loso_rows += group_rows(truth, s, dec, fc_groups, neg_idx, teachers, n_perm, _rng(seed, "perm", key), meta)
    loso = pd.DataFrame(loso_rows, columns=METRIC_COLS)

    # leave-one-grid-out: tau from the E1 grid (all runs as rejects) + K / K_n; evaluated on every other core grid
    logo_rows: list[dict] = []
    logo_idx = logo_population(runs, logo_grids)
    other_groups = [g for g in core_pos if g.grid not in set(logo_grids)]
    for det in DETECTORS:
        s = scores(a_all, det, a_base_all if det == "base_known" else None)
        _, m = margins(s)
        key = cal_key("probability", "all", det, "logo")
        tau = _tau_for(key, m[logo_idx], taus, cal, fpr_max, n_min, {"population": f"core runs of grids {list(logo_grids)} (positives treated as rejects)", "n_population": int(len(logo_idx))})
        dec, _ = decide(s, tau)
        meta = dict(table="logo", calibration="logo", subset="all", readout="probability", detector=det, tau_policy="calibrated", tau=tau)
        logo_rows += group_rows(truth, s, dec, other_groups, neg_idx, teachers, n_perm, _rng(seed, "perm", key), meta, core_neg_groups)
    logo = pd.DataFrame(logo_rows, columns=METRIC_COLS)

    # sampled-answer readout: n draws per order, n_rep repetitions; tau pooled over the repetitions' negatives
    samp_rows: list[dict] = []
    for n in sample_n:
        rng = _rng(seed, "sampled", n)
        A = np.empty((n_rep, R, K))
        for b in range(n_rep):
            Sb = sample_sym(world.S.p_o1, world.S.p_o2, n, rng).reshape(R, -1)
            A[b] = agreement_rate(*agreement_counts(Sb, T))
        for det in DETECTORS:
            s = scores(A, det, a_base_all[None] if det == "base_known" else None)  # (B, R, K)
            _, m = margins(s)
            key = cal_key(f"sampled_n{n}", "all", det)
            tau = _tau_for(key, m[:, neg_idx].ravel(), taus, cal, fpr_max, n_min, {"n_draws": n, "pooled_over_reps": n_rep})
            dec, _ = decide(s, tau)
            meta = dict(table="sampled", calibration="main", subset="all", readout=f"sampled_n{n}", detector=det, tau_policy="calibrated", tau=tau, n_draws=n)
            prng = _rng(seed, "perm", key)
            for b in range(n_rep):
                samp_rows += [r | {"rep": b} for r in group_rows(truth, s[b], dec[b], core_pos, neg_idx, teachers, n_perm_rep, prng, meta, core_neg_groups)]
    samp_keys = ["table", "calibration", "grid", "version", "role", "subset", "readout", "n_draws", "detector", "tau_policy", "tau", "teacher", "n"]
    samp_vals = ["recall", "wilson_lo", "wilson_hi", "unattributed_rate", "macro_recall", "chance", "perm_p", "auroc", "fpr"]
    sampled = aggregate_reps(pd.DataFrame(samp_rows), samp_keys, samp_vals) if samp_rows else pd.DataFrame(columns=samp_keys)

    # probe-budget curve: k random families x n_rep (the base reference on the same families); tau per budget and the all-cell tau
    curve_rows: list[dict] = []
    eff_budgets = sorted({min(int(k), n_fam) for k in budgets})
    for k in eff_budgets:
        rng = _rng(seed, "budget", k)
        Wf = probe_masks(n_fam, k, n_rep, rng)
        Wc = family_cell_weights(Wf, n_var)
        A = agreement_rate(agree, valid, Wc)  # (B, R, K)
        Ab = agreement_rate(*agreement_counts(B0, T), Wc)  # (B, 1, K)
        for det in DETECTORS:
            s = scores(A, det, Ab if det == "base_known" else None)
            _, m = margins(s)
            key = cal_key("probability", f"budget{k}", det)
            tau_source = "budget"
            if k >= n_fam:  # every family = the all-cells configuration; its tau is the main one (no separate entry)
                tau_k, tau_source = main_tau[det], "all_cells"
            elif taus is not None and key not in taus:  # a budget the dev split could not calibrate (e.g. k = dev family count): fall back, say so
                tau_k, tau_source = main_tau[det], "all_cells_fallback"
                notes.append(f"probe budget {k} ({det}): no tau in the calibration file (on the calibration split this budget was the all-cells configuration); the all-cells tau {main_tau[det]:.4f} is used")
            else:
                tau_k = _tau_for(key, m[:, neg_idx].ravel(), taus, cal, fpr_max, n_min, {"budget_families": k, "pooled_over_reps": int(A.shape[0])})
            for policy, tau_p in (("calibrated", tau_k), ("fixed_all_cells", main_tau[det])):
                dec, _ = decide(s, tau_p)
                meta = dict(table="probe_curve", calibration="main", subset=f"budget{k}", budget=k, all_families=k >= n_fam, readout="probability", detector=det, tau_policy=policy, tau=tau_p,
                            tau_source=(tau_source if policy == "calibrated" else "all_cells"))
                prng = _rng(seed, "perm", key, policy)
                for b in range(A.shape[0]):
                    curve_rows += [r | {"rep": b} for r in group_rows(truth, s[b], dec[b], core_pos, neg_idx, teachers, n_perm_rep, prng, meta, core_neg_groups)]
    curve_keys = ["table", "calibration", "grid", "version", "role", "subset", "budget", "all_families", "readout", "detector", "tau_policy", "tau", "tau_source", "teacher", "n"]
    probe_curve = aggregate_reps(pd.DataFrame(curve_rows), curve_keys, samp_vals) if curve_rows else pd.DataFrame(columns=curve_keys)

    verdict = primary_verdict(metrics, teachers, split=split)
    verdict["calibration_reused"] = calibration is not None
    return E7Result(run_tab, metrics, probe_curve, sampled, loso, logo, verdict, cal, notes)


def primary_verdict(metrics: pd.DataFrame, teachers: Sequence[str], primary: Mapping[str, str] = PRIMARY, split: str = "dev") -> dict:
    """Plan §4 main verdict on the primary configuration: teachers whose recall Wilson lower bound > 1/3, and whether the open-set FPR <= 10%."""
    out = {"primary": dict(primary), "verdict": "pending (primary group missing)", "n_pass": 0, "n_teachers": len(teachers), "passing": [], "fpr": float("nan"), "fpr_ok": None,
           "per_teacher": [], "descriptive_only": split != "test", "rule": RULE}
    if metrics.empty:
        return out
    m = metrics[(metrics["table"] == "main") & (metrics["grid"] == primary["grid"]) & (metrics["version"] == primary["version"]) & (metrics["detector"] == primary["detector"])
                & (metrics["readout"] == primary["readout"]) & (metrics["subset"] == primary["subset"]) & (metrics["tau_policy"] == "calibrated")]
    rows = m[m["teacher"].isin(list(teachers))]
    if rows.empty:
        return out
    passing = [str(r.teacher) for r in rows.itertuples() if not _nan(r.wilson_lo) and r.wilson_lo > RECALL_FLOOR]
    fpr = float(rows["fpr"].iloc[0])
    n_pass = len(passing)
    label = "溯源可行（有条件）" if n_pass * 3 >= 2 * len(teachers) else ("部分" if n_pass >= 1 else "不可行")
    fpr_ok = bool(fpr <= FPR_VERDICT_MAX) if not _nan(fpr) else None
    out.update(verdict=label, n_pass=n_pass, passing=passing, fpr=fpr, fpr_ok=fpr_ok, fpr_max=FPR_VERDICT_MAX, recall_floor=RECALL_FLOOR, tau=float(rows["tau"].iloc[0]),
               per_teacher=[dict(teacher=r.teacher, n=int(r.n), n_correct=int(r.n_correct), recall=float(r.recall), wilson_lo=float(r.wilson_lo), wilson_hi=float(r.wilson_hi),
                                 auroc=float(r.auroc), passes=(str(r.teacher) in passing)) for r in rows.itertuples()],
               macro=m[m["teacher"] == "macro"][["macro_recall", "chance", "perm_p", "unattributed_rate"]].iloc[0].to_dict() if (m["teacher"] == "macro").any() else {})
    return out
