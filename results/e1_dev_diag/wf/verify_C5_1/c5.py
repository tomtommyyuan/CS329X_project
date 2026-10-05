"""EXPLORATORY (dev only, not pre-registered): is the grid permutation evidence for own-teacher closeness?"""
import itertools, json, numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["claude46", "deepseek_v4", "gpt4o"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
srows = [r for r in srows if any(f".{t}_O_" in r.teacher for t in TS)]
sh_t = P.framing_shifts(M.sym_table(M.frame_table(trows, prompts)), V)
sh_s = P.framing_shifts(M.sym_table(M.frame_table(srows, prompts)), V)
runs = sorted(sh_s.teacher.unique()); own = {r: M.parse_run_id(r).teacher for r in runs}
inh = M.inheritance(sh_s, sh_t, own, V, n_perm=0, n_boot=0)
inh = inh[inh.variant == "all"] if "all" in set(inh.variant) else inh
print(inh[["run_id", "teacher"] + [f"rho__{t}" for t in TS] + ["delta_rho"]].round(3).to_string(index=False))
g = M.grid_permutation(inh, n_perm=10000, seed=0); print("official-style grid perm:", g)
R = inh[[f"rho__{t}" for t in TS]].to_numpy(); oi = np.array([TS.index(x) for x in inh.teacher])
def d_row(row, j):
    m = row.copy(); m[j] = -np.inf; return row[j] - m.max()
D = np.array([[d_row(R[i], j) for j in range(3)] for i in range(len(R))])  # per-run delta if labelled j
grp = np.array([TS.index(own[r]) for r in inh.run_id])
print("\nseed-mean delta matrix (rows=student group, cols=label assigned):")
Dg = np.array([D[grp == a].mean(0) for a in range(3)]); print(pd.DataFrame(Dg, index=TS, columns=TS).round(3))
print("\nblock-level (exchangeable unit = teacher group) exact permutation, 3! = 6 assignments:")
vals = []
for perm in itertools.permutations(range(3)):
    v = np.mean([Dg[a, perm[a]] for a in range(3)]); vals.append(v)
    print(" ", {TS[a]: TS[perm[a]] for a in range(3)}, round(v, 4))
obs = vals[0]; print("observed", round(obs, 4), "rank-p", sum(v >= obs for v in vals) / 6)
# pseudo-replication check: replace each run row by its group mean (zero seed noise) -> grid perm sd
Rg = np.array([R[grp == a].mean(0) for a in range(3)])[grp]
g2 = M.grid_permutation(inh.assign(**{f"rho__{t}": Rg[:, k] for k, t in enumerate(TS)}), n_perm=10000, seed=0)
print("\ngrid perm with seeds collapsed to group means (5 identical copies each):", g2)
# family bootstrap of double-centred diagonal (trace) on seed-pooled profiles
pooled = sh_s.assign(g=sh_s.teacher.map(lambda w: "S_" + own[w])).groupby(["g", "family_id", "variant"])["r"].mean().reset_index()
fam = sorted(set(pooled.family_id) & set(sh_t.family_id))
def mat(df, who_col, whos):
    return np.stack([df[df[who_col] == w].pivot_table(index="family_id", columns="variant", values="r").reindex(index=fam, columns=V).to_numpy() for w in whos])
S = mat(pooled, "g", ["S_" + t for t in TS]); T = mat(sh_t, "teacher", TS)
ok = ~np.isnan(S).any((0, 2)) & ~np.isnan(T).any((0, 2)); S, T = S[:, ok], T[:, ok]; nf = ok.sum()
def corrmat(S, T):
    s = S.reshape(3, -1); t = T.reshape(3, -1); s = s - s.mean(1, keepdims=True); t = t - t.mean(1, keepdims=True)
    return (s @ t.T) / np.outer(np.sqrt((s**2).sum(1)), np.sqrt((t**2).sum(1)))
def stats(C):
    traces = [sum(C[a, p[a]] for a in range(3)) for p in itertools.permutations(range(3))]
    dc = C - C.mean(1, keepdims=True) - C.mean(0, keepdims=True) + C.mean()
    Dm = np.array([[d_row(C[a], j) for j in range(3)] for a in range(3)])
    dl = [np.mean([Dm[a, p[a]] for a in range(3)]) for p in itertools.permutations(range(3))]
    return traces[0] - np.mean(traces[1:]), np.diag(dc), dl[0] - np.mean(dl[1:])
C = corrmat(S, T); print(f"\nseed-pooled corr matrix ({nf} families), rows=students cols=teachers:\n", pd.DataFrame(C, index=TS, columns=TS).round(3))
c0 = stats(C); print("trace contrast", round(c0[0], 4), "double-centred diag", c0[1].round(3), "delta-stat contrast", round(c0[2], 4))
rng = np.random.default_rng(0); B = []
for _ in range(5000):
    ix = rng.integers(0, nf, nf); st = stats(corrmat(S[:, ix], T[:, ix])); B.append([st[0], *st[1], st[2]])
B = np.array(B); lab = ["trace_contrast", "dc_claude", "dc_deepseek", "dc_gpt4o", "delta_contrast"]
for k, l in enumerate(lab):
    print(f"  {l}: est {[c0[0], *c0[1], c0[2]][k]:.3f} 95% family-boot CI [{np.quantile(B[:, k], .025):.3f}, {np.quantile(B[:, k], .975):.3f}], share<=0 {np.mean(B[:, k] <= 0):.3f}")
