# E7 词汇溯源：学生生成文本（phase 3；tasks/e7_plan.md §5；自动生成）

对象：6 个学生 run 的 14400 条生成（scripts/25，test 探针；有 rationale 的 14400 条进入分类）。分类器 = 与训练文本 baseline 相同的 hashed 字符 3–5-gram + 词 uni / bigram L2 多项 logistic 回归（C = 1.0，balanced，sklearn，每块 2^18 桶），训练集 = teacher 的 O 训练 rationale（10877 条：{'gpt4o': 4527, 'claude46': 4122, 'deepseek_v4': 2228}）；长度对照只用词数、句数、平均词长。run 级判定 = 该 run 生成的多数票（闭集：总会判一个 teacher，chance = 1/3；行为检测器是开集、可拒判）。

## 结论

run 级多数票 macro 准确率（全部有真值的 run）：n-gram 1.000 [1.000, 1.000]，长度对照 0.833 [0.602, 1.000]；生成级：n-gram 0.861 [0.856, 0.867]，长度对照 0.717 [0.711, 0.723]。

与行为检测器（基座未知）逐 run 对照（6 个有真值且在 e7_runs.csv 里的 run）：两者都对 4，只有词汇对 2，只有行为对 0，都错 0；行为不判定 2；词汇多数票 = 行为判定的 run 4。
与行为检测器（基座已知）逐 run 对照（6 个有真值且在 e7_runs.csv 里的 run）：两者都对 2，只有词汇对 4，只有行为对 0，都错 0；行为不判定 4；词汇多数票 = 行为判定的 run 2。

## 准确率（run 级 = 多数票 vs 真值，generation 级 = 每条生成；行 = 特征 × 层级 × 网格 × 版本）

| features | level | grid | version | gpt4o | claude46 | deepseek_v4 | macro | pooled | n |
|---|---|---|---|---|---|---|---|---|---|
| ngram | run | all | all | 1.000 [0.342, 1.000] | 1.000 [0.342, 1.000] | 1.000 [0.342, 1.000] | 1.000 [1.000, 1.000] | 1.000 [0.610, 1.000] | 6 |
| ngram | generation | all | all | 0.897 [0.888, 0.905] | 0.956 [0.950, 0.962] | 0.731 [0.718, 0.743] | 0.861 [0.856, 0.867] | 0.861 [0.856, 0.867] | 14400 |
| ngram | run | qwen3-4b-e2c-gen | C | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 1.000 [1.000, 1.000] | 1.000 [0.439, 1.000] | 3 |
| ngram | generation | qwen3-4b-e2c-gen | C | 0.827 [0.811, 0.842] | 0.954 [0.945, 0.962] | 0.588 [0.569, 0.608] | 0.790 [0.781, 0.799] | 0.790 [0.780, 0.799] | 7200 |
| ngram | run | qwen3-4b-e2c-gen | O | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 1.000 [1.000, 1.000] | 1.000 [0.439, 1.000] | 3 |
| ngram | generation | qwen3-4b-e2c-gen | O | 0.966 [0.958, 0.973] | 0.958 [0.950, 0.966] | 0.873 [0.859, 0.886] | 0.933 [0.927, 0.938] | 0.933 [0.927, 0.938] | 7200 |
| length | run | all | all | 1.000 [0.342, 1.000] | 1.000 [0.342, 1.000] | 0.500 [0.095, 0.905] | 0.833 [0.602, 1.000] | 0.833 [0.436, 0.970] | 6 |
| length | generation | all | all | 0.771 [0.759, 0.783] | 0.964 [0.958, 0.969] | 0.416 [0.402, 0.430] | 0.717 [0.711, 0.723] | 0.717 [0.710, 0.724] | 14400 |
| length | run | qwen3-4b-e2c-gen | C | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 0.000 [0.000, 0.793] | 0.667 [0.667, 0.667] | 0.667 [0.208, 0.939] | 3 |
| length | generation | qwen3-4b-e2c-gen | C | 0.764 [0.746, 0.780] | 0.978 [0.971, 0.983] | 0.330 [0.312, 0.349] | 0.691 [0.682, 0.699] | 0.691 [0.680, 0.701] | 7200 |
| length | run | qwen3-4b-e2c-gen | O | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 1.000 [0.207, 1.000] | 1.000 [1.000, 1.000] | 1.000 [0.439, 1.000] | 3 |
| length | generation | qwen3-4b-e2c-gen | O | 0.779 [0.762, 0.795] | 0.950 [0.940, 0.958] | 0.501 [0.481, 0.521] | 0.743 [0.734, 0.752] | 0.743 [0.733, 0.753] | 7200 |

## 每 run（students_runs.csv）

| run_id | grid | version | truth | n_gen | n_classified | letter_rate | share_gpt4o_ngram | share_claude46_ngram | share_deepseek_v4_ngram | majority_ngram | correct_ngram | majority_length | correct_length |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-gen.claude46_C_s1 | qwen3-4b-e2c-gen | C | claude46 | 2400 | 2400 | 1.000 | 0.023 | 0.954 | 0.023 | claude46 | yes | claude46 | yes |
| qwen3-4b-e2c-gen.deepseek_v4_C_s1 | qwen3-4b-e2c-gen | C | deepseek_v4 | 2400 | 2400 | 1.000 | 0.247 | 0.165 | 0.588 | deepseek_v4 | yes | gpt4o | no |
| qwen3-4b-e2c-gen.gpt4o_C_s1 | qwen3-4b-e2c-gen | C | gpt4o | 2400 | 2400 | 1.000 | 0.827 | 0.052 | 0.121 | gpt4o | yes | gpt4o | yes |
| qwen3-4b-e2c-gen.claude46_O_s1 | qwen3-4b-e2c-gen | O | claude46 | 2400 | 2400 | 1.000 | 0.034 | 0.958 | 0.008 | claude46 | yes | claude46 | yes |
| qwen3-4b-e2c-gen.deepseek_v4_O_s1 | qwen3-4b-e2c-gen | O | deepseek_v4 | 2400 | 2400 | 1.000 | 0.089 | 0.037 | 0.873 | deepseek_v4 | yes | deepseek_v4 | yes |
| qwen3-4b-e2c-gen.gpt4o_O_s1 | qwen3-4b-e2c-gen | O | gpt4o | 2400 | 2400 | 1.000 | 0.966 | 0.013 | 0.021 | gpt4o | yes | gpt4o | yes |

## 词汇 vs 行为（students_vs_behavioural.csv；行为判定来自 scripts/21 的 e7_runs.csv，`unattributed` = 行为检测器拒判）

| run_id | grid | version | truth | majority_ngram | share_own_ngram | decision_unknown | margin_unknown | decision_known | lexical_correct_ngram | behavioural_correct_unknown | agree_unknown_ngram | in_behavioural |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| qwen3-4b-e2c-gen.claude46_C_s1 | qwen3-4b-e2c-gen | C | claude46 | claude46 | 0.954 | claude46 | 0.024 | claude46 | 1.000 | 1.000 | 1.000 | yes |
| qwen3-4b-e2c-gen.deepseek_v4_C_s1 | qwen3-4b-e2c-gen | C | deepseek_v4 | deepseek_v4 | 0.588 | deepseek_v4 | 0.039 | unattributed | 1.000 | 1.000 | 1.000 | yes |
| qwen3-4b-e2c-gen.gpt4o_C_s1 | qwen3-4b-e2c-gen | C | gpt4o | gpt4o | 0.827 | unattributed | 0.002 | unattributed | 1.000 | 0.000 | 0.000 | yes |
| qwen3-4b-e2c-gen.claude46_O_s1 | qwen3-4b-e2c-gen | O | claude46 | claude46 | 0.958 | claude46 | 0.025 | claude46 | 1.000 | 1.000 | 1.000 | yes |
| qwen3-4b-e2c-gen.deepseek_v4_O_s1 | qwen3-4b-e2c-gen | O | deepseek_v4 | deepseek_v4 | 0.873 | deepseek_v4 | 0.032 | unattributed | 1.000 | 1.000 | 1.000 | yes |
| qwen3-4b-e2c-gen.gpt4o_O_s1 | qwen3-4b-e2c-gen | O | gpt4o | gpt4o | 0.966 | unattributed | 0.005 | unattributed | 1.000 | 0.000 | 0.000 | yes |

## 混淆（run 级，全部网格）

| features | true_teacher | n | pred_gpt4o | pred_claude46 | pred_deepseek_v4 |
|---|---|---|---|---|---|
| ngram | gpt4o | 2 | 2 | 0 | 0 |
| ngram | claude46 | 2 | 0 | 2 | 0 |
| ngram | deepseek_v4 | 2 | 0 | 0 | 2 |
| length | gpt4o | 2 | 2 | 0 | 0 |
| length | claude46 | 2 | 0 | 2 | 0 |
| length | deepseek_v4 | 2 | 1 | 0 | 1 |

## 运行

- 命令：`scripts/22_lexical_provenance.py classify-generations --train-sft-dirs data/sft_e2c_paired --generations runs/qwen3-4b-e2c-gen/*/eval/test_generations.jsonl --behavioural results/e7_gen/e7_runs.csv --out results/e7_lexical_students`
- 生成文件 6 个；训练目录 data/sft_e2c_paired；耗时 16 s
