"""Exploratory (dev, not pre-registered): diagonal-minus-offdiagonal interaction of the student x teacher
profile matrix, label permutation over the 15 runs, family bootstrap, per-seed values."""
import pickle, numpy as np, pandas as pd
from scipy.stats import rankdata
D = pickle.load(open("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q3_2/tables.pkl", "rb"))
TS = ["claude46", "deepseek_v4", "gpt4o"]
RUNS = [f"qwen3-4b.{t}_O_s{s}" for t in TS for s in range(1, 6)]
LAB = np.repeat(np.arange(3), 5)
rng = np.random.default_rng(12345)
NP, NB = 20000, 5000

def arrays(name, variants=None, value="r"):
    sh_t, sh_s = D[name]
    sh = pd.concat([sh_t, sh_s])
    if variants: sh = sh[sh.variant.isin(variants)]
    piv = sh.pivot_table(index=["family_id", "variant"], columns="teacher", values=value)
    piv = piv[TS + RUNS + ["S0_relaxed"]]
    full = piv.dropna(subset=TS + RUNS)
    # keep families complete on all variants for all whos
    nv = full.reset_index().groupby("family_id").size()
    nvar = sh.variant.nunique()
    fams = nv[nv == nvar].index
    full = full[full.index.get_level_values(0).isin(fams)]
    return full

def corr_rows(A, B):  # A (k,n), B (m,n) -> (k,m) Pearson
    A = A - A.mean(1, keepdims=True); B = B - B.mean(1, keepdims=True)
    return (A @ B.T) / np.sqrt((A**2).sum(1))[:, None] / np.sqrt((B**2).sum(1))[None, :]

def inter(Mx):
    d = np.trace(Mx) / 3; o = (Mx.sum() - np.trace(Mx)) / 6
    return d - o

def group_mean(X, lab):
    return np.stack([X[lab == g].mean(0) for g in range(3)])

def stat_pooled(X, T, lab, spearman=False):
    G = group_mean(X, lab)
    if spearman:
        G = np.apply_along_axis(rankdata, 1, G); T = np.apply_along_axis(rankdata, 1, T)
    return inter(corr_rows(G, T))

def stat_perseed(X, T, lab):
    C = corr_rows(X, T)  # 15x3
    Mx = np.stack([C[lab == g].mean(0) for g in range(3)])
    return inter(Mx)

def agree_stat(X, T, lab):
    A = ((X[:, None, :] > 0.5) == (T[None, :, :] > 0.5)).mean(2)  # 15x3
    return inter(np.stack([A[lab == g].mean(0) for g in range(3)]))

def negjsd_stat(X, T, lab):
    e = 1e-6
    def jsd(p, q):
        p = np.clip(p, e, 1-e); q = np.clip(q, e, 1-e); m = (p+q)/2
        kl = lambda a, b: a*np.log2(a/b) + (1-a)*np.log2((1-a)/(1-b))
        return 0.5*kl(p, m) + 0.5*kl(q, m)
    J = jsd(X[:, None, :], T[None, :, :]).mean(2)
    return inter(-np.stack([J[lab == g].mean(0) for g in range(3)]))

def run(name, full, fn, fam_index, boot=True):
    X = full[RUNS].to_numpy().T; T = full[TS].to_numpy().T
    obs = fn(X, T, LAB)
    null = np.array([fn(X, T, rng.permutation(LAB)) for _ in range(NP)])
    p = (np.sum(null >= obs) + 1) / (NP + 1)
    seeds = [fn(X[[s, 5+s, 10+s]], T, np.arange(3)) for s in range(5)]
    ci = (np.nan, np.nan)
    if boot:
        fams = fam_index.unique(); codes = pd.Categorical(fam_index, categories=fams).codes
        rows_by_f = [np.flatnonzero(codes == i) for i in range(len(fams))]
        bs = []
        for _ in range(NB):
            pick = rng.integers(0, len(fams), len(fams))
            ix = np.concatenate([rows_by_f[i] for i in pick])
            bs.append(fn(X[:, ix], T[:, ix], LAB))
        ci = tuple(np.quantile(bs, [0.025, 0.975]))
    print(f"{name:45s} nfam={len(fam_index.unique()):3d} ncell={X.shape[1]:4d} obs={obs:+.3f} null_mean={null.mean():+.3f} null_sd={null.std():.3f} p={p:.5f} "
          f"seeds=[{', '.join(f'{s:+.3f}' for s in seeds)}] famboot95=[{ci[0]:+.3f},{ci[1]:+.3f}]", flush=True)
    return obs, p, seeds

res = {}
seen = arrays("seen"); fi = seen.index.get_level_values(0)
res["pooled_pearson_seen"] = run("pooled Pearson r, seen T1/3/5/6", seen, stat_pooled, fi)
res["pooled_spearman_seen"] = run("pooled Spearman r, seen", seen, lambda X, T, l: stat_pooled(X, T, l, True), fi)
res["perseed_pearson_seen"] = run("per-seed Pearson averaged, seen", seen, stat_perseed, fi)
a5 = arrays("all5"); fi5 = a5.index.get_level_values(0)
res["pooled_pearson_all5"] = run("pooled Pearson r, T0+seen", a5, stat_pooled, fi5)
t0 = a5[a5.index.get_level_values(1) == "T0"]
res["pooled_pearson_T0only"] = run("pooled Pearson r, T0 cells only (5-var demean)", t0, stat_pooled, t0.index.get_level_values(0))
# T5/T6 suggestibility cells only
s56 = seen[seen.index.get_level_values(1).isin(["T5", "T6"])]
res["pooled_T5T6"] = run("pooled Pearson r, T5/T6 cells only", s56, stat_pooled, s56.index.get_level_values(0))
# teacher-centered: subtract mean teacher profile from each teacher (teacher-specific component)
tc = seen.copy(); tm = tc[TS].mean(1)
for t in TS: tc[t] = tc[t] - tm
res["teacher_centered"] = run("pooled Pearson, teachers minus teacher mean", tc, stat_pooled, fi)
# residualize students and teachers on S0_relaxed profile (cells where S0 has r)
rs = seen.dropna(subset=["S0_relaxed"]).copy()
z = rs["S0_relaxed"].to_numpy(); z = z - z.mean()
for c in TS + RUNS:
    y = rs[c].to_numpy(); b = (y - y.mean()) @ z / (z @ z); rs[c] = y - b * z
res["resid_S0"] = run("pooled Pearson, residualized on S0_relaxed", rs, stat_pooled, rs.index.get_level_values(0))
# first-order: agreement and -JSD on p_sym, seen variants, cells all have
sym = pd.concat([D["sym_t"], D["sym_s"]]); sym = sym[sym.variant.isin(["T1","T3","T5","T6"])]
ps = sym.pivot_table(index=["family_id","variant"], columns="teacher", values="p_sym")[TS+RUNS].dropna()
res["agreement"] = run("majority agreement on p_sym, seen", ps, agree_stat, ps.index.get_level_values(0))
res["neg_jsd"] = run("-JSD on p_sym, seen", ps, negjsd_stat, ps.index.get_level_values(0))
pickle.dump(res, open("/hai/scratch/tomyyc/vcd_diag/wf/verify_Q3_2/res.pkl", "wb"))
