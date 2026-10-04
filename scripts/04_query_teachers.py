"""Step 04: query one teacher on the pilot prompts.

Examples
  python scripts/04_query_teachers.py --teacher gpt41 --mode demo
  python scripts/04_query_teachers.py --teacher gpt41 --mode profile
  python scripts/04_query_teachers.py --teacher claude46 --mode profile --limit 20   # smoke test
Output: data/teacher/{teacher}_{mode}.jsonl (append, resumable; cached calls are free).
"""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from vcd.config import load_e0, load_models_cfg
from vcd.io import load_models
from vcd.llm.registry import build_client, teacher_spec
from vcd.schemas import Prompt
from vcd.teacher.query import main_sync, plan_for


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--teacher", required=True, help="key in configs/models.yaml, e.g. gpt41")
    ap.add_argument("--mode", choices=["demo", "profile"], required=True)
    ap.add_argument("--config", default="configs/e0.yaml")
    ap.add_argument("--prompts", default=None, help="override prompts file")
    ap.add_argument("--limit", type=int, default=None, help="only the first N prompts (smoke test)")
    ap.add_argument("--variants", default=None, help="comma list, e.g. T1,T3")
    ap.add_argument("--no-cache", action="store_true")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
    for noisy in ("httpx", "httpx2", "openai", "anthropic", "httpcore"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

    cfg = load_e0(args.config)
    models = load_models_cfg()
    spec = teacher_spec(models, args.teacher)
    prompts = load_models(Path(args.prompts) if args.prompts else cfg["paths"]["prompts"], Prompt)
    if args.variants:
        keep = set(args.variants.split(","))
        prompts = [p for p in prompts if p.variant in keep]
    if args.limit:
        prompts = prompts[: args.limit]
    plan = plan_for(args.teacher, spec, cfg, args.mode)
    print(plan)
    out = Path(args.out) if args.out else cfg["paths"]["teacher_dir"] / f"{args.teacher}_{args.mode}.jsonl"
    client = build_client(args.teacher, spec, cfg, use_cache=not args.no_cache)
    main_sync(client, prompts, plan, out, spec, use_cache=not args.no_cache)


if __name__ == "__main__":
    main()
