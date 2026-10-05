"""EXPLORATORY (dev only, not pre-registered): project E2 rule outcome at 300 families; base-prior control."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V=["T1","T3","T5","T6"]; TS=["claude46","deepseek_v4","gpt4o"]
prompts=M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows=M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows=[r for r in M.load_run_responses("runs","dev","qwen3-4b") if M.is_run_id(r.teacher)]
base=[r.model_copy(update={"category":"answer","teacher":"S0"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
stud=[r for r in srows if not r.teacher.endswith("base_B_s0") and "random" not in r.teacher]
sh_t=P.framing_shifts(M.sym_table(M.frame_table(trows,prompts)),V)
sh_s=P.framing_shifts(M.sym_table(M.frame_table(stud+base,prompts)),V)
def grp(w):
    if w=="S0": return w
    return "S_"+M.parse_run_id(w).teacher
sh_s["g"]=sh_s.teacher.map(grp)
pool=sh_s.groupby(["g","family_id","variant"])["r"].mean().unstack("variant")[V]
tt=sh_t.groupby(["teacher","family_id","variant"])["r"].mean().unstack("variant")[V]
groups=["S_"+t for t in TS]
fams=None
for k in groups: 
    f=set(pool.loc[k].dropna().index); fams=f if fams is None else fams&f
for t in TS: fams&=set(tt.loc[t].dropna().index)
fams=sorted(fams); print("complete families (students+teachers):",len(fams))
S={k:pool.loc[k].loc[fams].to_numpy() for k in groups}; T={t:tt.loc[t].loc[fams].to_numpy() for t in TS}
def corr(a,b):
    a=a-a.mean(-1,keepdims=True); b=b-b.mean(-1,keepdims=True)
    return (a*b).sum(-1)/np.sqrt((a*a).sum(-1)*(b*b).sum(-1))
def delta(Sm,Tm,own):
    r={t:corr(Sm.reshape(Sm.shape[0],-1),Tm[t].reshape(Sm.shape[0],-1)) for t in TS}
    return r[own]-np.max([r[t] for t in TS if t!=own],axis=0)
n=len(fams)
for t in TS:
    d=delta(S["S_"+t][None],{u:T[u][None] for u in TS},t); print("dev pooled delta",t,round(float(d[0]),3))
rng=np.random.default_rng(1); B=1000; NP=1000; NT=300
res={"plugin":[], "predictive":[]}
for mode in res:
  for b in range(B):
    if mode=="plugin": idx=rng.integers(0,n,NT)
    else: base_idx=rng.integers(0,n,n); idx=base_idx[rng.integers(0,n,NT)]
    out={}
    for t in TS:
        Sb=S["S_"+t][idx]; Tb={u:T[u][idx] for u in TS}
        d=float(delta(Sb[None],{u:Tb[u][None] for u in TS},t)[0])
        perms=np.stack([rng.permutation(NT) for _ in range(NP)])
        dn=delta(Sb[perms],{u:np.broadcast_to(Tb[u],(NP,)+Tb[u].shape) for u in TS},t)
        out[t]=(d,(np.sum(dn>=d)+1)/(NP+1))
    ph=M.holm([out[t][1] for t in TS])
    res[mode].append({**{f"d_{t}":out[t][0] for t in TS},**{f"pass_{t}":(out[t][0]>0 and ph[i]<0.05) for i,t in enumerate(TS)}})
for mode,rows in res.items():
    df=pd.DataFrame(rows); npass=df[[f"pass_{t}" for t in TS]].sum(1)
    print(f"\n[{mode}] B={B}, n_test_fam={NT}")
    for t in TS: print(f"  {t}: mean d {df['d_'+t].mean():.3f}, P(d>0) {np.mean(df['d_'+t]>0):.3f}, P(pass) {df['pass_'+t].mean():.3f}")
    print("  P(n_pass=0,1,2,3):",[round(float(np.mean(npass==k)),3) for k in range(4)])
# base-prior control: residualize student pooled profile on S0 relaxed profile (families where S0 complete)
f0=sorted(set(fams)&set(pool.loc["S0"].dropna().index)); print("\nfamilies with S0 relaxed complete:",len(f0))
s0=pool.loc["S0"].loc[f0].to_numpy().ravel()
for t in TS:
    x=pool.loc["S_"+t].loc[f0].to_numpy().ravel()
    beta=np.polyfit(s0,x,1); res_x=x-np.polyval(beta,s0)
    raw={u:np.corrcoef(x,tt.loc[u].loc[f0].to_numpy().ravel())[0,1] for u in TS}
    par={u:np.corrcoef(res_x,tt.loc[u].loc[f0].to_numpy().ravel()-np.polyval(np.polyfit(s0,tt.loc[u].loc[f0].to_numpy().ravel(),1),s0))[0,1] for u in TS}
    dr=raw[t]-max(raw[u] for u in TS if u!=t); dp=par[t]-max(par[u] for u in TS if u!=t)
    print(f"  S_{t}: raw rho {{{', '.join(f'{u}:{raw[u]:.3f}' for u in TS)}}} delta {dr:.3f} | partial(S0) {{{', '.join(f'{u}:{par[u]:.3f}' for u in TS)}}} delta {dp:.3f}")
print("S0 corr with teachers on these families:",{u:round(float(np.corrcoef(s0,tt.loc[u].loc[f0].to_numpy().ravel())[0,1]),3) for u in TS})
