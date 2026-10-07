# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.998, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.711 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.143 [-0.320, 0.032] p_perm 0.921 (null mean -0.066) p_holm 1.000; deepseek_v4 0.141 [-0.030, 0.261] p_perm 0.109 (null mean 0.079) p_holm 0.326; gpt4o -0.150 [-0.323, 0.007] p_perm 0.935 (null mean -0.078) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.005 [-0.058, 0.068], p 0.502; D_specific 0.009 [-0.054, 0.073], D_shared -0.004 (138 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 138 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.030 | teacher-level exact p 0.667 (rank 4 of 6 relabellings, floor 0.167); the run-level null (mean -0.028, sd 0.011, p 0.543, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 0.770 (pearson 0.810, seed-noise sd 0.018, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 2.0e-04 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.076 [-0.265, 0.098] p_holm 1.000; deepseek_v4 0.036 [-0.164, 0.160] p_holm 1.000; gpt4o -0.063 [-0.233, 0.092] p_holm 1.000 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.019 [-0.121, 0.078], p 0.733 (136 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.014 [-0.039, 0.066], p 0.565 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.007 [-0.055, 0.070] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.141 | 0.744 | 0.190 | 0.285 | deepseek_v4 | -0.143 | -0.320 | 0.032 | 0.921 | -0.066 | 0.054 | 1.000 | False |
| deepseek_v4 | 5 | 138 | 0.418 | 0.825 | 0.507 | 0.277 | gpt4o | 0.141 | -0.030 | 0.261 | 0.109 | 0.079 | 0.050 | 0.326 | False |
| gpt4o | 5 | 139 | 0.215 | 0.898 | 0.239 | 0.365 | deepseek_v4 | -0.150 | -0.323 | 0.007 | 0.935 | -0.078 | 0.048 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.044 | -0.054 | 0.011 | 0.178 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.005 | -0.058 | 0.068 | 0.502 | 0.005 | 0.021 | 0.014 | 138 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.004 | 0.009 | -0.054 | 0.073 | 0.446 | 0.006 | 0.022 | 0.007 | -0.055 | 0.070 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2ckn.claude46_O_pooled 0.080, qwen3-4b-e2ckn.deepseek_v4_O_pooled 0.099, qwen3-4b-e2ckn.gpt4o_O_pooled 0.087.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | 0.078 | 0.145 | 0.049 | 0.744 | -0.019 | 0.023 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.174 | 0.209 | 0.166 | 0.825 | 0.039 | -0.021 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | 0.058 | 0.170 | 0.110 | 0.898 | -0.005 | 0.026 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | -0.041 | -0.051 | -0.076 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.078 | 0.051 | 0.065 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | -0.051 | -0.010 | -0.005 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | 0.147 | 0.285 | 0.133 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.265 | 0.418 | 0.277 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | 0.157 | 0.367 | 0.219 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | 0.083 | -0.047 | 0.177 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.159 | 0.020 | 0.264 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | -0.061 | 0.030 | 0.100 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 138 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 138 | 0.049 | 0.028 | 0.075 |
| students:deepseek_v4 | 5 | 138 | 0.137 | 0.100 | 0.178 |
| students:gpt4o | 5 | 138 | 0.106 | 0.076 | 0.140 |
| teacher:claude46 | 1 | 138 | 0.052 | 0.017 | 0.089 |
| teacher:deepseek_v4 | 1 | 138 | 0.150 | 0.120 | 0.181 |
| teacher:gpt4o | 1 | 138 | 0.074 | 0.047 | 0.105 |
| base_prior | 1 | 138 | 0.164 | 0.143 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.087 | -0.120 | -0.057 |
| students:claude46 | students:gpt4o | -0.057 | -0.082 | -0.033 |
| students:claude46 | teacher:claude46 | -0.003 | -0.042 | 0.037 |
| students:claude46 | base_prior | -0.115 | -0.142 | -0.086 |
| students:deepseek_v4 | students:gpt4o | 0.031 | 0.003 | 0.059 |
| students:deepseek_v4 | teacher:deepseek_v4 | -0.013 | -0.050 | 0.026 |
| students:deepseek_v4 | base_prior | -0.027 | -0.063 | 0.010 |
| students:gpt4o | teacher:gpt4o | 0.032 | -0.006 | 0.070 |
| students:gpt4o | base_prior | -0.058 | -0.090 | -0.025 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.073 | -0.091 | 0.164 | 138 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.052 | 0.049 | 0.011 | 5 |
| deepseek_v4 | 0.150 | 0.137 | 0.022 | 5 |
| gpt4o | 0.074 | 0.106 | 0.020 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.999 | True | data/sft_e2ckn/claude46_O_s1.jsonl |
| qwen3-4b-e2ckn.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.999 | True | data/sft_e2ckn/claude46_O_s1.jsonl |
| qwen3-4b-e2ckn.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.999 | True | data/sft_e2ckn/claude46_O_s1.jsonl |
| qwen3-4b-e2ckn.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 1.000 | True | data/sft_e2ckn/claude46_O_s1.jsonl |
| qwen3-4b-e2ckn.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.999 | True | data/sft_e2ckn/claude46_O_s1.jsonl |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.999 | True | data/sft_e2ckn/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 1.000 | True | data/sft_e2ckn/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 1.000 | True | data/sft_e2ckn/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 1.000 | True | data/sft_e2ckn/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.998 | True | data/sft_e2ckn/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 1.000 | True | data/sft_e2ckn/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.999 | True | data/sft_e2ckn/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.999 | True | data/sft_e2ckn/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.999 | True | data/sft_e2ckn/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.998 | True | data/sft_e2ckn/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 9 | 9 | 5 | 45 | 0.956 | 0.889 | 1.000 | True |
| claude46 | gpt4o | 29 | 27 | 5 | 145 | 0.917 | 0.860 | 0.966 | True |
| deepseek_v4 | claude46 | 9 | 9 | 5 | 45 | 0.867 | 0.711 | 1.000 | True |
| deepseek_v4 | gpt4o | 16 | 16 | 5 | 80 | 0.938 | 0.850 | 1.000 | True |
| gpt4o | claude46 | 29 | 27 | 5 | 145 | 0.903 | 0.814 | 0.968 | True |
| gpt4o | deepseek_v4 | 16 | 16 | 5 | 80 | 0.875 | 0.725 | 0.975 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2ckn.claude46_O_s1 | 1.000 | 0.076 | 150 | 0.822 | 0.814 | 0.144 | 0.079 | 0.035 |
| qwen3-4b-e2ckn.claude46_O_s2 | 1.000 | 0.086 | 150 | 0.821 | 0.822 | 0.157 | 0.052 | 0.027 |
| qwen3-4b-e2ckn.claude46_O_s3 | 1.000 | 0.068 | 150 | 0.806 | 0.797 | 0.165 | 0.047 | 0.028 |
| qwen3-4b-e2ckn.claude46_O_s4 | 1.000 | 0.076 | 150 | 0.835 | 0.840 | 0.144 | 0.061 | 0.034 |
| qwen3-4b-e2ckn.claude46_O_s5 | 1.000 | 0.061 | 150 | 0.801 | 0.800 | 0.170 | 0.053 | 0.027 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 0.999 | 0.091 | 150 | 0.829 | 0.838 | 0.101 | 0.109 | 0.056 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 1.000 | 0.067 | 150 | 0.815 | 0.828 | 0.109 | 0.082 | 0.044 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 0.999 | 0.078 | 149 | 0.808 | 0.835 | 0.105 | 0.103 | 0.055 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 1.000 | 0.072 | 150 | 0.837 | 0.850 | 0.101 | 0.090 | 0.050 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 1.000 | 0.064 | 150 | 0.830 | 0.850 | 0.105 | 0.063 | 0.039 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 1.000 | 0.066 | 150 | 0.836 | 0.833 | 0.123 | 0.081 | 0.051 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 1.000 | 0.074 | 150 | 0.829 | 0.835 | 0.119 | 0.079 | 0.033 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 1.000 | 0.077 | 150 | 0.817 | 0.822 | 0.132 | 0.071 | 0.027 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 0.999 | 0.074 | 150 | 0.834 | 0.840 | 0.120 | 0.071 | 0.030 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 1.000 | 0.060 | 150 | 0.838 | 0.840 | 0.119 | 0.062 | 0.034 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2ckn.claude46_O_s1 | 0.822 | 0.808 | 0.814 | 0.144 | 0.111 | 0.127 |
| qwen3-4b-e2ckn.claude46_O_s2 | 0.821 | 0.818 | 0.822 | 0.157 | 0.116 | 0.134 |
| qwen3-4b-e2ckn.claude46_O_s3 | 0.806 | 0.797 | 0.787 | 0.165 | 0.124 | 0.159 |
| qwen3-4b-e2ckn.claude46_O_s4 | 0.835 | 0.824 | 0.840 | 0.144 | 0.108 | 0.118 |
| qwen3-4b-e2ckn.claude46_O_s5 | 0.801 | 0.800 | 0.793 | 0.170 | 0.124 | 0.156 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 0.837 | 0.829 | 0.838 | 0.134 | 0.101 | 0.120 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 0.828 | 0.815 | 0.826 | 0.141 | 0.109 | 0.133 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 0.835 | 0.808 | 0.825 | 0.135 | 0.105 | 0.124 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 0.837 | 0.837 | 0.850 | 0.138 | 0.101 | 0.114 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 0.833 | 0.830 | 0.850 | 0.139 | 0.105 | 0.108 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 0.833 | 0.824 | 0.836 | 0.143 | 0.107 | 0.123 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 0.835 | 0.824 | 0.829 | 0.142 | 0.100 | 0.119 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 0.822 | 0.805 | 0.817 | 0.148 | 0.110 | 0.132 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 0.840 | 0.829 | 0.834 | 0.138 | 0.102 | 0.120 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 0.840 | 0.825 | 0.838 | 0.135 | 0.104 | 0.119 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.817 | 0.815 | 0.156 | 0.058 | 0.030 |
| deepseek_v4 | O | 5 | 1.000 | 0.824 | 0.840 | 0.104 | 0.089 | 0.049 |
| gpt4o | O | 5 | 1.000 | 0.831 | 0.834 | 0.123 | 0.073 | 0.035 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_s1 | 139.000 | 0.343 | 0.049 | 0.744 | 0.078 | deepseek_v4 | -0.030 | 0.398 | -0.046 | -0.218 | 0.133 | 0.049 | 0.078 | -0.052 |
| qwen3-4b-e2ckn.claude46_O_s2 | 139.000 | 0.225 | 0.043 | 0.744 | 0.184 | deepseek_v4 | -0.142 | 0.943 | -0.042 | -0.345 | 0.047 | 0.043 | 0.184 | 0.109 |
| qwen3-4b-e2ckn.claude46_O_s3 | 139.000 | 0.256 | 0.118 | 0.744 | 0.107 | deepseek_v4 | 0.010 | 0.184 | -0.040 | -0.185 | 0.131 | 0.118 | 0.107 | 0.102 |
| qwen3-4b-e2ckn.claude46_O_s4 | 139.000 | 0.298 | -0.017 | 0.744 | 0.114 | deepseek_v4 | -0.131 | 0.944 | -0.041 | -0.289 | 0.010 | -0.017 | 0.114 | 0.015 |
| qwen3-4b-e2ckn.claude46_O_s5 | 139.000 | 0.195 | 0.105 | 0.744 | 0.134 | deepseek_v4 | -0.029 | 0.430 | -0.039 | -0.216 | 0.143 | 0.105 | 0.134 | 0.052 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 139.000 | 0.494 | 0.198 | 0.825 | 0.125 | gpt4o | 0.074 | 0.148 | 0.016 | -0.105 | 0.194 | 0.117 | 0.198 | 0.125 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 139.000 | 0.455 | 0.205 | 0.825 | 0.172 | claude46 | 0.033 | 0.339 | 0.009 | -0.169 | 0.186 | 0.172 | 0.205 | 0.121 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 138.000 | 0.453 | 0.182 | 0.825 | 0.154 | claude46 | 0.028 | 0.407 | 0.014 | -0.150 | 0.140 | 0.154 | 0.182 | 0.149 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 139.000 | 0.473 | 0.172 | 0.825 | 0.159 | gpt4o | 0.013 | 0.486 | 0.011 | -0.207 | 0.148 | 0.158 | 0.172 | 0.159 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 139.000 | 0.364 | 0.179 | 0.825 | 0.191 | gpt4o | -0.012 | 0.631 | 0.007 | -0.183 | 0.132 | 0.147 | 0.179 | 0.191 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 139.000 | 0.409 | 0.077 | 0.898 | 0.187 | deepseek_v4 | -0.111 | 0.931 | -0.032 | -0.259 | 0.044 | 0.018 | 0.187 | 0.077 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 139.000 | 0.377 | 0.159 | 0.898 | 0.166 | deepseek_v4 | -0.007 | 0.327 | -0.030 | -0.189 | 0.163 | 0.067 | 0.166 | 0.159 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 139.000 | 0.412 | 0.134 | 0.898 | 0.159 | deepseek_v4 | -0.025 | 0.471 | -0.028 | -0.175 | 0.094 | 0.066 | 0.159 | 0.134 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 139.000 | 0.369 | 0.088 | 0.898 | 0.151 | deepseek_v4 | -0.063 | 0.751 | -0.028 | -0.238 | 0.092 | 0.072 | 0.151 | 0.088 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 139.000 | 0.427 | 0.021 | 0.898 | 0.075 | deepseek_v4 | -0.054 | 0.683 | -0.029 | -0.273 | 0.131 | -0.006 | 0.075 | 0.021 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.064 | 0.068 | 5 |
| deepseek_v4 | 0.027 | 0.031 | 5 |
| gpt4o | -0.052 | 0.040 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.030 | 0.667 | 4 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_s1 | 0.128 | 0.744 | 0.245 | deepseek_v4 | -0.117 | 0.814 | -0.301 | 0.050 |
| qwen3-4b-e2ckn.claude46_O_s2 | 0.095 | 0.744 | 0.272 | deepseek_v4 | -0.177 | 0.975 | -0.371 | 0.012 |
| qwen3-4b-e2ckn.claude46_O_s3 | 0.173 | 0.744 | 0.224 | deepseek_v4 | -0.051 | 0.471 | -0.212 | 0.089 |
| qwen3-4b-e2ckn.claude46_O_s4 | 0.057 | 0.744 | 0.251 | deepseek_v4 | -0.194 | 0.992 | -0.349 | -0.047 |
| qwen3-4b-e2ckn.claude46_O_s5 | 0.148 | 0.744 | 0.215 | deepseek_v4 | -0.068 | 0.619 | -0.234 | 0.095 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 0.409 | 0.825 | 0.241 | gpt4o | 0.168 | 0.029 | 0.020 | 0.277 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 0.397 | 0.825 | 0.260 | claude46 | 0.137 | 0.085 | -0.044 | 0.268 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 0.379 | 0.825 | 0.254 | gpt4o | 0.125 | 0.157 | -0.032 | 0.229 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 0.380 | 0.825 | 0.266 | gpt4o | 0.115 | 0.180 | -0.082 | 0.252 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 0.335 | 0.825 | 0.271 | gpt4o | 0.063 | 0.454 | -0.087 | 0.199 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 0.180 | 0.898 | 0.362 | deepseek_v4 | -0.182 | 0.983 | -0.319 | -0.035 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 0.246 | 0.898 | 0.331 | deepseek_v4 | -0.086 | 0.618 | -0.266 | 0.087 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 0.231 | 0.898 | 0.342 | deepseek_v4 | -0.111 | 0.800 | -0.239 | 0.012 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 0.181 | 0.898 | 0.316 | deepseek_v4 | -0.135 | 0.927 | -0.307 | 0.027 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 0.137 | 0.898 | 0.285 | deepseek_v4 | -0.148 | 0.947 | -0.373 | 0.053 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.070 | 0.040 | 5 |
| claude46 | T1 | -0.208 | 0.103 | 5 |
| claude46 | T3 | -0.154 | 0.086 | 5 |
| claude46 | T5 | -0.086 | 0.078 | 5 |
| claude46 | T6 | -0.002 | 0.090 | 5 |
| deepseek_v4 | T0 | -0.189 | 0.118 | 5 |
| deepseek_v4 | T1 | -0.222 | 0.126 | 5 |
| deepseek_v4 | T3 | -0.099 | 0.122 | 5 |
| deepseek_v4 | T5 | 0.013 | 0.052 | 5 |
| deepseek_v4 | T6 | 0.050 | 0.013 | 5 |
| gpt4o | T0 | 0.052 | 0.058 | 5 |
| gpt4o | T1 | 0.005 | 0.091 | 5 |
| gpt4o | T3 | -0.104 | 0.085 | 5 |
| gpt4o | T5 | -0.151 | 0.057 | 5 |
| gpt4o | T6 | -0.027 | 0.092 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.314 | 0.070 | 0.744 | 0.146 | deepseek_v4 | -0.076 | -0.265 | 0.098 | 0.713 | -0.045 | 1.000 |
| deepseek_v4 | 5 | 138 | 0.494 | 0.209 | 0.825 | 0.174 | claude46 | 0.036 | -0.164 | 0.160 | 0.366 | 0.016 | 1.000 |
| gpt4o | 5 | 139 | 0.443 | 0.107 | 0.898 | 0.170 | deepseek_v4 | -0.063 | -0.233 | 0.092 | 0.731 | -0.031 | 1.000 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.245 | 0.744 | 0.118 | 0.365 | 3 | -0.288 | -0.419 | -0.164 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.533 | 0.825 | 0.448 | 0.611 | 1 | 0.256 | 0.130 | 0.359 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.277 | 0.898 | 0.166 | 0.380 | 2 | -0.256 | -0.383 | -0.133 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 3/5 seeds pass -> partial (old rule, not the verdict)
- deepseek_v4: 0/5 seeds pass -> fail (old rule, not the verdict)
- gpt4o: 1/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial -0.030 vs run-reassignment null mean -0.028 sd 0.011, p 0.543 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.667
- P2 slope 0.770, run-reassignment p 2.0e-04 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.005 [-0.058, 0.068] p 0.502 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.009 [-0.054, 0.073] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.017 | 0.010 | 0.031 |
| agree_own | deepseek_v4 | O | 10 | 0.015 | 0.009 | 0.026 |
| agree_own | gpt4o | O | 10 | 0.010 | 0.007 | 0.020 |
| agree_own | all | all | 30 | 0.014 | 0.009 | 0.029 |
| jsd_own | claude46 | O | 10 | 0.014 | 0.009 | 0.026 |
| jsd_own | deepseek_v4 | O | 10 | 0.004 | 0.003 | 0.008 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.005 | 0.014 |
| jsd_own | all | all | 30 | 0.008 | 0.007 | 0.023 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.015 | 0.010 | 0.030 |
| flip_rate | deepseek_v4 | O | 10 | 0.022 | 0.013 | 0.043 |
| flip_rate | gpt4o | O | 10 | 0.009 | 0.006 | 0.018 |
| flip_rate | all | all | 30 | 0.015 | 0.011 | 0.036 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.005 | 0.003 | 0.008 |
| mean_jsd | deepseek_v4 | O | 10 | 0.009 | 0.005 | 0.017 |
| mean_jsd | gpt4o | O | 10 | 0.010 | 0.009 | 0.023 |
| mean_jsd | all | all | 30 | 0.008 | 0.007 | 0.020 |
| delta_rho | claude46 | O | 10 | 0.079 | 0.045 | 0.135 |
| delta_rho | deepseek_v4 | O | 10 | 0.046 | 0.029 | 0.091 |
| delta_rho | gpt4o | O | 10 | 0.046 | 0.025 | 0.085 |
| delta_rho | all | all | 30 | 0.057 | 0.037 | 0.126 |
| delta_rho_partial | claude46 | O | 10 | 0.081 | 0.054 | 0.147 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.038 | 0.024 | 0.074 |
| delta_rho_partial | gpt4o | O | 10 | 0.049 | 0.029 | 0.095 |
| delta_rho_partial | all | all | 30 | 0.056 | 0.041 | 0.128 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.