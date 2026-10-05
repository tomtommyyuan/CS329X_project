"""Step 14 (E0.7 for students, tasks/e1_plan.md §2 step 2b): first-token p(A) from scripts/12 vs vLLM sampling.

For every prompt in a scripts/12 responses file, sample k continuations of the same prompt string (the SFT
template ending in "Answer:", tokenized with add_special_tokens=False exactly like the readout) at temperature 1,
parse each as "Answer:" + text, and compare the letter frequency with the file's p_letters["A"].
Gate: mean |p_logit_A - freq_A| <= gates.readout_diff_max (configs/e0.yaml, 0.05); otherwise student evaluation
switches to sampling (log it in tasks/hpc_log.md). The summary also reports the difference expected from
binomial sampling noise alone (vcd.student.readout_check.binomial_noise_floor).

Needs vLLM (run with .venv-vllm/bin/python on a GPU node). Examples
  # gate student and untrained base on the first 200 dev prompts (12 was run with --limit 200)
  .venv-vllm/bin/python scripts/14_readout_check.py --responses runs/_smoke/eval_tf/dev_responses.jsonl \\
      --model runs/_smoke/gpt4o_O_s1/checkpoint --split dev --k 20 --out results/e1_gate/readout_check_gate_student.csv
  .venv-vllm/bin/python scripts/14_readout_check.py --responses runs/_smoke/eval_base_tf/dev_responses.jsonl \\
      --model Qwen/Qwen3-4B-Base --split dev --k 20 --out results/e1_gate/readout_check_base.csv

Writes the per-prompt CSV and a JSON summary with the same stem.
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import yaml

from vcd.config import resolve
from vcd.io import load_models, read_jsonl
from vcd.schemas import Prompt
from vcd.student.readout_check import compare_readouts, summarize_check
from vcd.train.data import load_train_yaml, render_prompt


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--responses", required=True, help="scripts/12 output ({split}_responses.jsonl) with p_letters per prompt")
    ap.add_argument("--model", required=True, help="checkpoint dir or HF id to sample from (the model that produced --responses)")
    ap.add_argument("--split", default="dev", choices=["dev", "test", "pilot"], help="prompt split (selects paths.prompts_{split})")
    ap.add_argument("--prompts", default=None, help="prompt jsonl (default: config paths.prompts_{split})")
    ap.add_argument("--k", type=int, default=20, help="samples per prompt (default 20)")
    ap.add_argument("--temperature", type=float, default=1.0)
    ap.add_argument("--max-tokens", type=int, default=8, help="tokens per sample; the letter is the first one for a trained student")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--limit", type=int, default=None, help="only the first N prompts of --responses")
    ap.add_argument("--diff-max", type=float, default=None, help="gate threshold (default: gates.readout_diff_max in configs/e0.yaml)")
    ap.add_argument("--config", default="configs/train.yaml")
    ap.add_argument("--out", required=True, help="per-prompt CSV; the JSON summary goes next to it")
    args = ap.parse_args()

    from vllm import LLM, SamplingParams  # optional dependency: .venv-vllm on a GPU node

    cfg = load_train_yaml(args.config)
    diff_max = args.diff_max
    if diff_max is None:
        diff_max = float(yaml.safe_load(resolve("configs/e0.yaml").read_text(encoding="utf-8"))["gates"]["readout_diff_max"])
    resp = list(read_jsonl(resolve(args.responses)))
    if args.limit:
        resp = resp[: args.limit]
    p_logit = {r["prompt_id"]: (r["p_letters"] or {}).get("A") for r in resp}
    prompts_path = resolve(args.prompts) if args.prompts else cfg["paths"][f"prompts_{args.split}"]
    by_id = {p.prompt_id: p for p in load_models(prompts_path, Prompt)}
    missing = [pid for pid in p_logit if pid not in by_id]
    if missing:
        raise SystemExit(f"{len(missing)} prompt_ids of --responses are not in {prompts_path}, e.g. {missing[:3]}")
    prompts = [by_id[pid] for pid in p_logit]
    meta = {r["prompt_id"]: {"variant": by_id[r["prompt_id"]].variant, "order": by_id[r["prompt_id"]].order,
                             "mass_AB": (r.get("usage") or {}).get("mass_AB"), "top1": (r.get("usage") or {}).get("top1")} for r in resp}

    t0 = time.time()
    rd = cfg.get("readout", {})
    llm = LLM(model=args.model, dtype=rd.get("dtype", "bfloat16"), max_model_len=int(cfg["train"]["max_seq_len"]), gpu_memory_utilization=0.85, seed=args.seed)
    tok = llm.get_tokenizer()
    ids = [tok.encode(render_prompt(p.system, p.user), add_special_tokens=False) for p in prompts]
    params = SamplingParams(n=args.k, temperature=args.temperature, max_tokens=args.max_tokens, seed=args.seed)
    outs = llm.generate([{"prompt_token_ids": x} for x in ids], params, use_tqdm=False)
    samples = {p.prompt_id: [c.text for c in o.outputs] for p, o in zip(prompts, outs)}

    df = compare_readouts(p_logit, samples, meta)
    s = summarize_check(df, diff_max)
    s.update({"model": args.model, "responses": args.responses, "split": args.split, "k": args.k, "temperature": args.temperature,
              "max_tokens": args.max_tokens, "seed": args.seed, "n_prompts": len(prompts), "seconds": round(time.time() - t0, 1)})
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    out.with_suffix(".json").write_text(json.dumps(s, indent=2), encoding="utf-8")
    print(json.dumps(s, indent=2))
    print(f"-> {out}, {out.with_suffix('.json')}")


if __name__ == "__main__":
    main()
