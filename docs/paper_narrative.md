# 论文叙事与结构（2026-10-14）

> 怎么讲这个故事。数字以 `docs/story.md` 与各 results 目录为准，画图的精确文件与列见 `docs/figures_data_map.md`；实验清单与披露项见 `docs/supplemental_experiments.md`。本文件只定叙事、结构、图表与措辞边界。

## 1. 一句话主张与题目

**主张**：蒸馏传递的是 teacher 们的公约数；只有当示范来自 teacher 彼此不一致的题时，学生才继承某个 teacher 特有的判断倾向——这种继承随分歧比例单调、跨基座成立、穿过文风改写，而且是"倾向"而非"型号"：它让学生在理想候选集里可被溯源，却在含同家族兄弟的真实候选集里认不出具体是谁。

题目候选（选一个，或合成）：
- *Distillation Inherits Disagreement: When and What Students Learn from Their Teacher's Value Judgments*
- *Consensus Is Not Heritable: Teacher-Specific Value Judgments Transfer Only Through Contested Demonstrations*
- *What Survives Distillation: Tendencies, Not Models — Inheritance and Provenance of Value Judgments*

## 2. 摘要骨架（5 句）

1. 问题：aligned 模型在价值问题上的判断与不一致性是否会通过蒸馏传给学生，文风改写是否改变它，能否据此溯源。
2. 方法：三个闭源前沿 teacher × 可控的因子化训练集（原文 / 正式 / 口语；争议 / 共识 / 混合）× 两个开放基座学生，全部预注册、test 只跑一次。
3. 发现一：常规数据上什么都传不出来，因为 teacher 一致 93–96%；争议示范让学生继承 teacher 特有倾向，随争议比例单调，跨基座成立，代价是学生更不稳定。
4. 发现二：文风改写只扰动少数判断，继承原样穿过；学到的是系统性倾向而非逐题立场。
5. 发现三：这些倾向让黑盒溯源在 3 候选下可行且只需答案，但在含同家族兄弟的真实候选集下模型层面失效、真 teacher 缺席时会错指别家——检测应以家族与倾向为单位。

## 3. 贡献（4 条，按这个顺序）

| # | 贡献 | 支撑 |
|---|---|---|
| 1 | 一个可控的蒸馏 testbed：三 teacher、规则转换的争议题池、严格内容保持的改写层、两基座学生、预注册与冻结 test | §3 testbed；docs/02、E0 |
| 2 | "共识不可继承"：常规蒸馏传公约数，teacher 特有倾向只经分歧示范传递，且呈剂量反应；代价是不稳定 | E1 / E2 null + E2c + dose + base2 + K_n / Cnf |
| 3 | 继承的是系统性倾向：文风改写穿透、逐题立场不传、GPT-4o 居中无可继承信号 | E3 / E3c + 分解 |
| 4 | 真实条件下的溯源：3 选 1 上界、7 候选下界、缺席误告，词汇与行为两条渠道的分工 | E7 四个阶段 |

## 4. 叙事主线：从 null 到条件

写法是"**先给 null，再给条件**"，不是"我们发现了继承"。每一步的转折都有机制解释，这是整篇文章可信的来源。

| 步 | 节 | 论点 | 证据 | 图表 |
|---|---|---|---|---|
| 0 | 引言 | Moore et al. 的 puzzle（aligned 比 base 更不一致）无法解释，因为看不到数据；我们构造数据并因子化操纵 | — | 图 1：设计总图（teacher → 示范版本 → 学生 → 冻结 test） |
| 1 | teacher | 前沿模型几乎不拒答；中性换说法不动答案；极性问法系统性移动答案（7 家同号）；suggestibility 是 teacher 特有且与能力不单调；三家训练标签一致 93–96% | E0 v2、Phase 1 | 表 1：7 模型的极性效应与 suggestibility；图 2：teacher 标签一致矩阵 |
| 2 | 常规蒸馏 | 学生学会标签（≥ 0.98）却像所有 teacher，profile 继承未检出 | E1 / E2 | 表 2：own vs other agreement；E2 判定行 |
| 3 | 诊断 | 没有信号可传：这是 null 的原因，不是蒸馏无效 | E1 一致率 | 一段文字 |
| 4 | 争议示范 | 把"信号是否存在"做成变量：争议 C vs 共识 K，继承随之出现又消失；K_n / Cnf 排除规模与顺序噪音；剂量反应单调；第二基座复现 | E2c、robustness、dose、base2 | **图 3（主图）**：gap 随争议比例的四点曲线 × 3 teacher × 2 基座；表 3：E2c 判定与归因 |
| 5 | 机制 | 分解到"teacher 唱独角"的格子：DeepSeek 学生跟 83%、Claude 58%、GPT-4o 51%；学到的是系统性倾向 | 分解（补 `scripts/23`） | 图 4：按格子结构的跟随率 |
| 6 | 代价 | 争议训练让学生更不稳定，不是训练量造成（K_n），且随比例单调 | E2c / K_n / dose | 图 3 的第二面板：翻转率随比例 |
| 7 | 文风 | 原集 null 的解释（无信号可调节）；争议集上口语体扰动 1–2% 判断，继承原样穿过 | E3、E3c | 表 4：E3 vs E3c 的 13 + 1 行并排 |
| 8 | 溯源 | 3 选 1：有条件可行、只需答案、穿过改写；7 候选：兄弟抢第一名，模型层面失效；缺席：同家族替代正确，无家族时错指别家；词汇渠道更强但可被改写削弱 | E7 §7.3–7.6 | 图 5：召回 / 误报随候选集与探针数；表 5：缺席实验 |
| 9 | 讨论 | 对一致性 puzzle 的回答；对蒸馏检测争论的含义；限制 | — | — |

## 5. 每个"坏结果"的讲法

| 结果 | 不要写成 | 要写成 |
|---|---|---|
| E2 预注册 0/3 | "失败" | "常规示范里没有可继承的 teacher 特有信号，这是一个可解释、可复现的 null，并由 E2c 的操纵证实" |
| E2c PARTIAL（1/3 → Cnf 2/3） | "部分支持" | "效应小（约 3 个百分点）但方向一致、跨基座、随剂量单调；GPT-4o 的零是机制的一部分（居中、无系统性怪癖）" |
| E3 12/13 inconclusive | "没有效应" | "在有信号的争议集上也只测出口语体的小扰动，继承穿过改写；等价性因功效不足未确立" |
| 修订 1 / 2（epoch、步数） | 藏在附录 | 正文一句 + 附录表：争议标签更难学，训练预算按步数匹配；修订前已见 dev，test 未动 |
| E7 7 候选失效 | 删掉 | "现实下界：倾向被同家族共享，所以认得出家族认不出型号；缺席时的误告是检测器必须有拒判的理由" |
| 词汇 baseline 预测落空 | 删掉 | "改写抹掉正字法但不抹长度与论证词汇；两条渠道互补" |
| 基座先验像 DeepSeek（两个基座都是） | 不提 | 明写为最大混杂，C − K 配对差控制它，但 DeepSeek 最可继承与先验相像分不开 |

## 6. 不要 claim 的

- 不说"不一致性是可继承的"（profile 层面未检出）。
- 不说"可以检测蒸馏来源"；说"在候选集小且 teacher 有系统性倾向时可归属到家族层面"。
- 不说"文风无关"；说"未检出文风对继承的影响，口语体有小的判断扰动"。
- 不把 K_n / Cnf / 家族规则等事后分析写成确认性。
- 不用总准确率掩盖 teacher 间差异；溯源与继承都按 teacher 报。

## 7. 图表清单与数据来源（正文 5 图 5 表，其余附录）

| 图表 | 内容 | 数据 |
|---|---|---|
| 图 1 | 设计总图 | 手画 |
| 表 1 | 7 个 teacher 的极性效应、suggestibility、顺序稳定性 | results/e0_v2、results/phase1 |
| 图 2 | teacher 训练标签一致矩阵 + 争议率按来源 | data/teacher_phase1、results/e2c/screen_report.csv |
| 表 2 | E1 / E2：agreement 矩阵与判定 | results/e1 |
| **图 3** | gap 与翻转率随争议比例（0 / 0.25 / 0.5 / 1），3 teacher，Qwen 实线、SmolLM3 两端点 | results/dose、results/e2c、results/e2c_robust/Kn、results/base2 |
| 表 3 | E2c 判定、归因、K_n、Cnf、base2 | results/e2c*、results/base2 |
| 图 4 | 按格子结构的跟随率（唱独角 / 两家对一家 / 全同），3 teacher × C / K / E1 / E3c | `results/e2c/decomposition/test/`（`scripts/23_cell_decomposition.py`） |
| 表 4 | E3 vs E3c 的 13 + 1 行判定并排 | results/e3、results/e3c |
| 图 5 | 溯源：召回与误报随候选集（3 vs 7）与探针数；采样 readout | results/e7、results/e7_p2、e7_probe_curve.csv |
| 表 5 | 缺席实验 + 词汇 vs 行为（6 个生成学生） | results/e7_p2_drop_*、results/e7_lexical_students |
| 附录 | 训练曲线、改写保留率与审计、抽检轮次、全部修订与披露、register 可分性、家族层面探索 | runs/*/train_log.jsonl、data/rewrites_*、tasks/*_plan.md |

## 8. 术语表（全文统一）

| 术语 | 定义 | 别名禁用 |
|---|---|---|
| contested / consensus demonstrations（争议 / 共识示范） | 三 teacher 多数答案不同或某 teacher 不确定 / 三家一致且确定的题 | "hard / easy" |
| inheritance gap（继承 gap） | agree_own − max_other agree_other | "alignment" |
| suggestibility | δ(T5) − δ(T6)，对极性问法的敏感度 | "sycophancy" |
| K / K_n / Cnf / M25 / M50 | 共识对照 / 规模匹配共识 / 去顺序翻转项 / 25% 与 50% 混合 | — |
| register rewriting（文风改写） | 只改 register 的 F / C 版本 | "paraphrase" |
| provenance（溯源） | 黑盒行为归属到 teacher 或其家族 | "fingerprinting"（只在相关工作用） |

## 9. 限制与伦理（正文各一段）

限制：两个基座且先验都偏 DeepSeek；三 teacher 的推断单位小；效应约 3 个百分点；探针与训练同为道德困境两选项；AI 判官审计（真人抽检待补）；学生 checkpoint 已删。伦理：用闭源 API 输出做研究性蒸馏，不发布学生权重；teacher 输出以 id 与行为统计释放；溯源结论不构成任何实际的蒸馏指控。
