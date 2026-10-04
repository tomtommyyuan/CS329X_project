"""DailyDilemmas (Chiu et al., ICLR 2025) -> Family records.

Source file: dilemma_to_action_to_values_aggregated.csv, two rows per dilemma (to_do / not_to_do).
`dilemma_situation` is second person and ends with a leading question ("Should you ...?") that
favours the to_do action; we strip it and attach our own framing stems later.
"""

from __future__ import annotations

import ast
from pathlib import Path

import pandas as pd

from vcd.data.normalize import detect_person, normalize_action, split_trailing_question
from vcd.schemas import Family


def _parse_list(s) -> list[str]:
    try:
        v = ast.literal_eval(str(s))
        return [str(x) for x in v] if isinstance(v, (list, tuple)) else []
    except (ValueError, SyntaxError):
        return []


def load_daily_dilemmas(csv_path: str | Path) -> list[Family]:
    df = pd.read_csv(csv_path)
    fams: list[Family] = []
    for dilemma_idx, g in df.groupby("dilemma_idx", sort=True):
        to_do = g[g["action_type"] == "to_do"]
        not_to_do = g[g["action_type"] == "not_to_do"]
        flags: list[str] = []
        if len(to_do) != 1 or len(not_to_do) != 1:
            flags.append("dd_action_rows_not_2")
            if len(to_do) == 0 or len(not_to_do) == 0:
                continue
        td, ntd = to_do.iloc[0], not_to_do.iloc[0]
        situation, question = split_trailing_question(str(td["dilemma_situation"]))
        if not question:
            flags.append("dd_no_trailing_question")
        person = detect_person(situation)
        if person != "second":
            flags.append(f"{person}_person_situation")
        ax, fx = normalize_action(str(td["action"]))
        ay, fy = normalize_action(str(ntd["action"]))
        flags += [f"x_{f}" for f in fx] + [f"y_{f}" for f in fy]
        fams.append(
            Family(
                family_id=f"dd_{int(dilemma_idx):04d}",
                source="daily_dilemmas",
                source_id=str(int(dilemma_idx)),
                topic_group=str(g.iloc[0]["topic_group"]),
                situation=situation,
                question_original=question,
                action_x=ax,
                action_y=ay,
                ambiguity="high",
                needs_review=flags,
                meta={
                    "basic_situation": str(g.iloc[0]["basic_situation"]),
                    "topic": str(g.iloc[0]["topic"]),
                    "values_x": _parse_list(td["values_aggregated"]),
                    "values_y": _parse_list(ntd["values_aggregated"]),
                },
            )
        )
    return fams
