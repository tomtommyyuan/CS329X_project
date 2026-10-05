"""EXPLORATORY (dev only): dependence of delta_rho across teachers under joint family bootstrap (n=278)."""
import sys, numpy as np, pickle
from scipy.stats import norm
sys.path.insert(0, "src")
from vcd.analysis.e1_metrics import holm, _rowwise_corr
mats = pickle.load(open("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q4_3/mats.pkl", "rb"))
TS = ["claude46", "deepseek_v4", "gpt4o"]; nf = 139; rng = np.random.default_rng(99)
mu0 = {"claude46": -0.0905, "deepseek_v4": 0.0891, "gpt4o": -0.0955}; sd0 = {"claude46": 0.0599, "deepseek_v4": 0.0472, "gpt4o": 0.0495}  # my dev perm null (5000)
def run(n, B, joint=True):
    D = np.empty((B, 3))
    for c in range(0, B, 1000):
        k = min(1000, B - c)
        idx_common = rng.integers(0, nf, (k, n))
        for j, t in enumerate(TS):
            idx = idx_common if joint else rng.integers(0, nf, (k, n))
            S = mats[t][1][idx].reshape(k, -1)
            r = {u: _rowwise_corr(S, mats[t][2][u][idx].reshape(k, -1)) for u in TS}
            D[c:c+k, j] = r[t] - np.max(np.stack([r[u] for u in TS if u != t]), 0)
    return D
for joint in (True, False):
    D = run(278, 40000, joint)
    p = np.stack([norm.sf((D[:, j] - mu0[t]) / (sd0[t] / np.sqrt(2))) for j, t in enumerate(TS)], 1)
    ph = np.array([holm(r) for r in p[:20000]]); passed = (ph < .05) & (D[:20000] > 0)
    print("joint" if joint else "indep", "sd", D.std(0).round(4), "corr\n", np.corrcoef(D.T).round(3),
          "\nP(delta>0)", (D > 0).mean(0).round(4), "per-teacher pass", passed.mean(0).round(4), "P(>=2 pass)", (passed.sum(1) >= 2).mean().round(4))
    g = D[:, 2] > 0; print("  P(ds delta | gpt delta>0) mean", D[g, 1].mean().round(4), "vs overall", D[:, 1].mean().round(4))
