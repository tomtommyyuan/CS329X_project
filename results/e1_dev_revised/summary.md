# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy nan, min answer rate nan | pending |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo nan | pending |
| **E1** | E1a and E1b for all teachers | | **pending (no train readouts)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.111 [-0.260, 0.034] p_perm 0.634 (null mean -0.091) p_holm 0.956; deepseek_v4 0.182 [0.054, 0.308] p_perm 0.021 (null mean 0.088) p_holm 0.063; gpt4o -0.092 [-0.233, 0.056] p_perm 0.478 (null mean -0.094) p_holm 0.956; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.101 [0.041, 0.164], p 1.0e-04; D_specific 0.140 [0.065, 0.226], D_shared -0.039 (139 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.026 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.060, sd 0.019, p 1.3e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.151 (pearson 0.880, seed-noise sd 0.012, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.022 [-0.195, 0.103] p_holm 0.338; deepseek_v4 0.086 [-0.063, 0.230] p_holm 0.325; gpt4o 0.020 [-0.140, 0.181] p_holm 0.338 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.027 [-0.035, 0.092], p 0.150 (137 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.090 [0.040, 0.142], p 1.0e-04 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.118 [0.055, 0.183] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.234 | 0.744 | 0.314 | 0.345 | deepseek_v4 | -0.111 | -0.260 | 0.034 | 0.634 | -0.091 | 0.060 | 0.956 | False |
| deepseek_v4 | 5 | 139 | 0.504 | 0.825 | 0.611 | 0.322 | gpt4o | 0.182 | 0.054 | 0.308 | 0.021 | 0.088 | 0.047 | 0.063 | False |
| gpt4o | 5 | 139 | 0.377 | 0.898 | 0.420 | 0.469 | deepseek_v4 | -0.092 | -0.233 | 0.056 | 0.478 | -0.094 | 0.049 | 0.956 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.005 | -0.081 | 0.017 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.101 | 0.041 | 0.164 | 1.0e-04 | 0.005 | 0.022 | 0.090 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.039 | 0.140 | 0.065 | 0.226 | 1.0e-04 | 0.009 | 0.027 | 0.118 | 0.055 | 0.183 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b.claude46_O_pooled 0.055, qwen3-4b.deepseek_v4_O_pooled 0.110, qwen3-4b.gpt4o_O_pooled 0.078.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.156 | 0.177 | 0.134 | 0.744 | -2.8e-04 | 0.262 |
| qwen3-4b.deepseek_v4_O_pooled | 0.009 | 0.298 | 0.211 | 0.825 | 0.187 | 0.099 |
| qwen3-4b.gpt4o_O_pooled | 0.072 | 0.264 | 0.284 | 0.898 | 0.116 | 0.057 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.063 | -0.209 | -0.189 |
| qwen3-4b.deepseek_v4_O_pooled | -0.037 | 0.107 | 0.052 |
| qwen3-4b.gpt4o_O_pooled | 0.008 | -0.005 | 0.058 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.234 | 0.345 | 0.226 |
| qwen3-4b.deepseek_v4_O_pooled | 0.142 | 0.504 | 0.322 |
| qwen3-4b.gpt4o_O_pooled | 0.187 | 0.469 | 0.377 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.175 | 0.136 | 0.122 |
| qwen3-4b.deepseek_v4_O_pooled | 0.173 | 0.244 | 0.213 |
| qwen3-4b.gpt4o_O_pooled | 0.111 | 0.199 | 0.140 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.048 | 0.031 | 0.068 |
| students:deepseek_v4 | 5 | 139 | 0.171 | 0.129 | 0.215 |
| students:gpt4o | 5 | 139 | 0.120 | 0.089 | 0.153 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| students:R | 3 | 139 | 7.7e-04 | 6.8e-04 | 8.6e-04 |
| base_prior | 1 | 139 | 0.165 | 0.144 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.123 | -0.157 | -0.091 |
| students:claude46 | students:gpt4o | -0.072 | -0.096 | -0.050 |
| students:claude46 | teacher:claude46 | -0.011 | -0.050 | 0.025 |
| students:claude46 | students:R | 0.047 | 0.030 | 0.067 |
| students:claude46 | base_prior | -0.117 | -0.140 | -0.094 |
| students:deepseek_v4 | students:gpt4o | 0.051 | 0.025 | 0.078 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.021 | -0.021 | 0.065 |
| students:deepseek_v4 | students:R | 0.170 | 0.128 | 0.214 |
| students:deepseek_v4 | base_prior | 0.006 | -0.033 | 0.047 |
| students:gpt4o | teacher:gpt4o | 0.045 | 0.013 | 0.077 |
| students:gpt4o | students:R | 0.119 | 0.088 | 0.152 |
| students:gpt4o | base_prior | -0.045 | -0.075 | -0.014 |
| students:R | base_prior | -0.164 | -0.186 | -0.143 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.random_R_s1 | run | -5.7e-04 | -6.6e-04 | 9.0e-05 | 139 |
| qwen3-4b.random_R_s2 | run | 4.7e-04 | 1.8e-04 | 2.9e-04 | 139 |
| qwen3-4b.random_R_s3 | run | 8.6e-04 | -0.001 | 0.002 | 139 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.091 | 0.165 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.048 | 0.004 | 5 |
| deepseek_v4 | 0.149 | 0.171 | 0.015 | 5 |
| gpt4o | 0.075 | 0.120 | 0.013 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

pending: no eval/train_responses.jsonl (run `scripts/12_eval_student.py --run-dir <run> --split train` for every O and R run)

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

pending (needs the train readouts and the SFT files or train demos)

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b.claude46_O_s1 | 1.000 | 0.057 | 150 | 0.853 | 0.829 | 0.116 | 0.048 | 0.014 |
| qwen3-4b.claude46_O_s2 | 0.999 | 0.065 | 150 | 0.844 | 0.822 | 0.115 | 0.049 | 0.014 |
| qwen3-4b.claude46_O_s3 | 1.000 | 0.058 | 150 | 0.837 | 0.841 | 0.115 | 0.042 | 0.011 |
| qwen3-4b.claude46_O_s4 | 1.000 | 0.067 | 150 | 0.847 | 0.815 | 0.115 | 0.041 | 0.016 |
| qwen3-4b.claude46_O_s5 | 1.000 | 0.061 | 150 | 0.851 | 0.836 | 0.110 | 0.053 | 0.012 |
| qwen3-4b.deepseek_v4_O_s1 | 1.000 | 0.058 | 150 | 0.834 | 0.819 | 0.085 | 0.104 | 0.051 |
| qwen3-4b.deepseek_v4_O_s2 | 1.000 | 0.058 | 150 | 0.857 | 0.829 | 0.085 | 0.102 | 0.058 |
| qwen3-4b.deepseek_v4_O_s3 | 1.000 | 0.047 | 150 | 0.847 | 0.833 | 0.083 | 0.091 | 0.047 |
| qwen3-4b.deepseek_v4_O_s4 | 1.000 | 0.059 | 150 | 0.839 | 0.824 | 0.081 | 0.119 | 0.061 |
| qwen3-4b.deepseek_v4_O_s5 | 1.000 | 0.057 | 150 | 0.844 | 0.826 | 0.079 | 0.091 | 0.046 |
| qwen3-4b.gpt4o_O_s1 | 1.000 | 0.049 | 150 | 0.861 | 0.861 | 0.085 | 0.086 | 0.033 |
| qwen3-4b.gpt4o_O_s2 | 1.000 | 0.051 | 150 | 0.841 | 0.844 | 0.103 | 0.081 | 0.023 |
| qwen3-4b.gpt4o_O_s3 | 1.000 | 0.047 | 150 | 0.857 | 0.849 | 0.096 | 0.071 | 0.032 |
| qwen3-4b.gpt4o_O_s4 | 1.000 | 0.051 | 150 | 0.859 | 0.862 | 0.091 | 0.078 | 0.026 |
| qwen3-4b.gpt4o_O_s5 | 1.000 | 0.052 | 150 | 0.862 | 0.864 | 0.090 | 0.057 | 0.023 |
| qwen3-4b.random_R_s1 | 1.000 | 0.056 | 150 | nan | 0.594 | nan | 0.050 | 3.9e-06 |
| qwen3-4b.random_R_s2 | 1.000 | 0.042 | 150 | nan | 0.465 | nan | 0.038 | 2.9e-06 |
| qwen3-4b.random_R_s3 | 1.000 | 0.019 | 150 | nan | 0.432 | nan | 0.037 | 6.2e-06 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b.claude46_O_s1 | 0.853 | 0.803 | 0.829 | 0.116 | 0.105 | 0.108 |
| qwen3-4b.claude46_O_s2 | 0.844 | 0.798 | 0.822 | 0.115 | 0.098 | 0.106 |
| qwen3-4b.claude46_O_s3 | 0.837 | 0.812 | 0.841 | 0.115 | 0.098 | 0.099 |
| qwen3-4b.claude46_O_s4 | 0.847 | 0.800 | 0.815 | 0.115 | 0.105 | 0.111 |
| qwen3-4b.claude46_O_s5 | 0.851 | 0.808 | 0.836 | 0.110 | 0.103 | 0.102 |
| qwen3-4b.deepseek_v4_O_s1 | 0.808 | 0.834 | 0.819 | 0.160 | 0.085 | 0.127 |
| qwen3-4b.deepseek_v4_O_s2 | 0.817 | 0.857 | 0.829 | 0.150 | 0.085 | 0.116 |
| qwen3-4b.deepseek_v4_O_s3 | 0.822 | 0.847 | 0.833 | 0.149 | 0.083 | 0.119 |
| qwen3-4b.deepseek_v4_O_s4 | 0.817 | 0.839 | 0.824 | 0.149 | 0.081 | 0.117 |
| qwen3-4b.deepseek_v4_O_s5 | 0.822 | 0.844 | 0.826 | 0.142 | 0.079 | 0.115 |
| qwen3-4b.gpt4o_O_s1 | 0.844 | 0.861 | 0.861 | 0.120 | 0.075 | 0.085 |
| qwen3-4b.gpt4o_O_s2 | 0.838 | 0.844 | 0.841 | 0.128 | 0.086 | 0.103 |
| qwen3-4b.gpt4o_O_s3 | 0.831 | 0.849 | 0.857 | 0.132 | 0.084 | 0.096 |
| qwen3-4b.gpt4o_O_s4 | 0.838 | 0.862 | 0.859 | 0.129 | 0.080 | 0.091 |
| qwen3-4b.gpt4o_O_s5 | 0.851 | 0.864 | 0.862 | 0.124 | 0.079 | 0.090 |
| qwen3-4b.random_R_s1 | 0.542 | 0.585 | 0.594 | 0.287 | 0.194 | 0.273 |
| qwen3-4b.random_R_s2 | 0.439 | 0.444 | 0.465 | 0.288 | 0.196 | 0.275 |
| qwen3-4b.random_R_s3 | 0.426 | 0.415 | 0.432 | 0.289 | 0.197 | 0.277 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.846 | 0.829 | 0.114 | 0.047 | 0.013 |
| deepseek_v4 | O | 5 | 1.000 | 0.844 | 0.826 | 0.083 | 0.102 | 0.053 |
| gpt4o | O | 5 | 1.000 | 0.856 | 0.856 | 0.093 | 0.074 | 0.027 |
| random | R | 3 | 1.000 | nan | 0.497 | nan | 0.041 | 4.4e-06 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_s1 | 139.000 | 0.370 | 0.155 | 0.744 | 0.119 | deepseek_v4 | 0.036 | 0.074 | -0.056 | -0.125 | 0.143 | 0.155 | 0.119 | 0.096 |
| qwen3-4b.claude46_O_s2 | 139.000 | 0.376 | 0.139 | 0.744 | 0.217 | deepseek_v4 | -0.078 | 0.638 | -0.057 | -0.271 | 0.085 | 0.139 | 0.217 | 0.128 |
| qwen3-4b.claude46_O_s3 | 139.000 | 0.382 | 0.095 | 0.744 | 0.162 | deepseek_v4 | -0.067 | 0.592 | -0.054 | -0.258 | 0.060 | 0.095 | 0.162 | 0.133 |
| qwen3-4b.claude46_O_s4 | 139.000 | 0.298 | 0.099 | 0.744 | 0.112 | deepseek_v4 | -0.013 | 0.271 | -0.050 | -0.178 | 0.085 | 0.099 | 0.112 | 0.089 |
| qwen3-4b.claude46_O_s5 | 139.000 | 0.334 | 0.214 | 0.744 | 0.194 | deepseek_v4 | 0.020 | 0.126 | -0.054 | -0.150 | 0.146 | 0.214 | 0.194 | 0.165 |
| qwen3-4b.deepseek_v4_O_s1 | 139.000 | 0.499 | 0.281 | 0.825 | 0.213 | gpt4o | 0.068 | 0.178 | 0.018 | -0.083 | 0.214 | -0.042 | 0.281 | 0.213 |
| qwen3-4b.deepseek_v4_O_s2 | 139.000 | 0.536 | 0.287 | 0.825 | 0.212 | gpt4o | 0.075 | 0.146 | 0.016 | -0.076 | 0.222 | 0.027 | 0.287 | 0.212 |
| qwen3-4b.deepseek_v4_O_s3 | 139.000 | 0.555 | 0.291 | 0.825 | 0.191 | gpt4o | 0.100 | 0.068 | 0.018 | -0.063 | 0.256 | 0.040 | 0.291 | 0.191 |
| qwen3-4b.deepseek_v4_O_s4 | 139.000 | 0.513 | 0.274 | 0.825 | 0.212 | gpt4o | 0.062 | 0.219 | 0.019 | -0.077 | 0.197 | 0.016 | 0.274 | 0.212 |
| qwen3-4b.deepseek_v4_O_s5 | 139.000 | 0.525 | 0.258 | 0.825 | 0.153 | gpt4o | 0.104 | 0.057 | 0.018 | -0.046 | 0.245 | 0.001 | 0.258 | 0.153 |
| qwen3-4b.gpt4o_O_s1 | 139.000 | 0.505 | 0.301 | 0.898 | 0.261 | deepseek_v4 | 0.040 | 0.096 | -0.033 | -0.130 | 0.214 | 0.099 | 0.261 | 0.301 |
| qwen3-4b.gpt4o_O_s2 | 139.000 | 0.492 | 0.202 | 0.898 | 0.240 | deepseek_v4 | -0.038 | 0.537 | -0.032 | -0.202 | 0.124 | 0.081 | 0.240 | 0.202 |
| qwen3-4b.gpt4o_O_s3 | 139.000 | 0.486 | 0.288 | 0.898 | 0.218 | deepseek_v4 | 0.070 | 0.032 | -0.034 | -0.079 | 0.215 | 0.043 | 0.218 | 0.288 |
| qwen3-4b.gpt4o_O_s4 | 139.000 | 0.486 | 0.282 | 0.898 | 0.242 | deepseek_v4 | 0.041 | 0.092 | -0.032 | -0.123 | 0.210 | 0.028 | 0.242 | 0.282 |
| qwen3-4b.gpt4o_O_s5 | 139.000 | 0.505 | 0.237 | 0.898 | 0.273 | deepseek_v4 | -0.036 | 0.524 | -0.033 | -0.180 | 0.115 | 0.086 | 0.273 | 0.237 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.020 | 0.051 | 5 |
| deepseek_v4 | 0.082 | 0.019 | 5 |
| gpt4o | 0.015 | 0.049 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.026 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_s1 | 0.230 | 0.744 | 0.290 | deepseek_v4 | -0.060 | 0.331 | -0.189 | 0.062 |
| qwen3-4b.claude46_O_s2 | 0.217 | 0.744 | 0.370 | deepseek_v4 | -0.154 | 0.865 | -0.336 | 0.017 |
| qwen3-4b.claude46_O_s3 | 0.178 | 0.744 | 0.330 | deepseek_v4 | -0.152 | 0.874 | -0.318 | 0.006 |
| qwen3-4b.claude46_O_s4 | 0.165 | 0.744 | 0.249 | deepseek_v4 | -0.085 | 0.566 | -0.237 | 0.037 |
| qwen3-4b.claude46_O_s5 | 0.277 | 0.744 | 0.333 | deepseek_v4 | -0.056 | 0.330 | -0.201 | 0.084 |
| qwen3-4b.deepseek_v4_O_s1 | 0.472 | 0.825 | 0.315 | gpt4o | 0.157 | 0.059 | 0.023 | 0.290 |
| qwen3-4b.deepseek_v4_O_s2 | 0.491 | 0.825 | 0.321 | gpt4o | 0.170 | 0.036 | 0.037 | 0.299 |
| qwen3-4b.deepseek_v4_O_s3 | 0.500 | 0.825 | 0.306 | gpt4o | 0.194 | 0.010 | 0.059 | 0.322 |
| qwen3-4b.deepseek_v4_O_s4 | 0.472 | 0.825 | 0.317 | gpt4o | 0.155 | 0.072 | 0.037 | 0.273 |
| qwen3-4b.deepseek_v4_O_s5 | 0.465 | 0.825 | 0.271 | gpt4o | 0.194 | 0.009 | 0.062 | 0.319 |
| qwen3-4b.gpt4o_O_s1 | 0.389 | 0.898 | 0.460 | deepseek_v4 | -0.071 | 0.345 | -0.225 | 0.094 |
| qwen3-4b.gpt4o_O_s2 | 0.306 | 0.898 | 0.439 | deepseek_v4 | -0.133 | 0.814 | -0.281 | 0.017 |
| qwen3-4b.gpt4o_O_s3 | 0.377 | 0.898 | 0.421 | deepseek_v4 | -0.044 | 0.162 | -0.175 | 0.087 |
| qwen3-4b.gpt4o_O_s4 | 0.372 | 0.898 | 0.438 | deepseek_v4 | -0.066 | 0.331 | -0.212 | 0.084 |
| qwen3-4b.gpt4o_O_s5 | 0.336 | 0.898 | 0.468 | deepseek_v4 | -0.132 | 0.814 | -0.261 | 0.007 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | 0.025 | 0.069 | 5 |
| claude46 | T1 | -0.011 | 0.095 | 5 |
| claude46 | T3 | -0.155 | 0.084 | 5 |
| claude46 | T5 | -0.018 | 0.043 | 5 |
| claude46 | T6 | 0.026 | 0.046 | 5 |
| deepseek_v4 | T0 | 0.021 | 0.069 | 5 |
| deepseek_v4 | T1 | 0.217 | 0.086 | 5 |
| deepseek_v4 | T3 | 0.289 | 0.041 | 5 |
| deepseek_v4 | T5 | -0.029 | 0.056 | 5 |
| deepseek_v4 | T6 | -0.030 | 0.035 | 5 |
| gpt4o | T0 | -0.068 | 0.047 | 5 |
| gpt4o | T1 | -0.146 | 0.064 | 5 |
| gpt4o | T3 | -0.147 | 0.050 | 5 |
| gpt4o | T5 | 0.163 | 0.077 | 5 |
| gpt4o | T6 | 0.020 | 0.070 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.387 | 0.156 | 0.744 | 0.177 | deepseek_v4 | -0.022 | -0.195 | 0.103 | 0.285 | -0.057 | 0.338 |
| deepseek_v4 | 5 | 139 | 0.551 | 0.298 | 0.825 | 0.211 | gpt4o | 0.086 | -0.063 | 0.230 | 0.108 | 0.020 | 0.325 |
| gpt4o | 5 | 139 | 0.521 | 0.284 | 0.898 | 0.264 | deepseek_v4 | 0.020 | -0.140 | 0.181 | 0.169 | -0.033 | 0.338 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.245 | 0.744 | 0.118 | 0.365 | 3 | -0.288 | -0.419 | -0.164 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.533 | 0.825 | 0.448 | 0.611 | 1 | 0.256 | 0.130 | 0.359 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.277 | 0.898 | 0.166 | 0.380 | 2 | -0.256 | -0.383 | -0.133 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 4/5 seeds pass -> partial (old rule, not the verdict)
- deepseek_v4: 5/5 seeds pass -> ok (old rule, not the verdict)
- gpt4o: 2/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 0.026 vs run-reassignment null mean -0.060 sd 0.019, p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 1.151, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.101 [0.041, 0.164] p 1.0e-04 alone would read pass; the frozen rule (version 5) also needs D_specific 0.140 [0.065, 0.226] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.008 | 0.005 | 0.015 |
| agree_own | deepseek_v4 | O | 10 | 0.011 | 0.006 | 0.021 |
| agree_own | gpt4o | O | 10 | 0.009 | 0.008 | 0.020 |
| agree_own | all | all | 30 | 0.009 | 0.006 | 0.020 |
| jsd_own | claude46 | O | 10 | 0.003 | 0.002 | 0.006 |
| jsd_own | deepseek_v4 | O | 10 | 0.003 | 0.002 | 0.006 |
| jsd_own | gpt4o | O | 10 | 0.008 | 0.005 | 0.016 |
| jsd_own | all | all | 30 | 0.005 | 0.004 | 0.013 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.006 | 0.004 | 0.012 |
| flip_rate | deepseek_v4 | O | 10 | 0.014 | 0.009 | 0.028 |
| flip_rate | gpt4o | O | 10 | 0.014 | 0.009 | 0.027 |
| flip_rate | random | R | 3 | 0.009 | 0.007 | 0.013 |
| flip_rate | all | all | 33 | 0.011 | 0.008 | 0.028 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.002 | 0.001 | 0.004 |
| mean_jsd | deepseek_v4 | O | 10 | 0.008 | 0.005 | 0.014 |
| mean_jsd | gpt4o | O | 10 | 0.006 | 0.004 | 0.010 |
| mean_jsd | random | R | 3 | 2.2e-06 | 1.2e-06 | 3.2e-06 |
| mean_jsd | all | all | 33 | 0.005 | 0.004 | 0.013 |
| delta_rho | claude46 | O | 10 | 0.058 | 0.039 | 0.097 |
| delta_rho | deepseek_v4 | O | 10 | 0.023 | 0.015 | 0.039 |
| delta_rho | gpt4o | O | 10 | 0.049 | 0.033 | 0.089 |
| delta_rho | all | all | 30 | 0.043 | 0.033 | 0.095 |
| delta_rho_partial | claude46 | O | 10 | 0.063 | 0.037 | 0.110 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.023 | 0.014 | 0.040 |
| delta_rho_partial | gpt4o | O | 10 | 0.058 | 0.040 | 0.107 |
| delta_rho_partial | all | all | 30 | 0.048 | 0.036 | 0.107 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.