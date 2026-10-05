"""RESIDUAL variant of section (a): r minus each model's own variant mean (type effect), i.e. family-specific
profile only (profile.residual_shifts). EXPLORATORY follow-up analyses on DEV only (not pre-registered; no test file is read).

Run from the repo root:
  PYTHONPATH=/hai/scratch/tomyyc/vcd_diag/wf/quant .venv/bin/python /hai/scratch/tomyyc/vcd_diag/wf/quant/analysis.py

Inputs (via load.py): data/prompts/dev_prompts_v2.jsonl, data/teacher_phase1/{t}_dev_profile.jsonl,
runs/qwen3-4b/*/eval/dev_responses.jsonl. Student groups are seed-pooled (mean p_sym over seeds; r is linear in p,
so this equals the pre-registered pooled_shifts). S0_relaxed = untrained base with the 0.9 letter-mass rule relaxed.

Sections: (a) base-controlled inheritance, (b) distillation gain, (c) agreement gain over base,
(d) per-family suggestibility, (e) power, (f) unseen framing T0. Output: stdout + CSVs in OUT.
"""
import sys
import numpy as np, pandas as pd
from load import load, TS, OUT

N_BOOT, N_PERM, SEED = 5000, 5000, 20261005
d = load(); P = d["P"]; RUNS = d["runs"]
G3 = {"gpt4o": "S[gpt4o]", "claude46": "S[claude46]", "deepseek_v4": "S[deepseek_v4]"}
GALL = list(G3.values()) + ["S[R]"]
SEEN = [1, 2, 3, 4]  # columns T1 T3 T5 T6 in V5 order
WHO = TS + ["S0_relaxed"] + GALL
F = np.all([np.isfinite(P[w][:, SEEN]).all(1) for w in WHO], 0)
F5 = np.all([np.isfinite(P[w]).all(1) for w in WHO], 0)
print(f"families complete on T1,T3,T5,T6 for all teachers/groups/S0: {F.sum()}; also on T0: {F5.sum()}")


def shifts(p):
    """r on seen variants (n x 4) and r_T0 = p(T0) - mean_seen p (n,)."""
    m = p[:, SEEN].mean(1, keepdims=True)
    return p[:, SEEN] - m, p[:, 0] - m[:, 0]


R = {w: shifts(P[w][F])[0] for w in WHO}
R = {w: v - v.mean(0, keepdims=True) for w, v in R.items()}  # RESIDUAL: remove each model's own type effects delta(j)
R["rbar"] = np.mean([R[t] for t in TS], 0)
nF = int(F.sum())


def corr(x, y):
    x = np.ravel(x) - np.mean(x); y = np.ravel(y) - np.mean(y)
    den = np.sqrt((x * x).sum() * (y * y).sum())
    return float((x * y).sum() / den) if den > 0 else np.nan


def resid(y, Zs):
    y = np.ravel(y)
    Z = np.column_stack([np.ones_like(y)] + [np.ravel(z) for z in Zs])
    return y - Z @ np.linalg.lstsq(Z, y, rcond=None)[0]


def pcorr(x, y, Zs):
    return corr(x, y) if not Zs else corr(resid(x, Zs), resid(y, Zs))


def ci(a):
    a = np.asarray(a, float); a = a[np.isfinite(a)]
    return float(np.quantile(a, 0.025)), float(np.quantile(a, 0.975)), float(a.std())


def holm(p):
    p = np.asarray(p, float); o = np.argsort(p); m = len(p)
    adj = np.minimum(1, p[o] * (m - np.arange(m))); adj = np.maximum.accumulate(adj)
    out = np.empty(m); out[o] = adj; return out


def label_perms(n_perm, n, rng, k=3):
    """(n_perm, n, k) within-family permutations of k student-group labels."""
    return np.argsort(rng.random((n_perm, n, k)), axis=2)


rng = np.random.default_rng(SEED)
BOOTS = rng.integers(0, nF, size=(N_BOOT, nF))
FPERMS = np.stack([rng.permutation(nF) for _ in range(N_PERM)])
LPERMS = label_perms(N_PERM, nF, rng)
GORD = [G3[t] for t in TS]  # label order for the within-family label permutation


def row_col_deltas(mat):
    """mat[g_idx, t_idx] (rows students in TS order, cols teachers in TS order).
    row delta(T) = m(S_T,T) - max_{T'!=T} m(S_T,T')  [pre-registered shape];
    col delta(T) = m(S_T,T) - max_{g!=T} m(S_g,T)    [own student vs other students, teacher fixed];
    interaction = mean diag - mean off-diagonal."""
    k = len(TS); out = {}
    for i, t in enumerate(TS):
        out[f"row_{t}"] = mat[i, i] - max(mat[i, j] for j in range(k) if j != i)
        out[f"col_{t}"] = mat[i, i] - max(mat[j, i] for j in range(k) if j != i)
    off = mat[~np.eye(k, dtype=bool)]
    out["interaction"] = float(np.trace(mat) / k - off.mean())
    return out


def run_matrix_test(name, metric, mats_fn, extra_rows=()):
    """metric(S, idx) -> {teacher: value}; S = student matrix (rows = families idx). Returns a long table with
    observed values, row/col deltas, bootstrap CI (families resampled jointly), within-family label permutation p
    for col deltas / interaction, and family-permutation p for row deltas (student rows shuffled)."""
    full = np.arange(nF)
    obs = {g: metric(mats_fn(g, full), full) for g in GALL}
    mat = np.array([[obs[G3[s]][t] for t in TS] for s in TS])
    dlt = row_col_deltas(mat)
    boot = [row_col_deltas(np.array([[metric(mats_fn(G3[s], b), b)[t] for t in TS] for s in TS])) for b in BOOTS]
    # within-family label permutation (students exchangeable under H0 'training teacher does not matter')
    stack = np.stack([mats_fn(g, full) for g in GORD])  # (3, nF, ...)
    lp = []
    for pm in LPERMS:
        Sp = [stack[pm[:, gi], full] for gi in range(3)]
        lp.append(row_col_deltas(np.array([[metric(Sp[gi], full)[t] for t in TS] for gi in range(3)])))
    # family permutation for row deltas (student rows vs fixed teacher side), pre-registered style
    fp = {t: [] for t in TS}
    for pm in FPERMS:
        for i, t in enumerate(TS):
            m = metric(mats_fn(G3[t], full)[pm], full, permuted=True)
            fp[t].append(m[t] - max(m[o] for o in TS if o != t))
    rows = []
    for g in GALL:
        rows.append(dict(analysis=name, student=g, **{f"m__{t}": obs[g][t] for t in TS}))
    tab = pd.DataFrame(rows)
    stats = []
    for key, v in dlt.items():
        lo, hi, se = ci([b[key] for b in boot])
        if key.startswith("col") or key == "interaction":
            null = np.array([x[key] for x in lp]); p = float((np.sum(null >= v) + 1) / (len(null) + 1)); ptype = "label-perm"
        else:
            t = key[4:]; null = np.array(fp[t]); p = float((np.sum(null >= v) + 1) / (len(null) + 1)); ptype = "family-perm"
        stats.append(dict(analysis=name, stat=key, value=v, ci_lo=lo, ci_hi=hi, boot_se=se, p=p, p_type=ptype, null_mean=float(null.mean()), null_sd=float(null.std())))
    st = pd.DataFrame(stats)
    for kind in ("row", "col"):
        m = st.stat.str.startswith(kind)
        st.loc[m, "p_holm"] = holm(st.loc[m, "p"].to_numpy())
    return tab, st


# ------------------------------------------------------------------ metrics on seen shifts
def make_metric(controls):
    """Partial Pearson of r_s with r_T controlling for `controls` (subset of {'S0','rbar'}); teacher side fixed."""
    def metric(S, idx, permuted=False):
        Zs = []
        if "S0" in controls:
            # S0 is student-side: when student rows are permuted (permuted=True) S0 travels with them (mats_fn packs it)
            Zs.append(S[..., 4:8].reshape(len(idx), 4))
        if "rbar" in controls:
            Zs.append(R["rbar"][idx])
        s = S[..., 0:4].reshape(len(idx), 4)
        return {t: pcorr(s, R[t][idx], Zs) for t in TS}
    return metric


def mats_seen(g, idx):
    """student shifts packed with S0 shifts (so S0 moves with the student under family permutation)."""
    return np.concatenate([R[g][idx], R["S0_relaxed"][idx]], axis=1)


all_tabs, all_stats = [], []
print("\n=== (a) base-controlled inheritance: partial Pearson(r_s, r_T | controls), seed-pooled students, 139 families ===")
for controls in [(), ("S0",), ("rbar",), ("S0", "rbar")]:
    name = "a_resid_rho|" + ("+".join(controls) or "none")
    tab, st = run_matrix_test(name, make_metric(controls), mats_seen)
    all_tabs.append(tab); all_stats.append(st)
    print(f"\n-- {name}"); print(tab.round(3).to_string(index=False)); print(st.round(4).to_string(index=False))
    sys.stdout.flush()

# S0 itself vs teachers (reference)
print("\nS0_relaxed vs teachers on the same 139 families: " + ", ".join(f"{t} {corr(R['S0_relaxed'], R[t]):.3f}" for t in TS)
      + " | vs rbar " + f"{corr(R['S0_relaxed'], R['rbar']):.3f}")
print("teacher-teacher on same cells: " + ", ".join(f"{a}-{b} {corr(R[a], R[b]):.3f}" for i, a in enumerate(TS) for b in TS[i + 1:]))


pd.concat(all_tabs).to_csv(f"{OUT}/resid_matrix_values.csv", index=False)
pd.concat(all_stats).to_csv(f"{OUT}/resid_matrix_stats.csv", index=False)
