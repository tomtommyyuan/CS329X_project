"""EXPLORATORY (dev only): student-vs-base profile correlation; seed-to-seed profile reliability."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r.model_copy(update={"category": "answer", "teacher": "S0"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
stu = [r for r in srows if not r.teacher.endswith("base_B_s0")]
sh = P.framing_shifts(M.sym_table(M.frame_table(stu + base, prompts)), V)
W = sh.pivot_table(index=["family_id", "variant"], columns="teacher", values="r").dropna()
cols = [c for c in W.columns if c != "S0"]
for t in ["gpt4o", "claude46", "deepseek_v4", "random"]:
    cs = [c for c in cols if f".{t}_" in c]
    pooled = W[cs].mean(axis=1)
    pair = [np.corrcoef(W[a], W[b])[0, 1] for i, a in enumerate(cs) for b in cs[i + 1:]]
    print(t, "corr(pooled, S0)=%.3f" % np.corrcoef(pooled, W["S0"])[0, 1], "seed-seed profile r mean=%.3f min=%.3f" % (np.mean(pair), np.min(pair)), "n_cells", len(W))
# cross-teacher student-student
g = {t: W[[c for c in cols if f".{t}_" in c]].mean(axis=1) for t in ["gpt4o", "claude46", "deepseek_v4"]}
print("student-student pooled corr", {f"{a}-{b}": round(np.corrcoef(g[a], g[b])[0, 1], 3) for a, b in [("gpt4o","claude46"),("gpt4o","deepseek_v4"),("claude46","deepseek_v4")]})
