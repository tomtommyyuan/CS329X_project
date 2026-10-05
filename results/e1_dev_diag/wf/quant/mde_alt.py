"""EXPLORATORY (dev only). Normal-approximation MDE on test (assumes ~2x dev families: spread / sqrt(2); null mean kept)
for the alternative statistics in matrix_stats.csv / resid_matrix_stats.csv. Holm alpha for 3 col deltas = 0.05/3;
interaction = single test at 0.05. One-sided (p = share null >= observed)."""
import pandas as pd, numpy as np
from scipy.stats import norm
OUT = "/hai/scratch/tomyyc/vcd_diag/wf/quant"
st = pd.concat([pd.read_csv(f"{OUT}/matrix_stats.csv"), pd.read_csv(f"{OUT}/resid_matrix_stats.csv")])
st = st[st.analysis.isin(["a_rho|none", "a_rho|S0", "a_rho|S0+rbar", "a_resid_rho|none", "a_resid_rho|S0", "b_gain_vs_(rT-rbar)", "d_sugg_corr", "f_T0_corr"])]
rows = []
for _, r in st.iterrows():
    if not (r.stat.startswith("col") or r.stat == "interaction" or r.stat.startswith("row")):
        continue
    a = 0.05 if r.stat == "interaction" else 0.05 / 3
    thr = r.null_mean + norm.ppf(1 - a) * r.null_sd / np.sqrt(2)
    se_t = r.boot_se / np.sqrt(2)
    rows.append(dict(analysis=r.analysis, stat=r.stat, dev_value=r.value, dev_p=r.p, thr_test=thr, mde80_test=thr + norm.ppf(0.8) * se_t,
                     power_if_true_eq_dev=norm.sf((thr - r.value) / se_t)))
out = pd.DataFrame(rows)
print(out.round(3).to_string(index=False))
out.to_csv(f"{OUT}/mde_alt.csv", index=False)
