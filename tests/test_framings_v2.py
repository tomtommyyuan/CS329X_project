import pandas as pd

from vcd.data.framings import action_vp, is_negative_action, make_prompts, positive_act
from vcd.schemas import Family
from vcd.teacher.profile import align_to_focus


def _fam(x, y, fid="f1"):
    return Family(family_id=fid, source="daily_dilemmas", source_id="1", topic_group="t", situation="You face a choice.", action_x=x, action_y=y, ambiguity="high")


def test_negative_detection_and_vp():
    assert is_negative_action("Do not report the colleague.")
    assert is_negative_action("Refuse to assist in suicide.")
    assert not is_negative_action("Report the colleague.")
    assert action_vp("Report the colleague.")[0] == "report the colleague"
    assert action_vp("Tell John the truth.")[0] == "tell John the truth"


def test_positive_act_selection():
    # DailyDilemmas pattern: x = to_do, y = not_to_do -> focus x
    assert positive_act(_fam("Report the colleague.", "Do not report the colleague."))[0] == "x"
    # MoralChoice pattern: action1 is the refusal -> focus y
    label, vp, _ = positive_act(_fam("Refuse to assist in suicide.", "Assist in suicide."))
    assert label == "y" and vp == "assist in suicide"
    # neither negated -> x
    assert positive_act(_fam("Tell the truth.", "Keep silent."))[0] == "x"


def test_t5_t6_stems_and_focus():
    fam = _fam("Do not throw the grenade.", "Throw the grenade.")
    prompts, flags = make_prompts(fam, ["T1", "T3", "T5", "T6"])
    assert len(prompts) == 8 and all(p.focus_action == "y" for p in prompts)
    t5 = next(p for p in prompts if p.variant == "T5")
    t6 = next(p for p in prompts if p.variant == "T6")
    assert "Should you throw the grenade?" in t5.user
    assert "Should you not throw the grenade?" in t6.user
    assert "A. Do not throw the grenade." in t5.user  # options unchanged, order 1 has x first
    assert "both_actions_negative" not in flags


def test_align_to_focus_flips_only_focus_y_families():
    df = pd.DataFrame(
        [
            dict(family_id="fx", p_x=0.8, choice_action="x"),
            dict(family_id="fy", p_x=0.8, choice_action="x"),
            dict(family_id="fy", p_x=None, choice_action=None),
        ]
    )
    out = align_to_focus(df, {"fx": "x", "fy": "y"})
    assert out.loc[0, "p_x"] == 0.8 and out.loc[0, "choice_action"] == "x"
    assert abs(out.loc[1, "p_x"] - 0.2) < 1e-9 and out.loc[1, "choice_action"] == "y"
    assert pd.isna(out.loc[2, "p_x"]) and out.loc[2, "choice_action"] is None or pd.isna(out.loc[2, "choice_action"])
