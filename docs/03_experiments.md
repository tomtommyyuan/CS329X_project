# 实验

> 其余文档：[01 Related work](01_related_work.md)、[02 模型与数据](02_models_and_datasets.md)、[04 指标](04_eval_metrics.md)。
> 记号：teacher A / A' / A''；rewriter B；student S（默认 Qwen3-4B-Base）；S_{T,V} = 用 teacher T 的 V 版本训练的学生；一个 run = 一次从 base 出发的 SFT。指标定义见 04。

## 0. 总表

| ID | 问题 | 对比 | 新 run | 数据 | 主指标 | 决策规则 |
|---|---|---|---|---|---|---|
| E0 前提 pilot | teacher 肯答吗？profile 系统、可重复、彼此不同吗？B 能保持内容吗？ | A / A' / A''；F / C vs O | 0 | Pilot；300 条改写审计 | 拒答率；type 效应与 reliability；teacher profile 相关；内容保持通过率 | §1 门槛；决定 RQ1 是否仍是 headline |
| E1 蒸馏基线 | 学生学到 teacher 判断了吗？seed noise 多大？ | S_{T,O} × 3 teacher；随机标签学生 | 15 + 3 | Train-O；Test | teacher agreement；JSD；seed-noise null | 与自己 teacher 的 agreement 不高于与其他 teacher，先修训练 |
| E2 Heritability（headline） | 未见 family 上，学生 profile 更像自己的 teacher 吗？ | 复用 E1 | 0 | Test | Δρ = ρ(own) − max ρ(other)；按 type 分解；permutation p | ≥ 2 / 3 teacher 上 Δρ > 0 且 p < 0.05，且不局限于单一 type |
| E2b 不一致的来源 | 学生一致性随示范一致性变化吗？ | 同 teacher 的 O 数据按 teacher 跨 type 一致性分 tercile，取两端等量 | 18 | Train-O 子集；Test | flip rate；JSD；dose-response | 不一致示范训出的学生更不一致且超 seed null，teacher agreement 不变 |
| E3 Form 调节 | answer 风格改变判断、一致性、继承吗？ | S_{T,O} vs S_{T,F} vs S_{T,C}；可选 R_F / R_C | 30 + 可选 9 | Train-O / F / C；Test | 跨学生分歧率；Δ 一致性；Δ 继承；excess teacher drift；homogenization | 效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；R 有而 F / C 无则归因于隐性内容变化 |
| E4 机制 | H1 / H2 / H3 哪个解释 E3？ | F_len / C_len；O_rev；S_0 对训练文本的 perplexity | 27 | Train 变体；Test | 控制后效应是否消失；perplexity 与结果的相关 | §5 裁决表 |
| E5 Fix | 能恢复一致性而不同质化不同 teacher 的学生吗？ | S_{T,M}；按 E4 结论选的 F* | 9 + 9 | Train-M / F*；Test | 一致性恢复比例；teacher 可区分度 | 填回 ≥ 50% gap；teacher agreement 在 S_{T,O} 的 seed null 内；可区分度保持 |
| E6 稳健性与特异性 | 效应是 readout artifact 吗？是 value 特有吗？ | 同 checkpoint 换 readout；open-ended；事实 control 学生 | 9 | Test；100 family open-ended；control set | 各 readout 下效应保持；MC 与 open-ended 一致；value vs factual | 只在一种 readout 下出现，报告为测量效应 |
| E7 Provenance | 改写后 profile 还能识别 teacher 吗？胜过词汇 baseline 吗？ | 行为最近邻 vs PoS / n-gram baseline；leave-one-style-out | 0 | Test | 学生级准确率 + Wilson CI；margin | 只 claim 信号，不 claim 审计系统 |
| E8 Scale | E2 / E3 在 1.7B、8B 成立吗？ | {A, A'} × {O, F, C} × 3 seeds | 18 + 18 | 同上 | 同 E2 / E3 | 方向一致即支持；8B 反转先查清 |

## 0.1 核心网格与 run 数

核心网格 = 3 teacher × {O, F, C} × 5 seeds = 45。同一行共用 family、teacher 选择和每 seed 的 family 顺序；横向看 form，纵向看 teacher。

| Phase | 内容 | runs | GPU-h |
|---|---|---|---|
| 1 | 核心网格 + 随机标签 | 48 | 19 |
| 2 | E2b 18、E4 27、E5 18、E6 9、E3 可选 9 | 81 | 32 |
| 3 | E8：1.7B 18、8B 18 | 36 | 59 |
| 合计 | | 165 | 约 110 |

最小版本：核心网格 3 seeds、无 A''、无 E8，约 60 runs。

## 0.2 顺序

E0 不过不训练 → Phase 1 在 dev 上冻结阈值和 readout，再跑一次 test → Phase 2（E5 的 F* 等 E4 结果后选）→ Phase 3 → 写作从 Phase 1 的 test 结果开始。

## 1. E0（不训练）

| 子项 | 测什么 | 数据 / 模型 |
|---|---|---|
| 答题率 | 拒答、insufficient、malformed，按 teacher / type / 来源数据集 | Pilot，每 teacher 1,000 prompts，T = 0 |
| 顺序稳定 | 两种顺序选同一行动的比例 | 同上 |
| Type profile | symmetrized p(X)、r_T(i,j)、δ_T(j)、split-half reliability、两次独立采样的 reliability | k = 10 或 logprobs |
| Teacher 差异 | 两两 corr(r_T, r_T') | 同上 |
| Framing 等价 | 人工判 T0 到 T4 问同一决定 | 300 family × 5，两人 |
| 改写保持 | choice / reasons / conditions / strength / style，丢弃率 | 300 × {F, C}，J + 两人 |
| Readout 校验 | 开源模型的 first-token logit 与采样频率是否一致 | 1,000 prompts |

| 结果 | 决定 |
|---|---|
| 任一 teacher 拒答 + insufficient > 25% | 去掉 controversial 题，只留日常困境，重测 |
| 没有 type 的均值 shift ≥ 0.05，或 ≥ 2 个 teacher 的 reliability < 0.5 | P2 不成立：RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5 |
| 任两 teacher profile corr > 0.9 | 换 teacher：alignment 更少的开源模型，或同模型不同配置，称 "source configuration" |
| 人工通过 < 85% 或丢弃 > 30% | 换 B 或收紧 record → text 的 prompt |
| logit 与采样差 > 0.05 | 学生也改用采样 |

## 2. E1

15 个 S_{T,O} 加 3 个随机标签学生（同 prompt，均衡随机字母 + 模板 rationale，标定 "只学格式" 长什么样）。seed-noise null = 同条件 seed 两两之差的分布，后面所有比较都对着它。随机标签学生会因处处 50/50 而显得 "一致"，所以一致性永远与 agreement、分布指标一起报。

## 3. E2

复用 E1 checkpoint。对每个学生算 ρ(own)、ρ(other)、Δρ；按 type 分解；T0（未见 framing）vs T1 到 T4（见过的 type）。permutation：打乱学生的 teacher 归属与 family 标签各 10,000 次；family bootstrap 给 CI。r 在 family 内去均值，平均判断相似不会伪装成 profile 相似，E2 不是 E1 的复述。

## 4. E2b

按 teacher 在训练 family 上 T1 到 T4 的不一致程度排序，取上下 tercile 各约 490 family，等量，从 O 数据建两套训练集，3 seeds × 3 teacher × 2 = 18。混杂检查：两组的 topic 分布，必要时按 topic 分层重取。

## 5. E3 与 E4

E3 分三阶段测：改写前（teacher profile）、改写后训练前（对实际训练文件做内容检查，不只审计样本）、训练后。第二阶段有变化 = 内容漂移；第二阶段干净而第三阶段有变化 = 学习结果不保持。

E4 裁决表（预注册）：

| 观察 | 支持 |
|---|---|
| 长度匹配后 E3 效应消失，效应大小随 rationale 长度 | H2 |
| 长度匹配后仍在，且集中在 T3 / T2 | H1 |
| S_0 对训练文本的 perplexity 预测各 cell 的一致性与 agreement | H3 |
| 决策位置独立于 style 改变一致性 | 训练与 readout 的对齐本身是因素，作为方法学发现报告 |

## 6. E5

M 是 H1 下的自然 fix。F* 按 E4 结论：H2 → 长度匹配或决策 token loss 加权；H3 → 每 teacher 选 S_0 perplexity 最低的 register（SDFT 思路）。验收：一致性 gap 填回 ≥ 50%、teacher agreement 不降、S_{A,·} 与 S_{A',·} 的距离保持在 E1 区间。靠同质化换一致性算失败。

## 7. E6 / E7 / E8

- E6：翻转顺序、中性 label、改答题指令三种 readout 重算 E2 / E3；100 test family × T1、T3 做 open-ended，J 标 stance，人工抽 600；事实 control 学生 9 个；在 T0 子集报 Moore 的 D-D divergence 以便对照。
- E7：对每个 checkpoint 用平均判断、profile、合并、PoS 词汇四种特征做最近 teacher，单位是 checkpoint，Wilson CI；leave-one-style-out；资源允许加一个 held-out rewriter。
- E8：{A, A'} × {O, F, C} × 3 seeds，在 1.7B 和 8B（8B 用 2×H100）。

## 8. 固定协议

- 训练：同 base、同超参、同 template；同 seed 下 O / F / C 同 family 顺序；loss 只算 assistant token；记录训练 token 数。
- 学生 readout：assistant 前缀 `Answer:`，取两个选项字母上的下一 token 分布归一化，两种顺序平均；记录无限制 top-1 以检测 malformed。O_rev 与 open-ended 用生成 + 解析。
- 预注册：framing stems、改写阈值、readout、null 构造、E2 决策规则在任何 test 评估前冻结；E4 裁决表、E5 验收在 Phase 2 前冻结。
- 永不：family 跨 train / test；看 test 后选 readout；单独报一致性；拒答当均匀分布。
