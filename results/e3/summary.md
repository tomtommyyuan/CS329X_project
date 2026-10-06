# E3 summary (test, student qwen3-4b-paired, variants T1, T3, T5, T6; E3 rule pre-specified 2026-10-05 (docs/03 E3 row, tasks/e3_plan.md §3) before any F / C run existed; frozen at commit 5e98fe3 (tasks/hpc_log.md); auto-generated)

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
| disagreement F vs C | primary | claude46 0.005 [-0.008, 0.019] (1.407 null sd, p 0.092, Holm 0.185, TOST False); deepseek_v4 0.008 [-0.004, 0.021] (2.945 null sd, p 0.006, Holm 0.018, TOST False)*; gpt4o 0.004 [-0.009, 0.017] (0.779 null sd, p 0.226, Holm 0.226, TOST False) | 0.006 (0.009; 30) | 1/3 | 0/3 | + | **inconclusive** |
| disagreement O vs F | secondary | claude46 -0.010 [-0.019, -8.4e-04] (-2.960 null sd, p 0.994, Holm 1.000, TOST False); deepseek_v4 -0.008 [-0.017, 0.002] (-2.764 null sd, p 0.991, Holm 1.000, TOST False); gpt4o -0.017 [-0.027, -0.007] (-3.646 null sd, p 0.998, Holm 1.000, TOST False) | 0.006 (0.009; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| disagreement O vs C | secondary | claude46 0.007 [-0.006, 0.022] (2.135 null sd, p 0.027, Holm 0.081, TOST False)*; deepseek_v4 0.005 [-0.007, 0.017] (1.743 null sd, p 0.053, Holm 0.107, TOST False); gpt4o 0.006 [-0.007, 0.021] (1.381 null sd, p 0.096, Holm 0.107, TOST False) | 0.006 (0.009; 30) | 1/3 | 0/3 | + | **inconclusive** |
| consistency change: flip rate F - O | primary | claude46 -1.1e-04 [-0.007, 0.007] (-0.035 null sd, p 0.973, Holm 1.000, TOST False); deepseek_v4 -0.002 [-0.012, 0.007] (-0.763 null sd, p 0.460, Holm 1.000, TOST False); gpt4o 0.002 [-0.006, 0.010] (0.589 null sd, p 0.567, Holm 1.000, TOST False) | 0.007 (0.012; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: cross-framing JSD F - O | primary | claude46 -3.3e-04 [-0.001, 3.7e-04] (-0.139 null sd, p 0.892, Holm 1.000, TOST True); deepseek_v4 0.001 [-0.001, 0.004] (0.430 null sd, p 0.675, Holm 1.000, TOST False); gpt4o -3.5e-04 [-0.002, 7.8e-04] (-0.146 null sd, p 0.886, Holm 1.000, TOST True) | 0.005 (0.011; 30) | 0/3 | 2/3 | nan | **no effect** |
| teacher agreement change F - O | secondary | claude46 0.004 [-0.003, 0.010] (1.007 null sd, p 0.334, Holm 1.000, TOST False); deepseek_v4 3.3e-04 [-0.007, 0.008] (0.090 null sd, p 0.930, Holm 1.000, TOST False); gpt4o -0.003 [-0.010, 0.003] (-0.885 null sd, p 0.394, Holm 1.000, TOST False) | 0.008 (0.015; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| excess teacher drift (JSD to own teacher) F - O | primary | claude46 -0.002 [-0.005, 0.002] (-0.688 null sd, p 0.505, Holm 1.000, TOST False); deepseek_v4 -0.002 [-0.005, 0.002] (-0.739 null sd, p 0.474, Holm 1.000, TOST False); gpt4o 0.002 [-9.5e-04, 0.005] (0.799 null sd, p 0.440, Holm 1.000, TOST False) | 0.005 (0.010; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho F - O | primary | claude46 0.003 [-0.023, 0.044] (0.260 null sd, p 0.799, Holm 0.799, TOST False); deepseek_v4 0.035 [3.0e-04, 0.065] (3.424 null sd, p 0.005, Holm 0.015, TOST False)*; gpt4o -0.034 [-0.080, 0.006] (-3.340 null sd, p 0.006, Holm 0.015, TOST False)* | 0.022 (0.036; 30) | 2/3 | 0/3 | mixed | **inconclusive** |
| consistency change: flip rate C - O | primary | claude46 -7.4e-20 [-0.010, 0.009] (-2.3e-17 null sd, p 1.000, Holm 1.000, TOST False); deepseek_v4 0.005 [-0.005, 0.015] (1.421 null sd, p 0.181, Holm 0.542, TOST False); gpt4o -0.003 [-0.014, 0.009] (-0.867 null sd, p 0.403, Holm 0.806, TOST False) | 0.007 (0.012; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| consistency change: cross-framing JSD C - O | primary | claude46 -3.2e-04 [-0.001, 7.5e-04] (-0.133 null sd, p 0.896, Holm 0.896, TOST True); deepseek_v4 -0.002 [-0.005, 0.001] (-0.839 null sd, p 0.418, Holm 0.836, TOST False); gpt4o -0.003 [-0.005, -7.0e-04] (-1.249 null sd, p 0.236, Holm 0.707, TOST False) | 0.005 (0.011; 30) | 0/3 | 1/3 | nan | **inconclusive** |
| teacher agreement change C - O | secondary | claude46 -0.004 [-0.017, 0.008] (-1.190 null sd, p 0.257, Holm 0.514, TOST False); deepseek_v4 -0.002 [-0.012, 0.009] (-0.497 null sd, p 0.628, Holm 0.628, TOST False); gpt4o 0.008 [-0.003, 0.019] (2.188 null sd, p 0.049, Holm 0.147, TOST False)* | 0.008 (0.015; 30) | 1/3 | 0/3 | + | **inconclusive** |
| excess teacher drift (JSD to own teacher) C - O | primary | claude46 0.001 [-0.005, 0.008] (0.597 null sd, p 0.562, Holm 0.692, TOST False); deepseek_v4 -0.002 [-0.007, 0.002] (-0.981 null sd, p 0.346, Holm 0.692, TOST False); gpt4o -0.004 [-0.010, 0.002] (-1.450 null sd, p 0.173, Holm 0.518, TOST False) | 0.005 (0.010; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| inheritance by form: partial delta_rho C - O | primary | claude46 -0.021 [-0.081, 0.056] (-2.033 null sd, p 0.065, Holm 0.130, TOST False); deepseek_v4 0.054 [-0.004, 0.100] (5.346 null sd, p 1.7e-04, Holm 5.2e-04, TOST False)*; gpt4o 0.010 [-0.032, 0.054] (1.039 null sd, p 0.319, Holm 0.319, TOST False) | 0.022 (0.036; 30) | 1/3 | 0/3 | + | **inconclusive** |

Descriptive (no verdict): homogenization index, joint partial D per version, suggestibility per version, content and register checks of the training files.

## Seed-pair null: the same quantity between two O seeds of one teacher, pooled over teachers (seed_pair_null.csv)

| metric | n | mean | sd | q95 |
|---|---|---|---|---|
| flip | 30 | 0.006 | 0.004 | 0.012 |
| jsd | 30 | 0.004 | 0.004 | 0.011 |
| agree_own | 30 | 0.007 | 0.004 | 0.015 |
| jsd_own | 30 | 0.005 | 0.003 | 0.010 |
| disagree_O-O | 30 | 0.045 | 0.008 | 0.056 |
| jsd_between_O-O | 30 | 0.012 | 0.003 | 0.016 |
| delta_rho | 30 | 0.020 | 0.011 | 0.036 |

## (1) Cross-student disagreement: share of (family, variant) cells with different majority acts, same teacher and seed (disagreement.csv; disagree_conf = cells where both |p - 0.5| >= 0.1, robustness)

| teacher | pair | n_seeds | n_families | disagree | ci_lo | ci_hi | disagree_conf | jsd | jsd_ci_lo | jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 299 | 0.041 | 0.029 | 0.055 | 0.028 | 0.011 | 0.008 | 0.013 |
| claude46 | O-F | 5 | 299 | 0.026 | 0.018 | 0.035 | 0.006 | 0.005 | 0.003 | 0.006 |
| claude46 | O-C | 5 | 299 | 0.043 | 0.030 | 0.058 | 0.025 | 0.011 | 0.008 | 0.013 |
| deepseek_v4 | F-C | 5 | 300 | 0.056 | 0.044 | 0.069 | 0.028 | 0.016 | 0.013 | 0.019 |
| deepseek_v4 | O-F | 5 | 300 | 0.040 | 0.031 | 0.049 | 0.013 | 0.009 | 0.007 | 0.011 |
| deepseek_v4 | O-C | 5 | 300 | 0.052 | 0.041 | 0.065 | 0.029 | 0.016 | 0.013 | 0.019 |
| gpt4o | F-C | 5 | 300 | 0.055 | 0.042 | 0.068 | 0.029 | 0.013 | 0.010 | 0.016 |
| gpt4o | O-F | 5 | 300 | 0.034 | 0.024 | 0.044 | 0.011 | 0.006 | 0.005 | 0.008 |
| gpt4o | O-C | 5 | 300 | 0.058 | 0.044 | 0.072 | 0.030 | 0.014 | 0.011 | 0.017 |

Excess over the teacher's own O-O seed-pair mean (disagreement_excess.csv; the verdict statistic; var_oo_mean = delete-one-seed jackknife variance of the O-O mean):

| teacher | pair | n_seeds | disagree | oo_mean | n_oo_pairs | var_oo_mean | excess | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | F-C | 5 | 0.041 | 0.036 | 10 | 7.0e-06 | 0.005 | -0.008 | 0.019 |
| claude46 | O-F | 5 | 0.026 | 0.036 | 10 | 7.0e-06 | -0.010 | -0.019 | -8.4e-04 |
| claude46 | O-C | 5 | 0.043 | 0.036 | 10 | 7.0e-06 | 0.007 | -0.006 | 0.022 |
| deepseek_v4 | F-C | 5 | 0.056 | 0.048 | 10 | 2.8e-06 | 0.008 | -0.004 | 0.021 |
| deepseek_v4 | O-F | 5 | 0.040 | 0.048 | 10 | 2.8e-06 | -0.008 | -0.017 | 0.002 |
| deepseek_v4 | O-C | 5 | 0.052 | 0.048 | 10 | 2.8e-06 | 0.005 | -0.007 | 0.017 |
| gpt4o | F-C | 5 | 0.055 | 0.051 | 10 | 1.7e-05 | 0.004 | -0.009 | 0.017 |
| gpt4o | O-F | 5 | 0.034 | 0.051 | 10 | 1.7e-05 | -0.017 | -0.027 | -0.007 |
| gpt4o | O-C | 5 | 0.058 | 0.051 | 10 | 1.7e-05 | 0.006 | -0.007 | 0.021 |

## (2) Consistency change V - O, paired by seed (consistency_delta.csv; flip = flip rate, jsd = cross-framing JSD)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| flip | claude46 | F | 5 | 299 | 0.028 | 0.028 | -1.1e-04 | -0.007 | 0.007 | - |
| flip | claude46 | C | 5 | 299 | 0.028 | 0.028 | -7.4e-20 | -0.010 | 0.009 | - |
| flip | deepseek_v4 | F | 5 | 300 | 0.082 | 0.084 | -0.002 | -0.012 | 0.007 | - |
| flip | deepseek_v4 | C | 5 | 300 | 0.089 | 0.084 | 0.005 | -0.005 | 0.015 | + |
| flip | gpt4o | F | 5 | 300 | 0.068 | 0.066 | 0.002 | -0.006 | 0.010 | + |
| flip | gpt4o | C | 5 | 300 | 0.063 | 0.066 | -0.003 | -0.014 | 0.009 | - |
| jsd | claude46 | F | 5 | 299 | 0.006 | 0.006 | -3.3e-04 | -0.001 | 3.7e-04 | - |
| jsd | claude46 | C | 5 | 299 | 0.006 | 0.006 | -3.2e-04 | -0.001 | 7.5e-04 | - |
| jsd | deepseek_v4 | F | 5 | 300 | 0.040 | 0.039 | 0.001 | -0.001 | 0.004 | + |
| jsd | deepseek_v4 | C | 5 | 300 | 0.037 | 0.039 | -0.002 | -0.005 | 0.001 | - |
| jsd | gpt4o | F | 5 | 300 | 0.023 | 0.023 | -3.5e-04 | -0.002 | 7.8e-04 | - |
| jsd | gpt4o | C | 5 | 300 | 0.020 | 0.023 | -0.003 | -0.005 | -7.0e-04 | - |

## (3) Teacher agreement change and excess teacher drift V - O, paired by seed (drift.csv; agree = majority-act agreement with the own teacher, jsd = JSD to the own teacher)

| metric | teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| agree | claude46 | F | 5 | 296 | 0.873 | 0.869 | 0.004 | -0.003 | 0.010 | + |
| agree | claude46 | C | 5 | 296 | 0.865 | 0.869 | -0.004 | -0.017 | 0.008 | - |
| agree | deepseek_v4 | F | 5 | 300 | 0.854 | 0.854 | 3.3e-04 | -0.007 | 0.008 | + |
| agree | deepseek_v4 | C | 5 | 300 | 0.852 | 0.854 | -0.002 | -0.012 | 0.009 | - |
| agree | gpt4o | F | 5 | 291 | 0.858 | 0.861 | -0.003 | -0.010 | 0.003 | - |
| agree | gpt4o | C | 5 | 291 | 0.869 | 0.861 | 0.008 | -0.003 | 0.019 | + |
| jsd | claude46 | F | 5 | 297 | 0.100 | 0.101 | -0.002 | -0.005 | 0.002 | - |
| jsd | claude46 | C | 5 | 297 | 0.103 | 0.101 | 0.001 | -0.005 | 0.008 | + |
| jsd | deepseek_v4 | F | 5 | 300 | 0.080 | 0.081 | -0.002 | -0.005 | 0.002 | - |
| jsd | deepseek_v4 | C | 5 | 300 | 0.079 | 0.081 | -0.002 | -0.007 | 0.002 | - |
| jsd | gpt4o | F | 5 | 291 | 0.094 | 0.092 | 0.002 | -9.5e-04 | 0.005 | + |
| jsd | gpt4o | C | 5 | 291 | 0.088 | 0.092 | -0.004 | -0.010 | 0.002 | - |

## (4) Homogenization index per version: distance between students of different teachers, seed-matched (homogenization.csv; a fix that homogenises shows a drop vs O; 1 - corr is scale-free and is the index to read first)

| version | n_cells | n_seeds | n_families | one_minus_corr | omc_ci_lo | omc_ci_hi | jsd | jsd_ci_lo | jsd_ci_hi | n_paired_cells | d_omc_vs_O | d_omc_ci_lo | d_omc_ci_hi | d_jsd_vs_O | d_jsd_ci_lo | d_jsd_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 15 | 5 | 299 | 0.524 | 0.471 | 0.581 | 0.040 | 0.033 | 0.048 | 0 | nan | nan | nan | nan | nan | nan |
| F | 15 | 5 | 299 | 0.541 | 0.487 | 0.595 | 0.042 | 0.035 | 0.050 | 15 | 0.016 | -0.006 | 0.039 | 0.002 | -3.9e-05 | 0.005 |
| C | 15 | 5 | 299 | 0.537 | 0.482 | 0.595 | 0.040 | 0.034 | 0.047 | 15 | 0.013 | -0.025 | 0.052 | 3.3e-04 | -0.004 | 0.004 |

Calibration guard (judgment JSD and majority disagreement shrink / grow mechanically when readouts move towards 0.5): mean |p - 0.5|, share of cells with |p - 0.5| < 0.1, cross-teacher majority disagreement (all cells / confident cells).

| version | mean_abs_margin | share_low_margin | maj_disagree | maj_disagree_conf |
|---|---|---|---|---|
| O | 0.439 | 0.043 | 0.089 | 0.058 |
| F | 0.438 | 0.043 | 0.092 | 0.061 |
| C | 0.431 | 0.049 | 0.097 | 0.061 |

## (5) Inheritance by form: delta_rho partial given r_0 of V minus O, paired by seed (inheritance_by_form.csv)

| teacher | version | n_seeds | n_families | mean_v | mean_o | diff | ci_lo | ci_hi | direction | control |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | F | 5 | 290 | -0.073 | -0.076 | 0.003 | -0.023 | 0.044 | + | qwen3-4b.base_B_s0 |
| claude46 | C | 5 | 290 | -0.096 | -0.076 | -0.021 | -0.081 | 0.056 | - | qwen3-4b.base_B_s0 |
| deepseek_v4 | F | 5 | 290 | 0.150 | 0.116 | 0.035 | 3.0e-04 | 0.065 | + | qwen3-4b.base_B_s0 |
| deepseek_v4 | C | 5 | 290 | 0.170 | 0.116 | 0.054 | -0.004 | 0.100 | + | qwen3-4b.base_B_s0 |
| gpt4o | F | 5 | 290 | -0.069 | -0.035 | -0.034 | -0.080 | 0.006 | - | qwen3-4b.base_B_s0 |
| gpt4o | C | 5 | 290 | -0.025 | -0.035 | 0.010 | -0.032 | 0.054 | + | qwen3-4b.base_B_s0 |

Per-run delta_rho seed means by version (inheritance_by_form_runs.csv):

| teacher | version | mean | std | count |
|---|---|---|---|---|
| claude46 | C | -0.096 | 0.025 | 5 |
| claude46 | F | -0.073 | 0.008 | 5 |
| claude46 | O | -0.076 | 0.013 | 5 |
| deepseek_v4 | C | 0.170 | 0.038 | 5 |
| deepseek_v4 | F | 0.150 | 0.042 | 5 |
| deepseek_v4 | O | 0.116 | 0.015 | 5 |
| gpt4o | C | -0.025 | 0.027 | 5 |
| gpt4o | F | -0.069 | 0.015 | 5 |
| gpt4o | O | -0.035 | 0.019 | 5 |

### Joint partial D per version (joint_D_by_version.csv; e2 secondary statistic computed on each version's seed-pooled students)

| version | n_teachers | n_families | D | ci_lo | ci_hi | p_perm | D_specific | ci_specific_lo | ci_specific_hi | D_shared | D_raw | e2_secondary_rule |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O | 3 | 290 | 0.038 | -0.006 | 0.083 | 0.021 | 0.077 | 0.017 | 0.137 | -0.038 | 0.048 | fail |
| F | 3 | 290 | 0.050 | 0.002 | 0.098 | 0.004 | 0.096 | 0.028 | 0.164 | -0.045 | 0.059 | pass |
| C | 3 | 290 | 0.055 | 6.2e-04 | 0.113 | 0.003 | 0.098 | 0.028 | 0.170 | -0.043 | 0.059 | pass |

### Suggestibility s = delta(T5) - delta(T6) per (teacher, version) group with family-bootstrap CI (suggestibility_by_version.csv) and version differences (suggestibility_version_diffs.csv)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46:O | 5 | 290 | 0.015 | 0.009 | 0.022 |
| students:claude46:F | 5 | 290 | 0.013 | 0.007 | 0.019 |
| students:claude46:C | 5 | 290 | 0.011 | 0.005 | 0.017 |
| students:deepseek_v4:O | 5 | 290 | 0.143 | 0.118 | 0.170 |
| students:deepseek_v4:F | 5 | 290 | 0.146 | 0.121 | 0.173 |
| students:deepseek_v4:C | 5 | 290 | 0.142 | 0.118 | 0.167 |
| students:gpt4o:O | 5 | 290 | 0.105 | 0.086 | 0.126 |
| students:gpt4o:F | 5 | 290 | 0.107 | 0.088 | 0.127 |
| students:gpt4o:C | 5 | 290 | 0.103 | 0.085 | 0.121 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |

| teacher | version | contrast | diff | ci_lo | ci_hi |
|---|---|---|---|---|---|
| claude46 | F | students:V - students:O | -0.002 | -0.004 | 1.8e-04 |
| claude46 | C | students:V - students:O | -0.004 | -0.008 | -8.5e-04 |
| claude46 | O | students:V - teacher | -0.030 | -0.053 | -0.008 |
| claude46 | F | students:V - teacher | -0.031 | -0.055 | -0.010 |
| claude46 | C | students:V - teacher | -0.034 | -0.057 | -0.011 |
| deepseek_v4 | F | students:V - students:O | 0.003 | -0.004 | 0.011 |
| deepseek_v4 | C | students:V - students:O | -5.9e-04 | -0.010 | 0.009 |
| deepseek_v4 | O | students:V - teacher | 0.029 | 0.004 | 0.055 |
| deepseek_v4 | F | students:V - teacher | 0.032 | 0.008 | 0.058 |
| deepseek_v4 | C | students:V - teacher | 0.029 | 0.006 | 0.053 |
| gpt4o | F | students:V - students:O | 0.002 | -0.003 | 0.006 |
| gpt4o | C | students:V - students:O | -0.003 | -0.011 | 0.005 |
| gpt4o | O | students:V - teacher | 0.042 | 0.019 | 0.066 |
| gpt4o | F | students:V - teacher | 0.044 | 0.021 | 0.067 |
| gpt4o | C | students:V - teacher | 0.040 | 0.017 | 0.062 |

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