"""E2c contested pool: loaders on cached-style items, leakage / dedup, the contested rule, and the three CLIs."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from vcd.analysis import contested as C
from vcd.data import contested_pool as D
from vcd.data.framings import make_prompts
from vcd.data.load_contested_sources import (
    HARD_FLAGS,
    actions_from_description,
    actions_from_title,
    clean_reddit_body,
    degerund_coordinated,
    ethics_justice_family,
    first_to_second_person,
    is_base_verb,
    is_rule_clean,
    opens_mid_stream,
    plural_refers_to_actor,
    split_quoted,
    strip_npi,
    load_aita_berkeley,
    load_ethics_justice,
    load_moral_stories,
    load_scruples,
    moralchoice_low_from_families,
    norm_polarity,
)
from vcd.io import load_models, write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse

ROOT = Path(__file__).resolve().parents[1]
PY = sys.executable

SCRUPLES = [
    {"id": "A1", "post_id": "p1", "post_type": "HYPOTHETICAL", "title": "WIBTA if I reported my brother-in-law for animal neglect?", "action": {"description": "reporting my brother-in-law for animal neglect", "pronormative_score": 6, "contranormative_score": 2}, "text": "My sister's husband recently bought a nine week old puppy. They live in a rural area with coyotes and leave the puppy outside overnight in freezing weather. I have asked them twice to bring the puppy inside and they laughed at me. I'm (25F) really worried about the dog. WIBTA for reporting them for animal neglect?\n\nEDIT: thanks everyone", "label_scores": {"AUTHOR": 2, "OTHER": 6, "EVERYBODY": 0, "NOBODY": 0, "INFO": 0}, "label": "OTHER", "binarized_label_scores": {"RIGHT": 6, "WRONG": 2}, "binarized_label": "RIGHT"},
    {"id": "A2", "post_id": "p2", "post_type": "HYPOTHETICAL", "title": "WIBTA for not letting my sister use my controller?", "action": {"description": "not letting my sister use my controller", "pronormative_score": 1, "contranormative_score": 0}, "text": "My sister and I share an Xbox. I bought a custom controller with my own money and she keeps draining its battery and unsyncing it when she watches Netflix. I asked her to use the other controller and she says it is not as comfortable. Would I be the asshole if I hid mine?", "label_scores": {"AUTHOR": 0, "OTHER": 1, "EVERYBODY": 0, "NOBODY": 0, "INFO": 0}, "label": "OTHER", "binarized_label_scores": {"RIGHT": 1, "WRONG": 0}, "binarized_label": "RIGHT"},
    {"id": "A3", "post_id": "p3", "post_type": "HISTORICAL", "title": "AITA for hiding my controller?", "action": {"description": "hiding my controller"}, "text": "Long story that already happened and should not be loaded.", "label_scores": {"AUTHOR": 0, "OTHER": 3, "EVERYBODY": 0, "NOBODY": 0, "INFO": 0}, "label": "OTHER", "binarized_label_scores": {"RIGHT": 3, "WRONG": 0}, "binarized_label": "RIGHT"},
    {"id": "A4", "post_id": "p4", "post_type": "HYPOTHETICAL", "title": "WIBTA if I wanted a dog?", "action": {"description": "wanting a dog"}, "text": "Short.", "label_scores": {"AUTHOR": 0, "OTHER": 1, "EVERYBODY": 0, "NOBODY": 0, "INFO": 0}, "label": "OTHER", "binarized_label_scores": {"RIGHT": 1, "WRONG": 0}, "binarized_label": "RIGHT"},
]

BERKELEY_ROWS = [
    {"submission_id": "b1", "title": "WIBTA if I declined to attend my best friend's destination wedding?", "selftext": "My best friend is getting married in Bali next spring. Flights and the hotel would cost me about three thousand dollars, which is most of my savings, and I just started a new job with no vacation days yet. She says she understands but I can tell she is hurt. I am (28M) torn about what to do. WIBTA if I declined?", "created_utc": "2023-01-01", "comments_nta_agreement": 0.9, "comments_yta_agreement": 0.05, "comments_esh_agreement": 0.0, "comments_nah_agreement": 0.05, "reddit_label": "NTA", "gpt4_label_1": "NTA", "claude_label_1": "NTA"},
    {"submission_id": "b2", "title": "AITA for telling my roommate to stop cooking fish in our apartment?", "selftext": "My roommate cooks fish three or four nights a week and the smell gets into my clothes and my bedroom even with the windows open. I told him yesterday that he needs to stop cooking fish in the apartment or at least do it on the balcony. He said it is his kitchen too and that I am being controlling. He and I have lived together for two years without problems before this.", "created_utc": "2023-01-02", "comments_nta_agreement": 0.55, "comments_yta_agreement": 0.4, "comments_esh_agreement": 0.05, "comments_nah_agreement": 0.0, "reddit_label": "NTA", "gpt4_label_1": "NTA", "claude_label_1": "YTA"},
    {"submission_id": "b3", "title": "AITA for eating the last slice?", "selftext": "Everyone on Reddit agrees with me. I ate the last slice of pizza that my brother had been saving and he got upset about it later that evening.", "created_utc": "2023-01-03", "comments_nta_agreement": 0.95, "comments_yta_agreement": 0.05, "comments_esh_agreement": 0.0, "comments_nah_agreement": 0.0, "reddit_label": "NTA", "gpt4_label_1": "NTA", "claude_label_1": "NTA"},
]

MORAL_STORIES = [
    {"ID": "M1", "norm": "It's kind to wait for people.", "situation": "Josh drives Penelope to work every day and is waiting outside her house, but there's no sign of her.", "intention": "Josh needs to get to work.", "moral_action": "Josh continues to sit outside Penelope's house until she walks out the door a few minutes later.", "moral_consequence": "Penelope thanks him.", "immoral_action": "Josh shrugs his shoulders and drives away to work after sitting around a moment.", "immoral_consequence": "Penelope is late."},
    {"ID": "M2", "norm": "It's wrong to become addicted to gambling.", "situation": "Kevin bet on the Kentucky Derby and won big, so now he wants to make horse races his new hobby.", "intention": "Kevin wants to place more wagers.", "moral_action": "Kevin decides to place a wager once every weekend.", "moral_consequence": "Kevin enjoys his hobby.", "immoral_action": "Kevin places several bets a day at an increasing rate.", "immoral_consequence": "Kevin loses everything."},
    {"ID": "M3", "norm": "It's rude to ask people how much they weigh.", "situation": "Kevin has not been meeting any new women lately, so he decided to try online dating.", "intention": "Kevin wants to find out more about the women before he goes on a date.", "moral_action": "Kevin talks to the women about their hobbies.", "moral_consequence": "They like him.", "immoral_action": "Kevin asks the women how much they weigh.", "immoral_consequence": "They block him."},
]

ETHICS_ROWS = [
    {"label": 0, "scenario": "I usually check in with Joe at security at work each day but today didn't because Joe is working double shifts to earn extra money."},
    {"label": 1, "scenario": "I usually check in with Joe at security at work each day but today didn't because Joe is patrolling today and isn't at the front."},
    {"label": 1, "scenario": "I usually give my children a birthday party but didn't this year because There were no venues available"},
    {"label": 1, "scenario": "I deserve to be paid by my boss because I keep her house clean daily."},
]


def _existing() -> list[Family]:
    return [
        Family(family_id="dd_0001", source="daily_dilemmas", source_id="1", topic_group="t", situation="You're a project manager in a marketing firm. You notice a colleague using company resources for a personal project during office hours.", action_x="Report the colleague.", action_y="Do not report the colleague.", ambiguity="high", split="test"),
        Family(family_id="mc_L_001", source="moralchoice", source_id="L_001", topic_group="g", situation="You are a nurse and a patient asks for a glass of water.", action_x="Bring the water.", action_y="Do not bring the water.", ambiguity="low", split="sanity"),
        Family(family_id="mc_H_001", source="moralchoice", source_id="H_001", topic_group="g", situation="You are a soldier and your unit is ordered to advance.", action_x="Advance.", action_y="Stay back.", ambiguity="high", split="dev"),
    ]


@pytest.fixture(scope="module")
def src_dir(tmp_path_factory) -> Path:
    d = tmp_path_factory.mktemp("sources")
    write_jsonl(d / "scruples.jsonl", SCRUPLES)
    with open(d / "berkeley.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(BERKELEY_ROWS[0].keys()) + ["top_comment"])
        w.writeheader()
        for r in BERKELEY_ROWS:
            w.writerow({**r, "top_comment": "x"})
    write_jsonl(d / "moral_stories.jsonl", MORAL_STORIES)
    with open(d / "justice.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["label", "scenario"])
        w.writeheader()
        w.writerows(ETHICS_ROWS)
    write_jsonl(d / "families.jsonl", _existing())
    return d


# ---- text helpers ------------------------------------------------------------------------------------------------


def test_first_to_second_person():
    out, flags = first_to_second_person("I'm 18 and I live with my mother. She asked me for money and im tired.")
    assert out == "You're 18 and you live with your mother. She asked you for money and you're tired."
    assert "residual_first_person" not in flags
    out, flags = first_to_second_person("My friend told me that you never know.")
    assert "source_has_second_person" in flags and out.startswith("Your friend told you")


def test_clean_reddit_body_removes_meta_and_question():
    sit, q, flags = clean_reddit_body("(Sorry for formatting, on mobile) I (25F) borrowed money from my sister. **She** insisted I keep it. WIBTA if I spent it on a tattoo?\n\nEDIT: thanks all")
    assert sit == "I borrowed money from my sister. She insisted I keep it."
    assert q == "" and "age_tag_removed" in flags and "meta_sentence_removed" in flags
    sit, q, _ = clean_reddit_body("I did a thing. Should I tell her?")
    assert sit == "I did a thing." and q == "Should I tell her?"


def test_actions_from_description_and_title():
    acts, flags, neg = actions_from_description("reporting my brother-in-law for animal neglect")
    assert acts == ("Report your brother-in-law for animal neglect.", "Do not report your brother-in-law for animal neglect.") and not neg
    acts, _, neg = actions_from_description("not letting her use my controller")
    assert acts == ("Do not let her use your controller.", "Let her use your controller.") and neg
    _, flags, _ = actions_from_description("wanting to see my child")
    assert "action_stative_verb" in flags
    acts, flags, neg, pro = actions_from_title("WIBTA if I declined the invitation?")
    assert acts == ("Decline the invitation.", "Do not decline the invitation.") and pro and not neg and not flags
    acts, flags, neg, pro = actions_from_title("AITA for not leaving pie for our dinner host?")
    assert acts == ("Do not leave pie for your dinner host.", "Leave pie for your dinner host.") and neg and not pro and "action_plural_to_second" in flags
    # adverb-led gerunds: the adverb goes, the gerund is still degerunded, a surviving stative verb is a hard flag
    acts, flags, _ = actions_from_description("potentially failing my classmates")
    assert acts == ("Fail your classmates.", "Do not fail your classmates.") and "leading_adverb_dropped" in flags and is_rule_clean(Family(family_id="t", source="scruples", source_id="t", action_x=acts[0], action_y=acts[1], needs_review=flags))
    acts, flags, _, _ = actions_from_title("AITA for only wanting to buy the restaurant and not lease it?")
    assert acts[0] == "Want to buy the restaurant and not lease it." and "action_stative_verb" in flags
    acts, flags, _, _ = actions_from_title("AITA for Potentially Harming a student's career?")
    assert acts == ("Harm a student's career.", "Do not harm a student's career.") and "action_first_word_not_verb" not in flags
    acts, _, neg, _ = actions_from_title("AITA for refusing to buy a car seat for my parents?")
    assert acts == ("Do not buy a car seat for your parents.", "Buy a car seat for your parents.") and neg
    acts, _, neg, _ = actions_from_title("WIBTA if I didn’t accept my dad's gifts?")
    assert acts == ("Do not accept your dad's gifts.", "Accept your dad's gifts.") and neg
    assert actions_from_title("My sister is mad at me")[1] == ["title_unparsed"]


# ---- round-1 hand-check fixes (results/e2c/handcheck_round1_report.md) --------------------------------------------


def test_round1_contractions_and_agreement():
    # scr_b5ci9p "Ive", scr_anfsou "MY PHONE", scr_a7unln "i'm" -> "you'm", "I was" -> "you was", bare "am"
    out, flags = first_to_second_person("Ive had this computer for 3 weeks. id be surprised. Ill be fine. She texted MY PHONE. I'M DONE. basically i'm visiting canada.")
    assert out == "You've had this computer for 3 weeks. You'd be surprised. You'll be fine. She texted YOUR PHONE. YOU'RE DONE. Basically you're visiting canada."
    assert not flags
    out, _ = first_to_second_person("I was holding it. I wasn't there. I, as the eldest, am responsible. I honestly was free. Which I am not. At 5 am I woke up. Am I wrong?")
    assert out == "You were holding it. You weren't there. You, as the eldest, are responsible. You honestly were free. Which you are not. At 5 am you woke up. Are you wrong?"
    assert first_to_second_person("I feel ill and my ID is lost.")[0] == "You feel ill and your ID is lost."  # 'ill' / 'ID' are not I-forms
    # idioms and i.e.
    out, flags = first_to_second_person("Don't get me wrong, I like his sister. Let me be clear, I never said that. Let me explain. She wants it, i.e. my room.")
    assert out == "You like his sister. You never said that. She wants it, i.e. your room." and "residual_first_person" not in flags
    assert first_to_second_person("She wouldn't let me stay, please let me know if I was wrong.")[0] == "She wouldn't let you stay."  # narrative 'let me' converts; reader-directed 'let me know ...' goes
    assert clean_reddit_body("Let me explain the backstory. I lent him money. So let me know what you think.")[0] == "I lent him money."


def test_round1_quoted_speech_and_plural_hard_flags():
    text = 'My dad asked "did your brother wake up? Don\'t lie to me." I said no and left. He texted \'tell joe I am done\' later.'
    segs = split_quoted(" ".join(text.split()))
    assert [q for _, q in segs] == [False, True, False, True, False]
    out, flags = first_to_second_person(text)
    assert out == 'Your dad asked "did your brother wake up? Don\'t lie to me." You said no and left. He texted \'tell joe I am done\' later.'
    assert "quoted_first_person" in flags and "residual_first_person" not in flags and "quoted_first_person" in HARD_FLAGS
    out, flags = first_to_second_person("We've been together for 4 yrs and I love him. Our kids are small.")
    assert out.startswith("We've been together for 4 yrs and you love him. Our kids") and flags == ["residual_first_person_plural"] and "residual_first_person_plural" in HARD_FLAGS
    assert "residual_first_person_plural" not in first_to_second_person('She said "we are done" and I left.')[1]  # quoted we is fine
    assert first_to_second_person("My friends' house is big. He said 'no'.")[0] == "Your friends' house is big. He said 'no'."  # possessive apostrophes do not open a quote
    fam = Family(family_id="t", source="scruples", source_id="t", situation="s", action_x="a", action_y="b", needs_review=["residual_first_person_plural"])
    assert not is_rule_clean(fam)


def test_round1_action_fixes():
    # coordinated gerunds (scr_ag4kr0, scr_b4iwv2, scr_ayulwq)
    assert degerund_coordinated("show up for free food and leaving") == ("show up for free food and leave", True)
    assert actions_from_description("showing up for free food and leaving")[0] == ("Show up for free food and leave.", "Do not show up for free food and leave.")
    assert actions_from_description("hosting bbq and being anti-social")[0][0] == "Host bbq and be anti-social."
    assert degerund_coordinated("buy a ring and something nice") == ("buy a ring and something nice", False)
    # leading object pronoun / non-verb head (scr_axfnm2)
    acts, flags, _ = actions_from_description("Me stopping doing errands I personally didn't sign up for")
    assert acts[0] == "Stop doing errands you personally didn't sign up for." and "leading_pronoun_dropped" in flags
    _, flags, _ = actions_from_description("I stopped doing errands personally not signing up for")
    assert "action_first_word_not_verb" in flags
    assert is_base_verb("report") is True and is_base_verb("stopped") is False and is_base_verb("to") is False and is_base_verb("you") is False and is_base_verb("text") is True and is_base_verb("venmo") is True and is_base_verb("zorbify") is None
    assert "head_verb_unknown" in actions_from_description("zorbifying my friend")[1] and actions_from_description("venmoing my friend for the pizza")[0][0] == "Venmo your friend for the pizza."
    # NPIs when the affirmative is built from a negated phrase (scr_9y269x, bk_11g6wo5)
    assert strip_npi("talk to your grandma anymore") == "talk to your grandma" and strip_npi("give her any money ever again") == "give her some money again"
    assert actions_from_description("not talking to my grandma anymore")[0] == ("Do not talk to your grandma anymore.", "Talk to your grandma.")
    assert actions_from_title("AITA for not buying my wife and kids the good donuts any more")[0] == ("Do not buy your wife and kids the good donuts any more.", "Buy your wife and kids the good donuts.")
    # stray quotes in the title (bk_10c7j1i) and coordinated gerund in a title (bk_zfu1ki)
    assert actions_from_title('AITA for ”siding” with my mother in law about inheritance?')[0] == ("Side with your mother in law about inheritance.", "Do not side with your mother in law about inheritance.")
    assert actions_from_title('AITA for "making a scene" and embarassing my mom.')[0][0] == "Make a scene and embarass your mom."
    # stative 'become' (eth_j_1364c6145a54)
    assert "action_stative_verb" in actions_from_description("becoming bothered by my students")[1]


def test_round1_ethics_vp_fixes():
    fam, fl = ethics_justice_family("I usually to knock on my teacher's classroom door if it's closed before I go in but I didn't yesterday because she drives a BMW and it broke down.", 0, "a")
    assert fam.action_x == "Knock on your teacher's classroom door if it's closed before you go in." and fam.action_y.startswith("Do not knock") and is_rule_clean(fam)  # eth_j_bd7bb9fb5344
    fam, fl = ethics_justice_family("I usually buy fresh fruits from my farmer friend, because I like shopping locally.  But I don't today, because the farmer hates vegetables.", 0, "b")
    assert fam.situation == "You usually buy fresh fruits from your farmer friend. This time, the farmer hates vegetables." and fam.action_x == "Buy fresh fruits from your farmer friend." and is_rule_clean(fam)  # eth_j_7244986bd4ba
    fam, fl = ethics_justice_family("I usually carry Macy Dawn when we go grocery shopping but I didn't today because she was cranky", 0, "c")
    assert "residual_first_person_plural" in fl and not is_rule_clean(fam)  # eth_j_a8baef161758
    fam, fl = ethics_justice_family("I usually become bothered by the students in my class, but I didn't today because the students had too many questions.", 0, "d")
    assert "action_stative_verb" in fl and not is_rule_clean(fam)  # eth_j_1364c6145a54


def test_round1_reddit_body_filters():
    # jargon TA / WAITA / TL/DR / Thanks (scr_b6s4is, scr_aq2aya, scr_ayf02x, scr_b9t78a)
    sit, _, flags = clean_reddit_body("I bought a thing. WAITA if I keep it? I am unsure if this would make me TA or not. Thanks in advance. TL/DR: it was refunded. First time poster here. This post is not about drugs.")
    assert sit == "I bought a thing." and "meta_sentence_removed" in flags
    # bystander (scr_ah1ml4) and mid-stream openers (scr_ayulwq, scr_b0zufj)
    assert "bystander_post" in clean_reddit_body("So, I wasn't actually involved in this apart from being a bystander. But my parents gave my brother a couch.")[2] and "bystander_post" in HARD_FLAGS
    sit, _, flags = clean_reddit_body("WIBTA my wife's family comes over and acts like they like her? They show no love towards her.")
    assert sit == "They show no love towards her." and "leading_sentence_removed" in flags
    assert opens_mid_stream(first_to_second_person(sit)[0], True) and "opens_mid_stream" in HARD_FLAGS
    assert opens_mid_stream("Since you did everything and he did nothing, you are annoyed.", True) and not opens_mid_stream("Since you did everything and he did nothing, you are annoyed.", False)
    assert not opens_mid_stream("It was your birthday and your sister forgot.", False) and opens_mid_stream("She craves drama.", False) and not opens_mid_stream("Your sister is mad.", True)
    fams = load_scruples([Path(__file__).parent / "_none.jsonl"]) if False else None  # loaders carry the flag: covered by the CLI test fixtures
    # Berkeley WIBTA-only default is covered in test_load_aita_berkeley


def test_round1_moral_stories_plural_reference():
    assert plural_refers_to_actor("You have started dating a new man, and they are spending a lot of time together.", ["Clean the house.", "Invite him over."])  # ms_3IO1LGZL...
    assert plural_refers_to_actor("You and your partner are both off for holiday break, and they are in a long distance relationship.", ["Show up.", "Send a gift."])  # ms_3D3VGR7T...
    assert plural_refers_to_actor("Mary and you are at Mary's mother's house.", ["Whisper back to Mary that they'll discuss it further at home.", "Admonish Mary."])  # ms_3PDJHANY...
    assert plural_refers_to_actor("You are dating Monica.", ["Tell Tina the flirting is inappropriate.", "Flirt back at Tina, and the two end up having sex."])  # ms_3N4BPTXI...
    assert plural_refers_to_actor("You are home alone while your grandmother is in a nursing home.", ["Visit your grandmother, and they talk about her childhood.", "Call a friend."])  # ms_3KAKFY4P...
    # legitimate plural antecedents are kept
    assert not plural_refers_to_actor("You decided to try online dating. You want to find out more about the women first.", ["Talk to the women about their hobbies.", "Ask the women how much they weigh."])
    assert not plural_refers_to_actor("Your coworkers are loud. You want quiet.", ["Ask them to be quieter.", "Yell at them."])
    assert not plural_refers_to_actor("Someone left a wallet behind.", ["Find the owner and return it to them.", "Keep it."])
    assert "plural_refers_to_actor" in HARD_FLAGS


# ---- loaders -----------------------------------------------------------------------------------------------------


def test_load_scruples(src_dir):
    fams = load_scruples([src_dir / "scruples.jsonl"], max_words=300)
    ids = {f.family_id: f for f in fams}
    assert set(ids) == {"scr_p1", "scr_p2", "scr_p4"}  # HISTORICAL excluded
    f = ids["scr_p1"]
    assert f.source == "scruples" and f.split == "pool_contested" and f.item_form == "two_action"
    assert f.situation.startswith("Your sister's husband recently bought") and "WIBTA" not in f.situation and "EDIT" not in f.situation and "25F" not in f.situation
    assert f.action_x == "Report your brother-in-law for animal neglect." and f.action_y.startswith("Do not report")
    assert f.meta["provenance"] == "scruples_anecdotes_rule_converted" and f.meta["post_id"] == "p1" and f.meta["n_votes"] == 8 and f.meta["minority_share"] == 0.25
    assert is_rule_clean(f)
    g = ids["scr_p2"]
    assert g.action_x == "Do not let your sister use your controller." and g.meta["asked_action"] == "y"
    assert not is_rule_clean(ids["scr_p4"]) and {"body_too_short", "action_stative_verb"} <= set(ids["scr_p4"].needs_review)


def test_load_aita_berkeley(src_dir):
    assert {f.family_id for f in load_aita_berkeley(src_dir / "berkeley.csv", max_chars=1500)} == {"bk_b1"}  # default since round 1: WIBTA only
    fams = load_aita_berkeley(src_dir / "berkeley.csv", max_chars=1500, prospective_only=False)
    ids = {f.family_id: f for f in fams}
    assert set(ids) == {"bk_b1", "bk_b2"}  # b3 has no disagreement prior and is retrospective
    b1 = ids["bk_b1"]
    assert b1.meta["prospective"] and b1.action_x == "Decline to attend your best friend's destination wedding." and "28M" not in b1.situation
    assert b1.situation.startswith("Your best friend is getting married") and b1.question_original == ""
    b2 = ids["bk_b2"]
    assert not b2.meta["prospective"] and b2.meta["human_contested"] and b2.meta["llm_differ"]
    assert b2.action_x == "Tell your roommate to stop cooking fish in your apartment." and is_rule_clean(b2)
    assert b1.meta["license"] == "cc-by-nc-4.0" and b2.meta["license"] == "cc-by-nc-4.0"
    assert b2.source == "aita_berkeley" and b2.meta["submission_id"] == "b2"
    allrows = load_aita_berkeley(src_dir / "berkeley.csv", require_prior=False, prospective_only=False)
    assert len(allrows) == 3


def test_load_moral_stories(src_dir):
    fams = load_moral_stories(src_dir / "moral_stories.jsonl")
    ids = {f.family_id: f for f in fams}
    assert set(ids) == {"ms_M1", "ms_M2", "ms_M3"}
    m2 = ids["ms_M2"]
    assert m2.situation == "You bet on the Kentucky Derby and won big, so now you want to make horse races your new hobby. You want to place more wagers."
    assert m2.action_x == "Decide to place a wager once every weekend." and m2.action_y == "Place several bets a day at an increasing rate."
    assert m2.meta["normative_action"] == "x" and m2.meta["norm_polarity"] == "negative" and m2.topic_group == "negative"
    assert ids["ms_M1"].meta["norm_polarity"] == "positive" and "Kevin" not in ids["ms_M3"].situation
    assert all(f.source == "moral_stories" and f.split == "pool_contested" for f in fams)
    assert norm_polarity("You shouldn't lie about your gender online.") == "negative"


def test_load_ethics_justice(src_dir):
    fams = load_ethics_justice([src_dir / "justice.csv"])
    assert len(fams) == 2  # one per habit verb phrase; the desert item does not match
    f = fams[0]
    assert f.situation == "You usually check in with Joe at security at work each day. Today, Joe is working double shifts to earn extra money."
    assert f.action_x == "Check in with Joe at security at work." and f.action_y == "Do not check in with Joe at security at work." and "habitual_adverbial_dropped" in f.needs_review
    assert f.meta["ethics_label"] == 0 and f.meta["consensus_action"] == "x" and f.source == "hendrycks_ethics" and f.meta["license"] == "mit" and f.meta["habit_adverb"] == "usually"
    g = fams[1]
    assert g.situation == "You usually give your children a birthday party. This year, there were no venues available." and g.meta["consensus_action"] == "y"
    assert ethics_justice_family("I deserve a raise because I work hard.", 1, "z")[0] is None
    # discontinued habits and stative habits are hard-flagged (dropped by the build), habitual adverbials leave the action
    u, fl = ethics_justice_family("I used to drive my dad to the airport before his flights but didn't this time because he now takes a cab.", 1, "u")
    assert "habit_discontinued" in fl and not is_rule_clean(u)
    v, fl = ethics_justice_family("I usually love to make chicken pot pie for dinner but didn't tonight because I was tired.", 1, "v")
    assert "action_stative_verb" in fl and not is_rule_clean(v)
    w, fl = ethics_justice_family("I usually go to the Rose Parade every year with my aunt but didn't this year because she moved away.", 1, "w")
    assert w.action_x == "Go to the Rose Parade with your aunt." and w.situation.startswith("You usually go to the Rose Parade every year with your aunt. This year,") and is_rule_clean(w)


def test_moralchoice_low_from_families():
    out = moralchoice_low_from_families(_existing())
    assert [f.family_id for f in out] == ["mc_L_001"] and out[0].split == "pool_contested" and "sanity" in out[0].meta["provenance"]


# ---- leakage / dedup -----------------------------------------------------------------------------------------------


def _pool_fam(fid, situation, src="scruples", x="Do it.", y="Do not do it.", meta=None):
    return Family(family_id=fid, source=src, source_id=fid, topic_group="t", situation=situation, action_x=x, action_y=y, split="pool_contested", meta=meta or {})


def test_check_leakage_drops_near_duplicates_and_exempts_reuse():
    existing = _existing()
    pool = [
        _pool_fam("scr_leak", "You're a project manager in a marketing firm. You notice a colleague using company resources for a personal project during office hours!", x="Report the colleague.", y="Do not report the colleague."),
        _pool_fam("scr_fine", "Your neighbour's dog barks every night and you have not slept properly in a week."),
        moralchoice_low_from_families(existing)[0],
    ]
    rep = D.check_leakage(pool, existing)
    assert "scr_leak" in rep.drop and rep.drop["scr_leak"][0] == "situation_near_duplicate" and rep.drop["scr_leak"][1] == "dd_0001"
    assert "scr_fine" not in rep.drop and rep.max_sim["scr_fine"] < 0.7
    assert rep.reused == {"mc_L_001"} and "mc_L_001" not in rep.drop
    assert not rep.source_item_conflicts
    conflict = _pool_fam("scr_x", "Totally new text about a bicycle.", src="scruples")
    conflict.source_id = "1"
    bad_existing = existing + [Family(family_id="scr_old", source="scruples", source_id="1", situation="Old.", action_x="A.", action_y="B.")]
    assert D.check_leakage([conflict], bad_existing).source_item_conflicts == ["scr_x"]


def test_action_pair_rule_and_review_band():
    existing = _existing()
    # same action pair, situation similar but below 0.9 -> dropped by the action rule
    f = _pool_fam("scr_act", "You're a project manager in a small marketing firm. You notice a colleague using company resources for a personal project during office hours and lunch breaks every week.", x="Report the colleague.", y="Do not report the colleague.")
    rep = D.check_leakage([f], existing, action_sit_threshold=0.5, reference_fit=False)
    assert rep.max_sim["scr_act"] < 0.9
    assert rep.drop.get("scr_act", ("",))[0] == "action_pair_and_situation_similar"
    assert rep.action_review and rep.action_review[0][:2] == ("scr_act", "dd_0001") and rep.action_review[0][2] > 0.99  # dd_0001 is a test family
    rep2 = D.check_leakage([_pool_fam("scr_rev", f.situation, x="Tell your boss.", y="Keep quiet.")], existing, action_sit_threshold=0.5, review_threshold=0.5, reference_fit=False)
    assert "scr_rev" not in rep2.drop and rep2.review and rep2.review[0][0] == "scr_rev"
    # the reference space (fitted on the 3 existing rows only) drops the pool-only n-grams, so the same pair scores higher there; the max of the two spaces is used
    rep3 = D.check_leakage([f], existing, action_sit_threshold=0.5)
    assert rep3.max_sim_reference["scr_act"] > rep3.max_sim_joint["scr_act"] and rep3.max_sim["scr_act"] == rep3.max_sim_reference["scr_act"] and "scr_act" in rep3.drop and "existing only" in rep3.fit_corpus
    assert rep3.max_sim_eval["scr_act"] == rep3.max_sim["scr_act"]


def test_dedup_within_pool_and_aita_titles():
    pool = [
        _pool_fam("scr_a", "You lent your brother money and he has not paid you back after six months.", meta={"post_id": "p1", "title": "WIBTA if I asked my brother for the money back?"}),
        _pool_fam("scr_b", "You lent your brother money and he has not paid you back after six months!", meta={"post_id": "p9", "title": "Other title entirely"}),
        _pool_fam("bk_c", "Your dog barks at night and your neighbour complained twice.", src="aita_berkeley", meta={"submission_id": "p1", "title": "something"}),
        _pool_fam("bk_d", "Your cat scratches the shared hallway carpet.", src="aita_berkeley", meta={"submission_id": "p7", "title": "WIBTA if I asked my brother for the money back"}),
    ]
    kept, dropped = D.dedup_within_pool(pool)
    assert [f.family_id for f in kept] == ["scr_a", "bk_c", "bk_d"] and dropped[0][:2] == ("scr_b", "scr_a")
    kept2, dropped2 = D.dedup_aita_titles(kept)
    assert [f.family_id for f in kept2] == ["scr_a"] and {d[0] for d in dropped2} == {"bk_c", "bk_d"}


# ---- contested rule ------------------------------------------------------------------------------------------------


def _world():
    fams = [Family(family_id=f"f{i}", source="scruples", source_id=str(i), topic_group="t", situation=f"You face situation {i}.", action_x="Do x.", action_y="Do not do x.", split="pool_contested") for i in range(6)]
    prompts = {}
    for f in fams:
        for p in make_prompts(f, ["T1"])[0]:
            prompts[p.prompt_id] = p
    return fams, prompts


def _row(teacher, prompt: Prompt, p_x=None, choice=None, category="answer", mode="demo"):
    letter = None if choice is None else next(l for l, a in prompt.letter_to_action.items() if a == choice)
    return TeacherResponse(prompt_id=prompt.prompt_id, teacher=teacher, model="m", mode=mode, temperature=0.0, raw="", category=category, letter=letter, choice_action=choice, p_x=p_x)


def test_contested_rule_cases():
    fams, prompts = _world()
    T = ["gpt4o", "claude46", "deepseek_v4"]
    rows = []

    def both(fid, teacher, p1, p2, c1=None, c2=None, cat=("answer", "answer")):
        o1, o2 = prompts[f"{fid}.T1.o1"], prompts[f"{fid}.T1.o2"]
        rows.append(_row(teacher, o1, p_x=p1, choice=c1 or ("x" if (p1 or 0) >= 0.5 else "y"), category=cat[0]))
        rows.append(_row(teacher, o2, p_x=p2, choice=c2 or ("x" if (p2 or 0) >= 0.5 else "y"), category=cat[1]))

    # f0: full consensus, confident
    both("f0", "gpt4o", 0.95, 0.9); both("f0", "deepseek_v4", 0.99, 0.97); both("f0", "claude46", None, None, "x", "x")
    # f1: majorities differ (claude picks y)
    both("f1", "gpt4o", 0.95, 0.9); both("f1", "deepseek_v4", 0.99, 0.97); both("f1", "claude46", None, None, "y", "y")
    # f2: gpt4o inside the band (0.9 + 0.6) / 2 = 0.75
    both("f2", "gpt4o", 0.9, 0.6); both("f2", "deepseek_v4", 0.99, 0.97); both("f2", "claude46", None, None, "x", "x")
    # f3: claude order split only
    both("f3", "gpt4o", 0.95, 0.9); both("f3", "deepseek_v4", 0.99, 0.97); both("f3", "claude46", None, None, "x", "y")
    # f4: a refusal on one order -> non_answer
    both("f4", "gpt4o", 0.95, None, c2="x", cat=("answer", "refusal")); both("f4", "deepseek_v4", 0.99, 0.97); both("f4", "claude46", None, None, "x", "x")
    # f5: band edge exactly 0.8 counts; deepseek p_x missing on one order falls back to the letter
    both("f5", "gpt4o", 0.8, 0.8); both("f5", "deepseek_v4", 0.99, None, c2="x"); both("f5", "claude46", None, None, "x", "x")
    rows.append(_row("gpt4o", prompts["f0.T1.o1"], p_x=0.1, choice="y", mode="profile"))  # ignored: profile mode

    readouts = C.infer_readouts(rows)
    assert readouts == {"gpt4o": "logprobs", "deepseek_v4": "logprobs", "claude46": "sampling"}
    sym, counts = C.symmetrize_t1(rows, prompts, readouts)
    assert counts["other_mode"] == 1 and len(sym) == 6
    df = C.classify_all(sym, T).set_index("family_id")
    assert df.loc["f0", "verdict"] == "consensus" and df.loc["f0", "reasons"] == ""
    assert df.loc["f1", "verdict"] == "contested" and df.loc["f1", "reasons"] == "majority_differ"
    assert df.loc["f2", "verdict"] == "contested" and df.loc["f2", "reasons"] == "uncertain_band" and df.loc["f2", "p_sym_gpt4o"] == pytest.approx(0.75)
    assert df.loc["f3", "verdict"] == "contested" and df.loc["f3", "reasons"] == "claude_order_split" and df.loc["f3", "p_sym_claude46"] == 0.5
    assert df.loc["f4", "verdict"] == "non_answer" and not df.loc["f4", "answered_gpt4o"]
    assert df.loc["f5", "verdict"] == "contested" and df.loc["f5", "reasons"] == "uncertain_band" and df.loc["f5", "p_x_missing_deepseek_v4"] == 1
    pw = C.pairwise_disagreement(df.reset_index(), T).set_index("pair")
    assert pw.loc["gpt4o-claude46", "n_differ"] == 1 and pw.loc["gpt4o-deepseek_v4", "n_differ"] == 0 and pw.loc["gpt4o-claude46", "n_families"] == 4
    rt = C.rate_table(df.reset_index(), df.reset_index()["family_id"].map(lambda x: "a" if x in ("f0", "f1", "f4") else "b"), "grp").set_index("grp")
    assert rt.loc["a", "non_answer"] == 1 and rt.loc["a", "contested"] == 1 and rt.loc["a", "contested_rate"] == pytest.approx(0.5)
    assert rt.loc["b", "contested"] == 3 and rt.loc["b", "contested_rate"] == pytest.approx(1.0)
    hist = dict(C.p_histogram(df.reset_index(), "gpt4o"))
    assert sum(hist.values()) == 5


def test_stratified_sample_is_deterministic_and_proportional():
    fams = [_pool_fam(f"scr_{i}", f"s {i}", src="scruples") for i in range(60)] + [_pool_fam(f"ms_{i}", f"m {i}", src="moral_stories") for i in range(40)]
    a = C.stratified_sample(fams, 50, seed=1)
    b = C.stratified_sample(fams, 50, seed=1)
    assert [f.family_id for f in a] == [f.family_id for f in b] and len(a) == 50
    assert sum(f.source == "scruples" for f in a) == 30 and sum(f.source == "moral_stories" for f in a) == 20
    assert len(C.stratified_sample(fams, 500, seed=1)) == 100
    assert [f.family_id for f in C.stratified_sample(fams, 50, seed=2)] != [f.family_id for f in a]


# ---- CLIs ----------------------------------------------------------------------------------------------------------


def _run(args: list[str]) -> subprocess.CompletedProcess:
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    return subprocess.run([PY, *args], cwd=ROOT, env=env, capture_output=True, text=True)


def test_cli_build_prompts_select(src_dir, tmp_path):
    pool = tmp_path / "pool.jsonl"
    report = tmp_path / "pool_report.md"
    r = _run(["scripts/16_build_contested_pool.py", "--no-hf", "--families", str(src_dir / "families.jsonl"), "--out", str(pool), "--report", str(report), "--scruples-files", str(src_dir / "scruples.jsonl"), "--berkeley-file", str(src_dir / "berkeley.csv"), "--moral-stories-file", str(src_dir / "moral_stories.jsonl"), "--ethics-files", str(src_dir / "justice.csv"), "--ms-wave1", "2", "--ethics-wave1", "1", "--berkeley-retrospective", "--berkeley-retro-pilot", "1", "--ms-wave2", "1", "--ethics-wave2", "1", "--handcheck-dir", str(tmp_path / "hc"), "--handcheck-n", "2"])
    assert r.returncode == 0, r.stderr
    fams = load_models(pool, Family)
    by_src = {}
    for f in fams:
        by_src.setdefault(f.source, []).append(f)
    assert {f.family_id for f in by_src["scruples"]} == {"scr_p1", "scr_p2"} and len(by_src["aita_berkeley"]) == 2 and len(by_src["moral_stories"]) == 3 and len(by_src["hendrycks_ethics"]) == 2
    assert [f.family_id for f in by_src["moralchoice"]] == ["mc_L_001"]
    assert all(f.split == "pool_contested" and "provenance" in f.meta and "wave" in f.meta and "leak_max_cosine" in f.meta for f in fams)
    waves = {f.family_id: f.meta["wave"] for f in fams}
    assert waves["bk_b1"] == "1" and waves["bk_b2"] == "1_pilot"
    assert sorted(waves[f.family_id] for f in by_src["moral_stories"]) == ["1", "1", "reserve"] and sorted(waves[f.family_id] for f in by_src["hendrycks_ethics"]) == ["1", "2b"]  # M1 is the only positive-norm story and is in wave 1, so 2a is empty here
    assert all(f.meta.get("license") for f in fams)
    txt = report.read_text()
    assert "## Per source" in txt and "re-used on purpose (same family_id, sanity split): 1" in txt and "source-item conflicts: 0" in txt
    assert "### Leakage audit vs dev / test only" in txt and "## Licenses (meta.license)" in txt and "## Hand-check samples" in txt
    hc = sorted(p.name for p in (tmp_path / "hc").glob("*.csv"))
    assert hc == ["e2c_handcheck_aita_berkeley.csv", "e2c_handcheck_hendrycks_ethics.csv", "e2c_handcheck_moral_stories.csv", "e2c_handcheck_scruples.csv"]
    with open(tmp_path / "hc" / "e2c_handcheck_scruples.csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assert len(rows) == 2 and {"family_id", "situation", "action_x", "action_y", "pass_second_person", "pass_two_exclusive_actions", "pass_no_verdict_in_situation", "note"} <= set(rows[0])
    # the existing file is untouched
    assert [f.family_id for f in load_models(src_dir / "families.jsonl", Family)] == ["dd_0001", "mc_L_001", "mc_H_001"]

    # default of script 17 since round 1: wave "1" only (no 1_pilot)
    r = _run(["scripts/17_contested_prompts.py", "--families", str(pool), "--out", str(tmp_path / "w1_only.jsonl")])
    assert r.returncode == 0, r.stderr
    w1_only = load_models(tmp_path / "w1_only.jsonl", Prompt)
    assert len(w1_only) == 2 * sum(f.meta["wave"] == "1" for f in fams) and "bk_b2" not in {p.family_id for p in w1_only}
    prompts_path = tmp_path / "pool_T1.jsonl"
    r = _run(["scripts/17_contested_prompts.py", "--families", str(pool), "--out", str(prompts_path), "--waves", "1,1_pilot"])
    assert r.returncode == 0, r.stderr
    prompts = load_models(prompts_path, Prompt)
    wave1 = [f for f in fams if f.meta["wave"] in ("1", "1_pilot")]
    assert len(prompts) == 2 * len(wave1) and all(p.variant == "T1" and p.focus_action in ("x", "y") for p in prompts)
    assert {p.order for p in prompts} == {1, 2} and "What should you do?" in prompts[0].user
    r = _run(["scripts/17_contested_prompts.py", "--families", str(pool), "--out", str(tmp_path / "w2.jsonl"), "--waves", "2a,2b"])
    assert r.returncode == 0 and len(load_models(tmp_path / "w2.jsonl", Prompt)) == 2 * sum(f.meta["wave"] in ("2a", "2b") for f in fams) == 2

    # synthetic screening demos: every wave-1 family answered; the first two contested in different ways
    pmap = {p.prompt_id: p for p in prompts}
    rows = {t: [] for t in ("gpt4o", "claude46", "deepseek_v4")}
    for k, f in enumerate(sorted(wave1, key=lambda f: f.family_id)):
        o1, o2 = pmap[f"{f.family_id}.T1.o1"], pmap[f"{f.family_id}.T1.o2"]
        if k == 0:  # gpt4o in the band
            g, d, c = (0.7, 0.6), (0.98, 0.97), ("x", "x")
        elif k == 1:  # claude disagrees
            g, d, c = (0.95, 0.9), (0.98, 0.97), ("y", "y")
        else:
            g, d, c = (0.95, 0.9), (0.98, 0.97), ("x", "x")
        rows["gpt4o"] += [_row("gpt4o", o1, p_x=g[0], choice="x"), _row("gpt4o", o2, p_x=g[1], choice="x")]
        rows["deepseek_v4"] += [_row("deepseek_v4", o1, p_x=d[0], choice="x"), _row("deepseek_v4", o2, p_x=d[1], choice="x")]
        rows["claude46"] += [_row("claude46", o1, choice=c[0]), _row("claude46", o2, choice=c[1])]
    for t, rs in rows.items():
        write_jsonl(tmp_path / f"{t}_screen.jsonl", rs)
    out = tmp_path / "selected.jsonl"
    cons = tmp_path / "consensus.jsonl"
    rep = tmp_path / "screen_report.md"
    r = _run(["scripts/18_select_contested.py", "--families", str(pool), "--prompts", str(prompts_path), "--demos", ",".join(f"{t}={tmp_path / f'{t}_screen.jsonl'}" for t in rows), "--target", "1", "--out", str(out), "--consensus-out", str(cons), "--report", str(rep), "--no-models-cfg"])
    assert r.returncode == 0, r.stderr
    sel = load_models(out, Family)
    assert len(sel) == 1 and sel[0].split == "train_contested" and sel[0].meta["screen"]["verdict"] == "contested" and sel[0].meta["screen"]["tier"] == "pool"
    assert set(sel[0].meta["screen"]["p_sym"]) == {"gpt4o", "claude46", "deepseek_v4"} and sel[0].meta["screen"]["flip_only"] is False
    assert len(load_models(cons, Family)) == len(wave1) - 2
    # families outside wave 1 have no T1 prompt yet: reported as not_screened, never as non-answers
    with open(tmp_path / "screen_report.csv", newline="") as fh:
        verdicts = {row["family_id"]: row["verdict"] for row in csv.DictReader(fh)}
    unscreened = [f.family_id for f in fams if f.meta["wave"] not in ("1", "1_pilot")]
    assert unscreened and all(verdicts[fid] == "not_screened" for fid in unscreened) and not any(v == "non_answer" for v in verdicts.values())
    assert "not_screened" in rep.read_text() and "families_not_screened" in rep.read_text()
    # a demo file passed under the wrong teacher key is refused unless --trust-file-labels
    bad = _run(["scripts/18_select_contested.py", "--families", str(pool), "--prompts", str(prompts_path), "--demos", f"gpt4o={tmp_path / 'claude46_screen.jsonl'},claude46={tmp_path / 'gpt4o_screen.jsonl'},deepseek_v4={tmp_path / 'deepseek_v4_screen.jsonl'}", "--target", "1", "--out", str(tmp_path / "bad.jsonl"), "--report", str(tmp_path / "bad.md"), "--no-models-cfg"])
    assert bad.returncode != 0 and "labelled teacher=" in bad.stderr
    # --exclude-waves keeps those families out of C and K
    excl_wave = sorted(wave1, key=lambda f: f.family_id)[1].meta["wave"]
    rx = _run(["scripts/18_select_contested.py", "--families", str(pool), "--prompts", str(prompts_path), "--demos", ",".join(f"{t}={tmp_path / f'{t}_screen.jsonl'}" for t in rows), "--target", "100", "--out", str(tmp_path / "ex.jsonl"), "--consensus-out", str(tmp_path / "ex_cons.jsonl"), "--consensus-select-out", str(tmp_path / "ex_k.jsonl"), "--report", str(tmp_path / "ex.md"), "--no-models-cfg", "--exclude-waves", excl_wave])
    assert rx.returncode == 0, rx.stderr
    kept_waves = {f.meta["wave"] for f in load_models(tmp_path / "ex.jsonl", Family)} | {f.meta["wave"] for f in load_models(tmp_path / "ex_cons.jsonl", Family)} | {f.meta["wave"] for f in load_models(tmp_path / "ex_k.jsonl", Family)}
    assert excl_wave not in kept_waves
    r2 = _run(["scripts/18_select_contested.py", "--families", str(pool), "--prompts", str(prompts_path), "--demos", ",".join(f"{t}={tmp_path / f'{t}_screen.jsonl'}" for t in rows), "--target", "100", "--out", str(out), "--report", str(rep), "--no-models-cfg"])
    assert r2.returncode == 0, r2.stderr
    sel2 = load_models(out, Family)
    assert len(sel2) == 2 and {f.meta["screen"]["reasons"][0] for f in sel2} == {"uncertain_band", "majority_differ"}
    # E2c-K: per source exactly the counts of C, drawn from the consensus pool, split train_consensus_control
    rk = _run(["scripts/18_select_contested.py", "--families", str(pool), "--prompts", str(prompts_path), "--demos", ",".join(f"{t}={tmp_path / f'{t}_screen.jsonl'}" for t in rows), "--target", "100", "--out", str(out), "--consensus-select-out", str(tmp_path / "k.jsonl"), "--report", str(rep), "--no-models-cfg"])
    assert rk.returncode == 0, rk.stderr
    k = load_models(tmp_path / "k.jsonl", Family)
    # both contested families are the only two Berkeley rows, so the matched draw falls back to the other sources
    assert len(k) == len(sel2) == 2 and all(f.split == "train_consensus_control" and f.meta["screen"]["verdict"] == "consensus" for f in k)
    assert not ({f.family_id for f in k} & {f.family_id for f in sel2}) and "E2c-K" in rep.read_text() and "| aita_berkeley | 2 | 2 | 0 | 0 |" in rep.read_text()
    txt = rep.read_text()
    assert "## Contested rate per set and source" in txt and "## Teacher pairwise disagreement" in txt and "p_sym distribution" in txt
    assert (tmp_path / "screen_report.csv").exists()

    # tier 0 / calibration path: two existing train families with phase-1-style demos, one contested; no pool demos
    t0 = [Family(family_id=f"dd_{i}", source="daily_dilemmas", source_id=str(i), topic_group="t", situation=f"You are in existing situation {i}.", action_x="Do x.", action_y="Do not do x.", ambiguity="high", split="train") for i in range(2)]
    t0_prompts = [p for f in t0 for p in make_prompts(f, ["T1", "T3"])[0]]
    write_jsonl(tmp_path / "t0_fams.jsonl", t0)
    write_jsonl(tmp_path / "t0_prompts.jsonl", t0_prompts)
    pm = {p.prompt_id: p for p in t0_prompts}
    t0_rows = {t: [] for t in rows}
    for i in range(2):
        o1, o2 = pm[f"dd_{i}.T1.o1"], pm[f"dd_{i}.T1.o2"]
        t0_rows["gpt4o"] += [_row("gpt4o", o1, p_x=0.95, choice="x"), _row("gpt4o", o2, p_x=0.9, choice="x")]
        t0_rows["deepseek_v4"] += [_row("deepseek_v4", o1, p_x=0.5 if i == 0 else 0.99, choice="x"), _row("deepseek_v4", o2, p_x=0.5 if i == 0 else 0.98, choice="x")]
        t0_rows["claude46"] += [_row("claude46", o1, choice="x"), _row("claude46", o2, choice="x")]
        t0_rows["claude46"].append(_row("claude46", pm[f"dd_{i}.T3.o1"], choice="y"))  # other variant, ignored
    for t, rs in t0_rows.items():
        write_jsonl(tmp_path / f"{t}_t0.jsonl", rs)
    out3 = tmp_path / "selected_t0.jsonl"
    r3 = _run(["scripts/18_select_contested.py", "--families", str(pool), "--prompts", str(prompts_path), "--tier0-families", str(tmp_path / "t0_fams.jsonl"), "--tier0-prompts", str(tmp_path / "t0_prompts.jsonl"), "--tier0-demos", ",".join(f"{t}={tmp_path / f'{t}_t0.jsonl'}" for t in rows), "--target", "5", "--out", str(out3), "--report", str(tmp_path / "t0_report.md"), "--no-models-cfg"])
    assert r3.returncode == 0, r3.stderr
    sel3 = load_models(out3, Family)
    assert [f.family_id for f in sel3] == ["dd_0"] and sel3[0].split == "train_contested" and sel3[0].meta["screen"]["tier"] == "tier0" and sel3[0].meta["screen"]["reasons"] == ["uncertain_band"]
    assert "## Calibration" in (tmp_path / "t0_report.md").read_text()


def test_exact_flip_subtally_and_last_row_wins():
    fams, pm = _world()
    f = fams[0].family_id
    o1, o2 = pm[f"{f}.T1.o1"], pm[f"{f}.T1.o2"]
    ro = {"gpt4o": "logprobs", "claude46": "sampling", "deepseek_v4": "logprobs"}
    # DeepSeek flips exactly between orders; gpt4o and Claude are confident and agree -> contested, flip_only
    rows = [_row("gpt4o", o1, p_x=0.98, choice="x"), _row("gpt4o", o2, p_x=0.97, choice="x"), _row("claude46", o1, choice="x"), _row("claude46", o2, choice="x"), _row("deepseek_v4", o1, p_x=1.0, choice="x"), _row("deepseek_v4", o2, p_x=0.0, choice="y")]
    sym, _ = C.symmetrize_t1(rows, pm, ro)
    df = C.classify_all(sym, ["gpt4o", "claude46", "deepseek_v4"])
    r = df.iloc[0]
    assert r.verdict == "contested" and r.reasons == "uncertain_band" and bool(r.band_exact_flip_deepseek_v4) and not bool(r.band_exact_flip_gpt4o) and bool(r.flip_only)
    assert C.flip_table(df, ["deepseek_v4"])[0][1:4] == [1, 1, 1]
    rt = C.rate_table(df, df["verdict"], "v")
    assert int(rt.loc[0, "flip_only"]) == 1 and int(rt.loc[0, "contested_excl_flip_only"]) == 0
    # a genuinely intermediate gpt4o p alongside the flip -> not flip_only
    rows2 = rows[:2] + rows[4:] + [_row("gpt4o", o1, p_x=0.6, choice="x"), _row("gpt4o", o2, p_x=0.55, choice="x")] + rows[2:4]
    sym2, counts = C.symmetrize_t1(rows2, pm, ro)
    assert counts["duplicate_rows"] == 2 and sym2[f]["gpt4o"].p_o1 == 0.6  # the appended re-run (last rows) wins
    r2 = C.classify_all(sym2, ["gpt4o", "claude46", "deepseek_v4"]).iloc[0]
    assert r2.verdict == "contested" and not bool(r2.flip_only) and bool(r2.band_exact_flip_deepseek_v4)


def test_matched_sample_exact_counts_and_shortfall():
    fams = [_pool_fam(f"scr_{i}", f"s {i}", src="scruples") for i in range(10)] + [_pool_fam(f"ms_{i}", f"m {i}", src="moral_stories") for i in range(2)] + [_pool_fam(f"eth_{i}", f"e {i}", src="hendrycks_ethics") for i in range(10)]
    rows, alloc = C.matched_sample(fams, {"scruples": 3, "moral_stories": 1, "hendrycks_ethics": 2}, seed=1)
    assert len(rows) == 6 and alloc["scruples"]["drawn"] == 3 and alloc["moral_stories"]["drawn"] == 1 and alloc["hendrycks_ethics"]["drawn"] == 2
    assert [f.family_id for f in rows] == [f.family_id for f in C.matched_sample(fams, {"scruples": 3, "moral_stories": 1, "hendrycks_ethics": 2}, seed=1)[0]]
    # moral_stories can give only 2 of 5: the shortfall of 3 goes to the other sources in proportion to their targets (3 : 1)
    rows, alloc = C.matched_sample(fams, {"scruples": 3, "moral_stories": 5, "hendrycks_ethics": 1}, seed=1)
    assert len(rows) == 9 and alloc["moral_stories"]["drawn"] == 2 and alloc["scruples"]["drawn"] == 5 and alloc["hendrycks_ethics"]["drawn"] == 2
    assert alloc["moral_stories"] == {"target": 5, "drawn": 2, "available": 2}
    # every targeted source exhausted -> the remainder comes from non-targeted sources by availability
    rows, alloc = C.matched_sample(fams, {"moral_stories": 4}, seed=1)
    assert len(rows) == 4 and alloc["moral_stories"]["drawn"] == 2 and alloc["scruples"]["drawn"] + alloc["hendrycks_ethics"]["drawn"] == 2


def test_reddit_cleanup_residues():
    sit, _, flags = clean_reddit_body("Hi Everybody! &x200B; Quick back story. My ex and I were together for five years and we have a child. NTA all the way I think. Hey y'all, this sub told me to post this. WIBTA if I left?")
    assert sit == "Quick back story. My ex and I were together for five years and we have a child." and "meta_sentence_removed" in flags
    out, fl = first_to_second_person("My SO and I's anniversary is coming up and my husband and I's party was fun.")
    assert out == "Your and your SO's anniversary is coming up and your and your husband's party was fun." and "pronoun_residue" not in fl
