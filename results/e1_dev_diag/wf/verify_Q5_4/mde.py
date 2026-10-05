"""EXPLORATORY (dev only, not pre-registered). Independent recomputation of the pooled delta_rho
permutation null, bootstrap SE, and an MDE80 projection to a test set of ~2x families."""
import sys, json
sys.path.insert(0, "src")
import numpy as np, pandas as pd
from scipy.stats import norm
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P

V = ["T1", "T3", "T5", "T6"]
TS = ["claude46", "deepseek_v4", "gpt4o"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
pid = set(prompts)
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if r.prompt_id in pid and M.is_run_id(r.teacher)]
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], pid)
ss = M.sym_table(M.frame_table(srows, prompts)); st = M.sym_table(M.frame_table(trows, prompts))
sh_s = P.framing_shifts(ss, V); sh_t = P.framing_shifts(st, V)

def mat(sh, who):
    return sh[sh.teacher == who].pivot_table(index="family_id", columns="variant", values="r")[V]

Tm = {t: mat(sh_t, t) for t in TS}
runs = sorted(sh_s.teacher.unique())
rng = np.random.default_rng(12345)
NP = 10000
def corr_rows(X, y):
    Xc = X - X.mean(1, keepdims=True); yc = y - y.mean()
    return (Xc @ yc) / np.sqrt((Xc**2).sum(1) * (yc**2).sum())
def rowcorr(A, B):
    Ac = A - A.mean(1, keepdims=True); Bc = B - B.mean(1, keepdims=True)
    return (Ac*Bc).sum(1) / np.sqrt((Ac**2).sum(1)*(Bc**2).sum(1))

def analyse(S, T, own, fam_idx, nperm=NP, nboot=NP):
    S = S[fam_idx]; T = {u: T[u][fam_idx] for u in TS}; n = len(fam_idx)
    oth = [u for u in TS if u != own]
    obs = {u: corr_rows(S.reshape(1, -1), T[u].ravel())[0] for u in TS}
    d = obs[own] - max(obs[u] for u in oth)
    pm = np.stack([rng.permutation(n) for _ in range(nperm)])
    Xp = S[pm].reshape(nperm, -1)
    rp = {u: corr_rows(Xp, T[u].ravel()) for u in TS}
    dn = rp[own] - np.maximum(rp[oth[0]], rp[oth[1]])
    # structural (expected) correlation under permutation: E[sum S_pi T] = n * sum_j sbar_j tbar_j; S,T are family-demeaned so ravel mean = 0
    sbar = S.mean(0)
    r0 = {u: n*np.dot(sbar, T[u].mean(0)) / np.sqrt((S**2).sum()*(T[u]**2).sum()) for u in TS}
    d0 = r0[own] - max(r0[u] for u in oth)
    b = rng.integers(0, n, size=(nboot, n))
    rb = {u: rowcorr(S[b].reshape(nboot, -1), T[u][b].reshape(nboot, -1)) for u in TS}
    db = rb[own] - np.maximum(rb[oth[0]], rb[oth[1]])
    return dict(n=n, d=d, p=(np.sum(dn >= d)+1)/(nperm+1), null_mean=dn.mean(), null_sd=dn.std(), boot_se=db.std(),
                null_struct=d0, r0={u: round(r0[u], 3) for u in TS}, rp_mean={u: round(rp[u].mean(), 3) for u in TS},
                rp_sd={u: round(rp[u].std(), 3) for u in TS}, obs={u: round(obs[u], 3) for u in TS})

out = {}
for t in TS:
    rs = [r for r in runs if M.parse_run_id(r).teacher == t and M.parse_run_id(r).version == "O"]
    mats = [mat(sh_s, r) for r in rs]
    fams = sorted(set.intersection(*[set(m.index) for m in mats], *[set(Tm[u].index) for u in TS]))
    S = np.mean([m.loc[fams].to_numpy() for m in mats], axis=0)
    T = {u: Tm[u].loc[fams].to_numpy() for u in TS}
    full = analyse(S, T, t, np.arange(len(fams)))
    # dependence of null mean / sd on n: half-size subsamples (n=70), 200 replicates x 2000 perms
    sub = [analyse(S, T, t, rng.choice(len(fams), 70, replace=False), nperm=2000, nboot=500) for _ in range(100)]
    full["sub70_null_mean"] = float(np.mean([s["null_mean"] for s in sub]))
    full["sub70_null_sd"] = float(np.mean([s["null_sd"] for s in sub]))
    full["sub70_struct"] = float(np.mean([s["null_struct"] for s in sub]))
    full["sub70_boot_se"] = float(np.mean([s["boot_se"] for s in sub]))
    out[t] = full
    print(t, json.dumps({k: (round(v, 4) if isinstance(v, float) else v) for k, v in full.items()}, default=float))

print("\n=== MDE80 projection to test (n_test/n_dev = k) ===")
z8 = norm.ppf(0.8)
for k in (2.0, 300/139 * 139/150 * 1.0):
    for a in (0.05/3, 0.025, 0.05):
        za = norm.ppf(1-a)
        for t in TS:
            o = out[t]; f = 1/np.sqrt(k)
            noise = o["null_mean"] - o["null_struct"]
            thrA = o["null_mean"] + za*o["null_sd"]*f              # null mean kept (claim)
            thrB = o["null_struct"] + noise*f + za*o["null_sd"]*f  # noise part of null mean shrinks
            seT = o["boot_se"]*f
            res = dict(k=round(k, 3), alpha=round(a, 4), teacher=t, thrA=thrA, mdeA=thrA+z8*seT,
                       mdeA_with_gt0=max(thrA, 0)+z8*seT, thrB=thrB, mdeB=thrB+z8*seT, mdeB_with_gt0=max(thrB, 0)+z8*seT,
                       powerA_if_dev=1-norm.cdf((max(thrA, 0)-o["d"])/seT))
            print({kk: (round(vv, 3) if isinstance(vv, float) else vv) for kk, vv in res.items()})
