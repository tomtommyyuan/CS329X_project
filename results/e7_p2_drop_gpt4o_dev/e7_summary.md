# E7 黑盒溯源（dev，variants T1, T3, T5, T6；E7 detector, tau rule, metrics and verdict pre-registered in tasks/e7_plan.md §3-§4 before any provenance result; not yet frozen (freeze commit pending)；auto-generated）

**主判定（E2c-C 的 O 学生，基座已知，字母概率 readout，全部探针）：不可行**（0/2 个 teacher 的召回 Wilson 下界 > 1/3：无；开集 FPR 0.029（≤ 10%）；τ = 0.026）。

**dev = 标定 split，以下全部只作描述**（tasks/e7_plan.md §4：阈值只在 dev 定，test 冻结后只跑一次，`--calibration` 复用本次写出的 calibration.json）。

规则（tasks/e7_plan.md §3–4 原文，`vcd.analysis.provenance`）：a_t = run 与 teacher t 的 symmetrized 多数行动一致率（`e1_metrics.teacher_agreement`，p_sym = 0.5 的 cell 不计）；基座已知 s_t = a_t − a_t(S_0)，基座未知 s_t = a_t − mean_t' a_t'；t* = argmax s_t，margin = s_t* − 第二大，margin > τ 判为 t*，否则不判定；τ = 使 dev 负例（K、K_n、R、S_0）被判为任一 teacher 的比例 ≤ 5% 的最小值（负例 < 20 时 τ = 0），每个检测器配置（变体 × readout × 探针子集 × 预算）各一个，test 原样复用；召回 Wilson 95% CI（不判定计错），macro 召回，开集 FPR，一对多 AUROC（以 s_t 为分数，负类含 none），随机参照 (1/3)(1 − 不判定率)，teacher 标签在该网格可判定 run 间置换 10,000 次的 p（seed 为近复本，p 只作描述）。主判定：E2c-C 的 15 个 O 学生，基座已知，字母概率，全部探针：召回 Wilson 下界 > 1/3 的 teacher ≥ 2/3 → 溯源可行（有条件），1/3 → 部分，0/3 → 不可行，并报开集 FPR 是否 ≤ 10%。

## 候选集与真值（phase 2：候选 = 检测器比对的 teacher；真值 = run id 里的 teacher）

候选 6 个：claude46, deepseek_v4, gpt41, gpt4o_mini, gpt4_0613, claude_haiku45（已去掉 gpt4o）；真值 teacher：claude46, deepseek_v4, gpt4o；真 teacher 不在候选集的 run：55（真值 gpt4o，见 e7_absent.csv）；家族：claude46:anthropic, claude_haiku45:anthropic, deepseek_v4:deepseek, gpt41:openai, gpt4_0613:openai, gpt4o:openai, gpt4o_mini:openai；calibration 键 `claude46,claude_haiku45,deepseek_v4,gpt41,gpt4_0613,gpt4o_mini`。主判定的 teacher 数 = 主组里有学生的候选（2）。

## 标定（calibration.json，本次写出）

负例 34 个（E1, K, K_n）；基座参照 = prior（596 个有效 cell / 600）；teacher 分歧 cell 137 / 600；family 150；重复 200；seed 0。

| configuration | tau | n_neg | n_margins | n_attributed | fpr_at_tau | fallback | note |
|---|---|---|---|---|---|---|---|
| main|probability|all|base_known | 0.026 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| main|probability|all|base_unknown | 0.020 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| main|probability|disagreement|base_known | 0.088 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| main|probability|disagreement|base_unknown | 0.073 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| loso|probability|all|base_known | 0.026 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| loso|probability|all|base_unknown | 0.020 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| logo|probability|all|base_known | 0.022 | 49 | 49 | 2 | 0.041 | False | 49 negatives, at most 2 may be attributed |
| logo|probability|all|base_unknown | 0.018 | 49 | 49 | 2 | 0.041 | False | 49 negatives, at most 2 may be attributed |
| main|sampled_n1|all|base_known | 0.024 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n1|all|base_unknown | 0.016 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n3|all|base_known | 0.024 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n3|all|base_unknown | 0.016 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n10|all|base_known | 0.025 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n10|all|base_unknown | 0.017 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget30|base_known | 0.060 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget30|base_unknown | 0.065 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget60|base_known | 0.046 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget60|base_unknown | 0.042 | 6800 | 6800 | 338 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget100|base_known | 0.034 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget100|base_unknown | 0.028 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |

## 主表：基座已知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.723 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E2c_C | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.223 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E2c_C | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E1 | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.933 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E1 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.954 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E1 | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E3 | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.882 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.959 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3 | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E3 | F | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.903 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3 | F | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.954 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3 | F | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E3 | C | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.908 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3 | C | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.946 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3 | C | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E3c | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.621 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3c | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.156 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3c | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E3c | F | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.595 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3c | F | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.149 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3c | F | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E3c | C | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.562 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3c | C | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.144 | nan | nan | nan | 0.029 | 34 | 0.026 |
| E3c | C | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| Cnf | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.208 | nan | nan | nan | 0.029 | 34 | 0.026 |
| Cnf | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.164 | nan | nan | nan | 0.029 | 34 | 0.026 |
| Cnf | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.026 |
| E1 | R | none | 3 | 3 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 3 | 0.026 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.026 |
| K | O | none | 15 | 14 | 0.933 | [nan, nan] | 0.933 | nan | nan | nan | nan | 0.067 | 15 | 0.026 |
| K_n | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.026 |

## 主表：基座未知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E2c_C | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E2c_C | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E1 | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.944 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E1 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E1 | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E3 | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.938 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3 | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E3 | F | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3 | F | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3 | F | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E3 | C | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3 | C | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3 | C | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E3c | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3c | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3c | O | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E3c | F | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3c | F | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3c | F | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| E3c | C | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3c | C | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| E3c | C | macro | 10 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 | 34 | 0.020 |
| Cnf | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| Cnf | O | deepseek_v4 | 5 | 2 | 0.400 | [0.118, 0.769] | 0.600 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.020 |
| Cnf | O | macro | 10 | 2 | 0.200 | [nan, nan] | 0.800 | nan | 0.200 | 0.033 | 0.231 | 0.029 | 34 | 0.020 |
| E1 | R | none | 3 | 2 | 0.667 | [nan, nan] | 0.667 | nan | nan | nan | nan | 0.333 | 3 | 0.020 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.020 |
| K | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.020 |
| K_n | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.020 |

## 真 teacher 不在候选集（e7_absent.csv；概率 readout，全部 cell，calibrated τ；这些 run 不进召回 / AUROC，也不进任何标定）

### 基座已知（τ = 0.026）

| grid | version | role | truth | truth_family | n | same_family | other_family | unattributed | attributed_to |
|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E1 | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3 | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3 | F | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3 | C | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3c | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3c | F | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3c | C | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| Cnf | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| Cnf_5ep | O | descriptive | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E2c_C_3ep | O | descriptive | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| all_core | all | core | gpt4o | openai | 45 | 0/45 (0.000 [0.000, 0.079]) | 0/45 (0.000 [0.000, 0.079]) | 45/45 (1.000 [0.921, 1.000]) | — |

- 基座已知，gpt4o（家族 openai）的学生、候选集不含 gpt4o：E2c_C O 学生（5 个 run）：**0/5 判为同家族候选**（—），0/5 判为其他家族（—），5/5 不判定；全部 core 网格（45 个 run）：**0/45 判为同家族候选**（—），0/45 判为其他家族（—），45/45 不判定。

### 基座未知（τ = 0.020）

| grid | version | role | truth | truth_family | n | same_family | other_family | unattributed | attributed_to |
|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E1 | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3 | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3 | F | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3 | C | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3c | O | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3c | F | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| E3c | C | core | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| Cnf | O | core | gpt4o | openai | 5 | 1/5 (0.200 [0.036, 0.624]) | 0/5 (0.000 [0.000, 0.434]) | 4/5 (0.800 [0.376, 0.964]) | gpt4o_mini 1 |
| Cnf_5ep | O | descriptive | gpt4o | openai | 5 | 2/5 (0.400 [0.118, 0.769]) | 0/5 (0.000 [0.000, 0.434]) | 3/5 (0.600 [0.231, 0.882]) | gpt4o_mini 2 |
| E2c_C_3ep | O | descriptive | gpt4o | openai | 5 | 0/5 (0.000 [0.000, 0.434]) | 0/5 (0.000 [0.000, 0.434]) | 5/5 (1.000 [0.566, 1.000]) | — |
| all_core | all | core | gpt4o | openai | 45 | 1/45 (0.022 [0.004, 0.116]) | 0/45 (0.000 [0.000, 0.079]) | 44/45 (0.978 [0.884, 0.996]) | gpt4o_mini 1 |

- 基座未知，gpt4o（家族 openai）的学生、候选集不含 gpt4o：E2c_C O 学生（5 个 run）：**0/5 判为同家族候选**（—），0/5 判为其他家族（—），5/5 不判定；全部 core 网格（45 个 run）：**1/45 判为同家族候选**（gpt4o_mini 1），0/45 判为其他家族（—），44/45 不判定。

## 分歧探针（三家多数行动不全同的 cell，137 / 600；τ = 该配置自标定（calibrated）；全 cell 的 τ 作灵敏度（fixed_all_cells，只列 macro 行））

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.088 | E2c_C | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E2c_C | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E1 | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.977 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E1 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E1 | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E3 | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.979 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3 | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E3 | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.992 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.992 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3 | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E3 | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.985 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3 | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E3c | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3c | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.979 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3c | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E3c | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.982 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3c | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | E3c | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.962 | nan | nan | nan | 0.029 |
| base_known | 0.088 | E3c | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.088 | Cnf | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.987 | nan | nan | nan | 0.029 |
| base_known | 0.088 | Cnf | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.029 |
| base_known | 0.088 | Cnf | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | E2c_C | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.985 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E2c_C | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | E1 | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.944 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E1 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.974 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E1 | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | E3 | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.949 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3 | O | deepseek_v4 | 5 | 0.200 | [0.036, 0.624] | 0.800 | 0.974 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3 | O | macro | 10 | 0.100 | [nan, nan] | 0.900 | nan | 0.100 | 0.017 | 0.499 | 0.029 |
| base_unknown | 0.073 | E3 | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.974 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3 | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | E3 | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3 | C | deepseek_v4 | 5 | 0.200 | [0.036, 0.624] | 0.800 | 0.974 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3 | C | macro | 10 | 0.100 | [nan, nan] | 0.900 | nan | 0.100 | 0.017 | 0.503 | 0.029 |
| base_unknown | 0.073 | E3c | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3c | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.979 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3c | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | E3c | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3c | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | E3c | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.974 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | E3c | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.073 | Cnf | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 0.600 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | Cnf | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.029 |
| base_unknown | 0.073 | Cnf | O | macro | 10 | 0.000 | [nan, nan] | 0.800 | nan | 0.000 | 0.033 | 1.000 | 0.029 |

| detector | tau_policy | tau | grid | version | n | macro_recall | unattributed_rate | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|
| base_known | fixed_all_cells | 0.026 | E2c_C | O | 10 | 0.000 | 0.500 | 0.083 | 1.000 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E1 | O | 10 | 0.000 | 0.400 | 0.100 | 1.000 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E3 | O | 10 | 0.000 | 0.400 | 0.100 | 1.000 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E3 | F | 10 | 0.000 | 0.700 | 0.050 | 1.000 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E3 | C | 10 | 0.000 | 0.400 | 0.100 | 1.000 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E3c | O | 10 | 0.100 | 0.500 | 0.083 | 0.496 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E3c | F | 10 | 0.200 | 0.400 | 0.100 | 0.222 | 0.824 |
| base_known | fixed_all_cells | 0.026 | E3c | C | 10 | 0.000 | 0.600 | 0.067 | 1.000 | 0.824 |
| base_known | fixed_all_cells | 0.026 | Cnf | O | 10 | 0.100 | 0.400 | 0.100 | 0.497 | 0.824 |
| base_unknown | fixed_all_cells | 0.020 | E2c_C | O | 10 | 0.400 | 0.300 | 0.117 | 0.023 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E1 | O | 10 | 0.500 | 0.100 | 0.150 | 0.004 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E3 | O | 10 | 0.200 | 0.500 | 0.083 | 0.225 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E3 | F | 10 | 0.500 | 0.200 | 0.133 | 0.004 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E3 | C | 10 | 0.500 | 0.200 | 0.133 | 0.005 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E3c | O | 10 | 0.200 | 0.600 | 0.067 | 0.281 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E3c | F | 10 | 0.500 | 0.400 | 0.100 | 0.043 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | E3c | C | 10 | 0.100 | 0.600 | 0.067 | 0.495 | 0.559 |
| base_unknown | fixed_all_cells | 0.020 | Cnf | O | 10 | 0.500 | 0.200 | 0.133 | 0.019 | 0.559 |

## 采样 readout：n = 1 / 3 / 10 个答案取多数（每 cell 两序各抽；均值 [2.5, 97.5] 分位，e7_sampled.csv）

macro 召回（行 = 检测器 × 网格，列 = n）：

| detector | grid | version | 1 | 3 | 10 |
|---|---|---|---|---|---|
| base_known | E2c_C | O | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E1 | O | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E3 | O | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E3 | F | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E3 | C | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E3c | O | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E3c | F | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | E3c | C | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | Cnf | O | 0.003 [0.000, 0.003] | 0.001 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_unknown | E2c_C | O | 0.029 [0.000, 0.100] | 0.024 [0.000, 0.103] | 0.006 [0.000, 0.100] |
| base_unknown | E1 | O | 0.013 [0.000, 0.100] | 0.006 [0.000, 0.100] | 5.0e-04 [0.000, 0.000] |
| base_unknown | E3 | O | 0.009 [0.000, 0.100] | 0.002 [0.000, 0.000] | 5.0e-04 [0.000, 0.000] |
| base_unknown | E3 | F | 0.015 [0.000, 0.100] | 0.012 [0.000, 0.100] | 0.003 [0.000, 0.100] |
| base_unknown | E3 | C | 0.043 [0.000, 0.200] | 0.044 [0.000, 0.200] | 0.013 [0.000, 0.100] |
| base_unknown | E3c | O | 0.025 [0.000, 0.100] | 0.029 [0.000, 0.100] | 0.006 [0.000, 0.100] |
| base_unknown | E3c | F | 0.077 [0.000, 0.300] | 0.089 [0.000, 0.200] | 0.075 [0.000, 0.200] |
| base_unknown | E3c | C | 0.018 [0.000, 0.100] | 0.012 [0.000, 0.100] | 0.007 [0.000, 0.100] |
| base_unknown | Cnf | O | 0.193 [0.000, 0.300] | 0.194 [0.000, 0.300] | 0.161 [0.098, 0.300] |

E2c_C O 学生的每 teacher 召回与 AUROC：

| detector | teacher | 1 | 3 | 10 |
|---|---|---|---|---|
| base_known | claude46 | 0.000 [0.000, 0.000] / AUROC 0.762 | 0.000 [0.000, 0.000] / AUROC 0.742 | 0.000 [0.000, 0.000] / AUROC 0.719 |
| base_known | deepseek_v4 | 0.000 [0.000, 0.000] / AUROC 0.231 | 0.000 [0.000, 0.000] / AUROC 0.230 | 0.000 [0.000, 0.000] / AUROC 0.239 |
| base_unknown | claude46 | 0.014 [0.000, 0.200] / AUROC 0.995 | 0.012 [0.000, 0.200] / AUROC 0.997 | 0.004 [0.000, 0.000] / AUROC 0.996 |
| base_unknown | deepseek_v4 | 0.044 [0.000, 0.200] / AUROC 0.995 | 0.035 [0.000, 0.200] / AUROC 0.994 | 0.007 [0.000, 0.200] / AUROC 0.991 |

开集 FPR（各重复均值）与 τ：

| detector | 1 | 3 | 10 |
|---|---|---|---|
| base_known | FPR 0.050 [0.000, 0.118]; τ 0.024 | FPR 0.050 [0.000, 0.118]; τ 0.024 | FPR 0.050 [0.000, 0.118]; τ 0.025 |
| base_unknown | FPR 0.050 [0.000, 0.118]; τ 0.016 | FPR 0.050 [0.000, 0.118]; τ 0.016 | FPR 0.050 [0.000, 0.118]; τ 0.017 |

## 探针预算曲线：随机 k 个 family × 重复（基座参照取同一批 family；均值 [2.5, 97.5]，e7_probe_curve.csv）

macro 召回（行 = 检测器 × τ 策略 × 网格，列 = family 预算 k；calibrated = 该预算自标定的 τ_k，fixed_all_cells = 全 cell 的 τ）：

| detector | tau_policy | grid | version | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|---|
| base_known | calibrated | E2c_C | O | 0.006 [0.000, 0.000] | 0.005 [0.000, 0.003] | 0.001 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E1 | O | 0.005 [0.000, 0.000] | 0.004 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E3 | O | 0.004 [0.000, 0.003] | 0.005 [0.000, 0.003] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E3 | F | 0.008 [0.000, 0.200] | 0.009 [0.000, 0.200] | 0.001 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E3 | C | 0.005 [0.000, 0.100] | 0.005 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E3c | O | 0.008 [0.000, 0.103] | 0.008 [0.000, 0.103] | 0.002 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E3c | F | 0.012 [0.000, 0.200] | 0.012 [0.000, 0.200] | 0.003 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | E3c | C | 0.007 [0.000, 0.100] | 0.004 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | Cnf | O | 0.015 [0.000, 0.103] | 0.007 [0.000, 0.100] | 0.015 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E2c_C | O | 0.096 [0.000, 0.500] | 0.050 [0.000, 0.403] | 0.015 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E1 | O | 0.037 [0.000, 0.400] | 0.023 [0.000, 0.300] | 0.002 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E3 | O | 0.041 [0.000, 0.300] | 0.028 [0.000, 0.300] | 0.002 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E3 | F | 0.061 [0.000, 0.400] | 0.043 [0.000, 0.400] | 0.008 [0.000, 0.100] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E3 | C | 0.040 [0.000, 0.400] | 0.026 [0.000, 0.400] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E3c | O | 0.089 [0.000, 0.503] | 0.049 [0.000, 0.403] | 0.010 [0.000, 0.103] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E3c | F | 0.096 [0.000, 0.500] | 0.068 [0.000, 0.400] | 0.019 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E3c | C | 0.063 [0.000, 0.500] | 0.028 [0.000, 0.500] | 0.003 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | Cnf | O | 0.116 [0.000, 0.500] | 0.086 [0.000, 0.403] | 0.052 [0.000, 0.300] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E2c_C | O | 0.031 [0.000, 0.400] | 0.046 [0.000, 0.400] | 0.067 [0.000, 0.400] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E1 | O | 0.017 [0.000, 0.203] | 0.021 [0.000, 0.300] | 0.041 [0.000, 0.303] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E3 | O | 0.014 [0.000, 0.200] | 0.014 [0.000, 0.200] | 0.027 [0.000, 0.203] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E3 | F | 0.019 [0.000, 0.303] | 0.032 [0.000, 0.400] | 0.048 [0.000, 0.403] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E3 | C | 0.014 [0.000, 0.205] | 0.022 [0.000, 0.300] | 0.044 [0.000, 0.400] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E3c | O | 0.023 [0.000, 0.303] | 0.029 [0.000, 0.400] | 0.030 [0.000, 0.300] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E3c | F | 0.025 [0.000, 0.300] | 0.049 [0.000, 0.400] | 0.073 [0.000, 0.400] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E3c | C | 0.022 [0.000, 0.300] | 0.027 [0.000, 0.303] | 0.022 [0.000, 0.300] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | Cnf | O | 0.034 [0.000, 0.500] | 0.060 [0.000, 0.500] | 0.102 [0.000, 0.500] | 0.200 [0.200, 0.200] |
| base_unknown | fixed_all_cells | E2c_C | O | 0.256 [0.000, 0.900] | 0.236 [0.000, 0.800] | 0.146 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E1 | O | 0.159 [0.000, 0.600] | 0.134 [0.000, 0.500] | 0.099 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E3 | O | 0.157 [0.000, 0.603] | 0.132 [0.000, 0.500] | 0.080 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E3 | F | 0.186 [0.000, 0.703] | 0.168 [0.000, 0.603] | 0.127 [0.000, 0.600] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E3 | C | 0.172 [0.000, 0.600] | 0.146 [0.000, 0.500] | 0.106 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E3c | O | 0.231 [0.000, 0.900] | 0.183 [0.000, 0.708] | 0.106 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E3c | F | 0.231 [0.000, 0.803] | 0.219 [0.000, 0.800] | 0.170 [0.000, 0.503] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | E3c | C | 0.210 [0.000, 0.903] | 0.157 [0.000, 0.800] | 0.072 [0.000, 0.500] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | Cnf | O | 0.276 [0.000, 0.800] | 0.274 [0.000, 0.803] | 0.204 [0.000, 0.503] | 0.200 [0.200, 0.200] |

开集 FPR（各重复均值）与 τ：

| detector | tau_policy | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|
| base_known | calibrated | FPR 0.050 [0.000, 0.235]; τ 0.060 | FPR 0.050 [0.000, 0.236]; τ 0.046 | FPR 0.050 [0.000, 0.296]; τ 0.034 | FPR 0.029 [0.029, 0.029]; τ 0.026 |
| base_known | fixed_all_cells | FPR 0.329 [0.029, 0.853]; τ 0.026 | FPR 0.231 [0.029, 0.765]; τ 0.026 | FPR 0.121 [0.000, 0.501]; τ 0.026 | FPR 0.029 [0.029, 0.029]; τ 0.026 |
| base_unknown | calibrated | FPR 0.050 [0.000, 0.265]; τ 0.065 | FPR 0.050 [0.000, 0.235]; τ 0.042 | FPR 0.050 [0.000, 0.235]; τ 0.028 | FPR 0.029 [0.029, 0.029]; τ 0.020 |
| base_unknown | fixed_all_cells | FPR 0.440 [0.088, 0.913]; τ 0.020 | FPR 0.298 [0.029, 0.795]; τ 0.020 | FPR 0.128 [0.000, 0.471]; τ 0.020 | FPR 0.029 [0.029, 0.029]; τ 0.020 |

E2c_C O 学生的每 teacher 召回：

| detector | tau_policy | teacher | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|
| base_known | calibrated | claude46 | 0.008 [0.000, 0.000] | 0.009 [0.000, 0.005] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | deepseek_v4 | 0.003 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.002 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | claude46 | 0.080 [0.000, 1.000] | 0.049 [0.000, 0.800] | 0.005 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | deepseek_v4 | 0.111 [0.000, 0.800] | 0.051 [0.000, 0.600] | 0.026 [0.000, 0.400] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | claude46 | 0.011 [0.000, 0.005] | 0.014 [0.000, 0.200] | 0.003 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | deepseek_v4 | 0.051 [0.000, 0.800] | 0.078 [0.000, 0.800] | 0.131 [0.000, 0.800] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | claude46 | 0.157 [0.000, 1.000] | 0.113 [0.000, 1.000] | 0.025 [0.000, 0.400] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | deepseek_v4 | 0.355 [0.000, 1.000] | 0.359 [0.000, 1.000] | 0.268 [0.000, 1.000] | 0.000 [0.000, 0.000] |

## leave-one-style-out：τ 只用 O / R / B 的负例标定（与主 τ 相同），认 E3 / E3c 的 F / C 学生（e7_loso.csv）

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.026 | E3 | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.903 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.954 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3 | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.026 | E3 | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.908 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.946 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3 | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.026 | E3c | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.595 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.149 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3c | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_known | 0.026 | E3c | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.562 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.144 | nan | nan | nan | 0.029 |
| base_known | 0.026 | E3c | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.020 | E3 | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3 | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.020 | E3 | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3 | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.020 | E3c | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3c | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |
| base_unknown | 0.020 | E3c | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.020 | E3c | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.029 |

## leave-one-grid-out：τ 在网格 E1, K, K_n 上标定（E1 的学生一并视为应拒判的总体），用到其余网格（e7_logo.csv）

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.022 | E2c_C | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.723 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.223 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E2c_C | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | E3 | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.882 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.959 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3 | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | E3 | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.903 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.954 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3 | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | E3 | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.908 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.946 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3 | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | E3c | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.621 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3c | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.156 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3c | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | E3c | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.595 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.149 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3c | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | E3c | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.562 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.144 | nan | nan | nan | 0.059 |
| base_known | 0.022 | E3c | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_known | 0.022 | Cnf | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 0.800 | 0.208 | nan | nan | nan | 0.059 |
| base_known | 0.022 | Cnf | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.164 | nan | nan | nan | 0.059 |
| base_known | 0.022 | Cnf | O | macro | 10 | 0.000 | [nan, nan] | 0.900 | nan | 0.000 | 0.017 | 1.000 | 0.059 |
| base_unknown | 0.018 | E2c_C | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E2c_C | O | deepseek_v4 | 5 | 0.200 | [0.036, 0.624] | 0.800 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E2c_C | O | macro | 10 | 0.100 | [nan, nan] | 0.900 | nan | 0.100 | 0.017 | 0.506 | 0.059 |
| base_unknown | 0.018 | E3 | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.938 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.990 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3 | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_unknown | 0.018 | E3 | F | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3 | F | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_unknown | 0.018 | E3 | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3 | C | deepseek_v4 | 5 | 0.200 | [0.036, 0.624] | 0.800 | 0.990 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3 | C | macro | 10 | 0.100 | [nan, nan] | 0.900 | nan | 0.100 | 0.017 | 0.502 | 0.059 |
| base_unknown | 0.018 | E3c | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3c | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3c | O | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_unknown | 0.018 | E3c | F | claude46 | 5 | 0.200 | [0.036, 0.624] | 0.800 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3c | F | macro | 10 | 0.100 | [nan, nan] | 0.900 | nan | 0.100 | 0.017 | 0.500 | 0.059 |
| base_unknown | 0.018 | E3c | C | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | E3c | C | macro | 10 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.059 |
| base_unknown | 0.018 | Cnf | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | Cnf | O | deepseek_v4 | 5 | 0.400 | [0.118, 0.769] | 0.600 | 1.000 | nan | nan | nan | 0.059 |
| base_unknown | 0.018 | Cnf | O | macro | 10 | 0.200 | [nan, nan] | 0.800 | nan | 0.200 | 0.033 | 0.215 | 0.059 |

## 描述：负例按类型的误判率（K / K_n / R / S_0）；归档 run；T0

| table | detector | grid | version | n | n_neg_attributed | fpr | tau |
|---|---|---|---|---|---|---|---|
| main | base_known | E1 | R | 3 | 0 | 0.000 | 0.026 |
| main | base_known | E1 | B | 1 | 0 | 0.000 | 0.026 |
| main | base_known | K | O | 15 | 1 | 0.067 | 0.026 |
| main | base_known | K_n | O | 15 | 0 | 0.000 | 0.026 |
| descriptive | base_known | K_3ep | O | 15 | 0 | 0.000 | 0.026 |
| main | base_unknown | E1 | R | 3 | 1 | 0.333 | 0.020 |
| main | base_unknown | E1 | B | 1 | 0 | 0.000 | 0.020 |
| main | base_unknown | K | O | 15 | 0 | 0.000 | 0.020 |
| main | base_unknown | K_n | O | 15 | 0 | 0.000 | 0.020 |
| descriptive | base_unknown | K_3ep | O | 15 | 0 | 0.000 | 0.020 |

归档配方（只有 dev readout；不进标定）：

| detector | grid | version | teacher | n | recall | CI | auroc | macro_recall | fpr |
|---|---|---|---|---|---|---|---|---|---|
| base_known | Cnf_5ep | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 0.374 | nan | 0.029 |
| base_known | Cnf_5ep | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 0.154 | nan | 0.029 |
| base_known | Cnf_5ep | O | macro | 10 | 0.000 | [nan, nan] | nan | 0.000 | 0.029 |
| base_known | E2c_C_3ep | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 0.869 | nan | 0.029 |
| base_known | E2c_C_3ep | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 0.321 | nan | 0.029 |
| base_known | E2c_C_3ep | O | macro | 10 | 0.000 | [nan, nan] | nan | 0.000 | 0.029 |
| base_known | K_3ep | O | none | 15 | 1.000 | [nan, nan] | nan | nan | 0.000 |
| base_unknown | Cnf_5ep | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | nan | 0.029 |
| base_unknown | Cnf_5ep | O | deepseek_v4 | 5 | 0.200 | [0.036, 0.624] | 1.000 | nan | 0.029 |
| base_unknown | Cnf_5ep | O | macro | 10 | 0.100 | [nan, nan] | nan | 0.100 | 0.029 |
| base_unknown | E2c_C_3ep | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | nan | 0.029 |
| base_unknown | E2c_C_3ep | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | nan | 0.029 |
| base_unknown | E2c_C_3ep | O | macro | 10 | 0.000 | [nan, nan] | nan | 0.000 | 0.029 |
| base_unknown | K_3ep | O | none | 15 | 1.000 | [nan, nan] | nan | nan | 0.000 |

T0（训练未见的无框架变体，不进分数）：各网格 run 均值的 a_t；对照 seen variants 的 a_t：

| grid | version | a_T0__claude46 | a_T0__deepseek_v4 | a_T0__gpt41 | a_T0__gpt4o_mini | a_T0__gpt4_0613 | a_T0__claude_haiku45 | a__claude46 | a__deepseek_v4 | a__gpt41 | a__gpt4o_mini | a__gpt4_0613 | a__claude_haiku45 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E1 | O | 0.859 | 0.851 | nan | nan | nan | nan | 0.835 | 0.835 | 0.831 | 0.836 | 0.829 | 0.831 |
| E1 | R | 0.457 | 0.479 | nan | nan | nan | nan | 0.469 | 0.481 | 0.499 | 0.485 | 0.491 | 0.459 |
| E3 | C | 0.855 | 0.850 | nan | nan | nan | nan | 0.834 | 0.828 | 0.824 | 0.831 | 0.826 | 0.834 |
| E3 | F | 0.860 | 0.852 | nan | nan | nan | nan | 0.832 | 0.829 | 0.824 | 0.830 | 0.825 | 0.827 |
| E3 | O | 0.860 | 0.850 | nan | nan | nan | nan | 0.833 | 0.833 | 0.828 | 0.835 | 0.828 | 0.829 |
| E2c_C | O | 0.806 | 0.812 | nan | nan | nan | nan | 0.795 | 0.797 | 0.790 | 0.804 | 0.794 | 0.785 |
| K | O | 0.848 | 0.849 | nan | nan | nan | nan | 0.830 | 0.815 | 0.821 | 0.829 | 0.830 | 0.835 |
| K_n | O | 0.840 | 0.847 | nan | nan | nan | nan | 0.828 | 0.818 | 0.818 | 0.834 | 0.831 | 0.831 |
| Cnf | O | 0.778 | 0.786 | nan | nan | nan | nan | 0.744 | 0.766 | 0.741 | 0.766 | 0.737 | 0.734 |
| E3c | C | 0.800 | 0.798 | nan | nan | nan | nan | 0.795 | 0.787 | 0.782 | 0.797 | 0.783 | 0.783 |
| E3c | F | 0.810 | 0.804 | nan | nan | nan | nan | 0.791 | 0.791 | 0.786 | 0.798 | 0.787 | 0.779 |
| E3c | O | 0.802 | 0.806 | nan | nan | nan | nan | 0.791 | 0.795 | 0.789 | 0.802 | 0.790 | 0.778 |
| E2c_C_3ep | O | 0.817 | 0.826 | nan | nan | nan | nan | 0.803 | 0.804 | 0.797 | 0.808 | 0.801 | 0.793 |
| K_3ep | O | 0.840 | 0.849 | nan | nan | nan | nan | 0.835 | 0.822 | 0.827 | 0.831 | 0.838 | 0.835 |
| Cnf_5ep | O | 0.791 | 0.806 | nan | nan | nan | nan | 0.767 | 0.782 | 0.763 | 0.789 | 0.766 | 0.758 |
| E1 | B | 0.857 | 0.714 | nan | nan | nan | nan | 0.847 | 0.857 | 0.819 | 0.838 | 0.875 | 0.796 |

## 每 run（e7_runs.csv 节选：grid、真值、a_t、两种分数的判定）

| run_id | grid | version | truth | n_cells_valid | a__claude46 | a__deepseek_v4 | a__gpt41 | a__gpt4o_mini | a__gpt4_0613 | a__claude_haiku45 | decision_known | margin_known | decision_unknown | margin_unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | Cnf | O | claude46 | 596 | 0.792 | 0.765 | 0.752 | 0.772 | 0.750 | 0.805 | unattributed | 0.022 | unattributed | 0.013 |
| qwen3-4b-e2cnf.claude46_O_s2 | Cnf | O | claude46 | 597 | 0.794 | 0.768 | 0.760 | 0.760 | 0.751 | 0.805 | unattributed | 0.020 | unattributed | 0.011 |
| qwen3-4b-e2cnf.claude46_O_s3 | Cnf | O | claude46 | 596 | 0.796 | 0.750 | 0.753 | 0.770 | 0.763 | 0.810 | unattributed | 0.024 | unattributed | 0.015 |
| qwen3-4b-e2cnf.claude46_O_s4 | Cnf | O | claude46 | 596 | 0.783 | 0.738 | 0.726 | 0.732 | 0.746 | 0.776 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-e2cnf.claude46_O_s5 | Cnf | O | claude46 | 596 | 0.801 | 0.750 | 0.757 | 0.763 | 0.772 | 0.793 | unattributed | 1.0e-03 | unattributed | 0.008 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | Cnf | O | deepseek_v4 | 596 | 0.680 | 0.751 | 0.708 | 0.740 | 0.681 | 0.671 | unattributed | 0.007 | unattributed | 0.011 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | Cnf | O | deepseek_v4 | 596 | 0.680 | 0.753 | 0.699 | 0.728 | 0.678 | 0.659 | unattributed | 0.020 | deepseek_v4 | 0.025 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | Cnf | O | deepseek_v4 | 596 | 0.700 | 0.773 | 0.723 | 0.758 | 0.708 | 0.690 | unattributed | 0.010 | unattributed | 0.015 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | Cnf | O | deepseek_v4 | 596 | 0.691 | 0.758 | 0.715 | 0.757 | 0.698 | 0.681 | unattributed | 0.003 | unattributed | 0.001 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | Cnf | O | deepseek_v4 | 596 | 0.675 | 0.753 | 0.696 | 0.732 | 0.684 | 0.660 | unattributed | 0.017 | deepseek_v4 | 0.021 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | Cnf | O | gpt4o | 597 | 0.735 | 0.775 | 0.752 | 0.789 | 0.748 | 0.710 | unattributed | 0.012 | unattributed | 0.013 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | Cnf | O | gpt4o | 596 | 0.742 | 0.776 | 0.753 | 0.784 | 0.753 | 0.724 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | Cnf | O | gpt4o | 597 | 0.764 | 0.800 | 0.781 | 0.797 | 0.776 | 0.743 | unattributed | 0.002 | unattributed | 0.003 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | Cnf | O | gpt4o | 596 | 0.753 | 0.790 | 0.770 | 0.800 | 0.762 | 0.736 | unattributed | 0.008 | unattributed | 0.010 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | Cnf | O | gpt4o | 597 | 0.776 | 0.789 | 0.775 | 0.810 | 0.782 | 0.750 | unattributed | 7.5e-05 | gpt4o_mini | 0.022 |
| qwen3-4b.base_B_s0 | E1 | B | none | 105 | 0.847 | 0.857 | 0.819 | 0.838 | 0.875 | 0.796 | unattributed | 0.026 | unattributed | 0.018 |
| qwen3-4b.claude46_O_s1 | E1 | O | claude46 | 596 | 0.853 | 0.803 | 0.819 | 0.817 | 0.823 | 0.852 | unattributed | 0.008 | unattributed | 8.5e-04 |
| qwen3-4b.claude46_O_s2 | E1 | O | claude46 | 596 | 0.844 | 0.798 | 0.812 | 0.822 | 0.825 | 0.843 | unattributed | 0.008 | unattributed | 5.9e-04 |
| qwen3-4b.claude46_O_s3 | E1 | O | claude46 | 596 | 0.837 | 0.812 | 0.831 | 0.819 | 0.842 | 0.845 | unattributed | 0.014 | unattributed | 0.003 |
| qwen3-4b.claude46_O_s4 | E1 | O | claude46 | 596 | 0.847 | 0.800 | 0.804 | 0.804 | 0.828 | 0.845 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b.claude46_O_s5 | E1 | O | claude46 | 596 | 0.851 | 0.808 | 0.826 | 0.829 | 0.832 | 0.853 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b.deepseek_v4_O_s1 | E1 | O | deepseek_v4 | 596 | 0.808 | 0.834 | 0.811 | 0.829 | 0.818 | 0.795 | unattributed | 0.007 | unattributed | 0.005 |
| qwen3-4b.deepseek_v4_O_s2 | E1 | O | deepseek_v4 | 596 | 0.817 | 0.857 | 0.828 | 0.842 | 0.828 | 0.814 | unattributed | 0.003 | unattributed | 0.015 |
| qwen3-4b.deepseek_v4_O_s3 | E1 | O | deepseek_v4 | 596 | 0.822 | 0.847 | 0.831 | 0.846 | 0.832 | 0.814 | unattributed | 0.007 | unattributed | 0.001 |
| qwen3-4b.deepseek_v4_O_s4 | E1 | O | deepseek_v4 | 596 | 0.817 | 0.839 | 0.819 | 0.827 | 0.808 | 0.805 | unattributed | 0.003 | unattributed | 0.011 |
| qwen3-4b.deepseek_v4_O_s5 | E1 | O | deepseek_v4 | 596 | 0.822 | 0.844 | 0.824 | 0.829 | 0.818 | 0.812 | unattributed | 0.001 | unattributed | 0.015 |
| qwen3-4b.gpt4o_O_s1 | E1 | O | gpt4o | 596 | 0.844 | 0.861 | 0.858 | 0.861 | 0.837 | 0.843 | unattributed | 0.003 | unattributed | 2.3e-04 |
| qwen3-4b.gpt4o_O_s2 | E1 | O | gpt4o | 596 | 0.838 | 0.844 | 0.840 | 0.847 | 0.835 | 0.831 | unattributed | 0.002 | unattributed | 0.004 |
| qwen3-4b.gpt4o_O_s3 | E1 | O | gpt4o | 596 | 0.831 | 0.849 | 0.848 | 0.859 | 0.832 | 0.826 | unattributed | 0.004 | unattributed | 0.010 |
| qwen3-4b.gpt4o_O_s4 | E1 | O | gpt4o | 596 | 0.838 | 0.862 | 0.853 | 0.849 | 0.830 | 0.838 | unattributed | 0.003 | unattributed | 0.009 |
| qwen3-4b.gpt4o_O_s5 | E1 | O | gpt4o | 596 | 0.851 | 0.864 | 0.856 | 0.854 | 0.846 | 0.852 | unattributed | 0.010 | unattributed | 0.007 |
| qwen3-4b.random_R_s1 | E1 | R | none | 596 | 0.542 | 0.585 | 0.613 | 0.599 | 0.592 | 0.538 | unattributed | 0.015 | unattributed | 0.014 |
| qwen3-4b.random_R_s2 | E1 | R | none | 596 | 0.439 | 0.444 | 0.459 | 0.403 | 0.475 | 0.414 | unattributed | 0.022 | unattributed | 0.016 |
| qwen3-4b.random_R_s3 | E1 | R | none | 596 | 0.426 | 0.415 | 0.426 | 0.455 | 0.407 | 0.426 | unattributed | 0.009 | gpt4o_mini | 0.028 |
| qwen3-4b-e2c.claude46_O_s1 | E2c_C | O | claude46 | 596 | 0.833 | 0.766 | 0.792 | 0.787 | 0.808 | 0.836 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-e2c.claude46_O_s2 | E2c_C | O | claude46 | 596 | 0.833 | 0.773 | 0.797 | 0.790 | 0.804 | 0.836 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-e2c.claude46_O_s3 | E2c_C | O | claude46 | 596 | 0.853 | 0.782 | 0.802 | 0.792 | 0.828 | 0.848 | unattributed | 0.005 | unattributed | 0.004 |
| qwen3-4b-e2c.claude46_O_s4 | E2c_C | O | claude46 | 596 | 0.826 | 0.768 | 0.780 | 0.795 | 0.804 | 0.831 | unattributed | 0.014 | unattributed | 0.005 |
| qwen3-4b-e2c.claude46_O_s5 | E2c_C | O | claude46 | 596 | 0.838 | 0.778 | 0.794 | 0.795 | 0.815 | 0.838 | unattributed | 0.009 | unattributed | 4.3e-04 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | E2c_C | O | deepseek_v4 | 596 | 0.721 | 0.792 | 0.738 | 0.777 | 0.722 | 0.703 | unattributed | 0.010 | unattributed | 0.015 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | E2c_C | O | deepseek_v4 | 596 | 0.751 | 0.802 | 0.769 | 0.802 | 0.750 | 0.728 | unattributed | 0.005 | unattributed | 3.3e-04 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | E2c_C | O | deepseek_v4 | 596 | 0.707 | 0.766 | 0.713 | 0.755 | 0.705 | 0.686 | unattributed | 0.007 | unattributed | 0.011 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | E2c_C | O | deepseek_v4 | 596 | 0.726 | 0.782 | 0.748 | 0.768 | 0.719 | 0.714 | unattributed | 0.007 | unattributed | 0.013 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | E2c_C | O | deepseek_v4 | 596 | 0.728 | 0.798 | 0.748 | 0.780 | 0.738 | 0.712 | unattributed | 0.013 | unattributed | 0.018 |
| qwen3-4b-e2c.gpt4o_O_s1 | E2c_C | O | gpt4o | 596 | 0.822 | 0.832 | 0.831 | 0.846 | 0.842 | 0.809 | unattributed | 0.017 | unattributed | 0.003 |
| qwen3-4b-e2c.gpt4o_O_s2 | E2c_C | O | gpt4o | 596 | 0.810 | 0.827 | 0.828 | 0.841 | 0.837 | 0.797 | unattributed | 0.016 | unattributed | 0.004 |
| qwen3-4b-e2c.gpt4o_O_s3 | E2c_C | O | gpt4o | 596 | 0.831 | 0.835 | 0.850 | 0.859 | 0.856 | 0.810 | unattributed | 0.013 | unattributed | 0.003 |
| qwen3-4b-e2c.gpt4o_O_s4 | E2c_C | O | gpt4o | 596 | 0.826 | 0.820 | 0.831 | 0.847 | 0.840 | 0.812 | unattributed | 0.012 | unattributed | 0.007 |
| qwen3-4b-e2c.gpt4o_O_s5 | E2c_C | O | gpt4o | 596 | 0.824 | 0.829 | 0.829 | 0.832 | 0.835 | 0.810 | unattributed | 0.009 | unattributed | 0.003 |
| qwen3-4b-paired.claude46_C_s1 | E3 | C | claude46 | 596 | 0.847 | 0.790 | 0.806 | 0.804 | 0.835 | 0.853 | unattributed | 0.015 | unattributed | 0.006 |
| qwen3-4b-paired.claude46_C_s2 | E3 | C | claude46 | 596 | 0.845 | 0.792 | 0.804 | 0.805 | 0.846 | 0.848 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-paired.claude46_C_s3 | E3 | C | claude46 | 596 | 0.847 | 0.805 | 0.806 | 0.805 | 0.828 | 0.841 | unattributed | 0.003 | unattributed | 0.006 |
| qwen3-4b-paired.claude46_C_s4 | E3 | C | claude46 | 596 | 0.842 | 0.793 | 0.809 | 0.814 | 0.823 | 0.850 | unattributed | 0.017 | unattributed | 0.008 |
| qwen3-4b-paired.claude46_C_s5 | E3 | C | claude46 | 595 | 0.840 | 0.791 | 0.790 | 0.807 | 0.820 | 0.839 | unattributed | 0.008 | unattributed | 4.8e-04 |
| qwen3-4b-paired.deepseek_v4_C_s1 | E3 | C | deepseek_v4 | 596 | 0.813 | 0.840 | 0.811 | 0.832 | 0.815 | 0.805 | unattributed | 6.3e-04 | unattributed | 0.008 |
| qwen3-4b-paired.deepseek_v4_C_s2 | E3 | C | deepseek_v4 | 593 | 0.812 | 0.836 | 0.815 | 0.833 | 0.807 | 0.810 | unattributed | 0.006 | unattributed | 0.003 |
| qwen3-4b-paired.deepseek_v4_C_s3 | E3 | C | deepseek_v4 | 596 | 0.813 | 0.844 | 0.824 | 0.836 | 0.816 | 0.814 | unattributed | 0.008 | unattributed | 0.008 |
| qwen3-4b-paired.deepseek_v4_C_s4 | E3 | C | deepseek_v4 | 596 | 0.810 | 0.854 | 0.824 | 0.836 | 0.813 | 0.814 | unattributed | 0.005 | unattributed | 0.018 |
| qwen3-4b-paired.deepseek_v4_C_s5 | E3 | C | deepseek_v4 | 596 | 0.826 | 0.837 | 0.824 | 0.831 | 0.808 | 0.829 | unattributed | 0.012 | unattributed | 0.006 |
| qwen3-4b-paired.gpt4o_C_s1 | E3 | C | gpt4o | 596 | 0.831 | 0.844 | 0.855 | 0.854 | 0.822 | 0.834 | unattributed | 0.002 | unattributed | 7.0e-04 |
| qwen3-4b-paired.gpt4o_C_s2 | E3 | C | gpt4o | 596 | 0.851 | 0.847 | 0.848 | 0.851 | 0.849 | 0.850 | unattributed | 0.008 | unattributed | 1.3e-04 |
| qwen3-4b-paired.gpt4o_C_s3 | E3 | C | gpt4o | 596 | 0.840 | 0.835 | 0.840 | 0.849 | 0.832 | 0.826 | unattributed | 0.005 | unattributed | 0.009 |
| qwen3-4b-paired.gpt4o_C_s4 | E3 | C | gpt4o | 596 | 0.840 | 0.854 | 0.851 | 0.854 | 0.839 | 0.845 | unattributed | 0.012 | unattributed | 2.5e-04 |
| qwen3-4b-paired.gpt4o_C_s5 | E3 | C | gpt4o | 596 | 0.844 | 0.854 | 0.855 | 0.861 | 0.840 | 0.850 | unattributed | 0.014 | unattributed | 0.006 |
| qwen3-4b-paired.claude46_F_s1 | E3 | F | claude46 | 596 | 0.845 | 0.795 | 0.804 | 0.805 | 0.823 | 0.848 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-paired.claude46_F_s2 | E3 | F | claude46 | 596 | 0.847 | 0.795 | 0.797 | 0.799 | 0.827 | 0.831 | unattributed | 0.007 | unattributed | 0.016 |
| qwen3-4b-paired.claude46_F_s3 | E3 | F | claude46 | 596 | 0.838 | 0.792 | 0.792 | 0.802 | 0.823 | 0.833 | unattributed | 0.003 | unattributed | 0.006 |
| qwen3-4b-paired.claude46_F_s4 | E3 | F | claude46 | 596 | 0.853 | 0.795 | 0.806 | 0.805 | 0.827 | 0.843 | unattributed | 5.1e-04 | unattributed | 0.009 |
| qwen3-4b-paired.claude46_F_s5 | E3 | F | claude46 | 596 | 0.837 | 0.797 | 0.799 | 0.807 | 0.825 | 0.843 | unattributed | 0.015 | unattributed | 0.007 |
| qwen3-4b-paired.deepseek_v4_F_s1 | E3 | F | deepseek_v4 | 596 | 0.799 | 0.839 | 0.816 | 0.834 | 0.816 | 0.793 | unattributed | 0.007 | unattributed | 0.005 |
| qwen3-4b-paired.deepseek_v4_F_s2 | E3 | F | deepseek_v4 | 596 | 0.819 | 0.842 | 0.816 | 0.831 | 0.822 | 0.809 | unattributed | 2.5e-04 | unattributed | 0.011 |
| qwen3-4b-paired.deepseek_v4_F_s3 | E3 | F | deepseek_v4 | 596 | 0.817 | 0.849 | 0.829 | 0.841 | 0.815 | 0.805 | unattributed | 0.003 | unattributed | 0.008 |
| qwen3-4b-paired.deepseek_v4_F_s4 | E3 | F | deepseek_v4 | 596 | 0.803 | 0.845 | 0.826 | 0.841 | 0.818 | 0.803 | unattributed | 0.001 | unattributed | 0.005 |
| qwen3-4b-paired.deepseek_v4_F_s5 | E3 | F | deepseek_v4 | 596 | 0.808 | 0.837 | 0.821 | 0.829 | 0.822 | 0.800 | unattributed | 0.007 | unattributed | 0.008 |
| qwen3-4b-paired.gpt4o_F_s1 | E3 | F | gpt4o | 596 | 0.853 | 0.850 | 0.855 | 0.847 | 0.835 | 0.848 | unattributed | 0.005 | unattributed | 0.002 |
| qwen3-4b-paired.gpt4o_F_s2 | E3 | F | gpt4o | 596 | 0.842 | 0.837 | 0.843 | 0.844 | 0.828 | 0.829 | unattributed | 0.004 | unattributed | 0.001 |
| qwen3-4b-paired.gpt4o_F_s3 | E3 | F | gpt4o | 596 | 0.837 | 0.861 | 0.855 | 0.861 | 0.834 | 0.838 | unattributed | 0.001 | unattributed | 2.3e-04 |
| qwen3-4b-paired.gpt4o_F_s4 | E3 | F | gpt4o | 596 | 0.840 | 0.852 | 0.853 | 0.859 | 0.830 | 0.836 | unattributed | 0.001 | unattributed | 0.006 |
| qwen3-4b-paired.gpt4o_F_s5 | E3 | F | gpt4o | 596 | 0.840 | 0.857 | 0.846 | 0.847 | 0.832 | 0.841 | unattributed | 0.010 | unattributed | 0.010 |
| qwen3-4b-paired.claude46_O_s1 | E3 | O | claude46 | 596 | 0.851 | 0.800 | 0.812 | 0.814 | 0.827 | 0.853 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-paired.claude46_O_s2 | E3 | O | claude46 | 596 | 0.835 | 0.788 | 0.792 | 0.802 | 0.813 | 0.833 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-paired.claude46_O_s3 | E3 | O | claude46 | 596 | 0.835 | 0.818 | 0.816 | 0.829 | 0.840 | 0.843 | unattributed | 0.014 | unattributed | 0.003 |
| qwen3-4b-paired.claude46_O_s4 | E3 | O | claude46 | 596 | 0.858 | 0.803 | 0.814 | 0.807 | 0.839 | 0.848 | unattributed | 6.7e-04 | unattributed | 0.010 |
| qwen3-4b-paired.claude46_O_s5 | E3 | O | claude46 | 595 | 0.847 | 0.803 | 0.810 | 0.815 | 0.837 | 0.853 | unattributed | 0.015 | unattributed | 0.006 |
| qwen3-4b-paired.deepseek_v4_O_s1 | E3 | O | deepseek_v4 | 596 | 0.801 | 0.840 | 0.821 | 0.846 | 0.816 | 0.803 | unattributed | 8.5e-04 | unattributed | 0.005 |
| qwen3-4b-paired.deepseek_v4_O_s2 | E3 | O | deepseek_v4 | 596 | 0.819 | 0.844 | 0.821 | 0.842 | 0.820 | 0.812 | unattributed | 0.002 | unattributed | 0.001 |
| qwen3-4b-paired.deepseek_v4_O_s3 | E3 | O | deepseek_v4 | 596 | 0.819 | 0.852 | 0.833 | 0.841 | 0.827 | 0.810 | unattributed | 7.3e-04 | unattributed | 0.011 |
| qwen3-4b-paired.deepseek_v4_O_s4 | E3 | O | deepseek_v4 | 594 | 0.822 | 0.847 | 0.827 | 0.845 | 0.818 | 0.810 | unattributed | 0.002 | unattributed | 0.001 |
| qwen3-4b-paired.deepseek_v4_O_s5 | E3 | O | deepseek_v4 | 596 | 0.821 | 0.840 | 0.828 | 0.829 | 0.822 | 0.803 | unattributed | 0.002 | unattributed | 0.011 |
| qwen3-4b-paired.gpt4o_O_s1 | E3 | O | gpt4o | 596 | 0.837 | 0.852 | 0.850 | 0.856 | 0.827 | 0.834 | unattributed | 0.003 | unattributed | 0.004 |
| qwen3-4b-paired.gpt4o_O_s2 | E3 | O | gpt4o | 596 | 0.840 | 0.835 | 0.841 | 0.842 | 0.827 | 0.822 | unattributed | 0.008 | unattributed | 0.001 |
| qwen3-4b-paired.gpt4o_O_s3 | E3 | O | gpt4o | 596 | 0.833 | 0.850 | 0.848 | 0.857 | 0.830 | 0.824 | unattributed | 0.006 | unattributed | 0.007 |
| qwen3-4b-paired.gpt4o_O_s4 | E3 | O | gpt4o | 596 | 0.845 | 0.862 | 0.853 | 0.852 | 0.832 | 0.843 | unattributed | 0.007 | unattributed | 0.009 |
| qwen3-4b-paired.gpt4o_O_s5 | E3 | O | gpt4o | 596 | 0.840 | 0.861 | 0.850 | 0.854 | 0.839 | 0.841 | unattributed | 0.010 | unattributed | 0.006 |
| qwen3-4b-e2c-paired.claude46_C_s1 | E3c | C | claude46 | 596 | 0.844 | 0.776 | 0.794 | 0.790 | 0.801 | 0.841 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.claude46_C_s2 | E3c | C | claude46 | 596 | 0.812 | 0.755 | 0.780 | 0.782 | 0.796 | 0.809 | unattributed | 0.006 | unattributed | 0.003 |
| qwen3-4b-e2c-paired.claude46_C_s3 | E3c | C | claude46 | 597 | 0.831 | 0.760 | 0.782 | 0.763 | 0.796 | 0.834 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-e2c-paired.claude46_C_s4 | E3c | C | claude46 | 596 | 0.835 | 0.782 | 0.796 | 0.795 | 0.815 | 0.833 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.claude46_C_s5 | E3c | C | claude46 | 596 | 0.821 | 0.768 | 0.789 | 0.799 | 0.792 | 0.826 | unattributed | 0.014 | unattributed | 0.005 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | E3c | C | deepseek_v4 | 595 | 0.709 | 0.749 | 0.724 | 0.755 | 0.708 | 0.690 | unattributed | 0.009 | unattributed | 0.005 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | E3c | C | deepseek_v4 | 596 | 0.728 | 0.773 | 0.720 | 0.762 | 0.714 | 0.710 | unattributed | 0.007 | unattributed | 0.011 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | E3c | C | deepseek_v4 | 596 | 0.721 | 0.761 | 0.738 | 0.760 | 0.717 | 0.697 | unattributed | 3.2e-04 | unattributed | 0.001 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | E3c | C | deepseek_v4 | 596 | 0.723 | 0.773 | 0.736 | 0.772 | 0.726 | 0.710 | unattributed | 0.003 | unattributed | 0.001 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | E3c | C | deepseek_v4 | 596 | 0.753 | 0.788 | 0.758 | 0.790 | 0.743 | 0.733 | unattributed | 0.006 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | E3c | C | gpt4o | 596 | 0.833 | 0.832 | 0.836 | 0.846 | 0.846 | 0.826 | unattributed | 0.008 | unattributed | 1.2e-05 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | E3c | C | gpt4o | 596 | 0.828 | 0.805 | 0.801 | 0.826 | 0.808 | 0.802 | unattributed | 0.017 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | E3c | C | gpt4o | 596 | 0.817 | 0.824 | 0.823 | 0.837 | 0.823 | 0.809 | unattributed | 0.003 | unattributed | 0.014 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | E3c | C | gpt4o | 596 | 0.824 | 0.830 | 0.828 | 0.847 | 0.827 | 0.809 | unattributed | 7.0e-05 | unattributed | 0.017 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | E3c | C | gpt4o | 596 | 0.840 | 0.827 | 0.829 | 0.837 | 0.830 | 0.819 | unattributed | 0.012 | unattributed | 0.003 |
| qwen3-4b-e2c-paired.claude46_F_s1 | E3c | F | claude46 | 596 | 0.822 | 0.773 | 0.787 | 0.787 | 0.798 | 0.821 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.claude46_F_s2 | E3c | F | claude46 | 596 | 0.829 | 0.775 | 0.796 | 0.789 | 0.811 | 0.834 | unattributed | 0.014 | unattributed | 0.005 |
| qwen3-4b-e2c-paired.claude46_F_s3 | E3c | F | claude46 | 596 | 0.842 | 0.780 | 0.794 | 0.794 | 0.806 | 0.834 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.claude46_F_s4 | E3c | F | claude46 | 596 | 0.828 | 0.770 | 0.784 | 0.784 | 0.799 | 0.809 | unattributed | 0.010 | unattributed | 0.019 |
| qwen3-4b-e2c-paired.claude46_F_s5 | E3c | F | claude46 | 596 | 0.831 | 0.770 | 0.792 | 0.787 | 0.798 | 0.817 | unattributed | 0.005 | unattributed | 0.014 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | E3c | F | deepseek_v4 | 597 | 0.734 | 0.765 | 0.743 | 0.767 | 0.729 | 0.716 | unattributed | 0.002 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | E3c | F | deepseek_v4 | 594 | 0.721 | 0.781 | 0.744 | 0.774 | 0.733 | 0.706 | unattributed | 0.002 | unattributed | 0.006 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | E3c | F | deepseek_v4 | 595 | 0.725 | 0.778 | 0.745 | 0.783 | 0.739 | 0.718 | unattributed | 0.010 | unattributed | 0.005 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | E3c | F | deepseek_v4 | 596 | 0.707 | 0.765 | 0.725 | 0.748 | 0.712 | 0.698 | unattributed | 0.012 | unattributed | 0.016 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | E3c | F | deepseek_v4 | 596 | 0.718 | 0.787 | 0.740 | 0.775 | 0.719 | 0.705 | unattributed | 0.007 | unattributed | 0.011 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | E3c | F | gpt4o | 596 | 0.838 | 0.837 | 0.841 | 0.847 | 0.854 | 0.817 | unattributed | 0.013 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | E3c | F | gpt4o | 596 | 0.829 | 0.825 | 0.828 | 0.842 | 0.839 | 0.814 | unattributed | 0.007 | unattributed | 0.004 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | E3c | F | gpt4o | 596 | 0.819 | 0.829 | 0.833 | 0.836 | 0.832 | 0.807 | unattributed | 0.006 | unattributed | 0.003 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | E3c | F | gpt4o | 596 | 0.819 | 0.822 | 0.826 | 0.839 | 0.825 | 0.793 | unattributed | 0.004 | unattributed | 0.013 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | E3c | F | gpt4o | 596 | 0.806 | 0.815 | 0.812 | 0.826 | 0.818 | 0.793 | unattributed | 0.009 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.claude46_O_s1 | E3c | O | claude46 | 596 | 0.833 | 0.778 | 0.796 | 0.785 | 0.806 | 0.817 | unattributed | 0.007 | unattributed | 0.016 |
| qwen3-4b-e2c-paired.claude46_O_s2 | E3c | O | claude46 | 596 | 0.842 | 0.785 | 0.806 | 0.799 | 0.818 | 0.840 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.claude46_O_s3 | E3c | O | claude46 | 596 | 0.826 | 0.773 | 0.784 | 0.784 | 0.806 | 0.819 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.claude46_O_s4 | E3c | O | claude46 | 596 | 0.829 | 0.773 | 0.784 | 0.787 | 0.806 | 0.828 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.claude46_O_s5 | E3c | O | claude46 | 596 | 0.824 | 0.773 | 0.791 | 0.794 | 0.801 | 0.817 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | E3c | O | deepseek_v4 | 596 | 0.725 | 0.778 | 0.735 | 0.777 | 0.726 | 0.712 | unattributed | 0.003 | unattributed | 0.001 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | E3c | O | deepseek_v4 | 596 | 0.735 | 0.787 | 0.757 | 0.789 | 0.738 | 0.716 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | E3c | O | deepseek_v4 | 596 | 0.714 | 0.776 | 0.733 | 0.768 | 0.726 | 0.702 | unattributed | 0.003 | unattributed | 0.008 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | E3c | O | deepseek_v4 | 596 | 0.703 | 0.766 | 0.726 | 0.758 | 0.708 | 0.686 | unattributed | 0.003 | unattributed | 0.008 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | E3c | O | deepseek_v4 | 596 | 0.723 | 0.780 | 0.747 | 0.782 | 0.722 | 0.703 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | E3c | O | gpt4o | 596 | 0.821 | 0.827 | 0.831 | 0.834 | 0.840 | 0.803 | unattributed | 0.016 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | E3c | O | gpt4o | 596 | 0.821 | 0.834 | 0.836 | 0.851 | 0.837 | 0.812 | unattributed | 0.008 | unattributed | 0.014 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | E3c | O | gpt4o | 596 | 0.828 | 0.847 | 0.845 | 0.864 | 0.844 | 0.814 | unattributed | 0.006 | unattributed | 0.017 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | E3c | O | gpt4o | 596 | 0.817 | 0.815 | 0.823 | 0.822 | 0.825 | 0.791 | unattributed | 0.005 | unattributed | 0.002 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | E3c | O | gpt4o | 596 | 0.819 | 0.832 | 0.836 | 0.839 | 0.846 | 0.812 | unattributed | 0.016 | unattributed | 0.007 |
| qwen3-4b-e2ck.claude46_O_s1 | K | O | none | 596 | 0.824 | 0.812 | 0.819 | 0.832 | 0.832 | 0.834 | unattributed | 0.014 | unattributed | 0.002 |
| qwen3-4b-e2ck.claude46_O_s2 | K | O | none | 596 | 0.835 | 0.827 | 0.824 | 0.844 | 0.847 | 0.843 | unattributed | 0.007 | unattributed | 0.003 |
| qwen3-4b-e2ck.claude46_O_s3 | K | O | none | 596 | 0.817 | 0.792 | 0.792 | 0.812 | 0.818 | 0.812 | unattributed | 0.004 | unattributed | 0.001 |
| qwen3-4b-e2ck.claude46_O_s4 | K | O | none | 596 | 0.833 | 0.822 | 0.836 | 0.832 | 0.835 | 0.845 | unattributed | 0.021 | unattributed | 0.009 |
| qwen3-4b-e2ck.claude46_O_s5 | K | O | none | 597 | 0.822 | 0.799 | 0.804 | 0.816 | 0.808 | 0.821 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | K | O | none | 596 | 0.824 | 0.803 | 0.812 | 0.817 | 0.822 | 0.822 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | K | O | none | 596 | 0.835 | 0.834 | 0.823 | 0.847 | 0.839 | 0.836 | unattributed | 0.009 | unattributed | 0.009 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | K | O | none | 596 | 0.815 | 0.797 | 0.782 | 0.800 | 0.804 | 0.817 | unattributed | 0.011 | unattributed | 0.002 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | K | O | none | 596 | 0.847 | 0.832 | 0.840 | 0.842 | 0.839 | 0.847 | unattributed | 0.008 | unattributed | 7.0e-04 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | K | O | none | 596 | 0.824 | 0.810 | 0.823 | 0.824 | 0.825 | 0.834 | unattributed | 0.019 | unattributed | 0.009 |
| qwen3-4b-e2ck.gpt4o_O_s1 | K | O | none | 596 | 0.847 | 0.845 | 0.856 | 0.852 | 0.852 | 0.845 | unattributed | 0.004 | unattributed | 0.004 |
| qwen3-4b-e2ck.gpt4o_O_s2 | K | O | none | 596 | 0.824 | 0.817 | 0.824 | 0.834 | 0.832 | 0.838 | unattributed | 0.018 | unattributed | 0.004 |
| qwen3-4b-e2ck.gpt4o_O_s3 | K | O | none | 594 | 0.820 | 0.809 | 0.820 | 0.827 | 0.825 | 0.828 | unattributed | 0.014 | unattributed | 9.9e-04 |
| qwen3-4b-e2ck.gpt4o_O_s4 | K | O | none | 596 | 0.833 | 0.808 | 0.823 | 0.832 | 0.825 | 0.853 | claude_haiku45 | 0.029 | unattributed | 0.020 |
| qwen3-4b-e2ck.gpt4o_O_s5 | K | O | none | 596 | 0.849 | 0.824 | 0.841 | 0.824 | 0.842 | 0.845 | unattributed | 0.005 | unattributed | 0.004 |
| qwen3-4b-e2ckn.claude46_O_s1 | K_n | O | none | 596 | 0.822 | 0.808 | 0.812 | 0.831 | 0.834 | 0.826 | unattributed | 0.004 | unattributed | 0.003 |
| qwen3-4b-e2ckn.claude46_O_s2 | K_n | O | none | 596 | 0.821 | 0.818 | 0.816 | 0.834 | 0.844 | 0.833 | unattributed | 3.4e-04 | unattributed | 0.010 |
| qwen3-4b-e2ckn.claude46_O_s3 | K_n | O | none | 597 | 0.806 | 0.797 | 0.779 | 0.812 | 0.813 | 0.798 | unattributed | 0.003 | unattributed | 9.6e-04 |
| qwen3-4b-e2ckn.claude46_O_s4 | K_n | O | none | 596 | 0.835 | 0.824 | 0.831 | 0.847 | 0.839 | 0.847 | unattributed | 0.019 | unattributed | 7.6e-04 |
| qwen3-4b-e2ckn.claude46_O_s5 | K_n | O | none | 597 | 0.801 | 0.800 | 0.786 | 0.827 | 0.813 | 0.799 | unattributed | 0.003 | unattributed | 0.014 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | K_n | O | none | 596 | 0.837 | 0.829 | 0.834 | 0.849 | 0.828 | 0.829 | unattributed | 0.002 | unattributed | 0.012 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | K_n | O | none | 596 | 0.828 | 0.815 | 0.812 | 0.829 | 0.825 | 0.822 | unattributed | 0.004 | unattributed | 0.001 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | K_n | O | none | 595 | 0.835 | 0.808 | 0.812 | 0.827 | 0.826 | 0.832 | unattributed | 0.007 | unattributed | 0.002 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | K_n | O | none | 596 | 0.837 | 0.837 | 0.840 | 0.861 | 0.844 | 0.843 | unattributed | 0.011 | unattributed | 0.017 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | K_n | O | none | 596 | 0.833 | 0.830 | 0.843 | 0.851 | 0.846 | 0.833 | unattributed | 0.001 | unattributed | 0.005 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | K_n | O | none | 596 | 0.833 | 0.824 | 0.828 | 0.834 | 0.822 | 0.841 | unattributed | 0.017 | unattributed | 0.007 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | K_n | O | none | 596 | 0.835 | 0.824 | 0.818 | 0.831 | 0.837 | 0.845 | unattributed | 0.019 | unattributed | 0.008 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | K_n | O | none | 596 | 0.822 | 0.805 | 0.802 | 0.812 | 0.818 | 0.833 | unattributed | 0.019 | unattributed | 0.010 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | K_n | O | none | 596 | 0.840 | 0.829 | 0.826 | 0.846 | 0.846 | 0.855 | unattributed | 0.021 | unattributed | 0.010 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | K_n | O | none | 596 | 0.840 | 0.825 | 0.829 | 0.826 | 0.837 | 0.836 | unattributed | 0.005 | unattributed | 0.003 |

## 输入

| namespace | grid | role | version | n_runs | truths |
|---|---|---|---|---|---|
| qwen3-4b | E1 | core | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b | E1 | core | R | 3 | none |
| qwen3-4b-paired | E3 | core | C | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-paired | E3 | core | F | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-paired | E3 | core | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2c | E2c_C | core | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2ck | K | core | O | 15 | none |
| qwen3-4b-e2ckn | K_n | core | O | 15 | none |
| qwen3-4b-e2cnf | Cnf | core | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2c-paired | E3c | core | C | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2c-paired | E3c | core | F | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2c-paired | E3c | core | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2c-3ep | E2c_C_3ep | descriptive | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b-e2ck-3ep | K_3ep | descriptive | O | 15 | none |
| qwen3-4b-e2cnf-5ep | Cnf_5ep | descriptive | O | 15 | claude46,deepseek_v4,gpt4o |
| qwen3-4b | E1 | core | B | 1 | none |

说明：

- version-B copies skipped (S_0 is read once from --base-run): qwen3-4b/base_B_s0, qwen3-4b-e2c/base_B_s0, qwen3-4b-e2ck/base_B_s0, qwen3-4b-e2ckn/base_B_s0, qwen3-4b-e2cnf/base_B_s0, qwen3-4b-e2c-paired/base_B_s0, qwen3-4b-e2c-3ep/base_B_s0, qwen3-4b-e2ck-3ep/base_B_s0, qwen3-4b-e2cnf-5ep/base_B_s0
- true-teacher-absent runs: 55 (truth in ['gpt4o'], not in the candidates ['claude46', 'deepseek_v4', 'gpt41', 'gpt4o_mini', 'gpt4_0613', 'claude_haiku45']); scored against the candidates, kept out of the recall / AUROC groups and of every calibration population's positives, reported in e7_absent.csv

## 预注册之外的实现决定（披露）

- 基座已知的参照 a_t(S_0) 默认用 S_0 的**未门控**两字母概率（`sym_table(mass_gate=False)`，与 E2 的协变量 r_0 同一对象）：门控 readout 下未训练基座只有约 1/6 的 cell 有答案；S_0 作为**被测**负例时仍用门控 readout。`--base-reference gated` 可切换。
- τ 按检测器配置各标一个（变体 × readout × 探针子集 × 预算），全部写入 calibration.json 并在 test 复用；分歧探针与预算曲线同时报自标定 τ 与全 cell τ（tau_policy）。
- 采样 readout 只作用于被测模型；teacher 参照与基座参照保持概率 readout。τ 在 200 次重复的负例 margin 合并后标定。
- leave-one-grid-out 的标定总体 = E1 网格的全部 run（15 个 O 学生一并视为应拒判）+ K / K_n 负例；评估其余网格。
- 置换 p 以 run 为单位（同 teacher 的 seed 为近复本，只作描述）；采样与预算曲线各重复内用 --n-perm-rep 次置换后取均值。
- 不足两个有限分数的 run 记为不判定（margin nan）；AUROC 的负类 = 该网格其余 run + 全部 none 负例。
- phase 2：候选集（--candidates / --drop-candidate）与真值分离；真 teacher 不在候选集的 run 照常打分，但不进召回 / AUROC 组，也不进标定（负例仍是 K / K_n / R / S_0），单独报在 e7_absent.csv；τ 按候选集在 dev 重新标定（规则不变），calibration.json 按候选集（排序后的候选名）分节保存，test 没有对应节则拒绝运行；主判定的 teacher 数 = 主组里有学生的候选。
