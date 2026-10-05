"""EXPLORATORY (dev only). Family-bootstrap SE of the structural permutation-null mean d0 (estimated on dev, projected to test)."""
import sys; sys.argv=[sys.argv[0]]
exec(open("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q5_4/mde.py").read().split("out = {}")[0])
for t in TS:
    rs = [r for r in runs if M.parse_run_id(r).teacher == t and M.parse_run_id(r).version == "O"]
    mats = [mat(sh_s, r) for r in rs]
    fams = sorted(set.intersection(*[set(m.index) for m in mats], *[set(Tm[u].index) for u in TS]))
    S = np.mean([m.loc[fams].to_numpy() for m in mats], axis=0); T = {u: Tm[u].loc[fams].to_numpy() for u in TS}
    n = len(fams); oth = [u for u in TS if u != t]; d0s = []
    for _ in range(2000):
        b = rng.integers(0, n, n); Sb = S[b]; Tb = {u: T[u][b] for u in TS}
        Sb = Sb - Sb.mean(1, keepdims=True)*0  # keep rows as is (already family-demeaned)
        r0 = {u: n*np.dot(Sb.mean(0), Tb[u].mean(0))/np.sqrt((Sb**2).sum()*(Tb[u]**2).sum()) for u in TS}
        d0s.append(r0[t]-max(r0[u] for u in oth))
    d0s = np.array(d0s); print(t, "d0 boot mean %.3f sd(dev n) %.3f sd(test, /sqrt2) %.3f" % (d0s.mean(), d0s.std(), d0s.std()/np.sqrt(2)))
