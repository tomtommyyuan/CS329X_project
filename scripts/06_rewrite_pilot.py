"""Step 06 (E0.6): strict F / C rewrites of sampled teacher answers with B, checked by J.

Needs OpenAI-compatible endpoints for B and J (VLLM_B_URL, VLLM_J_URL), e.g. vLLM on HAIC.
  python scripts/06_rewrite_pilot.py --teacher gpt41 --n 300
Outputs data/rewrites/{teacher}/records.jsonl, rewrites.jsonl and the human audit sheet
data/annotation/rewrite_audit_{teacher}.csv (export via scripts/08_annotation.py export-rewrite).
"""

from __future__ import annotations

import argparse
import asyncio
import logging

from vcd.config import load_e0, load_models_cfg
from vcd.io import load_models
from vcd.llm.registry import build_client, teacher_spec
from vcd.rewrite.pipeline import run_rewrite_pilot, sample_items, summarize
from vcd.schemas import Prompt, TeacherResponse


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", required=True)
    ap.add_argument("--n", type=int, default=None)
    ap.add_argument("--styles", default=None, help="comma list, default from config")
    ap.add_argument("--rewriter", default="gemini38_flash")
    ap.add_argument("--judge", default="glm53_flash_together")
    ap.add_argument("--judge-fallback", default="glm53_together", help="same-family judge used when the first judge returns no JSON; 'none' disables")
    ap.add_argument("--config", default="configs/e0.yaml")
    ap.add_argument("--tag", default=None, help="write to data/rewrites_<tag>/ instead of data/rewrites/ (e.g. a new strict-layer version)")
    ap.add_argument("--sentence-mode-styles", default=None, help="override config: comma list of styles rewritten sentence by sentence, or 'none'")
    ap.add_argument("--c-instruction", default="conv", choices=["conv", "plain", "convlex"], help="C style: conversational wording (default, for Gemini), the mechanical plain-register recipe (for Llama), or conversational syntax with content words kept")
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO)
    for noisy in ("httpx", "httpx2", "openai", "anthropic", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
    cfg = load_e0(args.config)
    models = load_models_cfg()
    if args.c_instruction != "conv":
        from vcd.rewrite import prompts as RP
        RP.STYLE_INSTRUCTIONS["C"] = {"plain": RP.STYLE_INSTRUCTIONS_PLAIN_C, "convlex": RP.STYLE_INSTRUCTIONS_CONVLEX_C}[args.c_instruction]
    rw_cfg = dict(cfg["rewrite"])
    if args.sentence_mode_styles is not None:
        rw_cfg["sentence_mode_styles"] = [] if args.sentence_mode_styles == "none" else args.sentence_mode_styles.split(",")
    styles = args.styles.split(",") if args.styles else list(rw_cfg["styles"])

    prompts = {p.prompt_id: p for p in load_models(cfg["paths"]["prompts"], Prompt)}
    demos = load_models(cfg["paths"]["teacher_dir"] / f"{args.teacher}_demo.jsonl", TeacherResponse)
    items = sample_items(prompts, demos, int(args.n or rw_cfg["n_items"]), seed=int(cfg["seed"]))
    print(f"{len(items)} answered items sampled from {len(demos)} demo rows")

    rw_spec, j_spec = teacher_spec(models, args.rewriter), teacher_spec(models, args.judge)
    if rw_spec.get("max_tokens"):  # reasoning rewriters spend hidden tokens inside max_tokens
        rw_cfg["rewrite_max_tokens"] = int(rw_spec["max_tokens"])
    rewriter = build_client(args.rewriter, rw_spec, cfg)
    judge = build_client(args.judge, j_spec, cfg)
    fallback = None
    if args.judge_fallback and args.judge_fallback != "none":
        fb_spec = teacher_spec(models, args.judge_fallback)
        fallback = (build_client(args.judge_fallback, fb_spec, cfg), fb_spec["model"])
    out_dir = cfg["paths"]["teacher_dir"].parent / ("rewrites" + (f"_{args.tag}" if args.tag else "")) / args.teacher
    stats = asyncio.run(run_rewrite_pilot(prompts, items, styles, rewriter, rw_spec["model"], args.rewriter, judge, j_spec["model"], out_dir, rw_cfg, judge_fallback=fallback))
    print(summarize(stats, styles))
    print(f"-> {out_dir}")


if __name__ == "__main__":
    main()
