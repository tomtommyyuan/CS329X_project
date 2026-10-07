# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.998, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.711 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.093 [-0.219, -0.006] p_perm 0.873 (null mean -0.049) p_holm 1.000; deepseek_v4 0.067 [-0.050, 0.186] p_perm 0.472 (null mean 0.063) p_holm 1.000; gpt4o -0.051 [-0.167, 0.075] p_perm 0.458 (null mean -0.055) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.027 [-0.014, 0.067], p 0.054; D_specific 0.036 [-0.006, 0.078], D_shared -0.009 (290 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 290 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.014 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.031, sd 0.009, p 0.033, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.272 (pearson 0.937, seed-noise sd 0.009, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.036 [-0.184, 0.047] p_holm 1.000; deepseek_v4 0.029 [-0.106, 0.156] p_holm 1.000; gpt4o -0.022 [-0.153, 0.117] p_holm 0.934 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.018 [-0.045, 0.076], p 0.221 (288 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.037 [-9.0e-04, 0.076], p 0.063 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.034 [-0.007, 0.074] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.380 [0.327, 0.434], margin over the next 0.100 [0.036, 0.167] (290 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.099 | 0.704 | 0.141 | 0.192 | deepseek_v4 | -0.093 | -0.219 | -0.006 | 0.873 | -0.049 | 0.040 | 1.000 | False |
| deepseek_v4 | 5 | 290 | 0.371 | 0.797 | 0.465 | 0.304 | gpt4o | 0.067 | -0.050 | 0.186 | 0.472 | 0.063 | 0.036 | 1.000 | False |
| gpt4o | 5 | 290 | 0.248 | 0.904 | 0.274 | 0.299 | deepseek_v4 | -0.051 | -0.167 | 0.075 | 0.458 | -0.055 | 0.038 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.025 | -0.052 | 0.010 | 0.001 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.027 | -0.014 | 0.067 | 0.054 | 0.003 | 0.015 | 0.037 | 290 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.009 | 0.036 | -0.006 | 0.078 | 0.020 | 0.003 | 0.016 | 0.034 | -0.007 | 0.074 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2ckn.claude46_O_pooled 0.064, qwen3-4b-e2ckn.deepseek_v4_O_pooled 0.093, qwen3-4b-e2ckn.gpt4o_O_pooled 0.076.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | 0.072 | 0.108 | 0.107 | 0.704 | -0.035 | 0.075 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.090 | 0.226 | 0.198 | 0.797 | 0.083 | 0.033 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | 0.071 | 0.183 | 0.161 | 0.904 | 0.033 | 0.001 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | -0.023 | -0.109 | -0.087 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.024 | 0.077 | 0.064 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | -0.010 | -0.002 | -0.005 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | 0.099 | 0.192 | 0.170 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.136 | 0.371 | 0.304 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | 0.110 | 0.299 | 0.248 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_pooled | -0.011 | 0.253 | 0.039 |
| qwen3-4b-e2ckn.deepseek_v4_O_pooled | 0.003 | 0.267 | 0.088 |
| qwen3-4b-e2ckn.gpt4o_O_pooled | -0.071 | 0.171 | 0.038 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 290 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 290 | 0.031 | 0.019 | 0.044 |
| students:deepseek_v4 | 5 | 290 | 0.125 | 0.100 | 0.151 |
| students:gpt4o | 5 | 290 | 0.081 | 0.062 | 0.101 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |
| base_prior | 1 | 290 | 0.146 | 0.133 | 0.159 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.095 | -0.116 | -0.074 |
| students:claude46 | students:gpt4o | -0.050 | -0.066 | -0.035 |
| students:claude46 | teacher:claude46 | -0.014 | -0.038 | 0.010 |
| students:claude46 | base_prior | -0.115 | -0.131 | -0.099 |
| students:deepseek_v4 | students:gpt4o | 0.044 | 0.025 | 0.065 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.012 | -0.014 | 0.038 |
| students:deepseek_v4 | base_prior | -0.021 | -0.044 | 0.003 |
| students:gpt4o | teacher:gpt4o | 0.018 | -0.007 | 0.043 |
| students:gpt4o | base_prior | -0.065 | -0.086 | -0.044 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.057 | -0.120 | 0.178 | 8 |
| qwen3-4b.base_B_s0 | base_prior | 0.068 | -0.078 | 0.146 | 290 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.031 | 0.008 | 5 |
| deepseek_v4 | 0.113 | 0.125 | 0.009 | 5 |
| gpt4o | 0.063 | 0.081 | 0.009 | 5 |

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
| qwen3-4b.base_B_s0 | 0.213 | 0.097 | 8 | nan | 0.830 | nan | 0.188 | 0.028 |
| qwen3-4b-e2ckn.claude46_O_s1 | 0.999 | 0.052 | 300 | 0.860 | 0.856 | 0.129 | 0.042 | 0.023 |
| qwen3-4b-e2ckn.claude46_O_s2 | 1.000 | 0.065 | 300 | 0.850 | 0.853 | 0.130 | 0.043 | 0.019 |
| qwen3-4b-e2ckn.claude46_O_s3 | 1.000 | 0.059 | 300 | 0.854 | 0.856 | 0.128 | 0.041 | 0.018 |
| qwen3-4b-e2ckn.claude46_O_s4 | 1.000 | 0.049 | 300 | 0.855 | 0.853 | 0.131 | 0.041 | 0.020 |
| qwen3-4b-e2ckn.claude46_O_s5 | 1.000 | 0.057 | 300 | 0.866 | 0.856 | 0.126 | 0.033 | 0.018 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 1.000 | 0.084 | 300 | 0.851 | 0.846 | 0.093 | 0.080 | 0.045 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 1.000 | 0.081 | 300 | 0.852 | 0.853 | 0.094 | 0.076 | 0.045 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 1.000 | 0.077 | 300 | 0.849 | 0.855 | 0.089 | 0.081 | 0.043 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 1.000 | 0.087 | 300 | 0.863 | 0.848 | 0.087 | 0.088 | 0.044 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 0.999 | 0.074 | 299 | 0.863 | 0.858 | 0.086 | 0.067 | 0.034 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 1.000 | 0.065 | 300 | 0.851 | 0.854 | 0.118 | 0.057 | 0.030 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 1.000 | 0.071 | 300 | 0.834 | 0.841 | 0.119 | 0.047 | 0.022 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 1.000 | 0.072 | 300 | 0.848 | 0.859 | 0.116 | 0.052 | 0.026 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 1.000 | 0.066 | 300 | 0.847 | 0.850 | 0.119 | 0.046 | 0.022 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 1.000 | 0.059 | 300 | 0.841 | 0.844 | 0.117 | 0.052 | 0.027 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.776 | 0.830 | 0.782 | 0.185 | 0.098 | 0.163 |
| qwen3-4b-e2ckn.claude46_O_s1 | 0.860 | 0.856 | 0.840 | 0.129 | 0.100 | 0.125 |
| qwen3-4b-e2ckn.claude46_O_s2 | 0.850 | 0.853 | 0.832 | 0.130 | 0.099 | 0.131 |
| qwen3-4b-e2ckn.claude46_O_s3 | 0.854 | 0.856 | 0.840 | 0.128 | 0.099 | 0.121 |
| qwen3-4b-e2ckn.claude46_O_s4 | 0.855 | 0.853 | 0.841 | 0.131 | 0.102 | 0.119 |
| qwen3-4b-e2ckn.claude46_O_s5 | 0.866 | 0.856 | 0.845 | 0.126 | 0.100 | 0.125 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 0.846 | 0.851 | 0.842 | 0.135 | 0.093 | 0.122 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 0.853 | 0.852 | 0.838 | 0.136 | 0.094 | 0.125 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 0.855 | 0.849 | 0.851 | 0.127 | 0.089 | 0.113 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 0.848 | 0.863 | 0.845 | 0.133 | 0.087 | 0.115 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 0.852 | 0.863 | 0.858 | 0.130 | 0.086 | 0.110 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 0.854 | 0.852 | 0.851 | 0.134 | 0.100 | 0.118 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 0.838 | 0.841 | 0.834 | 0.138 | 0.096 | 0.119 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 0.859 | 0.846 | 0.848 | 0.130 | 0.097 | 0.116 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 0.850 | 0.842 | 0.847 | 0.134 | 0.099 | 0.119 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 0.840 | 0.844 | 0.841 | 0.139 | 0.098 | 0.117 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.213 | nan | 0.830 | nan | 0.188 | 0.028 |
| claude46 | O | 5 | 1.000 | 0.857 | 0.855 | 0.129 | 0.040 | 0.020 |
| deepseek_v4 | O | 5 | 1.000 | 0.856 | 0.852 | 0.090 | 0.078 | 0.042 |
| gpt4o | O | 5 | 1.000 | 0.844 | 0.850 | 0.118 | 0.051 | 0.025 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_s1 | 290.000 | 0.255 | 0.110 | 0.704 | 0.104 | deepseek_v4 | 0.006 | 0.187 | -0.031 | -0.093 | 0.082 | 0.110 | 0.104 | 0.075 |
| qwen3-4b-e2ckn.claude46_O_s2 | 290.000 | 0.186 | 0.008 | 0.704 | 0.083 | gpt4o | -0.075 | 0.880 | -0.028 | -0.232 | 0.022 | 0.008 | 0.051 | 0.083 |
| qwen3-4b-e2ckn.claude46_O_s3 | 290.000 | 0.246 | 0.048 | 0.704 | 0.103 | deepseek_v4 | -0.055 | 0.753 | -0.027 | -0.195 | 0.032 | 0.048 | 0.103 | 0.085 |
| qwen3-4b-e2ckn.claude46_O_s4 | 290.000 | 0.199 | 0.087 | 0.704 | 0.126 | gpt4o | -0.039 | 0.670 | -0.023 | -0.184 | 0.086 | 0.087 | 0.067 | 0.126 |
| qwen3-4b-e2ckn.claude46_O_s5 | 290.000 | 0.167 | 0.042 | 0.704 | 0.123 | deepseek_v4 | -0.081 | 0.919 | -0.024 | -0.203 | 0.006 | 0.042 | 0.123 | 0.079 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 290.000 | 0.443 | 0.218 | 0.797 | 0.189 | gpt4o | 0.029 | 0.489 | 0.028 | -0.100 | 0.156 | 0.096 | 0.218 | 0.189 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 290.000 | 0.446 | 0.215 | 0.797 | 0.160 | gpt4o | 0.055 | 0.247 | 0.028 | -0.076 | 0.180 | 0.053 | 0.215 | 0.160 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 290.000 | 0.468 | 0.201 | 0.797 | 0.193 | gpt4o | 0.008 | 0.744 | 0.032 | -0.123 | 0.137 | 0.049 | 0.201 | 0.193 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 290.000 | 0.445 | 0.173 | 0.797 | 0.153 | gpt4o | 0.019 | 0.545 | 0.023 | -0.118 | 0.116 | 0.117 | 0.173 | 0.153 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 290.000 | 0.445 | 0.186 | 0.797 | 0.173 | gpt4o | 0.013 | 0.605 | 0.023 | -0.117 | 0.129 | 0.077 | 0.186 | 0.173 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 290.000 | 0.341 | 0.137 | 0.904 | 0.155 | deepseek_v4 | -0.018 | 0.280 | -0.041 | -0.148 | 0.123 | 0.060 | 0.155 | 0.137 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 290.000 | 0.347 | 0.100 | 0.904 | 0.117 | deepseek_v4 | -0.016 | 0.259 | -0.042 | -0.179 | 0.123 | 0.084 | 0.117 | 0.100 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 290.000 | 0.320 | 0.164 | 0.904 | 0.163 | deepseek_v4 | 0.002 | 0.194 | -0.031 | -0.123 | 0.125 | 0.094 | 0.163 | 0.164 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 290.000 | 0.305 | 0.182 | 0.904 | 0.179 | deepseek_v4 | 0.003 | 0.151 | -0.038 | -0.112 | 0.127 | 0.063 | 0.179 | 0.182 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 290.000 | 0.336 | 0.115 | 0.904 | 0.179 | deepseek_v4 | -0.064 | 0.750 | -0.037 | -0.184 | 0.062 | 0.013 | 0.179 | 0.115 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.049 | 0.035 | 5 |
| deepseek_v4 | 0.025 | 0.019 | 5 |
| gpt4o | -0.019 | 0.027 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.014 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ckn.claude46_O_s1 | 0.136 | 0.704 | 0.190 | deepseek_v4 | -0.055 | 0.512 | -0.147 | 0.025 |
| qwen3-4b-e2ckn.claude46_O_s2 | 0.030 | 0.704 | 0.131 | gpt4o | -0.101 | 0.928 | -0.250 | -0.015 |
| qwen3-4b-e2ckn.claude46_O_s3 | 0.075 | 0.704 | 0.186 | deepseek_v4 | -0.111 | 0.948 | -0.231 | -0.022 |
| qwen3-4b-e2ckn.claude46_O_s4 | 0.108 | 0.704 | 0.174 | gpt4o | -0.066 | 0.781 | -0.208 | 0.056 |
| qwen3-4b-e2ckn.claude46_O_s5 | 0.061 | 0.704 | 0.176 | deepseek_v4 | -0.115 | 0.972 | -0.230 | -0.027 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | 0.349 | 0.797 | 0.287 | gpt4o | 0.062 | 0.459 | -0.052 | 0.179 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | 0.348 | 0.797 | 0.262 | gpt4o | 0.085 | 0.224 | -0.029 | 0.200 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | 0.342 | 0.797 | 0.295 | gpt4o | 0.047 | 0.666 | -0.067 | 0.164 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | 0.312 | 0.797 | 0.257 | gpt4o | 0.056 | 0.471 | -0.065 | 0.168 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | 0.323 | 0.797 | 0.273 | gpt4o | 0.050 | 0.528 | -0.067 | 0.161 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | 0.219 | 0.904 | 0.264 | deepseek_v4 | -0.045 | 0.417 | -0.163 | 0.088 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | 0.188 | 0.904 | 0.233 | deepseek_v4 | -0.046 | 0.404 | -0.188 | 0.096 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | 0.239 | 0.904 | 0.264 | deepseek_v4 | -0.025 | 0.340 | -0.137 | 0.093 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | 0.252 | 0.904 | 0.273 | deepseek_v4 | -0.022 | 0.242 | -0.126 | 0.090 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | 0.199 | 0.904 | 0.284 | deepseek_v4 | -0.085 | 0.838 | -0.193 | 0.029 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.233 | 0.067 | 5 |
| claude46 | T1 | -0.182 | 0.090 | 5 |
| claude46 | T3 | -0.060 | 0.051 | 5 |
| claude46 | T5 | -0.019 | 0.070 | 5 |
| claude46 | T6 | -0.033 | 0.055 | 5 |
| deepseek_v4 | T0 | 0.159 | 0.053 | 5 |
| deepseek_v4 | T1 | 0.115 | 0.030 | 5 |
| deepseek_v4 | T3 | -0.141 | 0.055 | 5 |
| deepseek_v4 | T5 | 0.072 | 0.077 | 5 |
| deepseek_v4 | T6 | 0.060 | 0.044 | 5 |
| gpt4o | T0 | -0.114 | 0.092 | 5 |
| gpt4o | T1 | -0.115 | 0.033 | 5 |
| gpt4o | T3 | 0.023 | 0.042 | 5 |
| gpt4o | T5 | 0.044 | 0.025 | 5 |
| gpt4o | T6 | -0.077 | 0.060 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.252 | 0.072 | 0.704 | 0.108 | deepseek_v4 | -0.036 | -0.184 | 0.047 | 0.581 | -0.029 | 1.000 |
| deepseek_v4 | 5 | 290 | 0.497 | 0.226 | 0.797 | 0.198 | gpt4o | 0.029 | -0.106 | 0.156 | 0.536 | 0.032 | 1.000 |
| gpt4o | 5 | 290 | 0.373 | 0.161 | 0.904 | 0.183 | deepseek_v4 | -0.022 | -0.153 | 0.117 | 0.311 | -0.041 | 0.934 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 290 | 0.118 | 0.704 | 0.035 | 0.198 | 3 | -0.262 | -0.357 | -0.172 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 290 | 0.380 | 0.797 | 0.327 | 0.434 | 1 | 0.100 | 0.036 | 0.167 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 290 | 0.280 | 0.904 | 0.213 | 0.344 | 2 | -0.100 | -0.167 | -0.036 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 3/5 seeds pass -> partial (old rule, not the verdict)
- deepseek_v4: 3/5 seeds pass -> partial (old rule, not the verdict)
- gpt4o: 0/5 seeds pass -> fail (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial -0.014 vs run-reassignment null mean -0.031 sd 0.009, p 0.033 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 1.272, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.027 [-0.014, 0.067] p 0.054 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.036 [-0.006, 0.078] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.007 | 0.004 | 0.014 |
| agree_own | deepseek_v4 | O | 10 | 0.008 | 0.006 | 0.014 |
| agree_own | gpt4o | O | 10 | 0.008 | 0.005 | 0.015 |
| agree_own | all | all | 30 | 0.008 | 0.005 | 0.015 |
| jsd_own | claude46 | O | 10 | 0.003 | 0.002 | 0.005 |
| jsd_own | deepseek_v4 | O | 10 | 0.005 | 0.003 | 0.008 |
| jsd_own | gpt4o | O | 10 | 0.002 | 9.1e-04 | 0.003 |
| jsd_own | all | all | 30 | 0.003 | 0.002 | 0.007 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.004 | 0.004 | 0.010 |
| flip_rate | deepseek_v4 | O | 10 | 0.010 | 0.006 | 0.018 |
| flip_rate | gpt4o | O | 10 | 0.006 | 0.004 | 0.011 |
| flip_rate | all | all | 30 | 0.006 | 0.005 | 0.014 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.002 | 0.002 | 0.004 |
| mean_jsd | deepseek_v4 | O | 10 | 0.005 | 0.005 | 0.011 |
| mean_jsd | gpt4o | O | 10 | 0.004 | 0.003 | 0.009 |
| mean_jsd | all | all | 30 | 0.004 | 0.003 | 0.010 |
| delta_rho | claude46 | O | 10 | 0.033 | 0.021 | 0.058 |
| delta_rho | deepseek_v4 | O | 10 | 0.018 | 0.013 | 0.037 |
| delta_rho | gpt4o | O | 10 | 0.030 | 0.021 | 0.062 |
| delta_rho | all | all | 30 | 0.027 | 0.019 | 0.060 |
| delta_rho_partial | claude46 | O | 10 | 0.042 | 0.027 | 0.084 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.022 | 0.015 | 0.045 |
| delta_rho_partial | gpt4o | O | 10 | 0.031 | 0.024 | 0.066 |
| delta_rho_partial | all | all | 30 | 0.032 | 0.023 | 0.075 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.