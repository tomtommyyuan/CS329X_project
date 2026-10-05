"""EXPLORATORY (dev only, not pre-registered): base-controlled inheritance measures.
Seed-pooled student profiles vs teacher profiles, controlling for the untrained base S_0 (0.9 mass rule relaxed)."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r.model_copy(update={"category": "answer", "teacher": "S0"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
stu = [r for r in srows if not r.teacher.endswith("base_B_s0")]
sh_t = P.framing_shifts(M.sym_table(M.frame_table(trows, prompts)), V)
sh_s = P.framing_shifts(M.sym_table(M.frame_table(stu + base, prompts)), V)
def grp(w):
    if w == "S0": return w
    k = M.parse_run_id(w); return f"S_{k.teacher}"
sh_s["g"] = sh_s.teacher.map(grp)
pooled = sh_s.groupby(["g", "family_id", "variant"])["r"].mean().reset_index()
pt = sh_t.pivot_table(index=["family_id", "variant"], columns="teacher", values="r")
ps = pooled.pivot_table(index=["family_id", "variant"], columns="g", values="r")
X = pt.join(ps, how="inner").dropna()
fams = X.index.get_level_values(0)
ok = pd.Series(fams).groupby(fams).transform("size").values == 4
X = X[ok]
print("cells", len(X), "families", X.index.get_level_values(0).nunique())
def resid_type(df):  # remove each column's per-variant mean (type main effect)
    return df - df.groupby(level=1).transform("mean")
def pcorr(y, x, z):
    Z = np.column_stack([np.ones(len(z)), z])
    ry = y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]; rx = x - Z @ np.linalg.lstsq(Z, x, rcond=None)[0]
    return np.corrcoef(ry, rx)[0, 1]
def measures(D):
    out = {}
    R = resid_type(D)
    for s in TS:
        S = f"S_{s}"
        for t in TS:
            out[("raw", s, t)] = np.corrcoef(D[S], D[t])[0, 1]
            out[("type_resid", s, t)] = np.corrcoef(R[S], R[t])[0, 1]
            out[("partial|S0", s, t)] = pcorr(D[S].values, D[t].values, D["S0"].values)
            out[("shift_vs_gap", s, t)] = np.corrcoef(D[S] - D["S0"], D[t] - D["S0"])[0, 1]
            out[("resid_partial|S0", s, t)] = pcorr(R[S].values, R[t].values, R["S0"].values)
        # multiple regression: unique contribution of each teacher + base
        Z = np.column_stack([np.ones(len(D))] + [D[t].values for t in TS] + [D["S0"].values])
        b = np.linalg.lstsq(Z, D[S].values, rcond=None)[0]
        for i, t in enumerate(TS): out[("mreg_beta", s, t)] = b[1 + i]
        out[("mreg_beta", s, "S0")] = b[-1]
    return out
obs = measures(X)
rng = np.random.default_rng(0); F = X.index.get_level_values(0).unique().values
boots = []
Xg = {f: X.xs(f, level=0, drop_level=False) for f in F}
for _ in range(2000):
    samp = rng.choice(F, len(F), replace=True)
    D = pd.concat([Xg[f] for f in samp]); boots.append(measures(D))
B = pd.DataFrame(boots)
rows = []
for kind in ["raw", "type_resid", "partial|S0", "resid_partial|S0", "shift_vs_gap"]:
    for s in TS:
        oth = [t for t in TS if t != s]
        d_obs = obs[(kind, s, s)] - max(obs[(kind, s, t)] for t in oth)
        d_b = B[(kind, s, s)] - np.maximum(B[(kind, s, oth[0])], B[(kind, s, oth[1])])
        rows.append(dict(measure=kind, student=s, **{f"r_{t}": round(obs[(kind, s, t)], 3) for t in TS},
                         delta_own_minus_maxother=round(d_obs, 3), ci_lo=round(np.quantile(d_b, .025), 3), ci_hi=round(np.quantile(d_b, .975), 3),
                         p_boot_le0=round(float((d_b <= 0).mean()), 4)))
res = pd.DataFrame(rows); print(res.to_string(index=False))
print("\nmultiple regression r_S ~ r_gpt4o + r_claude46 + r_deepseek_v4 + r_S0 (beta, 95% boot CI)")
for s in TS:
    print(s, {t: f"{obs[('mreg_beta', s, t)]:.3f} [{np.quantile(B[('mreg_beta', s, t)], .025):.3f},{np.quantile(B[('mreg_beta', s, t)], .975):.3f}]" for t in TS + ["S0"]})
# polarity vs non-polarity subsets
print("\nby variant subset (raw Pearson, seed-pooled)")
for sub in (["T1", "T3"], ["T5", "T6"]):
    Y = X[X.index.get_level_values(1).isin(sub)]
    print(sub, {f"S_{s}": {t: round(np.corrcoef(Y[f'S_{s}'], Y[t])[0, 1], 3) for t in TS + ['S0']} for s in TS})
print("\nteacher-teacher and teacher-S0 raw / type-resid corr")
R = resid_type(X)
for a, b in [("gpt4o","claude46"),("gpt4o","deepseek_v4"),("claude46","deepseek_v4"),("S0","gpt4o"),("S0","claude46"),("S0","deepseek_v4")]:
    print(a, b, round(np.corrcoef(X[a], X[b])[0,1],3), round(np.corrcoef(R[a], R[b])[0,1],3))
res.to_csv("/hai/scratch/tomyyc/vcd_diag/wf/ac_review/base_controlled_inheritance.csv", index=False)
