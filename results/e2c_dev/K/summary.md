# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.998, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.713 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.138 [-0.279, -0.004] p_perm 0.875 (null mean -0.076) p_holm 1.000; deepseek_v4 0.182 [0.032, 0.291] p_perm 0.019 (null mean 0.084) p_holm 0.056; gpt4o -0.151 [-0.356, 0.020] p_perm 0.958 (null mean -0.067) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.017 [-0.029, 0.067], p 0.272; D_specific 0.025 [-0.020, 0.073], D_shared -0.008 (138 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 138 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.018 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.033, sd 0.011, p 0.098, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.150 (pearson 0.956, seed-noise sd 0.015, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 2.6e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.061 [-0.217, 0.067] p_holm 1.000; deepseek_v4 0.090 [-0.076, 0.212] p_holm 0.273; gpt4o -0.069 [-0.264, 0.086] p_holm 1.000 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.009 [-0.071, 0.063], p 0.619 (136 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.018 [-0.020, 0.058], p 0.484 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.026 [-0.021, 0.076] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.116 | 0.744 | 0.156 | 0.254 | deepseek_v4 | -0.138 | -0.279 | -0.004 | 0.875 | -0.076 | 0.055 | 1.000 | False |
| deepseek_v4 | 5 | 139 | 0.455 | 0.825 | 0.552 | 0.273 | claude46 | 0.182 | 0.032 | 0.291 | 0.019 | 0.084 | 0.048 | 0.056 | False |
| gpt4o | 5 | 138 | 0.161 | 0.898 | 0.179 | 0.312 | deepseek_v4 | -0.151 | -0.356 | 0.020 | 0.958 | -0.067 | 0.048 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.038 | -0.055 | 0.011 | 0.056 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.017 | -0.029 | 0.067 | 0.272 | 0.005 | 0.021 | 0.018 | 138 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.008 | 0.025 | -0.020 | 0.073 | 0.184 | 0.006 | 0.022 | 0.026 | -0.021 | 0.076 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2ck.claude46_O_pooled 0.083, qwen3-4b-e2ck.deepseek_v4_O_pooled 0.113, qwen3-4b-e2ck.gpt4o_O_pooled 0.086.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | 0.046 | 0.111 | 0.028 | 0.744 | -0.024 | 0.014 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.179 | 0.267 | 0.150 | 0.825 | 0.102 | 0.031 |
| qwen3-4b-e2ck.gpt4o_O_pooled | 0.034 | 0.117 | 0.048 | 0.898 | -0.027 | 0.030 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | -0.062 | -0.087 | -0.066 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.100 | 0.121 | 0.081 |
| qwen3-4b-e2ck.gpt4o_O_pooled | -0.071 | -0.075 | -0.043 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | 0.117 | 0.261 | 0.117 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.260 | 0.441 | 0.256 |
| qwen3-4b-e2ck.gpt4o_O_pooled | 0.127 | 0.312 | 0.161 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | 0.071 | -0.023 | 0.227 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.108 | -0.008 | 0.069 |
| qwen3-4b-e2ck.gpt4o_O_pooled | -0.079 | 0.047 | 0.085 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 138 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 138 | 0.059 | 0.037 | 0.085 |
| students:deepseek_v4 | 5 | 138 | 0.164 | 0.124 | 0.206 |
| students:gpt4o | 5 | 138 | 0.089 | 0.062 | 0.121 |
| teacher:claude46 | 1 | 138 | 0.056 | 0.019 | 0.094 |
| teacher:deepseek_v4 | 1 | 138 | 0.144 | 0.116 | 0.174 |
| teacher:gpt4o | 1 | 138 | 0.076 | 0.049 | 0.106 |
| base_prior | 1 | 138 | 0.163 | 0.143 | 0.185 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.104 | -0.136 | -0.076 |
| students:claude46 | students:gpt4o | -0.030 | -0.054 | -0.008 |
| students:claude46 | teacher:claude46 | 0.003 | -0.038 | 0.045 |
| students:claude46 | base_prior | -0.104 | -0.131 | -0.077 |
| students:deepseek_v4 | students:gpt4o | 0.074 | 0.044 | 0.106 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.019 | -0.020 | 0.059 |
| students:deepseek_v4 | base_prior | 2.9e-04 | -0.039 | 0.041 |
| students:gpt4o | teacher:gpt4o | 0.014 | -0.024 | 0.051 |
| students:gpt4o | base_prior | -0.074 | -0.103 | -0.044 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.090 | 0.163 | 138 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.056 | 0.059 | 0.014 | 5 |
| deepseek_v4 | 0.144 | 0.164 | 0.017 | 5 |
| gpt4o | 0.076 | 0.089 | 0.013 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_s1 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.999 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| qwen3-4b-e2ck.claude46_O_s2 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.999 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| qwen3-4b-e2ck.claude46_O_s3 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.999 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| qwen3-4b-e2ck.claude46_O_s4 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.999 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| qwen3-4b-e2ck.claude46_O_s5 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.999 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 1.000 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.998 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2ck.gpt4o_O_s1 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.998 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ck.gpt4o_O_s2 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.999 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ck.gpt4o_O_s3 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.999 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ck.gpt4o_O_s4 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.999 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| qwen3-4b-e2ck.gpt4o_O_s5 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.998 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 24 | 23 | 5 | 120 | 0.883 | 0.793 | 0.958 | True |
| claude46 | gpt4o | 38 | 35 | 5 | 190 | 0.884 | 0.810 | 0.954 | True |
| deepseek_v4 | claude46 | 24 | 23 | 5 | 120 | 0.833 | 0.713 | 0.933 | True |
| deepseek_v4 | gpt4o | 23 | 23 | 5 | 115 | 0.922 | 0.870 | 0.974 | True |
| gpt4o | claude46 | 38 | 35 | 5 | 190 | 0.868 | 0.784 | 0.939 | True |
| gpt4o | deepseek_v4 | 23 | 23 | 5 | 115 | 0.843 | 0.730 | 0.948 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2ck.claude46_O_s1 | 1.000 | 0.067 | 150 | 0.824 | 0.824 | 0.145 | 0.056 | 0.029 |
| qwen3-4b-e2ck.claude46_O_s2 | 1.000 | 0.063 | 150 | 0.835 | 0.833 | 0.143 | 0.057 | 0.028 |
| qwen3-4b-e2ck.claude46_O_s3 | 1.000 | 0.065 | 150 | 0.817 | 0.803 | 0.158 | 0.056 | 0.030 |
| qwen3-4b-e2ck.claude46_O_s4 | 1.000 | 0.072 | 150 | 0.833 | 0.841 | 0.141 | 0.058 | 0.033 |
| qwen3-4b-e2ck.claude46_O_s5 | 1.000 | 0.070 | 150 | 0.822 | 0.810 | 0.150 | 0.068 | 0.032 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 1.000 | 0.059 | 150 | 0.803 | 0.824 | 0.112 | 0.099 | 0.065 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 1.000 | 0.068 | 150 | 0.834 | 0.836 | 0.098 | 0.097 | 0.062 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 0.999 | 0.068 | 150 | 0.797 | 0.815 | 0.113 | 0.112 | 0.076 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 0.999 | 0.083 | 150 | 0.832 | 0.848 | 0.102 | 0.093 | 0.054 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 1.000 | 0.082 | 150 | 0.810 | 0.828 | 0.109 | 0.086 | 0.050 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 0.999 | 0.063 | 150 | 0.862 | 0.847 | 0.107 | 0.069 | 0.034 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 1.000 | 0.074 | 150 | 0.829 | 0.824 | 0.114 | 0.086 | 0.038 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 0.998 | 0.072 | 149 | 0.827 | 0.820 | 0.126 | 0.068 | 0.028 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 1.000 | 0.066 | 150 | 0.828 | 0.833 | 0.124 | 0.073 | 0.039 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 1.000 | 0.059 | 150 | 0.847 | 0.849 | 0.108 | 0.072 | 0.029 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2ck.claude46_O_s1 | 0.824 | 0.812 | 0.824 | 0.145 | 0.118 | 0.136 |
| qwen3-4b-e2ck.claude46_O_s2 | 0.835 | 0.827 | 0.833 | 0.143 | 0.112 | 0.127 |
| qwen3-4b-e2ck.claude46_O_s3 | 0.817 | 0.792 | 0.803 | 0.158 | 0.124 | 0.147 |
| qwen3-4b-e2ck.claude46_O_s4 | 0.833 | 0.822 | 0.841 | 0.141 | 0.103 | 0.117 |
| qwen3-4b-e2ck.claude46_O_s5 | 0.822 | 0.799 | 0.810 | 0.150 | 0.114 | 0.140 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 0.824 | 0.803 | 0.815 | 0.144 | 0.112 | 0.132 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 0.835 | 0.834 | 0.836 | 0.138 | 0.098 | 0.116 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 0.815 | 0.797 | 0.798 | 0.148 | 0.113 | 0.146 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 0.847 | 0.832 | 0.848 | 0.131 | 0.102 | 0.113 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 0.824 | 0.810 | 0.828 | 0.137 | 0.109 | 0.124 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 0.847 | 0.845 | 0.862 | 0.136 | 0.101 | 0.107 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 0.824 | 0.817 | 0.829 | 0.143 | 0.104 | 0.114 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 0.820 | 0.809 | 0.827 | 0.149 | 0.110 | 0.126 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 0.833 | 0.808 | 0.828 | 0.141 | 0.104 | 0.124 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 0.849 | 0.824 | 0.847 | 0.132 | 0.099 | 0.108 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.826 | 0.822 | 0.147 | 0.059 | 0.030 |
| deepseek_v4 | O | 5 | 1.000 | 0.815 | 0.830 | 0.107 | 0.097 | 0.061 |
| gpt4o | O | 5 | 0.999 | 0.839 | 0.835 | 0.116 | 0.074 | 0.034 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_s1 | 139.000 | 0.262 | -0.007 | 0.744 | 0.096 | deepseek_v4 | -0.103 | 0.863 | -0.041 | -0.264 | 0.047 | -0.007 | 0.096 | -0.021 |
| qwen3-4b-e2ck.claude46_O_s2 | 139.000 | 0.247 | 0.028 | 0.744 | 0.111 | deepseek_v4 | -0.082 | 0.749 | -0.045 | -0.238 | 0.050 | 0.028 | 0.111 | 0.064 |
| qwen3-4b-e2ck.claude46_O_s3 | 139.000 | 0.274 | 0.128 | 0.744 | 0.075 | gpt4o | 0.054 | 0.045 | -0.047 | -0.128 | 0.154 | 0.128 | 0.070 | 0.075 |
| qwen3-4b-e2ck.claude46_O_s4 | 139.000 | 0.298 | -0.020 | 0.744 | 0.078 | deepseek_v4 | -0.099 | 0.797 | -0.048 | -0.247 | 0.011 | -0.020 | 0.078 | -0.022 |
| qwen3-4b-e2ck.claude46_O_s5 | 139.000 | 0.343 | 0.041 | 0.744 | 0.083 | deepseek_v4 | -0.042 | 0.433 | -0.053 | -0.230 | 0.088 | 0.041 | 0.083 | 0.035 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 139.000 | 0.472 | 0.242 | 0.825 | 0.182 | claude46 | 0.060 | 0.187 | 0.011 | -0.108 | 0.208 | 0.182 | 0.242 | 0.071 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 139.000 | 0.450 | 0.290 | 0.825 | 0.163 | gpt4o | 0.127 | 0.019 | 0.011 | -0.024 | 0.255 | 0.093 | 0.290 | 0.163 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 139.000 | 0.406 | 0.243 | 0.825 | 0.191 | claude46 | 0.052 | 0.256 | 0.015 | -0.119 | 0.179 | 0.191 | 0.243 | 0.150 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 139.000 | 0.396 | 0.230 | 0.825 | 0.176 | claude46 | 0.055 | 0.211 | 0.010 | -0.108 | 0.180 | 0.176 | 0.230 | 0.134 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 139.000 | 0.397 | 0.210 | 0.825 | 0.176 | claude46 | 0.034 | 0.365 | 0.013 | -0.120 | 0.149 | 0.176 | 0.210 | 0.128 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 139.000 | 0.354 | 0.102 | 0.898 | 0.138 | deepseek_v4 | -0.036 | 0.558 | -0.028 | -0.188 | 0.102 | 0.045 | 0.138 | 0.102 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 139.000 | 0.387 | 0.044 | 0.898 | 0.094 | deepseek_v4 | -0.050 | 0.638 | -0.030 | -0.243 | 0.102 | 0.046 | 0.094 | 0.044 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 138.000 | 0.406 | -0.006 | 0.898 | 0.106 | deepseek_v4 | -0.111 | 0.948 | -0.030 | -0.342 | 0.069 | 0.003 | 0.106 | -0.006 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 139.000 | 0.390 | 0.025 | 0.898 | 0.093 | deepseek_v4 | -0.068 | 0.775 | -0.028 | -0.234 | 0.062 | 0.059 | 0.093 | 0.025 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 139.000 | 0.357 | 0.031 | 0.898 | 0.092 | deepseek_v4 | -0.062 | 0.753 | -0.027 | -0.267 | 0.130 | -0.012 | 0.092 | 0.031 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.054 | 0.065 | 5 |
| deepseek_v4 | 0.066 | 0.036 | 5 |
| gpt4o | -0.065 | 0.029 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.018 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_s1 | 0.057 | 0.744 | 0.218 | deepseek_v4 | -0.160 | 0.974 | -0.303 | -0.022 |
| qwen3-4b-e2ck.claude46_O_s2 | 0.087 | 0.744 | 0.223 | deepseek_v4 | -0.135 | 0.905 | -0.282 | 0.012 |
| qwen3-4b-e2ck.claude46_O_s3 | 0.187 | 0.744 | 0.203 | deepseek_v4 | -0.016 | 0.185 | -0.183 | 0.116 |
| qwen3-4b-e2ck.claude46_O_s4 | 0.054 | 0.744 | 0.222 | deepseek_v4 | -0.168 | 0.949 | -0.278 | -0.072 |
| qwen3-4b-e2ck.claude46_O_s5 | 0.121 | 0.744 | 0.248 | deepseek_v4 | -0.128 | 0.787 | -0.293 | 0.021 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 0.432 | 0.825 | 0.271 | claude46 | 0.161 | 0.040 | 0.012 | 0.295 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 0.459 | 0.825 | 0.265 | gpt4o | 0.194 | 0.007 | 0.062 | 0.309 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 0.404 | 0.825 | 0.269 | claude46 | 0.135 | 0.113 | -0.015 | 0.241 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 0.390 | 0.825 | 0.253 | claude46 | 0.137 | 0.085 | -0.007 | 0.251 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 0.375 | 0.825 | 0.254 | claude46 | 0.121 | 0.190 | -0.012 | 0.219 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 0.190 | 0.898 | 0.298 | deepseek_v4 | -0.108 | 0.836 | -0.241 | 0.032 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 0.146 | 0.898 | 0.280 | deepseek_v4 | -0.134 | 0.905 | -0.342 | 0.044 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 0.108 | 0.898 | 0.294 | deepseek_v4 | -0.185 | 0.996 | -0.418 | 0.016 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 0.130 | 0.898 | 0.281 | deepseek_v4 | -0.150 | 0.957 | -0.318 | 0.003 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 0.127 | 0.898 | 0.263 | deepseek_v4 | -0.137 | 0.950 | -0.356 | 0.054 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.122 | 0.074 | 5 |
| claude46 | T1 | -0.104 | 0.118 | 5 |
| claude46 | T3 | -0.116 | 0.103 | 5 |
| claude46 | T5 | -0.147 | 0.104 | 5 |
| claude46 | T6 | -0.021 | 0.083 | 5 |
| deepseek_v4 | T0 | -0.112 | 0.078 | 5 |
| deepseek_v4 | T1 | -0.206 | 0.034 | 5 |
| deepseek_v4 | T3 | 0.102 | 0.157 | 5 |
| deepseek_v4 | T5 | 0.090 | 0.061 | 5 |
| deepseek_v4 | T6 | 0.043 | 0.072 | 5 |
| gpt4o | T0 | 0.035 | 0.053 | 5 |
| gpt4o | T1 | 0.035 | 0.031 | 5 |
| gpt4o | T3 | -0.160 | 0.110 | 5 |
| gpt4o | T5 | -0.121 | 0.068 | 5 |
| gpt4o | T6 | -0.067 | 0.026 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.326 | 0.040 | 0.744 | 0.100 | deepseek_v4 | -0.061 | -0.217 | 0.067 | 0.585 | -0.050 | 1.000 |
| deepseek_v4 | 5 | 139 | 0.469 | 0.275 | 0.825 | 0.185 | claude46 | 0.090 | -0.076 | 0.212 | 0.091 | 0.016 | 0.273 |
| gpt4o | 5 | 138 | 0.426 | 0.048 | 0.898 | 0.117 | deepseek_v4 | -0.069 | -0.264 | 0.086 | 0.771 | -0.031 | 1.000 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.245 | 0.744 | 0.118 | 0.365 | 3 | -0.288 | -0.419 | -0.164 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.533 | 0.825 | 0.448 | 0.611 | 1 | 0.256 | 0.130 | 0.359 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.277 | 0.898 | 0.166 | 0.380 | 2 | -0.256 | -0.383 | -0.133 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 4/5 seeds pass -> partial (old rule, not the verdict)
- deepseek_v4: 0/5 seeds pass -> fail (old rule, not the verdict)
- gpt4o: 3/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial -0.018 vs run-reassignment null mean -0.033 sd 0.011, p 0.098 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 1.150, run-reassignment p 2.6e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.017 [-0.029, 0.067] p 0.272 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.025 [-0.020, 0.073] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.009 | 0.005 | 0.017 |
| agree_own | deepseek_v4 | O | 10 | 0.021 | 0.013 | 0.036 |
| agree_own | gpt4o | O | 10 | 0.018 | 0.013 | 0.035 |
| agree_own | all | all | 30 | 0.016 | 0.012 | 0.035 |
| jsd_own | claude46 | O | 10 | 0.009 | 0.006 | 0.017 |
| jsd_own | deepseek_v4 | O | 10 | 0.008 | 0.005 | 0.014 |
| jsd_own | gpt4o | O | 10 | 0.011 | 0.007 | 0.018 |
| jsd_own | all | all | 30 | 0.009 | 0.006 | 0.018 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.005 | 0.005 | 0.012 |
| flip_rate | deepseek_v4 | O | 10 | 0.012 | 0.008 | 0.023 |
| flip_rate | gpt4o | O | 10 | 0.008 | 0.006 | 0.017 |
| flip_rate | all | all | 30 | 0.008 | 0.007 | 0.018 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.002 | 0.001 | 0.004 |
| mean_jsd | deepseek_v4 | O | 10 | 0.013 | 0.007 | 0.025 |
| mean_jsd | gpt4o | O | 10 | 0.006 | 0.004 | 0.010 |
| mean_jsd | all | all | 30 | 0.007 | 0.006 | 0.019 |
| delta_rho | claude46 | O | 10 | 0.067 | 0.057 | 0.148 |
| delta_rho | deepseek_v4 | O | 10 | 0.035 | 0.023 | 0.067 |
| delta_rho | gpt4o | O | 10 | 0.034 | 0.022 | 0.066 |
| delta_rho | all | all | 30 | 0.045 | 0.040 | 0.133 |
| delta_rho_partial | claude46 | O | 10 | 0.074 | 0.058 | 0.155 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.039 | 0.034 | 0.085 |
| delta_rho_partial | gpt4o | O | 10 | 0.034 | 0.023 | 0.069 |
| delta_rho_partial | all | all | 30 | 0.049 | 0.043 | 0.145 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.