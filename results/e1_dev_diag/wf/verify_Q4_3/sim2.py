"""EXPLORATORY (dev only): simulate test E2 outcome treating dev as truth."""
import sys, numpy as np, pickle
sys.path.insert(0, "src")
from vcd.analysis.e1_metrics import holm, _corr_with_fixed, _rowwise_corr
mats = pickle.load(open("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q4_3/mats.pkl", "rb"))
TS = ["claude46", "deepseek_v4", "gpt4o"]
fams0 = mats[TS[0]][0]; assert all(mats[t][0] == fams0 for t in TS)
nf = len(fams0); rng = np.random.default_rng(12345)
def delta(S, T, t):
    r = {u: _corr_with_fixed(S.reshape(1, -1), T[u].ravel())[0] for u in TS}
    return r[t] - max(r[u] for u in TS if u != t)
def perm_p(S, T, t, n_perm, rng):
    n = S.shape[0]; d0 = delta(S, T, t)
    perms = np.argsort(rng.random((n_perm, n)), axis=1)
    Xp = S[perms].reshape(n_perm, -1)
    r = {u: _corr_with_fixed(Xp, T[u].ravel()) for u in TS}
    dn = r[t] - np.max(np.stack([r[u] for u in TS if u != t]), 0)
    return d0, (np.sum(dn >= d0) + 1) / (n_perm + 1), dn.mean(), dn.std()
# dev perm null stats
for t in TS:
    S, T = mats[t][1], mats[t][2]
    d0, p, m, s = perm_p(S, T, t, 5000, rng); print("dev", t, round(d0,4), "p", round(p,4), "null mean", round(m,4), "sd", round(s,4))
for k_mult, B, NP in [(1, 1000, 1000), (2, 2000, 1000)]:
    n = nf * k_mult
    res = []
    for b in range(B):
        idx = rng.integers(0, nf, n)
        out = []
        for t in TS:
            S, T = mats[t][1][idx], {u: mats[t][2][u][idx] for u in TS}
            d, p, _, _ = perm_p(S, T, t, NP, rng)
            # per-variant delta (for 'not single type' condition)
            dv = [delta(S[:, [j]], {u: T[u][:, [j]] for u in TS}, t) for j in range(4)]
            out.append((d, p, sum(x > 0 for x in dv)))
        ds = np.array([o[0] for o in out]); ps = np.array([o[1] for o in out]); nv = np.array([o[2] for o in out])
        ph = holm(ps); passed = (ds > 0) & (ph < 0.05)
        res.append((passed.sum(), ((passed) & (nv >= 2)).sum(), *passed, *(ds > 0)))
    res = np.array(res)
    print(f"n_fam={n} B={B}: P(>=2/3 pass)={np.mean(res[:,0]>=2):.4f}  P(>=2/3 pass & >=2 variants delta>0)={np.mean(res[:,1]>=2):.4f}  "
          f"per-teacher pass {res[:,2:5].mean(0).round(4)}  P(delta>0) {res[:,5:8].mean(0).round(4)}  P(>=1 pass)={np.mean(res[:,0]>=1):.4f}")
