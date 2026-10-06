"""The E2c contested rule (tasks/e2c_plan.md §3), applied to T1 demo rows of the three teachers.

Definition (verbatim): A family is CONTESTED if the symmetrized majority action differs between at least two
teachers, or any teacher's symmetrized p (logprob teachers) lies in [0.2, 0.8].

Implementation details fixed before any screening file is opened:
  symmetrized p   logprob teacher: mean of p_x over the two option orders; sampling teacher (Claude): mean of
                  the two order indicators 1[choice == x] in {0, 0.5, 1}
  majority        p_sym > 0.5 -> x, < 0.5 -> y, == 0.5 -> undefined; an undefined Claude majority (the two
                  orders disagree) counts as contested and is tallied as `claude_order_split`
  non-answer      any teacher, either order, category != answer -> the family is neither contested nor consensus
  sub-tally       `band_exact_flip_<teacher>`: a logprob teacher is in the band only because the two orders are
                  confidently opposite (|p_o1 - p_o2| >= FLIP_GAP); `flip_only`: the family is contested solely
                  through such flips (no majority difference, no Claude split, no genuinely intermediate p).
                  The rule is unchanged; the pre-registered sensitivity set is contested minus flip_only.
  duplicates      when a prompt has several demo rows for one teacher (a re-run appended to the same file) the
                  LAST row counts; the number of superseded rows is reported as `duplicate_rows`.
"""

from __future__ import annotations

import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Optional

import pandas as pd

from vcd.schemas import Family, Prompt, TeacherResponse

BAND = (0.2, 0.8)
REASONS = ("majority_differ", "uncertain_band", "claude_order_split")
FLIP_GAP = 0.9  # |p_o1 - p_o2| >= FLIP_GAP: an order flip between two confident answers


@dataclass(frozen=True)
class TeacherSym:
    teacher: str
    readout: str  # "logprobs" | "sampling"
    p_o1: Optional[float]
    p_o2: Optional[float]
    answered: bool
    n_rows: int
    p_x_missing: int = 0  # answer rows of a logprob teacher without p_x (letter indicator used instead)

    @property
    def p_sym(self) -> Optional[float]:
        if self.p_o1 is None or self.p_o2 is None:
            return None
        return (self.p_o1 + self.p_o2) / 2.0

    @property
    def majority(self) -> Optional[str]:
        p = self.p_sym
        if p is None or p == 0.5:
            return None
        return "x" if p > 0.5 else "y"

    def in_band(self, band: tuple[float, float] = BAND) -> bool:
        return self.readout == "logprobs" and self.p_sym is not None and band[0] <= self.p_sym <= band[1]

    def exact_flip(self, band: tuple[float, float] = BAND) -> bool:
        """In the band only through an order flip between two confident answers (DeepSeek's binary p_x)."""
        return self.in_band(band) and self.p_o1 is not None and self.p_o2 is not None and abs(self.p_o1 - self.p_o2) >= FLIP_GAP


def infer_readouts(rows: Iterable[TeacherResponse], cfg: Optional[dict] = None) -> dict[str, str]:
    """teacher -> readout. From configs/models.yaml when given, else 'logprobs' if the teacher has any p_x."""
    out: dict[str, str] = {}
    if cfg:
        for k, spec in (cfg.get("teachers") or {}).items():
            if spec.get("readout"):
                out[k] = spec["readout"]
    seen_px: dict[str, bool] = defaultdict(bool)
    teachers: set[str] = set()
    for r in rows:
        teachers.add(r.teacher)
        seen_px[r.teacher] |= r.p_x is not None
    for t in teachers:
        out.setdefault(t, "logprobs" if seen_px[t] else "sampling")
    return {t: out[t] for t in teachers}


def _order_p(rows: list[TeacherResponse], readout: str) -> tuple[Optional[float], bool, int]:
    """(P(x) for one (teacher, prompt), answered, p_x_missing) from the LAST demo row for that prompt."""
    if not rows:
        return None, False, 0
    r = rows[-1]
    if r.category != "answer" or r.choice_action not in ("x", "y"):
        return None, False, 0
    if readout == "logprobs":
        if r.p_x is not None:
            return float(r.p_x), True, 0
        return (1.0 if r.choice_action == "x" else 0.0), True, 1
    return (1.0 if r.choice_action == "x" else 0.0), True, 0


def symmetrize_t1(
    rows: Iterable[TeacherResponse], prompts: dict[str, Prompt], readouts: dict[str, str], variant: str = "T1"
) -> tuple[dict[str, dict[str, TeacherSym]], Counter]:
    """family_id -> teacher -> TeacherSym over demo rows of `variant`. Also returns bookkeeping counts
    (duplicate rows, rows whose prompt is unknown, rows of other variants / modes)."""
    by_key: dict[tuple[str, str, int], list[TeacherResponse]] = defaultdict(list)
    counts: Counter = Counter()
    for r in rows:
        p = prompts.get(r.prompt_id)
        if p is None:
            counts["unknown_prompt"] += 1
            continue
        if p.variant != variant:
            counts["other_variant"] += 1
            continue
        if r.mode != "demo":
            counts["other_mode"] += 1
            continue
        key = (r.teacher, p.family_id, p.order)
        if by_key[key]:
            counts["duplicate_rows"] += 1
        by_key[key].append(r)
    fams: set[str] = {k[1] for k in by_key}
    teachers: set[str] = {k[0] for k in by_key}
    out: dict[str, dict[str, TeacherSym]] = {}
    for fam in sorted(fams):
        out[fam] = {}
        for t in sorted(teachers):
            ro = readouts.get(t, "sampling")
            p1, a1, m1 = _order_p(by_key.get((t, fam, 1), []), ro)
            p2, a2, m2 = _order_p(by_key.get((t, fam, 2), []), ro)
            n = len(by_key.get((t, fam, 1), [])) + len(by_key.get((t, fam, 2), []))
            out[fam][t] = TeacherSym(teacher=t, readout=ro, p_o1=p1, p_o2=p2, answered=a1 and a2, n_rows=n, p_x_missing=m1 + m2)
    return out, counts


def classify_family(syms: dict[str, TeacherSym], teachers: Iterable[str], band: tuple[float, float] = BAND) -> dict:
    """Verdict for one family: contested | consensus | non_answer, with the reasons that fired."""
    teachers = list(teachers)
    if any(t not in syms or not syms[t].answered for t in teachers):
        return {"verdict": "non_answer", "reasons": [], "majorities": {}, "p_sym": {}}
    reasons: list[str] = []
    maj = {t: syms[t].majority for t in teachers}
    psym = {t: syms[t].p_sym for t in teachers}
    defined = {m for m in maj.values() if m is not None}
    if len(defined) > 1:
        reasons.append("majority_differ")
    flips = {t: syms[t].exact_flip(band) for t in teachers}
    genuine_band = False
    for t in teachers:
        s = syms[t]
        if s.in_band(band):
            if "uncertain_band" not in reasons:
                reasons.append("uncertain_band")
            genuine_band |= not flips[t]
        if s.readout == "sampling" and s.majority is None:
            if "claude_order_split" not in reasons:
                reasons.append("claude_order_split")
    flip_only = bool(reasons) and reasons == ["uncertain_band"] and not genuine_band
    return {"verdict": "contested" if reasons else "consensus", "reasons": reasons, "majorities": maj, "p_sym": psym, "flips": flips, "flip_only": flip_only}


def classify_all(sym: dict[str, dict[str, TeacherSym]], teachers: list[str], band: tuple[float, float] = BAND) -> pd.DataFrame:
    rows = []
    for fam, syms in sym.items():
        c = classify_family(syms, teachers, band)
        row = {"family_id": fam, "verdict": c["verdict"], "reasons": ",".join(c["reasons"]), "flip_only": bool(c.get("flip_only", False))}
        for r in REASONS:
            row[r] = r in c["reasons"]
        for t in teachers:
            s = syms.get(t)
            row[f"p_sym_{t}"] = c["p_sym"].get(t)
            row[f"maj_{t}"] = c["majorities"].get(t)
            row[f"answered_{t}"] = bool(s and s.answered)
            row[f"p_x_missing_{t}"] = int(s.p_x_missing) if s else 0
            row[f"band_exact_flip_{t}"] = bool(c.get("flips", {}).get(t, False))
        rows.append(row)
    return pd.DataFrame(rows, columns=classify_columns(teachers))


def classify_columns(teachers: list[str]) -> list[str]:
    return ["family_id", "verdict", "reasons", "flip_only", *REASONS] + [c for t in teachers for c in (f"p_sym_{t}", f"maj_{t}", f"answered_{t}", f"p_x_missing_{t}", f"band_exact_flip_{t}")]


def pairwise_disagreement(df: pd.DataFrame, teachers: list[str]) -> pd.DataFrame:
    """Share of families (both teachers answered) whose defined majorities differ, per teacher pair."""
    out = []
    for i, a in enumerate(teachers):
        for b in teachers[i + 1 :]:
            d = df[df[f"answered_{a}"] & df[f"answered_{b}"]]
            d = d[d[f"maj_{a}"].notna() & d[f"maj_{b}"].notna()]
            n = len(d)
            k = int((d[f"maj_{a}"] != d[f"maj_{b}"]).sum()) if n else 0
            out.append({"pair": f"{a}-{b}", "n_families": n, "n_differ": k, "rate": (k / n) if n else float("nan")})
    return pd.DataFrame(out)


def p_histogram(df: pd.DataFrame, teacher: str, edges: tuple[float, ...] = (0.0, 0.05, 0.2, 0.35, 0.5, 0.65, 0.8, 0.95, 1.0)) -> list[tuple[str, int]]:
    vals = df.loc[df[f"answered_{teacher}"], f"p_sym_{teacher}"].dropna().to_numpy(dtype=float)
    out = []
    for i, (lo, hi) in enumerate(zip(edges[:-1], edges[1:])):
        last = i == len(edges) - 2
        mask = (vals >= lo) & ((vals <= hi) if last else (vals < hi))
        out.append((f"[{lo:.2f}, {hi:.2f}{']' if last else ')'}", int(mask.sum())))
    return out


RATE_COLUMNS = ["n", "not_screened", "screened", "non_answer", "non_answer_rate", "answered", "contested", "contested_rate", *REASONS, "flip_only", "contested_excl_flip_only"]


def rate_table(df: pd.DataFrame, group: pd.Series, name: str) -> pd.DataFrame:
    """Per group: n, not-screened rows (no T1 prompt yet), non-answer rate among screened, contested rate among
    answered, the count of each reason among contested, and the flip-only sub-tally with the sensitivity count."""
    d = df.assign(**{name: group.values})
    out = []
    for g, sub in d.groupby(name, sort=True, dropna=False):
        n = len(sub)
        ns = int((sub["verdict"] == "not_screened").sum())
        screened = n - ns
        na = int((sub["verdict"] == "non_answer").sum())
        answered = screened - na
        con = int((sub["verdict"] == "contested").sum())
        fo = int(sub["flip_only"].fillna(False).astype(bool).sum()) if "flip_only" in sub else 0
        row = {name: g, "n": n, "not_screened": ns, "screened": screened, "non_answer": na, "non_answer_rate": na / screened if screened else float("nan"), "answered": answered, "contested": con, "contested_rate": con / answered if answered else float("nan")}
        for r in REASONS:
            row[r] = int(sub[r].fillna(False).astype(bool).sum())
        row["flip_only"] = fo
        row["contested_excl_flip_only"] = con - fo
        out.append(row)
    return pd.DataFrame(out, columns=[name, *RATE_COLUMNS])


def flip_table(df: pd.DataFrame, teachers: list[str]) -> list[list]:
    """Per teacher: answered families, in-band, of which exact order flips."""
    rows = []
    for t in teachers:
        d = df[df[f"answered_{t}"].astype(bool)]
        p = d[f"p_sym_{t}"].astype(float)
        band = int(((p >= BAND[0]) & (p <= BAND[1])).sum())
        flips = int(d[f"band_exact_flip_{t}"].fillna(False).astype(bool).sum()) if f"band_exact_flip_{t}" in d else 0
        rows.append([t, len(d), band, flips, (flips / band) if band else float("nan")])
    return rows


def _largest_remainder(weights: dict[str, float], n: int) -> dict[str, int]:
    total = sum(weights.values())
    if total <= 0 or n <= 0:
        return {g: 0 for g in weights}
    quotas = {g: n * w / total for g, w in weights.items()}
    alloc = {g: int(q) for g, q in quotas.items()}
    rem = n - sum(alloc.values())
    for g in sorted(weights, key=lambda g: (-(quotas[g] - alloc[g]), g))[:rem]:
        alloc[g] += 1
    return alloc


def stratified_sample(fams: list[Family], n: int, seed: int, key=lambda f: f.source) -> list[Family]:
    """Deterministic sample of n rows, allocated across `key` groups in proportion to availability (largest
    remainder), shuffled within group with `seed`. Returns everything when n >= len(fams)."""
    if n >= len(fams):
        return list(fams)
    groups: dict[str, list[Family]] = defaultdict(list)
    for f in fams:
        groups[key(f)].append(f)
    alloc = _largest_remainder({g: len(lst) for g, lst in groups.items()}, n)
    rng = random.Random(seed)
    out: list[Family] = []
    for g in sorted(groups):
        lst = sorted(groups[g], key=lambda f: f.family_id)
        rng.shuffle(lst)
        out += lst[: alloc[g]]
    return out


def matched_sample(fams: list[Family], target_counts: dict[str, int], seed: int, key=lambda f: f.source) -> tuple[list[Family], dict[str, dict[str, int]]]:
    """E2c-K: draw per group EXACTLY the counts of the E2c-C set. A group with fewer rows than its count gives
    everything, and the shortfall is redistributed over the other TARGETED groups in proportion to their target
    counts (largest remainder, repeated until filled or exhausted); only when no targeted group has rows left does
    the remainder come from the non-targeted groups in proportion to availability. Returns
    (rows, {group: {target, drawn, available}})."""
    groups: dict[str, list[Family]] = defaultdict(list)
    for f in fams:
        groups[key(f)].append(f)
    rng = random.Random(seed)
    shuffled: dict[str, list[Family]] = {}
    for g in sorted(set(groups) | set(target_counts)):
        lst = sorted(groups.get(g, []), key=lambda f: f.family_id)
        rng.shuffle(lst)
        shuffled[g] = lst
    want = {g: int(target_counts.get(g, 0)) for g in shuffled}
    drawn = {g: 0 for g in shuffled}
    pending = dict(want)
    while True:
        short = 0
        for g in sorted(pending):
            take = min(pending[g], len(shuffled[g]) - drawn[g])
            drawn[g] += take
            short += pending[g] - take
        open_groups = {g: want[g] for g in shuffled if len(shuffled[g]) - drawn[g] > 0 and want[g] > 0}
        if short and not open_groups:  # degenerate: every targeted source is exhausted
            open_groups = {g: len(shuffled[g]) - drawn[g] for g in shuffled if len(shuffled[g]) - drawn[g] > 0}
        if short == 0 or not open_groups:
            break
        pending = _largest_remainder(open_groups, short)
        pending = {g: min(k, len(shuffled[g]) - drawn[g]) for g, k in pending.items() if k > 0}
        if not pending:
            break
    out: list[Family] = []
    for g in sorted(shuffled):
        out += shuffled[g][: drawn[g]]
    return out, {g: {"target": want[g], "drawn": drawn[g], "available": len(shuffled[g])} for g in sorted(shuffled)}
