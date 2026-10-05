# Exploratory (dev, not pre-registered): independent recomputation of family-permutation null means.
import sys, numpy as np, pandas as pd
from pathlib import Path
sys.path.insert(0, "src")
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1","T3","T5","T6"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl"); pid=set(prompts)
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if r.prompt_id in pid and M.is_run_id(r.teacher)]
T = ["claude46","deepseek_v4","gpt4o"]
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in T], pid)
ss = M.sym_table(M.frame_table(srows, prompts)); st = M.sym_table(M.frame_table(trows, prompts))
sh_s = P.framing_shifts(ss, V); sh_t = P.framing_shifts(st, V)
def mat(sh, who):
    return sh[sh.teacher==who].pivot_table(index="family_id", columns="variant", values="r")[V]
Tm = {t: mat(sh_t, t) for t in T}
runs = sorted(sh_s.teacher.unique())
Sm = {r: mat(sh_s, r) for r in runs}
def corr(a, b):  # rows of a vs vector b
    a = a - a.mean(1, keepdims=True); b = b - b.mean()
    return (a@b)/np.sqrt((a**2).sum(1)*(b**2).sum())
rng = np.random.default_rng(12345)
NP = 20000
def analyse(S, own, fams, resid):
    S = S.loc[fams].to_numpy(); TT = {t: Tm[t].loc[fams].to_numpy() for t in T}
    if resid:
        S = S - S.mean(0, keepdims=True); TT = {t: x - x.mean(0, keepdims=True) for t, x in TT.items()}
    n = len(fams); others=[t for t in T if t!=own]
    obs = {t: corr(S.ravel()[None], TT[t].ravel())[0] for t in T}
    d_obs = obs[own] - max(obs[t] for t in others)
    perms = np.argsort(rng.random((NP, n)), axis=1)
    X = S[perms].reshape(NP, -1)
    rt = {t: corr(X, TT[t].ravel()) for t in T}
    d = rt[own] - np.max([rt[t] for t in others], axis=0)
    return dict(d_obs=d_obs, null_mean=d.mean(), null_sd=d.std(), p=(np.sum(d>=d_obs)+1)/(NP+1),
                null_rho={t: round(rt[t].mean(),3) for t in T}, n=n)
own_of = lambda r: M.parse_run_id(r).teacher
out=[]
for teach in T:
    rs = [r for r in runs if own_of(r)==teach and M.parse_run_id(r).version=="O"]
    piv = pd.concat([Sm[r].stack().rename(r) for r in rs], axis=1).dropna()
    pooled = piv.mean(1).unstack()[V]
    fams = sorted(set(pooled.index).intersection(*[set(Tm[t].dropna().index) for t in T]))
    for resid in (False, True):
        res = analyse(pooled, teach, fams, resid); out.append(dict(run=f"{teach}_pooled", resid=resid, **res))
    for r in rs:
        f2 = sorted(set(Sm[r].dropna().index).intersection(*[set(Tm[t].dropna().index) for t in T]))
        for resid in (False, True):
            res = analyse(Sm[r], teach, f2, resid); out.append(dict(run=r.split(".")[1], resid=resid, **res))
pd.set_option("display.width", 250); pd.set_option("display.max_colwidth", 80)
df = pd.DataFrame(out); print(df.to_string())
# type effects (column means) for reference
for t in T: print(t, Tm[t].mean().round(3).to_dict())
