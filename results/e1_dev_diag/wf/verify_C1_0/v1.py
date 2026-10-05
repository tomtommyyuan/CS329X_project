"""Exploratory (dev, not pre-registered): independent re-check of claim C1 (training not broken)."""
import json, glob, collections
import numpy as np
from vcd.io import read_jsonl
TS = ["gpt4o", "claude46", "deepseek_v4"]
S = "/hai/scratch/tomyyc/vcd_diag"
# 1. SFT letters vs teacher demo letters; target begins with letter
demo = {t: {r["prompt_id"]: r for r in read_jsonl(f"data/teacher_phase1/{t}_train_demo.jsonl")} for t in TS}
for t in TS:
    for s in range(1, 6):
        rows = list(read_jsonl(f"data/sft/{t}_O_s{s}.jsonl"))
        bad_letter = sum(r["letter"] != demo[t][r["prompt_id"]]["letter"] for r in rows)
        bad_tgt = sum(not r["text_target"].startswith(" " + r["letter"] + "\n") for r in rows)
        bad_rat = sum(r["text_target"].split("Rationale:")[-1].strip()[:40] not in demo[t][r["prompt_id"]]["raw"] for r in rows)
        fams = len({r["family_id"] for r in rows})
        if s == 1 or bad_letter or bad_tgt:
            print(f"{t} s{s}: n={len(rows)} letter!=demo {bad_letter} target-format-bad {bad_tgt} rationale-not-in-demo {bad_rat} families {fams}")
    # seeds: same (prompt, letter) set?
    sets = [frozenset((r["prompt_id"], r["letter"]) for r in read_jsonl(f"data/sft/{t}_O_s{s}.jsonl")) for s in range(1, 6)]
    print(t, "seed files identical (prompt,letter) sets:", all(x == sets[0] for x in sets))
# R labels vs teachers
R = {r["prompt_id"]: r["letter"] for r in read_jsonl("data/sft/random_R_s1.jsonl")}
for t in TS:
    k = [p for p in R if p in demo[t]]; print("R_s1 label agreement with", t, round(np.mean([R[p] == demo[t][p]["letter"] for p in k]), 3), len(k))
# 2. family leakage train vs dev
dev = {r["family_id"] for r in read_jsonl("data/prompts/dev_prompts_v2.jsonl")}
trf = set()
for t in TS: trf |= {r["family_id"] for r in read_jsonl(f"data/sft/{t}_O_s1.jsonl")}
print("dev families", len(dev), "overlap with train", len(dev & trf))
# 3. recompute train reproduction with family-cluster bootstrap CIs (seed 1 only exists)
lab = {t: {r["prompt_id"]: (r["letter"], r["family_id"]) for r in read_jsonl(f"data/sft/{t}_O_s1.jsonl")} for t in TS}
rng = np.random.default_rng(0)
def cboot(vals, fams, B=2000):
    vals = np.asarray(vals, float); fams = np.asarray(fams); uf = np.unique(fams)
    idx = {f: np.where(fams == f)[0] for f in uf}
    bs = [vals[np.concatenate([idx[f] for f in rng.choice(uf, len(uf))])].mean() for _ in range(B)]
    return vals.mean(), np.quantile(bs, .025), np.quantile(bs, .975), len(uf)
for f in sorted(glob.glob(f"{S}/train_readout/*/dev_responses.jsonl")):
    run = f.split("/")[-2]
    st = {r["prompt_id"]: r for r in read_jsonl(f)}
    cats = collections.Counter(r["category"] for r in st.values())
    out = [run, dict(cats)]
    for t in TS:
        k = [p for p in lab[t] if p in st]
        out.append(f"acc_{t}={np.mean([st[p]['letter'] == lab[t][p][0] for p in k]):.4f} (n={len(k)}, miss={len(lab[t])-len(k)})")
    print(*out)
    own = run.split("_O_")[0]
    if own in TS:
        for o in TS:
            if o == own: continue
            k = [p for p in lab[own] if p in lab[o] and p in st and lab[own][p][0] != lab[o][p][0]]
            m, lo, hi, nf = cboot([st[p]["letter"] == lab[own][p][0] for p in k], [lab[own][p][1] for p in k])
            print(f"   side with own vs {o}: {m:.3f} [{lo:.3f},{hi:.3f}] n_items={len(k)} n_fam={nf}")
