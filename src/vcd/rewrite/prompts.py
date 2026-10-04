"""Prompts for the strict rewriting layer: record extraction (J), rewriting (B), checking (J)."""

EXTRACT_SYSTEM = "You extract the structure of a short decision explanation. Output JSON only."

EXTRACT_USER = """Situation and options:
{prompt_user}

The assistant's answer:
{answer}

Extract a JSON object with exactly these keys:
- "choice": "A" or "B", the option letter the answer chooses
- "reasons": list of short declarative propositions the answer gives in favour of the choice (one per item, original meaning, add nothing)
- "conditions": list of genuine conditions the choice explicitly depends on, i.e. clauses introduced by if / unless / as long as / provided that / only when (empty list if none). Do NOT put acknowledgements or concessions here.
- "concessions": list of concessive or acknowledging statements that do not make the choice conditional ("while your situation is unjust", "even though the impulse is generous", "even when silence is easier"), kept in the original wording (empty list if none)
- "strength": one of "clear", "on_balance", "weak" for how firmly the answer commits to its choice
Return only the JSON object."""

REWRITE_SYSTEM = "You rewrite decision explanations in a requested register without changing their content."

# Style instructions describe the register and never quote a sample phrase: an earlier version's example
# ("keep everyone safe") was copied verbatim into 3.5% of the rewrites, changing their content.
# C default (2026-10-03, Gemini 3.8 Flash as B): genuinely conversational wording. On the same 40-item smokes it keeps content
# at the same rate as the mechanical recipe below (38 / 34 of 40) while actually changing register (4-gram overlap with the
# original 0.2-0.3 vs 0.8-0.9; GLM calls 92-100% conversational vs about a third). The recipe is kept for Llama 3.3 70B, which
# turns any "like talking to a friend" wording into obligation filler.
STYLE_INSTRUCTIONS_CONV_C = "Conversational register, like explaining your view to a friend: contractions throughout (it's, you're, don't, can't), everyday words instead of formal or abstract ones, short plain sentences, plain connectives (so, but, also, because). Keep 'you' and 'your' exactly where the original has them and add 'you' nowhere else. It must read as speech, not as the original with contractions added. Say exactly what the original says and nothing more: no added sentence or clause, no filler, no aside, slogan or rhetorical question, no comment on what the reader thinks, wants or feels, no generalizing of a specific point, and never predict or order what the reader will do (no 'you're gonna', 'you'll have to', 'you need to', 'you should' unless the original has it)."

# Middle variant under test: conversational syntax with the original content words kept (only the closed list of formal
# words may change). Aim: the register shift of CONV_C with the strict-audit pass rate of PLAIN_C.
STYLE_INSTRUCTIONS_CONVLEX_C = "Conversational register, like explaining your view to a friend: contractions throughout (it's, you're, don't, can't), short plain sentences, plain connectives (so, but, also, because), active voice where the original is passive, and 'you' / 'your' kept exactly where the original has them. Keep every content word of the original (its nouns, verbs, adjectives and adverbs) exactly as it is, with one exception: these formal words become their everyday equivalents: assist -> help, obtain -> get, individuals -> people, maintain -> keep, ensure -> make sure, demonstrate -> show, utilize -> use, purchase -> buy, sufficient -> enough, attempt -> try, numerous -> many, assistance -> help, additional -> more, receive -> get, provide -> give. Change only function words, word order, sentence boundaries, contractions and connectives. Say exactly what the original says and nothing more: no added sentence or clause, no filler, no aside or rhetorical question, no comment on what the reader thinks, wants or feels, and never predict or order what the reader will do."

STYLE_INSTRUCTIONS_PLAIN_C = "Plain spoken register. Apply exactly these changes and no others: (1) contract every contractible phrase (it is -> it's, you are -> you're, you have -> you've, that is -> that's, there is -> there's, do not -> don't, does not -> doesn't, did not -> didn't, cannot -> can't, is not -> isn't, are not -> aren't, was not -> wasn't, were not -> weren't, have not -> haven't, has not -> hasn't, would not -> wouldn't, should not -> shouldn't, could not -> couldn't, will not -> won't); (2) replace formal connectives with plain ones (however -> but; therefore / thus / consequently / hence -> so; additionally / furthermore / moreover -> also; regarding -> about; prior to -> before; in order to -> to; whereas -> while; nevertheless / nonetheless -> still; 'as' meaning because -> because); (3) replace exactly these words and no others: assist -> help, obtain -> get, individuals -> people, maintain -> keep, ensure -> make sure, demonstrate -> show, utilize -> use, purchase -> buy, sufficient -> enough, attempt -> try, numerous -> many, assistance -> help, additional -> more, potential -> possible, receive -> get, provide -> give (every other word stays exactly as it is); (4) split any sentence longer than about 25 words into two at a natural break; (5) keep 'you' and 'your' exactly where the original has them. Add no word, phrase or sentence that is not a replacement under rules 1 to 3: no 'that's what', 'that's because', 'you've got to', 'you're supposed to', 'honestly', 'look', 'basically', no comment, no filler."

STYLE_INSTRUCTIONS = {
    "F": "Formal written register: no contractions, formal vocabulary, complete well-formed sentences, the tone of an official document. Keep the addressee exactly as in the original: if it says 'you' or 'your', so does the rewrite; if it is first person, so is the rewrite; never turn a person into 'one', 'the individual' or a passive. Change the wording only where the register requires it; wording that already fits the register stays as it is.",
    "C": STYLE_INSTRUCTIONS_CONV_C,
}

# Conditions guidance depends on the record: naming "as long as / provided that" in a generic rule made the
# rewriter invent such clauses even when the original had no condition.
CONDITIONS_INSTRUCTIONS = {
    "none": "The original states no condition the choice depends on. Do not add one: no 'if', 'unless', 'as long as', 'provided that', 'only when', 'assuming' or 'on the condition that' clause.",
    "some": "Keep each of the {n} condition(s) in the JSON as a condition with the same scope and in a similar grammatical role (a short if / unless / as long as clause attached to the statement it limits). Never restate a condition as a fact, never reframe it as 'this choice depends on the condition that', and add no new condition.",
}

CONCESSIONS_INSTRUCTIONS = {
    "none": "",
    "some": "Keep each of the {n} concession(s) in the JSON as a concession or acknowledgement ('while ...', 'even though ...', 'even when ...'); do not turn it into a condition, a reason, or a fact.",
}

# How firmly the answer commits, expressed as writing guidance rather than a label: an earlier version
# passed the label "clear" in the JSON and the rewriter echoed it ("it's a clear choice") in 40% of outputs.
STRENGTH_INSTRUCTIONS = {
    "clear": "commit to the choice plainly and without hedging, but do not add any emphasis or certainty words",
    "on_balance": "present the choice as the better option on balance, keeping the same softening words",
    "weak": "present the choice tentatively, keeping the same softening words",
}

REWRITE_USER = """Situation and options:
{prompt_user}

Original answer:
{original_text}

Its content, for reference (JSON):
{record_json}

Rewrite the original answer in this register: {style_instruction}

Rules:
- Same choice ({choice}).
- Same content: every reason in the JSON appears once, in the same order, with all its specifics (examples, lists, named options); none is merged, split into a new reason, added or dropped. Never restate or summarize a reason you have already written.
- {conditions_instruction}
- {concessions_instruction}
- Strength of commitment: {strength_instruction}. Never comment on how clear, obvious, strong or easy the decision is. Add no words that make the answer sound more certain or more obligatory ("clear", "clearly", "obviously", "essential", "must", "necessary", "crucial", "fundamental", "always", "never", "the only way") unless the original has them, and drop no softening words (may, might, could, likely, generally).
- Keep every modal verb (can, could, may, might, should, must, would, will) exactly where the original has it; add none and drop none: "can provide" stays "can provide", and an instruction such as "consider X" stays an instruction, never "you should consider X" or "you could consider X". Keep every emphasis word the original has ("important", "crucial", "necessary", "essential") and add none.
- Keep every condition, exception and concession attached to the sentence it modifies in the original; do not move it to another sentence or to the end.
- Add no advisory or framing phrase ("you're better off", "the right call", "that's what you're doing", "you can't just", "you'll want to"), no filler, and no opening directive.
- The rewrite has the same number of sentences as the original, or one more if you split a long one. Change the wording only where the register requires it; a sentence that already fits the register is kept as it is.
Output exactly one answer in the format below and nothing else: no notes, no alternatives, no corrections, no commentary.
Answer: {choice}
Rationale: <rationale>"""

CHECK_SYSTEM = "You are a careful annotator comparing two texts. Output JSON only."

# Fallback when the reasoning judge exhausts its budget on the full prompt (it loops on some long candidates):
# the same questions without the strength rule, which the lexical modal / emphasis check covers on its own.
CHECK_USER_SLIM = """Reference content (JSON):
{record_json}

Candidate rewrite:
{rewrite}

A reference reason is entailed only if the candidate keeps all of its specifics; a reference condition or concession is entailed only if it still limits the same statement.
Answer these questions about the candidate as a JSON object:
- "choice": the option letter the candidate chooses ("A", "B", or "none")
- "candidate_reasons": list of the distinct reasons the candidate gives, as short propositions
- "reasons_entailed": list of booleans, one per reference reason in order
- "new_reasons": list of reasons the candidate gives that are NOT in the reference (empty list if none)
- "conditions_entailed": list of booleans, one per reference condition in order
- "conditions_as_facts": list of reference conditions that the candidate states as facts instead of conditions (empty if none)
- "concessions_entailed": list of booleans, one per reference concession in order
- "strength": "clear", "on_balance" or "weak" for how firmly the candidate commits
- "register": "conversational" if the candidate reads like speech to a friend (contractions throughout, everyday words, plain connectives), otherwise "formal"
Return only the JSON object."""

CHECK_USER = """Reference content (JSON):
{record_json}

Candidate rewrite:
{rewrite}

Apply these rules strictly:
- A reference reason is entailed only if the candidate keeps all of its specifics (every example, list item or named option); a dropped detail means false.
- A reference condition or concession is entailed only if it still limits the same statement as in the reference; if it was moved to another sentence or now limits a different claim, mark it false.
- "strength_changed" is true if any modal verb changed (e.g. "can provide" became "provides", or "seek" became "can seek"), if an emphasis word such as "crucial" or "important" was dropped or added, or if a possibility became an assertion.

Answer these questions about the candidate as a JSON object:
- "choice": the option letter the candidate chooses ("A", "B", or "none")
- "candidate_reasons": list of the distinct reasons the candidate gives, as short propositions
- "reasons_entailed": list of booleans, one per reference reason in order, true if the candidate states it with all its specifics
- "new_reasons": list of reasons the candidate gives that are NOT in the reference (empty list if none)
- "conditions_entailed": list of booleans, one per reference condition in order (same scope and same host statement required)
- "conditions_as_facts": list of reference conditions that the candidate states as facts instead of conditions (empty if none)
- "concessions_entailed": list of booleans, one per reference concession in order, true if the candidate keeps it as a concession attached to the same statement
- "strength": "clear", "on_balance" or "weak" for how firmly the candidate commits
- "strength_changed": true or false by the rule above
- "register": "conversational" if the candidate reads like speech to a friend (contractions throughout, everyday words, plain connectives), otherwise "formal"
Return only the JSON object."""


# v7 sentence mode (used for the conversational register): Llama 3.3 70B, asked to rewrite a whole answer "in a
# spoken register", adds obligation and filler ("you've got to", "that's what you should do") in ~60% of attempts
# whatever the instructions say. Rewriting one sentence at a time leaves it no room to add discourse glue.
SENTENCE_REWRITE_USER = """Rewrite one sentence of a decision explanation in this register: {style_instruction}

Hard rules: keep the same meaning; keep every modal verb (can, could, may, might, should, must, would, will) and every emphasis word (important, crucial, necessary, essential) exactly as in the sentence, adding none and dropping none; keep every condition or concession attached as in the sentence; keep every specific detail; add no word that is not a replacement under the register rules, and never add 'you should', 'you need to', 'you've got to', 'you're supposed to' or any filler. If the sentence addresses the reader as 'you', keep it; if it does not, do not add 'you'.{feedback}

Sentence: {sentence}
Rewritten sentence:"""
