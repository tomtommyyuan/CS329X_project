# EXPLORATORY (dev only, not pre-registered). Independent recomputation of agreement gains over S0_relaxed.
import json, glob, collections, numpy as np, pandas as pd
V=["T1","T3","T5","T6"]; TS=["gpt4o","claude46","deepseek_v4"]
prom={}
for l in open("data/prompts/dev_prompts_v2.jsonl"):
    d=json.loads(l); prom[d["prompt_id"]]=d
def load(path, name, relaxed=False, mass_min=None):
    acc=collections.defaultdict(list)
    for l in open(path):
        r=json.loads(l)
        if r["mode"]!="profile" or r["prompt_id"] not in prom: continue
        p=prom[r["prompt_id"]]
        if relaxed:
            if not r.get("p_letters"): continue
            px=r["p_x"]
            if mass_min is not None and r["usage"]["mass_AB"]<mass_min: continue
        else:
            if r["category"]!="answer": continue
            px=r["p_x"]
            if px is None: px=1.0 if r["choice_action"]=="x" else 0.0
        if p["focus_action"]=="y": px=1-px
        acc[(p["family_id"],p["variant"],p["order"],r["pass_idx"])].append(px)
    c=collections.defaultdict(list)
    for (f,v,o,pi),xs in acc.items(): c[(f,v,o)].append(np.mean(xs))
    out={}
    for (f,v,o),xs in c.items():
        if o!=1: continue
        if (f,v,2) in c: out[(f,v)]=(np.mean(xs)+np.mean(c[(f,v,2)]))/2
    return pd.Series(out,name=name)
S={t:load(f"data/teacher_phase1/{t}_dev_profile.jsonl",t) for t in TS}
runs={}
for p in sorted(glob.glob("runs/qwen3-4b/*/eval/dev_responses.jsonl")):
    rn=p.split("/")[2]
    if rn=="base_B_s0":
        runs["S0_relaxed"]=load(p,"S0_relaxed",relaxed=True)
        runs["S0_strict"]=load(p,"S0_strict")
    else: runs[rn]=load(p,rn)
def agree(a,b):
    df=pd.concat([a,b],axis=1).dropna()
    df=df[[k[1] in V for k in df.index]]
    x,y=df.iloc[:,0].values,df.iloc[:,1].values
    ok=(x!=0.5)&(y!=0.5)
    return ((x[ok]>.5)==(y[ok]>.5)).mean(), ok.sum()
rows=[]
for rn,s in runs.items():
    for t in TS:
        a,n=agree(s,S[t]); rows.append(dict(run=rn,teacher=t,agree=a,n=n))
A=pd.DataFrame(rows); W=A.pivot(index="run",columns="teacher",values="agree")
print(A.pivot(index="run",columns="teacher",values="n").to_string())
print(W.round(4).to_string())
s0=W.loc["S0_relaxed"]
print("S0_relaxed n cells:", len(runs["S0_relaxed"]), "S0_strict:", len(runs["S0_strict"]))
G=(W-s0)
G["grp"]=[r.rsplit("_O_",1)[0] if "_O_" in r else r for r in G.index]
gm=G[G.grp.isin(TS+["random_R_s1","random_R_s2","random_R_s3"])].groupby("grp")[TS].mean()
gm.loc["random_R"]=G[G.grp.str.startswith("random")][TS].mean()
print("\nseed-mean gain over S0_relaxed (rows=student group, cols=teacher)"); print(gm.round(4).to_string())
for t in TS:
    own=gm.loc[t,t]; oth=[gm.loc[t,u] for u in TS if u!=t]
    # 'own-specific' variants: column-demeaned (gain to t by S[t] minus mean gain to t by other students), row-demeaned
    col_other=[gm.loc[u,t] for u in TS if u!=t]
    print(t, "own gain %.4f | own - mean other-teacher gain (row) %.4f | own - max other (row) %.4f | own - mean other-students (col) %.4f"%(own, own-np.mean(oth), own-max(oth), own-np.mean(col_other)))
# double-centered (interaction) on 3x3
M=gm.loc[TS,TS].values; dc=M-M.mean(1,keepdims=True)-M.mean(0,keepdims=True)+M.mean()
print("double-centered diag:", dict(zip(TS,np.diag(dc).round(4))))
# per-seed own gain range
for t in TS:
    v=G[G.grp==t][t]; print(t,"per-seed own gain", v.round(4).tolist())
W.to_csv("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q6_5/agree.csv")

print("\n=== EXPLORATORY robustness ===")
# (1) per-seed row-specific gain: (agree_own - S0_own) - max_other(agree_other - S0_other)
for t in TS:
    vals=[]
    for s in range(1,6):
        g=W.loc[f"{t}_O_s{s}"]-s0
        vals.append(g[t]-max(g[u] for u in TS if u!=t))
    print(t,"per-seed row-specific gain",np.round(vals,4).tolist())
# (2) restrict to 139-family common set (families complete on seen for all teachers, S0, all runs)
def fams_complete(s):
    ok=collections.defaultdict(int)
    for (f,v) in s.dropna().index:
        if v in V: ok[f]+=1
    return {f for f,n in ok.items() if n==4}
common=set.intersection(*[fams_complete(S[t]) for t in TS],*[fams_complete(runs[r]) for r in runs if r!="S0_strict"])
print("common families", len(common))
def agree_f(a,b,fams):
    a=a[[k[0] in fams for k in a.index]]; return agree(a,b)[0]
Wc=pd.DataFrame({r:{t:agree_f(runs[r],S[t],common) for t in TS} for r in runs if r!="S0_strict"}).T
s0c=Wc.loc["S0_relaxed"]
for t in TS:
    seeds=[f"{t}_O_s{s}" for s in range(1,6)]
    g=(Wc.loc[seeds]-s0c).mean()
    print(t,"common-set gains",g.round(4).to_dict(),"row-specific %.4f"%(g[t]-max(g[u] for u in TS if u!=t)))
# (3) sensitivity of S0 baseline to the letter-mass threshold
for mm in [0.0,0.1,0.3,0.5,0.9]:
    s0m=load("runs/qwen3-4b/base_B_s0/eval/dev_responses.jsonl","s0m",relaxed=True,mass_min=mm)
    ag={t:agree(s0m,S[t]) for t in TS}
    line=f"mass>={mm}: n_cells(S0)={s0m.notna().sum()} "
    for t in TS:
        # students restricted to the same cells
        cells=s0m.dropna().index
        st=np.mean([agree(runs[f'{t}_O_s{s}'].reindex(cells),S[t])[0] for s in range(1,6)])
        oth={u:np.mean([agree(runs[f'{t}_O_s{s}'].reindex(cells),S[u])[0] for s in range(1,6)])-ag[u][0] for u in TS if u!=t}
        line+=f"| {t}: S0 {ag[t][0]:.3f} own-gain {st-ag[t][0]:+.3f} rowspec {st-ag[t][0]-max(oth.values()):+.3f} (n={ag[t][1]}) "
    print(line)
# (4) family bootstrap of seed-mean row-specific gains (all cells)
rng=np.random.default_rng(0)
fam=sorted({k[0] for k in runs["S0_relaxed"].index})
def tab(r,t):
    df=pd.concat([runs[r],S[t]],axis=1).dropna(); df=df[[k[1] in V for k in df.index]]
    x,y=df.iloc[:,0].values,df.iloc[:,1].values; ok=(x!=.5)&(y!=.5)
    return pd.DataFrame({"f":[k[0] for k in df.index],"m":((x>.5)==(y>.5)).astype(float),"ok":ok}).query("ok")
T={(r,t):tab(r,t) for r in runs if r!="S0_strict" and not r.startswith("random") for t in TS}
agg={k:v.groupby("f")["m"].agg(["sum","count"]).reindex(fam).fillna(0) for k,v in T.items()}
for t in TS:
    bs=[]
    for b in range(2000):
        idx=rng.integers(0,len(fam),len(fam))
        def A(r,u):
            a=agg[(r,u)].values[idx]; return a[:,0].sum()/a[:,1].sum()
        g={u:np.mean([A(f"{t}_O_s{s}",u) for s in range(1,6)])-A("S0_relaxed",u) for u in TS}
        bs.append(g[t]-max(g[u] for u in TS if u!=t))
    print(t,"row-specific gain family-bootstrap 95% CI",np.percentile(bs,[2.5,97.5]).round(4))
