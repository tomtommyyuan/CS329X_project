# E2c 分析（test，variants T1, T3, T5, T6；rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed; frozen at commit a694423；auto-generated）

**E2c primary（own > other，条件 C）：PARTIAL**（1/3 teacher 过）；**归因（C − K）：attributed to contestedness**（2/3）。

规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = 2000（seed 0），每个 run 重算 agreement，取 seed 均值，2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。

## 判定表（e2c_gaps.csv）

| condition | role | teacher | n_seeds | agree_own | agree_other_max | gap | CI | null_q95 | null_sd | null_n_pairs | exceeds_null | ci_above_zero | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | primary | gpt4o | 5 | 0.812 | 0.810 | 0.003 | [-0.018, 0.021] | 0.015 | 0.005 | 10 | False | False | False |
| C | primary | claude46 | 5 | 0.859 | 0.831 | 0.028 | [0.005, 0.047] | 0.032 | 0.011 | 10 | False | True | False |
| C | primary | deepseek_v4 | 5 | 0.788 | 0.753 | 0.035 | [0.015, 0.054] | 0.030 | 0.011 | 10 | True | True | True |
| K | reference | gpt4o | 5 | 0.844 | 0.850 | -0.005 | [-0.030, 0.012] | 0.015 | 0.005 | 10 | False | False | False |
| K | reference | claude46 | 5 | 0.857 | 0.855 | 0.002 | [-0.022, 0.027] | 0.014 | 0.004 | 10 | False | False | False |
| K | reference | deepseek_v4 | 5 | 0.856 | 0.852 | 0.003 | [-0.020, 0.019] | 0.014 | 0.006 | 10 | False | False | False |
| E1 | reference | gpt4o | 5 | 0.857 | 0.855 | 0.002 | [-0.022, 0.020] | 0.016 | 0.005 | 10 | False | False | False |
| E1 | reference | claude46 | 5 | 0.882 | 0.862 | 0.020 | [-0.006, 0.041] | 0.023 | 0.008 | 10 | False | False | False |
| E1 | reference | deepseek_v4 | 5 | 0.857 | 0.848 | 0.009 | [-0.015, 0.025] | 0.008 | 0.003 | 10 | True | False | False |

## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）

| teacher | gap_C | gap_K | diff | CI | ci_above_zero |
|---|---|---|---|---|---|
| gpt4o | 0.003 | -0.005 | 0.008 | [-0.008, 0.031] | False |
| claude46 | 0.028 | 0.002 | 0.026 | [0.001, 0.049] | True |
| deepseek_v4 | 0.035 | 0.003 | 0.032 | [0.012, 0.059] | True |

## 输入

| condition | label | glob | n_files | n_runs | n_rows | seeds_per_teacher | skipped_run_ids |
|---|---|---|---|---|---|---|---|
| C | E2c-C (contested) | runs/qwen3-4b-e2c/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| K | E2c-K (consensus control) | runs/qwen3-4b-e2ckn/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| E1 | E1 (original train, reference) | runs/qwen3-4b/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |

## 描述

### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）

| condition | run_id | answer_rate | n_families | agree__gpt4o | agree__claude46 | agree__deepseek_v4 | agree_own | agree_other_max | other_argmax | gap | jsd_own | flip_rate | mean_jsd | s | n_examples | n_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | qwen3-4b-e2c.claude46_O_s1 | 1.000 | 300 | 0.832 | 0.862 | 0.832 | 0.862 | 0.832 | gpt4o | 0.030 | 0.119 | 0.097 | 0.035 | 0.090 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s2 | 1.000 | 300 | 0.828 | 0.874 | 0.829 | 0.874 | 0.829 | deepseek_v4 | 0.045 | 0.118 | 0.090 | 0.034 | 0.082 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s3 | 1.000 | 300 | 0.816 | 0.838 | 0.826 | 0.838 | 0.826 | deepseek_v4 | 0.012 | 0.133 | 0.096 | 0.038 | 0.069 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s4 | 1.000 | 300 | 0.827 | 0.865 | 0.835 | 0.865 | 0.835 | deepseek_v4 | 0.030 | 0.120 | 0.092 | 0.036 | 0.082 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s5 | 1.000 | 300 | 0.826 | 0.859 | 0.834 | 0.859 | 0.834 | deepseek_v4 | 0.025 | 0.129 | 0.086 | 0.035 | 0.078 | 4838 | 351284 |
| C | qwen3-4b-e2c.deepseek_v4_O_s1 | 1.000 | 300 | 0.740 | 0.726 | 0.776 | 0.776 | 0.740 | gpt4o | 0.036 | 0.143 | 0.248 | 0.159 | 0.426 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s2 | 1.000 | 300 | 0.769 | 0.757 | 0.808 | 0.808 | 0.769 | gpt4o | 0.040 | 0.132 | 0.239 | 0.172 | 0.425 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s3 | 1.000 | 300 | 0.748 | 0.735 | 0.782 | 0.782 | 0.748 | gpt4o | 0.033 | 0.139 | 0.275 | 0.187 | 0.474 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s4 | 1.000 | 300 | 0.753 | 0.739 | 0.787 | 0.787 | 0.753 | gpt4o | 0.034 | 0.139 | 0.264 | 0.193 | 0.477 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s5 | 1.000 | 300 | 0.753 | 0.745 | 0.786 | 0.786 | 0.753 | gpt4o | 0.032 | 0.137 | 0.261 | 0.183 | 0.455 | 2497 | 110114 |
| C | qwen3-4b-e2c.gpt4o_O_s1 | 1.000 | 300 | 0.809 | 0.789 | 0.804 | 0.809 | 0.804 | deepseek_v4 | 0.005 | 0.144 | 0.148 | 0.091 | 0.261 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s2 | 1.000 | 300 | 0.805 | 0.793 | 0.808 | 0.805 | 0.808 | deepseek_v4 | -0.003 | 0.148 | 0.161 | 0.102 | 0.309 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s3 | 1.000 | 300 | 0.814 | 0.796 | 0.809 | 0.814 | 0.809 | deepseek_v4 | 0.005 | 0.140 | 0.149 | 0.084 | 0.264 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s4 | 1.000 | 300 | 0.822 | 0.801 | 0.812 | 0.822 | 0.812 | deepseek_v4 | 0.010 | 0.136 | 0.131 | 0.084 | 0.259 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s5 | 1.000 | 300 | 0.811 | 0.801 | 0.814 | 0.811 | 0.814 | deepseek_v4 | -0.003 | 0.139 | 0.161 | 0.094 | 0.294 | 4964 | 244064 |
| E1 | qwen3-4b.claude46_O_s1 | 1.000 | 300 | 0.859 | 0.878 | 0.855 | 0.878 | 0.859 | gpt4o | 0.019 | 0.103 | 0.026 | 0.009 | 0.029 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s2 | 0.999 | 299 | 0.861 | 0.882 | 0.860 | 0.882 | 0.861 | gpt4o | 0.020 | 0.099 | 0.031 | 0.008 | 0.027 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s3 | 0.999 | 299 | 0.864 | 0.872 | 0.862 | 0.872 | 0.864 | gpt4o | 0.008 | 0.107 | 0.021 | 0.007 | 0.020 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s4 | 1.000 | 300 | 0.853 | 0.881 | 0.852 | 0.881 | 0.853 | gpt4o | 0.028 | 0.103 | 0.025 | 0.007 | 0.021 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s5 | 1.000 | 299 | 0.875 | 0.898 | 0.858 | 0.898 | 0.875 | gpt4o | 0.023 | 0.095 | 0.025 | 0.007 | 0.024 | 5642 | 447303 |
| E1 | qwen3-4b.deepseek_v4_O_s1 | 1.000 | 300 | 0.839 | 0.848 | 0.856 | 0.856 | 0.848 | claude46 | 0.008 | 0.082 | 0.084 | 0.040 | 0.147 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s2 | 1.000 | 300 | 0.847 | 0.848 | 0.862 | 0.862 | 0.848 | claude46 | 0.013 | 0.084 | 0.084 | 0.046 | 0.158 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s3 | 1.000 | 300 | 0.837 | 0.852 | 0.855 | 0.855 | 0.852 | claude46 | 0.003 | 0.077 | 0.078 | 0.034 | 0.138 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s4 | 1.000 | 300 | 0.834 | 0.838 | 0.853 | 0.853 | 0.838 | claude46 | 0.016 | 0.083 | 0.089 | 0.042 | 0.147 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s5 | 1.000 | 300 | 0.854 | 0.852 | 0.860 | 0.860 | 0.854 | gpt4o | 0.006 | 0.073 | 0.074 | 0.031 | 0.127 | 4936 | 221871 |
| E1 | qwen3-4b.gpt4o_O_s1 | 1.000 | 300 | 0.856 | 0.846 | 0.849 | 0.856 | 0.849 | deepseek_v4 | 0.007 | 0.096 | 0.068 | 0.026 | 0.121 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s2 | 1.000 | 300 | 0.867 | 0.865 | 0.859 | 0.867 | 0.865 | claude46 | 0.002 | 0.090 | 0.059 | 0.016 | 0.090 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s3 | 1.000 | 300 | 0.860 | 0.857 | 0.850 | 0.860 | 0.857 | claude46 | 0.003 | 0.095 | 0.068 | 0.026 | 0.114 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s4 | 1.000 | 300 | 0.847 | 0.843 | 0.848 | 0.847 | 0.848 | deepseek_v4 | -0.001 | 0.097 | 0.073 | 0.023 | 0.111 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s5 | 1.000 | 300 | 0.856 | 0.857 | 0.847 | 0.856 | 0.857 | claude46 | -6.0e-04 | 0.089 | 0.077 | 0.024 | 0.112 | 5619 | 279029 |
| K | qwen3-4b-e2ckn.claude46_O_s1 | 0.999 | 300 | 0.840 | 0.860 | 0.856 | 0.860 | 0.856 | deepseek_v4 | 0.004 | 0.129 | 0.042 | 0.023 | 0.047 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s2 | 1.000 | 300 | 0.832 | 0.850 | 0.853 | 0.850 | 0.853 | deepseek_v4 | -0.003 | 0.130 | 0.043 | 0.019 | 0.028 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s3 | 1.000 | 300 | 0.840 | 0.854 | 0.856 | 0.854 | 0.856 | deepseek_v4 | -0.001 | 0.128 | 0.041 | 0.018 | 0.033 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s4 | 1.000 | 300 | 0.841 | 0.855 | 0.853 | 0.855 | 0.853 | deepseek_v4 | 0.002 | 0.131 | 0.041 | 0.020 | 0.030 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s5 | 1.000 | 300 | 0.845 | 0.866 | 0.856 | 0.866 | 0.856 | deepseek_v4 | 0.010 | 0.126 | 0.033 | 0.018 | 0.026 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s1 | 1.000 | 300 | 0.842 | 0.846 | 0.851 | 0.851 | 0.846 | claude46 | 0.004 | 0.093 | 0.080 | 0.045 | 0.135 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s2 | 1.000 | 300 | 0.838 | 0.853 | 0.852 | 0.852 | 0.853 | claude46 | -0.002 | 0.094 | 0.076 | 0.045 | 0.132 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s3 | 1.000 | 300 | 0.851 | 0.855 | 0.849 | 0.849 | 0.855 | claude46 | -0.006 | 0.089 | 0.081 | 0.043 | 0.135 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s4 | 1.000 | 300 | 0.845 | 0.848 | 0.863 | 0.863 | 0.848 | claude46 | 0.015 | 0.087 | 0.088 | 0.044 | 0.127 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s5 | 0.999 | 299 | 0.858 | 0.852 | 0.863 | 0.863 | 0.858 | gpt4o | 0.005 | 0.086 | 0.067 | 0.034 | 0.112 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.gpt4o_O_s1 | 1.000 | 300 | 0.851 | 0.854 | 0.852 | 0.851 | 0.854 | claude46 | -0.004 | 0.118 | 0.057 | 0.030 | 0.091 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s2 | 1.000 | 300 | 0.834 | 0.838 | 0.841 | 0.834 | 0.841 | deepseek_v4 | -0.006 | 0.119 | 0.047 | 0.022 | 0.080 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s3 | 1.000 | 300 | 0.848 | 0.859 | 0.846 | 0.848 | 0.859 | claude46 | -0.011 | 0.116 | 0.052 | 0.026 | 0.075 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s4 | 1.000 | 300 | 0.847 | 0.850 | 0.842 | 0.847 | 0.850 | claude46 | -0.003 | 0.119 | 0.046 | 0.022 | 0.071 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s5 | 1.000 | 300 | 0.841 | 0.840 | 0.844 | 0.841 | 0.844 | deepseek_v4 | -0.003 | 0.117 | 0.052 | 0.027 | 0.088 | 4964 | 234276 |

### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）

| condition | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| C | claude46 | O | 10 | 0.016 | 0.011 | 0.032 |
| C | deepseek_v4 | O | 10 | 0.014 | 0.011 | 0.030 |
| C | gpt4o | O | 10 | 0.008 | 0.005 | 0.015 |
| C | all | all | 30 | 0.013 | 0.010 | 0.030 |
| K | claude46 | O | 10 | 0.007 | 0.004 | 0.014 |
| K | deepseek_v4 | O | 10 | 0.008 | 0.006 | 0.014 |
| K | gpt4o | O | 10 | 0.008 | 0.005 | 0.015 |
| K | all | all | 30 | 0.008 | 0.005 | 0.015 |
| E1 | claude46 | O | 10 | 0.011 | 0.008 | 0.023 |
| E1 | deepseek_v4 | O | 10 | 0.004 | 0.003 | 0.008 |
| E1 | gpt4o | O | 10 | 0.008 | 0.005 | 0.016 |
| E1 | all | all | 30 | 0.008 | 0.006 | 0.019 |

### 按 teacher 的训练规模（train_manifest.json 与 --sft-meta；O seed 共享同一 prompt 集）

| condition | teacher | n_runs | n_examples | n_target_tokens | n_families | order_stable_rate | n_dropped_order_unstable |
|---|---|---|---|---|---|---|---|
| C | gpt4o | 5 | 4964 | 244064 | nan | nan | nan |
| C | claude46 | 5 | 4838 | 351284 | nan | nan | nan |
| C | deepseek_v4 | 5 | 2497 | 110114 | nan | nan | nan |
| K | gpt4o | 5 | 4964 | 234276 | nan | nan | nan |
| K | claude46 | 5 | 4838 | 332906 | nan | nan | nan |
| K | deepseek_v4 | 5 | 2497 | 100375 | nan | nan | nan |
| E1 | gpt4o | 5 | 5619 | 279029 | nan | nan | nan |
| E1 | claude46 | 5 | 5642 | 447303 | nan | nan | nan |
| E1 | deepseek_v4 | 5 | 4936 | 221871 | nan | nan | nan |

注：JSD 受 teacher 校准混淆，只与 agreement 同报；flip rate 与 mean_jsd 不单独解读。
