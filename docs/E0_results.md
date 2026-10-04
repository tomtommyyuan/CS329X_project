# E0 结果记录

> 更新：2026-10-02。E0.1 到 E0.4 已完成（三个 teacher）；E0.5 标注表已导出待填；E0.6、E0.7 等 vLLM endpoint。
> 原始表：`results/e0/*.csv`，自动汇总：`results/e0/e0_summary.md`，日志：`results/e0/logs/`。

## 1. 设置

| 项 | 值 |
|---|---|
| Pilot | 100 个 two-action family（DD 60 + MC-high 30 + MC-low 10）+ 20 条 ValueConsistency 英文 U.S. 原题作拒答 probe |
| Prompt | T1 到 T4 × 2 种选项顺序 = 800，VC 20 × 2 = 40，共 840；T0 未生成（需 J） |
| demo mode | T = 0，全文，1 次 / prompt |
| profile mode | T = 1，截断 8 token；GPT 与 DeepSeek 读字母位置 top-20 logprobs（1 次 / prompt）；Claude 采样 k = 10 × 2 passes |
| Teacher | GPT-4.1 `gpt-4.1-2025-04-14`；Claude Sonnet 4.6 `claude-sonnet-4-6`（无 thinking，temperature 经 extra_body）；DeepSeek V4 Pro `deepseek-v4-pro`（thinking disabled） |
| 费用 | GPT-4.1 约 $1.0；Claude 约 $10.3；DeepSeek 约 $0.1 |

数据事实：DD 1,360 条中 486 条第三人称、15 条第一人称叙事，放入 `excluded`（可用 `03c` 转二人称后回收）；去重丢 1 条；splits：train 998（DD 516 + MC 482）、dev 150、test 300、pilot 120、sanity 676（MC low）、pool 190（VC）。

## 2. E0.1 答题率（demo）

| teacher | DD | MC | VC 争议题 | 备注 |
|---|---|---|---|---|
| GPT-4.1 | 99.6% | 100% | 100% | 2 条拒答，都是 dd_29454 的 T3（怀孕决定） |
| Claude 4.6 | 99.8% | 100% | 97.5% | 1 条 VC 枪控题拒绝站队 |
| DeepSeek V4 Pro | 100% | 100% | 100% | |

P1 成立。VC 子集拒答率远低于门槛，可以进 test 池。

## 3. E0.2 选项顺序

| teacher | 顺序稳定率（T=0） | order artifact mean abs(p_o1 − p_o2) | P(选 A) |
|---|---|---|---|
| GPT-4.1 | 96.0% | 0.041 | 0.498 |
| Claude 4.6 | 97.0% | 0.033 | 0.495 |
| DeepSeek V4 Pro | 86.0% | 0.132 | 0.440 |

DeepSeek 偏向后一个选项（recency），训练标签按 order-stable 过滤会丢 14%。Claude 用 A/B 字母时 artifact 很小，和 yes–no bias 论文在 yes/no 格式下的发现不同。

## 4. E0.3 framing 敏感性（profile，symmetrized，T1 到 T4）

Type effect δ(j)：三个 teacher × 四种 framing 共 12 个值，全部 |δ| ≤ 0.02，95% bootstrap CI 全含 0。最大的是 DeepSeek T3 = +0.018，CI [−0.004, 0.039]。**没有任何 framing 系统性地推动任何 teacher 的平均判断。**

| teacher | 中间概率 cell（0.05 < p < 0.95） | 两两 framing 翻转率 | 有翻转的 family | 跨 framing 平均 JSD | profile 可靠度（按顺序 split-half，SB 校正） | 跨 pass 重测 |
|---|---|---|---|---|---|---|
| GPT-4.1 | 6.3% | 0.041 | 8.2% | 0.019 | 0.405 | 不适用 |
| Claude 4.6 | 4.5% | 0.052 | 9.1% | 0.036 | 0.667 | 0.996 |
| DeepSeek V4 Pro | 38.3% | 0.072 | 13.0% | 0.020 | 0.668 | 不适用 |

翻转最多的 framing 对，三个 teacher 一致都是 T3 对 T4（第一人称求建议 vs 什么结果更好）：GPT 6.1%、Claude 8.1%、DeepSeek 13%。翻转最少的是 T1 对 T2。

## 5. E0.4 teacher 之间

| 对 | profile Pearson | profile Spearman | 多数判断一致率 | 翻转 family 重叠（Jaccard） |
|---|---|---|---|---|
| Claude × DeepSeek | 0.125 | 0.114 | 0.894 | 0.16 |
| Claude × GPT | 0.088 | 0.100 | 0.890 | 0.13 |
| DeepSeek × GPT | 0.094 | 0.168 | 0.880 | 0.11 |

平均判断方向也一致：三者在 MC 上都偏向守规则的 action1（p_x 0.74 到 0.86），在 DD 上都略偏 not_to_do（p_x 0.42 到 0.45）。

## 6. 结论

- **P1 成立**。
- **P2 部分成立**：family-level profile 对 Claude 和 DeepSeek 可靠（0.67）且三者彼此不同（相关 0.1 左右，翻的 family 不重叠）；但 type 主效应为零。teacher 的差别不在平均判断（一致率近 0.9），而在"哪些情境在哪种 framing 下翻"。
- **P3 经六轮迭代后成立（单一 AI 审计者）**：v1 严格层放过的改写里约 40% 被独立审计认定改了语气、条件或理由；逐轮修正改写提示、record 抽取和检查规则后，Claude 审计的四项全同通过率 F 93%、C 94%（§11），过 85% 门槛。待 Codex 复审同一张表算 κ，论文仍需人工抽样。
- 影响：heritability 只能在 family × framing 的 cell 级检验，学生要学的是情境与 framing 的交互，RQ1 难度上调、power 存疑；RQ2 和 RQ3 不受影响，建议作为主线；RQ4 依赖 RQ1。
- 可能原因：teacher 太强，或我们的四种 framing 太温和。前者已用更弱的 GPT 和 Claude 模型验证，**不成立**（见 §8）。

## 7. 待决定

- 03 文档 E0 门槛中的 "某 type 的 δ ≥ 0.05" 是否改为 "family-level profile 可靠度 ≥ 0.5 且两两相关 ≤ 0.8"，type 主效应降为报告项。
- 是否按 teacher 中间概率筛更 ambiguous 的 family 进 test 池，或加 alignment 更弱的 teacher。

## 8. 弱 teacher 检验：type 主效应为零不是因为 teacher 太强

同一 pilot 上加跑四个更弱或更旧的模型：GPT-4 `gpt-4-0613`（2023）、GPT-4o `gpt-4o-2024-08-06`、GPT-4o-mini `gpt-4o-mini-2024-07-18`、Claude Haiku 4.5 `claude-haiku-4-5-20251001`。费用约 $14（GPT-4 占 $9.4）。七个 teacher 合计约 $25.5。

| teacher | 拒答 DD / VC | 顺序稳定 | order artifact | P(选 A) | 中间概率 cell | 有翻转的 family | profile 可靠度（顺序 split-half） | 最大 abs δ(j) |
|---|---|---|---|---|---|---|---|---|
| GPT-4 (0613) | 3.1% / 10% | 96.2% | 0.050 | 0.484 | 11.4% | 5.2% | 0.543 | 0.017（T3，CI 含 0） |
| GPT-4o | 0 / 0 | 95.2% | 0.035 | 0.484 | 8.1% | 6.3% | 0.571 | 0.005 |
| GPT-4o-mini | 0 / 0 | 90.2% | 0.098 | 0.461 | 14.2% | 8.0% | 0.433 | 0.007 |
| GPT-4.1 | 0.4% / 0 | 96.0% | 0.041 | 0.498 | 6.3% | 8.2% | 0.405 | 0.010 |
| Claude Haiku 4.5 | 1.9% / 7.5% | 95.2% | 0.055 | 0.518 | 8.1% | 9.1% | 0.611（重测 0.931） | 0.012 |
| Claude Sonnet 4.6 | 0.2% / 2.5% | 97.0% | 0.033 | 0.495 | 4.5% | 9.1% | 0.667（重测 0.996） | 0.010 |
| DeepSeek V4 Pro | 0 / 0 | 86.0% | 0.132 | 0.440 | 38.3% | 13.0% | 0.668 | 0.018（T3，CI 含 0） |

发现：

- **28 个 δ(j) 值全部 |δ| ≤ 0.018，CI 全含 0。** 2023 年的 GPT-4、小模型 GPT-4o-mini 和 Haiku 4.5 与前沿模型一样，没有任何 framing 系统性地推动平均判断。"teacher 太强" 的解释被排除。
- 弱模型的区别体现在别处：更多拒答（GPT-4、Haiku）、更大的顺序 artifact 和位置偏好（GPT-4o-mini 0.098、P(选 A) 0.461）、更多中间概率；翻转 family 的比例并不更高（GPT-4 反而最低，5.2%）。
- family-level profile 在 7 个 teacher 中 5 个过 0.5 可靠度门槛（Claude 4.6、DeepSeek、Haiku、GPT-4o、GPT-4），GPT-4.1 与 GPT-4o-mini 不过。
- 21 对 teacher 的 profile 相关在 −0.01 到 0.33 之间（最高 DeepSeek × GPT-4o-mini 0.328），多数判断一致率 0.84 到 0.92。**同一家族内也不相关**：Sonnet 4.6 与 Haiku 4.5 相关 0.167，翻转的 family 17 个里只有 1 个重合。
- 翻转最多的 framing 对在 7 个 teacher 中 5 个是 T3 对 T4（第一人称求建议 vs 什么结果更好）。

对研究的含义：在这套温和的 framing 和日常困境上，aligned 聊天模型不存在 framing type 主效应，不论强弱、不论厂商。存在的是可靠且 teacher 特有的 family 级脆弱性（5% 到 13% 的 family，位置几乎互不重叠）。要让 RQ1 有 power，剩下的杠杆是题而不是 teacher：加入更强的 framing 类型（否定或极性框架，文献中效应最大的那种），或按 teacher 中间概率筛更 ambiguous 的 family。GPT 系 teacher 若保留，GPT-4o 的 profile 比 GPT-4.1 可靠（0.571 vs 0.405），可考虑替换，最终以 300 个 test family 上的可靠度为准。

## 9. Framing v2：极性问法产生了系统性效应

v2 把 T2 / T4 换成围绕"正向行动"的极性问法：T5 "Should you {act}?"、T6 "Should you not {act}?"，保留 T1、T3。坐标统一到正向行动，δ > 0 表示推向该行动。七个 teacher 全部重跑，约 $24.5；E0 累计 teacher 花费约 $50。原始表在 `results/e0_v2/`。

| teacher | δ(T1) | δ(T3) | δ(T5) | δ(T6) | suggestibility T5−T6 | 中间概率 cell | 有翻转的 family | 可靠度（顺序 split-half） | 跨 pass 重测 |
|---|---|---|---|---|---|---|---|---|---|
| Claude Sonnet 4.6 | +0.011 | +0.010 | +0.004 | −0.025 * | 0.030 | 4.3% | 9.1% | 0.357 | 0.997 |
| Claude Haiku 4.5 | +0.006 | −0.007 | +0.018 * | −0.017 * | 0.036 | 9.1% | 9.1% | 0.265 | 0.923 |
| DeepSeek V4 Pro | +0.023 * | +0.039 * | +0.048 * | −0.110 * | 0.158 | 43% | 26% | 0.627 | 不适用 |
| GPT-4.1 | +0.019 * | +0.011 | +0.026 * | −0.056 * | 0.082 | 8.8% | 11.2% | 0.579 | 不适用 |
| GPT-4 (0613) | +0.004 | +0.013 | +0.006 | −0.023 * | 0.029 | 13.8% | 7.2% | 0.504 | 不适用 |
| GPT-4o | +0.009 | +0.016 * | +0.020 * | −0.045 * | 0.065 | 8.8% | 9.3% | 0.726 | 不适用 |
| GPT-4o-mini | +0.029 * | +0.020 | +0.019 * | −0.069 * | 0.087 | 16% | 18% | 0.645 | 不适用 |

\* = 95% bootstrap CI 不含 0。答题率、顺序稳定率与 v1 基本一致（DeepSeek 顺序稳定 82.5%，artifact 0.165，位置偏好 0.437）。

发现：

- **T6（否定框架）对全部七个 teacher 都是系统性的、同方向的**：问 "Should you not do it?" 把每个模型推离该行动，CI 全不含 0。幅度过 0.05 门槛的是 DeepSeek（−0.110）、GPT-4o-mini（−0.069）、GPT-4.1（−0.056）；T5−T6 过 0.05 的还有 GPT-4o。T5（肯定框架）在 5 个 teacher 上系统性为正。
- **suggestibility 是 teacher 特有的，跨 5 倍**：DeepSeek 0.158 > 4o-mini 0.087 ≈ GPT-4.1 0.082 > GPT-4o 0.065 > Haiku 0.036 ≈ Sonnet 0.030 ≈ GPT-4 (2023) 0.029。它不随模型强弱单调：两个 Claude 和 2023 版 GPT-4 最不受问法影响，DeepSeek 最受影响。这更像训练谱系的特征，不是能力的特征。
- **可靠度**：顺序 split-half 5 / 7 过 0.5。两个 Claude 不过（0.357、0.265），但跨 pass 重测 0.997 / 0.923：Claude 的翻转是确定性的，却依赖选项顺序，同一 framing 只在一种顺序下翻。对 Claude 作 teacher，symmetrize 和 order-stable 过滤会去掉这些 cell。
- **区分性**：原始 profile 相关升到 0.01 到 0.53（GPT-4.1 × GPT-4o 0.53，DeepSeek × 4o-mini 0.50），因为 T6 把所有 teacher 推向同一方向。去掉各自 type 效应后的残差相关 −0.03 到 0.49：GPT 谱系与 DeepSeek 在相同的 family 上脆弱（GPT-4.1 × GPT-4o 0.49），Claude 与任何模型的残差相关 ≤ 0.27。多数判断一致率 0.81 到 0.93。全部远低于 0.8 门槛。
- 对比 v1：DeepSeek 翻转 family 从 13% 升到 26%，GPT-4o-mini 从 8% 到 18%，GPT-4.1 从 8.2% 到 11.2%；Claude 和 GPT-4o 基本不变。

**P2 结论（v2）：成立。** 系统性（T6 在所有 teacher 上同方向，幅度门槛 3 到 4 个 teacher 过）、可靠性（5 / 7）、区分性（幅度跨 5 倍，残差相关 ≤ 0.49）三条都满足。

对研究的含义：

- RQ1 有了明确、可学、有 power 的形态：**suggestibility 是否遗传**。学生在 teacher 的回答上训练（回答里嵌着 teacher 对问法极性的顺从程度），在未见 family 上测学生的 δ(T6)、δ(T5)，看是否跟随自己的 teacher，并且三个学生的排序是否复现三个 teacher 的排序。300 个 test family 下 δ 的 CI 半宽约 0.02 到 0.03，teacher 之间 0.03 到 0.11 的差距可检出。cell 级残差相关作为次级检验。
- 主研究的三个 teacher 恰好构成 suggestibility 梯度：DeepSeek V4 Pro（高，且 43% 中间概率）、GPT-4.1 或 GPT-4o（中；GPT-4o 可靠度 0.726 好于 GPT-4.1 的 0.579）、Claude Sonnet 4.6（低，翻转依赖顺序）。
- 训练与测试都改用 v2 framing（T1、T3、T5、T6，测试加 T0）。E0.5 的人工等价校验要对 T5 / T6 重做，v2 标注表已导出到 `data/annotation/v2/`。

## 10. E0.6 改写内容保持（P3）、T0、第三人称转换

服务：rewriter B = Together AI `meta-llama/Llama-3.3-70B-Instruct-Turbo`；judge J = Together `zai-org/GLM-5.3-Flash`（Zhipu 家族，与所有角色不重叠；Gemini key 无效、Together 上的 Gemma 只有 dedicated 部署）。严格层流程：J 抽 record → B 从 record 按 F / C 重写 → J 判 choice / 每条 reason 的 entailment / 无新增 reason / conditions / strength / register，失败重写一次。每个 teacher 从 v2 demo 回答里按 framing 分层抽 300 条。Together 总花费约 $3（含 T0 与第三人称转换）。

| teacher | 版本 | 保留 / 条 | 过滤率 | choice | reasons | conditions | strength | style | judge JSON 失败 | 原文 → 改写长度（词，中位数） |
|---|---|---|---|---|---|---|---|---|---|---|
| GPT-4o | F | 274 / 299 | 8% | 1.00 | 0.79 | 0.99 | 0.99 | 0.99 | 5 | 41 → 60 |
| GPT-4o | C | 296 / 299 | 1% | 1.00 | 0.93 | 1.00 | 0.97 | 0.98 | 5 | 41 → 55 |
| Claude 4.6 | F | 274 / 295 | 7% | 1.00 | 0.83 | 0.94 | 0.93 | 0.93 | 22 | 64 → 78 |
| Claude 4.6 | C | 269 / 295 | 9% | 1.00 | 0.78 | 0.91 | 0.90 | 0.90 | 36 | 64 → 71 |
| DeepSeek V4 Pro | F | 267 / 295 | 9% | 1.00 | 0.77 | 1.00 | 0.98 | 0.98 | 7 | 36 → 62 |
| DeepSeek V4 Pro | C | 289 / 295 | 2% | 1.00 | 0.94 | 0.99 | 0.98 | 0.99 | 4 | 36 → 55 |

检查列是按次（含重试）的通过率；record 抽取失败 GPT-4o 1 条、Claude 5 条、DeepSeek 5 条。

发现：

- **自动门槛全部通过**：过滤率 1% 到 9%，远低于 30%；choice 100% 保持。P3 的自动部分成立，人工部分待审（每 teacher 约 550 条审计表已导出到 `data/annotation/v2/rewrite_audit_*.csv`，门槛通过 ≥ 85%、κ ≥ 0.6）。
- **主要失败是"多加理由"**：正式版 F 被 judge 标出新增 reason 的次数 GPT-4o 70 次、DeepSeek 72 次、Claude 24 次；口语版少得多。B 在"写得正式"时倾向补一句原文没有的依据，这正是严格层要拦的隐性内容变化，也说明 v1 文档里"现实层改写会漂移"的担心是真的。
- **改写一律变长**：F 比原文长 20% 到 70%，C 长 10% 到 50%。E4 的长度匹配版本（F_len / C_len）有必要，否则 F 与 C 的差别混着长度差。
- Claude 的 judge JSON 失败明显多（22 / 36 次 vs 其他 4 到 7 次），它的 rationale 最长（64 词），GLM 的 reasoning 更容易挤占输出。pilot 里这些计为改写失败，Claude 的过滤率因此略偏高；代码已改为 judge 失败先重判一次再计失败。

**T0（Moore 式自由 rephrase）对 T1**：mean |p_T0 − p_T1| GPT-4o 0.061、Claude 0.069、DeepSeek 0.096；多数翻转率 7.1% / 8.0% / 10.0%；T0 答题率 100%。只换说法就能翻掉 7% 到 10% 的 family，和极性 framing 的翻转率同量级，可直接对照 Moore 的结论。

**第三人称转换（03c）**：502 条 DD 叙事中 495 条转为二人称并入 train，7 条多主体情境失败保留 excluded；train 池 1,493 family（DD 1,011 + MC 482）。人工抽检表 100 条已导出。

## 11. 独立审计（Codex）：自动 judge 放过了约 40% 有内容变化的改写

2026-10-03 收到一位独立 AI 审计者（OpenAI Codex agent）对四张表的完整标注，单人标注，无 κ。原始文件在 `data/annotation/v2/returned/`。

| 表 | 行数 | 结果 | 门槛 |
|---|---|---|---|
| 改写审计（全部 1,669 条 GLM 放过的改写，盲审） | 1,669 | 四项全同 F 60.5%、C 58.8%；choice 100%；register 识别 100% | ≥ 85%，**未过** |
| framing 等价 | 500 | same_decision 五种问法全部 100%；T0 有 9% 改动了情境事实，T1 / T3 / T5 / T6 为 0 | ≥ 95%，**通过** |
| T3 自动转换审核 | 100 | 96% 通过，4 条给了修正 | 通过 |
| 第三人称转换抽检 | 100 | 87% 忠实；失败是漏掉细节或新增"你亲眼看到"之类的观察者 | 可接受，情境对所有 teacher 共享，不构成 teacher 间混杂 |

改写失败的分解（1,669 条中 674 条）：strength 303、reasons 269、conditions 261（可重叠）。按 teacher：Claude C 只有 34.9% 通过、Claude F 57.7%，DeepSeek 约 70%，GPT-4o C 69.6%、F 52.6%。审计者是 OpenAI 家族，对 GPT-4o 并不宽松，Claude 的低通过率更可能来自它最长、hedge 最多的 rationale 被改写压缩。

诊断：

- **语气加强**是最大问题：strength 失败的 303 条里 91% 伴随 intensifier 增加（原文平均 0.28 个，改写 1.82 个："clearly"、"essential"、"must"、"necessity"）或 hedge 丢失（"may" 变 "puts"）。GLM 的 strength 标签 96% 都是 "clear"，太粗，等于没检查。
- **条件变事实**："If the student truly shows great potential" 改成 "given that"。
- **理由增删**：只有一条理由的 record 失败率 32%（改写补了第二条）；Claude 三四条理由的长 rationale 被省略其中一条。

这正是项目的核心命题在自家管线上的体现：文本层的自动内容检查会漏掉判断强度和适用条件的变化。处理：

1. 改写提示新增硬约束：理由数量与顺序一致、条件保持为条件、不加强语气词、不丢 hedge。
2. 检查端新增词汇级 intensifier / hedge 差分（规则，直接对应 91% 的 strength 失败），judge 新增 candidate_reasons、conditions_as_facts、intensifiers_added、hedges_removed 四个逐项列举字段，理由数量必须一致。
3. 在 pilot 的同一批 900 条上重跑严格层（`data/rewrites_v2/`），导出新的 300 行盲审表重新审计；目标通过率 ≥ 85%。预期过滤率会明显上升，这是严格层应付的代价，需报告。
4. T0 的 9% 事实改动：生成提示加 "不得增删任何细节"，对 test 集生成时启用。

**严格层 v3 重跑结果（同一批 300 条 / teacher，自动检查）**：

| teacher | 版本 | 保留 / 条 | 过滤率 | reasons | conditions | strength | style | 长度（词） |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | F | 269 / 300 | 10% | 0.96 | 0.96 | 0.87 | 1.00 | 41 → 47 |
| GPT-4o | C | 235 / 300 | 22% | 0.83 | 0.99 | 0.78 | 0.98 | 41 → 54 |
| Claude 4.6 | F | 265 / 300 | 12% | 0.95 | 0.96 | 0.87 | 1.00 | 64 → 73 |
| Claude 4.6 | C | 239 / 300 | 20% | 0.86 | 0.97 | 0.81 | 0.99 | 64 → 76 |
| DeepSeek V4 Pro | F | 267 / 299 | 11% | 0.90 | 0.95 | 0.93 | 1.00 | 35 → 46 |
| DeepSeek V4 Pro | C | 240 / 299 | 20% | 0.81 | 0.96 | 0.83 | 0.98 | 36 → 52 |

choice 全部 100%；judge JSON 失败 8 到 25 次 / teacher-版本（已计入失败，略高估过滤率）。过滤率 10% 到 22%，仍在 30% 门槛内；剩余失败主要是真实的 hedge 丢失（"consider"、"rather"、"might"）和理由增删。改写长度从 v1 的 +50% 降到 F +15%、C +30%。新的 300 行盲审表 `data/annotation/v2/rewrite_audit_blind_v3.csv` 待复审，门槛 ≥ 85%。

v3 盲审表先由 Claude Sonnet 4.6 作为第二审计者过了一遍（`scripts/08b_ai_audit.py`，与 Codex 不同家族）：四项全同 F 76.7%、C 56.7%；同一审计者看 v1 改写只有 F 21.3%、C 48.0%，所以 v3 是大幅改善但仍未到 85%。Claude 的评语指出剩余失败又是提示诱导的：条件规则里举例的 "as long as / provided that" 被改写器在原文无条件时凭空加上（甚至写出 "This choice is made without any conditions"）；口语版加了 "You're probably thinking…"、"You're better off…" 这类读者框架。v4 修法：条件指令按 record 有无条件分别给出、不再列举触发短语；明令不加读者框架句；词汇检查新增"原文无条件却出现条件标记"和"新增建议框架短语"两项。

**严格层 v4**（条件指令按 record 有无条件分别给出、禁读者框架句、口语指令重新平衡）在同一批 900 条上重跑，自动过滤率 F 8% 到 15%、C 18% 到 29%（Claude 的 C 版最高）。Claude 作为审计者看 v4 盲审表（300 行）：四项全同 **C 82.7%、F 77.3%**（v3 为 56.7% / 76.7%，v1 为 48.0% / 21.3%）；same_reasons 97%，same_conditions 83% 到 93%，same_strength 85% 到 86%，风格识别 98%。按 teacher：Claude 自己的改写最难通过（72% 到 76%），DeepSeek 80% 到 88%，GPT-4o 80% 到 84%。离 85% 门槛还差几个点；盲审表 `rewrite_audit_blind_v4.csv` 待 Codex 复审以算 κ。

| 版本迭代 | 变化 | 自动过滤率 F / C | Claude 审计四项全同 F / C |
|---|---|---|---|
| v1 | 原始严格层 | 8% / 1% | 21% / 48% |
| v3 | strength 作指令、词汇级 hedge / intensifier 差分、理由数一致 | 10% 到 12% / 20% 到 22% | 77% / 57% |
| v4 | 条件指令按 record 分情况、禁框架句、口语指令平衡 | 8% 到 15% / 18% 到 29% | 77% / 83% |
| v5 | concession 与 condition 分开抽取和保持、禁 "on the condition that / assuming" 重构、禁指令式开头 | 7% 到 8% / 19% 到 26% | **93%** / 81% |
| v6（只改 C） | 口语版明令"解释选择，不预测、不命令读者"；词汇检查加 gonna / going to / have to / need to | — / 13% 到 21% | — / **94%** |

v6 按 teacher（C 版）：Claude 98%、DeepSeek 94%、GPT-4o 90%。**最终严格层 = v5 的 F 提示 + v6 的 C 提示**（同一套代码），自动过滤率 F 7% 到 8%、C 13% 到 21%。合并的最终盲审表 `rewrite_audit_blind_final.csv`（F 取自 v5、C 取自 v6，各 teacher × 版本 50 条）供外部复审算 κ。

v5 按 teacher（Claude 审计，四项全同）：GPT-4o F 98% / C 76%，DeepSeek F 92% / C 88%，Claude F 88% / C 78%。**正式版 F 过 85% 门槛；口语版 C 81%，差在 strength（84%）**。v5 的 record 抽取失败升到 5 到 20 条 / teacher（concessions 字段让 GLM 的 reasoning 更长），已加倍预算重试。

v4 剩余失败几乎全在 record 带条件的 item 上：无条件 item 通过 92.9%，一个条件 64.6%，两个条件 58.1%。审计评语显示根因在 record 抽取：GLM 把让步 / 承认句（"While your situation is deeply unjust"、"the impulse is generous"）标成了 condition，改写器再按"保持为条件"的指令把它们改写成 "This choice depends on the condition that…"。v5：抽取时把 concession 和 condition 分开（新字段 concessions，要求以让步句保留），条件须保持原有语法角色、禁止 "on the condition that / assuming" 一类重构，口语版禁止 "you're gonna want to" 之类指令式开头，judge 增加 concessions_entailed。

严格层 v2 第一次重跑（GPT-4o）暴露了一个自己造成的 artifact：传给 B 的 record JSON 里有 `"strength": "clear"`，B 把这个标签原样写进了 40% 的改写（"it's a clear choice"、"the strength of this decision is clear"），被新的词汇检查全部拦下，C 版过滤率飙到 58%。修法：strength 不再以标签形式出现在 JSON 里，改为写作指令（"commit plainly without adding emphasis words"），并明令不得评论决定有多清楚；词汇检查里 "clear" 只在加强用法（"it is clear"、"a clear choice"）计数。重跑记为 v3。

**Codex 复审最终盲审表（2026-10-03）**：`rewrite_audit_blind_final.csv` 300 行，四项全同 **F 79.3% / C 71.3%**（Claude 审同一表 92.7% / 94.0%），两位审计者 κ = 0.22，分歧几乎全是单向的（Codex 更严）。Codex 的失败分类：情态词 / 强度变化 37（"can provide" → "provides"、"seek" → "can seek"、丢 "crucial"），省略细节 26，从句换了挂接对象 14，新增或回声短语 14，过程文字 / 格式 4。回头查 1,537 条保留池里的确有真缺陷：54 条回声了 C 风格指令里的例句 "keep everyone safe"（3.5%），2 条多段 Answer，3 条带 "Revised / as requested" 之类的过程文字，4 条长度超原文 2.5 倍，以及系统性地把让步句挪到句尾。判断：Codex 不是过严，是按字面执行 rubric；采纳 Codex 标准为门槛。

**严格层 v7（2026-10-03，按 Codex 标准重做）**。改动分三类：

1. 修真缺陷：风格指令不再举内容例句；规则过滤多段 Answer、过程文字、长度 > 2 倍、被 token 上限截断；改写提示要求条件 / 让步句挂在原句上、保留理由内部的具体细节。
2. 把 rubric 写死：情态词增删（含缩写展开后的 can / could / may / might / should / must / would / will / need to / have to）、强调词增删（important / crucial / necessary / essential …）一律算 strength 失败，词汇级对称差分 + judge 字段 `strength_changed`；少一个例子算 reasons 失败；从句换挂接对象算 conditions 失败。人类说明 `INSTRUCTIONS_rewrite_audit.md` 和 `08b` 的 AI 审计提示用同一套细则。
3. 流程：重试时把失败原因（精确到哪个词）反馈给改写器，最多 2 次重试，重试温度 0.5；GLM judge 预算 2000 → 4000 → 精简提示 4000 → 同家族 GLM-5.3 兜底（GLM-5.3-Flash 对少数样本会 reasoning 到上限不出 JSON）。

v7 冒烟（gpt4o 20 条，C 版）暴露了口语版的根本矛盾：Llama 3.3 70B 一旦被要求"像和朋友说话"，就会加义务句和口头禅（"you've got to"、"that's what you should do"、"that's because …"），四种提示写法都一样（整段改写 C 保留率 30% 到 50%）；而让它只做缩写 + 同义替换，GLM 又判 70% 为 formal。Together 上 Meta 家族只有 3.3 70B 可 serverless 调（Llama 4 Scout / 3.1 405B 都是 dedicated-only），Gemini key 仍无效，GLM 是 judge 家族、Qwen 是学生家族，换改写器不可行。决定：**C 重新定义为"平实口语"（plain spoken register）并用词汇规则把关**：所有可缩写短语必须缩写、不得出现正式连接词（however / therefore / moreover …）、不得出现指令里列出的正式词（assist / obtain / ensure / maintain …，专有名词除外），逐句改写（改写器没有加话的空间）；GLM 的 formal / conversational 判断只记录不把关。F 另加"无缩写"规则。

| v7 冒烟（20 条 / teacher） | GPT-4o F | GPT-4o C | Claude F | Claude C |
|---|---|---|---|---|
| 整段改写，v6 式 C 指令去掉例句 | 85% | 30% | — | — |
| 整段改写 + 原文可见 + 机械配方 C | 90% | 50% | 90% | 55% |
| 逐句改写 C，GLM 判 register | — | 55% | — | — |
| **逐句改写 C，词汇规则判 register（最终）** | — | **80%** | — | **70%** |

剩余 C 失败是真实的严格标准命中：加 "could" / "should"、"consider" 变 "try"、"perhaps" 变 "maybe"、Claude 长 rationale 被补一句。v7 全量（300 条 × 3 teacher × F / C）结果与双审计 κ 见下。

**v7 全量（300 条 / teacher，自动检查）与双 AI 审计（300 行盲审表 `rewrite_audit_blind_v7.csv`，每 teacher × 版本 50 条）**：

| teacher | 版本 | 保留 | 过滤率 | 平均尝试 | judge 无 JSON | 长度（词） | Claude 审四项全同 | GPT-5.5 审四项全同 |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | F | 241 / 299 | 19% | 1.52 | 3 | 41 → 45 | 80% | 58% |
| GPT-4o | C | 226 / 299 | 24% | 1.64 | 4 | 41 → 42 | 92% | 74% |
| Claude 4.6 | F | 243 / 299 | 19% | 1.52 | 1 | 65 → 67 | 78% | 56% |
| Claude 4.6 | C | 186 / 299 | 38% | 1.89 | 26 | 65 → 66 | 80% | 74% |
| DeepSeek V4 | F | 248 / 293 | 15% | 1.47 | 0 | 36 → 39 | 74% | 50% |
| DeepSeek V4 | C | 241 / 293 | 18% | 1.51 | 8 | 36 → 37 | 90% | 78% |
| 合计 | F | | | | | | **77.3%** | **54.7%** |
| 合计 | C | | | | | | **87.3%** | **75.3%** |

两位审计者的 κ：C 0.40、F 0.33（Codex 对最终表是 0.22）。GPT-5.5 作为 OpenAI 家族的自动第二审计者（`configs/models.yaml` 的 `auditor.gpt55`，reasoning 模型，不传 temperature）和 Codex 一样严，可以在不等人工跑 Codex 的情况下先算 κ。

v7 的新问题在 F：same_reasons 只有 Claude 83% / GPT-5.5 59%。两位审计者的评语里 F 的 reasons 失败大半是**去人称化**：F 指令要求"不直接称呼读者"，改写器把 "your brother" 改成 "the individual"、"you" 改成 "one"，而新细则把"针对某个人的说法泛化"算作 reasons 失败（GPT-5.5 的 62 条 F reasons 失败里 31 条是这个，Claude 11 条），其余是复述式新增（13 到 14 条）和漏细节（7 到 8 条）。这是我们自己的风格定义和 rubric 打架：**F 改为只管 register（无缩写、正式词汇、完整句），称呼对象（you / I）与原文完全一致**；已经符合正式语体的句子原样保留。C 的失败则是改写器越过词表做同义替换（"influence" → "help"、"violates" → "doesn't follow"、"talent" → "possible talent"）和偶尔把说明文字写进句子（"but doesn't become: …"）：词表改成封闭列表（"只替换这些词"），规则过滤加 "doesn't become / becomes: / -> / original:" 这类标记和 "doesn't it / isn't it / right?" 反问尾巴。Claude C 的 26 条 judge 无 JSON 几乎都是 ≥ 4 条理由带让步句的长 record；GLM-5.3 兜底用精简提示 6000 token 能救回 20 / 27，兜底改为精简提示。

v8 冒烟（F，20 条 / teacher）：GPT-4o 95%、Claude 95% 保留，register 100%。C 版的 v8 第一版因为句级提示里列出了情态词 / 强调词示例又被改写器回声（"essential"、"crucial" 各出现 11 次）而回退，句级提示改为不列任何实词。v8 C 版冒烟（同一批 40 条 / teacher，与 v7 全量在相同 item 上对比）：GPT-4o 31 / 40 保留（v7 全量同批 28 / 40），Claude 23 / 40（v7 全量 25 / 40）。Claude 的长 rationale 仍是最难的 cell：剩余失败里改写器自行加强调词（"crucial"、"essential"、"necessary"、"fundamental"）和加 "will / can" 占大半，提示词怎么写都在这个水平，判断已到 Llama 3.3 70B 的能力边界，不再调提示。v8 全量结果见下。

**v8 全量（300 条 / teacher）与双 AI 审计（盲审表 `rewrite_audit_blind_v8.csv`，每 teacher × 版本 50 条）**：

| teacher | 版本 | 保留 | 过滤率 | judge 无 JSON | Claude 审四项全同 | GPT-5.5 审四项全同 |
|---|---|---|---|---|---|---|
| GPT-4o | F | 267 / 299 | 11% | 0 | 98% | 96% |
| GPT-4o | C | 235 / 299 | 21% | 5 | 88% | 82% |
| Claude 4.6 | F | 259 / 299 | 13% | 0 | 94% | 90% |
| Claude 4.6 | C | 173 / 299 | 42% | 20 | 72% | 62% |
| DeepSeek V4 | F | 272 / 293 | 7% | 0 | 98% | 94% |
| DeepSeek V4 | C | 229 / 293 | 22% | 7 | 82% | 74% |
| 合计 | F | | | | **96.7%** | **93.3%** |
| 合计 | C | | | | **80.7%** | **72.7%** |

两位审计者都判通过的比例：F 91.3%、C 66.7%；κ：C 0.45，F 0.23（F 的 κ 低是因为两人几乎全判通过，基数效应，不是分歧）。

- **F 在 Codex 级标准下过门槛**（两位审计者都 ≥ 90%，过滤率 7% 到 13%）。残余失败：条件性让步 "even if" 改成事实性 "even though"、多加一个 "can"、Claude 长 rationale 漏一个从句。
- **C 不过**：Claude 80.7%、GPT-5.5 72.7%，Claude 自己的 C 版最差（72% / 62%），自动过滤率 42% 也超 30% 门槛。失败三类各占三分之一：词表外的同义替换（"encouraging" → "helping"、"exploring" → "showing"、"indefinitely" → "for too long"）；"While X, Y" 改成 "But X, Y" 把让步改成转折（配方里 whereas → while 的连接词替换被泛化）；逐句改写时塞进 "doesn't" / "so it's not worth it" 之类碎片。七轮提示迭代（v7 冒烟 1 到 7、v8 冒烟 1 到 3）里 C 的句级保留率一直在 55% 到 80% 之间波动，不同写法之间的差异与 20 到 40 条样本的噪声同量级，判断是 Llama 3.3 70B 的能力边界。

**Plan B 落地：B 换成 Gemini 3.8 Flash（2026-10-03）**。用户换了有计费的 Gemini key（免费档每模型每分钟 5 次，第一次冒烟全死在 429）。Google 已不向新用户提供 Gemini 2.5；3.8 Flash 在真实改写提示上无论怎么设都会先想约 300 个隐藏 token 且计入 max_tokens，所以改写预算下限设 2500。同一批 40 条 / teacher：

| B | 模式 | GPT-4o F | GPT-4o C | Claude F | Claude C |
|---|---|---|---|---|---|
| Llama 3.3 70B（v8） | F 整段、C 逐句 | 37 / 40 | 31 / 40 | 35 / 40 | 23 / 40 |
| Gemini 3.8 Flash | 整段 | **38 / 40** | **38 / 40** | **37 / 40** | **34 / 40** |
| Gemini 3.8 Flash | C 逐句 | — | 5 / 40 | — | 2 / 40（输出格式不同，不适用） |

Gemini 整段：judge 无 JSON 0，格式失败 0，每条平均 1.2 到 1.35 次尝试。保留的 C 版与原文 4-gram 重合 0.81 到 0.90，GLM 只把其中约三分之一判为 conversational：按"平实口语"的词汇定义它过了，但风格差异偏弱。正在同一批上试更强的口语指令（"像给朋友解释"，仍禁一切增删），看 Gemini 能否在不丢内容的前提下把 register 拉开。更强的口语指令（"像给朋友解释你的看法"，仍禁一切增删）在同一批 40 条上的结果：

| C 指令 | GPT-4o 保留 | Claude 保留 | 与原文 4-gram 重合 | GLM 判 conversational |
|---|---|---|---|---|
| 平实配方（词表替换） | 38 / 40 | 34 / 40 | 0.81 / 0.90 | 32% / 35% |
| 口语指令 | 38 / 40 | 34 / 40 | **0.32 / 0.23** | **100% / 94%** |

内容检查通过率一样，风格差异从"加几个缩写"变成真正的改写（"Standing up for someone who is being excluded" → "Sticking up for someone who's left out"）。剩余失败是真实命中：hedge 丢失（"consider"、"perhaps"）、强调词变化（"serious"、"significant"）。**决定：B = Gemini 3.8 Flash，两种风格都整段改写，C 用口语指令（词汇规则仍作底线）；Llama 3.3 70B 和平实配方降为备选（`06 --rewriter llama33_70b_together --c-instruction plain --sentence-mode-styles C`）。** v9 全量（300 条 × 3 teacher × F / C）与双审计见下。

**v9 全量（B = Gemini 3.8 Flash，整段，C 口语指令）与双 AI 审计（盲审表 `rewrite_audit_blind_v9.csv`，每 teacher × 版本 50 条）**：

| teacher | 版本 | 保留 | 过滤率 | judge 无 JSON | 长度（词） | 与原文 4-gram 重合 | Claude 审四项全同 | GPT-5.5 审四项全同 |
|---|---|---|---|---|---|---|---|---|
| GPT-4o | F | 279 / 299 | 7% | 0 | 42 → 42 | 0.83 | 96% | 92% |
| GPT-4o | C | 275 / 299 | 8% | 0 | 41 → 42 | 0.27 | 98% | 78% |
| Claude 4.6 | F | 274 / 299 | 8% | 0 | 65 → 65 | 0.80 | 98% | 90% |
| Claude 4.6 | C | 254 / 299 | 15% | 0 | 64 → 66 | 0.23 | 100% | 68% |
| DeepSeek V4 | F | 279 / 293 | 5% | 0 | 36 → 37 | 0.70 | 98% | 98% |
| DeepSeek V4 | C | 279 / 293 | 5% | 0 | 36 → 38 | 0.27 | 94% | 78% |
| 合计 | F | | | | | | **97.3%** | **93.3%** |
| 合计 | C | | | | | | **97.3%** | **74.7%** |

两位都判通过：F 93.3%、C 72.7%。κ：F 0.55，C ≈ 0（Claude 几乎全判过，GPT-5.5 判掉四分之一，没有一致性结构可言）。GLM 把 91% 到 96% 的保留 C 判为 conversational，F 全部 formal。

- **F 两位审计者都过 85%**，过滤率 5% 到 8%，judge 无 JSON 和格式失败归零（Gemini 不会出多段 Answer、过程文字或截断）。
- **C 在 Claude 眼里过（97%），在 GPT-5.5 眼里不过（75%）**。GPT-5.5 的 C 失败是真正改写的代价：按字面 rubric，"father's alcoholism" → "dad's drinking" 算泛化，"trust in the medical profession" → "trust in doctors" 算缩窄，"requires" → "needs" 算 strength 变化，"the precautionary principle" 这类专名被口语化算漏细节。这就是 register 强度和字面内容保持之间的根本张力：平实配方的 C（4-gram 重合 0.8 到 0.9）字面上更保险但风格差异弱；口语指令的 C（重合 0.23 到 0.27，GLM 判 conversational 90% 以上）风格差异真实但严格审计掉四分之一。两种 C 在同一批 40 条上的 GPT-5.5 严格审计对比见下一段。

**同一批保留的 C 改写（Gemini，GPT-4o 38 条 + Claude 34 条 = 72 条）送 GPT-5.5 严格审计**：

| C 指令 | 四项全同 | same_reasons | same_strength | GPT-5.5 认出是口语 | 与原文 4-gram 重合 |
|---|---|---|---|---|---|
| 平实配方（封闭词表） | **98.6%** | 100% | 100% | 75% | 0.81 / 0.90 |
| 口语指令 | 79.2% | 86% | 89% | 100% | 0.32 / 0.23 |

这把张力量化了：平实配方在严格标准下近乎无损，但四分之一的 C 连审计者都认不出是口语；口语指令风格真实，但严格审计掉五分之一。中间方案（`--c-instruction convlex`：口语句法 + 保留全部实词，只换封闭词表）在同一批上：GPT-4o 39 / 40、Claude 36 / 40 保留；GPT-5.5 严格审计 **92.0%**（GPT-4o 94.9%、Claude 88.9%），认出是口语 85%；但与原文 4-gram 重合 0.74 / 0.82，GLM 只把 49% / 36% 判为 conversational，Claude 的长 rationale 几乎只改了缩写。三种 C 定义的完整对比：

| C 定义 | GPT-5.5 严格审计 | 审计者认出是口语 | GLM 判 conversational | 与原文 4-gram 重合 | 自动过滤率（Claude teacher） |
|---|---|---|---|---|---|
| 平实配方 | 98.6% | 75% | 33% | 0.81 / 0.90 | 15% |
| 口语句法 + 保留实词 | 92.0% | 85% | 49% / 36% | 0.74 / 0.82 | 10% |
| 口语指令（v9 默认） | 79.2% | 100% | 100% / 94% | 0.32 / 0.23 | 15% |

结论：Gemini 已经把"B 能不能做到"的问题解决了（F 两位审计者都 ≥ 90%，judge / 格式失败归零）；剩下的是研究设计选择——C 要多"口语"。风格差异和字面内容保持是一条连续的权衡曲线，不是提示词能同时拿满的。建议主实验用口语指令（E3 的 form 操纵需要真实的风格差异），同时报告两位审计者的通过率并用双审计都通过的子集做敏感性分析；平实配方和中间方案保留为 `--c-instruction plain / convlex`，可作"最小风格差异"对照。待用户拍板。


原决定点（已由 plan B 解决，留档）：F 可以进主实验；C 有三条路：(a) 接受 C 在严格标准下约 75% 到 80% 并写进 limitation，用双审计都通过的子集训练；(b) 给 C 换改写器——Google 家族与所有角色都不重叠（Gemini 2.5 Flash / Pro，需要有效的 `GEMINI_API_KEY`），或在 HAIC 上自托管 Llama 4 Scout / Gemma 3 27B，预计 C 通过率能到 F 的水平；(c) 把 C 做成纯规则变换（代码做缩写、连接词和封闭词表替换），内容零风险但风格差异只剩表层标记。推荐 (b)，其次 (a)。

## 13. Phase 1：dev 集上的 teacher profile 复现了 pilot（2026-10-04）

Phase 1 采集中（`data/teacher_phase1/`，配置 `configs/phase1_dev.yaml` / `phase1_test.yaml`，`05_e0_analysis.py` 直接复用）。dev 150 个 family、T1 / T3 / T5 / T6 × 2 顺序，Claude 10 × 2 pass 采样（写到此处时完成 1,482 / 1,500 条）：

| teacher | δ(T5) | δ(T6) | suggestibility | 可靠度（顺序 split-half） | 跨 pass 重测 | 中间概率 cell | 位置偏置 P(A) |
|---|---|---|---|---|---|---|---|
| GPT-4o | 0.029 | −0.048 | 0.077 | 0.675 | — | 12.5% | 0.483 |
| Claude 4.6 | 0.019 | −0.037 | 0.056 | 0.383 | 0.993 | 8.0% | 0.507 |
| DeepSeek V4 | 0.060 | −0.081 | 0.140 | 0.515 | — | 42.4% | 0.440 |

与 pilot 一致：T6 对三个 teacher 都是同向负偏移（CI 不含 0），suggestibility 梯度 DeepSeek > GPT-4o > Claude（pilot 0.158 / 0.065 / 0.030），Claude 的翻转依赖选项顺序（顺序 split-half 低、跨 pass 重测 0.99），残差 profile 相关 0.17 到 0.34。P2 在未见过的 family 上成立，可以用作 E2 的 test 侧度量。GPT-4o 在 dev 上有 25 条拒答 + 21 条格式错误（3%），对应 10 个 family 进不了 profile。

## 12. 过程记录

- DeepSeek API 已不提供 V3；`deepseek-chat` 别名指向 `deepseek-flash`；改用 `deepseek-v4-pro`，它默认 thinking，200 token 全花在 reasoning 上导致空回答，已用 `thinking: disabled` 关闭。
- Parser 两处修补：弯引号的 "I can’t"；"not appropriate for me to take a side" 一类拒绝站队的表述。存量数据已用 `scripts/04b_reparse.py` 重算。
- 8 条早期 smoke 行属于后来被重新切分出 pilot 的 family，已清除。
- v1 的 DD 选项有 30% 以动名词开头（"Reading the journal" / "Do not reading the journal"），语法不对但模型照常作答；v2 前用 lemminflect 统一改成祈使句（421 个 family 受影响），pilot 切分不变。v1 结果按原文本记录，不重跑。
