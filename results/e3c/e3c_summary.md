# E3c gap 分析（test，student qwen3-4b-e2c-paired，variants T1, T3, T5, T6；E3c gap rule pre-specified (tasks/e3c_plan.md; statistics = the frozen E3 rules of tasks/e3_plan.md §2-3) before any E3c F / C run existed; frozen at commit 45f3d30 (tasks/hpc_log.md)；auto-generated）

**gap F - O：inconclusive**（1/3 过 q95，0/3 过 TOST，方向 -）；**gap C - O：inconclusive**（1/3 过 q95，0/3 过 TOST，方向 -）。

问题：contested-set 示范的文风改写（O → F / C）是否改变学生对**自己** teacher 判断的继承量。量 = E2c 的 gap（tasks/e2c_plan.md §6）按 family 计：每 run 每 family f 的 d_f = agree_own_f − agree_other_f，agree = 该 family 内有定义多数的 (family, variant) cell 上学生多数行动与 teacher 多数行动相同的份额（symmetrized，p_sym = 0.5 的 cell 不计，`e3_metrics.family_compare`）；run 值 = mean_f d_f，同 teacher 的所有 run 共用一个 family 集（对每个 run 都完整且 gap 有定义的 family），null、水平与配对统计量在同一组 family 上。参照 other teacher 按 teacher 固定：与该 teacher 的 O 学生 run 级 agreement（`e1_metrics.teacher_agreement`，cell 加权）seed 均值最高的其他 teacher（并列取字母序最前），O / F / C 共用，见下表。

规则（docs/03 E3 行原文：效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；tasks/e3_plan.md §2–3 的冻结统计，`e3_metrics.paired_delta` / `seed_pair_null` / `e3_verdict`）：每 teacher 统计量 = 5 个 seed 配对差 mean_f d_f(S_T,V,s) − mean_f d_f(S_T,O,s) 的均值，family bootstrap 95% CI（B = 10000，seed 0，同 teacher 各 seed 联动重抽）；null = 同 teacher 两个 O seed 的 mean_f d_f 之差（带符号，C(n_O, 2) 对，跨 teacher 合并，n = 30），尺度匹配到 seed 均值：SD_stat = sqrt(mean(d²) / n_seeds)，q95 = t(0.975, df = Σ(n_O − 1) = 12) × SD_stat；teacher 过 ⇔ |stat| > q95；effect ⇔ ≥ 2/3 的 3 个 teacher 过且同号；no effect ⇔ ≥ 2/3 teacher 过 TOST（CI 与点估计落在 ± 1 SD_stat 内）；否则 inconclusive；无配对 run 或 teacher < 3 → pending。单对 q95（`null_q95_single`、`n_pass_single`）只作敏感性列。假设：seed 噪声近似正态、跨 seed 独立（同 seed 的 F / O 对共享初始化与数据顺序，null 偏保守）。

## 判定（e3c_gap_verdicts.csv；confirmatory）

| metric | teachers: stat [CI] (effect in null sd, p, Holm, TOST) * = exceeds q95 | null q95 of the stat (single-pair q95; n) | pass | TOST pass | direction | verdict |
|---|---|---|---|---|---|---|
| gap F - O | claude46 -0.009 [-0.025, 0.005] (-2.571 null sd, p 0.024, Holm 0.073, TOST False)*; deepseek_v4 0.003 [-0.003, 0.008] (0.772 null sd, p 0.455, Holm 0.455, TOST False); gpt4o 0.006 [-6.9e-04, 0.014] (1.641 null sd, p 0.127, Holm 0.253, TOST False) | 0.008 (0.015; 30) | 1/3 | 0/3 | - | **inconclusive** |
| gap C - O | claude46 -0.009 [-0.025, 0.005] (-2.635 null sd, p 0.022, Holm 0.065, TOST False)*; deepseek_v4 0.004 [-0.006, 0.013] (1.062 null sd, p 0.309, Holm 0.309, TOST False); gpt4o -0.006 [-0.014, 0.002] (-1.738 null sd, p 0.108, Holm 0.216, TOST False) | 0.008 (0.015; 30) | 1/3 | 0/3 | - | **inconclusive** |

每 teacher 的统计量（e3c_gap_verdict_teachers.csv）：

| metric | teacher | n_seeds | stat | ci_lo | ci_hi | null_sd | q95 | effect_sd | exceeds_q95 | exceeds_q95_single | p_null | p_holm | tost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap F - O | claude46 | 5 | -0.009 | -0.025 | 0.005 | 0.004 | 0.008 | -2.571 | True | False | 0.024 | 0.073 | False |
| gap F - O | deepseek_v4 | 5 | 0.003 | -0.003 | 0.008 | 0.004 | 0.008 | 0.772 | False | False | 0.455 | 0.455 | False |
| gap F - O | gpt4o | 5 | 0.006 | -6.9e-04 | 0.014 | 0.004 | 0.008 | 1.641 | False | False | 0.127 | 0.253 | False |
| gap C - O | claude46 | 5 | -0.009 | -0.025 | 0.005 | 0.004 | 0.008 | -2.635 | True | False | 0.022 | 0.065 | False |
| gap C - O | deepseek_v4 | 5 | 0.004 | -0.006 | 0.013 | 0.004 | 0.008 | 1.062 | False | False | 0.309 | 0.309 | False |
| gap C - O | gpt4o | 5 | -0.006 | -0.014 | 0.002 | 0.004 | 0.008 | -1.738 | False | False | 0.108 | 0.216 | False |

## 每 (teacher, version) 的水平与配对差（e3c_gap_by_teacher.csv；agree_own / agree_other / gap = family 单位的 seed 均值，CI = family bootstrap；diff = 与 O 按 seed 配对的差，e3c_gap_by_seed.csv 为每 seed）

| teacher | version | n_seeds | n_families | agree_own [CI] | agree_other [CI] | gap [CI] | n_pairs | n_families_paired | diff vs O [CI] | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | O | 5 | 295 | 0.845 [0.813, 0.875] | 0.833 [0.801, 0.865] | 0.012 [-0.012, 0.036] |  |  |  |  |
| claude46 | F | 5 | 295 | 0.839 [0.805, 0.871] | 0.837 [0.805, 0.869] | 0.002 [-0.023, 0.028] | 5 | 295 | -0.009 [-0.025, 0.005] | - |
| claude46 | C | 5 | 295 | 0.838 [0.803, 0.871] | 0.836 [0.803, 0.867] | 0.002 [-0.023, 0.028] | 5 | 295 | -0.009 [-0.025, 0.005] | - |
| deepseek_v4 | O | 5 | 291 | 0.787 [0.757, 0.815] | 0.754 [0.721, 0.785] | 0.033 [0.015, 0.052] |  |  |  |  |
| deepseek_v4 | F | 5 | 291 | 0.788 [0.759, 0.816] | 0.752 [0.719, 0.784] | 0.036 [0.018, 0.056] | 5 | 291 | 0.003 [-0.003, 0.008] | + |
| deepseek_v4 | C | 5 | 291 | 0.786 [0.756, 0.815] | 0.749 [0.715, 0.781] | 0.037 [0.017, 0.058] | 5 | 291 | 0.004 [-0.006, 0.013] | + |
| gpt4o | O | 5 | 291 | 0.811 [0.777, 0.844] | 0.813 [0.779, 0.845] | -0.002 [-0.021, 0.017] |  |  |  |  |
| gpt4o | F | 5 | 291 | 0.814 [0.782, 0.846] | 0.810 [0.778, 0.842] | 0.004 [-0.014, 0.022] | 5 | 291 | 0.006 [-6.9e-04, 0.014] | + |
| gpt4o | C | 5 | 291 | 0.806 [0.772, 0.838] | 0.814 [0.782, 0.844] | -0.008 [-0.028, 0.011] | 5 | 291 | -0.006 [-0.014, 0.002] | - |

## 参照 other teacher（e3c_reference_other.csv；由该 teacher 的 O 学生的 cell 加权 run 级 agreement 的 seed 均值选出，并列取字母序最前）

| teacher | reference_other | n_O_runs | agree_ref | tie | candidates | agree__gpt4o | agree__claude46 | agree__deepseek_v4 |
|---|---|---|---|---|---|---|---|---|
| gpt4o | deepseek_v4 | 5 | 0.807 | False | deepseek_v4=0.806833;claude46=0.792763 | 0.809 | 0.793 | 0.807 |
| claude46 | deepseek_v4 | 5 | 0.831 | False | deepseek_v4=0.830667;gpt4o=0.820439 | 0.820 | 0.853 | 0.831 |
| deepseek_v4 | gpt4o | 5 | 0.750 | False | gpt4o=0.749662;claude46=0.735922 | 0.750 | 0.736 | 0.780 |

## seed-pair null：同 teacher 两个 O seed 的 mean_f d_f 之差（e3c_gap_null.csv）

| teacher | n | mean_diff | rms | mean_abs | q95_abs |
|---|---|---|---|---|---|
| claude46 | 10 | 7.3e-04 | 0.011 | 0.009 | 0.017 |
| deepseek_v4 | 10 | 0.002 | 0.004 | 0.003 | 0.007 |
| gpt4o | 10 | 0.002 | 0.007 | 0.007 | 0.012 |
| all | 30 | 0.002 | 0.008 | 0.006 | 0.015 |

尺度匹配后统计量的 null SD = 0.004，q95 = 0.008（单对 RMS 0.008，单对 q95 0.015；df = 12）。

## Run inventory（e3c_inventory.csv；本 split 有 readout 的 run）

| teacher | n_O | n_F | n_C | seeds_O | seeds_F | seeds_C | paired_F | paired_C |
|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| deepseek_v4 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| gpt4o | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |

## 每 run（e3c_gap_runs.csv；gap = family 单位 mean_f d_f；*_cw = 同一 run 的 cell 加权 run 级值，`e1_metrics.teacher_agreement`：gap_cw 对参照 other，gap_e2c_cw = own − max_other 即 E2c 原定义）

| run_id | reference_other | n_families | agree_own | agree_other | gap | agree_own_cw | agree_other_cw | gap_cw | other_argmax_cw | gap_e2c_cw | n_ties_own_cw |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | deepseek_v4 | 295 | 0.834 | 0.826 | 0.008 | 0.846 | 0.822 | 0.024 | deepseek_v4 | 0.024 | 61 |
| qwen3-4b-e2c-paired.claude46_C_s2 | deepseek_v4 | 295 | 0.849 | 0.831 | 0.018 | 0.856 | 0.828 | 0.028 | gpt4o | 0.021 | 61 |
| qwen3-4b-e2c-paired.claude46_C_s3 | deepseek_v4 | 295 | 0.827 | 0.842 | -0.015 | 0.840 | 0.837 | 0.004 | deepseek_v4 | 0.004 | 61 |
| qwen3-4b-e2c-paired.claude46_C_s4 | deepseek_v4 | 295 | 0.837 | 0.840 | -0.003 | 0.845 | 0.836 | 0.009 | deepseek_v4 | 0.009 | 61 |
| qwen3-4b-e2c-paired.claude46_C_s5 | deepseek_v4 | 295 | 0.843 | 0.841 | 0.003 | 0.853 | 0.838 | 0.014 | deepseek_v4 | 0.014 | 61 |
| qwen3-4b-e2c-paired.claude46_F_s1 | deepseek_v4 | 295 | 0.844 | 0.840 | 0.004 | 0.853 | 0.835 | 0.018 | deepseek_v4 | 0.018 | 61 |
| qwen3-4b-e2c-paired.claude46_F_s2 | deepseek_v4 | 295 | 0.838 | 0.839 | -8.5e-04 | 0.847 | 0.836 | 0.011 | deepseek_v4 | 0.011 | 61 |
| qwen3-4b-e2c-paired.claude46_F_s3 | deepseek_v4 | 295 | 0.832 | 0.831 | 0.002 | 0.840 | 0.827 | 0.014 | deepseek_v4 | 0.014 | 61 |
| qwen3-4b-e2c-paired.claude46_F_s4 | deepseek_v4 | 295 | 0.836 | 0.832 | 0.004 | 0.846 | 0.828 | 0.017 | deepseek_v4 | 0.017 | 60 |
| qwen3-4b-e2c-paired.claude46_F_s5 | deepseek_v4 | 295 | 0.845 | 0.842 | 0.003 | 0.854 | 0.840 | 0.014 | deepseek_v4 | 0.014 | 61 |
| qwen3-4b-e2c-paired.claude46_O_s1 | deepseek_v4 | 295 | 0.849 | 0.841 | 0.009 | 0.857 | 0.837 | 0.020 | deepseek_v4 | 0.020 | 61 |
| qwen3-4b-e2c-paired.claude46_O_s2 | deepseek_v4 | 295 | 0.854 | 0.836 | 0.018 | 0.863 | 0.833 | 0.030 | deepseek_v4 | 0.030 | 61 |
| qwen3-4b-e2c-paired.claude46_O_s3 | deepseek_v4 | 295 | 0.842 | 0.837 | 0.005 | 0.853 | 0.835 | 0.018 | deepseek_v4 | 0.018 | 61 |
| qwen3-4b-e2c-paired.claude46_O_s4 | deepseek_v4 | 295 | 0.851 | 0.830 | 0.021 | 0.856 | 0.828 | 0.029 | deepseek_v4 | 0.029 | 61 |
| qwen3-4b-e2c-paired.claude46_O_s5 | deepseek_v4 | 295 | 0.828 | 0.823 | 0.005 | 0.838 | 0.821 | 0.017 | deepseek_v4 | 0.017 | 61 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | gpt4o | 291 | 0.765 | 0.724 | 0.040 | 0.760 | 0.721 | 0.039 | gpt4o | 0.039 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | gpt4o | 291 | 0.790 | 0.748 | 0.042 | 0.782 | 0.745 | 0.038 | gpt4o | 0.038 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | gpt4o | 291 | 0.785 | 0.748 | 0.037 | 0.778 | 0.746 | 0.033 | gpt4o | 0.033 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | gpt4o | 291 | 0.789 | 0.753 | 0.035 | 0.784 | 0.752 | 0.032 | gpt4o | 0.032 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | gpt4o | 291 | 0.800 | 0.770 | 0.030 | 0.796 | 0.766 | 0.030 | gpt4o | 0.030 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | gpt4o | 291 | 0.798 | 0.756 | 0.042 | 0.791 | 0.752 | 0.039 | gpt4o | 0.039 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | gpt4o | 291 | 0.785 | 0.755 | 0.030 | 0.780 | 0.751 | 0.029 | gpt4o | 0.029 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | gpt4o | 291 | 0.790 | 0.753 | 0.037 | 0.785 | 0.749 | 0.036 | gpt4o | 0.036 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | gpt4o | 291 | 0.786 | 0.749 | 0.037 | 0.781 | 0.745 | 0.036 | gpt4o | 0.036 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | gpt4o | 291 | 0.781 | 0.747 | 0.034 | 0.776 | 0.743 | 0.033 | gpt4o | 0.033 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | gpt4o | 291 | 0.778 | 0.743 | 0.035 | 0.771 | 0.739 | 0.032 | gpt4o | 0.032 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | gpt4o | 291 | 0.795 | 0.763 | 0.032 | 0.789 | 0.759 | 0.030 | gpt4o | 0.030 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | gpt4o | 291 | 0.788 | 0.753 | 0.035 | 0.782 | 0.749 | 0.033 | gpt4o | 0.033 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | gpt4o | 291 | 0.791 | 0.756 | 0.035 | 0.784 | 0.752 | 0.032 | gpt4o | 0.032 | 0 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | gpt4o | 291 | 0.782 | 0.753 | 0.028 | 0.776 | 0.749 | 0.027 | gpt4o | 0.027 | 0 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | deepseek_v4 | 291 | 0.808 | 0.809 | -8.6e-04 | 0.803 | 0.805 | -0.002 | deepseek_v4 | -0.002 | 0 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | deepseek_v4 | 291 | 0.802 | 0.814 | -0.011 | 0.798 | 0.807 | -0.009 | deepseek_v4 | -0.009 | 0 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | deepseek_v4 | 291 | 0.804 | 0.815 | -0.011 | 0.800 | 0.810 | -0.010 | deepseek_v4 | -0.010 | 0 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | deepseek_v4 | 291 | 0.807 | 0.814 | -0.008 | 0.803 | 0.808 | -0.005 | deepseek_v4 | -0.005 | 0 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | deepseek_v4 | 291 | 0.807 | 0.816 | -0.009 | 0.803 | 0.810 | -0.007 | deepseek_v4 | -0.007 | 0 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | deepseek_v4 | 291 | 0.820 | 0.808 | 0.011 | 0.816 | 0.802 | 0.013 | deepseek_v4 | 0.013 | 0 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | deepseek_v4 | 291 | 0.816 | 0.812 | 0.004 | 0.812 | 0.806 | 0.007 | deepseek_v4 | 0.007 | 0 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | deepseek_v4 | 291 | 0.814 | 0.813 | 8.6e-04 | 0.811 | 0.806 | 0.005 | deepseek_v4 | 0.005 | 0 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | deepseek_v4 | 291 | 0.814 | 0.815 | -8.6e-04 | 0.813 | 0.810 | 0.003 | deepseek_v4 | 0.003 | 0 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | deepseek_v4 | 291 | 0.808 | 0.804 | 0.004 | 0.807 | 0.799 | 0.008 | deepseek_v4 | 0.008 | 0 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | deepseek_v4 | 291 | 0.809 | 0.808 | 8.6e-04 | 0.807 | 0.802 | 0.005 | deepseek_v4 | 0.005 | 0 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | deepseek_v4 | 291 | 0.807 | 0.811 | -0.004 | 0.804 | 0.806 | -0.002 | deepseek_v4 | -0.002 | 0 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | deepseek_v4 | 291 | 0.814 | 0.815 | -8.6e-04 | 0.812 | 0.809 | 0.003 | deepseek_v4 | 0.003 | 0 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | deepseek_v4 | 291 | 0.814 | 0.810 | 0.004 | 0.814 | 0.804 | 0.010 | deepseek_v4 | 0.010 | 0 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | deepseek_v4 | 291 | 0.809 | 0.819 | -0.009 | 0.807 | 0.812 | -0.005 | deepseek_v4 | -0.005 | 0 |

family 单位与 cell 加权之差 |gap − gap_cw|（预期不为 0：d_f 是 family 均值，不按 cell 加权；单位 = family 是 e3_metrics.family_compare 的约定）：

| version | n_runs | mean_abs_diff | max_abs_diff | mean_gap | mean_gap_cw | mean_gap_e2c_cw |
|---|---|---|---|---|---|---|
| C | 15 | 0.006 | 0.019 | 0.010 | 0.014 | 0.014 |
| F | 15 | 0.006 | 0.015 | 0.014 | 0.019 | 0.019 |
| O | 15 | 0.006 | 0.014 | 0.014 | 0.019 | 0.019 |
| all | 45 | 0.006 | 0.019 | 0.013 | 0.017 | 0.017 |

注：学生在 teacher 内按 seed 配对比较；gap 不单独解读，与 e3c 的 agreement / JSD 表（scripts/15 在同一 run 上）同报；R 学生与基座不是 E3c 的 cell。