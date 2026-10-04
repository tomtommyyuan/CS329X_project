from vcd.rewrite.pipeline import Record, evaluate_checks, parse_json_object, record_from_json


def test_parse_json_object_tolerates_fences_and_prose():
    txt = 'Here you go:\n```json\n{"choice": "B", "reasons": ["Promises bind."], "conditions": [], "strength": "clear"}\n```\nDone.'
    d = parse_json_object(txt)
    assert d["choice"] == "B" and d["reasons"] == ["Promises bind."]
    assert parse_json_object("no json here") is None


def test_record_from_json_validation():
    assert record_from_json({"choice": "C", "reasons": ["x"]}, "p", "t", "") is None
    assert record_from_json({"choice": "A", "reasons": []}, "p", "t", "") is None
    r = record_from_json({"choice": "a", "reasons": ["x"], "strength": "odd"}, "p", "t", "")
    assert r.choice == "A" and r.strength == "on_balance" and r.concessions == []
    r2 = record_from_json({"choice": "B", "reasons": ["x"], "concessions": ["while the impulse is generous"]}, "p", "t", "")
    assert r2.concessions == ["while the impulse is generous"]


def test_concessions_must_survive_as_concessions():
    rec = Record(prompt_id="p", teacher="t", choice="A", reasons=["r1"], conditions=[], concessions=["while the impulse is generous"], strength="clear", source_text="Answer: A\nRationale: While the impulse is generous, r1.")
    base = {"choice": "A", "candidate_reasons": ["r1"], "reasons_entailed": [True], "new_reasons": [], "conditions_entailed": [], "conditions_as_facts": [], "strength": "clear", "register": "formal"}
    assert evaluate_checks(rec, "Answer: A\nRationale: While the impulse is generous, r1.", {**base, "concessions_entailed": [True]}, "F")["kept"]
    assert not evaluate_checks(rec, "Answer: A\nRationale: On the condition that the impulse is generous, r1.", {**base, "concessions_entailed": [False]}, "F")["conditions"]
    # judge silent about concessions -> not accepted
    assert not evaluate_checks(rec, "Answer: A\nRationale: r1.", base, "F")["conditions"]


def test_lexical_strength_check():
    from vcd.rewrite.pipeline import lexical_strength_check

    orig = "Answer: A\nRationale: You may want to keep the promise, since it is important to your friend."
    worse = "Answer: A\nRationale: You must keep the promise; it is clearly essential to your friend."
    same = "Answer: A\nRationale: Keeping the promise may be the right call, as it matters to your friend."
    lx = lexical_strength_check(orig, worse)
    assert set(lx["intensifiers_added"]) >= {"must", "clearly", "essential"} and lx["hedges_removed"] == ["may"]
    assert lexical_strength_check(orig, same) == {"intensifiers_added": [], "hedges_removed": []}
    # "clear" only in intensifying uses
    echoed = "Answer: A\nRationale: It's a clear choice; you may want to keep the promise since it matters to your friend."
    neutral = "Answer: A\nRationale: You may want to keep the promise and set clear boundaries with your sister."
    assert "clear choice" in lexical_strength_check(orig, echoed)["intensifiers_added"]
    assert lexical_strength_check(orig, neutral)["intensifiers_added"] == []


def test_lexical_addition_check():
    from vcd.rewrite.pipeline import lexical_addition_check

    orig = "Answer: A\nRationale: Keeping the promise matters to your friend."
    added = "Answer: A\nRationale: You're better off keeping the promise, as long as nothing new comes up; it matters to your friend."
    out = lexical_addition_check(orig, added, n_conditions=0)
    assert out["conditions_added"] == ["as long as"] and out["framing_added"] == ["you're better off"]
    pred = "Answer: A\nRationale: You're gonna have to keep the promise since it matters to your friend."
    assert {"gonna", "have to"} <= set(lexical_addition_check(orig, pred, n_conditions=0)["framing_added"])
    # phrases already in the original are not flagged
    assert lexical_addition_check("You have to keep it.", "You have to keep the promise.", 0)["framing_added"] == []
    # when the original already has conditions, conditional markers are the judge's business, not a lexical fail
    assert lexical_addition_check(orig, added, n_conditions=1)["conditions_added"] == []


def test_modal_shift_and_format_checks():
    from vcd.rewrite.pipeline import format_check, modal_shift_check

    orig = "Answer: A\nRationale: Drawing can provide a healthy outlet, and it is crucial to seek help."
    assert modal_shift_check(orig, "Answer: A\nRationale: Drawing provides a healthy outlet, and it is crucial to seek help.")["modals_changed"] == ["can"]
    assert modal_shift_check(orig, "Answer: A\nRationale: Drawing can provide a healthy outlet, and it is good to seek help.")["emphasis_changed"] == ["crucial"]
    assert modal_shift_check(orig, "Answer: A\nRationale: Drawing can provide a healthy outlet; it is crucial to seek help.") == {"modals_changed": [], "emphasis_changed": []}
    # contractions, inflection and derived forms are the same modal / emphasis word
    assert modal_shift_check("You will need to help; you cannot ignore the importance of it.", "You'll need to help; you can't ignore how important it is.") == {"modals_changed": [], "emphasis_changed": []}
    assert modal_shift_check("You need to help.", "One needs to help.")["modals_changed"] == []
    assert modal_shift_check("The key is to help.", "The main thing is to help.")["emphasis_changed"] == []
    fmt = format_check(orig, "Answer: A\nRationale: x.\n\nRevised to:\nAnswer: A\nRationale: y.")
    assert fmt["multiple_answers"] and fmt["meta_text"]
    assert format_check(orig, "Answer: A\nRationale: " + "word " * 60)["too_long"]
    assert not any(format_check(orig, "Answer: A\nRationale: Drawing can provide a healthy outlet, and it is crucial to seek help.").values())


def test_evaluate_checks():
    rec = Record(prompt_id="p", teacher="t", choice="A", reasons=["r1", "r2"], conditions=["c1"], strength="clear",
                 source_text="Answer: A\nRationale: r1, and r2, as long as c1.")
    good = {"choice": "A", "candidate_reasons": ["r1", "r2"], "reasons_entailed": [True, True], "new_reasons": [], "conditions_entailed": [True],
            "conditions_as_facts": [], "intensifiers_added": [], "hedges_removed": [], "strength": "clear", "register": "formal"}
    c = evaluate_checks(rec, "Answer: A\nRationale: ...", good, "F")
    assert c["kept"]
    # judge-reported intensification, a condition stated as fact, or a merged reason each fail the item
    assert not evaluate_checks(rec, "Answer: A\nRationale: ...", {**good, "intensifiers_added": ["clearly"]}, "F")["strength"]
    assert not evaluate_checks(rec, "Answer: A\nRationale: ...", {**good, "conditions_as_facts": ["c1"]}, "F")["conditions"]
    # the judge may segment two entailed reasons as one proposition; that is not a content change
    assert evaluate_checks(rec, "Answer: A\nRationale: ...", {**good, "candidate_reasons": ["r1 and r2"]}, "F")["reasons"]
    assert not evaluate_checks(rec, "Answer: A\nRationale: ...", {**good, "candidate_reasons": ["r1", "r2", "r2 again"]}, "F")["reasons"]
    # lexical check catches intensification even when the judge misses it
    assert not evaluate_checks(rec, "Answer: A\nRationale: It is clearly essential: r1 and r2, given c1.", good, "F")["strength"]
    # an invented condition on a record without conditions, or added advisory framing, fail lexically
    rec0 = Record(prompt_id="p", teacher="t", choice="A", reasons=["r1"], conditions=[], strength="clear", source_text="Answer: A\nRationale: r1.")
    good0 = {**good, "candidate_reasons": ["r1"], "reasons_entailed": [True], "conditions_entailed": [], "register": "conversational"}
    assert not evaluate_checks(rec0, "Answer: A\nRationale: r1, as long as you can.", good0, "C")["conditions"]
    assert not evaluate_checks(rec0, "Answer: A\nRationale: You're better off doing r1.", good0, "C")["strength"]
    assert evaluate_checks(rec0, "Answer: A\nRationale: r1, and that's it.", good0, "C")["kept"]
    # judge-reported modal change, or process text, each fail the item
    assert not evaluate_checks(rec0, "Answer: A\nRationale: r1, and that's it.", {**good0, "strength_changed": True}, "C")["strength"]
    assert not evaluate_checks(rec0, "Answer: A\nRationale: r1.\nRevised to:\nAnswer: A\nRationale: r1!", good0, "C")["format"]
    bad_style = evaluate_checks(rec, "Answer: A\nRationale: ...", {**good, "register": "conversational"}, "F")
    assert not bad_style["kept"] and bad_style["choice"]
    new_reason = evaluate_checks(rec, "Answer: A\nRationale: ...", {**good, "new_reasons": ["extra"]}, "F")
    assert not new_reason["reasons"]
    wrong_letter = evaluate_checks(rec, "Answer: B\nRationale: ...", good, "F")
    assert not wrong_letter["choice"] and not wrong_letter["kept"]


def test_clean_rewrite_and_feedback():
    from vcd.rewrite.pipeline import build_feedback, clean_rewrite

    two = "Answer: B\nRationale: first block.\n\nCorrected response:\nAnswer: B\nRationale: second block."
    assert clean_rewrite(two) == "Answer: B\nRationale: first block."
    assert clean_rewrite("Answer: A\nRationale: fine.") == "Answer: A\nRationale: fine."
    assert clean_rewrite("**Answer:** B\n**Rationale:** It is `fine`.") == "Answer: B\nRationale: It is fine."
    rec = Record(prompt_id="p", teacher="t", choice="A", reasons=["r1", "r2"], conditions=[], strength="clear", source_text="Answer: A\nRationale: r1. r2.")
    judged = {"choice": "A", "candidate_reasons": ["r1", "r2", "extra"], "reasons_entailed": [True, True], "new_reasons": ["extra"], "conditions_entailed": [], "strength": "clear", "register": "formal"}
    checks = evaluate_checks(rec, "Answer: A\nRationale: r1. r2. You should do extra.", judged, "C")
    fb = build_feedback(rec, checks, judged, "C")
    assert "3 reasons where the original has 2" in fb and "extra" in fb and "should" in fb
    # register is gated lexically: an uncontracted phrase and a formal word are named in the feedback
    formal_c = evaluate_checks(rec, "Answer: A\nRationale: It is r1, and r2 will assist.", ok := {**judged, "candidate_reasons": ["r1", "r2"], "new_reasons": []}, "C")
    assert not formal_c["style"] and "it is" in build_feedback(rec, formal_c, ok, "C") and "assist" in build_feedback(rec, formal_c, ok, "C")
    ok = {**judged, "candidate_reasons": ["r1", "r2"], "new_reasons": [], "register": "conversational"}
    assert build_feedback(rec, evaluate_checks(rec, "Answer: A\nRationale: r1, and r2.", ok, "C"), ok, "C") == ""


def test_split_rationale():
    from vcd.rewrite.pipeline import _strip_sentence_output, split_rationale

    src = "Answer: A  \nRationale: Keeping promises matters. It builds trust, e.g. with Dr. Smith. Also, you promised!"
    assert split_rationale(src) == ["Keeping promises matters.", "It builds trust, e.g. with Dr. Smith.", "Also, you promised!"]
    assert _strip_sentence_output('Rewritten sentence: "Keeping promises matters."\nNote: done') == "Keeping promises matters."
    assert _strip_sentence_output("Keeping promises matters, doesn't change to: Keeping promises matters.") == "Keeping promises matters."
    assert _strip_sentence_output("It helps, which could help keep the species, doesn't change to: It helps.") == "It helps, which could help keep the species."


def test_register_check():
    from vcd.rewrite.pipeline import register_check

    plain = "Answer: A\nRationale: It's important to keep your word. So you'd better help, but don't overdo it."
    assert not any(register_check(plain, "C").values())
    formal = "Answer: A\nRationale: It is important to maintain your word. However, you should not overdo it in order to assist."
    r = register_check(formal, "C")
    assert r["uncontracted"] == ["it is", "should not"] and r["formal_connectives"] == ["however", "in order to"] and r["formal_words"] == ["assist", "maintain"]
    assert register_check(formal, "F") == {"contractions": []}
    assert register_check(plain, "F")["contractions"] == ["don't", "it's", "you'd"]
    assert register_check("Answer: A\nRationale: You've got rights under the Individuals with Disabilities Education Act.", "C")["formal_words"] == []
    # possessive 's is not a contraction
    assert register_check("Answer: A\nRationale: The gallery's reputation matters.", "F")["contractions"] == []
