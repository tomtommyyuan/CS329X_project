# E2 执行计划：Heritability（headline；复用 E1 的 checkpoint，不训练）

> 协议：[docs/03_experiments.md](../docs/03_experiments.md) §3；指标 D 组：[docs/04_eval_metrics.md](../docs/04_eval_metrics.md) §2；实现：`src/vcd/analysis/e1_metrics.py`（`inheritance`、`pooled_inheritance`、`grid_permutation`、`seed_noise_null`、`shared_component_r2`），由 `scripts/13_e1_analysis.py` 一并输出。E0 的 teacher 侧结果：[docs/E0_results.md](../docs/E0_results.md) §9、§13。

## 0. 问题

在**未见过的** test family 上，学生的 framing profile 更像自己的 teacher 吗？profile 指 family 内去均值后的 framing shift r(i, j)，它不是"平均判断像不像"（那是 E1），而是"哪类情境在哪种问法下往哪边偏"。特别地：teacher 的 suggestibility（δ(T5) − δ(T6)）是否被学生继承，并保持 DeepSeek > GPT-4o > Claude 的顺序。

## 1. 量

| 量 | 定义 | 实现 |
|---|---|---|
| r_s(i, j), r_T(i, j) | test 集 (family, variant) cell 上，两种顺序平均后的 p(正向行动) 减该 family 跨 variant 的均值 | `sym_table` → `framing_shifts` |
| ρ(own), ρ(other) | r_s 与各 teacher r_T 在共同 cell 上的 Pearson 与 Spearman | `inheritance` |
| Δρ | ρ(own) − max ρ(other)，每个学生一个 | 同上 |
| pooled Δρ | 同 (teacher, O) 五个 seed 的 r_s 先平均再算 ρ，一个 teacher 一个数 | `pooled_inheritance` |
| p 值 | family permutation 10,000 次（打乱 family 标签，重算 Δρ），teacher 间 Holm 校正 | `grid_permutation`, `holm` |
| CI | family bootstrap 10,000 | 同上 |
| 按 type | Δρ 只用 T1 / T3 / T5 / T6 中的一种 variant 的 cell | 同上，自动写 `inheritance_by_variant.csv` |
| 见过 vs 未见 | T1 / T3 / T5 / T6（训练见过的 type）vs T0（未见） | `seen_vs_unseen` |
| suggestibility 继承 | 学生的 δ(T5) − δ(T6) 对 teacher 的；三 teacher 的顺序是否保持 | `type_effects` 复用 |
| 共享成分 | r_s 对 r_own 与 r_other 联合回归的 R² | `shared_component_r2` |
| 上界 | teacher 自身的顺序 split-half 可靠度（test：GPT-4o 0.69、DeepSeek 0.47、Claude 0.33） | 直接报 ρ / 可靠度 |

## 2. 预注册的决策规则（dev 上冻结，test 只跑一次）

| 结果 | 结论 |
|---|---|
| ≥ 2 / 3 teacher 的 pooled Δρ > 0 且 Holm 后 p < 0.05，且不是只靠单一 type | **heritability 成立**，RQ1 是 headline |
| 只有 1 个 teacher 成立，或只在一种 type 上成立 | 部分成立，按 type 报告，headline 转 E3 的 form 调节 |
| 都不成立 | RQ1 降为 exploratory，主线 E2b / E3 / E4 / E5；仍报共享成分 R² 和 suggestibility 的方向 |

控制必须同时满足：R 学生的 Δρ ≈ 0（p 不显著）；S_0 基座的 Δρ ≈ 0；E1 的 agreement 规则已过（否则 E2 的 ρ 只是没学会）。

## 3. 步骤

| # | 做什么 | 命令 | 产出 |
|---|---|---|---|
| 1 | dev 上跑全套，检查流程与上界 | `python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split dev --out results/e1_dev --n-perm 10000 --n-boot 10000` | `results/e1_dev/inheritance.csv`、`inheritance_pooled.csv`、`inheritance_by_variant.csv`、`seen_vs_unseen.csv`、`summary.md` |
| 2 | 冻结 | 在 `tasks/hpc_log.md` 写一行"E2 规则冻结于 <commit>"，之后不改 13 的任何默认值 | — |
| 3 | test | 同 1，`--split test --out results/e1` | 同上，`summary.md` 里的 "E2 PASS / FAIL" 行就是结论 |
| 4 | 提交 | `git add results/e1_dev results/e1 tasks/hpc_log.md && git commit && git pull --rebase && git push` | Mac 侧写论文表 |

## 4. 怎么读结果

- Δρ 的尺度：teacher 两两 profile 相关在 test 上只有 0.25 到 0.35（残差 0.20 到 0.28），所以 Δρ 即便成立也可能只有 0.05 到 0.15；要和 seed-noise null 的 SD 一起报效应量。
- ρ 的天花板是 teacher 自己的可靠度：Claude 学生的 ρ(own) 超不过 0.33 左右，这不是学生的问题；报 ρ / 可靠度。
- T0 是学生从未见过的问法：T0 上的 Δρ > 0 是"继承 disposition"最干净的证据；T1 到 T6 上的 Δρ 可能混有对 stem 措辞的记忆。
- 任何在 test 上"再试一种 readout 或阈值"的念头都违反预注册；想试就回 dev，并在 log 里写明。

## 5. 后续依赖

E3（F / C 学生）复用同一套量，比较 Δρ(S_{T,F / C}) − Δρ(S_{T,O})（seed 配对）；E7 的 provenance 用 ρ 做最近 teacher 分类。两者都要等 `data/rewrites_train/` 完成后重建 paired 的 O / F / C 文件再训。
