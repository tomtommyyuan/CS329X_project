# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.998, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.696 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.100 [-0.208, -0.009] p_perm 0.965 (null mean -0.027) p_holm 1.000; deepseek_v4 0.128 [0.026, 0.229] p_perm 0.027 (null mean 0.061) p_holm 0.081; gpt4o -0.044 [-0.144, 0.054] p_perm 0.543 (null mean -0.040) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.049 [0.014, 0.082], p 0.013; D_specific 0.068 [0.032, 0.104], D_shared -0.020 (290 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 290 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = smollm3-3b.base_B_s0) | 8.9e-04 | teacher-level exact p 0.333 (rank 2 of 6 relabellings, floor 0.167); the run-level null (mean -0.042, sd 0.017, p 0.004, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.533 (pearson 0.852, seed-noise sd 0.027, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 4.0e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.094 [-0.205, 9.5e-04] p_holm 0.962; deepseek_v4 0.116 [0.008, 0.219] p_holm 0.068; gpt4o -0.022 [-0.122, 0.075] p_holm 0.833 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.017 [-0.045, 0.074], p 0.229 (288 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.049 [0.015, 0.082], p 0.031 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.067 [0.034, 0.098] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.250 [0.185, 0.314], margin over the next 0.076 [-3.7e-04, 0.152] (290 families) | control holds (no teacher preferred before training) |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.041 | 0.704 | 0.058 | 0.141 | gpt4o | -0.100 | -0.208 | -0.009 | 0.965 | -0.027 | 0.040 | 1.000 | False |
| deepseek_v4 | 5 | 290 | 0.408 | 0.797 | 0.512 | 0.280 | gpt4o | 0.128 | 0.026 | 0.229 | 0.027 | 0.061 | 0.036 | 0.081 | False |
| gpt4o | 5 | 290 | 0.194 | 0.904 | 0.215 | 0.238 | deepseek_v4 | -0.044 | -0.144 | 0.054 | 0.543 | -0.040 | 0.039 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.003 | -0.048 | 0.017 | 0.003 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = smollm3-3b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.049 | 0.014 | 0.082 | 0.013 | 0.015 | 0.015 | 0.049 | 290 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.020 | 0.068 | 0.032 | 0.104 | 1.0e-03 | 0.019 | 0.016 | 0.067 | 0.034 | 0.098 |

Row scales (sd of each pooled student's residual given r_0): smollm3-3b-e2ck.claude46_O_pooled 0.063, smollm3-3b-e2ck.deepseek_v4_O_pooled 0.105, smollm3-3b-e2ck.gpt4o_O_pooled 0.084.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | 0.026 | 0.054 | 0.120 | 0.704 | -0.061 | 0.100 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | 0.133 | 0.354 | 0.239 | 0.797 | 0.169 | 0.097 |
| smollm3-3b-e2ck.gpt4o_O_pooled | 0.047 | 0.167 | 0.145 | 0.904 | 0.038 | 0.008 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | -0.077 | -0.236 | -0.118 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | 0.071 | 0.181 | 0.096 |
| smollm3-3b-e2ck.gpt4o_O_pooled | -0.030 | -0.049 | -0.032 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | 0.041 | 0.087 | 0.141 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | 0.162 | 0.408 | 0.280 |
| smollm3-3b-e2ck.gpt4o_O_pooled | 0.082 | 0.238 | 0.194 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | -0.057 | 0.342 | -0.098 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | -7.3e-04 | 0.359 | -0.039 |
| smollm3-3b-e2ck.gpt4o_O_pooled | 0.004 | 0.298 | 4.2e-04 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 290 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 290 | 0.012 | 0.003 | 0.022 |
| students:deepseek_v4 | 5 | 290 | 0.126 | 0.103 | 0.150 |
| students:gpt4o | 5 | 290 | 0.071 | 0.054 | 0.089 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |
| base_prior | 1 | 290 | 0.084 | 0.079 | 0.090 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.114 | -0.136 | -0.092 |
| students:claude46 | students:gpt4o | -0.059 | -0.074 | -0.044 |
| students:claude46 | teacher:claude46 | -0.032 | -0.056 | -0.010 |
| students:claude46 | base_prior | -0.072 | -0.082 | -0.061 |
| students:deepseek_v4 | students:gpt4o | 0.055 | 0.039 | 0.072 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.013 | -0.011 | 0.037 |
| students:deepseek_v4 | base_prior | 0.042 | 0.018 | 0.066 |
| students:gpt4o | teacher:gpt4o | 0.008 | -0.016 | 0.032 |
| students:gpt4o | base_prior | -0.013 | -0.030 | 0.004 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | base_prior | 0.055 | -0.029 | 0.084 | 290 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.012 | 0.008 | 5 |
| deepseek_v4 | 0.113 | 0.126 | 0.040 | 5 |
| gpt4o | 0.063 | 0.071 | 0.023 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.998 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| smollm3-3b-e2ck.claude46_O_s2 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.998 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| smollm3-3b-e2ck.claude46_O_s3 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.998 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| smollm3-3b-e2ck.claude46_O_s4 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.998 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| smollm3-3b-e2ck.claude46_O_s5 | 5836 | 1.000 | 5836 | 5836 | 0 | 0 | 0.999 | True | data/sft_e2ck/claude46_O_s1.jsonl |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.999 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 5370 | 1.000 | 5370 | 5370 | 0 | 0 | 0.998 | True | data/sft_e2ck/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2ck.gpt4o_O_s1 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.998 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| smollm3-3b-e2ck.gpt4o_O_s2 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.998 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| smollm3-3b-e2ck.gpt4o_O_s3 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.999 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| smollm3-3b-e2ck.gpt4o_O_s4 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.998 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |
| smollm3-3b-e2ck.gpt4o_O_s5 | 5874 | 1.000 | 5874 | 5874 | 0 | 0 | 0.999 | True | data/sft_e2ck/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 24 | 23 | 5 | 120 | 0.842 | 0.723 | 0.948 | True |
| claude46 | gpt4o | 38 | 35 | 5 | 190 | 0.842 | 0.756 | 0.922 | True |
| deepseek_v4 | claude46 | 24 | 23 | 5 | 120 | 0.833 | 0.713 | 0.931 | True |
| deepseek_v4 | gpt4o | 23 | 23 | 5 | 115 | 0.852 | 0.739 | 0.948 | True |
| gpt4o | claude46 | 38 | 35 | 5 | 190 | 0.811 | 0.705 | 0.905 | True |
| gpt4o | deepseek_v4 | 23 | 23 | 5 | 115 | 0.826 | 0.696 | 0.939 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 1.000 | 0.067 | 300 | 0.874 | 0.866 | 0.119 | 0.038 | 0.018 |
| smollm3-3b-e2ck.claude46_O_s2 | 1.000 | 0.065 | 300 | 0.866 | 0.863 | 0.122 | 0.041 | 0.017 |
| smollm3-3b-e2ck.claude46_O_s3 | 1.000 | 0.064 | 300 | 0.862 | 0.856 | 0.121 | 0.050 | 0.019 |
| smollm3-3b-e2ck.claude46_O_s4 | 1.000 | 0.065 | 300 | 0.860 | 0.851 | 0.126 | 0.044 | 0.018 |
| smollm3-3b-e2ck.claude46_O_s5 | 1.000 | 0.059 | 300 | 0.866 | 0.874 | 0.126 | 0.039 | 0.017 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 1.000 | 0.077 | 300 | 0.845 | 0.857 | 0.088 | 0.112 | 0.068 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 1.000 | 0.069 | 300 | 0.862 | 0.869 | 0.088 | 0.065 | 0.035 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 1.000 | 0.086 | 300 | 0.845 | 0.851 | 0.090 | 0.087 | 0.050 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 1.000 | 0.063 | 300 | 0.842 | 0.853 | 0.096 | 0.094 | 0.048 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 1.000 | 0.061 | 300 | 0.858 | 0.859 | 0.087 | 0.070 | 0.036 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 1.000 | 0.079 | 300 | 0.846 | 0.856 | 0.118 | 0.056 | 0.028 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 1.000 | 0.080 | 300 | 0.845 | 0.847 | 0.115 | 0.066 | 0.037 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 1.000 | 0.083 | 300 | 0.859 | 0.861 | 0.110 | 0.063 | 0.033 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 1.000 | 0.083 | 300 | 0.848 | 0.848 | 0.117 | 0.057 | 0.035 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 1.000 | 0.059 | 300 | 0.859 | 0.851 | 0.104 | 0.051 | 0.026 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 0.874 | 0.863 | 0.866 | 0.119 | 0.091 | 0.106 |
| smollm3-3b-e2ck.claude46_O_s2 | 0.866 | 0.862 | 0.863 | 0.122 | 0.094 | 0.112 |
| smollm3-3b-e2ck.claude46_O_s3 | 0.862 | 0.851 | 0.856 | 0.121 | 0.094 | 0.113 |
| smollm3-3b-e2ck.claude46_O_s4 | 0.860 | 0.850 | 0.851 | 0.126 | 0.100 | 0.121 |
| smollm3-3b-e2ck.claude46_O_s5 | 0.866 | 0.853 | 0.874 | 0.126 | 0.097 | 0.106 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 0.857 | 0.845 | 0.851 | 0.123 | 0.088 | 0.109 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 0.869 | 0.862 | 0.867 | 0.120 | 0.088 | 0.106 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 0.849 | 0.845 | 0.851 | 0.131 | 0.090 | 0.115 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 0.853 | 0.842 | 0.850 | 0.131 | 0.096 | 0.118 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 0.859 | 0.858 | 0.851 | 0.125 | 0.087 | 0.115 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 0.856 | 0.843 | 0.846 | 0.130 | 0.101 | 0.118 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 0.838 | 0.847 | 0.845 | 0.139 | 0.096 | 0.115 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 0.861 | 0.852 | 0.859 | 0.126 | 0.091 | 0.110 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 0.848 | 0.845 | 0.848 | 0.138 | 0.096 | 0.117 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 0.851 | 0.840 | 0.859 | 0.130 | 0.100 | 0.104 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| claude46 | O | 5 | 1.000 | 0.865 | 0.862 | 0.123 | 0.042 | 0.018 |
| deepseek_v4 | O | 5 | 1.000 | 0.850 | 0.858 | 0.090 | 0.086 | 0.048 |
| gpt4o | O | 5 | 1.000 | 0.852 | 0.853 | 0.113 | 0.058 | 0.032 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = smollm3-3b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 290.000 | 0.120 | 0.015 | 0.704 | 0.091 | gpt4o | -0.076 | 0.949 | -0.011 | -0.178 | 0.022 | 0.015 | -0.003 | 0.091 |
| smollm3-3b-e2ck.claude46_O_s2 | 290.000 | 0.106 | 0.014 | 0.704 | 0.094 | gpt4o | -0.080 | 0.938 | -0.018 | -0.214 | 0.034 | 0.014 | 0.017 | 0.094 |
| smollm3-3b-e2ck.claude46_O_s3 | 290.000 | 0.120 | 0.027 | 0.704 | 0.112 | gpt4o | -0.085 | 0.959 | -0.015 | -0.202 | -0.003 | 0.027 | 0.088 | 0.112 |
| smollm3-3b-e2ck.claude46_O_s4 | 290.000 | 0.091 | 0.013 | 0.704 | 0.076 | gpt4o | -0.062 | 0.838 | -0.023 | -0.174 | 0.015 | 0.013 | 0.064 | 0.076 |
| smollm3-3b-e2ck.claude46_O_s5 | 290.000 | 0.150 | 0.040 | 0.704 | 0.132 | gpt4o | -0.092 | 0.908 | -0.036 | -0.189 | -0.005 | 0.040 | 0.059 | 0.132 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 290.000 | 0.333 | 0.375 | 0.797 | 0.269 | gpt4o | 0.105 | 0.065 | 0.050 | 0.005 | 0.206 | 0.116 | 0.375 | 0.269 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 290.000 | 0.254 | 0.289 | 0.797 | 0.186 | gpt4o | 0.103 | 0.034 | 0.033 | -0.005 | 0.196 | 0.129 | 0.289 | 0.186 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 290.000 | 0.323 | 0.305 | 0.797 | 0.178 | gpt4o | 0.127 | 0.005 | 0.032 | 0.026 | 0.229 | 0.088 | 0.305 | 0.178 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 290.000 | 0.323 | 0.305 | 0.797 | 0.192 | gpt4o | 0.112 | 0.034 | 0.044 | 0.001 | 0.221 | 0.092 | 0.305 | 0.192 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 290.000 | 0.272 | 0.253 | 0.797 | 0.202 | gpt4o | 0.051 | 0.187 | 0.018 | -0.069 | 0.141 | 0.161 | 0.253 | 0.202 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 290.000 | 0.267 | 0.085 | 0.904 | 0.064 | deepseek_v4 | 0.021 | 0.144 | -0.019 | -0.067 | 0.092 | 0.028 | 0.064 | 0.085 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 290.000 | 0.339 | 0.134 | 0.904 | 0.175 | deepseek_v4 | -0.040 | 0.610 | -0.029 | -0.134 | 0.054 | 0.024 | 0.175 | 0.134 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 290.000 | 0.312 | 0.148 | 0.904 | 0.193 | deepseek_v4 | -0.044 | 0.565 | -0.038 | -0.150 | 0.059 | 0.063 | 0.193 | 0.148 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 290.000 | 0.338 | 0.141 | 0.904 | 0.141 | deepseek_v4 | -4.6e-04 | 0.237 | -0.028 | -0.104 | 0.100 | 0.046 | 0.141 | 0.141 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 290.000 | 0.240 | 0.110 | 0.904 | 0.135 | deepseek_v4 | -0.025 | 0.522 | -0.023 | -0.140 | 0.086 | 0.040 | 0.135 | 0.110 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.079 | 0.011 | 5 |
| deepseek_v4 | 0.100 | 0.029 | 5 |
| gpt4o | -0.018 | 0.028 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 8.9e-04 | 0.333 | 2 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 0.028 | 0.704 | 0.110 | gpt4o | -0.082 | 0.956 | -0.181 | 0.015 |
| smollm3-3b-e2ck.claude46_O_s2 | 0.026 | 0.704 | 0.111 | gpt4o | -0.085 | 0.941 | -0.214 | 0.023 |
| smollm3-3b-e2ck.claude46_O_s3 | 0.040 | 0.704 | 0.131 | gpt4o | -0.090 | 0.962 | -0.206 | -0.011 |
| smollm3-3b-e2ck.claude46_O_s4 | 0.023 | 0.704 | 0.090 | gpt4o | -0.067 | 0.855 | -0.181 | 0.008 |
| smollm3-3b-e2ck.claude46_O_s5 | 0.056 | 0.704 | 0.154 | gpt4o | -0.099 | 0.910 | -0.196 | -0.012 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 0.425 | 0.797 | 0.308 | gpt4o | 0.117 | 0.080 | 0.019 | 0.218 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 0.334 | 0.797 | 0.221 | gpt4o | 0.113 | 0.037 | 0.008 | 0.209 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 0.360 | 0.797 | 0.222 | gpt4o | 0.138 | 0.006 | 0.040 | 0.239 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 0.360 | 0.797 | 0.235 | gpt4o | 0.125 | 0.035 | 0.019 | 0.230 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 0.303 | 0.797 | 0.239 | gpt4o | 0.065 | 0.190 | -0.050 | 0.159 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 0.127 | 0.904 | 0.126 | deepseek_v4 | 5.8e-04 | 0.257 | -0.087 | 0.079 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 0.183 | 0.904 | 0.244 | deepseek_v4 | -0.060 | 0.711 | -0.153 | 0.033 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 0.193 | 0.904 | 0.255 | deepseek_v4 | -0.062 | 0.635 | -0.168 | 0.042 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 0.189 | 0.904 | 0.213 | deepseek_v4 | -0.024 | 0.359 | -0.125 | 0.077 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 0.147 | 0.904 | 0.187 | deepseek_v4 | -0.040 | 0.640 | -0.154 | 0.073 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.340 | 0.056 | 5 |
| claude46 | T1 | 0.009 | 0.063 | 5 |
| claude46 | T3 | -0.245 | 0.058 | 5 |
| claude46 | T5 | -0.153 | 0.034 | 5 |
| claude46 | T6 | -0.018 | 0.018 | 5 |
| deepseek_v4 | T0 | 0.310 | 0.031 | 5 |
| deepseek_v4 | T1 | 0.134 | 0.058 | 5 |
| deepseek_v4 | T3 | -0.022 | 0.055 | 5 |
| deepseek_v4 | T5 | 0.119 | 0.076 | 5 |
| deepseek_v4 | T6 | 0.093 | 0.057 | 5 |
| gpt4o | T0 | -0.256 | 0.094 | 5 |
| gpt4o | T1 | -0.085 | 0.057 | 5 |
| gpt4o | T3 | 8.0e-04 | 0.030 | 5 |
| gpt4o | T5 | -0.085 | 0.040 | 5 |
| gpt4o | T6 | 0.043 | 0.036 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.139 | 0.026 | 0.704 | 0.120 | gpt4o | -0.094 | -0.205 | 9.5e-04 | 0.962 | -0.022 | 0.962 |
| deepseek_v4 | 5 | 290 | 0.344 | 0.354 | 0.797 | 0.239 | gpt4o | 0.116 | 0.008 | 0.219 | 0.023 | 0.043 | 0.068 |
| gpt4o | 5 | 290 | 0.346 | 0.145 | 0.904 | 0.167 | deepseek_v4 | -0.022 | -0.122 | 0.075 | 0.417 | -0.030 | 0.833 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | ungated covariate profile | claude46 | 290 | 0.111 | 0.704 | 0.037 | 0.182 | 3 | -0.138 | -0.232 | -0.053 |
| smollm3-3b.base_B_s0 | ungated covariate profile | deepseek_v4 | 290 | 0.250 | 0.797 | 0.185 | 0.314 | 1 | 0.076 | -3.7e-04 | 0.152 |
| smollm3-3b.base_B_s0 | ungated covariate profile | gpt4o | 290 | 0.174 | 0.904 | 0.114 | 0.233 | 2 | -0.076 | -0.155 | -3.4e-04 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 4/5 seeds pass -> partial (old rule, not the verdict)
- deepseek_v4: 0/5 seeds pass -> fail (old rule, not the verdict)
- gpt4o: 1/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 8.9e-04 vs run-reassignment null mean -0.042 sd 0.017, p 0.004 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.333
- P2 slope 1.533, run-reassignment p 4.0e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.049 [0.014, 0.082] p 0.013 alone would read pass; the frozen rule (version 5) also needs D_specific 0.068 [0.032, 0.104] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.006 | 0.004 | 0.013 |
| agree_own | deepseek_v4 | O | 10 | 0.011 | 0.007 | 0.019 |
| agree_own | gpt4o | O | 10 | 0.008 | 0.006 | 0.014 |
| agree_own | all | all | 30 | 0.008 | 0.006 | 0.017 |
| jsd_own | claude46 | O | 10 | 0.004 | 0.002 | 0.007 |
| jsd_own | deepseek_v4 | O | 10 | 0.004 | 0.003 | 0.008 |
| jsd_own | gpt4o | O | 10 | 0.007 | 0.004 | 0.013 |
| jsd_own | all | all | 30 | 0.005 | 0.004 | 0.012 |
| flip_rate | claude46 | O | 10 | 0.006 | 0.004 | 0.011 |
| flip_rate | deepseek_v4 | O | 10 | 0.023 | 0.013 | 0.044 |
| flip_rate | gpt4o | O | 10 | 0.008 | 0.004 | 0.014 |
| flip_rate | all | all | 30 | 0.012 | 0.011 | 0.036 |
| mean_jsd | claude46 | O | 10 | 8.4e-04 | 7.8e-04 | 0.002 |
| mean_jsd | deepseek_v4 | O | 10 | 0.016 | 0.011 | 0.032 |
| mean_jsd | gpt4o | O | 10 | 0.006 | 0.003 | 0.011 |
| mean_jsd | all | all | 30 | 0.008 | 0.009 | 0.026 |
| delta_rho | claude46 | O | 10 | 0.015 | 0.009 | 0.029 |
| delta_rho | deepseek_v4 | O | 10 | 0.032 | 0.025 | 0.067 |
| delta_rho | gpt4o | O | 10 | 0.032 | 0.019 | 0.062 |
| delta_rho | all | all | 30 | 0.026 | 0.020 | 0.062 |
| delta_rho_partial | claude46 | O | 10 | 0.014 | 0.008 | 0.027 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.033 | 0.026 | 0.070 |
| delta_rho_partial | gpt4o | O | 10 | 0.034 | 0.020 | 0.063 |
| delta_rho_partial | all | all | 30 | 0.027 | 0.021 | 0.064 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.