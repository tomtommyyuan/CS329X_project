# E2c 分析（dev，variants T1, T3, T5, T6；rule pre-registered in tasks/e2c_plan.md §6 before any E2c run existed; freeze commit not given (tasks/e2c_plan.md §9)；auto-generated）

**E2c primary（own > other，条件 C）：FAIL**（0/3 teacher 过）；**归因（C − K）：attributed to contestedness**（2/3）。

**dev 只作描述**（tasks/e2c_plan.md §5：test 每条件只跑一次，看 test 后不改任何量）；只有 results/e2c（test）是确认性的。

规则（tasks/e2c_plan.md §6 原文，`vcd.analysis.e2c_metrics`）：gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]，agreement 为 symmetrized 多数行动一致率，与 E1 描述项同一函数（`e1_metrics.teacher_agreement`：cell 加权，p_sym = 0.5 的 cell 不计）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree_own| 的分布，取 q95（10 对，`e1_metrics.seed_noise_null`，不按 √n 缩放）；family bootstrap 95% CI：family 有放回重抽 B = 2000（seed 0），每个 run 重算 agreement，取 seed 均值，2.5 / 97.5 分位；三条件共用同一组重抽 family，所以 C − K 的 CI 是配对的。E2c primary：E2c-C 上 gap_T > q95 **且** CI 下界 > 0 的 teacher ≥ 2/3 → PASS，1/3 PARTIAL，0/3 FAIL。归因：gap_T(C) − gap_T(K) 的 CI 下界 > 0 的 teacher ≥ 2/3 → 效应归于争议性而非换源。E2c-E1 门（E1a / E1b）由 scripts/13 在同一批 run 上判，此处不重复。K 与 E1 行只作参照（同一规则的旗标，不出判定）。

## 判定表（e2c_gaps.csv）

| condition | role | teacher | n_seeds | agree_own | agree_other_max | gap | CI | null_q95 | null_sd | null_n_pairs | exceeds_null | ci_above_zero | passed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | primary | gpt4o | 5 | 0.818 | 0.799 | 0.019 | [-0.017, 0.042] | 0.016 | 0.005 | 10 | True | False | False |
| C | primary | claude46 | 5 | 0.834 | 0.799 | 0.036 | [-0.003, 0.078] | 0.018 | 0.006 | 10 | True | False | False |
| C | primary | deepseek_v4 | 5 | 0.767 | 0.740 | 0.027 | [-0.007, 0.057] | 0.013 | 0.005 | 10 | True | False | False |
| K | reference | gpt4o | 5 | 0.844 | 0.840 | 0.003 | [-0.036, 0.035] | 0.017 | 0.005 | 10 | False | False | False |
| K | reference | claude46 | 5 | 0.831 | 0.843 | -0.012 | [-0.055, 0.027] | 0.039 | 0.013 | 10 | False | False | False |
| K | reference | deepseek_v4 | 5 | 0.818 | 0.846 | -0.028 | [-0.068, 0.005] | 0.031 | 0.014 | 10 | False | False | False |

## 归因 C − K（e2c_attribution.csv；配对 family bootstrap）

| teacher | gap_C | gap_K | diff | CI | ci_above_zero |
|---|---|---|---|---|---|
| gpt4o | 0.019 | 0.003 | 0.016 | [-0.016, 0.048] | False |
| claude46 | 0.036 | -0.012 | 0.047 | [0.012, 0.097] | True |
| deepseek_v4 | 0.027 | -0.028 | 0.054 | [0.023, 0.096] | True |

## 输入

| condition | label | glob | n_files | n_runs | n_rows | seeds_per_teacher | skipped_run_ids |
|---|---|---|---|---|---|---|---|
| C | E2c-C (contested) | runs/smollm3-3b-e2c/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| K | E2c-K (consensus control) | runs/smollm3-3b-e2ck/*_O_s*/eval/dev_responses.jsonl | 15 | 15 | 22500 | gpt4o: 1,2,3,4,5; claude46: 1,2,3,4,5; deepseek_v4: 1,2,3,4,5 |  |
| E1 | E1 (original train, reference) | runs/smollm3-3b/*_O_s*/eval/dev_responses.jsonl | 0 | 0 | 0 | (missing) |  |

缺失条件（glob 无匹配，行已跳过）：E1（runs/smollm3-3b/*_O_s*/eval/dev_responses.jsonl）。

## 描述

### 每 run：与每个 teacher 的 agreement、gap、JSD、一致性、suggestibility s = δ(T5) − δ(T6)、训练规模（e2c_runs.csv）

| condition | run_id | answer_rate | n_families | agree__gpt4o | agree__claude46 | agree__deepseek_v4 | agree_own | agree_other_max | other_argmax | gap | jsd_own | flip_rate | mean_jsd | s | n_examples | n_target_tokens |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| C | smollm3-3b-e2c.claude46_O_s1 | 1.000 | 150 | 0.807 | 0.842 | 0.768 | 0.842 | 0.807 | gpt4o | 0.035 | 0.135 | 0.078 | 0.030 | 0.101 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s2 | 1.000 | 150 | 0.803 | 0.837 | 0.773 | 0.837 | 0.803 | gpt4o | 0.033 | 0.145 | 0.074 | 0.031 | 0.082 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s3 | 1.000 | 150 | 0.787 | 0.824 | 0.760 | 0.824 | 0.787 | gpt4o | 0.037 | 0.146 | 0.079 | 0.035 | 0.080 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s4 | 1.000 | 150 | 0.807 | 0.842 | 0.773 | 0.842 | 0.807 | gpt4o | 0.035 | 0.137 | 0.077 | 0.036 | 0.106 | 4838 | 351048 |
| C | smollm3-3b-e2c.claude46_O_s5 | 1.000 | 150 | 0.789 | 0.828 | 0.760 | 0.828 | 0.789 | gpt4o | 0.039 | 0.142 | 0.083 | 0.037 | 0.101 | 4838 | 351048 |
| C | smollm3-3b-e2c.deepseek_v4_O_s1 | 1.000 | 150 | 0.737 | 0.718 | 0.761 | 0.761 | 0.737 | gpt4o | 0.024 | 0.150 | 0.331 | 0.230 | 0.547 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s2 | 0.999 | 149 | 0.740 | 0.723 | 0.765 | 0.765 | 0.740 | gpt4o | 0.024 | 0.142 | 0.281 | 0.201 | 0.478 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s3 | 1.000 | 150 | 0.739 | 0.721 | 0.771 | 0.771 | 0.739 | gpt4o | 0.033 | 0.141 | 0.304 | 0.211 | 0.512 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s4 | 1.000 | 150 | 0.732 | 0.723 | 0.761 | 0.761 | 0.732 | gpt4o | 0.030 | 0.142 | 0.302 | 0.212 | 0.500 | 2497 | 110040 |
| C | smollm3-3b-e2c.deepseek_v4_O_s5 | 1.000 | 150 | 0.753 | 0.734 | 0.775 | 0.775 | 0.753 | gpt4o | 0.022 | 0.131 | 0.300 | 0.204 | 0.487 | 2497 | 110040 |
| C | smollm3-3b-e2c.gpt4o_O_s1 | 1.000 | 150 | 0.822 | 0.792 | 0.802 | 0.822 | 0.802 | deepseek_v4 | 0.021 | 0.120 | 0.189 | 0.118 | 0.348 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s2 | 1.000 | 150 | 0.815 | 0.783 | 0.798 | 0.815 | 0.798 | deepseek_v4 | 0.017 | 0.119 | 0.184 | 0.111 | 0.328 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s3 | 1.000 | 150 | 0.814 | 0.798 | 0.800 | 0.814 | 0.800 | deepseek_v4 | 0.014 | 0.121 | 0.177 | 0.108 | 0.335 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s4 | 1.000 | 150 | 0.810 | 0.783 | 0.793 | 0.810 | 0.793 | deepseek_v4 | 0.017 | 0.122 | 0.177 | 0.100 | 0.313 | 4964 | 243988 |
| C | smollm3-3b-e2c.gpt4o_O_s5 | 1.000 | 150 | 0.828 | 0.796 | 0.800 | 0.828 | 0.800 | deepseek_v4 | 0.028 | 0.117 | 0.190 | 0.118 | 0.338 | 4964 | 243988 |
| K | smollm3-3b-e2ck.claude46_O_s1 | 1.000 | 150 | 0.843 | 0.828 | 0.817 | 0.828 | 0.843 | gpt4o | -0.015 | 0.145 | 0.032 | 0.017 | 0.012 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s2 | 1.000 | 150 | 0.854 | 0.853 | 0.839 | 0.853 | 0.854 | gpt4o | -0.001 | 0.136 | 0.047 | 0.026 | 0.031 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s3 | 1.000 | 150 | 0.829 | 0.815 | 0.813 | 0.815 | 0.829 | gpt4o | -0.014 | 0.164 | 0.039 | 0.021 | 0.003 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s4 | 1.000 | 150 | 0.838 | 0.812 | 0.813 | 0.812 | 0.838 | gpt4o | -0.026 | 0.161 | 0.036 | 0.024 | 0.004 | 5836 | 401646 |
| K | smollm3-3b-e2ck.claude46_O_s5 | 1.000 | 150 | 0.848 | 0.847 | 0.820 | 0.847 | 0.848 | gpt4o | -0.001 | 0.144 | 0.028 | 0.023 | 0.039 | 5836 | 401646 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s1 | 1.000 | 150 | 0.848 | 0.838 | 0.827 | 0.827 | 0.848 | gpt4o | -0.022 | 0.108 | 0.097 | 0.062 | 0.184 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s2 | 1.000 | 150 | 0.857 | 0.844 | 0.825 | 0.825 | 0.857 | gpt4o | -0.032 | 0.116 | 0.051 | 0.027 | 0.079 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s3 | 1.000 | 150 | 0.848 | 0.835 | 0.820 | 0.820 | 0.848 | gpt4o | -0.028 | 0.111 | 0.083 | 0.046 | 0.125 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s4 | 1.000 | 150 | 0.821 | 0.812 | 0.795 | 0.795 | 0.821 | gpt4o | -0.026 | 0.122 | 0.084 | 0.046 | 0.143 | 5370 | 216330 |
| K | smollm3-3b-e2ck.deepseek_v4_O_s5 | 1.000 | 150 | 0.855 | 0.844 | 0.825 | 0.825 | 0.855 | gpt4o | -0.030 | 0.108 | 0.089 | 0.047 | 0.105 | 5370 | 216330 |
| K | smollm3-3b-e2ck.gpt4o_O_s1 | 1.000 | 150 | 0.845 | 0.835 | 0.815 | 0.845 | 0.835 | claude46 | 0.010 | 0.116 | 0.038 | 0.025 | 0.053 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s2 | 1.000 | 150 | 0.841 | 0.835 | 0.820 | 0.841 | 0.835 | claude46 | 0.007 | 0.116 | 0.068 | 0.040 | 0.113 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s3 | 1.000 | 150 | 0.833 | 0.840 | 0.813 | 0.833 | 0.840 | claude46 | -0.007 | 0.123 | 0.074 | 0.036 | 0.108 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s4 | 1.000 | 150 | 0.850 | 0.837 | 0.824 | 0.850 | 0.837 | claude46 | 0.014 | 0.115 | 0.063 | 0.037 | 0.098 | 5874 | 277030 |
| K | smollm3-3b-e2ck.gpt4o_O_s5 | 1.000 | 150 | 0.848 | 0.854 | 0.822 | 0.848 | 0.854 | claude46 | -0.006 | 0.111 | 0.047 | 0.023 | 0.055 | 5874 | 277030 |

### seed-pair null：|agree_own(seed a) − agree_own(seed b)|（e2c_seed_null.csv）

| condition | teacher | version | n_pairs | mean | sd | q95 |
|---|---|---|---|---|---|---|
| C | claude46 | O | 10 | 0.010 | 0.006 | 0.018 |
| C | deepseek_v4 | O | 10 | 0.007 | 0.005 | 0.013 |
| C | gpt4o | O | 10 | 0.009 | 0.005 | 0.016 |
| C | all | all | 30 | 0.009 | 0.005 | 0.018 |
| K | claude46 | O | 10 | 0.023 | 0.013 | 0.039 |
| K | deepseek_v4 | O | 10 | 0.014 | 0.014 | 0.031 |
| K | gpt4o | O | 10 | 0.008 | 0.005 | 0.017 |
| K | all | all | 30 | 0.015 | 0.013 | 0.037 |

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
