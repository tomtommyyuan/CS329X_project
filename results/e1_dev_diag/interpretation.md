<!-- Generated 2026-10-05 by a 25-agent analysis on the HPC side (4 analysts, 13 adversarial claim checks, 6 audits of new numbers, 1 synthesis). Everything is EXPLORATORY: dev split only, not pre-registered, no test file opened. Scripts and outputs: results/e1_dev_diag/wf/. Full record (analyses, verdicts, audits): interpretation_record.json. Citations outside docs/01 were found by web search and must be re-verified before use. -->

# 现在的 dev 结果意味着什么

以下所有新分析都是探索性的：只用了 dev，没有预注册，test 没有碰过。

## 1. 一句话结论

训练没有坏，学生确实学到了各自 teacher 的东西，但学到的很少，而且被基座先验盖住了。所以预注册的头条"不一致会遗传"（F1）在 dev 上不成立，照现规则跑 test 大概率也不成立。值得写成论文的是另外两件事：teacher 特有的信号能传多少、被什么挡住（F2），以及现有继承指标的几处系统性偏差（F3）。现在的结果够投 Findings，要冲 main 还要补两三个关键实验。

## 2. 结果到底说明了什么

### 已站住

| 结论 | 关键数字 |
|---|---|
| 训练和数据管线没有 bug | 15 个 SFT 文件的标签与 teacher demo 100% 一致；学生在训练 prompt 上复现自己 teacher 98.5–99.5%，在训练集的争议项上站自己 teacher 0.90–0.97。复现率这一项只核了 seed 1 |
| E1 失败是系统性的，不是 seed 运气 | gpt4o 学生对 GPT-4o 与对 DeepSeek 的 agreement 差，5 个 seed 全为负（−0.003 到 −0.014）；seed SD ≤ 0.008 |
| 主因是对未见题泛化弱，不是争议 cell 太少 | 未见 family 的争议 cell 上，学生站自己 teacher 只有 0.45–0.66（训练集上是 0.90–0.97）。如果学生站自己 teacher 的比例达到 90%，同样数量的争议 cell 下差距会是 0.072–0.117，E1 能稳过 |
| 学生带有 teacher 特有成分（按相对比较） | 在 A、B 两个 teacher 意见不同的 cell 上，A 的学生比 B 的学生更常站 A：三对分别约 +0.09、+0.14、+0.19，CI 都不含 0（gpt4o–claude 这一对的下界只有 0.003，勉强） |
| 未训练的基座 profile 最像 DeepSeek（描述层面） | 139 个 family 上，S_0 与 DeepSeek 相关 0.533，与 GPT-4o 0.277，与 Claude 0.245；去掉 framing 主效应后是 0.333 / 0.125 / 0.168，差距的 CI 不含 0 |
| 预注册 Δρ 的置换 null 不以 0 为中心，并且随 teacher 变 | null 均值：gpt4o −0.094，claude −0.090，DeepSeek +0.088（两套代码独立复算一致）。原因是置换保留了每个 teacher 的 T5 / T6 主效应 |
| 三个 teacher 在标签层面本来就很像 | 训练标签两两一致 93.3–95.8%；gpt4o 与 DeepSeek 只有 198/4,734 项不同 |

### 有条件成立

| 结论 | 数字 | 条件与保留意见 |
|---|---|---|
| 学生 × teacher 矩阵有对角结构：固定一个 teacher，最像它的是它自己的学生 | 交互（对角均值减非对角均值）0.090 [0.040, 0.140]，5/5 个 seed 为正；双中心化后的对角 0.060 [0.026, 0.092] | 只在训练见过的 framing 上成立；在未见的 T0 上是 0.026，p 0.20。分析员报告"8 个版本全过"，实际算了 15 个版本，没报的里面有两个是 T0 版本，都不显著。单看每一列，只有 Claude 稳定显著 |
| 学生的 suggestibility 排序是 DeepSeek > GPT-4o > Claude | 学生 0.174 / 0.123 / 0.052，两两 CI 都不含 0 | 这不等于从 teacher 继承，理由有四条：(1) dev 上 teacher 的 GPT-4o 与 Claude 分不开（差 +0.012 [−0.034, 0.057]）；(2) DeepSeek 学生基本等于基座（0.174 vs 0.168）；(3) 随机标签学生 R 也降到 0.001，所以"把 suggestibility 降下来"是任何 framing 信号弱的 SFT 都会做的事；(4) stable_one 过滤改变了每个 teacher 实际传给学生的 framing 信号。两位审查者在一点上意见不一：按 family 内的标签翻转算，过滤后训练标签的顺序是 G > D > C（0.050 / 0.038 / 0.013）；按边际算是 D > G > C。较稳的说法是：SFT 用训练标签里的 framing–标签关联，替换了基座自带的 suggestibility |
| 学生对 teacher 的 agreement 约 0.85，大部分是基座本来就有的 | S_0（放宽 0.9 阈值）与三个 teacher 的 agreement 已有 0.78–0.81；训练后对自己 teacher 只提高 +0.03 到 +0.07。扣除这部分后的"只对自己 teacher 的增益"：gpt4o 约 0，DeepSeek 约 0，Claude +0.035 [−0.006, 0.081] | 前提是放宽阈值读出的 S_0 可以当基座参照 |
| 基座先验能解释 DeepSeek 偏向 | 控制 S_0 后的 Δρ：gpt4o 从 −0.092 变成 +0.020，claude 从 −0.111 变成 −0.022，DeepSeek 从 +0.182 降到 +0.086，三者 CI 都含 0 | 基座是重要原因，但不是全部，还有三点：DeepSeek 是唯一概率呈渐变的 teacher，改用硬标签后 S_0 就不再特别像 DeepSeek（0.245 vs 0.187 / 0.225）；DeepSeek 与 GPT-4o 本身相关 0.432；S_0 在 0.9 规则下 75% malformed，以上全部是放宽规则测的 |
| JSD 偏向 DeepSeek，原因是 teacher 校准差异 | 什么都没学的 R 学生，JSD 对 DeepSeek 是 0.199，对另外两个是 0.276 / 0.290 | 做校准修正后，gpt4o 学生变成 5/5 通过，Claude 学生仍然不过，而且所有差值的 CI 都含 0。结论是 JSD 本身分不开这三个 teacher |

### 被推翻或证据不足

| 说法 | 问题在哪 |
|---|---|
| grid permutation p < 1e-4，说明学生更像自己的 teacher | 这是伪重复。同一 teacher 的 5 个 seed 几乎是复制品，真正可交换的单位只有 3 个 teacher，即 6 种指派。真实指派确实排第一，但精确 p = 1/6，这也是这个设计能给出的最小 p。论文里不能引用 1e-4 |
| 每个学生的 profile 最接近自己的 teacher（预注册的 RQ1） | 0/3 通过；控制基座后，所有 CI 都含 0 |
| T0（未见 framing）上有继承 | 交互 0.026，p 0.20；三个 teacher 彼此在 T0 上也只相关 0.08–0.17 |
| "teacher 太像，所以差异只是噪声" | 部分不对。差距在 seed 之间很稳定，主因是对未见题泛化弱加上基座先验，不是 seed 噪声 |
| R 学生的 ρ ≈ 0 就是零基准 | profile 相关的置换 null 本身是 0.07–0.15。R 只能当机会水平和校准的对照，控制不了基座先验 |
| 照现规则跑 test，最可能的结果是"RQ1 降为 exploratory" | 模拟显示最可能的是只有 DeepSeek 通过（约 0.70），对应 e2_plan 里"部分成立"那一行。P(≥2/3 通过) 约 0.01–0.02，原先报告的 0.046 偏高；把 dev 估计误差也算进去约 0.09。另外 E1 未过，S_0 的 Δρ 算不出来（NaN），所以严格按 plan，test 结果其实无法解释。scripts/13 遇到 1/3 也打印 "E2 FAIL"，不区分 partial 和 fail |

## 3. 对 ACL 投稿意味着什么

**F1 不能再当头条。** dev 上 E2 是 0/3。唯一接近通过的是 DeepSeek，而它恰好是基座最像的那个 teacher，控制基座后就不显著了。如果 test 上出现"只有 DeepSeek 通过"，审稿人会直接归因于基座。F1 应该作为未通过的预注册假设如实报告。

**最有希望的组合：F2 做主线，F3 作为其中的方法一节。**

- **F2 需要重新表述。** 建议的核心句：跨家族全量 SFT 之后，学生的 framing 敏感性主要由基座先验和训练数据里的 framing–标签关联决定；teacher 特有的逐题结构只有小幅、相对的传递（见过的 framing 上对角约 0.06–0.09，未见 framing 上测不到）。原先设想的"suggestibility 按 teacher 顺序遗传"现在撑不住，要等下文行动 4 的受控实验。
- **F3 是目前最稳的部分。** 本项目已经找到几处可以复用的偏差：
  - Δρ 的置换 null 随 teacher 偏移；
  - 基座先验让 Δρ 和 agreement 都偏向某一个 teacher；
  - JSD 偏向校准更温和的 teacher；
  - 按 15 个 run 做置换属于伪重复；
  - R 对照的零基准不是 0。

  这些对所有判断"学生像谁"的蒸馏、provenance 工作都有警示意义。F3 单独成文偏窄（Findings 或 workshop），放进 F2 里反而是加分项，能抵消"这只是个 null"的批评。
- **文献定位。** 以下出处是文献分析员检索到的，不在 docs/01 里，引用前要再核一遍：subliminal learning 在 teacher 与学生基座不同时不传递（Cloud et al., arXiv 2507.14805）；phantom transfer 表明低维 trait 可以跨家族传递（arXiv 2602.04899）；fine-tune 后的模型会回到预训练分布（Ji et al., arXiv 2406.06144）。我们的结果与这些都一致。"基座先验主导、teacher 特有结构几乎不传"这个组合，在约 25 次检索里没有找到先例，但这不是系统检索。

**main 还是 Findings，现实判断如下（分数来自审稿模拟）：**

| 情况 | 预估 |
|---|---|
| 现在以 F1 投稿 | Findings 都难（overall 约 2） |
| 现在以 F2 + F3 投稿，只有 dev 诊断 | Findings 下限（约 3） |
| 补上受控剂量实验、第二个基座家族、合规的 S_0 参照，并在 test 上给出等价界 | 有机会冲 main（约 3.5–4） |

## 4. 主要风险与审稿人会攻击的点

1. **"teacher 太像，null 反映的是数据而不是蒸馏。"** 训练标签一致 93–96%。需要用保留争议项的训练或剂量实验证明：有信号时，信号能传下去。
2. **"只有一个基座，又碰巧像 DeepSeek。"** 需要一个不同家族的第二个基座来回应。
3. **基座参照不合规。** S_0 在 0.9 规则下 75% malformed，目前所有"基座先验"的论证都建立在放宽规则上。
4. **事后改指标。** 新指标只要看起来是为挽救结果而选，就会被重罚。交互已经算了 15 个版本，只能冻结一个主统计量，并披露全部尝试过的版本。
5. **预注册文件之间互相冲突。**
   - 按 e1_plan，E1 未过会把 E3 也挡住。
   - docs/E0_results §9 把 suggestibility 当作 RQ1 的主形态，e2_plan §2 却用 cell 级 Δρ 做判定。

   这两点都需要 Mac 侧书面裁决。
6. **统计方面。**
   - 只有 3 个 teacher，teacher 层面的置换 p 最小只能到 1/6。
   - docs/04 §3 要求的 power 模拟没有找到记录。
   - 按 docs 里已有的 test 侧 teacher 可靠度（Claude 0.329、DeepSeek 0.466），E0 的"两个及以上 teacher 可靠度 < 0.5"门槛在 test 上会被触发。这个门槛原本是在 pilot 上使用的。
7. **只有 first-token readout，没有 open-ended 评估。**

## 5. 建议的下一步

**推荐：以 b 为主，同时守住 a 的纪律；c 只作补充，不作替代。**

- **不建议只做 a。** test 结果大概率落在"部分成立"或"无法解释"，等于用掉唯一一次 test，对论文的增量很小。
- **b 的做法：** 原 E2 规则保留为 primary，如实报告失败；在 dev 上冻结少量预先声明的次级指标；然后 test 只跑一次。这是 O 学生那次 test 最有信息量的用法。
- **c 不能替代 b。** 改训练或换基座会重置预注册。但少量受控重训恰恰是把 null 变成"有界、有机制解释的 null"的关键，应当作为新实验单独预注册。

**按性价比排序的行动：**

| # | 行动 | 资源 | 作用 |
|---|---|---|---|
| 1 | 在 hpc_log 写偏离说明，等 Mac 侧确认以下几件事：<br>• E1 门槛如何解释，是否放行 E3<br>• 只冻结一个次级主统计量。建议用 seed 合并 profile 的双中心化对角或交互，限见过的 framing，用 family bootstrap 给 CI；T0 版本作为预先声明的次级指标<br>• grid permutation 改报 teacher 层面的精确 p（最小 1/6）<br>• scripts/13 区分 partial 和 fail | 现有 checkpoint，CPU，几小时 | test 之前必须完成 |
| 2 | 在 dev 上补一份完整规则的 power 模拟：三个 teacher 联合重抽样、Holm、要求 Δ > 0；同时给出冻结后次级指标的 power | CPU，几分钟 | 补上 docs/04 §3 缺的记录。现有估计：原规则通过概率约 0.01–0.02；加上 Δ > 0 要求后 MDE80 为 gpt4o 0.044、claude 0.045、DeepSeek 0.198。交互的 MDE80 约 0.05–0.06，低于 dev 上的 0.09–0.10（正态近似，这一项未经审计） |
| 3 | 建一个合规的 S_0 参照：不放宽 0.9 规则，改用 few-shot 格式提示或采样读数。同时对 seed 2–5 跑训练 prompt 的 readout | 现有 checkpoint，GPU 评估、不训练，每个几分钟 | 让基座先验的论证站得住；排除 seed 特有的训练问题 |
| 4 | 受控剂量实验。第一步：每个 teacher 用 `order_policy both` 重训 1 个 seed，看 DeepSeek 学生会不会从约 0.17 降到 0.14 附近。第二步：chimeric 剂量反应，T5 / T6 的回答按 0 / 33 / 67 / 100% 的比例取自 DeepSeek | 新训练，起步 3 个 run，之后约 12–15 个，每个约 15 分钟 | 区分"从 teacher 继承"和"基座加过滤"；最有可能救回 F1 的受控版本 |
| 5 | consensus 对照学生：只用三个 teacher 意见一致的项训练 | 新训练，3–6 个 run | 得到"基座 + 格式 + 共识"的参照，teacher 特有的继承定义为相对它的偏移 |
| 6 | 换一个不同家族的第二个基座（具体型号选定前要核实） | 新训练，9–15 个 run | 决定能否冲 main：看 DeepSeek 偏向是否跟着基座走 |

交互分配还剩约 16 小时，1–3 可以全部做完，4 的第一步（3 个 run）也放得下。但 4–6 改变了训练，必须先作为新实验在 hpc_log 写明设计和判定规则，等 Mac 侧确认，不能塞进当前 E2 的 test。

**冻结纪律：**

- 指标、阈值、规则的任何改动，只能根据 dev 决定，写进 `tasks/hpc_log.md`（或 e0_plan），等 Mac 侧确认后再提交冻结 commit。E2 的决策规则属于 CLAUDE.md 列出的协议性常量。
- 原预注册规则的失败结果必须照实报告，新指标放在旁边，不能替换它。
- 冻结之后 test 只跑一次；看过 test 之后，不再改 readout、阈值或规则。
- 论文里披露所有尝试过的分析版本，包括交互的 15 个版本。

各分析的脚本和输出在 `results/e1_dev_diag/wf/` 下（例如 `quant/`、`claims_mapper/`、`ac_review/`、`verify_C*/`、`verify_Q*/`），官方 dev 结果在 `/hai/scratch/tomyyc/CS329X_project/results/e1_dev/`。
