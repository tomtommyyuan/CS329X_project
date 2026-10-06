# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.983, min answer rate 0.999 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.862 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.155 [-0.307, -0.055] p_perm 0.973 (null mean -0.073) p_holm 0.973; deepseek_v4 0.127 [0.029, 0.229] p_perm 0.116 (null mean 0.082) p_holm 0.348; gpt4o -0.067 [-0.185, 0.054] p_perm 0.348 (null mean -0.082) p_holm 0.696; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.027 [-0.013, 0.070], p 0.061; D_specific 0.067 [0.011, 0.125], D_shared -0.040 (290 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 290 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.014 | teacher-level exact p 0.333 (rank 2 of 6 relabellings, floor 0.167); the run-level null (mean -0.046, sd 0.014, p 0.012, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.441 (pearson 0.856, seed-noise sd 0.010, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.104 [-0.274, -0.005] p_holm 0.927; deepseek_v4 0.105 [-0.009, 0.217] p_holm 0.242; gpt4o -0.033 [-0.169, 0.103] p_holm 0.489 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.054 [-6.4e-04, 0.114], p 0.006 (288 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.033 [-0.003, 0.071], p 0.099 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.057 [0.011, 0.104] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.380 [0.327, 0.434], margin over the next 0.100 [0.036, 0.167] (290 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.085 | 0.704 | 0.121 | 0.240 | deepseek_v4 | -0.155 | -0.307 | -0.055 | 0.973 | -0.073 | 0.041 | 0.973 | False |
| deepseek_v4 | 5 | 290 | 0.444 | 0.797 | 0.557 | 0.317 | gpt4o | 0.127 | 0.029 | 0.229 | 0.116 | 0.082 | 0.037 | 0.348 | False |
| gpt4o | 5 | 290 | 0.374 | 0.904 | 0.413 | 0.440 | deepseek_v4 | -0.067 | -0.185 | 0.054 | 0.348 | -0.082 | 0.039 | 0.696 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.030 | -0.068 | 0.014 | 0.001 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.027 | -0.013 | 0.070 | 0.061 | 0.004 | 0.015 | 0.033 | 290 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.040 | 0.067 | 0.011 | 0.125 | 0.004 | 0.010 | 0.021 | 0.057 | 0.011 | 0.104 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b.claude46_O_pooled 0.040, qwen3-4b.deepseek_v4_O_pooled 0.095, qwen3-4b.gpt4o_O_pooled 0.075.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.055 | 0.150 | 0.158 | 0.704 | -0.099 | 0.114 |
| qwen3-4b.deepseek_v4_O_pooled | 0.131 | 0.322 | 0.216 | 0.797 | 0.148 | 0.071 |
| qwen3-4b.gpt4o_O_pooled | 0.184 | 0.317 | 0.283 | 0.904 | 0.033 | 0.016 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b.claude46_O_pooled | -0.180 | -0.349 | -0.240 |
| qwen3-4b.deepseek_v4_O_pooled | 0.031 | 0.110 | 0.047 |
| qwen3-4b.gpt4o_O_pooled | 0.057 | 0.049 | 0.069 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.085 | 0.240 | 0.225 |
| qwen3-4b.deepseek_v4_O_pooled | 0.171 | 0.444 | 0.317 |
| qwen3-4b.gpt4o_O_pooled | 0.216 | 0.440 | 0.374 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b.claude46_O_pooled | 0.029 | 0.285 | 0.066 |
| qwen3-4b.deepseek_v4_O_pooled | -0.038 | 0.377 | -0.078 |
| qwen3-4b.gpt4o_O_pooled | -0.040 | 0.299 | 0.002 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 290 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 290 | 0.026 | 0.018 | 0.034 |
| students:deepseek_v4 | 5 | 290 | 0.140 | 0.116 | 0.166 |
| students:gpt4o | 5 | 290 | 0.108 | 0.089 | 0.129 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |
| students:R | 3 | 290 | 7.9e-04 | 7.1e-04 | 8.6e-04 |
| base_prior | 1 | 290 | 0.146 | 0.133 | 0.159 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.114 | -0.136 | -0.094 |
| students:claude46 | students:gpt4o | -0.082 | -0.099 | -0.067 |
| students:claude46 | teacher:claude46 | -0.019 | -0.042 | 0.004 |
| students:claude46 | students:R | 0.025 | 0.018 | 0.033 |
| students:claude46 | base_prior | -0.120 | -0.134 | -0.107 |
| students:deepseek_v4 | students:gpt4o | 0.032 | 0.017 | 0.047 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.027 | 0.002 | 0.053 |
| students:deepseek_v4 | students:R | 0.139 | 0.115 | 0.166 |
| students:deepseek_v4 | base_prior | -0.006 | -0.030 | 0.019 |
| students:gpt4o | teacher:gpt4o | 0.045 | 0.022 | 0.068 |
| students:gpt4o | students:R | 0.108 | 0.088 | 0.128 |
| students:gpt4o | base_prior | -0.038 | -0.057 | -0.017 |
| students:R | base_prior | -0.145 | -0.158 | -0.132 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.057 | -0.120 | 0.178 | 8 |
| qwen3-4b.random_R_s1 | run | -6.0e-04 | -7.5e-04 | 1.4e-04 | 290 |
| qwen3-4b.random_R_s2 | run | 4.0e-04 | 1.2e-04 | 2.8e-04 | 290 |
| qwen3-4b.random_R_s3 | run | 8.9e-04 | -0.001 | 0.002 | 290 |
| qwen3-4b.base_B_s0 | base_prior | 0.068 | -0.078 | 0.146 | 290 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.026 | 0.004 | 5 |
| deepseek_v4 | 0.113 | 0.140 | 0.012 | 5 |
| gpt4o | 0.063 | 0.108 | 0.012 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_s1 | 5642 | 0.999 | 5642 | 5642 | 0 | 0 | 0.985 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s2 | 5642 | 1.000 | 5642 | 5642 | 0 | 0 | 0.988 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s3 | 5642 | 1.000 | 5642 | 5642 | 0 | 0 | 0.985 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s4 | 5642 | 0.999 | 5642 | 5642 | 0 | 0 | 0.985 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s5 | 5642 | 1.000 | 5642 | 5642 | 0 | 0 | 0.985 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/claude46_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s1 | 4936 | 1.000 | 4936 | 4936 | 0 | 0 | 0.995 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s2 | 4936 | 1.000 | 4936 | 4936 | 0 | 0 | 0.996 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s3 | 4936 | 1.000 | 4936 | 4936 | 0 | 0 | 0.989 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s4 | 4936 | 1.000 | 4936 | 4936 | 0 | 0 | 0.992 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s5 | 4936 | 1.000 | 4936 | 4936 | 0 | 0 | 0.991 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/deepseek_v4_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s1 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.986 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s2 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.985 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s3 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.984 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s4 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.985 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s5 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.983 | True | /hai/scratch/tomyyc/CS329X_project/data/sft/gpt4o_O_s1.jsonl |
| qwen3-4b.random_R_s1 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.554 | nan | /hai/scratch/tomyyc/CS329X_project/data/sft/random_R_s1.jsonl |
| qwen3-4b.random_R_s2 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.553 | nan | /hai/scratch/tomyyc/CS329X_project/data/sft/random_R_s2.jsonl |
| qwen3-4b.random_R_s3 | 5619 | 1.000 | 5619 | 5619 | 0 | 0 | 0.557 | nan | /hai/scratch/tomyyc/CS329X_project/data/sft/random_R_s3.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 299 | 166 | 5 | 1495 | 0.930 | 0.902 | 0.954 | True |
| claude46 | gpt4o | 357 | 186 | 5 | 1785 | 0.919 | 0.892 | 0.945 | True |
| deepseek_v4 | claude46 | 299 | 166 | 5 | 1495 | 0.951 | 0.931 | 0.968 | True |
| deepseek_v4 | gpt4o | 198 | 126 | 5 | 990 | 0.918 | 0.889 | 0.944 | True |
| gpt4o | claude46 | 357 | 186 | 5 | 1785 | 0.910 | 0.883 | 0.934 | True |
| gpt4o | deepseek_v4 | 198 | 126 | 5 | 990 | 0.900 | 0.862 | 0.933 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.213 | 0.097 | 8 | nan | 0.830 | nan | 0.188 | 0.028 |
| qwen3-4b.claude46_O_s1 | 1.000 | 0.059 | 300 | 0.878 | 0.859 | 0.103 | 0.026 | 0.009 |
| qwen3-4b.claude46_O_s2 | 0.999 | 0.058 | 299 | 0.882 | 0.861 | 0.099 | 0.031 | 0.008 |
| qwen3-4b.claude46_O_s3 | 0.999 | 0.057 | 299 | 0.872 | 0.864 | 0.107 | 0.021 | 0.007 |
| qwen3-4b.claude46_O_s4 | 1.000 | 0.059 | 300 | 0.881 | 0.853 | 0.103 | 0.025 | 0.007 |
| qwen3-4b.claude46_O_s5 | 1.000 | 0.064 | 299 | 0.898 | 0.875 | 0.095 | 0.025 | 0.007 |
| qwen3-4b.deepseek_v4_O_s1 | 1.000 | 0.058 | 300 | 0.856 | 0.848 | 0.082 | 0.084 | 0.040 |
| qwen3-4b.deepseek_v4_O_s2 | 1.000 | 0.056 | 300 | 0.862 | 0.848 | 0.084 | 0.084 | 0.046 |
| qwen3-4b.deepseek_v4_O_s3 | 1.000 | 0.052 | 300 | 0.855 | 0.852 | 0.077 | 0.078 | 0.034 |
| qwen3-4b.deepseek_v4_O_s4 | 1.000 | 0.064 | 300 | 0.853 | 0.838 | 0.083 | 0.089 | 0.042 |
| qwen3-4b.deepseek_v4_O_s5 | 1.000 | 0.057 | 300 | 0.860 | 0.854 | 0.073 | 0.074 | 0.031 |
| qwen3-4b.gpt4o_O_s1 | 1.000 | 0.064 | 300 | 0.856 | 0.849 | 0.096 | 0.068 | 0.026 |
| qwen3-4b.gpt4o_O_s2 | 1.000 | 0.059 | 300 | 0.867 | 0.865 | 0.090 | 0.059 | 0.016 |
| qwen3-4b.gpt4o_O_s3 | 1.000 | 0.066 | 300 | 0.860 | 0.857 | 0.095 | 0.068 | 0.026 |
| qwen3-4b.gpt4o_O_s4 | 1.000 | 0.061 | 300 | 0.847 | 0.848 | 0.097 | 0.073 | 0.023 |
| qwen3-4b.gpt4o_O_s5 | 1.000 | 0.066 | 300 | 0.856 | 0.857 | 0.089 | 0.077 | 0.024 |
| qwen3-4b.random_R_s1 | 1.000 | 0.054 | 300 | nan | 0.583 | nan | 0.072 | 4.4e-06 |
| qwen3-4b.random_R_s2 | 1.000 | 0.044 | 300 | nan | 0.436 | nan | 0.034 | 2.8e-06 |
| qwen3-4b.random_R_s3 | 1.000 | 0.019 | 300 | nan | 0.359 | nan | 0.059 | 6.3e-06 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.776 | 0.830 | 0.782 | 0.185 | 0.098 | 0.163 |
| qwen3-4b.claude46_O_s1 | 0.878 | 0.855 | 0.859 | 0.103 | 0.080 | 0.098 |
| qwen3-4b.claude46_O_s2 | 0.882 | 0.860 | 0.861 | 0.099 | 0.079 | 0.096 |
| qwen3-4b.claude46_O_s3 | 0.872 | 0.862 | 0.864 | 0.107 | 0.080 | 0.097 |
| qwen3-4b.claude46_O_s4 | 0.881 | 0.852 | 0.853 | 0.103 | 0.085 | 0.099 |
| qwen3-4b.claude46_O_s5 | 0.898 | 0.858 | 0.875 | 0.095 | 0.077 | 0.093 |
| qwen3-4b.deepseek_v4_O_s1 | 0.848 | 0.856 | 0.839 | 0.132 | 0.082 | 0.116 |
| qwen3-4b.deepseek_v4_O_s2 | 0.848 | 0.862 | 0.847 | 0.130 | 0.084 | 0.110 |
| qwen3-4b.deepseek_v4_O_s3 | 0.852 | 0.855 | 0.837 | 0.124 | 0.077 | 0.108 |
| qwen3-4b.deepseek_v4_O_s4 | 0.838 | 0.853 | 0.834 | 0.139 | 0.083 | 0.117 |
| qwen3-4b.deepseek_v4_O_s5 | 0.852 | 0.860 | 0.854 | 0.125 | 0.073 | 0.105 |
| qwen3-4b.gpt4o_O_s1 | 0.846 | 0.849 | 0.856 | 0.126 | 0.079 | 0.096 |
| qwen3-4b.gpt4o_O_s2 | 0.865 | 0.859 | 0.867 | 0.116 | 0.078 | 0.090 |
| qwen3-4b.gpt4o_O_s3 | 0.857 | 0.850 | 0.860 | 0.124 | 0.079 | 0.095 |
| qwen3-4b.gpt4o_O_s4 | 0.843 | 0.848 | 0.847 | 0.126 | 0.078 | 0.097 |
| qwen3-4b.gpt4o_O_s5 | 0.857 | 0.847 | 0.856 | 0.117 | 0.074 | 0.089 |
| qwen3-4b.random_R_s1 | 0.537 | 0.583 | 0.571 | 0.286 | 0.208 | 0.282 |
| qwen3-4b.random_R_s2 | 0.409 | 0.436 | 0.427 | 0.289 | 0.210 | 0.285 |
| qwen3-4b.random_R_s3 | 0.359 | 0.353 | 0.334 | 0.291 | 0.212 | 0.287 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.213 | nan | 0.830 | nan | 0.188 | 0.028 |
| claude46 | O | 5 | 1.000 | 0.882 | 0.862 | 0.101 | 0.026 | 0.007 |
| deepseek_v4 | O | 5 | 1.000 | 0.857 | 0.848 | 0.080 | 0.082 | 0.039 |
| gpt4o | O | 5 | 1.000 | 0.857 | 0.855 | 0.094 | 0.069 | 0.023 |
| random | R | 3 | 1.000 | nan | 0.459 | nan | 0.055 | 4.5e-06 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_s1 | 290.000 | 0.294 | 0.086 | 0.704 | 0.188 | gpt4o | -0.102 | 0.891 | -0.047 | -0.266 | -8.6e-05 | 0.086 | 0.169 | 0.188 |
| qwen3-4b.claude46_O_s2 | 290.000 | 0.254 | 0.058 | 0.704 | 0.151 | gpt4o | -0.092 | 0.898 | -0.040 | -0.282 | 0.032 | 0.058 | 0.127 | 0.151 |
| qwen3-4b.claude46_O_s3 | 290.000 | 0.226 | 0.003 | 0.704 | 0.115 | deepseek_v4 | -0.112 | 0.968 | -0.034 | -0.271 | -0.016 | 0.003 | 0.115 | 0.109 |
| qwen3-4b.claude46_O_s4 | 290.000 | 0.260 | 0.010 | 0.704 | 0.153 | gpt4o | -0.143 | 0.992 | -0.036 | -0.308 | -0.007 | 0.010 | 0.079 | 0.153 |
| qwen3-4b.claude46_O_s5 | 290.000 | 0.230 | 0.083 | 0.704 | 0.175 | deepseek_v4 | -0.092 | 0.896 | -0.039 | -0.205 | 0.009 | 0.083 | 0.175 | 0.099 |
| qwen3-4b.deepseek_v4_O_s1 | 290.000 | 0.423 | 0.278 | 0.797 | 0.209 | gpt4o | 0.069 | 0.268 | 0.045 | -0.052 | 0.169 | 0.184 | 0.278 | 0.209 |
| qwen3-4b.deepseek_v4_O_s2 | 290.000 | 0.439 | 0.285 | 0.797 | 0.217 | gpt4o | 0.068 | 0.276 | 0.044 | -0.049 | 0.184 | 0.105 | 0.285 | 0.217 |
| qwen3-4b.deepseek_v4_O_s3 | 290.000 | 0.465 | 0.331 | 0.797 | 0.178 | gpt4o | 0.153 | 0.002 | 0.046 | 0.011 | 0.266 | 0.129 | 0.331 | 0.178 |
| qwen3-4b.deepseek_v4_O_s4 | 290.000 | 0.472 | 0.271 | 0.797 | 0.183 | gpt4o | 0.088 | 0.133 | 0.044 | -0.029 | 0.198 | 0.096 | 0.271 | 0.183 |
| qwen3-4b.deepseek_v4_O_s5 | 290.000 | 0.467 | 0.329 | 0.797 | 0.210 | gpt4o | 0.119 | 0.025 | 0.042 | -0.008 | 0.241 | 0.085 | 0.329 | 0.210 |
| qwen3-4b.gpt4o_O_s1 | 290.000 | 0.470 | 0.262 | 0.904 | 0.296 | deepseek_v4 | -0.034 | 0.252 | -0.062 | -0.169 | 0.097 | 0.146 | 0.296 | 0.262 |
| qwen3-4b.gpt4o_O_s2 | 290.000 | 0.426 | 0.263 | 0.904 | 0.300 | deepseek_v4 | -0.037 | 0.285 | -0.061 | -0.218 | 0.126 | 0.243 | 0.300 | 0.263 |
| qwen3-4b.gpt4o_O_s3 | 290.000 | 0.465 | 0.281 | 0.904 | 0.275 | deepseek_v4 | 0.006 | 0.060 | -0.060 | -0.131 | 0.140 | 0.181 | 0.275 | 0.281 |
| qwen3-4b.gpt4o_O_s4 | 290.000 | 0.459 | 0.201 | 0.904 | 0.284 | deepseek_v4 | -0.083 | 0.700 | -0.061 | -0.208 | 0.042 | 0.142 | 0.284 | 0.201 |
| qwen3-4b.gpt4o_O_s5 | 290.000 | 0.451 | 0.307 | 0.904 | 0.319 | deepseek_v4 | -0.012 | 0.144 | -0.057 | -0.133 | 0.109 | 0.154 | 0.319 | 0.307 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.108 | 0.021 | 5 |
| deepseek_v4 | 0.100 | 0.036 | 5 |
| gpt4o | -0.032 | 0.034 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.014 | 0.333 | 2 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_O_s1 | 0.116 | 0.704 | 0.261 | deepseek_v4 | -0.145 | 0.935 | -0.293 | -0.053 |
| qwen3-4b.claude46_O_s2 | 0.086 | 0.704 | 0.211 | gpt4o | -0.125 | 0.922 | -0.307 | -0.015 |
| qwen3-4b.claude46_O_s3 | 0.029 | 0.704 | 0.189 | deepseek_v4 | -0.160 | 0.992 | -0.299 | -0.056 |
| qwen3-4b.claude46_O_s4 | 0.040 | 0.704 | 0.215 | gpt4o | -0.175 | 0.995 | -0.336 | -0.049 |
| qwen3-4b.claude46_O_s5 | 0.107 | 0.704 | 0.245 | deepseek_v4 | -0.138 | 0.957 | -0.246 | -0.036 |
| qwen3-4b.deepseek_v4_O_s1 | 0.394 | 0.797 | 0.300 | gpt4o | 0.094 | 0.331 | -0.007 | 0.194 |
| qwen3-4b.deepseek_v4_O_s2 | 0.404 | 0.797 | 0.310 | gpt4o | 0.094 | 0.330 | -0.009 | 0.200 |
| qwen3-4b.deepseek_v4_O_s3 | 0.448 | 0.797 | 0.282 | gpt4o | 0.166 | 0.006 | 0.049 | 0.280 |
| qwen3-4b.deepseek_v4_O_s4 | 0.401 | 0.797 | 0.287 | gpt4o | 0.114 | 0.151 | 0.012 | 0.216 |
| qwen3-4b.deepseek_v4_O_s5 | 0.446 | 0.797 | 0.309 | gpt4o | 0.137 | 0.044 | 0.028 | 0.246 |
| qwen3-4b.gpt4o_O_s1 | 0.353 | 0.904 | 0.420 | deepseek_v4 | -0.067 | 0.363 | -0.185 | 0.048 |
| qwen3-4b.gpt4o_O_s2 | 0.348 | 0.904 | 0.412 | deepseek_v4 | -0.065 | 0.366 | -0.220 | 0.082 |
| qwen3-4b.gpt4o_O_s3 | 0.369 | 0.904 | 0.402 | deepseek_v4 | -0.033 | 0.128 | -0.158 | 0.094 |
| qwen3-4b.gpt4o_O_s4 | 0.300 | 0.904 | 0.408 | deepseek_v4 | -0.108 | 0.771 | -0.219 | 0.001 |
| qwen3-4b.gpt4o_O_s5 | 0.390 | 0.904 | 0.435 | deepseek_v4 | -0.045 | 0.225 | -0.156 | 0.063 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.241 | 0.058 | 5 |
| claude46 | T1 | -0.082 | 0.065 | 5 |
| claude46 | T3 | -0.118 | 0.051 | 5 |
| claude46 | T5 | -0.155 | 0.040 | 5 |
| claude46 | T6 | -0.100 | 0.026 | 5 |
| deepseek_v4 | T0 | 0.391 | 0.011 | 5 |
| deepseek_v4 | T1 | 0.112 | 0.076 | 5 |
| deepseek_v4 | T3 | 0.019 | 0.075 | 5 |
| deepseek_v4 | T5 | 0.096 | 0.044 | 5 |
| deepseek_v4 | T6 | 0.090 | 0.048 | 5 |
| gpt4o | T0 | -0.273 | 0.037 | 5 |
| gpt4o | T1 | -0.032 | 0.071 | 5 |
| gpt4o | T3 | 0.110 | 0.048 | 5 |
| gpt4o | T5 | -0.080 | 0.048 | 5 |
| gpt4o | T6 | -0.028 | 0.068 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.283 | 0.055 | 0.704 | 0.158 | gpt4o | -0.104 | -0.274 | -0.005 | 0.927 | -0.042 | 0.927 |
| deepseek_v4 | 5 | 290 | 0.482 | 0.322 | 0.797 | 0.216 | gpt4o | 0.105 | -0.009 | 0.217 | 0.081 | 0.050 | 0.242 |
| gpt4o | 5 | 290 | 0.483 | 0.283 | 0.904 | 0.317 | deepseek_v4 | -0.033 | -0.169 | 0.103 | 0.244 | -0.063 | 0.489 |

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

- P1 mean deltaRhoPartial -0.014 vs run-reassignment null mean -0.046 sd 0.014, p 0.012 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.333
- P2 slope 1.441, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.027 [-0.013, 0.070] p 0.061 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.067 [0.011, 0.125] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.011 | 0.008 | 0.023 |
| agree_own | deepseek_v4 | O | 10 | 0.004 | 0.003 | 0.008 |
| agree_own | gpt4o | O | 10 | 0.008 | 0.005 | 0.016 |
| agree_own | all | all | 30 | 0.008 | 0.006 | 0.019 |
| jsd_own | claude46 | O | 10 | 0.005 | 0.003 | 0.010 |
| jsd_own | deepseek_v4 | O | 10 | 0.005 | 0.004 | 0.010 |
| jsd_own | gpt4o | O | 10 | 0.004 | 0.003 | 0.008 |
| jsd_own | all | all | 30 | 0.005 | 0.003 | 0.010 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.004 | 0.003 | 0.008 |
| flip_rate | deepseek_v4 | O | 10 | 0.007 | 0.004 | 0.014 |
| flip_rate | gpt4o | O | 10 | 0.008 | 0.005 | 0.016 |
| flip_rate | random | R | 3 | 0.025 | 0.013 | 0.036 |
| flip_rate | all | all | 33 | 0.008 | 0.008 | 0.021 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.001 | 6.3e-04 | 0.002 |
| mean_jsd | deepseek_v4 | O | 10 | 0.008 | 0.004 | 0.014 |
| mean_jsd | gpt4o | O | 10 | 0.004 | 0.003 | 0.009 |
| mean_jsd | random | R | 3 | 2.3e-06 | 1.0e-06 | 3.3e-06 |
| mean_jsd | all | all | 33 | 0.004 | 0.004 | 0.011 |
| delta_rho | claude46 | O | 10 | 0.024 | 0.013 | 0.044 |
| delta_rho | deepseek_v4 | O | 10 | 0.038 | 0.024 | 0.072 |
| delta_rho | gpt4o | O | 10 | 0.035 | 0.023 | 0.070 |
| delta_rho | all | all | 30 | 0.032 | 0.020 | 0.072 |
| delta_rho_partial | claude46 | O | 10 | 0.024 | 0.018 | 0.051 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.044 | 0.028 | 0.084 |
| delta_rho_partial | gpt4o | O | 10 | 0.041 | 0.026 | 0.082 |
| delta_rho_partial | all | all | 30 | 0.036 | 0.025 | 0.084 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.