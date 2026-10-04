# Related Work 与 Research Questions

> 项目：**Is Inconsistency Heritable? 风格改写蒸馏下的价值判断一致性**。状态 planning，2026-10-02。目标 ACL / EMNLP main。
> 其余文档：[02 模型与数据](02_models_and_datasets.md)、[03 实验](03_experiments.md)、[04 指标](04_eval_metrics.md)。

## 1. 一段话

Moore et al. 发现 aligned 模型在价值问题上比 base 模型更不一致，但解释不了原因，因为看不到 fine-tuning 数据。我们自己构造 fine-tuning 数据并做因子化操纵：多个 teacher 在 typed framings 下作答，rewriter B 保持判断只改 style，训练 student，再在从未见过的题上测：student 是否继承了 teacher "在哪种 framing 下容易翻转" 的模式，改写 answer 的 style 会不会改变这种继承。正负结果都有意义，并且设计自带机制检验和 fix。

## 2. Anchor：Moore, Deshpande & Yang (Findings EMNLP 2024, arXiv 2407.02996)

- 做法：4 种 consistency（paraphrase、同 topic 相关问题、MC vs open-ended、四语言）；约 8k 题、300+ topics，题目与 paraphrase 全由 GPT-4 生成、MTurk 校验；MC 读 option-token logprob；指标是各回答分布到 JS centroid 的平均 JSD。
- 发现：整体相对一致；controversial topic 更不一致；**base 比 aligned 更一致且均匀**，aligned 模型 "inconsistently inconsistent"。
- 没解决的，原话："Why are fine-tuned models less consistently consistent than base models? The models we investigated did not have open fine-tuning data we could analyze—future work might home in on this question with fully open models."
- 我们看到的第二个限制：他们的 paraphrase 是 GPT-4 "rephrase so that it asks the same thing" 的自由改写，没有类型。于是 inconsistency 只是每题一个标量，说不出哪类措辞在推动模型，也说不出两个同样不一致的模型是否在同样的地方不一致。我们用 typed framings 把标量变成 profile，这是 "继承" 可检验的前提。

## 3. 已有工作确立了什么、还缺什么

### 3.1 价值判断的一致性与 framing 敏感性

| 工作 | 确立了 |
|---|---|
| Scherrer et al. 2023, MoralChoice (NeurIPS) | question template 与选项顺序改变道德选择；不一致集中在 high-ambiguity 场景 |
| Röttger et al. 2024 (ACL) | forced-choice 在 paraphrase 下不稳，且与 open-ended 结果不同 |
| Sclar et al. 2024, FormatSpread (ICLR) | 纯格式变化就能造成大波动，不限于价值题 |
| Framing Instability, arXiv 2601.21433 (2026) | 否定 framing 的敏感性是**系统性、有方向的**，不是随机噪声 |
| Contextual MoralChoice, arXiv 2603.23114 (2026) | typed context 变化系统性移动 22 个模型的判断；base case 对齐不等于敏感性对齐 |
| Shen et al. 2025 (EMNLP); SaGE 2024; Cheung et al. 2025 (PNAS) | 测量方法影响测到的价值；问卷值与情境行为相关弱；LLM 的 yes-no / omission bias 比人强 |

缺口：全是对已部署模型的观察。没人问 framing 敏感性从哪来、是否是从示范数据学来的 trait、会不会随蒸馏传给下一个模型。

### 3.2 Readout artifact 还是真实判断变化

| 工作 | 确立了 |
|---|---|
| Yes–no bias, arXiv 2607.05552 (2026) | crossed symmetrization 后，yes-no bias 分解为 recency bias、对 "no" 的词汇吸引和 label 效应；Claude 系列 artifact 大，GPT / Gemini 几乎没有 |

缺口：symmetrize 之后的残余敏感性是否可遗传；teacher 带 order artifact 的标签进入训练后 artifact 是否被学走。两者都是我们的设计约束。

### 3.3 SFT 数据的 form 改变行为

| 工作 | 确立了 |
|---|---|
| LIMA 2023; URIAL 2024 | alignment 主要教 style 和 format |
| SDFT, Yang et al. (ACL 2024) | 把 SFT response 改写进模型自身分布再训练会改变下游行为；content 保持只在文本层检查 |
| When Style Breaks Safety, Xiao et al. (ICLR 2026) | 在带某 style 的数据上 fine-tune，对同 style 的 jailbreak 更脆弱；style-matched safety 数据可修复 |
| Betley et al. 2025 Emergent Misalignment (ICML); Qi et al. 2024 (ICLR) | 不含显式价值的 fine-tune 数据改变 broad values / safety |
| Shahid et al. (CHI 2026) | LLM "constructive" 改写系统性削弱 Conservative values、抬高 Benevolence / Universalism |

缺口：以上只回答 "行为变不变"，且多在 safety。没人拆开**变的是什么**（判断、一致性、还是敏感性结构）；没人分开 teacher 来源与 rewriter 来源；没人检验文本层 content-preservation 能否预测下游行为保持。

### 3.4 蒸馏中的 trait 传递与来源归因

| 工作 | 确立了 |
|---|---|
| Subliminal Learning, Cloud et al. 2025 (arXiv 2507.14805)；steering-vector 解释 arXiv 2606.00995 | 学生从语义无关的数据继承 teacher trait；**teacher 与 student 不同 base 时不发生**，机制是 steering vector |
| Who Taught You That? (ACL 2025) | 用 PoS template 等词汇特征能从学生输出识别 teacher |
| arXiv 2512.20908；Antidistillation Fingerprinting arXiv 2602.03812 | 白盒句级 provenance；主动设计能穿过蒸馏的 fingerprint |
| Chakraborty et al. (EMNLP 2025) | 结构化道德推理可以蒸馏给小模型 |

对我们的含义：teacher 闭源且与 student 不同家族，subliminal 那条共享初始化的通道不存在，任何继承只能来自示范数据里可学的规律，比同家族设定更干净。

缺口：行为层 disposition（framing 敏感性 profile）能否穿过抹掉词汇痕迹的改写；是否存在黑盒、仅行为的 provenance 信号；蒸馏学生是否继承 teacher 的**不一致**而不只是判断。

### 3.5 同名不同题

VC-Soup (arXiv 2603.18113) 的 "value consistency" 指多目标 RM 的 cross-value coherence；reasoning 里的 self-consistency 指采样一致。论文里要明确定义我们的术语。

## 4. Gap map（粗体是我们的）

| 问题 | 状态 |
|---|---|
| 价值回答跨 paraphrase 一致吗 | 已答：大体一致，有系统例外 |
| 测到的不一致有多少是 readout artifact | 已答：相当一部分，必须 symmetrize |
| framing 敏感性按类型系统吗 | 部分：否定与 context 类型有证据；meaning-preserving framing types 跨大量题目没有 |
| post-training 降低并打乱一致性吗 | 已答（观察） |
| **为什么？训练数据的哪个性质？** | **open，Moore 原文的 limitation** |
| SFT 数据 style 改变行为吗 | 已答（safety / 通用） |
| **变的是判断、一致性还是敏感性结构？文本层 content 保持能否保证行为保持？** | **open** |
| 学生继承 teacher trait 吗 | 已答：同家族内是 |
| **跨家族、在未见题上，学生继承 teacher 的 framing 敏感性 profile 吗？** | **open** |
| 能从学生识别 teacher 吗 | 已答：词汇特征 |
| **改写抹掉词汇痕迹后，行为层 provenance 还在吗？** | **open** |

## 5. Research questions

定义 r_M(i,j) = p_M(选 X ∣ family i, framing j) − 该 family 跨 framing 的均值，选项顺序 symmetrize 后计算。r_M 的全体是 M 的 **sensitivity profile**。

- **RQ1 Heritability**：在训练未见的 family 上，corr(r_S_A, r_A) > corr(r_S_A, r_A') 吗？
- **RQ2 Data origin**：固定 teacher，用它 "跨 framing 一致" 的示范训出的学生，是否比用 "不一致" 示范训出的更一致？
- **RQ3 Form modulation**：B 保持判断、理由、条件，只改 register（formal F / conversational C）后，学生的 (a) 未见题判断、(b) 一致性、(c) 继承强度是否超出 seed noise 地改变？机制是 H1 register 与问题 framing 的交互、H2 长度改变决策 token 的有效 loss 权重、还是 H3 与 student 预训练分布的距离？
- **RQ4 Provenance**：继承的 profile 在改写后是否仍能识别 teacher，且胜过 PoS / 词汇 baseline？

前提（E0 先验）：P1 teacher 肯答；P2 teacher 的 type profile 系统、可重复、彼此不同；P3 B 能通过严格内容保持检查。P2 不成立则 RQ1 / RQ4 降级，RQ2 / RQ3 仍可做。

## 6. Contributions 与结果解读

| 贡献 | 依赖 |
|---|---|
| C1 首个受控、可操纵的证据：价值不一致是否通过蒸馏遗传，直接回答 Moore 的 open question | RQ1, RQ2 |
| C2 typed-framing 一致性 benchmark + 前沿模型的敏感性 profile | P2 |
| C3 拆开 answer 风格改写改变了学生的什么，以及文本层检查能否发现；对 data-rewriting pipeline 直接相关 | RQ3 |
| C4 机制（H1 到 H3 之一）+ 不同质化不同 teacher 的 fix | RQ3 |
| C5 穿过 style laundering 的行为 provenance 信号 | RQ1, RQ4 |

| 结果 | 能说 | 不能说 |
|---|---|---|
| profile 系统且被继承 | 不一致是示范数据的可遗传 trait；给 Moore 的 base-vs-aligned gap 一个机制 | 内部 "价值观" 变了；任何真实模型的来源被识别 |
| profile 系统但不被继承 | 学生的不一致是自己的，teacher 特有的脆弱性不经 SFT 传递 | 其他规模或目标下也不传 |
| form 改变一致性但不改判断 | "学到同样的选择" 不等于 "以同样稳定性做选择"；content 检查漏掉它 | 任何改写都不安全 |
| 无 form 效应 | 在声明的 power 和 tolerance 内，严格 style 改写行为安全 | 超出 tolerance 的等价 |

最没价值的结果是 "B 悄悄改了结论，学生跟着改"：Shahid et al. 已蕴含，只作 baseline。

## 7. 不 claim

不给任何道德选择打 "正确"；测的是受控 readout 下的选择行为，不是内部价值；provenance 只在封闭候选集内成立；null 结果以 power 和 tolerance 为界。

## 8. References

- Moore, Deshpande, Yang. Are LLMs Consistent over Value-laden Questions? Findings EMNLP 2024. https://arxiv.org/abs/2407.02996
- Scherrer et al. Evaluating the Moral Beliefs Encoded in LLMs. NeurIPS 2023. https://arxiv.org/abs/2307.14324
- Röttger et al. Political Compass or Spinning Arrow? ACL 2024. https://arxiv.org/abs/2402.16786
- Sclar et al. FormatSpread. ICLR 2024. https://arxiv.org/abs/2310.11324
- Bonagiri et al. SaGE. LREC-COLING 2024. https://arxiv.org/abs/2402.13709
- Shen et al. Revisiting LLM Value Probing Strategies. EMNLP 2025. https://arxiv.org/abs/2507.13490
- Cheung, Maier, Lieder. Amplified cognitive biases in moral decision-making. PNAS 2025. https://www.pnas.org/doi/10.1073/pnas.2412015122
- Framing Instability in LLM Ethical Stance. arXiv 2026. https://arxiv.org/abs/2601.21433
- On the Context Sensitivity of LLM Moral Judgment. arXiv 2026. https://arxiv.org/abs/2603.23114
- The yes–no bias of LLMs reflects answer order and wording. arXiv 2026. https://arxiv.org/abs/2607.05552
- Zhou et al. LIMA. NeurIPS 2023. https://arxiv.org/abs/2305.11206 ；Lin et al. URIAL. ICLR 2024. https://arxiv.org/abs/2312.01552
- Yang et al. Self-Distillation Bridges Distribution Gap. ACL 2024. https://arxiv.org/abs/2402.13669
- Xiao et al. When Style Breaks Safety. ICLR 2026. https://arxiv.org/abs/2506.07452
- Qi et al. Fine-tuning Aligned LMs Compromises Safety. ICLR 2024. https://arxiv.org/abs/2310.03693
- Betley et al. Emergent Misalignment. ICML 2025. https://arxiv.org/abs/2502.17424
- Shahid, Zhang, Vashistha. LLMs Homogenize Values in Constructive Arguments. CHI 2026. https://arxiv.org/abs/2509.10637
- Cloud et al. Subliminal Learning. 2025. https://arxiv.org/abs/2507.14805 ；Subliminal Learning Is Steering Vector Distillation. 2026. https://arxiv.org/abs/2606.00995
- Who Taught You That? ACL 2025. https://arxiv.org/abs/2502.06659
- Where Did This Sentence Come From? 2025. https://arxiv.org/abs/2512.20908 ；Antidistillation Fingerprinting. 2026. https://arxiv.org/abs/2602.03812
- Chakraborty, Wang, Jurgens. Structured Moral Reasoning in LMs. EMNLP 2025. https://arxiv.org/abs/2506.14948
- VC-Soup. 2026. https://arxiv.org/abs/2603.18113
- Russo et al. The Pluralistic Moral Gap. EACL 2026. https://arxiv.org/abs/2507.17216 ；Chiu et al. DailyDilemmas. ICLR 2025. https://arxiv.org/abs/2410.02683
