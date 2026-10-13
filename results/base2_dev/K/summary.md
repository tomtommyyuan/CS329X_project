# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.998, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.696 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.117 [-0.279, 0.012] p_perm 0.940 (null mean -0.036) p_holm 1.000; deepseek_v4 0.134 [-0.011, 0.249] p_perm 0.098 (null mean 0.073) p_holm 0.295; gpt4o -0.142 [-0.282, -0.001] p_perm 0.940 (null mean -0.067) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.001 [-0.049, 0.050], p 0.774; D_specific 0.020 [-0.030, 0.071], D_shared -0.019 (139 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = smollm3-3b.base_B_s0) | -0.030 | teacher-level exact p 0.500 (rank 3 of 6 relabellings, floor 0.167); the run-level null (mean -0.040, sd 0.012, p 0.232, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 0.966 (pearson 0.748, seed-noise sd 0.029, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 8.8e-04 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.102 [-0.273, 0.025] p_holm 1.000; deepseek_v4 0.107 [-0.042, 0.221] p_holm 0.210; gpt4o -0.105 [-0.229, 0.029] p_holm 1.000 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.038 [-0.031, 0.095], p 0.050 (138 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.003 [-0.047, 0.050], p 0.882 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.020 [-0.026, 0.066] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.328 [0.239, 0.413], margin over the next 0.185 [0.051, 0.307] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.033 | 0.744 | 0.044 | 0.150 | deepseek_v4 | -0.117 | -0.279 | 0.012 | 0.940 | -0.036 | 0.052 | 1.000 | False |
| deepseek_v4 | 5 | 139 | 0.350 | 0.825 | 0.425 | 0.217 | gpt4o | 0.134 | -0.011 | 0.249 | 0.098 | 0.073 | 0.048 | 0.295 | False |
| gpt4o | 5 | 139 | 0.142 | 0.898 | 0.158 | 0.284 | deepseek_v4 | -0.142 | -0.282 | -0.001 | 0.940 | -0.067 | 0.048 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.034 | -0.047 | 0.014 | 0.180 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = smollm3-3b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.001 | -0.049 | 0.050 | 0.774 | 0.015 | 0.018 | 0.003 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.019 | 0.020 | -0.030 | 0.071 | 0.482 | 0.019 | 0.021 | 0.020 | -0.026 | 0.066 |

Row scales (sd of each pooled student's residual given r_0): smollm3-3b-e2ck.claude46_O_pooled 0.061, smollm3-3b-e2ck.deepseek_v4_O_pooled 0.104, smollm3-3b-e2ck.gpt4o_O_pooled 0.085.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | 0.022 | 0.124 | 0.106 | 0.744 | -0.093 | 0.036 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | 0.149 | 0.297 | 0.190 | 0.825 | 0.128 | 0.039 |
| smollm3-3b-e2ck.gpt4o_O_pooled | 0.064 | 0.212 | 0.107 | 0.898 | -0.031 | -0.015 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | -0.099 | -0.184 | -0.087 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | 0.077 | 0.116 | 0.077 |
| smollm3-3b-e2ck.gpt4o_O_pooled | -0.023 | -0.010 | -0.032 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | 0.033 | 0.150 | 0.119 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | 0.169 | 0.350 | 0.217 |
| smollm3-3b-e2ck.gpt4o_O_pooled | 0.091 | 0.284 | 0.142 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_pooled | -0.025 | -0.033 | -0.048 |
| smollm3-3b-e2ck.deepseek_v4_O_pooled | -0.073 | 0.055 | -0.004 |
| smollm3-3b-e2ck.gpt4o_O_pooled | -0.066 | 0.067 | 0.006 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.016 | 0.002 | 0.033 |
| students:deepseek_v4 | 5 | 139 | 0.122 | 0.090 | 0.157 |
| students:gpt4o | 5 | 139 | 0.084 | 0.058 | 0.112 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.082 | 0.074 | 0.091 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.106 | -0.137 | -0.077 |
| students:claude46 | students:gpt4o | -0.067 | -0.089 | -0.047 |
| students:claude46 | teacher:claude46 | -0.042 | -0.084 | -0.003 |
| students:claude46 | base_prior | -0.066 | -0.082 | -0.048 |
| students:deepseek_v4 | students:gpt4o | 0.038 | 0.017 | 0.060 |
| students:deepseek_v4 | teacher:deepseek_v4 | -0.027 | -0.063 | 0.008 |
| students:deepseek_v4 | base_prior | 0.040 | 0.005 | 0.076 |
| students:gpt4o | teacher:gpt4o | 0.009 | -0.026 | 0.042 |
| students:gpt4o | base_prior | 0.001 | -0.025 | 0.030 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | base_prior | 0.053 | -0.030 | 0.082 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.016 | 0.016 | 5 |
| deepseek_v4 | 0.149 | 0.122 | 0.039 | 5 |
| gpt4o | 0.075 | 0.084 | 0.028 | 5 |

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
| smollm3-3b-e2ck.claude46_O_s1 | 1.000 | 0.060 | 150 | 0.828 | 0.843 | 0.145 | 0.032 | 0.017 |
| smollm3-3b-e2ck.claude46_O_s2 | 1.000 | 0.064 | 150 | 0.853 | 0.854 | 0.136 | 0.047 | 0.026 |
| smollm3-3b-e2ck.claude46_O_s3 | 1.000 | 0.056 | 150 | 0.815 | 0.829 | 0.164 | 0.039 | 0.021 |
| smollm3-3b-e2ck.claude46_O_s4 | 1.000 | 0.061 | 150 | 0.812 | 0.838 | 0.161 | 0.036 | 0.024 |
| smollm3-3b-e2ck.claude46_O_s5 | 1.000 | 0.059 | 150 | 0.847 | 0.848 | 0.144 | 0.028 | 0.023 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 1.000 | 0.067 | 150 | 0.827 | 0.848 | 0.108 | 0.097 | 0.062 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 1.000 | 0.059 | 150 | 0.825 | 0.857 | 0.116 | 0.051 | 0.027 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 1.000 | 0.069 | 150 | 0.820 | 0.848 | 0.111 | 0.083 | 0.046 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 1.000 | 0.052 | 150 | 0.795 | 0.821 | 0.122 | 0.084 | 0.046 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 1.000 | 0.065 | 150 | 0.825 | 0.855 | 0.108 | 0.089 | 0.047 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 1.000 | 0.059 | 150 | 0.845 | 0.835 | 0.116 | 0.038 | 0.025 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 1.000 | 0.060 | 150 | 0.841 | 0.835 | 0.116 | 0.068 | 0.040 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 1.000 | 0.081 | 150 | 0.833 | 0.840 | 0.123 | 0.074 | 0.036 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 1.000 | 0.078 | 150 | 0.850 | 0.837 | 0.115 | 0.063 | 0.037 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 1.000 | 0.056 | 150 | 0.848 | 0.854 | 0.111 | 0.047 | 0.023 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 0.828 | 0.817 | 0.843 | 0.145 | 0.120 | 0.119 |
| smollm3-3b-e2ck.claude46_O_s2 | 0.853 | 0.839 | 0.854 | 0.136 | 0.110 | 0.111 |
| smollm3-3b-e2ck.claude46_O_s3 | 0.815 | 0.813 | 0.829 | 0.164 | 0.127 | 0.133 |
| smollm3-3b-e2ck.claude46_O_s4 | 0.812 | 0.813 | 0.838 | 0.161 | 0.122 | 0.132 |
| smollm3-3b-e2ck.claude46_O_s5 | 0.847 | 0.820 | 0.848 | 0.144 | 0.123 | 0.125 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 0.838 | 0.827 | 0.848 | 0.140 | 0.108 | 0.120 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 0.844 | 0.825 | 0.857 | 0.144 | 0.116 | 0.113 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 0.835 | 0.820 | 0.848 | 0.139 | 0.111 | 0.114 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 0.812 | 0.795 | 0.821 | 0.157 | 0.122 | 0.137 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 0.844 | 0.825 | 0.855 | 0.138 | 0.108 | 0.114 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 0.835 | 0.815 | 0.845 | 0.140 | 0.117 | 0.116 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 0.835 | 0.820 | 0.841 | 0.144 | 0.112 | 0.116 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 0.840 | 0.813 | 0.833 | 0.137 | 0.104 | 0.123 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 0.837 | 0.824 | 0.850 | 0.137 | 0.102 | 0.115 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 0.854 | 0.822 | 0.848 | 0.124 | 0.109 | 0.111 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| claude46 | O | 5 | 1.000 | 0.831 | 0.843 | 0.150 | 0.036 | 0.022 |
| deepseek_v4 | O | 5 | 1.000 | 0.818 | 0.846 | 0.113 | 0.081 | 0.046 |
| gpt4o | O | 5 | 1.000 | 0.844 | 0.840 | 0.116 | 0.058 | 0.032 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = smollm3-3b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 139.000 | 0.110 | -0.003 | 0.744 | 0.074 | gpt4o | -0.076 | 0.841 | -0.021 | -0.277 | 0.072 | -0.003 | 0.030 | 0.074 |
| smollm3-3b-e2ck.claude46_O_s2 | 139.000 | 0.102 | 0.079 | 0.744 | 0.134 | deepseek_v4 | -0.055 | 0.706 | -0.028 | -0.207 | 0.108 | 0.079 | 0.134 | 0.053 |
| smollm3-3b-e2ck.claude46_O_s3 | 139.000 | 0.052 | 0.037 | 0.744 | 0.099 | gpt4o | -0.062 | 0.818 | -0.015 | -0.257 | 0.070 | 0.037 | 0.094 | 0.099 |
| smollm3-3b-e2ck.claude46_O_s4 | 139.000 | -4.6e-04 | -0.043 | 0.744 | 0.108 | deepseek_v4 | -0.151 | 0.992 | -0.019 | -0.265 | -0.073 | -0.043 | 0.108 | 0.074 |
| smollm3-3b-e2ck.claude46_O_s5 | 139.000 | 0.155 | 0.011 | 0.744 | 0.117 | gpt4o | -0.107 | 0.867 | -0.040 | -0.283 | 0.041 | 0.011 | 0.092 | 0.117 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 139.000 | 0.274 | 0.321 | 0.825 | 0.190 | gpt4o | 0.131 | 0.030 | 0.037 | -0.020 | 0.236 | 0.162 | 0.321 | 0.190 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 139.000 | 0.127 | 0.234 | 0.825 | 0.155 | claude46 | 0.079 | 0.114 | 0.017 | -0.082 | 0.189 | 0.155 | 0.234 | 0.142 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 139.000 | 0.204 | 0.221 | 0.825 | 0.172 | gpt4o | 0.049 | 0.294 | 0.021 | -0.108 | 0.179 | 0.122 | 0.221 | 0.172 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 139.000 | 0.241 | 0.251 | 0.825 | 0.167 | gpt4o | 0.084 | 0.141 | 0.030 | -0.067 | 0.206 | 0.111 | 0.251 | 0.167 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 139.000 | 0.167 | 0.257 | 0.825 | 0.153 | gpt4o | 0.104 | 0.040 | 0.016 | -0.042 | 0.212 | 0.101 | 0.257 | 0.153 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 139.000 | 0.143 | 0.061 | 0.898 | 0.161 | deepseek_v4 | -0.100 | 0.940 | -0.025 | -0.214 | 0.024 | 0.015 | 0.161 | 0.061 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 139.000 | 0.304 | 0.170 | 0.898 | 0.220 | deepseek_v4 | -0.050 | 0.574 | -0.040 | -0.184 | 0.077 | 0.112 | 0.220 | 0.170 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 139.000 | 0.266 | 0.049 | 0.898 | 0.193 | deepseek_v4 | -0.143 | 0.980 | -0.037 | -0.282 | 0.003 | 0.059 | 0.193 | 0.049 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 139.000 | 0.246 | 0.082 | 0.898 | 0.191 | deepseek_v4 | -0.108 | 0.939 | -0.033 | -0.246 | 0.039 | 0.052 | 0.191 | 0.082 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 139.000 | 0.229 | 0.094 | 0.898 | 0.142 | deepseek_v4 | -0.048 | 0.664 | -0.027 | -0.195 | 0.099 | 0.022 | 0.142 | 0.094 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.090 | 0.040 | 5 |
| deepseek_v4 | 0.089 | 0.030 | 5 |
| gpt4o | -0.090 | 0.041 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.030 | 0.500 | 3 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2ck.claude46_O_s1 | 0.009 | 0.744 | 0.088 | gpt4o | -0.079 | 0.826 | -0.292 | 0.062 |
| smollm3-3b-e2ck.claude46_O_s2 | 0.089 | 0.744 | 0.159 | deepseek_v4 | -0.070 | 0.719 | -0.213 | 0.090 |
| smollm3-3b-e2ck.claude46_O_s3 | 0.042 | 0.744 | 0.106 | deepseek_v4 | -0.064 | 0.812 | -0.253 | 0.061 |
| smollm3-3b-e2ck.claude46_O_s4 | -0.043 | 0.744 | 0.102 | deepseek_v4 | -0.145 | 0.989 | -0.252 | -0.070 |
| smollm3-3b-e2ck.claude46_O_s5 | 0.027 | 0.744 | 0.137 | gpt4o | -0.110 | 0.833 | -0.288 | 0.021 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | 0.381 | 0.825 | 0.220 | gpt4o | 0.161 | 0.041 | 0.013 | 0.270 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | 0.261 | 0.825 | 0.167 | claude46 | 0.095 | 0.163 | -0.059 | 0.196 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | 0.271 | 0.825 | 0.196 | gpt4o | 0.075 | 0.358 | -0.077 | 0.205 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | 0.309 | 0.825 | 0.195 | gpt4o | 0.115 | 0.169 | -0.034 | 0.233 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | 0.294 | 0.825 | 0.173 | gpt4o | 0.121 | 0.059 | -0.021 | 0.228 |
| smollm3-3b-e2ck.gpt4o_O_s1 | 0.080 | 0.898 | 0.198 | deepseek_v4 | -0.117 | 0.938 | -0.226 | 0.004 |
| smollm3-3b-e2ck.gpt4o_O_s2 | 0.204 | 0.898 | 0.297 | deepseek_v4 | -0.093 | 0.675 | -0.220 | 0.037 |
| smollm3-3b-e2ck.gpt4o_O_s3 | 0.085 | 0.898 | 0.263 | deepseek_v4 | -0.177 | 0.985 | -0.337 | -0.020 |
| smollm3-3b-e2ck.gpt4o_O_s4 | 0.114 | 0.898 | 0.255 | deepseek_v4 | -0.141 | 0.954 | -0.298 | 0.013 |
| smollm3-3b-e2ck.gpt4o_O_s5 | 0.123 | 0.898 | 0.205 | deepseek_v4 | -0.082 | 0.767 | -0.251 | 0.077 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.023 | 0.066 | 5 |
| claude46 | T1 | -0.008 | 0.130 | 5 |
| claude46 | T3 | -0.133 | 0.114 | 5 |
| claude46 | T5 | -0.083 | 0.060 | 5 |
| claude46 | T6 | -0.180 | 0.102 | 5 |
| deepseek_v4 | T0 | 0.055 | 0.051 | 5 |
| deepseek_v4 | T1 | -0.122 | 0.139 | 5 |
| deepseek_v4 | T3 | 0.017 | 0.065 | 5 |
| deepseek_v4 | T5 | 0.100 | 0.104 | 5 |
| deepseek_v4 | T6 | 0.108 | 0.036 | 5 |
| gpt4o | T0 | -0.056 | 0.068 | 5 |
| gpt4o | T1 | -0.046 | 0.133 | 5 |
| gpt4o | T3 | -0.165 | 0.058 | 5 |
| gpt4o | T5 | -0.189 | 0.052 | 5 |
| gpt4o | T6 | -0.018 | 0.076 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.104 | 0.022 | 0.744 | 0.124 | deepseek_v4 | -0.102 | -0.273 | 0.025 | 0.927 | -0.026 | 1.000 |
| deepseek_v4 | 5 | 139 | 0.237 | 0.297 | 0.825 | 0.190 | gpt4o | 0.107 | -0.042 | 0.221 | 0.070 | 0.033 | 0.210 |
| gpt4o | 5 | 139 | 0.278 | 0.107 | 0.898 | 0.212 | deepseek_v4 | -0.105 | -0.229 | 0.029 | 0.920 | -0.036 | 1.000 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | ungated covariate profile | claude46 | 139 | 0.108 | 0.744 | 0.009 | 0.205 | 3 | -0.220 | -0.332 | -0.108 |
| smollm3-3b.base_B_s0 | ungated covariate profile | deepseek_v4 | 139 | 0.328 | 0.825 | 0.239 | 0.413 | 1 | 0.185 | 0.051 | 0.307 |
| smollm3-3b.base_B_s0 | ungated covariate profile | gpt4o | 139 | 0.143 | 0.898 | 0.001 | 0.263 | 2 | -0.185 | -0.336 | -0.051 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 0/5 seeds pass -> fail (old rule, not the verdict)
- deepseek_v4: 0/5 seeds pass -> fail (old rule, not the verdict)
- gpt4o: 3/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial -0.030 vs run-reassignment null mean -0.040 sd 0.012, p 0.232 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.500
- P2 slope 0.966, run-reassignment p 8.8e-04 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.001 [-0.049, 0.050] p 0.774 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.020 [-0.030, 0.071] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.023 | 0.013 | 0.039 |
| agree_own | deepseek_v4 | O | 10 | 0.014 | 0.014 | 0.031 |
| agree_own | gpt4o | O | 10 | 0.008 | 0.005 | 0.017 |
| agree_own | all | all | 30 | 0.015 | 0.013 | 0.037 |
| jsd_own | claude46 | O | 10 | 0.015 | 0.009 | 0.027 |
| jsd_own | deepseek_v4 | O | 10 | 0.008 | 0.005 | 0.014 |
| jsd_own | gpt4o | O | 10 | 0.005 | 0.004 | 0.011 |
| jsd_own | all | all | 30 | 0.009 | 0.007 | 0.023 |
| flip_rate | claude46 | O | 10 | 0.009 | 0.005 | 0.017 |
| flip_rate | deepseek_v4 | O | 10 | 0.019 | 0.016 | 0.042 |
| flip_rate | gpt4o | O | 10 | 0.019 | 0.011 | 0.034 |
| flip_rate | all | all | 30 | 0.016 | 0.012 | 0.037 |
| mean_jsd | claude46 | O | 10 | 0.004 | 0.002 | 0.008 |
| mean_jsd | deepseek_v4 | O | 10 | 0.014 | 0.011 | 0.028 |
| mean_jsd | gpt4o | O | 10 | 0.009 | 0.006 | 0.016 |
| mean_jsd | all | all | 30 | 0.009 | 0.008 | 0.020 |
| delta_rho | claude46 | O | 10 | 0.040 | 0.027 | 0.078 |
| delta_rho | deepseek_v4 | O | 10 | 0.040 | 0.024 | 0.077 |
| delta_rho | gpt4o | O | 10 | 0.048 | 0.027 | 0.090 |
| delta_rho | all | all | 30 | 0.042 | 0.025 | 0.085 |
| delta_rho_partial | claude46 | O | 10 | 0.048 | 0.031 | 0.093 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.038 | 0.022 | 0.070 |
| delta_rho_partial | gpt4o | O | 10 | 0.050 | 0.031 | 0.095 |
| delta_rho_partial | all | all | 30 | 0.045 | 0.028 | 0.095 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.