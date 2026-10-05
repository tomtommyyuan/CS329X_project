"""EXPLORATORY (dev only). Per-seed replication of the column deltas / interaction (seed k of each teacher's
students, k = 1..5; raw Pearson and partial on S0_relaxed), 139 families."""
import numpy as np, pandas as pd
from load import load, TS, OUT
d = load(); P = d["P"]; RUNS = d["runs"]
G3 = {"gpt4o": "S[gpt4o]", "claude46": "S[claude46]", "deepseek_v4": "S[deepseek_v4]"}
SEEN = [1, 2, 3, 4]
WHO = TS + ["S0_relaxed"] + list(G3.values()) + ["S[R]"]
F = np.all([np.isfinite(P[w][:, SEEN]).all(1) for w in WHO], 0)
sh = lambda p: p[F][:, SEEN] - p[F][:, SEEN].mean(1, keepdims=True)
RT = {t: sh(P[t]) for t in TS}; R0 = sh(P["S0_relaxed"])
def res(y):
    y = y.ravel(); Z = np.column_stack([np.ones_like(y), R0.ravel()]); return y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]
c = lambda a, b: np.corrcoef(a.ravel(), b.ravel())[0, 1]
rows = []
for k in range(5):
    for ctl in ("none", "S0"):
        S = {t: sh(P[RUNS[G3[t]][k]]) for t in TS}
        m = np.array([[c(S[s], RT[t]) if ctl == "none" else c(res(S[s]), res(RT[t])) for t in TS] for s in TS])
        r = dict(seed=k + 1, control=ctl)
        for i, t in enumerate(TS):
            r[f"row_{t}"] = m[i, i] - max(m[i, j] for j in range(3) if j != i)
            r[f"col_{t}"] = m[i, i] - max(m[j, i] for j in range(3) if j != i)
        r["interaction"] = np.trace(m) / 3 - m[~np.eye(3, dtype=bool)].mean()
        rows.append(r)
df = pd.DataFrame(rows)
print(df.round(3).to_string(index=False))
print("\nshare of seeds with value > 0:")
print(df.groupby("control").agg(lambda x: (x > 0).mean() if x.dtype.kind == "f" else x.iloc[0]).drop(columns="seed").round(2).to_string())
df.to_csv(f"{OUT}/seedwise.csv", index=False)
