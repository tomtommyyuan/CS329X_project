# E7 黑盒溯源（dev，variants T1, T3, T5, T6；E7 detector, tau rule, metrics and verdict pre-registered in tasks/e7_plan.md §3-§4 before any provenance result; not yet frozen (freeze commit pending)；auto-generated）

**主判定（E2c-C 的 O 学生，基座已知，字母概率 readout，全部探针）：溯源可行（有条件）**（2/3 个 teacher 的召回 Wilson 下界 > 1/3：gpt4o, claude46；开集 FPR 0.938（> 10%）；τ = 0.000）。

**dev = 标定 split，以下全部只作描述**（tasks/e7_plan.md §4：阈值只在 dev 定，test 冻结后只跑一次，`--calibration` 复用本次写出的 calibration.json）。

规则（tasks/e7_plan.md §3–4 原文，`vcd.analysis.provenance`）：a_t = run 与 teacher t 的 symmetrized 多数行动一致率（`e1_metrics.teacher_agreement`，p_sym = 0.5 的 cell 不计）；基座已知 s_t = a_t − a_t(S_0)，基座未知 s_t = a_t − mean_t' a_t'；t* = argmax s_t，margin = s_t* − 第二大，margin > τ 判为 t*，否则不判定；τ = 使 dev 负例（K、K_n、R、S_0）被判为任一 teacher 的比例 ≤ 5% 的最小值（负例 < 20 时 τ = 0），每个检测器配置（变体 × readout × 探针子集 × 预算）各一个，test 原样复用；召回 Wilson 95% CI（不判定计错），macro 召回，开集 FPR，一对多 AUROC（以 s_t 为分数，负类含 none），随机参照 (1/3)(1 − 不判定率)，teacher 标签在该网格可判定 run 间置换 10,000 次的 p（seed 为近复本，p 只作描述）。主判定：E2c-C 的 15 个 O 学生，基座已知，字母概率，全部探针：召回 Wilson 下界 > 1/3 的 teacher ≥ 2/3 → 溯源可行（有条件），1/3 → 部分，0/3 → 不可行，并报开集 FPR 是否 ≤ 10%。

## 候选集与真值（phase 2：候选 = 检测器比对的 teacher；真值 = run id 里的 teacher）

候选 3 个：gpt4o, claude46, deepseek_v4；真值 teacher：claude46, deepseek_v4, gpt4o；真 teacher 不在候选集的 run：0；家族：claude46:anthropic, deepseek_v4:deepseek, gpt4o:openai；calibration 键 `claude46,deepseek_v4,gpt4o`。主判定的 teacher 数 = 主组里有学生的候选（3）。

## 标定（calibration.json，本次写出）

负例 16 个（E1, K）；基座参照 = prior（596 个有效 cell / 600）；teacher 分歧 cell 91 / 600；family 150；重复 200；seed 0。

| configuration | tau | n_neg | n_margins | n_attributed | fpr_at_tau | fallback | note |
|---|---|---|---|---|---|---|---|
| main|probability|all|base_known | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| main|probability|all|base_unknown | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| main|probability|disagreement|base_known | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| main|probability|disagreement|base_unknown | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| loso|probability|all|base_known | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| loso|probability|all|base_unknown | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| logo|probability|all|base_known | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| logo|probability|all|base_unknown | 0.000 | 16 | 16 | 15 | 0.938 | True | only 16 negatives (< 20): tau = 0 fallback |
| main|sampled_n1|all|base_known | 0.035 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|sampled_n1|all|base_unknown | 0.019 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|sampled_n3|all|base_known | 0.035 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|sampled_n3|all|base_unknown | 0.019 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|sampled_n10|all|base_known | 0.036 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|sampled_n10|all|base_unknown | 0.019 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|probability|budget30|base_known | 0.092 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|probability|budget30|base_unknown | 0.067 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|probability|budget60|base_known | 0.062 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|probability|budget60|base_unknown | 0.042 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|probability|budget100|base_known | 0.055 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |
| main|probability|budget100|base_unknown | 0.033 | 3200 | 3200 | 160 | 0.050 | False | 3200 negatives, at most 160 may be attributed |

## 主表：基座已知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | gpt4o | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.416 | nan | nan | nan | 0.938 | 16 | 0.000 |
| E2c_C | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.672 | nan | nan | nan | 0.938 | 16 | 0.000 |
| E2c_C | O | deepseek_v4 | 5 | 2 | 0.400 | [0.118, 0.769] | 0.000 | 0.112 | nan | nan | nan | 0.938 | 16 | 0.000 |
| E2c_C | O | macro | 15 | 12 | 0.800 | [nan, nan] | 0.000 | nan | 0.800 | 0.333 | 2.0e-04 | 0.938 | 16 | 0.000 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.000 |
| K | O | none | 15 | 0 | 0.000 | [nan, nan] | 0.000 | nan | nan | nan | nan | 1.000 | 15 | 0.000 |

## 主表：基座未知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | gpt4o | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.888 | nan | nan | nan | 0.938 | 16 | 0.000 |
| E2c_C | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 | 16 | 0.000 |
| E2c_C | O | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 | 16 | 0.000 |
| E2c_C | O | macro | 15 | 15 | 1.000 | [nan, nan] | 0.000 | nan | 1.000 | 0.333 | 1.0e-04 | 0.938 | 16 | 0.000 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.000 |
| K | O | none | 15 | 0 | 0.000 | [nan, nan] | 0.000 | nan | nan | nan | nan | 1.000 | 15 | 0.000 |

## 真 teacher 不在候选集（e7_absent.csv；概率 readout，全部 cell，calibrated τ；这些 run 不进召回 / AUROC，也不进任何标定）

（无：候选集包含全部真值 teacher。）

## 分歧探针（三家多数行动不全同的 cell，91 / 600；τ = 该配置自标定（calibrated）；全 cell 的 τ 作灵敏度（fixed_all_cells，只列 macro 行））

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.000 | E2c_C | O | gpt4o | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.752 | nan | nan | nan | 0.938 |
| base_known | 0.000 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 |
| base_known | 0.000 | E2c_C | O | deepseek_v4 | 5 | 0.400 | [0.118, 0.769] | 0.400 | 1.000 | nan | nan | nan | 0.938 |
| base_known | 0.000 | E2c_C | O | macro | 15 | 0.800 | [nan, nan] | 0.133 | nan | 0.800 | 0.289 | 1.0e-04 | 0.938 |
| base_unknown | 0.000 | E2c_C | O | gpt4o | 5 | 0.800 | [0.376, 0.964] | 0.200 | 0.756 | nan | nan | nan | 0.938 |
| base_unknown | 0.000 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 |
| base_unknown | 0.000 | E2c_C | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 |
| base_unknown | 0.000 | E2c_C | O | macro | 15 | 0.933 | [nan, nan] | 0.067 | nan | 0.933 | 0.311 | 1.0e-04 | 0.938 |

| detector | tau_policy | tau | grid | version | n | macro_recall | unattributed_rate | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|
| base_known | fixed_all_cells | 0.000 | E2c_C | O | 15 | 0.800 | 0.133 | 0.289 | 1.0e-04 | 0.938 |
| base_unknown | fixed_all_cells | 0.000 | E2c_C | O | 15 | 0.933 | 0.067 | 0.311 | 1.0e-04 | 0.938 |

## 采样 readout：n = 1 / 3 / 10 个答案取多数（每 cell 两序各抽；均值 [2.5, 97.5] 分位，e7_sampled.csv）

macro 召回（行 = 检测器 × 网格，列 = n）：

| detector | grid | version | 1 | 3 | 10 |
|---|---|---|---|---|---|
| base_known | E2c_C | O | 0.323 [0.267, 0.333] | 0.328 [0.267, 0.333] | 0.330 [0.267, 0.333] |
| base_unknown | E2c_C | O | 0.890 [0.733, 1.000] | 0.882 [0.800, 1.000] | 0.867 [0.798, 1.000] |

E2c_C O 学生的每 teacher 召回与 AUROC：

| detector | teacher | 1 | 3 | 10 |
|---|---|---|---|---|
| base_known | gpt4o | 0.964 [0.800, 1.000] / AUROC 0.603 | 0.983 [0.800, 1.000] / AUROC 0.583 | 0.990 [0.800, 1.000] / AUROC 0.591 |
| base_known | claude46 | 0.004 [0.000, 0.000] / AUROC 0.720 | 0.000 [0.000, 0.000] / AUROC 0.717 | 0.000 [0.000, 0.000] / AUROC 0.729 |
| base_known | deepseek_v4 | 0.000 [0.000, 0.000] / AUROC 0.121 | 0.000 [0.000, 0.000] / AUROC 0.124 | 0.000 [0.000, 0.000] / AUROC 0.122 |
| base_unknown | gpt4o | 0.707 [0.400, 1.000] / AUROC 0.946 | 0.670 [0.400, 1.000] / AUROC 0.942 | 0.622 [0.400, 1.000] / AUROC 0.944 |
| base_unknown | claude46 | 0.976 [0.800, 1.000] / AUROC 1.000 | 0.986 [0.800, 1.000] / AUROC 1.000 | 0.980 [0.800, 1.000] / AUROC 1.000 |
| base_unknown | deepseek_v4 | 0.987 [0.800, 1.000] / AUROC 1.000 | 0.991 [0.800, 1.000] / AUROC 1.000 | 0.998 [1.000, 1.000] / AUROC 1.000 |

开集 FPR（各重复均值）与 τ：

| detector | 1 | 3 | 10 |
|---|---|---|---|
| base_known | FPR 0.050 [0.000, 0.188]; τ 0.035 | FPR 0.050 [0.000, 0.125]; τ 0.035 | FPR 0.050 [0.000, 0.125]; τ 0.036 |
| base_unknown | FPR 0.050 [0.000, 0.188]; τ 0.019 | FPR 0.050 [0.000, 0.125]; τ 0.019 | FPR 0.050 [0.000, 0.125]; τ 0.019 |

## 探针预算曲线：随机 k 个 family × 重复（基座参照取同一批 family；均值 [2.5, 97.5]，e7_probe_curve.csv）

macro 召回（行 = 检测器 × τ 策略 × 网格，列 = family 预算 k；calibrated = 该预算自标定的 τ_k，fixed_all_cells = 全 cell 的 τ）：

| detector | tau_policy | grid | version | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|---|
| base_known | calibrated | E2c_C | O | 0.031 [0.000, 0.333] | 0.053 [0.000, 0.333] | 0.050 [0.000, 0.333] | 0.800 [0.800, 0.800] |
| base_known | fixed_all_cells | E2c_C | O | 0.606 [0.332, 1.000] | 0.702 [0.333, 1.000] | 0.798 [0.465, 1.000] | 0.800 [0.800, 0.800] |
| base_unknown | calibrated | E2c_C | O | 0.116 [0.000, 0.533] | 0.214 [0.000, 0.600] | 0.335 [0.000, 0.667] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | E2c_C | O | 0.683 [0.333, 1.000] | 0.828 [0.467, 1.000] | 0.951 [0.667, 1.000] | 1.000 [1.000, 1.000] |

开集 FPR（各重复均值）与 τ：

| detector | tau_policy | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|
| base_known | calibrated | FPR 0.050 [0.000, 0.627]; τ 0.092 | FPR 0.050 [0.000, 0.438]; τ 0.062 | FPR 0.050 [0.000, 0.625]; τ 0.055 | FPR 0.938 [0.938, 0.938]; τ 0.000 |
| base_known | fixed_all_cells | FPR 0.934 [0.875, 0.938]; τ 0.000 | FPR 0.936 [0.938, 0.938]; τ 0.000 | FPR 0.937 [0.938, 0.938]; τ 0.000 | FPR 0.938 [0.938, 0.938]; τ 0.000 |
| base_unknown | calibrated | FPR 0.050 [0.000, 0.383]; τ 0.067 | FPR 0.050 [0.000, 0.500]; τ 0.042 | FPR 0.050 [0.000, 0.500]; τ 0.033 | FPR 0.938 [0.938, 0.938]; τ 0.000 |
| base_unknown | fixed_all_cells | FPR 0.932 [0.873, 0.938]; τ 0.000 | FPR 0.936 [0.938, 0.938]; τ 0.000 | FPR 0.937 [0.938, 0.938]; τ 0.000 | FPR 0.938 [0.938, 0.938]; τ 0.000 |

E2c_C O 学生的每 teacher 召回：

| detector | tau_policy | teacher | 30 | 60 | 100 | 150 |
|---|---|---|---|---|---|---|
| base_known | calibrated | gpt4o | 0.083 [0.000, 1.000] | 0.140 [0.000, 1.000] | 0.150 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_known | calibrated | claude46 | 0.004 [0.000, 0.000] | 0.010 [0.000, 0.200] | 0.000 [0.000, 0.000] | 1.000 [1.000, 1.000] |
| base_known | calibrated | deepseek_v4 | 0.006 [0.000, 0.000] | 0.010 [0.000, 0.200] | 0.000 [0.000, 0.000] | 0.400 [0.400, 0.400] |
| base_known | fixed_all_cells | gpt4o | 0.680 [0.000, 1.000] | 0.787 [0.000, 1.000] | 0.953 [0.200, 1.000] | 1.000 [1.000, 1.000] |
| base_known | fixed_all_cells | claude46 | 0.717 [0.000, 1.000] | 0.880 [0.195, 1.000] | 0.970 [0.600, 1.000] | 1.000 [1.000, 1.000] |
| base_known | fixed_all_cells | deepseek_v4 | 0.420 [0.000, 1.000] | 0.438 [0.000, 1.000] | 0.471 [0.000, 1.000] | 0.400 [0.400, 0.400] |
| base_unknown | calibrated | gpt4o | 0.035 [0.000, 0.600] | 0.054 [0.000, 0.600] | 0.091 [0.000, 0.800] | 1.000 [1.000, 1.000] |
| base_unknown | calibrated | claude46 | 0.222 [0.000, 1.000] | 0.402 [0.000, 1.000] | 0.622 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | calibrated | deepseek_v4 | 0.090 [0.000, 1.000] | 0.186 [0.000, 1.000] | 0.291 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | gpt4o | 0.545 [0.000, 1.000] | 0.690 [0.000, 1.000] | 0.892 [0.195, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | claude46 | 0.795 [0.000, 1.000] | 0.920 [0.000, 1.000] | 0.985 [0.995, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | deepseek_v4 | 0.708 [0.000, 1.000] | 0.874 [0.000, 1.000] | 0.976 [0.600, 1.000] | 1.000 [1.000, 1.000] |

## leave-one-style-out：τ 只用 O / R / B 的负例标定（与主 τ 相同），认 E3 / E3c 的 F / C 学生（e7_loso.csv）

(empty)

## leave-one-grid-out：τ 在网格 E1, K, K_n 上标定（E1 的学生一并视为应拒判的总体），用到其余网格（e7_logo.csv）

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.000 | E2c_C | O | gpt4o | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.416 | nan | nan | nan | 0.938 |
| base_known | 0.000 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.672 | nan | nan | nan | 0.938 |
| base_known | 0.000 | E2c_C | O | deepseek_v4 | 5 | 0.400 | [0.118, 0.769] | 0.000 | 0.112 | nan | nan | nan | 0.938 |
| base_known | 0.000 | E2c_C | O | macro | 15 | 0.800 | [nan, nan] | 0.000 | nan | 0.800 | 0.333 | 5.0e-04 | 0.938 |
| base_unknown | 0.000 | E2c_C | O | gpt4o | 5 | 1.000 | [0.566, 1.000] | 0.000 | 0.888 | nan | nan | nan | 0.938 |
| base_unknown | 0.000 | E2c_C | O | claude46 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 |
| base_unknown | 0.000 | E2c_C | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.938 |
| base_unknown | 0.000 | E2c_C | O | macro | 15 | 1.000 | [nan, nan] | 0.000 | nan | 1.000 | 0.333 | 1.0e-04 | 0.938 |

## 描述：负例按类型的误判率（K / K_n / R / S_0）；归档 run；T0

| table | detector | grid | version | n | n_neg_attributed | fpr | tau |
|---|---|---|---|---|---|---|---|
| main | base_known | E1 | B | 1 | 0 | 0.000 | 0.000 |
| main | base_known | K | O | 15 | 15 | 1.000 | 0.000 |
| main | base_unknown | E1 | B | 1 | 0 | 0.000 | 0.000 |
| main | base_unknown | K | O | 15 | 15 | 1.000 | 0.000 |

T0（训练未见的无框架变体，不进分数）：各网格 run 均值的 a_t；对照 seen variants 的 a_t：

| grid | version | a_T0__gpt4o | a_T0__claude46 | a_T0__deepseek_v4 | a__gpt4o | a__claude46 | a__deepseek_v4 |
|---|---|---|---|---|---|---|---|
| E2c_C | O | 0.810 | 0.776 | 0.796 | 0.785 | 0.783 | 0.777 |
| K | O | 0.852 | 0.841 | 0.843 | 0.844 | 0.835 | 0.819 |
| E1 | B | nan | nan | nan | nan | nan | nan |

## 每 run（e7_runs.csv 节选：grid、真值、a_t、两种分数的判定）

| run_id | grid | version | truth | n_cells_valid | a__gpt4o | a__claude46 | a__deepseek_v4 | decision_known | margin_known | decision_unknown | margin_unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | E1 | B | none | 0 | nan | nan | nan | unattributed | nan | unattributed | nan |
| smollm3-3b-e2c.claude46_O_s1 | E2c_C | O | claude46 | 596 | 0.807 | 0.842 | 0.768 | claude46 | 0.019 | claude46 | 0.035 |
| smollm3-3b-e2c.claude46_O_s2 | E2c_C | O | claude46 | 596 | 0.803 | 0.837 | 0.773 | claude46 | 0.017 | claude46 | 0.033 |
| smollm3-3b-e2c.claude46_O_s3 | E2c_C | O | claude46 | 596 | 0.787 | 0.824 | 0.760 | claude46 | 0.021 | claude46 | 0.037 |
| smollm3-3b-e2c.claude46_O_s4 | E2c_C | O | claude46 | 596 | 0.807 | 0.842 | 0.773 | claude46 | 0.019 | claude46 | 0.035 |
| smollm3-3b-e2c.claude46_O_s5 | E2c_C | O | claude46 | 596 | 0.789 | 0.828 | 0.760 | claude46 | 0.022 | claude46 | 0.039 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | E2c_C | O | deepseek_v4 | 596 | 0.737 | 0.718 | 0.761 | gpt4o | 0.003 | deepseek_v4 | 0.024 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | E2c_C | O | deepseek_v4 | 596 | 0.740 | 0.723 | 0.765 | gpt4o | 0.003 | deepseek_v4 | 0.024 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | E2c_C | O | deepseek_v4 | 596 | 0.739 | 0.721 | 0.771 | deepseek_v4 | 0.005 | deepseek_v4 | 0.033 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | E2c_C | O | deepseek_v4 | 596 | 0.732 | 0.723 | 0.761 | deepseek_v4 | 0.002 | deepseek_v4 | 0.030 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | E2c_C | O | deepseek_v4 | 596 | 0.753 | 0.734 | 0.775 | gpt4o | 0.005 | deepseek_v4 | 0.022 |
| smollm3-3b-e2c.gpt4o_O_s1 | E2c_C | O | gpt4o | 596 | 0.822 | 0.792 | 0.802 | gpt4o | 0.046 | gpt4o | 0.021 |
| smollm3-3b-e2c.gpt4o_O_s2 | E2c_C | O | gpt4o | 596 | 0.815 | 0.783 | 0.798 | gpt4o | 0.045 | gpt4o | 0.017 |
| smollm3-3b-e2c.gpt4o_O_s3 | E2c_C | O | gpt4o | 596 | 0.814 | 0.798 | 0.800 | gpt4o | 0.032 | gpt4o | 0.014 |
| smollm3-3b-e2c.gpt4o_O_s4 | E2c_C | O | gpt4o | 596 | 0.810 | 0.783 | 0.793 | gpt4o | 0.043 | gpt4o | 0.017 |
| smollm3-3b-e2c.gpt4o_O_s5 | E2c_C | O | gpt4o | 596 | 0.828 | 0.796 | 0.800 | gpt4o | 0.048 | gpt4o | 0.028 |
| smollm3-3b-e2ck.claude46_O_s1 | K | O | none | 596 | 0.843 | 0.828 | 0.817 | gpt4o | 0.032 | gpt4o | 0.015 |
| smollm3-3b-e2ck.claude46_O_s2 | K | O | none | 596 | 0.854 | 0.853 | 0.839 | gpt4o | 0.017 | gpt4o | 0.001 |
| smollm3-3b-e2ck.claude46_O_s3 | K | O | none | 596 | 0.829 | 0.815 | 0.813 | gpt4o | 0.030 | gpt4o | 0.014 |
| smollm3-3b-e2ck.claude46_O_s4 | K | O | none | 596 | 0.838 | 0.812 | 0.813 | gpt4o | 0.042 | gpt4o | 0.025 |
| smollm3-3b-e2ck.claude46_O_s5 | K | O | none | 596 | 0.848 | 0.847 | 0.820 | gpt4o | 0.017 | gpt4o | 0.001 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | K | O | none | 596 | 0.848 | 0.838 | 0.827 | gpt4o | 0.026 | gpt4o | 0.010 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | K | O | none | 596 | 0.857 | 0.844 | 0.825 | gpt4o | 0.030 | gpt4o | 0.013 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | K | O | none | 596 | 0.848 | 0.835 | 0.820 | gpt4o | 0.030 | gpt4o | 0.014 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | K | O | none | 596 | 0.821 | 0.812 | 0.795 | gpt4o | 0.025 | gpt4o | 0.009 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | K | O | none | 596 | 0.855 | 0.844 | 0.825 | gpt4o | 0.028 | gpt4o | 0.012 |
| smollm3-3b-e2ck.gpt4o_O_s1 | K | O | none | 596 | 0.845 | 0.835 | 0.815 | gpt4o | 0.026 | gpt4o | 0.010 |
| smollm3-3b-e2ck.gpt4o_O_s2 | K | O | none | 596 | 0.841 | 0.835 | 0.820 | gpt4o | 0.023 | gpt4o | 0.007 |
| smollm3-3b-e2ck.gpt4o_O_s3 | K | O | none | 596 | 0.833 | 0.840 | 0.813 | gpt4o | 0.009 | claude46 | 0.007 |
| smollm3-3b-e2ck.gpt4o_O_s4 | K | O | none | 596 | 0.850 | 0.837 | 0.824 | gpt4o | 0.030 | gpt4o | 0.014 |
| smollm3-3b-e2ck.gpt4o_O_s5 | K | O | none | 596 | 0.848 | 0.854 | 0.822 | gpt4o | 0.010 | claude46 | 0.006 |

## 输入

| namespace | grid | role | version | n_runs | truths |
|---|---|---|---|---|---|
| smollm3-3b-e2c | E2c_C | core | O | 15 | claude46,deepseek_v4,gpt4o |
| smollm3-3b-e2ck | K | core | O | 15 | none |
| smollm3-3b | E1 | core | B | 1 | none |

说明：

- version-B copies skipped (S_0 is read once from --base-run): smollm3-3b-e2c/base_B_s0, smollm3-3b-e2ck/base_B_s0

## 预注册之外的实现决定（披露）

- 基座已知的参照 a_t(S_0) 默认用 S_0 的**未门控**两字母概率（`sym_table(mass_gate=False)`，与 E2 的协变量 r_0 同一对象）：门控 readout 下未训练基座只有约 1/6 的 cell 有答案；S_0 作为**被测**负例时仍用门控 readout。`--base-reference gated` 可切换。
- τ 按检测器配置各标一个（变体 × readout × 探针子集 × 预算），全部写入 calibration.json 并在 test 复用；分歧探针与预算曲线同时报自标定 τ 与全 cell τ（tau_policy）。
- 采样 readout 只作用于被测模型；teacher 参照与基座参照保持概率 readout。τ 在 200 次重复的负例 margin 合并后标定。
- leave-one-grid-out 的标定总体 = E1 网格的全部 run（15 个 O 学生一并视为应拒判）+ K / K_n 负例；评估其余网格。
- 置换 p 以 run 为单位（同 teacher 的 seed 为近复本，只作描述）；采样与预算曲线各重复内用 --n-perm-rep 次置换后取均值。
- 不足两个有限分数的 run 记为不判定（margin nan）；AUROC 的负类 = 该网格其余 run + 全部 none 负例。
- phase 2：候选集（--candidates / --drop-candidate）与真值分离；真 teacher 不在候选集的 run 照常打分，但不进召回 / AUROC 组，也不进标定（负例仍是 K / K_n / R / S_0），单独报在 e7_absent.csv；τ 按候选集在 dev 重新标定（规则不变），calibration.json 按候选集（排序后的候选名）分节保存，test 没有对应节则拒绝运行；主判定的 teacher 数 = 主组里有学生的候选。
