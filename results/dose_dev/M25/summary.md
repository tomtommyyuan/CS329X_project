# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.996, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.946 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -6.4e-04 [-0.170, 0.141] p_perm 0.119 (null mean -0.070) p_holm 0.239; deepseek_v4 0.170 [0.010, 0.322] p_perm 0.038 (null mean 0.087) p_holm 0.115; gpt4o -0.159 [-0.319, -0.003] p_perm 0.929 (null mean -0.088) p_holm 0.929; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.078 [0.011, 0.137], p 0.002; D_specific 0.090 [0.021, 0.160], D_shared -0.012 (138 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 138 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.020 | teacher-level exact p 0.333 (rank 2 of 6 relabellings, floor 0.167); the run-level null (mean -0.046, sd 0.022, p 0.001, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.228 (pearson 0.878, seed-noise sd 0.015, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 0.086 [-0.105, 0.203] p_holm 0.052; deepseek_v4 0.072 [-0.104, 0.223] p_holm 0.334; gpt4o -0.080 [-0.238, 0.085] p_holm 0.814 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.014 [-0.066, 0.097], p 0.359 (137 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.080 [0.022, 0.131], p 0.002 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.078 [0.015, 0.137] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.244 | 0.744 | 0.328 | 0.245 | deepseek_v4 | -6.4e-04 | -0.170 | 0.141 | 0.119 | -0.070 | 0.060 | 0.239 | False |
| deepseek_v4 | 5 | 138 | 0.431 | 0.825 | 0.523 | 0.261 | gpt4o | 0.170 | 0.010 | 0.322 | 0.038 | 0.087 | 0.047 | 0.115 | False |
| gpt4o | 5 | 139 | 0.244 | 0.898 | 0.272 | 0.403 | deepseek_v4 | -0.159 | -0.319 | -0.003 | 0.929 | -0.088 | 0.049 | 0.929 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| 0.005 | -0.063 | 0.022 | 6.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.078 | 0.011 | 0.137 | 0.002 | 0.006 | 0.025 | 0.080 | 138 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.012 | 0.090 | 0.021 | 0.160 | 0.001 | 0.008 | 0.027 | 0.078 | 0.015 | 0.137 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2cmix25.claude46_O_pooled 0.075, qwen3-4b-e2cmix25.deepseek_v4_O_pooled 0.121, qwen3-4b-e2cmix25.gpt4o_O_pooled 0.095.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_pooled | 0.192 | 0.093 | 0.086 | 0.744 | 0.102 | 0.197 |
| qwen3-4b-e2cmix25.deepseek_v4_O_pooled | 0.066 | 0.215 | 0.142 | 0.825 | 0.111 | 0.047 |
| qwen3-4b-e2cmix25.gpt4o_O_pooled | 0.022 | 0.220 | 0.142 | 0.898 | 0.021 | 0.028 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_pooled | 0.083 | -0.147 | -0.079 |
| qwen3-4b-e2cmix25.deepseek_v4_O_pooled | -0.001 | 0.066 | 0.040 |
| qwen3-4b-e2cmix25.gpt4o_O_pooled | -0.063 | 0.031 | 0.012 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_pooled | 0.253 | 0.244 | 0.167 |
| qwen3-4b-e2cmix25.deepseek_v4_O_pooled | 0.178 | 0.431 | 0.261 |
| qwen3-4b-e2cmix25.gpt4o_O_pooled | 0.125 | 0.403 | 0.246 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_pooled | 0.227 | 0.055 | 0.155 |
| qwen3-4b-e2cmix25.deepseek_v4_O_pooled | 0.147 | 0.139 | 0.223 |
| qwen3-4b-e2cmix25.gpt4o_O_pooled | 0.038 | 0.077 | 0.023 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 138 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 138 | 0.047 | 0.026 | 0.071 |
| students:deepseek_v4 | 5 | 138 | 0.185 | 0.141 | 0.231 |
| students:gpt4o | 5 | 138 | 0.133 | 0.099 | 0.170 |
| teacher:claude46 | 1 | 138 | 0.052 | 0.017 | 0.089 |
| teacher:deepseek_v4 | 1 | 138 | 0.150 | 0.120 | 0.181 |
| teacher:gpt4o | 1 | 138 | 0.074 | 0.047 | 0.105 |
| base_prior | 1 | 138 | 0.164 | 0.143 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.138 | -0.178 | -0.100 |
| students:claude46 | students:gpt4o | -0.086 | -0.120 | -0.053 |
| students:claude46 | teacher:claude46 | -0.005 | -0.040 | 0.030 |
| students:claude46 | base_prior | -0.117 | -0.142 | -0.092 |
| students:deepseek_v4 | students:gpt4o | 0.052 | 0.018 | 0.087 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.035 | -0.008 | 0.082 |
| students:deepseek_v4 | base_prior | 0.021 | -0.022 | 0.066 |
| students:gpt4o | teacher:gpt4o | 0.059 | 0.020 | 0.099 |
| students:gpt4o | base_prior | -0.031 | -0.066 | 0.006 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.073 | -0.091 | 0.164 | 138 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.052 | 0.047 | 0.009 | 5 |
| deepseek_v4 | 0.150 | 0.185 | 0.008 | 5 |
| gpt4o | 0.074 | 0.133 | 0.022 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.996 | True | data/sft_e2c_mix25/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix25.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.998 | True | data/sft_e2c_mix25/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix25.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.998 | True | data/sft_e2c_mix25/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix25.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.997 | True | data/sft_e2c_mix25/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix25.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.997 | True | data/sft_e2c_mix25/claude46_O_s1.jsonl |
| qwen3-4b-e2cmix25.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix25.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix25.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix25.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.998 | True | data/sft_e2c_mix25/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix25.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cmix25.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.998 | True | data/sft_e2c_mix25/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix25.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix25.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix25.gpt4o_O_s4 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.998 | True | data/sft_e2c_mix25/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cmix25.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.999 | True | data/sft_e2c_mix25/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 53 | 50 | 5 | 265 | 0.985 | 0.962 | 1.000 | True |
| claude46 | gpt4o | 83 | 77 | 5 | 415 | 0.976 | 0.946 | 0.995 | True |
| deepseek_v4 | claude46 | 53 | 50 | 5 | 265 | 0.996 | 0.988 | 1.000 | True |
| deepseek_v4 | gpt4o | 36 | 33 | 5 | 180 | 1.000 | 1.000 | 1.000 | True |
| gpt4o | claude46 | 83 | 77 | 5 | 415 | 0.981 | 0.955 | 0.998 | True |
| gpt4o | deepseek_v4 | 36 | 33 | 5 | 180 | 0.989 | 0.965 | 1.000 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2cmix25.claude46_O_s1 | 1.000 | 0.072 | 150 | 0.842 | 0.831 | 0.127 | 0.063 | 0.026 |
| qwen3-4b-e2cmix25.claude46_O_s2 | 1.000 | 0.075 | 150 | 0.863 | 0.841 | 0.123 | 0.053 | 0.024 |
| qwen3-4b-e2cmix25.claude46_O_s3 | 1.000 | 0.076 | 150 | 0.835 | 0.815 | 0.129 | 0.067 | 0.031 |
| qwen3-4b-e2cmix25.claude46_O_s4 | 1.000 | 0.076 | 150 | 0.860 | 0.838 | 0.123 | 0.046 | 0.024 |
| qwen3-4b-e2cmix25.claude46_O_s5 | 1.000 | 0.077 | 150 | 0.842 | 0.821 | 0.135 | 0.050 | 0.028 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s1 | 1.000 | 0.075 | 150 | 0.835 | 0.824 | 0.100 | 0.103 | 0.069 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s2 | 1.000 | 0.084 | 150 | 0.825 | 0.829 | 0.097 | 0.142 | 0.068 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s3 | 1.000 | 0.089 | 150 | 0.820 | 0.812 | 0.102 | 0.116 | 0.060 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s4 | 0.999 | 0.070 | 149 | 0.823 | 0.832 | 0.104 | 0.114 | 0.067 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s5 | 1.000 | 0.062 | 150 | 0.818 | 0.829 | 0.100 | 0.099 | 0.063 |
| qwen3-4b-e2cmix25.gpt4o_O_s1 | 1.000 | 0.071 | 150 | 0.845 | 0.832 | 0.107 | 0.089 | 0.041 |
| qwen3-4b-e2cmix25.gpt4o_O_s2 | 1.000 | 0.080 | 150 | 0.852 | 0.842 | 0.111 | 0.089 | 0.048 |
| qwen3-4b-e2cmix25.gpt4o_O_s3 | 1.000 | 0.084 | 150 | 0.852 | 0.842 | 0.108 | 0.084 | 0.043 |
| qwen3-4b-e2cmix25.gpt4o_O_s4 | 1.000 | 0.091 | 150 | 0.834 | 0.837 | 0.117 | 0.089 | 0.043 |
| qwen3-4b-e2cmix25.gpt4o_O_s5 | 1.000 | 0.091 | 150 | 0.857 | 0.846 | 0.105 | 0.062 | 0.032 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2cmix25.claude46_O_s1 | 0.842 | 0.810 | 0.831 | 0.127 | 0.122 | 0.117 |
| qwen3-4b-e2cmix25.claude46_O_s2 | 0.863 | 0.815 | 0.841 | 0.123 | 0.120 | 0.117 |
| qwen3-4b-e2cmix25.claude46_O_s3 | 0.835 | 0.805 | 0.815 | 0.129 | 0.121 | 0.120 |
| qwen3-4b-e2cmix25.claude46_O_s4 | 0.860 | 0.807 | 0.838 | 0.123 | 0.124 | 0.117 |
| qwen3-4b-e2cmix25.claude46_O_s5 | 0.842 | 0.790 | 0.821 | 0.135 | 0.135 | 0.127 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s1 | 0.815 | 0.835 | 0.824 | 0.159 | 0.100 | 0.134 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s2 | 0.824 | 0.825 | 0.829 | 0.145 | 0.097 | 0.119 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s3 | 0.798 | 0.820 | 0.812 | 0.171 | 0.102 | 0.140 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s4 | 0.820 | 0.823 | 0.832 | 0.154 | 0.104 | 0.124 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s5 | 0.819 | 0.818 | 0.829 | 0.153 | 0.100 | 0.121 |
| qwen3-4b-e2cmix25.gpt4o_O_s1 | 0.829 | 0.832 | 0.845 | 0.132 | 0.096 | 0.107 |
| qwen3-4b-e2cmix25.gpt4o_O_s2 | 0.829 | 0.842 | 0.852 | 0.140 | 0.092 | 0.111 |
| qwen3-4b-e2cmix25.gpt4o_O_s3 | 0.842 | 0.829 | 0.852 | 0.132 | 0.099 | 0.108 |
| qwen3-4b-e2cmix25.gpt4o_O_s4 | 0.837 | 0.825 | 0.834 | 0.134 | 0.098 | 0.117 |
| qwen3-4b-e2cmix25.gpt4o_O_s5 | 0.840 | 0.846 | 0.857 | 0.132 | 0.095 | 0.105 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.848 | 0.829 | 0.127 | 0.056 | 0.027 |
| deepseek_v4 | O | 5 | 1.000 | 0.824 | 0.825 | 0.101 | 0.115 | 0.065 |
| gpt4o | O | 5 | 1.000 | 0.848 | 0.840 | 0.110 | 0.083 | 0.041 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_s1 | 139.000 | 0.249 | 0.095 | 0.744 | 0.088 | deepseek_v4 | 0.007 | 0.218 | -0.041 | -0.174 | 0.146 | 0.095 | 0.088 | 0.064 |
| qwen3-4b-e2cmix25.claude46_O_s2 | 139.000 | 0.272 | 0.143 | 0.744 | 0.074 | deepseek_v4 | 0.068 | 0.030 | -0.044 | -0.143 | 0.189 | 0.143 | 0.074 | 0.067 |
| qwen3-4b-e2cmix25.claude46_O_s3 | 139.000 | 0.272 | 0.166 | 0.744 | 0.095 | gpt4o | 0.070 | 0.035 | -0.042 | -0.083 | 0.197 | 0.166 | 0.048 | 0.095 |
| qwen3-4b-e2cmix25.claude46_O_s4 | 139.000 | 0.258 | 0.225 | 0.744 | 0.121 | deepseek_v4 | 0.105 | 0.007 | -0.047 | -0.056 | 0.235 | 0.225 | 0.121 | 0.083 |
| qwen3-4b-e2cmix25.claude46_O_s5 | 139.000 | 0.339 | 0.167 | 0.744 | 0.092 | deepseek_v4 | 0.076 | 0.018 | -0.051 | -0.117 | 0.202 | 0.167 | 0.092 | 0.072 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s1 | 139.000 | 0.448 | 0.156 | 0.825 | 0.065 | gpt4o | 0.091 | 0.070 | 0.011 | -0.103 | 0.255 | -0.001 | 0.156 | 0.065 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s2 | 139.000 | 0.479 | 0.230 | 0.825 | 0.103 | claude46 | 0.127 | 0.019 | 0.014 | -0.060 | 0.245 | 0.103 | 0.230 | 0.088 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s3 | 139.000 | 0.490 | 0.134 | 0.825 | 0.087 | gpt4o | 0.046 | 0.273 | 0.014 | -0.129 | 0.187 | 0.041 | 0.134 | 0.087 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s4 | 138.000 | 0.484 | 0.198 | 0.825 | 0.203 | gpt4o | -0.005 | 0.636 | 0.014 | -0.156 | 0.135 | 0.112 | 0.198 | 0.203 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s5 | 139.000 | 0.441 | 0.229 | 0.825 | 0.177 | gpt4o | 0.052 | 0.241 | 0.015 | -0.121 | 0.201 | -0.004 | 0.229 | 0.177 |
| qwen3-4b-e2cmix25.gpt4o_O_s1 | 139.000 | 0.377 | 0.057 | 0.898 | 0.180 | deepseek_v4 | -0.123 | 0.963 | -0.029 | -0.311 | 0.063 | -0.001 | 0.180 | 0.057 |
| qwen3-4b-e2cmix25.gpt4o_O_s2 | 139.000 | 0.435 | 0.065 | 0.898 | 0.191 | deepseek_v4 | -0.125 | 0.960 | -0.031 | -0.286 | 0.043 | -0.035 | 0.191 | 0.065 |
| qwen3-4b-e2cmix25.gpt4o_O_s3 | 139.000 | 0.395 | 0.147 | 0.898 | 0.153 | deepseek_v4 | -0.006 | 0.310 | -0.032 | -0.151 | 0.126 | 0.042 | 0.153 | 0.147 |
| qwen3-4b-e2cmix25.gpt4o_O_s4 | 139.000 | 0.405 | 0.181 | 0.898 | 0.246 | deepseek_v4 | -0.065 | 0.741 | -0.030 | -0.214 | 0.089 | 0.044 | 0.246 | 0.181 |
| qwen3-4b-e2cmix25.gpt4o_O_s5 | 139.000 | 0.368 | 0.190 | 0.898 | 0.209 | deepseek_v4 | -0.019 | 0.432 | -0.028 | -0.171 | 0.126 | 0.044 | 0.209 | 0.190 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | 0.065 | 0.036 | 5 |
| deepseek_v4 | 0.062 | 0.050 | 5 |
| gpt4o | -0.068 | 0.056 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.020 | 0.333 | 2 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cmix25.claude46_O_s1 | 0.150 | 0.744 | 0.205 | deepseek_v4 | -0.055 | 0.495 | -0.228 | 0.102 |
| qwen3-4b-e2cmix25.claude46_O_s2 | 0.200 | 0.744 | 0.205 | deepseek_v4 | -0.006 | 0.159 | -0.190 | 0.139 |
| qwen3-4b-e2cmix25.claude46_O_s3 | 0.221 | 0.744 | 0.184 | deepseek_v4 | 0.038 | 0.054 | -0.123 | 0.154 |
| qwen3-4b-e2cmix25.claude46_O_s4 | 0.274 | 0.744 | 0.236 | deepseek_v4 | 0.038 | 0.037 | -0.099 | 0.169 |
| qwen3-4b-e2cmix25.claude46_O_s5 | 0.235 | 0.744 | 0.253 | deepseek_v4 | -0.018 | 0.146 | -0.190 | 0.132 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s1 | 0.356 | 0.825 | 0.180 | gpt4o | 0.177 | 0.015 | 0.005 | 0.339 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s2 | 0.426 | 0.825 | 0.207 | gpt4o | 0.219 | 0.001 | 0.040 | 0.332 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s3 | 0.360 | 0.825 | 0.209 | gpt4o | 0.151 | 0.049 | -0.010 | 0.301 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s4 | 0.405 | 0.825 | 0.306 | gpt4o | 0.099 | 0.316 | -0.039 | 0.238 |
| qwen3-4b-e2cmix25.deepseek_v4_O_s5 | 0.409 | 0.825 | 0.275 | gpt4o | 0.134 | 0.114 | -0.022 | 0.281 |
| qwen3-4b-e2cmix25.gpt4o_O_s1 | 0.155 | 0.898 | 0.342 | deepseek_v4 | -0.187 | 0.990 | -0.384 | -0.003 |
| qwen3-4b-e2cmix25.gpt4o_O_s2 | 0.177 | 0.898 | 0.377 | deepseek_v4 | -0.200 | 0.990 | -0.365 | -0.034 |
| qwen3-4b-e2cmix25.gpt4o_O_s3 | 0.239 | 0.898 | 0.329 | deepseek_v4 | -0.090 | 0.541 | -0.222 | 0.033 |
| qwen3-4b-e2cmix25.gpt4o_O_s4 | 0.271 | 0.898 | 0.406 | deepseek_v4 | -0.135 | 0.854 | -0.281 | 0.015 |
| qwen3-4b-e2cmix25.gpt4o_O_s5 | 0.271 | 0.898 | 0.361 | deepseek_v4 | -0.089 | 0.627 | -0.229 | 0.046 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | 0.052 | 0.124 | 5 |
| claude46 | T1 | 0.039 | 0.116 | 5 |
| claude46 | T3 | -0.072 | 0.059 | 5 |
| claude46 | T5 | -0.018 | 0.072 | 5 |
| claude46 | T6 | 0.163 | 0.045 | 5 |
| deepseek_v4 | T0 | -0.083 | 0.057 | 5 |
| deepseek_v4 | T1 | 0.147 | 0.130 | 5 |
| deepseek_v4 | T3 | -0.052 | 0.064 | 5 |
| deepseek_v4 | T5 | 0.042 | 0.064 | 5 |
| deepseek_v4 | T6 | 0.006 | 0.066 | 5 |
| gpt4o | T0 | -0.071 | 0.072 | 5 |
| gpt4o | T1 | -0.083 | 0.093 | 5 |
| gpt4o | T3 | -0.190 | 0.059 | 5 |
| gpt4o | T5 | -0.001 | 0.083 | 5 |
| gpt4o | T6 | -0.062 | 0.051 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.315 | 0.182 | 0.744 | 0.096 | deepseek_v4 | 0.086 | -0.105 | 0.203 | 0.017 | -0.048 | 0.052 |
| deepseek_v4 | 5 | 138 | 0.515 | 0.215 | 0.825 | 0.142 | gpt4o | 0.072 | -0.104 | 0.223 | 0.167 | 0.020 | 0.334 |
| gpt4o | 5 | 139 | 0.442 | 0.142 | 0.898 | 0.221 | deepseek_v4 | -0.080 | -0.238 | 0.085 | 0.814 | -0.032 | 0.814 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.245 | 0.744 | 0.118 | 0.365 | 3 | -0.288 | -0.419 | -0.164 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.533 | 0.825 | 0.448 | 0.611 | 1 | 0.256 | 0.130 | 0.359 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.277 | 0.898 | 0.166 | 0.380 | 2 | -0.256 | -0.383 | -0.133 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 5/5 seeds pass -> ok (old rule, not the verdict)
- deepseek_v4: 2/5 seeds pass -> partial (old rule, not the verdict)
- gpt4o: 4/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 0.020 vs run-reassignment null mean -0.046 sd 0.022, p 0.001 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.333
- P2 slope 1.228, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.078 [0.011, 0.137] p 0.002 alone would read pass; the frozen rule (version 5) also needs D_specific 0.090 [0.021, 0.160] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.015 | 0.010 | 0.027 |
| agree_own | deepseek_v4 | O | 10 | 0.008 | 0.005 | 0.016 |
| agree_own | gpt4o | O | 10 | 0.010 | 0.007 | 0.020 |
| agree_own | all | all | 30 | 0.011 | 0.008 | 0.024 |
| jsd_own | claude46 | O | 10 | 0.006 | 0.004 | 0.013 |
| jsd_own | deepseek_v4 | O | 10 | 0.003 | 0.002 | 0.006 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.004 | 0.011 |
| jsd_own | all | all | 30 | 0.005 | 0.003 | 0.012 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.011 | 0.006 | 0.020 |
| flip_rate | deepseek_v4 | O | 10 | 0.020 | 0.014 | 0.041 |
| flip_rate | gpt4o | O | 10 | 0.012 | 0.012 | 0.027 |
| flip_rate | all | all | 30 | 0.014 | 0.012 | 0.034 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.003 | 0.002 | 0.006 |
| mean_jsd | deepseek_v4 | O | 10 | 0.005 | 0.003 | 0.009 |
| mean_jsd | gpt4o | O | 10 | 0.007 | 0.005 | 0.014 |
| mean_jsd | all | all | 30 | 0.005 | 0.004 | 0.012 |
| delta_rho | claude46 | O | 10 | 0.048 | 0.030 | 0.093 |
| delta_rho | deepseek_v4 | O | 10 | 0.057 | 0.031 | 0.104 |
| delta_rho | gpt4o | O | 10 | 0.064 | 0.039 | 0.110 |
| delta_rho | all | all | 30 | 0.056 | 0.033 | 0.110 |
| delta_rho_partial | claude46 | O | 10 | 0.041 | 0.032 | 0.085 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.062 | 0.036 | 0.116 |
| delta_rho_partial | gpt4o | O | 10 | 0.068 | 0.042 | 0.118 |
| delta_rho_partial | all | all | 30 | 0.057 | 0.037 | 0.118 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.