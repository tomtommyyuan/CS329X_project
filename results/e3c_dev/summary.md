# E3 summary (dev, student qwen3-4b-e2c-paired, variants T1, T3, T5, T6; E3 rule pre-specified 2026-10-05 (docs/03 E3 row, tasks/e3_plan.md §3) before any F / C run existed; not yet frozen (freeze line pending in tasks/hpc_log.md); auto-generated)

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
| disagreement F vs C | primary | claude46 0.009 [-0.009, 0.028] (1.836 null sd, p 0.046, Holm 0.091, TOST False)*; deepseek_v4 0.018 [0.002, 0.035] (3.358 null sd, p 0.003, Holm 0.009, TOST False)*; gpt4o 0.001 [-0.013, 0.017] (0.156 null sd, p 0.439, Holm 0.439, TOST False) | 0.010 (0.010; 30) | 2/3 | 0/3 | + | **effect** |
| disagreement O vs F | secondary | claude46 -0.003 [-0.018, 0.014] (-0.635 null sd, p 0.731, Holm 1.000, TOST False); deepseek_v4 -0.005 [-0.017, 0.009] (-0.887 null sd, p 0.804, Holm 1.000, TOST False); gpt4o -0.008 [-0.020, 0.004] (-1.301 null sd, p 0.891, Holm 1.000, TOST False) | 0.010 (0.010; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| disagreement O vs C | secondary | claude46 0.004 [-0.011, 0.020] (0.777 null sd, p 0.226, Holm 0.226, TOST False); deepseek_v4 0.008 [-0.008, 0.025] (1.520 null sd, p 0.077, Holm 0.167, TOST False); gpt4o 0.011 [-0.005, 0.029] (1.717 null sd, p 0.056, Holm 0.167, TOST False) | 0.010 (0.010; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: flip rate F - O | primary | claude46 0.006 [-0.006, 0.017] (0.751 null sd, p 0.467, Holm 0.558, TOST False); deepseek_v4 0.013 [-0.004, 0.031] (1.796 null sd, p 0.098, Holm 0.293, TOST False); gpt4o 0.008 [-0.005, 0.022] (1.134 null sd, p 0.279, Holm 0.558, TOST False) | 0.016 (0.027; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: cross-framing JSD F - O | primary | claude46 3.7e-04 [-0.005, 0.006] (0.086 null sd, p 0.933, Holm 0.933, TOST False); deepseek_v4 0.003 [-0.006, 0.012] (0.781 null sd, p 0.450, Holm 0.900, TOST False); gpt4o 0.011 [0.005, 0.018] (2.609 null sd, p 0.023, Holm 0.069, TOST False)* | 0.009 (0.017; 30) | 1/3 | 0/3 | + | **inconclusive** |
| teacher agreement change F - O | secondary | claude46 -5.7e-04 [-0.011, 0.010] (-0.116 null sd, p 0.909, Holm 1.000, TOST False); deepseek_v4 -0.001 [-0.014, 0.011] (-0.281 null sd, p 0.783, Holm 1.000, TOST False); gpt4o -0.007 [-0.018, 0.004] (-1.455 null sd, p 0.171, Holm 0.514, TOST False) | 0.011 (0.018; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| excess teacher drift (JSD to own teacher) F - O | primary | claude46 -5.4e-05 [-0.009, 0.009] (-0.016 null sd, p 0.988, Holm 0.988, TOST False); deepseek_v4 0.005 [-0.001, 0.011] (1.313 null sd, p 0.214, Holm 0.427, TOST False); gpt4o 0.007 [-8.1e-04, 0.014] (1.976 null sd, p 0.072, Holm 0.215, TOST False) | 0.008 (0.015; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho F - O | primary | claude46 0.011 [-0.037, 0.059] (0.418 null sd, p 0.684, Holm 1.000, TOST False); deepseek_v4 0.005 [-0.040, 0.055] (0.199 null sd, p 0.845, Holm 1.000, TOST False); gpt4o -0.044 [-0.089, -0.002] (-1.670 null sd, p 0.121, Holm 0.363, TOST False) | 0.058 (0.109; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: flip rate C - O | primary | claude46 -0.018 [-0.036, 2.2e-04] (-2.432 null sd, p 0.032, Holm 0.095, TOST False)*; deepseek_v4 0.013 [-0.005, 0.032] (1.796 null sd, p 0.098, Holm 0.195, TOST False); gpt4o 0.010 [-0.008, 0.027] (1.312 null sd, p 0.214, Holm 0.214, TOST False) | 0.016 (0.027; 30) | 1/3 | 0/3 | - | **inconclusive** |
| consistency change: cross-framing JSD C - O | primary | claude46 -0.014 [-0.022, -0.007] (-3.269 null sd, p 0.007, Holm 0.020, TOST False)*; deepseek_v4 0.004 [-0.007, 0.015] (0.944 null sd, p 0.364, Holm 0.364, TOST False); gpt4o 0.009 [7.9e-04, 0.017] (2.076 null sd, p 0.060, Holm 0.120, TOST False) | 0.009 (0.017; 30) | 1/3 | 0/3 | - | **inconclusive** |
| teacher agreement change C - O | secondary | claude46 -0.003 [-0.016, 0.011] (-0.581 null sd, p 0.572, Holm 0.572, TOST False); deepseek_v4 -0.009 [-0.023, 0.005] (-1.756 null sd, p 0.104, Holm 0.209, TOST False); gpt4o -0.013 [-0.030, 0.004] (-2.619 null sd, p 0.022, Holm 0.067, TOST False)* | 0.011 (0.018; 30) | 1/3 | 0/3 | - | **inconclusive** |
| excess teacher drift (JSD to own teacher) C - O | primary | claude46 1.1e-04 [-0.008, 0.009] (0.031 null sd, p 0.976, Holm 1.000, TOST False); deepseek_v4 0.002 [-0.005, 0.008] (0.458 null sd, p 0.655, Holm 1.000, TOST False); gpt4o 0.005 [-0.006, 0.017] (1.521 null sd, p 0.154, Holm 0.462, TOST False) | 0.008 (0.015; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho C - O | primary | claude46 0.080 [-0.007, 0.148] (3.038 null sd, p 0.010, Holm 0.031, TOST False)*; deepseek_v4 0.023 [-0.028, 0.070] (0.883 null sd, p 0.395, Holm 0.789, TOST False); gpt4o -0.017 [-0.067, 0.030] (-0.643 null sd, p 0.533, Holm 0.789, TOST False) | 0.058 (0.109; 30) | 1/3 | 0/3 | + | **inconclusive** |

Descriptive (no verdict): homogenization index, joint partial D per version, suggestibility per version, content and register checks of the training files.

## Seed-pair null: the same quantity between two O seeds of one teacher, pooled over teachers (seed_pair_null.csv)

| metric | n | mean | sd | q95 |
|---|---|---|---|---|
| flip | 30 | 0.014 | 0.009 | 0.027 |
| jsd | 30 | 0.007 | 0.007 | 0.017 |
| agree_own | 30 | 0.009 | 0.006 | 0.018 |
| jsd_own | 30 | 0.006 | 0.005 | 0.015 |
| disagree_O-O | 30 | 0.057 | 0.012 | 0.076 |
| jsd_between_O-O | 30 | 0.021 | 0.004 | 0.027 |
| delta_rho | 30 | 0.051 | 0.031 | 0.109 |

## (1) Cross-student disagreement: share of (family, variant) cells with different majority acts, same teacher and seed (disagreement.csv; disagree_conf = cells where both |p - 0.5| >= 0.1, robustness)

| teacher | pair | n_seeds | n_families | disagree | ci_lo | ci_hi | disagree_conf | jsd | jsd_ci_lo | jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 148 | 0.058 | 0.040 | 0.077 | 0.041 | 0.028 | 0.020 | 0.036 |
| claude46 | O-F | 5 | 148 | 0.046 | 0.031 | 0.063 | 0.026 | 0.020 | 0.015 | 0.025 |
| claude46 | O-C | 5 | 148 | 0.053 | 0.038 | 0.069 | 0.033 | 0.023 | 0.018 | 0.029 |
| deepseek_v4 | F-C | 5 | 146 | 0.088 | 0.072 | 0.105 | 0.043 | 0.034 | 0.028 | 0.041 |
| deepseek_v4 | O-F | 5 | 146 | 0.065 | 0.052 | 0.078 | 0.027 | 0.024 | 0.020 | 0.028 |
| deepseek_v4 | O-C | 5 | 146 | 0.078 | 0.062 | 0.095 | 0.038 | 0.032 | 0.026 | 0.039 |
| gpt4o | F-C | 5 | 149 | 0.053 | 0.039 | 0.069 | 0.024 | 0.021 | 0.016 | 0.026 |
| gpt4o | O-F | 5 | 149 | 0.044 | 0.032 | 0.056 | 0.016 | 0.014 | 0.011 | 0.017 |
| gpt4o | O-C | 5 | 149 | 0.063 | 0.047 | 0.081 | 0.032 | 0.024 | 0.019 | 0.029 |

Excess over the teacher's own O-O seed-pair mean (disagreement_excess.csv; the verdict statistic; var_oo_mean = delete-one-seed jackknife variance of the O-O mean):

| teacher | pair | n_seeds | disagree | oo_mean | n_oo_pairs | var_oo_mean | excess | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 0.058 | 0.049 | 10 | 1.1e-05 | 0.009 | -0.009 | 0.028 |
| claude46 | O-F | 5 | 0.046 | 0.049 | 10 | 1.1e-05 | -0.003 | -0.018 | 0.014 |
| claude46 | O-C | 5 | 0.053 | 0.049 | 10 | 1.1e-05 | 0.004 | -0.011 | 0.020 |
| deepseek_v4 | F-C | 5 | 0.088 | 0.070 | 10 | 1.8e-05 | 0.018 | 0.002 | 0.035 |
| deepseek_v4 | O-F | 5 | 0.065 | 0.070 | 10 | 1.8e-05 | -0.005 | -0.017 | 0.009 |
| deepseek_v4 | O-C | 5 | 0.078 | 0.070 | 10 | 1.8e-05 | 0.008 | -0.008 | 0.025 |
| gpt4o | F-C | 5 | 0.053 | 0.052 | 10 | 3.0e-05 | 0.001 | -0.013 | 0.017 |
| gpt4o | O-F | 5 | 0.044 | 0.052 | 10 | 3.0e-05 | -0.008 | -0.020 | 0.004 |
| gpt4o | O-C | 5 | 0.063 | 0.052 | 10 | 3.0e-05 | 0.011 | -0.005 | 0.029 |

## (2) Consistency change V - O, paired by seed (consistency_delta.csv; flip = flip rate, jsd = cross-framing JSD)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| flip | claude46 | F | 5 | 149 | 0.091 | 0.086 | 0.006 | -0.006 | 0.017 | + |
| flip | claude46 | C | 5 | 149 | 0.068 | 0.086 | -0.018 | -0.036 | 2.2e-04 | - |
| flip | deepseek_v4 | F | 5 | 147 | 0.252 | 0.239 | 0.013 | -0.004 | 0.031 | + |
| flip | deepseek_v4 | C | 5 | 147 | 0.252 | 0.239 | 0.013 | -0.005 | 0.032 | + |
| flip | gpt4o | F | 5 | 150 | 0.176 | 0.168 | 0.008 | -0.005 | 0.022 | + |
| flip | gpt4o | C | 5 | 150 | 0.178 | 0.168 | 0.010 | -0.008 | 0.027 | + |
| jsd | claude46 | F | 5 | 149 | 0.049 | 0.048 | 3.7e-04 | -0.005 | 0.006 | + |
| jsd | claude46 | C | 5 | 149 | 0.034 | 0.048 | -0.014 | -0.022 | -0.007 | - |
| jsd | deepseek_v4 | F | 5 | 147 | 0.178 | 0.174 | 0.003 | -0.006 | 0.012 | + |
| jsd | deepseek_v4 | C | 5 | 147 | 0.178 | 0.174 | 0.004 | -0.007 | 0.015 | + |
| jsd | gpt4o | F | 5 | 150 | 0.119 | 0.108 | 0.011 | 0.005 | 0.018 | + |
| jsd | gpt4o | C | 5 | 150 | 0.117 | 0.108 | 0.009 | 7.9e-04 | 0.017 | + |

## (3) Teacher agreement change and excess teacher drift V - O, paired by seed (drift.csv; agree = majority-act agreement with the own teacher, jsd = JSD to the own teacher)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| agree | claude46 | F | 5 | 146 | 0.825 | 0.826 | -5.7e-04 | -0.011 | 0.010 | - |
| agree | claude46 | C | 5 | 146 | 0.823 | 0.826 | -0.003 | -0.016 | 0.011 | - |
| agree | deepseek_v4 | F | 5 | 145 | 0.777 | 0.778 | -0.001 | -0.014 | 0.011 | - |
| agree | deepseek_v4 | C | 5 | 145 | 0.770 | 0.778 | -0.009 | -0.023 | 0.005 | - |
| agree | gpt4o | F | 5 | 140 | 0.835 | 0.842 | -0.007 | -0.018 | 0.004 | - |
| agree | gpt4o | C | 5 | 140 | 0.829 | 0.842 | -0.013 | -0.030 | 0.004 | - |
| jsd | claude46 | F | 5 | 147 | 0.139 | 0.139 | -5.4e-05 | -0.009 | 0.009 | - |
| jsd | claude46 | C | 5 | 147 | 0.139 | 0.139 | 1.1e-04 | -0.008 | 0.009 | + |
| jsd | deepseek_v4 | F | 5 | 146 | 0.138 | 0.134 | 0.005 | -0.001 | 0.011 | + |
| jsd | deepseek_v4 | C | 5 | 146 | 0.135 | 0.134 | 0.002 | -0.005 | 0.008 | + |
| jsd | gpt4o | F | 5 | 140 | 0.118 | 0.111 | 0.007 | -8.1e-04 | 0.014 | + |
| jsd | gpt4o | C | 5 | 140 | 0.116 | 0.111 | 0.005 | -0.006 | 0.017 | + |

## (4) Homogenization index per version: distance between students of different teachers, seed-matched (homogenization.csv; a fix that homogenises shows a drop vs O; 1 - corr is scale-free and is the index to read first)

| version | n_cells | n_seeds | n_families | one_minus_corr | omc_ci_lo | omc_ci_hi | jsd | jsd_ci_lo | jsd_ci_hi | n_paired_cells | d_omc_vs_O | d_omc_ci_lo | d_omc_ci_hi | d_jsd_vs_O | d_jsd_ci_lo | d_jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 15 | 5 | 146 | 0.537 | 0.480 | 0.599 | 0.132 | 0.110 | 0.155 | 0 | nan | nan | nan | nan | nan | nan |
| F | 15 | 5 | 146 | 0.549 | 0.497 | 0.605 | 0.138 | 0.116 | 0.162 | 15 | 0.012 | -0.013 | 0.038 | 0.006 | 3.6e-04 | 0.013 |
| C | 15 | 5 | 146 | 0.591 | 0.541 | 0.643 | 0.137 | 0.115 | 0.161 | 15 | 0.054 | 0.013 | 0.095 | 0.005 | -0.002 | 0.013 |

Calibration guard (judgment JSD and majority disagreement shrink / grow mechanically when readouts move towards 0.5): mean |p - 0.5|, share of cells with |p - 0.5| < 0.1, cross-teacher majority disagreement (all cells / confident cells).

| version | mean_abs_margin | share_low_margin | maj_disagree | maj_disagree_conf |
|---|---|---|---|---|
| O | 0.437 | 0.059 | 0.196 | 0.162 |
| F | 0.440 | 0.056 | 0.192 | 0.166 |
| C | 0.440 | 0.059 | 0.196 | 0.169 |

## (5) Inheritance by form: delta_rho partial given r_0 of V minus O, paired by seed (inheritance_by_form.csv)

| teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction | control |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F | 5 | 138 | -0.126 | -0.137 | 0.011 | -0.037 | 0.059 | + | qwen3-4b.base_B_s0 |
| claude46 | C | 5 | 138 | -0.057 | -0.137 | 0.080 | -0.007 | 0.148 | + | qwen3-4b.base_B_s0 |
| deepseek_v4 | F | 5 | 136 | 0.043 | 0.038 | 0.005 | -0.040 | 0.055 | + | qwen3-4b.base_B_s0 |
| deepseek_v4 | C | 5 | 136 | 0.061 | 0.038 | 0.023 | -0.028 | 0.070 | + | qwen3-4b.base_B_s0 |
| gpt4o | F | 5 | 139 | 0.009 | 0.053 | -0.044 | -0.089 | -0.002 | - | qwen3-4b.base_B_s0 |
| gpt4o | C | 5 | 139 | 0.036 | 0.053 | -0.017 | -0.067 | 0.030 | - | qwen3-4b.base_B_s0 |

Per-run delta_rho seed means by version (inheritance_by_form_runs.csv):

| teacher | version | mean | std | count |
|---|---|---|---|---|
| claude46 | C | -0.057 | 0.018 | 5 |
| claude46 | F | -0.126 | 0.057 | 5 |
| claude46 | O | -0.137 | 0.041 | 5 |
| deepseek_v4 | C | 0.061 | 0.035 | 5 |
| deepseek_v4 | F | 0.043 | 0.017 | 5 |
| deepseek_v4 | O | 0.038 | 0.052 | 5 |
| gpt4o | C | 0.036 | 0.042 | 5 |
| gpt4o | F | 0.009 | 0.040 | 5 |
| gpt4o | O | 0.053 | 0.029 | 5 |

### Joint partial D per version (joint_D_by_version.csv; e2 secondary statistic computed on each version's seed-pooled students)

| version | n_teachers | n_families | D | ci_lo | ci_hi | p_perm | D_specific | ci_specific_lo | ci_specific_hi | D_shared | D_raw | e2_secondary_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 3 | 139 | 0.059 | -0.014 | 0.126 | 0.034 | 0.091 | 0.006 | 0.175 | -0.032 | 0.058 | fail |
| F | 3 | 137 | 0.055 | -0.016 | 0.123 | 0.047 | 0.085 | 0.003 | 0.168 | -0.030 | 0.054 | fail |
| C | 3 | 137 | 0.078 | 0.002 | 0.150 | 0.008 | 0.133 | 0.032 | 0.233 | -0.055 | 0.077 | pass |

### Suggestibility s = delta(T5) - delta(T6) per (teacher, version) group with family-bootstrap CI (suggestibility_by_version.csv) and version differences (suggestibility_version_diffs.csv)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46:O | 5 | 135 | 0.124 | 0.091 | 0.161 |
| students:claude46:F | 5 | 135 | 0.123 | 0.087 | 0.163 |
| students:claude46:C | 5 | 135 | 0.079 | 0.054 | 0.107 |
| students:deepseek_v4:O | 5 | 135 | 0.449 | 0.387 | 0.511 |
| students:deepseek_v4:F | 5 | 135 | 0.442 | 0.380 | 0.504 |
| students:deepseek_v4:C | 5 | 135 | 0.455 | 0.390 | 0.519 |
| students:gpt4o:O | 5 | 135 | 0.304 | 0.245 | 0.365 |
| students:gpt4o:F | 5 | 135 | 0.329 | 0.267 | 0.392 |
| students:gpt4o:C | 5 | 135 | 0.321 | 0.261 | 0.383 |
| teacher:claude46 | 1 | 135 | 0.051 | 0.015 | 0.087 |
| teacher:deepseek_v4 | 1 | 135 | 0.144 | 0.114 | 0.176 |
| teacher:gpt4o | 1 | 135 | 0.069 | 0.042 | 0.100 |

| teacher | version | contrast | diff | ci_lo | ci_hi |
|---|---|---|---|---|---|
| claude46 | F | students:V - students:O | -8.5e-04 | -0.016 | 0.014 |
| claude46 | C | students:V - students:O | -0.045 | -0.065 | -0.027 |
| claude46 | O | students:V - teacher | 0.073 | 0.025 | 0.123 |
| claude46 | F | students:V - teacher | 0.073 | 0.023 | 0.123 |
| claude46 | C | students:V - teacher | 0.029 | -0.014 | 0.071 |
| deepseek_v4 | F | students:V - students:O | -0.007 | -0.029 | 0.015 |
| deepseek_v4 | C | students:V - students:O | 0.006 | -0.021 | 0.032 |
| deepseek_v4 | O | students:V - teacher | 0.305 | 0.245 | 0.365 |
| deepseek_v4 | F | students:V - teacher | 0.298 | 0.236 | 0.359 |
| deepseek_v4 | C | students:V - teacher | 0.311 | 0.248 | 0.374 |
| gpt4o | F | students:V - students:O | 0.025 | 0.011 | 0.040 |
| gpt4o | C | students:V - students:O | 0.017 | -0.003 | 0.036 |
| gpt4o | O | students:V - teacher | 0.235 | 0.182 | 0.289 |
| gpt4o | F | students:V - teacher | 0.260 | 0.203 | 0.318 |
| gpt4o | C | students:V - teacher | 0.252 | 0.197 | 0.308 |

## (6) Stage-2 content check of the ACTUAL training files (content_check.csv; docs/03 §5: a change here = content drift, not form)

| teacher | version | n_items | n_families | same_prompt_set_as_O | letter_identity_with_O | letter_matches_rewrite | kept_attempt_found | check_choice | check_reasons | check_conditions | check_strength | check_style | check_format | mean_attempts | kept_share | mean_words | mean_chars | mean_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O | 4527 | 1431 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 37.898 | 229.586 | 47.755 |
| gpt4o | F | 4527 | 1431 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.134 | 0.952 | 38.679 | 245.805 | 48.676 |
| gpt4o | C | 4527 | 1431 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.246 | 0.940 | 38.292 | 213.370 | 48.868 |
| claude46 | O | 4122 | 1425 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 56.811 | 351.252 | 70.248 |
| claude46 | F | 4122 | 1425 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.187 | 0.935 | 57.817 | 376.037 | 71.397 |
| claude46 | C | 4122 | 1425 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.334 | 0.883 | 57.174 | 324.001 | 71.230 |
| deepseek_v4 | O | 2228 | 1061 | True | 1.000 | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 32.438 | 198.697 | 42.511 |
| deepseek_v4 | F | 2228 | 1061 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.130 | 0.933 | 33.809 | 218.142 | 43.866 |
| deepseek_v4 | C | 2228 | 1061 | True | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.000 | 1.228 | 0.923 | 34.043 | 191.849 | 44.660 |

Letter identity with O: 100% for every F / C file.

**letter_matches_rewrite < 1 for 1 file(s)** (SFT letter differs from the kept rewrite text's leading 'Answer: X' (format leak in the rewrite, letter itself still equals O)): claude46 C 0.99976 (~1 item(s))

### Lexical register per version (register_check.csv; rates per word; fk_grade = Flesch-Kincaid proxy) and F vs C separability (register_separation.csv; frozen bar >= 0.90, e3_plan §2; Wilson 95% CIs)

| teacher | version | n | n_words | n_sentences | contraction_rate | formal_connective_rate | formal_word_rate | mean_word_len | words_per_sentence | fk_grade |
|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O | 4527 | 38.064 | 1.717 | 0.006 | 0.002 | 0.025 | 4.968 | 23.537 | 12.791 |
| gpt4o | F | 4527 | 38.845 | 1.717 | 6.9e-05 | 0.005 | 0.033 | 5.270 | 23.994 | 14.468 |
| gpt4o | C | 4527 | 38.444 | 1.791 | 0.031 | 3.2e-05 | 0.004 | 4.494 | 22.478 | 9.655 |
| claude46 | O | 4122 | 57.007 | 2.662 | 0.008 | 0.002 | 0.015 | 5.044 | 21.678 | 12.320 |
| claude46 | F | 4122 | 58.112 | 2.657 | 1.2e-04 | 0.004 | 0.024 | 5.367 | 22.136 | 14.156 |
| claude46 | C | 4122 | 57.396 | 2.661 | 0.031 | 9.3e-05 | 0.003 | 4.563 | 21.776 | 9.617 |
| deepseek_v4 | O | 2228 | 33.298 | 1.384 | 2.9e-04 | 5.0e-04 | 0.014 | 4.899 | 25.341 | 13.272 |
| deepseek_v4 | F | 2228 | 34.112 | 1.384 | 1.8e-05 | 0.005 | 0.025 | 5.331 | 25.943 | 15.533 |
| deepseek_v4 | C | 2228 | 34.383 | 1.540 | 0.034 | 1.2e-05 | 0.003 | 4.520 | 23.591 | 10.189 |

| teacher | a | b | n_a | n_b | nearest_centroid_loo_acc | nc_ci_lo | nc_ci_hi | logistic_cv_acc | lr_ci_lo | lr_ci_hi | min_acc | status | top_feature |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | F | C | 4527 | 4527 | 0.900 | 0.894 | 0.906 | 0.949 | 0.945 | 0.954 | 0.900 | pass | contraction_rate d=-1.76 |
| gpt4o | O | F | 4527 | 4527 | 0.663 | 0.653 | 0.673 | 0.678 | 0.668 | 0.688 | 0.900 | descriptive | contraction_rate d=0.59 |
| gpt4o | O | C | 4527 | 4527 | 0.817 | 0.809 | 0.825 | 0.854 | 0.847 | 0.861 | 0.900 | descriptive | contraction_rate d=-1.28 |
| claude46 | F | C | 4122 | 4122 | 0.901 | 0.894 | 0.907 | 0.954 | 0.950 | 0.959 | 0.900 | pass | mean_word_len d=1.84 |
| claude46 | O | F | 4122 | 4122 | 0.680 | 0.669 | 0.690 | 0.703 | 0.693 | 0.713 | 0.900 | descriptive | contraction_rate d=0.76 |
| claude46 | O | C | 4122 | 4122 | 0.799 | 0.791 | 0.808 | 0.836 | 0.828 | 0.844 | 0.900 | descriptive | contraction_rate d=-1.18 |
| deepseek_v4 | F | C | 2228 | 2228 | 0.885 | 0.875 | 0.894 | 0.936 | 0.928 | 0.943 | 0.900 | fail | fk_grade d=1.66 |
| deepseek_v4 | O | F | 2228 | 2228 | 0.674 | 0.660 | 0.688 | 0.684 | 0.670 | 0.697 | 0.900 | descriptive | mean_word_len d=-0.74 |
| deepseek_v4 | O | C | 2228 | 2228 | 0.811 | 0.799 | 0.822 | 0.868 | 0.858 | 0.878 | 0.900 | descriptive | contraction_rate d=-1.61 |

The >= 0.90 bar applies to F vs C (pass / fail); O vs F and O vs C are descriptive (O is already a formal register, so O vs F near chance is expected and O vs C mirrors F vs C).

Notes: students are compared within teacher and paired by seed; the paired O students (runs/qwen3-4b-paired) are trained on the prompt intersection of O / F / C, not on the full O set of E1. 
Consistency is never read alone: every consistency row sits next to the agreement / JSD rows of the same runs. R students and the base are not E3 cells.