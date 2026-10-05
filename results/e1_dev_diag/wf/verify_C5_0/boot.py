# exploratory (dev, not pre-registered): family bootstrap of diagonal contrasts on seed-pooled profiles
import numpy as np, pandas as pd, itertools
from pathlib import Path
import vcd.analysis.e1_metrics as M, vcd.teacher.profile as P
V=["T1","T3","T5","T6"]; T=["claude46","deepseek_v4","gpt4o"]
prompts=M.load_prompts("data/prompts/dev_prompts_v2.jsonl"); pid=set(prompts)
srows=[r for r in M.load_run_responses(Path("runs"),"dev","qwen3-4b") if r.prompt_id in pid]
trows=M.load_responses([Path(f"data/teacher_phase1/{t}_dev_profile.jsonl") for t in T],pid)
ss=P.framing_shifts(M.sym_table(M.frame_table(srows,prompts)),V); st=P.framing_shifts(M.sym_table(M.frame_table(trows,prompts)),V)
runs=sorted(ss.teacher.unique()); print(runs)
def piv(df,name): return df[df.teacher==name].pivot(index="family_id",columns="variant",values="r")[V]
grp={t:[r for r in runs if M.is_run_id(r) and M.parse_run_id(r).teacher==t and M.parse_run_id(r).version=="O"] for t in T}
grpR=[r for r in runs if M.is_run_id(r) and M.parse_run_id(r).teacher=="R"] if any("_R_" in r for r in runs) else [r for r in runs if "R_" in r]
print({k:len(v) for k,v in grp.items()},grpR)
tm={t:piv(st,t) for t in T}
runm={r:piv(ss,r) for r in runs}
fams=set.intersection(*[set(m.dropna().index) for m in list(tm.values())+[runm[r] for t in T for r in grp[t]]])
fams=sorted(fams); print("families",len(fams))
Tm=np.stack([tm[t].loc[fams].to_numpy() for t in T])            # (3,F,4)
Sm=np.stack([np.mean([runm[r].loc[fams].to_numpy() for r in grp[t]],0) for t in T])  # seed-pooled (3,F,4)
def G_of(idx):
    G=np.zeros((3,3))
    for i in range(3):
        for j in range(3):
            G[i,j]=np.corrcoef(Sm[i][idx].ravel(),Tm[j][idx].ravel())[0,1]
    return G
def stats(G):
    col=np.mean([G[t,t]-np.mean([G[s,t] for s in range(3) if s!=t]) for t in range(3)])
    D=G-G.mean(0)-G.mean(1)[:,None]+G.mean()
    dr=np.mean([G[t,t]-max(G[t,j] for j in range(3) if j!=t) for t in range(3)])
    colmin=min(G[t,t]-max(G[s,t] for s in range(3) if s!=t) for t in range(3))
    return dict(col_contrast=col,dc_trace=np.trace(D)/3,mean_delta_rho=dr,min_col_margin=colmin)
F=len(fams); G=G_of(np.arange(F)); print(pd.DataFrame(G,index=["S_"+t for t in T],columns=T).round(3)); obs=stats(G); print({k:round(v,4) for k,v in obs.items()})
rng=np.random.default_rng(0); B=[stats(G_of(rng.integers(0,F,F))) for _ in range(5000)]
B=pd.DataFrame(B)
for k in obs: print(k,"obs",round(obs[k],4),"boot 95%",np.percentile(B[k],[2.5,97.5]).round(4),"P(<=0)",(B[k]<=0).mean().round(4))
# share of bootstraps where every column's max row is its own student group (diagonal argmax)
def diagmax(idx):
    g=G_of(idx); return all(np.argmax(g[:,t])==t for t in range(3))
print("P(col argmax = own for all 3 cols)",np.mean([diagmax(rng.integers(0,F,F)) for _ in range(2000)]))
