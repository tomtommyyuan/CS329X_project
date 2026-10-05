"""EXPLORATORY (dev only, not pre-registered). (c) agreement gain over the base; (e) power of the pre-registered
pooled delta_rho test, extrapolated to test size. Run from the repo root:
  PYTHONPATH=/hai/scratch/tomyyc/vcd_diag/wf/quant .venv/bin/python /hai/scratch/tomyyc/vcd_diag/wf/quant/agreement_power.py
"""
import numpy as np, pandas as pd
from scipy.stats import norm
from load import load, TS, OUT

N_BOOT, N_PERM, SEED = 5000, 5000, 7
d = load(); P = d["P"]; RUNS = d["runs"]
G3 = {"gpt4o": "S[gpt4o]", "claude46": "S[claude46]", "deepseek_v4": "S[deepseek_v4]"}
SEEN = [1, 2, 3, 4]
WHO = TS + ["S0_relaxed"] + list(G3.values()) + ["S[R]"]
F = np.all([np.isfinite(P[w][:, SEEN]).all(1) for w in WHO], 0)
F5 = np.all([np.isfinite(P[w]).all(1) for w in WHO], 0)
rng = np.random.default_rng(SEED)


def agree(a, b):
    ok = (a != 0.5) & (b != 0.5)
    return float(((a[ok] > 0.5) == (b[ok] > 0.5)).mean()) if ok.any() else np.nan


def run_agreement(cols, fmask, label):
    """cols: variant columns of V5 to use; fmask: family mask. Seed-mean agreement per group."""
    fam = np.flatnonzero(fmask); n = len(fam)
    PT = {t: P[t][fam][:, cols] for t in TS}
    P0 = P["S0_relaxed"][fam][:, cols]
    SR = {g: np.stack([P[r][fam][:, cols] for r in RUNS[g]]) for g in list(G3.values()) + ["S[R]"]}  # (seeds, n, k)
    contested = ~np.all([(PT[t] > .5) == (PT[TS[0]] > .5) for t in TS], 0)

    def stats(idx, SRx):
        out = {}
        a0 = {t: agree(P0[idx].ravel(), PT[t][idx].ravel()) for t in TS}
        for g, S in SRx.items():
            for t in TS:
                pt = PT[t][idx].ravel(); p0 = P0[idx].ravel()
                a = np.mean([agree(s[idx].ravel(), pt) for s in S])
                fix = (p0 > .5) != (pt > .5)
                corr_rate = np.mean([((s[idx].ravel()[fix] > .5) == (pt[fix] > .5)).mean() for s in S]) if fix.any() else np.nan
                cm = contested[idx].ravel()
                a_c = np.mean([agree(s[idx].ravel()[cm], pt[cm]) for s in S])
                out[(g, t)] = dict(agree=a, agree_S0=a0[t], gain=a - a0[t], n_base_wrong=int(fix.sum()), correction_rate=corr_rate, agree_contested=a_c, n_contested=int(cm.sum()))
        return out

    full = np.arange(n)
    obs = stats(full, SR)
    tab = pd.DataFrame([dict(cells=label, student=g, teacher=t, **v) for (g, t), v in obs.items()])

    def deltas(o):
        res = {}
        for t in TS:
            g = G3[t]
            for m in ("gain", "correction_rate", "agree_contested"):
                res[f"row_{m}_{t}"] = o[(g, t)][m] - max(o[(g, u)][m] for u in TS if u != t)
                res[f"col_{m}_{t}"] = o[(g, t)][m] - max(o[(G3[u], t)][m] for u in TS if u != t)
        return res

    dobs = deltas(obs)
    boot = []
    for _ in range(N_BOOT // 5):  # agreement bootstrap is slower (seed loop); 1000 resamples
        b = rng.integers(0, n, n)
        boot.append(deltas(stats(b, SR)))
    # label permutation for col deltas: per family, permute which trained group (with all its seeds) gets which label
    st3 = np.stack([SR[G3[t]] for t in TS])  # (3, 5, n, k)
    lp = []
    for _ in range(N_PERM // 5):
        pm = np.argsort(rng.random((n, 3)), axis=1)
        SRp = {G3[t]: st3[pm[:, gi], :, full].transpose(1, 0, 2) for gi, t in enumerate(TS)}
        lp.append(deltas(stats(full, SRp)))
    rows = []
    for k, v in dobs.items():
        bb = np.array([x[k] for x in boot]); bb = bb[np.isfinite(bb)]
        r = dict(cells=label, stat=k, value=v, ci_lo=np.quantile(bb, .025), ci_hi=np.quantile(bb, .975), boot_se=bb.std())
        if k.startswith("col"):
            nl = np.array([x[k] for x in lp]); r["p_labelperm"] = (np.sum(nl >= v) + 1) / (len(nl) + 1)
        rows.append(r)
    return tab, pd.DataFrame(rows)


print("=== (c) agreement with each teacher, seed-mean, vs S0_relaxed on the same cells ===")
tabs, sts = [], []
for cols, fm, label in [(SEEN, F, "seen T1-T6 (139 fam)"), ([0], F5, "T0 only (137 fam)")]:
    tab, st = run_agreement(cols, fm, label)
    tabs.append(tab); sts.append(st)
    print(f"\n-- {label}"); print(tab.round(3).to_string(index=False)); print(st.round(4).to_string(index=False))
pd.concat(tabs).to_csv(f"{OUT}/agreement_gain.csv", index=False); pd.concat(sts).to_csv(f"{OUT}/agreement_gain_stats.csv", index=False)

# ------------------------------------------------------------------ (e) power
print("\n=== (e) power of the pre-registered pooled delta_rho (row delta, raw Pearson), 139 dev families ===")
fam = np.flatnonzero(np.all([np.isfinite(P[w][:, SEEN]).all(1) for w in TS + list(G3.values())], 0)); n = len(fam)
def sh(p): p = p[fam][:, SEEN]; return p - p.mean(1, keepdims=True)
RT = {t: sh(P[t]) for t in TS}; RS = {t: sh(P[G3[t]]) for t in TS}


def rowcorr(X, Y):
    X = X - X.mean(1, keepdims=True); Y = Y - Y.mean(1, keepdims=True)
    return (X * Y).sum(1) / np.sqrt((X * X).sum(1) * (Y * Y).sum(1))


NB = 10000
rows = []
for t in TS:
    others = [u for u in TS if u != t]
    S = RS[t]
    obs = {u: rowcorr(S.reshape(1, -1), RT[u].reshape(1, -1))[0] for u in TS}
    d_obs = obs[t] - max(obs[u] for u in others)
    b = rng.integers(0, n, (NB, n))
    rb = {u: rowcorr(S[b].reshape(NB, -1), RT[u][b].reshape(NB, -1)) for u in TS}
    db = rb[t] - np.maximum(*[rb[u] for u in others])
    pm = np.stack([rng.permutation(n) for _ in range(NB)])
    rp = {u: rowcorr(S[pm].reshape(NB, -1), np.broadcast_to(RT[u].reshape(1, -1), (NB, RT[u].size))) for u in TS}
    dn = rp[t] - np.maximum(*[rp[u] for u in others])
    se = db.std(); se_t = se / np.sqrt(2)
    r = dict(teacher=t, n_fam=n, delta_obs=d_obs, boot_se_dev=se, boot_se_test=se_t, null_mean_dev=dn.mean(), null_sd_dev=dn.std(),
             p_perm=(np.sum(dn >= d_obs) + 1) / (NB + 1))
    for lab, a in [("a.0167", 0.05 / 3), ("a.025", 0.025), ("a.05", 0.05)]:
        thr = np.quantile(dn, 1 - a) / np.sqrt(2)   # whole null scales ~ 1/sqrt(n_families)
        r[f"thr_test_{lab}"] = thr
        r[f"mde80_test_{lab}"] = thr + norm.ppf(0.8) * se_t
    rows.append(r)
pw = pd.DataFrame(rows)
print(pw.round(4).T.to_string())
pw.to_csv(f"{OUT}/power.csv", index=False)

# full-rule power by simulation: >= 2/3 teachers with delta > 0 and Holm p < .05; normal approx of null (scaled)
print("\nP(E2 rule passes on test) by simulation (normal approximations; delta true = same value for all 3 teachers unless noted)")
sim = []
for lab, dtrue in [("0.05 each", [0.05] * 3), ("0.10 each", [0.10] * 3), ("0.15 each", [0.15] * 3), ("0.20 each", [0.20] * 3),
                   ("dev point estimates", list(pw.delta_obs))]:
    k = 100000
    dh = np.stack([rng.normal(dt, s, k) for dt, s in zip(dtrue, pw.boot_se_test)], 1)
    mu0 = pw.null_mean_dev.to_numpy() / np.sqrt(2); sd0 = pw.null_sd_dev.to_numpy() / np.sqrt(2)
    p = norm.sf((dh - mu0) / sd0)
    o = np.argsort(p, 1); ps = np.take_along_axis(p, o, 1)
    adj = np.maximum.accumulate(np.minimum(1, ps * np.array([3, 2, 1])), axis=1)
    padj = np.empty_like(adj); np.put_along_axis(padj, o, adj, 1)
    passes = ((padj < 0.05) & (dh > 0)).sum(1)
    sim.append(dict(scenario=lab, deltas=np.round(dtrue, 3).tolist(), p_ge2_pass=(passes >= 2).mean(), p_ge1_pass=(passes >= 1).mean(), p_3_pass=(passes == 3).mean()))
print(pd.DataFrame(sim).round(3).to_string(index=False))
pd.DataFrame(sim).to_csv(f"{OUT}/power_rule_sim.csv", index=False)
