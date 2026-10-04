"""Step 08b: fill a blind rewrite-audit sheet with an LLM auditor, using the same rubric humans get.

Produces a CSV in the sheet's own format so it can be scored against another annotator with
`08_annotation.py score-rewrite A.csv B.csv --key KEY.csv`. The auditor should come from a family that is
not the rewriter's; a teacher-family auditor (e.g. Claude) is acceptable as a *second* opinion, not the sole gate.

  python scripts/08b_ai_audit.py --sheet data/annotation/v2/rewrite_audit_blind_v3.csv --model-key claude46
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import json
from pathlib import Path

from vcd.config import load_e0, load_models_cfg
from vcd.llm.base import LLMRequest
from vcd.llm.registry import build_client, teacher_spec
from vcd.rewrite.pipeline import parse_json_object

SYSTEM = "You are a careful annotator comparing two short texts. You judge content preservation only, never whether the choice is morally right. Output JSON only."

USER = """Original answer:
{original}

Rewrite:
{rewrite}

Decision rules (apply them literally, do not be lenient):
- same_reasons = 0 if any reason, or any specific detail inside a reason (an example, a list item, a named option), is dropped, or if a new justification or a generalization appears (e.g. a point about one person becomes a point about everyone).
- same_conditions = 0 if a condition, exception or concession is dropped, added, turned into a fact, or moved so that it limits a different statement than in the original.
- same_strength = 0 if any modal verb changed (e.g. "can provide" became "provides", "seek" became "can seek", "should" became "could"), if an emphasis word such as "crucial" or "important" was dropped or added, if a possibility became an assertion, or if directive or predictive phrasing was added.
- Paraphrase and reordering that keep all of the above are fine.

Compare the rewrite to the original and answer as a JSON object with exactly these keys:
- "same_choice": 1 if the rewrite picks the same option letter, else 0
- "same_reasons": 1 or 0 by the rules above
- "same_conditions": 1 or 0 by the rules above
- "same_strength": 1 or 0 by the rules above
- "register": "F" if the rewrite is formal written prose (no contractions, no direct address), "C" if it is plain spoken English (contractions such as it's / don't, everyday words, plain connectives such as so / but / also)
- "comment": one short sentence, only when something is 0
Return only the JSON object."""

FIELDS = ["same_choice(1/0)", "same_reasons(1/0)", "same_conditions(1/0)", "same_strength(1/0)", "register(F/C)", "comment"]


async def run(rows: list[dict], client, model: str, max_tokens: int) -> list[dict]:
    async def one(r: dict) -> dict:
        req = LLMRequest(model=model, system=SYSTEM, user=USER.format(original=r["original_answer"], rewrite=r["rewrite"]), temperature=0.0, max_tokens=max_tokens)
        resp = await client.complete(req)
        d = parse_json_object(resp.text) or {}
        out = dict(r)
        out["same_choice(1/0)"] = str(int(bool(d.get("same_choice", 0)))) if d else ""
        out["same_reasons(1/0)"] = str(int(bool(d.get("same_reasons", 0)))) if d else ""
        out["same_conditions(1/0)"] = str(int(bool(d.get("same_conditions", 0)))) if d else ""
        out["same_strength(1/0)"] = str(int(bool(d.get("same_strength", 0)))) if d else ""
        out["register(F/C)"] = str(d.get("register", "")).strip().upper()[:1]
        out["comment"] = str(d.get("comment", "")) if d else "JUDGE_PARSE_FAILED"
        return out

    return await asyncio.gather(*(one(r) for r in rows))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--sheet", required=True)
    ap.add_argument("--model-key", default="claude46")
    ap.add_argument("--config", default="configs/e0_v2.yaml")
    ap.add_argument("--max-tokens", type=int, default=300)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    cfg = load_e0(args.config)
    spec = teacher_spec(load_models_cfg(), args.model_key)
    client = build_client(args.model_key, spec, cfg)
    sheet = Path(args.sheet)
    with open(sheet, newline="", encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh))
    filled = asyncio.run(run(rows, client, spec["model"], args.max_tokens))
    out = Path(args.out) if args.out else sheet.with_name(f"{sheet.stem}_{args.model_key}.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(filled)
    failed = sum(1 for r in filled if r["comment"] == "JUDGE_PARSE_FAILED")
    print(f"{len(filled)} rows annotated by {spec['model']} -> {out} (parse failures: {failed})")


if __name__ == "__main__":
    main()
