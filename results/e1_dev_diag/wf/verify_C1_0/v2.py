"""Exploratory (dev, not pre-registered): prompt-level re-check of dev agreement directly from raw letters."""
import glob, collections, numpy as np
from vcd.io import read_jsonl
TS = ["gpt4o", "claude46", "deepseek_v4"]
P = {r["prompt_id"]: r for r in read_jsonl("data/prompts/dev_prompts_v2.jsonl")}
SEEN = {"T1", "T3", "T5", "T6"}
tmaj = {}
for t in TS:
    acts = collections.defaultdict(list)
    for r in read_jsonl(f"data/teacher_phase1/{t}_dev_profile.jsonl"):
        if r["category"] == "answer": acts[r["prompt_id"]].append(r["choice_action"] == "x")
    tmaj[t] = {p: np.mean(v) for p, v in acts.items()}
    nmap = collections.Counter(len(v) for v in acts.values())
    print(t, "samples/prompt", dict(nmap))
bad_map = 0
res = collections.defaultdict(dict)
for f in sorted(glob.glob("runs/qwen3-4b/*/eval/dev_responses.jsonl")):
    run = f.split("/")[-3]
    st = {}
    for r in read_jsonl(f):
        if r["category"] != "answer": continue
        if P[r["prompt_id"]]["letter_to_action"][r["letter"]] != r["choice_action"]: bad_map += 1
        st[r["prompt_id"]] = r["choice_action"] == "x"
    for t in TS:
        k = [p for p in st if p in tmaj[t] and tmaj[t][p] != .5 and P[p]["variant"] in SEEN]
        res[run][t] = np.mean([st[p] == (tmaj[t][p] > .5) for p in k])
print("letter->action mapping mismatches in student files:", bad_map)
print("prompt-level agreement with teacher per-prompt majority (seen framings):")
for run, d in res.items():
    own = run.split("_O_")[0]
    flag = ""
    if own in TS: flag = "PASS" if d[own] > max(v for k, v in d.items() if k != own) else "fail"
    print(f"{run:20s}", " ".join(f"{t}={d[t]:.3f}" for t in TS), flag)
# teacher-teacher agreement on dev (prompt level)
for i, a in enumerate(TS):
    for b in TS[i+1:]:
        k = [p for p in tmaj[a] if p in tmaj[b] and P[p]["variant"] in SEEN and tmaj[a][p] != .5 and tmaj[b][p] != .5]
        print("teacher", a, b, round(np.mean([(tmaj[a][p] > .5) == (tmaj[b][p] > .5) for p in k]), 3), len(k))
