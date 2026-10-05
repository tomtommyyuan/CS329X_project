"""EXPLORATORY (dev, not pre-registered): training-label suggestibility vs student suggestibility."""
import json, numpy as np, pandas as pd
rng = np.random.default_rng(1); NB = 10000
TS = ["gpt4o", "claude46", "deepseek_v4"]
tp = {}
for line in open("data/prompts/train_prompts_v2.jsonl"):
    p = json.loads(line); tp[p["prompt_id"]] = p
def ci(v): return np.quantile(v, [.025, .975]).round(3)
def summarize(rows, name):
    df = pd.DataFrame(rows, columns=["f", "v", "act"]).groupby(["f", "v"]).act.mean().unstack()
    both = df[["T5", "T6"]].dropna(); dd = (both.T5 - both.T6).values
    bi = rng.integers(0, len(dd), (NB, len(dd)))
    print(f"  {name:28s} n_fam={len(both):5d} T5-T6={dd.mean():.3f} CI {ci(dd[bi].mean(1))}  n_items={df.notna().sum().to_dict()}")
print("SFT files (hard labels after order-stable filter), act-rate(T5)-act-rate(T6):")
for f in [f"{t}_O_s{s}" for t in TS for s in (1, 3)] + ["random_R_s1"]:
    rows = []
    for line in open(f"data/sft/{f}.jsonl"):
        e = json.loads(line); p = tp[e["prompt_id"]]
        rows.append((e["family_id"], e["variant"], float(p["letter_to_action"][e["letter"]] == p["focus_action"])))
    summarize(rows, f)
print("\nfull teacher train demos (all answered, both orders averaged, no stability filter):")
for t in TS:
    rows = []; uns = {}
    for line in open(f"data/teacher_phase1/{t}_train_demo.jsonl"):
        e = json.loads(line)
        if e["prompt_id"] not in tp or e["category"] != "answer": continue
        p = tp[e["prompt_id"]]
        if p["variant"] not in ("T1", "T3", "T5", "T6"): continue
        rows.append((p["family_id"], p["variant"], float(e["choice_action"] == p["focus_action"])))
    summarize(rows, t + "_all")
    df = pd.DataFrame(rows, columns=["f", "v", "act"]).groupby(["f", "v"]).act.mean()
    print("     share of items order-unstable (act mean = 0.5) by variant:", (df == 0.5).groupby(level=1).mean().round(3).to_dict())
