# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.990, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.977 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.231 [-0.382, -0.085] p_perm 0.980 (null mean -0.114) p_holm 0.980; deepseek_v4 0.191 [0.090, 0.297] p_perm 0.074 (null mean 0.133) p_holm 0.223; gpt4o -0.080 [-0.203, 0.036] p_perm 0.244 (null mean -0.113) p_holm 0.488; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.059 [-0.014, 0.126], p 0.034; D_specific 0.091 [0.006, 0.175], D_shared -0.032 (139 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.012 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.065, sd 0.016, p 1.1e-04, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 3.168 (pearson 0.912, seed-noise sd 0.018, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.144 [-0.309, -0.012] p_holm 0.889; deepseek_v4 0.046 [-0.090, 0.189] p_holm 0.887; gpt4o 0.057 [-0.066, 0.178] p_holm 0.126 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.020 [-0.090, 0.056], p 0.660 (138 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.058 [0.002, 0.109], p 0.047 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.081 [0.005, 0.151] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.108 | 0.744 | 0.145 | 0.339 | deepseek_v4 | -0.231 | -0.382 | -0.085 | 0.980 | -0.114 | 0.058 | 0.980 | False |
| deepseek_v4 | 5 | 139 | 0.517 | 0.825 | 0.627 | 0.326 | gpt4o | 0.191 | 0.090 | 0.297 | 0.074 | 0.133 | 0.041 | 0.223 | False |
| gpt4o | 5 | 139 | 0.413 | 0.898 | 0.460 | 0.494 | deepseek_v4 | -0.080 | -0.203 | 0.036 | 0.244 | -0.113 | 0.046 | 0.488 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.033 | -0.091 | 0.013 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.059 | -0.014 | 0.126 | 0.034 | 0.008 | 0.028 | 0.058 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.032 | 0.091 | 0.006 | 0.175 | 0.005 | 0.013 | 0.030 | 0.081 | 0.005 | 0.151 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2c-paired.claude46_O_pooled 0.105, qwen3-4b-e2c-paired.deepseek_v4_O_pooled 0.174, qwen3-4b-e2c-paired.gpt4o_O_pooled 0.156.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | 0.006 | 0.150 | 0.090 | 0.744 | -0.114 | 0.148 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.033 | 0.238 | 0.192 | 0.825 | 0.125 | 0.039 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.046 | 0.265 | 0.322 | 0.898 | 0.167 | 0.087 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | -0.037 | -0.164 | -0.206 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.007 | 0.050 | 0.014 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.017 | 0.055 | 0.123 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | 0.108 | 0.339 | 0.195 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.194 | 0.517 | 0.326 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.179 | 0.494 | 0.413 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_pooled | 0.046 | 0.186 | 0.097 |
| qwen3-4b-e2c-paired.deepseek_v4_O_pooled | 0.128 | 0.065 | -0.047 |
| qwen3-4b-e2c-paired.gpt4o_O_pooled | 0.078 | 0.148 | 0.124 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.123 | 0.090 | 0.159 |
| students:deepseek_v4 | 5 | 139 | 0.456 | 0.395 | 0.516 |
| students:gpt4o | 5 | 139 | 0.305 | 0.247 | 0.365 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.165 | 0.144 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.333 | -0.392 | -0.273 |
| students:claude46 | students:gpt4o | -0.182 | -0.234 | -0.131 |
| students:claude46 | teacher:claude46 | 0.064 | 0.014 | 0.115 |
| students:claude46 | base_prior | -0.041 | -0.074 | -0.008 |
| students:deepseek_v4 | students:gpt4o | 0.151 | 0.090 | 0.211 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.306 | 0.247 | 0.365 |
| students:deepseek_v4 | base_prior | 0.291 | 0.239 | 0.343 |
| students:gpt4o | teacher:gpt4o | 0.230 | 0.179 | 0.283 |
| students:gpt4o | base_prior | 0.140 | 0.088 | 0.194 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | run | 0.039 | -0.058 | 0.097 | 139 |
| qwen3-4b-e2c-paired.claude46_C_s2 | run | 0.040 | -0.030 | 0.070 | 139 |
| qwen3-4b-e2c-paired.claude46_C_s3 | run | 0.033 | -0.040 | 0.073 | 138 |
| qwen3-4b-e2c-paired.claude46_C_s4 | run | 0.032 | -0.048 | 0.079 | 139 |
| qwen3-4b-e2c-paired.claude46_C_s5 | run | 0.045 | -0.035 | 0.079 | 139 |
| qwen3-4b-e2c-paired.claude46_F_s1 | run | 0.056 | -0.070 | 0.126 | 139 |
| qwen3-4b-e2c-paired.claude46_F_s2 | run | 0.057 | -0.062 | 0.118 | 139 |
| qwen3-4b-e2c-paired.claude46_F_s3 | run | 0.061 | -0.062 | 0.123 | 139 |
| qwen3-4b-e2c-paired.claude46_F_s4 | run | 0.055 | -0.067 | 0.122 | 139 |
| qwen3-4b-e2c-paired.claude46_F_s5 | run | 0.057 | -0.063 | 0.120 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | run | 0.208 | -0.297 | 0.505 | 138 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | run | 0.197 | -0.266 | 0.463 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | run | 0.194 | -0.253 | 0.447 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | run | 0.195 | -0.282 | 0.476 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | run | 0.170 | -0.240 | 0.410 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | run | 0.199 | -0.294 | 0.494 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | run | 0.209 | -0.289 | 0.498 | 137 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | run | 0.157 | -0.219 | 0.375 | 138 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | run | 0.182 | -0.276 | 0.458 | 139 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | run | 0.161 | -0.240 | 0.401 | 139 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | run | 0.115 | -0.171 | 0.287 | 139 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | run | 0.154 | -0.207 | 0.360 | 139 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | run | 0.140 | -0.189 | 0.329 | 139 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | run | 0.127 | -0.183 | 0.310 | 139 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | run | 0.133 | -0.201 | 0.334 | 139 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | run | 0.129 | -0.166 | 0.296 | 139 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | run | 0.135 | -0.187 | 0.323 | 139 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | run | 0.138 | -0.199 | 0.338 | 139 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | run | 0.131 | -0.198 | 0.329 | 139 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | run | 0.149 | -0.206 | 0.355 | 139 |
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.091 | 0.165 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.123 | 0.013 | 5 |
| deepseek_v4 | 0.149 | 0.456 | 0.024 | 5 |
| gpt4o | 0.075 | 0.305 | 0.015 | 5 |

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
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2c-paired.claude46_C_s1 | 1.000 | 0.085 | 150 | 0.844 | 0.807 | 0.134 | 0.079 | 0.037 |
| qwen3-4b-e2c-paired.claude46_C_s2 | 1.000 | 0.071 | 150 | 0.812 | 0.786 | 0.150 | 0.076 | 0.037 |
| qwen3-4b-e2c-paired.claude46_C_s3 | 0.999 | 0.079 | 149 | 0.831 | 0.784 | 0.144 | 0.075 | 0.032 |
| qwen3-4b-e2c-paired.claude46_C_s4 | 1.000 | 0.067 | 150 | 0.835 | 0.801 | 0.138 | 0.053 | 0.033 |
| qwen3-4b-e2c-paired.claude46_C_s5 | 1.000 | 0.077 | 150 | 0.821 | 0.794 | 0.138 | 0.058 | 0.033 |
| qwen3-4b-e2c-paired.claude46_F_s1 | 1.000 | 0.077 | 150 | 0.822 | 0.796 | 0.145 | 0.090 | 0.051 |
| qwen3-4b-e2c-paired.claude46_F_s2 | 1.000 | 0.073 | 150 | 0.829 | 0.801 | 0.146 | 0.102 | 0.047 |
| qwen3-4b-e2c-paired.claude46_F_s3 | 1.000 | 0.062 | 150 | 0.842 | 0.800 | 0.133 | 0.088 | 0.049 |
| qwen3-4b-e2c-paired.claude46_F_s4 | 1.000 | 0.070 | 150 | 0.828 | 0.793 | 0.143 | 0.094 | 0.050 |
| qwen3-4b-e2c-paired.claude46_F_s5 | 1.000 | 0.073 | 150 | 0.831 | 0.798 | 0.143 | 0.083 | 0.048 |
| qwen3-4b-e2c-paired.claude46_O_s1 | 1.000 | 0.090 | 150 | 0.833 | 0.801 | 0.139 | 0.091 | 0.050 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 1.000 | 0.080 | 150 | 0.842 | 0.812 | 0.140 | 0.076 | 0.047 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 1.000 | 0.073 | 150 | 0.826 | 0.793 | 0.145 | 0.083 | 0.046 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 1.000 | 0.077 | 150 | 0.829 | 0.793 | 0.146 | 0.079 | 0.048 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 1.000 | 0.098 | 150 | 0.824 | 0.800 | 0.141 | 0.101 | 0.053 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 0.999 | 0.128 | 149 | 0.749 | 0.723 | 0.143 | 0.292 | 0.198 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 1.000 | 0.120 | 150 | 0.773 | 0.728 | 0.131 | 0.253 | 0.179 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 1.000 | 0.098 | 150 | 0.761 | 0.744 | 0.141 | 0.252 | 0.177 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 1.000 | 0.103 | 150 | 0.773 | 0.739 | 0.144 | 0.258 | 0.195 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 1.000 | 0.098 | 150 | 0.788 | 0.763 | 0.123 | 0.230 | 0.155 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 1.000 | 0.113 | 150 | 0.765 | 0.739 | 0.140 | 0.296 | 0.201 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 0.999 | 0.108 | 148 | 0.781 | 0.743 | 0.141 | 0.262 | 0.196 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 0.999 | 0.094 | 149 | 0.778 | 0.740 | 0.141 | 0.223 | 0.156 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 1.000 | 0.138 | 150 | 0.765 | 0.726 | 0.136 | 0.262 | 0.177 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 1.000 | 0.093 | 150 | 0.787 | 0.740 | 0.140 | 0.231 | 0.163 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 1.000 | 0.123 | 150 | 0.778 | 0.744 | 0.136 | 0.250 | 0.178 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 1.000 | 0.132 | 150 | 0.787 | 0.756 | 0.126 | 0.233 | 0.162 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 1.000 | 0.120 | 150 | 0.776 | 0.737 | 0.142 | 0.253 | 0.181 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 1.000 | 0.145 | 150 | 0.766 | 0.726 | 0.135 | 0.256 | 0.191 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 1.000 | 0.115 | 150 | 0.780 | 0.749 | 0.137 | 0.229 | 0.175 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 1.000 | 0.090 | 150 | 0.841 | 0.833 | 0.110 | 0.151 | 0.102 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 1.000 | 0.098 | 150 | 0.801 | 0.828 | 0.128 | 0.198 | 0.130 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 1.000 | 0.090 | 150 | 0.831 | 0.824 | 0.113 | 0.201 | 0.124 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 1.000 | 0.083 | 150 | 0.836 | 0.830 | 0.113 | 0.163 | 0.107 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 1.000 | 0.084 | 150 | 0.840 | 0.840 | 0.116 | 0.174 | 0.122 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 1.000 | 0.094 | 150 | 0.847 | 0.838 | 0.111 | 0.157 | 0.103 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 1.000 | 0.084 | 150 | 0.836 | 0.829 | 0.119 | 0.173 | 0.121 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 1.000 | 0.080 | 150 | 0.836 | 0.829 | 0.116 | 0.182 | 0.122 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 1.000 | 0.085 | 150 | 0.833 | 0.822 | 0.123 | 0.178 | 0.121 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 1.000 | 0.090 | 150 | 0.822 | 0.815 | 0.123 | 0.191 | 0.129 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 1.000 | 0.074 | 150 | 0.840 | 0.827 | 0.109 | 0.157 | 0.105 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 1.000 | 0.087 | 150 | 0.840 | 0.834 | 0.112 | 0.172 | 0.106 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 1.000 | 0.079 | 150 | 0.850 | 0.847 | 0.104 | 0.154 | 0.104 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 1.000 | 0.076 | 150 | 0.831 | 0.817 | 0.122 | 0.182 | 0.119 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 1.000 | 0.094 | 150 | 0.847 | 0.832 | 0.109 | 0.173 | 0.105 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2c-paired.claude46_C_s1 | 0.844 | 0.776 | 0.807 | 0.134 | 0.150 | 0.148 |
| qwen3-4b-e2c-paired.claude46_C_s2 | 0.812 | 0.755 | 0.786 | 0.150 | 0.152 | 0.150 |
| qwen3-4b-e2c-paired.claude46_C_s3 | 0.831 | 0.760 | 0.784 | 0.144 | 0.155 | 0.156 |
| qwen3-4b-e2c-paired.claude46_C_s4 | 0.835 | 0.782 | 0.801 | 0.138 | 0.148 | 0.144 |
| qwen3-4b-e2c-paired.claude46_C_s5 | 0.821 | 0.768 | 0.794 | 0.138 | 0.150 | 0.142 |
| qwen3-4b-e2c-paired.claude46_F_s1 | 0.822 | 0.773 | 0.796 | 0.145 | 0.156 | 0.154 |
| qwen3-4b-e2c-paired.claude46_F_s2 | 0.829 | 0.775 | 0.801 | 0.146 | 0.152 | 0.149 |
| qwen3-4b-e2c-paired.claude46_F_s3 | 0.842 | 0.780 | 0.800 | 0.133 | 0.149 | 0.148 |
| qwen3-4b-e2c-paired.claude46_F_s4 | 0.828 | 0.770 | 0.793 | 0.143 | 0.152 | 0.150 |
| qwen3-4b-e2c-paired.claude46_F_s5 | 0.831 | 0.770 | 0.798 | 0.143 | 0.155 | 0.149 |
| qwen3-4b-e2c-paired.claude46_O_s1 | 0.833 | 0.778 | 0.801 | 0.139 | 0.144 | 0.149 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 0.842 | 0.785 | 0.812 | 0.140 | 0.142 | 0.139 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 0.826 | 0.773 | 0.793 | 0.145 | 0.147 | 0.149 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 0.829 | 0.773 | 0.793 | 0.146 | 0.145 | 0.148 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 0.824 | 0.773 | 0.800 | 0.141 | 0.143 | 0.141 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 0.709 | 0.749 | 0.723 | 0.236 | 0.143 | 0.207 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 0.728 | 0.773 | 0.728 | 0.223 | 0.131 | 0.202 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 0.721 | 0.761 | 0.744 | 0.235 | 0.141 | 0.199 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 0.723 | 0.773 | 0.739 | 0.237 | 0.144 | 0.207 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 0.753 | 0.788 | 0.763 | 0.209 | 0.123 | 0.185 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 0.734 | 0.765 | 0.739 | 0.231 | 0.140 | 0.205 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 0.721 | 0.781 | 0.743 | 0.238 | 0.141 | 0.202 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 0.725 | 0.778 | 0.740 | 0.240 | 0.141 | 0.208 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 0.707 | 0.765 | 0.726 | 0.233 | 0.136 | 0.201 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 0.718 | 0.787 | 0.740 | 0.242 | 0.140 | 0.205 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 0.725 | 0.778 | 0.744 | 0.233 | 0.136 | 0.204 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 0.735 | 0.787 | 0.756 | 0.220 | 0.126 | 0.188 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 0.714 | 0.776 | 0.737 | 0.245 | 0.142 | 0.208 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 0.703 | 0.766 | 0.726 | 0.233 | 0.135 | 0.198 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 0.723 | 0.780 | 0.749 | 0.233 | 0.137 | 0.200 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 0.833 | 0.832 | 0.841 | 0.140 | 0.106 | 0.110 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 0.828 | 0.805 | 0.801 | 0.142 | 0.110 | 0.128 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 0.817 | 0.824 | 0.831 | 0.146 | 0.108 | 0.113 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 0.824 | 0.830 | 0.836 | 0.144 | 0.106 | 0.113 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 0.840 | 0.827 | 0.840 | 0.138 | 0.111 | 0.116 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 0.838 | 0.837 | 0.847 | 0.141 | 0.106 | 0.111 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 0.829 | 0.825 | 0.836 | 0.145 | 0.106 | 0.119 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 0.819 | 0.829 | 0.836 | 0.153 | 0.109 | 0.116 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 0.819 | 0.822 | 0.833 | 0.153 | 0.109 | 0.123 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 0.806 | 0.815 | 0.822 | 0.158 | 0.113 | 0.123 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 0.821 | 0.827 | 0.840 | 0.146 | 0.107 | 0.109 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 0.821 | 0.834 | 0.840 | 0.149 | 0.101 | 0.112 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 0.828 | 0.847 | 0.850 | 0.142 | 0.097 | 0.104 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 0.817 | 0.815 | 0.831 | 0.155 | 0.113 | 0.122 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 0.819 | 0.832 | 0.847 | 0.147 | 0.105 | 0.109 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | C | 5 | 1.000 | 0.828 | 0.794 | 0.141 | 0.068 | 0.034 |
| claude46 | F | 5 | 1.000 | 0.831 | 0.798 | 0.142 | 0.092 | 0.049 |
| claude46 | O | 5 | 1.000 | 0.831 | 0.800 | 0.142 | 0.086 | 0.049 |
| deepseek_v4 | C | 5 | 1.000 | 0.769 | 0.739 | 0.136 | 0.257 | 0.181 |
| deepseek_v4 | F | 5 | 1.000 | 0.775 | 0.738 | 0.140 | 0.255 | 0.179 |
| deepseek_v4 | O | 5 | 1.000 | 0.777 | 0.743 | 0.135 | 0.244 | 0.177 |
| gpt4o | C | 5 | 1.000 | 0.830 | 0.831 | 0.116 | 0.178 | 0.117 |
| gpt4o | F | 5 | 1.000 | 0.835 | 0.827 | 0.118 | 0.176 | 0.119 |
| gpt4o | O | 5 | 1.000 | 0.841 | 0.831 | 0.111 | 0.168 | 0.108 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_O_s1 | 139.000 | 0.430 | -0.044 | 0.744 | 0.134 | deepseek_v4 | -0.178 | 0.953 | -0.069 | -0.339 | -0.069 | -0.044 | 0.134 | 0.104 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 139.000 | 0.346 | 0.039 | 0.744 | 0.180 | deepseek_v4 | -0.141 | 0.895 | -0.060 | -0.335 | 0.043 | 0.039 | 0.180 | 0.068 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 139.000 | 0.326 | 0.037 | 0.744 | 0.175 | deepseek_v4 | -0.138 | 0.891 | -0.060 | -0.295 | -3.9e-04 | 0.037 | 0.175 | 0.086 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 139.000 | 0.392 | -0.021 | 0.744 | 0.089 | deepseek_v4 | -0.110 | 0.792 | -0.060 | -0.273 | 0.015 | -0.021 | 0.089 | 0.030 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 139.000 | 0.373 | 0.011 | 0.744 | 0.101 | gpt4o | -0.090 | 0.662 | -0.063 | -0.219 | -0.008 | 0.011 | 0.079 | 0.101 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 139.000 | 0.686 | 0.182 | 0.825 | 0.158 | gpt4o | 0.024 | 0.584 | 0.034 | -0.112 | 0.160 | 0.009 | 0.182 | 0.158 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 139.000 | 0.670 | 0.293 | 0.825 | 0.177 | gpt4o | 0.116 | 0.053 | 0.034 | -0.015 | 0.246 | 0.082 | 0.293 | 0.177 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 139.000 | 0.658 | 0.176 | 0.825 | 0.180 | gpt4o | -0.003 | 0.786 | 0.036 | -0.137 | 0.128 | -0.003 | 0.176 | 0.180 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 139.000 | 0.674 | 0.246 | 0.825 | 0.175 | gpt4o | 0.071 | 0.255 | 0.038 | -0.070 | 0.211 | 0.033 | 0.246 | 0.175 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 139.000 | 0.666 | 0.202 | 0.825 | 0.195 | gpt4o | 0.007 | 0.695 | 0.033 | -0.137 | 0.152 | 0.033 | 0.202 | 0.195 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 139.000 | 0.546 | 0.293 | 0.898 | 0.221 | deepseek_v4 | 0.071 | 0.026 | -0.034 | -0.049 | 0.189 | 0.034 | 0.221 | 0.293 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 139.000 | 0.540 | 0.327 | 0.898 | 0.306 | deepseek_v4 | 0.021 | 0.150 | -0.035 | -0.108 | 0.154 | 0.041 | 0.306 | 0.327 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 139.000 | 0.581 | 0.317 | 0.898 | 0.266 | deepseek_v4 | 0.051 | 0.054 | -0.036 | -0.077 | 0.178 | 0.026 | 0.266 | 0.317 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 139.000 | 0.564 | 0.299 | 0.898 | 0.207 | deepseek_v4 | 0.092 | 0.010 | -0.034 | -0.023 | 0.201 | 0.056 | 0.207 | 0.299 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 139.000 | 0.568 | 0.278 | 0.898 | 0.247 | deepseek_v4 | 0.030 | 0.105 | -0.036 | -0.094 | 0.152 | 0.058 | 0.247 | 0.278 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.131 | 0.033 | 5 |
| deepseek_v4 | 0.043 | 0.050 | 5 |
| gpt4o | 0.053 | 0.029 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.012 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | 0.125 | 0.744 | 0.258 | deepseek_v4 | -0.133 | 0.725 | -0.310 | 0.004 |
| qwen3-4b-e2c-paired.claude46_C_s2 | 0.095 | 0.744 | 0.185 | deepseek_v4 | -0.090 | 0.643 | -0.241 | 0.043 |
| qwen3-4b-e2c-paired.claude46_C_s3 | 0.078 | 0.744 | 0.193 | deepseek_v4 | -0.115 | 0.707 | -0.259 | 0.018 |
| qwen3-4b-e2c-paired.claude46_C_s4 | 0.181 | 0.744 | 0.286 | deepseek_v4 | -0.105 | 0.618 | -0.275 | 0.037 |
| qwen3-4b-e2c-paired.claude46_C_s5 | 0.085 | 0.744 | 0.218 | deepseek_v4 | -0.134 | 0.831 | -0.259 | -0.026 |
| qwen3-4b-e2c-paired.claude46_F_s1 | 0.033 | 0.744 | 0.305 | deepseek_v4 | -0.272 | 0.998 | -0.430 | -0.117 |
| qwen3-4b-e2c-paired.claude46_F_s2 | 0.062 | 0.744 | 0.236 | deepseek_v4 | -0.174 | 0.909 | -0.326 | -0.027 |
| qwen3-4b-e2c-paired.claude46_F_s3 | 0.077 | 0.744 | 0.273 | deepseek_v4 | -0.196 | 0.961 | -0.354 | -0.029 |
| qwen3-4b-e2c-paired.claude46_F_s4 | 0.087 | 0.744 | 0.306 | deepseek_v4 | -0.220 | 0.978 | -0.378 | -0.078 |
| qwen3-4b-e2c-paired.claude46_F_s5 | 0.175 | 0.744 | 0.312 | deepseek_v4 | -0.137 | 0.748 | -0.289 | 0.006 |
| qwen3-4b-e2c-paired.claude46_O_s1 | 0.067 | 0.744 | 0.332 | deepseek_v4 | -0.265 | 0.993 | -0.408 | -0.122 |
| qwen3-4b-e2c-paired.claude46_O_s2 | 0.120 | 0.744 | 0.327 | deepseek_v4 | -0.207 | 0.966 | -0.383 | -0.029 |
| qwen3-4b-e2c-paired.claude46_O_s3 | 0.114 | 0.744 | 0.314 | deepseek_v4 | -0.200 | 0.958 | -0.348 | -0.061 |
| qwen3-4b-e2c-paired.claude46_O_s4 | 0.077 | 0.744 | 0.278 | deepseek_v4 | -0.201 | 0.962 | -0.347 | -0.060 |
| qwen3-4b-e2c-paired.claude46_O_s5 | 0.102 | 0.744 | 0.261 | deepseek_v4 | -0.159 | 0.826 | -0.285 | -0.053 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | 0.479 | 0.825 | 0.289 | gpt4o | 0.190 | 0.072 | 0.093 | 0.288 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | 0.489 | 0.825 | 0.278 | gpt4o | 0.211 | 0.021 | 0.107 | 0.315 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | 0.469 | 0.825 | 0.294 | gpt4o | 0.175 | 0.102 | 0.067 | 0.285 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | 0.468 | 0.825 | 0.290 | gpt4o | 0.178 | 0.102 | 0.072 | 0.286 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | 0.513 | 0.825 | 0.282 | gpt4o | 0.231 | 0.003 | 0.112 | 0.336 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | 0.481 | 0.825 | 0.306 | gpt4o | 0.174 | 0.128 | 0.087 | 0.265 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | 0.490 | 0.825 | 0.295 | gpt4o | 0.196 | 0.053 | 0.095 | 0.296 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | 0.466 | 0.825 | 0.282 | gpt4o | 0.184 | 0.047 | 0.069 | 0.301 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | 0.510 | 0.825 | 0.326 | gpt4o | 0.184 | 0.092 | 0.095 | 0.279 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | 0.452 | 0.825 | 0.276 | gpt4o | 0.176 | 0.085 | 0.070 | 0.284 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | 0.478 | 0.825 | 0.300 | gpt4o | 0.178 | 0.099 | 0.078 | 0.276 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | 0.541 | 0.825 | 0.312 | gpt4o | 0.229 | 0.005 | 0.119 | 0.332 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | 0.463 | 0.825 | 0.312 | gpt4o | 0.151 | 0.298 | 0.045 | 0.257 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | 0.513 | 0.825 | 0.311 | gpt4o | 0.202 | 0.043 | 0.102 | 0.303 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | 0.482 | 0.825 | 0.324 | gpt4o | 0.159 | 0.219 | 0.059 | 0.260 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | 0.396 | 0.898 | 0.461 | deepseek_v4 | -0.065 | 0.207 | -0.203 | 0.062 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | 0.382 | 0.898 | 0.521 | deepseek_v4 | -0.139 | 0.695 | -0.261 | -0.017 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | 0.374 | 0.898 | 0.462 | deepseek_v4 | -0.088 | 0.312 | -0.235 | 0.045 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | 0.428 | 0.898 | 0.473 | deepseek_v4 | -0.045 | 0.077 | -0.165 | 0.068 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | 0.388 | 0.898 | 0.490 | deepseek_v4 | -0.103 | 0.437 | -0.239 | 0.024 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | 0.372 | 0.898 | 0.446 | deepseek_v4 | -0.074 | 0.231 | -0.196 | 0.040 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | 0.366 | 0.898 | 0.500 | deepseek_v4 | -0.134 | 0.701 | -0.265 | -0.004 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | 0.367 | 0.898 | 0.461 | deepseek_v4 | -0.095 | 0.340 | -0.208 | 0.014 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | 0.343 | 0.898 | 0.491 | deepseek_v4 | -0.148 | 0.774 | -0.266 | -0.032 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | 0.380 | 0.898 | 0.494 | deepseek_v4 | -0.114 | 0.499 | -0.253 | 0.015 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | 0.387 | 0.898 | 0.448 | deepseek_v4 | -0.061 | 0.191 | -0.183 | 0.053 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | 0.414 | 0.898 | 0.506 | deepseek_v4 | -0.092 | 0.370 | -0.218 | 0.030 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | 0.409 | 0.898 | 0.493 | deepseek_v4 | -0.084 | 0.290 | -0.206 | 0.033 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | 0.394 | 0.898 | 0.445 | deepseek_v4 | -0.052 | 0.114 | -0.171 | 0.058 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | 0.377 | 0.898 | 0.475 | deepseek_v4 | -0.098 | 0.378 | -0.223 | 0.021 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.134 | 0.073 | 5 |
| claude46 | T1 | -0.061 | 0.041 | 5 |
| claude46 | T3 | -0.275 | 0.073 | 5 |
| claude46 | T5 | -0.203 | 0.093 | 5 |
| claude46 | T6 | -0.079 | 0.062 | 5 |
| deepseek_v4 | T0 | -0.056 | 0.064 | 5 |
| deepseek_v4 | T1 | 0.106 | 0.058 | 5 |
| deepseek_v4 | T3 | 0.108 | 0.060 | 5 |
| deepseek_v4 | T5 | -0.074 | 0.045 | 5 |
| deepseek_v4 | T6 | -0.002 | 0.066 | 5 |
| gpt4o | T0 | -0.021 | 0.034 | 5 |
| gpt4o | T1 | 0.027 | 0.074 | 5 |
| gpt4o | T3 | -0.154 | 0.010 | 5 |
| gpt4o | T5 | 0.211 | 0.030 | 5 |
| gpt4o | T6 | 0.063 | 0.038 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.420 | 0.006 | 0.744 | 0.150 | deepseek_v4 | -0.144 | -0.309 | -0.012 | 0.889 | -0.067 | 0.889 |
| deepseek_v4 | 5 | 139 | 0.700 | 0.238 | 0.825 | 0.192 | gpt4o | 0.046 | -0.090 | 0.189 | 0.443 | 0.038 | 0.887 |
| gpt4o | 5 | 139 | 0.584 | 0.322 | 0.898 | 0.265 | deepseek_v4 | 0.057 | -0.066 | 0.178 | 0.042 | -0.036 | 0.126 |

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

- P1 mean deltaRhoPartial -0.012 vs run-reassignment null mean -0.065 sd 0.016, p 1.1e-04 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 3.168, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.059 [-0.014, 0.126] p 0.034 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.091 [0.006, 0.175] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | C | 10 | 0.016 | 0.009 | 0.028 |
| agree_own | claude46 | F | 10 | 0.009 | 0.006 | 0.017 |
| agree_own | claude46 | O | 10 | 0.009 | 0.005 | 0.017 |
| agree_own | deepseek_v4 | C | 10 | 0.018 | 0.011 | 0.034 |
| agree_own | deepseek_v4 | F | 10 | 0.012 | 0.007 | 0.022 |
| agree_own | deepseek_v4 | O | 10 | 0.009 | 0.006 | 0.017 |
| agree_own | gpt4o | C | 10 | 0.018 | 0.016 | 0.039 |
| agree_own | gpt4o | F | 10 | 0.010 | 0.007 | 0.020 |
| agree_own | gpt4o | O | 10 | 0.009 | 0.005 | 0.018 |
| agree_own | all | all | 90 | 0.012 | 0.009 | 0.031 |
| jsd_own | claude46 | C | 10 | 0.008 | 0.005 | 0.014 |
| jsd_own | claude46 | F | 10 | 0.005 | 0.005 | 0.012 |
| jsd_own | claude46 | O | 10 | 0.003 | 0.002 | 0.006 |
| jsd_own | deepseek_v4 | C | 10 | 0.011 | 0.007 | 0.020 |
| jsd_own | deepseek_v4 | F | 10 | 0.002 | 0.002 | 0.005 |
| jsd_own | deepseek_v4 | O | 10 | 0.007 | 0.005 | 0.014 |
| jsd_own | gpt4o | C | 10 | 0.008 | 0.006 | 0.017 |
| jsd_own | gpt4o | F | 10 | 0.006 | 0.004 | 0.012 |
| jsd_own | gpt4o | O | 10 | 0.008 | 0.006 | 0.016 |
| jsd_own | all | all | 90 | 0.006 | 0.005 | 0.017 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | C | 10 | 0.014 | 0.010 | 0.024 |
| flip_rate | claude46 | F | 10 | 0.009 | 0.005 | 0.017 |
| flip_rate | claude46 | O | 10 | 0.013 | 0.007 | 0.024 |
| flip_rate | deepseek_v4 | C | 10 | 0.026 | 0.019 | 0.052 |
| flip_rate | deepseek_v4 | F | 10 | 0.035 | 0.022 | 0.069 |
| flip_rate | deepseek_v4 | O | 10 | 0.015 | 0.010 | 0.026 |
| flip_rate | gpt4o | C | 10 | 0.027 | 0.015 | 0.048 |
| flip_rate | gpt4o | F | 10 | 0.016 | 0.010 | 0.030 |
| flip_rate | gpt4o | O | 10 | 0.014 | 0.009 | 0.027 |
| flip_rate | all | all | 90 | 0.019 | 0.015 | 0.044 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | C | 10 | 0.003 | 0.002 | 0.005 |
| mean_jsd | claude46 | F | 10 | 0.002 | 0.001 | 0.003 |
| mean_jsd | claude46 | O | 10 | 0.004 | 0.002 | 0.007 |
| mean_jsd | deepseek_v4 | C | 10 | 0.021 | 0.013 | 0.041 |
| mean_jsd | deepseek_v4 | F | 10 | 0.025 | 0.014 | 0.043 |
| mean_jsd | deepseek_v4 | O | 10 | 0.013 | 0.008 | 0.025 |
| mean_jsd | gpt4o | C | 10 | 0.014 | 0.009 | 0.025 |
| mean_jsd | gpt4o | F | 10 | 0.011 | 0.009 | 0.023 |
| mean_jsd | gpt4o | O | 10 | 0.006 | 0.007 | 0.015 |
| mean_jsd | all | all | 90 | 0.011 | 0.011 | 0.037 |
| delta_rho | claude46 | C | 10 | 0.023 | 0.014 | 0.043 |
| delta_rho | claude46 | F | 10 | 0.063 | 0.035 | 0.118 |
| delta_rho | claude46 | O | 10 | 0.044 | 0.032 | 0.087 |
| delta_rho | deepseek_v4 | C | 10 | 0.029 | 0.018 | 0.055 |
| delta_rho | deepseek_v4 | F | 10 | 0.010 | 0.007 | 0.021 |
| delta_rho | deepseek_v4 | O | 10 | 0.040 | 0.023 | 0.075 |
| delta_rho | gpt4o | C | 10 | 0.045 | 0.025 | 0.085 |
| delta_rho | gpt4o | F | 10 | 0.037 | 0.020 | 0.068 |
| delta_rho | gpt4o | O | 10 | 0.025 | 0.015 | 0.043 |
| delta_rho | all | all | 90 | 0.035 | 0.026 | 0.081 |
| delta_rho_partial | claude46 | C | 10 | 0.026 | 0.015 | 0.050 |
| delta_rho_partial | claude46 | F | 10 | 0.067 | 0.043 | 0.133 |
| delta_rho_partial | claude46 | O | 10 | 0.041 | 0.024 | 0.079 |
| delta_rho_partial | deepseek_v4 | C | 10 | 0.040 | 0.025 | 0.076 |
| delta_rho_partial | deepseek_v4 | F | 10 | 0.019 | 0.012 | 0.038 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.060 | 0.038 | 0.114 |
| delta_rho_partial | gpt4o | C | 10 | 0.052 | 0.029 | 0.100 |
| delta_rho_partial | gpt4o | F | 10 | 0.051 | 0.028 | 0.089 |
| delta_rho_partial | gpt4o | O | 10 | 0.037 | 0.020 | 0.067 |
| delta_rho_partial | all | all | 90 | 0.044 | 0.030 | 0.103 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.