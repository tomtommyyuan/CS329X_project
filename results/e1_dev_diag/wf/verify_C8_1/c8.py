"""EXPLORATORY (dev only, not pre-registered): C8 checks.
(1) S_0-controlled delta_rho (partial out relaxed S_0 profile) on seed-pooled students.
(2) Predictive pass probability of the E2 rule at 300 families via family bootstrap of dev (plug-in)."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["claude46", "deepseek_v4", "gpt4o"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r.model_copy(update={"category": "answer", "teacher": "S0"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
stu = [r for r in srows if not r.teacher.endswith("base_B_s0") and "random" not in r.teacher]
sh_t = P.framing_shifts(M.sym_table(M.frame_table(trows, prompts)), V)
sh_s = P.framing_shifts(M.sym_table(M.frame_table(stu + base, prompts)), V)
pooled = {}
for t in TS:
    runs = [w for w in sh_s.teacher.unique() if w.startswith(f"qwen3-4b.{t}_O_s")]
    pooled[t] = M.pooled_shifts(sh_s, runs, f"S[{t}]")
allsh = pd.concat([sh_t, sh_s[sh_s.teacher == "S0"]] + list(pooled.values()))
whos = TS + ["S0"] + [f"S[{t}]" for t in TS]
fams = M._complete_families(allsh, whos, V)
print("families complete for all incl S0_relaxed:", len(fams))
mat = {w: M._shift_matrix(allsh, w, fams, V) for w in whos}
def corr(a, b): return float(np.corrcoef(a.ravel(), b.ravel())[0, 1])
def resid(y, x):
    y, x = y.ravel(), x.ravel(); X = np.c_[np.ones_like(x), x]; b = np.linalg.lstsq(X, y, rcond=None)[0]; return y - X @ b
print("\n(1) seed-pooled rho, raw vs partial (S0 relaxed partialled out of student AND teacher profiles)")
rows = []
for t in TS:
    s = mat[f"S[{t}]"]; r = {}
    for u in TS + ["S0"]:
        r[f"raw_{u}"] = corr(s, mat[u])
    for u in TS:
        r[f"part_{u}"] = corr(resid(s, mat["S0"]), resid(mat[u], mat["S0"]))
    others = [u for u in TS if u != t]
    r["draw"] = r[f"raw_{t}"] - max(r[f"raw_{u}"] for u in others)
    r["dpart"] = r[f"part_{t}"] - max(r[f"part_{u}"] for u in others)
    # bootstrap CI for dpart
    rng = np.random.default_rng(0); nf = len(fams); bs = []
    for _ in range(2000):
        ix = rng.integers(0, nf, nf)
        sb, b0 = s[ix], mat["S0"][ix]
        pr = {u: corr(resid(sb, b0), resid(mat[u][ix], b0)) for u in TS}
        bs.append(pr[t] - max(pr[u] for u in others))
    r["dpart_lo"], r["dpart_hi"] = np.quantile(bs, [0.025, 0.975])
    rows.append(dict(student=t, **r))
print(pd.DataFrame(rows).round(3).to_string(index=False))
print("teacher-S0 corr on these families:", {u: round(corr(mat[u], mat["S0"]), 3) for u in TS})

# (2) predictive rule pass at 300 families (plug-in bootstrap of the official 139-family pooled set, no S0 needed)
fams2 = M._complete_families(pd.concat([sh_t] + list(pooled.values())), TS + [f"S[{t}]" for t in TS], V)
m2 = {w: M._shift_matrix(pd.concat([sh_t] + list(pooled.values())), w, fams2, V) for w in TS + [f"S[{t}]" for t in TS]}
print("\n(2) official pooled family count:", len(fams2))
def cw(X, t):
    xc = X - X.mean(1, keepdims=True); tc = t - t.mean()
    return (xc @ tc) / (np.sqrt((xc**2).sum(1)) * np.sqrt((tc**2).sum()))
rng = np.random.default_rng(1); NF = 300; NSIM = 1000; NPERM = 1000
res = []
for _ in range(NSIM):
    ix = rng.integers(0, len(fams2), NF); ps = {}; ds = {}
    perms = np.stack([rng.permutation(NF) for _ in range(NPERM)])
    for t in TS:
        S = m2[f"S[{t}]"][ix]; T = {u: m2[u][ix].ravel() for u in TS}; others = [u for u in TS if u != t]
        rh = {u: float(np.corrcoef(S.ravel(), T[u])[0, 1]) for u in TS}
        d = rh[t] - max(rh[u] for u in others)
        Xp = S[perms].reshape(NPERM, -1); rn = {u: cw(Xp, T[u]) for u in TS}
        dn = rn[t] - np.max(np.stack([rn[u] for u in others]), 0)
        ps[t] = (np.sum(dn >= d) + 1) / (NPERM + 1); ds[t] = d
    ph = dict(zip(TS, M.holm([ps[t] for t in TS])))
    passed = {t: (ds[t] > 0) and (ph[t] < 0.05) for t in TS}
    res.append(dict(**{f"pass_{t}": passed[t] for t in TS}, n_pass=sum(passed.values())))
R = pd.DataFrame(res)
print("plug-in bootstrap at 300 families, P(pass) per teacher:", R[[f"pass_{t}" for t in TS]].mean().round(3).to_dict())
print("distribution of n_pass:", R.n_pass.value_counts(normalize=True).sort_index().round(3).to_dict())
print("P(>=2/3 pass):", round((R.n_pass >= 2).mean(), 3), " P(exactly DeepSeek only):", round(((R.n_pass == 1) & R.pass_deepseek_v4).mean(), 3))
