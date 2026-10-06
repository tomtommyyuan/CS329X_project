# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.902, min answer rate 0.999 | fail |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.804 | pass |
| **E1** | E1a and E1b for all teachers | | **FAIL (E1a fail, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.181 [-0.323, -0.044] p_perm 0.829 (null mean -0.125) p_holm 0.829; deepseek_v4 0.202 [0.096, 0.316] p_perm 0.044 (null mean 0.132) p_holm 0.133; gpt4o -0.086 [-0.212, 0.034] p_perm 0.237 (null mean -0.118) p_holm 0.475; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.096 [0.027, 0.160], p 7.0e-04; D_specific 0.159 [0.056, 0.272], D_shared -0.064 (139 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.020 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.062, sd 0.018, p 1.3e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 2.954 (pearson 0.906, seed-noise sd 0.022, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.064 [-0.226, 0.054] p_holm 0.650; deepseek_v4 0.060 [-0.058, 0.186] p_holm 0.650; gpt4o 0.064 [-0.065, 0.186] p_holm 0.083 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.014 [-0.085, 0.058], p 0.634 (138 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.082 [0.031, 0.129], p 0.002 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.118 [0.045, 0.191] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.207 | 0.744 | 0.278 | 0.388 | deepseek_v4 | -0.181 | -0.323 | -0.044 | 0.829 | -0.125 | 0.059 | 0.829 | False |
| deepseek_v4 | 5 | 139 | 0.528 | 0.825 | 0.640 | 0.326 | gpt4o | 0.202 | 0.096 | 0.316 | 0.044 | 0.132 | 0.041 | 0.133 | False |
| gpt4o | 5 | 139 | 0.427 | 0.898 | 0.476 | 0.513 | deepseek_v4 | -0.086 | -0.212 | 0.034 | 0.237 | -0.118 | 0.046 | 0.475 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.019 | -0.091 | 0.014 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.096 | 0.027 | 0.160 | 7.0e-04 | 0.009 | 0.027 | 0.082 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.064 | 0.159 | 0.056 | 0.272 | 1.0e-04 | 0.020 | 0.035 | 0.118 | 0.045 | 0.191 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2c.claude46_O_pooled 0.060, qwen3-4b-e2c.deepseek_v4_O_pooled 0.147, qwen3-4b-e2c.gpt4o_O_pooled 0.118.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.100 | 0.164 | 0.109 | 0.744 | -0.036 | 0.311 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.014 | 0.252 | 0.191 | 0.825 | 0.149 | 0.070 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.055 | 0.275 | 0.339 | 0.898 | 0.174 | 0.096 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.019 | -0.277 | -0.307 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | -0.019 | 0.072 | 0.022 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.013 | 0.051 | 0.128 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.207 | 0.388 | 0.230 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.183 | 0.528 | 0.326 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.193 | 0.513 | 0.427 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.078 | 0.184 | 0.093 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.118 | 0.050 | 0.023 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.087 | 0.159 | 0.161 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.080 | 0.061 | 0.100 |
| students:deepseek_v4 | 5 | 139 | 0.390 | 0.335 | 0.445 |
| students:gpt4o | 5 | 139 | 0.250 | 0.205 | 0.298 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.165 | 0.144 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.311 | -0.360 | -0.261 |
| students:claude46 | students:gpt4o | -0.171 | -0.211 | -0.132 |
| students:claude46 | teacher:claude46 | 0.021 | -0.019 | 0.060 |
| students:claude46 | base_prior | -0.085 | -0.107 | -0.063 |
| students:deepseek_v4 | students:gpt4o | 0.140 | 0.096 | 0.185 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.241 | 0.189 | 0.295 |
| students:deepseek_v4 | base_prior | 0.226 | 0.180 | 0.272 |
| students:gpt4o | teacher:gpt4o | 0.175 | 0.135 | 0.218 |
| students:gpt4o | base_prior | 0.086 | 0.046 | 0.128 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.091 | 0.165 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.080 | 0.012 | 5 |
| deepseek_v4 | 0.149 | 0.390 | 0.029 | 5 |
| gpt4o | 0.075 | 0.250 | 0.022 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.902 | False | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.906 | False | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.909 | False | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.906 | False | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.912 | False | data/sft_e2c/claude46_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.965 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.962 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.956 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.970 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.964 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.953 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.952 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.955 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s4 | 4964 | 0.999 | 4964 | 4964 | 0 | 0 | 0.950 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| qwen3-4b-e2c.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.956 | True | data/sft_e2c/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 782 | 419 | 5 | 3910 | 0.866 | 0.838 | 0.891 | True |
| claude46 | gpt4o | 1046 | 546 | 5 | 5230 | 0.830 | 0.804 | 0.853 | True |
| deepseek_v4 | claude46 | 782 | 419 | 5 | 3910 | 0.953 | 0.939 | 0.965 | True |
| deepseek_v4 | gpt4o | 574 | 334 | 5 | 2870 | 0.938 | 0.919 | 0.955 | True |
| gpt4o | claude46 | 1046 | 546 | 5 | 5230 | 0.928 | 0.913 | 0.942 | True |
| gpt4o | deepseek_v4 | 574 | 334 | 5 | 2870 | 0.922 | 0.902 | 0.941 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2c.claude46_O_s1 | 1.000 | 0.075 | 150 | 0.849 | 0.794 | 0.122 | 0.052 | 0.013 |
| qwen3-4b-e2c.claude46_O_s2 | 1.000 | 0.067 | 150 | 0.833 | 0.780 | 0.129 | 0.068 | 0.017 |
| qwen3-4b-e2c.claude46_O_s3 | 1.000 | 0.074 | 150 | 0.851 | 0.807 | 0.124 | 0.068 | 0.014 |
| qwen3-4b-e2c.claude46_O_s4 | 1.000 | 0.080 | 150 | 0.835 | 0.786 | 0.130 | 0.080 | 0.018 |
| qwen3-4b-e2c.claude46_O_s5 | 1.000 | 0.067 | 150 | 0.851 | 0.805 | 0.120 | 0.070 | 0.015 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 1.000 | 0.106 | 150 | 0.787 | 0.753 | 0.124 | 0.244 | 0.150 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 1.000 | 0.110 | 150 | 0.820 | 0.777 | 0.100 | 0.196 | 0.121 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 1.000 | 0.115 | 150 | 0.785 | 0.751 | 0.112 | 0.234 | 0.121 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 1.000 | 0.093 | 150 | 0.793 | 0.761 | 0.107 | 0.213 | 0.117 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 1.000 | 0.093 | 150 | 0.803 | 0.782 | 0.101 | 0.196 | 0.118 |
| qwen3-4b-e2c.gpt4o_O_s1 | 1.000 | 0.071 | 150 | 0.852 | 0.839 | 0.096 | 0.149 | 0.066 |
| qwen3-4b-e2c.gpt4o_O_s2 | 1.000 | 0.072 | 150 | 0.848 | 0.834 | 0.102 | 0.152 | 0.082 |
| qwen3-4b-e2c.gpt4o_O_s3 | 1.000 | 0.071 | 150 | 0.850 | 0.844 | 0.100 | 0.143 | 0.069 |
| qwen3-4b-e2c.gpt4o_O_s4 | 1.000 | 0.074 | 150 | 0.861 | 0.847 | 0.097 | 0.114 | 0.054 |
| qwen3-4b-e2c.gpt4o_O_s5 | 1.000 | 0.083 | 150 | 0.852 | 0.845 | 0.097 | 0.131 | 0.056 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2c.claude46_O_s1 | 0.849 | 0.770 | 0.794 | 0.122 | 0.115 | 0.130 |
| qwen3-4b-e2c.claude46_O_s2 | 0.833 | 0.770 | 0.780 | 0.129 | 0.120 | 0.138 |
| qwen3-4b-e2c.claude46_O_s3 | 0.851 | 0.776 | 0.807 | 0.124 | 0.116 | 0.132 |
| qwen3-4b-e2c.claude46_O_s4 | 0.835 | 0.765 | 0.786 | 0.130 | 0.112 | 0.136 |
| qwen3-4b-e2c.claude46_O_s5 | 0.851 | 0.783 | 0.805 | 0.120 | 0.108 | 0.125 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 0.730 | 0.787 | 0.753 | 0.224 | 0.124 | 0.189 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 0.755 | 0.820 | 0.777 | 0.198 | 0.100 | 0.166 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 0.725 | 0.785 | 0.751 | 0.216 | 0.112 | 0.179 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 0.730 | 0.793 | 0.761 | 0.205 | 0.107 | 0.171 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 0.750 | 0.803 | 0.782 | 0.195 | 0.101 | 0.157 |
| qwen3-4b-e2c.gpt4o_O_s1 | 0.826 | 0.839 | 0.852 | 0.130 | 0.085 | 0.096 |
| qwen3-4b-e2c.gpt4o_O_s2 | 0.824 | 0.834 | 0.848 | 0.138 | 0.086 | 0.102 |
| qwen3-4b-e2c.gpt4o_O_s3 | 0.824 | 0.844 | 0.850 | 0.132 | 0.086 | 0.100 |
| qwen3-4b-e2c.gpt4o_O_s4 | 0.833 | 0.847 | 0.861 | 0.132 | 0.081 | 0.097 |
| qwen3-4b-e2c.gpt4o_O_s5 | 0.833 | 0.845 | 0.852 | 0.129 | 0.081 | 0.097 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.844 | 0.794 | 0.125 | 0.068 | 0.015 |
| deepseek_v4 | O | 5 | 1.000 | 0.798 | 0.765 | 0.109 | 0.217 | 0.125 |
| gpt4o | O | 5 | 1.000 | 0.853 | 0.842 | 0.098 | 0.138 | 0.065 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 139.000 | 0.425 | 0.103 | 0.744 | 0.133 | deepseek_v4 | -0.030 | 0.303 | -0.063 | -0.216 | 0.068 | 0.103 | 0.133 | 0.115 |
| qwen3-4b-e2c.claude46_O_s2 | 139.000 | 0.460 | 0.089 | 0.744 | 0.149 | deepseek_v4 | -0.060 | 0.440 | -0.071 | -0.214 | 0.047 | 0.089 | 0.149 | 0.102 |
| qwen3-4b-e2c.claude46_O_s3 | 139.000 | 0.450 | 0.093 | 0.744 | 0.175 | deepseek_v4 | -0.082 | 0.592 | -0.068 | -0.261 | 0.074 | 0.093 | 0.175 | 0.094 |
| qwen3-4b-e2c.claude46_O_s4 | 139.000 | 0.530 | 0.082 | 0.744 | 0.158 | deepseek_v4 | -0.076 | 0.501 | -0.077 | -0.218 | 0.040 | 0.082 | 0.158 | 0.076 |
| qwen3-4b-e2c.claude46_O_s5 | 139.000 | 0.492 | 0.098 | 0.744 | 0.146 | deepseek_v4 | -0.048 | 0.366 | -0.070 | -0.220 | 0.069 | 0.098 | 0.146 | 0.119 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 139.000 | 0.671 | 0.180 | 0.825 | 0.140 | gpt4o | 0.041 | 0.461 | 0.035 | -0.090 | 0.169 | 0.013 | 0.180 | 0.140 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 139.000 | 0.703 | 0.272 | 0.825 | 0.177 | gpt4o | 0.095 | 0.113 | 0.034 | -0.016 | 0.212 | 0.004 | 0.272 | 0.177 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 139.000 | 0.701 | 0.225 | 0.825 | 0.179 | gpt4o | 0.046 | 0.448 | 0.039 | -0.072 | 0.163 | -0.003 | 0.225 | 0.179 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 139.000 | 0.689 | 0.274 | 0.825 | 0.189 | gpt4o | 0.085 | 0.161 | 0.035 | -0.032 | 0.206 | 0.035 | 0.274 | 0.189 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 139.000 | 0.672 | 0.245 | 0.825 | 0.224 | gpt4o | 0.021 | 0.593 | 0.032 | -0.107 | 0.155 | 0.019 | 0.245 | 0.224 |
| qwen3-4b-e2c.gpt4o_O_s1 | 139.000 | 0.604 | 0.316 | 0.898 | 0.236 | deepseek_v4 | 0.079 | 0.019 | -0.035 | -0.054 | 0.209 | 0.035 | 0.236 | 0.316 |
| qwen3-4b-e2c.gpt4o_O_s2 | 139.000 | 0.604 | 0.339 | 0.898 | 0.290 | deepseek_v4 | 0.049 | 0.061 | -0.037 | -0.081 | 0.178 | 0.049 | 0.290 | 0.339 |
| qwen3-4b-e2c.gpt4o_O_s3 | 139.000 | 0.613 | 0.336 | 0.898 | 0.266 | deepseek_v4 | 0.070 | 0.024 | -0.038 | -0.056 | 0.195 | 0.075 | 0.266 | 0.336 |
| qwen3-4b-e2c.gpt4o_O_s4 | 139.000 | 0.578 | 0.312 | 0.898 | 0.249 | deepseek_v4 | 0.063 | 0.027 | -0.038 | -0.067 | 0.194 | 0.050 | 0.249 | 0.312 |
| qwen3-4b-e2c.gpt4o_O_s5 | 139.000 | 0.619 | 0.319 | 0.898 | 0.273 | deepseek_v4 | 0.046 | 0.059 | -0.038 | -0.074 | 0.167 | 0.054 | 0.273 | 0.319 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.059 | 0.021 | 5 |
| deepseek_v4 | 0.057 | 0.031 | 5 |
| gpt4o | 0.062 | 0.014 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.020 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 0.194 | 0.744 | 0.328 | deepseek_v4 | -0.134 | 0.702 | -0.295 | 0.002 |
| qwen3-4b-e2c.claude46_O_s2 | 0.189 | 0.744 | 0.357 | deepseek_v4 | -0.168 | 0.793 | -0.302 | -0.042 |
| qwen3-4b-e2c.claude46_O_s3 | 0.191 | 0.744 | 0.372 | deepseek_v4 | -0.181 | 0.862 | -0.349 | -0.022 |
| qwen3-4b-e2c.claude46_O_s4 | 0.197 | 0.744 | 0.396 | deepseek_v4 | -0.199 | 0.879 | -0.322 | -0.082 |
| qwen3-4b-e2c.claude46_O_s5 | 0.203 | 0.744 | 0.370 | deepseek_v4 | -0.166 | 0.798 | -0.324 | -0.018 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 0.471 | 0.825 | 0.285 | gpt4o | 0.185 | 0.089 | 0.069 | 0.299 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 0.538 | 0.825 | 0.315 | gpt4o | 0.223 | 0.010 | 0.109 | 0.342 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 0.509 | 0.825 | 0.317 | gpt4o | 0.192 | 0.082 | 0.089 | 0.304 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 0.535 | 0.825 | 0.323 | gpt4o | 0.213 | 0.020 | 0.106 | 0.325 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 0.512 | 0.825 | 0.345 | gpt4o | 0.166 | 0.151 | 0.063 | 0.275 |
| qwen3-4b-e2c.gpt4o_O_s1 | 0.409 | 0.898 | 0.481 | deepseek_v4 | -0.072 | 0.218 | -0.206 | 0.053 |
| qwen3-4b-e2c.gpt4o_O_s2 | 0.427 | 0.898 | 0.518 | deepseek_v4 | -0.091 | 0.292 | -0.221 | 0.030 |
| qwen3-4b-e2c.gpt4o_O_s3 | 0.425 | 0.898 | 0.505 | deepseek_v4 | -0.080 | 0.210 | -0.201 | 0.036 |
| qwen3-4b-e2c.gpt4o_O_s4 | 0.405 | 0.898 | 0.480 | deepseek_v4 | -0.075 | 0.177 | -0.199 | 0.042 |
| qwen3-4b-e2c.gpt4o_O_s5 | 0.412 | 0.898 | 0.511 | deepseek_v4 | -0.099 | 0.338 | -0.225 | 0.019 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.100 | 0.058 | 5 |
| claude46 | T1 | -0.018 | 0.022 | 5 |
| claude46 | T3 | -0.179 | 0.045 | 5 |
| claude46 | T5 | -0.229 | 0.048 | 5 |
| claude46 | T6 | 0.075 | 0.025 | 5 |
| deepseek_v4 | T0 | -0.064 | 0.032 | 5 |
| deepseek_v4 | T1 | 0.150 | 0.069 | 5 |
| deepseek_v4 | T3 | 0.063 | 0.053 | 5 |
| deepseek_v4 | T5 | -0.006 | 0.028 | 5 |
| deepseek_v4 | T6 | 0.014 | 0.057 | 5 |
| gpt4o | T0 | 0.004 | 0.089 | 5 |
| gpt4o | T1 | 0.052 | 0.057 | 5 |
| gpt4o | T3 | -0.115 | 0.038 | 5 |
| gpt4o | T5 | 0.277 | 0.022 | 5 |
| gpt4o | T6 | 0.029 | 0.041 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.503 | 0.100 | 0.744 | 0.164 | deepseek_v4 | -0.064 | -0.226 | 0.054 | 0.446 | -0.073 | 0.650 |
| deepseek_v4 | 5 | 139 | 0.708 | 0.252 | 0.825 | 0.191 | gpt4o | 0.060 | -0.058 | 0.186 | 0.325 | 0.037 | 0.650 |
| gpt4o | 5 | 139 | 0.620 | 0.339 | 0.898 | 0.275 | deepseek_v4 | 0.064 | -0.065 | 0.186 | 0.028 | -0.037 | 0.083 |

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

- P1 mean deltaRhoPartial 0.020 vs run-reassignment null mean -0.062 sd 0.018, p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 2.954, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.096 [0.027, 0.160] p 7.0e-04 alone would read pass; the frozen rule (version 5) also needs D_specific 0.159 [0.056, 0.272] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.010 | 0.008 | 0.018 |
| agree_own | deepseek_v4 | O | 10 | 0.017 | 0.011 | 0.035 |
| agree_own | gpt4o | O | 10 | 0.005 | 0.004 | 0.011 |
| agree_own | all | all | 30 | 0.011 | 0.010 | 0.031 |
| jsd_own | claude46 | O | 10 | 0.005 | 0.003 | 0.010 |
| jsd_own | deepseek_v4 | O | 10 | 0.012 | 0.008 | 0.023 |
| jsd_own | gpt4o | O | 10 | 0.003 | 0.002 | 0.005 |
| jsd_own | all | all | 30 | 0.007 | 0.006 | 0.020 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.012 | 0.008 | 0.023 |
| flip_rate | deepseek_v4 | O | 10 | 0.027 | 0.017 | 0.049 |
| flip_rate | gpt4o | O | 10 | 0.019 | 0.012 | 0.036 |
| flip_rate | all | all | 30 | 0.019 | 0.014 | 0.044 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.003 | 0.001 | 0.005 |
| mean_jsd | deepseek_v4 | O | 10 | 0.014 | 0.015 | 0.033 |
| mean_jsd | gpt4o | O | 10 | 0.013 | 0.008 | 0.027 |
| mean_jsd | all | all | 30 | 0.010 | 0.011 | 0.031 |
| delta_rho | claude46 | O | 10 | 0.029 | 0.018 | 0.057 |
| delta_rho | deepseek_v4 | O | 10 | 0.028 | 0.015 | 0.052 |
| delta_rho | gpt4o | O | 10 | 0.014 | 0.008 | 0.026 |
| delta_rho | all | all | 30 | 0.024 | 0.016 | 0.052 |
| delta_rho_partial | claude46 | O | 10 | 0.026 | 0.015 | 0.049 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.039 | 0.023 | 0.070 |
| delta_rho_partial | gpt4o | O | 10 | 0.018 | 0.010 | 0.032 |
| delta_rho_partial | all | all | 30 | 0.027 | 0.018 | 0.060 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.