# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.998, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.713 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.120 [-0.238, -0.034] p_perm 0.928 (null mean -0.061) p_holm 1.000; deepseek_v4 0.139 [0.018, 0.251] p_perm 0.034 (null mean 0.073) p_holm 0.102; gpt4o -0.097 [-0.209, 0.026] p_perm 0.889 (null mean -0.050) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.032 [-0.008, 0.071], p 0.032; D_specific 0.045 [0.002, 0.086], D_shared -0.013 (290 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 290 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.008 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.039, sd 0.012, p 0.001, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.420 (pearson 0.942, seed-noise sd 0.016, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.060 [-0.199, 0.022] p_holm 1.000; deepseek_v4 0.121 [-0.020, 0.229] p_holm 0.052; gpt4o -0.075 [-0.198, 0.062] p_holm 1.000 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.027 [-0.046, 0.092], p 0.122 (288 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.037 [-6.2e-04, 0.072], p 0.063 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.045 [0.004, 0.085] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.380 [0.327, 0.434], margin over the next 0.100 [0.036, 0.167] (290 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.111 | 0.704 | 0.157 | 0.230 | deepseek_v4 | -0.120 | -0.238 | -0.034 | 0.928 | -0.061 | 0.040 | 1.000 | False |
| deepseek_v4 | 5 | 290 | 0.433 | 0.797 | 0.543 | 0.294 | gpt4o | 0.139 | 0.018 | 0.251 | 0.034 | 0.073 | 0.037 | 0.102 | False |
| gpt4o | 5 | 290 | 0.230 | 0.904 | 0.255 | 0.327 | deepseek_v4 | -0.097 | -0.209 | 0.026 | 0.889 | -0.050 | 0.039 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.022 | -0.058 | 0.012 | 3.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.032 | -0.008 | 0.071 | 0.032 | 0.006 | 0.014 | 0.037 | 290 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.013 | 0.045 | 0.002 | 0.086 | 0.006 | 0.008 | 0.015 | 0.045 | 0.004 | 0.085 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2ck.claude46_O_pooled 0.069, qwen3-4b-e2ck.deepseek_v4_O_pooled 0.101, qwen3-4b-e2ck.gpt4o_O_pooled 0.077.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | 0.082 | 0.142 | 0.118 | 0.704 | -0.048 | 0.063 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.146 | 0.317 | 0.196 | 0.797 | 0.146 | 0.060 |
| qwen3-4b-e2ck.gpt4o_O_pooled | 0.070 | 0.218 | 0.143 | 0.904 | -0.001 | 0.013 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | -0.042 | -0.141 | -0.070 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.061 | 0.124 | 0.068 |
| qwen3-4b-e2ck.gpt4o_O_pooled | -0.042 | -0.036 | -0.026 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | 0.111 | 0.230 | 0.186 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | 0.182 | 0.433 | 0.294 |
| qwen3-4b-e2ck.gpt4o_O_pooled | 0.108 | 0.327 | 0.230 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_pooled | -0.081 | 0.203 | 0.041 |
| qwen3-4b-e2ck.deepseek_v4_O_pooled | -0.082 | 0.234 | -0.027 |
| qwen3-4b-e2ck.gpt4o_O_pooled | -0.047 | 0.143 | 0.042 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 290 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 290 | 0.041 | 0.028 | 0.056 |
| students:deepseek_v4 | 5 | 290 | 0.141 | 0.115 | 0.168 |
| students:gpt4o | 5 | 290 | 0.076 | 0.057 | 0.096 |
| teacher:claude46 | 1 | 290 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 290 | 0.113 | 0.096 | 0.131 |
| teacher:gpt4o | 1 | 290 | 0.063 | 0.045 | 0.084 |
| base_prior | 1 | 290 | 0.146 | 0.133 | 0.159 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.100 | -0.120 | -0.081 |
| students:claude46 | students:gpt4o | -0.035 | -0.049 | -0.021 |
| students:claude46 | teacher:claude46 | -0.003 | -0.028 | 0.021 |
| students:claude46 | base_prior | -0.105 | -0.121 | -0.088 |
| students:deepseek_v4 | students:gpt4o | 0.065 | 0.048 | 0.083 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.028 | 0.001 | 0.055 |
| students:deepseek_v4 | base_prior | -0.005 | -0.029 | 0.021 |
| students:gpt4o | teacher:gpt4o | 0.013 | -0.012 | 0.038 |
| students:gpt4o | base_prior | -0.070 | -0.090 | -0.050 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.057 | -0.120 | 0.178 | 8 |
| qwen3-4b.base_B_s0 | base_prior | 0.068 | -0.078 | 0.146 | 290 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.041 | 0.012 | 5 |
| deepseek_v4 | 0.113 | 0.141 | 0.024 | 5 |
| gpt4o | 0.063 | 0.076 | 0.008 | 5 |

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
| qwen3-4b.base_B_s0 | 0.213 | 0.097 | 8 | nan | 0.830 | nan | 0.188 | 0.028 |
| qwen3-4b-e2ck.claude46_O_s1 | 0.999 | 0.048 | 299 | 0.861 | 0.867 | 0.127 | 0.047 | 0.021 |
| qwen3-4b-e2ck.claude46_O_s2 | 1.000 | 0.058 | 300 | 0.855 | 0.858 | 0.131 | 0.045 | 0.018 |
| qwen3-4b-e2ck.claude46_O_s3 | 1.000 | 0.056 | 300 | 0.860 | 0.855 | 0.127 | 0.047 | 0.023 |
| qwen3-4b-e2ck.claude46_O_s4 | 1.000 | 0.055 | 299 | 0.859 | 0.859 | 0.128 | 0.053 | 0.025 |
| qwen3-4b-e2ck.claude46_O_s5 | 1.000 | 0.062 | 300 | 0.859 | 0.848 | 0.123 | 0.054 | 0.024 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 1.000 | 0.059 | 300 | 0.839 | 0.838 | 0.101 | 0.094 | 0.058 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 1.000 | 0.062 | 300 | 0.849 | 0.849 | 0.095 | 0.091 | 0.050 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 1.000 | 0.078 | 300 | 0.849 | 0.853 | 0.093 | 0.090 | 0.062 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 1.000 | 0.066 | 300 | 0.858 | 0.849 | 0.090 | 0.081 | 0.039 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 1.000 | 0.064 | 300 | 0.851 | 0.852 | 0.093 | 0.074 | 0.043 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 1.000 | 0.072 | 300 | 0.845 | 0.850 | 0.119 | 0.051 | 0.026 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 1.000 | 0.073 | 300 | 0.839 | 0.838 | 0.122 | 0.061 | 0.028 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 1.000 | 0.071 | 300 | 0.834 | 0.838 | 0.126 | 0.052 | 0.024 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 1.000 | 0.062 | 300 | 0.855 | 0.856 | 0.113 | 0.052 | 0.028 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 1.000 | 0.065 | 300 | 0.834 | 0.837 | 0.122 | 0.054 | 0.024 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.776 | 0.830 | 0.782 | 0.185 | 0.098 | 0.163 |
| qwen3-4b-e2ck.claude46_O_s1 | 0.861 | 0.867 | 0.848 | 0.127 | 0.098 | 0.118 |
| qwen3-4b-e2ck.claude46_O_s2 | 0.855 | 0.858 | 0.841 | 0.131 | 0.097 | 0.123 |
| qwen3-4b-e2ck.claude46_O_s3 | 0.860 | 0.855 | 0.842 | 0.127 | 0.100 | 0.123 |
| qwen3-4b-e2ck.claude46_O_s4 | 0.859 | 0.859 | 0.844 | 0.128 | 0.095 | 0.118 |
| qwen3-4b-e2ck.claude46_O_s5 | 0.859 | 0.848 | 0.840 | 0.123 | 0.097 | 0.118 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 0.838 | 0.839 | 0.829 | 0.143 | 0.101 | 0.128 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 0.849 | 0.849 | 0.843 | 0.132 | 0.095 | 0.119 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 0.853 | 0.849 | 0.846 | 0.132 | 0.093 | 0.120 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 0.846 | 0.858 | 0.849 | 0.131 | 0.090 | 0.115 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 0.852 | 0.851 | 0.847 | 0.130 | 0.093 | 0.112 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 0.848 | 0.850 | 0.845 | 0.134 | 0.097 | 0.119 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 0.831 | 0.838 | 0.839 | 0.142 | 0.100 | 0.122 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 0.829 | 0.838 | 0.834 | 0.141 | 0.102 | 0.126 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 0.856 | 0.851 | 0.855 | 0.130 | 0.097 | 0.113 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 0.835 | 0.837 | 0.834 | 0.143 | 0.099 | 0.122 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.213 | nan | 0.830 | nan | 0.188 | 0.028 |
| claude46 | O | 5 | 1.000 | 0.859 | 0.857 | 0.127 | 0.049 | 0.022 |
| deepseek_v4 | O | 5 | 1.000 | 0.849 | 0.848 | 0.094 | 0.086 | 0.050 |
| gpt4o | O | 5 | 1.000 | 0.841 | 0.844 | 0.120 | 0.054 | 0.026 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_s1 | 290.000 | 0.156 | 0.061 | 0.704 | 0.124 | deepseek_v4 | -0.063 | 0.821 | -0.025 | -0.170 | 0.022 | 0.061 | 0.124 | 0.040 |
| qwen3-4b-e2ck.claude46_O_s2 | 290.000 | 0.242 | 0.059 | 0.704 | 0.131 | deepseek_v4 | -0.072 | 0.848 | -0.031 | -0.206 | 0.024 | 0.059 | 0.131 | 0.105 |
| qwen3-4b-e2ck.claude46_O_s3 | 290.000 | 0.237 | 0.051 | 0.704 | 0.121 | gpt4o | -0.070 | 0.804 | -0.034 | -0.232 | 0.043 | 0.051 | 0.072 | 0.121 |
| qwen3-4b-e2ck.claude46_O_s4 | 290.000 | 0.259 | 0.108 | 0.704 | 0.160 | deepseek_v4 | -0.052 | 0.685 | -0.033 | -0.171 | 0.048 | 0.108 | 0.160 | 0.108 |
| qwen3-4b-e2ck.claude46_O_s5 | 290.000 | 0.263 | 0.059 | 0.704 | 0.120 | gpt4o | -0.060 | 0.726 | -0.036 | -0.214 | 0.024 | 0.059 | 0.102 | 0.120 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 290.000 | 0.410 | 0.280 | 0.797 | 0.189 | gpt4o | 0.091 | 0.077 | 0.036 | -0.047 | 0.200 | 0.132 | 0.280 | 0.189 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 290.000 | 0.402 | 0.257 | 0.797 | 0.115 | claude46 | 0.142 | 0.002 | 0.031 | -6.5e-04 | 0.229 | 0.115 | 0.257 | 0.115 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 290.000 | 0.423 | 0.260 | 0.797 | 0.168 | gpt4o | 0.092 | 0.094 | 0.041 | -0.036 | 0.183 | 0.143 | 0.260 | 0.168 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 290.000 | 0.391 | 0.302 | 0.797 | 0.188 | gpt4o | 0.114 | 0.007 | 0.024 | -0.037 | 0.231 | 0.119 | 0.302 | 0.188 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 290.000 | 0.375 | 0.286 | 0.797 | 0.197 | gpt4o | 0.090 | 0.071 | 0.033 | -0.041 | 0.206 | 0.123 | 0.286 | 0.197 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 290.000 | 0.311 | 0.100 | 0.904 | 0.208 | deepseek_v4 | -0.108 | 0.967 | -0.035 | -0.214 | 0.002 | 0.116 | 0.208 | 0.100 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 290.000 | 0.348 | 0.105 | 0.904 | 0.169 | deepseek_v4 | -0.064 | 0.730 | -0.039 | -0.188 | 0.073 | 0.027 | 0.169 | 0.105 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 290.000 | 0.300 | 0.122 | 0.904 | 0.185 | deepseek_v4 | -0.063 | 0.762 | -0.034 | -0.216 | 0.084 | 0.066 | 0.185 | 0.122 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 290.000 | 0.341 | 0.172 | 0.904 | 0.200 | deepseek_v4 | -0.028 | 0.404 | -0.038 | -0.161 | 0.114 | 0.059 | 0.200 | 0.172 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 290.000 | 0.313 | 0.115 | 0.904 | 0.178 | deepseek_v4 | -0.063 | 0.803 | -0.030 | -0.175 | 0.061 | 0.036 | 0.178 | 0.115 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.063 | 0.008 | 5 |
| deepseek_v4 | 0.106 | 0.023 | 5 |
| gpt4o | -0.065 | 0.028 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.008 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2ck.claude46_O_s1 | 0.078 | 0.704 | 0.172 | deepseek_v4 | -0.094 | 0.920 | -0.196 | -0.009 |
| qwen3-4b-e2ck.claude46_O_s2 | 0.085 | 0.704 | 0.210 | deepseek_v4 | -0.124 | 0.961 | -0.246 | -0.026 |
| qwen3-4b-e2ck.claude46_O_s3 | 0.077 | 0.704 | 0.179 | gpt4o | -0.102 | 0.866 | -0.255 | -0.005 |
| qwen3-4b-e2ck.claude46_O_s4 | 0.134 | 0.704 | 0.242 | deepseek_v4 | -0.108 | 0.888 | -0.218 | -0.008 |
| qwen3-4b-e2ck.claude46_O_s5 | 0.088 | 0.704 | 0.191 | deepseek_v4 | -0.103 | 0.839 | -0.242 | -0.034 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | 0.392 | 0.797 | 0.281 | gpt4o | 0.111 | 0.113 | -0.011 | 0.224 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | 0.370 | 0.797 | 0.213 | gpt4o | 0.157 | 0.004 | 0.032 | 0.263 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | 0.378 | 0.797 | 0.264 | gpt4o | 0.114 | 0.128 | 0.003 | 0.217 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | 0.406 | 0.797 | 0.276 | gpt4o | 0.130 | 0.011 | -0.003 | 0.247 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | 0.388 | 0.797 | 0.280 | gpt4o | 0.108 | 0.103 | -0.008 | 0.220 |
| qwen3-4b-e2ck.gpt4o_O_s1 | 0.178 | 0.904 | 0.301 | deepseek_v4 | -0.123 | 0.980 | -0.218 | -0.018 |
| qwen3-4b-e2ck.gpt4o_O_s2 | 0.192 | 0.904 | 0.279 | deepseek_v4 | -0.087 | 0.835 | -0.201 | 0.038 |
| qwen3-4b-e2ck.gpt4o_O_s3 | 0.196 | 0.904 | 0.277 | deepseek_v4 | -0.081 | 0.846 | -0.219 | 0.053 |
| qwen3-4b-e2ck.gpt4o_O_s4 | 0.251 | 0.904 | 0.304 | deepseek_v4 | -0.053 | 0.549 | -0.175 | 0.078 |
| qwen3-4b-e2ck.gpt4o_O_s5 | 0.192 | 0.904 | 0.275 | deepseek_v4 | -0.083 | 0.889 | -0.187 | 0.030 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.251 | 0.043 | 5 |
| claude46 | T1 | -0.144 | 0.064 | 5 |
| claude46 | T3 | -0.080 | 0.025 | 5 |
| claude46 | T5 | -0.073 | 0.038 | 5 |
| claude46 | T6 | -0.020 | 0.020 | 5 |
| deepseek_v4 | T0 | 0.227 | 0.051 | 5 |
| deepseek_v4 | T1 | 0.169 | 0.056 | 5 |
| deepseek_v4 | T3 | -0.005 | 0.058 | 5 |
| deepseek_v4 | T5 | 0.107 | 0.030 | 5 |
| deepseek_v4 | T6 | 0.100 | 0.032 | 5 |
| gpt4o | T0 | -0.086 | 0.072 | 5 |
| gpt4o | T1 | -0.166 | 0.067 | 5 |
| gpt4o | T3 | 0.026 | 0.081 | 5 |
| gpt4o | T5 | -0.083 | 0.057 | 5 |
| gpt4o | T6 | -0.092 | 0.029 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.275 | 0.082 | 0.704 | 0.142 | deepseek_v4 | -0.060 | -0.199 | 0.022 | 0.735 | -0.034 | 1.000 |
| deepseek_v4 | 5 | 290 | 0.450 | 0.317 | 0.797 | 0.196 | gpt4o | 0.121 | -0.020 | 0.229 | 0.017 | 0.041 | 0.052 |
| gpt4o | 5 | 290 | 0.368 | 0.143 | 0.904 | 0.218 | deepseek_v4 | -0.075 | -0.198 | 0.062 | 0.822 | -0.038 | 1.000 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | ungated covariate profile | claude46 | 290 | 0.118 | 0.704 | 0.035 | 0.198 | 3 | -0.262 | -0.357 | -0.172 |
| qwen3-4b.base_B_s0 | ungated covariate profile | deepseek_v4 | 290 | 0.380 | 0.797 | 0.327 | 0.434 | 1 | 0.100 | 0.036 | 0.167 |
| qwen3-4b.base_B_s0 | ungated covariate profile | gpt4o | 290 | 0.280 | 0.904 | 0.213 | 0.344 | 2 | -0.100 | -0.167 | -0.036 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 2/5 seeds pass -> partial (old rule, not the verdict)
- deepseek_v4: 3/5 seeds pass -> partial (old rule, not the verdict)
- gpt4o: 1/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial -0.008 vs run-reassignment null mean -0.039 sd 0.012, p 0.001 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 1.420, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.032 [-0.008, 0.071] p 0.032 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.045 [0.002, 0.086] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.003 | 0.002 | 0.005 |
| agree_own | deepseek_v4 | O | 10 | 0.008 | 0.006 | 0.015 |
| agree_own | gpt4o | O | 10 | 0.011 | 0.007 | 0.021 |
| agree_own | all | all | 30 | 0.007 | 0.006 | 0.020 |
| jsd_own | claude46 | O | 10 | 0.003 | 0.002 | 0.006 |
| jsd_own | deepseek_v4 | O | 10 | 0.005 | 0.004 | 0.010 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.004 | 0.011 |
| jsd_own | all | all | 30 | 0.005 | 0.003 | 0.010 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.005 | 0.003 | 0.009 |
| flip_rate | deepseek_v4 | O | 10 | 0.010 | 0.006 | 0.018 |
| flip_rate | gpt4o | O | 10 | 0.004 | 0.004 | 0.010 |
| flip_rate | all | all | 30 | 0.006 | 0.005 | 0.016 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.003 | 0.002 | 0.006 |
| mean_jsd | deepseek_v4 | O | 10 | 0.012 | 0.007 | 0.021 |
| mean_jsd | gpt4o | O | 10 | 0.002 | 0.001 | 0.004 |
| mean_jsd | all | all | 30 | 0.006 | 0.006 | 0.019 |
| delta_rho | claude46 | O | 10 | 0.013 | 0.009 | 0.027 |
| delta_rho | deepseek_v4 | O | 10 | 0.023 | 0.018 | 0.048 |
| delta_rho | gpt4o | O | 10 | 0.029 | 0.021 | 0.057 |
| delta_rho | all | all | 30 | 0.022 | 0.017 | 0.048 |
| delta_rho_partial | claude46 | O | 10 | 0.010 | 0.006 | 0.019 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.026 | 0.020 | 0.052 |
| delta_rho_partial | gpt4o | O | 10 | 0.032 | 0.025 | 0.064 |
| delta_rho_partial | all | all | 30 | 0.022 | 0.021 | 0.052 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.