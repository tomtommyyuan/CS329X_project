"""EXPLORATORY (dev only): robustness of S0~DeepSeek: mass thresholds, Spearman, change scores."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
b = [r for r in srows if r.teacher.endswith("base_B_s0")]
print("S0 example fields:", {k: v for k, v in b[0].model_dump().items() if k not in ("raw_text","text")} )
sh_t = P.framing_shifts(M.sym_table(M.frame_table(trows, prompts)), V)
def mass(r):
    pl = r.p_letters or {}; return sum(pl.values()) if isinstance(pl, dict) else np.nan
for thr in [0.0, 0.7, 0.8, 0.85, 0.9]:
    base = [r.model_copy(update={"category": "answer", "teacher": "S0"}) for r in b if r.p_letters and r.usage["mass_AB"] >= thr]
    sh = P.framing_shifts(M.sym_table(M.frame_table(base, prompts)), V)
    rho = M.profile_rho(sh, sh_t, V)
    print(f"thr={thr}: rows={len(base)} ", rho[["teacher","pearson","spearman","n_cells"]].round(3).to_dict("records"))
