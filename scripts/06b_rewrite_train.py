"""Step 06b: strict F / C rewrites of the TRAIN-set teacher answers that made it into the O training files.

Rewrites exactly the prompt_ids of data/sft/{teacher}_O_s1.jsonl (the order-stable, one-order-per-item set; identical
across seeds), so nothing outside the training files is paid for. Same strict layer as scripts/06_rewrite_pilot.py
(B = Gemini 3.8 Flash, J = GLM-5.3-Flash with GLM-5.3 fallback), resumable by prompt_id, output under
data/rewrites_train/{teacher}/ which scripts/10_build_sft_data.py reads via --rewrites-dir.

  python scripts/06b_rewrite_train.py --teacher gpt4o            # all ~5,600 items, both styles
  python scripts/06b_rewrite_train.py --teacher gpt4o --limit 50 # smoke
"""

from __future__ import annotations

import argparse
import asyncio
import logging
from pathlib import Path

from vcd.config import load_e0, load_models_cfg
from vcd.io import load_models, read_jsonl
from vcd.llm.registry import build_client, teacher_spec
from vcd.rewrite.pipeline import run_rewrite_pilot, summarize
from vcd.schemas import Prompt, TeacherResponse


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", required=True)
    ap.add_argument("--config", default="configs/e0_v2.yaml")
    ap.add_argument("--sft", default=None, help="O training file whose prompt_ids are rewritten (default data/sft/{teacher}_O_s1.jsonl)")
    ap.add_argument("--demos", default=None, help="default data/teacher_phase1/{teacher}_train_demo.jsonl")
    ap.add_argument("--prompts", default="data/prompts/train_prompts_v2.jsonl")
    ap.add_argument("--rewriter", default="gemini38_flash")
    ap.add_argument("--judge", default="glm53_flash_together")
    ap.add_argument("--judge-fallback", default="glm53_together")
    ap.add_argument("--styles", default="F,C")
    ap.add_argument("--out-dir", default="data/rewrites_train")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--shard", default=None, help="k/n: process every n-th item starting at k (run n workers in parallel on one teacher; they share the output files)")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO)
    for noisy in ("httpx", "openai", "anthropic", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    cfg = load_e0(args.config)
    models = load_models_cfg()
    rw_cfg = dict(cfg["rewrite"])
    sft_path = Path(args.sft or f"data/sft/{args.teacher}_O_s1.jsonl")
    wanted = {r["prompt_id"] for r in read_jsonl(sft_path)}
    prompts = {p.prompt_id: p for p in load_models(Path(args.prompts), Prompt)}
    demos = load_models(Path(args.demos or f"data/teacher_phase1/{args.teacher}_train_demo.jsonl"), TeacherResponse)
    items = [d for d in demos if d.prompt_id in wanted and d.category == "answer"]
    items.sort(key=lambda d: d.prompt_id)
    if args.shard:
        k, n = (int(x) for x in args.shard.split("/"))
        items = items[k::n]
    if args.limit:
        items = items[: args.limit]
    print(f"{len(items)} training items to rewrite for {args.teacher} (from {sft_path})")

    rw_spec, j_spec = teacher_spec(models, args.rewriter), teacher_spec(models, args.judge)
    if rw_spec.get("max_tokens"):
        rw_cfg["rewrite_max_tokens"] = int(rw_spec["max_tokens"])
    rewriter = build_client(args.rewriter, rw_spec, cfg)
    judge = build_client(args.judge, j_spec, cfg)
    fallback = None
    if args.judge_fallback and args.judge_fallback != "none":
        fb_spec = teacher_spec(models, args.judge_fallback)
        fallback = (build_client(args.judge_fallback, fb_spec, cfg), fb_spec["model"])
    out_dir = Path(args.out_dir) / args.teacher
    stats = asyncio.run(run_rewrite_pilot(prompts, items, args.styles.split(","), rewriter, rw_spec["model"], args.rewriter, judge, j_spec["model"], out_dir, rw_cfg, judge_fallback=fallback))
    print(summarize(stats, args.styles.split(",")))
    print(f"-> {out_dir}")


if __name__ == "__main__":
    main()
