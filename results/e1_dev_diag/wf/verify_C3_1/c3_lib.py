"""EXPLORATORY (dev only, not pre-registered): test claim C3 that the base prior explains the DeepSeek pull."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r.model_copy(update={"category": "answer", "teacher": "S0"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
stud = [r for r in srows if not r.teacher.endswith("base_B_s0")]
def grp(w):
    if w in TS or w == "S0": return w
    k = M.parse_run_id(w); return f"S_{k.teacher}"
def build(hard=False):
    sym_t = M.sym_table(M.frame_table(trows, prompts)); sym_s = M.sym_table(M.frame_table(stud + base, prompts))
    if hard:
        for s in (sym_t, sym_s): s["p_sym"] = (s["p_sym"] > 0.5).astype(float).where(s["p_sym"].notna())
    sh_t, sh_s = P.framing_shifts(sym_t, V), P.framing_shifts(sym_s, V)
    sh_s = sh_s.assign(g=sh_s.teacher.map(grp)).groupby(["g", "family_id", "variant"])["r"].mean().reset_index()
    allp = pd.concat([sh_t.assign(g=sh_t.teacher)[["g", "family_id", "variant", "r"]], sh_s])
    W = allp.pivot_table(index=["family_id", "variant"], columns="g", values="r")
    return W
def pr(x, y): return np.corrcoef(x, y)[0, 1]
def partial(x, y, z):
    rxy, rxz, ryz = pr(x, y), pr(x, z), pr(y, z); return (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))
