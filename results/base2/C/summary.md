# E1 / E2 summary (test, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.964, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.936 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.051 [-0.153, 0.051] p_perm 0.257 (null mean -0.077) p_holm 0.515; deepseek_v4 0.232 [0.157, 0.304] p_perm 1.0e-04 (null mean 0.116) p_holm 3.0e-04; gpt4o -0.105 [-0.189, -0.029] p_perm 0.585 (null mean -0.098) p_holm 0.585; 1/3 pass | **PARTIAL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.102 [0.061, 0.144], p 1.0e-04; D_specific 0.159 [0.107, 0.214], D_shared -0.056 (289 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (test): claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 289 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = smollm3-3b.base_B_s0) | 0.039 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.065, sd 0.024, p 1.3e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 5.824 (pearson 0.945, seed-noise sd 0.019, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.020 [-0.124, 0.082] p_holm 0.344; deepseek_v4 0.232 [0.150, 0.306] p_holm 3.0e-04; gpt4o -0.089 [-0.179, -0.006] p_holm 0.584 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -4.1e-04 [-0.059, 0.058], p 0.504 (287 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.097 [0.057, 0.136], p 1.0e-04 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.130 [0.090, 0.169] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.250 [0.185, 0.314], margin over the next 0.076 [-3.7e-04, 0.152] (290 families) | control holds (no teacher preferred before training) |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.161 | 0.704 | 0.229 | 0.212 | deepseek_v4 | -0.051 | -0.153 | 0.051 | 0.257 | -0.077 | 0.040 | 0.515 | False |
| deepseek_v4 | 5 | 289 | 0.437 | 0.797 | 0.548 | 0.205 | gpt4o | 0.232 | 0.157 | 0.304 | 1.0e-04 | 0.116 | 0.031 | 3.0e-04 | True |
| gpt4o | 5 | 290 | 0.331 | 0.904 | 0.366 | 0.436 | deepseek_v4 | -0.105 | -0.189 | -0.029 | 0.585 | -0.098 | 0.034 | 0.585 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| 0.025 | -0.071 | 0.022 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = smollm3-3b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.102 | 0.061 | 0.144 | 1.0e-04 | 0.023 | 0.017 | 0.097 | 289 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.056 | 0.159 | 0.107 | 0.214 | 1.0e-04 | 0.048 | 0.020 | 0.130 | 0.090 | 0.169 |

Row scales (sd of each pooled student's residual given r_0): smollm3-3b-e2c.claude46_O_pooled 0.096, smollm3-3b-e2c.deepseek_v4_O_pooled 0.241, smollm3-3b-e2c.gpt4o_O_pooled 0.171.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | 0.137 | 0.157 | 0.094 | 0.704 | 0.012 | 0.273 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.093 | 0.376 | 0.145 | 0.797 | 0.258 | 0.125 |
| smollm3-3b-e2c.gpt4o_O_pooled | 0.122 | 0.380 | 0.289 | 0.904 | 0.038 | 0.078 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | -0.058 | -0.434 | -0.229 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.015 | 0.140 | 0.016 |
| smollm3-3b-e2c.gpt4o_O_pooled | 0.012 | 0.047 | 0.107 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | 0.161 | 0.212 | 0.135 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | 0.132 | 0.437 | 0.205 |
| smollm3-3b-e2c.gpt4o_O_pooled | 0.156 | 0.438 | 0.331 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| smollm3-3b-e2c.claude46_O_pooled | 0.072 | 0.367 | 0.023 |
| smollm3-3b-e2c.deepseek_v4_O_pooled | -0.036 | 0.152 | -0.052 |
| smollm3-3b-e2c.gpt4o_O_pooled | -0.078 | 0.151 | -0.037 |
| ceiling sqrt(2r/(1+r)) | 0.704 | 0.797 | 0.904 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 289 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 289 | 0.079 | 0.060 | 0.099 |
| students:deepseek_v4 | 5 | 289 | 0.508 | 0.462 | 0.553 |
| students:gpt4o | 5 | 289 | 0.316 | 0.278 | 0.354 |
| teacher:claude46 | 1 | 289 | 0.045 | 0.024 | 0.067 |
| teacher:deepseek_v4 | 1 | 289 | 0.112 | 0.095 | 0.130 |
| teacher:gpt4o | 1 | 289 | 0.063 | 0.045 | 0.083 |
| base_prior | 1 | 289 | 0.084 | 0.079 | 0.090 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.429 | -0.477 | -0.380 |
| students:claude46 | students:gpt4o | -0.237 | -0.274 | -0.199 |
| students:claude46 | teacher:claude46 | 0.034 | 0.007 | 0.061 |
| students:claude46 | base_prior | -0.006 | -0.024 | 0.015 |
| students:deepseek_v4 | students:gpt4o | 0.192 | 0.147 | 0.238 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.395 | 0.352 | 0.440 |
| students:deepseek_v4 | base_prior | 0.423 | 0.377 | 0.469 |
| students:gpt4o | teacher:gpt4o | 0.253 | 0.215 | 0.290 |
| students:gpt4o | base_prior | 0.231 | 0.193 | 0.270 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | base_prior | 0.055 | -0.030 | 0.084 | 289 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.045 | 0.079 | 0.015 | 5 |
| deepseek_v4 | 0.112 | 0.508 | 0.024 | 5 |
| gpt4o | 0.063 | 0.316 | 0.016 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.973 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s2 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.975 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s3 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.975 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s4 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.964 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.claude46_O_s5 | 4838 | 1.000 | 4838 | 4838 | 0 | 0 | 0.973 | True | data/sft_e2c/claude46_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.995 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.992 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.994 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.996 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 2497 | 1.000 | 2497 | 2497 | 0 | 0 | 0.994 | True | data/sft_e2c/deepseek_v4_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s1 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.991 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s2 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.989 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s3 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.988 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s4 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.988 | True | data/sft_e2c/gpt4o_O_s1.jsonl |
| smollm3-3b-e2c.gpt4o_O_s5 | 4964 | 1.000 | 4964 | 4964 | 0 | 0 | 0.992 | True | data/sft_e2c/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 782 | 419 | 5 | 3910 | 0.958 | 0.945 | 0.968 | True |
| claude46 | gpt4o | 1046 | 546 | 5 | 5230 | 0.948 | 0.936 | 0.959 | True |
| deepseek_v4 | claude46 | 782 | 419 | 5 | 3910 | 0.992 | 0.988 | 0.995 | True |
| deepseek_v4 | gpt4o | 574 | 334 | 5 | 2870 | 0.988 | 0.982 | 0.993 | True |
| gpt4o | claude46 | 1046 | 546 | 5 | 5230 | 0.987 | 0.981 | 0.991 | True |
| gpt4o | deepseek_v4 | 574 | 334 | 5 | 2870 | 0.985 | 0.977 | 0.991 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 1.000 | 0.087 | 300 | 0.847 | 0.816 | 0.124 | 0.093 | 0.035 |
| smollm3-3b-e2c.claude46_O_s2 | 1.000 | 0.097 | 300 | 0.849 | 0.817 | 0.123 | 0.108 | 0.040 |
| smollm3-3b-e2c.claude46_O_s3 | 1.000 | 0.083 | 300 | 0.869 | 0.837 | 0.120 | 0.068 | 0.036 |
| smollm3-3b-e2c.claude46_O_s4 | 1.000 | 0.090 | 300 | 0.855 | 0.833 | 0.122 | 0.084 | 0.039 |
| smollm3-3b-e2c.claude46_O_s5 | 1.000 | 0.088 | 300 | 0.875 | 0.838 | 0.113 | 0.079 | 0.035 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 1.000 | 0.107 | 299 | 0.761 | 0.729 | 0.164 | 0.300 | 0.222 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 1.000 | 0.095 | 300 | 0.757 | 0.727 | 0.151 | 0.291 | 0.207 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 1.000 | 0.100 | 300 | 0.753 | 0.734 | 0.155 | 0.303 | 0.217 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 1.000 | 0.082 | 300 | 0.758 | 0.731 | 0.160 | 0.291 | 0.214 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 1.000 | 0.084 | 300 | 0.770 | 0.745 | 0.146 | 0.274 | 0.192 |
| smollm3-3b-e2c.gpt4o_O_s1 | 1.000 | 0.092 | 300 | 0.825 | 0.817 | 0.137 | 0.194 | 0.114 |
| smollm3-3b-e2c.gpt4o_O_s2 | 1.000 | 0.088 | 300 | 0.818 | 0.804 | 0.138 | 0.182 | 0.115 |
| smollm3-3b-e2c.gpt4o_O_s3 | 1.000 | 0.102 | 300 | 0.809 | 0.807 | 0.142 | 0.193 | 0.104 |
| smollm3-3b-e2c.gpt4o_O_s4 | 1.000 | 0.099 | 300 | 0.819 | 0.814 | 0.142 | 0.150 | 0.093 |
| smollm3-3b-e2c.gpt4o_O_s5 | 1.000 | 0.093 | 300 | 0.813 | 0.807 | 0.139 | 0.184 | 0.111 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 0.847 | 0.816 | 0.816 | 0.124 | 0.110 | 0.137 |
| smollm3-3b-e2c.claude46_O_s2 | 0.849 | 0.807 | 0.817 | 0.123 | 0.106 | 0.134 |
| smollm3-3b-e2c.claude46_O_s3 | 0.869 | 0.829 | 0.837 | 0.120 | 0.107 | 0.132 |
| smollm3-3b-e2c.claude46_O_s4 | 0.855 | 0.833 | 0.825 | 0.122 | 0.099 | 0.132 |
| smollm3-3b-e2c.claude46_O_s5 | 0.875 | 0.838 | 0.835 | 0.113 | 0.098 | 0.128 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 0.719 | 0.761 | 0.729 | 0.249 | 0.164 | 0.225 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 0.723 | 0.757 | 0.727 | 0.235 | 0.151 | 0.221 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 0.719 | 0.753 | 0.734 | 0.243 | 0.155 | 0.220 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 0.727 | 0.758 | 0.731 | 0.244 | 0.160 | 0.224 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 0.734 | 0.770 | 0.745 | 0.232 | 0.146 | 0.208 |
| smollm3-3b-e2c.gpt4o_O_s1 | 0.805 | 0.817 | 0.825 | 0.171 | 0.113 | 0.137 |
| smollm3-3b-e2c.gpt4o_O_s2 | 0.804 | 0.803 | 0.818 | 0.168 | 0.113 | 0.138 |
| smollm3-3b-e2c.gpt4o_O_s3 | 0.795 | 0.807 | 0.809 | 0.173 | 0.110 | 0.142 |
| smollm3-3b-e2c.gpt4o_O_s4 | 0.801 | 0.814 | 0.819 | 0.173 | 0.112 | 0.142 |
| smollm3-3b-e2c.gpt4o_O_s5 | 0.799 | 0.807 | 0.813 | 0.172 | 0.111 | 0.139 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| claude46 | O | 5 | 1.000 | 0.859 | 0.828 | 0.120 | 0.086 | 0.037 |
| deepseek_v4 | O | 5 | 1.000 | 0.760 | 0.733 | 0.155 | 0.292 | 0.210 |
| gpt4o | O | 5 | 1.000 | 0.817 | 0.810 | 0.140 | 0.181 | 0.107 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = smollm3-3b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 290.000 | 0.250 | 0.103 | 0.704 | 0.152 | deepseek_v4 | -0.049 | 0.409 | -0.059 | -0.160 | 0.035 | 0.103 | 0.152 | 0.116 |
| smollm3-3b-e2c.claude46_O_s2 | 290.000 | 0.258 | 0.148 | 0.704 | 0.099 | deepseek_v4 | 0.048 | 0.009 | -0.046 | -0.071 | 0.156 | 0.148 | 0.099 | 0.054 |
| smollm3-3b-e2c.claude46_O_s3 | 290.000 | 0.194 | 0.105 | 0.704 | 0.113 | deepseek_v4 | -0.008 | 0.205 | -0.044 | -0.137 | 0.124 | 0.105 | 0.113 | 0.039 |
| smollm3-3b-e2c.claude46_O_s4 | 290.000 | 0.250 | 0.160 | 0.704 | 0.177 | deepseek_v4 | -0.016 | 0.137 | -0.061 | -0.109 | 0.073 | 0.160 | 0.177 | 0.134 |
| smollm3-3b-e2c.claude46_O_s5 | 290.000 | 0.222 | 0.093 | 0.704 | 0.160 | deepseek_v4 | -0.067 | 0.628 | -0.056 | -0.149 | 0.009 | 0.093 | 0.160 | 0.077 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 289.000 | 0.431 | 0.350 | 0.797 | 0.141 | gpt4o | 0.208 | 4.0e-04 | 0.098 | 0.128 | 0.285 | 0.083 | 0.350 | 0.141 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 290.000 | 0.453 | 0.375 | 0.797 | 0.127 | gpt4o | 0.247 | 1.0e-04 | 0.092 | 0.156 | 0.319 | 0.095 | 0.375 | 0.127 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 290.000 | 0.440 | 0.370 | 0.797 | 0.147 | gpt4o | 0.222 | 1.0e-04 | 0.098 | 0.145 | 0.296 | 0.096 | 0.370 | 0.147 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 290.000 | 0.425 | 0.336 | 0.797 | 0.129 | gpt4o | 0.206 | 3.0e-04 | 0.099 | 0.123 | 0.282 | 0.082 | 0.336 | 0.129 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 290.000 | 0.410 | 0.363 | 0.797 | 0.147 | gpt4o | 0.216 | 4.0e-04 | 0.094 | 0.136 | 0.291 | 0.089 | 0.363 | 0.147 |
| smollm3-3b-e2c.gpt4o_O_s1 | 290.000 | 0.408 | 0.295 | 0.904 | 0.333 | deepseek_v4 | -0.039 | 0.182 | -0.073 | -0.131 | 0.048 | 0.122 | 0.333 | 0.295 |
| smollm3-3b-e2c.gpt4o_O_s2 | 290.000 | 0.394 | 0.264 | 0.904 | 0.353 | deepseek_v4 | -0.088 | 0.630 | -0.076 | -0.174 | -0.008 | 0.123 | 0.353 | 0.264 |
| smollm3-3b-e2c.gpt4o_O_s3 | 290.000 | 0.399 | 0.254 | 0.904 | 0.361 | deepseek_v4 | -0.107 | 0.768 | -0.080 | -0.196 | -0.025 | 0.127 | 0.361 | 0.254 |
| smollm3-3b-e2c.gpt4o_O_s4 | 290.000 | 0.376 | 0.262 | 0.904 | 0.349 | deepseek_v4 | -0.087 | 0.622 | -0.076 | -0.188 | 0.010 | 0.090 | 0.349 | 0.262 |
| smollm3-3b-e2c.gpt4o_O_s5 | 290.000 | 0.401 | 0.292 | 0.904 | 0.393 | deepseek_v4 | -0.101 | 0.714 | -0.080 | -0.187 | -0.016 | 0.113 | 0.393 | 0.292 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.704 | 0.797 | 0.904 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.019 | 0.044 | 5 |
| deepseek_v4 | 0.220 | 0.016 | 5 |
| gpt4o | -0.084 | 0.027 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 0.039 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| smollm3-3b-e2c.claude46_O_s1 | 0.127 | 0.704 | 0.205 | deepseek_v4 | -0.078 | 0.501 | -0.179 | 0.007 |
| smollm3-3b-e2c.claude46_O_s2 | 0.170 | 0.704 | 0.157 | deepseek_v4 | 0.013 | 0.026 | -0.103 | 0.122 |
| smollm3-3b-e2c.claude46_O_s3 | 0.124 | 0.704 | 0.156 | deepseek_v4 | -0.032 | 0.288 | -0.158 | 0.097 |
| smollm3-3b-e2c.claude46_O_s4 | 0.182 | 0.704 | 0.228 | deepseek_v4 | -0.046 | 0.199 | -0.139 | 0.046 |
| smollm3-3b-e2c.claude46_O_s5 | 0.114 | 0.704 | 0.206 | deepseek_v4 | -0.092 | 0.702 | -0.173 | -0.014 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | 0.413 | 0.797 | 0.200 | gpt4o | 0.212 | 6.0e-04 | 0.138 | 0.286 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | 0.436 | 0.797 | 0.190 | gpt4o | 0.246 | 1.0e-04 | 0.165 | 0.321 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | 0.431 | 0.797 | 0.207 | gpt4o | 0.224 | 2.0e-04 | 0.150 | 0.297 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | 0.400 | 0.797 | 0.189 | gpt4o | 0.211 | 8.0e-04 | 0.135 | 0.286 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | 0.423 | 0.797 | 0.203 | gpt4o | 0.220 | 6.0e-04 | 0.146 | 0.292 |
| smollm3-3b-e2c.gpt4o_O_s1 | 0.336 | 0.904 | 0.396 | deepseek_v4 | -0.061 | 0.198 | -0.147 | 0.022 |
| smollm3-3b-e2c.gpt4o_O_s2 | 0.308 | 0.904 | 0.412 | deepseek_v4 | -0.104 | 0.633 | -0.185 | -0.029 |
| smollm3-3b-e2c.gpt4o_O_s3 | 0.299 | 0.904 | 0.420 | deepseek_v4 | -0.121 | 0.766 | -0.202 | -0.046 |
| smollm3-3b-e2c.gpt4o_O_s4 | 0.304 | 0.904 | 0.407 | deepseek_v4 | -0.103 | 0.616 | -0.195 | -0.014 |
| smollm3-3b-e2c.gpt4o_O_s5 | 0.333 | 0.904 | 0.449 | deepseek_v4 | -0.115 | 0.709 | -0.197 | -0.035 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.262 | 0.066 | 5 |
| claude46 | T1 | -0.014 | 0.050 | 5 |
| claude46 | T3 | -0.043 | 0.037 | 5 |
| claude46 | T5 | -0.064 | 0.033 | 5 |
| claude46 | T6 | 0.067 | 0.049 | 5 |
| deepseek_v4 | T0 | 0.157 | 0.020 | 5 |
| deepseek_v4 | T1 | -0.019 | 0.039 | 5 |
| deepseek_v4 | T3 | 0.100 | 0.020 | 5 |
| deepseek_v4 | T5 | 0.151 | 0.018 | 5 |
| deepseek_v4 | T6 | 0.211 | 0.029 | 5 |
| gpt4o | T0 | -0.172 | 0.032 | 5 |
| gpt4o | T1 | -0.130 | 0.045 | 5 |
| gpt4o | T3 | 0.014 | 0.040 | 5 |
| gpt4o | T5 | -0.040 | 0.042 | 5 |
| gpt4o | T6 | -0.019 | 0.022 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 290 | 0.263 | 0.137 | 0.704 | 0.157 | deepseek_v4 | -0.020 | -0.124 | 0.082 | 0.172 | -0.058 | 0.344 |
| deepseek_v4 | 5 | 289 | 0.447 | 0.376 | 0.797 | 0.145 | gpt4o | 0.232 | 0.150 | 0.306 | 1.0e-04 | 0.100 | 3.0e-04 |
| gpt4o | 5 | 290 | 0.414 | 0.289 | 0.904 | 0.378 | deepseek_v4 | -0.089 | -0.179 | -0.006 | 0.584 | -0.081 | 0.584 |

### S_0 control row: ungated covariate profile vs every teacher (base_control.csv)

| who | profile | teacher | n_families | rho | ceiling | ci_lo | ci_hi | rank | margin | margin_ci_lo | margin_ci_hi |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | ungated covariate profile | claude46 | 290 | 0.111 | 0.704 | 0.037 | 0.182 | 3 | -0.138 | -0.232 | -0.053 |
| smollm3-3b.base_B_s0 | ungated covariate profile | deepseek_v4 | 290 | 0.250 | 0.797 | 0.185 | 0.314 | 1 | 0.076 | -3.7e-04 | 0.152 |
| smollm3-3b.base_B_s0 | ungated covariate profile | gpt4o | 290 | 0.174 | 0.904 | 0.114 | 0.233 | 2 | -0.076 | -0.155 | -3.4e-04 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 5/5 seeds pass -> ok (old rule, not the verdict)
- deepseek_v4: 5/5 seeds pass -> ok (old rule, not the verdict)
- gpt4o: 5/5 seeds pass -> ok (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 0.039 vs run-reassignment null mean -0.065 sd 0.024, p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 5.824, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.102 [0.061, 0.144] p 1.0e-04 alone would read pass; the frozen rule (version 5) also needs D_specific 0.159 [0.107, 0.214] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.015 | 0.009 | 0.027 |
| agree_own | deepseek_v4 | O | 10 | 0.007 | 0.005 | 0.015 |
| agree_own | gpt4o | O | 10 | 0.008 | 0.004 | 0.014 |
| agree_own | all | all | 30 | 0.010 | 0.007 | 0.024 |
| jsd_own | claude46 | O | 10 | 0.005 | 0.004 | 0.011 |
| jsd_own | deepseek_v4 | O | 10 | 0.009 | 0.005 | 0.016 |
| jsd_own | gpt4o | O | 10 | 0.003 | 0.002 | 0.005 |
| jsd_own | all | all | 30 | 0.006 | 0.004 | 0.014 |
| flip_rate | claude46 | O | 10 | 0.019 | 0.011 | 0.035 |
| flip_rate | deepseek_v4 | O | 10 | 0.014 | 0.009 | 0.028 |
| flip_rate | gpt4o | O | 10 | 0.020 | 0.017 | 0.044 |
| flip_rate | all | all | 30 | 0.017 | 0.012 | 0.042 |
| mean_jsd | claude46 | O | 10 | 0.003 | 0.002 | 0.005 |
| mean_jsd | deepseek_v4 | O | 10 | 0.014 | 0.009 | 0.028 |
| mean_jsd | gpt4o | O | 10 | 0.011 | 0.007 | 0.021 |
| mean_jsd | all | all | 30 | 0.009 | 0.008 | 0.024 |
| delta_rho | claude46 | O | 10 | 0.051 | 0.030 | 0.099 |
| delta_rho | deepseek_v4 | O | 10 | 0.016 | 0.012 | 0.034 |
| delta_rho | gpt4o | O | 10 | 0.027 | 0.022 | 0.058 |
| delta_rho | all | all | 30 | 0.031 | 0.026 | 0.077 |
| delta_rho_partial | claude46 | O | 10 | 0.054 | 0.033 | 0.107 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.019 | 0.014 | 0.040 |
| delta_rho_partial | gpt4o | O | 10 | 0.030 | 0.025 | 0.065 |
| delta_rho_partial | all | all | 30 | 0.034 | 0.029 | 0.084 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.