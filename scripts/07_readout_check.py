"""Step 07 (E0.7): logit readout vs sampling on an open model (vLLM endpoint).
  python scripts/07_readout_check.py --model-key llama33_70b --limit 200
Writes results/e0/readout_check_{model}.csv and prints mean |p_logit - freq| against the gate."""

from __future__ import annotations

import argparse
import asyncio
import json

from vcd.config import load_e0, load_models_cfg
from vcd.io import load_models
from vcd.llm.registry import build_client, teacher_spec
from vcd.readout.logit_vs_sample import run, summarize
from vcd.schemas import Prompt


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-key", default="llama33_70b")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--config", default="configs/e0.yaml")
    args = ap.parse_args()
    cfg = load_e0(args.config)
    spec = teacher_spec(load_models_cfg(), args.model_key)
    prompts = [p for p in load_models(cfg["paths"]["prompts"], Prompt) if p.variant != "VC"]
    if args.limit:
        prompts = prompts[: args.limit]
    client = build_client(args.model_key, spec, cfg)
    rc = cfg["readout_check"]
    df = asyncio.run(run(client, spec["model"], prompts, int(rc["k_sampling"]), float(rc["temperature"])))
    out = cfg["paths"]["results"] / f"readout_check_{args.model_key}.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    s = summarize(df)
    s["gate"] = "ok" if s["mean_abs_diff"] <= cfg["gates"]["readout_diff_max"] else "FAIL: use sampling for students too"
    print(json.dumps(s, indent=2))
    print(f"-> {out}")


if __name__ == "__main__":
    main()
