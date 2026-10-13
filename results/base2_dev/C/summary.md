# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.964, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.936 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.173 [-0.308, -0.035] p_perm 0.893 (null mean -0.103) p_holm 0.893; deepseek_v4 0.229 [0.135, 0.321] p_perm 0.007 (null mean 0.131) p_holm 0.020; gpt4o -0.114 [-0.222, -0.011] p_perm 0.436 (null mean -0.121) p_holm 0.872; 1/3 pass | **PARTIAL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.075 [0.016, 0.140], p 0.007; D_specific 0.139 [0.058, 0.229], D_shared -0.064 (139 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = smollm3-3b.base_B_s0) | -0.003 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.071, sd 0.015, p 1.3e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 3.908 (pearson 0.905, seed-noise sd 0.019, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.145 [-0.294, 0.007] p_holm 0.896; deepseek_v4 0.187 [0.085, 0.294] p_holm 0.020; gpt4o -0.062 [-0.175, 0.047] p_holm 0.822 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.010 [-0.089, 0.079], p 0.580 (138 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.074 [0.021, 0.130], p 0.013 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.113 [0.051, 0.176] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.328 [0.239, 0.413], margin over the next 0.185 [0.051, 0.307] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.154 | 0.744 | 0.206 | 0.327 | deepseek_v4 | -0.173 | -0.308 | -0.035 | 0.893 | -0.103 | 0.056 | 0.893 | False |
| deepseek_v4 | 5 | 139 | 0.574 | 0.825 | 0.697 | 0.346 | gpt4o | 0.229 | 0.135 | 0.321 | 0.007 | 0.131 | 0.041 | 0.020 | True |
| gpt4o | 5 | 139 | 0.381 | 0.898 | 0.425 | 0.495 | deepseek_v4 | -0.114 | -0.222 | -0.011 | 0.436 | -0.121 | 0.044 | 0.872 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.014 | -0.084 | 0.015 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = smollm3-3b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.075 | 0.016 | 0.140 | 0.007 | 0.015 | 0.024 | 0.074 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.064 | 0.139 | 0.058 | 0.229 | 5.0e-04 | 0.040 | 0.030 | 0.113 | 0.051 | 0.176 |

Row scales (sd of each pooled student's residual given r_0): smollm3-3b-e2c.claude46_O_pooled 0.095, smollm3-3b-e2c.deepseek_v4_O_pooled 0.242, smollm3-3b-e2c.gpt4o_O_pooled 0.172.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | 0.135 | 0.280 | 0.121 | 0.744 | -0.065 | 0.245 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.198 | 0.505 | 0.318 | 0.825 | 0.247 | 0.113 |
| smollm3-3b-e2c.gpt4o_O_pooled | 0.210 | 0.419 | 0.357 | 0.898 | 0.042 | 0.060 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | -0.205 | -0.495 | -0.405 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.064 | 0.200 | 0.111 |
| smollm3-3b-e2c.gpt4o_O_pooled | 0.023 | -0.008 | 0.067 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | 0.154 | 0.327 | 0.146 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.224 | 0.574 | 0.346 |
| smollm3-3b-e2c.gpt4o_O_pooled | 0.235 | 0.495 | 0.381 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | 0.061 | 0.055 | 0.116 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.070 | 0.037 | -0.093 |
| smollm3-3b-e2c.gpt4o_O_pooled | -0.004 | 0.042 | -0.036 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.094 | 0.067 | 0.124 |
| students:deepseek_v4 | 5 | 139 | 0.508 | 0.445 | 0.570 |
| students:gpt4o | 5 | 139 | 0.328 | 0.275 | 0.382 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.082 | 0.074 | 0.091 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.414 | -0.478 | -0.348 |
| students:claude46 | students:gpt4o | -0.234 | -0.285 | -0.183 |
| students:claude46 | teacher:claude46 | 0.035 | -0.010 | 0.080 |
| students:claude46 | base_prior | 0.012 | -0.016 | 0.043 |
| students:deepseek_v4 | students:gpt4o | 0.180 | 0.122 | 0.237 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.358 | 0.301 | 0.415 |
| students:deepseek_v4 | base_prior | 0.425 | 0.363 | 0.488 |
| students:gpt4o | teacher:gpt4o | 0.253 | 0.201 | 0.304 |
| students:gpt4o | base_prior | 0.245 | 0.192 | 0.300 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | base_prior | 0.053 | -0.030 | 0.082 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.094 | 0.010 | 5 |
| deepseek_v4 | 0.149 | 0.508 | 0.029 | 5 |
| gpt4o | 0.075 | 0.328 | 0.013 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.973 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.975 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.975 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.964 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.973 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.995 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.992 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.994 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.996 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.994 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.991 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.989 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.988 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s4 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.988 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.992 | True | data/sft_e2c/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 782 | 419 | 5 | 3910 | 0.958 | 0.945 | 0.968 | True |
| claude46 | gpt4o | 1046 | 546 | 5 | 5230 | 0.948 | 0.936 | 0.959 | True |
| deepseek_v4 | claude46 | 782 | 419 | 5 | 3910 | 0.992 | 0.988 | 0.995 | True |
| deepseek_v4 | gpt4o | 574 | 334 | 5 | 2870 | 0.988 | 0.982 | 0.993 | True |
| gpt4o | claude46 | 1046 | 546 | 5 | 5230 | 0.987 | 0.981 | 0.991 | True |
| gpt4o | deepseek_v4 | 574 | 334 | 5 | 2870 | 0.985 | 0.977 | 0.991 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 1.000 | 0.080 | 150 | 0.842 | 0.807 | 0.135 | 0.078 | 0.030 |
| smollm3-3b-e2c.claude46_O_s2 | 1.000 | 0.086 | 150 | 0.837 | 0.803 | 0.145 | 0.074 | 0.031 |
| smollm3-3b-e2c.claude46_O_s3 | 1.000 | 0.079 | 150 | 0.824 | 0.787 | 0.146 | 0.079 | 0.035 |
| smollm3-3b-e2c.claude46_O_s4 | 1.000 | 0.080 | 150 | 0.842 | 0.807 | 0.137 | 0.077 | 0.036 |
| smollm3-3b-e2c.claude46_O_s5 | 1.000 | 0.084 | 150 | 0.828 | 0.789 | 0.142 | 0.083 | 0.037 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 1.000 | 0.120 | 150 | 0.761 | 0.737 | 0.150 | 0.331 | 0.230 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 0.999 | 0.091 | 149 | 0.765 | 0.740 | 0.142 | 0.281 | 0.201 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 1.000 | 0.105 | 150 | 0.771 | 0.739 | 0.141 | 0.304 | 0.211 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 1.000 | 0.097 | 150 | 0.761 | 0.732 | 0.142 | 0.302 | 0.212 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 1.000 | 0.090 | 150 | 0.775 | 0.753 | 0.131 | 0.300 | 0.204 |
| smollm3-3b-e2c.gpt4o_O_s1 | 1.000 | 0.096 | 150 | 0.822 | 0.802 | 0.120 | 0.189 | 0.118 |
| smollm3-3b-e2c.gpt4o_O_s2 | 1.000 | 0.079 | 150 | 0.815 | 0.798 | 0.119 | 0.184 | 0.111 |
| smollm3-3b-e2c.gpt4o_O_s3 | 1.000 | 0.106 | 150 | 0.814 | 0.800 | 0.121 | 0.177 | 0.108 |
| smollm3-3b-e2c.gpt4o_O_s4 | 1.000 | 0.105 | 150 | 0.810 | 0.793 | 0.122 | 0.177 | 0.100 |
| smollm3-3b-e2c.gpt4o_O_s5 | 1.000 | 0.078 | 150 | 0.828 | 0.800 | 0.117 | 0.190 | 0.118 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 0.842 | 0.768 | 0.807 | 0.135 | 0.135 | 0.142 |
| smollm3-3b-e2c.claude46_O_s2 | 0.837 | 0.773 | 0.803 | 0.145 | 0.136 | 0.146 |
| smollm3-3b-e2c.claude46_O_s3 | 0.824 | 0.760 | 0.787 | 0.146 | 0.148 | 0.156 |
| smollm3-3b-e2c.claude46_O_s4 | 0.842 | 0.773 | 0.807 | 0.137 | 0.131 | 0.142 |
| smollm3-3b-e2c.claude46_O_s5 | 0.828 | 0.760 | 0.789 | 0.142 | 0.142 | 0.151 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 0.718 | 0.761 | 0.737 | 0.248 | 0.150 | 0.210 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 0.723 | 0.765 | 0.740 | 0.241 | 0.142 | 0.206 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 0.721 | 0.771 | 0.739 | 0.244 | 0.141 | 0.204 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 0.723 | 0.761 | 0.732 | 0.244 | 0.142 | 0.212 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 0.734 | 0.775 | 0.753 | 0.230 | 0.131 | 0.192 |
| smollm3-3b-e2c.gpt4o_O_s1 | 0.792 | 0.802 | 0.822 | 0.165 | 0.110 | 0.120 |
| smollm3-3b-e2c.gpt4o_O_s2 | 0.783 | 0.798 | 0.815 | 0.170 | 0.111 | 0.119 |
| smollm3-3b-e2c.gpt4o_O_s3 | 0.798 | 0.800 | 0.814 | 0.168 | 0.109 | 0.121 |
| smollm3-3b-e2c.gpt4o_O_s4 | 0.783 | 0.793 | 0.810 | 0.168 | 0.107 | 0.122 |
| smollm3-3b-e2c.gpt4o_O_s5 | 0.796 | 0.800 | 0.828 | 0.170 | 0.111 | 0.117 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| claude46 | O | 5 | 1.000 | 0.834 | 0.799 | 0.141 | 0.078 | 0.034 |
| deepseek_v4 | O | 5 | 1.000 | 0.767 | 0.740 | 0.141 | 0.304 | 0.212 |
| gpt4o | O | 5 | 1.000 | 0.818 | 0.799 | 0.120 | 0.183 | 0.111 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = smollm3-3b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 139.000 | 0.163 | 0.120 | 0.744 | 0.273 | deepseek_v4 | -0.153 | 0.898 | -0.074 | -0.318 | 0.004 | 0.120 | 0.273 | 0.154 |
| smollm3-3b-e2c.claude46_O_s2 | 139.000 | 0.172 | 0.161 | 0.744 | 0.269 | deepseek_v4 | -0.109 | 0.806 | -0.060 | -0.268 | 0.053 | 0.161 | 0.269 | 0.103 |
| smollm3-3b-e2c.claude46_O_s3 | 139.000 | 0.183 | 0.098 | 0.744 | 0.248 | deepseek_v4 | -0.150 | 0.948 | -0.055 | -0.292 | -0.003 | 0.098 | 0.248 | 0.097 |
| smollm3-3b-e2c.claude46_O_s4 | 139.000 | 0.210 | 0.137 | 0.744 | 0.240 | deepseek_v4 | -0.103 | 0.712 | -0.068 | -0.239 | 0.047 | 0.137 | 0.240 | 0.102 |
| smollm3-3b-e2c.claude46_O_s5 | 139.000 | 0.191 | 0.088 | 0.744 | 0.221 | deepseek_v4 | -0.133 | 0.870 | -0.066 | -0.276 | 0.006 | 0.088 | 0.221 | 0.083 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 139.000 | 0.460 | 0.455 | 0.825 | 0.293 | gpt4o | 0.163 | 0.029 | 0.080 | 0.056 | 0.270 | 0.195 | 0.455 | 0.293 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 139.000 | 0.437 | 0.505 | 0.825 | 0.298 | gpt4o | 0.207 | 0.001 | 0.069 | 0.106 | 0.312 | 0.173 | 0.505 | 0.298 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 139.000 | 0.439 | 0.483 | 0.825 | 0.302 | gpt4o | 0.181 | 0.010 | 0.076 | 0.068 | 0.297 | 0.180 | 0.483 | 0.302 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 139.000 | 0.434 | 0.481 | 0.825 | 0.297 | gpt4o | 0.184 | 0.009 | 0.075 | 0.083 | 0.289 | 0.192 | 0.481 | 0.297 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 139.000 | 0.421 | 0.490 | 0.825 | 0.330 | gpt4o | 0.159 | 0.029 | 0.073 | 0.050 | 0.268 | 0.204 | 0.490 | 0.330 |
| smollm3-3b-e2c.gpt4o_O_s1 | 139.000 | 0.395 | 0.300 | 0.898 | 0.399 | deepseek_v4 | -0.099 | 0.738 | -0.069 | -0.218 | 0.019 | 0.204 | 0.399 | 0.300 |
| smollm3-3b-e2c.gpt4o_O_s2 | 139.000 | 0.398 | 0.364 | 0.898 | 0.394 | deepseek_v4 | -0.030 | 0.211 | -0.069 | -0.141 | 0.077 | 0.226 | 0.394 | 0.364 |
| smollm3-3b-e2c.gpt4o_O_s3 | 139.000 | 0.381 | 0.369 | 0.898 | 0.412 | deepseek_v4 | -0.042 | 0.277 | -0.072 | -0.154 | 0.067 | 0.156 | 0.412 | 0.369 |
| smollm3-3b-e2c.gpt4o_O_s4 | 139.000 | 0.374 | 0.342 | 0.898 | 0.398 | deepseek_v4 | -0.056 | 0.385 | -0.070 | -0.162 | 0.047 | 0.197 | 0.398 | 0.342 |
| smollm3-3b-e2c.gpt4o_O_s5 | 139.000 | 0.381 | 0.318 | 0.898 | 0.383 | deepseek_v4 | -0.065 | 0.456 | -0.071 | -0.180 | 0.046 | 0.211 | 0.383 | 0.318 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.129 | 0.023 | 5 |
| deepseek_v4 | 0.179 | 0.019 | 5 |
| gpt4o | -0.058 | 0.026 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.003 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 0.135 | 0.744 | 0.308 | deepseek_v4 | -0.173 | 0.876 | -0.325 | -0.027 |
| smollm3-3b-e2c.claude46_O_s2 | 0.176 | 0.744 | 0.307 | deepseek_v4 | -0.131 | 0.793 | -0.276 | 0.016 |
| smollm3-3b-e2c.claude46_O_s3 | 0.116 | 0.744 | 0.290 | deepseek_v4 | -0.175 | 0.950 | -0.305 | -0.039 |
| smollm3-3b-e2c.claude46_O_s4 | 0.156 | 0.744 | 0.290 | deepseek_v4 | -0.135 | 0.723 | -0.264 | 0.004 |
| smollm3-3b-e2c.claude46_O_s5 | 0.107 | 0.744 | 0.267 | deepseek_v4 | -0.161 | 0.877 | -0.293 | -0.029 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 0.533 | 0.825 | 0.323 | gpt4o | 0.210 | 0.025 | 0.109 | 0.307 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 0.572 | 0.825 | 0.328 | gpt4o | 0.244 | 0.001 | 0.143 | 0.344 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 0.554 | 0.825 | 0.331 | gpt4o | 0.223 | 0.012 | 0.125 | 0.321 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 0.551 | 0.825 | 0.327 | gpt4o | 0.225 | 0.008 | 0.130 | 0.319 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 0.558 | 0.825 | 0.357 | gpt4o | 0.201 | 0.034 | 0.101 | 0.298 |
| smollm3-3b-e2c.gpt4o_O_s1 | 0.330 | 0.898 | 0.476 | deepseek_v4 | -0.146 | 0.751 | -0.263 | -0.030 |
| smollm3-3b-e2c.gpt4o_O_s2 | 0.388 | 0.898 | 0.472 | deepseek_v4 | -0.084 | 0.241 | -0.191 | 0.016 |
| smollm3-3b-e2c.gpt4o_O_s3 | 0.393 | 0.898 | 0.485 | deepseek_v4 | -0.092 | 0.278 | -0.196 | 0.010 |
| smollm3-3b-e2c.gpt4o_O_s4 | 0.368 | 0.898 | 0.471 | deepseek_v4 | -0.104 | 0.398 | -0.201 | -0.008 |
| smollm3-3b-e2c.gpt4o_O_s5 | 0.345 | 0.898 | 0.459 | deepseek_v4 | -0.114 | 0.503 | -0.227 | -0.004 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.047 | 0.031 | 5 |
| claude46 | T1 | 0.079 | 0.073 | 5 |
| claude46 | T3 | -0.108 | 0.059 | 5 |
| claude46 | T5 | -0.129 | 0.052 | 5 |
| claude46 | T6 | -0.105 | 0.020 | 5 |
| deepseek_v4 | T0 | -0.030 | 0.050 | 5 |
| deepseek_v4 | T1 | 0.262 | 0.042 | 5 |
| deepseek_v4 | T3 | 0.174 | 0.032 | 5 |
| deepseek_v4 | T5 | 0.088 | 0.060 | 5 |
| deepseek_v4 | T6 | 0.103 | 0.033 | 5 |
| gpt4o | T0 | -0.094 | 0.084 | 5 |
| gpt4o | T1 | 0.089 | 0.073 | 5 |
| gpt4o | T3 | -0.125 | 0.056 | 5 |
| gpt4o | T5 | -0.012 | 0.033 | 5 |
| gpt4o | T6 | -0.013 | 0.062 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.206 | 0.135 | 0.744 | 0.280 | deepseek_v4 | -0.145 | -0.294 | 0.007 | 0.896 | -0.070 | 0.896 |
| deepseek_v4 | 5 | 139 | 0.455 | 0.505 | 0.825 | 0.318 | gpt4o | 0.187 | 0.085 | 0.294 | 0.007 | 0.079 | 0.020 |
| gpt4o | 5 | 139 | 0.404 | 0.357 | 0.898 | 0.419 | deepseek_v4 | -0.062 | -0.175 | 0.047 | 0.411 | -0.073 | 0.822 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.108 | 0.744 | 0.009 | 0.205 | 3 | -0.220 | -0.332 | -0.108 |
| smollm3-3b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.328 | 0.825 | 0.239 | 0.413 | 1 | 0.185 | 0.051 | 0.307 |
| smollm3-3b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.143 | 0.898 | 0.001 | 0.263 | 2 | -0.185 | -0.336 | -0.051 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 5/5 seeds pass -> ok (old rule, not the verdict)
- deepseek_v4: 5/5 seeds pass -> ok (old rule, not the verdict)
- gpt4o: 5/5 seeds pass -> ok (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial -0.003 vs run-reassignment null mean -0.071 sd 0.015, p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 3.908, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.075 [0.016, 0.140] p 0.007 alone would read pass; the frozen rule (version 5) also needs D_specific 0.139 [0.058, 0.229] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.010 | 0.006 | 0.018 |
| agree_own | deepseek_v4 | O | 10 | 0.007 | 0.005 | 0.013 |
| agree_own | gpt4o | O | 10 | 0.009 | 0.005 | 0.016 |
| agree_own | all | all | 30 | 0.009 | 0.005 | 0.018 |
| jsd_own | claude46 | O | 10 | 0.006 | 0.003 | 0.011 |
| jsd_own | deepseek_v4 | O | 10 | 0.008 | 0.006 | 0.015 |
| jsd_own | gpt4o | O | 10 | 0.003 | 0.001 | 0.005 |
| jsd_own | all | all | 30 | 0.006 | 0.004 | 0.011 |
| flip_rate | claude46 | O | 10 | 0.004 | 0.003 | 0.008 |
| flip_rate | deepseek_v4 | O | 10 | 0.021 | 0.015 | 0.042 |
| flip_rate | gpt4o | O | 10 | 0.008 | 0.005 | 0.013 |
| flip_rate | all | all | 30 | 0.011 | 0.012 | 0.030 |
| mean_jsd | claude46 | O | 10 | 0.004 | 0.002 | 0.007 |
| mean_jsd | deepseek_v4 | O | 10 | 0.013 | 0.009 | 0.027 |
| mean_jsd | gpt4o | O | 10 | 0.009 | 0.006 | 0.018 |
| mean_jsd | all | all | 30 | 0.009 | 0.007 | 0.023 |
| delta_rho | claude46 | O | 10 | 0.025 | 0.016 | 0.042 |
| delta_rho | deepseek_v4 | O | 10 | 0.021 | 0.012 | 0.040 |
| delta_rho | gpt4o | O | 10 | 0.029 | 0.019 | 0.059 |
| delta_rho | all | all | 30 | 0.025 | 0.016 | 0.050 |
| delta_rho_partial | claude46 | O | 10 | 0.028 | 0.017 | 0.049 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.023 | 0.014 | 0.046 |
| delta_rho_partial | gpt4o | O | 10 | 0.032 | 0.020 | 0.063 |
| delta_rho_partial | all | all | 30 | 0.028 | 0.017 | 0.054 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.