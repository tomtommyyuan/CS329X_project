# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.990, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.977 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.137 [-0.240, -0.053] p_perm 0.920 (null mean -0.083) p_holm 1.000; deepseek_v4 0.222 [0.149, 0.294] p_perm 5.0e-04 (null mean 0.119) p_holm 0.001; gpt4o -0.141 [-0.231, -0.052] p_perm 0.870 (null mean -0.101) p_holm 1.000; 1/3 pass | **PARTIAL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.048 [0.004, 0.092], p 0.022; D_specific 0.070 [0.022, 0.120], D_shared -0.021 (290 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 290 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.017 | teacher-level exact p 0.333 (rank 2 of 6 relabellings, floor 0.167); the run-level null (mean -0.049, sd 0.021, p 2.1e-04, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 5.268 (pearson 0.965, seed-noise sd 0.016, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.065 [-0.184, 0.012] p_holm 1.000; deepseek_v4 0.237 [0.135, 0.304] p_holm 3.0e-04; gpt4o -0.117 [-0.228, -0.009] p_holm 1.000 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.029 [-0.109, 0.050], p 0.814 (288 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.052 [0.014, 0.089], p 0.052 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.072 [0.026, 0.118] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.380 [0.327, 0.434], margin over the next 0.100 [0.036, 0.167] (290 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.117 | 0.704 | 0.167 | 0.254 | deepseek_v4 | -0.137 | -0.240 | -0.053 | 0.920 | -0.083 | 0.038 | 1.000 | False |
| deepseek_v4 | 5 | 290 | 0.493 | 0.797 | 0.618 | 0.271 | gpt4o | 0.222 | 0.149 | 0.294 | 5.0e-04 | 0.119 | 0.032 | 0.001 | True |
| gpt4o | 5 | 290 | 0.312 | 0.904 | 0.346 | 0.453 | deepseek_v4 | -0.141 | -0.231 | -0.052 | 0.870 | -0.101 | 0.035 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.013 | -0.077 | 0.019 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.048 | 0.004 | 0.092 | 0.022 | 0.010 | 0.019 | 0.052 | 290 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.021 | 0.070 | 0.022 | 0.120 | 0.003 | 0.015 | 0.020 | 0.072 | 0.026 | 0.118 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2c-paired.claude46_O_pooled 0.108, qwen3-4b-e2c-paired.deepseek_v4_O_pooled 0.180, qwen3-4b-e2c-paired.gpt4o_O_pooled 0.144.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | 0.084 | 0.149 | 0.131 | 0.704 | -0.056 | 0.075 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.099 | 0.342 | 0.105 | 0.797 | 0.240 | 0.116 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.155 | 0.310 | 0.193 | 0.904 | -0.040 | 0.018 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | -0.068 | -0.230 | -0.057 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.008 | 0.116 | -0.007 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.041 | 0.027 | 0.052 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | 0.117 | 0.254 | 0.210 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.153 | 0.493 | 0.271 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.194 | 0.453 | 0.312 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | -0.058 | 0.133 | 0.030 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.004 | 0.143 | -0.006 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | -0.023 | 0.171 | -0.018 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 290 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 290 | 0.091 | 0.071 | 0.113 |
| students:deepseek_v4 | 5 | 290 | 0.478 | 0.433 | 0.524 |
| students:gpt4o | 5 | 290 | 0.281 | 0.244 | 0.320 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |
| base_prior | 1 | 290 | 0.146 | 0.133 | 0.159 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.387 | -0.434 | -0.343 |
| students:claude46 | students:gpt4o | -0.190 | -0.227 | -0.155 |
| students:claude46 | teacher:claude46 | 0.047 | 0.018 | 0.074 |
| students:claude46 | base_prior | -0.055 | -0.076 | -0.033 |
| students:deepseek_v4 | students:gpt4o | 0.197 | 0.154 | 0.240 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.365 | 0.323 | 0.408 |
| students:deepseek_v4 | base_prior | 0.332 | 0.294 | 0.372 |
| students:gpt4o | teacher:gpt4o | 0.218 | 0.182 | 0.258 |
| students:gpt4o | base_prior | 0.136 | 0.101 | 0.171 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | run | 0.035 | -0.063 | 0.097 | 290 |
| qwen3-4b-e2c-paired.claude46_C_s2 | run | 0.021 | -0.033 | 0.054 | 290 |
| qwen3-4b-e2c-paired.claude46_C_s3 | run | 0.031 | -0.045 | 0.076 | 289 |
| qwen3-4b-e2c-paired.claude46_C_s4 | run | 0.022 | -0.039 | 0.061 | 290 |
| qwen3-4b-e2c-paired.claude46_C_s5 | run | 0.032 | -0.038 | 0.070 | 290 |
| qwen3-4b-e2c-paired.claude46_F_s1 | run | 0.038 | -0.053 | 0.092 | 290 |
| qwen3-4b-e2c-paired.claude46_F_s2 | run | 0.039 | -0.047 | 0.086 | 290 |
| qwen3-4b-e2c-paired.claude46_F_s3 | run | 0.038 | -0.048 | 0.086 | 290 |
| qwen3-4b-e2c-paired.claude46_F_s4 | run | 0.039 | -0.051 | 0.090 | 289 |
| qwen3-4b-e2c-paired.claude46_F_s5 | run | 0.039 | -0.054 | 0.093 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | run | 0.200 | -0.307 | 0.507 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | run | 0.179 | -0.280 | 0.460 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | run | 0.189 | -0.269 | 0.457 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | run | 0.198 | -0.298 | 0.496 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | run | 0.165 | -0.242 | 0.407 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | run | 0.209 | -0.306 | 0.515 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | run | 0.198 | -0.303 | 0.502 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | run | 0.169 | -0.254 | 0.423 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | run | 0.185 | -0.282 | 0.468 | 290 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | run | 0.181 | -0.276 | 0.457 | 290 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | run | 0.121 | -0.166 | 0.287 | 290 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | run | 0.144 | -0.190 | 0.334 | 290 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | run | 0.135 | -0.185 | 0.320 | 290 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | run | 0.134 | -0.177 | 0.311 | 290 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | run | 0.131 | -0.183 | 0.314 | 290 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | run | 0.116 | -0.154 | 0.270 | 290 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | run | 0.127 | -0.185 | 0.312 | 290 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | run | 0.134 | -0.182 | 0.316 | 290 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | run | 0.138 | -0.185 | 0.323 | 290 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | run | 0.142 | -0.197 | 0.339 | 290 |
| qwen3-4b.base_B_s0 | run | 0.057 | -0.120 | 0.178 | 8 |
| qwen3-4b.base_B_s0 | base_prior | 0.068 | -0.078 | 0.146 | 290 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.091 | 0.010 | 5 |
| deepseek_v4 | 0.113 | 0.478 | 0.011 | 5 |
| gpt4o | 0.063 | 0.281 | 0.024 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.988 | nan | data/sft_e2c_paired/claude46_C_s1.jsonl |
| qwen3-4b-e2c-paired.claude46_C_s2 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.993 | nan | data/sft_e2c_paired/claude46_C_s2.jsonl |
| qwen3-4b-e2c-paired.claude46_C_s3 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.989 | nan | data/sft_e2c_paired/claude46_C_s3.jsonl |
| qwen3-4b-e2c-paired.claude46_C_s4 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.988 | nan | data/sft_e2c_paired/claude46_C_s4.jsonl |
| qwen3-4b-e2c-paired.claude46_C_s5 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.990 | nan | data/sft_e2c_paired/claude46_C_s5.jsonl |
| qwen3-4b-e2c-paired.claude46_F_s1 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.990 | nan | data/sft_e2c_paired/claude46_F_s1.jsonl |
| qwen3-4b-e2c-paired.claude46_F_s2 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.992 | nan | data/sft_e2c_paired/claude46_F_s2.jsonl |
| qwen3-4b-e2c-paired.claude46_F_s3 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.989 | nan | data/sft_e2c_paired/claude46_F_s3.jsonl |
| qwen3-4b-e2c-paired.claude46_F_s4 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.985 | nan | data/sft_e2c_paired/claude46_F_s4.jsonl |
| qwen3-4b-e2c-paired.claude46_F_s5 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.991 | nan | data/sft_e2c_paired/claude46_F_s5.jsonl |
| qwen3-4b-e2c-paired.claude46_O_s1 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.990 | True | data/sft_e2c_paired/claude46_O_s1.jsonl |
| qwen3-4b-e2c-paired.claude46_O_s2 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.993 | True | data/sft_e2c_paired/claude46_O_s1.jsonl |
| qwen3-4b-e2c-paired.claude46_O_s3 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.991 | True | data/sft_e2c_paired/claude46_O_s1.jsonl |
| qwen3-4b-e2c-paired.claude46_O_s4 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.990 | True | data/sft_e2c_paired/claude46_O_s1.jsonl |
| qwen3-4b-e2c-paired.claude46_O_s5 | 4122 | 1.000 | 4122 | 4122 | 0 | 0 | 0.991 | True | data/sft_e2c_paired/claude46_O_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.997 | nan | data/sft_e2c_paired/deepseek_v4_C_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.998 | nan | data/sft_e2c_paired/deepseek_v4_C_s2.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.997 | nan | data/sft_e2c_paired/deepseek_v4_C_s3.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 1.000 | nan | data/sft_e2c_paired/deepseek_v4_C_s4.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.996 | nan | data/sft_e2c_paired/deepseek_v4_C_s5.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.997 | nan | data/sft_e2c_paired/deepseek_v4_F_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.997 | nan | data/sft_e2c_paired/deepseek_v4_F_s2.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.999 | nan | data/sft_e2c_paired/deepseek_v4_F_s3.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.998 | nan | data/sft_e2c_paired/deepseek_v4_F_s4.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.996 | nan | data/sft_e2c_paired/deepseek_v4_F_s5.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.996 | True | data/sft_e2c_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.996 | True | data/sft_e2c_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.996 | True | data/sft_e2c_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.999 | True | data/sft_e2c_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 2228 | 1.000 | 2228 | 2228 | 0 | 0 | 0.998 | True | data/sft_e2c_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.992 | nan | data/sft_e2c_paired/gpt4o_C_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.995 | nan | data/sft_e2c_paired/gpt4o_C_s2.jsonl |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | nan | data/sft_e2c_paired/gpt4o_C_s3.jsonl |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | nan | data/sft_e2c_paired/gpt4o_C_s4.jsonl |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | nan | data/sft_e2c_paired/gpt4o_C_s5.jsonl |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.995 | nan | data/sft_e2c_paired/gpt4o_F_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | nan | data/sft_e2c_paired/gpt4o_F_s2.jsonl |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.993 | nan | data/sft_e2c_paired/gpt4o_F_s3.jsonl |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | nan | data/sft_e2c_paired/gpt4o_F_s4.jsonl |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.995 | nan | data/sft_e2c_paired/gpt4o_F_s5.jsonl |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | True | data/sft_e2c_paired/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.995 | True | data/sft_e2c_paired/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.995 | True | data/sft_e2c_paired/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.994 | True | data/sft_e2c_paired/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 4527 | 1.000 | 4527 | 4527 | 0 | 0 | 0.993 | True | data/sft_e2c_paired/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 563 | 363 | 5 | 2815 | 0.989 | 0.983 | 0.994 | True |
| claude46 | gpt4o | 760 | 463 | 5 | 3800 | 0.984 | 0.977 | 0.990 | True |
| deepseek_v4 | claude46 | 563 | 363 | 5 | 2815 | 0.994 | 0.991 | 0.998 | True |
| deepseek_v4 | gpt4o | 456 | 286 | 5 | 2280 | 0.995 | 0.991 | 0.998 | True |
| gpt4o | claude46 | 760 | 463 | 5 | 3800 | 0.989 | 0.983 | 0.994 | True |
| gpt4o | deepseek_v4 | 456 | 286 | 5 | 2280 | 0.989 | 0.982 | 0.996 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.213 | 0.097 | 8 | nan | 0.830 | nan | 0.188 | 0.028 |
| qwen3-4b-e2c-paired.claude46_C_s1 | 1.000 | 0.109 | 300 | 0.846 | 0.822 | 0.128 | 0.088 | 0.043 |
| qwen3-4b-e2c-paired.claude46_C_s2 | 1.000 | 0.103 | 300 | 0.856 | 0.835 | 0.124 | 0.085 | 0.041 |
| qwen3-4b-e2c-paired.claude46_C_s3 | 1.000 | 0.107 | 299 | 0.840 | 0.837 | 0.132 | 0.071 | 0.033 |
| qwen3-4b-e2c-paired.claude46_C_s4 | 1.000 | 0.109 | 300 | 0.845 | 0.836 | 0.130 | 0.090 | 0.034 |
| qwen3-4b-e2c-paired.claude46_C_s5 | 1.000 | 0.104 | 300 | 0.853 | 0.838 | 0.129 | 0.073 | 0.034 |
| qwen3-4b-e2c-paired.claude46_F_s1 | 1.000 | 0.109 | 300 | 0.853 | 0.835 | 0.128 | 0.093 | 0.043 |
| qwen3-4b-e2c-paired.claude46_F_s2 | 1.000 | 0.117 | 300 | 0.847 | 0.836 | 0.128 | 0.100 | 0.041 |
| qwen3-4b-e2c-paired.claude46_F_s3 | 1.000 | 0.108 | 300 | 0.840 | 0.827 | 0.133 | 0.088 | 0.044 |
| qwen3-4b-e2c-paired.claude46_F_s4 | 0.999 | 0.107 | 299 | 0.846 | 0.828 | 0.131 | 0.094 | 0.044 |
| qwen3-4b-e2c-paired.claude46_F_s5 | 1.000 | 0.105 | 300 | 0.854 | 0.840 | 0.130 | 0.084 | 0.041 |
| qwen3-4b-e2c-paired.claude46_O_s1 | 1.000 | 0.110 | 300 | 0.857 | 0.837 | 0.125 | 0.101 | 0.051 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 1.000 | 0.107 | 300 | 0.863 | 0.833 | 0.121 | 0.096 | 0.048 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 1.000 | 0.109 | 300 | 0.853 | 0.835 | 0.127 | 0.088 | 0.041 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 1.000 | 0.106 | 300 | 0.856 | 0.828 | 0.123 | 0.092 | 0.043 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 1.000 | 0.116 | 300 | 0.838 | 0.821 | 0.132 | 0.096 | 0.050 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 1.000 | 0.118 | 300 | 0.760 | 0.721 | 0.159 | 0.289 | 0.208 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 1.000 | 0.112 | 300 | 0.782 | 0.745 | 0.141 | 0.267 | 0.183 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 1.000 | 0.092 | 300 | 0.778 | 0.746 | 0.144 | 0.259 | 0.183 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 1.000 | 0.100 | 300 | 0.784 | 0.752 | 0.149 | 0.267 | 0.204 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 1.000 | 0.101 | 300 | 0.796 | 0.766 | 0.132 | 0.227 | 0.156 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 1.000 | 0.112 | 300 | 0.791 | 0.752 | 0.143 | 0.289 | 0.207 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 1.000 | 0.103 | 300 | 0.780 | 0.751 | 0.148 | 0.282 | 0.207 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 1.000 | 0.090 | 299 | 0.785 | 0.749 | 0.138 | 0.247 | 0.174 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 1.000 | 0.119 | 300 | 0.781 | 0.745 | 0.144 | 0.252 | 0.186 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 1.000 | 0.095 | 300 | 0.776 | 0.743 | 0.147 | 0.254 | 0.189 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 1.000 | 0.111 | 300 | 0.771 | 0.739 | 0.146 | 0.286 | 0.187 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 1.000 | 0.116 | 300 | 0.789 | 0.759 | 0.136 | 0.258 | 0.184 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 1.000 | 0.104 | 300 | 0.782 | 0.749 | 0.145 | 0.282 | 0.198 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 1.000 | 0.124 | 300 | 0.784 | 0.752 | 0.143 | 0.272 | 0.198 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 1.000 | 0.098 | 300 | 0.776 | 0.749 | 0.144 | 0.274 | 0.194 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 1.000 | 0.113 | 300 | 0.803 | 0.805 | 0.146 | 0.163 | 0.092 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 1.000 | 0.104 | 300 | 0.798 | 0.807 | 0.154 | 0.177 | 0.117 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 1.000 | 0.106 | 300 | 0.800 | 0.810 | 0.151 | 0.177 | 0.111 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 1.000 | 0.107 | 300 | 0.803 | 0.808 | 0.145 | 0.168 | 0.103 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 1.000 | 0.105 | 300 | 0.803 | 0.810 | 0.148 | 0.176 | 0.109 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 1.000 | 0.098 | 300 | 0.816 | 0.802 | 0.145 | 0.147 | 0.092 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 1.000 | 0.097 | 300 | 0.812 | 0.806 | 0.142 | 0.181 | 0.107 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 1.000 | 0.096 | 300 | 0.811 | 0.806 | 0.145 | 0.167 | 0.111 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 1.000 | 0.103 | 300 | 0.813 | 0.810 | 0.145 | 0.183 | 0.112 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 1.000 | 0.105 | 300 | 0.807 | 0.799 | 0.147 | 0.187 | 0.120 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 1.000 | 0.090 | 300 | 0.807 | 0.802 | 0.142 | 0.129 | 0.084 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 1.000 | 0.095 | 300 | 0.804 | 0.806 | 0.148 | 0.139 | 0.094 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 1.000 | 0.098 | 300 | 0.812 | 0.809 | 0.139 | 0.148 | 0.095 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 1.000 | 0.098 | 300 | 0.814 | 0.804 | 0.142 | 0.174 | 0.109 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 1.000 | 0.104 | 300 | 0.807 | 0.812 | 0.145 | 0.144 | 0.095 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.776 | 0.830 | 0.782 | 0.185 | 0.098 | 0.163 |
| qwen3-4b-e2c-paired.claude46_C_s1 | 0.846 | 0.822 | 0.813 | 0.128 | 0.108 | 0.133 |
| qwen3-4b-e2c-paired.claude46_C_s2 | 0.856 | 0.828 | 0.835 | 0.124 | 0.108 | 0.128 |
| qwen3-4b-e2c-paired.claude46_C_s3 | 0.840 | 0.837 | 0.818 | 0.132 | 0.109 | 0.132 |
| qwen3-4b-e2c-paired.claude46_C_s4 | 0.845 | 0.836 | 0.824 | 0.130 | 0.105 | 0.132 |
| qwen3-4b-e2c-paired.claude46_C_s5 | 0.853 | 0.838 | 0.827 | 0.129 | 0.107 | 0.130 |
| qwen3-4b-e2c-paired.claude46_F_s1 | 0.853 | 0.835 | 0.827 | 0.128 | 0.109 | 0.135 |
| qwen3-4b-e2c-paired.claude46_F_s2 | 0.847 | 0.836 | 0.819 | 0.128 | 0.109 | 0.136 |
| qwen3-4b-e2c-paired.claude46_F_s3 | 0.840 | 0.827 | 0.810 | 0.133 | 0.116 | 0.145 |
| qwen3-4b-e2c-paired.claude46_F_s4 | 0.846 | 0.828 | 0.817 | 0.131 | 0.110 | 0.135 |
| qwen3-4b-e2c-paired.claude46_F_s5 | 0.854 | 0.840 | 0.827 | 0.130 | 0.110 | 0.137 |
| qwen3-4b-e2c-paired.claude46_O_s1 | 0.857 | 0.837 | 0.822 | 0.125 | 0.110 | 0.140 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 0.863 | 0.833 | 0.829 | 0.121 | 0.107 | 0.133 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 0.853 | 0.835 | 0.827 | 0.127 | 0.106 | 0.135 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 0.856 | 0.828 | 0.819 | 0.123 | 0.102 | 0.130 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 0.838 | 0.821 | 0.806 | 0.132 | 0.113 | 0.141 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 0.704 | 0.760 | 0.721 | 0.247 | 0.159 | 0.221 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 0.735 | 0.782 | 0.745 | 0.219 | 0.141 | 0.201 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 0.730 | 0.778 | 0.746 | 0.230 | 0.144 | 0.205 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 0.735 | 0.784 | 0.752 | 0.230 | 0.149 | 0.209 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 0.749 | 0.796 | 0.766 | 0.216 | 0.132 | 0.193 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 0.744 | 0.791 | 0.752 | 0.227 | 0.143 | 0.210 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 0.730 | 0.780 | 0.751 | 0.235 | 0.148 | 0.210 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 0.735 | 0.785 | 0.749 | 0.221 | 0.138 | 0.201 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 0.730 | 0.781 | 0.745 | 0.229 | 0.144 | 0.207 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 0.724 | 0.776 | 0.743 | 0.236 | 0.147 | 0.210 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 0.731 | 0.771 | 0.739 | 0.229 | 0.146 | 0.213 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 0.743 | 0.789 | 0.759 | 0.216 | 0.136 | 0.195 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 0.734 | 0.782 | 0.749 | 0.230 | 0.145 | 0.210 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 0.739 | 0.784 | 0.752 | 0.228 | 0.143 | 0.204 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 0.733 | 0.776 | 0.749 | 0.229 | 0.144 | 0.205 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 0.786 | 0.805 | 0.803 | 0.179 | 0.118 | 0.146 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 0.790 | 0.807 | 0.798 | 0.182 | 0.121 | 0.154 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 0.784 | 0.810 | 0.800 | 0.181 | 0.121 | 0.151 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 0.792 | 0.808 | 0.803 | 0.178 | 0.119 | 0.145 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 0.795 | 0.810 | 0.803 | 0.179 | 0.122 | 0.148 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 0.793 | 0.802 | 0.816 | 0.184 | 0.128 | 0.145 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 0.798 | 0.806 | 0.812 | 0.173 | 0.119 | 0.142 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 0.790 | 0.806 | 0.811 | 0.181 | 0.123 | 0.145 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 0.796 | 0.810 | 0.813 | 0.178 | 0.124 | 0.145 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 0.787 | 0.799 | 0.807 | 0.182 | 0.123 | 0.147 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 0.792 | 0.802 | 0.807 | 0.177 | 0.121 | 0.142 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 0.794 | 0.806 | 0.804 | 0.180 | 0.124 | 0.148 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 0.793 | 0.809 | 0.812 | 0.177 | 0.118 | 0.139 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 0.793 | 0.804 | 0.814 | 0.177 | 0.122 | 0.142 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 0.791 | 0.812 | 0.807 | 0.178 | 0.119 | 0.145 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.213 | nan | 0.830 | nan | 0.188 | 0.028 |
| claude46 | C | 5 | 1.000 | 0.848 | 0.834 | 0.129 | 0.081 | 0.037 |
| claude46 | F | 5 | 1.000 | 0.848 | 0.833 | 0.130 | 0.092 | 0.043 |
| claude46 | O | 5 | 1.000 | 0.853 | 0.831 | 0.125 | 0.095 | 0.047 |
| deepseek_v4 | C | 5 | 1.000 | 0.780 | 0.746 | 0.145 | 0.262 | 0.187 |
| deepseek_v4 | F | 5 | 1.000 | 0.782 | 0.748 | 0.144 | 0.265 | 0.192 |
| deepseek_v4 | O | 5 | 1.000 | 0.780 | 0.750 | 0.143 | 0.274 | 0.192 |
| gpt4o | C | 5 | 1.000 | 0.802 | 0.808 | 0.149 | 0.172 | 0.106 |
| gpt4o | F | 5 | 1.000 | 0.812 | 0.805 | 0.145 | 0.173 | 0.108 |
| gpt4o | O | 5 | 1.000 | 0.809 | 0.807 | 0.143 | 0.147 | 0.095 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_s1 | 290.000 | 0.308 | 0.058 | 0.704 | 0.125 | deepseek_v4 | -0.067 | 0.722 | -0.044 | -0.192 | 0.008 | 0.058 | 0.125 | 0.123 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 290.000 | 0.246 | 0.072 | 0.704 | 0.140 | deepseek_v4 | -0.068 | 0.771 | -0.038 | -0.203 | 0.013 | 0.072 | 0.140 | 0.120 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 290.000 | 0.310 | 0.093 | 0.704 | 0.167 | deepseek_v4 | -0.074 | 0.811 | -0.039 | -0.213 | 0.004 | 0.093 | 0.167 | 0.166 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 290.000 | 0.292 | 0.060 | 0.704 | 0.122 | gpt4o | -0.062 | 0.748 | -0.036 | -0.193 | 0.010 | 0.060 | 0.118 | 0.122 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 290.000 | 0.300 | 0.087 | 0.704 | 0.106 | deepseek_v4 | -0.018 | 0.301 | -0.040 | -0.118 | 0.068 | 0.087 | 0.106 | 0.051 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 290.000 | 0.697 | 0.316 | 0.797 | 0.109 | claude46 | 0.207 | 1.0e-04 | 0.079 | 0.109 | 0.283 | 0.109 | 0.316 | 0.082 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 290.000 | 0.695 | 0.332 | 0.797 | 0.115 | gpt4o | 0.217 | 1.0e-04 | 0.079 | 0.116 | 0.287 | 0.104 | 0.332 | 0.115 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 290.000 | 0.686 | 0.329 | 0.797 | 0.094 | gpt4o | 0.235 | 1.0e-04 | 0.082 | 0.137 | 0.308 | 0.079 | 0.329 | 0.094 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 290.000 | 0.692 | 0.316 | 0.797 | 0.095 | gpt4o | 0.221 | 1.0e-04 | 0.084 | 0.122 | 0.298 | 0.072 | 0.316 | 0.095 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 290.000 | 0.703 | 0.318 | 0.797 | 0.109 | gpt4o | 0.209 | 2.0e-04 | 0.078 | 0.103 | 0.278 | 0.102 | 0.318 | 0.109 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 290.000 | 0.529 | 0.167 | 0.904 | 0.282 | deepseek_v4 | -0.116 | 0.888 | -0.066 | -0.221 | -0.010 | 0.139 | 0.282 | 0.167 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 290.000 | 0.541 | 0.200 | 0.904 | 0.298 | deepseek_v4 | -0.098 | 0.734 | -0.073 | -0.216 | 0.012 | 0.165 | 0.298 | 0.200 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 290.000 | 0.543 | 0.150 | 0.904 | 0.267 | deepseek_v4 | -0.117 | 0.857 | -0.075 | -0.234 | -0.001 | 0.131 | 0.267 | 0.150 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 290.000 | 0.570 | 0.203 | 0.904 | 0.280 | deepseek_v4 | -0.077 | 0.492 | -0.077 | -0.168 | 0.015 | 0.138 | 0.280 | 0.203 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 290.000 | 0.527 | 0.171 | 0.904 | 0.307 | deepseek_v4 | -0.136 | 0.936 | -0.075 | -0.249 | -0.020 | 0.146 | 0.307 | 0.171 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.058 | 0.022 | 5 |
| deepseek_v4 | 0.218 | 0.011 | 5 |
| gpt4o | -0.109 | 0.022 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.017 | 0.333 | 2 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | 0.053 | 0.704 | 0.218 | deepseek_v4 | -0.164 | 0.962 | -0.257 | -0.088 |
| qwen3-4b-e2c-paired.claude46_C_s2 | 0.045 | 0.704 | 0.162 | deepseek_v4 | -0.117 | 0.947 | -0.212 | -0.035 |
| qwen3-4b-e2c-paired.claude46_C_s3 | 0.048 | 0.704 | 0.223 | deepseek_v4 | -0.175 | 0.991 | -0.271 | -0.095 |
| qwen3-4b-e2c-paired.claude46_C_s4 | 0.094 | 0.704 | 0.239 | deepseek_v4 | -0.146 | 0.975 | -0.247 | -0.054 |
| qwen3-4b-e2c-paired.claude46_C_s5 | 0.037 | 0.704 | 0.187 | deepseek_v4 | -0.149 | 0.977 | -0.252 | -0.070 |
| qwen3-4b-e2c-paired.claude46_F_s1 | 0.088 | 0.704 | 0.216 | deepseek_v4 | -0.128 | 0.899 | -0.220 | -0.050 |
| qwen3-4b-e2c-paired.claude46_F_s2 | 0.106 | 0.704 | 0.248 | deepseek_v4 | -0.141 | 0.953 | -0.258 | -0.035 |
| qwen3-4b-e2c-paired.claude46_F_s3 | 0.107 | 0.704 | 0.229 | deepseek_v4 | -0.122 | 0.893 | -0.229 | -0.031 |
| qwen3-4b-e2c-paired.claude46_F_s4 | 0.091 | 0.704 | 0.218 | gpt4o | -0.127 | 0.895 | -0.254 | -0.044 |
| qwen3-4b-e2c-paired.claude46_F_s5 | 0.047 | 0.704 | 0.239 | deepseek_v4 | -0.192 | 0.997 | -0.294 | -0.098 |
| qwen3-4b-e2c-paired.claude46_O_s1 | 0.091 | 0.704 | 0.227 | deepseek_v4 | -0.136 | 0.919 | -0.241 | -0.051 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 0.098 | 0.704 | 0.219 | deepseek_v4 | -0.120 | 0.890 | -0.236 | -0.038 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 0.124 | 0.704 | 0.265 | deepseek_v4 | -0.141 | 0.951 | -0.257 | -0.056 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 0.092 | 0.704 | 0.215 | deepseek_v4 | -0.123 | 0.926 | -0.239 | -0.047 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 0.118 | 0.704 | 0.207 | deepseek_v4 | -0.089 | 0.640 | -0.187 | -7.0e-05 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 0.456 | 0.797 | 0.230 | gpt4o | 0.226 | 7.0e-04 | 0.154 | 0.300 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 0.463 | 0.797 | 0.255 | gpt4o | 0.208 | 0.002 | 0.133 | 0.285 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 0.459 | 0.797 | 0.272 | gpt4o | 0.187 | 0.009 | 0.110 | 0.266 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 0.444 | 0.797 | 0.257 | gpt4o | 0.187 | 0.015 | 0.110 | 0.267 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 0.454 | 0.797 | 0.241 | gpt4o | 0.213 | 4.0e-04 | 0.133 | 0.298 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 0.485 | 0.797 | 0.267 | gpt4o | 0.219 | 9.0e-04 | 0.145 | 0.295 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 0.475 | 0.797 | 0.256 | gpt4o | 0.219 | 0.001 | 0.145 | 0.295 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 0.468 | 0.797 | 0.240 | gpt4o | 0.228 | 3.0e-04 | 0.151 | 0.305 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 0.473 | 0.797 | 0.250 | gpt4o | 0.223 | 6.0e-04 | 0.143 | 0.302 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 0.466 | 0.797 | 0.254 | gpt4o | 0.212 | 1.0e-03 | 0.138 | 0.288 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 0.475 | 0.797 | 0.251 | gpt4o | 0.223 | 4.0e-04 | 0.152 | 0.294 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 0.485 | 0.797 | 0.274 | gpt4o | 0.210 | 0.001 | 0.137 | 0.286 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 0.482 | 0.797 | 0.258 | gpt4o | 0.224 | 4.0e-04 | 0.148 | 0.301 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 0.474 | 0.797 | 0.260 | gpt4o | 0.214 | 1.0e-03 | 0.139 | 0.291 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 0.476 | 0.797 | 0.272 | gpt4o | 0.205 | 0.002 | 0.128 | 0.280 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 0.314 | 0.904 | 0.448 | deepseek_v4 | -0.135 | 0.838 | -0.213 | -0.059 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 0.312 | 0.904 | 0.464 | deepseek_v4 | -0.152 | 0.931 | -0.250 | -0.062 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 0.299 | 0.904 | 0.452 | deepseek_v4 | -0.153 | 0.932 | -0.243 | -0.067 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 0.321 | 0.904 | 0.457 | deepseek_v4 | -0.136 | 0.847 | -0.234 | -0.046 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 0.334 | 0.904 | 0.458 | deepseek_v4 | -0.124 | 0.745 | -0.220 | -0.032 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 0.299 | 0.904 | 0.393 | deepseek_v4 | -0.094 | 0.506 | -0.185 | -0.008 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 0.323 | 0.904 | 0.440 | deepseek_v4 | -0.118 | 0.678 | -0.211 | -0.029 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 0.315 | 0.904 | 0.429 | deepseek_v4 | -0.113 | 0.667 | -0.202 | -0.030 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 0.313 | 0.904 | 0.441 | deepseek_v4 | -0.128 | 0.798 | -0.213 | -0.049 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 0.311 | 0.904 | 0.456 | deepseek_v4 | -0.145 | 0.900 | -0.241 | -0.053 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 0.284 | 0.904 | 0.422 | deepseek_v4 | -0.138 | 0.917 | -0.226 | -0.052 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 0.313 | 0.904 | 0.437 | deepseek_v4 | -0.124 | 0.790 | -0.223 | -0.032 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 0.273 | 0.904 | 0.414 | deepseek_v4 | -0.141 | 0.894 | -0.238 | -0.042 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 0.320 | 0.904 | 0.429 | deepseek_v4 | -0.110 | 0.606 | -0.191 | -0.031 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 0.287 | 0.904 | 0.441 | deepseek_v4 | -0.154 | 0.944 | -0.247 | -0.062 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.164 | 0.080 | 5 |
| claude46 | T1 | -0.120 | 0.024 | 5 |
| claude46 | T3 | -0.075 | 0.033 | 5 |
| claude46 | T5 | -0.030 | 0.049 | 5 |
| claude46 | T6 | -0.080 | 0.059 | 5 |
| deepseek_v4 | T0 | 0.113 | 0.070 | 5 |
| deepseek_v4 | T1 | 0.096 | 0.034 | 5 |
| deepseek_v4 | T3 | 0.111 | 0.045 | 5 |
| deepseek_v4 | T5 | 0.058 | 0.036 | 5 |
| deepseek_v4 | T6 | 0.247 | 0.021 | 5 |
| gpt4o | T0 | -0.173 | 0.026 | 5 |
| gpt4o | T1 | -0.080 | 0.023 | 5 |
| gpt4o | T3 | -0.062 | 0.074 | 5 |
| gpt4o | T5 | -0.094 | 0.044 | 5 |
| gpt4o | T6 | -0.097 | 0.028 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.327 | 0.084 | 0.704 | 0.149 | deepseek_v4 | -0.065 | -0.184 | 0.012 | 0.715 | -0.043 | 1.000 |
| deepseek_v4 | 5 | 290 | 0.716 | 0.342 | 0.797 | 0.105 | gpt4o | 0.237 | 0.135 | 0.304 | 1.0e-04 | 0.084 | 3.0e-04 |
| gpt4o | 5 | 290 | 0.573 | 0.193 | 0.904 | 0.310 | deepseek_v4 | -0.117 | -0.228 | -0.009 | 0.841 | -0.078 | 1.000 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 290 | 0.118 | 0.704 | 0.035 | 0.198 | 3 | -0.262 | -0.357 | -0.172 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 290 | 0.380 | 0.797 | 0.327 | 0.434 | 1 | 0.100 | 0.036 | 0.167 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 290 | 0.280 | 0.904 | 0.213 | 0.344 | 2 | -0.100 | -0.167 | -0.036 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 5/5 seeds pass -> ok (old rule, not the verdict)
- deepseek_v4: 5/5 seeds pass -> ok (old rule, not the verdict)
- gpt4o: 3/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 0.017 vs run-reassignment null mean -0.049 sd 0.021, p 2.1e-04 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.333
- P2 slope 5.268, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.048 [0.004, 0.092] p 0.022 alone would read pass; the frozen rule (version 5) also needs D_specific 0.070 [0.022, 0.120] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | C | 10 | 0.008 | 0.005 | 0.014 |
| agree_own | claude46 | F | 10 | 0.007 | 0.004 | 0.014 |
| agree_own | claude46 | O | 10 | 0.011 | 0.008 | 0.023 |
| agree_own | deepseek_v4 | C | 10 | 0.015 | 0.010 | 0.031 |
| agree_own | deepseek_v4 | F | 10 | 0.007 | 0.004 | 0.013 |
| agree_own | deepseek_v4 | O | 10 | 0.009 | 0.005 | 0.016 |
| agree_own | gpt4o | C | 10 | 0.003 | 0.002 | 0.005 |
| agree_own | gpt4o | F | 10 | 0.004 | 0.002 | 0.007 |
| agree_own | gpt4o | O | 10 | 0.005 | 0.003 | 0.009 |
| agree_own | all | all | 90 | 0.008 | 0.006 | 0.019 |
| jsd_own | claude46 | C | 10 | 0.003 | 0.002 | 0.007 |
| jsd_own | claude46 | F | 10 | 0.003 | 0.002 | 0.005 |
| jsd_own | claude46 | O | 10 | 0.005 | 0.003 | 0.010 |
| jsd_own | deepseek_v4 | C | 10 | 0.012 | 0.007 | 0.023 |
| jsd_own | deepseek_v4 | F | 10 | 0.005 | 0.003 | 0.010 |
| jsd_own | deepseek_v4 | O | 10 | 0.004 | 0.004 | 0.009 |
| jsd_own | gpt4o | C | 10 | 0.004 | 0.003 | 0.008 |
| jsd_own | gpt4o | F | 10 | 0.002 | 0.001 | 0.004 |
| jsd_own | gpt4o | O | 10 | 0.004 | 0.003 | 0.008 |
| jsd_own | all | all | 90 | 0.005 | 0.004 | 0.011 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | C | 10 | 0.011 | 0.007 | 0.018 |
| flip_rate | claude46 | F | 10 | 0.008 | 0.004 | 0.014 |
| flip_rate | claude46 | O | 10 | 0.006 | 0.003 | 0.010 |
| flip_rate | deepseek_v4 | C | 10 | 0.027 | 0.019 | 0.053 |
| flip_rate | deepseek_v4 | F | 10 | 0.022 | 0.015 | 0.039 |
| flip_rate | deepseek_v4 | O | 10 | 0.013 | 0.008 | 0.026 |
| flip_rate | gpt4o | C | 10 | 0.007 | 0.005 | 0.014 |
| flip_rate | gpt4o | F | 10 | 0.019 | 0.014 | 0.038 |
| flip_rate | gpt4o | O | 10 | 0.020 | 0.014 | 0.041 |
| flip_rate | all | all | 90 | 0.015 | 0.013 | 0.040 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | C | 10 | 0.006 | 0.004 | 0.010 |
| mean_jsd | claude46 | F | 10 | 0.002 | 0.001 | 0.004 |
| mean_jsd | claude46 | O | 10 | 0.005 | 0.003 | 0.009 |
| mean_jsd | deepseek_v4 | C | 10 | 0.025 | 0.016 | 0.050 |
| mean_jsd | deepseek_v4 | F | 10 | 0.017 | 0.011 | 0.033 |
| mean_jsd | deepseek_v4 | O | 10 | 0.008 | 0.005 | 0.014 |
| mean_jsd | gpt4o | C | 10 | 0.011 | 0.007 | 0.021 |
| mean_jsd | gpt4o | F | 10 | 0.012 | 0.009 | 0.025 |
| mean_jsd | gpt4o | O | 10 | 0.010 | 0.008 | 0.020 |
| mean_jsd | all | all | 90 | 0.011 | 0.010 | 0.028 |
| delta_rho | claude46 | C | 10 | 0.027 | 0.016 | 0.053 |
| delta_rho | claude46 | F | 10 | 0.031 | 0.028 | 0.068 |
| delta_rho | claude46 | O | 10 | 0.024 | 0.017 | 0.049 |
| delta_rho | deepseek_v4 | C | 10 | 0.021 | 0.013 | 0.039 |
| delta_rho | deepseek_v4 | F | 10 | 0.007 | 0.004 | 0.014 |
| delta_rho | deepseek_v4 | O | 10 | 0.010 | 0.006 | 0.019 |
| delta_rho | gpt4o | C | 10 | 0.015 | 0.009 | 0.029 |
| delta_rho | gpt4o | F | 10 | 0.024 | 0.014 | 0.044 |
| delta_rho | gpt4o | O | 10 | 0.021 | 0.012 | 0.039 |
| delta_rho | all | all | 90 | 0.020 | 0.016 | 0.051 |
| delta_rho_partial | claude46 | C | 10 | 0.021 | 0.012 | 0.039 |
| delta_rho_partial | claude46 | F | 10 | 0.038 | 0.027 | 0.079 |
| delta_rho_partial | claude46 | O | 10 | 0.023 | 0.023 | 0.053 |
| delta_rho_partial | deepseek_v4 | C | 10 | 0.028 | 0.018 | 0.056 |
| delta_rho_partial | deepseek_v4 | F | 10 | 0.008 | 0.004 | 0.015 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.013 | 0.008 | 0.027 |
| delta_rho_partial | gpt4o | C | 10 | 0.019 | 0.012 | 0.036 |
| delta_rho_partial | gpt4o | F | 10 | 0.030 | 0.018 | 0.057 |
| delta_rho_partial | gpt4o | O | 10 | 0.027 | 0.016 | 0.050 |
| delta_rho_partial | all | all | 90 | 0.023 | 0.018 | 0.056 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.