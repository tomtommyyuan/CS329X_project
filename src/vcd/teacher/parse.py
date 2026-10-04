"""Parse teacher outputs into (category, letter) and read option probabilities from logprobs."""

from __future__ import annotations

import math
import re
from typing import Iterable, Optional

from vcd.llm.base import TokenLogprob
from vcd.schemas import Category

_ANSWER_RE = re.compile(r"answer\s*[:：]\s*\**\s*[\(\[]?\s*([AB])(?![A-Za-z])", re.IGNORECASE)
_LEAD_RE = re.compile(r"^\s*\**\s*[\(\[]?\s*([AB])(?![A-Za-z])")

_REFUSAL = re.compile(
    r"\b(i can(?:'|no)?t|i cannot|i won'?t|i am not able|i'm not able|i am unable|i'm unable|"
    r"as an ai|i do not feel comfortable|i don't feel comfortable|i must decline|appropriate for me to|"
    r"i'm not going to|i am not going to|unable to (?:choose|pick|select|answer)|take a side|take sides|"
    r"not my place|i'd rather not (?:choose|decide|pick)|i will not (?:choose|decide|pick)|"
    r"i don't think it's appropriate|i do not think it is appropriate|decline to (?:choose|answer|pick))\b",
    re.IGNORECASE,
)
_INSUFFICIENT = re.compile(
    r"\b(it depends|depends on|more (?:information|context|details)|not enough (?:information|context)|"
    r"without (?:more|additional) (?:information|context)|both options|neither option|"
    r"can'?t say without|hard to say without)\b",
    re.IGNORECASE,
)


_QUOTES = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"'})


def parse_answer(text: str) -> tuple[Category, Optional[str]]:
    """Return (category, letter). A letter found in the required format wins over refusal phrases."""
    if text is None:
        return "malformed", None
    text = text.translate(_QUOTES)
    m = _ANSWER_RE.search(text) or _LEAD_RE.match(text)
    if m:
        return "answer", m.group(1).upper()
    if _REFUSAL.search(text):
        return "refusal", None
    if _INSUFFICIENT.search(text):
        return "insufficient", None
    return "malformed", None


def _clean(tok: str) -> str:
    return re.sub(r"[^A-Za-z]", "", tok)


def letter_probs_from_logprobs(tokens: Iterable[TokenLogprob]) -> Optional[dict[str, float]]:
    """Find the first token that is the answer letter and renormalize its alternatives over {A, B}.

    Handles tokenizations like " A", "A", "(A", "**A" by stripping non-letters. Returns None when no
    letter token is found (e.g. refusal).
    """
    toks = list(tokens)
    seen_answer = False
    for idx, t in enumerate(toks):
        c = _clean(t.token)
        if "answer" in c.lower():
            seen_answer = True
            continue
        if c in ("A", "B") and (seen_answer or idx <= 4):
            mass = {"A": 0.0, "B": 0.0}
            alts = dict(t.top) if t.top else {}
            alts.setdefault(t.token, t.logprob)
            for tok, lp in alts.items():
                cc = _clean(tok)
                if cc in mass:
                    mass[cc] += math.exp(lp)
            z = mass["A"] + mass["B"]
            if z <= 0:
                return None
            return {"A": mass["A"] / z, "B": mass["B"] / z}
    return None


def p_x_from_letters(p_letters: dict[str, float], letter_to_action: dict[str, str]) -> float:
    return sum(p for letter, p in p_letters.items() if letter_to_action.get(letter) == "x")
