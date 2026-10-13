# E2c 分析（test，variants T1, T3, T5, T6；rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed; frozen at commit 4ae6ccb；auto-generated）

**E2c primary（own > other，条件 C）：PASS**（2/3 teacher 过）；**归因（C − K）：attributed to contestedness**（2/3）。

规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = 2000（seed 0），每个 run 重算 agreement，取 seed 均值，2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。

## 判定表（e2c_gaps.csv）

| condition | role | teacher | n_seeds | agree_own | agree_other_max | gap | CI | null_q95 | null_sd | null_n_pairs | exceeds_null | ci_above_zero | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | primary | gpt4o | 5 | 0.817 | 0.810 | 0.007 | [-0.014, 0.024] | 0.014 | 0.004 | 10 | False | False | False |
| C | primary | claude46 | 5 | 0.859 | 0.828 | 0.031 | [0.008, 0.050] | 0.027 | 0.009 | 10 | True | True | True |
| C | primary | deepseek_v4 | 5 | 0.760 | 0.733 | 0.027 | [0.007, 0.044] | 0.015 | 0.005 | 10 | True | True | True |
| K | reference | gpt4o | 5 | 0.852 | 0.853 | -0.001 | [-0.023, 0.017] | 0.014 | 0.006 | 10 | False | False | False |
| K | reference | claude46 | 5 | 0.865 | 0.862 | 0.003 | [-0.022, 0.022] | 0.013 | 0.004 | 10 | False | False | False |
| K | reference | deepseek_v4 | 5 | 0.850 | 0.858 | -0.008 | [-0.031, 0.008] | 0.019 | 0.007 | 10 | False | False | False |

## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）

| teacher | gap_C | gap_K | diff | CI | ci_above_zero |
|---|---|---|---|---|---|
| gpt4o | 0.007 | -0.001 | 0.008 | [-0.009, 0.027] | False |
| claude46 | 0.031 | 0.003 | 0.028 | [0.005, 0.054] | True |
| deepseek_v4 | 0.027 | -0.008 | 0.034 | [0.012, 0.063] | True |

## 输入

| condition | label | glob | n_files | n_runs | n_rows | seeds_per_teacher | skipped_run_ids |
|---|---|---|---|---|---|---|---|
| C | E2c-C (contested) | runs/smollm3-3b-e2c/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| K | E2c-K (consensus control) | runs/smollm3-3b-e2ck/*_O_s*/eval/test_responses.jsonl | 15 | 15 | 45000 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| E1 | E1 (original train, reference) | runs/smollm3-3b/*_O_s*/eval/test_responses.jsonl | 0 | 0 | 0 | (missing) |  |

缺失条件（glob 无匹配，行已跳过）：E1（runs/smollm3-3b/*_O_s*/eval/test_responses.jsonl）。

## 描述

### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）

| condition | run_id | answer_rate | n_families | agree__gpt4o | agree__claude46 | agree__deepseek_v4 | agree_own | agree_other_max | other_argmax | gap | jsd_own | flip_rate | mean_jsd | s | n_examples | n_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | smollm3-3b-e2c.claude46_O_s1 | 1.000 | 300 | 0.816 | 0.847 | 0.816 | 0.847 | 0.816 | gpt4o | 0.031 | 0.124 | 0.093 | 0.035 | 0.094 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s2 | 1.000 | 300 | 0.817 | 0.849 | 0.807 | 0.849 | 0.817 | gpt4o | 0.032 | 0.123 | 0.108 | 0.040 | 0.081 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s3 | 1.000 | 300 | 0.837 | 0.869 | 0.829 | 0.869 | 0.837 | gpt4o | 0.032 | 0.120 | 0.068 | 0.036 | 0.062 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s4 | 1.000 | 300 | 0.825 | 0.855 | 0.833 | 0.855 | 0.833 | deepseek_v4 | 0.022 | 0.122 | 0.084 | 0.039 | 0.096 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s5 | 1.000 | 300 | 0.835 | 0.875 | 0.838 | 0.875 | 0.838 | deepseek_v4 | 0.037 | 0.113 | 0.079 | 0.035 | 0.085 | 4838 | 351048 |
| C | smollm3-3b-e2c.deepseek_v4_O_s1 | 1.000 | 299 | 0.729 | 0.719 | 0.761 | 0.761 | 0.729 | gpt4o | 0.032 | 0.164 | 0.300 | 0.222 | 0.525 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s2 | 1.000 | 300 | 0.727 | 0.723 | 0.757 | 0.757 | 0.727 | gpt4o | 0.030 | 0.151 | 0.291 | 0.207 | 0.504 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s3 | 1.000 | 300 | 0.734 | 0.719 | 0.753 | 0.753 | 0.734 | gpt4o | 0.019 | 0.155 | 0.303 | 0.217 | 0.535 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s4 | 1.000 | 300 | 0.731 | 0.727 | 0.758 | 0.758 | 0.731 | gpt4o | 0.027 | 0.160 | 0.291 | 0.214 | 0.511 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s5 | 1.000 | 300 | 0.745 | 0.734 | 0.770 | 0.770 | 0.745 | gpt4o | 0.025 | 0.146 | 0.274 | 0.192 | 0.469 | 2497 | 110040 |
| C | smollm3-3b-e2c.gpt4o_O_s1 | 1.000 | 300 | 0.825 | 0.805 | 0.817 | 0.825 | 0.817 | deepseek_v4 | 0.009 | 0.137 | 0.194 | 0.114 | 0.326 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s2 | 1.000 | 300 | 0.818 | 0.804 | 0.803 | 0.818 | 0.804 | claude46 | 0.014 | 0.138 | 0.182 | 0.115 | 0.325 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s3 | 1.000 | 300 | 0.809 | 0.795 | 0.807 | 0.809 | 0.807 | deepseek_v4 | 0.002 | 0.142 | 0.193 | 0.104 | 0.324 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s4 | 1.000 | 300 | 0.819 | 0.801 | 0.814 | 0.819 | 0.814 | deepseek_v4 | 0.005 | 0.142 | 0.150 | 0.093 | 0.291 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s5 | 1.000 | 300 | 0.813 | 0.799 | 0.807 | 0.813 | 0.807 | deepseek_v4 | 0.006 | 0.139 | 0.184 | 0.111 | 0.326 | 4964 | 243988 |
| K | smollm3-3b-e2ck.claude46_O_s1 | 1.000 | 300 | 0.866 | 0.874 | 0.863 | 0.874 | 0.866 | gpt4o | 0.008 | 0.119 | 0.038 | 0.018 | 0.005 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s2 | 1.000 | 300 | 0.863 | 0.866 | 0.862 | 0.866 | 0.863 | gpt4o | 0.003 | 0.122 | 0.041 | 0.017 | 0.012 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s3 | 1.000 | 300 | 0.856 | 0.862 | 0.851 | 0.862 | 0.856 | gpt4o | 0.006 | 0.121 | 0.050 | 0.019 | 0.011 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s4 | 1.000 | 300 | 0.851 | 0.860 | 0.850 | 0.860 | 0.851 | gpt4o | 0.009 | 0.126 | 0.044 | 0.018 | 0.012 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s5 | 1.000 | 300 | 0.874 | 0.866 | 0.853 | 0.866 | 0.874 | gpt4o | -0.008 | 0.126 | 0.039 | 0.017 | 0.027 | 5836 | 401646 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s1 | 1.000 | 300 | 0.851 | 0.857 | 0.845 | 0.845 | 0.857 | claude46 | -0.012 | 0.088 | 0.112 | 0.068 | 0.192 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s2 | 1.000 | 300 | 0.867 | 0.869 | 0.862 | 0.862 | 0.869 | claude46 | -0.008 | 0.088 | 0.065 | 0.035 | 0.095 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s3 | 1.000 | 300 | 0.851 | 0.849 | 0.845 | 0.845 | 0.851 | gpt4o | -0.006 | 0.090 | 0.087 | 0.050 | 0.129 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s4 | 1.000 | 300 | 0.850 | 0.853 | 0.842 | 0.842 | 0.853 | claude46 | -0.011 | 0.096 | 0.094 | 0.048 | 0.136 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s5 | 1.000 | 300 | 0.851 | 0.859 | 0.858 | 0.858 | 0.859 | claude46 | -0.001 | 0.087 | 0.070 | 0.036 | 0.088 | 5370 | 216330 |
| K | smollm3-3b-e2ck.gpt4o_O_s1 | 1.000 | 300 | 0.846 | 0.856 | 0.843 | 0.846 | 0.856 | claude46 | -0.010 | 0.118 | 0.056 | 0.028 | 0.049 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s2 | 1.000 | 300 | 0.845 | 0.838 | 0.847 | 0.845 | 0.847 | deepseek_v4 | -0.001 | 0.115 | 0.066 | 0.037 | 0.089 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s3 | 1.000 | 300 | 0.859 | 0.861 | 0.852 | 0.859 | 0.861 | claude46 | -0.002 | 0.110 | 0.063 | 0.033 | 0.091 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s4 | 1.000 | 300 | 0.848 | 0.848 | 0.845 | 0.848 | 0.848 | claude46 | -2.2e-04 | 0.117 | 0.057 | 0.035 | 0.085 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s5 | 1.000 | 300 | 0.859 | 0.851 | 0.840 | 0.859 | 0.851 | claude46 | 0.008 | 0.104 | 0.051 | 0.026 | 0.043 | 5874 | 277030 |

### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）

| condition | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| C | claude46 | O | 10 | 0.015 | 0.009 | 0.027 |
| C | deepseek_v4 | O | 10 | 0.007 | 0.005 | 0.015 |
| C | gpt4o | O | 10 | 0.008 | 0.004 | 0.014 |
| C | all | all | 30 | 0.010 | 0.007 | 0.024 |
| K | claude46 | O | 10 | 0.006 | 0.004 | 0.013 |
| K | deepseek_v4 | O | 10 | 0.011 | 0.007 | 0.019 |
| K | gpt4o | O | 10 | 0.008 | 0.006 | 0.014 |
| K | all | all | 30 | 0.008 | 0.006 | 0.017 |

### 按 teacher 的训练规模（train_manifest.json 与 --sft-meta；O seed 共享同一 prompt 集）

| condition | teacher | n_runs | n_examples | n_target_tokens | n_families | order_stable_rate | n_dropped_order_unstable |
|---|---|---|---|---|---|---|---|
| C | gpt4o | 5 | 4964 | 243988 | nan | nan | nan |
| C | claude46 | 5 | 4838 | 351048 | nan | nan | nan |
| C | deepseek_v4 | 5 | 2497 | 110040 | nan | nan | nan |
| K | gpt4o | 5 | 5874 | 277030 | nan | nan | nan |
| K | claude46 | 5 | 5836 | 401646 | nan | nan | nan |
| K | deepseek_v4 | 5 | 5370 | 216330 | nan | nan | nan |

注：JSD 受 teacher 校准混淆，只与 agreement 同报；flip rate 与 mean_jsd 不单独解读。
