# 格子结构分解（dev；描述性）

teacher 两两一致率：gpt4o vs claude46 0.910；gpt4o vs deepseek_v4 0.901；claude46 vs deepseek_v4 0.855（545 个三家都有多数行动的 cell）

| 结构 | cell 数 |
|---|---|
| all_agree | 454 |
| unique_deepseek_v4 | 42 |
| unique_claude46 | 37 |
| unique_gpt4o | 12 |

## 学生在自己 teacher 唱独角的 cell 上的跟随率（seed 均值；follow_other_max = 跟随别家中最高者）

| 条件 | 版本 | teacher | cell 数 | follow_own | follow_other_max | n_runs |
|---|---|---|---|---|---|---|
| Cnf | O | claude46 | 37 | 0.681 | 0.319 | 5 |
| Cnf | O | deepseek_v4 | 42 | 0.762 | 0.238 | 5 |
| Cnf | O | gpt4o | 12 | 0.433 | 0.567 | 5 |
| E1 | O | claude46 | 37 | 0.541 | 0.459 | 5 |
| E1 | O | deepseek_v4 | 42 | 0.629 | 0.371 | 5 |
| E1 | O | gpt4o | 12 | 0.333 | 0.667 | 5 |
| E2c_C | O | claude46 | 37 | 0.665 | 0.335 | 5 |
| E2c_C | O | deepseek_v4 | 42 | 0.743 | 0.257 | 5 |
| E2c_C | O | gpt4o | 12 | 0.533 | 0.467 | 5 |
| E3c | C | claude46 | 37 | 0.625 | 0.375 | 5 |
| E3c | C | deepseek_v4 | 42 | 0.719 | 0.281 | 5 |
| E3c | C | gpt4o | 12 | 0.550 | 0.450 | 5 |
| E3c | F | claude46 | 37 | 0.665 | 0.335 | 5 |
| E3c | F | deepseek_v4 | 42 | 0.767 | 0.233 | 5 |
| E3c | F | gpt4o | 12 | 0.517 | 0.483 | 5 |
| E3c | O | claude46 | 37 | 0.649 | 0.351 | 5 |
| E3c | O | deepseek_v4 | 42 | 0.729 | 0.271 | 5 |
| E3c | O | gpt4o | 12 | 0.517 | 0.483 | 5 |
| K | O | claude46 | 37 | 0.459 | 0.541 | 5 |
| K | O | deepseek_v4 | 42 | 0.467 | 0.533 | 5 |
| K | O | gpt4o | 12 | 0.500 | 0.500 | 5 |
| K_n | O | claude46 | 37 | 0.476 | 0.524 | 5 |
| K_n | O | deepseek_v4 | 42 | 0.471 | 0.529 | 5 |
| K_n | O | gpt4o | 12 | 0.483 | 0.517 | 5 |
| base2_C | O | claude46 | 37 | 0.681 | 0.319 | 5 |
| base2_C | O | deepseek_v4 | 42 | 0.729 | 0.271 | 5 |
| base2_C | O | gpt4o | 12 | 0.583 | 0.417 | 5 |
| base2_K | O | claude46 | 37 | 0.389 | 0.611 | 5 |
| base2_K | O | deepseek_v4 | 42 | 0.400 | 0.600 | 5 |
| base2_K | O | gpt4o | 12 | 0.583 | 0.417 | 5 |
