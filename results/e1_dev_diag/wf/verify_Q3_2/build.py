"""Exploratory (dev, not pre-registered): build per-run shift and p tables for Q3 verification."""
import pickle, numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
TS = ["claude46", "deepseek_v4", "gpt4o"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base_relaxed = [r.model_copy(update={"category": "answer", "teacher": "S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
sym_t = M.sym_table(M.frame_table(trows, prompts))
sym_s = M.sym_table(M.frame_table([r for r in srows if "base_B" not in r.teacher and "random_R" not in r.teacher] + base_relaxed, prompts))
out = {}
for V, name in [(["T1","T3","T5","T6"], "seen"), (["T0","T1","T3","T5","T6"], "all5")]:
    out[name] = (P.framing_shifts(sym_t, V), P.framing_shifts(sym_s, V))
out["sym_t"], out["sym_s"] = sym_t, sym_s
pickle.dump(out, open("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q3_2/tables.pkl", "wb"))
print(sym_s.teacher.unique())
