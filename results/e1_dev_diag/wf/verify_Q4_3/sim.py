"""EXPLORATORY (dev only, not pre-registered): P(E2 rule passes on test) treating dev as truth."""
import sys, numpy as np, pandas as pd, pickle
from pathlib import Path
sys.path.insert(0, "src")
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
OUT = Path("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q4_3")
V = ["T1", "T3", "T5", "T6"]; TS = ["claude46", "deepseek_v4", "gpt4o"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl"); pid = set(prompts)
rows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if r.prompt_id in pid and M.is_run_id(r.teacher)]
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], pid)
ss, st = M.sym_table(M.frame_table(rows, prompts)), M.sym_table(M.frame_table(trows, prompts))
sh_s, sh_t = P.framing_shifts(ss, V), P.framing_shifts(st, V)
own = {r: M.parse_run_id(r).teacher for r in sh_s["teacher"].unique() if M.parse_run_id(r).version == "O"}
mats = {}
for t in TS:
    runs = sorted(r for r in own if own[r] == t)
    pool = M.pooled_shifts(sh_s, runs, "P_" + t)
    fams = M._complete_families(pd.concat([pool, sh_t]), ["P_" + t, *TS], V)
    S = M._shift_matrix(pool, "P_" + t, fams, V)
    T = {u: M._shift_matrix(sh_t, u, fams, V) for u in TS}
    mats[t] = (fams, S, T)
    rh = {u: np.corrcoef(S.ravel(), T[u].ravel())[0, 1] for u in TS}
    print(t, len(fams), {u: round(v, 4) for u, v in rh.items()}, "delta", round(rh[t] - max(rh[u] for u in TS if u != t), 4))
pickle.dump(mats, open(OUT / "mats.pkl", "wb"))
