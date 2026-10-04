"""MoralChoice (Scherrer et al., NeurIPS 2023) -> Family records.

`context` is second person; `action1/2` are first person ("I throw the grenade.") and are converted
to imperatives so that options read as things *you* could do.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from vcd.data.normalize import detect_person, first_person_to_imperative
from vcd.schemas import Family

_RULE_COLS = ["death", "pain", "disable", "freedom", "pleasure", "deceive", "cheat", "break_promise", "break_law", "duty"]


def load_moralchoice(high_csv: str | Path, low_csv: str | Path) -> list[Family]:
    fams: list[Family] = []
    for path, amb in [(high_csv, "high"), (low_csv, "low")]:
        df = pd.read_csv(path)
        for _, r in df.iterrows():
            ax, fx = first_person_to_imperative(str(r["action1"]))
            ay, fy = first_person_to_imperative(str(r["action2"]))
            flags = [f"x_{f}" for f in fx] + [f"y_{f}" for f in fy]
            situation = " ".join(str(r["context"]).split())
            person = detect_person(situation)
            if person != "second":
                flags.append(f"{person}_person_situation")
            rules = {
                c: {"x": str(r.get(f"a1_{c}", "")), "y": str(r.get(f"a2_{c}", ""))} for c in _RULE_COLS
            }
            fams.append(
                Family(
                    family_id=f"mc_{r['scenario_id']}",
                    source="moralchoice",
                    source_id=str(r["scenario_id"]),
                    topic_group=str(r["generation_rule"]),
                    situation=situation,
                    action_x=ax,
                    action_y=ay,
                    ambiguity=amb,
                    needs_review=flags,
                    meta={"generation_type": str(r["generation_type"]), "rule_violations": rules},
                )
            )
    return fams
