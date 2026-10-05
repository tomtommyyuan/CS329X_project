"""EXPLORATORY (dev): ties, agreement on common cells, family-bootstrap CIs of JSD_own - JSD_other (seed-pooled)."""
import numpy as np, pandas as pd
exec(open("/hai/scratch/tomyyc/vcd_diag/wf/verify_C6_0/c6.py").read().split("T0 = W[TS]")[0])
T0=W[TS]
print("teacher exact-0.5 cells on common:", {t:int((T0.loc[common,t]==.5).sum()) for t in TS})
print("teacher exact 0/1 share:", {t: round(float(((T0.loc[common,t]<=1e-9)|(T0.loc[common,t]>=1-1e-9)).mean()),3) for t in TS})
# agreement on common cells, excluding ties
for g in TS:
    rs=[r for r in runs if grp(r)==g]
    out={}
    for t in TS:
        a=[]
        for r in rs:
            s=W.loc[common,r].to_numpy(); p=T0.loc[common,t].to_numpy(); ok=(~np.isnan(s))&(s!=.5)&(p!=.5)
            a.append(((s[ok]>.5)==(p[ok]>.5)).mean())
        out[t]=np.round(a,3).tolist()
    print("agreement on common cells", g, out)
# quantile mapping again
pool=np.sort(np.concatenate([np.abs(T0.loc[common,t].to_numpy()-.5) for t in TS]))
Tq=T0.loc[common].copy()
for t in TS:
    c=np.abs(T0.loc[common,t]-.5); rk=c.rank(pct=True).to_numpy(); s=np.sign(T0.loc[common,t]-.5).to_numpy()
    Tq[t]=.5+s*np.quantile(pool,rk)
Th=(T0.loc[common]>.5).astype(float).where(T0.loc[common]!=.5,.5)
fam=common.get_level_values("family_id").to_numpy(); uf=np.unique(fam); idx={f:np.where(fam==f)[0] for f in uf}
rng=np.random.default_rng(1)
B=[np.concatenate([idx[f] for f in rng.choice(uf,len(uf))]) for _ in range(2000)]
for label,T in [("raw",T0.loc[common]),("quantile",Tq),("hard",Th)]:
    for g in TS:
        rs=[r for r in runs if grp(r)==g]
        S=W.loc[common,rs].to_numpy()
        jt={t: np.nanmean(np.stack([M.binary_jsd(S[:,k],T[t].to_numpy()) for k in range(len(rs))],1),axis=1) for t in TS}  # per-cell seed-mean
        for o in TS:
            if o==g: continue
            d=jt[g]-jt[o]; bs=[np.nanmean(d[b]) for b in B]
            print(f"{label:9s} S[{g}] JSD_own - JSD_{o}: {np.nanmean(d):+.4f} [{np.quantile(bs,.025):+.4f},{np.quantile(bs,.975):+.4f}]")
