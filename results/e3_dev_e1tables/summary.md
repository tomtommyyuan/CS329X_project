# E1 / E2 summary (dev, variants T1, T3, T5, T6; rules frozen on dev 2026-10-05, corrected 2026-10-05: family-level inference; auto-generated)

## Verdicts (rules frozen on dev 2026-10-05, corrected 2026-10-05; test is evaluated once)

**dev = rule-selection split** (the rules were chosen here after the dev diagnostics and frozen on 2026-10-05): the verdicts on this split are descriptive and not confirmatory; only results/e1 (test) is confirmatory.

| test | rule | value | verdict |
|---|---|---|---|
| E1a | every O run reproduces >= 0.95 of its SFT target letters (all prompts read out) | min accuracy 0.981, min answer rate 1.000 | pass |
| E1b | contested training items: ci_lo of the own-teacher share > 0.5 vs every other teacher | min ci_lo 0.841 | pass |
| **E1** | E1a and E1b for all teachers | | **PASS (E1a pass, E1b pass)** |
| **E2 primary** | pre-registered: per teacher, seed-mean delta_rho = rho(own) - max rho(other) > 0 with family-permutation Holm p < 0.05; PASS >= 2/3 teachers, PARTIAL 1/3, FAIL 0/3 | claude46 -0.117 [-0.297, 0.058] p_perm 0.761 (null mean -0.077) p_holm 1.000; deepseek_v4 0.153 [0.019, 0.280] p_perm 0.084 (null mean 0.088) p_holm 0.251; gpt4o -0.096 [-0.241, 0.053] p_perm 0.528 (null mean -0.093) p_holm 1.000; 0/3 pass | **FAIL** |
| **E2 secondary** | pre-declared: D = diagonal - off-diagonal mean of the seed-pooled student x teacher partial-rho matrix given r_0, seen framings; family-bootstrap 95% CI excludes 0, family-permutation p < 0.05, and the student-specific part D_specific (D = D_shared + D_specific) has a CI above 0 | D nan [nan, nan], p nan; D_specific nan [nan, nan], D_shared nan (0 families, 0 perm / 0 boot) | **pending (no base readout for the covariate r_0, or fewer than 2 teachers with O runs)** |

Reliability ceilings (teacher order split-half reliability r of the framing profile, docs/E0_results.md §13): the symmetrized profile averages the two orders, so its reliability is Spearman-Brown 2r / (1 + r) and the ceiling of any student-teacher rho with it is sqrt(2r / (1 + r)); the raw r is NOT a bound. The tables print the own teacher's ceiling and rho / ceiling next to every rho_own, and a ceiling row under every rho__{teacher} / partial__{teacher} / raw__{teacher} column (column ceilings apply to every entry of that column). This split (dev): claude46 r 0.383 -> ceiling 0.744, deepseek_v4 r 0.515 -> ceiling 0.825, gpt4o r 0.675 -> ceiling 0.898; test split: claude46 r 0.329 -> ceiling 0.704, deepseek_v4 r 0.466 -> ceiling 0.797, gpt4o r 0.691 -> ceiling 0.904.
E0 gate (docs/03 §1, on the raw split-half r): 2 of 3 teachers (claude46, deepseek_v4) are below 0.5 on the test split, so E0's P2 fails: per docs/03 §1 'RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5' -- family-level inheritance (RQ1 / E2 / E7) is reported as exploratory / secondary and the pre-specified main line is E2b / E3 / E4 / E5, of which this project runs E3 (form effects on inheritance).

Conventions: family-permutation p = (count + 1) / (n + 1) (floor 1 / (n + 1)); CIs = 2.5 / 97.5 percentiles of the family bootstrap (families resampled jointly for students, teachers and r_0); teacher-level exact p = share of the k! teacher relabellings (the observed one included) with statistic >= observed (floor 1 / k!); the run-level reassignment p (756,756 assignments for 3 x 5 runs) is pseudo-replicated and no longer a test. Suggestibility values are computed on the 137 families complete for every O run, every teacher and r_0.

## Descriptive (no verdict)

| item | value | note |
|---|---|---|
| mean deltaRhoPartial over the O runs (r_0 = absent) | nan | teacher-level exact p nan (rank None of 0 relabellings, floor nan); the run-level null (mean nan, sd nan, p nan, 0 assignments) is pseudo-replicated |
| suggestibility dose-response: slope of s_run on own s_T | 1.367 (pearson 0.911, seed-noise sd 0.010, ordering preserved True) | teacher-level exact p 0.167 (rank 1 of 6, floor 0.167); run-level p 1.3e-06 is pseudo-replicated. Statement under test, descriptively: SFT replaces the base model's suggestibility with the training labels' framing-label association (see the group table) |
| P3: per-teacher seed-mean deltaRhoPartial (partial given r_0), family permutation + Holm | nan | supportive only |
| D on T0 only (unseen framing; r demeaned over T0 + seen) | nan [nan, nan], p nan (0 families) | exploratory |
| raw D (no r_0 control), seen framings | nan [nan, nan], p nan | exploratory; the partial D above is the pre-declared one |
| scale-free D (pooled row scale s_bar, shared part cancels exactly), seen framings, partial | nan [nan, nan] | exploratory alternative to the D_specific guard |
| S_0 control (e2_plan: S_0's delta_rho ~ 0), ungated covariate profile | nan | pending (no base readout) |

## E2 primary: seed-mean profile per teacher, uncontrolled delta_rho with family permutation + Holm (inheritance_pooled.csv)

| teacher | n_seeds | n_families | rho_own | ceiling | rho_over_ceiling | rho_other_max | other_argmax | delta_rho | ci_lo | ci_hi | p_perm | perm_null_mean | perm_null_sd | p_holm | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 138 | 0.215 | 0.744 | 0.289 | 0.332 | deepseek_v4 | -0.117 | -0.297 | 0.058 | 0.761 | -0.077 | 0.059 | 1.000 | False |
| deepseek_v4 | 5 | 138 | 0.505 | 0.825 | 0.613 | 0.353 | gpt4o | 0.153 | 0.019 | 0.280 | 0.084 | 0.088 | 0.047 | 0.251 | False |
| gpt4o | 5 | 139 | 0.373 | 0.898 | 0.415 | 0.469 | deepseek_v4 | -0.096 | -0.241 | 0.053 | 0.528 | -0.093 | 0.050 | 1.000 | False |

The permutation null of delta_rho is not centred at 0 (the family permutation keeps each profile's variant main effects), so p_perm is read against perm_null_mean.

Grid permutation of the pre-registration (random run -> teacher label shuffles; descriptive, pseudo-replicated):

| observed | null_mean | null_sd | p | method | n_perm | n_runs |
|---|---|---|---|---|---|---|
| -0.013 | -0.081 | 0.016 | 1.0e-04 | random | 10000 | 15 |

## E2 secondary: D from the seed-pooled student x teacher partial-rho matrix given r_0 = absent, seen framings (e2_secondary_D.json)

pending: no base run (version B) with a prior profile, or fewer than 2 teachers with O runs

## Suggestibility s = delta(T5) - delta(T6) per group, family-bootstrap 95% CI (suggestibility_groups.csv, suggestibility_group_pairs.csv; 137 common families)

| group | n_profiles | n_families | s | ci_lo | ci_hi |
|---|---|---|---|---|---|
| students:claude46 | 5 | 137 | 0.031 | 0.019 | 0.045 |
| students:deepseek_v4 | 5 | 137 | 0.177 | 0.132 | 0.222 |
| students:gpt4o | 5 | 137 | 0.121 | 0.089 | 0.156 |
| teacher:claude46 | 1 | 137 | 0.049 | 0.014 | 0.086 |
| teacher:deepseek_v4 | 1 | 137 | 0.145 | 0.116 | 0.174 |
| teacher:gpt4o | 1 | 137 | 0.075 | 0.047 | 0.105 |

Pairwise differences (students of A - students of B; students - own teacher; students - base prior):

| a | b | diff | ci_lo | ci_hi |
|---|---|---|---|---|
| students:claude46 | students:deepseek_v4 | -0.146 | -0.184 | -0.108 |
| students:claude46 | students:gpt4o | -0.090 | -0.118 | -0.064 |
| students:claude46 | teacher:claude46 | -0.018 | -0.052 | 0.017 |
| students:deepseek_v4 | students:gpt4o | 0.055 | 0.029 | 0.083 |
| students:deepseek_v4 | teacher:deepseek_v4 | 0.032 | -0.009 | 0.076 |
| students:gpt4o | teacher:gpt4o | 0.047 | 0.014 | 0.080 |

Per profile: R runs and the base (prior profile without the mass gate, and the gated readout where it has complete families):

| who | kind | delta_T5 | delta_T6 | s | n_families |
|---|---|---|---|---|---|
| qwen3-4b.claude46_C_s1 | run | 0.008 | -0.002 | 0.010 | 137 |
| qwen3-4b.claude46_C_s2 | run | 0.018 | -0.013 | 0.031 | 137 |
| qwen3-4b.claude46_C_s3 | run | 0.022 | -0.015 | 0.037 | 137 |
| qwen3-4b.claude46_C_s4 | run | 0.017 | -0.019 | 0.036 | 137 |
| qwen3-4b.claude46_C_s5 | run | 0.014 | -0.009 | 0.023 | 137 |
| qwen3-4b.claude46_F_s1 | run | 0.012 | -0.016 | 0.028 | 137 |
| qwen3-4b.claude46_F_s2 | run | 0.015 | -0.017 | 0.032 | 137 |
| qwen3-4b.claude46_F_s3 | run | 0.015 | -0.013 | 0.028 | 137 |
| qwen3-4b.claude46_F_s4 | run | 0.018 | -0.014 | 0.032 | 137 |
| qwen3-4b.claude46_F_s5 | run | 0.013 | -0.012 | 0.025 | 137 |
| qwen3-4b.deepseek_v4_C_s1 | run | 0.069 | -0.117 | 0.185 | 137 |
| qwen3-4b.deepseek_v4_C_s2 | run | 0.070 | -0.115 | 0.185 | 137 |
| qwen3-4b.deepseek_v4_C_s3 | run | 0.056 | -0.084 | 0.140 | 137 |
| qwen3-4b.deepseek_v4_C_s4 | run | 0.073 | -0.110 | 0.183 | 137 |
| qwen3-4b.deepseek_v4_C_s5 | run | 0.067 | -0.097 | 0.164 | 137 |
| qwen3-4b.deepseek_v4_F_s1 | run | 0.077 | -0.113 | 0.190 | 137 |
| qwen3-4b.deepseek_v4_F_s2 | run | 0.075 | -0.109 | 0.184 | 137 |
| qwen3-4b.deepseek_v4_F_s3 | run | 0.074 | -0.099 | 0.173 | 137 |
| qwen3-4b.deepseek_v4_F_s4 | run | 0.070 | -0.103 | 0.172 | 137 |
| qwen3-4b.deepseek_v4_F_s5 | run | 0.060 | -0.092 | 0.151 | 137 |
| qwen3-4b.gpt4o_C_s1 | run | 0.041 | -0.065 | 0.107 | 137 |
| qwen3-4b.gpt4o_C_s2 | run | 0.046 | -0.056 | 0.102 | 137 |
| qwen3-4b.gpt4o_C_s3 | run | 0.053 | -0.067 | 0.120 | 137 |
| qwen3-4b.gpt4o_C_s4 | run | 0.050 | -0.063 | 0.113 | 137 |
| qwen3-4b.gpt4o_C_s5 | run | 0.046 | -0.062 | 0.108 | 137 |
| qwen3-4b.gpt4o_F_s1 | run | 0.051 | -0.076 | 0.128 | 137 |
| qwen3-4b.gpt4o_F_s2 | run | 0.047 | -0.066 | 0.113 | 137 |
| qwen3-4b.gpt4o_F_s3 | run | 0.052 | -0.074 | 0.127 | 137 |
| qwen3-4b.gpt4o_F_s4 | run | 0.045 | -0.060 | 0.106 | 137 |
| qwen3-4b.gpt4o_F_s5 | run | 0.045 | -0.057 | 0.102 | 137 |

Dose-response inputs per teacher (dose_response.json):

| teacher | s_teacher | s_student_mean | s_student_sd | n_runs |
|---|---|---|---|---|
| claude46 | 0.049 | 0.031 | 0.002 | 5 |
| deepseek_v4 | 0.145 | 0.177 | 0.012 | 5 |
| gpt4o | 0.075 | 0.121 | 0.013 | 5 |

## E1a: training-label reproduction (e1_train_reproduction.csv)

| run_id | n_rows | answer_rate | n_targets | n_scored | n_missing | n_no_letter | accuracy | passed | sft_source |
|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_C_s1 | 4682 | 0.999 | 4682 | 4682 | 0 | 0 | 0.987 | nan | data/sft_paired/claude46_C_s1.jsonl |
| qwen3-4b.claude46_C_s2 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.988 | nan | data/sft_paired/claude46_C_s2.jsonl |
| qwen3-4b.claude46_C_s3 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.987 | nan | data/sft_paired/claude46_C_s3.jsonl |
| qwen3-4b.claude46_C_s4 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.984 | nan | data/sft_paired/claude46_C_s4.jsonl |
| qwen3-4b.claude46_C_s5 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.982 | nan | data/sft_paired/claude46_C_s5.jsonl |
| qwen3-4b.claude46_F_s1 | 4682 | 0.999 | 4682 | 4682 | 0 | 0 | 0.988 | nan | data/sft_paired/claude46_F_s1.jsonl |
| qwen3-4b.claude46_F_s2 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.987 | nan | data/sft_paired/claude46_F_s2.jsonl |
| qwen3-4b.claude46_F_s3 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.985 | nan | data/sft_paired/claude46_F_s3.jsonl |
| qwen3-4b.claude46_F_s4 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.983 | nan | data/sft_paired/claude46_F_s4.jsonl |
| qwen3-4b.claude46_F_s5 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.980 | nan | data/sft_paired/claude46_F_s5.jsonl |
| qwen3-4b.claude46_O_s1 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.987 | True | data/sft_paired/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s2 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.986 | True | data/sft_paired/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s3 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.986 | True | data/sft_paired/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s4 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.982 | True | data/sft_paired/claude46_O_s1.jsonl |
| qwen3-4b.claude46_O_s5 | 4682 | 1.000 | 4682 | 4682 | 0 | 0 | 0.981 | True | data/sft_paired/claude46_O_s1.jsonl |
| qwen3-4b.deepseek_v4_C_s1 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.995 | nan | data/sft_paired/deepseek_v4_C_s1.jsonl |
| qwen3-4b.deepseek_v4_C_s2 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.993 | nan | data/sft_paired/deepseek_v4_C_s2.jsonl |
| qwen3-4b.deepseek_v4_C_s3 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.992 | nan | data/sft_paired/deepseek_v4_C_s3.jsonl |
| qwen3-4b.deepseek_v4_C_s4 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.991 | nan | data/sft_paired/deepseek_v4_C_s4.jsonl |
| qwen3-4b.deepseek_v4_C_s5 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.993 | nan | data/sft_paired/deepseek_v4_C_s5.jsonl |
| qwen3-4b.deepseek_v4_F_s1 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.994 | nan | data/sft_paired/deepseek_v4_F_s1.jsonl |
| qwen3-4b.deepseek_v4_F_s2 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.994 | nan | data/sft_paired/deepseek_v4_F_s2.jsonl |
| qwen3-4b.deepseek_v4_F_s3 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.991 | nan | data/sft_paired/deepseek_v4_F_s3.jsonl |
| qwen3-4b.deepseek_v4_F_s4 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.992 | nan | data/sft_paired/deepseek_v4_F_s4.jsonl |
| qwen3-4b.deepseek_v4_F_s5 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.992 | nan | data/sft_paired/deepseek_v4_F_s5.jsonl |
| qwen3-4b.deepseek_v4_O_s1 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.994 | True | data/sft_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s2 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.994 | True | data/sft_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s3 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.990 | True | data/sft_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s4 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.993 | True | data/sft_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b.deepseek_v4_O_s5 | 4668 | 1.000 | 4668 | 4668 | 0 | 0 | 0.992 | True | data/sft_paired/deepseek_v4_O_s1.jsonl |
| qwen3-4b.gpt4o_C_s1 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.987 | nan | data/sft_paired/gpt4o_C_s1.jsonl |
| qwen3-4b.gpt4o_C_s2 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.989 | nan | data/sft_paired/gpt4o_C_s2.jsonl |
| qwen3-4b.gpt4o_C_s3 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.987 | nan | data/sft_paired/gpt4o_C_s3.jsonl |
| qwen3-4b.gpt4o_C_s4 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.988 | nan | data/sft_paired/gpt4o_C_s4.jsonl |
| qwen3-4b.gpt4o_C_s5 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.987 | nan | data/sft_paired/gpt4o_C_s5.jsonl |
| qwen3-4b.gpt4o_F_s1 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.986 | nan | data/sft_paired/gpt4o_F_s1.jsonl |
| qwen3-4b.gpt4o_F_s2 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.988 | nan | data/sft_paired/gpt4o_F_s2.jsonl |
| qwen3-4b.gpt4o_F_s3 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.988 | nan | data/sft_paired/gpt4o_F_s3.jsonl |
| qwen3-4b.gpt4o_F_s4 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.985 | nan | data/sft_paired/gpt4o_F_s4.jsonl |
| qwen3-4b.gpt4o_F_s5 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.987 | nan | data/sft_paired/gpt4o_F_s5.jsonl |
| qwen3-4b.gpt4o_O_s1 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.986 | True | data/sft_paired/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s2 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.986 | True | data/sft_paired/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s3 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.986 | True | data/sft_paired/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s4 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.984 | True | data/sft_paired/gpt4o_O_s1.jsonl |
| qwen3-4b.gpt4o_O_s5 | 5132 | 1.000 | 5132 | 5132 | 0 | 0 | 0.986 | True | data/sft_paired/gpt4o_O_s1.jsonl |

## E1b: contested training items, seed-pooled share siding with the own teacher (e1_contested.csv; family-bootstrap 95% CI)

| teacher | other | n_items | n_families | n_runs | n_pairs | share | ci_lo | ci_hi | passed |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | deepseek_v4 | 220 | 145 | 5 | 1100 | 0.936 | 0.906 | 0.962 | True |
| claude46 | gpt4o | 249 | 151 | 5 | 1245 | 0.917 | 0.886 | 0.945 | True |
| deepseek_v4 | claude46 | 220 | 145 | 5 | 1100 | 0.954 | 0.933 | 0.972 | True |
| deepseek_v4 | gpt4o | 163 | 106 | 5 | 815 | 0.914 | 0.878 | 0.945 | True |
| gpt4o | claude46 | 249 | 151 | 5 | 1245 | 0.908 | 0.874 | 0.938 | True |
| gpt4o | deepseek_v4 | 163 | 106 | 5 | 815 | 0.888 | 0.841 | 0.930 | True |

## E1 descriptive (no gate): per run agreement with every teacher; JSD is calibration-confounded (more extreme teachers are penalised more)

| run_id | answer_rate | order_gap_mean | n_families | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_C_s1 | 1.000 | 0.062 | 150 | 0.847 | 0.815 | 0.111 | 0.021 | 0.006 |
| qwen3-4b.claude46_C_s2 | 0.999 | 0.062 | 150 | 0.845 | 0.817 | 0.108 | 0.053 | 0.010 |
| qwen3-4b.claude46_C_s3 | 1.000 | 0.074 | 150 | 0.847 | 0.829 | 0.111 | 0.060 | 0.013 |
| qwen3-4b.claude46_C_s4 | 1.000 | 0.072 | 150 | 0.842 | 0.819 | 0.111 | 0.041 | 0.009 |
| qwen3-4b.claude46_C_s5 | 0.999 | 0.069 | 149 | 0.840 | 0.801 | 0.114 | 0.029 | 0.008 |
| qwen3-4b.claude46_F_s1 | 1.000 | 0.057 | 150 | 0.845 | 0.814 | 0.116 | 0.042 | 0.010 |
| qwen3-4b.claude46_F_s2 | 1.000 | 0.065 | 150 | 0.847 | 0.807 | 0.114 | 0.044 | 0.012 |
| qwen3-4b.claude46_F_s3 | 1.000 | 0.067 | 150 | 0.838 | 0.805 | 0.117 | 0.042 | 0.010 |
| qwen3-4b.claude46_F_s4 | 1.000 | 0.064 | 150 | 0.853 | 0.819 | 0.115 | 0.040 | 0.011 |
| qwen3-4b.claude46_F_s5 | 1.000 | 0.059 | 150 | 0.837 | 0.810 | 0.117 | 0.028 | 0.012 |
| qwen3-4b.claude46_O_s1 | 1.000 | 0.055 | 150 | 0.851 | 0.822 | 0.116 | 0.048 | 0.009 |
| qwen3-4b.claude46_O_s2 | 1.000 | 0.062 | 150 | 0.835 | 0.805 | 0.116 | 0.049 | 0.010 |
| qwen3-4b.claude46_O_s3 | 1.000 | 0.061 | 150 | 0.835 | 0.829 | 0.118 | 0.053 | 0.010 |
| qwen3-4b.claude46_O_s4 | 1.000 | 0.062 | 150 | 0.858 | 0.828 | 0.114 | 0.041 | 0.011 |
| qwen3-4b.claude46_O_s5 | 0.999 | 0.053 | 149 | 0.847 | 0.820 | 0.113 | 0.039 | 0.011 |
| qwen3-4b.deepseek_v4_C_s1 | 1.000 | 0.054 | 150 | 0.840 | 0.819 | 0.083 | 0.118 | 0.052 |
| qwen3-4b.deepseek_v4_C_s2 | 0.997 | 0.053 | 148 | 0.836 | 0.818 | 0.081 | 0.115 | 0.053 |
| qwen3-4b.deepseek_v4_C_s3 | 1.000 | 0.057 | 150 | 0.844 | 0.826 | 0.081 | 0.084 | 0.039 |
| qwen3-4b.deepseek_v4_C_s4 | 1.000 | 0.060 | 150 | 0.854 | 0.833 | 0.073 | 0.109 | 0.049 |
| qwen3-4b.deepseek_v4_C_s5 | 0.999 | 0.062 | 150 | 0.837 | 0.829 | 0.081 | 0.088 | 0.045 |
| qwen3-4b.deepseek_v4_F_s1 | 1.000 | 0.052 | 150 | 0.839 | 0.821 | 0.084 | 0.106 | 0.059 |
| qwen3-4b.deepseek_v4_F_s2 | 1.000 | 0.061 | 150 | 0.842 | 0.824 | 0.084 | 0.119 | 0.055 |
| qwen3-4b.deepseek_v4_F_s3 | 0.999 | 0.050 | 150 | 0.849 | 0.836 | 0.082 | 0.114 | 0.054 |
| qwen3-4b.deepseek_v4_F_s4 | 0.999 | 0.058 | 150 | 0.845 | 0.831 | 0.082 | 0.101 | 0.051 |
| qwen3-4b.deepseek_v4_F_s5 | 1.000 | 0.053 | 150 | 0.837 | 0.833 | 0.086 | 0.091 | 0.043 |
| qwen3-4b.deepseek_v4_O_s1 | 1.000 | 0.053 | 150 | 0.840 | 0.826 | 0.084 | 0.109 | 0.053 |
| qwen3-4b.deepseek_v4_O_s2 | 1.000 | 0.057 | 150 | 0.844 | 0.834 | 0.085 | 0.122 | 0.057 |
| qwen3-4b.deepseek_v4_O_s3 | 1.000 | 0.054 | 150 | 0.852 | 0.836 | 0.081 | 0.086 | 0.049 |
| qwen3-4b.deepseek_v4_O_s4 | 0.999 | 0.055 | 149 | 0.847 | 0.832 | 0.082 | 0.111 | 0.063 |
| qwen3-4b.deepseek_v4_O_s5 | 1.000 | 0.056 | 150 | 0.840 | 0.833 | 0.083 | 0.093 | 0.049 |
| qwen3-4b.gpt4o_C_s1 | 1.000 | 0.051 | 150 | 0.859 | 0.844 | 0.088 | 0.068 | 0.024 |
| qwen3-4b.gpt4o_C_s2 | 1.000 | 0.063 | 150 | 0.861 | 0.851 | 0.084 | 0.061 | 0.021 |
| qwen3-4b.gpt4o_C_s3 | 1.000 | 0.049 | 150 | 0.848 | 0.840 | 0.096 | 0.078 | 0.023 |
| qwen3-4b.gpt4o_C_s4 | 1.000 | 0.056 | 150 | 0.861 | 0.854 | 0.093 | 0.068 | 0.025 |
| qwen3-4b.gpt4o_C_s5 | 1.000 | 0.055 | 150 | 0.857 | 0.854 | 0.090 | 0.057 | 0.023 |
| qwen3-4b.gpt4o_F_s1 | 1.000 | 0.054 | 150 | 0.864 | 0.853 | 0.087 | 0.072 | 0.030 |
| qwen3-4b.gpt4o_F_s2 | 1.000 | 0.050 | 150 | 0.848 | 0.842 | 0.099 | 0.070 | 0.025 |
| qwen3-4b.gpt4o_F_s3 | 1.000 | 0.055 | 150 | 0.861 | 0.861 | 0.094 | 0.074 | 0.030 |
| qwen3-4b.gpt4o_F_s4 | 1.000 | 0.055 | 150 | 0.855 | 0.852 | 0.096 | 0.058 | 0.022 |
| qwen3-4b.gpt4o_F_s5 | 1.000 | 0.051 | 150 | 0.852 | 0.857 | 0.095 | 0.063 | 0.023 |
| qwen3-4b.gpt4o_O_s1 | 1.000 | 0.053 | 150 | 0.857 | 0.852 | 0.089 | 0.089 | 0.036 |
| qwen3-4b.gpt4o_O_s2 | 1.000 | 0.050 | 150 | 0.843 | 0.840 | 0.101 | 0.078 | 0.027 |
| qwen3-4b.gpt4o_O_s3 | 1.000 | 0.046 | 150 | 0.857 | 0.850 | 0.099 | 0.070 | 0.032 |
| qwen3-4b.gpt4o_O_s4 | 1.000 | 0.047 | 150 | 0.855 | 0.862 | 0.091 | 0.058 | 0.025 |
| qwen3-4b.gpt4o_O_s5 | 1.000 | 0.052 | 150 | 0.852 | 0.861 | 0.093 | 0.068 | 0.027 |

| run_id | agree__claude46 | agree__deepseek_v4 | agree__gpt4o | jsd__claude46 | jsd__deepseek_v4 | jsd__gpt4o |
|---|---|---|---|---|---|---|
| qwen3-4b.claude46_C_s1 | 0.847 | 0.790 | 0.815 | 0.111 | 0.106 | 0.111 |
| qwen3-4b.claude46_C_s2 | 0.845 | 0.792 | 0.817 | 0.108 | 0.097 | 0.105 |
| qwen3-4b.claude46_C_s3 | 0.847 | 0.805 | 0.829 | 0.111 | 0.099 | 0.104 |
| qwen3-4b.claude46_C_s4 | 0.842 | 0.793 | 0.819 | 0.111 | 0.098 | 0.107 |
| qwen3-4b.claude46_C_s5 | 0.840 | 0.791 | 0.801 | 0.114 | 0.104 | 0.112 |
| qwen3-4b.claude46_F_s1 | 0.845 | 0.795 | 0.814 | 0.116 | 0.112 | 0.115 |
| qwen3-4b.claude46_F_s2 | 0.847 | 0.795 | 0.807 | 0.114 | 0.105 | 0.115 |
| qwen3-4b.claude46_F_s3 | 0.838 | 0.792 | 0.805 | 0.117 | 0.103 | 0.115 |
| qwen3-4b.claude46_F_s4 | 0.853 | 0.795 | 0.819 | 0.115 | 0.107 | 0.114 |
| qwen3-4b.claude46_F_s5 | 0.837 | 0.797 | 0.810 | 0.117 | 0.111 | 0.119 |
| qwen3-4b.claude46_O_s1 | 0.851 | 0.800 | 0.822 | 0.116 | 0.108 | 0.113 |
| qwen3-4b.claude46_O_s2 | 0.835 | 0.788 | 0.805 | 0.116 | 0.105 | 0.114 |
| qwen3-4b.claude46_O_s3 | 0.835 | 0.818 | 0.829 | 0.118 | 0.099 | 0.108 |
| qwen3-4b.claude46_O_s4 | 0.858 | 0.803 | 0.828 | 0.114 | 0.105 | 0.114 |
| qwen3-4b.claude46_O_s5 | 0.847 | 0.803 | 0.820 | 0.113 | 0.109 | 0.111 |
| qwen3-4b.deepseek_v4_C_s1 | 0.813 | 0.840 | 0.819 | 0.153 | 0.083 | 0.122 |
| qwen3-4b.deepseek_v4_C_s2 | 0.812 | 0.836 | 0.818 | 0.145 | 0.081 | 0.115 |
| qwen3-4b.deepseek_v4_C_s3 | 0.813 | 0.844 | 0.826 | 0.149 | 0.081 | 0.120 |
| qwen3-4b.deepseek_v4_C_s4 | 0.810 | 0.854 | 0.833 | 0.143 | 0.073 | 0.109 |
| qwen3-4b.deepseek_v4_C_s5 | 0.826 | 0.837 | 0.829 | 0.137 | 0.081 | 0.115 |
| qwen3-4b.deepseek_v4_F_s1 | 0.799 | 0.839 | 0.821 | 0.157 | 0.084 | 0.115 |
| qwen3-4b.deepseek_v4_F_s2 | 0.819 | 0.842 | 0.824 | 0.146 | 0.084 | 0.119 |
| qwen3-4b.deepseek_v4_F_s3 | 0.817 | 0.849 | 0.836 | 0.150 | 0.082 | 0.112 |
| qwen3-4b.deepseek_v4_F_s4 | 0.803 | 0.845 | 0.831 | 0.153 | 0.082 | 0.110 |
| qwen3-4b.deepseek_v4_F_s5 | 0.808 | 0.837 | 0.833 | 0.151 | 0.086 | 0.119 |
| qwen3-4b.deepseek_v4_O_s1 | 0.801 | 0.840 | 0.826 | 0.155 | 0.084 | 0.116 |
| qwen3-4b.deepseek_v4_O_s2 | 0.819 | 0.844 | 0.834 | 0.144 | 0.085 | 0.113 |
| qwen3-4b.deepseek_v4_O_s3 | 0.819 | 0.852 | 0.836 | 0.147 | 0.081 | 0.112 |
| qwen3-4b.deepseek_v4_O_s4 | 0.822 | 0.847 | 0.832 | 0.147 | 0.082 | 0.109 |
| qwen3-4b.deepseek_v4_O_s5 | 0.821 | 0.840 | 0.833 | 0.150 | 0.083 | 0.115 |
| qwen3-4b.gpt4o_C_s1 | 0.831 | 0.844 | 0.859 | 0.124 | 0.081 | 0.088 |
| qwen3-4b.gpt4o_C_s2 | 0.851 | 0.847 | 0.861 | 0.115 | 0.082 | 0.084 |
| qwen3-4b.gpt4o_C_s3 | 0.840 | 0.835 | 0.848 | 0.121 | 0.083 | 0.096 |
| qwen3-4b.gpt4o_C_s4 | 0.840 | 0.854 | 0.861 | 0.122 | 0.082 | 0.093 |
| qwen3-4b.gpt4o_C_s5 | 0.844 | 0.854 | 0.857 | 0.124 | 0.082 | 0.090 |
| qwen3-4b.gpt4o_F_s1 | 0.853 | 0.850 | 0.864 | 0.118 | 0.081 | 0.087 |
| qwen3-4b.gpt4o_F_s2 | 0.842 | 0.837 | 0.848 | 0.123 | 0.086 | 0.099 |
| qwen3-4b.gpt4o_F_s3 | 0.837 | 0.861 | 0.861 | 0.129 | 0.084 | 0.094 |
| qwen3-4b.gpt4o_F_s4 | 0.840 | 0.852 | 0.855 | 0.127 | 0.082 | 0.096 |
| qwen3-4b.gpt4o_F_s5 | 0.840 | 0.857 | 0.852 | 0.129 | 0.086 | 0.095 |
| qwen3-4b.gpt4o_O_s1 | 0.837 | 0.852 | 0.857 | 0.125 | 0.078 | 0.089 |
| qwen3-4b.gpt4o_O_s2 | 0.840 | 0.835 | 0.843 | 0.127 | 0.087 | 0.101 |
| qwen3-4b.gpt4o_O_s3 | 0.833 | 0.850 | 0.857 | 0.135 | 0.087 | 0.099 |
| qwen3-4b.gpt4o_O_s4 | 0.845 | 0.862 | 0.855 | 0.124 | 0.080 | 0.091 |
| qwen3-4b.gpt4o_O_s5 | 0.840 | 0.861 | 0.852 | 0.126 | 0.081 | 0.093 |

### Seed means

| teacher | version | n_seeds | answer_rate | agree_own | agree_other_max | jsd_own | flip_rate | mean_jsd |
|---|---|---|---|---|---|---|---|---|
| claude46 | C | 5 | 1.000 | 0.844 | 0.816 | 0.111 | 0.041 | 0.009 |
| claude46 | F | 5 | 1.000 | 0.844 | 0.811 | 0.116 | 0.039 | 0.011 |
| claude46 | O | 5 | 1.000 | 0.845 | 0.821 | 0.115 | 0.046 | 0.010 |
| deepseek_v4 | C | 5 | 0.999 | 0.842 | 0.825 | 0.080 | 0.103 | 0.048 |
| deepseek_v4 | F | 5 | 1.000 | 0.842 | 0.829 | 0.084 | 0.106 | 0.053 |
| deepseek_v4 | O | 5 | 1.000 | 0.845 | 0.832 | 0.083 | 0.104 | 0.054 |
| gpt4o | C | 5 | 1.000 | 0.857 | 0.848 | 0.090 | 0.066 | 0.023 |
| gpt4o | F | 5 | 1.000 | 0.856 | 0.853 | 0.094 | 0.068 | 0.026 |
| gpt4o | O | 5 | 1.000 | 0.853 | 0.853 | 0.095 | 0.072 | 0.029 |

## Per-run inheritance (descriptive): deltaRhoPartial given r_0 = absent (inheritance_partial.csv) and uncontrolled delta_rho (inheritance.csv)

pending: no base run (version B) with a prior profile; evaluate S_0 on this split first

Uncontrolled delta_rho per run (inheritance.csv):

| run_id | rho_own | ceiling | rho_other_max | other_argmax | delta_rho | p_perm | ci_lo | ci_hi |
|---|---|---|---|---|---|---|---|---|
| qwen3-4b.claude46_C_s1 | 0.157 | 0.744 | 0.178 | gpt4o | -0.021 | 0.397 | -0.146 | 0.058 |
| qwen3-4b.claude46_C_s2 | 0.169 | 0.744 | 0.270 | deepseek_v4 | -0.101 | 0.785 | -0.266 | 0.022 |
| qwen3-4b.claude46_C_s3 | 0.121 | 0.744 | 0.306 | gpt4o | -0.186 | 0.986 | -0.399 | -0.035 |
| qwen3-4b.claude46_C_s4 | 0.184 | 0.744 | 0.261 | deepseek_v4 | -0.077 | 0.537 | -0.217 | 0.011 |
| qwen3-4b.claude46_C_s5 | 0.135 | 0.744 | 0.256 | deepseek_v4 | -0.121 | 0.872 | -0.316 | 0.006 |
| qwen3-4b.claude46_F_s1 | 0.210 | 0.744 | 0.239 | deepseek_v4 | -0.029 | 0.286 | -0.217 | 0.122 |
| qwen3-4b.claude46_F_s2 | 0.171 | 0.744 | 0.313 | deepseek_v4 | -0.142 | 0.929 | -0.326 | 0.017 |
| qwen3-4b.claude46_F_s3 | 0.169 | 0.744 | 0.279 | deepseek_v4 | -0.110 | 0.812 | -0.315 | 0.039 |
| qwen3-4b.claude46_F_s4 | 0.197 | 0.744 | 0.285 | deepseek_v4 | -0.089 | 0.669 | -0.312 | 0.116 |
| qwen3-4b.claude46_F_s5 | 0.208 | 0.744 | 0.299 | deepseek_v4 | -0.090 | 0.740 | -0.290 | 0.122 |
| qwen3-4b.claude46_O_s1 | 0.192 | 0.744 | 0.264 | deepseek_v4 | -0.072 | 0.556 | -0.228 | 0.075 |
| qwen3-4b.claude46_O_s2 | 0.157 | 0.744 | 0.324 | deepseek_v4 | -0.167 | 0.948 | -0.336 | -0.003 |
| qwen3-4b.claude46_O_s3 | 0.229 | 0.744 | 0.351 | deepseek_v4 | -0.122 | 0.821 | -0.311 | 0.047 |
| qwen3-4b.claude46_O_s4 | 0.190 | 0.744 | 0.279 | deepseek_v4 | -0.088 | 0.614 | -0.273 | 0.089 |
| qwen3-4b.claude46_O_s5 | 0.228 | 0.744 | 0.298 | deepseek_v4 | -0.070 | 0.559 | -0.264 | 0.118 |
| qwen3-4b.deepseek_v4_C_s1 | 0.484 | 0.825 | 0.362 | gpt4o | 0.122 | 0.252 | -0.027 | 0.273 |
| qwen3-4b.deepseek_v4_C_s2 | 0.498 | 0.825 | 0.335 | gpt4o | 0.162 | 0.066 | 0.027 | 0.289 |
| qwen3-4b.deepseek_v4_C_s3 | 0.485 | 0.825 | 0.272 | gpt4o | 0.213 | 0.004 | 0.080 | 0.334 |
| qwen3-4b.deepseek_v4_C_s4 | 0.506 | 0.825 | 0.358 | gpt4o | 0.148 | 0.137 | 0.009 | 0.283 |
| qwen3-4b.deepseek_v4_C_s5 | 0.486 | 0.825 | 0.322 | gpt4o | 0.164 | 0.061 | 0.022 | 0.288 |
| qwen3-4b.deepseek_v4_F_s1 | 0.488 | 0.825 | 0.361 | gpt4o | 0.128 | 0.187 | -0.018 | 0.280 |
| qwen3-4b.deepseek_v4_F_s2 | 0.506 | 0.825 | 0.332 | gpt4o | 0.173 | 0.034 | 0.043 | 0.293 |
| qwen3-4b.deepseek_v4_F_s3 | 0.523 | 0.825 | 0.318 | gpt4o | 0.205 | 0.008 | 0.046 | 0.347 |
| qwen3-4b.deepseek_v4_F_s4 | 0.451 | 0.825 | 0.373 | gpt4o | 0.078 | 0.542 | -0.056 | 0.218 |
| qwen3-4b.deepseek_v4_F_s5 | 0.453 | 0.825 | 0.370 | gpt4o | 0.083 | 0.463 | -0.062 | 0.235 |
| qwen3-4b.deepseek_v4_O_s1 | 0.479 | 0.825 | 0.350 | gpt4o | 0.129 | 0.170 | -0.010 | 0.266 |
| qwen3-4b.deepseek_v4_O_s2 | 0.494 | 0.825 | 0.333 | gpt4o | 0.160 | 0.064 | 0.026 | 0.287 |
| qwen3-4b.deepseek_v4_O_s3 | 0.516 | 0.825 | 0.326 | gpt4o | 0.190 | 0.016 | 0.051 | 0.317 |
| qwen3-4b.deepseek_v4_O_s4 | 0.485 | 0.825 | 0.330 | gpt4o | 0.155 | 0.068 | 0.028 | 0.276 |
| qwen3-4b.deepseek_v4_O_s5 | 0.483 | 0.825 | 0.338 | gpt4o | 0.145 | 0.098 | 0.003 | 0.279 |
| qwen3-4b.gpt4o_C_s1 | 0.384 | 0.898 | 0.423 | deepseek_v4 | -0.039 | 0.167 | -0.188 | 0.118 |
| qwen3-4b.gpt4o_C_s2 | 0.408 | 0.898 | 0.410 | deepseek_v4 | -0.002 | 0.048 | -0.155 | 0.142 |
| qwen3-4b.gpt4o_C_s3 | 0.342 | 0.898 | 0.434 | deepseek_v4 | -0.093 | 0.475 | -0.231 | 0.047 |
| qwen3-4b.gpt4o_C_s4 | 0.313 | 0.898 | 0.415 | deepseek_v4 | -0.102 | 0.613 | -0.237 | 0.037 |
| qwen3-4b.gpt4o_C_s5 | 0.367 | 0.898 | 0.448 | deepseek_v4 | -0.081 | 0.421 | -0.224 | 0.062 |
| qwen3-4b.gpt4o_F_s1 | 0.405 | 0.898 | 0.457 | deepseek_v4 | -0.052 | 0.204 | -0.206 | 0.104 |
| qwen3-4b.gpt4o_F_s2 | 0.315 | 0.898 | 0.433 | deepseek_v4 | -0.118 | 0.710 | -0.270 | 0.035 |
| qwen3-4b.gpt4o_F_s3 | 0.382 | 0.898 | 0.455 | deepseek_v4 | -0.073 | 0.349 | -0.212 | 0.064 |
| qwen3-4b.gpt4o_F_s4 | 0.327 | 0.898 | 0.436 | deepseek_v4 | -0.108 | 0.654 | -0.236 | 0.032 |
| qwen3-4b.gpt4o_F_s5 | 0.328 | 0.898 | 0.444 | deepseek_v4 | -0.116 | 0.719 | -0.243 | 0.023 |
| qwen3-4b.gpt4o_O_s1 | 0.382 | 0.898 | 0.467 | deepseek_v4 | -0.085 | 0.448 | -0.235 | 0.068 |
| qwen3-4b.gpt4o_O_s2 | 0.332 | 0.898 | 0.445 | deepseek_v4 | -0.113 | 0.673 | -0.265 | 0.035 |
| qwen3-4b.gpt4o_O_s3 | 0.359 | 0.898 | 0.432 | deepseek_v4 | -0.072 | 0.361 | -0.221 | 0.080 |
| qwen3-4b.gpt4o_O_s4 | 0.354 | 0.898 | 0.418 | deepseek_v4 | -0.064 | 0.329 | -0.215 | 0.088 |
| qwen3-4b.gpt4o_O_s5 | 0.346 | 0.898 | 0.470 | deepseek_v4 | -0.124 | 0.792 | -0.251 | 0.016 |

## Pre-revision rule versions (disclosure; none of these is the verdict)

### E1 (old): every O seed agree_own > agree_other_max

- claude46: 5/5 seeds pass -> ok (old rule, not the verdict)
- deepseek_v4: 5/5 seeds pass -> ok (old rule, not the verdict)
- gpt4o: 3/5 seeds pass -> partial (old rule, not the verdict)

### E2 run-level permutations P1 / P2 (frozen in c2c9d96, withdrawn the same day: pseudo-replicated, kept as numbers only)

- P1 mean deltaRhoPartial nan vs run-reassignment null mean nan sd nan, p nan (none, 0 assignments) -> not a test; teacher-level exact p nan
- P2 slope 1.367, run-reassignment p 1.3e-06 (exact, 756756 assignments) -> not a test; teacher-level exact p 0.167

### E2 secondary D without the decomposition guard (version 4 of the rule, superseded before the freeze commit)

- D nan [nan, nan] p nan alone would read fail / pending; the frozen rule (version 5) also needs D_specific nan [nan, nan] above 0 -> pending (no base readout for the covariate r_0, or fewer than 2 teachers with O runs)

## Seed-noise null: |metric(seed a) - metric(seed b)| within (teacher, version)

| metric | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| agree_own | claude46 | C | 10 | 0.004 | 0.003 | 0.007 |
| agree_own | claude46 | F | 10 | 0.008 | 0.005 | 0.015 |
| agree_own | claude46 | O | 10 | 0.012 | 0.008 | 0.023 |
| agree_own | deepseek_v4 | C | 10 | 0.008 | 0.006 | 0.017 |
| agree_own | deepseek_v4 | F | 10 | 0.006 | 0.003 | 0.011 |
| agree_own | deepseek_v4 | O | 10 | 0.006 | 0.004 | 0.012 |
| agree_own | gpt4o | C | 10 | 0.006 | 0.005 | 0.012 |
| agree_own | gpt4o | F | 10 | 0.008 | 0.004 | 0.014 |
| agree_own | gpt4o | O | 10 | 0.007 | 0.005 | 0.014 |
| agree_own | all | all | 90 | 0.007 | 0.005 | 0.016 |
| jsd_own | claude46 | C | 10 | 0.002 | 0.002 | 0.004 |
| jsd_own | claude46 | F | 10 | 0.002 | 9.8e-04 | 0.003 |
| jsd_own | claude46 | O | 10 | 0.002 | 0.001 | 0.004 |
| jsd_own | deepseek_v4 | C | 10 | 0.004 | 0.004 | 0.009 |
| jsd_own | deepseek_v4 | F | 10 | 0.002 | 0.001 | 0.004 |
| jsd_own | deepseek_v4 | O | 10 | 0.002 | 0.001 | 0.004 |
| jsd_own | gpt4o | C | 10 | 0.006 | 0.003 | 0.010 |
| jsd_own | gpt4o | F | 10 | 0.005 | 0.003 | 0.010 |
| jsd_own | gpt4o | O | 10 | 0.006 | 0.004 | 0.011 |
| jsd_own | all | all | 90 | 0.003 | 0.003 | 0.009 |
| flip_rate | claude46 | C | 10 | 0.020 | 0.011 | 0.036 |
| flip_rate | claude46 | F | 10 | 0.007 | 0.006 | 0.016 |
| flip_rate | claude46 | O | 10 | 0.007 | 0.004 | 0.013 |
| flip_rate | deepseek_v4 | C | 10 | 0.019 | 0.012 | 0.032 |
| flip_rate | deepseek_v4 | F | 10 | 0.014 | 0.008 | 0.026 |
| flip_rate | deepseek_v4 | O | 10 | 0.018 | 0.010 | 0.033 |
| flip_rate | gpt4o | C | 10 | 0.010 | 0.006 | 0.019 |
| flip_rate | gpt4o | F | 10 | 0.008 | 0.005 | 0.016 |
| flip_rate | gpt4o | O | 10 | 0.014 | 0.008 | 0.027 |
| flip_rate | all | all | 90 | 0.013 | 0.009 | 0.031 |
| mean_jsd | claude46 | C | 10 | 0.003 | 0.002 | 0.006 |
| mean_jsd | claude46 | F | 10 | 0.001 | 6.1e-04 | 0.002 |
| mean_jsd | claude46 | O | 10 | 7.7e-04 | 4.8e-04 | 0.002 |
| mean_jsd | deepseek_v4 | C | 10 | 0.007 | 0.004 | 0.014 |
| mean_jsd | deepseek_v4 | F | 10 | 0.007 | 0.005 | 0.014 |
| mean_jsd | deepseek_v4 | O | 10 | 0.007 | 0.004 | 0.014 |
| mean_jsd | gpt4o | C | 10 | 0.002 | 0.001 | 0.003 |
| mean_jsd | gpt4o | F | 10 | 0.005 | 0.003 | 0.008 |
| mean_jsd | gpt4o | O | 10 | 0.005 | 0.004 | 0.010 |
| mean_jsd | all | all | 90 | 0.004 | 0.004 | 0.013 |
| delta_rho | claude46 | C | 10 | 0.074 | 0.043 | 0.139 |
| delta_rho | claude46 | F | 10 | 0.049 | 0.032 | 0.098 |
| delta_rho | claude46 | O | 10 | 0.048 | 0.033 | 0.095 |
| delta_rho | deepseek_v4 | C | 10 | 0.040 | 0.027 | 0.080 |
| delta_rho | deepseek_v4 | F | 10 | 0.069 | 0.040 | 0.125 |
| delta_rho | deepseek_v4 | O | 10 | 0.027 | 0.017 | 0.054 |
| delta_rho | gpt4o | C | 10 | 0.050 | 0.032 | 0.095 |
| delta_rho | gpt4o | F | 10 | 0.035 | 0.024 | 0.065 |
| delta_rho | gpt4o | O | 10 | 0.032 | 0.019 | 0.056 |
| delta_rho | all | all | 90 | 0.047 | 0.033 | 0.104 |

Notes: R students are random-label controls; their consistency is reported only next to agreement / JSD. 
Teachers' own cross-framing consistency is in consistency.csv (rows with a teacher name instead of a run id). 
The base prior profile r_0 bypasses the 0.9 answer-mass gate ONLY as a covariate and for the S_0 control row; S_0's answers are still read out with the gate.