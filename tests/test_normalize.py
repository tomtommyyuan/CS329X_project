from vcd.data.normalize import (
    first_person_to_imperative,
    normalize_action,
    second_to_first_person,
    split_trailing_question,
)


def test_split_trailing_question_daily_dilemmas():
    text = (
        "You're a project manager in a marketing firm. You notice a colleague using company resources "
        "for a personal project during office hours, undermining the company's policy. "
        "Should you take initiative and report this to your superior?"
    )
    body, q = split_trailing_question(text)
    assert body.endswith("undermining the company's policy.")
    assert q.startswith("Should you take initiative")


def test_split_trailing_question_keeps_all_if_only_question():
    body, q = split_trailing_question("Should you do it?")
    assert body == "Should you do it?" and q == ""


def test_normalize_action():
    assert normalize_action("Report the colleague")[0] == "Report the colleague."
    assert normalize_action("Not report the colleague")[0] == "Do not report the colleague."
    a, flags = normalize_action("Report")
    assert a == "Report." and "short_action" in flags


def test_normalize_action_degerund():
    a, flags = normalize_action("Reading the journal")
    assert a == "Read the journal." and "degerund" in flags
    assert normalize_action("Not reading the journal")[0] == "Do not read the journal."
    assert normalize_action("Continuing the relationship")[0] == "Continue the relationship."
    assert normalize_action("Not confronting the owner")[0] == "Do not confront the owner."
    assert normalize_action("Bring the documents")[0] == "Bring the documents."  # base verb ending in -ing


def test_first_person_to_imperative():
    assert first_person_to_imperative("I do not throw the grenade.")[0] == "Do not throw the grenade."
    assert first_person_to_imperative("I throw the grenade.")[0] == "Throw the grenade."
    assert first_person_to_imperative("I refuse to assist in suicide.")[0] == "Refuse to assist in suicide."
    assert first_person_to_imperative("I tell my mother that I love her.")[0] == "Tell your mother that you love her."
    out, flags = first_person_to_imperative("Throw the grenade.")
    assert out == "Throw the grenade." and "action_not_first_person" in flags


def test_second_to_first_person():
    text = (
        "Your mother is terminally ill, in constant pain, and wishes to end her life. "
        "She asks you to help to assist her in suicide."
    )
    out, flags = second_to_first_person(text)
    assert out.startswith("My mother is terminally ill")
    assert "She asks me to help" in out
    assert "t3_auto" in flags and "t3_residual_you" not in flags


def test_second_to_first_person_subject():
    out, _ = second_to_first_person("You're a soldier in a war. You notice a colleague. He trusts you.")
    assert out == "I'm a soldier in a war. I notice a colleague. He trusts me."
    out, _ = second_to_first_person("You promised a friend to keep a secret. Your sister presses you to reveal it.")
    assert out == "I promised a friend to keep a secret. My sister presses me to reveal it."


def test_detect_person():
    from vcd.data.normalize import detect_person

    assert detect_person("You're a manager. Your team is late.") == "second"
    assert detect_person("Sarah is in a relationship with John. She fears leaving him.") == "third"
    assert detect_person("I run a small shop and my landlord raised the rent.") == "first"
