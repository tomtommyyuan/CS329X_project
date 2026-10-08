# E3c 预注册：争议集上的文风改写（Form modulation where a teacher-specific signal exists）

> 状态：**2026-10-07 写于任何 F / C run 存在之前**；改写（Mac 侧，付费）与本文件同日开始。上游：[e3_plan](e3_plan.md) §2–§3（统计量与判定规则，原样复用）、[e2c_plan](e2c_plan.md) §4–§6、§12（争议集与其结果）、[docs/story.md](../docs/story.md) §6。付费 API 只在 Mac 侧。

## 0. 问题

E3 在原训练集上没有检出文风改写的任何效应（13 行判定 12 inconclusive、1 no effect），但那套训练集里 teacher 之间几乎没有可继承的特有信号（E1 标签一致 93–96%），所以 E3 等于在没有信号的地方测调节。E2c 证明争议集 C 上有信号（own > other，归因于争议性，K_n / Cnf 两轮 robustness 成立）。E3c 问：**在有信号的争议集上，只改 register（正式 F / 口语 C）的改写会不会改变 (a) 学生的判断与一致性（E3 的 13 行），(b) 学生对自己 teacher 判断倾向的继承（gap）？**

## 1. 输入

| 项 | 值 |
|---|---|
| 待改写的示范 | E2c-C 的 O 训练项：`data/sft_e2c/{teacher}_O_s1.jsonl` 的 prompt_id（gpt4o 4,964 / claude46 4,838 / deepseek_v4 2,497 = 12,299 条），示范文本取 `data/teacher_e2c/{teacher}_e2c_C_demo.jsonl`，prompt 取 `data/prompts/e2c_C_prompts.jsonl` |
| 改写层 | 与 E1 训练集改写**完全相同**：`scripts/06b_rewrite_train.py`，rewriter B = Gemini 3.8 Flash，judge J = GLM-5.3-Flash（fallback GLM-5.3），`configs/e0_v2.yaml`，F = register only、C = conversational wording（`STYLE_INSTRUCTIONS_CONV_C`），词汇层检查、反馈重试 2 次；输出 `data/rewrites_e2c/{teacher}/rewrites.jsonl` |
| 训练文件 | `10 --versions O,F,C --rewrites-dir data/rewrites_e2c --prompts data/prompts/e2c_C_prompts.jsonl --demos data/teacher_e2c/{t}_e2c_C_demo.jsonl --out-dir data/sft_e2c_paired`：paired（三版本同一 prompt 集 = F 与 C 都保留的项），`stable_one`、`order_seed` 不变；预期保留 85–95%。jsonl 不入库，meta + runs.txt 提交 |
| 学生 | 45 run：3 teacher × {O, F, C} × 5 seed，`STUDENT_SHORT=qwen3-4b-e2c-paired`，`CONFIG=configs/train_e2c.yaml`（5 epoch，E2c 修订 1 的配方） |
| 评估 | 冻结的 dev 150 / test 300 family；transformers fp32 readout，0.9 门；S_0 复用 `runs/qwen3-4b/base_B_s0/eval/` |

## 2. 训练门与预先写好的阶梯

| 门 | 规则 | 不过时 |
|---|---|---|
| E1a | 45 个 run 都复现自己训练目标字母 ≥ 0.95（F / C 的目标字母与 O 相同，内容检查会核对 100%） | paired 集比 C 小，步数随之减少；若某 teacher 任一版本未过，则该 teacher 的 **O / F / C 三个版本一起**改为与其 E2c-C run 相同的步数（`--max-steps` 780 / 760 / 395，`configs/train_e2c_cnf.yaml` 的 9 epoch 上界，即修订 2 的做法）重训；只此一级，仍不过则如实报告 |
| E1b | O run 的争议项上站自己 teacher（六对 ci_lo > 0.5） | 同上 |
| 内容 / register 检查（e3_plan §2 第 6 行） | 三版本 prompt 集与字母 100% 一致；F vs C register 可分性 ≥ 0.90 | 可分性不足 → 改写无效，不训练 F / C |

## 3. 冻结的量与判定规则

**(a) E3 的 13 行原样复用**：`scripts/15_e3_analysis.py --student qwen3-4b-e2c-paired --sft-dir data/sft_e2c_paired --rewrites-dir data/rewrites_e2c`，统计量、seed-pair null 的尺度匹配、TOST、`e3_verdict` 全部按 e3_plan §2–§3，不改默认值。

**(b) 新增 1 个主行：gap 的 V − O（`scripts/20_e3c_gap.py`，`vcd.analysis.e3c_metrics`）**

| 项 | 定义 |
|---|---|
| 单位 | family |
| 每 run 每 family | d_f = agree_own_f − agree_other_f：该 family 的 (variant) cell 上，学生多数行动与自己 teacher 一致的比例，减去与**参照他家 teacher** 一致的比例；p_sym = 0.5 的 cell 不计 |
| 参照他家 teacher | 每个 teacher T 固定一个：与 T 的 **O** 学生（本网格，同 split）seed 均值 agreement 最高的另一家；O / F / C 共用；写入输出 |
| 统计量 | e3_metrics.paired_delta：每 (teacher, V ∈ {F, C}) 的 5 个 seed 配对差 mean_f d_f(V) − mean_f d_f(O) 的均值，family bootstrap 10,000 的 CI（同 teacher 各 seed 联动） |
| null | 同一 teacher 两个 O seed 的 mean_f d_f 之差（带符号），跨 teacher 合并 30 个；尺度匹配、df = 12、TOST 与 e3_plan §3 相同（`e3_verdict`） |
| 判定 | 两行：`gap F - O`、`gap C - O`；effect（≥ 2/3 teacher 超 q95 且同号）/ no effect（≥ 2/3 过 TOST）/ inconclusive / pending |
| family 集 | 每 teacher 一个集：该 teacher 所有 run（三版本）都完整的 family ∩ 两侧（自己 / 参照 teacher）cell 都非平局的 family；null、水平表、配对差共用 |
| 参照 teacher 平局 | 浮点完全相等时取字母序第一个并标 tie |
| 预测 | 无预设方向。**no effect** = 继承对 register 稳健（文风不携带判断信息）；**effect** = register 调节继承（方向与大小如实报）。两者都是可发表的回答；inconclusive 则报功效不足 |

**(c) 描述项**：`19 --split test --c-glob` 分别指向 O / F / C 的 run，给每版本的 gap_T 与对 K（`runs/qwen3-4b-e2ck`）的归因；每版本 n_examples；改写保留率与 attempt 数；register 特征表。

## 4. 步骤

| # | 侧 | 做什么 | 验收 |
|---|---|---|---|
| 1 | Mac | 提交本文件；`06b` 改写三个 teacher（Gemini 日配额 5 个项目 × 10k，可一天内完成）；`10` 建 paired；提交 `data/rewrites_e2c/`、`data/sft_e2c_paired/*.meta.json` + runs.txt；`20` 在 E3 旧网格上冒烟后提交 | 保留率、三版本 n_examples 相同；20 的冒烟**已做**（2026-10-07，`runs/qwen3-4b-paired`）：dev / test 两行均 inconclusive（与 E3 一致），family 单位的 agree_own 与 results/e3* 的 run_scalars 逐 run 相同，cell 加权聚合与 `teacher_agreement` 相同；11 个单测 |
| 2 | HPC | 重建 45 个 SFT（sha256 对 meta）；S_0 复制到 `runs/qwen3-4b-e2c-paired/base_B_s0/eval/`；训练 45 run（`DATA_LIST=data/sft_e2c_paired/runs.txt --array=0-44%8`）；train / dev readout | manifest：5 epoch、前缀 `qwen3-4b-e2c-paired.`、sha256 |
| 3 | HPC | 13（`--sft-dir data/sft_e2c_paired --prompts-train data/prompts/e2c_C_prompts.jsonl`，对 O / F / C 全部 run 的 E1a）→ §2 的门；`15 --split dev --out results/e3c_dev`、`20 --split dev --out results/e3c_dev`（描述，看表齐不齐）；hpc_log 写冻结行 | 门过 |
| 4 | HPC | test readout 每 run 一次；`15 --split test --out results/e3c --frozen-commit <本文件提交 hash>`、`20 --split test --out results/e3c --frozen-commit <同>`、`19` 三次（描述） | `results/e3c/summary.md`、`e3c_summary.md` |
| 5 | Mac | 论文表：E3（原集）vs E3c（争议集）的 13 + 1 行并排 | — |

## 5. 预算

| 项 | 量 | 费用 |
|---|---|---|
| Gemini 改写（2 风格 × 12,299 + 重试） | ≈ 30k 次 | ≈ $60–80 |
| GLM 抽取 + 判官 | ≈ 50k 次 | ≈ $30–50 |
| GPU | 45 run × 12–28 分钟 + 135 次 readout | ≈ 20 H100 小时 |

## 6. 披露

E3c 在看到 E2c（含 robustness）的 test 结果之后决定；统计量与规则是 E3 的冻结版本原样复用，新增的 gap 行在任何争议集 F / C run 存在之前写定于此（提交 hash 见 §4 步 4）。改写层与 E1 相同，审计结论沿用（F 过严格门，C 严格标准下 75–80%，见 docs/E0_results.md）；不再做新的人工审计，但报告保留率与 register 可分性。
