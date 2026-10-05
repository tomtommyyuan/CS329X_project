# E2 执行计划：Heritability（headline；复用 E1 的 checkpoint，不训练）

> 协议：[docs/03_experiments.md](../docs/03_experiments.md) §3；指标 D 组：[docs/04_eval_metrics.md](../docs/04_eval_metrics.md) §2；实现：`src/vcd/analysis/e1_metrics.py`（`base_prior_shifts`、`inheritance_partial`、`pooled_inheritance_partial`、`grid_permutation_partial`、`suggestibility_by_run`、`dose_response`；原规则的 `inheritance`、`pooled_inheritance`、`grid_permutation` 保留），由 `scripts/13_e1_analysis.py` 一并输出（docs/05 §6）。E0 的 teacher 侧结果：[docs/E0_results.md](../docs/E0_results.md) §9、§13。dev 诊断：`results/e1_dev_diag/README.md`。

## 0. 问题

在**未见过的** test family 上，学生的 framing profile 更像自己的 teacher 吗？profile 指 family 内去均值后的 framing shift r(i, j)，它不是"平均判断像不像"（那是 E1），而是"哪类情境在哪种问法下往哪边偏"。特别地：teacher 的 suggestibility（δ(T5) − δ(T6)）是否被学生继承，并保持 DeepSeek > GPT-4o > Claude 的顺序。

dev 发现（2026-10-04）：所有学生从同一个基座出发，而基座自己的先验 profile 就像 DeepSeek（相关 0.49 vs 0.28 / 0.25），所以未控制基座的 Δρ = ρ(own) − max ρ(other) 对非 DeepSeek 学生结构性为负；但打乱 teacher 归属的 permutation p < 1e-4，suggestibility 的 teacher 顺序被学生保持。2026-10-05 Mac 侧据此在 dev 上修订量与规则并冻结（§1、§2）。

## 1. 量（2026-10-05 冻结）

| 量 | 定义 | 实现 |
|---|---|---|
| r_s(i, j), r_T(i, j) | split 的 (family, variant) cell 上，两种顺序平均后的 p(正向行动) 减该 family 跨 variant 的均值 | `sym_table` → `framing_shifts` |
| r_0(i, j) | **基座先验 profile**：未训练 S_0 的两字母重归一化概率，**不加 0.9 质量门**（否则 S_0 只有 5 个完整 family），同样去均值。它是协变量，不是 S_0 答案的 readout；readout 的 0.9 规则不变 | `sym_table(mass_gate=False)` → `base_prior_shifts` |
| partial ρ(own | r_0), partial ρ(other | r_0) | r_s 与 r_T 各对 [1, r_0] 回归取残差后的 Pearson，在 run / 全部 teacher / r_0 都完整的 cell 上 | `inheritance_partial`（`profile_rho_partial` 给 raw 与 partial 对照） |
| ΔρPartial | partial ρ(own) − max partial ρ(other)，每个 O run 一个；另给 family permutation p 与 family bootstrap CI | 同上 → `inheritance_partial.csv` |
| **P1** | mean over 15 个 O run 的 ΔρPartial；null = 把 15 个 run 重新指派给 teacher（每 teacher 5 个），全部 756,756 种枚举（method `exact`，p 下限 1/756,756） | `grid_permutation_partial` → `grid_permutation_partial.json` |
| s_run, s_T | δ(T5) − δ(T6)，正向行动坐标，**在同一 family 集上**：对全部 15 个 O run、3 个 teacher 和 r_0 都完整的 family（`complete_families`，dev 139 个；各 teacher 自己的完整集 148 / 149 / 140 不用，test 上也不另选） | `suggestibility_by_run(families=公共集)` → `suggestibility_runs.csv` |
| **P2** | s_run 对自己 teacher 的 s_T（3 个取值）在 15 个 O run 上回归的 slope；p 单侧，null 同 P1 的重指派；另报 seed-noise SD、三 teacher 的学生均值、顺序是否保持、R run 与 S_0 的 s（描述） | `dose_response` → `dose_response.json` |
| **P3**（supportive） | 每 teacher 5 seed 的 seed-mean r_s 的 ΔρPartial，family permutation 10,000 + Holm | `pooled_inheritance_partial` → `inheritance_partial_pooled.csv` |
| 按 type / 未见 | ΔρPartial 只用 T1 / T3 / T5 / T6 中一种 variant 的 cell；T0 行：r 在 T0 + 四个 seen variant 上去均值，只取 T0 cell | `inheritance_partial_by_variant.csv` |
| 原规则（透明度） | uncontrolled Δρ、pooled Δρ + Holm、随机打乱归属的 grid permutation | `inheritance.csv`、`inheritance_pooled.csv`、`grid_permutation.json` |
| 共享成分 | r_s 对 r_own 与 r_other 联合回归的 R² | `shared_component_r2` |
| 上界 | teacher 自身的顺序 split-half 可靠度（test：GPT-4o 0.69、DeepSeek 0.47、Claude 0.33） | 直接报 ρ / 可靠度 |

## 2. 决策规则（2026-10-05 在 dev 上冻结，test 只跑一次）

| 结果 | 结论 |
|---|---|
| P1 p < 0.05 **且** P2 slope > 0、p < 0.05 | **E2 PASS：teacher 归属可预测学生 profile 与 suggestibility（超出基座先验 r_0）**，RQ1 是 headline。P1 / P2 是相对检验（与随机归属比），不保证每个学生离自己 teacher 最近，所以论文表必须把 P3 的逐 teacher 行放在 P1 旁边（dev 上 claude46 学生的 ΔρPartial 为负、最近的仍是 DeepSeek，也要照报）；P3 ≥ 2/3 teacher 为正则补"每个 teacher 单独也朝对的方向" |
| 只有 P1 或只有 P2 成立 | 部分成立：成立的那条做 headline（profile 继承 vs suggestibility 剂量继承），另一条按 type 报告 |
| 都不成立 | RQ1 降为 exploratory，主线 E2b / E3 / E4 / E5；仍报共享成分 R² 和 suggestibility 的方向 |

前提：E1（e1_plan §0 的 E1a + E1b）已过，否则 E2 的 ρ 只是没学会。R run 与 S_0 不进 P1 / P2 的统计，只在表里描述（R 的 s ≈ 0、ΔρPartial 不定义；S_0 的 s 用先验 profile 报）。**dev 是选规则的 split**：P1 / P2 正是因为 dev 诊断里未控制的归属 permutation 已经 p < 1e-4、suggestibility 顺序已经保持才被选中，所以 dev 上的 PASS 由构造保证，只是描述；13 在 split ≠ test 时会在 Verdicts 表下自动印这句，只有 `results/e1`（test）是确认性的。dev 值（`results/e1_dev_revised/summary.md`，n_perm = n_boot = 10,000）：P1 mean ΔρPartial 0.026、null −0.060 ± 0.019、p 1.3e-6（exact，观测指派是 756,756 种里的唯一最大值）；P2 slope 1.15、p 1.3e-6、顺序保持、seed-noise SD 0.012；P3 deepseek_v4 +0.086 / gpt4o +0.020 / claude46 −0.022（Holm p 全部 > 0.3）。p 约定：exact p = 全部指派中（含观测）统计量 ≥ 观测的占比；family permutation 与随机指派 p = (count + 1) / (n + 1)；CI = family bootstrap 2.5 / 97.5 分位。

原规则（2026-10-04 在 dev 上未过，2026-10-05 被上表替换，留档一行）：≥ 2/3 teacher 的 seed-mean uncontrolled Δρ > 0 且 Holm 后 p < 0.05 → heritability 成立；dev 结果 0/3（claude46 −0.111、deepseek_v4 +0.182、gpt4o −0.092）。

## 3. 步骤

| # | 做什么 | 命令 | 产出 |
|---|---|---|---|
| 1 | dev 上用新 13 重跑（覆盖 `results/e1_dev`），核对与 Mac 侧 `results/e1_dev_revised` 一致；dev 的 E2 判定只是描述（见 §2），不要当结果报 | `python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split dev --out results/e1_dev --n-perm 10000 --n-boot 10000` | `results/e1_dev/inheritance_partial*.csv`、`grid_permutation_partial.json`、`dose_response.json`、`e1_train_reproduction.csv`、`e1_contested.csv`、`summary.md` |
| 2 | 冻结 | 在 `tasks/hpc_log.md` 写一行"E1 / E2 规则冻结于 <commit>"（<commit> = 含本次修订的 main HEAD），之后不改 13 的任何默认值 | — |
| 3 | test | 同 1，`--split test --out results/e1`（先评 S_0 与全部 run 的 test，e1_plan §7） | 同上，`summary.md` 的 Verdicts 表就是结论 |
| 4 | 提交 | `git add results/e1_dev results/e1 tasks/hpc_log.md && git commit && git pull --rebase && git push` | Mac 侧写论文表 |

## 4. 怎么读结果

- Δρ 的尺度：teacher 两两 profile 相关在 test 上只有 0.25 到 0.35（残差 0.20 到 0.28），所以 Δρ 即便成立也可能只有 0.05 到 0.15；要和 seed-noise null 的 SD 一起报效应量。ΔρPartial 比 raw Δρ 更小（dev 上 mean 0.026），它的意义在"与随机归属相比"（null 均值 −0.06），不在绝对值。
- ρ 的天花板是 teacher 自己的可靠度：Claude 学生的 ρ(own) 超不过 0.33 左右，这不是学生的问题；报 ρ / 可靠度。
- T0 是学生从未见过的问法：T0 上的 Δρ > 0 是"继承 disposition"最干净的证据；T1 到 T6 上的 Δρ 可能混有对 stem 措辞的记忆。
- 任何在 test 上"再试一种 readout 或阈值"的念头都违反预注册；想试就回 dev，并在 log 里写明。

## 5. 后续依赖

E3（F / C 学生）复用同一套量，比较 Δρ(S_{T,F / C}) − Δρ(S_{T,O})（seed 配对）；E7 的 provenance 用 ρ 做最近 teacher 分类。两者都要等 `data/rewrites_train/` 完成后重建 paired 的 O / F / C 文件再训。
