# E2c 分析（dev，variants T1, T3, T5, T6；rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed; freeze commit not given (tasks/e2c_plan.md §9)；auto-generated）

**E2c primary（own > other，条件 C）：PASS**（2/3 teacher 过）；**归因（C − K）：attributed to contestedness**（2/3）。

**dev 只作描述**（tasks/e2c_plan.md §5：test 每条件只跑一次，看 test 后不改任何量）；只有 results/e2c（test）是确认性的。

规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = 2000（seed 0），每个 run 重算 agreement，取 seed 均值，2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。

## 判定表（e2c_gaps.csv）

| condition | role | teacher | n_seeds | agree_own | agree_other_max | gap | CI | null_q95 | null_sd | null_n_pairs | exceeds_null | ci_above_zero | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | primary | gpt4o | 5 | 0.802 | 0.809 | -0.007 | [-0.045, 0.026] | 0.021 | 0.007 | 10 | False | False | False |
| C | primary | claude46 | 5 | 0.819 | 0.780 | 0.039 | [9.2e-04, 0.075] | 0.022 | 0.008 | 10 | True | True | True |
| C | primary | deepseek_v4 | 5 | 0.770 | 0.725 | 0.046 | [0.011, 0.078] | 0.022 | 0.008 | 10 | True | True | True |
| K | reference | gpt4o | 5 | 0.839 | 0.835 | 0.004 | [-0.034, 0.031] | 0.035 | 0.013 | 10 | False | False | False |
| K | reference | claude46 | 5 | 0.826 | 0.822 | 0.004 | [-0.040, 0.039] | 0.017 | 0.005 | 10 | False | False | False |
| K | reference | deepseek_v4 | 5 | 0.815 | 0.830 | -0.015 | [-0.062, 0.019] | 0.036 | 0.013 | 10 | False | False | False |
| E1 | reference | gpt4o | 5 | 0.856 | 0.856 | 3.0e-04 | [-0.040, 0.030] | 0.020 | 0.008 | 10 | False | False | False |
| E1 | reference | claude46 | 5 | 0.846 | 0.829 | 0.017 | [-0.021, 0.052] | 0.015 | 0.005 | 10 | True | False | False |
| E1 | reference | deepseek_v4 | 5 | 0.844 | 0.826 | 0.018 | [-0.025, 0.052] | 0.021 | 0.006 | 10 | False | False | False |

## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）

| teacher | gap_C | gap_K | diff | CI | ci_above_zero |
|---|---|---|---|---|---|
| gpt4o | -0.007 | 0.004 | -0.011 | [-0.041, 0.031] | False |
| claude46 | 0.039 | 0.004 | 0.035 | [0.008, 0.070] | True |
| deepseek_v4 | 0.046 | -0.015 | 0.061 | [0.032, 0.106] | True |

## 输入

| condition | label | glob | n_files | n_runs | n_rows | seeds_per_teacher | skipped_run_ids |
|---|---|---|---|---|---|---|---|
| C | E2c-C (contested) | runs/qwen3-4b-e2cnf/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| K | E2c-K (consensus control) | runs/qwen3-4b-e2ck/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| E1 | E1 (original train, reference) | runs/qwen3-4b/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |

## 描述

### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）

| condition | run_id | answer_rate | n_families | agree__gpt4o | agree__claude46 | agree__deepseek_v4 | agree_own | agree_other_max | other_argmax | gap | jsd_own | flip_rate | mean_jsd | s | n_examples | n_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | qwen3-4b-e2cnf.claude46_O_s1 | 1.000 | 150 | 0.777 | 0.815 | 0.758 | 0.815 | 0.777 | gpt4o | 0.038 | 0.148 | 0.109 | 0.041 | 0.146 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s2 | 1.000 | 150 | 0.796 | 0.835 | 0.778 | 0.835 | 0.796 | gpt4o | 0.039 | 0.142 | 0.093 | 0.045 | 0.141 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s3 | 1.000 | 150 | 0.782 | 0.819 | 0.766 | 0.819 | 0.782 | gpt4o | 0.037 | 0.154 | 0.101 | 0.046 | 0.144 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s4 | 1.000 | 150 | 0.780 | 0.817 | 0.771 | 0.817 | 0.780 | gpt4o | 0.037 | 0.147 | 0.124 | 0.046 | 0.160 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s5 | 1.000 | 150 | 0.767 | 0.810 | 0.760 | 0.810 | 0.767 | gpt4o | 0.043 | 0.148 | 0.119 | 0.047 | 0.129 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s1 | 1.000 | 150 | 0.735 | 0.710 | 0.783 | 0.783 | 0.735 | gpt4o | 0.048 | 0.139 | 0.211 | 0.148 | 0.391 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s2 | 1.000 | 150 | 0.723 | 0.703 | 0.771 | 0.771 | 0.723 | gpt4o | 0.048 | 0.145 | 0.192 | 0.130 | 0.369 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s3 | 1.000 | 150 | 0.730 | 0.702 | 0.770 | 0.770 | 0.730 | gpt4o | 0.040 | 0.135 | 0.200 | 0.130 | 0.356 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s4 | 1.000 | 150 | 0.716 | 0.687 | 0.756 | 0.756 | 0.716 | gpt4o | 0.040 | 0.143 | 0.224 | 0.154 | 0.428 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s5 | 1.000 | 150 | 0.720 | 0.700 | 0.771 | 0.771 | 0.720 | gpt4o | 0.052 | 0.140 | 0.197 | 0.140 | 0.381 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.gpt4o_O_s1 | 1.000 | 150 | 0.796 | 0.774 | 0.805 | 0.796 | 0.805 | deepseek_v4 | -0.009 | 0.141 | 0.196 | 0.121 | 0.355 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s2 | 1.000 | 150 | 0.807 | 0.796 | 0.810 | 0.807 | 0.810 | deepseek_v4 | -0.003 | 0.130 | 0.177 | 0.105 | 0.320 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s3 | 1.000 | 150 | 0.815 | 0.790 | 0.820 | 0.815 | 0.820 | deepseek_v4 | -0.005 | 0.137 | 0.183 | 0.118 | 0.347 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s4 | 1.000 | 150 | 0.793 | 0.771 | 0.802 | 0.793 | 0.802 | deepseek_v4 | -0.009 | 0.142 | 0.224 | 0.143 | 0.420 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s5 | 1.000 | 150 | 0.798 | 0.782 | 0.808 | 0.798 | 0.808 | deepseek_v4 | -0.010 | 0.143 | 0.191 | 0.123 | 0.359 | 2924 | 145922 |
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
| K | qwen3-4b-e2ck.claude46_O_s1 | 1.000 | 150 | 0.824 | 0.824 | 0.812 | 0.824 | 0.824 | gpt4o | 1.1e-04 | 0.145 | 0.056 | 0.029 | 0.044 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s2 | 1.000 | 150 | 0.833 | 0.835 | 0.827 | 0.835 | 0.833 | gpt4o | 0.002 | 0.143 | 0.057 | 0.028 | 0.055 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s3 | 1.000 | 150 | 0.803 | 0.817 | 0.792 | 0.817 | 0.803 | gpt4o | 0.014 | 0.158 | 0.056 | 0.030 | 0.057 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s4 | 1.000 | 150 | 0.841 | 0.833 | 0.822 | 0.833 | 0.841 | gpt4o | -0.008 | 0.141 | 0.058 | 0.033 | 0.070 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s5 | 1.000 | 150 | 0.810 | 0.822 | 0.799 | 0.822 | 0.810 | gpt4o | 0.012 | 0.150 | 0.068 | 0.032 | 0.077 | 5836 | 401877 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s1 | 1.000 | 150 | 0.815 | 0.824 | 0.803 | 0.803 | 0.824 | claude46 | -0.021 | 0.112 | 0.099 | 0.065 | 0.183 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s2 | 1.000 | 150 | 0.836 | 0.835 | 0.834 | 0.834 | 0.836 | gpt4o | -0.003 | 0.098 | 0.097 | 0.062 | 0.170 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s3 | 0.999 | 150 | 0.798 | 0.815 | 0.797 | 0.797 | 0.815 | claude46 | -0.019 | 0.113 | 0.112 | 0.076 | 0.199 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s4 | 0.999 | 150 | 0.848 | 0.847 | 0.832 | 0.832 | 0.848 | gpt4o | -0.016 | 0.102 | 0.093 | 0.054 | 0.149 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s5 | 1.000 | 150 | 0.828 | 0.824 | 0.810 | 0.810 | 0.828 | gpt4o | -0.017 | 0.109 | 0.086 | 0.050 | 0.158 | 5370 | 216426 |
| K | qwen3-4b-e2ck.gpt4o_O_s1 | 0.999 | 150 | 0.862 | 0.847 | 0.845 | 0.862 | 0.847 | claude46 | 0.015 | 0.107 | 0.069 | 0.034 | 0.086 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s2 | 1.000 | 150 | 0.829 | 0.824 | 0.817 | 0.829 | 0.824 | claude46 | 0.005 | 0.114 | 0.086 | 0.038 | 0.103 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s3 | 0.998 | 149 | 0.827 | 0.820 | 0.809 | 0.827 | 0.820 | claude46 | 0.007 | 0.126 | 0.068 | 0.028 | 0.075 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s4 | 1.000 | 150 | 0.828 | 0.833 | 0.808 | 0.828 | 0.833 | claude46 | -0.006 | 0.124 | 0.073 | 0.039 | 0.102 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s5 | 1.000 | 150 | 0.847 | 0.849 | 0.824 | 0.847 | 0.849 | claude46 | -0.002 | 0.108 | 0.072 | 0.029 | 0.081 | 5874 | 277098 |

### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）

| condition | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| C | claude46 | O | 10 | 0.011 | 0.008 | 0.022 |
| C | deepseek_v4 | O | 10 | 0.011 | 0.008 | 0.022 |
| C | gpt4o | O | 10 | 0.011 | 0.007 | 0.021 |
| C | all | all | 30 | 0.011 | 0.008 | 0.024 |
| K | claude46 | O | 10 | 0.009 | 0.005 | 0.017 |
| K | deepseek_v4 | O | 10 | 0.021 | 0.013 | 0.036 |
| K | gpt4o | O | 10 | 0.018 | 0.013 | 0.035 |
| K | all | all | 30 | 0.016 | 0.012 | 0.035 |
| E1 | claude46 | O | 10 | 0.008 | 0.005 | 0.015 |
| E1 | deepseek_v4 | O | 10 | 0.011 | 0.006 | 0.021 |
| E1 | gpt4o | O | 10 | 0.009 | 0.008 | 0.020 |
| E1 | all | all | 30 | 0.009 | 0.006 | 0.020 |

### 按 teacher 的训练规模（train_manifest.json 与 --sft-meta；O seed 共享同一 prompt 集）

| condition | teacher | n_runs | n_examples | n_target_tokens | n_families | order_stable_rate | n_dropped_order_unstable |
|---|---|---|---|---|---|---|---|
| C | gpt4o | 5 | 2924 | 145922 | nan | nan | nan |
| C | claude46 | 5 | 2764 | 207007 | nan | nan | nan |
| C | deepseek_v4 | 5 | 1990 | 88387 | nan | nan | nan |
| K | gpt4o | 5 | 5874 | 277098 | nan | nan | nan |
| K | claude46 | 5 | 5836 | 401877 | nan | nan | nan |
| K | deepseek_v4 | 5 | 5370 | 216426 | nan | nan | nan |
| E1 | gpt4o | 5 | 5619 | 279029 | nan | nan | nan |
| E1 | claude46 | 5 | 5642 | 447303 | nan | nan | nan |
| E1 | deepseek_v4 | 5 | 4936 | 221871 | nan | nan | nan |

注：JSD 受 teacher 校准混淆，只与 agreement 同报；flip rate 与 mean_jsd 不单独解读。
