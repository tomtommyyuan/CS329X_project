# E3 summary (test, student qwen3-4b-e2c-paired, variants T1, T3, T5, T6; E3 rule pre-specified 2026-10-05 (docs/03 E3 row, tasks/e3_plan.md §3) before any F / C run existed; frozen at commit 45f3d30 (tasks/hpc_log.md); auto-generated)

Rule (docs/03 E3 row, verbatim): 效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；R 有而 F / C 无则归因于隐性内容变化. Operationalised (tasks/e3_plan.md §3): per metric, the per-teacher statistic is the seed mean of the paired difference S_{T,V,s} - S_{T,O,s} (disagreement: the mean V-W disagreement minus the teacher's own O-O seed-pair mean); the seed-pair null is the same single-pair quantity between two O seeds of the same teacher, pooled over teachers, and scaled to the statistic: SD_stat = sqrt(mean(d^2) / n_seeds [+ jackknife var of the O-O mean]), q95 = t(0.975, df = sum(n_O - 1) = 12) x SD_stat (disagreement: t(0.95)); a teacher exceeds when |stat| > q95; effect iff >= 2/3 of the 3 teachers exceed with the same sign. p from the t reference with Holm over the teachers; `no effect` only when >= 2/3 teachers pass the TOST (family-bootstrap 95% CI inside +/- 1 SD_stat; docs/04 §3), otherwise `inconclusive`. The raw single-pair q95 (`null_q95_single`, `n_pass_single`) is a sensitivity column. Primary rows: disagreement F vs C, consistency change, excess drift, inheritance by form; the other rows are secondary. Under H0 the q95 rule has a per-row false-positive rate of about 0.004, <= 0.05 family-wise over the 13 rows (Bonferroni); `p_row_holm_primary` is descriptive. CIs are family-bootstrap 2.5 / 97.5 percentiles with families resampled jointly for every seed of a teacher. Assumptions: seed noise approximately normal and independent across seeds (same-seed F / O pairs share init and data order, so the null is conservative).

## Run inventory (runs with a readout on this split)

| teacher | n_O | n_F | n_C | seeds_O | seeds_F | seeds_C | paired_F | paired_C |
|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| deepseek_v4 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| gpt4o | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |

Base prior covariate r_0: qwen3-4b.base_B_s0 (300 complete families without the mass gate).

## Verdicts (rule 7; confirmatory)

| metric | tier | teachers: stat [CI] (effect in null sd, p, Holm, TOST) * = exceeds q95 | null q95 of the stat (single-pair q95; n) | pass | TOST pass | direction | verdict |
|---|---|---|---|---|---|---|---|
| disagreement F vs C | primary | claude46 0.007 [-0.008, 0.024] (1.444 null sd, p 0.087, Holm 0.087, TOST False); deepseek_v4 0.019 [0.008, 0.030] (3.956 null sd, p 9.5e-04, Holm 0.003, TOST False)*; gpt4o 0.009 [-0.002, 0.019] (2.047 null sd, p 0.032, Holm 0.063, TOST False)* | 0.008 (0.011; 30) | 2/3 | 0/3 | + | **effect** |
| disagreement O vs F | secondary | claude46 -0.005 [-0.017, 0.008] (-1.050 null sd, p 0.843, Holm 1.000, TOST False); deepseek_v4 -0.002 [-0.010, 0.007] (-0.416 null sd, p 0.658, Holm 1.000, TOST False); gpt4o -0.005 [-0.014, 0.005] (-1.120 null sd, p 0.858, Holm 1.000, TOST False) | 0.008 (0.011; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| disagreement O vs C | secondary | claude46 0.007 [-0.008, 0.023] (1.411 null sd, p 0.092, Holm 0.092, TOST False); deepseek_v4 0.019 [0.008, 0.030] (3.852 null sd, p 0.001, Holm 0.003, TOST False)*; gpt4o 0.009 [-0.002, 0.021] (2.162 null sd, p 0.026, Holm 0.051, TOST False)* | 0.008 (0.011; 30) | 2/3 | 0/3 | + | **effect** |
| consistency change: flip rate F - O | primary | claude46 -0.003 [-0.013, 0.008] (-0.342 null sd, p 0.738, Holm 0.738, TOST False); deepseek_v4 -0.009 [-0.020, 6.7e-04] (-1.230 null sd, p 0.242, Holm 0.485, TOST False); gpt4o 0.026 [0.015, 0.037] (3.441 null sd, p 0.005, Holm 0.015, TOST False)* | 0.016 (0.033; 30) | 1/3 | 0/3 | + | **inconclusive** |
| consistency change: cross-framing JSD F - O | primary | claude46 -0.004 [-0.007, 2.0e-04] (-0.815 null sd, p 0.431, Holm 0.862, TOST False); deepseek_v4 1.7e-04 [-0.005, 0.005] (0.039 null sd, p 0.970, Holm 0.970, TOST False); gpt4o 0.013 [0.008, 0.018] (2.987 null sd, p 0.011, Holm 0.034, TOST False)* | 0.009 (0.015; 30) | 1/3 | 0/3 | + | **inconclusive** |
| teacher agreement change F - O | secondary | claude46 -0.006 [-0.019, 0.007] (-1.197 null sd, p 0.254, Holm 0.763, TOST False); deepseek_v4 0.002 [-0.005, 0.010] (0.452 null sd, p 0.660, Holm 0.936, TOST False); gpt4o 0.004 [-0.005, 0.013] (0.749 null sd, p 0.468, Holm 0.936, TOST False) | 0.010 (0.022; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| excess teacher drift (JSD to own teacher) F - O | primary | claude46 0.005 [-9.9e-04, 0.011] (1.991 null sd, p 0.070, Holm 0.209, TOST False); deepseek_v4 9.4e-04 [-0.003, 0.005] (0.385 null sd, p 0.707, Holm 1.000, TOST False); gpt4o 0.001 [-0.005, 0.007] (0.410 null sd, p 0.689, Holm 1.000, TOST False) | 0.005 (0.009; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho F - O | primary | claude46 -0.029 [-0.073, 0.034] (-2.333 null sd, p 0.038, Holm 0.114, TOST False)*; deepseek_v4 0.009 [-0.020, 0.037] (0.734 null sd, p 0.477, Holm 0.477, TOST False); gpt4o 0.018 [-0.015, 0.050] (1.466 null sd, p 0.168, Holm 0.337, TOST False) | 0.027 (0.054; 30) | 1/3 | 0/3 | - | **inconclusive** |
| consistency change: flip rate C - O | primary | claude46 -0.013 [-0.026, 6.7e-04] (-1.665 null sd, p 0.122, Holm 0.234, TOST False); deepseek_v4 -0.013 [-0.026, 0.001] (-1.689 null sd, p 0.117, Holm 0.234, TOST False); gpt4o 0.025 [0.012, 0.039] (3.367 null sd, p 0.006, Holm 0.017, TOST False)* | 0.016 (0.033; 30) | 1/3 | 0/3 | + | **inconclusive** |
| consistency change: cross-framing JSD C - O | primary | claude46 -0.009 [-0.014, -0.004] (-2.115 null sd, p 0.056, Holm 0.112, TOST False); deepseek_v4 -0.005 [-0.013, 0.002] (-1.227 null sd, p 0.243, Holm 0.243, TOST False); gpt4o 0.011 [0.004, 0.018] (2.486 null sd, p 0.029, Holm 0.086, TOST False)* | 0.009 (0.015; 30) | 1/3 | 0/3 | + | **inconclusive** |
| teacher agreement change C - O | secondary | claude46 -0.007 [-0.023, 0.009] (-1.455 null sd, p 0.171, Holm 0.514, TOST False); deepseek_v4 0.000 [-0.011, 0.011] (0.000 null sd, p 1.000, Holm 1.000, TOST False); gpt4o -0.005 [-0.016, 0.005] (-1.071 null sd, p 0.305, Holm 0.611, TOST False) | 0.010 (0.022; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| excess teacher drift (JSD to own teacher) C - O | primary | claude46 0.003 [-0.007, 0.013] (1.378 null sd, p 0.193, Holm 0.415, TOST False); deepseek_v4 0.002 [-0.004, 0.009] (0.923 null sd, p 0.374, Holm 0.415, TOST False); gpt4o 0.004 [-0.004, 0.011] (1.588 null sd, p 0.138, Holm 0.415, TOST False) | 0.005 (0.009; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho C - O | primary | claude46 -0.034 [-0.077, 0.025] (-2.735 null sd, p 0.018, Holm 0.054, TOST False)*; deepseek_v4 -0.017 [-0.060, 0.025] (-1.389 null sd, p 0.190, Holm 0.380, TOST False); gpt4o -0.008 [-0.055, 0.038] (-0.633 null sd, p 0.539, Holm 0.539, TOST False) | 0.027 (0.054; 30) | 1/3 | 0/3 | - | **inconclusive** |

Descriptive (no verdict): homogenization index, joint partial D per version, suggestibility per version, content and register checks of the training files.

## Seed-pair null: the same quantity between two O seeds of one teacher, pooled over teachers (seed_pair_null.csv)

| metric | n | mean | sd | q95 |
|---|---|---|---|---|
| flip | 30 | 0.013 | 0.011 | 0.033 |
| jsd | 30 | 0.008 | 0.006 | 0.015 |
| agree_own | 30 | 0.008 | 0.007 | 0.022 |
| jsd_own | 30 | 0.005 | 0.003 | 0.009 |
| disagree_O-O | 30 | 0.058 | 0.008 | 0.071 |
| jsd_between_O-O | 30 | 0.021 | 0.003 | 0.026 |
| delta_rho | 30 | 0.022 | 0.018 | 0.054 |

## (1) Cross-student disagreement: share of (family, variant) cells with different majority acts, same teacher and seed (disagreement.csv; disagree_conf = cells where both |p - 0.5| >= 0.1, robustness)

| teacher | pair | n_seeds | n_families | disagree | ci_lo | ci_hi | disagree_conf | jsd | jsd_ci_lo | jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 298 | 0.071 | 0.056 | 0.088 | 0.041 | 0.031 | 0.025 | 0.037 |
| claude46 | O-F | 5 | 298 | 0.059 | 0.046 | 0.071 | 0.025 | 0.020 | 0.017 | 0.024 |
| claude46 | O-C | 5 | 298 | 0.071 | 0.056 | 0.087 | 0.039 | 0.029 | 0.024 | 0.036 |
| deepseek_v4 | F-C | 5 | 299 | 0.073 | 0.062 | 0.084 | 0.035 | 0.031 | 0.027 | 0.035 |
| deepseek_v4 | O-F | 5 | 299 | 0.052 | 0.044 | 0.061 | 0.021 | 0.019 | 0.017 | 0.022 |
| deepseek_v4 | O-C | 5 | 299 | 0.073 | 0.062 | 0.084 | 0.035 | 0.029 | 0.025 | 0.033 |
| gpt4o | F-C | 5 | 300 | 0.066 | 0.055 | 0.076 | 0.035 | 0.027 | 0.023 | 0.031 |
| gpt4o | O-F | 5 | 300 | 0.052 | 0.043 | 0.061 | 0.023 | 0.019 | 0.016 | 0.022 |
| gpt4o | O-C | 5 | 300 | 0.066 | 0.055 | 0.078 | 0.030 | 0.026 | 0.022 | 0.030 |

Excess over the teacher's own O-O seed-pair mean (disagreement_excess.csv; the verdict statistic; var_oo_mean = delete-one-seed jackknife variance of the O-O mean):

| teacher | pair | n_seeds | disagree | oo_mean | n_oo_pairs | var_oo_mean | excess | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 0.071 | 0.064 | 10 | 1.8e-05 | 0.007 | -0.008 | 0.024 |
| claude46 | O-F | 5 | 0.059 | 0.064 | 10 | 1.8e-05 | -0.005 | -0.017 | 0.008 |
| claude46 | O-C | 5 | 0.071 | 0.064 | 10 | 1.8e-05 | 0.007 | -0.008 | 0.023 |
| deepseek_v4 | F-C | 5 | 0.073 | 0.054 | 10 | 1.5e-05 | 0.019 | 0.008 | 0.030 |
| deepseek_v4 | O-F | 5 | 0.052 | 0.054 | 10 | 1.5e-05 | -0.002 | -0.010 | 0.007 |
| deepseek_v4 | O-C | 5 | 0.073 | 0.054 | 10 | 1.5e-05 | 0.019 | 0.008 | 0.030 |
| gpt4o | F-C | 5 | 0.066 | 0.057 | 10 | 1.0e-05 | 0.009 | -0.002 | 0.019 |
| gpt4o | O-F | 5 | 0.052 | 0.057 | 10 | 1.0e-05 | -0.005 | -0.014 | 0.005 |
| gpt4o | O-C | 5 | 0.066 | 0.057 | 10 | 1.0e-05 | 0.009 | -0.002 | 0.021 |

## (2) Consistency change V - O, paired by seed (consistency_delta.csv; flip = flip rate, jsd = cross-framing JSD)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| flip | claude46 | F | 5 | 298 | 0.091 | 0.093 | -0.003 | -0.013 | 0.008 | - |
| flip | claude46 | C | 5 | 298 | 0.081 | 0.093 | -0.013 | -0.026 | 6.7e-04 | - |
| flip | deepseek_v4 | F | 5 | 299 | 0.264 | 0.274 | -0.009 | -0.020 | 6.7e-04 | - |
| flip | deepseek_v4 | C | 5 | 299 | 0.261 | 0.274 | -0.013 | -0.026 | 0.001 | - |
| flip | gpt4o | F | 5 | 300 | 0.173 | 0.147 | 0.026 | 0.015 | 0.037 | + |
| flip | gpt4o | C | 5 | 300 | 0.172 | 0.147 | 0.025 | 0.012 | 0.039 | + |
| jsd | claude46 | F | 5 | 298 | 0.043 | 0.046 | -0.004 | -0.007 | 2.0e-04 | - |
| jsd | claude46 | C | 5 | 298 | 0.037 | 0.046 | -0.009 | -0.014 | -0.004 | - |
| jsd | deepseek_v4 | F | 5 | 299 | 0.192 | 0.192 | 1.7e-04 | -0.005 | 0.005 | + |
| jsd | deepseek_v4 | C | 5 | 299 | 0.186 | 0.192 | -0.005 | -0.013 | 0.002 | - |
| jsd | gpt4o | F | 5 | 300 | 0.108 | 0.095 | 0.013 | 0.008 | 0.018 | + |
| jsd | gpt4o | C | 5 | 300 | 0.106 | 0.095 | 0.011 | 0.004 | 0.018 | + |

## (3) Teacher agreement change and excess teacher drift V - O, paired by seed (drift.csv; agree = majority-act agreement with the own teacher, jsd = JSD to the own teacher)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| agree | claude46 | F | 5 | 295 | 0.839 | 0.845 | -0.006 | -0.019 | 0.007 | - |
| agree | claude46 | C | 5 | 295 | 0.838 | 0.845 | -0.007 | -0.023 | 0.009 | - |
| agree | deepseek_v4 | F | 5 | 299 | 0.783 | 0.780 | 0.002 | -0.005 | 0.010 | + |
| agree | deepseek_v4 | C | 5 | 299 | 0.780 | 0.780 | 0.000 | -0.011 | 0.011 | 0 |
| agree | gpt4o | F | 5 | 291 | 0.814 | 0.811 | 0.004 | -0.005 | 0.013 | + |
| agree | gpt4o | C | 5 | 291 | 0.806 | 0.811 | -0.005 | -0.016 | 0.005 | - |
| jsd | claude46 | F | 5 | 295 | 0.129 | 0.124 | 0.005 | -9.9e-04 | 0.011 | + |
| jsd | claude46 | C | 5 | 295 | 0.127 | 0.124 | 0.003 | -0.007 | 0.013 | + |
| jsd | deepseek_v4 | F | 5 | 299 | 0.144 | 0.143 | 9.4e-04 | -0.003 | 0.005 | + |
| jsd | deepseek_v4 | C | 5 | 299 | 0.145 | 0.143 | 0.002 | -0.004 | 0.009 | + |
| jsd | gpt4o | F | 5 | 291 | 0.143 | 0.142 | 0.001 | -0.005 | 0.007 | + |
| jsd | gpt4o | C | 5 | 291 | 0.146 | 0.142 | 0.004 | -0.004 | 0.011 | + |

## (4) Homogenization index per version: distance between students of different teachers, seed-matched (homogenization.csv; a fix that homogenises shows a drop vs O; 1 - corr is scale-free and is the index to read first)

| version | n_cells | n_seeds | n_families | one_minus_corr | omc_ci_lo | omc_ci_hi | jsd | jsd_ci_lo | jsd_ci_hi | n_paired_cells | d_omc_vs_O | d_omc_ci_lo | d_omc_ci_hi | d_jsd_vs_O | d_jsd_ci_lo | d_jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 15 | 5 | 297 | 0.593 | 0.552 | 0.634 | 0.131 | 0.117 | 0.145 | 0 | nan | nan | nan | nan | nan | nan |
| F | 15 | 5 | 297 | 0.596 | 0.555 | 0.635 | 0.133 | 0.119 | 0.148 | 15 | 0.003 | -0.016 | 0.023 | 0.002 | -0.002 | 0.006 |
| C | 15 | 5 | 297 | 0.614 | 0.576 | 0.653 | 0.133 | 0.119 | 0.147 | 15 | 0.022 | -0.004 | 0.046 | 0.002 | -0.004 | 0.008 |

Calibration guard (judgment JSD and majority disagreement shrink / grow mechanically when readouts move towards 0.5): mean |p - 0.5|, share of cells with |p - 0.5| < 0.1, cross-teacher majority disagreement (all cells / confident cells).

| version | mean_abs_margin | share_low_margin | maj_disagree | maj_disagree_conf |
|---|---|---|---|---|
| O | 0.431 | 0.067 | 0.200 | 0.162 |
| F | 0.432 | 0.066 | 0.199 | 0.165 |
| C | 0.430 | 0.066 | 0.200 | 0.164 |

## (5) Inheritance by form: delta_rho partial given r_0 of V minus O, paired by seed (inheritance_by_form.csv)

| teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction | control |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F | 5 | 288 | -0.085 | -0.056 | -0.029 | -0.073 | 0.034 | - | qwen3-4b.base_B_s0 |
| claude46 | C | 5 | 288 | -0.090 | -0.056 | -0.034 | -0.077 | 0.025 | - | qwen3-4b.base_B_s0 |
| deepseek_v4 | F | 5 | 290 | 0.227 | 0.218 | 0.009 | -0.020 | 0.037 | + | qwen3-4b.base_B_s0 |
| deepseek_v4 | C | 5 | 290 | 0.200 | 0.218 | -0.017 | -0.060 | 0.025 | - | qwen3-4b.base_B_s0 |
| gpt4o | F | 5 | 290 | -0.091 | -0.109 | 0.018 | -0.015 | 0.050 | + | qwen3-4b.base_B_s0 |
| gpt4o | C | 5 | 290 | -0.117 | -0.109 | -0.008 | -0.055 | 0.038 | - | qwen3-4b.base_B_s0 |

Per-run delta_rho seed means by version (inheritance_by_form_runs.csv):

| teacher | version | mean | std | count |
|---|---|---|---|---|
| claude46 | C | -0.090 | 0.017 | 5 |
| claude46 | F | -0.085 | 0.032 | 5 |
| claude46 | O | -0.056 | 0.023 | 5 |
| deepseek_v4 | C | 0.200 | 0.023 | 5 |
| deepseek_v4 | F | 0.227 | 0.006 | 5 |
| deepseek_v4 | O | 0.218 | 0.011 | 5 |
| gpt4o | C | -0.117 | 0.016 | 5 |
| gpt4o | F | -0.091 | 0.025 | 5 |
| gpt4o | O | -0.109 | 0.022 | 5 |

### Joint partial D per version (joint_D_by_version.csv; e2 secondary statistic computed on each version's seed-pooled students)

| version | n_teachers | n_families | D | ci_lo | ci_hi | p_perm | D_specific | ci_specific_lo | ci_specific_hi | D_shared | D_raw | e2_secondary_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 3 | 290 | 0.048 | 0.004 | 0.092 | 0.022 | 0.070 | 0.022 | 0.120 | -0.021 | 0.052 | pass |
| F | 3 | 289 | 0.055 | 0.011 | 0.098 | 0.010 | 0.079 | 0.031 | 0.128 | -0.024 | 0.057 | pass |
| C | 3 | 289 | 0.037 | -0.004 | 0.076 | 0.086 | 0.068 | 0.019 | 0.118 | -0.032 | 0.043 | fail |

### Suggestibility s = delta(T5) - delta(T6) per (teacher, version) group with family-bootstrap CI (suggestibility_by_version.csv) and version differences (suggestibility_version_diffs.csv)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46:O | 5 | 288 | 0.092 | 0.071 | 0.114 |
| students:claude46:F | 5 | 288 | 0.090 | 0.069 | 0.112 |
| students:claude46:C | 5 | 288 | 0.072 | 0.054 | 0.091 |
| students:deepseek_v4:O | 5 | 288 | 0.480 | 0.434 | 0.526 |
| students:deepseek_v4:F | 5 | 288 | 0.475 | 0.430 | 0.521 |
| students:deepseek_v4:C | 5 | 288 | 0.468 | 0.422 | 0.513 |
| students:gpt4o:O | 5 | 288 | 0.283 | 0.246 | 0.322 |
| students:gpt4o:F | 5 | 288 | 0.313 | 0.274 | 0.353 |
| students:gpt4o:C | 5 | 288 | 0.315 | 0.276 | 0.354 |
| teacher:claude46 | 1 | 288 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 288 | 0.114 | 0.097 | 0.132 |
| teacher:gpt4o | 1 | 288 | 0.063 | 0.045 | 0.084 |

| teacher | version | contrast | diff | ci_lo | ci_hi |
|---|---|---|---|---|---|
| claude46 | F | students:V - students:O | -0.002 | -0.011 | 0.007 |
| claude46 | C | students:V - students:O | -0.020 | -0.032 | -0.008 |
| claude46 | O | students:V - teacher | 0.047 | 0.018 | 0.075 |
| claude46 | F | students:V - teacher | 0.045 | 0.015 | 0.074 |
| claude46 | C | students:V - teacher | 0.027 | -8.5e-04 | 0.055 |
| deepseek_v4 | F | students:V - students:O | -0.005 | -0.017 | 0.007 |
| deepseek_v4 | C | students:V - students:O | -0.012 | -0.029 | 0.005 |
| deepseek_v4 | O | students:V - teacher | 0.366 | 0.322 | 0.410 |
| deepseek_v4 | F | students:V - teacher | 0.361 | 0.318 | 0.405 |
| deepseek_v4 | C | students:V - teacher | 0.354 | 0.310 | 0.397 |
| gpt4o | F | students:V - students:O | 0.030 | 0.018 | 0.043 |
| gpt4o | C | students:V - students:O | 0.031 | 0.015 | 0.048 |
| gpt4o | O | students:V - teacher | 0.220 | 0.183 | 0.259 |
| gpt4o | F | students:V - teacher | 0.250 | 0.211 | 0.290 |
| gpt4o | C | students:V - teacher | 0.251 | 0.213 | 0.290 |

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