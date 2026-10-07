# E2c 分析（dev，variants T1, T3, T5, T6；rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed; freeze commit not given (tasks/e2c_plan.md §9)；auto-generated）

**E2c primary（own > other，条件 C）：PASS**（2/3 teacher 过）；**归因（C − K）：attributed to contestedness**（2/3）。

**dev 只作描述**（tasks/e2c_plan.md §5：test 每条件只跑一次，看 test 后不改任何量）；只有 results/e2c（test）是确认性的。

规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = 2000（seed 0），每个 run 重算 agreement，取 seed 均值，2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。

## 判定表（e2c_gaps.csv）

| condition | role | teacher | n_seeds | agree_own | agree_other_max | gap | CI | null_q95 | null_sd | null_n_pairs | exceeds_null | ci_above_zero | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | primary | gpt4o | 5 | 0.839 | 0.830 | 0.009 | [-0.028, 0.033] | 0.013 | 0.005 | 10 | False | False | False |
| C | primary | claude46 | 5 | 0.837 | 0.799 | 0.038 | [2.8e-04, 0.077] | 0.023 | 0.008 | 10 | True | True | True |
| C | primary | deepseek_v4 | 5 | 0.788 | 0.747 | 0.041 | [0.002, 0.074] | 0.034 | 0.011 | 10 | True | True | True |
| K | reference | gpt4o | 5 | 0.831 | 0.834 | -0.003 | [-0.043, 0.026] | 0.020 | 0.007 | 10 | False | False | False |
| K | reference | claude46 | 5 | 0.817 | 0.815 | 0.002 | [-0.045, 0.035] | 0.031 | 0.010 | 10 | False | False | False |
| K | reference | deepseek_v4 | 5 | 0.824 | 0.840 | -0.016 | [-0.062, 0.017] | 0.026 | 0.009 | 10 | False | False | False |
| E1 | reference | gpt4o | 5 | 0.856 | 0.856 | 3.0e-04 | [-0.040, 0.030] | 0.020 | 0.008 | 10 | False | False | False |
| E1 | reference | claude46 | 5 | 0.846 | 0.829 | 0.017 | [-0.021, 0.052] | 0.015 | 0.005 | 10 | True | False | False |
| E1 | reference | deepseek_v4 | 5 | 0.844 | 0.826 | 0.018 | [-0.025, 0.052] | 0.021 | 0.006 | 10 | False | False | False |

## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）

| teacher | gap_C | gap_K | diff | CI | ci_above_zero |
|---|---|---|---|---|---|
| gpt4o | 0.009 | -0.003 | 0.012 | [-0.021, 0.049] | False |
| claude46 | 0.038 | 0.002 | 0.035 | [0.012, 0.072] | True |
| deepseek_v4 | 0.041 | -0.016 | 0.057 | [0.031, 0.095] | True |

## 输入

| condition | label | glob | n_files | n_runs | n_rows | seeds_per_teacher | skipped_run_ids |
|---|---|---|---|---|---|---|---|
| C | E2c-C (contested) | runs/qwen3-4b-e2c/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| K | E2c-K (consensus control) | runs/qwen3-4b-e2ckn/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| E1 | E1 (original train, reference) | runs/qwen3-4b/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |

## 描述

### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）

| condition | run_id | answer_rate | n_families | agree__gpt4o | agree__claude46 | agree__deepseek_v4 | agree_own | agree_other_max | other_argmax | gap | jsd_own | flip_rate | mean_jsd | s | n_examples | n_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | qwen3-4b-e2c.claude46_O_s1 | 1.000 | 150 | 0.798 | 0.833 | 0.766 | 0.833 | 0.798 | gpt4o | 0.035 | 0.135 | 0.094 | 0.045 | 0.123 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s2 | 1.000 | 150 | 0.803 | 0.833 | 0.773 | 0.833 | 0.803 | gpt4o | 0.030 | 0.137 | 0.083 | 0.044 | 0.112 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s3 | 1.000 | 150 | 0.812 | 0.853 | 0.782 | 0.853 | 0.812 | gpt4o | 0.041 | 0.131 | 0.067 | 0.035 | 0.091 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s4 | 1.000 | 150 | 0.782 | 0.826 | 0.768 | 0.826 | 0.782 | gpt4o | 0.044 | 0.140 | 0.084 | 0.042 | 0.113 | 4838 | 351284 |
| C | qwen3-4b-e2c.claude46_O_s5 | 1.000 | 150 | 0.800 | 0.838 | 0.778 | 0.838 | 0.800 | gpt4o | 0.039 | 0.130 | 0.076 | 0.035 | 0.093 | 4838 | 351284 |
| C | qwen3-4b-e2c.deepseek_v4_O_s1 | 1.000 | 150 | 0.744 | 0.721 | 0.792 | 0.792 | 0.744 | gpt4o | 0.048 | 0.129 | 0.206 | 0.148 | 0.407 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s2 | 1.000 | 150 | 0.770 | 0.751 | 0.802 | 0.802 | 0.770 | gpt4o | 0.032 | 0.123 | 0.218 | 0.160 | 0.403 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s3 | 1.000 | 150 | 0.725 | 0.707 | 0.766 | 0.766 | 0.725 | gpt4o | 0.042 | 0.145 | 0.251 | 0.174 | 0.453 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s4 | 1.000 | 150 | 0.747 | 0.726 | 0.782 | 0.782 | 0.747 | gpt4o | 0.034 | 0.127 | 0.253 | 0.180 | 0.455 | 2497 | 110114 |
| C | qwen3-4b-e2c.deepseek_v4_O_s5 | 1.000 | 150 | 0.751 | 0.728 | 0.798 | 0.798 | 0.751 | gpt4o | 0.047 | 0.129 | 0.239 | 0.171 | 0.434 | 2497 | 110114 |
| C | qwen3-4b-e2c.gpt4o_O_s1 | 1.000 | 150 | 0.838 | 0.822 | 0.832 | 0.838 | 0.832 | deepseek_v4 | 0.006 | 0.110 | 0.158 | 0.101 | 0.279 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s2 | 1.000 | 150 | 0.834 | 0.810 | 0.827 | 0.834 | 0.827 | deepseek_v4 | 0.008 | 0.116 | 0.188 | 0.120 | 0.344 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s3 | 1.000 | 150 | 0.848 | 0.831 | 0.835 | 0.848 | 0.835 | deepseek_v4 | 0.013 | 0.103 | 0.153 | 0.091 | 0.275 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s4 | 1.000 | 150 | 0.836 | 0.826 | 0.820 | 0.836 | 0.826 | claude46 | 0.010 | 0.112 | 0.128 | 0.086 | 0.265 | 4964 | 244064 |
| C | qwen3-4b-e2c.gpt4o_O_s5 | 1.000 | 150 | 0.838 | 0.824 | 0.829 | 0.838 | 0.829 | deepseek_v4 | 0.009 | 0.109 | 0.180 | 0.103 | 0.313 | 4964 | 244064 |
| E1 | qwen3-4b.claude46_O_s1 | 1.000 | 150 | 0.829 | 0.853 | 0.803 | 0.853 | 0.829 | gpt4o | 0.023 | 0.116 | 0.048 | 0.014 | 0.054 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s2 | 0.999 | 150 | 0.822 | 0.844 | 0.798 | 0.844 | 0.822 | gpt4o | 0.021 | 0.115 | 0.049 | 0.014 | 0.054 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s3 | 1.000 | 150 | 0.841 | 0.837 | 0.812 | 0.837 | 0.841 | gpt4o | -0.005 | 0.115 | 0.042 | 0.011 | 0.050 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s4 | 1.000 | 150 | 0.815 | 0.847 | 0.800 | 0.847 | 0.815 | gpt4o | 0.032 | 0.115 | 0.041 | 0.016 | 0.051 | 5642 | 447303 |
| E1 | qwen3-4b.claude46_O_s5 | 1.000 | 150 | 0.836 | 0.851 | 0.808 | 0.851 | 0.836 | gpt4o | 0.015 | 0.110 | 0.053 | 0.012 | 0.045 | 5642 | 447303 |
| E1 | qwen3-4b.deepseek_v4_O_s1 | 1.000 | 150 | 0.819 | 0.808 | 0.834 | 0.834 | 0.819 | gpt4o | 0.015 | 0.085 | 0.104 | 0.051 | 0.166 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s2 | 1.000 | 150 | 0.829 | 0.817 | 0.857 | 0.857 | 0.829 | gpt4o | 0.028 | 0.085 | 0.102 | 0.058 | 0.174 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s3 | 1.000 | 150 | 0.833 | 0.822 | 0.847 | 0.847 | 0.833 | gpt4o | 0.014 | 0.083 | 0.091 | 0.047 | 0.163 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s4 | 1.000 | 150 | 0.824 | 0.817 | 0.839 | 0.839 | 0.824 | gpt4o | 0.015 | 0.081 | 0.119 | 0.061 | 0.187 | 4936 | 221871 |
| E1 | qwen3-4b.deepseek_v4_O_s5 | 1.000 | 150 | 0.826 | 0.822 | 0.844 | 0.844 | 0.826 | gpt4o | 0.018 | 0.079 | 0.091 | 0.046 | 0.150 | 4936 | 221871 |
| E1 | qwen3-4b.gpt4o_O_s1 | 1.000 | 150 | 0.861 | 0.844 | 0.861 | 0.861 | 0.861 | deepseek_v4 | 1.2e-04 | 0.085 | 0.086 | 0.033 | 0.135 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s2 | 1.000 | 150 | 0.841 | 0.838 | 0.844 | 0.841 | 0.844 | deepseek_v4 | -0.002 | 0.103 | 0.081 | 0.023 | 0.111 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s3 | 1.000 | 150 | 0.857 | 0.831 | 0.849 | 0.857 | 0.849 | deepseek_v4 | 0.008 | 0.096 | 0.071 | 0.032 | 0.135 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s4 | 1.000 | 150 | 0.859 | 0.838 | 0.862 | 0.859 | 0.862 | deepseek_v4 | -0.003 | 0.091 | 0.078 | 0.026 | 0.115 | 5619 | 279029 |
| E1 | qwen3-4b.gpt4o_O_s5 | 1.000 | 150 | 0.862 | 0.851 | 0.864 | 0.862 | 0.864 | deepseek_v4 | -0.001 | 0.090 | 0.057 | 0.023 | 0.107 | 5619 | 279029 |
| K | qwen3-4b-e2ckn.claude46_O_s1 | 1.000 | 150 | 0.814 | 0.822 | 0.808 | 0.822 | 0.814 | gpt4o | 0.009 | 0.144 | 0.079 | 0.035 | 0.066 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s2 | 1.000 | 150 | 0.822 | 0.821 | 0.818 | 0.821 | 0.822 | gpt4o | -0.002 | 0.157 | 0.052 | 0.027 | 0.048 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s3 | 1.000 | 150 | 0.787 | 0.806 | 0.797 | 0.806 | 0.797 | deepseek_v4 | 0.009 | 0.165 | 0.047 | 0.028 | 0.046 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s4 | 1.000 | 150 | 0.840 | 0.835 | 0.824 | 0.835 | 0.840 | gpt4o | -0.005 | 0.144 | 0.061 | 0.034 | 0.059 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.claude46_O_s5 | 1.000 | 150 | 0.793 | 0.801 | 0.800 | 0.801 | 0.800 | deepseek_v4 | 7.3e-04 | 0.170 | 0.053 | 0.027 | 0.042 | 4838 | 332906 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s1 | 0.999 | 150 | 0.838 | 0.837 | 0.829 | 0.829 | 0.838 | gpt4o | -0.009 | 0.101 | 0.109 | 0.056 | 0.167 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s2 | 1.000 | 150 | 0.826 | 0.828 | 0.815 | 0.815 | 0.828 | claude46 | -0.013 | 0.109 | 0.082 | 0.044 | 0.131 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s3 | 0.999 | 149 | 0.825 | 0.835 | 0.808 | 0.808 | 0.835 | claude46 | -0.026 | 0.105 | 0.103 | 0.055 | 0.160 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s4 | 1.000 | 150 | 0.850 | 0.837 | 0.837 | 0.837 | 0.850 | gpt4o | -0.013 | 0.101 | 0.090 | 0.050 | 0.148 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.deepseek_v4_O_s5 | 1.000 | 150 | 0.850 | 0.833 | 0.830 | 0.830 | 0.850 | gpt4o | -0.020 | 0.105 | 0.063 | 0.039 | 0.113 | 2497 | 100375 |
| K | qwen3-4b-e2ckn.gpt4o_O_s1 | 1.000 | 150 | 0.836 | 0.833 | 0.824 | 0.836 | 0.833 | claude46 | 0.003 | 0.123 | 0.081 | 0.051 | 0.139 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s2 | 1.000 | 150 | 0.829 | 0.835 | 0.824 | 0.829 | 0.835 | claude46 | -0.006 | 0.119 | 0.079 | 0.033 | 0.103 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s3 | 1.000 | 150 | 0.817 | 0.822 | 0.805 | 0.817 | 0.822 | claude46 | -0.005 | 0.132 | 0.071 | 0.027 | 0.094 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s4 | 0.999 | 150 | 0.834 | 0.840 | 0.829 | 0.834 | 0.840 | claude46 | -0.006 | 0.120 | 0.071 | 0.030 | 0.092 | 4964 | 234276 |
| K | qwen3-4b-e2ckn.gpt4o_O_s5 | 1.000 | 150 | 0.838 | 0.840 | 0.825 | 0.838 | 0.840 | claude46 | -0.002 | 0.119 | 0.062 | 0.034 | 0.098 | 4964 | 234276 |

### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）

| condition | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| C | claude46 | O | 10 | 0.012 | 0.008 | 0.023 |
| C | deepseek_v4 | O | 10 | 0.017 | 0.011 | 0.034 |
| C | gpt4o | O | 10 | 0.006 | 0.005 | 0.013 |
| C | all | all | 30 | 0.012 | 0.009 | 0.030 |
| K | claude46 | O | 10 | 0.017 | 0.010 | 0.031 |
| K | deepseek_v4 | O | 10 | 0.015 | 0.009 | 0.026 |
| K | gpt4o | O | 10 | 0.010 | 0.007 | 0.020 |
| K | all | all | 30 | 0.014 | 0.009 | 0.029 |
| E1 | claude46 | O | 10 | 0.008 | 0.005 | 0.015 |
| E1 | deepseek_v4 | O | 10 | 0.011 | 0.006 | 0.021 |
| E1 | gpt4o | O | 10 | 0.009 | 0.008 | 0.020 |
| E1 | all | all | 30 | 0.009 | 0.006 | 0.020 |

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
