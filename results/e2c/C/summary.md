# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.975, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.946 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.147 [-0.258, -0.058] p_perm 0.938 (null mean -0.085) p_holm 1.000; deepseek_v4 0.221 [0.148, 0.296] p_perm 0.001 (null mean 0.116) p_holm 0.003; gpt4o -0.121 [-0.211, -0.032] p_perm 0.710 (null mean -0.102) p_holm 1.000; 1/3 pass | **PARTIAL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.051 [0.009, 0.094], p 0.012; D_specific 0.077 [0.031, 0.125], D_shared -0.026 (290 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 290 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 0.021 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.049, sd 0.020, p 7.3e-05, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 4.931 (pearson 0.948, seed-noise sd 0.020, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.079 [-0.213, 0.005] p_holm 1.000; deepseek_v4 0.234 [0.136, 0.300] p_holm 3.0e-04; gpt4o -0.091 [-0.200, 0.014] p_holm 1.000 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.033 [-0.113, 0.043], p 0.851 (288 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.055 [0.018, 0.092], p 0.027 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.078 [0.036, 0.122] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.380 [0.327, 0.434], margin over the next 0.100 [0.036, 0.167] (290 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.103 | 0.704 | 0.147 | 0.250 | deepseek_v4 | -0.147 | -0.258 | -0.058 | 0.938 | -0.085 | 0.040 | 1.000 | False |
| deepseek_v4 | 5 | 290 | 0.486 | 0.797 | 0.609 | 0.264 | gpt4o | 0.221 | 0.148 | 0.296 | 0.001 | 0.116 | 0.032 | 0.003 | True |
| gpt4o | 5 | 290 | 0.327 | 0.904 | 0.362 | 0.448 | deepseek_v4 | -0.121 | -0.211 | -0.032 | 0.710 | -0.102 | 0.035 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.011 | -0.078 | 0.019 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.051 | 0.009 | 0.094 | 0.012 | 0.008 | 0.019 | 0.055 | 290 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.026 | 0.077 | 0.031 | 0.125 | 0.001 | 0.014 | 0.021 | 0.078 | 0.036 | 0.122 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2c.claude46_O_pooled 0.096, qwen3-4b-e2c.deepseek_v4_O_pooled 0.177, qwen3-4b-e2c.gpt4o_O_pooled 0.139.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.070 | 0.149 | 0.125 | 0.704 | -0.067 | 0.082 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.091 | 0.333 | 0.099 | 0.797 | 0.237 | 0.117 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.151 | 0.301 | 0.210 | 0.904 | -0.016 | 0.033 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | -0.082 | -0.249 | -0.078 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.008 | 0.116 | -0.012 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.046 | 0.026 | 0.069 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | 0.103 | 0.250 | 0.202 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | 0.147 | 0.486 | 0.264 |
| qwen3-4b-e2c.gpt4o_O_pooled | 0.190 | 0.448 | 0.327 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2c.claude46_O_pooled | -0.042 | 0.191 | 0.049 |
| qwen3-4b-e2c.deepseek_v4_O_pooled | -0.011 | 0.159 | 0.015 |
| qwen3-4b-e2c.gpt4o_O_pooled | -0.038 | 0.177 | -0.025 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 290 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 290 | 0.079 | 0.061 | 0.099 |
| students:deepseek_v4 | 5 | 290 | 0.447 | 0.402 | 0.493 |
| students:gpt4o | 5 | 290 | 0.276 | 0.239 | 0.314 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |
| base_prior | 1 | 290 | 0.146 | 0.133 | 0.159 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.367 | -0.413 | -0.323 |
| students:claude46 | students:gpt4o | -0.197 | -0.233 | -0.162 |
| students:claude46 | teacher:claude46 | 0.035 | 0.007 | 0.061 |
| students:claude46 | base_prior | -0.067 | -0.086 | -0.047 |
| students:deepseek_v4 | students:gpt4o | 0.170 | 0.128 | 0.213 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.333 | 0.291 | 0.378 |
| students:deepseek_v4 | base_prior | 0.301 | 0.263 | 0.341 |
| students:gpt4o | teacher:gpt4o | 0.213 | 0.178 | 0.251 |
| students:gpt4o | base_prior | 0.130 | 0.097 | 0.165 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.057 | -0.120 | 0.178 | 8 |
| qwen3-4b.base_B_s0 | base_prior | 0.068 | -0.078 | 0.146 | 290 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.079 | 0.008 | 5 |
| deepseek_v4 | 0.113 | 0.447 | 0.024 | 5 |
| gpt4o | 0.063 | 0.276 | 0.023 | 5 |

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
| qwen3-4b.base_B_s0 | 0.213 | 0.097 | 8 | nan | 0.830 | nan | 0.188 | 0.028 |
| qwen3-4b-e2c.claude46_O_s1 | 1.000 | 0.115 | 300 | 0.862 | 0.832 | 0.119 | 0.097 | 0.035 |
| qwen3-4b-e2c.claude46_O_s2 | 1.000 | 0.106 | 300 | 0.874 | 0.829 | 0.118 | 0.090 | 0.034 |
| qwen3-4b-e2c.claude46_O_s3 | 1.000 | 0.120 | 300 | 0.838 | 0.826 | 0.133 | 0.096 | 0.038 |
| qwen3-4b-e2c.claude46_O_s4 | 1.000 | 0.109 | 300 | 0.865 | 0.835 | 0.120 | 0.092 | 0.036 |
| qwen3-4b-e2c.claude46_O_s5 | 1.000 | 0.115 | 300 | 0.859 | 0.834 | 0.129 | 0.086 | 0.035 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 1.000 | 0.105 | 300 | 0.776 | 0.740 | 0.143 | 0.248 | 0.159 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 1.000 | 0.098 | 300 | 0.808 | 0.769 | 0.132 | 0.239 | 0.172 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 1.000 | 0.097 | 300 | 0.782 | 0.748 | 0.139 | 0.275 | 0.187 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 1.000 | 0.086 | 300 | 0.787 | 0.753 | 0.139 | 0.264 | 0.193 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 1.000 | 0.114 | 300 | 0.786 | 0.753 | 0.137 | 0.261 | 0.183 |
| qwen3-4b-e2c.gpt4o_O_s1 | 1.000 | 0.085 | 300 | 0.809 | 0.804 | 0.144 | 0.148 | 0.091 |
| qwen3-4b-e2c.gpt4o_O_s2 | 1.000 | 0.090 | 300 | 0.805 | 0.808 | 0.148 | 0.161 | 0.102 |
| qwen3-4b-e2c.gpt4o_O_s3 | 1.000 | 0.094 | 300 | 0.814 | 0.809 | 0.140 | 0.149 | 0.084 |
| qwen3-4b-e2c.gpt4o_O_s4 | 1.000 | 0.096 | 300 | 0.822 | 0.812 | 0.136 | 0.131 | 0.084 |
| qwen3-4b-e2c.gpt4o_O_s5 | 1.000 | 0.089 | 300 | 0.811 | 0.814 | 0.139 | 0.161 | 0.094 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.776 | 0.830 | 0.782 | 0.185 | 0.098 | 0.163 |
| qwen3-4b-e2c.claude46_O_s1 | 0.862 | 0.832 | 0.832 | 0.119 | 0.100 | 0.128 |
| qwen3-4b-e2c.claude46_O_s2 | 0.874 | 0.829 | 0.828 | 0.118 | 0.106 | 0.131 |
| qwen3-4b-e2c.claude46_O_s3 | 0.838 | 0.826 | 0.816 | 0.133 | 0.109 | 0.139 |
| qwen3-4b-e2c.claude46_O_s4 | 0.865 | 0.835 | 0.827 | 0.120 | 0.100 | 0.129 |
| qwen3-4b-e2c.claude46_O_s5 | 0.859 | 0.834 | 0.826 | 0.129 | 0.107 | 0.137 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 0.726 | 0.776 | 0.740 | 0.235 | 0.143 | 0.213 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 0.757 | 0.808 | 0.769 | 0.211 | 0.132 | 0.192 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 0.735 | 0.782 | 0.748 | 0.222 | 0.139 | 0.201 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 0.739 | 0.787 | 0.753 | 0.224 | 0.139 | 0.201 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 0.745 | 0.786 | 0.753 | 0.221 | 0.137 | 0.198 |
| qwen3-4b-e2c.gpt4o_O_s1 | 0.789 | 0.804 | 0.809 | 0.178 | 0.121 | 0.144 |
| qwen3-4b-e2c.gpt4o_O_s2 | 0.793 | 0.808 | 0.805 | 0.180 | 0.119 | 0.148 |
| qwen3-4b-e2c.gpt4o_O_s3 | 0.796 | 0.809 | 0.814 | 0.178 | 0.117 | 0.140 |
| qwen3-4b-e2c.gpt4o_O_s4 | 0.801 | 0.812 | 0.822 | 0.172 | 0.116 | 0.136 |
| qwen3-4b-e2c.gpt4o_O_s5 | 0.801 | 0.814 | 0.811 | 0.170 | 0.113 | 0.139 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.213 | nan | 0.830 | nan | 0.188 | 0.028 |
| claude46 | O | 5 | 1.000 | 0.859 | 0.831 | 0.124 | 0.092 | 0.036 |
| deepseek_v4 | O | 5 | 1.000 | 0.788 | 0.753 | 0.138 | 0.258 | 0.179 |
| gpt4o | O | 5 | 1.000 | 0.812 | 0.810 | 0.141 | 0.150 | 0.091 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 290.000 | 0.310 | 0.097 | 0.704 | 0.148 | deepseek_v4 | -0.051 | 0.522 | -0.049 | -0.176 | 0.018 | 0.097 | 0.148 | 0.143 |
| qwen3-4b-e2c.claude46_O_s2 | 290.000 | 0.269 | 0.085 | 0.704 | 0.143 | deepseek_v4 | -0.057 | 0.620 | -0.045 | -0.192 | 0.021 | 0.085 | 0.143 | 0.129 |
| qwen3-4b-e2c.claude46_O_s3 | 290.000 | 0.265 | 0.025 | 0.704 | 0.125 | deepseek_v4 | -0.100 | 0.938 | -0.038 | -0.226 | -0.007 | 0.025 | 0.125 | 0.079 |
| qwen3-4b-e2c.claude46_O_s4 | 290.000 | 0.291 | 0.053 | 0.704 | 0.124 | deepseek_v4 | -0.071 | 0.770 | -0.041 | -0.203 | 0.013 | 0.053 | 0.124 | 0.101 |
| qwen3-4b-e2c.claude46_O_s5 | 290.000 | 0.284 | 0.058 | 0.704 | 0.129 | deepseek_v4 | -0.071 | 0.773 | -0.041 | -0.205 | 0.016 | 0.058 | 0.129 | 0.112 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 290.000 | 0.689 | 0.309 | 0.797 | 0.073 | gpt4o | 0.236 | 1.0e-04 | 0.077 | 0.138 | 0.303 | 0.066 | 0.309 | 0.073 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 290.000 | 0.655 | 0.312 | 0.797 | 0.091 | gpt4o | 0.221 | 1.0e-04 | 0.073 | 0.123 | 0.297 | 0.078 | 0.312 | 0.091 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 290.000 | 0.678 | 0.311 | 0.797 | 0.102 | gpt4o | 0.209 | 1.0e-04 | 0.080 | 0.106 | 0.278 | 0.096 | 0.311 | 0.102 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 290.000 | 0.677 | 0.331 | 0.797 | 0.096 | claude46 | 0.235 | 1.0e-04 | 0.080 | 0.142 | 0.303 | 0.096 | 0.331 | 0.084 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 290.000 | 0.707 | 0.300 | 0.797 | 0.114 | gpt4o | 0.186 | 0.001 | 0.076 | 0.093 | 0.258 | 0.093 | 0.300 | 0.114 |
| qwen3-4b-e2c.gpt4o_O_s1 | 290.000 | 0.550 | 0.174 | 0.904 | 0.242 | deepseek_v4 | -0.068 | 0.492 | -0.069 | -0.169 | 0.030 | 0.140 | 0.242 | 0.174 |
| qwen3-4b-e2c.gpt4o_O_s2 | 290.000 | 0.590 | 0.174 | 0.904 | 0.317 | deepseek_v4 | -0.143 | 0.943 | -0.080 | -0.261 | -0.030 | 0.130 | 0.317 | 0.174 |
| qwen3-4b-e2c.gpt4o_O_s3 | 290.000 | 0.550 | 0.196 | 0.904 | 0.261 | deepseek_v4 | -0.066 | 0.421 | -0.074 | -0.162 | 0.030 | 0.125 | 0.261 | 0.196 |
| qwen3-4b-e2c.gpt4o_O_s4 | 290.000 | 0.541 | 0.206 | 0.904 | 0.260 | deepseek_v4 | -0.055 | 0.327 | -0.072 | -0.165 | 0.050 | 0.141 | 0.260 | 0.206 |
| qwen3-4b-e2c.gpt4o_O_s5 | 290.000 | 0.555 | 0.228 | 0.904 | 0.319 | deepseek_v4 | -0.091 | 0.617 | -0.079 | -0.204 | 0.019 | 0.167 | 0.319 | 0.228 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.070 | 0.019 | 5 |
| deepseek_v4 | 0.217 | 0.021 | 5 |
| gpt4o | -0.085 | 0.035 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.021 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c.claude46_O_s1 | 0.128 | 0.704 | 0.248 | deepseek_v4 | -0.120 | 0.780 | -0.227 | -0.042 |
| qwen3-4b-e2c.claude46_O_s2 | 0.113 | 0.704 | 0.229 | deepseek_v4 | -0.116 | 0.807 | -0.230 | -0.034 |
| qwen3-4b-e2c.claude46_O_s3 | 0.055 | 0.704 | 0.212 | deepseek_v4 | -0.158 | 0.987 | -0.266 | -0.064 |
| qwen3-4b-e2c.claude46_O_s4 | 0.085 | 0.704 | 0.221 | deepseek_v4 | -0.136 | 0.931 | -0.250 | -0.049 |
| qwen3-4b-e2c.claude46_O_s5 | 0.088 | 0.704 | 0.222 | deepseek_v4 | -0.134 | 0.930 | -0.251 | -0.041 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | 0.469 | 0.797 | 0.244 | gpt4o | 0.225 | 1.0e-04 | 0.152 | 0.299 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | 0.467 | 0.797 | 0.249 | gpt4o | 0.218 | 3.0e-04 | 0.139 | 0.298 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | 0.469 | 0.797 | 0.262 | gpt4o | 0.207 | 0.001 | 0.134 | 0.283 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | 0.482 | 0.797 | 0.249 | gpt4o | 0.233 | 4.0e-04 | 0.161 | 0.309 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | 0.465 | 0.797 | 0.276 | gpt4o | 0.189 | 0.009 | 0.116 | 0.265 |
| qwen3-4b-e2c.gpt4o_O_s1 | 0.294 | 0.904 | 0.396 | deepseek_v4 | -0.102 | 0.631 | -0.192 | -0.015 |
| qwen3-4b-e2c.gpt4o_O_s2 | 0.300 | 0.904 | 0.461 | deepseek_v4 | -0.161 | 0.949 | -0.257 | -0.068 |
| qwen3-4b-e2c.gpt4o_O_s3 | 0.311 | 0.904 | 0.411 | deepseek_v4 | -0.100 | 0.543 | -0.184 | -0.018 |
| qwen3-4b-e2c.gpt4o_O_s4 | 0.318 | 0.904 | 0.408 | deepseek_v4 | -0.091 | 0.453 | -0.183 | -0.002 |
| qwen3-4b-e2c.gpt4o_O_s5 | 0.338 | 0.904 | 0.456 | deepseek_v4 | -0.119 | 0.686 | -0.211 | -0.029 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.206 | 0.041 | 5 |
| claude46 | T1 | -0.171 | 0.025 | 5 |
| claude46 | T3 | -0.099 | 0.026 | 5 |
| claude46 | T5 | -0.071 | 0.050 | 5 |
| claude46 | T6 | -0.037 | 0.025 | 5 |
| deepseek_v4 | T0 | 0.115 | 0.038 | 5 |
| deepseek_v4 | T1 | 0.081 | 0.044 | 5 |
| deepseek_v4 | T3 | 0.120 | 0.044 | 5 |
| deepseek_v4 | T5 | 0.041 | 0.032 | 5 |
| deepseek_v4 | T6 | 0.260 | 0.023 | 5 |
| gpt4o | T0 | -0.184 | 0.059 | 5 |
| gpt4o | T1 | -0.064 | 0.023 | 5 |
| gpt4o | T3 | 0.008 | 0.046 | 5 |
| gpt4o | T5 | -0.087 | 0.054 | 5 |
| gpt4o | T6 | -0.071 | 0.038 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.314 | 0.070 | 0.704 | 0.149 | deepseek_v4 | -0.079 | -0.213 | 0.005 | 0.796 | -0.045 | 1.000 |
| deepseek_v4 | 5 | 290 | 0.703 | 0.333 | 0.797 | 0.099 | gpt4o | 0.234 | 0.136 | 0.300 | 1.0e-04 | 0.081 | 3.0e-04 |
| gpt4o | 5 | 290 | 0.585 | 0.210 | 0.904 | 0.301 | deepseek_v4 | -0.091 | -0.200 | 0.014 | 0.619 | -0.079 | 1.000 |

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

- P1 mean deltaRhoPartial 0.021 vs run-reassignment null mean -0.049 sd 0.020, p 7.3e-05 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 4.931, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.051 [0.009, 0.094] p 0.012 alone would read pass; the frozen rule (version 5) also needs D_specific 0.077 [0.031, 0.125] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.016 | 0.011 | 0.032 |
| agree_own | deepseek_v4 | O | 10 | 0.014 | 0.011 | 0.030 |
| agree_own | gpt4o | O | 10 | 0.008 | 0.005 | 0.015 |
| agree_own | all | all | 30 | 0.013 | 0.010 | 0.030 |
| jsd_own | claude46 | O | 10 | 0.008 | 0.005 | 0.015 |
| jsd_own | deepseek_v4 | O | 10 | 0.005 | 0.003 | 0.009 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.003 | 0.011 |
| jsd_own | all | all | 30 | 0.006 | 0.004 | 0.014 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.006 | 0.003 | 0.011 |
| flip_rate | deepseek_v4 | O | 10 | 0.018 | 0.010 | 0.032 |
| flip_rate | gpt4o | O | 10 | 0.015 | 0.010 | 0.030 |
| flip_rate | all | all | 30 | 0.013 | 0.010 | 0.030 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.002 | 0.001 | 0.004 |
| mean_jsd | deepseek_v4 | O | 10 | 0.016 | 0.010 | 0.031 |
| mean_jsd | gpt4o | O | 10 | 0.009 | 0.006 | 0.018 |
| mean_jsd | all | all | 30 | 0.009 | 0.009 | 0.026 |
| delta_rho | claude46 | O | 10 | 0.020 | 0.013 | 0.039 |
| delta_rho | deepseek_v4 | O | 10 | 0.021 | 0.012 | 0.041 |
| delta_rho | gpt4o | O | 10 | 0.032 | 0.024 | 0.066 |
| delta_rho | all | all | 30 | 0.024 | 0.018 | 0.060 |
| delta_rho_partial | claude46 | O | 10 | 0.022 | 0.015 | 0.046 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.025 | 0.016 | 0.050 |
| delta_rho_partial | gpt4o | O | 10 | 0.040 | 0.031 | 0.084 |
| delta_rho_partial | all | all | 30 | 0.029 | 0.023 | 0.077 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.