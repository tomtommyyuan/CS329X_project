"""Exploratory (dev, not pre-registered): prompt-level agreement using teacher p (p_x mean), order self-consistency ceiling."""
import glob, collections, numpy as np
from vcd.io import read_jsonl
TS = ["gpt4o", "claude46", "deepseek_v4"]
P = {r["prompt_id"]: r for r in read_jsonl("data/prompts/dev_prompts_v2.jsonl")}
SEEN = {"T1", "T3", "T5", "T6"}
tp = {}
for t in TS:
    v = collections.defaultdict(list); nonep = 0
    for r in read_jsonl(f"data/teacher_phase1/{t}_dev_profile.jsonl"):
        if r["category"] != "answer": continue
        if r.get("p_x") is None: nonep += 1; v[r["prompt_id"]].append(float(r["choice_action"] == "x"))
        else: v[r["prompt_id"]].append(r["p_x"])
    tp[t] = {p: np.mean(x) for p, x in v.items()}
    print(t, "rows without p_x:", nonep)
# order self-consistency (o1 vs o2 same family/variant) for teachers and students
def selfcons(d):
    k = collections.defaultdict(dict)
    for p, x in d.items():
        q = P[p]
        if q["variant"] in SEEN: k[(q["family_id"], q["variant"])][q["order"]] = x > .5
    pairs = [v for v in k.values() if len(v) == 2]
    return np.mean([v[1] == v[2] for v in pairs]), len(pairs)
for t in TS: print("order self-consistency", t, *[round(x, 3) for x in selfcons(tp[t])])
rows = {}
for f in sorted(glob.glob("runs/qwen3-4b/*_O_s*/eval/dev_responses.jsonl")):
    run = f.split("/")[-3]
    st = {r["prompt_id"]: r["p_x"] for r in read_jsonl(f) if r["category"] == "answer"}
    d = {}
    for t in TS:
        k = [p for p in st if p in tp[t] and P[p]["variant"] in SEEN and tp[t][p] != .5]
        d[t] = np.mean([(st[p] > .5) == (tp[t][p] > .5) for p in k])
    own = run.split("_O_")[0]
    print(f"{run:20s}", " ".join(f"{t}={d[t]:.3f}" for t in TS), "PASS" if d[own] > max(v for k, v in d.items() if k != own) else "fail", "selfcons", round(selfcons(st)[0], 3))
