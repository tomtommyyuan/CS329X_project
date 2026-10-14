# E7 黑盒溯源（test，variants T1, T3, T5, T6；E7 detector, tau rule, metrics and verdict pre-registered in tasks/e7_plan.md §3-§4 before any provenance result; frozen at commit 4ae6ccb；auto-generated）

**主判定（E2c-C 的 O 学生，基座已知，字母概率 readout，全部探针）：不可行**（0/3 个 teacher 的召回 Wilson 下界 > 1/3：无；开集 FPR 0.000（≤ 10%）；τ = 0.036）。

**test：τ 全部来自 dev 的 calibration.json，本次没有任何标定**。

规则（tasks/e7_plan.md §3–4 原文，`vcd.analysis.provenance`）：a_t = run 与 teacher t 的 symmetrized 多数行动一致率（`e1_metrics.teacher_agreement`，p_sym = 0.5 的 cell 不计）；基座已知 s_t = a_t − a_t(S_0)，基座未知 s_t = a_t − mean_t' a_t'；t* = argmax s_t，margin = s_t* − 第二大，margin > τ 判为 t*，否则不判定；τ = 使 dev 负例（K、K_n、R、S_0）被判为任一 teacher 的比例 ≤ 5% 的最小值（负例 < 20 时 τ = 0），每个检测器配置（变体 × readout × 探针子集 × 预算）各一个，test 原样复用；召回 Wilson 95% CI（不判定计错），macro 召回，开集 FPR，一对多 AUROC（以 s_t 为分数，负类含 none），随机参照 (1/3)(1 − 不判定率)，teacher 标签在该网格可判定 run 间置换 10,000 次的 p（seed 为近复本，p 只作描述）。主判定：E2c-C 的 15 个 O 学生，基座已知，字母概率，全部探针：召回 Wilson 下界 > 1/3 的 teacher ≥ 2/3 → 溯源可行（有条件），1/3 → 部分，0/3 → 不可行，并报开集 FPR 是否 ≤ 10%。

## 候选集与真值（phase 2：候选 = 检测器比对的 teacher；真值 = run id 里的 teacher）

候选 3 个：gpt4o, claude46, deepseek_v4；真值 teacher：claude46, deepseek_v4, gpt4o；真 teacher 不在候选集的 run：0；家族：claude46:anthropic, deepseek_v4:deepseek, gpt4o:openai；calibration 键 `claude46,deepseek_v4,gpt4o`。主判定的 teacher 数 = 主组里有学生的候选（3）。

## 标定（复用 dev 的 calibration.json）

负例 16 个（E1, K）；基座参照 = prior（1200 个有效 cell / 1200）；teacher 分歧 cell 127 / 1200；family 300；重复 200；seed 0。

(empty)

## 主表：基座已知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.252 | nan | nan | nan | 0.000 | 16 | 0.036 |
| E2c_C | O | claude46 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.696 | nan | nan | nan | 0.000 | 16 | 0.036 |
| E2c_C | O | deepseek_v4 | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.000 | nan | nan | nan | 0.000 | 16 | 0.036 |
| E2c_C | O | macro | 15 | 0 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.000 | 16 | 0.036 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.036 |
| K | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.036 |

## 主表：基座未知，字母概率 readout，全部 cell（e7_metrics.csv，table = main）

| grid | version | teacher | n | n_correct | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr | n_neg | tau |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| E2c_C | O | gpt4o | 5 | 0 | 0.000 | [0.000, 0.434] | 1.000 | 0.944 | nan | nan | nan | 0.000 | 16 | 0.017 |
| E2c_C | O | claude46 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 | 16 | 0.017 |
| E2c_C | O | deepseek_v4 | 5 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.000 | 16 | 0.017 |
| E2c_C | O | macro | 15 | 10 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.000 | 16 | 0.017 |
| E1 | B | none | 1 | 1 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 1 | 0.017 |
| K | O | none | 15 | 15 | 1.000 | [nan, nan] | 1.000 | nan | nan | nan | nan | 0.000 | 15 | 0.017 |

## 真 teacher 不在候选集（e7_absent.csv；概率 readout，全部 cell，calibrated τ；这些 run 不进召回 / AUROC，也不进任何标定）

（无：候选集包含全部真值 teacher。）

## 分歧探针（三家多数行动不全同的 cell，127 / 1200；τ = 该配置自标定（calibrated）；全 cell 的 τ 作灵敏度（fixed_all_cells，只列 macro 行））

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.220 | E2c_C | O | gpt4o | 5 | 0.200 | [0.036, 0.624] | 0.800 | 0.924 | nan | nan | nan | 0.125 |
| base_known | 0.220 | E2c_C | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.125 |
| base_known | 0.220 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 1.000 | nan | nan | nan | 0.125 |
| base_known | 0.220 | E2c_C | O | macro | 15 | 0.067 | [nan, nan] | 0.933 | nan | 0.067 | 0.022 | 0.334 | 0.125 |
| base_unknown | 0.088 | E2c_C | O | gpt4o | 5 | 0.200 | [0.036, 0.624] | 0.800 | 0.956 | nan | nan | nan | 0.125 |
| base_unknown | 0.088 | E2c_C | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 1.000 | nan | nan | nan | 0.125 |
| base_unknown | 0.088 | E2c_C | O | deepseek_v4 | 5 | 1.000 | [0.566, 1.000] | 0.000 | 1.000 | nan | nan | nan | 0.125 |
| base_unknown | 0.088 | E2c_C | O | macro | 15 | 0.667 | [nan, nan] | 0.333 | nan | 0.667 | 0.222 | 1.0e-04 | 0.125 |

| detector | tau_policy | tau | grid | version | n | macro_recall | unattributed_rate | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|
| base_known | fixed_all_cells | 0.036 | E2c_C | O | 15 | 1.000 | 0.000 | 0.333 | 1.0e-04 | 0.938 |
| base_unknown | fixed_all_cells | 0.017 | E2c_C | O | 15 | 1.000 | 0.000 | 0.333 | 1.0e-04 | 0.688 |

## 采样 readout：n = 1 / 3 / 10 个答案取多数（每 cell 两序各抽；均值 [2.5, 97.5] 分位，e7_sampled.csv）

macro 召回（行 = 检测器 × 网格，列 = n）：

| detector | grid | version | 1 | 3 | 10 |
|---|---|---|---|---|---|
| base_known | E2c_C | O | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] | 0.000 [0.000, 0.000] |
| base_unknown | E2c_C | O | 0.634 [0.533, 0.667] | 0.654 [0.600, 0.667] | 0.647 [0.598, 0.667] |

E2c_C O 学生的每 teacher 召回与 AUROC：

| detector | teacher | 1 | 3 | 10 |
|---|---|---|---|---|
| base_known | gpt4o | 0.000 [0.000, 0.000] / AUROC 0.226 | 0.000 [0.000, 0.000] / AUROC 0.220 | 0.000 [0.000, 0.000] / AUROC 0.217 |
| base_known | claude46 | 0.000 [0.000, 0.000] / AUROC 0.841 | 0.000 [0.000, 0.000] / AUROC 0.850 | 0.000 [0.000, 0.000] / AUROC 0.901 |
| base_known | deepseek_v4 | 0.000 [0.000, 0.000] / AUROC 0.000 | 0.000 [0.000, 0.000] / AUROC 0.000 | 0.000 [0.000, 0.000] / AUROC 0.000 |
| base_unknown | gpt4o | 0.000 [0.000, 0.000] / AUROC 0.953 | 0.000 [0.000, 0.000] / AUROC 0.943 | 0.000 [0.000, 0.000] / AUROC 0.941 |
| base_unknown | claude46 | 0.963 [0.800, 1.000] / AUROC 1.000 | 0.988 [0.800, 1.000] / AUROC 1.000 | 0.988 [0.800, 1.000] / AUROC 1.000 |
| base_unknown | deepseek_v4 | 0.938 [0.795, 1.000] / AUROC 1.000 | 0.973 [0.800, 1.000] / AUROC 1.000 | 0.954 [0.800, 1.000] / AUROC 1.000 |

开集 FPR（各重复均值）与 τ：

| detector | 1 | 3 | 10 |
|---|---|---|---|
| base_known | FPR 0.000 [0.000, 0.000]; τ 0.039 | FPR 0.000 [0.000, 0.000]; τ 0.038 | FPR 0.000 [0.000, 0.000]; τ 0.038 |
| base_unknown | FPR 0.000 [0.000, 0.000]; τ 0.022 | FPR 0.000 [0.000, 0.000]; τ 0.023 | FPR 0.000 [0.000, 0.000]; τ 0.025 |

## 探针预算曲线：随机 k 个 family × 重复（基座参照取同一批 family；均值 [2.5, 97.5]，e7_probe_curve.csv）

macro 召回（行 = 检测器 × τ 策略 × 网格，列 = family 预算 k；calibrated = 该预算自标定的 τ_k，fixed_all_cells = 全 cell 的 τ）：

| detector | tau_policy | grid | version | 30 | 60 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|---|---|
| base_known | calibrated | E2c_C | O | 0.028 [0.000, 0.333] | 0.029 [0.000, 0.333] | 0.049 [0.000, 0.333] | 0.082 [0.000, 0.333] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | E2c_C | O | 0.201 [0.000, 0.600] | 0.168 [0.000, 0.467] | 0.131 [0.000, 0.335] | 0.082 [0.000, 0.333] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | E2c_C | O | 0.055 [0.000, 0.333] | 0.120 [0.000, 0.402] | 0.243 [0.000, 0.600] | 0.557 [0.200, 0.800] | 0.667 [0.667, 0.667] |
| base_unknown | fixed_all_cells | E2c_C | O | 0.389 [0.000, 0.735] | 0.465 [0.132, 0.800] | 0.525 [0.133, 0.802] | 0.557 [0.200, 0.800] | 0.667 [0.667, 0.667] |

开集 FPR（各重复均值）与 τ：

| detector | tau_policy | 30 | 60 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|
| base_known | calibrated | FPR 0.030 [0.000, 0.377]; τ 0.086 | FPR 0.027 [0.000, 0.252]; τ 0.066 | FPR 0.046 [0.000, 0.439]; τ 0.046 | FPR 0.037 [0.000, 0.500]; τ 0.036 | FPR 0.000 [0.000, 0.000]; τ 0.036 |
| base_known | fixed_all_cells | FPR 0.285 [0.000, 0.877]; τ 0.036 | FPR 0.200 [0.000, 0.877]; τ 0.036 | FPR 0.101 [0.000, 0.692]; τ 0.036 | FPR 0.037 [0.000, 0.500]; τ 0.036 | FPR 0.000 [0.000, 0.000]; τ 0.036 |
| base_unknown | calibrated | FPR 0.019 [0.000, 0.252]; τ 0.069 | FPR 0.029 [0.000, 0.189]; τ 0.045 | FPR 0.028 [0.000, 0.189]; τ 0.032 | FPR 0.145 [0.000, 0.625]; τ 0.017 | FPR 0.000 [0.000, 0.000]; τ 0.017 |
| base_unknown | fixed_all_cells | FPR 0.469 [0.000, 0.938]; τ 0.017 | FPR 0.380 [0.000, 0.938]; τ 0.017 | FPR 0.197 [0.000, 0.689]; τ 0.017 | FPR 0.145 [0.000, 0.625]; τ 0.017 | FPR 0.000 [0.000, 0.000]; τ 0.017 |

E2c_C O 学生的每 teacher 召回：

| detector | tau_policy | teacher | 30 | 60 | 100 | 150 | 300 |
|---|---|---|---|---|---|---|---|
| base_known | calibrated | gpt4o | 0.025 [0.000, 0.405] | 0.032 [0.000, 0.605] | 0.048 [0.000, 0.600] | 0.070 [0.000, 0.800] | 0.000 [0.000, 0.000] |
| base_known | calibrated | claude46 | 0.057 [0.000, 1.000] | 0.055 [0.000, 0.805] | 0.094 [0.000, 0.800] | 0.160 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| base_known | calibrated | deepseek_v4 | 0.003 [0.000, 0.000] | 0.001 [0.000, 0.000] | 0.004 [0.000, 0.000] | 0.016 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | gpt4o | 0.156 [0.000, 1.000] | 0.167 [0.000, 1.000] | 0.127 [0.000, 1.000] | 0.070 [0.000, 0.800] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | claude46 | 0.300 [0.000, 1.000] | 0.248 [0.000, 1.000] | 0.215 [0.000, 1.000] | 0.160 [0.000, 1.000] | 0.000 [0.000, 0.000] |
| base_known | fixed_all_cells | deepseek_v4 | 0.148 [0.000, 1.000] | 0.088 [0.000, 0.800] | 0.052 [0.000, 0.600] | 0.016 [0.000, 0.200] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | gpt4o | 0.015 [0.000, 0.000] | 0.020 [0.000, 0.200] | 0.019 [0.000, 0.200] | 0.115 [0.000, 0.805] | 0.000 [0.000, 0.000] |
| base_unknown | calibrated | claude46 | 0.073 [0.000, 0.805] | 0.213 [0.000, 1.000] | 0.416 [0.000, 1.000] | 0.800 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | calibrated | deepseek_v4 | 0.076 [0.000, 1.000] | 0.126 [0.000, 1.000] | 0.295 [0.000, 1.000] | 0.756 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | gpt4o | 0.195 [0.000, 1.000] | 0.183 [0.000, 1.000] | 0.173 [0.000, 1.000] | 0.115 [0.000, 0.805] | 0.000 [0.000, 0.000] |
| base_unknown | fixed_all_cells | claude46 | 0.486 [0.000, 1.000] | 0.624 [0.000, 1.000] | 0.708 [0.000, 1.000] | 0.800 [0.000, 1.000] | 1.000 [1.000, 1.000] |
| base_unknown | fixed_all_cells | deepseek_v4 | 0.486 [0.000, 1.000] | 0.588 [0.000, 1.000] | 0.693 [0.000, 1.000] | 0.756 [0.000, 1.000] | 1.000 [1.000, 1.000] |

## leave-one-style-out：τ 只用 O / R / B 的负例标定（与主 τ 相同），认 E3 / E3c 的 F / C 学生（e7_loso.csv）

(empty)

## leave-one-grid-out：τ 在网格 E1, K, K_n 上标定（E1 的学生一并视为应拒判的总体），用到其余网格（e7_logo.csv）

| detector | tau | grid | version | teacher | n | recall | CI | unattributed_rate | auroc | macro_recall | chance | perm_p | fpr |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base_known | 0.040 | E2c_C | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.252 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E2c_C | O | claude46 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.696 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E2c_C | O | deepseek_v4 | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.000 | nan | nan | nan | 0.000 |
| base_known | 0.040 | E2c_C | O | macro | 15 | 0.000 | [nan, nan] | 1.000 | nan | 0.000 | 0.000 | 1.000 | 0.000 |
| base_unknown | 0.023 | E2c_C | O | gpt4o | 5 | 0.000 | [0.000, 0.434] | 1.000 | 0.944 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E2c_C | O | claude46 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E2c_C | O | deepseek_v4 | 5 | 0.800 | [0.376, 0.964] | 0.200 | 1.000 | nan | nan | nan | 0.000 |
| base_unknown | 0.023 | E2c_C | O | macro | 15 | 0.533 | [nan, nan] | 0.467 | nan | 0.533 | 0.178 | 1.0e-04 | 0.000 |

## 描述：负例按类型的误判率（K / K_n / R / S_0）；归档 run；T0

| table | detector | grid | version | n | n_neg_attributed | fpr | tau |
|---|---|---|---|---|---|---|---|
| main | base_known | E1 | B | 1 | 0 | 0.000 | 0.036 |
| main | base_known | K | O | 15 | 0 | 0.000 | 0.036 |
| main | base_unknown | E1 | B | 1 | 0 | 0.000 | 0.017 |
| main | base_unknown | K | O | 15 | 0 | 0.000 | 0.017 |

T0（训练未见的无框架变体，不进分数）：各网格 run 均值的 a_t；对照 seen variants 的 a_t：

| grid | version | a_T0__gpt4o | a_T0__claude46 | a_T0__deepseek_v4 | a__gpt4o | a__claude46 | a__deepseek_v4 |
|---|---|---|---|---|---|---|---|
| E2c_C | O | 0.818 | 0.808 | 0.821 | 0.792 | 0.795 | 0.798 |
| K | O | 0.853 | 0.837 | 0.854 | 0.856 | 0.858 | 0.850 |
| E1 | B | nan | nan | nan | nan | nan | nan |

## 每 run（e7_runs.csv 节选：grid、真值、a_t、两种分数的判定）

| run_id | grid | version | truth | n_cells_valid | a__gpt4o | a__claude46 | a__deepseek_v4 | decision_known | margin_known | decision_unknown | margin_unknown |
|---|---|---|---|---|---|---|---|---|---|---|---|
| smollm3-3b.base_B_s0 | E1 | B | none | 0 | nan | nan | nan | unattributed | nan | unattributed | nan |
| smollm3-3b-e2c.claude46_O_s1 | E2c_C | O | claude46 | 1200 | 0.816 | 0.847 | 0.816 | unattributed | 0.019 | claude46 | 0.031 |
| smollm3-3b-e2c.claude46_O_s2 | E2c_C | O | claude46 | 1200 | 0.817 | 0.849 | 0.807 | unattributed | 0.020 | claude46 | 0.032 |
| smollm3-3b-e2c.claude46_O_s3 | E2c_C | O | claude46 | 1200 | 0.837 | 0.869 | 0.829 | unattributed | 0.020 | claude46 | 0.032 |
| smollm3-3b-e2c.claude46_O_s4 | E2c_C | O | claude46 | 1200 | 0.825 | 0.855 | 0.833 | unattributed | 0.018 | claude46 | 0.022 |
| smollm3-3b-e2c.claude46_O_s5 | E2c_C | O | claude46 | 1200 | 0.835 | 0.875 | 0.838 | unattributed | 0.027 | claude46 | 0.037 |
| smollm3-3b-e2c.deepseek_v4_O_s1 | E2c_C | O | deepseek_v4 | 1199 | 0.729 | 0.719 | 0.761 | unattributed | 0.019 | deepseek_v4 | 0.032 |
| smollm3-3b-e2c.deepseek_v4_O_s2 | E2c_C | O | deepseek_v4 | 1200 | 0.727 | 0.723 | 0.757 | unattributed | 0.018 | deepseek_v4 | 0.030 |
| smollm3-3b-e2c.deepseek_v4_O_s3 | E2c_C | O | deepseek_v4 | 1200 | 0.734 | 0.719 | 0.753 | unattributed | 0.007 | deepseek_v4 | 0.019 |
| smollm3-3b-e2c.deepseek_v4_O_s4 | E2c_C | O | deepseek_v4 | 1200 | 0.731 | 0.727 | 0.758 | unattributed | 0.014 | deepseek_v4 | 0.027 |
| smollm3-3b-e2c.deepseek_v4_O_s5 | E2c_C | O | deepseek_v4 | 1200 | 0.745 | 0.734 | 0.770 | unattributed | 0.012 | deepseek_v4 | 0.025 |
| smollm3-3b-e2c.gpt4o_O_s1 | E2c_C | O | gpt4o | 1200 | 0.825 | 0.805 | 0.817 | unattributed | 0.021 | unattributed | 0.009 |
| smollm3-3b-e2c.gpt4o_O_s2 | E2c_C | O | gpt4o | 1200 | 0.818 | 0.804 | 0.803 | unattributed | 0.027 | unattributed | 0.014 |
| smollm3-3b-e2c.gpt4o_O_s3 | E2c_C | O | gpt4o | 1200 | 0.809 | 0.795 | 0.807 | unattributed | 0.014 | unattributed | 0.002 |
| smollm3-3b-e2c.gpt4o_O_s4 | E2c_C | O | gpt4o | 1200 | 0.819 | 0.801 | 0.814 | unattributed | 0.018 | unattributed | 0.005 |
| smollm3-3b-e2c.gpt4o_O_s5 | E2c_C | O | gpt4o | 1200 | 0.813 | 0.799 | 0.807 | unattributed | 0.019 | unattributed | 0.006 |
| smollm3-3b-e2ck.claude46_O_s1 | K | O | none | 1200 | 0.866 | 0.874 | 0.863 | unattributed | 0.004 | unattributed | 0.008 |
| smollm3-3b-e2ck.claude46_O_s2 | K | O | none | 1200 | 0.863 | 0.866 | 0.862 | unattributed | 0.010 | unattributed | 0.003 |
| smollm3-3b-e2ck.claude46_O_s3 | K | O | none | 1200 | 0.856 | 0.862 | 0.851 | unattributed | 0.007 | unattributed | 0.006 |
| smollm3-3b-e2ck.claude46_O_s4 | K | O | none | 1200 | 0.851 | 0.860 | 0.850 | unattributed | 0.003 | unattributed | 0.009 |
| smollm3-3b-e2ck.claude46_O_s5 | K | O | none | 1200 | 0.874 | 0.866 | 0.853 | unattributed | 0.021 | unattributed | 0.008 |
| smollm3-3b-e2ck.deepseek_v4_O_s1 | K | O | none | 1200 | 0.851 | 0.857 | 0.845 | unattributed | 0.007 | unattributed | 0.006 |
| smollm3-3b-e2ck.deepseek_v4_O_s2 | K | O | none | 1200 | 0.867 | 0.869 | 0.862 | unattributed | 0.011 | unattributed | 0.002 |
| smollm3-3b-e2ck.deepseek_v4_O_s3 | K | O | none | 1200 | 0.851 | 0.849 | 0.845 | unattributed | 0.015 | unattributed | 0.002 |
| smollm3-3b-e2ck.deepseek_v4_O_s4 | K | O | none | 1200 | 0.850 | 0.853 | 0.842 | unattributed | 0.010 | unattributed | 0.003 |
| smollm3-3b-e2ck.deepseek_v4_O_s5 | K | O | none | 1200 | 0.851 | 0.859 | 0.858 | unattributed | 0.005 | unattributed | 0.001 |
| smollm3-3b-e2ck.gpt4o_O_s1 | K | O | none | 1200 | 0.846 | 0.856 | 0.843 | unattributed | 0.003 | unattributed | 0.010 |
| smollm3-3b-e2ck.gpt4o_O_s2 | K | O | none | 1200 | 0.845 | 0.838 | 0.847 | unattributed | 0.011 | unattributed | 0.001 |
| smollm3-3b-e2ck.gpt4o_O_s3 | K | O | none | 1200 | 0.859 | 0.861 | 0.852 | unattributed | 0.010 | unattributed | 0.002 |
| smollm3-3b-e2ck.gpt4o_O_s4 | K | O | none | 1200 | 0.848 | 0.848 | 0.845 | unattributed | 0.012 | unattributed | 2.2e-04 |
| smollm3-3b-e2ck.gpt4o_O_s5 | K | O | none | 1200 | 0.859 | 0.851 | 0.840 | unattributed | 0.021 | unattributed | 0.008 |

## 输入

| namespace | grid | role | version | n_runs | truths |
|---|---|---|---|---|---|
| smollm3-3b-e2c | E2c_C | core | O | 15 | claude46,deepseek_v4,gpt4o |
| smollm3-3b-e2ck | K | core | O | 15 | none |
| smollm3-3b | E1 | core | B | 1 | none |

说明：

- version-B copies skipped (S_0 is read once from --base-run): smollm3-3b-e2c/base_B_s0, smollm3-3b-e2ck/base_B_s0
- probe budget 150 (base_known): no tau in the calibration file (on the calibration split this budget was the all-cells configuration); the all-cells tau 0.0356 is used
- probe budget 150 (base_unknown): no tau in the calibration file (on the calibration split this budget was the all-cells configuration); the all-cells tau 0.0174 is used

## 预注册之外的实现决定（披露）

- 基座已知的参照 a_t(S_0) 默认用 S_0 的**未门控**两字母概率（`sym_table(mass_gate=False)`，与 E2 的协变量 r_0 同一对象）：门控 readout 下未训练基座只有约 1/6 的 cell 有答案；S_0 作为**被测**负例时仍用门控 readout。`--base-reference gated` 可切换。
- τ 按检测器配置各标一个（变体 × readout × 探针子集 × 预算），全部写入 calibration.json 并在 test 复用；分歧探针与预算曲线同时报自标定 τ 与全 cell τ（tau_policy）。
- 采样 readout 只作用于被测模型；teacher 参照与基座参照保持概率 readout。τ 在 200 次重复的负例 margin 合并后标定。
- leave-one-grid-out 的标定总体 = E1 网格的全部 run（15 个 O 学生一并视为应拒判）+ K / K_n 负例；评估其余网格。
- 置换 p 以 run 为单位（同 teacher 的 seed 为近复本，只作描述）；采样与预算曲线各重复内用 --n-perm-rep 次置换后取均值。
- 不足两个有限分数的 run 记为不判定（margin nan）；AUROC 的负类 = 该网格其余 run + 全部 none 负例。
- phase 2：候选集（--candidates / --drop-candidate）与真值分离；真 teacher 不在候选集的 run 照常打分，但不进召回 / AUROC 组，也不进标定（负例仍是 K / K_n / R / S_0），单独报在 e7_absent.csv；τ 按候选集在 dev 重新标定（规则不变），calibration.json 按候选集（排序后的候选名）分节保存，test 没有对应节则拒绝运行；主判定的 teacher 数 = 主组里有学生的候选。
