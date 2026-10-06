"""Candidate sources for the contested-enriched pool (E2c) -> Family rows, rule-based, no LLM.

Sources (tasks/e2c_plan.md §1):
  scruples          Scruples Anecdotes, HYPOTHETICAL (WIBTA) posts only: body -> second person, action from
                    `action.description`, alternative = its negation. Community votes kept as a disagreement prior.
  aita_berkeley     ucberkeley-dlab everyday dilemmas (r/AITA 2022-23): WIBTA posts plus human-contested
                    retrospective posts; the action pair comes from the title.
  moral_stories     Moral Stories (Emelin et al.): situation + intention -> second person; x = normative action,
                    y = divergent action (both imperatives).
  hendrycks_ethics  ETHICS justice, impartiality items "I usually VP but didn't ... because R" -> habit + reason.

Every loader returns Family rows with split "pool_contested", `meta.provenance` and the source ids, plus
`needs_review` flags. Flags in HARD_FLAGS mean the conversion is not trusted; the build script drops those rows
and reports the counts. Everything else is informational and stays in the row.
"""

from __future__ import annotations

import csv
import hashlib
import html
import json
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

from vcd.data.normalize import _OBJECT_CUES, _cap, degerund_first_word, detect_person, normalize_action, split_trailing_question
from vcd.schemas import Family

POOL_SPLIT = "pool_contested"

# Conversions with any of these flags are dropped by scripts/16_build_contested_pool.py (reported per source).
HARD_FLAGS = {
    "title_unparsed",
    "action_missing",
    "action_stative_verb",
    "action_first_word_not_verb",
    "body_too_short",
    "body_too_long",
    "not_second_person",
    "residual_first_person",
    "residual_actor_name",
    "pronoun_ambiguous",
    "no_impartiality_match",
    "long_action",
    "gender_unknown",
    "habit_discontinued",  # ETHICS 'I used to VP but ...': the habit has stopped, no decision to make
    "pronoun_residue",  # "<X> and you's" that the rewrite could not repair
    # added after the round-1 hand check (results/e2c/handcheck_round1_report.md)
    "residual_first_person_plural",  # we / our / us / ours / ourselves left outside quoted speech
    "quoted_first_person",  # I / me / my inside quoted speech: the speaker would become unrecoverable
    "opens_mid_stream",  # first sentence starts with a pronoun whose antecedent was in the stripped title / question
    "bystander_post",  # narrator judges somebody else's act
    "plural_refers_to_actor",  # Moral Stories: they / their / the two standing for the actor plus someone
    # added after the round-2 hand check (results/e2c/handcheck_round2_report.md)
    "pronoun_same_gender_other",  # Moral Stories: the actor's pronoun follows a same-gender other person (14/18 wrong in round 2)
    "actions_identical",  # Moral Stories: x == y once bracketed insertions and source noise are stripped
    "reflexive_residual",  # Moral Stories: 'Introduce himself' after the imperative head: the actor's gender was mis-inferred
    # added after the round-3 hand check (results/e2c/handcheck_round3_report.md)
    "possessive_without_noun",  # Moral Stories: 'Your found out' / 'yours back yard': a possessive that no noun phrase follows
}

# License of each source as read from its Hugging Face card / upstream repo (tasks/e2c_plan.md §10).
LICENSES = {
    "scruples": "research-only (allenai/scruples upstream; tasksource mirror says apache-2.0)",
    "aita_berkeley": "cc-by-nc-4.0",
    "moral_stories": "unspecified on HF card; upstream github.com/demelin/moral_stories (derived from Social Chemistry 101, CC BY-SA 4.0)",
    "hendrycks_ethics": "mit",
    "moralchoice": "cc-by-4.0",
}


def is_rule_clean(fam: Family) -> bool:
    return not (HARD_FLAGS & set(fam.needs_review))


# ---- first person -> second person -------------------------------------------------------------------

_QUOTES = str.maketrans({"\u2019": "'", "\u2018": "'", "\u201c": '"', "\u201d": '"'})

# Case-insensitive contraction / agreement table (round-1 hand check: "i'm" -> "you'm", "Ive", "id", "MY",
# "I was" -> "you was" were the singular residue). Replacements are lower-case; `_match_case` restores the
# source casing and the sentence-initial pass capitalises.
_1_TO_2 = [
    (re.compile(r"\bI'm\b", re.IGNORECASE), "you're"),
    (re.compile(r"\b[Ii]m\b"), "you're"),  # Reddit spelling of I'm; upper-case IM is kept
    (re.compile(r"\bI am\b", re.IGNORECASE), "you are"),
    (re.compile(r"\bI was not\b", re.IGNORECASE), "you were not"),
    (re.compile(r"\bI wasn't\b", re.IGNORECASE), "you weren't"),
    (re.compile(r"\bI was\b", re.IGNORECASE), "you were"),
    (re.compile(r"\bI've\b", re.IGNORECASE), "you've"),
    (re.compile(r"\b[Ii]ve\b"), "you've"),
    (re.compile(r"\bI'd\b", re.IGNORECASE), "you'd"),
    (re.compile(r"\b[Ii]d\b"), "you'd"),  # 'id' (Reddit I'd); upper-case ID is kept
    (re.compile(r"\bI'll\b", re.IGNORECASE), "you'll"),
    (re.compile(r"\bIll\b"), "you'll"),  # capital I only: 'ill' is an adjective
    (re.compile(r"(?<!\d)(?<!\d )\bam I\b", re.IGNORECASE), "are you"),  # not clock times: "at 5 am I ..."
    (re.compile(r"\bwasn't I\b", re.IGNORECASE), "weren't you"),
    (re.compile(r"\bwas I\b", re.IGNORECASE), "were you"),
    (re.compile(r"\bmyself\b", re.IGNORECASE), "yourself"),
    (re.compile(r"\bmine\b", re.IGNORECASE), "yours"),
    (re.compile(r"\bmy\b", re.IGNORECASE), "your"),
    (re.compile(r"\bme\b", re.IGNORECASE), "you"),
    (re.compile(r"\bI\b|\bi\b"), "you"),
]
# Fixed expressions whose 'me' / 'I' is not the decision-maker's narrative: removed before conversion.
_IDIOMS = re.compile(
    r"\b(?:(?:don'?t|do not) get me wrong|bear with me|hear me out|believe me|trust me|mind you|"
    r"let me (?:just )?(?:be clear|explain|clarify|preface (?:this|it)(?: by saying)?|start (?:off )?(?:by saying|by|with)|say|add|"
    r"get this straight|put it this way|give (?:you )?(?:some|a (?:little|bit of)) (?:background|context))(?: that)?|"
    r"if you ask me|if (?:I'm|I am) (?:being )?honest|as far as I (?:know|can tell)|for what it's worth|"
    r"(?:I'll|I will|Ill) (?:try to )?(?:keep|make) (?:this|it) (?:as )?(?:very |really )?(?:short|brief|quick)(?: as possible)?|"
    r"(?:I'll|I will|Ill) start (?:off )?(?:with|by saying)(?: that)?)\b[,.!;:]?\s*|"
    r"\b(?:please )?let me know (?:if|what|whether|how|in the comments|below|your)\b[^.!?]*",
    re.IGNORECASE,
)
_IE = re.compile(r"\bi\.e\.", re.IGNORECASE)
_IE_TOKEN = "\x00IE\x00"
_ADVS_BETWEEN = r"(?:\s+(?:\w+ly|still|also|just|never|always|then|now|too|both|not|only|even|already|kinda|sorta|very|so|really|definitely|probably|obviously|certainly|usually|often|sometimes|genuinely|truly|seriously|totally|completely|absolutely|basically|literally|personally|honestly|actually))*"
_YOU_BE = re.compile(rf"\b(you)({_ADVS_BETWEEN})\s+(am|was not|wasn't|was)\b", re.IGNORECASE)
_BE_MAP = {"am": "are", "was": "were", "wasn't": "weren't", "was not": "were not"}
_BARE_AM = re.compile(r"(?<![\d.:])(?<!\d )\b[Aa]m\b")  # 'am' is first person only, except clock times
_FIRST_PERSON_RESIDUAL = re.compile(r"\b(I|me|my|myself|mine|I'm|I've|I'd|I'll|im|ive)\b", re.IGNORECASE)
_FIRST_PERSON_SINGULAR = re.compile(r"\b(I|me|my|myself|mine|I'm|I've|I'd|I'll|Im|Ive)\b")  # inside quotes: case-sensitive
_SECOND_PERSON_SRC = re.compile(r"\b(you|your|yours|yourself|you're|you've|you'll|you'd)\b", re.IGNORECASE)
_WE = re.compile(r"\b(we|us|our|ours|ourselves|we're|we've|we'll|we'd)\b", re.IGNORECASE)
# Quoted speech: "..." (typographic quotes already translated) and '...' opened after a non-word character and
# closed by a quote not followed by a letter (so possessives like friends' do not open or close a span).
_QUOTE_SPAN = re.compile(r"\"[^\"]{1,400}\"|(?<![A-Za-z0-9])'(?=[A-Za-z\"])[^\n]{1,300}?'(?![A-Za-z])")


def _match_case(src: str, rep: str) -> str:
    if len(src) > 1 and src.isupper():
        return rep.upper()
    if src[:1].isupper() and src.lower() not in ("i", "i'm", "im", "i've", "ive", "i'd", "id", "i'll", "ill", "i am", "i was", "i wasn't", "i was not"):
        return _cap(rep)
    return rep


def split_quoted(text: str) -> list[tuple[str, bool]]:
    """[(segment, is_quoted)] in order; quoted segments include their quote marks."""
    out: list[tuple[str, bool]] = []
    pos = 0
    for m in _QUOTE_SPAN.finditer(text):
        if m.start() > pos:
            out.append((text[pos : m.start()], False))
        out.append((m.group(0), True))
        pos = m.end()
    if pos < len(text):
        out.append((text[pos:], False))
    return out


def _convert_segment(seg: str) -> str:
    out = _IE.sub(_IE_TOKEN, seg)
    out = _IDIOMS.sub("", out)
    # "my SO and I's anniversary" -> "your and your SO's anniversary" (before the pronoun pass)
    out = re.sub(r"\b([Mm]y|[Oo]ur) ([A-Za-z-]+(?: [A-Za-z-]+)?) and I's\b", lambda m: ("Your" if m.group(1)[0].isupper() else "your") + f" and your {m.group(2)}'s", out)
    for pat, rep in _1_TO_2:
        out = pat.sub(lambda m, rep=rep: _match_case(m.group(0), rep), out)
    out = _YOU_BE.sub(lambda m: f"{m.group(1)}{m.group(2)} {_match_case(m.group(3), _BE_MAP[m.group(3).lower()])}", out)
    out = _BARE_AM.sub(lambda m: _match_case(m.group(0), "are"), out)
    return out.replace(_IE_TOKEN, "i.e.")


def first_to_second_person(text: str) -> tuple[str, list[str]]:
    """Author narrative -> addressed to 'you', outside quoted speech. Flags: source_has_second_person (generic
    'you' in the original becomes ambiguous), residual_first_person (hard), quoted_first_person (hard: a quoted
    speaker says I / me, the conversion would make the speaker unrecoverable), residual_first_person_plural (hard:
    we / our / us left outside quotes), pronoun_residue (hard)."""
    flags: list[str] = []
    text = " ".join(text.translate(_QUOTES).split())
    parts: list[str] = []
    for seg, quoted in split_quoted(text):
        if quoted:
            if _FIRST_PERSON_SINGULAR.search(seg):
                flags.append("quoted_first_person")
            parts.append(seg)
            continue
        if _SECOND_PERSON_SRC.search(seg):
            flags.append("source_has_second_person")
        parts.append(_convert_segment(seg))
    out = " ".join("".join(parts).split())
    out = re.sub(r"\s+([,.!?;:])", r"\1", out)
    out = re.sub(r"[,;:]\s*([.!?])", r"\1", out)  # ', .' left by a removed idiom
    out = re.sub(r"(^|(?<!i\.e)(?<!e\.g)[.!?][\"']?\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)
    unquoted = _IE.sub("", " ".join(seg for seg, quoted in split_quoted(out) if not quoted))
    if _FIRST_PERSON_RESIDUAL.search(unquoted):
        flags.append("residual_first_person")
    if re.search(r"\byou's\b", unquoted):
        flags.append("pronoun_residue")
    if _WE.search(unquoted):
        flags.append("residual_first_person_plural")
    return out, sorted(set(flags))


_WE_TO_YOU = [(r"\bwe're\b", "you're"), (r"\bwe've\b", "you've"), (r"\bwe'll\b", "you'll"), (r"\bwe'd\b", "you'd"), (r"\bwe\b", "you"), (r"\bus\b", "you"), (r"\bour\b", "your"), (r"\bours\b", "yours"), (r"\bourselves\b", "yourselves")]


def plural_to_second_person(text: str) -> tuple[str, bool]:
    """Inside an ACTION phrase the author is the agent, so 'our host' / 'let us' -> 'your host' / 'let you'."""
    out = text
    for pat, rep in _WE_TO_YOU:
        out = re.sub(pat, lambda m, rep=rep: _cap(rep) if m.group(0)[0].isupper() else rep, out)
    return out, out != text


# ---- Reddit body cleanup ----------------------------------------------------------------------------------

_TAIL_RE = re.compile(r"(?ims)^\s*(?:\*+)?\s*(edit|edited|update|updated|eta|tl;?dr|tldr)\b.*\Z")  # edit block on its own line
_TAIL_INLINE_RE = re.compile(r"(?s)\b(EDIT|UPDATE|ETA|TL;?DR|Edit|Update|Tl;?dr)\s*\d*\s*[:\-\u2013].*\Z")  # 'EDIT: ...' mid-paragraph
_AITA_SENT = re.compile(
    r"\b(aita|wibta|waita|aitah|wibtah|ass ?hole|a-? ?hole|the ah\b|an ah\b|the a\b|ta\?|tl\s*[;/:.]?\s*dr|reddit|upvote|downvote|"
    r"throw-?away|on mobile|mobile user|formatting|first post|long post|english is not|english isn't|"
    r"not a native speaker|this sub|first[- ]time poster|poster\b|this post|post (?:this|here|your|it)|(?:re)?post(?:ed|ing)? (?:this|here|it)|"
    r"don'?t (?:re)?post|legal advice|advice (?:is )?(?:also )?welcome|make this (?:very |really )?(?:short|brief|quick)|"
    r"unbiased opinion|outside (?:opinion|perspective)|strangers'? opinions?|what do you (?:guys|all|people) think|thanks? (?:you )?(?:all |everyone |guys )?in advance|"
    r"^thanks?\b|^thank you\b|opinions\?|^(?:(?:so|but|and|also|ok|okay|anyway|anyways)\W+)?let me\b)",
    re.IGNORECASE,
)
_AITA_VERDICT = re.compile(r"\b(NTA|YTA|ESH|NAH|WNBTA|YWBTA|YWNBTA|TA|AH|AITA|WAITA|WIBTA)\b")  # case-sensitive verdict / jargon acronyms
_BYSTANDER = re.compile(r"\b(?:(?:wasn'?t|was not|am not|not|never) (?:\w+ )?involved\b|bystander|not about me\b|asking for (?:a|my) friend\b|on behalf of (?:a|my) friend)", re.IGNORECASE)
_THIRD_PERSON_OPENER = {"he", "she", "they", "him", "her", "them", "his", "their", "hers", "theirs", "himself", "herself", "themselves", "he's", "she's", "they're", "they've", "he'd", "she'd", "they'd", "he'll", "she'll", "they'll"}
_CONNECTIVE_OPENER = {"it", "it's", "this", "that", "these", "those", "since", "but", "and", "because", "however", "which", "yet", "still", "either", "neither", "otherwise", "therefore", "instead"}


def opens_mid_stream(situation: str, leading_sentence_removed: bool) -> bool:
    """True when the first word is a third-person pronoun, or a connective / 'it' after a removed leading sentence
    (the antecedent or the topic lived in the stripped title / question)."""
    words = re.findall(r"[A-Za-z']+", situation)
    if not words:
        return False
    w0 = words[0].lower()
    return w0 in _THIRD_PERSON_OPENER or (leading_sentence_removed and w0 in _CONNECTIVE_OPENER)
_LABEL_PREFIX = re.compile(r"^(backstory|background|context|story|situation|so basically|basically|ok so|okay so|so)\s*[:,\-]\s*", re.IGNORECASE)
_AGE_TAG = re.compile(r"\(\s*\d{2}\s*[MFmf]\s*\)|\(\s*[MFmf]\s*\d{2}\s*\)|\b[MFmf]\s?\(\d{2}\)")  # parenthetical: removed
_AGE_TAG_BARE = re.compile(r"\b(\d{2})\s?[MF]\b|\b[MF](\d{2})\b")  # 'I'm 24F' -> 'I'm 24': the age stays, the gender letter goes
_GREETING = re.compile(
    r"^(?:(?:hi|hello|hey|howdy|greetings|good (?:morning|evening|afternoon))(?:\s+(?:there|all|everyone|everybody|guys|y'all|reddit|friends|folks|people|internet|strangers)){0,2}\s*[,!.:\-]+\s*|(?:hi|hello|hey)\s+(?=(?:i|you|we|my|so|this|here)\b)|(?:so|ok|okay|alright|right)\s*[,!.:\-]\s*)",
    re.IGNORECASE,
)
_META_PAREN = re.compile(r"\([^)]*\b(subreddit|mobile|format|formatting|throwaway|post|posting|reddit|sorry|english|typos|grammar|long)\b[^)]*\)", re.IGNORECASE)
_SENT_SPLIT = re.compile(r"(?<=[.!?])\s+")


def clean_reddit_body(body: str) -> tuple[str, str, list[str]]:
    """Strip markdown, edit tails, AITA / meta sentences and age tags; return (declarative situation,
    removed trailing question, flags). The situation is still in the author's first person."""
    flags: list[str] = []
    b = html.unescape(body or "").translate(_QUOTES)
    b = re.sub(r"&?#?x200B;?|\u200b|\ufeff", " ", b)  # zero-width space residue of the Reddit export
    b = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", b)  # markdown links -> text
    if _META_PAREN.search(b):
        flags.append("meta_sentence_removed")
        b = _META_PAREN.sub("", b)
    b = re.sub(r"https?://\S+", "", b)
    b = re.sub(r"[*_~`>#]+", "", b)
    b = _TAIL_RE.sub("", b)
    b = _TAIL_INLINE_RE.sub("", b)
    if _AGE_TAG.search(b) or _AGE_TAG_BARE.search(b):
        flags.append("age_tag_removed")
        b = _AGE_TAG.sub("", b)
        b = _AGE_TAG_BARE.sub(lambda m: m.group(1) or m.group(2), b)
        b = re.sub(r"\s+,", ",", b)
    b = " ".join(b.split())
    b = _LABEL_PREFIX.sub("", b)
    b = _GREETING.sub("", b)
    b = _LABEL_PREFIX.sub("", b)
    if _BYSTANDER.search(b):
        flags.append("bystander_post")
    sents = [s for s in _SENT_SPLIT.split(b) if s.strip()]
    kept = []
    for k, s in enumerate(sents):
        if _AITA_SENT.search(s) or _AITA_VERDICT.search(s):
            flags.append("meta_sentence_removed")
            if k == 0 or not kept:
                flags.append("leading_sentence_removed")
            continue
        s = re.sub(r"\s+([,.!?;:])", r"\1", s).strip()
        if not re.search(r"[.!?]$", s):
            s += "."
        kept.append(s)
    text = _cap(_GREETING.sub("", _LABEL_PREFIX.sub("", " ".join(kept))))
    situation, question = split_trailing_question(text)
    if "?" in situation:
        flags.append("inner_question")
    return situation.strip(), question.strip(), sorted(set(flags))


# ---- actions ------------------------------------------------------------------------------------------------

_STATIVE = {"want", "wanting", "be", "being", "feel", "feeling", "think", "thinking", "wish", "wishing", "hope", "hoping", "like", "liking", "need", "needing", "hate", "hating", "love", "loving", "believe", "believing", "prefer", "preferring", "consider", "considering", "expect", "expecting", "have", "having", "become", "becoming", "seem", "seeming", "remain", "remaining", "know", "knowing", "dislike", "disliking", "resent", "resenting", "deserve", "deserving", "understand", "understanding", "realize", "realizing", "realise", "realising", "regret", "regretting", "appreciate", "appreciating"}
_NEG_HEAD = re.compile(r"^(not|don't|dont|do not|didn't|didnt|did not|won't|wont|will not|never|refusing to|refuse to)\s+", re.IGNORECASE)
_PAST_RE = re.compile(r"^[a-z]+(ed|t)$")
_LEAD_PRONOUN = {"me", "us", "my", "our", "myself", "i", "you", "your"}
_COORD_GERUND = re.compile(r"\b(and|or|then|but)(\s+not|\s+then|\s+also|\s+still)?\s+([A-Za-z]+ing)\b")
_NPI = [(re.compile(r"\s+any ?more\b", re.I), ""), (re.compile(r"\s+ever\b", re.I), ""), (re.compile(r"\s+at all\b", re.I), ""), (re.compile(r"\s+yet\b", re.I), ""), (re.compile(r"\banything\b", re.I), "something"), (re.compile(r"\banyone\b", re.I), "someone"), (re.compile(r"\banybody\b", re.I), "somebody"), (re.compile(r"\banywhere\b", re.I), "somewhere"), (re.compile(r"\bany\b", re.I), "some"), (re.compile(r"\beither\b", re.I), "too")]
# Function words and other tokens that lemminflect does not know as verbs but may head a garbled phrase.
_NOT_VERB_HEAD = {"to", "you", "your", "me", "my", "i", "we", "our", "us", "he", "she", "it", "they", "them", "his", "her", "their", "the", "a", "an", "this", "that", "these", "those", "some", "any", "no", "not", "and", "or", "but", "so", "if", "when", "while", "because", "for", "of", "in", "on", "at", "by", "with", "from", "about", "into", "over", "after", "before", "up", "off", "down", "very", "too", "also", "just", "still", "even", "only", "all", "both", "each", "every", "more", "most", "much", "many", "such", "than", "then", "there", "here", "what", "which", "who", "whom", "whose", "how", "why", "where", "yes", "ok", "okay", "well", "one", "two", "three", "first", "last", "next", "other", "another", "same", "own", "new", "old", "good", "bad", "big", "little", "long", "short", "mad", "angry", "upset", "sad", "happy", "tired", "sick", "late", "early", "sorry", "fine", "nice", "rude", "mean", "wrong", "right", "able", "unable", "willing", "unwilling", "ready", "sure", "unsure", "aware", "unaware", "afraid", "scared", "annoyed", "pissed", "jealous", "selfish", "petty", "honest", "dishonest", "fair", "unfair", "friendly", "unfriendly", "comfortable", "uncomfortable", "being", "am", "is", "are", "was", "were"}


_EXTRA_VERBS = {"text", "message", "email", "dm", "facetime", "friend", "unfriend", "ghost", "venmo", "zelle", "google", "photoshop", "gift", "regift", "rehome", "uninvite", "rsvp", "babysit", "dogsit", "petsit", "housesit", "carpool", "vacation", "honeymoon", "picnic", "barbecue", "bbq", "party", "prank", "roast", "tattoo", "pierce", "dye", "nickname", "snitch", "tattle", "vent", "rant", "cosplay", "livestream", "stream", "vlog", "blog", "tweet", "post", "unfollow", "unmatch", "swipe", "ditch", "bail", "snoop", "spy", "stalk", "guilt", "gaslight", "shame", "fat-shame", "slut-shame", "bodyshame", "catfish", "doxx", "dox", "mute", "unmute", "tag", "untag", "screenshot", "sext", "flake", "nap", "diet", "fast", "vape", "smoke", "juul", "drink", "pregame", "tailgate", "cater", "tip", "overtip", "undertip", "re-gift", "cc", "bcc", "invoice", "bill", "charge", "overcharge", "sue", "report", "ground", "spank", "homeschool", "unschool", "co-sign", "cosign", "co-parent", "coparent", "foster", "adopt", "elope", "propose", "divorce", "remarry", "date", "dump", "cheat", "ghostwrite", "proofread", "rewrite", "regress", "unplug", "reschedule", "cancel", "uncancel", "rebook", "double-book", "no-show", "vacay", "christmas", "gatekeep", "mansplain", "overshare", "rehash", "nitpick", "lowball", "upcharge", "shortchange", "boycott", "picket", "unionize", "ghost-read", "deadname", "misgender", "outed", "out"}


def is_base_verb(word: str) -> Optional[bool]:
    """True / False when lemminflect knows the word; None when it is out of vocabulary (novel verbs such as
    'venmo' or 'uninvite' are kept unless they sit in `_NOT_VERB_HEAD`)."""
    w = re.sub(r"[^a-z-]", "", word.lower())
    if not w or w in _NOT_VERB_HEAD:
        return False
    if w in _EXTRA_VERBS:
        return True
    try:
        from lemminflect import getAllLemmas
    except Exception:
        return None
    lemmas = getAllLemmas(w)
    if not lemmas:
        return None
    return w in lemmas.get("VERB", ())


def _strip_leading_pronoun(phrase: str, flags: list[str]) -> str:
    """'me stopping errands' -> 'stopping errands'; 'to knock on the door' -> 'knock on the door'."""
    words = phrase.split()
    changed = False
    while len(words) > 1 and (words[0].lower() in _LEAD_PRONOUN or words[0].lower() == "to"):
        words.pop(0)
        changed = True
    if changed:
        flags.append("leading_pronoun_dropped")
    return " ".join(words)


def degerund_coordinated(phrase: str) -> tuple[str, bool]:
    """'show up for free food and leaving' -> 'show up for free food and leave': every -ing verb right after
    and / or / then / but (optionally 'not') takes its base form."""

    def rep(m: re.Match) -> str:
        w = m.group(3)
        if len(w) <= 4 or w.lower() in _ING_NOT_GERUND_LOCAL:
            return m.group(0)
        base = _verb_base(w)
        if not base or base == w.lower():
            return m.group(0)
        return f"{m.group(1)}{m.group(2) or ''} {base}"

    out = _COORD_GERUND.sub(rep, phrase)
    return out, out != phrase


def strip_npi(vp: str) -> str:
    """Affirmative built from a negated phrase: 'talk to your grandma anymore' -> 'talk to your grandma'."""
    out = vp
    for pat, rep in _NPI:
        out = pat.sub(rep, out)
    return " ".join(out.split())


def _verb_base(word: str) -> str:
    try:
        from lemminflect import getLemma

        lem = getLemma(word.lower(), upos="VERB")
        if lem:
            return lem[0]
    except Exception:
        pass
    return word.lower()


def _action_pair_from_vp(vp: str, negated: bool) -> tuple[str, str]:
    """vp = bare second-person verb phrase ('report your brother'). The asked action is x."""
    vp = vp.strip().rstrip(".?!").strip()
    pos_vp = strip_npi(vp) if negated else vp
    pos = _cap(pos_vp) + "."
    neg = "Do not " + vp[0].lower() + vp[1:] + "."
    return (neg, pos) if negated else (pos, neg)


_LEAD_ADV = {"only", "basically", "essentially", "potentially", "technically", "possibly", "probably", "maybe", "kinda", "literally", "actually", "accidentally", "purposely", "purposefully", "intentionally", "unintentionally", "indirectly", "jokingly", "repeatedly", "constantly", "mostly", "mainly", "sometimes", "occasionally", "rarely", "even", "just", "still", "also", "really", "pretty", "kind", "sort"}
_ING_NOT_GERUND_LOCAL = {"bring", "sing", "ring", "swing", "cling", "fling", "sting", "string", "wring", "spring", "thing", "nothing", "something", "everything", "anything", "morning", "evening"}


def _strip_leading_adverbs(phrase: str, flags: list[str]) -> str:
    """'potentially failing your classmates' -> 'failing your classmates' (flag leading_adverb_dropped)."""
    words = phrase.split()
    k = 0
    while k < len(words) - 1 and (_is_adv(words[k].lower()) or words[k].lower() in _LEAD_ADV):
        k += 1
    if k:
        flags.append("leading_adverb_dropped")
    return " ".join(words[k:])


def repair_head(vp: str) -> str:
    """A naive de-gerund can lose a final e ('rehoming' -> 'rehom'): when the head is unknown and head + 'e' is a
    known verb, use that."""
    words = vp.split()
    if words and is_base_verb(words[0]) is None and is_base_verb(words[0] + "e"):
        words[0] = words[0] + "e"
        return " ".join(words)
    return vp


def _check_imperative_head(vp: str, flags: list[str]) -> None:
    """After normalisation the first word must be a base verb: a surviving gerund or a stative verb is a hard flag."""
    w0 = vp.split()[0].lower() if vp.split() else ""
    if w0 in _STATIVE or w0 in ("am", "is", "are", "was", "were", "being"):
        flags.append("action_stative_verb")
    if len(w0) > 4 and w0.endswith("ing") and w0 not in _ING_NOT_GERUND_LOCAL:
        flags.append("action_first_word_not_verb")
    elif w0:
        known = is_base_verb(w0)
        if known is False:
            flags.append("action_first_word_not_verb")
        elif known is None:
            flags.append("head_verb_unknown")


def actions_from_description(desc: str) -> tuple[Optional[tuple[str, str]], list[str], bool]:
    """Scruples `action.description` (author's first-person gerund phrase) -> (x, y), flags, negated.

    'reporting my brother for neglect' -> ('Report your brother for neglect.', 'Do not report your brother for neglect.')
    'not letting her use my controller' -> ('Do not let her use your controller.', 'Let her use your controller.')
    """
    flags: list[str] = []
    d = " ".join((desc or "").translate(_QUOTES).replace('"', " ").split()).strip().rstrip("?.!")
    if not d:
        return None, ["action_missing"], False
    negated = bool(_NEG_HEAD.match(d))
    d = _NEG_HEAD.sub("", d)
    d = _strip_leading_pronoun(d, flags)
    d = _strip_leading_adverbs(d, flags)
    d2, fl = first_to_second_person(d)
    flags += [f for f in fl if f not in ("residual_first_person_plural", "quoted_first_person")]
    d2, changed = plural_to_second_person(d2)
    if changed:
        flags.append("action_plural_to_second")
    d2 = d2[0].lower() + d2[1:]
    act, nflags = normalize_action(d2)  # degerunds the first word, capitalizes, adds the period
    flags += nflags
    vp = repair_head(act.rstrip("."))
    vp, changed = degerund_coordinated(vp)
    if changed:
        flags.append("degerund_coordinated")
    _check_imperative_head(vp, flags)
    if len(vp.split()) > 22:
        flags.append("long_action")
    return _action_pair_from_vp(vp, negated), sorted(set(flags)), negated


_TITLE_RE = re.compile(
    r"^\s*(?:\[?\s*(?:AITA|WIBTA|AITAH|WIBTAH)\s*\]?)\s*[:\-?,]*\s*(?P<kind>for|if i|because i|bc i|when i|that i)\s+(?P<phrase>.+?)\s*[?.!]*\s*$",
    re.IGNORECASE,
)


def actions_from_title(title: str) -> tuple[Optional[tuple[str, str]], list[str], bool, bool]:
    """AITA / WIBTA title -> (x, y), flags, negated, prospective.

    'WIBTA if I declined the invitation?' -> ('Decline the invitation.', 'Do not decline the invitation.'), prospective
    'AITA for not leaving pie for our host?' -> ('Do not leave pie for your host.', 'Leave pie for your host.')
    """
    title = (title or "").translate(_QUOTES)
    m = _TITLE_RE.match(title)
    if not m:
        return None, ["title_unparsed"], False, False
    kind = m.group("kind").lower()
    phrase = " ".join(_AGE_TAG.sub("", m.group("phrase").replace('"', " ")).split())  # '"siding" with my mother' -> 'siding with my mother'; 'I (27f) ...' -> 'I ...'
    letters = [c for c in phrase if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.6:  # shouting title: pronoun rules are case-sensitive
        phrase = phrase.lower()
    prospective = bool(re.match(r"^\s*\[?\s*WIBTA", title or "", re.IGNORECASE))
    flags: list[str] = []
    neg_m = _NEG_HEAD.match(phrase)
    negated = bool(neg_m)
    refusal_head = bool(neg_m and "refus" in neg_m.group(0).lower())  # 'for refusing to X' -> rest is a base verb
    phrase = _NEG_HEAD.sub("", phrase)
    phrase = _strip_leading_pronoun(phrase, flags)
    phrase = _strip_leading_adverbs(phrase, flags)
    words = phrase.split()
    if not words:
        return None, ["title_unparsed"], negated, prospective
    w0 = words[0]
    if kind == "for" and not refusal_head:
        phrase2, changed = degerund_first_word(phrase)
        if not changed and not w0.lower().endswith("ing"):
            flags.append("title_first_word_not_gerund")
        words = phrase2.split()
        phrase2, changed = degerund_coordinated(" ".join(words))
        if changed:
            flags.append("degerund_coordinated")
        words = phrase2.split()
    else:  # 'if I <verb>' : past or present tense -> base form
        base = _verb_base(w0)
        if base == w0.lower() and _PAST_RE.match(w0.lower()) and len(w0) > 4:
            base = w0.lower()[:-1] if w0.lower().endswith("ed") and w0.lower()[-3] == "e" else w0.lower()[:-2] if w0.lower().endswith("ed") else base
        words[0] = base
    phrase = " ".join(words)
    phrase, fl = first_to_second_person(phrase)
    flags += [f for f in fl if f not in ("residual_first_person_plural", "quoted_first_person")]
    phrase, changed = plural_to_second_person(phrase)
    if changed:
        flags.append("action_plural_to_second")
    vp = repair_head(phrase[0].lower() + phrase[1:])
    _check_imperative_head(vp, flags)
    if len(vp.split()) > 22:
        flags.append("long_action")
    if len(vp.split()) <= 1:
        flags.append("short_action")
    return _action_pair_from_vp(vp, negated), sorted(set(flags)), negated, prospective


def _vote_stats(label_scores: dict, binarized: dict) -> dict:
    n = int(sum(int(v) for v in (label_scores or {}).values()))
    right, wrong = int((binarized or {}).get("RIGHT", 0)), int((binarized or {}).get("WRONG", 0))
    tot = right + wrong
    return {"n_votes": n, "right": right, "wrong": wrong, "minority_share": (min(right, wrong) / tot) if tot else None}


# ---- Scruples anecdotes -----------------------------------------------------------------------------------------


def load_scruples(paths: Iterable[str | Path], max_words: int = 300, min_words: int = 20, post_types: tuple[str, ...] = ("HYPOTHETICAL",)) -> list[Family]:
    """Scruples Anecdotes jsonl files -> Family rows (one per post). Only `post_types` are kept."""
    fams: list[Family] = []
    seen: set[str] = set()
    for path in paths:
        with open(path, encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                r = json.loads(line)
                if r.get("post_type") not in post_types or r["post_id"] in seen:
                    continue
                seen.add(r["post_id"])
                flags: list[str] = []
                acts, aflags, negated = actions_from_description((r.get("action") or {}).get("description", ""))
                flags += aflags
                sit1, question, cflags = clean_reddit_body(r.get("text", ""))
                flags += cflags
                sit2, pflags = first_to_second_person(sit1)
                flags += pflags
                if opens_mid_stream(sit2, "leading_sentence_removed" in cflags):
                    flags.append("opens_mid_stream")
                n_words = len(sit2.split())
                if n_words < min_words:
                    flags.append("body_too_short")
                if n_words > max_words:
                    flags.append("body_too_long")
                if detect_person(sit2) != "second":
                    flags.append("not_second_person")
                ax, ay = acts if acts else ("", "")
                if not acts:
                    flags.append("action_missing")
                fams.append(
                    Family(
                        family_id=f"scr_{r['post_id']}",
                        source="scruples",
                        source_id=str(r["id"]),
                        topic_group="aita",
                        situation=sit2,
                        question_original=first_to_second_person(question)[0] if question else "",
                        action_x=ax or "Unparsed.",
                        action_y=ay or "Unparsed.",
                        ambiguity="unknown",
                        split=POOL_SPLIT,
                        needs_review=sorted(set(flags)),
                        meta={
                            "provenance": "scruples_anecdotes_rule_converted",
                            "license": LICENSES["scruples"],
                            "post_id": r["post_id"],
                            "post_type": r.get("post_type"),
                            "title": r.get("title", ""),
                            "action_description": (r.get("action") or {}).get("description", ""),
                            "asked_action": "y" if negated else "x",
                            "label": r.get("label"),
                            "label_scores": r.get("label_scores"),
                            "binarized_label_scores": r.get("binarized_label_scores"),
                            **_vote_stats(r.get("label_scores") or {}, r.get("binarized_label_scores") or {}),
                            "n_words": n_words,
                        },
                    )
                )
    return fams


# ---- Berkeley AITA ---------------------------------------------------------------------------------------------

_BK_COLS = ["submission_id", "title", "selftext", "created_utc", "comments_nta_agreement", "comments_yta_agreement", "comments_esh_agreement", "comments_nah_agreement", "reddit_label", "gpt4_label_1", "claude_label_1"]


def _f(x) -> Optional[float]:
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return None if v != v else v


def load_aita_berkeley(csv_path: str | Path, max_chars: int = 1500, min_words: int = 20, human_max_agreement: float = 0.7, require_prior: bool = True, prospective_only: bool = True) -> list[Family]:
    """ucberkeley-dlab CSV -> Family rows. Default (`prospective_only`): WIBTA posts only -- the round-1 hand check
    found retrospective posts narrate a completed deed and its aftermath, so "What should you do?" is incoherent
    (no-verdict pass 62%). With `prospective_only=False`, retrospective posts with a human or LLM disagreement
    prior (max(nta, yta) < human_max_agreement, or gpt4 != claude among {NTA, YTA}) are kept too when
    `require_prior`. The length cap applies to the cleaned second-person situation."""
    import pandas as pd

    df = pd.read_csv(csv_path, usecols=lambda c: c in _BK_COLS)
    fams: list[Family] = []
    for r in df.to_dict("records"):
        acts, aflags, negated, prospective = actions_from_title(str(r.get("title", "")))
        nta, yta = _f(r.get("comments_nta_agreement")), _f(r.get("comments_yta_agreement"))
        g4, cl = str(r.get("gpt4_label_1")), str(r.get("claude_label_1"))
        human_contested = max(nta or 0.0, yta or 0.0) < human_max_agreement
        llm_differ = g4 != cl and g4 in ("NTA", "YTA") and cl in ("NTA", "YTA")
        if prospective_only and not prospective:
            continue
        if require_prior and not (prospective or human_contested or llm_differ):
            continue
        flags = list(aflags)
        sit1, question, cflags = clean_reddit_body(str(r.get("selftext") or ""))
        flags += cflags
        sit2, pflags = first_to_second_person(sit1)
        flags += pflags
        if opens_mid_stream(sit2, "leading_sentence_removed" in cflags):
            flags.append("opens_mid_stream")
        if len(sit2.split()) < min_words:
            flags.append("body_too_short")
        if len(sit2) > max_chars:
            flags.append("body_too_long")
        if detect_person(sit2) != "second":
            flags.append("not_second_person")
        ax, ay = acts if acts else ("Unparsed.", "Unparsed.")
        fams.append(
            Family(
                family_id=f"bk_{r['submission_id']}",
                source="aita_berkeley",
                source_id=str(r["submission_id"]),
                topic_group="aita",
                situation=sit2,
                question_original=first_to_second_person(question)[0] if question else "",
                action_x=ax,
                action_y=ay,
                ambiguity="unknown",
                split=POOL_SPLIT,
                needs_review=sorted(set(flags)),
                meta={
                    "provenance": "aita_berkeley_rule_converted",
                    "license": LICENSES["aita_berkeley"],
                    "submission_id": str(r["submission_id"]),
                    "title": str(r.get("title", "")),
                    "created_utc": str(r.get("created_utc", "")),
                    "prospective": prospective,
                    "asked_action": "y" if negated else "x",
                    "reddit_label": r.get("reddit_label"),
                    "nta": nta,
                    "yta": yta,
                    "esh": _f(r.get("comments_esh_agreement")),
                    "nah": _f(r.get("comments_nah_agreement")),
                    "gpt4_label": g4,
                    "claude_label": cl,
                    "human_contested": human_contested,
                    "llm_differ": llm_differ,
                    "n_chars": len(sit2),
                },
            )
        )
    return fams


# ---- Moral Stories -------------------------------------------------------------------------------------------------

_MALE = {"he", "him", "his", "himself", "he's", "he'd", "he'll"}
_FEMALE = {"she", "her", "hers", "herself", "she's", "she'd", "she'll"}
_MALE_N = {"husband", "boyfriend", "father", "dad", "brother", "son", "man", "guy", "boy", "uncle", "nephew", "grandfather", "grandpa", "stepfather", "fiance", "king", "waiter", "actor", "businessman", "gentleman", "mr", "stepdad", "grandson", "groom", "prince", "dude", "bro"}
_FEMALE_N = {"wife", "girlfriend", "mother", "mom", "sister", "daughter", "woman", "girl", "lady", "aunt", "niece", "grandmother", "grandma", "stepmother", "fiancee", "queen", "waitress", "actress", "businesswoman", "mrs", "ms", "stepmom", "granddaughter", "bride", "princess", "gal"}
_NEUTRAL_SG = {"friend", "boss", "coworker", "colleague", "neighbor", "neighbour", "roommate", "housemate", "teacher", "student", "customer", "clerk", "cashier", "kid", "child", "someone", "somebody", "stranger", "partner", "parent", "cousin", "doctor", "nurse", "officer", "manager", "employee", "client", "classmate", "teammate", "coach", "driver", "owner", "landlord", "tenant", "baby", "toddler", "person", "spouse", "sibling", "relative", "guest", "host", "buddy", "pal", "date", "ex", "professor", "dentist", "vet", "lawyer", "mechanic", "plumber", "babysitter", "twin", "passenger", "shopper", "cop", "supervisor", "assistant", "intern", "candidate", "applicant", "patient", "victim", "teen", "teenager", "infant", "chef", "bartender", "barista", "salesman", "salesperson", "agent", "realtor", "contractor", "worker", "volunteer", "mentor", "tutor", "principal", "dean", "judge", "referee", "umpire", "pastor", "priest", "rabbi", "counselor", "therapist", "visitor", "tourist", "newcomer", "acquaintance", "stepson", "stepdaughter", "stepbrother", "stepsister", "grandparent", "grandchild", "grandkid", "nanny", "caregiver", "secretary", "receptionist", "pharmacist", "surgeon", "soldier", "veteran", "pilot", "attendant", "server", "bully", "mugger", "thief", "robber", "burglar", "hitchhiker", "jogger", "cyclist", "biker", "pedestrian", "homeowner", "fiancé", "fiancée"}
# Round 4 (results/e2c/handcheck_round3_report.md item 1): role nouns beyond the gendered / neutral lists, so that any
# other person introduced by a noun blocks the actor reading of the next actor-gender pronoun.
_MALE_N |= {"jock", "mailman", "postman", "policeman", "fireman", "salesman", "repairman", "handyman", "doorman", "chairman", "boyfriend", "stepson", "stepbrother", "godfather", "godson", "widower", "bachelor", "groomsman", "nephew"}
_FEMALE_N |= {"policewoman", "saleswoman", "chairwoman", "stewardess", "hostess", "landlady", "godmother", "goddaughter", "widow", "bridesmaid", "ballerina", "mistress", "nun"}
_EXTRA_PERSON_N = {
    # people beyond the gendered / neutral lists; verb or adjective homographs (cook, guide, senior) are left out
    "opponent", "rival", "competitor", "challenger", "contender", "champion", "winner", "loser", "player", "gamer", "athlete", "wrestler", "boxer", "golfer", "skateboarder", "goalie", "quarterback", "defenseman", "freshman", "sophomore", "nerd", "geek", "cheerleader", "schoolmate", "flatmate", "dormmate", "roomate",
    "instructor", "lecturer", "librarian", "custodian", "janitor", "headmaster", "advisor", "adviser", "counsellor", "mentee", "protege", "trainee", "apprentice", "interviewer", "interviewee", "recruiter", "employer", "foreman", "subordinate", "ceo", "director", "president", "chairperson", "chairwoman", "entrepreneur", "shareholder", "treasurer", "trustee",
    "banker", "teller", "bookkeeper", "auditor", "inspector", "appraiser", "attorney", "notary", "juror", "defendant", "plaintiff", "suspect", "criminal", "inmate", "prisoner", "convict", "felon", "warden", "bailiff", "marshal", "sheriff", "deputy", "constable", "trooper", "detective", "investigator", "policeman", "policewoman", "firefighter", "paramedic", "medic", "emt", "physician", "pediatrician", "psychiatrist", "psychologist", "optometrist", "orthodontist", "hygienist", "chiropractor", "dietitian", "nutritionist", "midwife", "phlebotomist", "veterinarian", "radiologist", "oncologist", "cardiologist", "dermatologist", "neurologist", "anesthesiologist",
    "pastor", "preacher", "reverend", "imam", "monk", "bishop", "deacon", "parishioner", "congregant", "churchgoer", "atheist", "vegan", "vegetarian",
    "waiter", "busboy", "grocer", "stylist", "hairdresser", "barber", "beautician", "manicurist", "masseuse", "tattooist", "telemarketer", "scammer", "vendor", "patron", "shopper", "trucker", "chauffeur", "valet", "concierge", "bellhop", "butler", "maid", "housekeeper", "gardener", "groundskeeper", "landscaper", "lifeguard", "bouncer", "dj", "emcee", "rapper", "comedian", "magician", "clown", "mime", "juggler", "acrobat", "stuntman", "performer", "singer", "dancer", "musician", "guitarist", "drummer", "artist", "painter", "sculptor", "photographer", "writer", "author", "poet", "novelist", "journalist", "reporter", "blogger", "influencer", "youtuber", "celebrity", "groupie", "critic", "scientist", "chemist", "physicist", "biologist", "mathematician", "engineer", "programmer", "developer", "designer", "architect", "carpenter", "electrician", "technician", "repairman", "farmer", "rancher", "fisherman", "sailor", "sergeant", "cadet",
    "governor", "mayor", "senator", "congressman", "congresswoman", "politician", "diplomat", "ambassador", "consultant", "accountant", "economist", "historian", "philosopher", "organizer", "organiser", "coordinator", "spokesperson", "representative", "activist", "protester", "protestor", "voter", "citizen", "immigrant", "refugee", "foreigner",
    "lover", "crush", "sweetheart", "admirer", "suitor", "bestie", "bff", "companion", "chaperone", "stripper", "prostitute", "hooker", "pimp", "dealer", "junkie", "addict", "alcoholic", "drunkard", "smoker", "drinker", "gambler", "bookie", "stoner", "partier", "slacker", "beggar", "panhandler", "hobo", "squatter", "trespasser", "intruder", "stalker", "harasser", "abuser", "attacker", "assailant", "shooter", "killer", "murderer", "rapist", "molester", "pedophile", "kidnapper", "vandal", "arsonist", "shoplifter", "pickpocket", "scalper", "hacker", "snob", "brat", "bitch", "jerk", "idiot", "moron", "liar", "cheater", "hypocrite", "busybody", "narcissist", "sociopath", "hypochondriac", "schizophrenic", "hero", "heroine", "villain", "angel", "saint", "genius", "prodigy", "bookworm", "workaholic", "perfectionist", "introvert", "extrovert", "newlywed", "widow", "widower", "orphan", "adoptee", "godparent", "godfather", "godmother", "godson", "goddaughter", "mama", "papa", "mommy", "daddy", "mum", "mummy", "granny", "nana", "gramps", "auntie", "stepparent", "stepchild", "stepkid", "halfbrother", "halfsister", "inlaw", "newborn", "preschooler", "kindergartner", "tween", "adolescent", "youngster", "lad", "lass", "fella", "bloke", "chap", "retiree", "pensioner", "grandchild", "helper", "donor", "recipient", "survivor", "traveler", "traveller", "commuter", "motorist", "jaywalker", "conductor", "dispatcher", "paralegal", "newbie", "rookie", "amateur", "beginner", "sensei", "guru", "announcer", "commentator", "passerby", "bystander", "onlooker", "lodger", "subletter", "cabbie", "cabby", "deliveryman", "courier", "messenger", "caller", "texter", "spectator", "attendee", "participant", "contestant", "entrant", "nominee", "honoree", "awardee", "undergrad", "postdoc", "researcher", "prof", "provost", "chancellor", "registrar", "proctor", "examiner", "educator", "optician", "barkeep", "salesclerk", "shopkeeper", "storekeeper", "merchant", "wholesaler", "retailer", "supplier", "subcontractor", "locksmith", "welder", "roofer", "exterminator", "groomer", "breeder", "zookeeper", "jockey", "horseman", "cowboy", "cowgirl", "outlaw", "bandit", "pirate", "warrior", "knight", "informant", "hostage", "captive", "fugitive", "chum", "workmate", "bandmate", "triplet", "kinsman", "ancestor", "descendant", "heir", "heiress", "beneficiary", "executor", "tycoon", "mogul", "millionaire", "billionaire", "co-worker", "mailman", "postman", "handyman", "doorman", "chairman", "stewardess", "hostess", "landlady", "ballerina", "mistress", "nun", "jock", "fighter", "exterminator", "someone", "somebody", "anyone", "anybody", "nobody", "everyone", "everybody",
}
_PERSON_N = _MALE_N | _FEMALE_N | _NEUTRAL_SG | _EXTRA_PERSON_N  # any singular noun that can be the antecedent of he / she
# Capitalised tokens that are not people (brands, places, days, holidays, nationalities, interjections): never block
# the actor reading. Everything else that is Title-cased and not a dictionary word is a name (pets included).
_CAP_NOT_PERSON = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december", "christmas", "xmas", "halloween", "thanksgiving", "easter", "hanukkah", "valentine", "valentines", "fourth", "new", "year", "years", "eve", "day", "birthday", "party", "night", "weekend", "spring", "summer", "fall", "winter",
    "facebook", "netflix", "uber", "lyft", "twitter", "amazon", "reddit", "tinder", "bumble", "instagram", "snapchat", "tiktok", "disney", "walmart", "target", "costco", "xbox", "playstation", "nintendo", "switch", "wii", "craigslist", "ebay", "subway", "lego", "starbucks", "apple", "iphone", "android", "google", "youtube", "yelp", "goodwill", "skype", "zoom", "monopoly", "peleton", "peloton", "gameboy", "porsche", "toyota", "honda", "ford", "tesla", "bmw", "prime", "internet", "wifi", "covid", "coronavirus", "adderall", "xanax", "advil", "tylenol", "valium", "oxycontin", "alzheimer", "alzheimers", "syndrome", "math", "algebra", "calculus", "english", "spanish", "french", "german", "italian", "chinese", "japanese", "korean", "russian", "arabic", "latin", "science", "biology", "chemistry", "physics", "history", "art", "music", "gym", "pe",
    "american", "jewish", "indian", "asian", "muslim", "african", "mexican", "nigerian", "native", "black", "white", "republican", "democrat", "democratic", "mormon", "nazi", "jews", "mexicans", "americans", "catholic", "christian", "hindu", "buddhist", "jew", "latino", "latina", "hispanic", "european", "canadian", "british", "irish", "australian", "muslims", "christians",
    "vegas", "las", "paris", "world", "york", "united", "states", "europe", "hawaii", "harvard", "yale", "stanford", "america", "california", "texas", "florida", "thailand", "miami", "mexico", "germany", "china", "india", "canada", "france", "honduras", "navy", "army", "london", "chicago", "boston", "seattle", "denver", "atlanta", "dallas", "houston", "orlando", "nyc", "la", "dc", "earth", "mars",
    "god", "santa", "claus", "bible", "quran", "koran", "torah", "trump", "hitler", "obama", "biden", "hey", "hi", "hello", "no", "yes", "it", "you", "my", "happy", "down", "up", "master", "mechanical", "regional", "manager", "services", "call", "duty", "wars", "war", "animal", "high", "grand", "lives", "matter", "dungeons", "dragons", "fahrenheit", "alma", "mater", "fools", "reform", "anime", "bike", "donkey", "mint", "private", "miss", "mr", "mrs", "ms", "dr", "ok", "okay", "oh", "wow", "well", "please", "thanks", "sorry", "thank", "yeah", "yep", "nope", "hmm", "um", "uh", "ugh", "aw", "aww", "yay", "oops", "ouch", "congratulations", "congrats", "merry", "good", "great", "nice", "fine", "sure", "maybe", "also", "then", "now", "so", "but", "and", "or", "if", "when", "while", "after", "before", "because", "since", "as", "at", "in", "on", "of", "for", "with", "from", "to", "by", "about", "the", "a", "an", "this", "that", "these", "those", "there", "here", "he", "she", "they", "we", "i", "his", "her", "their", "our", "your", "its", "him", "them", "us", "me", "one", "every", "each", "some", "all", "no", "none", "today", "tomorrow", "yesterday", "tonight", "later", "once", "first", "last", "next", "being", "having", "going", "getting", "not", "even", "just", "still", "already", "never", "always", "often", "sometimes", "usually", "recently", "lately", "suddenly", "unfortunately", "luckily", "however", "instead", "meanwhile", "although", "though", "unless", "until", "whenever", "wherever", "whether", "what", "which", "who", "whom", "whose", "how", "why", "where", "someone", "somebody", "everyone", "everybody", "nobody", "anyone", "anybody", "people", "men", "women", "both", "neither", "either", "most", "many", "much", "more", "less", "few", "several", "another", "other", "others", "such", "same", "very", "too", "quite", "rather", "pretty", "really", "mom", "dad", "mother", "father", "aunt", "uncle", "grandma", "grandpa", "grandmother", "grandfather", "coach", "doctor", "nurse", "officer", "professor", "pastor", "father", "sister", "brother",  # titles: handled as role nouns
}
# Round 4 item 3: unapostrophised contractions in the Moral Stories fields (case-insensitive, initial capital kept).
_UNAPOSTROPHISED = [(re.compile(rf"\b{a}\b", re.IGNORECASE), b) for a, b in [("shes", "she's"), ("hes", "he's"), ("theyre", "they're"), ("youre", "you're"), ("im", "I'm"), ("ive", "I've"), ("dont", "don't"), ("doesnt", "doesn't"), ("didnt", "didn't"), ("isnt", "isn't"), ("wasnt", "wasn't"), ("arent", "aren't"), ("werent", "weren't"), ("cant", "can't"), ("couldnt", "couldn't"), ("wouldnt", "wouldn't"), ("shouldnt", "shouldn't"), ("hasnt", "hasn't"), ("havent", "haven't"), ("hadnt", "hadn't"), ("thats", "that's"), ("whats", "what's"), ("theres", "there's")]]
# Round 4 item 6: a plural pronoun followed by a togetherness phrase in a clause whose subject is 'you' = actor + others.
_GROUP_PHRASE = re.compile(r"\b(as a (?:family|couple|group|team|unit|pair|duo|trio)|together|the two of (?:you|them)|both of (?:you|them)|the (?:two|three|four) of (?:you|them)|all of you)\b", re.IGNORECASE)
# Round 4 item 5: stative main-clause heads of a Moral Stories action that no imperative can be made from.
_MS_STATIVE_VBZ = {"has", "had", "lives", "feels", "knows", "owns", "seems", "remains", "exists", "lacks", "resembles", "belongs", "weighs", "equals", "matters"}
_DEGREE_ADV = {"very", "really", "so", "too", "extremely", "quite", "pretty", "super", "incredibly", "rather", "somewhat", "totally", "completely", "absolutely", "fairly", "overly", "more", "most", "less", "much", "always", "never", "usually", "often", "sometimes", "constantly", "only", "just", "still", "already", "now", "also", "simply", "generally", "a"}
_EMBEDDED_VBZ = {"tastes", "looks", "smells", "sounds", "feels", "seems", "costs", "fits", "belongs", "matters", "hurts", "needs", "wants", "deserves", "lacks"}  # 'the food tastes wonderful and is ...': the noun owns the next verb
_SUB_3SG_SUBJ = {"he", "she", "it", "someone", "somebody", "everyone", "everybody", "nobody", "anyone", "anybody", "one", "this", "that", "there", "who", "which"}

_PLURAL = {"friends", "coworkers", "colleagues", "neighbors", "neighbours", "roommates", "teachers", "students", "customers", "kids", "children", "people", "parents", "family", "relatives", "siblings", "guests", "classmates", "teammates", "employees", "clients", "passengers", "workers", "others", "everyone", "everybody", "they", "them", "their", "group", "crowd", "team", "class", "couple", "twins", "guys", "girls", "boys", "men", "women", "folks"}
# plural / collective nouns that can be the antecedent of 'they' / 'their' (people, animals, groups); inanimate plurals
# ('things', 'walls') cannot, so 'their relationship' after only 'things' means the actor plus someone
_ANIMATE_PL = {"inlaws", "exes", "cops", "fans", "bosses", "ladies", "babies", "bullies", "adults", "humans", "citizens", "hosts", "pets", "animals", "cousins", "brothers", "sisters", "daughters", "sons", "aunts", "uncles", "nieces", "nephews", "husbands", "wives", "girlfriends", "boyfriends", "partners", "spouses", "grandkids", "grandchildren", "stepkids", "housemates", "bandmates", "buddies", "pals", "peers", "triplets", "gentlemen", "ladies", "lads", "fellas", "dudes", "bros", "ex", "staff", "police", "faculty", "management", "administration"}
_GROUP_N = {"family", "couple", "team", "class", "group", "crowd", "staff", "crew", "band", "club", "committee", "company", "school", "church", "congregation", "jury", "gang", "choir", "orchestra", "cast", "public", "government", "board", "council", "union", "army", "herd", "flock", "pack", "audience", "community", "neighborhood", "neighbourhood", "department", "office", "firm", "restaurant", "store", "shop", "hospital", "squad", "household", "generation", "mob", "duo", "trio", "pair", "clinic", "bank", "hotel", "airline", "charity", "organization", "organisation", "association", "league", "society", "tribe", "clan", "troop", "unit", "faculty", "management", "administration", "police"}
_ANIMAL_N = {"cat", "dog", "puppy", "kitten", "bird", "horse", "cow", "pig", "hamster", "rabbit", "bunny", "fish", "snake", "lizard", "turtle", "parrot", "goat", "sheep", "duck", "chicken", "mouse", "rat", "squirrel", "deer", "bear", "wolf", "fox", "pet", "animal", "pony", "goose", "bee", "ant", "spider", "frog", "monkey", "lion", "tiger", "elephant", "cub", "calf", "lamb", "foal", "chick", "pup", "gerbil", "ferret", "parakeet", "canary", "pigeon", "crow", "raccoon", "skunk", "possum", "opossum", "coyote", "moose", "elk", "bat", "owl", "hawk", "eagle", "stray"}
_ADV = {"also", "often", "now", "then", "just", "always", "never", "usually", "still", "even", "really", "simply", "later", "instead", "first", "again", "already", "sometimes", "frequently", "regularly", "occasionally", "soon", "once", "twice", "immediately", "finally", "eventually", "secretly", "politely", "quietly", "quickly", "calmly", "gently", "carefully", "happily", "angrily", "rudely", "honestly", "kindly", "promptly", "loudly", "sternly", "firmly", "reluctantly", "excitedly", "nervously", "casually", "openly", "privately", "publicly", "briefly", "actually", "generously", "graciously", "gracefully", "warmly", "coldly", "bluntly", "directly", "discreetly"}
_NOT_ADV_LY = {"family", "only", "early", "daily", "holy", "ugly", "lonely", "fly", "rely", "apply", "reply", "supply", "bully", "rally", "tally", "ally", "belly", "jelly", "silly", "chilly", "smelly", "lovely", "friendly", "likely", "costly", "deadly", "elderly", "lively", "lowly", "monthly", "weekly", "yearly", "hourly", "nightly", "orderly", "kindly", "assembly"}
_COORD = {"and", "but", "or", "then", "so"}
# words that cannot start the noun phrase of a determiner 'his' / 'her' (so the pronoun is an object or standalone)
_POSS_BLOCK = {"to", "that", "a", "an", "the", "about", "for", "with", "from", "into", "on", "at", "of", "as", "by", "in", "up", "out", "off", "down", "over", "back", "away", "here", "there", "again", "whether", "if", "how", "what", "when", "where", "why", "too", "instead", "alone", "and", "or", "but", "because", "while", "so", "is", "was", "has", "had", "will", "would", "can", "could", "should", "not", "this", "these", "those", "some", "any", "very", "then", "after", "before", "until", "since", "though", "although", "unless", "once", "than", "like", "through", "without", "around", "under", "toward", "towards", "onto", "upon", "yet", "still", "also", "just", "only", "even", "now", "soon", "later", "today", "tomorrow", "yesterday"}
# 'her first / last / next ...' is a determiner when another word follows ('her last day'), an object otherwise ('told her first')
_POSS_ORDINAL = {"first", "last", "next", "best", "other", "favorite", "favourite", "usual", "current", "former", "only"}
# 'his' is a standalone pronoun ('a friend of his', 'his too') only before one of these or before punctuation
_HIS_STANDALONE_NEXT = {"and", "or", "but", "too", "instead", "is", "was", "as", "than", "also", "while", "because", "so", "if", "when", "though", "although", "either", "anyway", "alone", "again", "yet", "still", "now", "then", "here", "there", "away", "with", "to", "for", "from", "on", "in", "at", "of", "by", "into", "onto"}
_SUBORD = {"when", "while", "because", "if", "who", "whom", "whose", "that", "which", "whenever", "after", "before", "until", "as", "since", "where", "although", "though", "unless", "how", "what", "why", "whether", "whatever", "whoever"}
_SUBJ_PRON = {"he", "she", "it", "they", "there", "this", "that", "someone", "somebody", "everyone", "everybody", "nobody", "one", "people", "i", "we"}
_PARTICLES = {"up", "out", "off", "down", "away", "back", "over", "along", "around", "through", "aside", "ahead", "forward", "together", "apart", "home"}
# prepositions whose object cannot be the clause subject ('you swipe at him'); comitative / locative ones can
# ('you take William with you', 'next to you') and are left out on purpose
_OBJ_PREP_OK = {"at", "to", "for", "about", "from", "of", "against", "toward", "towards", "after", "than", "like", "without", "into", "onto", "upon", "off", "past"}
_PREPS = {"at", "to", "for", "about", "from", "of", "against", "toward", "towards", "after", "than", "like", "without", "into", "onto", "upon", "with", "on", "in", "by", "before", "while", "despite", "besides", "instead"}
_DETS = {"a", "an", "the", "his", "her", "their", "your", "my", "its", "this", "that", "these", "those", "some", "any", "another", "every", "each", "one", "two", "several", "many", "few", "all", "both", "no"}
_PERSON_WORDS = {"him", "her", "them", "you", "me", "us", "everyone", "everybody", "someone", "somebody", "anyone", "anybody", "nobody", "people", "others", "himself", "herself", "yourself", "themselves"}
_AUX = {"is", "was", "are", "were", "will", "would", "can", "could", "should", "has", "have", "had", "do", "does", "did", "might", "may", "must", "doesn't", "isn't", "wasn't", "hasn't", "don't", "didn't", "won't", "can't", "aren't", "weren't", "it'll", "it's", "they're", "they'll", "they've", "they'd", "that's", "there's", "what's", "who's"}
_SUBJ_RESET = {"it", "they", "there", "this", "people", "we", "i", "it'll", "it's", "they're", "they'll", "they've", "they'd", "that's", "there's", "what's", "who's"}
# the object of these cannot be ruled out as the subject ('next to him', 'in front of him', 'across from him')
_LOC_PREPS = {"near", "next", "beside", "behind", "with", "by", "on", "in", "under", "over", "above", "below", "between", "among", "across", "opposite", "alongside", "inside", "outside", "front", "top", "side", "back", "ahead", "close", "beneath", "underneath", "along"}
_GERUND_SUBJ_PREPS = {"for", "about", "from", "of", "on", "at", "in", "into"}  # 'thank the host for having him': the gerund's subject is the object before the preposition
_CAUSATIVES = {"help", "helps", "let", "lets", "make", "makes", "watch", "watches"}
_REL_OBJ_NEXT = {"him", "her", "them", "you", "me", "us", "the", "a", "an", "his", "their", "your", "my", "its", "this", "that", "these", "those", "everyone", "someone", "people", "all", "at", "to", "for", "with", "about", "toward", "towards"} | _PARTICLES
_BARE_INF = {"go", "come", "do", "see", "know", "feel", "be", "get", "take", "have", "lift", "carry", "pick", "clean", "finish", "leave", "stay", "sit", "stand", "move", "try", "cry", "laugh", "sleep", "eat", "drink", "play", "work", "study", "pay", "buy", "drive", "walk", "run", "talk", "speak", "read", "write", "use", "keep", "hold", "put", "find", "look", "think", "understand", "learn", "win", "lose", "fix", "cook", "wash", "open", "close", "choose", "decide", "wait", "stop", "start", "continue", "quit"}
_TOK = re.compile(r"[A-Za-z']+|[^A-Za-z']+")
_NEG_MAP = {"doesn't": "don't", "isn't": "aren't", "wasn't": "weren't", "hasn't": "haven't", "is": "are", "has": "have", "was": "were", "does": "do"}
_NEG_AUX = {"doesn't", "isn't", "wasn't", "hasn't"}
# Words that lemminflect does not list but that are ordinary English, so that a sentence-initial capital is not a name.
_COMMON_CAPS_OK = _CAP_NOT_PERSON | _SUBORD | _COORD | _DETS | _PREPS | _AUX | _ADV | _SUBJ_PRON | _PARTICLES | _NOT_VERB_HEAD | _POSS_BLOCK | _PERSON_WORDS
_NEG_NORM = re.compile(
    r"\b(wrong|bad|rude|mean|cruel|hurtful|selfish|immoral|illegal|irresponsible|disrespectful|inappropriate|unacceptable|"
    r"shouldn't|should not|not okay|not ok|don't|do not|never|unkind|inconsiderate|unfair|dishonest|harmful|unethical|"
    r"unhealthy|dangerous|disgusting|gross|terrible|awful|frowned|hurt|lie|cheat|steal)\b",
    re.IGNORECASE,
)


def norm_polarity(norm: str) -> str:
    """'It's wrong to ...' -> negative (a prohibition); 'It's kind to ...' -> positive (a recommendation)."""
    return "negative" if _NEG_NORM.search(norm or "") else "positive"


def _lemma(w: str) -> Optional[str]:
    try:
        from lemminflect import getLemma

        lem = getLemma(w.lower(), upos="VERB")
        return lem[0] if lem else None
    except Exception:
        return None


def _all_lemmas(w: str) -> dict:
    try:
        from lemminflect import getAllLemmas

        return getAllLemmas(w.lower())
    except Exception:
        return {}


def _is_vbz(w: str) -> bool:
    lw = w.lower()
    if lw in _NEG_MAP:
        return True
    try:
        from lemminflect import getAllInflections

        lem = _lemma(lw)
        if not lem or lem == lw:
            return False
        return lw in getAllInflections(lem, upos="VERB").get("VBZ", ())
    except Exception:
        return lw.endswith("s") and not lw.endswith("ss")


def _is_extra_vbz(w: str) -> bool:
    """'texts', 'venmos': 3sg forms of verbs lemminflect does not know; only trusted right after a subject 'you'."""
    lw = w.lower()
    return lw.endswith("s") and (lw[:-1] in _EXTRA_VERBS or (lw.endswith("es") and lw[:-2] in _EXTRA_VERBS))


def _vbz_to_base(w: str) -> str:
    lw = w.lower()
    extra = lw[:-1] if lw.endswith("s") and lw[:-1] in _EXTRA_VERBS else lw[:-2] if lw.endswith("es") and lw[:-2] in _EXTRA_VERBS else None
    out = _NEG_MAP.get(lw) or extra or _lemma(lw) or lw
    return _cap(out) if w[0].isupper() else out


def _is_adv(w: str) -> bool:
    if w[:1].isupper() and w.lower() not in _ADV:
        return False
    lw = w.lower()
    return lw in _ADV or (lw.endswith("ly") and lw not in _NOT_ADV_LY)


def _is_gerund(w: str) -> bool:
    lw = w.lower()
    if not lw.endswith("ing") or lw in _ING_NOT_GERUND_LOCAL:
        return False
    lem = _all_lemmas(lw).get("VERB")
    return bool(lem) and lem[0] != lw


def _verb_like(w: str) -> bool:
    """A word that continues the same subject's predicate after 'and' (verb, adverb or negation), not a new subject."""
    lw = w.lower()
    if lw in {"not", "then", "also", "you"} or lw in _NEG_MAP or _is_adv(w) or _is_vbz(w) or _is_gerund(w):
        return True
    return bool(is_base_verb(w)) and not w[:1].isupper()


def _actor_of(r: dict) -> Optional[str]:
    m = re.match(r"^([A-Z][a-z]+)(?:'s)?\b", (r.get("intention") or "").strip())
    return m.group(1) if m else None


def _name_genders(rows: list[dict]) -> tuple[Counter, dict[str, str]]:
    actors = Counter(a for a in (_actor_of(r) for r in rows) if a)
    cnt: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for r in rows:
        n = _actor_of(r)
        if not n:
            continue
        for w in re.findall(r"[a-z']+", " ".join([r["situation"], r["intention"], r["moral_action"], r["immoral_action"]]).lower()):
            if w in _MALE:
                cnt[n][0] += 1
            if w in _FEMALE:
                cnt[n][1] += 1
    genders = {n: ("m" if m > f else "f") for n, (m, f) in cnt.items() if m + f >= 3 and max(m, f) / (m + f) >= 0.75}
    return actors, genders


_APPOSITIVE_HEADS = sorted(_MALE_N | _FEMALE_N | _NEUTRAL_SG, key=len, reverse=True)


_APPOS_MARK = "\x01"  # marks the possessor of a rewritten appositive ('his friend' = somebody else's), never converted


def _actor_appositive(text: str, actor: str) -> tuple[str, bool]:
    """'hissing at Jeff's friend Murray who ...' -> 'hissing at Murray, Jeff's friend, who ...' so that the actor's name
    can become 'you' without leaving 'Jeff's friend you'. Only possessive-headed appositives are rewritten; a pronoun
    possessor ('his friend Luke') belongs to the other person and is marked so the person pass leaves it alone."""
    pat = re.compile(rf"\b((?:[A-Z][a-z]+'s|[Hh]is|[Hh]er|[Tt]heir)\s+(?:[a-z]+\s+)?(?:{'|'.join(_APPOSITIVE_HEADS)}))\s+{re.escape(actor)}\b(?!'s)")

    def rep(m: re.Match) -> str:
        g = m.group(1)
        head = g.split()[0]
        if head in {"His", "Her", "Their"}:
            g = g[0].lower() + g[1:]
        if head.lower() in {"his", "her", "their"}:
            g = _APPOS_MARK + g
        return f"{actor}, {g},"

    out, n = pat.subn(rep, text)
    out = re.sub(r",\s*,", ",", out)
    out = re.sub(r",\s*([.!?;])", r"\1", out)
    return out, n > 0


def _noun_before_to(pw: str, before: str) -> bool:
    """Does `pw` read as a plural noun in 'V ... <pw> to V' ('sleeping pills to help her', 'videos on YouTube to help
    her')? A 3sg verb homograph ('goes to', 'wants to') counts only after a modifier or a noun-only word."""
    lem = _all_lemmas(pw)
    nouns = lem.get("NOUN", ())
    if not (pw.endswith("s") and nouns and nouns[0] != pw):
        return False
    if not (lem.get("VERB") and _is_vbz(pw)):
        return True
    before_lem = _all_lemmas(before)
    return before in _PLURAL_LICENSERS or before in _PARTICLES or before.endswith("ing") or _is_vbz(before) or bool(before_lem.get("NOUN") and not before_lem.get("VERB"))


def _object_np(words: list[str], pos: int) -> bool:
    """Is the noun at `pos` inside an object noun phrase ('with the visitor', 'tells his friend Luke')? Looks back over
    determiners / adjectives for an object cue; a verb or a clause boundary first means it is not."""
    for j in range(pos - 1, max(-1, pos - 4), -1):
        w = words[j]
        if w in _OBJECT_CUES:
            return True
        if w in _COORD or w in _SUBORD or w in {"you", "he", "she", "it", "they"} or _is_vbz(w) or w.endswith("ing"):
            return False
    return False


_TEMPORAL_SUBORD = {"after", "before", "until", "since", "while", "as"}


def _subord_is_clause(words: list[str], k: int, actor: str = "") -> bool:
    """Does the temporal word at `k` head a clause ('until the dog falls asleep', 'after he left', 'while cleaning')
    rather than a PP ('after work', 'after a long day at work')? A clause shows a subject pronoun / name right after it
    or a finite verb before the next coordinator (six tokens at most)."""
    if k + 1 >= len(words):
        return False
    n1 = words[k + 1]
    if n1 in _SUBJ_PRON or n1 in _MALE or n1 in _FEMALE or n1 in _INDEFINITE or n1 == "you" or n1 == actor.lower() or _is_gerund(n1):
        return True
    for j in range(k + 1, min(len(words), k + 7)):
        w = words[j]
        if w in _COORD or w in _SUBORD:
            return False
        if w in _AUX or w in {"will", "would", "can", "could", "should", "might", "may", "must", "was", "were", "had"} or _is_vbz(w):
            return True
        lem = _lemma(w)
        if lem and lem != w and not w.endswith("s") and not _is_gerund(w) and (w.endswith("ed") or not _all_lemmas(w).get("NOUN")):
            return True  # a past-tense verb: 'after he left', 'after the game ended'
    return False


def _is_name_token(t: str, sent_start: bool, actor: str, other_lower: set[str]) -> bool:
    """Round 4 item 1: a Title-cased token that is not the actor, not a known non-person capital (brand, place, day)
    and not a role noun reads as another person's name, pets included. Sentence-initially only when it is a known
    actor name or not an English word ('Lloyd, who is barehanded' yes; 'When Jenna got home' no)."""
    if len(t) < 2 or not (t[0].isupper() and t[1:].islower()) or t == actor:
        return False
    lw = t.lower()
    if lw in _CAP_NOT_PERSON or lw in _PERSON_N:
        return False
    if lw in other_lower:
        return True
    if not sent_start:
        return True
    return lw not in _COMMON_CAPS_OK and not _all_lemmas(lw)


def _animate_plural_lemmas(text: str) -> set[str]:
    """Lemmas of the people / animal / group plurals in `text` ('coworkers' -> 'coworker'), for the singular-their rule."""
    toks = re.findall(r"[A-Za-z]+", text.replace("in-laws", "inlaws").replace("co-workers", "coworkers"))
    out: set[str] = set()
    for j, w in enumerate(toks):
        sg = _plural_noun(w, toks[j - 1].lower() if j else "")
        if sg is not None and _animate_plural(w, sg):
            out.add(sg)
    return out


def _relation_noun_after(words: list[str], pos: int) -> Optional[str]:
    """The relation noun that 'their' at `pos` determines ('their coworkers', 'their best friend', 'their own family'),
    as a singular lemma, or None."""
    j = pos + 1
    while j < len(words) and j < pos + 3 and (words[j] in _POSS_ORDINAL or words[j] in {"own", "new", "old", "older", "younger", "little", "big", "close", "good", "dear", "late", "elderly", "young", "sick", "estranged"}):
        j += 1
    if j >= len(words):
        return None
    w = words[j]
    if w in _PERSON_N:
        return w
    if w in _GROUP_N and w in {"family", "team", "class", "household"}:
        return w
    sg = _plural_noun(w, words[j - 1])
    if sg is not None and (sg in _PERSON_N or w in _PLURAL or w in _ANIMATE_PL) and w not in {"others", "people", "everyone", "everybody", "they", "them", "their"}:
        return sg
    return None


def _possessive_without_noun(text: str) -> bool:
    """Round 4 item 4: every 'your' must be followed by a noun phrase ('Your found out' is a mis-mapped subject) and no
    'yours' may be followed by a noun ('yours back yard')."""
    toks = _TOK.findall(text)
    widx = [i for i, t in enumerate(toks) if re.match(r"^[A-Za-z']+$", t)]
    for pos, i in enumerate(widx):
        lw = toks[i].lower()
        if lw not in ("your", "yours"):
            continue
        if pos + 1 >= len(widx) or toks[i + 1 : widx[pos + 1]] and "".join(toks[i + 1 : widx[pos + 1]]).strip():
            if lw == "your":
                return True  # 'your.' / 'your,' : nothing follows
            if pos + 1 < len(widx) and re.search(r"\d", "".join(toks[i + 1 : widx[pos + 1]])):
                return True  # 'yours 3 dollar win'
            continue
        n = toks[widx[pos + 1]].lower()
        lem = _all_lemmas(n)
        if lw == "your":
            if n in _AUX or n in _PREPS or n in _COORD or n in _SUBORD or n in _DETS or n in _SUBJ_PRON or n in _PERSON_WORDS or n in {"i", "you", "he", "she", "we", "they", "it", "your", "yours"}:
                return True
            if lem.get("VERB") and not lem.get("NOUN") and not lem.get("ADJ") and not lem.get("ADV") and (any(l != n for l in lem["VERB"]) or _is_vbz(n)) and not n.endswith("ing"):
                return True  # 'your found', 'your goes': an inflected verb, not a noun phrase
        else:
            if (lem.get("NOUN") or lem.get("ADJ")) and not _is_adv(n) and n not in _COORD and n not in _AUX and n not in _PREPS and n not in _SUBORD and n not in _DETS and n not in _PARTICLES - {"back"} and n not in {"truly", "too", "alone", "forever", "now", "then", "again", "instead", "anyway", "first", "last", "next", "later", "soon", "today", "tomorrow", "tonight", "yesterday", "though", "either", "neither", "yet", "still", "even", "only", "just", "more", "most", "less", "much", "enough", "well", "right", "away"}:
                return True  # 'yours back yard' / 'yours 3 dollar win'
    return False


@dataclass
class _RowCtx:
    """What the whole Moral Stories row says, for the field-level passes (round 4).
    has_other: anybody (or any animal) besides the actor is mentioned anywhere in the row; when False a kept object
        pronoun is a sloppy reflexive ('to keep him motivated') and the row is flagged.
    row_others: genders ('m' / 'f' / 'n') of the other people named anywhere in the row; an actor-gender pronoun in a
        clause whose subject is not certainly the actor is ambiguous when one of them could be its antecedent.
    plurals: animate plural lemmas of the text before this field (situation for the intention and the actions), for
        the singular-their rule."""

    has_other: bool = True
    row_others: frozenset = frozenset()
    plurals: frozenset = frozenset()


_INDEFINITE = {"anyone", "anybody", "nobody", "everyone", "everybody"}  # generic quantifiers; 'someone' / 'somebody' do introduce a person
_COPULA = {"is", "was", "am", "are", "were", "be", "been", "being", "become", "became", "becomes", "remain", "remains", "remained", "as"}
_PRED_ADJ_OK = {"a", "an", "the", "good", "bad", "great", "new", "old", "young", "single", "former", "fellow", "best", "close", "high", "school", "college", "very", "really", "pretty", "quite", "longtime", "long", "time", "big", "little", "proud", "devoted", "loving", "hard", "working", "full", "part", "first", "second", "year", "grade", "junior", "senior", "stay", "at", "home", "working", "retired", "busy", "struggling", "successful", "popular", "lonely", "shy", "nervous", "strict", "kind", "patient"}


def _actor_predicate(words: list[str], pos: int) -> bool:
    """'<Actor> is a high school teacher' / 'is a 4th grader' / 'you, who are a nurse': the role noun at `pos` describes
    the clause subject (the caller checks that this is the actor), so it is not another person."""
    q = pos - 1
    while q >= 0 and q >= pos - 6 and words[q] not in _COPULA and (words[q] in _PRED_ADJ_OK or words[q] in _DETS or words[q] == "and" or re.match(r"^\d", words[q]) or (words[q] not in _AUX and words[q] not in _PREPS and words[q] not in _COORD and words[q] not in _SUBORD and words[q] not in _MALE and words[q] not in _FEMALE and words[q] != "you" and not _is_vbz(words[q]) and not _is_gerund(words[q]) and not words[q].endswith("ed"))):
        q -= 1
    return q >= 0 and words[q] in _COPULA


def _person_pass(text: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str], flags: list[str], pre: str, imperative: bool = False, ctx: Optional[_RowCtx] = None) -> str:
    """Actor name and the actor's third-person pronouns -> second person. `subj` tracks who is the subject of the
    current clause when that is certain (the actor, as a name or converted pronoun; always in an imperative action):
    an object 'him' / 'her' in such a clause cannot be the actor ('you swipe at him'), so it is kept and the row
    remembers another same-gender person was mentioned. Round 4: `others_seen` collects the genders ('m' / 'f' / 'n',
    plus 'animal') of every other person introduced earlier in this field by a role noun or a Title-cased non-actor
    name; an actor-gender pronoun is a hard flag, never a rewrite, when a same- or unknown-gender other was seen, or
    when the clause subject is not certainly the actor and the row names such a person elsewhere (`ctx.row_others`).
    `last` is the most recent other person, used to resolve an unknown gender from a later opposite-gender pronoun
    ('Penelope ... her house')."""
    text, appos = _actor_appositive(text, actor)
    if appos:
        flags.append(f"{pre}actor_appositive")
    toks = _TOK.findall(text)
    widx = [i for i, t in enumerate(toks) if re.match(r"^[A-Za-z']+$", t)]
    protected = {i for i in widx if toks[i - 1].endswith(_APPOS_MARK)} if appos else set()
    words = [toks[i].lower() for i in widx]
    other_lower = {n.lower() for n in other_names}
    ctx = ctx or _RowCtx()
    name_gender = dict(name_gender)  # extended locally: 'his wife, Mia' tells us Mia is f
    last = "actor"
    others_seen: set[str] = set()
    subj: Optional[str] = "actor" if imperative else None
    plural_seen: set[str] = set(ctx.plurals)
    cap_block = False  # the previous Title-cased token was not a name ('the Kentucky Derby'): nor is this one
    appos_zone = False  # inside '<Actor>, an accountant, ...': the role nouns describe the actor
    appos_start = -1
    for pos, i in enumerate(widx):
        t = toks[i]
        lw = t.lower()
        if i in protected:
            if lw in ("his", "her"):
                last = "m" if lw == "his" else "f"
                others_seen.add(last)
            continue
        nxt = toks[widx[pos + 1]] if pos + 1 < len(widx) else ""
        sep_next = "".join(toks[i + 1 : widx[pos + 1]]) if pos + 1 < len(widx) else ""
        adjacent = pos + 1 < len(widx) and sep_next.strip() == ""
        hyphen_compound = pos + 2 < len(widx) and "".join(toks[widx[pos + 1] + 1 : widx[pos + 2]]) == "-"
        nxt2_adjacent = pos + 2 < len(widx) and "".join(toks[widx[pos + 1] + 1 : widx[pos + 2]]).strip() == ""
        nxt2 = toks[widx[pos + 2]].lower() if pos + 2 < len(widx) else ""
        prev = words[pos - 1] if pos > 0 else ""
        pprev_w = words[pos - 2] if pos > 1 else ""
        prev_nonspace = next((toks[j].strip() for j in range(i - 1, -1, -1) if toks[j].strip()), "")
        sent_start = i == 0 or prev_nonspace == "" or prev_nonspace.endswith((".", "!", "?"))
        if sent_start and pos > 0:
            subj = None
        if lw in _SUBORD:
            clause = (nxt[:1].isupper() and nxt[1:].islower() and nxt.lower() not in _CAP_NOT_PERSON) or _subord_is_clause(words, pos, actor)
            if not (lw in _TEMPORAL_SUBORD and not clause) or (lw == "while" and pos + 1 < len(widx) and _is_gerund(nxt)):
                if not (lw in _TEMPORAL_SUBORD and pos + 1 < len(widx) and _is_gerund(nxt)):
                    subj = None  # a subordinate clause; 'after work' / 'after a long day' are PPs and keep the subject; 'while cleaning his house' keeps the actor too
            continue
        if lw in _COORD:
            coord_actor_pron = subj == "actor" and pos + 1 < len(widx) and nxt.lower() in {"he", "she", "he's", "she's"} and (("m" if nxt.lower() in _MALE else "f") == gender) and not (others_seen & {gender, "n"})
            if not (pos + 1 < len(widx) and (_verb_like(nxt) or coord_actor_pron)):
                subj = None  # '..., and she goes home' after an actor-subject clause with nobody else around stays the actor's
            continue
        if appos_zone and pos > appos_start and "," in "".join(toks[widx[pos - 1] + 1 : i]):
            appos_zone = False
        if t == actor or t == actor + "'s":
            if not t.endswith("'s") and sep_next.strip() == "," and nxt.lower() in {"a", "an", "the"} | _PRED_ADJ_OK:
                appos_zone, appos_start = True, pos + 1
            if t.endswith("'s"):
                n = nxt.lower()
                # "<Actor>'s eating a snack" = is (progressive); "<Actor>'s spending habits" = possessive + compound
                progressive = _is_gerund(n) and (not nxt2 or not nxt2_adjacent or nxt2 in _DETS or nxt2 in _PREPS or nxt2 in _PERSON_WORDS or nxt2 in _COORD or nxt2 in _SUBORD or nxt2 in _PARTICLES or _is_adv(nxt2) or nxt2 == "not")
                vl = _all_lemmas(n)
                perfect = adjacent and bool(vl.get("VERB")) and not vl.get("NOUN") and not vl.get("ADJ") and not vl.get("ADV") and any(l != n for l in vl["VERB"]) and not n.endswith("ing") and not _is_vbz(n)
                if adjacent and (progressive or n in {"a", "an", "the", "not", "very", "so", "too", "about", "at", "in", "on", "always", "never", "really"}):
                    toks[i] = ("You" if sent_start else "you") + " are"
                    flags.append(f"{pre}contraction_is")
                    subj = "actor"
                elif perfect:  # "<Actor>'s found out ..." = has found out (round 4 item 4: a subject never becomes 'Your')
                    toks[i] = ("You" if sent_start else "you") + " have"
                    flags.append(f"{pre}contraction_has")
                    subj = "actor"
                else:
                    toks[i] = "Your" if sent_start else "your"
            else:
                toks[i] = "You" if sent_start else "you"
                if prev not in _OBJECT_CUES:
                    subj = "actor"
            last = "actor"
            continue
        base = lw[:-2] if lw.endswith("'s") else lw
        name = t.replace("'s", "")
        titlecase = len(name) > 1 and name[0].isupper() and name[1:].islower()
        next_cap = adjacent and len(nxt) > 1 and nxt[0].isupper() and nxt[1:].islower() and nxt != actor and nxt not in other_names and nxt.lower() not in _PERSON_N
        chain = titlecase and name not in other_names and lw not in _PERSON_N and (next_cap or (cap_block and pos > 0 and "".join(toks[widx[pos - 1] + 1 : i]).strip() == ""))  # 'Ark Survival Evolved', 'Red Cross': a multi-word proper noun, not a person
        blocked = titlecase and name not in other_names and (prev in {"the", "a", "an", "this", "that", "these", "those"} or chain)
        is_other_name = name in other_names or (t[:1].islower() and base in other_lower) or (not blocked and _is_name_token(name, sent_start, actor, other_lower))
        cap_block = blocked
        is_role = base in _PERSON_N and sep_next.strip() != "-" and not (base == "ex" and adjacent and nxt.lower() in _PERSON_N) and not appos_zone  # 'ex-girlfriend' / 'ex boyfriend': the head decides
        if is_role and base in _INDEFINITE:
            is_role = False  # 'anyone who walks by' / 'let everyone hear him': generic, not an antecedent
        if is_other_name or is_role:
            # round 4 item 1: any other person (role noun or name) blocks the actor reading of the next actor-gender
            # pronoun, whatever branch below decides about the clause subject. Not another person: 'the governor of
            # his state' (defined relative to the actor), '<Actor> is a teacher' (the actor's own predicate), 'his wife,
            # Lisa' / 'her housemate Paul' when the name is the actor (the noun names the actor) or has a known gender
            of_actor = is_role and not is_other_name and adjacent and nxt.lower() == "of" and nxt2 in _MALE | _FEMALE
            predicate = is_role and not is_other_name and subj == "actor" and _actor_predicate(words, pos)
            names_actor = is_role and not is_other_name and (adjacent or sep_next.strip() == ",") and nxt == actor
            if not (of_actor or predicate or names_actor):
                if is_other_name and not is_role:
                    g = name_gender.get(_cap(name), "n")
                else:
                    g = "m" if base in _MALE_N else "f" if base in _FEMALE_N else "n"
                    if (adjacent or sep_next.strip() == ",") and len(nxt) > 1 and nxt[0].isupper() and nxt[1:].islower() and nxt != actor and nxt.lower() not in _CAP_NOT_PERSON:
                        if g == "n":
                            g = name_gender.get(nxt, "n")  # 'her housemate Paul': the name decides
                        else:
                            name_gender.setdefault(nxt, g)  # 'his wife, Mia': the role noun decides
                last = g
                others_seen.add(g)
        elif base in _PLURAL or base in _ANIMATE_PL or _plural_noun(lw, prev) is not None:
            sg = _plural_noun(lw, prev)
            if sg is not None and sg not in {"they", "them", "their", "theirs", "themselves", "everyone", "everybody", "others"} and _animate_plural(t, sg):
                plural_seen.add(sg)
            if pos >= 3 and words[pos - 3] in {"one", "each", "none", "some", "neither", "another", "any"} and words[pos - 2] == "of" and (words[pos - 1] in _DETS or words[pos - 1].endswith("'s")):
                last = "n"  # 'one of his friends asks him if he ...': a singular person out of the plural
                others_seen.add("n")
        if lw == "to" and pos + 1 < len(widx) and (is_base_verb(nxt) or (nxt.lower() == "not")):
            # infinitive: 'decide to V' keeps the actor as subject; 'ask your friend at work to V' / 'tell him to V'
            # (a person between the last verb and 'to') makes that person the subject
            for q in range(pos - 1, max(-1, pos - 7), -1):
                pw = words[q][:-2] if words[q].endswith("'s") else words[q]
                if pw in _PERSON_WORDS or pw in _MALE_N or pw in _FEMALE_N or pw in _NEUTRAL_SG or pw in _PLURAL or pw in other_lower or (toks[widx[q]][:1].isupper() and toks[widx[q]][1:].islower()):
                    subj = None
                    break
                det_at = next((d for d in (q - 1, q - 2) if d >= 0 and (words[d] in _DETS or words[d].endswith("'s"))), None)
                if _noun_before_to(pw, words[q - 1] if q > 0 else "") or det_at is not None:
                    head = det_at if det_at is not None else q
                    before = words[head - 1] if head > 0 else ""
                    if before == "for" or before not in _PREPS:  # a direct object: 'a cab to pick him up', 'videos on YouTube to help her', 'for an ambulance to come'
                        subj = None
                        break
                    continue  # a PP: 'go to the store to buy him a gift', the actor still acts
                if pw == "you" or pw in _COORD or pw in _SUBORD or _is_vbz(pw):
                    break
            continue
        if _is_gerund(t):
            if prev in _GERUND_SUBJ_PREPS or (prev == "not" and pprev_w in _GERUND_SUBJ_PREPS) or lw == "being":  # 'thank the host for having him', 'accuse her of not being faithful to him', 'the options being read to her'
                subj = None
            elif prev and pos > 0 and "".join(toks[widx[pos - 1] + 1 : i]).strip() == "" and prev not in _PREPS and prev not in _DETS and prev not in _COORD and prev not in _SUBORD and prev != "you" and prev not in _ADV and not prev.endswith("ly") and prev not in _AUX and not _is_vbz(prev) and not _is_gerund(prev) and (not _all_lemmas(prev).get("VERB") or pprev_w in _DETS or (pos > 2 and words[pos - 3] in _DETS)) and nxt.lower() in _REL_OBJ_NEXT:
                subj = None  # 'a phone call asking him to donate': reduced relative on a thing, the call asks
            elif pos > 0 and not "".join(toks[widx[pos - 1] + 1 : i]).strip(",;:") == "".join(toks[widx[pos - 1] + 1 : i]):
                pass  # ', guiding him': participial clause of the matrix subject
            elif prev and (prev in _PLURAL or prev in _MALE_N or prev in _FEMALE_N or prev in _NEUTRAL_SG or prev in _PERSON_WORDS or prev in other_lower or (toks[widx[pos - 1]][:1].isupper() and toks[widx[pos - 1]][1:].islower())) and "".join(toks[widx[pos - 1] + 1 : i]).strip() == "":
                subj = None  # 'your friends inviting him' / 'Sharon choosing her parents': reduced relative, they act
            continue
        if lw in _SUBJ_RESET and (lw in _AUX or (pos + 1 < len(widx) and (nxt.lower() in _AUX or _is_vbz(nxt) or bool(_all_lemmas(nxt).get("VERB"))))):
            subj = None
            continue
        nounish = lw not in _ADV and not lw.endswith("ly") and lw not in _COORD and lw not in _SUBORD and lw not in _DETS and lw not in _PREPS and lw not in _AUX and lw not in _MALE and lw not in _FEMALE and not _is_vbz(lw) and not _is_gerund(lw)
        if nounish and adjacent and nxt.lower() in _AUX and lw != "you":
            subj = None  # 'the company won't track him': a new subject
            continue
        prev_noun = prev and prev not in _AUX and prev not in _COORD and prev not in _ADV and prev not in _DETS and prev not in _PREPS and prev not in _SUBORD and prev not in _MALE and prev not in _FEMALE and prev != "you" and prev != actor.lower() and not _is_vbz(prev) and not _is_gerund(prev) and (not _all_lemmas(prev).get("VERB") or (_all_lemmas(prev).get("NOUN") and pprev_w in _DETS))
        if lw not in _AUX and lw not in _DETS and lw not in _PREPS and lw not in _COORD and lw not in _SUBORD and not _is_vbz(lw) and not _is_gerund(lw) and prev_noun and _all_lemmas(lw).get("VERB") and _all_lemmas(lw)["VERB"][0] != lw and not _all_lemmas(lw).get("NOUN") and "".join(toks[widx[pos - 1] + 1 : i]).strip() == "":
            subj = None  # 'the ticket written to him' / 'the woman left him': a verb form after a noun, i.e. another subject
            continue
        if nounish and adjacent and (prev in _DETS or pprev_w in _DETS) and is_base_verb(nxt) and not nxt.lower().endswith("ing") and not _is_vbz(nxt) and (nxt.lower() in _BARE_INF or not _all_lemmas(nxt).get("NOUN")):
            subj = None  # 'demand the tax firm pay him': a bare-infinitive complement with its own subject
            continue
        if (lw[:-2] if lw.endswith("'s") else lw) in _PLURAL and adjacent and (nxt.lower() in _AUX or nxt.lower() == "to" or (is_base_verb(nxt) and not nxt.lower().endswith("ing") and not _is_vbz(nxt) and nxt.lower() not in _PERSON_N)):
            subj = None  # 'your friends do all your chores and lose every game to him'
            continue
        if is_other_name or is_role:
            n = nxt.lower()
            # a new subject ('Angela is speaking to him'), a causative / object-control complement ('make the bully
            # stop bothering him', 'ask your friend to V') or an unknown role: the actor is no longer the certain subject
            infinitive = n == "to" and bool(nxt2) and nxt2 not in _DETS and nxt2 not in _PREPS and bool(is_base_verb(nxt2)) and not _is_vbz(nxt2)
            if not _object_np(words, pos) or (adjacent and (n in _AUX or _is_vbz(nxt) or infinitive or (is_base_verb(nxt) and not n.endswith("ing") and not _is_vbz(nxt) and n not in _PREPS))):
                subj = None
            continue
        if base in _PLURAL:
            if lw == "their" and subj == "actor" and adjacent and not (plural_seen - {_relation_noun_after(words, pos)}) and not any(w in {"they", "them", "their", "theirs", "themselves"} for w in words[:pos]):
                rel = _relation_noun_after(words, pos)
                if rel is not None:  # 'Decide not to join their coworkers' / 'Tell their friend': singular they for the actor
                    toks[i] = "Your" if t[0].isupper() else "your"
                    flags.append(f"{pre}singular_their")
                    continue
            continue
        if lw in _MALE or lw in _FEMALE:
            pg = "m" if lw in _MALE else "f"
            if pg != gender:
                if last == "n":  # 'Penelope ... her house': the other person of unknown gender has the other gender
                    last = pg
                    others_seen.discard("n")
                    others_seen.add(pg)
                n = nxt.lower()
                if lw in {"he", "she", "he's", "she's", "he'd", "she'd", "he'll", "she'll"}:
                    subj = None
                elif lw in {"him", "her"} and adjacent and (n == "to" or (is_base_verb(nxt) and not n.endswith("ing") and not _is_vbz(nxt) and n not in _PREPS)):
                    subj = None  # 'make her listen to him' / 'ask her to call him': she is the next subject
                continue
            cap = t[0].isupper()
            n = nxt.lower()
            if lw == "his":
                standalone = (not adjacent) or (n in _HIS_STANDALONE_NEXT and not hyphen_compound)
                determiner = not standalone
            elif lw == "her":
                if not adjacent:
                    determiner = False
                elif hyphen_compound:
                    determiner = True
                elif prev in _CAUSATIVES and is_base_verb(nxt) and not n.endswith("ing") and not n.endswith("s") and (n in _BARE_INF or not _all_lemmas(n).get("NOUN")):
                    determiner = False  # 'help her lift it'
                elif n in _POSS_ORDINAL:
                    determiner = bool(nxt2) and nxt2_adjacent and nxt2 not in _POSS_BLOCK and nxt2 not in _COORD
                else:
                    determiner = n not in _POSS_BLOCK
            else:
                determiner = False
            pprev = words[pos - 2] if pos > 1 else ""
            direct_object = (bool(_all_lemmas(prev).get("VERB")) or bool(is_base_verb(prev))) and prev not in _NEUTRAL_SG and prev not in _PERSON_WORDS and prev not in _PREPS and prev not in _LOC_PREPS and prev != "to"
            prep_object = prev in _OBJ_PREP_OK and pprev not in _LOC_PREPS and not (prev == "for" and n == "to")
            coordinated = n == "and" and bool(nxt2) and (toks[widx[pos + 2]][:1].isupper() or nxt2 in _DETS or nxt2 in _PERSON_WORDS)  # 'for her and Debbie'
            if (lw == "him" or (lw == "her" and not determiner)) and subj == "actor" and (direct_object or prep_object) and not coordinated:
                if not ctx.has_other:
                    flags.append("pronoun_ambiguous")  # 'to keep him motivated' with nobody else in the row: a sloppy reflexive
                    continue
                flags.append(f"{pre}object_pronoun_kept")  # 'you congratulate him' / 'you swipe at him': somebody else
                last = pg
                others_seen.add(pg)
                if adjacent and (n == "to" or (is_base_verb(nxt) and not n.endswith("ing") and not _is_vbz(nxt))):
                    subj = None  # 'tell him to V' / 'let him V': he is the next subject
                continue
            seen_here = pg in others_seen or "n" in others_seen
            seen_in_row = subj != "actor" and (pg in ctx.row_others or "n" in ctx.row_others)
            if seen_here or seen_in_row:
                flags.append("pronoun_same_gender_other")  # round 4: another possible antecedent exists; no rewrite
                continue
            if lw in {"he", "she"}:
                rep = "you"
                subj = "actor"
            elif lw in {"he's", "she's"}:
                rep = "you've" if (adjacent and n in {"been", "got", "gotten", "had"}) else "you're"
                subj = "actor"
            elif lw in {"he'd", "she'd"}:
                rep = "you'd"
                subj = "actor"
            elif lw in {"he'll", "she'll"}:
                rep = "you'll"
                subj = "actor"
            elif lw in {"himself", "herself"}:
                rep = "yourself"
            elif lw == "hers":
                rep = "yours"
            elif lw == "him":
                rep = "you"
            elif lw == "his":
                rep = "your" if determiner else "yours"
            else:  # her
                rep = "your" if determiner else "you"
            toks[i] = _cap(rep) if cap else rep
            last = "actor"
    return "".join(toks).replace(_APPOS_MARK, "")


# after a coordinated noun / verb homograph ('walks', 'starts'), these do not start a complement
_VBZ_NEXT_STOP = {"to", "for", "with", "from", "on", "at", "of", "as", "by", "in", "into", "onto", "upon", "about", "than", "like", "after", "before", "until", "since", "while", "because", "if", "when", "where", "whether", "although", "though", "unless", "once", "and", "or", "but", "so", "then", "too", "also", "instead", "again", "here", "there", "now", "soon", "later", "today", "tomorrow", "yesterday", "yet", "still", "just", "only", "even", "alone", "anyway", "that", "which", "who"}


def _coord_vbz_ok(toks: list[str], widx: list[int], words: list[str], nk: int, k: int) -> bool:
    """Is the word after the coordinator at `k` a third-person-singular verb of the actor rather than a plural noun?
    'and moves it' / 'and starts a fight' yes (a complement follows); 'flowers and wreaths and' no (a preposition,
    conjunction or the end follows AND a plural noun precedes the coordinator, i.e. nominal coordination)."""
    w = words[nk]
    if w in _NEG_MAP:
        return True
    if w in _PLURAL or w in _IRREGULAR_PLURAL or w in _ANIMATE_PL or not _is_vbz(toks[widx[nk]]):
        return False
    lem = _all_lemmas(w)
    noun = lem.get("NOUN")
    if noun == (w,) or (noun and noun[0] in _ANIMAL_N):
        return False
    if not noun:
        return True
    if nk + 1 < len(widx) and not "".join(toks[widx[nk] + 1 : widx[nk + 1]]).strip():
        n = words[nk + 1]
        if n in _PARTICLES or n == "not":
            return True
        if n not in _VBZ_NEXT_STOP and not _is_adv(toks[widx[nk + 1]]):
            return True
    pk = k - 1
    while pk > 0 and _is_adv(toks[widx[pk]]):
        pk -= 1
    if pk < 0:
        return False
    before = words[pk]
    if _plural_noun(before, words[pk - 1] if pk > 0 else "") is None:
        return True
    return not (before.endswith("s") or before in _IRREGULAR_PLURAL - _GROUP_N)  # 'your family and talks': a singular collective is no nominal coordination


def _verb_pass(text: str, flags: list[str], pre: str, imperative: bool = False) -> str:
    """Third-person-singular verbs whose subject became 'you' -> base form, including coordinated predicates. In an
    imperative action the actor stays the subject across nominal coordination ('the woman and breaks up' -> 'break
    up') and a coordinated verb after a subordinate clause is the actor's when a comma precedes it or the embedded
    verb does not agree with it ('toys that were ... and burns them' -> 'burn')."""
    try:
        from lemminflect import getAllLemmas
    except Exception:  # without lemminflect we leave verbs alone and flag the row
        flags.append("verb_agreement_unchecked")
        return text
    out_sents = []
    for sent in re.split(r"(?<=[.!?])\s+", text):
        toks = _TOK.findall(sent)
        widx = [i for i, t in enumerate(toks) if re.match(r"^[A-Za-z']+$", t)]
        words = [toks[i].lower() for i in widx]
        expect_verb = imperative
        you_clause = imperative
        in_sub = False  # inside a subordinate clause of an imperative action
        sub_vbz: Optional[bool] = None  # whether that clause's first verb is 3sg present
        sub_subj = False  # that clause has its own third-person subject ('until the dog falls asleep and stops')
        explicit_you = False  # an explicit 'you' subject appeared: coordinated 'are' is then correct
        embedded_3sg = False  # 'Tell her the food tastes wonderful and is ...': a 3sg subject inside the clause owns the next verb
        pending_main = -1  # index of 'who' in 'You, who live ..., <main verb>' while the main verb is still to be checked
        k = 0
        while k < len(widx):
            w = words[k]
            i = widx[k]
            prev = words[k - 1] if k > 0 else ""
            if pending_main >= 0 and k > pending_main + 1 and "," in "".join(toks[widx[k - 1] + 1 : i]):
                pending_main = -1
                expect_verb = True
            if w == "you":
                sep = "".join(toks[i + 1 : widx[k + 1]]) if k + 1 < len(widx) else ""
                j = k + 1
                if sep.strip().startswith(",") and j < len(widx) and words[j] != "who" and words[j] not in _SUBORD and words[j] not in _COORD and words[j] != "you":  # skip ', Jeff's friend,'
                    while j < len(widx) and not "".join(toks[widx[j] + 1 : widx[j + 1]] if j + 1 < len(widx) else "").strip().startswith(","):
                        j += 1
                    j += 1
                    if j - k > 6:  # not a short appositive
                        j = k + 1
                v = k + 1
                while v < len(widx) and _is_adv(toks[widx[v]]):
                    v += 1
                sep_before_you = "".join(toks[widx[k - 1] + 1 : i]) if k > 0 else ""
                subject = prev not in _OBJECT_CUES or (v < len(widx) and _is_vbz(toks[widx[v]]) and words[v] not in _PLURAL)
                if imperative and k > 0 and not (prev in _SUBORD or prev in _COORD or "," in sep_before_you or (v < len(widx) and _is_vbz(toks[widx[v]]) and words[v] not in _PLURAL)):
                    subject = False  # 'Text you and insults him': the object of the imperative
                if j < len(widx) and words[j] == "who":  # 'you, who lives ...' / 'at you, Jeff's friend, who has ...'
                    expect_verb = True
                    pending_main = j if (subject and j == k + 1 and sep.strip().startswith(",")) else -1
                    if subject:
                        you_clause, explicit_you = True, True
                    k = j
                    continue
                if subject:
                    you_clause = True
                    in_sub = False
                    expect_verb = True
                    explicit_you = True
                    k = j
                    continue
                k += 1
                continue
            if expect_verb:
                if _is_adv(toks[i]) or w in {"not", "also", "who", "only", "just", "even", "still", "already", "never", "always", "then"}:
                    k += 1
                    continue
                if (_is_vbz(toks[i]) or _is_extra_vbz(toks[i])) and not (k + 1 < len(widx) and words[k + 1] == "you" and w not in _NEG_MAP and k == 0):
                    toks[i] = _vbz_to_base(toks[i])
                    flags.append(f"{pre}verb_agreement")
                if k + 1 < len(widx) and words[k + 1] in _NEG_AUX:  # 'you are doesn't know' (source typo) -> 'don't'
                    toks[widx[k + 1]] = _vbz_to_base(toks[widx[k + 1]])
                    flags.append(f"{pre}verb_agreement")
                    k += 1
                expect_verb = False
                k += 1
                continue
            if w in _SUBORD and you_clause and not expect_verb:
                pp = w in _TEMPORAL_SUBORD and k + 1 < len(widx) and not toks[widx[k + 1]][:1].isupper() and not _subord_is_clause(words, k)
                if not pp:  # 'after work' / 'after a long day at work' are PPs: the clause and its subject go on
                    you_clause = False
                    if imperative:
                        in_sub, sub_vbz, sub_subj = True, None, w in {"who", "which"}  # a relative pronoun is its clause's subject
                k += 1
                continue
            if imperative and you_clause and not expect_verb and not in_sub and w in _EMBEDDED_VBZ and k >= 2 and k + 1 < len(widx) and words[k + 1] not in _COORD and words[k + 1] not in _SUBJ_PRON and words[k + 1] != "you" and "".join(toks[widx[k - 1] + 1 : i]).strip() == "":
                pprev = words[k - 2]
                prev_lem = getAllLemmas(prev)
                sg_noun = bool(prev_lem.get("NOUN")) and not prev.endswith("s") and not _is_vbz(toks[widx[k - 1]]) and prev not in _PERSON_WORDS and prev != "you"
                det_before = pprev in _DETS or pprev.endswith("'s") or (k >= 3 and words[k - 3] in _DETS and bool(getAllLemmas(pprev).get("ADJ")))
                if sg_noun and det_before:
                    embedded_3sg = True  # 'Tell her the food tastes wonderful and is ...': the noun phrase is the subject of this verb
            if in_sub and sub_vbz is None and not sub_subj and (w in _SUB_3SG_SUBJ or (toks[i][:1].isupper() and toks[i][1:].islower() and toks[i].lower() not in _CAP_NOT_PERSON) or ((prev in _DETS or prev.endswith("'s")) and k + 1 < len(widx) and (_is_vbz(toks[widx[k + 1]]) or words[k + 1] in _AUX or words[k + 1] in {"will", "would", "can", "could", "should", "might", "may", "must"}))):
                sub_subj = True  # 'until the dog falls asleep', 'if she agrees': the clause has its own subject
            if in_sub and sub_vbz is None and (w in _NEG_MAP or w in {"are", "were", "have", "do", "did", "didn't", "aren't", "weren't", "haven't", "don't"} or _is_vbz(toks[i]) or (getAllLemmas(w).get("VERB") and w.endswith("ed"))):
                sub_vbz = _is_vbz(toks[i]) and w not in {"are", "were", "have", "do"}
            sep_before = "".join(toks[widx[k - 1] + 1 : i]) if k > 0 else ""
            appositive_name = k >= 2 and toks[widx[k - 1]][:1].isupper() and toks[widx[k - 1]][1:].islower() and "," in "".join(toks[widx[k - 2] + 1 : widx[k - 1]])  # 'your wife, Mia, gets': the name is an appositive, the verb is hers
            if "," in sep_before and (you_clause or (imperative and in_sub)) and not expect_verb and not appositive_name and _is_vbz(toks[i]) and w not in _PLURAL and getAllLemmas(w).get("VERB") and not (k + 1 < len(widx) and words[k + 1] in _AUX):
                toks[i] = _vbz_to_base(toks[i])
                flags.append(f"{pre}verb_agreement_coord")
                k += 1
                continue
            if w in _COORD and embedded_3sg:
                embedded_3sg = False
                k += 1
                continue  # the coordinated verb belongs to the embedded 3sg subject
            if w in _COORD and (you_clause or (imperative and in_sub)):
                nk = k + 1
                while nk < len(widx) and (_is_adv(toks[widx[nk]]) or words[nk] in {"then", "ever", "hardly", "barely", "rarely", "seldom", "simply", "merely", "secretly", "quietly"}):
                    nk += 1
                if imperative and not explicit_you and nk < len(widx) and words[nk] in {"are", "is"} and w != "so" and (you_clause or (in_sub and sub_vbz is None and not sub_subj)):
                    toks[widx[nk]] = "be"  # 'Act up and are disruptive' / 'Sleep in ... and is forced' -> 'and be ...'
                    flags.append(f"{pre}verb_agreement_coord")
                    k = nk + 1
                    continue
                if nk < len(widx) and _coord_vbz_ok(toks, widx, words, nk, k):
                    # round 4 item 7: a VBZ right after and / then / but is the actor's when the clause before it is the
                    # imperative, including across a PP that starts with a subordinator-like word ('after work and brings')
                    if you_clause or "," in sep_before or sub_vbz is False or (in_sub and sub_vbz is None and not sub_subj):
                        toks[widx[nk]] = _vbz_to_base(toks[widx[nk]])
                        flags.append(f"{pre}verb_agreement_coord")
                        you_clause, in_sub = True, False
                        k = nk + 1
                        continue
                if nk < len(widx) and words[nk] != "you" and you_clause:
                    name_subject = toks[widx[nk]][:1].isupper() and toks[widx[nk]][1:].islower() and nk + 1 < len(widx) and (_is_vbz(toks[widx[nk + 1]]) or words[nk + 1] in _NEG_MAP or words[nk + 1] in {"will", "would", "can", "could", "should", "might", "may", "must", "did", "do", "does", "are", "were", "have", "had"})
                    if words[nk] in _SUBJ_PRON or name_subject:  # a new explicit subject ('and Anne takes it'), not 'Take John and Jake aside'
                        you_clause = False
            k += 1
        out_sents.append("".join(toks))
    return " ".join(out_sents)


def _ms_to_second(text: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str], flags: list[str], pre: str, ctx: Optional[_RowCtx] = None) -> str:
    out = _verb_pass(_person_pass(text, actor, gender, other_names, name_gender, flags, pre, ctx=ctx), flags, pre)
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)


def _ms_clean_field(text: str) -> str:
    """Moral Stories fields sometimes carry CSV-style doubled quotes and a wrapping quote pair."""
    t = " ".join((text or "").replace('""', '"').split())
    if len(t) > 1 and t[0] == '"' and t[-1] == '"':
        t = t[1:-1].strip()
    for pat, full in _UNAPOSTROPHISED:  # round 4 item 3: 'shes mad at her' -> "she's mad at her"
        t = pat.sub(lambda m, full=full: _cap(full) if m.group(0)[0].isupper() and full[0] != "I" else full, t)
    return t


_PLURAL_PRON = re.compile(r"\b(they|them|their|theirs|themselves|they're|they've|they'll|they'd|the two|both of them|the couple|the pair)\b", re.IGNORECASE)
_ANIMATE_PRON = {"they", "their", "theirs", "they're", "they've", "they'll", "they'd"}
_CONJOINED_YOU = re.compile(r"\b([Yy]ou and (?:your )?[A-Za-z]+|[A-Z][a-z]+ and [Yy]ou|[Yy]our [a-z]+ and [Yy]ou|[Yy]ou both|[Bb]oth of you|[Yy]ou two|[Tt]he two of you)\b")
_IRREGULAR_PLURAL = {"women", "men", "children", "people", "kids", "teeth", "feet", "police", "staff", "family", "couple", "pair", "team", "class", "crew", "group", "crowd", "everyone", "everybody", "someone", "somebody", "anyone", "anybody", "nobody", "person", "whoever", "each", "neither", "either", "folks", "cattle", "sheep", "fish", "deer", "mice", "geese", "others", "both", "several", "many", "few", "all", "parents", "siblings", "twins", "grandparents"}
_NOT_PLURAL_S = {"is", "was", "has", "his", "hers", "yours", "this", "thus", "us", "bus", "always", "perhaps", "besides", "yes", "its", "as", "does", "goes", "says", "class", "boss", "dress", "mess", "less", "unless", "across", "news", "glass", "grass", "kiss", "miss", "pass", "stress", "success", "business", "christmas", "thomas", "james", "lucas", "chris", "nicholas", "marcus", "charles", "miles", "jesus", "texas", "paris", "tennis", "chess", "gas", "bonus", "focus", "campus", "status", "virus", "plus", "minus", "famous", "serious", "various", "previous", "obvious", "nervous", "jealous", "anxious", "curious", "generous", "delicious", "religious", "dangerous", "enormous", "numerous", "furious", "precious", "cautious", "ambitious", "mysterious", "suspicious", "tedious", "hilarious", "ridiculous", "tremendous", "continuous", "conscious", "gorgeous", "courteous"}
# a plural noun that is also a 3sg verb ('needs', 'walls') counts as a noun only after a determiner-like word
_PLURAL_LICENSERS = {"the", "these", "those", "some", "many", "several", "few", "all", "both", "other", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten", "your", "his", "her", "their", "our", "my", "its", "of", "with", "for", "to", "from", "at", "on", "in", "by", "about", "among", "between", "and", "or", "no", "any", "more", "most", "various", "different", "new", "old", "young", "little", "big", "small", "good", "bad", "fellow", "close", "best", "older", "younger", "own", "are", "were", "have"}
_ANIMATE_SUFFIX = re.compile(r"(ers|ors|ists|ians|ees|ants|ents|mates|men)$")


def _plural_noun(tok: str, prev: str) -> Optional[str]:
    """The singular lemma when `tok` reads as a plural noun in context, else None."""
    lw = tok.lower()
    if lw in _PLURAL or lw in _IRREGULAR_PLURAL or lw in _ANIMATE_PL or lw in _GROUP_N:
        return lw
    if not (lw.endswith("s") and len(lw) > 3 and not lw.endswith("ss") and lw not in _NOT_PLURAL_S and not lw.endswith("ous") and not lw.endswith("ness")):
        return None
    lem = _all_lemmas(lw)
    if not lem:
        return lw  # unknown word ending in s: treat as a plural noun
    nouns = [n for n in lem.get("NOUN", ()) if n != lw]
    if not nouns:
        return None
    if lem.get("VERB") and _is_vbz(lw) and prev not in _PLURAL_LICENSERS:
        return None  # 'your son needs to', 'he hates': a verb
    return nouns[0]


def _animate_plural(tok: str, singular: str) -> bool:
    lw = tok.lower()
    if lw in _PLURAL or lw in _IRREGULAR_PLURAL or lw in _ANIMATE_PL or lw in _GROUP_N:
        return True
    if singular in _NEUTRAL_SG or singular in _MALE_N or singular in _FEMALE_N or singular in _ANIMAL_N or singular in _GROUP_N:
        return True
    if _ANIMATE_SUFFIX.search(lw):
        return True
    return tok[:1].isupper() and lw not in _all_lemmas(lw).get("NOUN", ())  # 'the Johnsons'


_GENDERED = re.compile(r"\b(he|she|him|her|his|hers|himself|herself|he's|she's)\b", re.IGNORECASE)


def _has_plural_antecedent(text: str, animate: bool = False, subject_they: bool = False) -> bool:
    """A plural noun before a plural pronoun; with `animate`, one that can be referred to by 'they' / 'their'
    (people, animals, groups), so that 'things ... their relationship' does not count. A gender-neutral singular
    ('your roommate ... their bedroom') licenses singular they only when no he / she is in play."""
    toks = re.findall(r"[A-Za-z]+", text.replace("in-laws", "inlaws").replace("co-workers", "coworkers"))
    names = [w for w in toks[1:] if w[:1].isupper() and w not in {"You", "Your", "I"}]
    neutral_ok = animate and not subject_they and not _GENDERED.search(text) and not names
    for j, w in enumerate(toks):
        if neutral_ok and w.lower() in _NEUTRAL_SG:
            return True
        sg = _plural_noun(w, toks[j - 1].lower() if j else "")
        if sg is None:
            continue
        if not animate or _animate_plural(w, sg):
            return True
    return False


def _group_phrase_follows(text: str, start: int) -> bool:
    """'they used to eat often as a family': a togetherness phrase in the same clause as the plural pronoun."""
    clause = re.split(r"[.;!?]|\b(?:and|but|or|so|because|while|when|if)\b", text[start:], maxsplit=1)[0]
    return bool(_GROUP_PHRASE.search(clause))


def plural_refers_to_actor(situation: str, actions: Iterable[str]) -> bool:
    """Heuristic for 'they / their / them / the two' standing for the actor plus someone after conversion:
    a plural pronoun after a 'you and <Name>' construction (situation), or a plural pronoun in an action or in
    the situation with no plural noun before it ('they' / 'their' need a people / animal / group antecedent, 'them'
    any plural noun or singular-they antecedent). Round 4 item 6: a plural pronoun followed by 'as a family' /
    'together' / 'the two of you' in a clause whose subject is 'you' (always, in an action) and that names no plural
    before the pronoun is the actor plus others."""
    conj = _CONJOINED_YOU.search(situation)
    for m in _PLURAL_PRON.finditer(situation):
        p = m.group(1).lower()
        if p in ("the two", "both of them", "the couple", "the pair"):
            return True
        if conj and m.start() > conj.start():
            return True
        if not _has_plural_antecedent(situation[: m.start()], animate=p in _ANIMATE_PRON, subject_they=p.startswith("they")):
            return True
        sent_start = max(situation.rfind(". ", 0, m.start()), -2) + 2
        sentence = situation[sent_start : m.start()]
        if re.search(r"\b[Yy]ou\b", sentence) and not _has_plural_antecedent(sentence, animate=True) and _group_phrase_follows(situation, m.end()):
            return True
    for a in actions:
        for m in _PLURAL_PRON.finditer(a):
            p = m.group(1).lower()
            if p in ("the two", "both of them", "the couple", "the pair"):
                return True
            if conj or _CONJOINED_YOU.search(a[: m.start()]):
                return True
            if not _has_plural_antecedent(situation + " " + a[: m.start()], animate=p in _ANIMATE_PRON, subject_they=p.startswith("they")):
                return True
            if not _has_plural_antecedent(a[: m.start()], animate=True) and _group_phrase_follows(a, m.end()):
                return True
    return False


_BRACKETS = re.compile(r"\[[^\]]*\]|\([^)]*\)")
_ACTION_NOISE = {"xor": "or"}  # source typos that make a pair differ only in noise


def action_core(a: str) -> str:
    """Lower-cased action text without bracketed insertions and punctuation, for the x == y check."""
    t = _BRACKETS.sub(" ", a).lower()
    t = re.sub(r"[^a-z0-9' ]", " ", t)
    return " ".join(_ACTION_NOISE.get(w, w) for w in t.split())


def _be_complement_is_adjectival(words: list[str], k: int) -> bool:
    """'is honest' / 'is very careful' / 'is there for her' -> an imperative 'Be ...' makes sense; 'is only around young
    girls' / 'is in the kitchen' / 'is a teacher' / 'is invited' (passive) -> a state, not an action (round 4 item 5)."""
    j = k + 1
    while j < len(words) and words[j].lower().strip(",.") in _DEGREE_ADV and words[j].lower().strip(",.") != "a":
        j += 1
    if j >= len(words):
        return False
    comp = words[j].lower().strip(",.;:")
    if comp in {"there", "ok", "okay", "fine", "alright", "upfront", "home", "early", "late", "ready", "present", "punctual", "nice", "sorry", "quiet", "polite"}:
        return True
    if comp == "on" and j + 1 < len(words) and words[j + 1].lower().strip(",.") == "time":
        return True
    if comp in _DETS or comp in _PREPS or comp in _PARTICLES or comp in _LOC_PREPS or comp in _SUBJ_PRON or comp in _PERSON_WORDS or comp in {"around", "away", "out", "off", "in", "at", "on", "with", "without", "like", "unlike", "about", "not", "no", "one", "part", "able", "unable", "supposed", "going", "due", "about"}:
        return comp in {"able", "unable"}
    lem = _all_lemmas(comp)
    if not lem:
        return True  # unknown word: assume an adjective ('is privy')
    if lem.get("ADJ"):
        return True
    return False  # a noun ('is a teacher' caught above by the determiner; 'is best friends'), a passive participle, an adverb


def _ms_rescue_clause(words: list[str], k: int, actor: str) -> Optional[str]:
    """For a stative head: the first 'so / and (then) / but' clause whose verb is the actor's eventive 3sg verb, rebuilt as
    '<Actor> <clause>' ('is only around young girls all day, so he joins a dating site' -> 'Sam joins a dating site');
    None when no such clause exists or the clause has another subject."""
    for coords in ({"so"}, {"and", "but", "then"}):  # a 'so' clause is the consequence, hence the action; 'and' clauses second
        j = k + 1
        while j < len(words):
            if words[j].lower().strip(",") in coords and not words[j].endswith("."):
                m = j + 1
                while m < len(words) and words[m].lower() in {"then", "also", "later", "instead", "immediately", "quickly", "just", "simply", "still", "eventually", "finally"}:
                    m += 1
                pron = m < len(words) and (words[m].lower() in {"he", "she"} or words[m] == actor)
                if pron:
                    m += 1
                    while m < len(words) and (_is_adv(words[m]) or words[m].lower() in {"then", "just", "also", "still", "only"}):
                        m += 1
                if m < len(words):
                    v = words[m].lower().strip(",.")
                    before = words[j - 1].lower().strip(",.") if j > 0 else ""
                    nominal = not pron and _plural_noun(before, words[j - 2].lower() if j > 1 else "") is not None and bool(_all_lemmas(v).get("NOUN"))  # 'positions and issues': nouns, not a clause
                    if (_is_vbz(v) or v in _NEG_MAP) and not nominal and v not in {"is", "was", "isn't", "wasn't"} and (_lemma(v) or v) not in _MS_STATIVE_VBZ and v not in _MS_STATIVE_VBZ and m + 1 < len(words):
                        return f"{actor} " + " ".join(words[m:])
            j += 1
    return None


def _ms_action_to_imperative(a: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str], flags: list[str], pre: str, ctx: Optional[_RowCtx] = None, _depth: int = 0) -> Optional[str]:
    a = " ".join(a.split()).strip().strip('"')
    m = re.match(rf"^{re.escape(actor)}\s+(.*)$", a)
    if not m:
        flags.append("action_first_word_not_verb")
        return None
    words = m.group(1).rstrip(".").strip().split()
    k = 0
    while k < len(words) - 1 and _is_adv(words[k]):
        k += 1
    lw = words[k].lower()
    nxt = words[k + 1].lower() if k + 1 < len(words) else ""
    nxt2 = words[k + 2].lower() if k + 2 < len(words) else ""
    going_to = nxt == "going" and nxt2 == "to" and k + 3 < len(words) and bool(is_base_verb(words[k + 3])) and not _is_gerund(words[k + 3])
    progressive = lw in {"is", "was", "isn't", "wasn't"} and _is_gerund(nxt) and (going_to or nxt == "going" or ("ADJ" not in _all_lemmas(nxt) and nxt2 != "of"))
    stative = (lw in {"is", "was", "isn't", "wasn't"} and not progressive and not _be_complement_is_adjectival(words, k)) or lw in _MS_STATIVE_VBZ or (lw in {"has", "had"} and nxt == "to")
    if stative:
        # round 4 item 5: a stative main clause is never imperativised; the 'so / and then' clause with the eventive
        # verb becomes the action, otherwise the row is dropped
        rescued = _ms_rescue_clause(words, k, actor) if _depth == 0 else None
        if rescued is None:
            flags.append("action_stative_verb")
            return None
        flags.append(f"{pre}stative_head_clause")
        return _ms_action_to_imperative(rescued, actor, gender, other_names, name_gender, flags, pre, ctx, _depth=1)
    if progressive:
        # progressive head: 'is having a picnic' -> 'Have a picnic'; 'is going to tell her' -> 'Tell her'
        neg = lw in {"isn't", "wasn't"}
        if nxt == "going" and k + 3 < len(words) and words[k + 2].lower() == "to" and is_base_verb(words[k + 3]) and not _is_gerund(words[k + 3]):
            del words[k : k + 3]
        else:
            del words[k]
            words[k] = _lemma(nxt) or nxt
        if neg:
            words.insert(k, "Do not")
        flags.append(f"{pre}progressive_head")
    elif lw in {"is", "was"}:
        words[k] = "Be"
    elif lw in {"isn't", "wasn't"}:
        words[k] = "Do not be"
    elif lw in {"doesn't", "didn't", "won't", "can't", "cannot"}:
        words[k] = "Do not"
    elif lw in {"will", "would", "should", "could", "can"} and len(words) > k + 1:
        del words[k]
    elif lw in {"has", "had", "have", "did", "does"}:
        flags.append("action_first_word_not_verb")
        return None
    else:
        try:
            from lemminflect import getAllLemmas

            lem = _lemma(lw)
            if not lem or (lem == lw and lw not in getAllLemmas(lw).get("VERB", ())):
                flags.append("action_first_word_not_verb")
                return None
        except Exception:
            lem = _lemma(lw) or lw
        words[k] = lem
    rest = " ".join(words)
    rest = _person_pass(rest, actor, gender, other_names, name_gender, flags, pre, imperative=True, ctx=ctx)
    rest = _verb_pass(rest, flags, pre, imperative=True)
    return _cap(rest) + "."


_ROW_PRED = re.compile(r"\b(?:{actor}|he|she|who)(?:'s)?\s+(?:is|was|became|becomes|become)\s+(?:a|an|the)?\s*(?:[a-z]+\s+){{0,3}}([a-z]+)", re.IGNORECASE)


def _learn_name_genders(allt: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str]) -> dict[str, str]:
    """name_gender plus the genders a row gives away itself: 'her husband Jeff' / 'Kimmy's son, Aden' (a gendered role
    noun names the person), and a single other name of unknown gender whose row carries pronouns of the gender the
    actor does not have ('Camden ... Savanna ... he sees her': Savanna is f)."""
    out = dict(name_gender)
    for m in re.finditer(r"\b([a-z]+),?\s+([A-Z][a-z]+)\b", allt):
        role, name = m.group(1), m.group(2)
        if name != actor and name not in out and name.lower() not in _CAP_NOT_PERSON and (role in _MALE_N or role in _FEMALE_N):
            out[name] = "m" if role in _MALE_N else "f"
    toks = re.findall(r"[A-Za-z]+", allt)
    unknown = {w for j, w in enumerate(toks) if w != actor and w not in out and (w in other_names or (j > 0 and toks[j - 1].lower() not in {"the", "a", "an"} and _is_name_token(w, False, actor, set()) and not (j + 1 < len(toks) and toks[j + 1][:1].isupper() and toks[j + 1].lower() not in _PERSON_N) and not toks[j - 1][:1].isupper()))}
    if len(unknown) == 1 and gender in ("m", "f"):
        opp = "f" if gender == "m" else "m"
        if re.search(r"\b(?:%s)\b" % "|".join(_FEMALE if opp == "f" else _MALE), allt.lower()):
            out[unknown.pop()] = opp
    return out


def _row_others(texts: list[str], actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str]) -> tuple[set[str], bool]:
    """Genders of the other people (role nouns / names) and whether anybody or any animal besides the actor appears
    in `texts` (the fields that precede the one being converted, or the whole row for the animacy check). Not counted
    as others: the actor's own predicate nouns ('<Actor> is a teacher'), indefinites ('nobody is looking'), capitals
    after a determiner or in a capitalised chain ('the Kentucky Derby'). A single other of unknown gender takes the
    gender of the row's non-actor pronouns ('Penelope ... her')."""
    allt = " ".join(texts)
    pred = {m.group(1).lower() for m in re.finditer(_ROW_PRED.pattern.format(actor=re.escape(actor)), allt, re.IGNORECASE)}
    toks = re.findall(r"[A-Za-z']+", allt)
    others: list[str] = []
    seen_names: set[str] = set()
    animate = False
    cap_block = False
    for j, w in enumerate(toks):
        base = w.lower()[:-2] if w.lower().endswith("'s") else w.lower()
        name = w.replace("'s", "")
        if w == actor or w == actor + "'s":
            cap_block = False
            continue
        titlecase = len(name) > 1 and name[0].isupper() and name[1:].islower()
        blocked = titlecase and name not in other_names and (j > 0 and (toks[j - 1].lower() in {"the", "a", "an", "this", "that", "these", "those"} or cap_block))
        if base in _PERSON_N and not (j + 1 < len(toks) and toks[j + 1] == actor):
            animate = True
            named = j + 1 < len(toks) and len(toks[j + 1]) > 1 and toks[j + 1][0].isupper() and toks[j + 1][1:].islower() and toks[j + 1].lower() not in _CAP_NOT_PERSON and toks[j + 1].lower() not in _PERSON_N
            if base not in pred and base not in _INDEFINITE and not named:  # 'her neighbor Penelope': the name is counted
                others.append("m" if base in _MALE_N else "f" if base in _FEMALE_N else "n")
        elif name in other_names or (j > 0 and not blocked and _is_name_token(name, False, actor, set())):
            animate = True
            if _cap(name) not in seen_names:  # each name once, so a single unknown-gender other can be resolved below
                seen_names.add(_cap(name))
                others.append(name_gender.get(_cap(name), "n"))
        elif base in _PLURAL | _ANIMATE_PL | _GROUP_N | _ANIMAL_N | _PERSON_WORDS - {"they", "them", "their", "him", "her", "you", "me", "us", "himself", "herself", "yourself", "themselves"}:
            animate = True
        cap_block = blocked
    return set(others), animate


def load_moral_stories(jsonl_path: str | Path) -> list[Family]:
    """moral_stories_full.jsonl -> Family rows. Situation = situation + intention in the second person;
    x = normative action, y = divergent action. Rows whose actor cannot be found or whose actions do not start
    with the actor are dropped silently (no family can be formed); doubtful conversions carry flags."""
    rows = [json.loads(l) for l in open(jsonl_path, encoding="utf-8") if l.strip()]
    for r in rows:
        for k in ("situation", "intention", "moral_action", "immoral_action"):
            r[k] = _ms_clean_field(r.get(k, ""))
    actors, corpus_name_gender = _name_genders(rows)
    name_pool = {a for a in actors if a.lower() not in _COMMON_CAPS_OK and a.lower() not in _PERSON_N}  # 'He' / 'Having' are not names
    fams: list[Family] = []
    for r in rows:
        flags: list[str] = []
        actor = _actor_of(r)
        if not actor:
            continue
        allt = " ".join([r["situation"], r["intention"], r["moral_action"], r["immoral_action"]])
        other_names = {w for w in re.findall(r"\b[A-Z][a-z]+\b", allt) if w != actor and w in name_pool}
        name_gender = corpus_name_gender
        # round 4: does the row mention anybody (or any animal) besides the actor? If not, a kept object pronoun is a
        # sloppy reflexive and the row is flagged (see _person_pass)
        low = allt.lower()
        m = sum(len(re.findall(rf"\b{w}\b", low)) for w in _MALE)
        f = sum(len(re.findall(rf"\b{w}\b", low)) for w in _FEMALE)
        gender = name_gender.get(actor) or ("m" if m > f else "f" if f > m else None)
        if gender is None and (m or f):
            flags.append("gender_unknown")
        name_gender_row = _learn_name_genders(allt, actor, gender, other_names, name_gender)
        all_others, has_other = _row_others([allt], actor, gender, other_names, name_gender_row)
        if gender and name_gender.get(actor) == gender and ((m and not f and gender == "f") or (f and not m and gender == "m")) and not ({"n", "m" if m else "f"} & all_others):
            gender = "m" if m else "f"  # 'Sam ... a car that she likes': the row's pronouns are unanimous and nobody else is around
            flags.append("gender_from_row")
        sit_others, _ = _row_others([r["situation"]], actor, gender, other_names, name_gender_row)
        pre_act_others, _ = _row_others([r["situation"], r["intention"]], actor, gender, other_names, name_gender_row)
        sit_plurals = _animate_plural_lemmas(r["situation"])
        all_plurals = sit_plurals | _animate_plural_lemmas(r["intention"])
        ctx_sit = _RowCtx(has_other)
        ctx_int = _RowCtx(has_other, frozenset(sit_others), frozenset(sit_plurals))
        ctx_act = _RowCtx(has_other, frozenset(pre_act_others), frozenset(all_plurals))
        name_gender = name_gender_row
        situation = f"{_ms_to_second(r['situation'], actor, gender, other_names, name_gender, flags, 'sit_', ctx_sit).strip()} {_ms_to_second(r['intention'], actor, gender, other_names, name_gender, flags, 'int_', ctx_int).strip()}"
        if detect_person(situation) != "second":
            flags.append("not_second_person")
        if re.search(rf"\b{re.escape(actor)}\b", situation):
            flags.append("residual_actor_name")
        ax = _ms_action_to_imperative(r["moral_action"], actor, gender, other_names, name_gender, flags, "x_", ctx_act)
        ay = _ms_action_to_imperative(r["immoral_action"], actor, gender, other_names, name_gender, flags, "y_", ctx_act)
        if ax is None or ay is None:
            continue
        if any(_possessive_without_noun(t) for t in (situation, ax, ay)):
            flags.append("possessive_without_noun")
        for a in (ax, ay):
            if re.search(rf"\b{re.escape(actor)}\b", a):
                flags.append("residual_actor_name")
        if plural_refers_to_actor(situation, (ax, ay)):
            flags.append("plural_refers_to_actor")
        if action_core(ax) == action_core(ay):
            flags.append("actions_identical")
        if any(re.match(r"^\w+(?: \w+)? (?:himself|herself)\b", a) for a in (ax, ay)):
            flags.append("reflexive_residual")  # 'Introduce himself ...': the actor's gender was mis-inferred
        auto = sorted({x for x in flags if any(s in x for s in ("verb_agreement", "contraction", "object_pronoun", "progressive_head", "actor_appositive", "singular_their", "stative_head_clause"))})
        review = sorted({x for x in flags if x not in auto})
        fams.append(
            Family(
                family_id=f"ms_{r['ID']}",
                source="moral_stories",
                source_id=str(r["ID"]),
                topic_group=norm_polarity(r["norm"]),
                situation=situation,
                action_x=ax,
                action_y=ay,
                ambiguity="unknown",
                split=POOL_SPLIT,
                needs_review=review,
                meta={
                    "provenance": "moral_stories_rule_converted",
                    "license": LICENSES["moral_stories"],
                    "norm": r["norm"],
                    "norm_polarity": norm_polarity(r["norm"]),
                    "actor": actor,
                    "normative_action": "x",
                    "moral_consequence": r.get("moral_consequence", ""),
                    "immoral_consequence": r.get("immoral_consequence", ""),
                    "auto_edits": auto,
                    "tier": "same_gender_other" if "pronoun_same_gender_other" in review else "clean",
                },
            )
        )
    return fams


# ---- ETHICS justice (impartiality) -------------------------------------------------------------------------------

_ETH_ADV = r"(usually|normally|typically|used to|always|often|generally|regularly|frequently|sometimes|tend to)"
_ETH_IMP = re.compile(
    rf"^I\s+(?P<habit>{_ETH_ADV})\s+(?P<vp>.+?)[,;]?\s+but\s+(?:I\s+)?(?:(?P<tail0>today|tonight|yesterday|this (?:time|year|week|month|morning|evening|weekend|semester|season|summer|winter|spring|fall)|last (?:night|week|year|time))\s+(?:I\s+)?)?(?:didn't|did not|don't|do not|haven't|have not|won't|will not|stopped|no longer do|not anymore|not today|not this time|this time I did not|this time I didn't|not this year|not this week|not this morning)\b(?P<tail>[^.]*?)\s+because\s+(?P<reason>.+)$",
    re.IGNORECASE,
)
_SENTENCE_STARTERS = {"i", "you", "he", "she", "it", "we", "they", "there", "the", "a", "an", "my", "your", "his", "her", "their", "our", "its", "this", "that", "these", "those", "it's", "there's", "he's", "she's", "they're", "you're", "we're", "i'm", "i've", "you've", "i'd", "you'd", "someone", "somebody", "everyone", "nobody", "no", "all", "some", "one", "today", "yesterday", "last", "none", "most", "many", "every", "each", "both", "neither", "either", "when", "after", "before", "because", "since", "while", "if", "as", "at", "in", "on", "of", "for", "with", "due", "being", "having", "going", "getting", "not"}
_TIME_TAIL = re.compile(r"^(today|tonight|this (?:time|year|week|month|morning|evening|weekend|semester|season|summer|winter|spring|fall)|yesterday|last (?:night|week|year|time))$", re.IGNORECASE)
_HABITUAL_ADV = re.compile(
    r"\s*\b(?:(?:every|each) (?:single )?(?:day|night|morning|evening|afternoon|week|weekend|month|year|time|summer|winter|spring|fall|semester|sunday|monday|tuesday|wednesday|thursday|friday|saturday)s?|"
    r"(?:once|twice) a (?:day|week|month|year)|all the time|always|daily|weekly|monthly|yearly|annually|usually|often|regularly|normally|typically|frequently|routinely|"
    r"(?:on|every) (?:sunday|monday|tuesday|wednesday|thursday|friday|saturday|weekend|weekday)s?(?: (?:mornings?|afternoons?|evenings?|nights?))?|on (?:the )?weekends?)\b",
    re.IGNORECASE,
)


def strip_habitual_adverbial(vp: str) -> tuple[str, bool]:
    """'go to the Rose Parade every year with your aunt' -> 'go to the Rose Parade with your aunt' (the habit stays
    in the situation; the action names the act itself)."""
    out = _HABITUAL_ADV.sub("", vp)
    out = re.sub(r"\s+([,.;])", r"\1", " ".join(out.split())).strip().rstrip(",")
    return (out, True) if out and out != vp else (vp, False)


def ethics_justice_family(scenario: str, label: int, source_id: str) -> tuple[Optional[Family], list[str]]:
    """'I usually VP but didn't today because R' -> situation 'You usually VP. Today, R.'; x = VP, y = Do not VP.
    label 1 = the excuse is reasonable (consensus: skipping is fine -> y); label 0 = unreasonable (consensus x)."""
    s = " ".join((scenario or "").split()).rstrip(".")
    m = _ETH_IMP.match(s)
    if not m:
        return None, ["no_impartiality_match"]
    flags: list[str] = []
    vp, reason, habit = m.group("vp").strip(), m.group("reason").strip().rstrip("."), m.group("habit").lower()
    if habit == "used to":
        flags.append("habit_discontinued")
    # the habit's own reason clause ('buy fruit from my friend, because I like shopping locally') is not part of the act
    vp = re.sub(r",?\s+(?:because|since)\b.*$", "", vp, flags=re.IGNORECASE).strip().rstrip(".,;").strip()
    vp = _strip_leading_pronoun(vp, flags)  # 'I usually to knock ...' (source typo)
    if len(vp.split()) < 2:
        flags.append("short_action")
    vp2, fl = first_to_second_person(vp)
    vp2 = vp2[0].lower() + vp2[1:]
    act_vp, stripped = strip_habitual_adverbial(vp2)
    if stripped:
        flags.append("habitual_adverbial_dropped")
    _check_imperative_head(act_vp, flags)
    reason2, fl2 = first_to_second_person(reason)
    if reason2.split() and reason2.split()[0].lower() in _SENTENCE_STARTERS:
        reason2 = reason2[0].lower() + reason2[1:]  # MTurk capitalisation ('because There were'), not a proper noun
    tail = (m.group("tail") or "").strip() or (m.group("tail0") or "").strip()
    lead = _cap(tail) if tail and _TIME_TAIL.match(tail) else "This time"
    situation = f"You {habit} {vp2}. {lead}, {reason2}."
    flags += [x for x in fl + fl2 if x != "source_has_second_person"]  # residual_first_person_plural stays: hard
    if detect_person(situation) != "second":
        flags.append("not_second_person")
    if len(act_vp.split()) > 22:
        flags.append("long_action")
    fam = Family(
        family_id=f"eth_j_{source_id}",
        source="hendrycks_ethics",
        source_id=source_id,
        topic_group="justice_impartiality",
        situation=situation,
        action_x=_cap(act_vp) + ".",
        action_y="Do not " + act_vp + ".",
        ambiguity="low",
        split=POOL_SPLIT,
        needs_review=sorted(set(flags)),
        meta={
            "provenance": "hendrycks_ethics_justice_rule_converted",
            "license": LICENSES["hendrycks_ethics"],
            "habit_adverb": habit,
            "ethics_label": int(label),
            "consensus_action": "y" if int(label) == 1 else "x",
            "habit_vp": vp2,
            "reason": reason2,
            "scenario": scenario,
        },
    )
    return fam, fam.needs_review


def load_ethics_justice(csv_paths: Iterable[str | Path], one_per_vp: bool = True) -> list[Family]:
    """ETHICS justice csv files (label, scenario) -> Family rows for the impartiality items. With `one_per_vp`
    only the first scenario of each habit verb phrase is kept (the others differ only in the excuse)."""
    fams: list[Family] = []
    seen_vp: set[str] = set()
    for path in csv_paths:
        with open(path, encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                scenario = r.get("scenario", "")
                sid = hashlib.md5(scenario.encode("utf-8")).hexdigest()[:12]
                fam, _ = ethics_justice_family(scenario, int(r.get("label", 0)), sid)
                if fam is None:
                    continue
                key = fam.meta["habit_vp"].lower()
                if one_per_vp and key in seen_vp:
                    continue
                seen_vp.add(key)
                fams.append(fam)
    return fams


# ---- MoralChoice low ambiguity (already Family rows) ------------------------------------------------------------


def moralchoice_low_from_families(fams: Iterable[Family]) -> list[Family]:
    """The `sanity` split of families.jsonl re-labelled for the pool. family_id is kept so the build script can
    recognise the rows as re-used (not leaked) when it checks against the existing families."""
    out: list[Family] = []
    for f in fams:
        if f.source == "moralchoice" and f.split == "sanity" and f.ambiguity == "low":
            g = f.model_copy(deep=True)
            g.split = POOL_SPLIT
            g.meta = {**g.meta, "provenance": "families.jsonl sanity split (moralchoice low ambiguity), family_id unchanged", "license": LICENSES["moralchoice"], "original_split": f.split}
            out.append(g)
    return out
