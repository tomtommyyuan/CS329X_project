import numpy as np
import pandas as pd

from vcd.data.framings import make_prompts
from vcd.schemas import Family, TeacherResponse
from vcd.teacher.profile import (
    cell_estimates,
    cross_teacher,
    flip_overlap,
    framing_shifts,
    order_stability,
    pairwise_flip_rates,
    reliability_by_order,
    responses_to_frame,
    symmetrize,
    teacher_consistency,
    type_effects,
)

V = ["T1", "T2", "T3", "T4"]


def _families(n=6):
    return [
        Family(family_id=f"f{i}", source="daily_dilemmas", source_id=str(i), topic_group="t", situation=f"You face situation {i}.", action_x="Do x.", action_y="Do y.", ambiguity="high")
        for i in range(n)
    ]


def _responses(teacher, p_fn, prompts):
    """Logprob-style profile rows (one per prompt) plus demo rows picking the majority action."""
    rows = []
    for p in prompts:
        px = p_fn(p.family_id, p.variant, p.order)
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=teacher, model="m", mode="profile", temperature=1.0, raw="Answer: A", category="answer", letter="A", choice_action=p.letter_to_action["A"], p_x=px))
        rows.append(TeacherResponse(prompt_id=p.prompt_id, teacher=teacher, model="m", mode="demo", temperature=0.0, raw="Answer: A", category="answer", letter="A", choice_action="x" if px >= 0.5 else "y", p_x=None))
    return rows


def test_pipeline_recovers_type_effects():
    fams = _families()
    prompts = {}
    for f in fams:
        ps, _ = make_prompts(f, V)
        for p in ps:
            prompts[p.prompt_id] = p
    # teacher A: T3 pushes +0.2 toward x, no order effect; teacher B: T2 pushes +0.2
    base = {f.family_id: 0.4 + 0.05 * i for i, f in enumerate(fams)}
    pa = lambda fid, v, o: base[fid] + (0.2 if v == "T3" else 0.0)
    pb = lambda fid, v, o: base[fid] + (0.2 if v == "T2" else 0.0)
    rows = _responses("A", pa, prompts.values()) + _responses("B", pb, prompts.values())
    df = responses_to_frame(rows, prompts)
    cells = cell_estimates(df)
    sym = symmetrize(cells)
    assert sym["p_sym"].notna().all() and (sym["order_gap"] == 0).all()
    shifts = framing_shifts(sym, V)
    te = type_effects(shifts, n_boot=200).set_index(["teacher", "variant"])["delta"]
    assert abs(te[("A", "T3")] - 0.15) < 1e-9 and abs(te[("A", "T1")] + 0.05) < 1e-9
    assert abs(te[("B", "T2")] - 0.15) < 1e-9
    ct = cross_teacher(shifts).iloc[0]
    assert ct["profile_pearson"] < 0  # opposite framing sensitivities
    rel = reliability_by_order(sym, V).set_index("teacher")["reliability"]
    assert np.isclose(rel["A"], 1.0)  # identical orders -> perfectly reliable
    st = order_stability(df).set_index("teacher")["order_stable_rate"]
    assert st["A"] == 1.0
    tc = teacher_consistency(sym, V).set_index("teacher")
    # teacher A: base p in [0.40, 0.65], T3 adds 0.2 -> families with base < 0.5 but base+0.2 > 0.5 flip on T3
    assert tc.loc["A", "n_families"] == 6 and 0 < tc.loc["A", "family_flip_share"] < 1
    assert tc.loc["A", "share_uncertain"] == 1.0 and tc.loc["A", "mean_jsd"] > 0
    pf = pairwise_flip_rates(sym, V)
    assert pf[(pf.teacher == "A") & (pf.pair == "T1-T2")].flip_rate.iloc[0] == 0.0  # A is only T3-sensitive
    assert pf[(pf.teacher == "A") & (pf.pair == "T1-T3")].flip_rate.iloc[0] > 0
    ov = flip_overlap(sym, V).iloc[0]
    # A flips families with base in (0.3, 0.5) on T3; B flips the same families on T2 -> full overlap
    assert ov["shared"] == ov["n_flip_a"] == ov["n_flip_b"] and ov["jaccard"] == 1.0


def test_symmetrize_requires_both_orders():
    df = pd.DataFrame(
        [dict(teacher="A", mode="profile", pass_idx=0, sample_idx=0, prompt_id="f0.T1.o1", family_id="f0", variant="T1", order=1, category="answer", choice_action="x", p_x=0.8)]
    )
    sym = symmetrize(cell_estimates(df))
    assert np.isnan(sym["p_sym"].iloc[0])


def test_sampling_readout_uses_frequency():
    rows = []
    for k in range(10):
        rows.append(dict(teacher="C", mode="profile", pass_idx=0, sample_idx=k, prompt_id="f0.T1.o1", family_id="f0", variant="T1", order=1, category="answer", choice_action="x" if k < 7 else "y", p_x=None))
    rows.append(dict(teacher="C", mode="profile", pass_idx=0, sample_idx=10, prompt_id="f0.T1.o1", family_id="f0", variant="T1", order=1, category="refusal", choice_action=None, p_x=None))
    cells = cell_estimates(pd.DataFrame(rows))
    assert np.isclose(cells["p_x"].iloc[0], 0.7) and cells["n_answer"].iloc[0] == 10 and cells["n_total"].iloc[0] == 11
