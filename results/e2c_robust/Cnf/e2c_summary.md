# E2c 分析（test，variants T1, T3, T5, T6；rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed; frozen at commit 22c7e9b；auto-generated）

**E2c primary（own > other，条件 C）：PASS**（2/3 teacher 过）；**归因（C − K）：not attributed**（1/3）。

规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = 2000（seed 0），每个 run 重算 agreement，取 seed 均值，2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。

## 判定表（e2c_gaps.csv）

| condition | role | teacher | n_seeds | agree_own | agree_other_max | gap | CI | null_q95 | null_sd | null_n_pairs | exceeds_null | ci_above_zero | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | primary | gpt4o | 5 | 0.762 | 0.770 | -0.007 | [-0.025, 0.011] | 0.020 | 0.007 | 10 | False | False | False |
| C | primary | claude46 | 5 | 0.823 | 0.797 | 0.026 | [0.003, 0.049] | 0.024 | 0.009 | 10 | True | True | True |
| C | primary | deepseek_v4 | 5 | 0.746 | 0.708 | 0.037 | [0.016, 0.058] | 0.034 | 0.010 | 10 | True | True | True |
| K | reference | gpt4o | 5 | 0.841 | 0.844 | -0.003 | [-0.027, 0.015] | 0.021 | 0.007 | 10 | False | False | False |
| K | reference | claude46 | 5 | 0.859 | 0.857 | 0.001 | [-0.023, 0.024] | 0.005 | 0.002 | 10 | False | False | False |
| K | reference | deepseek_v4 | 5 | 0.849 | 0.848 | 8.5e-04 | [-0.024, 0.018] | 0.015 | 0.006 | 10 | False | False | False |
| E1 | reference | gpt4o | 5 | 0.857 | 0.855 | 0.002 | [-0.022, 0.020] | 0.016 | 0.005 | 10 | False | False | False |
| E1 | reference | claude46 | 5 | 0.882 | 0.862 | 0.020 | [-0.006, 0.041] | 0.023 | 0.008 | 10 | False | False | False |
| E1 | reference | deepseek_v4 | 5 | 0.857 | 0.848 | 0.009 | [-0.015, 0.025] | 0.008 | 0.003 | 10 | True | False | False |

## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）

| teacher | gap_C | gap_K | diff | CI | ci_above_zero |
|---|---|---|---|---|---|
| gpt4o | -0.007 | -0.003 | -0.005 | [-0.022, 0.023] | False |
| claude46 | 0.026 | 0.001 | 0.025 | [-3.6e-04, 0.052] | False |
| deepseek_v4 | 0.037 | 8.5e-04 | 0.037 | [0.014, 0.067] | True |

## 输入

| condition | label | glob | n_files | n_runs | n_rows | seeds_per_teacher | skipped_run_ids |
|---|---|---|---|---|---|---|---|
| C | E2c-C (contested) | runs/qwen3-4b-e2cnf/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| K | E2c-K (consensus control) | runs/qwen3-4b-e2ck/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| E1 | E1 (original train, reference) | runs/qwen3-4b/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |

## 描述

### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）

| condition | run_id | answer_rate | n_families | agree__gpt4o | agree__claude46 | agree__deepseek_v4 | agree_own | agree_other_max | other_argmax | gap | jsd_own | flip_rate | mean_jsd | s | n_examples | n_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | qwen3-4b-e2cnf.claude46_O_s1 | 1.000 | 300 | 0.796 | 0.828 | 0.805 | 0.828 | 0.805 | deepseek_v4 | 0.023 | 0.152 | 0.164 | 0.102 | 0.183 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s2 | 1.000 | 300 | 0.785 | 0.825 | 0.801 | 0.825 | 0.801 | deepseek_v4 | 0.024 | 0.147 | 0.170 | 0.099 | 0.177 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s3 | 1.000 | 300 | 0.781 | 0.823 | 0.794 | 0.823 | 0.794 | deepseek_v4 | 0.029 | 0.150 | 0.141 | 0.078 | 0.134 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s4 | 1.000 | 300 | 0.779 | 0.806 | 0.789 | 0.806 | 0.789 | deepseek_v4 | 0.017 | 0.155 | 0.174 | 0.095 | 0.178 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.claude46_O_s5 | 0.999 | 299 | 0.785 | 0.831 | 0.795 | 0.831 | 0.795 | deepseek_v4 | 0.036 | 0.147 | 0.160 | 0.102 | 0.183 | 2764 | 207007 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s1 | 1.000 | 300 | 0.695 | 0.677 | 0.730 | 0.730 | 0.695 | gpt4o | 0.035 | 0.181 | 0.271 | 0.195 | 0.493 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s2 | 1.000 | 300 | 0.692 | 0.681 | 0.734 | 0.734 | 0.692 | gpt4o | 0.042 | 0.172 | 0.272 | 0.172 | 0.457 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s3 | 1.000 | 300 | 0.724 | 0.711 | 0.766 | 0.766 | 0.724 | gpt4o | 0.042 | 0.157 | 0.264 | 0.185 | 0.467 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s4 | 1.000 | 300 | 0.718 | 0.707 | 0.752 | 0.752 | 0.718 | gpt4o | 0.035 | 0.166 | 0.270 | 0.191 | 0.481 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.deepseek_v4_O_s5 | 1.000 | 300 | 0.712 | 0.695 | 0.745 | 0.745 | 0.712 | gpt4o | 0.033 | 0.170 | 0.285 | 0.199 | 0.486 | 1990 | 88387 |
| C | qwen3-4b-e2cnf.gpt4o_O_s1 | 1.000 | 300 | 0.758 | 0.732 | 0.767 | 0.758 | 0.767 | deepseek_v4 | -0.008 | 0.199 | 0.249 | 0.186 | 0.442 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s2 | 1.000 | 300 | 0.749 | 0.712 | 0.754 | 0.749 | 0.754 | deepseek_v4 | -0.005 | 0.205 | 0.264 | 0.194 | 0.476 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s3 | 1.000 | 300 | 0.769 | 0.741 | 0.775 | 0.769 | 0.775 | deepseek_v4 | -0.006 | 0.190 | 0.236 | 0.172 | 0.410 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s4 | 1.000 | 300 | 0.767 | 0.736 | 0.771 | 0.767 | 0.771 | deepseek_v4 | -0.004 | 0.190 | 0.231 | 0.166 | 0.426 | 2924 | 145922 |
| C | qwen3-4b-e2cnf.gpt4o_O_s5 | 0.999 | 299 | 0.769 | 0.750 | 0.783 | 0.769 | 0.783 | deepseek_v4 | -0.014 | 0.178 | 0.225 | 0.163 | 0.383 | 2924 | 145922 |
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
| K | qwen3-4b-e2ck.claude46_O_s1 | 0.999 | 299 | 0.848 | 0.861 | 0.867 | 0.861 | 0.867 | deepseek_v4 | -0.006 | 0.127 | 0.047 | 0.021 | 0.030 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s2 | 1.000 | 300 | 0.841 | 0.855 | 0.858 | 0.855 | 0.858 | deepseek_v4 | -0.003 | 0.131 | 0.045 | 0.018 | 0.038 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s3 | 1.000 | 300 | 0.842 | 0.860 | 0.855 | 0.860 | 0.855 | deepseek_v4 | 0.005 | 0.127 | 0.047 | 0.023 | 0.045 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s4 | 1.000 | 299 | 0.844 | 0.859 | 0.859 | 0.859 | 0.859 | deepseek_v4 | -3.9e-04 | 0.128 | 0.053 | 0.025 | 0.056 | 5836 | 401877 |
| K | qwen3-4b-e2ck.claude46_O_s5 | 1.000 | 300 | 0.840 | 0.859 | 0.848 | 0.859 | 0.848 | deepseek_v4 | 0.011 | 0.123 | 0.054 | 0.024 | 0.055 | 5836 | 401877 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s1 | 1.000 | 300 | 0.829 | 0.838 | 0.839 | 0.839 | 0.838 | claude46 | 6.8e-04 | 0.101 | 0.094 | 0.058 | 0.167 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s2 | 1.000 | 300 | 0.843 | 0.849 | 0.849 | 0.849 | 0.849 | claude46 | 9.3e-05 | 0.095 | 0.091 | 0.050 | 0.146 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s3 | 1.000 | 300 | 0.846 | 0.853 | 0.849 | 0.849 | 0.853 | claude46 | -0.004 | 0.093 | 0.090 | 0.062 | 0.173 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s4 | 1.000 | 300 | 0.849 | 0.846 | 0.858 | 0.858 | 0.849 | gpt4o | 0.009 | 0.090 | 0.081 | 0.039 | 0.121 | 5370 | 216426 |
| K | qwen3-4b-e2ck.deepseek_v4_O_s5 | 1.000 | 300 | 0.847 | 0.852 | 0.851 | 0.851 | 0.852 | claude46 | -8.9e-04 | 0.093 | 0.074 | 0.043 | 0.123 | 5370 | 216426 |
| K | qwen3-4b-e2ck.gpt4o_O_s1 | 1.000 | 300 | 0.845 | 0.848 | 0.850 | 0.845 | 0.850 | deepseek_v4 | -0.005 | 0.119 | 0.051 | 0.026 | 0.076 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s2 | 1.000 | 300 | 0.839 | 0.831 | 0.838 | 0.839 | 0.838 | deepseek_v4 | 3.5e-04 | 0.122 | 0.061 | 0.028 | 0.083 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s3 | 1.000 | 300 | 0.834 | 0.829 | 0.838 | 0.834 | 0.838 | deepseek_v4 | -0.005 | 0.126 | 0.052 | 0.024 | 0.066 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s4 | 1.000 | 300 | 0.855 | 0.856 | 0.851 | 0.855 | 0.856 | claude46 | -0.001 | 0.113 | 0.052 | 0.028 | 0.084 | 5874 | 277098 |
| K | qwen3-4b-e2ck.gpt4o_O_s5 | 1.000 | 300 | 0.834 | 0.835 | 0.837 | 0.834 | 0.837 | deepseek_v4 | -0.003 | 0.122 | 0.054 | 0.024 | 0.073 | 5874 | 277098 |

### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）

| condition | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| C | claude46 | O | 10 | 0.011 | 0.009 | 0.024 |
| C | deepseek_v4 | O | 10 | 0.018 | 0.010 | 0.034 |
| C | gpt4o | O | 10 | 0.010 | 0.007 | 0.020 |
| C | all | all | 30 | 0.013 | 0.009 | 0.029 |
| K | claude46 | O | 10 | 0.003 | 0.002 | 0.005 |
| K | deepseek_v4 | O | 10 | 0.008 | 0.006 | 0.015 |
| K | gpt4o | O | 10 | 0.011 | 0.007 | 0.021 |
| K | all | all | 30 | 0.007 | 0.006 | 0.020 |
| E1 | claude46 | O | 10 | 0.011 | 0.008 | 0.023 |
| E1 | deepseek_v4 | O | 10 | 0.004 | 0.003 | 0.008 |
| E1 | gpt4o | O | 10 | 0.008 | 0.005 | 0.016 |
| E1 | all | all | 30 | 0.008 | 0.006 | 0.019 |

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
