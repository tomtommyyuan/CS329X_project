"""EXPLORATORY (dev only, not pre-registered): independent checks for claim C1 (training/data not broken).

1. SFT rows vs raw teacher demos (letter, teacher field, rendered prompt, rationale) for all O files; R prompts.
2. family disjointness train vs dev.
3. dev student responses: letter == argmax p_letters, choice_action == letter_to_action[letter], p_x consistent.
4. loss curves first/last.
5. dev agreement split by whether the cell is order-stable for the own teacher (the training filter) and by
   whether teachers are unanimous.
"""
import glob, json, re
from collections import Counter, defaultdict
import numpy as np, pandas as pd
from vcd.io import read_jsonl
from vcd.train.data import render_prompt, canonical_target
from vcd.analysis import e1_metrics as M

T = ("gpt4o", "claude46", "deepseek_v4")
train_prompts = {r["prompt_id"]: r for r in read_jsonl("data/prompts/train_prompts_v2.jsonl")}
demo = {}
for t in T:
    d = {}
    for r in read_jsonl(f"data/teacher_phase1/{t}_train_demo.jsonl"):
        d.setdefault(r["prompt_id"], r)
    demo[t] = d

print("== 1. SFT rows vs raw demos")
for f in sorted(glob.glob("data/sft/*_s*.jsonl")):
    name = f.split("/")[-1][:-6]
    rows = list(read_jsonl(f))
    t = rows[0]["teacher"]
    c = Counter()
    for r in rows:
        p = train_prompts[r["prompt_id"]]
        c["prompt_render_ok"] += r["text_prompt"] == render_prompt(p["system"], p["user"])
        c["letter_matches_target"] += r["text_target"][1] == r["letter"]
        if t in demo:
            dm = demo[t][r["prompt_id"]]
            c["letter_eq_demo_letter"] += dm["letter"] == r["letter"]
            c["target_eq_canonical_demo"] += canonical_target(dm["raw"]) == r["text_target"]
            c["demo_action_eq_prompt_map"] += p["letter_to_action"][r["letter"]] == dm["choice_action"]
            # letter vs teacher's own logprob argmax (demo temp 0)
            pl = dm.get("p_letters") or {}
            if pl:
                c["letter_eq_demo_argmax_p"] += max(pl, key=pl.get) == r["letter"]
                c["n_with_p"] += 1
            # cross-teacher: does this letter match another teacher's demo more than own? (mislabel check)
            for o in T:
                if o != t and r["prompt_id"] in demo[o] and demo[o][r["prompt_id"]].get("letter"):
                    c[f"eq_{o}"] += demo[o][r["prompt_id"]]["letter"] == r["letter"]
                    c[f"n_{o}"] += 1
    n = len(rows)
    out = {k: (round(v / n, 4) if not k.startswith(("n_", "eq_")) else v) for k, v in c.items()}
    for o in T:
        if f"n_{o}" in c:
            out[f"agree_with_{o}"] = round(c[f"eq_{o}"] / c[f"n_{o}"], 4)
            del out[f"eq_{o}"], out[f"n_{o}"]
    print(name, "n", n, "teacher_field", set(r["teacher"] for r in rows), "version", set(r["version"] for r in rows), out)

print("\n== 2. family disjointness")
dev_prompts = {r["prompt_id"]: r for r in read_jsonl("data/prompts/dev_prompts_v2.jsonl")}
dev_fam = {r["family_id"] for r in dev_prompts.values()}
sft_fam = set()
for f in glob.glob("data/sft/*_s*.jsonl"):
    sft_fam |= {r["family_id"] for r in read_jsonl(f)}
print("dev families", len(dev_fam), "train families in SFT", len(sft_fam), "overlap", len(dev_fam & sft_fam))
# near-duplicate text check: same user text stem across splits
def stem(u):
    return re.sub(r"\s+", " ", u.split("Options:")[0]).strip().lower()[:200]
tr_stems = {stem(p["user"]) for p in train_prompts.values()}
print("dev prompts whose scenario text (first 200 chars) appears verbatim in train:", sum(stem(p["user"]) in tr_stems for p in dev_prompts.values()))

print("\n== 3. dev student response integrity")
bad = Counter()
for f in sorted(glob.glob("runs/qwen3-4b/*/eval/dev_responses.jsonl")):
    run = f.split("/")[-3]
    for r in read_jsonl(f):
        p = dev_prompts[r["prompt_id"]]
        if r["category"] != "answer":
            bad[(run, "nonanswer")] += 1
            continue
        pl = r["p_letters"]
        if max(pl, key=pl.get) != r["letter"]:
            bad[(run, "letter!=argmax")] += 1
        if p["letter_to_action"][r["letter"]] != r["choice_action"]:
            bad[(run, "action_map")] += 1
        xl = [k for k, v in p["letter_to_action"].items() if v == "x"][0]
        if abs(pl[xl] / (pl["A"] + pl["B"]) - r["p_x"]) > 1e-6:
            bad[(run, "p_x")] += 1
print({k: v for k, v in bad.items() if k[1] != "nonanswer"} or "no integrity errors among answers")
print("nonanswer counts", {k[0]: v for k, v in bad.items() if k[1] == "nonanswer"})

print("\n== 4. loss curves")
for f in sorted(glob.glob("runs/qwen3-4b/*/train_log.jsonl")):
    L = [json.loads(l) for l in open(f) if '"loss"' in l]
    L = [x for x in L if "loss" in x]
    if not L:
        continue
    ep = defaultdict(list)
    for x in L:
        ep[int(min(x.get("epoch", 0), 2.999))].append(x["loss"])
    print(f.split("/")[-2], "first", round(L[0]["loss"], 3), "epoch means", [round(np.mean(ep[e]), 3) for e in sorted(ep)], "last", round(L[-1]["loss"], 3), "nan", any(not np.isfinite(x["loss"]) for x in L))

print("\n== 5. dev agreement split by own-teacher order stability / teacher unanimity (seen variants T1,T3,T5,T6)")
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
tresp = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in T])
sym_t = M.sym_table(tresp, prompts)
sresp = M.load_run_responses("runs", "dev", "qwen3-4b")
sym_s = M.sym_table(sresp, prompts)
SEEN = ["T1", "T3", "T5", "T6"]
st = sym_t[sym_t.variant.isin(SEEN)].dropna(subset=["p_sym"])
wide = st.pivot_table(index=["family_id", "variant"], columns="teacher", values="p_sym")
stab = st.assign(stable=((st.p_o1 > .5) == (st.p_o2 > .5))).pivot_table(index=["family_id", "variant"], columns="teacher", values="stable")
maj = wide > 0.5
unanimous = maj.all(axis=1) | (~maj).all(axis=1)
ss = sym_s[sym_s.variant.isin(SEEN)].dropna(subset=["p_sym"])
ss = ss[ss.teacher.str.contains("_O_")]
ss["own"] = ss.teacher.str.extract(r"qwen3-4b\.(.+)_O_s\d")[0]
res = []
for own in T:
    g = ss[ss.own == own].set_index(["family_id", "variant"])
    for subset_name, mask in [
        ("all", pd.Series(True, index=wide.index)),
        ("own_order_stable", stab[own] == 1),
        ("own_order_unstable", stab[own] == 0),
        ("teachers_unanimous", unanimous),
        ("teachers_split", ~unanimous),
    ]:
        idx = mask[mask].index
        gg = g[g.index.isin(idx)]
        row = {"student": own, "subset": subset_name, "n_cells": int(len(idx))}
        for t in T:
            tm = maj[t].reindex(gg.index)
            row[f"agree_{t}"] = round(float(((gg.p_sym > .5) == tm).mean()), 3)
        res.append(row)
r5 = pd.DataFrame(res)
print(r5.to_string(index=False))
# teacher self order-stability rate on dev vs training stable rate
print("dev order-stable rate per teacher:", stab.mean().round(3).to_dict())
r5.to_csv("/hai/scratch/tomyyc/vcd_diag/wf/verify_C1_1/agreement_by_subset.csv", index=False)
