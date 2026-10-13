# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.994, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.968 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.124 [-0.265, 0.011] p_perm 0.734 (null mean -0.089) p_holm 0.734; deepseek_v4 0.208 [0.076, 0.334] p_perm 0.020 (null mean 0.114) p_holm 0.059; gpt4o -0.068 [-0.223, 0.084] p_perm 0.308 (null mean -0.092) p_holm 0.616; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.088 [0.011, 0.164], p 0.003; D_specific 0.110 [0.026, 0.201], D_shared -0.023 (138 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 138 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.032 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.046, sd 0.017, p 1.3e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 2.521 (pearson 0.982, seed-noise sd 0.018, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.028 [-0.189, 0.108] p_holm 0.324; deepseek_v4 0.089 [-0.055, 0.223] p_holm 0.298; gpt4o 0.043 [-0.123, 0.194] p_holm 0.271 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.013 [-0.100, 0.079], p 0.606 (137 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.086 [0.023, 0.151], p 0.003 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.098 [0.025, 0.176] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.163 | 0.744 | 0.219 | 0.288 | deepseek_v4 | -0.124 | -0.265 | 0.011 | 0.734 | -0.089 | 0.057 | 0.734 | False |
| deepseek_v4 | 5 | 138 | 0.518 | 0.825 | 0.629 | 0.311 | gpt4o | 0.208 | 0.076 | 0.334 | 0.020 | 0.114 | 0.046 | 0.059 | False |
| gpt4o | 5 | 139 | 0.376 | 0.898 | 0.418 | 0.443 | deepseek_v4 | -0.068 | -0.223 | 0.084 | 0.308 | -0.092 | 0.051 | 0.616 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| 0.009 | -0.072 | 0.017 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.088 | 0.011 | 0.164 | 0.003 | 0.008 | 0.028 | 0.086 | 138 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.023 | 0.110 | 0.026 | 0.201 | 0.001 | 0.012 | 0.031 | 0.098 | 0.025 | 0.176 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2cmix50.claude46_O_pooled 0.079, qwen3-4b-e2cmix50.deepseek_v4_O_pooled 0.152, qwen3-4b-e2cmix50.gpt4o_O_pooled 0.105.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_pooled | 0.077 | 0.099 | 0.034 | 0.744 | 0.010 | 0.171 |
| qwen3-4b-e2cmix50.deepseek_v4_O_pooled | 0.062 | 0.265 | 0.176 | 0.825 | 0.146 | 0.081 |
| qwen3-4b-e2cmix50.gpt4o_O_pooled | 0.120 | 0.240 | 0.287 | 0.898 | 0.107 | 0.079 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_pooled | -0.042 | -0.210 | -0.217 |
| qwen3-4b-e2cmix50.deepseek_v4_O_pooled | 6.1e-04 | 0.104 | 0.046 |
| qwen3-4b-e2cmix50.gpt4o_O_pooled | 0.031 | 0.007 | 0.098 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_pooled | 0.161 | 0.284 | 0.138 |
| qwen3-4b-e2cmix50.deepseek_v4_O_pooled | 0.202 | 0.518 | 0.311 |
| qwen3-4b-e2cmix50.gpt4o_O_pooled | 0.221 | 0.442 | 0.379 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_pooled | 0.179 | -0.004 | 0.165 |
| qwen3-4b-e2cmix50.deepseek_v4_O_pooled | 0.161 | 0.032 | 0.240 |
| qwen3-4b-e2cmix50.gpt4o_O_pooled | 0.116 | 0.080 | 0.130 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 138 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 138 | 0.071 | 0.047 | 0.096 |
| students:deepseek_v4 | 5 | 138 | 0.326 | 0.266 | 0.388 |
| students:gpt4o | 5 | 138 | 0.157 | 0.118 | 0.200 |
| teacher:claude46 | 1 | 138 | 0.052 | 0.017 | 0.089 |
| teacher:deepseek_v4 | 1 | 138 | 0.150 | 0.120 | 0.181 |
| teacher:gpt4o | 1 | 138 | 0.074 | 0.047 | 0.105 |
| base_prior | 1 | 138 | 0.164 | 0.143 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.255 | -0.312 | -0.201 |
| students:claude46 | students:gpt4o | -0.086 | -0.124 | -0.051 |
| students:claude46 | teacher:claude46 | 0.019 | -0.021 | 0.060 |
| students:claude46 | base_prior | -0.093 | -0.121 | -0.065 |
| students:deepseek_v4 | students:gpt4o | 0.169 | 0.116 | 0.223 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.177 | 0.119 | 0.233 |
| students:deepseek_v4 | base_prior | 0.162 | 0.111 | 0.216 |
| students:gpt4o | teacher:gpt4o | 0.083 | 0.046 | 0.122 |
| students:gpt4o | base_prior | -0.007 | -0.045 | 0.032 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.073 | -0.091 | 0.164 | 138 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.052 | 0.071 | 0.013 | 5 |
| deepseek_v4 | 0.150 | 0.326 | 0.021 | 5 |
| gpt4o | 0.074 | 0.157 | 0.019 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix50.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix50.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.994 | True | data/sft_e2c_mix50/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix50.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix50.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix50.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix50.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.996 | True | data/sft_e2c_mix50/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix50.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.997 | True | data/sft_e2c_mix50/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix50.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.997 | True | data/sft_e2c_mix50/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix50.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.998 | True | data/sft_e2c_mix50/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix50.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix50.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.997 | True | data/sft_e2c_mix50/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix50.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.997 | True | data/sft_e2c_mix50/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix50.gpt4o_O_s4 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.997 | True | data/sft_e2c_mix50/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix50.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.995 | True | data/sft_e2c_mix50/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 189 | 163 | 5 | 945 | 0.986 | 0.973 | 0.997 | True |
| claude46 | gpt4o | 276 | 234 | 5 | 1380 | 0.980 | 0.968 | 0.990 | True |
| deepseek_v4 | claude46 | 189 | 163 | 5 | 945 | 0.997 | 0.991 | 1.000 | True |
| deepseek_v4 | gpt4o | 114 | 100 | 5 | 570 | 0.988 | 0.974 | 0.998 | True |
| gpt4o | claude46 | 276 | 234 | 5 | 1380 | 0.991 | 0.986 | 0.996 | True |
| gpt4o | deepseek_v4 | 114 | 100 | 5 | 570 | 0.991 | 0.981 | 0.998 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2cmix50.claude46_O_s1 | 1.000 | 0.076 | 150 | 0.828 | 0.801 | 0.142 | 0.044 | 0.028 |
| qwen3-4b-e2cmix50.claude46_O_s2 | 1.000 | 0.080 | 150 | 0.824 | 0.794 | 0.142 | 0.069 | 0.033 |
| qwen3-4b-e2cmix50.claude46_O_s3 | 1.000 | 0.077 | 150 | 0.837 | 0.817 | 0.141 | 0.049 | 0.025 |
| qwen3-4b-e2cmix50.claude46_O_s4 | 1.000 | 0.072 | 150 | 0.840 | 0.812 | 0.134 | 0.067 | 0.028 |
| qwen3-4b-e2cmix50.claude46_O_s5 | 1.000 | 0.080 | 150 | 0.835 | 0.814 | 0.144 | 0.063 | 0.032 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s1 | 1.000 | 0.067 | 150 | 0.824 | 0.801 | 0.105 | 0.158 | 0.125 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s2 | 0.999 | 0.080 | 150 | 0.820 | 0.794 | 0.104 | 0.173 | 0.109 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s3 | 1.000 | 0.080 | 150 | 0.802 | 0.783 | 0.116 | 0.186 | 0.132 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s4 | 0.998 | 0.088 | 149 | 0.815 | 0.790 | 0.105 | 0.155 | 0.109 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s5 | 1.000 | 0.090 | 150 | 0.824 | 0.800 | 0.105 | 0.176 | 0.122 |
| qwen3-4b-e2cmix50.gpt4o_O_s1 | 1.000 | 0.070 | 150 | 0.859 | 0.849 | 0.099 | 0.082 | 0.053 |
| qwen3-4b-e2cmix50.gpt4o_O_s2 | 1.000 | 0.061 | 150 | 0.866 | 0.849 | 0.096 | 0.078 | 0.054 |
| qwen3-4b-e2cmix50.gpt4o_O_s3 | 1.000 | 0.066 | 150 | 0.866 | 0.861 | 0.092 | 0.099 | 0.061 |
| qwen3-4b-e2cmix50.gpt4o_O_s4 | 1.000 | 0.065 | 150 | 0.871 | 0.862 | 0.094 | 0.080 | 0.044 |
| qwen3-4b-e2cmix50.gpt4o_O_s5 | 1.000 | 0.071 | 150 | 0.861 | 0.849 | 0.097 | 0.094 | 0.043 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2cmix50.claude46_O_s1 | 0.828 | 0.780 | 0.801 | 0.142 | 0.136 | 0.143 |
| qwen3-4b-e2cmix50.claude46_O_s2 | 0.824 | 0.771 | 0.794 | 0.142 | 0.138 | 0.147 |
| qwen3-4b-e2cmix50.claude46_O_s3 | 0.837 | 0.797 | 0.817 | 0.141 | 0.127 | 0.142 |
| qwen3-4b-e2cmix50.claude46_O_s4 | 0.840 | 0.782 | 0.812 | 0.134 | 0.128 | 0.133 |
| qwen3-4b-e2cmix50.claude46_O_s5 | 0.835 | 0.790 | 0.814 | 0.144 | 0.132 | 0.141 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s1 | 0.801 | 0.824 | 0.798 | 0.174 | 0.105 | 0.155 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s2 | 0.776 | 0.820 | 0.794 | 0.189 | 0.104 | 0.162 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s3 | 0.783 | 0.802 | 0.780 | 0.194 | 0.116 | 0.172 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s4 | 0.786 | 0.815 | 0.790 | 0.188 | 0.105 | 0.163 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s5 | 0.790 | 0.824 | 0.800 | 0.189 | 0.105 | 0.161 |
| qwen3-4b-e2cmix50.gpt4o_O_s1 | 0.833 | 0.849 | 0.859 | 0.130 | 0.089 | 0.099 |
| qwen3-4b-e2cmix50.gpt4o_O_s2 | 0.845 | 0.849 | 0.866 | 0.126 | 0.091 | 0.096 |
| qwen3-4b-e2cmix50.gpt4o_O_s3 | 0.840 | 0.861 | 0.866 | 0.126 | 0.089 | 0.092 |
| qwen3-4b-e2cmix50.gpt4o_O_s4 | 0.840 | 0.862 | 0.871 | 0.134 | 0.089 | 0.094 |
| qwen3-4b-e2cmix50.gpt4o_O_s5 | 0.849 | 0.847 | 0.861 | 0.125 | 0.098 | 0.097 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.833 | 0.808 | 0.140 | 0.058 | 0.029 |
| deepseek_v4 | O | 5 | 0.999 | 0.817 | 0.794 | 0.107 | 0.170 | 0.119 |
| gpt4o | O | 5 | 1.000 | 0.864 | 0.854 | 0.096 | 0.087 | 0.051 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_s1 | 139.000 | 0.342 | 0.034 | 0.744 | 0.094 | deepseek_v4 | -0.059 | 0.545 | -0.054 | -0.240 | 0.082 | 0.034 | 0.094 | 0.039 |
| qwen3-4b-e2cmix50.claude46_O_s2 | 139.000 | 0.285 | 0.108 | 0.744 | 0.092 | deepseek_v4 | 0.016 | 0.151 | -0.046 | -0.116 | 0.136 | 0.108 | 0.092 | 0.026 |
| qwen3-4b-e2cmix50.claude46_O_s3 | 139.000 | 0.318 | 0.082 | 0.744 | 0.064 | deepseek_v4 | 0.018 | 0.132 | -0.045 | -0.181 | 0.132 | 0.082 | 0.064 | 0.050 |
| qwen3-4b-e2cmix50.claude46_O_s4 | 139.000 | 0.343 | 0.017 | 0.744 | 0.063 | deepseek_v4 | -0.046 | 0.454 | -0.053 | -0.189 | 0.083 | 0.017 | 0.063 | 0.028 |
| qwen3-4b-e2cmix50.claude46_O_s5 | 139.000 | 0.415 | 0.088 | 0.744 | 0.142 | deepseek_v4 | -0.054 | 0.481 | -0.058 | -0.204 | 0.097 | 0.088 | 0.142 | 0.038 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s1 | 139.000 | 0.593 | 0.270 | 0.825 | 0.148 | gpt4o | 0.122 | 0.039 | 0.025 | -0.018 | 0.256 | 0.009 | 0.270 | 0.148 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s2 | 139.000 | 0.617 | 0.267 | 0.825 | 0.160 | gpt4o | 0.106 | 0.065 | 0.024 | -0.038 | 0.236 | 0.085 | 0.267 | 0.160 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s3 | 139.000 | 0.637 | 0.209 | 0.825 | 0.143 | gpt4o | 0.067 | 0.223 | 0.026 | -0.066 | 0.201 | 0.017 | 0.209 | 0.143 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s4 | 138.000 | 0.626 | 0.252 | 0.825 | 0.185 | gpt4o | 0.067 | 0.224 | 0.026 | -0.093 | 0.217 | 0.086 | 0.252 | 0.185 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s5 | 139.000 | 0.633 | 0.220 | 0.825 | 0.165 | gpt4o | 0.055 | 0.311 | 0.028 | -0.078 | 0.181 | 0.071 | 0.220 | 0.165 |
| qwen3-4b-e2cmix50.gpt4o_O_s1 | 139.000 | 0.486 | 0.277 | 0.898 | 0.242 | deepseek_v4 | 0.034 | 0.125 | -0.031 | -0.127 | 0.175 | 0.137 | 0.242 | 0.277 |
| qwen3-4b-e2cmix50.gpt4o_O_s2 | 139.000 | 0.474 | 0.290 | 0.898 | 0.192 | deepseek_v4 | 0.098 | 0.013 | -0.032 | -0.077 | 0.236 | 0.112 | 0.192 | 0.290 |
| qwen3-4b-e2cmix50.gpt4o_O_s3 | 139.000 | 0.465 | 0.250 | 0.898 | 0.194 | deepseek_v4 | 0.056 | 0.055 | -0.033 | -0.108 | 0.193 | 0.097 | 0.194 | 0.250 |
| qwen3-4b-e2cmix50.gpt4o_O_s4 | 139.000 | 0.422 | 0.215 | 0.898 | 0.239 | deepseek_v4 | -0.024 | 0.443 | -0.031 | -0.199 | 0.143 | 0.046 | 0.239 | 0.215 |
| qwen3-4b-e2cmix50.gpt4o_O_s5 | 139.000 | 0.427 | 0.243 | 0.898 | 0.225 | deepseek_v4 | 0.018 | 0.193 | -0.031 | -0.145 | 0.170 | 0.103 | 0.225 | 0.243 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.025 | 0.039 | 5 |
| deepseek_v4 | 0.083 | 0.029 | 5 |
| gpt4o | 0.036 | 0.045 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.032 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix50.claude46_O_s1 | 0.115 | 0.744 | 0.257 | deepseek_v4 | -0.142 | 0.832 | -0.296 | -0.007 |
| qwen3-4b-e2cmix50.claude46_O_s2 | 0.170 | 0.744 | 0.226 | deepseek_v4 | -0.056 | 0.423 | -0.176 | 0.063 |
| qwen3-4b-e2cmix50.claude46_O_s3 | 0.153 | 0.744 | 0.221 | deepseek_v4 | -0.067 | 0.505 | -0.238 | 0.080 |
| qwen3-4b-e2cmix50.claude46_O_s4 | 0.099 | 0.744 | 0.232 | deepseek_v4 | -0.133 | 0.814 | -0.267 | 0.002 |
| qwen3-4b-e2cmix50.claude46_O_s5 | 0.179 | 0.744 | 0.331 | deepseek_v4 | -0.152 | 0.835 | -0.282 | -0.010 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s1 | 0.500 | 0.825 | 0.279 | gpt4o | 0.221 | 0.006 | 0.087 | 0.352 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s2 | 0.507 | 0.825 | 0.292 | gpt4o | 0.214 | 0.008 | 0.083 | 0.332 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s3 | 0.476 | 0.825 | 0.282 | gpt4o | 0.194 | 0.031 | 0.070 | 0.321 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s4 | 0.501 | 0.825 | 0.314 | gpt4o | 0.187 | 0.040 | 0.043 | 0.325 |
| qwen3-4b-e2cmix50.deepseek_v4_O_s5 | 0.481 | 0.825 | 0.298 | gpt4o | 0.183 | 0.060 | 0.064 | 0.297 |
| qwen3-4b-e2cmix50.gpt4o_O_s1 | 0.367 | 0.898 | 0.438 | deepseek_v4 | -0.071 | 0.403 | -0.229 | 0.074 |
| qwen3-4b-e2cmix50.gpt4o_O_s2 | 0.376 | 0.898 | 0.396 | deepseek_v4 | -0.019 | 0.084 | -0.180 | 0.129 |
| qwen3-4b-e2cmix50.gpt4o_O_s3 | 0.341 | 0.898 | 0.393 | deepseek_v4 | -0.052 | 0.238 | -0.205 | 0.092 |
| qwen3-4b-e2cmix50.gpt4o_O_s4 | 0.304 | 0.898 | 0.408 | deepseek_v4 | -0.104 | 0.667 | -0.267 | 0.061 |
| qwen3-4b-e2cmix50.gpt4o_O_s5 | 0.329 | 0.898 | 0.400 | deepseek_v4 | -0.071 | 0.417 | -0.221 | 0.076 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | 0.024 | 0.106 | 5 |
| claude46 | T1 | 0.115 | 0.030 | 5 |
| claude46 | T3 | -0.218 | 0.046 | 5 |
| claude46 | T5 | -0.040 | 0.055 | 5 |
| claude46 | T6 | 0.001 | 0.064 | 5 |
| deepseek_v4 | T0 | -0.191 | 0.073 | 5 |
| deepseek_v4 | T1 | 0.104 | 0.088 | 5 |
| deepseek_v4 | T3 | 0.090 | 0.092 | 5 |
| deepseek_v4 | T5 | 0.073 | 0.057 | 5 |
| deepseek_v4 | T6 | 0.043 | 0.030 | 5 |
| gpt4o | T0 | -1.5e-04 | 0.026 | 5 |
| gpt4o | T1 | -0.082 | 0.059 | 5 |
| gpt4o | T3 | -0.083 | 0.039 | 5 |
| gpt4o | T5 | 0.169 | 0.051 | 5 |
| gpt4o | T6 | 0.022 | 0.065 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.386 | 0.077 | 0.744 | 0.105 | deepseek_v4 | -0.028 | -0.189 | 0.108 | 0.324 | -0.056 | 0.324 |
| deepseek_v4 | 5 | 138 | 0.652 | 0.265 | 0.825 | 0.176 | gpt4o | 0.089 | -0.055 | 0.223 | 0.149 | 0.031 | 0.298 |
| gpt4o | 5 | 139 | 0.497 | 0.285 | 0.898 | 0.243 | deepseek_v4 | 0.043 | -0.123 | 0.194 | 0.090 | -0.032 | 0.271 |

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

- P1 mean deltaRhoPartial 0.032 vs run-reassignment null mean -0.046 sd 0.017, p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 2.521, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.088 [0.011, 0.164] p 0.003 alone would read pass; the frozen rule (version 5) also needs D_specific 0.110 [0.026, 0.201] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.008 | 0.005 | 0.014 |
| agree_own | deepseek_v4 | O | 10 | 0.011 | 0.008 | 0.022 |
| agree_own | gpt4o | O | 10 | 0.006 | 0.004 | 0.011 |
| agree_own | all | all | 30 | 0.008 | 0.006 | 0.020 |
| jsd_own | claude46 | O | 10 | 0.004 | 0.004 | 0.009 |
| jsd_own | deepseek_v4 | O | 10 | 0.005 | 0.005 | 0.012 |
| jsd_own | gpt4o | O | 10 | 0.003 | 0.002 | 0.006 |
| jsd_own | all | all | 30 | 0.004 | 0.004 | 0.011 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.013 | 0.009 | 0.023 |
| flip_rate | deepseek_v4 | O | 10 | 0.016 | 0.009 | 0.029 |
| flip_rate | gpt4o | O | 10 | 0.011 | 0.007 | 0.020 |
| flip_rate | all | all | 30 | 0.013 | 0.008 | 0.026 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.004 | 0.002 | 0.007 |
| mean_jsd | deepseek_v4 | O | 10 | 0.012 | 0.008 | 0.023 |
| mean_jsd | gpt4o | O | 10 | 0.009 | 0.005 | 0.017 |
| mean_jsd | all | all | 30 | 0.008 | 0.007 | 0.021 |
| delta_rho | claude46 | O | 10 | 0.053 | 0.036 | 0.091 |
| delta_rho | deepseek_v4 | O | 10 | 0.021 | 0.013 | 0.036 |
| delta_rho | gpt4o | O | 10 | 0.038 | 0.023 | 0.070 |
| delta_rho | all | all | 30 | 0.037 | 0.028 | 0.085 |
| delta_rho_partial | claude46 | O | 10 | 0.045 | 0.033 | 0.077 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.035 | 0.023 | 0.062 |
| delta_rho_partial | gpt4o | O | 10 | 0.056 | 0.032 | 0.103 |
| delta_rho_partial | all | all | 30 | 0.045 | 0.030 | 0.080 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.