"""Text normalization: situations in second person, actions as imperatives, T3 first-person conversion.

Everything here is rule-based so the pilot can be built without a GPU. Each function reports
flags for cases a human (or the judge model J) should look at.
"""

from __future__ import annotations

import re

_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z\"'(])")


def split_trailing_question(text: str) -> tuple[str, str]:
    """Drop trailing interrogative sentences. Returns (declarative_part, removed_questions)."""
    text = " ".join(text.split())
    sents = _SENT_SPLIT.split(text)
    removed: list[str] = []
    while sents and sents[-1].rstrip().endswith("?"):
        removed.insert(0, sents.pop())
    if not sents:  # the whole text was a question; keep it and let the caller flag it
        return text, ""
    return " ".join(sents).strip(), " ".join(removed).strip()


def _cap(s: str) -> str:
    return s[0].upper() + s[1:] if s else s


# words ending in -ing that are base verbs or nouns, not gerunds
_ING_NOT_GERUND = {"bring", "sing", "ring", "swing", "cling", "fling", "sting", "string", "wring", "spring", "thing", "nothing", "something", "everything", "anything", "morning", "evening"}


def _verb_lemma(word: str) -> str:
    try:
        from lemminflect import getLemma

        lem = getLemma(word.lower(), upos="VERB")
        if lem:
            return lem[0]
    except Exception:  # lemminflect missing: naive fallback
        pass
    w = word.lower()
    if w.endswith("ing") and len(w) > 4:
        stem = w[:-3]
        if len(stem) > 2 and stem[-1] == stem[-2] and stem[-1] not in "lsfz":
            stem = stem[:-1]
        return stem
    return w


def degerund_first_word(phrase: str) -> tuple[str, bool]:
    """'reading the journal' -> 'read the journal'. Returns (phrase, changed)."""
    words = phrase.split()
    if not words:
        return phrase, False
    w0 = words[0]
    if len(w0) > 4 and w0.lower().endswith("ing") and w0.lower() not in _ING_NOT_GERUND:
        base = _verb_lemma(w0)
        if base and base != w0.lower():
            words[0] = base[0].upper() + base[1:] if w0[0].isupper() else base
            return " ".join(words), True
    return phrase, False


def normalize_action(action: str) -> tuple[str, list[str]]:
    """DailyDilemmas actions -> imperative: 'Report the colleague' / 'Not report the colleague' /
    'Reading the journal' / 'Not reading the journal' -> 'Report the colleague.' / 'Do not report the colleague.' /
    'Read the journal.' / 'Do not read the journal.'"""
    flags: list[str] = []
    a = " ".join(action.split()).strip().rstrip(".").strip()
    prefix = ""
    if re.match(r"^not\s+", a, re.I):
        prefix, a = "Do not ", a[4:].lstrip()
    a, changed = degerund_first_word(a)
    if changed:
        flags.append("degerund")
    if len(a.split()) <= 2:
        flags.append("short_action")
    out = prefix + (a[0].lower() + a[1:] if prefix and a else a) if prefix else _cap(a)
    return out + ".", flags


_PRON_1_TO_2 = [
    (r"\bmyself\b", "yourself"),
    (r"\bMyself\b", "Yourself"),
    (r"\bmy\b", "your"),
    (r"\bMy\b", "Your"),
    (r"\bmine\b", "yours"),
    (r"\bMine\b", "Yours"),
    (r"\bme\b", "you"),
    (r"\bMe\b", "You"),
    (r"\bI'm\b", "you're"),
    (r"\bI am\b", "you are"),
    (r"\bI\b", "you"),
]


def first_person_to_imperative(action: str) -> tuple[str, list[str]]:
    """MoralChoice actions: 'I do not throw the grenade.' -> 'Do not throw the grenade.'"""
    flags: list[str] = []
    a = " ".join(action.split()).strip().rstrip(".").strip()
    m = re.match(r"^I\s+(.*)$", a)
    if not m:
        flags.append("action_not_first_person")
        rest = a
    else:
        rest = m.group(1)
        low = rest.lower()
        if low.startswith("do not "):
            rest = "Do not " + rest[7:]
        elif low.startswith("don't "):
            rest = "Don't " + rest[6:]
        elif low.startswith("am "):
            rest = "Be " + rest[3:]
        elif low.startswith("will "):
            rest = rest[5:]
        elif low.startswith("would "):
            rest = rest[6:]
        elif re.match(r"^(have|has|had|was|were)\b", low):
            flags.append("action_aux_verb")
    for pat, rep in _PRON_1_TO_2:
        rest = re.sub(pat, rep, rest)
    return _cap(rest) + ".", flags


# ---- second person -> first person (for T3) -------------------------------------------------

_FIXED_2_TO_1 = [
    (r"\byou're\b", "I'm"),
    (r"\bYou're\b", "I'm"),
    (r"\byou are\b", "I am"),
    (r"\bYou are\b", "I am"),
    (r"\byou were\b", "I was"),
    (r"\bYou were\b", "I was"),
    (r"\byou've\b", "I've"),
    (r"\bYou've\b", "I've"),
    (r"\byou'll\b", "I'll"),
    (r"\bYou'll\b", "I'll"),
    (r"\byou'd\b", "I'd"),
    (r"\bYou'd\b", "I'd"),
    (r"\byourselves\b", "ourselves"),
    (r"\byourself\b", "myself"),
    (r"\bYourself\b", "Myself"),
    (r"\byours\b", "mine"),
    (r"\bYours\b", "Mine"),
    (r"\byour\b", "my"),
    (r"\bYour\b", "My"),
]

# If the word before "you" is one of these, "you" is an object -> "me".
_OBJECT_CUES = {
    "to", "for", "with", "at", "from", "on", "of", "about", "against", "than", "like", "between",
    "toward", "towards", "near", "beside", "behind", "without", "around", "upon", "into", "onto",
    "over", "under", "after", "before", "by", "ask", "asks", "asked", "tell", "tells", "told", "give",
    "gives", "gave", "offer", "offers", "offered", "want", "wants", "wanted", "help", "helps",
    "helped", "let", "lets", "make", "makes", "made", "allow", "allows", "allowed", "force", "forces",
    "forced", "invite", "invites", "invited", "expect", "expects", "expected", "pay", "pays", "paid",
    "owe", "owes", "owed", "leave", "leaves", "left", "see", "sees", "saw", "approach", "approaches",
    "approached", "contact", "contacts", "contacted", "inform", "informs", "informed", "warn", "warns",
    "warned", "remind", "reminds", "reminded", "trust", "trusts", "trusted", "need", "needs", "needed",
    "call", "calls", "called", "thank", "thanks", "thanked", "blame", "blames", "blamed", "confront",
    "confronts", "confronted", "pressure", "pressures", "pressured", "beg", "begs", "begged",
    "press", "presses", "pressed", "urge", "urges", "urged", "convince", "convinces", "convinced",
    "encourage", "encourages", "encouraged", "persuade", "persuades", "persuaded", "advise", "advises",
    "advised", "order", "orders", "ordered", "instruct", "instructs", "instructed", "promise", "promises",
    "promised", "assure", "assures", "assured", "threaten", "threatens", "threatened", "accuse", "accuses",
    "accused", "criticize", "criticizes", "criticized", "support", "supports", "supported", "join", "joins",
    "joined", "visit", "visits", "visited", "notice", "notices", "noticed", "show", "shows", "showed",
    "teach", "teaches", "taught", "lend", "lends", "lent", "hire", "hires", "hired", "fire", "fires", "fired",
    "reach", "reaches", "reached", "stop", "stops", "stopped", "catch", "catches", "caught", "find", "finds",
    "found", "keep", "keeps", "kept", "put", "puts", "bring", "brings", "brought", "send", "sends", "sent",
    "take", "takes", "took", "drive", "drives", "drove", "pick", "picks", "picked", "drop", "drops", "dropped",
    "meet", "meets", "met", "love", "loves", "loved", "hate", "hates", "hated", "respect", "respects", "respected",
}

# If the word after "you" is one of these, "you" is an object -> "me" ("presses you to", "tells you that").
_OBJECT_NEXT = {
    "to", "that", "a", "an", "the", "some", "any", "this", "these", "those", "about", "for", "with", "from",
    "into", "on", "at", "of", "as", "by", "in", "up", "out", "off", "down", "over", "back", "away", "here",
    "there", "again", "anything", "something", "everything", "nothing", "whether", "if", "how", "what",
    "when", "where", "why", "money", "more", "less", "enough", "too", "instead", "first", "last", "alone",
}

_TOKEN = re.compile(r"[A-Za-z']+|[^A-Za-z']+")

_SECOND_PERSON = re.compile(r"\b(you|your|yours|yourself|yourselves|you're|you've|you'll|you'd)\b", re.IGNORECASE)
_FIRST_PERSON = re.compile(r"\b(I|I'm|I've|I'll|I'd|my|me|myself|mine)\b")


def detect_person(text: str) -> str:
    """'second' if the text addresses 'you', else 'first' if it has first-person pronouns, else 'third'."""
    if _SECOND_PERSON.search(text):
        return "second"
    if _FIRST_PERSON.search(text):
        return "first"
    return "third"


def second_to_first_person(text: str) -> tuple[str, list[str]]:
    """Heuristic conversion used to build T3. Always flagged `t3_auto` for human review."""
    flags = ["t3_auto"]
    out = " ".join(text.split())
    for pat, rep in _FIXED_2_TO_1:
        out = re.sub(pat, rep, out)
    tokens = _TOKEN.findall(out)
    words_idx = [i for i, t in enumerate(tokens) if re.match(r"^[A-Za-z']+$", t)]
    for pos, i in enumerate(words_idx):
        t = tokens[i]
        if t.lower() != "you":
            continue
        prev_w = tokens[words_idx[pos - 1]].lower() if pos > 0 else None
        nxt_i = words_idx[pos + 1] if pos + 1 < len(words_idx) else None
        # a following word counts only if nothing but whitespace separates them (same clause)
        between = "".join(tokens[i + 1 : nxt_i]) if nxt_i is not None else ""
        next_is_word = nxt_i is not None and between.strip() == ""
        next_w = tokens[nxt_i].lower() if next_is_word else None
        if prev_w in _OBJECT_CUES or not next_is_word or next_w in _OBJECT_NEXT:
            tokens[i] = "me"
        else:
            tokens[i] = "I"
    out = "".join(tokens)
    # sentence-initial capitalization after substitutions ("my mother" at sentence start -> "My")
    out = re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)
    if " you " in f" {out.lower()} ":
        flags.append("t3_residual_you")
    return out, flags
