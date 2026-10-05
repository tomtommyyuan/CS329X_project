"""EXPLORATORY (dev only): Spearman matrix + family bootstrap of (partial rho_own - partial rho_other_max | S0)."""
import sys; sys.path.insert(0, "/hai/scratch/tomyyc/vcd_diag/wf/verify_C3_1")
import numpy as np, pandas as pd
from c3_lib import build, partial, TS
W = build(False)[["S0", "S_gpt4o", "S_claude46", "S_deepseek_v4"] + TS].dropna()
print("Spearman (common cells):"); print(W.rank().corr().round(3).to_string())
own = {"S_gpt4o": "gpt4o", "S_claude46": "claude46", "S_deepseek_v4": "deepseek_v4"}
fams = W.index.get_level_values(0).unique().to_numpy(); rng = np.random.default_rng(0)
by = {f: W.xs(f, level=0) for f in fams}
def stats(D):
    out = {}
    for g, o in own.items():
        raw = {t: np.corrcoef(D[g], D[t])[0, 1] for t in TS}
        par = {t: partial(D[g], D[t], D["S0"]) for t in TS}
        out[g] = (raw[o] - max(v for t, v in raw.items() if t != o), par[o] - max(v for t, v in par.items() if t != o))
    return out
obs = stats(W); B = []
for _ in range(2000):
    D = pd.concat([by[f] for f in rng.choice(fams, len(fams))]); B.append(stats(D))
for g in own:
    a = np.array([b[g] for b in B])
    print(g, "delta_raw=%.3f [%.3f,%.3f]  delta_partial|S0=%.3f [%.3f,%.3f]" % (obs[g][0], *np.quantile(a[:, 0], [.025, .975]), obs[g][1], *np.quantile(a[:, 1], [.025, .975])))
