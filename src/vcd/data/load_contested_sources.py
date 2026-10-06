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
_NEUTRAL_SG = {"friend", "boss", "coworker", "colleague", "neighbor", "neighbour", "roommate", "teacher", "student", "customer", "clerk", "cashier", "kid", "child", "someone", "somebody", "stranger", "partner", "parent", "cousin", "doctor", "nurse", "officer", "manager", "employee", "client", "classmate", "teammate", "coach", "driver", "owner", "landlord", "tenant", "baby", "toddler", "person", "spouse", "sibling", "relative", "guest", "host", "buddy", "pal", "date", "ex", "professor", "dentist", "vet", "lawyer", "mechanic", "plumber", "babysitter", "twin", "passenger", "shopper", "cop", "supervisor", "assistant", "intern", "candidate", "applicant", "patient", "victim", "teen", "teenager", "infant", "chef", "bartender", "barista", "salesman", "salesperson", "agent", "realtor", "contractor", "worker", "volunteer", "mentor", "tutor", "principal", "dean", "judge", "referee", "umpire", "pastor", "priest", "rabbi", "counselor", "therapist"}
_PLURAL = {"friends", "coworkers", "colleagues", "neighbors", "neighbours", "roommates", "teachers", "students", "customers", "kids", "children", "people", "parents", "family", "relatives", "siblings", "guests", "classmates", "teammates", "employees", "clients", "passengers", "workers", "others", "everyone", "everybody", "they", "them", "their", "group", "crowd", "team", "class", "couple", "twins", "guys", "girls", "boys", "men", "women", "folks"}
_ADV = {"also", "often", "now", "then", "just", "always", "never", "usually", "still", "even", "really", "simply", "later", "instead", "first", "again", "already", "sometimes", "frequently", "regularly", "occasionally", "soon", "once", "twice", "immediately", "finally", "eventually", "secretly", "politely", "quietly", "quickly", "calmly", "gently", "carefully", "happily", "angrily", "rudely", "honestly", "kindly", "promptly", "loudly", "sternly", "firmly", "reluctantly", "excitedly", "nervously", "casually", "openly", "privately", "publicly", "briefly", "actually", "generously", "graciously", "gracefully", "warmly", "coldly", "bluntly", "directly", "discreetly"}
_NOT_ADV_LY = {"family", "only", "early", "daily", "holy", "ugly", "lonely", "fly", "rely", "apply", "reply", "supply", "bully", "rally", "tally", "ally", "belly", "jelly", "silly", "chilly", "smelly", "lovely", "friendly", "likely", "costly", "deadly", "elderly", "lively", "lowly", "monthly", "weekly", "yearly", "hourly", "nightly", "orderly", "kindly", "assembly"}
_COORD = {"and", "but", "or", "then", "so"}
_POSS_BLOCK = {"to", "that", "a", "an", "the", "about", "for", "with", "from", "into", "on", "at", "of", "as", "by", "in", "up", "out", "off", "down", "over", "back", "away", "here", "there", "again", "whether", "if", "how", "what", "when", "where", "why", "too", "instead", "first", "last", "alone", "and", "or", "but", "because", "while", "so", "is", "was", "has", "had", "will", "would", "can", "could", "should", "not", "this", "these", "those", "some", "any", "very", "then", "after", "before", "until", "since", "though", "although", "unless", "once", "than", "like", "through", "without", "around", "under", "toward", "towards", "onto", "upon", "yet", "still", "also", "just", "only", "even", "now", "soon", "later", "today", "tomorrow", "yesterday"}
_SUBORD = {"when", "while", "because", "if", "who", "whom", "whose", "that", "which", "whenever", "after", "before", "until", "as", "since", "where", "although", "though", "unless"}
_TOK = re.compile(r"[A-Za-z']+|[^A-Za-z']+")
_NEG_MAP = {"doesn't": "don't", "isn't": "aren't", "wasn't": "weren't", "hasn't": "haven't", "is": "are", "has": "have", "was": "were", "does": "do"}
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


def _vbz_to_base(w: str) -> str:
    lw = w.lower()
    out = _NEG_MAP.get(lw) or _lemma(lw) or lw
    return _cap(out) if w[0].isupper() else out


def _is_adv(w: str) -> bool:
    if w[:1].isupper() and w.lower() not in _ADV:
        return False
    lw = w.lower()
    return lw in _ADV or (lw.endswith("ly") and lw not in _NOT_ADV_LY)


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


def _person_pass(text: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str], flags: list[str], pre: str) -> str:
    toks = _TOK.findall(text)
    widx = [i for i, t in enumerate(toks) if re.match(r"^[A-Za-z']+$", t)]
    last = "actor"
    for pos, i in enumerate(widx):
        t = toks[i]
        lw = t.lower()
        nxt = toks[widx[pos + 1]] if pos + 1 < len(widx) else ""
        adjacent = pos + 1 < len(widx) and "".join(toks[i + 1 : widx[pos + 1]]).strip() == ""
        prev_nonspace = next((toks[j].strip() for j in range(i - 1, -1, -1) if toks[j].strip()), "")
        sent_start = i == 0 or prev_nonspace == "" or prev_nonspace.endswith((".", "!", "?"))
        if t == actor or t == actor + "'s":
            if t.endswith("'s"):
                if adjacent and (nxt.lower().endswith("ing") or nxt.lower() in {"a", "an", "the", "not", "very", "so", "too", "going", "about", "at", "in", "on", "always", "never", "really"}):
                    toks[i] = ("You" if sent_start else "you") + " are"
                    flags.append(f"{pre}contraction_is")
                else:
                    toks[i] = "Your" if sent_start else "your"
            else:
                toks[i] = "You" if sent_start else "you"
            last = "actor"
            continue
        base = lw[:-2] if lw.endswith("'s") else lw
        if t in other_names or t.replace("'s", "") in other_names:
            last = name_gender.get(t.replace("'s", ""), "n")
            continue
        if base in _MALE_N:
            last = "m"
            continue
        if base in _FEMALE_N:
            last = "f"
            continue
        if base in _NEUTRAL_SG:
            last = "n"
            continue
        if base in _PLURAL:
            continue
        if lw in _MALE or lw in _FEMALE:
            pg = "m" if lw in _MALE else "f"
            if pg != gender:
                continue
            if last == pg:
                flags.append("pronoun_same_gender_other")
                continue
            if last == "n":
                flags.append("pronoun_ambiguous")
                continue
            cap = t[0].isupper()
            if lw in {"he", "she"}:
                rep = "you"
            elif lw in {"he's", "she's"}:
                rep = "you've" if (adjacent and (nxt.lower().endswith("ed") or nxt.lower() in {"been", "got", "gotten", "done", "had"})) else "you're"
            elif lw in {"he'd", "she'd"}:
                rep = "you'd"
            elif lw in {"he'll", "she'll"}:
                rep = "you'll"
            elif lw in {"himself", "herself"}:
                rep = "yourself"
            elif lw == "hers":
                rep = "yours"
            elif lw == "him":
                rep = "you"
            elif lw == "his":
                rep = "your" if (adjacent and nxt.lower() not in _POSS_BLOCK) else "yours"
            else:  # her
                rep = "your" if (adjacent and nxt.lower() not in _POSS_BLOCK) else "you"
            toks[i] = _cap(rep) if cap else rep
            last = "actor"
    return "".join(toks)


def _verb_pass(text: str, flags: list[str], pre: str, imperative: bool = False) -> str:
    """Third-person-singular verbs whose subject became 'you' -> base form, including coordinated predicates."""
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
        k = 0
        while k < len(widx):
            w = words[k]
            i = widx[k]
            prev = words[k - 1] if k > 0 else ""
            if w == "you" and prev not in _OBJECT_CUES:
                you_clause = True
                expect_verb = True
                sep = "".join(toks[i + 1 : widx[k + 1]]) if k + 1 < len(widx) else ""
                if sep.strip().startswith(","):
                    j = k + 1
                    while j < len(widx) and not "".join(toks[widx[j] + 1 : widx[j + 1]] if j + 1 < len(widx) else "").strip().startswith(","):
                        j += 1
                    k = j + 1
                    expect_verb = True
                    continue
                k += 1
                continue
            if expect_verb:
                if _is_adv(toks[i]) or w in {"not", "also"}:
                    k += 1
                    continue
                if _is_vbz(toks[i]) and not (k + 1 < len(widx) and words[k + 1] == "you" and w not in _NEG_MAP and k == 0):
                    toks[i] = _vbz_to_base(toks[i])
                    flags.append(f"{pre}verb_agreement")
                expect_verb = False
                k += 1
                continue
            if w in _SUBORD and you_clause and not expect_verb:
                you_clause = False
            sep_before = "".join(toks[widx[k - 1] + 1 : i]) if k > 0 else ""
            if "," in sep_before and you_clause and not expect_verb and _is_vbz(toks[i]) and w not in _PLURAL and getAllLemmas(w).get("VERB"):
                toks[i] = _vbz_to_base(toks[i])
                flags.append(f"{pre}verb_agreement_coord")
                k += 1
                continue
            if w in _COORD and you_clause:
                nk = k + 1
                while nk < len(widx) and _is_adv(toks[widx[nk]]):
                    nk += 1
                if nk < len(widx) and _is_vbz(toks[widx[nk]]) and words[nk] not in _PLURAL and not getAllLemmas(words[nk]).get("NOUN") == (words[nk],):
                    toks[widx[nk]] = _vbz_to_base(toks[widx[nk]])
                    flags.append(f"{pre}verb_agreement_coord")
                    k = nk + 1
                    continue
                if nk < len(widx) and words[nk] != "you":
                    you_clause = False
            k += 1
        out_sents.append("".join(toks))
    return " ".join(out_sents)


def _ms_to_second(text: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str], flags: list[str], pre: str) -> str:
    out = _verb_pass(_person_pass(text, actor, gender, other_names, name_gender, flags, pre), flags, pre)
    return re.sub(r"(^|[.!?]\s+)([a-z])", lambda m: m.group(1) + m.group(2).upper(), out)


def _ms_clean_field(text: str) -> str:
    """Moral Stories fields sometimes carry CSV-style doubled quotes and a wrapping quote pair."""
    t = " ".join((text or "").replace('""', '"').split())
    if len(t) > 1 and t[0] == '"' and t[-1] == '"':
        t = t[1:-1].strip()
    return t


_PLURAL_PRON = re.compile(r"\b(they|them|their|theirs|themselves|they're|they've|they'll|they'd|the two|both of them|the couple|the pair)\b", re.IGNORECASE)
_CONJOINED_YOU = re.compile(r"\b([Yy]ou and (?:your )?[A-Za-z]+|[A-Z][a-z]+ and [Yy]ou|[Yy]our [a-z]+ and [Yy]ou|[Yy]ou both|[Bb]oth of you|[Yy]ou two|[Tt]he two of you)\b")
_IRREGULAR_PLURAL = {"women", "men", "children", "people", "kids", "teeth", "feet", "police", "staff", "family", "couple", "pair", "team", "class", "crew", "group", "crowd", "everyone", "everybody", "someone", "somebody", "anyone", "anybody", "nobody", "person", "whoever", "who", "each", "neither", "either", "folks", "cattle", "sheep", "fish", "deer", "mice", "geese", "others", "both", "several", "many", "few", "all", "parents", "siblings", "twins", "grandparents"}
_NOT_PLURAL_S = {"is", "was", "has", "his", "hers", "yours", "this", "thus", "us", "bus", "always", "perhaps", "besides", "yes", "its", "as", "does", "goes", "says", "class", "boss", "dress", "mess", "less", "unless", "across", "news", "glass", "grass", "kiss", "miss", "pass", "stress", "success", "business", "christmas", "thomas", "james", "lucas", "chris", "nicholas", "marcus", "charles", "miles", "jesus", "texas", "paris", "tennis", "chess", "gas", "bonus", "focus", "campus", "status", "virus", "plus", "minus", "famous", "serious", "various", "previous", "obvious", "nervous", "jealous", "anxious", "curious", "generous", "delicious", "religious", "dangerous", "enormous", "numerous", "furious", "precious", "cautious", "ambitious", "mysterious", "suspicious", "tedious", "hilarious", "ridiculous", "tremendous", "continuous", "conscious", "gorgeous", "courteous"}


def _has_plural_antecedent(text: str) -> bool:
    for w in re.findall(r"[A-Za-z]+", text):
        lw = w.lower()
        if lw in _PLURAL or lw in _IRREGULAR_PLURAL:
            return True
        if lw.endswith("s") and len(lw) > 3 and not lw.endswith("ss") and lw not in _NOT_PLURAL_S and not lw.endswith("ous") and not lw.endswith("ness"):
            try:
                from lemminflect import getAllLemmas

                noun = getAllLemmas(lw).get("NOUN")
                if noun and noun[0] != lw:
                    return True
                if not getAllLemmas(lw):  # unknown word ending in s: treat as a plural noun
                    return True
            except Exception:
                return True
    return False


def plural_refers_to_actor(situation: str, actions: Iterable[str]) -> bool:
    """Heuristic for 'they / their / them / the two' standing for the actor plus someone after conversion:
    a plural pronoun after a 'you and <Name>' construction (situation), or a plural pronoun in an action or in
    the situation with no plural noun (or singular-they antecedent) before it."""
    conj = _CONJOINED_YOU.search(situation)
    for m in _PLURAL_PRON.finditer(situation):
        if m.group(1).lower() in ("the two", "both of them", "the couple", "the pair"):
            return True
        if conj and m.start() > conj.start():
            return True
        if not _has_plural_antecedent(situation[: m.start()]):
            return True
    for a in actions:
        for m in _PLURAL_PRON.finditer(a):
            if m.group(1).lower() in ("the two", "both of them", "the couple", "the pair"):
                return True
            if conj or _CONJOINED_YOU.search(a[: m.start()]):
                return True
            if not _has_plural_antecedent(situation + " " + a[: m.start()]):
                return True
    return False


def _ms_action_to_imperative(a: str, actor: str, gender: Optional[str], other_names: set[str], name_gender: dict[str, str], flags: list[str], pre: str) -> Optional[str]:
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
    if lw in {"is", "was"}:
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
    rest = _person_pass(rest, actor, gender, other_names, name_gender, flags, pre)
    rest = _verb_pass(rest, flags, pre, imperative=True)
    return _cap(rest) + "."


def load_moral_stories(jsonl_path: str | Path) -> list[Family]:
    """moral_stories_full.jsonl -> Family rows. Situation = situation + intention in the second person;
    x = normative action, y = divergent action. Rows whose actor cannot be found or whose actions do not start
    with the actor are dropped silently (no family can be formed); doubtful conversions carry flags."""
    rows = [json.loads(l) for l in open(jsonl_path, encoding="utf-8") if l.strip()]
    for r in rows:
        for k in ("situation", "intention", "moral_action", "immoral_action"):
            r[k] = _ms_clean_field(r.get(k, ""))
    actors, name_gender = _name_genders(rows)
    fams: list[Family] = []
    for r in rows:
        flags: list[str] = []
        actor = _actor_of(r)
        if not actor:
            continue
        allt = " ".join([r["situation"], r["intention"], r["moral_action"], r["immoral_action"]])
        other_names = {w for w in re.findall(r"\b[A-Z][a-z]+\b", allt) if w != actor and w in actors and actors[w] >= 2}
        low = allt.lower()
        m = sum(len(re.findall(rf"\b{w}\b", low)) for w in _MALE)
        f = sum(len(re.findall(rf"\b{w}\b", low)) for w in _FEMALE)
        gender = name_gender.get(actor) or ("m" if m > f else "f" if f > m else None)
        if gender is None and (m or f):
            flags.append("gender_unknown")
        situation = f"{_ms_to_second(r['situation'], actor, gender, other_names, name_gender, flags, 'sit_').strip()} {_ms_to_second(r['intention'], actor, gender, other_names, name_gender, flags, 'int_').strip()}"
        if detect_person(situation) != "second":
            flags.append("not_second_person")
        if re.search(rf"\b{re.escape(actor)}\b", situation):
            flags.append("residual_actor_name")
        ax = _ms_action_to_imperative(r["moral_action"], actor, gender, other_names, name_gender, flags, "x_")
        ay = _ms_action_to_imperative(r["immoral_action"], actor, gender, other_names, name_gender, flags, "y_")
        if ax is None or ay is None:
            continue
        for a in (ax, ay):
            if re.search(rf"\b{re.escape(actor)}\b", a):
                flags.append("residual_actor_name")
        if plural_refers_to_actor(situation, (ax, ay)):
            flags.append("plural_refers_to_actor")
        auto = sorted({x for x in flags if "verb_agreement" in x or "contraction" in x})
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
