"""ValueConsistency (Moore et al., 2024) English / U.S. original questions -> yes_no Family records.

These are stance questions, not two-action dilemmas. In E0 they serve only as a refusal probe on
controversial topics (variant "VC"). action_x = "Yes" (supports), action_y = "No" (opposes).
"""

from __future__ import annotations

import re
from pathlib import Path

from vcd.io import read_jsonl
from vcd.schemas import Family


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]


def load_valueconsistency(jsonl_path: str | Path, language: str = "English", country: str = "U.S.") -> list[Family]:
    fams: list[Family] = []
    seen: set[str] = set()
    for i, r in enumerate(read_jsonl(jsonl_path)):
        if r.get("language") != language or r.get("country") != country or int(r.get("rephrase", 1)) != 0:
            continue
        q = " ".join(str(r["question"]).split())
        if q in seen:
            continue
        seen.add(q)
        opts = r.get("options", {})
        yes_key = next((k for k, v in opts.items() if v == "supports"), "yes")
        no_key = next((k for k, v in opts.items() if v == "opposes"), "no")
        fams.append(
            Family(
                family_id=f"vc_{i:05d}_{_slug(str(r['topic']))}",
                source="valueconsistency",
                source_id=str(i),
                item_form="yes_no",
                topic_group=str(r["topic"]),
                situation="",
                question_original=q,
                action_x=yes_key.capitalize() + ".",
                action_y=no_key.capitalize() + ".",
                ambiguity="unknown",
                controversial=bool(r.get("controversial")),
                meta={"options": opts},
            )
        )
    return fams
