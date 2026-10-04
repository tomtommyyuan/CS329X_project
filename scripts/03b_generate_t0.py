"""Step 03b: generate T0 (Moore-style free rephrase of situation + T1 stem) with the judge model J.

Requires an OpenAI-compatible endpoint for the judge (VLLM_J_URL) or any key in configs/models.yaml
via --model-key (using a teacher as rephraser is discouraged: it ties T0 to that teacher's family).
Writes data/prompts/t0_texts.jsonl; then re-run scripts/03_build_framings.py to include T0.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt

from vcd.config import load_e0, load_models_cfg
from vcd.data.framings import T0_REPHRASE_INSTRUCTION, t1_text
from vcd.io import load_models, read_jsonl, write_jsonl
from vcd.llm.base import LLMRequest
from vcd.llm.registry import build_client, teacher_spec
from vcd.schemas import Family


async def generate(cfg, spec, model_key, fams, out_path, temperature: float) -> None:
    client = build_client(model_key, spec, cfg)
    done = {r["family_id"] for r in read_jsonl(out_path)} if out_path.exists() else set()
    todo = [f for f in fams if f.family_id not in done]
    print(f"{len(todo)} families to rephrase ({len(done)} done)")

    # The reasoning judge occasionally returns an empty text (its thoughts exhaust the budget) and the cache would
    # replay that empty answer forever, so empties are retried with the cache bypassed and a larger budget.
    uncached = build_client(model_key, spec, cfg, use_cache=False)

    async def one(f: Family):
        user = T0_REPHRASE_INSTRUCTION.format(text=t1_text(f))
        text, model = "", spec["model"]
        for cl, max_tokens in ((client, 1200), (uncached, 3000), (uncached, 6000)):
            resp = await cl.complete(LLMRequest(model=spec["model"], system="You rewrite text faithfully.", user=user, temperature=temperature, max_tokens=max_tokens))
            text, model = resp.text.strip().strip('"'), resp.model
            if len(text) >= 20:
                break
        if len(text) < 20:
            print(f"T0 still empty for {f.family_id}; not written (re-run or use --model-key with another judge)")
            return
        write_jsonl(out_path, [{"family_id": f.family_id, "text": text, "model": model, "timestamp": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}], append=True)

    await asyncio.gather(*(one(f) for f in todo))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    ap.add_argument("--split", default="pilot")
    ap.add_argument("--model-key", default="glm53_flash_together")
    ap.add_argument("--temperature", type=float, default=0.7)
    args = ap.parse_args()
    cfg = load_e0(args.config)
    spec = teacher_spec(load_models_cfg(), args.model_key)
    fams = [f for f in load_models(cfg["paths"]["families"], Family) if f.split == args.split and f.item_form == "two_action"]
    asyncio.run(generate(cfg, spec, args.model_key, fams, cfg["paths"]["t0_texts"], args.temperature))
    print(f"-> {cfg['paths']['t0_texts']}; now re-run scripts/03_build_framings.py --split {args.split}")


if __name__ == "__main__":
    main()
