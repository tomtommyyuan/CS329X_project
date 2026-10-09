# E7 黑盒溯源（dev，variants T1, T3, T5, T6；E7 detector, tau rule, metrics and verdict pre-registered in tasks/e7_plan.md §3-§4 before any provenance result; not yet frozen (freeze commit pending)；auto-generated）

**主判定（E2c-C 的 O 学生，基座已知，字母概率 readout，全部探针）：部分**（1/3 个 teacher 的召回 Wilson 下界 > 1/3：claude46；开集 FPR 0.029（≤ 10%）；τ = 0.036）。

**dev = 标定 split，以下全部只作描述**（tasks/e7_plan.md §4：阈值只在 dev 定，test 冻结后只跑一次，`--calibration` 复用本次写出的 calibration.json）。

规则（tasks/e7_plan.md §3–4 原文，`vcd.analysis.provenance`）：a_t = run 与 teacher t 的 symmetrized 多数行动一致率（`e1_metrics.teacher_agreement`，p_sym = 0.5 的 cell 不计）；基座已知 s_t = a_t − a_t(S_0)，基座未知 s_t = a_t − mean_t' a_t'；t* = argmax s_t，margin = s_t* − 第二大，margin > τ 判为 t*，否则不判定；τ = 使 dev 负例（K、K_n、R、S_0）被判为任一 teacher 的比例 ≤ 5% 的最小值（负例 < 20 时 τ = 0），每个检测器配置（变体 × readout × 探针子集 × 预算）各一个，test 原样复用；召回 Wilson 95% CI（不判定计错），macro 召回，开集 FPR，一对多 AUROC（以 s_t 为分数，负类含 none），随机参照 (1/3)(1 − 不判定率)，teacher 标签在该网格可判定 run 间置换 10,000 次的 p（seed 为近复本，p 只作描述）。主判定：E2c-C 的 15 个 O 学生，基座已知，字母概率，全部探针：召回 Wilson 下界 > 1/3 的 teacher ≥ 2/3 → 溯源可行（有条件），1/3 → 部分，0/3 → 不可行，并报开集 FPR 是否 ≤ 10%。

## 标定（calibration.json，本次写出）

负例 34 个（E1, K, K_n）；基座参照 = prior（596 个有效 cell / 600）；teacher 分歧 cell 91 / 600；family 150；重复 200；seed 0。

| configuration | tau | n_neg | n_margins | n_attributed | fpr_at_tau | fallback | note |
|---|---|---|---|---|---|---|---|
| main|probability|all|base_known | 0.036 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| main|probability|all|base_unknown | 0.017 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| main|probability|disagreement|base_known | 0.220 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| main|probability|disagreement|base_unknown | 0.088 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| loso|probability|all|base_known | 0.036 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| loso|probability|all|base_unknown | 0.017 | 34 | 34 | 1 | 0.029 | False | 34 negatives, at most 1 may be attributed |
| logo|probability|all|base_known | 0.040 | 49 | 49 | 2 | 0.041 | False | 49 negatives, at most 2 may be attributed |
| logo|probability|all|base_unknown | 0.023 | 49 | 49 | 2 | 0.041 | False | 49 negatives, at most 2 may be attributed |
| main|sampled_n1|all|base_known | 0.039 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n1|all|base_unknown | 0.022 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n3|all|base_known | 0.038 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n3|all|base_unknown | 0.023 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n10|all|base_known | 0.038 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|sampled_n10|all|base_unknown | 0.025 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget30|base_known | 0.086 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget30|base_unknown | 0.069 | 6800 | 6800 | 339 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget60|base_known | 0.066 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget60|base_unknown | 0.045 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget100|base_known | 0.046 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |
| main|probability|budget100|base_unknown | 0.032 | 6800 | 6800 | 340 | 0.050 | False | 6800 negatives, at most 340 may be attributed |

## 主表：基座已知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.814 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E2c_C | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.748 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E2c_C | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.198 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E2c_C | O | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 8.0e-04 | 0.029 | 34 | 0.036 |
| E1 | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.957 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E1 | O | claude46 | 5 | 3 | 0.600 | [0.231, 0.882] | 0.400 | 0.909 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E1 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.861 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E1 | O | macro | 15 | 3 | 0.200 | [nan, nan] | 0.800 | nan | 0.200 | 0.067 | 0.022 | 0.029 | 34 | 0.036 |
| E3 | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.959 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | O | claude46 | 5 | 4 | 0.800 | [0.376, 0.964] | 0.200 | 0.859 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.880 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | O | macro | 15 | 4 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.003 | 0.029 | 34 | 0.036 |
| E3 | F | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.970 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | F | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.864 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | F | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.866 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | F | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 3.0e-04 | 0.029 | 34 | 0.036 |
| E3 | C | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.966 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | C | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.877 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | C | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.877 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3 | C | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 4.0e-04 | 0.029 | 34 | 0.036 |
| E3c | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.852 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.655 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.139 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | O | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 5.0e-04 | 0.029 | 34 | 0.036 |
| E3c | F | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.730 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | F | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.611 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | F | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.132 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | F | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 3.0e-04 | 0.029 | 34 | 0.036 |
| E3c | C | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 0.800 | 0.707 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | C | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.557 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | C | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.127 | nan | nan | nan | 0.029 | 34 | 0.036 |
| E3c | C | macro | 15 | 5 | 0.333 | [nan, nan] | 0.600 | nan | 0.333 | 0.133 | 0.001 | 0.029 | 34 | 0.036 |
| Cnf | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.270 | nan | nan | nan | 0.029 | 34 | 0.036 |
| Cnf | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.298 | nan | nan | nan | 0.029 | 34 | 0.036 |
| Cnf | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.145 | nan | nan | nan | 0.029 | 34 | 0.036 |
| Cnf | O | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 3.0e-04 | 0.029 | 34 | 0.036 |
| E1 | R | none | 3 | 3 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 3 | 0.036 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.036 |
| K | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.036 |
| K_n | O | none | 15 | 14 | 0.933 | [nan, nan] | 0.933 | nan | nan | nan | nan | 0.067 | 15 | 0.036 |

## 主表：基座未知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.873 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E2c_C | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E2c_C | O | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E2c_C | O | macro | 15 | 10 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 | 34 | 0.017 |
| E1 | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.632 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E1 | O | claude46 | 5 | 3 | 0.600 | [0.231, 0.882] | 0.400 | 0.955 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E1 | O | deepseek_v4 | 5 | 2 | 0.400 | [0.118, 0.769] | 0.600 | 0.995 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E1 | O | macro | 15 | 5 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 0.004 | 0.029 | 34 | 0.017 |
| E3 | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.627 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | O | claude46 | 5 | 4 | 0.800 | [0.376, 0.964] | 0.200 | 0.955 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.982 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | O | macro | 15 | 4 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.003 | 0.029 | 34 | 0.017 |
| E3 | F | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.723 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | F | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | F | deepseek_v4 | 5 | 2 | 0.400 | [0.118, 0.769] | 0.600 | 0.991 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | F | macro | 15 | 7 | 0.467 | [nan, nan] | 0.533 | nan | 0.467 | 0.156 | 3.0e-04 | 0.029 | 34 | 0.017 |
| E3 | C | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.841 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | C | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | C | deepseek_v4 | 5 | 4 | 0.800 | [0.376, 0.964] | 0.200 | 0.991 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3 | C | macro | 15 | 9 | 0.600 | [nan, nan] | 0.400 | nan | 0.600 | 0.200 | 1.0e-04 | 0.029 | 34 | 0.017 |
| E3c | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.900 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | O | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | O | macro | 15 | 10 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 | 34 | 0.017 |
| E3c | F | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.814 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | F | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | F | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | F | macro | 15 | 10 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 | 34 | 0.017 |
| E3c | C | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 0.800 | 0.605 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | C | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | C | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| E3c | C | macro | 15 | 10 | 0.667 | [nan, nan] | 0.267 | nan | 0.667 | 0.244 | 1.0e-04 | 0.029 | 34 | 0.017 |
| Cnf | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 0.800 | 0.418 | nan | nan | nan | 0.029 | 34 | 0.017 |
| Cnf | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| Cnf | O | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 | 34 | 0.017 |
| Cnf | O | macro | 15 | 10 | 0.667 | [nan, nan] | 0.267 | nan | 0.667 | 0.244 | 1.0e-04 | 0.029 | 34 | 0.017 |
| E1 | R | none | 3 | 2 | 0.667 | [nan, nan] | 0.667 | nan | nan | nan | nan | 0.333 | 3 | 0.017 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.017 |
| K | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.017 |
| K_n | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.017 |

## 分歧探针（三家多数行动不全同的 cell，91 / 600；τ = 该配置自标定（calibrated）；全 cell 的 τ 作灵敏度（fixed_all_cells，只列 macro 行））

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.220 | E2c_C | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.832 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E2c_C | O | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 2.0e-04 | 0.029 |
| base_known | 0.220 | E1 | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.716 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E1 | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.989 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E1 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.968 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E1 | O | macro | 15 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.004 | 0.029 |
| base_known | 0.220 | E3 | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.757 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.989 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.955 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | O | macro | 15 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.004 | 0.029 |
| base_known | 0.220 | E3 | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.832 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.982 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 3.0e-04 | 0.029 |
| base_known | 0.220 | E3 | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.825 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.982 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3 | C | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 1.0e-03 | 0.029 |
| base_known | 0.220 | E3c | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.889 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | O | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 7.0e-04 | 0.029 |
| base_known | 0.220 | E3c | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.766 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.995 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 3.0e-04 | 0.029 |
| base_known | 0.220 | E3c | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.800 | 0.475 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.993 | nan | nan | nan | 0.029 |
| base_known | 0.220 | E3c | C | macro | 15 | 0.333 | [nan, nan] | 0.600 | nan | 0.333 | 0.133 | 0.002 | 0.029 |
| base_known | 0.220 | Cnf | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.316 | nan | nan | nan | 0.029 |
| base_known | 0.220 | Cnf | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | Cnf | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.029 |
| base_known | 0.220 | Cnf | O | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 6.0e-04 | 0.029 |
| base_unknown | 0.088 | E2c_C | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.857 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E2c_C | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E2c_C | O | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 |
| base_unknown | 0.088 | E1 | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.573 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E1 | O | claude46 | 5 | 0.200 | [0.036, 0.624] | 0.800 | 0.964 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E1 | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.982 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E1 | O | macro | 15 | 0.400 | [nan, nan] | 0.600 | nan | 0.400 | 0.133 | 3.0e-04 | 0.029 |
| base_unknown | 0.088 | E3 | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.800 | 0.605 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.977 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.977 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | O | macro | 15 | 0.600 | [nan, nan] | 0.333 | nan | 0.600 | 0.222 | 3.0e-04 | 0.029 |
| base_unknown | 0.088 | E3 | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.689 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | F | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | F | deepseek_v4 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.991 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | F | macro | 15 | 0.533 | [nan, nan] | 0.467 | nan | 0.533 | 0.178 | 1.0e-04 | 0.029 |
| base_unknown | 0.088 | E3 | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.768 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | C | claude46 | 5 | 0.600 | [0.231, 0.882] | 0.400 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | C | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.982 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3 | C | macro | 15 | 0.533 | [nan, nan] | 0.467 | nan | 0.533 | 0.178 | 1.0e-04 | 0.029 |
| base_unknown | 0.088 | E3c | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.895 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | O | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 |
| base_unknown | 0.088 | E3c | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.752 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | F | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.995 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | F | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 |
| base_unknown | 0.088 | E3c | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.518 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | C | claude46 | 5 | 0.600 | [0.231, 0.882] | 0.400 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | C | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.995 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | E3c | C | macro | 15 | 0.533 | [nan, nan] | 0.467 | nan | 0.533 | 0.178 | 1.0e-04 | 0.029 |
| base_unknown | 0.088 | Cnf | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.000 | 0.295 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | Cnf | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | Cnf | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.088 | Cnf | O | macro | 15 | 0.600 | [nan, nan] | 0.067 | nan | 0.600 | 0.311 | 0.002 | 0.029 |

| detector | tau_policy | tau | grid | version | n | macro_recall | unattributed_rate | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|
| base_known | fixed_all_cells | 0.036 | E2c_C | O | 15 | 0.667 | 0.267 | 0.244 | 1.0e-04 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E1 | O | 15 | 0.333 | 0.200 | 0.267 | 0.270 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E3 | O | 15 | 0.400 | 0.200 | 0.267 | 0.076 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E3 | F | 15 | 0.467 | 0.200 | 0.267 | 0.019 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E3 | C | 15 | 0.400 | 0.267 | 0.244 | 0.042 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E3c | O | 15 | 0.733 | 0.200 | 0.267 | 1.0e-04 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E3c | F | 15 | 0.600 | 0.067 | 0.311 | 0.002 | 1.000 |
| base_known | fixed_all_cells | 0.036 | E3c | C | 15 | 0.467 | 0.200 | 0.267 | 0.020 | 1.000 |
| base_known | fixed_all_cells | 0.036 | Cnf | O | 15 | 0.667 | 0.200 | 0.267 | 1.0e-04 | 1.000 |
| base_unknown | fixed_all_cells | 0.017 | E2c_C | O | 15 | 0.867 | 0.067 | 0.311 | 1.0e-04 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E1 | O | 15 | 0.600 | 0.000 | 0.333 | 0.016 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E3 | O | 15 | 0.600 | 0.067 | 0.311 | 0.002 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E3 | F | 15 | 0.733 | 0.067 | 0.311 | 1.0e-04 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E3 | C | 15 | 0.733 | 0.200 | 0.267 | 1.0e-04 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E3c | O | 15 | 0.867 | 0.000 | 0.333 | 1.0e-04 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E3c | F | 15 | 0.867 | 0.133 | 0.289 | 1.0e-04 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | E3c | C | 15 | 0.733 | 0.200 | 0.267 | 1.0e-04 | 0.824 |
| base_unknown | fixed_all_cells | 0.017 | Cnf | O | 15 | 0.667 | 0.000 | 0.333 | 5.0e-04 | 0.824 |

## 采样 readout：n = 1 / 3 / 10 个答案取多数（每 cell 两序各抽；均值 [2.5, 97.5] 分位，e7_sampled.csv）

macro 召回（行 = 检测器 × 网格，列 = n）：

| detector | grid | version | 1 | 3 | 10 |
|---|---|---|---|---|---|
| base_known | E2c_C | O | 0.329 [0.267, 0.333] | 0.332 [0.333, 0.333] | 0.333 [0.333, 0.333] |
| base_known | E1 | O | 0.115 [0.000, 0.200] | 0.155 [0.067, 0.267] | 0.149 [0.067, 0.267] |
| base_known | E3 | O | 0.200 [0.067, 0.267] | 0.254 [0.200, 0.333] | 0.261 [0.200, 0.267] |
| base_known | E3 | F | 0.290 [0.200, 0.333] | 0.323 [0.267, 0.333] | 0.326 [0.267, 0.333] |
| base_known | E3 | C | 0.214 [0.067, 0.333] | 0.258 [0.198, 0.333] | 0.286 [0.200, 0.333] |
| base_known | E3c | O | 0.314 [0.265, 0.333] | 0.331 [0.267, 0.333] | 0.333 [0.333, 0.333] |
| base_known | E3c | F | 0.331 [0.267, 0.333] | 0.333 [0.333, 0.333] | 0.333 [0.333, 0.333] |
| base_known | E3c | C | 0.327 [0.267, 0.333] | 0.333 [0.333, 0.333] | 0.333 [0.333, 0.333] |
| base_known | Cnf | O | 0.336 [0.333, 0.400] | 0.335 [0.333, 0.335] | 0.334 [0.333, 0.333] |
| base_unknown | E2c_C | O | 0.654 [0.598, 0.733] | 0.651 [0.600, 0.667] | 0.626 [0.533, 0.667] |
| base_unknown | E1 | O | 0.102 [0.000, 0.267] | 0.096 [0.000, 0.200] | 0.042 [0.000, 0.133] |
| base_unknown | E3 | O | 0.168 [0.067, 0.267] | 0.203 [0.067, 0.267] | 0.196 [0.067, 0.267] |
| base_unknown | E3 | F | 0.271 [0.133, 0.333] | 0.299 [0.200, 0.333] | 0.280 [0.200, 0.333] |
| base_unknown | E3 | C | 0.210 [0.067, 0.400] | 0.231 [0.067, 0.335] | 0.202 [0.132, 0.333] |
| base_unknown | E3c | O | 0.623 [0.532, 0.733] | 0.641 [0.533, 0.733] | 0.603 [0.532, 0.667] |
| base_unknown | E3c | F | 0.660 [0.600, 0.667] | 0.663 [0.600, 0.667] | 0.659 [0.600, 0.667] |
| base_unknown | E3c | C | 0.635 [0.533, 0.667] | 0.638 [0.533, 0.667] | 0.613 [0.533, 0.667] |
| base_unknown | Cnf | O | 0.650 [0.600, 0.667] | 0.651 [0.600, 0.667] | 0.648 [0.600, 0.667] |

E2c_C O 学生的每 teacher 召回与 AUROC：

| detector | teacher | 1 | 3 | 10 |
|---|---|---|---|---|
| base_known | gpt4o | 0.000 [0.000, 0.000] / AUROC 0.807 | 0.000 [0.000, 0.000] / AUROC 0.783 | 0.000 [0.000, 0.000] / AUROC 0.787 |
| base_known | claude46 | 0.988 [0.800, 1.000] / AUROC 0.768 | 0.996 [1.000, 1.000] / AUROC 0.754 | 0.998 [1.000, 1.000] / AUROC 0.730 |
| base_known | deepseek_v4 | 0.000 [0.000, 0.000] / AUROC 0.205 | 0.000 [0.000, 0.000] / AUROC 0.204 | 0.000 [0.000, 0.000] / AUROC 0.212 |
| base_unknown | gpt4o | 0.013 [0.000, 0.200] / AUROC 0.879 | 0.002 [0.000, 0.000] / AUROC 0.883 | 0.000 [0.000, 0.000] / AUROC 0.882 |
| base_unknown | claude46 | 0.967 [0.800, 1.000] / AUROC 0.999 | 0.974 [0.800, 1.000] / AUROC 0.999 | 0.920 [0.800, 1.000] / AUROC 0.998 |
| base_unknown | deepseek_v4 | 0.982 [0.800, 1.000] / AUROC 0.992 | 0.977 [0.800, 1.000] / AUROC 0.992 | 0.957 [0.800, 1.000] / AUROC 0.986 |

开集 FPR（各重复均值）与 τ：

| detector | 1 | 3 | 10 |
|---|---|---|---|
| base_known | FPR 0.050 [0.000, 0.118]; τ 0.039 | FPR 0.050 [0.000, 0.088]; τ 0.038 | FPR 0.050 [0.029, 0.088]; τ 0.038 |
| base_unknown | FPR 0.050 [0.000, 0.118]; τ 0.022 | FPR 0.050 [0.000, 0.118]; τ 0.023 | FPR 0.050 [0.000, 0.118]; τ 0.025 |

## 探针预算曲线：随机 k 个 family × 重复（基座参照取同一批 family；均值 [2.5, 97.5]，e7_probe_curve.csv）

macro 召回（行 = 检测器 × τ 策略 × 网格，列 = family 预算 k；calibrated = 该预算自标定的 τ_k，fixed_all_cells = 全 cell 的 τ）：

| detector | tau_policy | grid | version | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|---|
| base_known | calibrated | E2c_C | O | 0.098 [0.000, 0.333] | 0.141 [0.000, 0.333] | 0.228 [0.000, 0.400] | 0.333 [0.333, 0.333] |
| base_known | calibrated | E1 | O | 0.044 [0.000, 0.333] | 0.062 [0.000, 0.267] | 0.099 [0.000, 0.267] | 0.200 [0.200, 0.200] |
| base_known | calibrated | E3 | O | 0.059 [0.000, 0.333] | 0.080 [0.000, 0.333] | 0.135 [0.000, 0.333] | 0.267 [0.267, 0.267] |
| base_known | calibrated | E3 | F | 0.074 [0.000, 0.333] | 0.113 [0.000, 0.333] | 0.196 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | calibrated | E3 | C | 0.065 [0.000, 0.333] | 0.087 [0.000, 0.333] | 0.157 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | calibrated | E3c | O | 0.076 [0.000, 0.333] | 0.115 [0.000, 0.333] | 0.181 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | calibrated | E3c | F | 0.079 [0.000, 0.333] | 0.121 [0.000, 0.333] | 0.197 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | calibrated | E3c | C | 0.083 [0.000, 0.333] | 0.122 [0.000, 0.333] | 0.196 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | calibrated | Cnf | O | 0.083 [0.000, 0.333] | 0.126 [0.000, 0.333] | 0.221 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | E2c_C | O | 0.295 [0.000, 0.667] | 0.316 [0.000, 0.667] | 0.309 [0.000, 0.533] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | E1 | O | 0.169 [0.000, 0.467] | 0.172 [0.000, 0.333] | 0.160 [0.000, 0.333] | 0.200 [0.200, 0.200] |
| base_known | fixed_all_cells | E3 | O | 0.188 [0.000, 0.402] | 0.200 [0.000, 0.335] | 0.198 [0.000, 0.333] | 0.267 [0.267, 0.267] |
| base_known | fixed_all_cells | E3 | F | 0.212 [0.000, 0.467] | 0.242 [0.000, 0.400] | 0.252 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | E3 | C | 0.207 [0.000, 0.467] | 0.217 [0.000, 0.335] | 0.228 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | E3c | O | 0.261 [0.000, 0.667] | 0.271 [0.000, 0.600] | 0.256 [0.000, 0.467] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | E3c | F | 0.264 [0.000, 0.600] | 0.272 [0.000, 0.600] | 0.274 [0.000, 0.468] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | E3c | C | 0.230 [0.000, 0.533] | 0.244 [0.000, 0.400] | 0.253 [0.000, 0.333] | 0.333 [0.333, 0.333] |
| base_known | fixed_all_cells | Cnf | O | 0.274 [0.000, 0.600] | 0.285 [0.000, 0.602] | 0.299 [0.000, 0.600] | 0.333 [0.333, 0.333] |
| base_unknown | calibrated | E2c_C | O | 0.139 [0.000, 0.533] | 0.255 [0.000, 0.667] | 0.456 [0.067, 0.667] | 0.667 [0.667, 0.667] |
| base_unknown | calibrated | E1 | O | 0.054 [0.000, 0.333] | 0.089 [0.000, 0.400] | 0.119 [0.000, 0.400] | 0.333 [0.333, 0.333] |
| base_unknown | calibrated | E3 | O | 0.061 [0.000, 0.333] | 0.091 [0.000, 0.400] | 0.128 [0.000, 0.400] | 0.267 [0.267, 0.267] |
| base_unknown | calibrated | E3 | F | 0.078 [0.000, 0.333] | 0.131 [0.000, 0.467] | 0.199 [0.000, 0.533] | 0.467 [0.467, 0.467] |
| base_unknown | calibrated | E3 | C | 0.071 [0.000, 0.333] | 0.112 [0.000, 0.400] | 0.177 [0.000, 0.533] | 0.600 [0.600, 0.600] |
| base_unknown | calibrated | E3c | O | 0.109 [0.000, 0.335] | 0.197 [0.000, 0.667] | 0.357 [0.000, 0.667] | 0.667 [0.667, 0.667] |
| base_unknown | calibrated | E3c | F | 0.118 [0.000, 0.400] | 0.204 [0.000, 0.667] | 0.387 [0.000, 0.667] | 0.667 [0.667, 0.667] |
| base_unknown | calibrated | E3c | C | 0.102 [0.000, 0.335] | 0.182 [0.000, 0.600] | 0.318 [0.065, 0.667] | 0.667 [0.667, 0.667] |
| base_unknown | calibrated | Cnf | O | 0.127 [0.000, 0.467] | 0.244 [0.000, 0.667] | 0.430 [0.132, 0.667] | 0.667 [0.667, 0.667] |
| base_unknown | fixed_all_cells | E2c_C | O | 0.535 [0.198, 0.933] | 0.611 [0.265, 1.000] | 0.670 [0.400, 0.933] | 0.667 [0.667, 0.667] |
| base_unknown | fixed_all_cells | E1 | O | 0.345 [0.000, 0.667] | 0.351 [0.000, 0.667] | 0.362 [0.067, 0.600] | 0.333 [0.333, 0.333] |
| base_unknown | fixed_all_cells | E3 | O | 0.353 [0.000, 0.667] | 0.361 [0.000, 0.667] | 0.363 [0.000, 0.667] | 0.267 [0.267, 0.267] |
| base_unknown | fixed_all_cells | E3 | F | 0.390 [0.000, 0.667] | 0.413 [0.065, 0.667] | 0.436 [0.133, 0.667] | 0.467 [0.467, 0.467] |
| base_unknown | fixed_all_cells | E3 | C | 0.395 [0.067, 0.667] | 0.418 [0.000, 0.667] | 0.448 [0.133, 0.667] | 0.600 [0.600, 0.600] |
| base_unknown | fixed_all_cells | E3c | O | 0.498 [0.132, 0.933] | 0.571 [0.133, 0.935] | 0.644 [0.333, 0.933] | 0.667 [0.667, 0.667] |
| base_unknown | fixed_all_cells | E3c | F | 0.500 [0.132, 0.867] | 0.560 [0.200, 0.933] | 0.620 [0.333, 0.800] | 0.667 [0.667, 0.667] |
| base_unknown | fixed_all_cells | E3c | C | 0.455 [0.132, 0.735] | 0.494 [0.133, 0.800] | 0.552 [0.265, 0.667] | 0.667 [0.667, 0.667] |
| base_unknown | fixed_all_cells | Cnf | O | 0.477 [0.133, 0.735] | 0.522 [0.198, 0.667] | 0.606 [0.333, 0.667] | 0.667 [0.667, 0.667] |

开集 FPR（各重复均值）与 τ：

| detector | tau_policy | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|
| base_known | calibrated | FPR 0.050 [0.000, 0.324]; τ 0.086 | FPR 0.050 [0.000, 0.471]; τ 0.066 | FPR 0.050 [0.000, 0.383]; τ 0.046 | FPR 0.029 [0.029, 0.029]; τ 0.036 |
| base_known | fixed_all_cells | FPR 0.375 [0.029, 0.941]; τ 0.036 | FPR 0.286 [0.000, 0.912]; τ 0.036 | FPR 0.148 [0.000, 0.735]; τ 0.036 | FPR 0.029 [0.029, 0.029]; τ 0.036 |
| base_unknown | calibrated | FPR 0.050 [0.000, 0.265]; τ 0.069 | FPR 0.050 [0.000, 0.295]; τ 0.045 | FPR 0.050 [0.000, 0.295]; τ 0.032 | FPR 0.029 [0.029, 0.029]; τ 0.017 |
| base_unknown | fixed_all_cells | FPR 0.600 [0.176, 0.971]; τ 0.017 | FPR 0.419 [0.088, 0.941]; τ 0.017 | FPR 0.257 [0.029, 0.795]; τ 0.017 | FPR 0.029 [0.029, 0.029]; τ 0.017 |

E2c_C O 学生的每 teacher 召回：

| detector | tau_policy | teacher | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|
| base_known | calibrated | gpt4o | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | claude46 | 0.289 [0.000, 1.000] | 0.420 [0.000, 1.000] | 0.668 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_known | calibrated | deepseek_v4 | 0.005 [0.000, 0.000] | 0.002 [0.000, 0.000] | 0.016 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | gpt4o | 0.059 [0.000, 0.800] | 0.020 [0.000, 0.200] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | claude46 | 0.616 [0.000, 1.000] | 0.748 [0.000, 1.000] | 0.826 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_known | fixed_all_cells | deepseek_v4 | 0.210 [0.000, 1.000] | 0.180 [0.000, 1.000] | 0.101 [0.000, 0.600] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | gpt4o | 0.005 [0.000, 0.000] | 0.017 [0.000, 0.200] | 0.013 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | claude46 | 0.192 [0.000, 1.000] | 0.358 [0.000, 1.000] | 0.657 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | calibrated | deepseek_v4 | 0.221 [0.000, 1.000] | 0.389 [0.000, 1.000] | 0.699 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | gpt4o | 0.282 [0.000, 1.000] | 0.269 [0.000, 1.000] | 0.153 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | claude46 | 0.626 [0.000, 1.000] | 0.760 [0.000, 1.000] | 0.913 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | deepseek_v4 | 0.696 [0.000, 1.000] | 0.804 [0.000, 1.000] | 0.943 [0.600, 1.000] | 1.000 [1.000, 1.000] |

## leave-one-style-out：τ 只用 O / R / B 的负例标定（与主 τ 相同），认 E3 / E3c 的 F / C 学生（e7_loso.csv）

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.036 | E3 | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.970 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3 | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.864 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.866 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3 | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 5.0e-04 | 0.029 |
| base_known | 0.036 | E3 | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.966 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3 | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.877 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.877 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3 | C | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 5.0e-04 | 0.029 |
| base_known | 0.036 | E3c | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.730 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3c | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.611 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.132 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3c | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 3.0e-04 | 0.029 |
| base_known | 0.036 | E3c | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.800 | 0.707 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3c | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.557 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.127 | nan | nan | nan | 0.029 |
| base_known | 0.036 | E3c | C | macro | 15 | 0.333 | [nan, nan] | 0.600 | nan | 0.333 | 0.133 | 0.002 | 0.029 |
| base_unknown | 0.017 | E3 | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.723 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3 | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3 | F | deepseek_v4 | 5 | 0.400 | [0.118, 0.769] | 0.600 | 0.991 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3 | F | macro | 15 | 0.467 | [nan, nan] | 0.533 | nan | 0.467 | 0.156 | 3.0e-04 | 0.029 |
| base_unknown | 0.017 | E3 | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.841 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3 | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3 | C | deepseek_v4 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.991 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3 | C | macro | 15 | 0.600 | [nan, nan] | 0.400 | nan | 0.600 | 0.200 | 1.0e-04 | 0.029 |
| base_unknown | 0.017 | E3c | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.814 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3c | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3c | F | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3c | F | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.029 |
| base_unknown | 0.017 | E3c | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.800 | 0.605 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3c | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3c | C | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.029 |
| base_unknown | 0.017 | E3c | C | macro | 15 | 0.667 | [nan, nan] | 0.267 | nan | 0.667 | 0.244 | 1.0e-04 | 0.029 |

## leave-one-grid-out：τ 在网格 E1, K, K_n 上标定（E1 的学生一并视为应拒判的总体），用到其余网格（e7_logo.csv）

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.040 | E2c_C | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.814 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.748 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.198 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E2c_C | O | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 5.0e-04 | 0.000 |
| base_known | 0.040 | E3 | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.959 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.859 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.880 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | O | macro | 15 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.004 | 0.000 |
| base_known | 0.040 | E3 | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.970 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.864 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.866 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 5.0e-04 | 0.000 |
| base_known | 0.040 | E3 | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.966 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | C | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.877 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.877 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3 | C | macro | 15 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.004 | 0.000 |
| base_known | 0.040 | E3c | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.852 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.655 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.139 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | O | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 6.0e-04 | 0.000 |
| base_known | 0.040 | E3c | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.730 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.611 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.132 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 4.0e-04 | 0.000 |
| base_known | 0.040 | E3c | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.800 | 0.707 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.557 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.127 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E3c | C | macro | 15 | 0.333 | [nan, nan] | 0.600 | nan | 0.333 | 0.133 | 0.002 | 0.000 |
| base_known | 0.040 | Cnf | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.270 | nan | nan | nan | 0.000 |
| base_known | 0.040 | Cnf | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.298 | nan | nan | nan | 0.000 |
| base_known | 0.040 | Cnf | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.145 | nan | nan | nan | 0.000 |
| base_known | 0.040 | Cnf | O | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 4.0e-04 | 0.000 |
| base_unknown | 0.023 | E2c_C | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.873 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E2c_C | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E2c_C | O | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.000 |
| base_unknown | 0.023 | E3 | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.627 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.955 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.982 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | O | macro | 15 | 0.267 | [nan, nan] | 0.733 | nan | 0.267 | 0.089 | 0.004 | 0.000 |
| base_unknown | 0.023 | E3 | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.723 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | F | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.991 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | F | macro | 15 | 0.333 | [nan, nan] | 0.667 | nan | 0.333 | 0.111 | 4.0e-04 | 0.000 |
| base_unknown | 0.023 | E3 | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.841 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | C | claude46 | 5 | 0.600 | [0.231, 0.882] | 0.400 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | C | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.991 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3 | C | macro | 15 | 0.200 | [nan, nan] | 0.800 | nan | 0.200 | 0.067 | 0.020 | 0.000 |
| base_unknown | 0.023 | E3c | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.900 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | O | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.000 |
| base_unknown | 0.023 | E3c | F | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.814 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | F | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | F | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | F | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.000 |
| base_unknown | 0.023 | E3c | C | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.605 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | C | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | C | deepseek_v4 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E3c | C | macro | 15 | 0.600 | [nan, nan] | 0.400 | nan | 0.600 | 0.200 | 1.0e-04 | 0.000 |
| base_unknown | 0.023 | Cnf | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.418 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | Cnf | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | Cnf | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | Cnf | O | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.000 |

## 描述：负例按类型的误判率（K / K_n / R / S_0）；归档 run；T0

| table | detector | grid | version | n | n_neg_attributed | fpr | tau |
|---|---|---|---|---|---|---|---|
| main | base_known | E1 | R | 3 | 0 | 0.000 | 0.036 |
| main | base_known | E1 | B | 1 | 0 | 0.000 | 0.036 |
| main | base_known | K | O | 15 | 0 | 0.000 | 0.036 |
| main | base_known | K_n | O | 15 | 1 | 0.067 | 0.036 |
| descriptive | base_known | K_3ep | O | 15 | 1 | 0.067 | 0.036 |
| main | base_unknown | E1 | R | 3 | 1 | 0.333 | 0.017 |
| main | base_unknown | E1 | B | 1 | 0 | 0.000 | 0.017 |
| main | base_unknown | K | O | 15 | 0 | 0.000 | 0.017 |
| main | base_unknown | K_n | O | 15 | 0 | 0.000 | 0.017 |
| descriptive | base_unknown | K_3ep | O | 15 | 1 | 0.067 | 0.017 |

归档配方（只有 dev readout；不进标定）：

| detector | grid | version | teacher | n | recall | CI | auroc | macro_recall | fpr |
|---|---|---|---|---|---|---|---|---|---|
| base_known | Cnf_5ep | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.361 | nan | 0.029 |
| base_known | Cnf_5ep | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.445 | nan | 0.029 |
| base_known | Cnf_5ep | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 0.136 | nan | 0.029 |
| base_known | Cnf_5ep | O | macro | 15 | 0.333 | [nan, nan] | nan | 0.333 | 0.029 |
| base_known | E2c_C_3ep | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.961 | nan | 0.029 |
| base_known | E2c_C_3ep | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.880 | nan | 0.029 |
| base_known | E2c_C_3ep | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 0.284 | nan | 0.029 |
| base_known | E2c_C_3ep | O | macro | 15 | 0.333 | [nan, nan] | nan | 0.333 | 0.029 |
| base_known | K_3ep | O | none | 15 | 0.933 | [nan, nan] | nan | nan | 0.067 |
| base_unknown | Cnf_5ep | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.627 | nan | 0.029 |
| base_unknown | Cnf_5ep | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 1.000 | nan | 0.029 |
| base_unknown | Cnf_5ep | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 1.000 | nan | 0.029 |
| base_unknown | Cnf_5ep | O | macro | 15 | 0.667 | [nan, nan] | nan | 0.667 | 0.029 |
| base_unknown | E2c_C_3ep | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 0.932 | nan | 0.029 |
| base_unknown | E2c_C_3ep | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 1.000 | nan | 0.029 |
| base_unknown | E2c_C_3ep | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 1.000 | nan | 0.029 |
| base_unknown | E2c_C_3ep | O | macro | 15 | 0.667 | [nan, nan] | nan | 0.667 | 0.029 |
| base_unknown | K_3ep | O | none | 15 | 0.933 | [nan, nan] | nan | nan | 0.067 |

T0（训练未见的无框架变体，不进分数）：各网格 run 均值的 a_t；对照 seen variants 的 a_t：

| grid | version | a_T0__gpt4o | a_T0__claude46 | a_T0__deepseek_v4 | a__gpt4o | a__claude46 | a__deepseek_v4 |
|---|---|---|---|---|---|---|---|
| E1 | O | 0.880 | 0.859 | 0.851 | 0.837 | 0.835 | 0.835 |
| E1 | R | 0.481 | 0.457 | 0.479 | 0.497 | 0.469 | 0.481 |
| E3 | C | 0.876 | 0.855 | 0.850 | 0.833 | 0.834 | 0.828 |
| E3 | F | 0.881 | 0.860 | 0.852 | 0.832 | 0.832 | 0.829 |
| E3 | O | 0.883 | 0.860 | 0.850 | 0.835 | 0.833 | 0.833 |
| E2c_C | O | 0.828 | 0.806 | 0.812 | 0.795 | 0.795 | 0.797 |
| K | O | 0.852 | 0.848 | 0.849 | 0.829 | 0.830 | 0.815 |
| K_n | O | 0.857 | 0.840 | 0.847 | 0.827 | 0.828 | 0.818 |
| Cnf | O | 0.797 | 0.778 | 0.786 | 0.747 | 0.744 | 0.766 |
| E3c | C | 0.814 | 0.800 | 0.798 | 0.788 | 0.795 | 0.787 |
| E3c | F | 0.823 | 0.810 | 0.804 | 0.790 | 0.791 | 0.791 |
| E3c | O | 0.819 | 0.802 | 0.806 | 0.795 | 0.791 | 0.795 |
| E2c_C_3ep | O | 0.833 | 0.817 | 0.826 | 0.804 | 0.803 | 0.804 |
| K_3ep | O | 0.852 | 0.840 | 0.849 | 0.835 | 0.835 | 0.822 |
| Cnf_5ep | O | 0.811 | 0.791 | 0.806 | 0.769 | 0.767 | 0.782 |
| E1 | B | 0.714 | 0.857 | 0.714 | 0.829 | 0.847 | 0.857 |

## 每 run（e7_runs.csv 节选：grid、真值、a_t、两种分数的判定）

| run_id | grid | version | truth | n_cells_valid | a__gpt4o | a__claude46 | a__deepseek_v4 | decision_known | margin_known | decision_unknown | margin_unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2cnf.claude46_O_s1 | Cnf | O | claude46 | 596 | 0.754 | 0.792 | 0.765 | claude46 | 0.056 | claude46 | 0.027 |
| qwen3-4b-e2cnf.claude46_O_s2 | Cnf | O | claude46 | 597 | 0.765 | 0.794 | 0.768 | claude46 | 0.047 | claude46 | 0.026 |
| qwen3-4b-e2cnf.claude46_O_s3 | Cnf | O | claude46 | 596 | 0.761 | 0.796 | 0.750 | claude46 | 0.053 | claude46 | 0.034 |
| qwen3-4b-e2cnf.claude46_O_s4 | Cnf | O | claude46 | 596 | 0.732 | 0.783 | 0.738 | claude46 | 0.070 | claude46 | 0.045 |
| qwen3-4b-e2cnf.claude46_O_s5 | Cnf | O | claude46 | 596 | 0.760 | 0.801 | 0.750 | claude46 | 0.060 | claude46 | 0.041 |
| qwen3-4b-e2cnf.deepseek_v4_O_s1 | Cnf | O | deepseek_v4 | 596 | 0.714 | 0.680 | 0.751 | unattributed | 0.020 | deepseek_v4 | 0.037 |
| qwen3-4b-e2cnf.deepseek_v4_O_s2 | Cnf | O | deepseek_v4 | 596 | 0.709 | 0.680 | 0.753 | unattributed | 0.027 | deepseek_v4 | 0.044 |
| qwen3-4b-e2cnf.deepseek_v4_O_s3 | Cnf | O | deepseek_v4 | 596 | 0.730 | 0.700 | 0.773 | unattributed | 0.026 | deepseek_v4 | 0.043 |
| qwen3-4b-e2cnf.deepseek_v4_O_s4 | Cnf | O | deepseek_v4 | 596 | 0.720 | 0.691 | 0.758 | unattributed | 0.021 | deepseek_v4 | 0.038 |
| qwen3-4b-e2cnf.deepseek_v4_O_s5 | Cnf | O | deepseek_v4 | 596 | 0.707 | 0.675 | 0.753 | unattributed | 0.028 | deepseek_v4 | 0.046 |
| qwen3-4b-e2cnf.gpt4o_O_s1 | Cnf | O | gpt4o | 597 | 0.756 | 0.735 | 0.775 | unattributed | 0.002 | deepseek_v4 | 0.019 |
| qwen3-4b-e2cnf.gpt4o_O_s2 | Cnf | O | gpt4o | 596 | 0.760 | 0.742 | 0.776 | unattributed | 0.001 | unattributed | 0.017 |
| qwen3-4b-e2cnf.gpt4o_O_s3 | Cnf | O | gpt4o | 597 | 0.784 | 0.764 | 0.800 | unattributed | 9.8e-04 | unattributed | 0.016 |
| qwen3-4b-e2cnf.gpt4o_O_s4 | Cnf | O | gpt4o | 596 | 0.777 | 0.753 | 0.790 | unattributed | 0.004 | unattributed | 0.013 |
| qwen3-4b-e2cnf.gpt4o_O_s5 | Cnf | O | gpt4o | 597 | 0.770 | 0.776 | 0.789 | unattributed | 0.023 | unattributed | 0.012 |
| qwen3-4b.base_B_s0 | E1 | B | none | 105 | 0.829 | 0.847 | 0.857 | unattributed | 0.025 | unattributed | 0.010 |
| qwen3-4b.claude46_O_s1 | E1 | O | claude46 | 596 | 0.829 | 0.853 | 0.803 | claude46 | 0.042 | claude46 | 0.023 |
| qwen3-4b.claude46_O_s2 | E1 | O | claude46 | 596 | 0.822 | 0.844 | 0.798 | claude46 | 0.040 | claude46 | 0.021 |
| qwen3-4b.claude46_O_s3 | E1 | O | claude46 | 596 | 0.841 | 0.837 | 0.812 | unattributed | 0.013 | unattributed | 0.005 |
| qwen3-4b.claude46_O_s4 | E1 | O | claude46 | 596 | 0.815 | 0.847 | 0.800 | claude46 | 0.050 | claude46 | 0.032 |
| qwen3-4b.claude46_O_s5 | E1 | O | claude46 | 596 | 0.836 | 0.851 | 0.808 | unattributed | 0.033 | unattributed | 0.015 |
| qwen3-4b.deepseek_v4_O_s1 | E1 | O | deepseek_v4 | 596 | 0.819 | 0.808 | 0.834 | unattributed | 0.008 | unattributed | 0.015 |
| qwen3-4b.deepseek_v4_O_s2 | E1 | O | deepseek_v4 | 596 | 0.829 | 0.817 | 0.857 | unattributed | 0.005 | deepseek_v4 | 0.028 |
| qwen3-4b.deepseek_v4_O_s3 | E1 | O | deepseek_v4 | 596 | 0.833 | 0.822 | 0.847 | unattributed | 0.008 | unattributed | 0.014 |
| qwen3-4b.deepseek_v4_O_s4 | E1 | O | deepseek_v4 | 596 | 0.824 | 0.817 | 0.839 | unattributed | 0.011 | unattributed | 0.015 |
| qwen3-4b.deepseek_v4_O_s5 | E1 | O | deepseek_v4 | 596 | 0.826 | 0.822 | 0.844 | unattributed | 0.014 | deepseek_v4 | 0.018 |
| qwen3-4b.gpt4o_O_s1 | E1 | O | gpt4o | 596 | 0.861 | 0.844 | 0.861 | unattributed | 0.001 | unattributed | 1.2e-04 |
| qwen3-4b.gpt4o_O_s2 | E1 | O | gpt4o | 596 | 0.841 | 0.838 | 0.844 | unattributed | 0.015 | unattributed | 0.002 |
| qwen3-4b.gpt4o_O_s3 | E1 | O | gpt4o | 596 | 0.857 | 0.831 | 0.849 | unattributed | 0.008 | unattributed | 0.008 |
| qwen3-4b.gpt4o_O_s4 | E1 | O | gpt4o | 596 | 0.859 | 0.838 | 0.862 | unattributed | 0.002 | unattributed | 0.003 |
| qwen3-4b.gpt4o_O_s5 | E1 | O | gpt4o | 596 | 0.862 | 0.851 | 0.864 | unattributed | 0.007 | unattributed | 0.001 |
| qwen3-4b.random_R_s1 | E1 | R | none | 596 | 0.594 | 0.542 | 0.585 | unattributed | 0.027 | unattributed | 0.009 |
| qwen3-4b.random_R_s2 | E1 | R | none | 596 | 0.465 | 0.439 | 0.444 | unattributed | 0.008 | gpt4o | 0.021 |
| qwen3-4b.random_R_s3 | E1 | R | none | 596 | 0.432 | 0.426 | 0.415 | unattributed | 0.012 | unattributed | 0.006 |
| qwen3-4b-e2c.claude46_O_s1 | E2c_C | O | claude46 | 596 | 0.798 | 0.833 | 0.766 | claude46 | 0.053 | claude46 | 0.035 |
| qwen3-4b-e2c.claude46_O_s2 | E2c_C | O | claude46 | 596 | 0.803 | 0.833 | 0.773 | claude46 | 0.048 | claude46 | 0.030 |
| qwen3-4b-e2c.claude46_O_s3 | E2c_C | O | claude46 | 596 | 0.812 | 0.853 | 0.782 | claude46 | 0.059 | claude46 | 0.041 |
| qwen3-4b-e2c.claude46_O_s4 | E2c_C | O | claude46 | 596 | 0.782 | 0.826 | 0.768 | claude46 | 0.062 | claude46 | 0.044 |
| qwen3-4b-e2c.claude46_O_s5 | E2c_C | O | claude46 | 596 | 0.800 | 0.838 | 0.778 | claude46 | 0.057 | claude46 | 0.039 |
| qwen3-4b-e2c.deepseek_v4_O_s1 | E2c_C | O | deepseek_v4 | 596 | 0.744 | 0.721 | 0.792 | unattributed | 0.030 | deepseek_v4 | 0.048 |
| qwen3-4b-e2c.deepseek_v4_O_s2 | E2c_C | O | deepseek_v4 | 596 | 0.770 | 0.751 | 0.802 | unattributed | 0.014 | deepseek_v4 | 0.032 |
| qwen3-4b-e2c.deepseek_v4_O_s3 | E2c_C | O | deepseek_v4 | 596 | 0.725 | 0.707 | 0.766 | unattributed | 0.024 | deepseek_v4 | 0.042 |
| qwen3-4b-e2c.deepseek_v4_O_s4 | E2c_C | O | deepseek_v4 | 596 | 0.747 | 0.726 | 0.782 | unattributed | 0.017 | deepseek_v4 | 0.034 |
| qwen3-4b-e2c.deepseek_v4_O_s5 | E2c_C | O | deepseek_v4 | 596 | 0.751 | 0.728 | 0.798 | unattributed | 0.030 | deepseek_v4 | 0.047 |
| qwen3-4b-e2c.gpt4o_O_s1 | E2c_C | O | gpt4o | 596 | 0.838 | 0.822 | 0.832 | unattributed | 0.003 | unattributed | 0.006 |
| qwen3-4b-e2c.gpt4o_O_s2 | E2c_C | O | gpt4o | 596 | 0.834 | 0.810 | 0.827 | unattributed | 0.006 | unattributed | 0.008 |
| qwen3-4b-e2c.gpt4o_O_s3 | E2c_C | O | gpt4o | 596 | 0.848 | 0.831 | 0.835 | unattributed | 0.001 | unattributed | 0.013 |
| qwen3-4b-e2c.gpt4o_O_s4 | E2c_C | O | gpt4o | 596 | 0.836 | 0.826 | 0.820 | unattributed | 0.008 | unattributed | 0.010 |
| qwen3-4b-e2c.gpt4o_O_s5 | E2c_C | O | gpt4o | 596 | 0.838 | 0.824 | 0.829 | unattributed | 0.004 | unattributed | 0.009 |
| qwen3-4b-paired.claude46_C_s1 | E3 | C | claude46 | 596 | 0.815 | 0.847 | 0.790 | claude46 | 0.050 | claude46 | 0.032 |
| qwen3-4b-paired.claude46_C_s2 | E3 | C | claude46 | 596 | 0.817 | 0.845 | 0.792 | claude46 | 0.047 | claude46 | 0.028 |
| qwen3-4b-paired.claude46_C_s3 | E3 | C | claude46 | 596 | 0.829 | 0.847 | 0.805 | claude46 | 0.036 | claude46 | 0.018 |
| qwen3-4b-paired.claude46_C_s4 | E3 | C | claude46 | 596 | 0.819 | 0.842 | 0.793 | claude46 | 0.041 | claude46 | 0.023 |
| qwen3-4b-paired.claude46_C_s5 | E3 | C | claude46 | 595 | 0.801 | 0.840 | 0.791 | claude46 | 0.057 | claude46 | 0.039 |
| qwen3-4b-paired.deepseek_v4_C_s1 | E3 | C | deepseek_v4 | 596 | 0.819 | 0.813 | 0.840 | unattributed | 0.009 | deepseek_v4 | 0.022 |
| qwen3-4b-paired.deepseek_v4_C_s2 | E3 | C | deepseek_v4 | 593 | 0.818 | 0.812 | 0.836 | unattributed | 0.012 | deepseek_v4 | 0.018 |
| qwen3-4b-paired.deepseek_v4_C_s3 | E3 | C | deepseek_v4 | 596 | 0.826 | 0.813 | 0.844 | unattributed | 0.005 | deepseek_v4 | 0.018 |
| qwen3-4b-paired.deepseek_v4_C_s4 | E3 | C | deepseek_v4 | 596 | 0.833 | 0.810 | 0.854 | unattributed | 0.004 | deepseek_v4 | 0.021 |
| qwen3-4b-paired.deepseek_v4_C_s5 | E3 | C | deepseek_v4 | 596 | 0.829 | 0.826 | 0.837 | unattributed | 0.015 | unattributed | 0.008 |
| qwen3-4b-paired.gpt4o_C_s1 | E3 | C | gpt4o | 596 | 0.859 | 0.831 | 0.844 | unattributed | 0.009 | unattributed | 0.015 |
| qwen3-4b-paired.gpt4o_C_s2 | E3 | C | gpt4o | 596 | 0.861 | 0.851 | 0.847 | unattributed | 0.008 | unattributed | 0.010 |
| qwen3-4b-paired.gpt4o_C_s3 | E3 | C | gpt4o | 596 | 0.848 | 0.840 | 0.835 | unattributed | 0.010 | unattributed | 0.008 |
| qwen3-4b-paired.gpt4o_C_s4 | E3 | C | gpt4o | 596 | 0.861 | 0.840 | 0.854 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-paired.gpt4o_C_s5 | E3 | C | gpt4o | 596 | 0.857 | 0.844 | 0.854 | unattributed | 0.005 | unattributed | 0.003 |
| qwen3-4b-paired.claude46_F_s1 | E3 | F | claude46 | 596 | 0.814 | 0.845 | 0.795 | claude46 | 0.050 | claude46 | 0.032 |
| qwen3-4b-paired.claude46_F_s2 | E3 | F | claude46 | 596 | 0.807 | 0.847 | 0.795 | claude46 | 0.059 | claude46 | 0.041 |
| qwen3-4b-paired.claude46_F_s3 | E3 | F | claude46 | 596 | 0.805 | 0.838 | 0.792 | claude46 | 0.052 | claude46 | 0.033 |
| qwen3-4b-paired.claude46_F_s4 | E3 | F | claude46 | 596 | 0.819 | 0.853 | 0.795 | claude46 | 0.052 | claude46 | 0.034 |
| qwen3-4b-paired.claude46_F_s5 | E3 | F | claude46 | 596 | 0.810 | 0.837 | 0.797 | claude46 | 0.045 | claude46 | 0.026 |
| qwen3-4b-paired.deepseek_v4_F_s1 | E3 | F | deepseek_v4 | 596 | 0.821 | 0.799 | 0.839 | unattributed | 7.6e-04 | deepseek_v4 | 0.018 |
| qwen3-4b-paired.deepseek_v4_F_s2 | E3 | F | deepseek_v4 | 596 | 0.824 | 0.819 | 0.842 | unattributed | 0.012 | deepseek_v4 | 0.018 |
| qwen3-4b-paired.deepseek_v4_F_s3 | E3 | F | deepseek_v4 | 596 | 0.836 | 0.817 | 0.849 | unattributed | 9.6e-04 | unattributed | 0.013 |
| qwen3-4b-paired.deepseek_v4_F_s4 | E3 | F | deepseek_v4 | 596 | 0.831 | 0.803 | 0.845 | unattributed | 0.003 | unattributed | 0.014 |
| qwen3-4b-paired.deepseek_v4_F_s5 | E3 | F | deepseek_v4 | 596 | 0.833 | 0.808 | 0.837 | unattributed | 0.006 | unattributed | 0.004 |
| qwen3-4b-paired.gpt4o_F_s1 | E3 | F | gpt4o | 596 | 0.864 | 0.853 | 0.850 | unattributed | 0.007 | unattributed | 0.012 |
| qwen3-4b-paired.gpt4o_F_s2 | E3 | F | gpt4o | 596 | 0.848 | 0.842 | 0.837 | unattributed | 0.012 | unattributed | 0.007 |
| qwen3-4b-paired.gpt4o_F_s3 | E3 | F | gpt4o | 596 | 0.861 | 0.837 | 0.861 | unattributed | 0.006 | unattributed | 1.2e-04 |
| qwen3-4b-paired.gpt4o_F_s4 | E3 | F | gpt4o | 596 | 0.855 | 0.840 | 0.852 | unattributed | 0.003 | unattributed | 0.003 |
| qwen3-4b-paired.gpt4o_F_s5 | E3 | F | gpt4o | 596 | 0.852 | 0.840 | 0.857 | unattributed | 0.006 | unattributed | 0.005 |
| qwen3-4b-paired.claude46_O_s1 | E3 | O | claude46 | 596 | 0.822 | 0.851 | 0.800 | claude46 | 0.047 | claude46 | 0.028 |
| qwen3-4b-paired.claude46_O_s2 | E3 | O | claude46 | 596 | 0.805 | 0.835 | 0.788 | claude46 | 0.048 | claude46 | 0.030 |
| qwen3-4b-paired.claude46_O_s3 | E3 | O | claude46 | 596 | 0.829 | 0.835 | 0.818 | unattributed | 0.024 | unattributed | 0.006 |
| qwen3-4b-paired.claude46_O_s4 | E3 | O | claude46 | 596 | 0.828 | 0.858 | 0.803 | claude46 | 0.049 | claude46 | 0.030 |
| qwen3-4b-paired.claude46_O_s5 | E3 | O | claude46 | 595 | 0.820 | 0.847 | 0.803 | claude46 | 0.045 | claude46 | 0.027 |
| qwen3-4b-paired.deepseek_v4_O_s1 | E3 | O | deepseek_v4 | 596 | 0.826 | 0.801 | 0.840 | unattributed | 0.003 | unattributed | 0.015 |
| qwen3-4b-paired.deepseek_v4_O_s2 | E3 | O | deepseek_v4 | 596 | 0.834 | 0.819 | 0.844 | unattributed | 0.003 | unattributed | 0.009 |
| qwen3-4b-paired.deepseek_v4_O_s3 | E3 | O | deepseek_v4 | 596 | 0.836 | 0.819 | 0.852 | unattributed | 8.2e-04 | unattributed | 0.016 |
| qwen3-4b-paired.deepseek_v4_O_s4 | E3 | O | deepseek_v4 | 594 | 0.832 | 0.822 | 0.847 | unattributed | 0.008 | unattributed | 0.014 |
| qwen3-4b-paired.deepseek_v4_O_s5 | E3 | O | deepseek_v4 | 596 | 0.833 | 0.821 | 0.840 | unattributed | 0.006 | unattributed | 0.008 |
| qwen3-4b-paired.gpt4o_O_s1 | E3 | O | gpt4o | 596 | 0.857 | 0.837 | 0.852 | unattributed | 0.002 | unattributed | 0.005 |
| qwen3-4b-paired.gpt4o_O_s2 | E3 | O | gpt4o | 596 | 0.843 | 0.840 | 0.835 | unattributed | 0.015 | unattributed | 0.003 |
| qwen3-4b-paired.gpt4o_O_s3 | E3 | O | gpt4o | 596 | 0.857 | 0.833 | 0.850 | unattributed | 0.006 | unattributed | 0.007 |
| qwen3-4b-paired.gpt4o_O_s4 | E3 | O | gpt4o | 596 | 0.855 | 0.845 | 0.862 | unattributed | 0.008 | unattributed | 0.007 |
| qwen3-4b-paired.gpt4o_O_s5 | E3 | O | gpt4o | 596 | 0.852 | 0.840 | 0.861 | unattributed | 0.006 | unattributed | 0.009 |
| qwen3-4b-e2c-paired.claude46_C_s1 | E3c | C | claude46 | 596 | 0.807 | 0.844 | 0.776 | claude46 | 0.055 | claude46 | 0.037 |
| qwen3-4b-e2c-paired.claude46_C_s2 | E3c | C | claude46 | 596 | 0.786 | 0.812 | 0.755 | claude46 | 0.044 | claude46 | 0.026 |
| qwen3-4b-e2c-paired.claude46_C_s3 | E3c | C | claude46 | 597 | 0.784 | 0.831 | 0.760 | claude46 | 0.065 | claude46 | 0.047 |
| qwen3-4b-e2c-paired.claude46_C_s4 | E3c | C | claude46 | 596 | 0.801 | 0.835 | 0.782 | claude46 | 0.052 | claude46 | 0.033 |
| qwen3-4b-e2c-paired.claude46_C_s5 | E3c | C | claude46 | 596 | 0.794 | 0.821 | 0.768 | claude46 | 0.044 | claude46 | 0.026 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s1 | E3c | C | deepseek_v4 | 595 | 0.723 | 0.709 | 0.749 | unattributed | 0.005 | deepseek_v4 | 0.027 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s2 | E3c | C | deepseek_v4 | 596 | 0.728 | 0.728 | 0.773 | unattributed | 0.009 | deepseek_v4 | 0.045 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s3 | E3c | C | deepseek_v4 | 596 | 0.744 | 0.721 | 0.761 | unattributed | 1.0e-04 | deepseek_v4 | 0.017 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s4 | E3c | C | deepseek_v4 | 596 | 0.739 | 0.723 | 0.773 | unattributed | 0.015 | deepseek_v4 | 0.034 |
| qwen3-4b-e2c-paired.deepseek_v4_C_s5 | E3c | C | deepseek_v4 | 596 | 0.763 | 0.753 | 0.788 | unattributed | 4.4e-04 | deepseek_v4 | 0.025 |
| qwen3-4b-e2c-paired.gpt4o_C_s1 | E3c | C | gpt4o | 596 | 0.841 | 0.833 | 0.832 | unattributed | 0.010 | unattributed | 0.008 |
| qwen3-4b-e2c-paired.gpt4o_C_s2 | E3c | C | gpt4o | 596 | 0.801 | 0.828 | 0.805 | claude46 | 0.045 | claude46 | 0.023 |
| qwen3-4b-e2c-paired.gpt4o_C_s3 | E3c | C | gpt4o | 596 | 0.831 | 0.817 | 0.824 | unattributed | 0.004 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.gpt4o_C_s4 | E3c | C | gpt4o | 596 | 0.836 | 0.824 | 0.830 | unattributed | 0.006 | unattributed | 0.006 |
| qwen3-4b-e2c-paired.gpt4o_C_s5 | E3c | C | gpt4o | 596 | 0.840 | 0.840 | 0.827 | unattributed | 0.019 | unattributed | 4.2e-04 |
| qwen3-4b-e2c-paired.claude46_F_s1 | E3c | F | claude46 | 596 | 0.796 | 0.822 | 0.773 | claude46 | 0.044 | claude46 | 0.026 |
| qwen3-4b-e2c-paired.claude46_F_s2 | E3c | F | claude46 | 596 | 0.801 | 0.829 | 0.775 | claude46 | 0.046 | claude46 | 0.028 |
| qwen3-4b-e2c-paired.claude46_F_s3 | E3c | F | claude46 | 596 | 0.800 | 0.842 | 0.780 | claude46 | 0.060 | claude46 | 0.042 |
| qwen3-4b-e2c-paired.claude46_F_s4 | E3c | F | claude46 | 596 | 0.793 | 0.828 | 0.770 | claude46 | 0.053 | claude46 | 0.035 |
| qwen3-4b-e2c-paired.claude46_F_s5 | E3c | F | claude46 | 596 | 0.798 | 0.831 | 0.770 | claude46 | 0.052 | claude46 | 0.033 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s1 | E3c | F | deepseek_v4 | 597 | 0.739 | 0.734 | 0.765 | unattributed | 0.004 | deepseek_v4 | 0.026 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s2 | E3c | F | deepseek_v4 | 594 | 0.743 | 0.721 | 0.781 | unattributed | 0.020 | deepseek_v4 | 0.038 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s3 | E3c | F | deepseek_v4 | 595 | 0.740 | 0.725 | 0.778 | unattributed | 0.018 | deepseek_v4 | 0.038 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s4 | E3c | F | deepseek_v4 | 596 | 0.726 | 0.707 | 0.765 | unattributed | 0.021 | deepseek_v4 | 0.038 |
| qwen3-4b-e2c-paired.deepseek_v4_F_s5 | E3c | F | deepseek_v4 | 596 | 0.740 | 0.718 | 0.787 | unattributed | 0.029 | deepseek_v4 | 0.046 |
| qwen3-4b-e2c-paired.gpt4o_F_s1 | E3c | F | gpt4o | 596 | 0.847 | 0.838 | 0.837 | unattributed | 0.010 | unattributed | 0.008 |
| qwen3-4b-e2c-paired.gpt4o_F_s2 | E3c | F | gpt4o | 596 | 0.836 | 0.829 | 0.825 | unattributed | 0.011 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.gpt4o_F_s3 | E3c | F | gpt4o | 596 | 0.836 | 0.819 | 0.829 | unattributed | 8.2e-04 | unattributed | 0.008 |
| qwen3-4b-e2c-paired.gpt4o_F_s4 | E3c | F | gpt4o | 596 | 0.833 | 0.819 | 0.822 | unattributed | 0.004 | unattributed | 0.011 |
| qwen3-4b-e2c-paired.gpt4o_F_s5 | E3c | F | gpt4o | 596 | 0.822 | 0.806 | 0.815 | unattributed | 0.002 | unattributed | 0.007 |
| qwen3-4b-e2c-paired.claude46_O_s1 | E3c | O | claude46 | 596 | 0.801 | 0.833 | 0.778 | claude46 | 0.050 | claude46 | 0.032 |
| qwen3-4b-e2c-paired.claude46_O_s2 | E3c | O | claude46 | 596 | 0.812 | 0.842 | 0.785 | claude46 | 0.048 | claude46 | 0.030 |
| qwen3-4b-e2c-paired.claude46_O_s3 | E3c | O | claude46 | 596 | 0.793 | 0.826 | 0.773 | claude46 | 0.051 | claude46 | 0.033 |
| qwen3-4b-e2c-paired.claude46_O_s4 | E3c | O | claude46 | 596 | 0.793 | 0.829 | 0.773 | claude46 | 0.055 | claude46 | 0.037 |
| qwen3-4b-e2c-paired.claude46_O_s5 | E3c | O | claude46 | 596 | 0.800 | 0.824 | 0.773 | claude46 | 0.043 | claude46 | 0.025 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s1 | E3c | O | deepseek_v4 | 596 | 0.744 | 0.725 | 0.778 | unattributed | 0.017 | deepseek_v4 | 0.034 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s2 | E3c | O | deepseek_v4 | 596 | 0.756 | 0.735 | 0.787 | unattributed | 0.013 | deepseek_v4 | 0.030 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s3 | E3c | O | deepseek_v4 | 596 | 0.737 | 0.714 | 0.776 | unattributed | 0.022 | deepseek_v4 | 0.040 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s4 | E3c | O | deepseek_v4 | 596 | 0.726 | 0.703 | 0.766 | unattributed | 0.023 | deepseek_v4 | 0.040 |
| qwen3-4b-e2c-paired.deepseek_v4_O_s5 | E3c | O | deepseek_v4 | 596 | 0.749 | 0.723 | 0.780 | unattributed | 0.013 | deepseek_v4 | 0.031 |
| qwen3-4b-e2c-paired.gpt4o_O_s1 | E3c | O | gpt4o | 596 | 0.840 | 0.821 | 0.827 | unattributed | 8.9e-04 | unattributed | 0.013 |
| qwen3-4b-e2c-paired.gpt4o_O_s2 | E3c | O | gpt4o | 596 | 0.840 | 0.821 | 0.834 | unattributed | 8.9e-04 | unattributed | 0.006 |
| qwen3-4b-e2c-paired.gpt4o_O_s3 | E3c | O | gpt4o | 596 | 0.850 | 0.828 | 0.847 | unattributed | 0.004 | unattributed | 0.003 |
| qwen3-4b-e2c-paired.gpt4o_O_s4 | E3c | O | gpt4o | 596 | 0.831 | 0.817 | 0.815 | unattributed | 0.004 | unattributed | 0.014 |
| qwen3-4b-e2c-paired.gpt4o_O_s5 | E3c | O | gpt4o | 596 | 0.847 | 0.819 | 0.832 | unattributed | 0.010 | unattributed | 0.015 |
| qwen3-4b-e2ck.claude46_O_s1 | K | O | none | 596 | 0.824 | 0.824 | 0.812 | unattributed | 0.018 | unattributed | 1.1e-04 |
| qwen3-4b-e2ck.claude46_O_s2 | K | O | none | 596 | 0.833 | 0.835 | 0.827 | unattributed | 0.020 | unattributed | 0.002 |
| qwen3-4b-e2ck.claude46_O_s3 | K | O | none | 596 | 0.803 | 0.817 | 0.792 | unattributed | 0.032 | unattributed | 0.014 |
| qwen3-4b-e2ck.claude46_O_s4 | K | O | none | 596 | 0.841 | 0.833 | 0.822 | unattributed | 0.010 | unattributed | 0.008 |
| qwen3-4b-e2ck.claude46_O_s5 | K | O | none | 597 | 0.810 | 0.822 | 0.799 | unattributed | 0.030 | unattributed | 0.012 |
| qwen3-4b-e2ck.deepseek_v4_O_s1 | K | O | none | 596 | 0.815 | 0.824 | 0.803 | unattributed | 0.027 | unattributed | 0.009 |
| qwen3-4b-e2ck.deepseek_v4_O_s2 | K | O | none | 596 | 0.836 | 0.835 | 0.834 | unattributed | 0.017 | unattributed | 0.001 |
| qwen3-4b-e2ck.deepseek_v4_O_s3 | K | O | none | 596 | 0.798 | 0.815 | 0.797 | unattributed | 0.036 | unattributed | 0.017 |
| qwen3-4b-e2ck.deepseek_v4_O_s4 | K | O | none | 596 | 0.848 | 0.847 | 0.832 | unattributed | 0.017 | unattributed | 0.001 |
| qwen3-4b-e2ck.deepseek_v4_O_s5 | K | O | none | 596 | 0.828 | 0.824 | 0.810 | unattributed | 0.015 | unattributed | 0.003 |
| qwen3-4b-e2ck.gpt4o_O_s1 | K | O | none | 596 | 0.862 | 0.847 | 0.845 | unattributed | 0.003 | unattributed | 0.015 |
| qwen3-4b-e2ck.gpt4o_O_s2 | K | O | none | 596 | 0.829 | 0.824 | 0.817 | unattributed | 0.013 | unattributed | 0.005 |
| qwen3-4b-e2ck.gpt4o_O_s3 | K | O | none | 594 | 0.827 | 0.820 | 0.809 | unattributed | 0.011 | unattributed | 0.007 |
| qwen3-4b-e2ck.gpt4o_O_s4 | K | O | none | 596 | 0.828 | 0.833 | 0.808 | unattributed | 0.024 | unattributed | 0.006 |
| qwen3-4b-e2ck.gpt4o_O_s5 | K | O | none | 596 | 0.847 | 0.849 | 0.824 | unattributed | 0.021 | unattributed | 0.002 |
| qwen3-4b-e2ckn.claude46_O_s1 | K_n | O | none | 596 | 0.814 | 0.822 | 0.808 | unattributed | 0.027 | unattributed | 0.009 |
| qwen3-4b-e2ckn.claude46_O_s2 | K_n | O | none | 596 | 0.822 | 0.821 | 0.818 | unattributed | 0.017 | unattributed | 0.002 |
| qwen3-4b-e2ckn.claude46_O_s3 | K_n | O | none | 597 | 0.787 | 0.806 | 0.797 | claude46 | 0.037 | unattributed | 0.009 |
| qwen3-4b-e2ckn.claude46_O_s4 | K_n | O | none | 596 | 0.840 | 0.835 | 0.824 | unattributed | 0.013 | unattributed | 0.005 |
| qwen3-4b-e2ckn.claude46_O_s5 | K_n | O | none | 597 | 0.793 | 0.801 | 0.800 | unattributed | 0.026 | unattributed | 7.3e-04 |
| qwen3-4b-e2ckn.deepseek_v4_O_s1 | K_n | O | none | 596 | 0.838 | 0.837 | 0.829 | unattributed | 0.017 | unattributed | 0.001 |
| qwen3-4b-e2ckn.deepseek_v4_O_s2 | K_n | O | none | 596 | 0.826 | 0.828 | 0.815 | unattributed | 0.020 | unattributed | 0.002 |
| qwen3-4b-e2ckn.deepseek_v4_O_s3 | K_n | O | none | 595 | 0.825 | 0.835 | 0.808 | unattributed | 0.027 | unattributed | 0.009 |
| qwen3-4b-e2ckn.deepseek_v4_O_s4 | K_n | O | none | 596 | 0.850 | 0.837 | 0.837 | unattributed | 0.005 | unattributed | 0.013 |
| qwen3-4b-e2ckn.deepseek_v4_O_s5 | K_n | O | none | 596 | 0.850 | 0.833 | 0.830 | unattributed | 0.001 | unattributed | 0.017 |
| qwen3-4b-e2ckn.gpt4o_O_s1 | K_n | O | none | 596 | 0.836 | 0.833 | 0.824 | unattributed | 0.015 | unattributed | 0.003 |
| qwen3-4b-e2ckn.gpt4o_O_s2 | K_n | O | none | 596 | 0.829 | 0.835 | 0.824 | unattributed | 0.024 | unattributed | 0.006 |
| qwen3-4b-e2ckn.gpt4o_O_s3 | K_n | O | none | 596 | 0.817 | 0.822 | 0.805 | unattributed | 0.024 | unattributed | 0.005 |
| qwen3-4b-e2ckn.gpt4o_O_s4 | K_n | O | none | 596 | 0.834 | 0.840 | 0.829 | unattributed | 0.024 | unattributed | 0.006 |
| qwen3-4b-e2ckn.gpt4o_O_s5 | K_n | O | none | 596 | 0.838 | 0.840 | 0.825 | unattributed | 0.020 | unattributed | 0.002 |

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

## 预注册之外的实现决定（披露）

- 基座已知的参照 a_t(S_0) 默认用 S_0 的**未门控**两字母概率（`sym_table(mass_gate=False)`，与 E2 的协变量 r_0 同一对象）：门控 readout 下未训练基座只有约 1/6 的 cell 有答案；S_0 作为**被测**负例时仍用门控 readout。`--base-reference gated` 可切换。
- τ 按检测器配置各标一个（变体 × readout × 探针子集 × 预算），全部写入 calibration.json 并在 test 复用；分歧探针与预算曲线同时报自标定 τ 与全 cell τ（tau_policy）。
- 采样 readout 只作用于被测模型；teacher 参照与基座参照保持概率 readout。τ 在 200 次重复的负例 margin 合并后标定。
- leave-one-grid-out 的标定总体 = E1 网格的全部 run（15 个 O 学生一并视为应拒判）+ K / K_n 负例；评估其余网格。
- 置换 p 以 run 为单位（同 teacher 的 seed 为近复本，只作描述）；采样与预算曲线各重复内用 --n-perm-rep 次置换后取均值。
- 不足两个有限分数的 run 记为不判定（margin nan）；AUROC 的负类 = 该网格其余 run + 全部 none 负例。
