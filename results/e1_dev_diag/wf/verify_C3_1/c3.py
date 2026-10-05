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
for hard in (False, True):
    W = build(hard)
    groups = ["S_gpt4o", "S_claude46", "S_deepseek_v4", "S_random"]
    W = W[[c for c in W.columns if c in TS + ["S0"] + groups]].dropna()
    print(f"\n===== {'HARD labels (p_sym>0.5)' if hard else 'soft p_sym'}; common cells n={len(W)} families={W.index.get_level_values(0).nunique()} =====")
    print("raw Pearson matrix:"); print(W.corr().round(3).to_string())
    Wd = W - W.groupby(level="variant").transform("mean")
    print("\nwithin-variant (variant main effect removed) Pearson:"); print(Wd.corr().round(3).to_string())
    print("\nvariant means of r:"); print(W.groupby(level="variant").mean().round(3).to_string())
    print("\npartial corr student~teacher | S0 (common cells):")
    rows = []
    for g in groups[:3]:
        rows.append({"student": g} | {t: round(partial(W[g], W[t], W["S0"]), 3) for t in TS} | {f"wv_{t}": round(partial(Wd[g], Wd[t], Wd["S0"]), 3) for t in TS})
    print(pd.DataFrame(rows).to_string(index=False))
    # residual movement: student - S0 correlated with teacher - S0? and with teacher
    print("\ncorr(student - S0, teacher) and corr(student-S0, teacher - S0):")
    rows = []
    for g in groups[:3]:
        d = W[g] - W["S0"]
        rows.append({"student": g} | {t: round(pr(d, W[t]), 3) for t in TS} | {f"dd_{t}": round(pr(d, W[t] - W["S0"]), 3) for t in TS})
    print(pd.DataFrame(rows).to_string(index=False))
    # cell-level variance of teacher profiles (sparsity)
    print("\nshare of cells with |r|<0.01:", (W.abs() < 0.01).mean().round(3).to_dict())
