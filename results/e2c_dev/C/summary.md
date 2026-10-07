# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.975, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.946 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.182 [-0.344, -0.030] p_perm 0.897 (null mean -0.107) p_holm 0.897; deepseek_v4 0.200 [0.094, 0.309] p_perm 0.043 (null mean 0.129) p_holm 0.128; gpt4o -0.078 [-0.202, 0.039] p_perm 0.210 (null mean -0.115) p_holm 0.420; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.079 [0.004, 0.147], p 0.009; D_specific 0.112 [0.024, 0.198], D_shared -0.033 (139 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.015 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.059, sd 0.016, p 4.0e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 3.063 (pearson 0.888, seed-noise sd 0.023, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.084 [-0.267, 0.033] p_holm 0.624; deepseek_v4 0.063 [-0.069, 0.205] p_holm 0.587; gpt4o 0.067 [-0.061, 0.188] p_holm 0.081 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.026 [-0.094, 0.046], p 0.713 (138 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.072 [0.014, 0.124], p 0.014 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.098 [0.023, 0.169] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.148 | 0.744 | 0.199 | 0.330 | deepseek_v4 | -0.182 | -0.344 | -0.030 | 0.897 | -0.107 | 0.060 | 0.897 | False |
| deepseek_v4 | 5 | 139 | 0.515 | 0.825 | 0.625 | 0.316 | gpt4o | 0.200 | 0.094 | 0.309 | 0.043 | 0.129 | 0.041 | 0.128 | False |
| gpt4o | 5 | 139 | 0.416 | 0.898 | 0.463 | 0.493 | deepseek_v4 | -0.078 | -0.202 | 0.039 | 0.210 | -0.115 | 0.046 | 0.420 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.016 | -0.085 | 0.014 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.079 | 0.004 | 0.147 | 0.009 | 0.009 | 0.029 | 0.072 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.033 | 0.112 | 0.024 | 0.198 | 0.001 | 0.014 | 0.032 | 0.098 | 0.023 | 0.169 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2c.claude46_O_pooled 0.098, qwen3-4b-e2c.deepseek_v4_O_pooled 0.173, qwen3-4b-e2c.gpt4o_O_pooled 0.149.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.049 | 0.134 | 0.103 | 0.744 | -0.069 | 0.180 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.027 | 0.244 | 0.180 | 0.825 | 0.140 | 0.063 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.059 | 0.258 | 0.325 | 0.898 | 0.166 | 0.091 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | -0.013 | -0.185 | -0.202 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | -0.008 | 0.063 | 0.008 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.018 | 0.048 | 0.124 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.148 | 0.330 | 0.208 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.187 | 0.515 | 0.316 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.192 | 0.493 | 0.416 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.021 | 0.159 | 0.070 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.137 | 0.074 | -0.025 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.099 | 0.173 | 0.133 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.106 | 0.077 | 0.138 |
| students:deepseek_v4 | 5 | 139 | 0.434 | 0.371 | 0.494 |
| students:gpt4o | 5 | 139 | 0.298 | 0.243 | 0.356 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.165 | 0.144 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.328 | -0.386 | -0.268 |
| students:claude46 | students:gpt4o | -0.192 | -0.244 | -0.142 |
| students:claude46 | teacher:claude46 | 0.047 | 7.0e-04 | 0.094 |
| students:claude46 | base_prior | -0.059 | -0.087 | -0.030 |
| students:deepseek_v4 | students:gpt4o | 0.135 | 0.075 | 0.196 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.284 | 0.225 | 0.343 |
| students:deepseek_v4 | base_prior | 0.269 | 0.215 | 0.322 |
| students:gpt4o | teacher:gpt4o | 0.223 | 0.174 | 0.276 |
| students:gpt4o | base_prior | 0.134 | 0.083 | 0.187 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.091 | 0.165 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.106 | 0.014 | 5 |
| deepseek_v4 | 0.149 | 0.434 | 0.022 | 5 |
| gpt4o | 0.075 | 0.298 | 0.030 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.975 | True | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.984 | True | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.980 | True | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.980 | True | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.977 | True | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.992 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.995 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.994 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.996 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.993 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.990 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.990 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.991 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s4 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.989 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.991 | True | data/sft_e2c/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 782 | 419 | 5 | 3910 | 0.973 | 0.963 | 0.982 | True |
| claude46 | gpt4o | 1046 | 546 | 5 | 5230 | 0.957 | 0.946 | 0.967 | True |
| deepseek_v4 | claude46 | 782 | 419 | 5 | 3910 | 0.989 | 0.984 | 0.994 | True |
| deepseek_v4 | gpt4o | 574 | 334 | 5 | 2870 | 0.989 | 0.983 | 0.994 | True |
| gpt4o | claude46 | 1046 | 546 | 5 | 5230 | 0.983 | 0.978 | 0.989 | True |
| gpt4o | deepseek_v4 | 574 | 334 | 5 | 2870 | 0.981 | 0.972 | 0.989 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2c.claude46_O_s1 | 1.000 | 0.079 | 150 | 0.833 | 0.798 | 0.135 | 0.094 | 0.045 |
| qwen3-4b-e2c.claude46_O_s2 | 1.000 | 0.077 | 150 | 0.833 | 0.803 | 0.137 | 0.083 | 0.044 |
| qwen3-4b-e2c.claude46_O_s3 | 1.000 | 0.070 | 150 | 0.853 | 0.812 | 0.131 | 0.067 | 0.035 |
| qwen3-4b-e2c.claude46_O_s4 | 1.000 | 0.076 | 150 | 0.826 | 0.782 | 0.140 | 0.084 | 0.042 |
| qwen3-4b-e2c.claude46_O_s5 | 1.000 | 0.071 | 150 | 0.838 | 0.800 | 0.130 | 0.076 | 0.035 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 1.000 | 0.124 | 150 | 0.792 | 0.744 | 0.129 | 0.206 | 0.148 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 1.000 | 0.111 | 150 | 0.802 | 0.770 | 0.123 | 0.218 | 0.160 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 1.000 | 0.096 | 150 | 0.766 | 0.725 | 0.145 | 0.251 | 0.174 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 1.000 | 0.091 | 150 | 0.782 | 0.747 | 0.127 | 0.253 | 0.180 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 1.000 | 0.118 | 150 | 0.798 | 0.751 | 0.129 | 0.239 | 0.171 |
| qwen3-4b-e2c.gpt4o_O_s1 | 1.000 | 0.070 | 150 | 0.838 | 0.832 | 0.110 | 0.158 | 0.101 |
| qwen3-4b-e2c.gpt4o_O_s2 | 1.000 | 0.076 | 150 | 0.834 | 0.827 | 0.116 | 0.188 | 0.120 |
| qwen3-4b-e2c.gpt4o_O_s3 | 1.000 | 0.072 | 150 | 0.848 | 0.835 | 0.103 | 0.153 | 0.091 |
| qwen3-4b-e2c.gpt4o_O_s4 | 1.000 | 0.081 | 150 | 0.836 | 0.826 | 0.112 | 0.128 | 0.086 |
| qwen3-4b-e2c.gpt4o_O_s5 | 1.000 | 0.086 | 150 | 0.838 | 0.829 | 0.109 | 0.180 | 0.103 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2c.claude46_O_s1 | 0.833 | 0.766 | 0.798 | 0.135 | 0.133 | 0.138 |
| qwen3-4b-e2c.claude46_O_s2 | 0.833 | 0.773 | 0.803 | 0.137 | 0.136 | 0.138 |
| qwen3-4b-e2c.claude46_O_s3 | 0.853 | 0.782 | 0.812 | 0.131 | 0.142 | 0.142 |
| qwen3-4b-e2c.claude46_O_s4 | 0.826 | 0.768 | 0.782 | 0.140 | 0.136 | 0.148 |
| qwen3-4b-e2c.claude46_O_s5 | 0.838 | 0.778 | 0.800 | 0.130 | 0.139 | 0.141 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 0.721 | 0.792 | 0.744 | 0.233 | 0.129 | 0.195 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 0.751 | 0.802 | 0.770 | 0.212 | 0.123 | 0.179 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 0.707 | 0.766 | 0.725 | 0.245 | 0.145 | 0.213 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 0.726 | 0.782 | 0.747 | 0.223 | 0.127 | 0.192 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 0.728 | 0.798 | 0.751 | 0.229 | 0.129 | 0.191 |
| qwen3-4b-e2c.gpt4o_O_s1 | 0.822 | 0.832 | 0.838 | 0.145 | 0.102 | 0.110 |
| qwen3-4b-e2c.gpt4o_O_s2 | 0.810 | 0.827 | 0.834 | 0.157 | 0.106 | 0.116 |
| qwen3-4b-e2c.gpt4o_O_s3 | 0.831 | 0.835 | 0.848 | 0.141 | 0.098 | 0.103 |
| qwen3-4b-e2c.gpt4o_O_s4 | 0.826 | 0.820 | 0.836 | 0.143 | 0.102 | 0.112 |
| qwen3-4b-e2c.gpt4o_O_s5 | 0.824 | 0.829 | 0.838 | 0.141 | 0.100 | 0.109 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.837 | 0.799 | 0.135 | 0.081 | 0.040 |
| deepseek_v4 | O | 5 | 1.000 | 0.788 | 0.747 | 0.131 | 0.233 | 0.167 |
| gpt4o | O | 5 | 1.000 | 0.839 | 0.830 | 0.110 | 0.161 | 0.100 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 139.000 | 0.410 | 0.012 | 0.744 | 0.136 | deepseek_v4 | -0.125 | 0.832 | -0.065 | -0.311 | -0.014 | 0.012 | 0.136 | 0.108 |
| qwen3-4b-e2c.claude46_O_s2 | 139.000 | 0.401 | 0.033 | 0.744 | 0.181 | deepseek_v4 | -0.148 | 0.916 | -0.061 | -0.362 | 0.019 | 0.033 | 0.181 | 0.115 |
| qwen3-4b-e2c.claude46_O_s3 | 139.000 | 0.365 | 0.070 | 0.744 | 0.125 | deepseek_v4 | -0.055 | 0.480 | -0.059 | -0.271 | 0.078 | 0.070 | 0.125 | 0.105 |
| qwen3-4b-e2c.claude46_O_s4 | 139.000 | 0.405 | 0.045 | 0.744 | 0.083 | gpt4o | -0.038 | 0.353 | -0.063 | -0.186 | 0.051 | 0.045 | 0.069 | 0.083 |
| qwen3-4b-e2c.claude46_O_s5 | 139.000 | 0.384 | 0.072 | 0.744 | 0.090 | deepseek_v4 | -0.018 | 0.262 | -0.060 | -0.157 | 0.076 | 0.072 | 0.090 | 0.055 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 139.000 | 0.675 | 0.192 | 0.825 | 0.170 | gpt4o | 0.022 | 0.584 | 0.032 | -0.106 | 0.153 | 0.025 | 0.192 | 0.170 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 139.000 | 0.658 | 0.273 | 0.825 | 0.180 | gpt4o | 0.093 | 0.117 | 0.032 | -0.040 | 0.224 | 0.105 | 0.273 | 0.180 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 139.000 | 0.648 | 0.176 | 0.825 | 0.156 | gpt4o | 0.020 | 0.615 | 0.035 | -0.106 | 0.145 | 0.002 | 0.176 | 0.156 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 139.000 | 0.635 | 0.261 | 0.825 | 0.192 | gpt4o | 0.069 | 0.249 | 0.034 | -0.072 | 0.213 | -0.011 | 0.261 | 0.192 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 139.000 | 0.671 | 0.224 | 0.825 | 0.136 | gpt4o | 0.089 | 0.137 | 0.033 | -0.057 | 0.227 | 0.011 | 0.224 | 0.136 |
| qwen3-4b-e2c.gpt4o_O_s1 | 139.000 | 0.568 | 0.301 | 0.898 | 0.249 | deepseek_v4 | 0.053 | 0.057 | -0.034 | -0.075 | 0.176 | 0.043 | 0.249 | 0.301 |
| qwen3-4b-e2c.gpt4o_O_s2 | 139.000 | 0.589 | 0.318 | 0.898 | 0.248 | deepseek_v4 | 0.070 | 0.025 | -0.036 | -0.056 | 0.193 | 0.044 | 0.248 | 0.318 |
| qwen3-4b-e2c.gpt4o_O_s3 | 139.000 | 0.566 | 0.324 | 0.898 | 0.228 | deepseek_v4 | 0.096 | 0.008 | -0.036 | -0.035 | 0.223 | 0.068 | 0.228 | 0.324 |
| qwen3-4b-e2c.gpt4o_O_s4 | 139.000 | 0.546 | 0.285 | 0.898 | 0.232 | deepseek_v4 | 0.053 | 0.050 | -0.035 | -0.078 | 0.185 | 0.053 | 0.232 | 0.285 |
| qwen3-4b-e2c.gpt4o_O_s5 | 139.000 | 0.582 | 0.293 | 0.898 | 0.253 | deepseek_v4 | 0.040 | 0.073 | -0.038 | -0.080 | 0.163 | 0.069 | 0.253 | 0.293 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.077 | 0.057 | 5 |
| deepseek_v4 | 0.058 | 0.036 | 5 |
| gpt4o | 0.063 | 0.022 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.015 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 0.111 | 0.744 | 0.324 | deepseek_v4 | -0.213 | 0.967 | -0.379 | -0.066 |
| qwen3-4b-e2c.claude46_O_s2 | 0.127 | 0.744 | 0.354 | deepseek_v4 | -0.226 | 0.982 | -0.416 | -0.040 |
| qwen3-4b-e2c.claude46_O_s3 | 0.152 | 0.744 | 0.293 | deepseek_v4 | -0.140 | 0.777 | -0.332 | 0.027 |
| qwen3-4b-e2c.claude46_O_s4 | 0.139 | 0.744 | 0.269 | deepseek_v4 | -0.130 | 0.685 | -0.263 | -0.011 |
| qwen3-4b-e2c.claude46_O_s5 | 0.158 | 0.744 | 0.275 | deepseek_v4 | -0.116 | 0.639 | -0.246 | 0.001 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 0.479 | 0.825 | 0.307 | gpt4o | 0.172 | 0.120 | 0.068 | 0.274 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 0.525 | 0.825 | 0.312 | gpt4o | 0.212 | 0.014 | 0.107 | 0.309 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 0.459 | 0.825 | 0.294 | gpt4o | 0.165 | 0.174 | 0.063 | 0.270 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 0.509 | 0.825 | 0.318 | gpt4o | 0.190 | 0.060 | 0.091 | 0.295 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 0.498 | 0.825 | 0.282 | gpt4o | 0.216 | 0.013 | 0.092 | 0.337 |
| qwen3-4b-e2c.gpt4o_O_s1 | 0.396 | 0.898 | 0.476 | deepseek_v4 | -0.080 | 0.310 | -0.211 | 0.044 |
| qwen3-4b-e2c.gpt4o_O_s2 | 0.410 | 0.898 | 0.483 | deepseek_v4 | -0.073 | 0.191 | -0.199 | 0.044 |
| qwen3-4b-e2c.gpt4o_O_s3 | 0.413 | 0.898 | 0.461 | deepseek_v4 | -0.047 | 0.093 | -0.169 | 0.067 |
| qwen3-4b-e2c.gpt4o_O_s4 | 0.380 | 0.898 | 0.455 | deepseek_v4 | -0.075 | 0.249 | -0.198 | 0.045 |
| qwen3-4b-e2c.gpt4o_O_s5 | 0.390 | 0.898 | 0.484 | deepseek_v4 | -0.094 | 0.318 | -0.213 | 0.024 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.126 | 0.066 | 5 |
| claude46 | T1 | -0.042 | 0.030 | 5 |
| claude46 | T3 | -0.187 | 0.114 | 5 |
| claude46 | T5 | -0.302 | 0.091 | 5 |
| claude46 | T6 | 0.038 | 0.043 | 5 |
| deepseek_v4 | T0 | -0.058 | 0.057 | 5 |
| deepseek_v4 | T1 | 0.098 | 0.088 | 5 |
| deepseek_v4 | T3 | 0.121 | 0.070 | 5 |
| deepseek_v4 | T5 | -0.009 | 0.029 | 5 |
| deepseek_v4 | T6 | -0.003 | 0.051 | 5 |
| gpt4o | T0 | -0.037 | 0.051 | 5 |
| gpt4o | T1 | -0.003 | 0.099 | 5 |
| gpt4o | T3 | -0.099 | 0.057 | 5 |
| gpt4o | T5 | 0.208 | 0.026 | 5 |
| gpt4o | T6 | 0.061 | 0.033 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.427 | 0.049 | 0.744 | 0.134 | deepseek_v4 | -0.084 | -0.267 | 0.033 | 0.624 | -0.065 | 0.624 |
| deepseek_v4 | 5 | 139 | 0.685 | 0.244 | 0.825 | 0.180 | gpt4o | 0.063 | -0.069 | 0.205 | 0.293 | 0.036 | 0.587 |
| gpt4o | 5 | 139 | 0.596 | 0.325 | 0.898 | 0.258 | deepseek_v4 | 0.067 | -0.061 | 0.188 | 0.027 | -0.036 | 0.081 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.245 | 0.744 | 0.118 | 0.365 | 3 | -0.288 | -0.419 | -0.164 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.533 | 0.825 | 0.448 | 0.611 | 1 | 0.256 | 0.130 | 0.359 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.277 | 0.898 | 0.166 | 0.380 | 2 | -0.256 | -0.383 | -0.133 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 5/5 seeds pass -> ok (old rule, not the verdict)
- deepseek_v4: 5/5 seeds pass -> ok (old rule, not the verdict)
- gpt4o: 5/5 seeds pass -> ok (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 0.015 vs run-reassignment null mean -0.059 sd 0.016, p 4.0e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 3.063, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.079 [0.004, 0.147] p 0.009 alone would read pass; the frozen rule (version 5) also needs D_specific 0.112 [0.024, 0.198] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.012 | 0.008 | 0.023 |
| agree_own | deepseek_v4 | O | 10 | 0.017 | 0.011 | 0.034 |
| agree_own | gpt4o | O | 10 | 0.006 | 0.005 | 0.013 |
| agree_own | all | all | 30 | 0.012 | 0.009 | 0.030 |
| jsd_own | claude46 | O | 10 | 0.006 | 0.003 | 0.010 |
| jsd_own | deepseek_v4 | O | 10 | 0.009 | 0.008 | 0.020 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.004 | 0.011 |
| jsd_own | all | all | 30 | 0.007 | 0.005 | 0.017 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.013 | 0.007 | 0.024 |
| flip_rate | deepseek_v4 | O | 10 | 0.026 | 0.015 | 0.047 |
| flip_rate | gpt4o | O | 10 | 0.029 | 0.017 | 0.057 |
| flip_rate | all | all | 30 | 0.023 | 0.015 | 0.050 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.006 | 0.004 | 0.010 |
| mean_jsd | deepseek_v4 | O | 10 | 0.016 | 0.009 | 0.030 |
| mean_jsd | gpt4o | O | 10 | 0.016 | 0.010 | 0.032 |
| mean_jsd | all | all | 30 | 0.013 | 0.009 | 0.031 |
| delta_rho | claude46 | O | 10 | 0.061 | 0.040 | 0.104 |
| delta_rho | deepseek_v4 | O | 10 | 0.028 | 0.017 | 0.049 |
| delta_rho | gpt4o | O | 10 | 0.020 | 0.014 | 0.040 |
| delta_rho | all | all | 30 | 0.036 | 0.031 | 0.097 |
| delta_rho_partial | claude46 | O | 10 | 0.069 | 0.042 | 0.121 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.043 | 0.028 | 0.073 |
| delta_rho_partial | gpt4o | O | 10 | 0.026 | 0.017 | 0.050 |
| delta_rho_partial | all | all | 30 | 0.046 | 0.035 | 0.108 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.