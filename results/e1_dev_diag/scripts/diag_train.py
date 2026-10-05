"""Training-set check: does each student reproduce its own teacher's training labels (exact training prompts),
overall and on the items where two teachers' labels disagree?"""
import glob
from itertools import combinations
import numpy as np, pandas as pd
from vcd.io import read_jsonl
S = "/hai/scratch/tomyyc/vcd_diag"
lab = {t: {r["prompt_id"]: r["letter"] for r in read_jsonl(f"data/sft/{t}_O_s1.jsonl")} for t in ("gpt4o", "claude46", "deepseek_v4")}
rows = []
for f in sorted(glob.glob(f"{S}/train_readout/*/dev_responses.jsonl")):
    run = f.split("/")[-2]
    st = {r["prompt_id"]: r["letter"] for r in read_jsonl(f)}
    row = {"run": run}
    for t, L in lab.items():
        k = [p for p in L if p in st]; row[f"acc__{t}"] = np.mean([st[p] == L[p] for p in k])
    for a, b in combinations(lab, 2):
        k = [p for p in lab[a] if p in lab[b] and p in st and lab[a][p] != lab[b][p]]
        row[f"{a}>{b} (n={len(k)})"] = np.mean([st[p] == lab[a][p] for p in k])
    rows.append(row)
print("acc__T = share of T's training items where the student's argmax letter equals T's label;")
print("a>b = on items where a and b's labels differ, share where the student gives a's letter")
print(pd.DataFrame(rows).set_index("run").round(3).to_string())
