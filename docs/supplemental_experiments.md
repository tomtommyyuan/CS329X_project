# 距 ACL / EMNLP main 还差什么：评估与补充实验（2026-10-08）

> 结论：故事成形、证据链完整、预注册与披露齐全，但按 main 审稿标准还在 borderline。最大的洞是**单一学生基座**；补完下表的 1–4 项后有机会稳在 accept 区。所有数字以 `docs/story.md`、各 results 目录为准。

## 1. 现在的强项

- 可控的因子化设计（3 teacher × 示范版本 O / F / C × 争议 / 共识 × 文风），确认性结论全部预注册、冻结 hash、test 只跑一次，规则修订逐条披露（`tasks/e2_plan.md` §2、`e2c_plan.md` §12、`e3c_plan.md` §7、`e7_plan.md` §7）。
- 一个有解释的 null（常规数据：teacher 标签一致 93–96%，什么都传不出来）、一个干净的正结果（争议示范 → teacher 特有判断的继承，两轮 robustness 成立）、一个机制分解（继承的是系统性倾向而非逐题立场）、一个应用（黑盒溯源有条件可行、只需答案）。
- 副产品：7 个前沿模型的极性问法效应与 suggestibility 排序；改写器会偷改内容；AI 审计虚高；争议题训练的代价。

## 2. 审稿人会打的地方（按杀伤力）

| # | 攻击 | 现状 | 对策 |
|---|---|---|---|
| 1 | **只有一个学生基座**（Qwen3-4B-Base），且训练前就最像 DeepSeek，而最强的结果恰是 DeepSeek 的 | 各 plan 均列为最大局限 | **必补**：第二个基座家族（Llama-3.1-8B-Base 或 OLMo-2-7B；不用 Gemma，与改写器 Gemini 同家族）。至少 E2c-C / K 各 15 run + S_0；最好加 E1 原集 O 15 run。效应若在不像 DeepSeek 的基座上仍在，混杂即解 |
| 2 | 效应 ≈ 3 个百分点、PARTIAL、只有 3 个 teacher | 如实报，不靠加 seed 凑 PASS | 可选第 4 个 teacher（Mistral Large / Grok 一类；不能是 Qwen 或 Gemini 家族），示范 + 筛选约 $150、30 run |
| 3 | C vs K 只有两个点，没有"分歧越多继承越多"的曲线 | 未做 | **必补、便宜**：剂量反应，争议比例 25% / 50%（混 C 与 K 的 item，总规模与 C 相同），各 15 run |
| 4 | 所有"人工审计"实为 AI 判官 | 文档已写明 | **必补**：真人抽检——改写内容保持 100–200 条、规则转换 100 条，报与 AI 判官的 κ |
| 5 | 溯源候选只 3 家，负例全是 Qwen 学生，没有"真 teacher 不在候选集"的情形；词汇 vs 行为没在同一批学生上比 | E7 阶段 2 / 3 待批 | 阶段 2：加 GPT-4.1、GPT-4o-mini、GPT-4 0613、Haiku 4.5 的 dev / test profile（≈ $60–90）；阶段 3：重训少量学生专供生成（≈ 3 GPU 小时） |
| 6 | 只做两选项 + 首 token 概率 readout | E0.7 只验了后端一致性 | 第二基座或阶段 3 的生成学生上顺带做小规模开放式一致性检查；或把论文范围限定在 forced-choice |
| 7 | 相关工作缺模型指纹 / API 溯源、蒸馏检测争议、subliminal learning 的最新文献 | docs/01 偏旧 | 写作期补 |
| 8 | 伦理与 ToS：用闭源 API 输出训练其他模型 | 未讨论 | ethics statement：研究用途、不发布学生权重、teacher 输出只以 id + 行为统计释放 |

## 3. 补充实验的顺序与代价

| 顺序 | 实验 | GPU | API | 日历 | 产出 |
|---|---|---|---|---|---|
| 1 | 剂量反应：25% / 50% 争议混合，各 15 run（5 epoch 配方，`19` 的 gap 与归因） | ≈ 10 h | 0 | 1 天 | 曲线：gap 随争议比例 |
| 2 | 第二基座：gate run、模板与 readout 复核、S_0、E2c-C + K 30 run（+ E1 O 15 run） | ≈ 30–40 h | 0 | 3–4 天 | 主张 3 / 4 / 5 跨基座 |
| 3 | 真人抽检（改写 + 转换） | 0 | 0 | 数小时 | 可信的质量门 |
| 4 | 溯源阶段 2 + 3 | ≈ 3 h | $60–90 | 1–2 天 | 开集、同家族误判、词汇 vs 行为 |
| 5（可选） | 第 4 个 teacher 全链路（示范、筛选、E2c-C / K、E7） | ≈ 15 h | ≈ $150 | 3 天 | 2/3 → 3/4 |

1、2、4 可并行；HPC 排队是瓶颈。做完 1–4 的论点结构：常规蒸馏传公约数（null 有解释）→ 分歧示范才传 teacher 倾向，且随分歧比例单调 → 跨基座成立 → 文风只扰动不改继承 → 黑盒溯源可行且只需答案。

## 4. 论文图表的数据清单（全部在仓库里，除注明者）

| 可能的图 / 表 | 数据 | 位置 |
|---|---|---|
| 训练曲线（loss / lr / epoch，每 10 步） | 214 个 run 的 `train_log.jsonl`；用时、峰值显存、步数在 `train_manifest.json` | `runs/*/*/`（含归档 `*-3ep`、`*-5ep`、`pilot5`） |
| 学生 readout（train / dev / test，首 token 概率） | 每 run 的 `eval/{train,dev,test}_responses.jsonl` + summary | `runs/*/*/eval/`（214 个 run） |
| teacher 侧：极性问法效应、suggestibility、顺序稳定性（7 个模型） | E0 v2 pilot、Phase 1 dev / test | `results/e0_v2/`、`results/phase1/{dev,test}`、`data/teacher_v2/`、`data/teacher_phase1/` |
| teacher 标签一致矩阵（93–96%） | 训练示范 | `data/teacher_phase1/*_train_demo.jsonl`、`data/teacher_e2c/*` |
| E1 / E2：agreement 矩阵、Δρ、D、suggestibility 继承、seed null | `results/e1/`、`results/e1_dev/`、`results/e1_dev_diag/` |
| E2c：gap 与 CI、归因、robustness（K_n、Cnf）、按来源争议率、抽检轮次 | `results/e2c/`、`results/e2c_robust*/`、`results/e2c/screen_report.csv`、`handcheck_round*.md` |
| E3 / E3c：13 行判定、register 可分性、内容检查、gap 水平 | `results/e3*/`、`results/e3c*/` |
| E7：按网格 / teacher 的召回、探针预算曲线、采样 readout、LOGO、词汇 baseline | `results/e7/`、`results/e7_dev/`、`results/e7_lexical/` |
| 改写保留率与失败原因 | `data/rewrites_train/`、`data/rewrites_e2c/`、`results/e3*/content_check.csv` |
| GPU 用量 / 费用 | manifest 的 `wall_time_sec`、`peak_memory_gib`；API 费用在 `tasks/*_plan.md` 预算节与 `hpc_log` |

只在 HPC 或只在本地、不在 git 里的：学生 **checkpoint**（已全部删除，不可再生成文本）；SLURM 日志（`logs/`，gitignore）；HPC agent 的草稿脚本与中间表（`/hai/scratch/tomyyc/vcd_diag/`，其结论都抄进了 `tasks/hpc_log.md`）；SFT jsonl（gitignore，可由已提交的输入确定性重建）。

**缺的只有一项代码**：E2c 的格子结构分解（teacher "唱独角"的 cell 上学生的跟随率、按问法拆分）是在对话里临时算的，尚未落成脚本；写论文前补成 `scripts/23_cell_decomposition.py` 并把表写入 `results/e2c/decomposition/`。
