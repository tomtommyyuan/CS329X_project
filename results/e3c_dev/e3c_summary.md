# E3c gap 分析（dev，student qwen3-4b-e2c-paired，variants T1, T3, T5, T6；E3c gap rule pre-specified (tasks/e3c_plan.md; statistics = the frozen E3 rules of tasks/e3_plan.md §2-3) before any E3c F / C run existed; not yet frozen (freeze line pending in tasks/hpc_log.md)；auto-generated）

**gap F - O：inconclusive**（0/3 过 q95，0/3 过 TOST，方向 nan）；**gap C - O：inconclusive**（0/3 过 q95，0/3 过 TOST，方向 nan）。

**dev = freeze split**：以下判定只作描述；只有 results/e3c（test，冻结后只跑一次）是确认性的。

问题：contested-set 示范的文风改写（O → F / C）是否改变学生对**自己** teacher 判断的继承量。量 = E2c 的 gap（tasks/e2c_plan.md §6）按 family 计：每 run 每 family f 的 d_f = agree_own_f − agree_other_f，agree = 该 family 内有定义多数的 (family, variant) cell 上学生多数行动与 teacher 多数行动相同的份额（symmetrized，p_sym = 0.5 的 cell 不计，`e3_metrics.family_compare`）；run 值 = mean_f d_f，同 teacher 的所有 run 共用一个 family 集（对每个 run 都完整且 gap 有定义的 family），null、水平与配对统计量在同一组 family 上。参照 other teacher 按 teacher 固定：与该 teacher 的 O 学生 run 级 agreement（`e1_metrics.teacher_agreement`，cell 加权）seed 均值最高的其他 teacher（并列取字母序最前），O / F / C 共用，见下表。

规则（docs/03 E3 行原文：效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；tasks/e3_plan.md §2–3 的冻结统计，`e3_metrics.paired_delta` / `seed_pair_null` / `e3_verdict`）：每 teacher 统计量 = 5 个 seed 配对差 mean_f d_f(S_T,V,s) − mean_f d_f(S_T,O,s) 的均值，family bootstrap 95% CI（B = 10000，seed 0，同 teacher 各 seed 联动重抽）；null = 同 teacher 两个 O seed 的 mean_f d_f 之差（带符号，C(n_O, 2) 对，跨 teacher 合并，n = 30），尺度匹配到 seed 均值：SD_stat = sqrt(mean(d²) / n_seeds)，q95 = t(0.975, df = Σ(n_O − 1) = 12) × SD_stat；teacher 过 ⇔ |stat| > q95；effect ⇔ ≥ 2/3 的 3 个 teacher 过且同号；no effect ⇔ ≥ 2/3 teacher 过 TOST（CI 与点估计落在 ± 1 SD_stat 内）；否则 inconclusive；无配对 run 或 teacher < 3 → pending。单对 q95（`null_q95_single`、`n_pass_single`）只作敏感性列。假设：seed 噪声近似正态、跨 seed 独立（同 seed 的 F / O 对共享初始化与数据顺序，null 偏保守）。

## 判定（e3c_gap_verdicts.csv；descriptive on dev）

| metric | teachers: stat [CI] (effect in null sd, p, Holm, TOST) * = exceeds q95 | null q95 of the stat (single-pair q95; n) | pass | TOST pass | direction | verdict |
|---|---|---|---|---|---|---|
| gap F - O | claude46 0.002 [-0.003, 0.008] (0.679 null sd, p 0.510, Holm 1.000, TOST False); deepseek_v4 0.003 [-0.007, 0.014] (0.863 null sd, p 0.405, Holm 1.000, TOST False); gpt4o -0.002 [-0.010, 0.005] (-0.634 null sd, p 0.538, Holm 1.000, TOST False) | 0.007 (0.014; 30) | 0/3 | 0/3 | nan | **inconclusive** |
| gap C - O | claude46 0.002 [-0.005, 0.009] (0.714 null sd, p 0.489, Holm 0.603, TOST False); deepseek_v4 -0.004 [-0.010, 0.003] (-1.079 null sd, p 0.302, Holm 0.603, TOST False); gpt4o -0.005 [-0.019, 0.008] (-1.479 null sd, p 0.165, Holm 0.495, TOST False) | 0.007 (0.014; 30) | 0/3 | 0/3 | nan | **inconclusive** |

每 teacher 的统计量（e3c_gap_verdict_teachers.csv）：

| metric | teacher | n_seeds | stat | ci_lo | ci_hi | null_sd | q95 | effect_sd | exceeds_q95 | exceeds_q95_single | p_null | p_holm | tost |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| gap F - O | claude46 | 5 | 0.002 | -0.003 | 0.008 | 0.003 | 0.007 | 0.679 | False | False | 0.510 | 1.000 | False |
| gap F - O | deepseek_v4 | 5 | 0.003 | -0.007 | 0.014 | 0.003 | 0.007 | 0.863 | False | False | 0.405 | 1.000 | False |
| gap F - O | gpt4o | 5 | -0.002 | -0.010 | 0.005 | 0.003 | 0.007 | -0.634 | False | False | 0.538 | 1.000 | False |
| gap C - O | claude46 | 5 | 0.002 | -0.005 | 0.009 | 0.003 | 0.007 | 0.714 | False | False | 0.489 | 0.603 | False |
| gap C - O | deepseek_v4 | 5 | -0.004 | -0.010 | 0.003 | 0.003 | 0.007 | -1.079 | False | False | 0.302 | 0.603 | False |
| gap C - O | gpt4o | 5 | -0.005 | -0.019 | 0.008 | 0.003 | 0.007 | -1.479 | False | False | 0.165 | 0.495 | False |

## 每 (teacher, version) 的水平与配对差（e3c_gap_by_teacher.csv；agree_own / agree_other / gap = family 单位的 seed 均值，CI = family bootstrap；diff = 与 O 按 seed 配对的差，e3c_gap_by_seed.csv 为每 seed）

| teacher | version | n_seeds | n_families | agree_own [CI] | agree_other [CI] | gap [CI] | n_pairs | n_families_paired | diff vs O [CI] | direction |
|---|---|---|---|---|---|---|---|---|---|---|
| claude46 | O | 5 | 138 | 0.829 [0.775, 0.879] | 0.800 [0.745, 0.853] | 0.029 [-0.010, 0.070] |  |  |  |  |
| claude46 | F | 5 | 138 | 0.828 [0.775, 0.878] | 0.797 [0.741, 0.849] | 0.031 [-0.007, 0.072] | 5 | 138 | 0.002 [-0.003, 0.008] | + |
| claude46 | C | 5 | 138 | 0.826 [0.771, 0.878] | 0.795 [0.739, 0.851] | 0.031 [-0.010, 0.074] | 5 | 138 | 0.002 [-0.005, 0.009] | + |
| deepseek_v4 | O | 5 | 137 | 0.785 [0.738, 0.827] | 0.749 [0.700, 0.798] | 0.035 [-0.001, 0.072] |  |  |  |  |
| deepseek_v4 | F | 5 | 137 | 0.781 [0.738, 0.823] | 0.743 [0.694, 0.790] | 0.038 [0.003, 0.074] | 5 | 137 | 0.003 [-0.007, 0.014] | + |
| deepseek_v4 | C | 5 | 137 | 0.776 [0.732, 0.818] | 0.745 [0.695, 0.791] | 0.032 [-0.004, 0.066] | 5 | 137 | -0.004 [-0.010, 0.003] | - |
| gpt4o | O | 5 | 140 | 0.842 [0.800, 0.881] | 0.837 [0.796, 0.875] | 0.005 [-0.033, 0.043] |  |  |  |  |
| gpt4o | F | 5 | 140 | 0.835 [0.792, 0.874] | 0.832 [0.790, 0.871] | 0.003 [-0.035, 0.042] | 5 | 140 | -0.002 [-0.010, 0.005] | - |
| gpt4o | C | 5 | 140 | 0.829 [0.786, 0.868] | 0.829 [0.786, 0.869] | 0.000 [-0.035, 0.037] | 5 | 140 | -0.005 [-0.019, 0.008] | - |

## 参照 other teacher（e3c_reference_other.csv；由该 teacher 的 O 学生的 cell 加权 run 级 agreement 的 seed 均值选出，并列取字母序最前）

| teacher | reference_other | n_O_runs | agree_ref | tie | candidates | agree__gpt4o | agree__claude46 | agree__deepseek_v4 |
|---|---|---|---|---|---|---|---|---|
| gpt4o | deepseek_v4 | 5 | 0.831 | False | deepseek_v4=0.830924;claude46=0.820959 | 0.841 | 0.821 | 0.831 |
| claude46 | gpt4o | 5 | 0.800 | False | gpt4o=0.799652;deepseek_v4=0.776471 | 0.800 | 0.831 | 0.776 |
| deepseek_v4 | gpt4o | 5 | 0.743 | False | gpt4o=0.742509;claude46=0.720071 | 0.743 | 0.720 | 0.777 |

## seed-pair null：同 teacher 两个 O seed 的 mean_f d_f 之差（e3c_gap_null.csv）

| teacher | n | mean_diff | rms | mean_abs | q95_abs |
|---|---|---|---|---|---|
| claude46 | 10 | 0.003 | 0.007 | 0.006 | 0.012 |
| deepseek_v4 | 10 | 7.3e-04 | 0.004 | 0.004 | 0.007 |
| gpt4o | 10 | -0.003 | 0.010 | 0.009 | 0.016 |
| all | 30 | 4.2e-04 | 0.008 | 0.006 | 0.014 |

尺度匹配后统计量的 null SD = 0.003，q95 = 0.007（单对 RMS 0.008，单对 q95 0.014；df = 12）。

## Run inventory（e3c_inventory.csv；本 split 有 readout 的 run）

| teacher | n_O | n_F | n_C | seeds_O | seeds_F | seeds_C | paired_F | paired_C |
|---|---|---|---|---|---|---|---|---|
| claude46 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| deepseek_v4 | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |
| gpt4o | 5 | 5 | 5 | 1,2,3,4,5 | 1,2,3,4,5 | 1,2,3,4,5 | 5 | 5 |

## 每 run（e3c_gap_runs.csv；gap = family 单位 mean_f d_f；*_cw = 同一 run 的 cell 加权 run 级值，`e1_metrics.teacher_agreement`：gap_cw 对参照 other，gap_e2c_cw = own − max_other 即 E2c 原定义）

| run_id | reference_other | n_families | agree_own | agree_other | gap | agree_own_cw | agree_other_cw | gap_cw | other_argmax_cw | gap_e2c_cw | n_ties_own_cw |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-paired.claude46_C_s1 | gpt4o | 138 | 0.844 | 0.808 | 0.036 | 0.844 | 0.807 | 0.037 | gpt4o | 0.037 | 34 |
| qwen3-4b-e2c-paired.claude46_C_s2 | gpt4o | 138 | 0.808 | 0.783 | 0.025 | 0.812 | 0.786 | 0.026 | gpt4o | 0.026 | 34 |
| qwen3-4b-e2c-paired.claude46_C_s3 | gpt4o | 138 | 0.830 | 0.790 | 0.040 | 0.831 | 0.784 | 0.047 | gpt4o | 0.047 | 34 |
| qwen3-4b-e2c-paired.claude46_C_s4 | gpt4o | 138 | 0.830 | 0.803 | 0.027 | 0.835 | 0.801 | 0.033 | gpt4o | 0.033 | 34 |
| qwen3-4b-e2c-paired.claude46_C_s5 | gpt4o | 138 | 0.819 | 0.793 | 0.026 | 0.821 | 0.794 | 0.026 | gpt4o | 0.026 | 34 |
| qwen3-4b-e2c-paired.claude46_F_s1 | gpt4o | 138 | 0.819 | 0.795 | 0.024 | 0.822 | 0.796 | 0.026 | gpt4o | 0.026 | 34 |
| qwen3-4b-e2c-paired.claude46_F_s2 | gpt4o | 138 | 0.826 | 0.801 | 0.025 | 0.829 | 0.801 | 0.028 | gpt4o | 0.028 | 34 |
| qwen3-4b-e2c-paired.claude46_F_s3 | gpt4o | 138 | 0.839 | 0.799 | 0.040 | 0.842 | 0.800 | 0.042 | gpt4o | 0.042 | 34 |
| qwen3-4b-e2c-paired.claude46_F_s4 | gpt4o | 138 | 0.826 | 0.792 | 0.034 | 0.828 | 0.793 | 0.035 | gpt4o | 0.035 | 34 |
| qwen3-4b-e2c-paired.claude46_F_s5 | gpt4o | 138 | 0.830 | 0.799 | 0.031 | 0.831 | 0.798 | 0.033 | gpt4o | 0.033 | 34 |
| qwen3-4b-e2c-paired.claude46_O_s1 | gpt4o | 138 | 0.835 | 0.803 | 0.033 | 0.833 | 0.801 | 0.032 | gpt4o | 0.032 | 34 |
| qwen3-4b-e2c-paired.claude46_O_s2 | gpt4o | 138 | 0.839 | 0.813 | 0.026 | 0.842 | 0.812 | 0.030 | gpt4o | 0.030 | 34 |
| qwen3-4b-e2c-paired.claude46_O_s3 | gpt4o | 138 | 0.824 | 0.793 | 0.030 | 0.826 | 0.793 | 0.033 | gpt4o | 0.033 | 34 |
| qwen3-4b-e2c-paired.claude46_O_s4 | gpt4o | 138 | 0.825 | 0.792 | 0.033 | 0.829 | 0.793 | 0.037 | gpt4o | 0.037 | 34 |
| qwen3-4b-e2c-paired.claude46_O_s5 | gpt4o | 138 | 0.821 | 0.801 | 0.021 | 0.824 | 0.800 | 0.025 | gpt4o | 0.025 | 34 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | gpt4o | 137 | 0.754 | 0.726 | 0.027 | 0.749 | 0.723 | 0.027 | gpt4o | 0.027 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | gpt4o | 137 | 0.779 | 0.737 | 0.042 | 0.773 | 0.728 | 0.045 | claude46 | 0.045 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | gpt4o | 137 | 0.768 | 0.748 | 0.020 | 0.761 | 0.744 | 0.017 | gpt4o | 0.017 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | gpt4o | 137 | 0.783 | 0.745 | 0.038 | 0.773 | 0.739 | 0.034 | gpt4o | 0.034 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | gpt4o | 137 | 0.797 | 0.766 | 0.031 | 0.788 | 0.763 | 0.025 | gpt4o | 0.025 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | gpt4o | 137 | 0.776 | 0.745 | 0.031 | 0.765 | 0.739 | 0.026 | gpt4o | 0.026 | 3 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | gpt4o | 137 | 0.785 | 0.746 | 0.038 | 0.781 | 0.743 | 0.038 | gpt4o | 0.038 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | gpt4o | 137 | 0.783 | 0.745 | 0.038 | 0.778 | 0.740 | 0.038 | gpt4o | 0.038 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | gpt4o | 137 | 0.774 | 0.735 | 0.038 | 0.765 | 0.726 | 0.038 | gpt4o | 0.038 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | gpt4o | 137 | 0.790 | 0.745 | 0.046 | 0.787 | 0.740 | 0.046 | gpt4o | 0.046 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | gpt4o | 137 | 0.788 | 0.750 | 0.038 | 0.778 | 0.744 | 0.034 | gpt4o | 0.034 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | gpt4o | 137 | 0.794 | 0.763 | 0.031 | 0.787 | 0.756 | 0.030 | gpt4o | 0.030 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | gpt4o | 137 | 0.783 | 0.745 | 0.038 | 0.776 | 0.737 | 0.040 | gpt4o | 0.040 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | gpt4o | 137 | 0.770 | 0.735 | 0.035 | 0.766 | 0.726 | 0.040 | gpt4o | 0.040 | 4 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | gpt4o | 137 | 0.788 | 0.754 | 0.035 | 0.780 | 0.749 | 0.031 | gpt4o | 0.031 | 4 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | deepseek_v4 | 140 | 0.839 | 0.836 | 0.004 | 0.841 | 0.832 | 0.010 | claude46 | 0.008 | 2 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | deepseek_v4 | 140 | 0.804 | 0.811 | -0.007 | 0.801 | 0.805 | -0.004 | claude46 | -0.026 | 2 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | deepseek_v4 | 140 | 0.830 | 0.830 | 0.000 | 0.831 | 0.824 | 0.007 | deepseek_v4 | 0.007 | 2 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | deepseek_v4 | 140 | 0.834 | 0.834 | 0.000 | 0.836 | 0.830 | 0.006 | deepseek_v4 | 0.006 | 2 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | deepseek_v4 | 140 | 0.838 | 0.834 | 0.004 | 0.840 | 0.827 | 0.013 | claude46 | -4.2e-04 | 2 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | deepseek_v4 | 140 | 0.848 | 0.845 | 0.004 | 0.847 | 0.837 | 0.010 | claude46 | 0.008 | 2 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | deepseek_v4 | 140 | 0.836 | 0.832 | 0.004 | 0.836 | 0.825 | 0.011 | claude46 | 0.007 | 2 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | deepseek_v4 | 140 | 0.836 | 0.836 | 0.000 | 0.836 | 0.829 | 0.008 | deepseek_v4 | 0.008 | 2 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | deepseek_v4 | 140 | 0.834 | 0.827 | 0.007 | 0.833 | 0.822 | 0.011 | deepseek_v4 | 0.011 | 2 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | deepseek_v4 | 140 | 0.820 | 0.820 | 0.000 | 0.822 | 0.815 | 0.007 | deepseek_v4 | 0.007 | 2 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | deepseek_v4 | 140 | 0.839 | 0.832 | 0.007 | 0.840 | 0.827 | 0.013 | deepseek_v4 | 0.013 | 2 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | deepseek_v4 | 140 | 0.841 | 0.841 | 0.000 | 0.840 | 0.834 | 0.006 | deepseek_v4 | 0.006 | 2 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | deepseek_v4 | 140 | 0.850 | 0.854 | -0.004 | 0.850 | 0.847 | 0.003 | deepseek_v4 | 0.003 | 2 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | deepseek_v4 | 140 | 0.832 | 0.818 | 0.014 | 0.831 | 0.815 | 0.016 | claude46 | 0.014 | 2 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | deepseek_v4 | 140 | 0.846 | 0.839 | 0.007 | 0.847 | 0.832 | 0.015 | deepseek_v4 | 0.015 | 2 |

family 单位与 cell 加权之差 |gap − gap_cw|（预期不为 0：d_f 是 family 均值，不按 cell 加权；单位 = family 是 e3_metrics.family_compare 的约定）：

| version | n_runs | mean_abs_diff | max_abs_diff | mean_gap | mean_gap_cw | mean_gap_e2c_cw |
|---|---|---|---|---|---|---|
| C | 15 | 0.004 | 0.009 | 0.021 | 0.023 | 0.021 |
| F | 15 | 0.003 | 0.008 | 0.024 | 0.026 | 0.026 |
| O | 15 | 0.004 | 0.008 | 0.023 | 0.026 | 0.025 |
| all | 45 | 0.004 | 0.009 | 0.023 | 0.025 | 0.024 |

注：学生在 teacher 内按 seed 配对比较；gap 不单独解读，与 e3c 的 agreement / JSD 表（scripts/15 在同一 run 上）同报；R 学生与基座不是 E3c 的 cell。