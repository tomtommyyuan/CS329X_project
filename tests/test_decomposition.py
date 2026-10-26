import pandas as pd

from vcd.analysis.decomposition import cell_structure, follow_rates, majority_frame, own_category, teacher_pairwise


def _sym(rows):
    return pd.DataFrame(rows, columns=["teacher", "family_id", "variant", "p_sym"])


def test_structure_and_follow_rates():
    T = ["a", "b", "c"]
    teach = _sym([("a", "f1", "T1", 0.9), ("b", "f1", "T1", 0.9), ("c", "f1", "T1", 0.9),   # all agree (x)
                  ("a", "f2", "T1", 0.9), ("b", "f2", "T1", 0.1), ("c", "f2", "T1", 0.1),   # unique_a
                  ("a", "f3", "T1", 0.1), ("b", "f3", "T1", 0.9), ("c", "f3", "T1", 0.1),   # unique_b
                  ("a", "f4", "T1", 0.5), ("b", "f4", "T1", 0.9), ("c", "f4", "T1", 0.9)])  # a tie -> dropped
    st = cell_structure(majority_frame(teach, ["T1"]), T)
    assert len(st) == 3 and set(st["structure"]) == {"all_agree", "unique_a", "unique_b"}
    pw = teacher_pairwise(st, T)
    assert pw.set_index(["a", "b"]).loc[("a", "b"), "agreement"] == 1 / 3
    assert own_category("unique_a", "a") == "own_unique" and own_category("unique_b", "a") == "own_with_one_other"
    student = majority_frame(_sym([("run", "f1", "T1", 0.8), ("run", "f2", "T1", 0.8), ("run", "f3", "T1", 0.2)]), ["T1"])
    fr = follow_rates(student, st, T, "a").set_index("category")
    assert fr.loc["own_unique", "follow_own"] == 1.0 and fr.loc["own_unique", "follow_other_max"] == 0.0
    assert fr.loc["own_with_one_other", "follow_own"] == 1.0 and fr.loc["own_with_one_other", "follow_other_max"] == 1.0
    assert fr.loc["all_agree", "follow_own"] == 1.0
