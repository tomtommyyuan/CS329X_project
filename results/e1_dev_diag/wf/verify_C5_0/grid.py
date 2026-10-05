# exploratory (dev, not pre-registered): re-examine grid permutation
import itertools, numpy as np, pandas as pd
t = pd.read_csv("results/e1_dev/inheritance.csv"); t = t[t.variant=="all"]
cols=[c for c in t.columns if c.startswith("rho__")]; T=[c[5:] for c in cols]
R=t[cols].to_numpy(); own=np.array([T.index(x) for x in t.teacher])
print(T); print(pd.DataFrame(R,index=t.run_id,columns=T).round(3))
def md(a):
    o=R[np.arange(len(R)),a]; m=R.copy(); m[np.arange(len(R)),a]=-np.inf
    return np.mean(o-m.max(1))
obs=md(own); print("obs",obs)
# group-level permutation (respect seed dependence): 3! assignments
grp=[T.index(x) for x in ["claude46","deepseek_v4","gpt4o"]]
for p in itertools.permutations(range(3)):
    a=np.array([p[i] for i in own]); print("perm",[T[i] for i in p], round(md(a),4))
# per-teacher mean delta under obs
for k,x in enumerate(T):
    s=own==k; o=R[s][:,k]; m=R[s].copy(); m[:,k]=-np.inf; print(x,"mean delta",np.mean(o-m.max(1)).round(4))
# column-wise test: for each teacher column, own students vs others' students
for k,x in enumerate(T):
    print(x,"col mean own students",R[own==k,k].mean().round(3),"other students",{T[j]:R[own==j,k].mean().round(3) for j in range(3) if j!=k})
# double-centered matrix of group means
G=np.array([[R[own==i,j].mean() for j in range(3)] for i in range(3)])
print("group means rows=student teacher, cols=teacher\n",pd.DataFrame(G,index=T,columns=T).round(3))
D=G-G.mean(0)-G.mean(1)[:,None]+G.mean(); print("double-centered\n",pd.DataFrame(D,index=T,columns=T).round(3))
print("trace stat (sum diag) obs",np.trace(G).round(3),[round(sum(G[i,p[i]] for i in range(3)),3) for p in itertools.permutations(range(3))])
# leave-DeepSeek-out: grid perm on claude+gpt only, 2 teachers columns restricted
rng=np.random.default_rng(0)
for drop in T:
    keep=[k for k in range(3) if T[k]!=drop]; s=np.isin(own,keep)
    R2=R[s][:,keep]; o2=np.array([keep.index(i) for i in own[s]])
    def md2(a):
        oo=R2[np.arange(len(R2)),a]; m=R2.copy(); m[np.arange(len(R2)),a]=-np.inf; return np.mean(oo-m.max(1))
    ob=md2(o2); nul=np.array([md2(rng.permutation(o2)) for _ in range(10000)])
    print("drop",drop,"obs",round(ob,4),"null mean",nul.mean().round(4),"p",((nul>=ob).sum()+1)/10001)
