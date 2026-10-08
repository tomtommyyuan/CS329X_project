# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.993, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.988 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.252 [-0.406, -0.103] p_perm 0.983 (null mean -0.136) p_holm 1.000; deepseek_v4 0.169 [0.075, 0.264] p_perm 0.180 (null mean 0.132) p_holm 0.541; gpt4o -0.147 [-0.246, -0.053] p_perm 0.616 (null mean -0.134) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D 0.051 [-0.014, 0.111], p 0.064; D_specific 0.070 [0.002, 0.134], D_shared -0.019 (139 families, 10000 perm / 10000 boot) | **fail** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 139 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = qwen3-4b.base_B_s0) | -0.042 | teacher-level exact p 0.167 (rank 1 of 6 relabellings, floor 0.167); the run-level null (mean -0.068, sd 0.014, p 0.028, 756756 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.776 (pearson 0.572, seed-noise sd 0.030, ordering preserved False) | teacher-level exact p 0.333 (rank 2 of 6, floor 0.167); run-level p 0.009 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | claude46 -0.146 [-0.313, 0.009] p_holm 1.000; deepseek_v4 0.015 [-0.116, 0.158] p_holm 1.000; gpt4o -0.015 [-0.147, 0.110] p_holm 0.897 | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | -0.018 [-0.086, 0.057], p 0.649 (137 families) | exploratory |
| raw D (no r_0 control), seen framings | 0.047 [-0.003, 0.091], p 0.068 | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | 0.063 [2.6e-04, 0.121] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | closest teacher deepseek_v4: rho 0.533 [0.448, 0.611], margin over the next 0.256 [0.130, 0.359] (139 families) | S_0 is systematically closest to deepseek_v4 before training: the confound the partial rho controls for |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.136 | 0.744 | 0.183 | 0.388 | deepseek_v4 | -0.252 | -0.406 | -0.103 | 0.983 | -0.136 | 0.055 | 1.000 | False |
| deepseek_v4 | 5 | 139 | 0.478 | 0.825 | 0.580 | 0.309 | gpt4o | 0.169 | 0.075 | 0.264 | 0.180 | 0.132 | 0.041 | 0.541 | False |
| gpt4o | 5 | 139 | 0.382 | 0.898 | 0.426 | 0.530 | deepseek_v4 | -0.147 | -0.246 | -0.053 | 0.616 | -0.134 | 0.042 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.067 | -0.101 | 0.010 | 3.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = qwen3-4b.base_B_s0, seen framings (e2_secondary_D.json)

| D | ci_lo | ci_hi | p_perm | null_mean | null_sd | D_raw | n_families | n_perm | n_boot |
|---|---|---|---|---|---|---|---|---|---|
| 0.051 | -0.014 | 0.111 | 0.064 | 0.008 | 0.028 | 0.047 | 139 | 10000 | 10000 |

Decomposition D = D_shared + D_specific (E_k = Ebar + U_k: the mean student residual given r_0 interacting with unequal row scales |E_k| carries no own-teacher information; the secondary passes only if D_specific's CI is also above 0). D_scalefree divides every row by the pooled scale s_bar so the shared part cancels exactly (exploratory):

| D_shared | D_specific | ci_specific_lo | ci_specific_hi | p_perm_specific | null_mean_specific | null_sd_specific | D_scalefree | ci_scalefree_lo | ci_scalefree_hi |
|---|---|---|---|---|---|---|---|---|---|
| -0.019 | 0.070 | 0.002 | 0.134 | 0.024 | 0.010 | 0.029 | 0.063 | 2.6e-04 | 0.121 |

Row scales (sd of each pooled student's residual given r_0): qwen3-4b-e2cnf.claude46_O_pooled 0.143, qwen3-4b-e2cnf.deepseek_v4_O_pooled 0.179, qwen3-4b-e2cnf.gpt4o_O_pooled 0.195.

Partial-rho matrix (rows = seed-pooled students, columns = teachers; `contrast` = diagonal - mean off-diagonal of the row; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o | ceiling_own | contrast | contrast_specific |
|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.013 | 0.159 | 0.057 | 0.744 | -0.095 | 0.156 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | -0.016 | 0.185 | 0.171 | 0.825 | 0.108 | -0.020 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | -0.017 | 0.294 | 0.278 | 0.898 | 0.140 | 0.074 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 | nan | nan | nan |

Student-specific part M_specific (U_k against the teachers; D_specific is its contrast):

| student | specific__claude46 | specific__deepseek_v4 | specific__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.023 | -0.105 | -0.160 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | -0.008 | -0.026 | -0.002 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | -0.009 | 0.100 | 0.120 |

Raw (non-partial) matrix on the same cells (last row = column ceilings):

| student | raw__claude46 | raw__deepseek_v4 | raw__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.136 | 0.388 | 0.188 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | 0.155 | 0.478 | 0.309 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | 0.142 | 0.530 | 0.382 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

T0-only matrix (exploratory; last row = column ceilings):

| student | partial__claude46 | partial__deepseek_v4 | partial__gpt4o |
|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_pooled | 0.004 | 0.221 | 0.027 |
| qwen3-4b-e2cnf.deepseek_v4_O_pooled | 0.027 | 0.040 | -0.050 |
| qwen3-4b-e2cnf.gpt4o_O_pooled | 0.092 | 0.029 | 0.076 |
| ceiling sqrt(2r/(1+r)) | 0.744 | 0.825 | 0.898 |

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 139 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 139 | 0.212 | 0.167 | 0.259 |
| students:deepseek_v4 | 5 | 139 | 0.455 | 0.395 | 0.514 |
| students:gpt4o | 5 | 139 | 0.475 | 0.410 | 0.538 |
| teacher:claude46 | 1 | 139 | 0.059 | 0.023 | 0.098 |
| teacher:deepseek_v4 | 1 | 139 | 0.149 | 0.120 | 0.180 |
| teacher:gpt4o | 1 | 139 | 0.075 | 0.048 | 0.106 |
| base_prior | 1 | 139 | 0.165 | 0.144 | 0.186 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.243 | -0.312 | -0.174 |
| students:claude46 | students:gpt4o | -0.263 | -0.328 | -0.195 |
| students:claude46 | teacher:claude46 | 0.153 | 0.096 | 0.212 |
| students:claude46 | base_prior | 0.047 | 0.005 | 0.090 |
| students:deepseek_v4 | students:gpt4o | -0.020 | -0.082 | 0.043 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.305 | 0.245 | 0.365 |
| students:deepseek_v4 | base_prior | 0.290 | 0.237 | 0.342 |
| students:gpt4o | teacher:gpt4o | 0.399 | 0.338 | 0.459 |
| students:gpt4o | base_prior | 0.310 | 0.250 | 0.369 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | run | 0.053 | -0.093 | 0.146 | 6 |
| qwen3-4b.base_B_s0 | base_prior | 0.074 | -0.091 | 0.165 | 139 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.059 | 0.212 | 0.026 | 5 |
| deepseek_v4 | 0.149 | 0.455 | 0.028 | 5 |
| gpt4o | 0.075 | 0.475 | 0.034 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.998 | True | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s2 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.999 | True | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s3 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.993 | True | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s4 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.999 | True | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.claude46_O_s5 | 2764 | 1.000 | 2764 | 2764 | 0 | 0 | 0.999 | True | data/sft_e2cnf/claude46_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.996 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.996 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.996 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.997 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 1990 | 1.000 | 1990 | 1990 | 0 | 0 | 0.995 | True | data/sft_e2cnf/deepseek_v4_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 1.000 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.999 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.999 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 0.998 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 2924 | 1.000 | 2924 | 2924 | 0 | 0 | 1.000 | True | data/sft_e2cnf/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 708 | 354 | 5 | 3540 | 0.997 | 0.995 | 0.999 | True |
| claude46 | gpt4o | 991 | 492 | 5 | 4955 | 0.997 | 0.995 | 0.999 | True |
| deepseek_v4 | claude46 | 708 | 354 | 5 | 3540 | 0.997 | 0.993 | 0.999 | True |
| deepseek_v4 | gpt4o | 513 | 278 | 5 | 2565 | 0.994 | 0.988 | 0.998 | True |
| gpt4o | claude46 | 991 | 492 | 5 | 4955 | 0.999 | 0.998 | 1.000 | True |
| gpt4o | deepseek_v4 | 513 | 278 | 5 | 2565 | 0.998 | 0.994 | 1.000 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.250 | 0.095 | 6 | nan | 0.857 | nan | 0.083 | 0.012 |
| qwen3-4b-e2cnf.claude46_O_s1 | 1.000 | 0.122 | 150 | 0.792 | 0.765 | 0.172 | 0.180 | 0.109 |
| qwen3-4b-e2cnf.claude46_O_s2 | 1.000 | 0.113 | 150 | 0.794 | 0.768 | 0.175 | 0.190 | 0.107 |
| qwen3-4b-e2cnf.claude46_O_s3 | 1.000 | 0.127 | 150 | 0.796 | 0.761 | 0.169 | 0.143 | 0.083 |
| qwen3-4b-e2cnf.claude46_O_s4 | 1.000 | 0.115 | 150 | 0.783 | 0.738 | 0.186 | 0.184 | 0.119 |
| qwen3-4b-e2cnf.claude46_O_s5 | 1.000 | 0.107 | 150 | 0.801 | 0.760 | 0.176 | 0.168 | 0.099 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 1.000 | 0.136 | 150 | 0.751 | 0.714 | 0.156 | 0.270 | 0.187 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 1.000 | 0.132 | 150 | 0.753 | 0.709 | 0.158 | 0.244 | 0.160 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 1.000 | 0.097 | 150 | 0.773 | 0.730 | 0.148 | 0.227 | 0.167 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 1.000 | 0.113 | 150 | 0.758 | 0.720 | 0.153 | 0.243 | 0.177 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 1.000 | 0.118 | 150 | 0.753 | 0.707 | 0.163 | 0.249 | 0.181 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 1.000 | 0.124 | 150 | 0.756 | 0.775 | 0.180 | 0.293 | 0.216 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 0.999 | 0.115 | 150 | 0.760 | 0.776 | 0.175 | 0.288 | 0.211 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 1.000 | 0.105 | 150 | 0.784 | 0.800 | 0.155 | 0.259 | 0.189 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 0.999 | 0.114 | 150 | 0.777 | 0.790 | 0.161 | 0.266 | 0.185 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 1.000 | 0.109 | 150 | 0.770 | 0.789 | 0.164 | 0.232 | 0.180 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.base_B_s0 | 0.847 | 0.857 | 0.829 | 0.134 | 0.061 | 0.117 |
| qwen3-4b-e2cnf.claude46_O_s1 | 0.792 | 0.765 | 0.754 | 0.172 | 0.157 | 0.184 |
| qwen3-4b-e2cnf.claude46_O_s2 | 0.794 | 0.768 | 0.765 | 0.175 | 0.149 | 0.180 |
| qwen3-4b-e2cnf.claude46_O_s3 | 0.796 | 0.750 | 0.761 | 0.169 | 0.148 | 0.173 |
| qwen3-4b-e2cnf.claude46_O_s4 | 0.783 | 0.738 | 0.732 | 0.186 | 0.173 | 0.200 |
| qwen3-4b-e2cnf.claude46_O_s5 | 0.801 | 0.750 | 0.760 | 0.176 | 0.168 | 0.185 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 0.680 | 0.751 | 0.714 | 0.270 | 0.156 | 0.226 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 0.680 | 0.753 | 0.709 | 0.271 | 0.158 | 0.231 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 0.700 | 0.773 | 0.730 | 0.259 | 0.148 | 0.220 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 0.691 | 0.758 | 0.720 | 0.266 | 0.153 | 0.222 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 0.675 | 0.753 | 0.707 | 0.279 | 0.163 | 0.238 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 0.735 | 0.775 | 0.756 | 0.229 | 0.141 | 0.180 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 0.742 | 0.776 | 0.760 | 0.221 | 0.147 | 0.175 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 0.764 | 0.800 | 0.784 | 0.203 | 0.129 | 0.155 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 0.753 | 0.790 | 0.777 | 0.212 | 0.131 | 0.161 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 0.776 | 0.789 | 0.770 | 0.201 | 0.141 | 0.164 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| base | B | 1 | 0.250 | nan | 0.857 | nan | 0.083 | 0.012 |
| claude46 | O | 5 | 1.000 | 0.793 | 0.758 | 0.176 | 0.173 | 0.103 |
| deepseek_v4 | O | 5 | 1.000 | 0.758 | 0.716 | 0.156 | 0.247 | 0.175 |
| gpt4o | O | 5 | 1.000 | 0.769 | 0.786 | 0.167 | 0.268 | 0.196 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = qwen3-4b.base_B_s0 (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

| run_id | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | perm_null_mean | ci_lo | ci_hi | rho__claude46 | rho__deepseek_v4 | rho__gpt4o |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | 139.000 | 0.505 | 0.079 | 0.744 | 0.111 | deepseek_v4 | -0.032 | 0.261 | -0.073 | -0.171 | 0.095 | 0.079 | 0.111 | 0.027 |
| qwen3-4b-e2cnf.claude46_O_s2 | 139.000 | 0.460 | -0.011 | 0.744 | 0.182 | deepseek_v4 | -0.193 | 0.975 | -0.072 | -0.365 | -0.023 | -0.011 | 0.182 | 0.030 |
| qwen3-4b-e2cnf.claude46_O_s3 | 139.000 | 0.423 | -0.008 | 0.744 | 0.121 | deepseek_v4 | -0.128 | 0.843 | -0.067 | -0.295 | 0.011 | -0.008 | 0.121 | 0.045 |
| qwen3-4b-e2cnf.claude46_O_s4 | 139.000 | 0.450 | 0.014 | 0.744 | 0.118 | deepseek_v4 | -0.104 | 0.701 | -0.072 | -0.255 | 0.035 | 0.014 | 0.118 | 0.047 |
| qwen3-4b-e2cnf.claude46_O_s5 | 139.000 | 0.420 | -0.021 | 0.744 | 0.147 | deepseek_v4 | -0.169 | 0.945 | -0.070 | -0.338 | -0.027 | -0.021 | 0.147 | 0.092 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 139.000 | 0.687 | 0.144 | 0.825 | 0.158 | gpt4o | -0.014 | 0.854 | 0.036 | -0.144 | 0.123 | -0.028 | 0.144 | 0.158 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 139.000 | 0.633 | 0.165 | 0.825 | 0.124 | gpt4o | 0.041 | 0.447 | 0.034 | -0.087 | 0.168 | 0.009 | 0.165 | 0.124 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 139.000 | 0.653 | 0.193 | 0.825 | 0.167 | gpt4o | 0.026 | 0.543 | 0.032 | -0.111 | 0.173 | -0.018 | 0.193 | 0.167 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 139.000 | 0.669 | 0.201 | 0.825 | 0.187 | gpt4o | 0.015 | 0.672 | 0.036 | -0.123 | 0.155 | -0.016 | 0.201 | 0.187 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 139.000 | 0.632 | 0.161 | 0.825 | 0.159 | gpt4o | 0.003 | 0.746 | 0.035 | -0.123 | 0.134 | -0.022 | 0.161 | 0.159 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 139.000 | 0.596 | 0.239 | 0.898 | 0.293 | deepseek_v4 | -0.053 | 0.614 | -0.039 | -0.167 | 0.056 | -0.024 | 0.293 | 0.239 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 139.000 | 0.623 | 0.277 | 0.898 | 0.268 | deepseek_v4 | 0.010 | 0.158 | -0.040 | -0.127 | 0.139 | -0.002 | 0.268 | 0.277 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 139.000 | 0.580 | 0.255 | 0.898 | 0.280 | deepseek_v4 | -0.025 | 0.415 | -0.037 | -0.163 | 0.111 | -0.030 | 0.280 | 0.255 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 139.000 | 0.597 | 0.278 | 0.898 | 0.289 | deepseek_v4 | -0.012 | 0.296 | -0.039 | -0.148 | 0.116 | -0.025 | 0.289 | 0.278 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 139.000 | 0.594 | 0.224 | 0.898 | 0.211 | deepseek_v4 | 0.013 | 0.172 | -0.036 | -0.112 | 0.138 | 0.006 | 0.211 | 0.224 |
| ceiling sqrt(2r/(1+r)) | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | nan | 0.744 | 0.825 | 0.898 |

Seed means of deltaRhoPartial per teacher:

| teacher | mean | std | count |
|---|---|---|---|
| claude46 | -0.125 | 0.062 | 5 |
| deepseek_v4 | 0.014 | 0.021 | 5 |
| gpt4o | -0.013 | 0.027 | 5 |

Teacher-level exact null of the mean deltaRhoPartial (k! relabellings; grid_permutation_partial.json `teacher_exact`):

| observed | p | rank | n_assignments | floor |
|---|---|---|---|---|
| -0.042 | 0.167 | 1 | 6 | 0.167 |

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | 0.189 | 0.744 | 0.350 | deepseek_v4 | -0.161 | 0.721 | -0.293 | -0.033 |
| qwen3-4b-e2cnf.claude46_O_s2 | 0.103 | 0.744 | 0.382 | deepseek_v4 | -0.279 | 0.997 | -0.450 | -0.115 |
| qwen3-4b-e2cnf.claude46_O_s3 | 0.097 | 0.744 | 0.318 | deepseek_v4 | -0.221 | 0.972 | -0.370 | -0.081 |
| qwen3-4b-e2cnf.claude46_O_s4 | 0.122 | 0.744 | 0.329 | deepseek_v4 | -0.206 | 0.924 | -0.352 | -0.060 |
| qwen3-4b-e2cnf.claude46_O_s5 | 0.084 | 0.744 | 0.337 | deepseek_v4 | -0.253 | 0.991 | -0.411 | -0.101 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | 0.454 | 0.825 | 0.301 | gpt4o | 0.154 | 0.283 | 0.066 | 0.244 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | 0.446 | 0.825 | 0.267 | gpt4o | 0.178 | 0.096 | 0.075 | 0.278 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | 0.472 | 0.825 | 0.303 | gpt4o | 0.169 | 0.125 | 0.074 | 0.267 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | 0.483 | 0.825 | 0.319 | gpt4o | 0.165 | 0.191 | 0.075 | 0.258 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | 0.443 | 0.825 | 0.293 | gpt4o | 0.149 | 0.294 | 0.057 | 0.245 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | 0.349 | 0.898 | 0.516 | deepseek_v4 | -0.167 | 0.833 | -0.263 | -0.074 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | 0.381 | 0.898 | 0.509 | deepseek_v4 | -0.128 | 0.456 | -0.228 | -0.036 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | 0.360 | 0.898 | 0.502 | deepseek_v4 | -0.142 | 0.664 | -0.251 | -0.038 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | 0.379 | 0.898 | 0.515 | deepseek_v4 | -0.135 | 0.550 | -0.237 | -0.043 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | 0.338 | 0.898 | 0.460 | deepseek_v4 | -0.123 | 0.528 | -0.230 | -0.020 |

### deltaRhoPartial by variant (seed mean over O runs; T0 = unseen framing, r demeaned over T0 + seen variants; inheritance_partial_by_variant.csv)

| teacher | variant | mean | std | count |
|---|---|---|---|---|
| claude46 | T0 | -0.181 | 0.099 | 5 |
| claude46 | T1 | -0.036 | 0.016 | 5 |
| claude46 | T3 | -0.344 | 0.111 | 5 |
| claude46 | T5 | -0.193 | 0.062 | 5 |
| claude46 | T6 | -0.018 | 0.091 | 5 |
| deepseek_v4 | T0 | 0.004 | 0.051 | 5 |
| deepseek_v4 | T1 | 0.043 | 0.071 | 5 |
| deepseek_v4 | T3 | -0.002 | 0.041 | 5 |
| deepseek_v4 | T5 | -0.046 | 0.069 | 5 |
| deepseek_v4 | T6 | -0.024 | 0.036 | 5 |
| gpt4o | T0 | 0.007 | 0.054 | 5 |
| gpt4o | T1 | -0.120 | 0.100 | 5 |
| gpt4o | T3 | -0.071 | 0.051 | 5 |
| gpt4o | T5 | 0.034 | 0.070 | 5 |
| gpt4o | T6 | 0.052 | 0.017 | 5 |

### P3: seed-mean profile per teacher, deltaRhoPartial with family permutation + Holm (inheritance_partial_pooled.csv)

| teacher | n_seeds | n_families | rho_base | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | p_holm |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 139 | 0.511 | 0.013 | 0.744 | 0.159 | deepseek_v4 | -0.146 | -0.313 | 0.009 | 0.876 | -0.077 | 1.000 |
| deepseek_v4 | 5 | 139 | 0.681 | 0.185 | 0.825 | 0.171 | gpt4o | 0.015 | -0.116 | 0.158 | 0.678 | 0.037 | 1.000 |
| gpt4o | 5 | 139 | 0.633 | 0.278 | 0.898 | 0.294 | deepseek_v4 | -0.015 | -0.147 | 0.110 | 0.299 | -0.042 | 0.897 |

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

- P1 mean deltaRhoPartial -0.042 vs run-reassignment null mean -0.068 sd 0.014, p 0.028 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167
- P2 slope 1.776, run-reassignment p 0.009 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.333

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D 0.051 [-0.014, 0.111] p 0.064 alone would read fail / pending; the frozen rule (version 5) also needs D_specific 0.070 [0.002, 0.134] above 0 -> fail

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | O | 10 | 0.008 | 0.005 | 0.015 |
| agree_own | deepseek_v4 | O | 10 | 0.010 | 0.009 | 0.021 |
| agree_own | gpt4o | O | 10 | 0.015 | 0.008 | 0.026 |
| agree_own | all | all | 30 | 0.011 | 0.008 | 0.023 |
| jsd_own | claude46 | O | 10 | 0.007 | 0.005 | 0.015 |
| jsd_own | deepseek_v4 | O | 10 | 0.007 | 0.004 | 0.012 |
| jsd_own | gpt4o | O | 10 | 0.013 | 0.007 | 0.023 |
| jsd_own | all | all | 30 | 0.009 | 0.006 | 0.020 |
| flip_rate | base | B | 0 | nan | nan | nan |
| flip_rate | claude46 | O | 10 | 0.022 | 0.015 | 0.044 |
| flip_rate | deepseek_v4 | O | 10 | 0.018 | 0.013 | 0.036 |
| flip_rate | gpt4o | O | 10 | 0.030 | 0.018 | 0.059 |
| flip_rate | all | all | 30 | 0.024 | 0.016 | 0.052 |
| mean_jsd | base | B | 0 | nan | nan | nan |
| mean_jsd | claude46 | O | 10 | 0.016 | 0.010 | 0.032 |
| mean_jsd | deepseek_v4 | O | 10 | 0.013 | 0.007 | 0.024 |
| mean_jsd | gpt4o | O | 10 | 0.020 | 0.013 | 0.034 |
| mean_jsd | all | all | 30 | 0.017 | 0.010 | 0.034 |
| delta_rho | claude46 | O | 10 | 0.057 | 0.031 | 0.106 |
| delta_rho | deepseek_v4 | O | 10 | 0.015 | 0.008 | 0.027 |
| delta_rho | gpt4o | O | 10 | 0.020 | 0.014 | 0.042 |
| delta_rho | all | all | 30 | 0.031 | 0.027 | 0.083 |
| delta_rho_partial | claude46 | O | 10 | 0.077 | 0.045 | 0.150 |
| delta_rho_partial | deepseek_v4 | O | 10 | 0.027 | 0.014 | 0.049 |
| delta_rho_partial | gpt4o | O | 10 | 0.034 | 0.020 | 0.065 |
| delta_rho_partial | all | all | 30 | 0.046 | 0.037 | 0.118 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.