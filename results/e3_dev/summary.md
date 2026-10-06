# E3 summary (dev, student qwen3-4b-paired, variants T1, T3, T5, T6; E3 rule pre-specified 2026-10-05 (docs/03 E3 row, tasks/e3_plan.md §3) before any F / C run existed; frozen at commit 5e98fe3 (tasks/hpc_log.md); auto-generated)

Rule (docs/03 E3 row, verbatim): 效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；R 有而 F / C 无则归因于隐性内容变化. Operationalised (tasks/e3_plan.md §3): per metric, the per-teacher statistic is the seed mean of the paired difference S_{T,V,s} - S_{T,O,s} (disagreement: the mean V-W disagreement minus the teacher's own O-O seed-pair mean); the seed-pair null is the same single-pair quantity between two O seeds of the same teacher, pooled over teachers, and scaled to the statistic: SD_stat = sqrt(mean(d^2) / n_seeds [+ jackknife var of the O-O mean]), q95 = t(0.975, df = sum(n_O - 1) = 12) x SD_stat (disagreement: t(0.95)); a teacher exceeds when |stat| > q95; effect iff >= 2/3 of the 3 teachers exceed with the same sign. p from the t reference with Holm over the teachers; `no effect` only when >= 2/3 teachers pass the TOST (family-bootstrap 95% CI inside +/- 1 SD_stat; docs/04 §3), otherwise `inconclusive`. The raw single-pair q95 (`null_q95_single`, `n_pass_single`) is a sensitivity column. Primary rows: disagreement F vs C, consistency change, excess drift, inheritance by form; the other rows are secondary. Under H0 the q95 rule has a per-row false-positive rate of about 0.004, <= 0.05 family-wise over the 13 rows (Bonferroni); `p_row_holm_primary` is descriptive. CIs are family-bootstrap 2.5 / 97.5 percentiles with families resampled jointly for every seed of a teacher. Assumptions: seed noise approximately normal and independent across seeds (same-seed F / O pairs share init and data order, so the null is conservative).

**dev = freeze split**: the verdicts below are descriptive; only results/e3 (test, evaluated once after the dev freeze line in tasks/hpc_log.md) is confirmatory.

## Run inventory (runs with a readout on this split)

| teacher | n_O | n_F | n_C | seeds_O | seeds_F | seeds_C | paired_F | paired_C |
|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| deepseek_v4 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| gpt4o | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |

Base prior covariate r_0: qwen3-4b.base_B_s0 (150 complete families without the mass gate).

## Verdicts (rule 7; descriptive on dev)

| metric | tier | teachers: stat [CI] (effect in null sd, p, Holm, TOST) * = exceeds q95 | null q95 of the stat (single-pair q95; n) | pass | TOST pass | direction | verdict |
|---|---|---|---|---|---|---|---|
| disagreement F vs C | primary | claude46 -0.006 [-0.024, 0.014] (-1.019 null sd, p 0.836, Holm 1.000, TOST False); deepseek_v4 -3.4e-04 [-0.014, 0.014] (-0.051 null sd, p 0.520, Holm 1.000, TOST False); gpt4o 0.005 [-0.009, 0.020] (0.833 null sd, p 0.211, Holm 0.632, TOST False) | 0.011 (0.011; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| disagreement O vs F | secondary | claude46 -0.026 [-0.037, -0.014] (-4.676 null sd, p 1.000, Holm 1.000, TOST False); deepseek_v4 -0.016 [-0.025, -0.005] (-2.394 null sd, p 0.983, Holm 1.000, TOST False); gpt4o -0.016 [-0.025, -0.006] (-2.857 null sd, p 0.993, Holm 1.000, TOST False) | 0.011 (0.011; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| disagreement O vs C | secondary | claude46 -0.006 [-0.023, 0.014] (-1.019 null sd, p 0.836, Holm 0.844, TOST False); deepseek_v4 0.002 [-0.012, 0.017] (0.255 null sd, p 0.402, Holm 0.844, TOST False); gpt4o 0.003 [-0.011, 0.019] (0.595 null sd, p 0.281, Holm 0.844, TOST False) | 0.011 (0.011; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: flip rate F - O | primary | claude46 -0.007 [-0.018, 0.004] (-0.908 null sd, p 0.382, Holm 1.000, TOST False); deepseek_v4 0.001 [-0.010, 0.013] (0.183 null sd, p 0.858, Holm 1.000, TOST False); gpt4o -0.005 [-0.016, 0.006] (-0.661 null sd, p 0.521, Holm 1.000, TOST False) | 0.016 (0.030; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: cross-framing JSD F - O | primary | claude46 8.8e-04 [-2.8e-04, 0.002] (0.321 null sd, p 0.753, Holm 1.000, TOST True); deepseek_v4 -0.002 [-0.005, 0.002] (-0.597 null sd, p 0.561, Holm 1.000, TOST False); gpt4o -0.003 [-0.006, -0.001] (-1.239 null sd, p 0.239, Holm 0.717, TOST False) | 0.006 (0.013; 30) | 0/3 | 1/3 | nan | **inconclusive** |
| teacher agreement change F - O | secondary | claude46 -0.002 [-0.012, 0.007] (-0.403 null sd, p 0.694, Holm 1.000, TOST False); deepseek_v4 -0.001 [-0.009, 0.007] (-0.269 null sd, p 0.793, Holm 1.000, TOST False); gpt4o 0.003 [-0.005, 0.010] (0.560 null sd, p 0.586, Holm 1.000, TOST False) | 0.011 (0.020; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| excess teacher drift (JSD to own teacher) F - O | primary | claude46 0.001 [-0.003, 0.006] (0.696 null sd, p 0.500, Holm 1.000, TOST False); deepseek_v4 6.8e-04 [-0.003, 0.004] (0.325 null sd, p 0.751, Holm 1.000, TOST False); gpt4o -7.2e-04 [-0.005, 0.003] (-0.342 null sd, p 0.738, Holm 1.000, TOST False) | 0.005 (0.010; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho F - O | primary | claude46 0.001 [-0.096, 0.072] (0.046 null sd, p 0.964, Holm 1.000, TOST False); deepseek_v4 -0.031 [-0.077, 0.010] (-1.293 null sd, p 0.220, Holm 0.661, TOST False); gpt4o -0.004 [-0.046, 0.034] (-0.184 null sd, p 0.857, Holm 1.000, TOST False) | 0.052 (0.112; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: flip rate C - O | primary | claude46 -0.005 [-0.018, 0.008] (-0.696 null sd, p 0.500, Holm 1.000, TOST False); deepseek_v4 4.5e-04 [-0.016, 0.016] (0.061 null sd, p 0.952, Holm 1.000, TOST False); gpt4o -0.006 [-0.020, 0.006] (-0.841 null sd, p 0.417, Holm 1.000, TOST False) | 0.016 (0.030; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: cross-framing JSD C - O | primary | claude46 -7.0e-04 [-0.003, 0.001] (-0.253 null sd, p 0.805, Holm 0.805, TOST True); deepseek_v4 -0.006 [-0.012, -6.0e-04] (-2.228 null sd, p 0.046, Holm 0.137, TOST False)*; gpt4o -0.006 [-0.009, -0.003] (-2.117 null sd, p 0.056, Holm 0.137, TOST False) | 0.006 (0.013; 30) | 1/3 | 1/3 | - | **inconclusive** |
| teacher agreement change C - O | secondary | claude46 -0.004 [-0.021, 0.011] (-0.828 null sd, p 0.424, Holm 1.000, TOST False); deepseek_v4 3.4e-04 [-0.014, 0.013] (0.067 null sd, p 0.948, Holm 1.000, TOST False); gpt4o 0.005 [-0.007, 0.016] (0.910 null sd, p 0.381, Holm 1.000, TOST False) | 0.011 (0.020; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| excess teacher drift (JSD to own teacher) C - O | primary | claude46 -0.003 [-0.013, 0.006] (-1.592 null sd, p 0.137, Holm 0.198, TOST False); deepseek_v4 -0.004 [-0.011, 0.003] (-1.788 null sd, p 0.099, Holm 0.198, TOST False); gpt4o -0.005 [-0.012, 0.002] (-2.172 null sd, p 0.051, Holm 0.152, TOST False) | 0.005 (0.010; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho C - O | primary | claude46 -0.039 [-0.173, 0.063] (-1.611 null sd, p 0.133, Holm 0.399, TOST False); deepseek_v4 0.011 [-0.037, 0.065] (0.455 null sd, p 0.657, Holm 0.657, TOST False); gpt4o 0.031 [-0.025, 0.083] (1.298 null sd, p 0.219, Holm 0.437, TOST False) | 0.052 (0.112; 30) | 0/3 | 0/3 | nan | **inconclusive** |

Descriptive (no verdict): homogenization index, joint partial D per version, suggestibility per version, content and register checks of the training files.

## Seed-pair null: the same quantity between two O seeds of one teacher, pooled over teachers (seed_pair_null.csv)

| metric | n | mean | sd | q95 |
|---|---|---|---|---|
| flip | 30 | 0.014 | 0.010 | 0.030 |
| jsd | 30 | 0.004 | 0.004 | 0.013 |
| agree_own | 30 | 0.009 | 0.007 | 0.020 |
| jsd_own | 30 | 0.004 | 0.003 | 0.010 |
| disagree_O-O | 30 | 0.046 | 0.011 | 0.065 |
| jsd_between_O-O | 30 | 0.012 | 0.003 | 0.016 |
| delta_rho | 30 | 0.042 | 0.034 | 0.112 |

## (1) Cross-student disagreement: share of (family, variant) cells with different majority acts, same teacher and seed (disagreement.csv; disagree_conf = cells where both |p - 0.5| >= 0.1, robustness)

| teacher | pair | n_seeds | n_families | disagree | ci_lo | ci_hi | disagree_conf | jsd | jsd_ci_lo | jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 148 | 0.050 | 0.032 | 0.069 | 0.026 | 0.011 | 0.008 | 0.015 |
| claude46 | O-F | 5 | 148 | 0.029 | 0.018 | 0.042 | 0.010 | 0.006 | 0.004 | 0.008 |
| claude46 | O-C | 5 | 148 | 0.050 | 0.032 | 0.069 | 0.024 | 0.012 | 0.009 | 0.016 |
| deepseek_v4 | F-C | 5 | 147 | 0.044 | 0.031 | 0.059 | 0.026 | 0.015 | 0.011 | 0.020 |
| deepseek_v4 | O-F | 5 | 147 | 0.029 | 0.019 | 0.039 | 0.012 | 0.008 | 0.006 | 0.011 |
| deepseek_v4 | O-C | 5 | 147 | 0.046 | 0.032 | 0.062 | 0.024 | 0.016 | 0.012 | 0.021 |
| gpt4o | F-C | 5 | 149 | 0.043 | 0.029 | 0.059 | 0.022 | 0.011 | 0.008 | 0.014 |
| gpt4o | O-F | 5 | 149 | 0.022 | 0.013 | 0.032 | 0.007 | 0.005 | 0.004 | 0.007 |
| gpt4o | O-C | 5 | 149 | 0.042 | 0.027 | 0.058 | 0.020 | 0.011 | 0.008 | 0.015 |

Excess over the teacher's own O-O seed-pair mean (disagreement_excess.csv; the verdict statistic; var_oo_mean = delete-one-seed jackknife variance of the O-O mean):

| teacher | pair | n_seeds | disagree | oo_mean | n_oo_pairs | var_oo_mean | excess | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 0.050 | 0.055 | 10 | 1.6e-05 | -0.006 | -0.024 | 0.014 |
| claude46 | O-F | 5 | 0.029 | 0.055 | 10 | 1.6e-05 | -0.026 | -0.037 | -0.014 |
| claude46 | O-C | 5 | 0.050 | 0.055 | 10 | 1.6e-05 | -0.006 | -0.023 | 0.014 |
| deepseek_v4 | F-C | 5 | 0.044 | 0.045 | 10 | 2.9e-05 | -3.4e-04 | -0.014 | 0.014 |
| deepseek_v4 | O-F | 5 | 0.029 | 0.045 | 10 | 2.9e-05 | -0.016 | -0.025 | -0.005 |
| deepseek_v4 | O-C | 5 | 0.046 | 0.045 | 10 | 2.9e-05 | 0.002 | -0.012 | 0.017 |
| gpt4o | F-C | 5 | 0.043 | 0.038 | 10 | 1.6e-05 | 0.005 | -0.009 | 0.020 |
| gpt4o | O-F | 5 | 0.022 | 0.038 | 10 | 1.6e-05 | -0.016 | -0.025 | -0.006 |
| gpt4o | O-C | 5 | 0.042 | 0.038 | 10 | 1.6e-05 | 0.003 | -0.011 | 0.019 |

## (2) Consistency change V - O, paired by seed (consistency_delta.csv; flip = flip rate, jsd = cross-framing JSD)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| flip | claude46 | F | 5 | 149 | 0.040 | 0.046 | -0.007 | -0.018 | 0.004 | - |
| flip | claude46 | C | 5 | 149 | 0.041 | 0.046 | -0.005 | -0.018 | 0.008 | - |
| flip | deepseek_v4 | F | 5 | 148 | 0.105 | 0.103 | 0.001 | -0.010 | 0.013 | + |
| flip | deepseek_v4 | C | 5 | 148 | 0.104 | 0.103 | 4.5e-04 | -0.016 | 0.016 | + |
| flip | gpt4o | F | 5 | 150 | 0.068 | 0.072 | -0.005 | -0.016 | 0.006 | - |
| flip | gpt4o | C | 5 | 150 | 0.066 | 0.072 | -0.006 | -0.020 | 0.006 | - |
| jsd | claude46 | F | 5 | 149 | 0.011 | 0.010 | 8.8e-04 | -2.8e-04 | 0.002 | + |
| jsd | claude46 | C | 5 | 149 | 0.009 | 0.010 | -7.0e-04 | -0.003 | 0.001 | - |
| jsd | deepseek_v4 | F | 5 | 148 | 0.052 | 0.054 | -0.002 | -0.005 | 0.002 | - |
| jsd | deepseek_v4 | C | 5 | 148 | 0.048 | 0.054 | -0.006 | -0.012 | -6.0e-04 | - |
| jsd | gpt4o | F | 5 | 150 | 0.026 | 0.029 | -0.003 | -0.006 | -0.001 | - |
| jsd | gpt4o | C | 5 | 150 | 0.023 | 0.029 | -0.006 | -0.009 | -0.003 | - |

## (3) Teacher agreement change and excess teacher drift V - O, paired by seed (drift.csv; agree = majority-act agreement with the own teacher, jsd = JSD to the own teacher)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| agree | claude46 | F | 5 | 146 | 0.843 | 0.845 | -0.002 | -0.012 | 0.007 | - |
| agree | claude46 | C | 5 | 146 | 0.841 | 0.845 | -0.004 | -0.021 | 0.011 | - |
| agree | deepseek_v4 | F | 5 | 146 | 0.844 | 0.845 | -0.001 | -0.009 | 0.007 | - |
| agree | deepseek_v4 | C | 5 | 146 | 0.846 | 0.845 | 3.4e-04 | -0.014 | 0.013 | + |
| agree | gpt4o | F | 5 | 140 | 0.857 | 0.854 | 0.003 | -0.005 | 0.010 | + |
| agree | gpt4o | C | 5 | 140 | 0.859 | 0.854 | 0.005 | -0.007 | 0.016 | + |
| jsd | claude46 | F | 5 | 147 | 0.111 | 0.110 | 0.001 | -0.003 | 0.006 | + |
| jsd | claude46 | C | 5 | 147 | 0.106 | 0.110 | -0.003 | -0.013 | 0.006 | - |
| jsd | deepseek_v4 | F | 5 | 147 | 0.082 | 0.082 | 6.8e-04 | -0.003 | 0.004 | + |
| jsd | deepseek_v4 | C | 5 | 147 | 0.078 | 0.082 | -0.004 | -0.011 | 0.003 | - |
| jsd | gpt4o | F | 5 | 140 | 0.093 | 0.094 | -7.2e-04 | -0.005 | 0.003 | - |
| jsd | gpt4o | C | 5 | 140 | 0.089 | 0.094 | -0.005 | -0.012 | 0.002 | - |

## (4) Homogenization index per version: distance between students of different teachers, seed-matched (homogenization.csv; a fix that homogenises shows a drop vs O; 1 - corr is scale-free and is the index to read first)

| version | n_cells | n_seeds | n_families | one_minus_corr | omc_ci_lo | omc_ci_hi | jsd | jsd_ci_lo | jsd_ci_hi | n_paired_cells | d_omc_vs_O | d_omc_ci_lo | d_omc_ci_hi | d_jsd_vs_O | d_jsd_ci_lo | d_jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 15 | 5 | 148 | 0.451 | 0.387 | 0.529 | 0.049 | 0.036 | 0.064 | 0 | nan | nan | nan | nan | nan | nan |
| F | 15 | 5 | 148 | 0.497 | 0.429 | 0.584 | 0.052 | 0.039 | 0.066 | 15 | 0.047 | 0.017 | 0.081 | 0.003 | 1.4e-04 | 0.006 |
| C | 15 | 5 | 148 | 0.528 | 0.450 | 0.620 | 0.052 | 0.039 | 0.066 | 15 | 0.077 | 0.027 | 0.127 | 0.003 | -0.002 | 0.009 |

Calibration guard (judgment JSD and majority disagreement shrink / grow mechanically when readouts move towards 0.5): mean |p - 0.5|, share of cells with |p - 0.5| < 0.1, cross-teacher majority disagreement (all cells / confident cells).

| version | mean_abs_margin | share_low_margin | maj_disagree | maj_disagree_conf |
|---|---|---|---|---|
| O | 0.439 | 0.042 | 0.101 | 0.074 |
| F | 0.438 | 0.044 | 0.107 | 0.080 |
| C | 0.432 | 0.050 | 0.111 | 0.079 |

## (5) Inheritance by form: delta_rho partial given r_0 of V minus O, paired by seed (inheritance_by_form.csv)

| teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction | control |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F | 5 | 138 | -0.045 | -0.046 | 0.001 | -0.096 | 0.072 | + | qwen3-4b.base_B_s0 |
| claude46 | C | 5 | 138 | -0.085 | -0.046 | -0.039 | -0.173 | 0.063 | - | qwen3-4b.base_B_s0 |
| deepseek_v4 | F | 5 | 137 | 0.027 | 0.058 | -0.031 | -0.077 | 0.010 | - | qwen3-4b.base_B_s0 |
| deepseek_v4 | C | 5 | 137 | 0.069 | 0.058 | 0.011 | -0.037 | 0.065 | + | qwen3-4b.base_B_s0 |
| gpt4o | F | 5 | 139 | 0.011 | 0.015 | -0.004 | -0.046 | 0.034 | - | qwen3-4b.base_B_s0 |
| gpt4o | C | 5 | 139 | 0.047 | 0.015 | 0.031 | -0.025 | 0.083 | + | qwen3-4b.base_B_s0 |

Per-run delta_rho seed means by version (inheritance_by_form_runs.csv):

| teacher | version | mean | std | count |
|---|---|---|---|---|
| claude46 | C | -0.085 | 0.071 | 5 |
| claude46 | F | -0.045 | 0.055 | 5 |
| claude46 | O | -0.046 | 0.053 | 5 |
| deepseek_v4 | C | 0.069 | 0.042 | 5 |
| deepseek_v4 | F | 0.027 | 0.058 | 5 |
| deepseek_v4 | O | 0.058 | 0.022 | 5 |
| gpt4o | C | 0.047 | 0.046 | 5 |
| gpt4o | F | 0.011 | 0.037 | 5 |
| gpt4o | O | 0.015 | 0.033 | 5 |

### Joint partial D per version (joint_D_by_version.csv; e2 secondary statistic computed on each version's seed-pooled students)

| version | n_teachers | n_families | D | ci_lo | ci_hi | p_perm | D_specific | ci_specific_lo | ci_specific_hi | D_shared | D_raw | e2_secondary_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 3 | 137 | 0.100 | 0.032 | 0.168 | 1.0e-04 | 0.156 | 0.062 | 0.269 | -0.056 | 0.093 | pass |
| F | 3 | 139 | 0.086 | 0.010 | 0.171 | 7.0e-04 | 0.132 | 0.039 | 0.242 | -0.046 | 0.082 | pass |
| C | 3 | 137 | 0.088 | 0.013 | 0.162 | 0.002 | 0.134 | 0.040 | 0.235 | -0.045 | 0.084 | pass |

### Suggestibility s = delta(T5) - delta(T6) per (teacher, version) group with family-bootstrap CI (suggestibility_by_version.csv) and version differences (suggestibility_version_diffs.csv)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46:O | 5 | 137 | 0.031 | 0.019 | 0.045 |
| students:claude46:F | 5 | 137 | 0.029 | 0.016 | 0.044 |
| students:claude46:C | 5 | 137 | 0.027 | 0.015 | 0.042 |
| students:deepseek_v4:O | 5 | 137 | 0.177 | 0.132 | 0.222 |
| students:deepseek_v4:F | 5 | 137 | 0.174 | 0.130 | 0.219 |
| students:deepseek_v4:C | 5 | 137 | 0.172 | 0.132 | 0.212 |
| students:gpt4o:O | 5 | 137 | 0.121 | 0.089 | 0.156 |
| students:gpt4o:F | 5 | 137 | 0.115 | 0.086 | 0.147 |
| students:gpt4o:C | 5 | 137 | 0.110 | 0.082 | 0.139 |
| teacher:claude46 | 1 | 137 | 0.049 | 0.014 | 0.086 |
| teacher:deepseek_v4 | 1 | 137 | 0.145 | 0.116 | 0.174 |
| teacher:gpt4o | 1 | 137 | 0.075 | 0.047 | 0.105 |

| teacher | version | contrast | diff | ci_lo | ci_hi |
|---|---|---|---|---|---|
| claude46 | F | students:V - students:O | -0.002 | -0.006 | 0.002 |
| claude46 | C | students:V - students:O | -0.004 | -0.011 | 0.004 |
| claude46 | O | students:V - teacher | -0.018 | -0.052 | 0.017 |
| claude46 | F | students:V - teacher | -0.020 | -0.054 | 0.013 |
| claude46 | C | students:V - teacher | -0.021 | -0.058 | 0.015 |
| deepseek_v4 | F | students:V - students:O | -0.003 | -0.011 | 0.006 |
| deepseek_v4 | C | students:V - students:O | -0.005 | -0.022 | 0.011 |
| deepseek_v4 | O | students:V - teacher | 0.032 | -0.009 | 0.076 |
| deepseek_v4 | F | students:V - teacher | 0.029 | -0.012 | 0.073 |
| deepseek_v4 | C | students:V - teacher | 0.027 | -0.012 | 0.067 |
| gpt4o | F | students:V - students:O | -0.006 | -0.014 | 8.6e-04 |
| gpt4o | C | students:V - students:O | -0.012 | -0.021 | -0.002 |
| gpt4o | O | students:V - teacher | 0.047 | 0.014 | 0.080 |
| gpt4o | F | students:V - teacher | 0.041 | 0.010 | 0.071 |
| gpt4o | C | students:V - teacher | 0.035 | 0.005 | 0.066 |

## (6) Stage-2 content check of the ACTUAL training files (content_check.csv; docs/03 §5: a change here = content drift, not form)

| teacher | version | n_items | n_families | same_prompt_set_as_O | letter_identity_with_O | letter_matches_rewrite | kept_attempt_found | check_choice | check_reasons | check_conditions | check_strength | check_style | check_format | mean_attempts | kept_share | mean_words | mean_chars | mean_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O | 5132 | 1463 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 37.936 | 245.656 | 48.326 |
| gpt4o | F | 5132 | 1463 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.631 | 0.954 | 38.331 | 252.259 | 48.681 |
| gpt4o | C | 5132 | 1463 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.296 | 0.935 | 38.932 | 229.276 | 49.987 |
| claude46 | O | 4682 | 1469 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 62.258 | 412.116 | 77.481 |
| claude46 | F | 4682 | 1469 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 2.055 | 0.932 | 62.510 | 423.308 | 77.880 |
| claude46 | C | 4682 | 1469 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.546 | 0.856 | 64.066 | 377.250 | 79.326 |
| deepseek_v4 | O | 4668 | 1411 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 33.168 | 216.075 | 43.634 |
| deepseek_v4 | F | 4668 | 1411 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.569 | 0.972 | 33.910 | 226.935 | 44.425 |
| deepseek_v4 | C | 4668 | 1411 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.291 | 0.960 | 35.558 | 209.403 | 46.604 |

Letter identity with O: 100% for every F / C file.

**letter_matches_rewrite < 1 for 1 file(s)** (SFT letter differs from the kept rewrite text's leading 'Answer: X' (format leak in the rewrite, letter itself still equals O)): claude46 C 0.99979 (~1 item(s))

### Lexical register per version (register_check.csv; rates per word; fk_grade = Flesch-Kincaid proxy) and F vs C separability (register_separation.csv; frozen bar >= 0.90, e3_plan §2; Wilson 95% CIs)

| teacher | version | n | n_words | n_sentences | contraction_rate | formal_connective_rate | formal_word_rate | mean_word_len | words_per_sentence | fk_grade |
|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O | 5132 | 38.222 | 1.835 | 0.005 | 0.002 | 0.050 | 5.393 | 21.799 | 13.989 |
| gpt4o | F | 5132 | 38.610 | 1.835 | 2.1e-04 | 0.004 | 0.055 | 5.498 | 22.010 | 14.656 |
| gpt4o | C | 5132 | 39.178 | 1.913 | 0.034 | 2.6e-04 | 0.012 | 4.811 | 21.139 | 10.374 |
| claude46 | O | 4682 | 62.694 | 2.905 | 0.003 | 0.002 | 0.028 | 5.492 | 21.759 | 14.438 |
| claude46 | F | 4682 | 63.046 | 2.900 | 3.8e-04 | 0.004 | 0.034 | 5.636 | 21.924 | 15.238 |
| claude46 | C | 4682 | 64.457 | 2.905 | 0.022 | 1.7e-04 | 0.006 | 4.779 | 22.365 | 10.775 |
| deepseek_v4 | O | 4668 | 33.969 | 1.516 | 9.4e-05 | 6.1e-04 | 0.031 | 5.333 | 23.931 | 14.548 |
| deepseek_v4 | F | 4668 | 34.340 | 1.515 | 1.3e-04 | 0.004 | 0.040 | 5.577 | 24.207 | 15.754 |
| deepseek_v4 | C | 4668 | 35.935 | 1.697 | 0.032 | 1.1e-04 | 0.007 | 4.784 | 22.514 | 10.773 |

| teacher | a | b | n_a | n_b | nearest_centroid_loo_acc | nc_ci_lo | nc_ci_hi | logistic_cv_acc | lr_ci_lo | lr_ci_hi | min_acc | status | top_feature |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | F | C | 5132 | 5132 | 0.921 | 0.916 | 0.926 | 0.959 | 0.955 | 0.963 | 0.900 | pass | contraction_rate d=-2.10 |
| gpt4o | O | F | 5132 | 5132 | 0.591 | 0.581 | 0.600 | 0.595 | 0.585 | 0.604 | 0.900 | descriptive | contraction_rate d=0.55 |
| gpt4o | O | C | 5132 | 5132 | 0.879 | 0.872 | 0.885 | 0.903 | 0.897 | 0.908 | 0.900 | descriptive | contraction_rate d=-1.62 |
| claude46 | F | C | 4682 | 4682 | 0.927 | 0.921 | 0.932 | 0.952 | 0.948 | 0.957 | 0.900 | pass | mean_word_len d=2.08 |
| claude46 | O | F | 4682 | 4682 | 0.605 | 0.595 | 0.615 | 0.605 | 0.595 | 0.615 | 0.900 | descriptive | contraction_rate d=0.48 |
| claude46 | O | C | 4682 | 4682 | 0.886 | 0.879 | 0.892 | 0.900 | 0.894 | 0.906 | 0.900 | descriptive | mean_word_len d=1.77 |
| deepseek_v4 | F | C | 4668 | 4668 | 0.907 | 0.901 | 0.913 | 0.942 | 0.937 | 0.946 | 0.900 | pass | contraction_rate d=-1.75 |
| deepseek_v4 | O | F | 4668 | 4668 | 0.607 | 0.597 | 0.617 | 0.612 | 0.602 | 0.622 | 0.900 | descriptive | mean_word_len d=-0.46 |
| deepseek_v4 | O | C | 4668 | 4668 | 0.864 | 0.857 | 0.871 | 0.918 | 0.912 | 0.923 | 0.900 | descriptive | contraction_rate d=-1.75 |

The >= 0.90 bar applies to F vs C (pass / fail); O vs F and O vs C are descriptive (O is already a formal register, so O vs F near chance is expected and O vs C mirrors F vs C).

Notes: students are compared within teacher and paired by seed; the paired O students (runs/qwen3-4b-paired) are trained on the prompt intersection of O / F / C, not on the full O set of E1. 
Consistency is never read alone: every consistency row sits next to the agreement / JSD rows of the same runs. R students and the base are not E3 cells.