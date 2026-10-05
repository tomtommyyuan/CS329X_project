# E2 执行计划：Heritability（headline；复用 E1 的 checkpoint，不训练）

> 协议：[docs/03_experiments.md](../docs/03_experiments.md) §3；指标 D 组：[docs/04_eval_metrics.md](../docs/04_eval_metrics.md) §2；实现：`src/vcd/analysis/e1_metrics.py`（primary `pooled_inheritance`；secondary `joint_partial_D`；描述 `inheritance_partial`、`pooled_inheritance_partial`、`grid_permutation_partial` + `teacher_level_exact_p`、`suggestibility_groups`、`dose_response`、`base_prior_control`），由 `scripts/13_e1_analysis.py` 一并输出（docs/05 §6）。E0 的 teacher 侧结果：[docs/E0_results.md](../docs/E0_results.md) §9、§13。dev 诊断：`results/e1_dev_diag/README.md`。

## 0. 问题

在**未见过的** test family 上，学生的 framing profile 更像自己的 teacher 吗？profile 指 family 内去均值后的 framing shift r(i, j)，它不是"平均判断像不像"（那是 E1），而是"哪类情境在哪种问法下往哪边偏"。特别地：teacher 的 suggestibility（δ(T5) − δ(T6)）是否被学生继承，并保持 DeepSeek > GPT-4o > Claude 的顺序。

dev 发现（2026-10-04）：所有学生从同一个基座出发，而基座自己的先验 profile 就像 DeepSeek（相关 0.53 vs 0.28 / 0.25），所以未控制基座的 Δρ = ρ(own) − max ρ(other) 对非 DeepSeek 学生结构性为负。2026-10-05 Mac 侧先在 dev 上改成 run-level 置换（c2c9d96），HPC agent 指出那是伪复制（同 teacher 的 seed 近复制，可交换单位只有 3 个 teacher）；同日更正为 §1、§2：原 Δρ 规则保留为 primary，family 作推断单位，次级统计量 D，剂量反应降为描述。更正稿审查又发现两点并在冻结前修掉：D 对"共享学生残差 × 行尺度不等"不免疫（加 D_specific 守门，版本 5）；split-half r 不是 ρ 的上界（上限改为 sqrt(2r / (1 + r))）。

## 1. 量（2026-10-05 冻结，同日更正）

| 量 | 定义 | 实现 |
|---|---|---|
| r_s(i, j), r_T(i, j) | split 的 (family, variant) cell 上，两种顺序平均后的 p(正向行动) 减该 family 跨 variant 的均值 | `sym_table` → `framing_shifts` |
| r_0(i, j) | **基座先验 profile**：未训练 S_0 的两字母重归一化概率，**不加 0.9 质量门**（否则 S_0 只有 5 个完整 family），同样去均值。协变量，不是 S_0 答案的 readout；readout 的 0.9 规则不变 | `sym_table(mass_gate=False)` → `base_prior_shifts` |
| **推断单位** | **family**（dev 150、test 300）。同一 teacher 的 5 个 seed 是同一训练数据的近复制，run 不可交换；teacher 只有 3 个（3! = 6 种重标号，精确 p 下限 1/6）。所有确认性统计量只用 family bootstrap CI 与 family permutation null | — |
| **Primary：Δρ** | 每 teacher 5 seed 的 seed-mean r_s 与各 teacher 的 Pearson；Δρ = ρ(own) − max ρ(other)，不控制 r_0（原预注册量）；family permutation 10,000 的 p，Holm 校正跨 teacher；family bootstrap CI | `pooled_inheritance` → `inheritance_pooled.csv` |
| **Secondary：D** | M[k, j] = partial ρ(r_{S_k}, r_{T_j} ∣ r_0)，S_k = teacher k 的 seed-mean 学生，只用见过的 framing（T1 / T3 / T5 / T6），family 对所有学生、teacher、r_0 完整；**D = mean_k [M[k,k] − mean_{j≠k} M[k,j]]**（对角减非对角均值）。family bootstrap 95% CI（三方联动重抽，10,000）；family permutation p（10,000）：对学生给定 r_0 的**残差**做同一个 family 置换（三个学生同步），teacher 与 r_0 不动——置换残差是因为偏相关用的就是残差（Kennedy / Freedman-Lane）；dev 上置换原始 profile 的 null 不可区分（sd 0.020 vs 0.022，p 相同），不是调出来的。另报 T0-only D（r 在 T0 + 四个 seen variant 上去均值，只取 T0 cell）与 raw D（不控制 r_0），都是探索 | `joint_partial_D` → `e2_secondary_D.json` |
| **D 的分解（守门）** | 学生残差 E_k = Ē + U_k（Ē = 三个学生残差的均值）。M = M_shared + M_specific，M_shared[k, j] = ⟨Ē, T_j⟩ / (‖E_k‖‖T_j‖)，M_specific 用 U_k；**D = D_shared + D_specific**。D_shared 不含任何 own-teacher 信息，只在行尺度 ‖E_k‖ 相等时抵消（dev 行尺度 0.055 / 0.110 / 0.078，不等），permutation null 与 bootstrap 都看不出它；D_specific 单独给 family bootstrap CI 与 permutation p。另报 D_scalefree（每行除以 pooled 尺度 s̄，shared 部分精确抵消）作探索 | `joint_partial_D` 的 `D_shared` / `D_specific` / `ci_specific_*` / `p_perm_specific` / `D_scalefree` |
| 描述：mean ΔρPartial | 15 个 O run 的 partial ρ(own ∣ r_0) − max partial ρ(other ∣ r_0) 的均值；只报 teacher 层面精确 p（6 种重标号中统计量 ≥ 观测的占比）；run-level 756,756 种重指派的 p 一并印出但标为伪复制 | `inheritance_partial`、`grid_permutation_partial`（`teacher_exact`）、`teacher_level_exact_p` |
| 描述：suggestibility | s = δ(T5) − δ(T6)，正向行动坐标，在对全部 O run、3 teacher、r_0 都完整的公共 family 集上（dev 139）。每组（某 teacher 的 5 个 O run、teacher 自己、R run、base prior）的 s 与 family-bootstrap CI，所有两两差及 CI（配对重抽）；剂量反应 slope 只报数字 + teacher 层面精确 p。检验的说法（描述性）："SFT 用训练标签里的 framing–标签关联替换了基座自带的 suggestibility" | `suggestibility_groups` → `suggestibility_groups.csv`、`suggestibility_group_pairs.csv`；`dose_response`（`teacher_exact`） |
| 描述：P3 | 每 teacher seed-mean 的 ΔρPartial，family permutation + Holm | `pooled_inheritance_partial` → `inheritance_partial_pooled.csv` |
| 控制：S_0 | 原 e2_plan 的"S_0 的 Δρ ≈ 0"用 **ungated covariate profile** r_0 算（0.9 门下 S_0 几乎没有完整 family，c2c9d96 版本里是 NaN）：r_0 对每个 teacher 的 ρ 与 CI，最近 teacher 的 margin = ρ − 次大 ρ 及 CI；margin CI 含 0 → 控制成立 | `base_prior_control` → `base_control.csv` |
| 上界 | r = teacher 的顺序 split-half 可靠度（docs/E0_results §13；dev GPT-4o 0.675 / DeepSeek 0.515 / Claude 0.383，test 0.691 / 0.466 / 0.329）。symmetrized profile 是两种顺序的平均，可靠度为 Spearman-Brown 2r / (1 + r)，任何变量与它的相关上限 = **sqrt(2r / (1 + r))**：dev 0.898 / 0.825 / 0.744，test 0.904 / 0.797 / 0.704。r 本身不是上界（dev 上 r_0 与 DeepSeek 的 ρ 0.533 > r 0.515）。每个 ρ_own 旁印上限与 ρ / 上限，每个 teacher 列下印列上限行；E0 门槛仍看 r | `reliability_ceiling`；13 的 `RELIABILITY`（`--reliability` 给 r，可覆盖） |
| 共享成分 | r_s 对 r_own 与 r_other 联合回归的 R² | `shared_component_r2` |

## 2. 决策规则（2026-10-05 在 dev 上冻结并更正，test 只跑一次）

| 判定 | 规则 | 结论 |
|---|---|---|
| **E2 primary** | ≥ 2/3 teacher 的 seed-mean Δρ > 0 且 Holm p < 0.05 → **PASS**；恰 1/3 → **PARTIAL**；0/3 → **FAIL**。如实报 | PASS：heritability 成立，RQ1 headline（但见下方可靠度门槛）；PARTIAL：按 teacher / type 报告；FAIL：RQ1 降为 exploratory |
| **E2 secondary** | D > 0、family bootstrap 95% CI 不含 0 且 family permutation p < 0.05，**且** D_specific 的 family bootstrap CI 下界 > 0 → pass；任一不满足 → fail | pass 的含义：扣掉基座先验与共享的学生残差后，固定一个 teacher，最像它的是它自己的学生——相对的、矩阵层面的继承，不等于每个学生离自己 teacher 最近 |
| 描述项 | 不判定；mean ΔρPartial、slope、P3、各组 s 与两两差、S_0 控制行、T0 D、raw D、D_scalefree 全部印在 Verdicts 下面的 Descriptive 表 | 论文表与正文 |
| 可靠度门槛 | test 侧 DeepSeek 0.47、Claude 0.33 两个 teacher 的 split-half r < 0.5，触发 docs/03 §1 的 E0 规则（≥ 2 个 teacher 可靠度 < 0.5 → P2 不成立） | docs/03 §1 原文：**"RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5"**，本项目做其中的 E3（form 对继承的调节）；13 在 summary 里自动印这段与每个 ρ 的上限 sqrt(2r / (1 + r)) |

前提：E1（e1_plan §0 的 E1a + E1b）已过，否则 E2 的 ρ 只是没学会。R run 与 S_0 不进 primary / secondary，只在描述表（R 的 s ≈ 0；S_0 的 s 与控制行用 ungated covariate profile）。**dev 是选规则的 split**，dev 上的判定只是描述；只有 `results/e1`（test）是确认性的。p 约定：family permutation p = (count + 1) / (n + 1)；teacher 层面精确 p = k! 种重标号中（含观测）统计量 ≥ 观测的占比（下限 1/6）；CI = family bootstrap 2.5 / 97.5 分位。

dev 值（`results/e1_dev_revised/summary.md`，n_perm = n_boot = 10,000，139 个公共 family）：

| 项 | dev |
|---|---|
| primary Δρ（p_perm；null 均值；Holm p） | claude46 −0.111 [−0.260, 0.034]（0.634；−0.091；0.956）；deepseek_v4 +0.182 [0.054, 0.308]（0.021；+0.088；0.063）；gpt4o −0.092 [−0.233, 0.056]（0.478；−0.094；0.956）→ 0/3，**FAIL**。permutation null 不以 0 为中心（置换保留各 profile 的 variant 主效应），deepseek 的 Δρ 有一半是 null 均值 |
| ρ_own / 上限 | claude46 0.234 / 0.744 = 0.31；deepseek_v4 0.504 / 0.825 = 0.61；gpt4o 0.377 / 0.898 = 0.42 |
| secondary D（seen，partial） | **0.101 [0.041, 0.164]，p 1.0e-4**（null 均值 0.005、sd 0.022）；**D_shared −0.039，D_specific 0.140 [0.065, 0.226]，p 1.0e-4**（null 0.009 ± 0.027）→ pass；D_scalefree 0.118 [0.055, 0.183]（探索） |
| D（T0-only，探索） | 0.027 [−0.035, 0.092]，p 0.15（137 family） |
| raw D（不控制 r_0，探索） | 0.090 [0.040, 0.142]，p 1.0e-4 |
| partial 矩阵（行 = 学生，列 = teacher：claude46 / deepseek_v4 / gpt4o） | claude 学生 0.156 / 0.177 / 0.134；deepseek 学生 0.009 / 0.298 / 0.211；gpt4o 学生 0.072 / 0.264 / 0.284；列上限 0.744 / 0.825 / 0.898；行 contrast −0.000 / 0.187 / 0.116，contrast_specific 0.262 / 0.099 / 0.057 |
| mean ΔρPartial（15 run） | 0.026，teacher 层面精确 p 1/6（rank 1 of 6）；run-level p 1.3e-6 伪复制 |
| slope | 1.15（pearson 0.88，seed-noise sd 0.012，顺序保持），teacher 层面精确 p 1/6 |
| P3 ΔρPartial（Holm p） | claude46 −0.022（0.338）、deepseek_v4 +0.086（0.325）、gpt4o +0.020（0.338） |
| 各组 s | 学生 claude46 0.048 [0.031, 0.068]、deepseek_v4 0.171 [0.129, 0.215]、gpt4o 0.120 [0.089, 0.153]；teacher 0.059 / 0.149 / 0.075；R 0.001；base prior 0.165 [0.144, 0.186] |
| 两两差 | 学生 deepseek − gpt4o +0.051 [0.025, 0.078]、gpt4o − claude +0.072 [0.050, 0.096]；学生 − 自己 teacher：claude −0.011 [−0.050, 0.025]、deepseek +0.021 [−0.021, 0.065]、gpt4o +0.045 [0.013, 0.077]；学生 − base prior：claude −0.117、gpt4o −0.045 [−0.075, −0.014]、deepseek +0.006 [−0.033, 0.047] |
| S_0 控制行 | 最近 teacher deepseek_v4：ρ 0.533 [0.448, 0.611]，margin 0.256 [0.130, 0.359] → 控制**不成立**：基座训练前就系统性最像 DeepSeek，这正是 partial ρ 要扣掉的混淆 |

**规则版本披露（按时间，论文必须全列）**：

| # | 版本 | 状态 |
|---|---|---|
| 1 | 原预注册（d06f6d5）：seed-mean uncontrolled Δρ > 0 且 Holm p < 0.05 的 teacher ≥ 2/3；控制 R 与 S_0 的 Δρ ≈ 0 | 2026-10-04 dev 上 0/3；**现在仍是 primary**，如实报 FAIL / PARTIAL / PASS |
| 2 | P3：每 teacher 的 partial Δρ（给定 r_0）+ Holm | dev 2/3 为正、无一显著；保留为描述（supportive） |
| 3 | c2c9d96 的 P1（15 个 run 重指派 teacher，756,756 种枚举，mean ΔρPartial）与 P2（s_run 对 s_T 的剂量反应 slope，同一 null） | **同日撤回**：run 不可交换（同 teacher 的 seed 近复制），伪复制；teacher 层面精确 p 下限 1/6，dev 两者都恰为 1/6。数字保留为描述 |
| 4 | secondary D（family bootstrap + family 残差置换，见过的 framing，partial 给定 r_0），单独判定 | 预先声明的次级统计量；dev 上同一族的交互量在 e1_dev_diag 里算过 15 个变体（见 `results/e1_dev_diag/interpretation.md`），这里只冻结这一个，T0 与 raw 版本标为探索。**冻结前审查发现** D 不免疫"共享学生残差 × 行尺度不等"（dev D_shared −0.039；模拟：无特有继承、Claude 偏差 ×3、DeepSeek ÷3 时 D 均值 +0.04，单看 D 的规则误拒约 28%），被版本 5 取代 |
| 5 | **本版**：D 同上 + 守门 D_specific 的 family bootstrap CI 下界 > 0（分解 D = D_shared + D_specific，见 §1） | 冻结；dev D_specific 0.140 [0.065, 0.226]。备选 D_scalefree（pooled 行尺度）只作探索报告 |

## 3. 步骤

| # | 做什么 | 命令 | 产出 |
|---|---|---|---|
| 1 | dev 上用新 13 重跑（覆盖 `results/e1_dev`），核对与 Mac 侧 `results/e1_dev_revised` 一致；dev 的判定只是描述 | `python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split dev --out results/e1_dev --n-perm 10000 --n-boot 10000` | `results/e1_dev/inheritance_pooled.csv`、`e2_secondary_D.json`、`suggestibility_groups.csv`、`suggestibility_group_pairs.csv`、`base_control.csv`、`inheritance_partial*.csv`、`grid_permutation_partial.json`、`dose_response.json`、`e1_train_reproduction.csv`、`e1_contested.csv`、`summary.md` |
| 2 | 冻结 | 在 `tasks/hpc_log.md` 写一行"E1 / E2 规则冻结于 <commit>"（<commit> = 含本次更正的 main HEAD，e1_plan §9），之后不改 13 的任何默认值 | — |
| 3 | test | 同 1，`--split test --out results/e1`（先评 S_0 与全部 run 的 test，e1_plan §7 第 5 步） | 同上，`summary.md` 的 Verdicts 表就是结论；Reliability ceilings 段一起进论文 |
| 4 | 提交 | `git add results/e1_dev results/e1 tasks/hpc_log.md && git commit && git pull --rebase && git push` | Mac 侧写论文表 |

## 4. 怎么读结果

- Δρ 的尺度：teacher 两两 profile 相关在 test 上只有 0.25 到 0.35（残差 0.20 到 0.28），所以 Δρ 即便成立也可能只有 0.05 到 0.15；要和 seed-noise null 的 SD 一起报效应量。ΔρPartial 比 raw Δρ 更小（dev 上 mean 0.026）且只有 teacher 层面的精确 p（下限 1/6），只作描述；D 才是有 family 级推断的量（dev 0.10，null sd 0.02；特有部分 D_specific 0.14），它说的是矩阵的对角结构，不是"每个学生离自己 teacher 最近"；D_shared 为负说明 dev 上共享成分是在压低 D，但它的符号随数据变，所以守门看 D_specific。
- ρ 的天花板是 teacher 自己的可靠度，但上限是 sqrt(2r / (1 + r)) 不是 r：Claude 学生的 ρ(own) 在 test 上超不过 0.70，DeepSeek 0.80，GPT-4o 0.90；报 ρ / 上限。
- T0 是学生从未见过的问法：T0 上的 Δρ > 0 是"继承 disposition"最干净的证据；T1 到 T6 上的 Δρ 可能混有对 stem 措辞的记忆。
- 任何在 test 上"再试一种 readout 或阈值"的念头都违反预注册；想试就回 dev，并在 log 里写明。

## 5. 后续依赖

E3（F / C 学生）复用同一套量，比较 Δρ(S_{T,F / C}) − Δρ(S_{T,O})（seed 配对）；E7 的 provenance 用 ρ 做最近 teacher 分类。两者都要等 `data/rewrites_train/` 完成后重建 paired 的 O / F / C 文件再训。
