"""EXPLORATORY (dev only, not pre-registered): does SFT move each student's profile toward its own teacher relative to S0_relaxed?"""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r.model_copy(update={"category": "answer", "teacher": "S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
sh_t = P.framing_shifts(M.sym_table(M.frame_table(trows, prompts)), V)
sh_s = P.framing_shifts(M.sym_table(M.frame_table([r for r in srows if r.teacher.split(".")[1].split("_")[0] in ("gpt4o","claude46","deepseek")] + base, prompts)), V)
sh_s["g"] = sh_s.teacher.map(lambda w: "S0" if w == "S0_relaxed" else M.parse_run_id(w).teacher)
pooled = sh_s.groupby(["g", "family_id", "variant"])["r"].mean().reset_index().rename(columns={"g": "teacher"})
fams = sorted(set.intersection(*[set(pooled[pooled.teacher == g].family_id) for g in TS + ["S0"]], *[set(sh_t[sh_t.teacher == t].family_id) for t in TS]))
print("families", len(fams))
def get(sh, who, idx): return sh[sh.teacher == who].set_index(["family_id", "variant"])["r"].reindex(idx).to_numpy()
def stats(fs):
    idx = pd.MultiIndex.from_tuples([(f, v) for f in fs for v in V])
    T = {t: get(sh_t, t, idx) for t in TS}; S = {g: get(pooled, g, idx) for g in TS + ["S0"]}
    c = lambda a, b: np.corrcoef(a, b)[0, 1]
    d = {("S0", t): c(S["S0"], T[t]) for t in TS}
    for g in TS:
        for t in TS: d[(g, t)] = c(S[g], T[t])
        d[(g, "S0")] = c(S[g], S["S0"])
    return d
d0 = stats(fams); rng = np.random.default_rng(1)
B = [stats(list(rng.choice(fams, len(fams)))) for _ in range(2000)]
print("\nrho(S0_relaxed, teacher):", {t: round(d0[("S0", t)], 3) for t in TS})
print("rho(student_pooled, S0_relaxed):", {g: round(d0[(g, "S0")], 3) for g in TS})
rows = []
for g in TS:
    for t in TS:
        mv = d0[(g, t)] - d0[("S0", t)]; b = np.array([x[(g, t)] - x[("S0", t)] for x in B])
        rows.append(dict(student=g, teacher=t, own=g == t, rho=d0[(g, t)], rho_S0=d0[("S0", t)], move=mv, ci_lo=np.quantile(b, .025), ci_hi=np.quantile(b, .975)))
print(pd.DataFrame(rows).round(3).to_string(index=False))
# diff-in-diff: move toward own minus mean move of the OTHER students toward that same teacher (teacher-wise contrast)
print("\nteacher-wise contrast: move(S_T -> T) - mean move(S_T' -> T), T' != T")
for t in TS:
    f = lambda x: (x[(t, t)] - x[("S0", t)]) - np.mean([x[(g, t)] - x[("S0", t)] for g in TS if g != t])
    b = np.array([f(x) for x in B]); print(t, round(f(d0), 3), np.round(np.quantile(b, [.025, .975]), 3))
