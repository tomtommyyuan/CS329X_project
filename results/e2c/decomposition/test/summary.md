# 格子结构分解（test；描述性）

teacher 两两一致率：gpt4o vs claude46 0.927；gpt4o vs deepseek_v4 0.930；claude46 vs deepseek_v4 0.917（1121 个三家都有多数行动的 cell）

| 结构 | cell 数 |
|---|---|
| all_agree | 994 |
| unique_claude46 | 48 |
| unique_deepseek_v4 | 45 |
| unique_gpt4o | 34 |

## 学生在自己 teacher 唱独角的 cell 上的跟随率（seed 均值；follow_other_max = 跟随别家中最高者）

| 条件 | 版本 | teacher | cell 数 | follow_own | follow_other_max | n_runs |
|---|---|---|---|---|---|---|
| Cnf | O | claude46 | 48 | 0.596 | 0.404 | 5 |
| Cnf | O | deepseek_v4 | 45 | 0.871 | 0.129 | 5 |
| Cnf | O | gpt4o | 34 | 0.606 | 0.394 | 5 |
| E1 | O | claude46 | 48 | 0.471 | 0.529 | 5 |
| E1 | O | deepseek_v4 | 45 | 0.498 | 0.502 | 5 |
| E1 | O | gpt4o | 34 | 0.418 | 0.582 | 5 |
| E2c_C | O | claude46 | 48 | 0.575 | 0.425 | 5 |
| E2c_C | O | deepseek_v4 | 45 | 0.827 | 0.173 | 5 |
| E2c_C | O | gpt4o | 34 | 0.506 | 0.494 | 5 |
| E3c | C | claude46 | 48 | 0.546 | 0.454 | 5 |
| E3c | C | deepseek_v4 | 45 | 0.813 | 0.187 | 5 |
| E3c | C | gpt4o | 34 | 0.459 | 0.541 | 5 |
| E3c | F | claude46 | 48 | 0.521 | 0.479 | 5 |
| E3c | F | deepseek_v4 | 45 | 0.813 | 0.187 | 5 |
| E3c | F | gpt4o | 34 | 0.553 | 0.447 | 5 |
| E3c | O | claude46 | 48 | 0.579 | 0.421 | 5 |
| E3c | O | deepseek_v4 | 45 | 0.778 | 0.222 | 5 |
| E3c | O | gpt4o | 34 | 0.524 | 0.476 | 5 |
| K | O | claude46 | 48 | 0.446 | 0.554 | 5 |
| K | O | deepseek_v4 | 45 | 0.436 | 0.564 | 5 |
| K | O | gpt4o | 34 | 0.394 | 0.606 | 5 |
| K_n | O | claude46 | 48 | 0.463 | 0.537 | 5 |
| K_n | O | deepseek_v4 | 45 | 0.480 | 0.520 | 5 |
| K_n | O | gpt4o | 34 | 0.382 | 0.618 | 5 |
| base2_C | O | claude46 | 48 | 0.637 | 0.362 | 5 |
| base2_C | O | deepseek_v4 | 45 | 0.778 | 0.222 | 5 |
| base2_C | O | gpt4o | 34 | 0.518 | 0.482 | 5 |
| base2_K | O | claude46 | 48 | 0.375 | 0.625 | 5 |
| base2_K | O | deepseek_v4 | 45 | 0.369 | 0.631 | 5 |
| base2_K | O | gpt4o | 34 | 0.429 | 0.571 | 5 |
