"""E0.6: teacher answer -> structured record (J) -> F / C rewrite (B) -> checks (J + rules)."""

from __future__ import annotations

import asyncio
import json
import random
import re
from collections import defaultdict
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field

from vcd.io import read_jsonl, write_jsonl
from vcd.llm.base import LLMClient, LLMRequest
from vcd.rewrite import prompts as RP
from vcd.schemas import Prompt, TeacherResponse
from vcd.teacher.parse import parse_answer

_STRENGTH = {"clear", "on_balance", "weak"}
JUDGE_MAX_TOKENS = 2000  # judges with built-in reasoning (GLM-5.3-Flash) spend tokens before the JSON; keep headroom.
# Intensifier / hedge changes are checked lexically (below), not by the judge: asking GLM to list them made its
# hidden reasoning exceed 3,000 tokens and the JSON came back empty.


class Record(BaseModel):
    prompt_id: str
    teacher: str
    choice: str
    reasons: list[str]
    conditions: list[str] = Field(default_factory=list)
    concessions: list[str] = Field(default_factory=list)  # acknowledgements that do not make the choice conditional
    strength: str = "on_balance"
    source_text: str = ""


class Rewrite(BaseModel):
    prompt_id: str
    teacher: str
    version: str  # F | C
    rewriter: str
    attempt: int
    text: str
    judged: dict = Field(default_factory=dict)
    checks: dict = Field(default_factory=dict)
    kept: bool = False


def parse_json_object(text: str) -> Optional[dict]:
    """Tolerates code fences and surrounding prose; returns the first top-level JSON object."""
    if not text:
        return None
    t = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.MULTILINE)
    start = t.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(t)):
        if t[i] == "{":
            depth += 1
        elif t[i] == "}":
            depth -= 1
            if depth == 0:
                try:
                    return json.loads(t[start : i + 1])
                except json.JSONDecodeError:
                    return None
    return None


def record_from_json(d: dict, prompt_id: str, teacher: str, source_text: str) -> Optional[Record]:
    choice = str(d.get("choice", "")).strip().upper()
    if choice not in ("A", "B"):
        return None
    reasons = [str(x).strip() for x in d.get("reasons", []) if str(x).strip()]
    if not reasons:
        return None
    strength = str(d.get("strength", "on_balance")).strip().lower()
    return Record(
        prompt_id=prompt_id, teacher=teacher, choice=choice, reasons=reasons,
        conditions=[str(x).strip() for x in d.get("conditions", []) if str(x).strip()],
        concessions=[str(x).strip() for x in d.get("concessions", []) if str(x).strip()],
        strength=strength if strength in _STRENGTH else "on_balance", source_text=source_text,
    )


# Lexical strength check (added after the E0 audit: 91% of strength failures were intensifiers added or hedges dropped).
_HEDGES = [
    "may", "might", "could", "perhaps", "possibly", "likely", "probably", "generally", "usually", "often",
    "sometimes", "tend", "tends", "consider", "arguably", "seem", "seems", "somewhat", "relatively", "rather",
    "fairly", "in most cases", "on balance", "it depends", "worth considering", "a good idea",
]
_INTENSIFIERS = [
    "clearly", "obviously", "essential", "essentially", "necessity", "necessary", "must", "imperative",
    "paramount", "crucial", "critical", "unequivocal", "unequivocally", "absolutely", "always", "never",
    "undeniably", "certainly", "definitely", "the only", "only way", "fundamental", "vital", "indispensable",
    "non-negotiable", "unacceptable", "mandatory", "required", "requires", "require", "no doubt", "without question",
    "cannot be", "can never", "under no circumstances",
]
# "clear" counts only in intensifying uses ("it is clear", "a clear choice"), not in "clear boundaries" or "make clear".
_INTENSIFIER_PATTERNS = [
    (re.compile(r"\b(it is|it's|is|seems|remains|becomes|that's|that is) clear\b", re.I), "it is clear"),
    (re.compile(r"\bclear (choice|decision|necessity|win|winner|priority|obligation|duty|case|answer|option|path|course|guideline|best|better|right|wrong|violation|breach)\b", re.I), "clear choice"),
]


def _terms(text: str, vocab: list[str]) -> set[str]:
    low = " " + re.sub(r"[^a-z' ]+", " ", text.lower()) + " "
    found = {t for t in vocab if f" {t} " in low}
    if vocab is _INTENSIFIERS:
        found |= {label for pat, label in _INTENSIFIER_PATTERNS if pat.search(text)}
    return found


_CONDITION_MARKERS = ["as long as", "provided that", "unless", "only if", "only when", "so long as", "on the condition", "if you", "if the", "if it", "if they", "if this", "if that"]
_FRAMING_PHRASES = ["you're better off", "you are better off", "you're probably", "you are probably", "don't you think", "the right call", "the right thing to do", "no-brainer", "you've got to", "you have got to", "trust me", "let's be honest", "honestly",
                    "you're gonna want to", "you are going to want to", "you'll want to", "you will want to", "on the condition that", "this choice depends on", "this decision depends on", "assuming that", "assuming it",
                    # v6: predicted / ordered actions in the conversational register ("you're gonna have to end it")
                    "gonna", "you're going to", "you are going to", "you'll have to", "you will have to", "have to", "has to", "need to", "needs to", "that's what you're",
                    # v7: conversational filler the rewriter adds when pushed to "sound spoken" (none of it is in any teacher answer)
                    "that's what", "that's not what", "that is what", "you can't just", "you cannot just", "that's something", "that is something", "it's about", "it is about",
                    "that's not how", "what matters", "nothing more", "simple as that", "end of story", "bottom line", "you don't want", "you do not want", "that's the thing", "that's all",
                    "that's because", "that is because", "you're supposed to", "you are supposed to", "a big deal", "you're best off", "you are best off", "the thing is", "look,", "basically",
                    "doesn't it", "isn't it", "don't you", "right?"]


def lexical_strength_check(original: str, rewrite: str) -> dict:
    """Intensifiers present in the rewrite but not the original, and hedges present in the original but not the rewrite."""
    return {
        "intensifiers_added": sorted(_terms(rewrite, _INTENSIFIERS) - _terms(original, _INTENSIFIERS)),
        "hedges_removed": sorted(_terms(original, _HEDGES) - _terms(rewrite, _HEDGES)),
    }


def lexical_addition_check(original: str, rewrite: str, n_conditions: int) -> dict:
    """Conditional markers added when the original had no condition, and advisory framing phrases added."""
    conds = sorted(_terms(rewrite, _CONDITION_MARKERS) - _terms(original, _CONDITION_MARKERS)) if n_conditions == 0 else []
    framing = sorted(_terms(rewrite, _FRAMING_PHRASES) - _terms(original, _FRAMING_PHRASES))
    return {"conditions_added": conds, "framing_added": framing}


# v7 (after the Codex audit of the final sheet): the stricter auditor failed 37/300 items for a changed modal
# ("can provide" -> "provides", "seek" -> "can seek") or a dropped emphasis word ("crucial"). Both are checked
# lexically as a symmetric difference, after expanding contractions so the conversational register is not penalised.
_MODALS = ["can", "could", "may", "might", "should", "must", "would", "will", "shall", "ought to", "need to", "have to"]
_EMPHASIS_PATTERNS = [
    (re.compile(r"\bcrucial(ly)?\b", re.I), "crucial"), (re.compile(r"\bimportan(t|ce)\b", re.I), "important"),
    (re.compile(r"\bessential(ly)?\b", re.I), "essential"), (re.compile(r"\bcritical(ly)?\b", re.I), "critical"),
    (re.compile(r"\bvital(ly)?\b", re.I), "vital"), (re.compile(r"\bparamount\b", re.I), "paramount"),
    (re.compile(r"\bnecess(ary|arily|ity)\b", re.I), "necessary"), (re.compile(r"\bsignifican(t|tly|ce)\b", re.I), "significant"),
    (re.compile(r"\bserious(ly|ness)?\b", re.I), "serious"), (re.compile(r"\bfundamental(ly)?\b", re.I), "fundamental"),
    (re.compile(r"\bimperative\b", re.I), "imperative"), (re.compile(r"\bindispensable\b", re.I), "indispensable"),
]
_CONTRACTIONS = [
    (re.compile(r"\bwon't\b", re.I), "will not"), (re.compile(r"\bcan't\b", re.I), "can not"), (re.compile(r"\bcannot\b", re.I), "can not"),
    (re.compile(r"\bshan't\b", re.I), "shall not"), (re.compile(r"n't\b", re.I), " not"),
    (re.compile(r"'ll\b", re.I), " will"), (re.compile(r"'d\b", re.I), " would"),
    # inflection only (the formal register turns "you need to" into "one needs to")
    (re.compile(r"\bneeds to\b", re.I), "need to"), (re.compile(r"\bhas to\b", re.I), "have to"),
]


def _expand_contractions(text: str) -> str:
    for pat, rep in _CONTRACTIONS:
        text = pat.sub(rep, text)
    return text


def modal_shift_check(original: str, rewrite: str) -> dict:
    """Modal verbs or emphasis words present in one text but not the other ('can provide' -> 'provides', 'seek' ->
    'can seek', a dropped 'crucial'); each changes how firmly the answer commits."""
    o, r = _expand_contractions(original), _expand_contractions(rewrite)
    mo, mr = _terms(o, _MODALS), _terms(r, _MODALS)
    eo = {lab for pat, lab in _EMPHASIS_PATTERNS if pat.search(o)}
    er = {lab for pat, lab in _EMPHASIS_PATTERNS if pat.search(r)}
    return {"modals_changed": sorted(mo ^ mr), "emphasis_changed": sorted(eo ^ er)}


# Process text the rewriter sometimes emits around or instead of the answer (3 items in the final kept pools).
_META_TEXT = re.compile(
    r"(?im)^\s*(revised|rewritten|rewrite:|revision|here is|here's|note:|no, that's not it|that's not it|alternatively:|or:|version \d)"
    r"|\b(as requested|rewritten (to|in|as)|revised (to|version)|that's not it|doesn't become|does not become|becomes:)\b|->|\u2192|\boriginal:|\brewritten:",
)


def format_check(original: str, rewrite: str, max_ratio: float = 2.0, truncated: bool = False) -> dict:
    """Exactly one answer, no process text, no runaway length (the rewriter sometimes emits several attempts), not cut off."""
    n_answers = len(re.findall(r"(?im)^\s*answer\s*:", rewrite))
    ratio = len(rewrite.split()) / max(1, len(original.split()))
    return {
        "multiple_answers": n_answers != 1,
        "meta_text": bool(_META_TEXT.search(rewrite)),
        "too_long": ratio > max_ratio,
        "truncated": truncated,
    }


_SECOND_BLOCK = re.compile(r"(?im)^\s*(?:answer\s*:|corrected response|corrected version|revised(?: version| response)?\s*:?|rewritten\s*:?|alternatively\s*:?|here is .*:)\s*$|^\s*answer\s*:", re.M)


_MARKDOWN = re.compile(r"\*\*|__|`+|^\s*#+\s*", re.M)


def clean_rewrite(text: str) -> str:
    """Keep the first `Answer: X / Rationale: ...` block only, without markdown decoration. The rewriter sometimes
    appends a self-check or a 'Corrected response:' second block; the first block is the answer and is judged on its own."""
    t = _MARKDOWN.sub("", text).strip()  # Gemini writes "**Answer:** A" by default
    starts = [m.start() for m in re.finditer(r"(?im)^\s*answer\s*:", t)]
    if len(starts) >= 2:
        t = t[: starts[1]].rstrip()
    m = re.search(r"(?im)^\s*(corrected response|corrected version|revised version|revised response|alternatively)\b.*$", t)
    if m:
        t = t[: m.start()].rstrip()
    return t


def build_feedback(record: Record, checks: dict, judged: dict, style: str) -> str:
    """Deterministic description of why an attempt was rejected, fed back to the rewriter on retry. It names only
    things taken from the rewrite itself, the record, or the rule set, so it cannot leak new content."""
    lex = checks["lexical"]
    msgs: list[str] = []
    if not checks["style"]:
        reg = lex.get("register", {})
        if style == "F":
            msgs.append("it used contractions (" + ", ".join(reg.get("contractions") or []) + "); use none, and no direct address")
        else:
            parts = []
            if reg.get("uncontracted"):
                parts.append("these phrases must be contracted: " + ", ".join(reg["uncontracted"]))
            if reg.get("formal_connectives"):
                parts.append("these connectives must be replaced by plain ones: " + ", ".join(reg["formal_connectives"]))
            if reg.get("formal_words"):
                parts.append("these words must be replaced by the everyday word of the same meaning: " + ", ".join(reg["formal_words"]))
            msgs.append("; ".join(parts) or "it did not read as plain spoken register")
    if not checks["reasons"]:
        n_ref, n_cand = len(record.reasons), len(judged.get("candidate_reasons") or [])
        if n_cand > n_ref:
            msgs.append(f"it contained {n_cand} reasons where the original has {n_ref}; do not restate a reason you have already written")
        ent = judged.get("reasons_entailed") or []
        dropped = [record.reasons[i] for i, ok in enumerate(ent) if i < len(record.reasons) and not ok]
        if dropped:
            msgs.append("it dropped or changed this content of the original: " + " | ".join(dropped))
        if judged.get("new_reasons"):
            msgs.append("it added content that is not in the original: " + " | ".join(map(str, judged["new_reasons"])))
    if not checks["conditions"]:
        msgs.append("it dropped, added, moved or stated as a fact a condition or concession; keep each one attached to the sentence it modifies in the original"
                    + (f" (added: {', '.join(lex['conditions_added'])})" if lex.get("conditions_added") else ""))
    if not checks["strength"]:
        if lex.get("modals_changed"):
            msgs.append("it added or dropped the modal verb(s) " + ", ".join(lex["modals_changed"]) + "; keep exactly the original's modal verbs")
        if lex.get("emphasis_changed"):
            msgs.append("it added or dropped the emphasis word(s) " + ", ".join(lex["emphasis_changed"]))
        if lex.get("intensifiers_added"):
            msgs.append("it added the certainty word(s) " + ", ".join(lex["intensifiers_added"]))
        if lex.get("hedges_removed"):
            msgs.append("it dropped the softening word(s) " + ", ".join(lex["hedges_removed"]))
        if lex.get("framing_added"):
            msgs.append("it added the phrase(s) " + ", ".join(lex["framing_added"]) + ", which are not in the original")
        if not any(lex.get(k) for k in ("modals_changed", "emphasis_changed", "intensifiers_added", "hedges_removed", "framing_added")):
            msgs.append("it sounded more or less committed to the choice than the original")
    if not checks["format"]:
        fmt = lex.get("format", {})
        if fmt.get("truncated") or fmt.get("too_long"):
            msgs.append("it was too long; the rewrite has about as many words as the original")
        if fmt.get("multiple_answers") or fmt.get("meta_text"):
            msgs.append("it contained more than one answer or some commentary; output one Answer line and one Rationale and nothing else")
    return "; ".join(msgs)


# Register is gated lexically (v7). The holistic "formal / conversational" call of the judge is recorded but does not
# gate C: on plain originals a content-faithful rewrite can never sound like chat, and the only serverless rewriter in
# the Meta family adds obligation filler when pushed to. C is therefore defined as a plain spoken register: every
# contractible phrase contracted, no formal connective, none of the listed formal words. F must have no contraction.
_UNCONTRACTED = ["it is", "you are", "you have", "that is", "there is", "do not", "does not", "did not", "cannot", "is not", "are not", "was not",
                 "were not", "have not", "has not", "would not", "should not", "could not", "will not"]
_FORMAL_CONNECTIVES = ["however", "therefore", "thus", "consequently", "hence", "additionally", "furthermore", "moreover", "regarding", "prior to",
                       "in order to", "whereas", "nevertheless", "nonetheless"]
_FORMAL_WORDS = ["assist", "assists", "assisting", "obtain", "obtains", "obtaining", "individuals", "maintain", "maintains", "maintaining", "ensure",
                 "ensures", "ensuring", "demonstrate", "demonstrates", "demonstrating", "utilize", "utilizes", "utilizing", "purchase", "purchases",
                 "purchasing", "sufficient", "attempt", "attempts", "attempting", "numerous", "assistance", "additional", "potential", "receive",
                 "receives", "receiving", "provide", "provides", "providing"]
_FORMAL_WORDS_RE = re.compile(r"\b(?:" + "|".join(_FORMAL_WORDS) + r")\b")
_CONTRACTION_FORMS = re.compile(r"\b\w+(?:n't|'re|'ve|'ll|'d)\b|\b(?:it|that|there|what|here|who|let|he|she)'s\b", re.I)


def register_check(text: str, style: str) -> dict:
    body = text.split("Rationale:", 1)[-1]
    if style == "F":
        return {"contractions": sorted({m.group(0).lower() for m in _CONTRACTION_FORMS.finditer(body)})}
    return {
        "uncontracted": sorted(_terms(body, _UNCONTRACTED)),
        "formal_connectives": sorted(_terms(body, _FORMAL_CONNECTIVES)),
        # case-sensitive so that proper nouns ("Individuals with Disabilities Education Act") are not flagged
        "formal_words": sorted({m.group(0) for m in _FORMAL_WORDS_RE.finditer(body)}),
    }


def evaluate_checks(record: Record, rewrite_text: str, judged: dict, style: str, truncated: bool = False) -> dict:
    _, letter = parse_answer(rewrite_text)
    choice_ok = letter == record.choice
    re_ent = judged.get("reasons_entailed") or []
    cand = judged.get("candidate_reasons")
    # fewer candidate reasons than the reference with every reference reason entailed is the judge segmenting
    # propositions differently (two sentences, five reasons); more candidates than the reference is a restatement or an addition
    count_ok = (len(cand) <= len(record.reasons)) if isinstance(cand, list) else True
    reasons_ok = len(re_ent) == len(record.reasons) and all(bool(x) for x in re_ent) and not judged.get("new_reasons") and count_ok
    co_ent = judged.get("conditions_entailed") or []
    lex = lexical_strength_check(record.source_text, rewrite_text) if record.source_text else {"intensifiers_added": [], "hedges_removed": []}
    add = lexical_addition_check(record.source_text, rewrite_text, len(record.conditions)) if record.source_text else {"conditions_added": [], "framing_added": []}
    lex.update(add)
    mod = modal_shift_check(record.source_text, rewrite_text) if record.source_text else {"modals_changed": [], "emphasis_changed": []}
    lex.update(mod)
    fmt = format_check(record.source_text, rewrite_text, truncated=truncated) if record.source_text else {"multiple_answers": False, "meta_text": False, "too_long": False, "truncated": truncated}
    format_ok = not any(fmt.values())
    lex["format"] = fmt
    cc_ent = judged.get("concessions_entailed")
    concessions_ok = True if not record.concessions else (isinstance(cc_ent, list) and len(cc_ent) == len(record.concessions) and all(bool(x) for x in cc_ent))
    conditions_ok = (
        len(co_ent) == len(record.conditions) and all(bool(x) for x in co_ent)
        and not judged.get("conditions_as_facts") and not add["conditions_added"] and concessions_ok
    )
    strength_ok = (
        str(judged.get("strength", "")).lower() == record.strength
        and not judged.get("strength_changed", False)
        and not judged.get("intensifiers_added")
        and not judged.get("hedges_removed")
        and not lex["intensifiers_added"]
        and not lex["hedges_removed"]
        and not add["framing_added"]
        and not mod["modals_changed"]
        and not mod["emphasis_changed"]
    )
    register = str(judged.get("register", "")).lower()
    reg = register_check(rewrite_text, style)
    lex["register"] = reg
    style_ok = (register == "formal" and not reg["contractions"]) if style == "F" else not any(reg.values())
    return dict(choice=choice_ok, reasons=reasons_ok, conditions=conditions_ok, strength=strength_ok, style=style_ok, format=format_ok,
                lexical=lex, kept=choice_ok and reasons_ok and conditions_ok and strength_ok and style_ok and format_ok)


async def extract_record(judge: LLMClient, judge_model: str, prompt: Prompt, answer: TeacherResponse) -> Optional[Record]:
    user = RP.EXTRACT_USER.format(prompt_user=prompt.user, answer=answer.raw)
    d = None
    for max_tokens in (JUDGE_MAX_TOKENS, JUDGE_MAX_TOKENS * 2):  # a reasoning judge sometimes exhausts the budget before the JSON
        resp = await judge.complete(LLMRequest(model=judge_model, system=RP.EXTRACT_SYSTEM, user=user, temperature=0.0, max_tokens=max_tokens))
        d = parse_json_object(resp.text)
        if d:
            break
    return record_from_json(d, prompt.prompt_id, answer.teacher, answer.raw) if d else None


_SENT_SPLIT = re.compile(r"(?<!\bDr\.)(?<!\bMr\.)(?<!\bMs\.)(?<!\bMrs\.)(?<!\be\.g\.)(?<!\bi\.e\.)(?<!\bvs\.)(?<=[.!?])\s+(?=[A-Z\"\u201c(])")


def split_rationale(source_text: str) -> list[str]:
    """Sentences of the rationale part of a teacher answer (`Answer: X / Rationale: ...`)."""
    m = re.search(r"(?is)rationale\s*:\s*", source_text)
    body = source_text[m.end():] if m else source_text
    return [x.strip() for x in _SENT_SPLIT.split(body.strip()) if x.strip()]


_INLINE_EXPLANATION = re.compile(r",?\s*(?:(?:this |it )?(?:doesn't|does not|didn't|did not) (?:change|become)(?: to)?|becomes|stays the same|remains the same|unchanged|->|\u2192)\s*:?\s", re.I)


def _strip_sentence_output(text: str) -> str:
    t = text.strip()
    t = re.sub(r"(?is)^(rewritten sentence|sentence|rewrite)\s*:\s*", "", t).strip()
    t = t.split("\n")[0].strip()
    m = _INLINE_EXPLANATION.search(t)  # "..., doesn't change to: <repeat>" is the rewriter explaining itself; keep the sentence
    if m and m.start() > 10:
        t = t[: m.start()].rstrip(" ,;")
        if t and t[-1] not in ".!?\"\u201d":
            t += "."
    if len(t) >= 2 and t[0] in "\"\u201c'" and t[-1] in "\"\u201d'":
        t = t[1:-1].strip()
    return t


async def rewrite_sentencewise(rewriter: LLMClient, rewriter_model: str, record: Record, style: str, temperature: float, feedback: Optional[str] = None, max_tokens_floor: int = 0) -> tuple[str, bool]:
    """Sentence-by-sentence rewrite: the answer line is copied, each rationale sentence is rewritten on its own."""
    fb = f" Your previous attempt was rejected because {feedback}; avoid exactly that." if feedback else ""
    sentences = split_rationale(record.source_text)
    truncated = False

    async def one(sent: str) -> str:
        nonlocal truncated
        user = RP.SENTENCE_REWRITE_USER.format(style_instruction=RP.STYLE_INSTRUCTIONS[style], sentence=sent, feedback=fb)
        resp = await rewriter.complete(LLMRequest(model=rewriter_model, system=RP.REWRITE_SYSTEM, user=user, temperature=temperature, max_tokens=max(max_tokens_floor, int(100 + 3 * len(sent.split())))))
        out = _strip_sentence_output(resp.text)
        # only the first line is used, so a cut-off is a defect only if that line itself is incomplete
        truncated = truncated or (resp.finish_reason == "length" and not re.search(r"[.!?\"\u201d')]$", out))
        return out

    outs = await asyncio.gather(*(one(s) for s in sentences))
    return f"Answer: {record.choice}\nRationale: " + " ".join(o for o in outs if o), truncated


async def rewrite_once(rewriter: LLMClient, rewriter_model: str, prompt: Prompt, record: Record, style: str, temperature: float, feedback: Optional[str] = None, mode: str = "whole", max_tokens_floor: int = 0) -> tuple[str, bool]:
    """One rewrite attempt. Returns the cleaned text and whether the generation was cut off by the token limit.
    `max_tokens_floor` lifts the budget for rewriters that spend hidden reasoning tokens inside max_tokens."""
    if mode == "sentence":
        return await rewrite_sentencewise(rewriter, rewriter_model, record, style, temperature, feedback, max_tokens_floor)
    # the strength label is deliberately NOT in the JSON the rewriter sees (it was echoed as "a clear choice")
    rec = {"choice": record.choice, "reasons": record.reasons, "conditions": record.conditions}
    if record.concessions:
        rec["concessions"] = record.concessions
    rec_json = json.dumps(rec, ensure_ascii=False)
    cond_instr = RP.CONDITIONS_INSTRUCTIONS["some"].format(n=len(record.conditions)) if record.conditions else RP.CONDITIONS_INSTRUCTIONS["none"]
    conc_instr = RP.CONCESSIONS_INSTRUCTIONS["some"].format(n=len(record.concessions)) if record.concessions else "No concessive or acknowledging statement is in the original; do not add one."
    user = RP.REWRITE_USER.format(prompt_user=prompt.user, record_json=rec_json, original_text=record.source_text.strip(), style_instruction=RP.STYLE_INSTRUCTIONS[style], choice=record.choice,
                                  strength_instruction=RP.STRENGTH_INSTRUCTIONS.get(record.strength, RP.STRENGTH_INSTRUCTIONS["on_balance"]),
                                  conditions_instruction=cond_instr, concessions_instruction=conc_instr)
    if feedback:
        user += f"\n\nYour previous attempt was rejected because {feedback}. Fix exactly these problems and change nothing else."
    # budget scales with the original: long answers were cut off at 300 tokens, and a cut-off rewrite is a defect
    max_tokens = max(max_tokens_floor, int(min(700, 160 + 2.5 * len(record.source_text.split()))))
    resp = await rewriter.complete(LLMRequest(model=rewriter_model, system=RP.REWRITE_SYSTEM, user=user, temperature=temperature, max_tokens=max_tokens))
    return clean_rewrite(resp.text), (resp.finish_reason == "length")


async def judge_rewrite(judge: LLMClient, judge_model: str, record: Record, rewrite_text: str, fallback: Optional[tuple[LLMClient, str]] = None) -> dict:
    rec_json = json.dumps({"choice": record.choice, "reasons": record.reasons, "conditions": record.conditions, "concessions": record.concessions, "strength": record.strength}, ensure_ascii=False)
    # The reasoning judge hides its reasoning in the output budget; with the v7 rules it sometimes needs ~3000 tokens
    # before the JSON, and on a few candidates it never stops (6000 tokens, no JSON). Escalate the budget, then fall
    # back to the slim prompt (no strength rule; the lexical modal / emphasis check covers that) before giving up.
    plan = [(judge, judge_model, RP.CHECK_USER, JUDGE_MAX_TOKENS), (judge, judge_model, RP.CHECK_USER, JUDGE_MAX_TOKENS * 2), (judge, judge_model, RP.CHECK_USER_SLIM, JUDGE_MAX_TOKENS * 2)]
    if fallback:  # a second judge of the same family for the few candidates the first one never finishes reasoning about;
        # the slim prompt at 3x budget recovered 20 of 27 such candidates in the v7 run, the full prompt at 4x none
        plan.append((fallback[0], fallback[1], RP.CHECK_USER_SLIM, JUDGE_MAX_TOKENS * 3))
    for client, model, template, max_tokens in plan:
        user = template.format(record_json=rec_json, rewrite=rewrite_text)
        resp = await client.complete(LLMRequest(model=model, system=RP.CHECK_SYSTEM, user=user, temperature=0.0, max_tokens=max_tokens))
        d = parse_json_object(resp.text)
        if d:
            return d
    return {}


def sample_items(prompts: dict[str, Prompt], demos: list[TeacherResponse], n: int, seed: int) -> list[TeacherResponse]:
    """Answered demo rows on two_action prompts (variant != VC), stratified by variant."""
    rng = random.Random(seed)
    by_variant: dict[str, list[TeacherResponse]] = defaultdict(list)
    for r in demos:
        p = prompts.get(r.prompt_id)
        if p and p.variant != "VC" and r.category == "answer":
            by_variant[p.variant].append(r)
    for lst in by_variant.values():
        rng.shuffle(lst)
    out: list[TeacherResponse] = []
    variants = sorted(by_variant)
    while len(out) < n and any(by_variant[v] for v in variants):
        for v in variants:
            if by_variant[v] and len(out) < n:
                out.append(by_variant[v].pop())
    return out


async def run_rewrite_pilot(
    prompts: dict[str, Prompt], items: list[TeacherResponse], styles: list[str],
    rewriter: LLMClient, rewriter_model: str, rewriter_name: str, judge: LLMClient, judge_model: str,
    out_dir: Path, cfg_rw: dict, judge_fallback: Optional[tuple[LLMClient, str]] = None,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    records_path, rewrites_path = out_dir / "records.jsonl", out_dir / "rewrites.jsonl"
    stats: dict = defaultdict(int)
    lock = asyncio.Lock()
    # resume: an item is done only when every requested style has a kept rewrite or has used all its attempts
    # (a record alone is not enough: a run killed between extraction and rewriting must redo that item; the
    # extraction itself is served from the cache).
    if rewrites_path.exists():
        max_attempts = int(cfg_rw["max_retries"]) + 1
        kept: dict[tuple[str, str], bool] = {}
        attempts: dict[tuple[str, str], int] = defaultdict(int)
        for r in read_jsonl(rewrites_path):
            key = (r["prompt_id"], r["version"])
            attempts[key] += 1
            kept[key] = kept.get(key, False) or bool(r.get("kept"))
        done = {pid for pid in {k[0] for k in attempts} if all(kept.get((pid, s), False) or attempts[(pid, s)] >= max_attempts for s in styles)}
        before = len(items)
        items = [it for it in items if it.prompt_id not in done]
        stats["skipped_done"] = before - len(items)

    async def one(item: TeacherResponse) -> None:
        p = prompts[item.prompt_id]
        rec = await extract_record(judge, judge_model, p, item)
        async with lock:
            stats["items"] += 1
            if rec is None:
                stats["record_failed"] += 1
                return
            write_jsonl(records_path, [rec], append=True)
        for style in styles:
            kept, attempt, feedback = False, 0, None
            while not kept and attempt <= int(cfg_rw["max_retries"]):
                temp = float(cfg_rw["rewrite_temperature"]) if attempt == 0 else float(cfg_rw["retry_temperature"])
                mode = "sentence" if style in (cfg_rw.get("sentence_mode_styles") or []) else "whole"
                text, truncated = await rewrite_once(rewriter, rewriter_model, p, rec, style, temp, feedback=feedback, mode=mode, max_tokens_floor=int(cfg_rw.get("rewrite_max_tokens", 0)))
                judged = await judge_rewrite(judge, judge_model, rec, text, fallback=judge_fallback)  # escalates budget, then falls back
                checks = evaluate_checks(rec, text, judged, style, truncated=truncated)
                checks["judge_failed"] = not judged
                kept = checks["kept"]
                feedback = None if kept or not judged else (build_feedback(rec, checks, judged, style) or None)
                row = Rewrite(prompt_id=p.prompt_id, teacher=item.teacher, version=style, rewriter=rewriter_name, attempt=attempt, text=text, judged=judged, checks=checks, kept=kept)
                async with lock:
                    write_jsonl(rewrites_path, [row], append=True)
                    stats[f"{style}_attempts"] += 1
                    stats[f"{style}_judge_failed"] += int(checks["judge_failed"])
                    for k, v in checks.items():
                        if k not in ("kept", "judge_failed", "lexical"):
                            stats[f"{style}_{k}_ok"] += int(v)
                attempt += 1
            async with lock:
                stats[f"{style}_kept"] += int(kept)

    await asyncio.gather(*(one(it) for it in items))
    return dict(stats)


def summarize(stats: dict, styles: list[str]) -> str:
    n = stats.get("items", 0) - stats.get("record_failed", 0)
    lines = [f"items: {stats.get('items', 0)}, record extraction failed: {stats.get('record_failed', 0)}"]
    for s in styles:
        att = stats.get(f"{s}_attempts", 0) or 1
        kept = stats.get(f"{s}_kept", 0)
        lines.append(
            f"[{s}] kept {kept}/{n} (filter rate {1 - kept / n if n else float('nan'):.2f}); per attempt: "
            + ", ".join(f"{k} {stats.get(f'{s}_{k}_ok', 0) / att:.2f}" for k in ("choice", "reasons", "conditions", "strength", "style", "format"))
            + f"; judge JSON failures {stats.get(f'{s}_judge_failed', 0)}"
        )
    return "\n".join(lines)
