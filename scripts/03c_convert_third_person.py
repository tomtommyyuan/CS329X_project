"""Step 03c: convert excluded third-/first-person DailyDilemmas narratives to second person with J,
so they can join the train pool. Pilot / dev / test assignments are never touched: converted families
go straight to split = train. Needs the judge endpoint (VLLM_J_URL) or --model-key.

  python scripts/03c_convert_third_person.py            # convert all excluded families
  python scripts/03c_convert_third_person.py --limit 20 # smoke test
Writes a review sheet data/annotation/person_conversion_review.csv (sample of 100).
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import random

from vcd.config import load_e0, load_models_cfg
from vcd.data.normalize import detect_person
from vcd.io import load_models, write_jsonl
from vcd.llm.base import LLMRequest
from vcd.llm.registry import build_client, teacher_spec
from vcd.schemas import Family

SYSTEM = "You rewrite short scenarios faithfully."
USER = """Rewrite the scenario below in the second person, so that it addresses the decision-maker as "you" (replace the decision-maker's name with you / your and adjust the verbs). Keep every fact, keep the names of all other people, keep the tense. Do not add, remove or soften any information. The decision-maker is the person who must choose between these two actions:
(X) {action_x}
(Y) {action_y}

Scenario: {situation}

Return only the rewritten scenario."""

_PERSON_FLAGS = {"third_person_situation", "first_person_situation"}


async def convert(fams: list[Family], client, model: str, temperature: float) -> list[Family]:
    async def one(f: Family) -> None:
        req = LLMRequest(model=model, system=SYSTEM, user=USER.format(action_x=f.action_x, action_y=f.action_y, situation=f.situation), temperature=temperature, max_tokens=1200)
        resp = await client.complete(req)
        new = " ".join(resp.text.strip().strip('"').split())
        ratio = len(new) / max(1, len(f.situation))
        ok = detect_person(new) == "second" and 0.6 <= ratio <= 1.6 and not new.lower().startswith(("here", "sure", "scenario:"))
        f.meta["situation_original"] = f.situation
        f.meta["converted_by"] = resp.model
        if ok:
            f.situation = new
            f.needs_review = [x for x in f.needs_review if x not in _PERSON_FLAGS] + ["converted_second_person_auto"]
            f.split = "train"
        else:
            f.needs_review.append("conversion_failed")

    await asyncio.gather(*(one(f) for f in fams))
    return fams


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    ap.add_argument("--model-key", default="glm53_flash_together")
    ap.add_argument("--temperature", type=float, default=0.2)
    ap.add_argument("--limit", type=int, default=None)
    args = ap.parse_args()
    cfg = load_e0(args.config)
    spec = teacher_spec(load_models_cfg(), args.model_key)
    client = build_client(args.model_key, spec, cfg)

    fams = load_models(cfg["paths"]["families"], Family)
    todo = [f for f in fams if f.split == "excluded" and _PERSON_FLAGS & set(f.needs_review) and "conversion_failed" not in f.needs_review]
    if args.limit:
        todo = todo[: args.limit]
    print(f"{len(todo)} families to convert")
    asyncio.run(convert(todo, client, spec["model"], args.temperature))
    ok = [f for f in todo if f.split == "train"]
    print(f"converted {len(ok)}/{len(todo)} -> split=train; failed {len(todo) - len(ok)}")
    write_jsonl(cfg["paths"]["families"], fams)

    ann = cfg["paths"]["annotation_dir"]
    ann.mkdir(parents=True, exist_ok=True)
    sample = random.Random(int(cfg["seed"])).sample(ok, min(100, len(ok)))
    with open(ann / "person_conversion_review.csv", "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["family_id", "original", "converted", "faithful(1/0)", "comment"])
        for f in sample:
            w.writerow([f.family_id, f.meta["situation_original"], f.situation, "", ""])
    print(f"review sheet -> {ann / 'person_conversion_review.csv'}")


if __name__ == "__main__":
    main()
