# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.942, min answer rate 0.999 | fail |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.922 | pass |
| **E1** | E1a and E1b for all teachers | | **FAIL (E1a fail, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.208 [-0.367, -0.055] p_perm 0.917 (null mean -0.129) p_holm 0.917; deepseek_v4 0.201 [0.092, 0.310] p_perm 0.037 (null mean 0.126) p_holm 0.110; gpt4o -0.106 [-0.222, -1.4e-04] p_perm 0.320 (null mean -0.126) p_holm 0.640; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.087 [0.023, 0.149], p 0.003; D_specific 0.116 [0.044, 0.190], D_shared -0.030 (139 families, 10000 perm / 10000 boot) | **pass** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | 9.3e-04 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.066, sd 0.016, p 2.6e-06, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.922 (pearson 0.675, seed-noise sd 0.028, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 3.6e-04 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.102 [-0.272, 0.051] p_holm 0.673; deepseek_v4 0.064 [-0.069, 0.212] p_holm 0.570; gpt4o 0.039 [-0.089, 0.161] p_holm 0.203 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | 0.001 [-0.072, 0.078], p 0.495 (138 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.075 [0.026, 0.120], p 0.004 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.103 [0.040, 0.165] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.185 | 0.744 | 0.248 | 0.393 | deepseek_v4 | -0.208 | -0.367 | -0.055 | 0.917 | -0.129 | 0.057 | 0.917 | False |
| deepseek_v4 | 5 | 139 | 0.502 | 0.825 | 0.609 | 0.302 | gpt4o | 0.201 | 0.092 | 0.310 | 0.037 | 0.126 | 0.043 | 0.110 | False |
| gpt4o | 5 | 139 | 0.394 | 0.898 | 0.439 | 0.500 | deepseek_v4 | -0.106 | -0.222 | -1.4e-04 | 0.320 | -0.126 | 0.044 | 0.640 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.035 | -0.095 | 0.013 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.087 | 0.023 | 0.149 | 0.003 | 0.007 | 0.028 | 0.075 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.030 | 0.116 | 0.044 | 0.190 | 6.0e-04 | 0.012 | 0.031 | 0.103 | 0.040 | 0.165 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2cnf.claude46_O_pooled 0.104, qwen3-4b-e2cnf.deepseek_v4_O_pooled 0.157, qwen3-4b-e2cnf.gpt4o_O_pooled 0.160.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.077 | 0.179 | 0.082 | 0.744 | -0.053 | 0.205 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | -0.005 | 0.225 | 0.161 | 0.825 | 0.147 | 0.040 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | 0.001 | 0.256 | 0.295 | 0.898 | 0.167 | 0.104 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.053 | -0.126 | -0.178 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | -0.021 | 0.024 | -0.011 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | -0.014 | 0.058 | 0.126 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.185 | 0.393 | 0.205 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | 0.163 | 0.502 | 0.302 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | 0.152 | 0.500 | 0.394 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.029 | 0.167 | 0.055 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | 0.114 | 0.105 | -0.041 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | 0.061 | 0.033 | 0.064 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.142 | 0.109 | 0.178 |
| students:deepseek_v4 | 5 | 139 | 0.383 | 0.325 | 0.439 |
| students:gpt4o | 5 | 139 | 0.364 | 0.305 | 0.423 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.165 | 0.144 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.241 | -0.299 | -0.183 |
| students:claude46 | students:gpt4o | -0.222 | -0.279 | -0.166 |
| students:claude46 | teacher:claude46 | 0.083 | 0.036 | 0.131 |
| students:claude46 | base_prior | -0.023 | -0.055 | 0.010 |
| students:deepseek_v4 | students:gpt4o | 0.019 | -0.036 | 0.074 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.233 | 0.178 | 0.288 |
| students:deepseek_v4 | base_prior | 0.218 | 0.169 | 0.267 |
| students:gpt4o | teacher:gpt4o | 0.289 | 0.235 | 0.342 |
| students:gpt4o | base_prior | 0.199 | 0.145 | 0.254 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.091 | 0.165 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.142 | 0.010 | 5 |
| deepseek_v4 | 0.149 | 0.383 | 0.029 | 5 |
| gpt4o | 0.075 | 0.364 | 0.037 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.946 | False | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s2 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.952 | True | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s3 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.947 | False | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s4 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.942 | False | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s5 | 2764 | 0.999 | 2764 | 2764 | 0 | 0 | 0.943 | False | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.993 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.992 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.996 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.994 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.993 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.983 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 2924 | 0.999 | 2924 | 2924 | 0 | 0 | 0.982 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.984 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.982 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.988 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 708 | 354 | 5 | 3540 | 0.947 | 0.931 | 0.961 | True |
| claude46 | gpt4o | 991 | 492 | 5 | 4955 | 0.936 | 0.922 | 0.949 | True |
| deepseek_v4 | claude46 | 708 | 354 | 5 | 3540 | 0.993 | 0.989 | 0.997 | True |
| deepseek_v4 | gpt4o | 513 | 278 | 5 | 2565 | 0.993 | 0.988 | 0.997 | True |
| gpt4o | claude46 | 991 | 492 | 5 | 4955 | 0.983 | 0.977 | 0.988 | True |
| gpt4o | deepseek_v4 | 513 | 278 | 5 | 2565 | 0.972 | 0.960 | 0.983 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2cnf.claude46_O_s1 | 1.000 | 0.090 | 150 | 0.815 | 0.777 | 0.148 | 0.109 | 0.041 |
| qwen3-4b-e2cnf.claude46_O_s2 | 1.000 | 0.097 | 150 | 0.835 | 0.796 | 0.142 | 0.093 | 0.045 |
| qwen3-4b-e2cnf.claude46_O_s3 | 1.000 | 0.086 | 150 | 0.819 | 0.782 | 0.154 | 0.101 | 0.046 |
| qwen3-4b-e2cnf.claude46_O_s4 | 1.000 | 0.092 | 150 | 0.817 | 0.780 | 0.147 | 0.124 | 0.046 |
| qwen3-4b-e2cnf.claude46_O_s5 | 1.000 | 0.087 | 150 | 0.810 | 0.767 | 0.148 | 0.119 | 0.047 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 1.000 | 0.119 | 150 | 0.783 | 0.735 | 0.139 | 0.211 | 0.148 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 1.000 | 0.144 | 150 | 0.771 | 0.723 | 0.145 | 0.192 | 0.130 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 1.000 | 0.095 | 150 | 0.770 | 0.730 | 0.135 | 0.200 | 0.130 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 1.000 | 0.139 | 150 | 0.756 | 0.716 | 0.143 | 0.224 | 0.154 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 1.000 | 0.111 | 150 | 0.771 | 0.720 | 0.140 | 0.197 | 0.140 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 1.000 | 0.087 | 150 | 0.796 | 0.805 | 0.141 | 0.196 | 0.121 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 1.000 | 0.091 | 150 | 0.807 | 0.810 | 0.130 | 0.177 | 0.105 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 1.000 | 0.090 | 150 | 0.815 | 0.820 | 0.137 | 0.183 | 0.118 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 1.000 | 0.096 | 150 | 0.793 | 0.802 | 0.142 | 0.224 | 0.143 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 1.000 | 0.093 | 150 | 0.798 | 0.808 | 0.143 | 0.191 | 0.123 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2cnf.claude46_O_s1 | 0.815 | 0.758 | 0.777 | 0.148 | 0.136 | 0.152 |
| qwen3-4b-e2cnf.claude46_O_s2 | 0.835 | 0.778 | 0.796 | 0.142 | 0.132 | 0.144 |
| qwen3-4b-e2cnf.claude46_O_s3 | 0.819 | 0.766 | 0.782 | 0.154 | 0.139 | 0.157 |
| qwen3-4b-e2cnf.claude46_O_s4 | 0.817 | 0.771 | 0.780 | 0.147 | 0.134 | 0.151 |
| qwen3-4b-e2cnf.claude46_O_s5 | 0.810 | 0.760 | 0.767 | 0.148 | 0.135 | 0.153 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 0.710 | 0.783 | 0.735 | 0.252 | 0.139 | 0.216 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 0.703 | 0.771 | 0.723 | 0.258 | 0.145 | 0.224 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 0.702 | 0.770 | 0.730 | 0.246 | 0.135 | 0.208 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 0.687 | 0.756 | 0.716 | 0.256 | 0.143 | 0.215 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 0.700 | 0.771 | 0.720 | 0.254 | 0.140 | 0.215 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 0.774 | 0.805 | 0.796 | 0.186 | 0.112 | 0.141 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 0.796 | 0.810 | 0.807 | 0.174 | 0.109 | 0.130 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 0.790 | 0.820 | 0.815 | 0.182 | 0.109 | 0.137 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 0.771 | 0.802 | 0.793 | 0.187 | 0.109 | 0.142 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 0.782 | 0.808 | 0.798 | 0.189 | 0.110 | 0.143 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.819 | 0.780 | 0.148 | 0.109 | 0.045 |
| deepseek_v4 | O | 5 | 1.000 | 0.770 | 0.725 | 0.141 | 0.205 | 0.140 |
| gpt4o | O | 5 | 1.000 | 0.802 | 0.809 | 0.139 | 0.194 | 0.122 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | 139.000 | 0.453 | 0.053 | 0.744 | 0.166 | deepseek_v4 | -0.113 | 0.732 | -0.073 | -0.274 | 0.036 | 0.053 | 0.166 | 0.068 |
| qwen3-4b-e2cnf.claude46_O_s2 | 139.000 | 0.475 | 0.083 | 0.744 | 0.198 | deepseek_v4 | -0.114 | 0.756 | -0.072 | -0.288 | 0.048 | 0.083 | 0.198 | 0.076 |
| qwen3-4b-e2cnf.claude46_O_s3 | 139.000 | 0.453 | 0.069 | 0.744 | 0.140 | deepseek_v4 | -0.071 | 0.501 | -0.072 | -0.248 | 0.086 | 0.069 | 0.140 | 0.047 |
| qwen3-4b-e2cnf.claude46_O_s4 | 139.000 | 0.494 | 0.068 | 0.744 | 0.160 | deepseek_v4 | -0.092 | 0.611 | -0.075 | -0.247 | 0.053 | 0.068 | 0.160 | 0.072 |
| qwen3-4b-e2cnf.claude46_O_s5 | 139.000 | 0.433 | 0.083 | 0.744 | 0.164 | deepseek_v4 | -0.082 | 0.599 | -0.067 | -0.249 | 0.041 | 0.083 | 0.164 | 0.117 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 139.000 | 0.639 | 0.222 | 0.825 | 0.130 | gpt4o | 0.092 | 0.116 | 0.030 | -0.042 | 0.226 | -0.031 | 0.222 | 0.130 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 139.000 | 0.640 | 0.197 | 0.825 | 0.129 | gpt4o | 0.069 | 0.233 | 0.031 | -0.068 | 0.201 | 0.033 | 0.197 | 0.129 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 139.000 | 0.641 | 0.233 | 0.825 | 0.167 | gpt4o | 0.066 | 0.237 | 0.028 | -0.081 | 0.226 | -1.7e-04 | 0.233 | 0.167 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 139.000 | 0.693 | 0.184 | 0.825 | 0.158 | gpt4o | 0.025 | 0.600 | 0.037 | -0.107 | 0.162 | -0.017 | 0.184 | 0.158 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 139.000 | 0.637 | 0.204 | 0.825 | 0.160 | gpt4o | 0.044 | 0.409 | 0.033 | -0.085 | 0.183 | -0.005 | 0.204 | 0.160 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 139.000 | 0.589 | 0.304 | 0.898 | 0.240 | deepseek_v4 | 0.064 | 0.030 | -0.036 | -0.063 | 0.187 | 0.013 | 0.240 | 0.304 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 139.000 | 0.582 | 0.264 | 0.898 | 0.201 | deepseek_v4 | 0.063 | 0.037 | -0.035 | -0.071 | 0.189 | -0.010 | 0.201 | 0.264 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 139.000 | 0.576 | 0.272 | 0.898 | 0.266 | deepseek_v4 | 0.007 | 0.210 | -0.036 | -0.118 | 0.133 | 0.016 | 0.266 | 0.272 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 139.000 | 0.633 | 0.281 | 0.898 | 0.270 | deepseek_v4 | 0.012 | 0.164 | -0.038 | -0.112 | 0.133 | -0.002 | 0.270 | 0.281 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 139.000 | 0.605 | 0.274 | 0.898 | 0.230 | deepseek_v4 | 0.044 | 0.061 | -0.036 | -0.094 | 0.176 | -0.012 | 0.230 | 0.274 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.094 | 0.019 | 5 |
| deepseek_v4 | 0.059 | 0.026 | 5 |
| gpt4o | 0.038 | 0.028 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| 9.3e-04 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | 0.157 | 0.744 | 0.367 | deepseek_v4 | -0.210 | 0.924 | -0.362 | -0.064 |
| qwen3-4b-e2cnf.claude46_O_s2 | 0.187 | 0.744 | 0.400 | deepseek_v4 | -0.213 | 0.941 | -0.379 | -0.055 |
| qwen3-4b-e2cnf.claude46_O_s3 | 0.171 | 0.744 | 0.347 | deepseek_v4 | -0.177 | 0.825 | -0.336 | -0.020 |
| qwen3-4b-e2cnf.claude46_O_s4 | 0.178 | 0.744 | 0.381 | deepseek_v4 | -0.203 | 0.904 | -0.348 | -0.061 |
| qwen3-4b-e2cnf.claude46_O_s5 | 0.178 | 0.744 | 0.356 | deepseek_v4 | -0.178 | 0.882 | -0.335 | -0.026 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 0.485 | 0.825 | 0.273 | gpt4o | 0.212 | 0.012 | 0.101 | 0.330 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 0.469 | 0.825 | 0.272 | gpt4o | 0.197 | 0.032 | 0.083 | 0.309 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 0.493 | 0.825 | 0.301 | gpt4o | 0.192 | 0.036 | 0.081 | 0.307 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 0.481 | 0.825 | 0.302 | gpt4o | 0.180 | 0.112 | 0.081 | 0.280 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 0.473 | 0.825 | 0.295 | gpt4o | 0.178 | 0.093 | 0.076 | 0.284 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 0.399 | 0.898 | 0.478 | deepseek_v4 | -0.079 | 0.189 | -0.196 | 0.032 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 0.368 | 0.898 | 0.448 | deepseek_v4 | -0.081 | 0.232 | -0.204 | 0.034 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 0.373 | 0.898 | 0.491 | deepseek_v4 | -0.117 | 0.488 | -0.233 | -0.003 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 0.385 | 0.898 | 0.514 | deepseek_v4 | -0.130 | 0.502 | -0.233 | -0.030 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 0.377 | 0.898 | 0.477 | deepseek_v4 | -0.100 | 0.333 | -0.214 | 0.004 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.123 | 0.041 | 5 |
| claude46 | T1 | -0.031 | 0.076 | 5 |
| claude46 | T3 | -0.309 | 0.029 | 5 |
| claude46 | T5 | -0.198 | 0.057 | 5 |
| claude46 | T6 | 0.049 | 0.035 | 5 |
| deepseek_v4 | T0 | -0.006 | 0.054 | 5 |
| deepseek_v4 | T1 | 0.076 | 0.090 | 5 |
| deepseek_v4 | T3 | 0.033 | 0.056 | 5 |
| deepseek_v4 | T5 | 0.015 | 0.045 | 5 |
| deepseek_v4 | T6 | 0.056 | 0.068 | 5 |
| gpt4o | T0 | 8.9e-04 | 0.047 | 5 |
| gpt4o | T1 | -0.040 | 0.100 | 5 |
| gpt4o | T3 | -0.079 | 0.053 | 5 |
| gpt4o | T5 | 0.129 | 0.057 | 5 |
| gpt4o | T6 | 0.085 | 0.041 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.490 | 0.077 | 0.744 | 0.179 | deepseek_v4 | -0.102 | -0.272 | 0.051 | 0.673 | -0.075 | 0.673 |
| deepseek_v4 | 5 | 139 | 0.680 | 0.225 | 0.825 | 0.161 | gpt4o | 0.064 | -0.069 | 0.212 | 0.285 | 0.035 | 0.570 |
| gpt4o | 5 | 139 | 0.619 | 0.295 | 0.898 | 0.256 | deepseek_v4 | 0.039 | -0.089 | 0.161 | 0.068 | -0.038 | 0.203 |

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
- gpt4o: 0/5 seeds pass -> fail (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial 9.3e-04 vs run-reassignment null mean -0.066 sd 0.016, p 2.6e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 1.922, run-reassignment p 3.6e-04 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.087 [0.023, 0.149] p 0.003 alone would read pass; the frozen rule (version 5) also needs D_specific 0.116 [0.044, 0.190] above 0 -> pass

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.011 | 0.008 | 0.022 |
| agree_own | deepseek_v4 | O | 10 | 0.011 | 0.008 | 0.022 |
| agree_own | gpt4o | O | 10 | 0.011 | 0.007 | 0.021 |
| agree_own | all | all | 30 | 0.011 | 0.008 | 0.024 |
| jsd_own | claude46 | O | 10 | 0.005 | 0.003 | 0.009 |
| jsd_own | deepseek_v4 | O | 10 | 0.005 | 0.003 | 0.009 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.004 | 0.013 |
| jsd_own | all | all | 30 | 0.005 | 0.004 | 0.012 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.016 | 0.009 | 0.029 |
| flip_rate | deepseek_v4 | O | 10 | 0.016 | 0.010 | 0.030 |
| flip_rate | gpt4o | O | 10 | 0.022 | 0.015 | 0.045 |
| flip_rate | all | all | 30 | 0.018 | 0.012 | 0.038 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.003 | 0.002 | 0.006 |
| mean_jsd | deepseek_v4 | O | 10 | 0.013 | 0.008 | 0.024 |
| mean_jsd | gpt4o | O | 10 | 0.016 | 0.011 | 0.032 |
| mean_jsd | all | all | 30 | 0.011 | 0.010 | 0.025 |
| delta_rho | claude46 | O | 10 | 0.021 | 0.014 | 0.036 |
| delta_rho | deepseek_v4 | O | 10 | 0.017 | 0.010 | 0.033 |
| delta_rho | gpt4o | O | 10 | 0.028 | 0.016 | 0.050 |
| delta_rho | all | all | 30 | 0.022 | 0.014 | 0.044 |
| delta_rho_partial | claude46 | O | 10 | 0.024 | 0.014 | 0.043 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.032 | 0.018 | 0.058 |
| delta_rho_partial | gpt4o | O | 10 | 0.033 | 0.021 | 0.057 |
| delta_rho_partial | all | all | 30 | 0.030 | 0.018 | 0.057 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.