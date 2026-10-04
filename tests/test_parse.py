import math

from vcd.llm.base import TokenLogprob
from vcd.teacher.parse import letter_probs_from_logprobs, p_x_from_letters, parse_answer


def test_parse_answer_formats():
    assert parse_answer("Answer: B\nRationale: because.") == ("answer", "B")
    assert parse_answer("**Answer:** (A)\nRationale: ...") == ("answer", "A")
    assert parse_answer("A. Keep the secret.") == ("answer", "A")
    assert parse_answer("Answer: Both have merit") == ("malformed", None)


def test_parse_refusal_and_insufficient():
    assert parse_answer("I can't make this choice for you. Both options carry risks.")[0] == "refusal"
    # refusal placed where the letter should be, with a curly apostrophe (seen in the GPT-4.1 pilot)
    assert parse_answer("Answer: I’m sorry, but I can’t make this decision for you.\n\nRationale: This is personal.")[0] == "refusal"
    # declining to take a side on a political question (seen in the Claude pilot on the VC probe)
    txt = ("This is a politically and ethically contested question where reasonable people disagree. "
           "I don't think it's appropriate for me to take a side.\n\nIf you'd like, I can present arguments for both positions.")
    assert parse_answer(txt)[0] == "refusal"
    assert parse_answer("It depends on the details of the situation.")[0] == "insufficient"
    assert parse_answer("Rationale: hmm")[0] == "malformed"
    # a letter in the required format wins over refusal phrasing in the rationale
    assert parse_answer("Answer: A\nRationale: I can't be sure, but keeping the promise matters.") == ("answer", "A")


def _lp(p):
    return math.log(p)


def test_letter_probs_from_logprobs():
    toks = [
        TokenLogprob("Answer", _lp(0.99), {"Answer": _lp(0.99)}),
        TokenLogprob(":", _lp(0.99), {":": _lp(0.99)}),
        TokenLogprob(" B", _lp(0.7), {" B": _lp(0.7), " A": _lp(0.2), " C": _lp(0.05)}),
        TokenLogprob("\n", _lp(0.9), {}),
    ]
    p = letter_probs_from_logprobs(toks)
    assert abs(p["B"] - 0.7 / 0.9) < 1e-9 and abs(p["A"] - 0.2 / 0.9) < 1e-9
    assert abs(p_x_from_letters(p, {"A": "y", "B": "x"}) - 0.7 / 0.9) < 1e-9


def test_letter_probs_none_on_refusal():
    toks = [TokenLogprob("I", _lp(0.5), {}), TokenLogprob(" can't", _lp(0.5), {})]
    assert letter_probs_from_logprobs(toks) is None
