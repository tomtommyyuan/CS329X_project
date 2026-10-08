# E3c 预注册：争议集上的文风改写（Form modulation where a teacher-specific signal exists）

> 状态：**2026-10-07 写于任何 F / C run 存在之前**；改写（Mac 侧，付费）与本文件同日开始；**2026-10-08 改写完成、paired 文件已建；训练前把预算改为与 E2c-C 相同的步数（§1，仍在任何 F / C run 之前）；**修订 1（2026-10-08，§7）：deepseek_v4 的 F vs C register 门豁免并训练其 F / C，决定作出时未见任何 F / C 学生结果**。上游：[e3_plan](e3_plan.md) §2–§3（统计量与判定规则，原样复用）、[e2c_plan](e2c_plan.md) §4–§6、§12（争议集与其结果）、[docs/story.md](../docs/story.md) §6。付费 API 只在 Mac 侧。

## 0. 问题

E3 在原训练集上没有检出文风改写的任何效应（13 行判定 12 inconclusive、1 no effect），但那套训练集里 teacher 之间几乎没有可继承的特有信号（E1 标签一致 93–96%），所以 E3 等于在没有信号的地方测调节。E2c 证明争议集 C 上有信号（own > other，归因于争议性，K_n / Cnf 两轮 robustness 成立）。E3c 问：**在有信号的争议集上，只改 register（正式 F / 口语 C）的改写会不会改变 (a) 学生的判断与一致性（E3 的 13 行），(b) 学生对自己 teacher 判断倾向的继承（gap）？**

## 1. 输入

| 项 | 值 |
|---|---|
| 待改写的示范 | E2c-C 的 O 训练项：`data/sft_e2c/{teacher}_O_s1.jsonl` 的 prompt_id（gpt4o 4,964 / claude46 4,838 / deepseek_v4 2,497 = 12,299 条），示范文本取 `data/teacher_e2c/{teacher}_e2c_C_demo.jsonl`，prompt 取 `data/prompts/e2c_C_prompts.jsonl` |
| 改写层 | 与 E1 训练集改写**完全相同**：`scripts/06b_rewrite_train.py`，rewriter B = Gemini 3.8 Flash，judge J = GLM-5.3-Flash（fallback GLM-5.3），`configs/e0_v2.yaml`，F = register only、C = conversational wording（`STYLE_INSTRUCTIONS_CONV_C`），词汇层检查、反馈重试 2 次；输出 `data/rewrites_e2c/{teacher}/rewrites.jsonl` |
| 训练文件 | `10 --versions O,F,C --rewrites-dir data/rewrites_e2c --prompts data/prompts/e2c_C_prompts.jsonl --demos data/teacher_e2c/{t}_e2c_C_demo.jsonl --out-dir data/sft_e2c_paired`：paired（三版本同一 prompt 集 = F 与 C 都保留的项），`stable_one`、`order_seed` 不变；预期保留 85–95%。**实际（2026-10-08）**：F / C 都保留的项 gpt4o 4,527（91.2%）/ claude46 4,122（85.2%）/ deepseek_v4 2,228（89.2%）；单风格保留 F 94.7 / 92.5 / 92.7%，C 93.6 / 87.4 / 91.7%；record 抽取失败 24 / 51 / 16 项；6 个 worker 曾因 Gemini 对个别 Reddit 来源题返回空候选而崩溃，修复后续跑（f6e0fb2）。jsonl 不入库，meta + runs_{teacher}.txt 提交 |
| 学生 | 45 run：3 teacher × {O, F, C} × 5 seed，`STUDENT_SHORT=qwen3-4b-e2c-paired`，`CONFIG=configs/train_e2c_cnf.yaml`（9 epoch 上界）+ 每 teacher `--max-steps` 780 / 760 / 395（= 同 teacher E2c-C run 的步数，`data/sft_e2c_paired/max_steps.json`；修订 2 的步数匹配做法，O / F / C 三版本相同）。**训练前的调整**：paired 集比 C 小，5 epoch 只有 710 / 645 / 350 步，而 Cnf 的经验是 Claude 在 435 步时 E1a 0.94–0.95 过不了门；直接给与 C 相同的优化预算，也使 paired-O 与 E2c-C 可比 |
| 评估 | 冻结的 dev 150 / test 300 family；transformers fp32 readout，0.9 门；S_0 复用 `runs/qwen3-4b/base_B_s0/eval/` |

## 2. 训练门与预先写好的阶梯

| 门 | 规则 | 不过时 |
|---|---|---|
| E1a | 45 个 run 都复现自己训练目标字母 ≥ 0.95（F / C 的目标字母与 O 相同，内容检查会核对 100%） | 步数已预先匹配到 C（§1）；若仍有版本未过，如实报告，不再调整 |
| E1b | O run 的争议项上站自己 teacher（六对 ci_lo > 0.5） | 同上 |
| 内容 / register 检查（e3_plan §2 第 6 行） | 三版本 prompt 集与字母 100% 一致；F vs C register 可分性 ≥ 0.90（最近质心 LOO 与 logistic 10 折都要） | 可分性不足 → 改写无效，不训练 F / C。**实际**：gpt4o 0.9005 / 0.949、claude46 0.9007 / 0.954 过；deepseek_v4 **0.885 / 0.936**，最近质心一项未过 → 修订 1 豁免（§7） |

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

**(c) 描述项**：每版本的 gap 水平（agree_own、agree_other、gap 及 family bootstrap CI）由 `20` 的 `e3c_gap_by_teacher.csv` 给出（19 的 gap 只对 O 版本定义，`e2c_metrics.GAP_VERSION = 'O'`，不用于 F / C）；`19 --split test --c-glob "runs/qwen3-4b-e2c-paired/*_O_s*/eval/test_responses.jsonl" --out results/e3c/19_O` 只跑一次，给 paired-O 对 K（`runs/qwen3-4b-e2ck`）的归因，与 E2c-C 的归因并列；每版本 n_examples；改写保留率与 attempt 数（deepseek_v4 的 `rewrites.jsonl` 曾因崩溃续跑多出 428 行完全重复的 F 行，已去重，paired SFT 的 sha256 不变）；register 特征表。

## 4. 步骤

| # | 侧 | 做什么 | 验收 |
|---|---|---|---|
| 1 | Mac | 提交本文件；`06b` 改写三个 teacher（Gemini 日配额 5 个项目 × 10k，可一天内完成）；`10` 建 paired；提交 `data/rewrites_e2c/`、`data/sft_e2c_paired/*.meta.json` + runs.txt；`20` 在 E3 旧网格上冒烟后提交 | 保留率、三版本 n_examples 相同；20 的冒烟**已做**（2026-10-07，`runs/qwen3-4b-paired`）：dev / test 两行均 inconclusive（与 E3 一致），family 单位的 agree_own 与 results/e3* 的 run_scalars 逐 run 相同，cell 加权聚合与 `teacher_agreement` 相同；11 个单测 |
| 2 | HPC | 重建 45 个 SFT（sha256 对 meta）；S_0 复制到 `runs/qwen3-4b-e2c-paired/base_B_s0/eval/`；训练 45 run，每 teacher 一个 array：`STUDENT_SHORT=qwen3-4b-e2c-paired CONFIG=configs/train_e2c_cnf.yaml DATA_LIST=data/sft_e2c_paired/runs_{teacher}.txt EXTRA_ARGS="--max-steps {780|760|395}" sbatch --array=0-14%8 slurm/train.sbatch`；train readout 带 `--prompts data/prompts/e2c_C_prompts.jsonl`；dev readout | manifest：`steps` = 780 / 760 / 395、`num_epochs` 9、前缀 `qwen3-4b-e2c-paired.`、data_sha256 = meta |
| 3 | HPC | 13（`--sft-dir data/sft_e2c_paired --prompts-train data/prompts/e2c_C_prompts.jsonl`，对 O / F / C 全部 run 的 E1a）→ §2 的门；`15 --split dev --out results/e3c_dev`、`20 --split dev --out results/e3c_dev`（描述，看表齐不齐）；hpc_log 写冻结行 | 门过 |
| 4 | HPC | test readout 每 run 一次；`15 --split test --out results/e3c --frozen-commit <修订 1 的提交 hash>`、`20 --split test --out results/e3c --frozen-commit <同>`、`19` 一次（paired-O vs K，描述） | `results/e3c/summary.md`、`e3c_summary.md` |
| 5 | Mac | 论文表：E3（原集）vs E3c（争议集）的 13 + 1 行并排 | — |

## 5. 预算

| 项 | 量 | 费用 |
|---|---|---|
| Gemini 改写（2 风格 × 12,299 + 重试） | ≈ 30k 次 | ≈ $60–80 |
| GLM 抽取 + 判官 | ≈ 50k 次 | ≈ $30–50 |
| GPU | 45 run × 12–28 分钟 + 135 次 readout | ≈ 20 H100 小时 |

## 6. 披露

E3c 在看到 E2c（含 robustness）的 test 结果之后决定；统计量与规则是 E3 的冻结版本原样复用，新增的 gap 行在任何争议集 F / C run 存在之前写定于此（提交 hash 见 §4 步 4）。改写层与 E1 相同，审计结论沿用（F 过严格门，C 严格标准下 75–80%，见 docs/E0_results.md）；不再做新的人工审计，但报告保留率与 register 可分性。

## 7. 修订记录

### 修订 1（2026-10-08）：deepseek_v4 的 register 门豁免

| 项 | 内容 |
|---|---|
| 触发 | 训练前的内容 / register 检查（只读训练文件）：deepseek_v4 F vs C 最近质心 LOO 0.885（Wilson 0.875–0.895；差门槛 67 条），logistic 0.936；gpt4o / claude46 0.9005 / 0.9007 刚过（各多 4、5 条，CI 跨 0.90） |
| HPC 侧独立复核（hpc_log 2026-10-08，5 个只读 agent） | 阈值效应：三家从 E3 到 E3c 都降约 0.02，因争议集 O 示范本身正式词更少（无正式词比例 39–63% vs E3 15–36%），F / C 对比度整体变小；最近质心对短文本偏严，deepseek 的 rationale 最短（平均 32 词，62% 的 F 单句），同长度档内与 gpt4o 一样可分；来源构成、改写器、重试率解释不了差距；弯引号不计缩写不改变结论 |
| 决定（用户 2026-10-08 批准） | 豁免 deepseek_v4 的 register 门，训练其 F / C（10 run，`--max-steps 395`）；保留三 teacher 设计。15 / 20 的判定规则、n_required、参照 teacher、null 都不变 |
| 为什么不是别的 | 只用两个 teacher 判定要改 15 / 20 的 n_required 并丢掉 E2c 信号最强的 teacher；照冻结文字执行则所有判定行 pending；重做 deepseek 改写要再付费且 E3 时也只有 0.907，paired-O 集会变、已训的 5 个 O run 作废 |
| 决定时未见的 | 任何 F / C 学生的 dev / test 结果（HPC agent 把 dev readout 留在本地未提交、未查看；15 / 20 未跑） |
| 披露 | 论文的 E3c 结果表给 deepseek_v4 行加注"register 门以最近质心 0.885 未过，logistic 0.936 过，经披露豁免"；可分性门在三家都只是勉强或未过，说明争议集上 F / C 的文风对比弱于原集，解读效应时须一并说明 |

## 8. 结果（2026-10-08，test 一次，冻结 45f3d30；`results/e3c/`，过程与独立复核见 hpc_log）

| 项 | 结果 |
|---|---|
| 门 | E1a 45/45（最低 0.985）、E1b 6/6（最低 0.977）、内容检查 100%、register：gpt4o 0.9005 / 0.949、claude46 0.9007 / 0.954 过，deepseek_v4 0.885 / 0.936 按修订 1 豁免；O vs F 可分性只有 0.66–0.68（F 与原文接近），O vs C 0.80–0.82 |
| 15 的 13 行 | **2 effect**：分歧率 F vs C（超额 claude46 +0.007 / deepseek_v4 +0.019 / gpt4o +0.009，后两家超 q95，方向一致）、分歧率 O vs C（同样两家超 q95）；O vs F 三家 ≈ 0（−0.002 到 −0.005）→ 分歧全部来自口语体 C。其余 11 行（flip rate、跨 framing JSD、agreement、excess drift、ΔρPartial 的 F − O / C − O）inconclusive，0 no effect |
| 20 的 2 行 | gap F − O、gap C − O 均 inconclusive：claude46 −0.009（−2.6 null sd，CI 含 0）、deepseek_v4 +0.003 / +0.004、gpt4o +0.006 / −0.006；TOST 不可能过（family bootstrap CI 宽 0.011–0.030 > 等价界 0.007） |
| gap 水平（20） | deepseek_v4 O / F / C = 0.033 / 0.036 / 0.037（CI 均不含 0）；claude46 0.012 / 0.002 / 0.002；gpt4o −0.002 / 0.004 / −0.008 |
| 19_O | paired-O primary PASS 2/3（claude46 0.023、deepseek_v4 0.031），对 K 归因 1/3 |
| 复核的提醒 | effect 两行依赖 deepseek_v4（被豁免者，3.96 null sd）与 gpt4o（只超 q95 0.0011），单对 null 下只有 deepseek 过，primary 行 Holm p 0.285；test 上只有 deepseek_v4 的 O 学生有 CI 不含 0 的 own-teacher 信号；§3(b) 的 family 集措辞（"两侧 cell 都非平局"）代码按逐侧丢平局 cell 实现，严格读法下两行仍 inconclusive |
| 一句话 | 在有信号的争议集上，口语体改写让学生在约 1–2% 的未见 cell 上改答，正式体与原文无差；一致性、对 teacher 的漂移、own-teacher gap 都没有可检出的变化，deepseek 的 gap 原样穿过改写 |

