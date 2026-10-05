"""EXPLORATORY (dev, not pre-registered): does calibration explain the JSD own-not-smallest result?"""
import numpy as np, pandas as pd
from scipy.special import logit, expit
from scipy.optimize import brentq
from vcd.analysis import e1_metrics as M
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
symt = M.sym_table(M.frame_table(trows, prompts)); syms = M.sym_table(M.frame_table(srows, prompts))
symt = symt[symt.variant.isin(V)].dropna(subset=["p_sym"]); syms = syms[syms.variant.isin(V)].dropna(subset=["p_sym"])
W = pd.concat([symt, syms]).pivot_table(index=["family_id","variant"], columns="teacher", values="p_sym")
runs = [c for c in W.columns if c not in TS]
common = W[TS].dropna().index
print("common teacher cells:", len(common))
J = lambda a,b: M.binary_jsd(a,b)
def grp(r): k=M.parse_run_id(r); return k.teacher
def table(Tmat, label, cells=common):
    rows=[]
    for r in runs:
        d = W.loc[cells, r]
        ok = d.notna()
        rows.append(dict(run=r, g=grp(r), **{t: float(J(d[ok].to_numpy(), Tmat.loc[cells,t][ok].to_numpy()).mean()) for t in TS}))
    df=pd.DataFrame(rows)
    df["own_min"] = [ (row[row.g]==min(row[t] for t in TS)) if row.g in TS else np.nan for _,row in df.iterrows()]
    g=df.groupby("g")[TS+["own_min"]].agg(lambda x: x.mean() if x.name!="own_min" else x.sum())
    print(f"\n== {label} ==\n", g.round(4).to_string())
    return df
T0 = W[TS]
base = table(T0, "raw JSD on common cells")
# 1. hard labels: teacher -> 0/1 by majority (clipped inside binary_jsd)
Th = (T0>0.5).astype(float).where(T0!=0.5, 0.5)
table(Th, "teacher hard majority labels")
# 2. temperature-match each teacher's extreme share to a common target (pooled-student extreme share)
def ext(p): return float(((p<.1)|(p>.9)).mean())
def conf(p): return float(np.abs(p-.5).mean())
pc = lambda p: np.clip(p,1e-6,1-1e-6)
stud_all = W.loc[common, [r for r in runs if grp(r) in TS]].to_numpy().ravel(); stud_all=stud_all[~np.isnan(stud_all)]
target = conf(stud_all); print("\nstudent pooled mean|p-.5|:", round(target,4), "extreme:", round(ext(stud_all),3))
Tt = T0.copy()
for t in TS:
    x = logit(pc(T0.loc[common,t].to_numpy()))
    k = brentq(lambda k: conf(expit(k*x))-target, 0.05, 20)
    Tt[t] = expit(k*logit(pc(T0[t].to_numpy())))
    print(t, "scale k=%.3f"%k, "raw conf %.3f ext %.3f -> conf %.3f ext %.3f"%(conf(T0.loc[common,t]),ext(T0.loc[common,t]),conf(Tt.loc[common,t]),ext(Tt.loc[common,t])))
table(Tt, "teachers logit-scaled to equal mean|p-.5| (= student pooled)")
# 3. quantile-map confidence: replace each teacher's |p-.5| by rank-matched value from pooled teacher confidences (keep side)
pool = np.sort(np.concatenate([np.abs(T0.loc[common,t].to_numpy()-.5) for t in TS]))
Tq = T0.copy()
for t in TS:
    c = np.abs(T0.loc[common,t]-.5); rk = c.rank(pct=True, method="average").to_numpy()
    newc = np.quantile(pool, np.clip(rk,0,1)); s=np.sign(T0.loc[common,t]-.5).to_numpy()
    Tq.loc[common,t] = .5 + s*newc
table(Tq, "teacher confidence quantile-mapped to pooled distribution (side + within-teacher rank kept)")
# 4. decomposition: JSD contributions from cells where student and teacher disagree vs agree, raw
rows=[]
for r in runs:
    if grp(r) not in TS: continue
    for t in TS:
        s=W.loc[common,r].to_numpy(); p=T0.loc[common,t].to_numpy(); ok=~np.isnan(s)
        j=J(s[ok],p[ok]); dis=(s[ok]>.5)!=(p[ok]>.5)
        rows.append(dict(g=grp(r), t=t, dis_rate=dis.mean(), jsd_dis_part=(j*dis).sum()/ok.sum(), jsd_agree_part=(j*~dis).sum()/ok.sum(), mean_jsd_given_dis=j[dis].mean(), mean_jsd_given_agree=j[~dis].mean()))
print("\n== decomposition (seed-mean) ==\n", pd.DataFrame(rows).groupby(["g","t"]).mean().round(4).to_string())
