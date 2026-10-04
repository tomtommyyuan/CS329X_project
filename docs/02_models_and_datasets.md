# 模型与数据

> 其余文档：[01 Related work](01_related_work.md)、[03 实验](03_experiments.md)、[04 指标](04_eval_metrics.md)。模型 id、价格、数据规模核对于 2026-10-02。

## 1. 模型：六个角色，六个家族互不重叠

| 角色 | 模型 | 为什么 |
|---|---|---|
| Teacher A | GPT-4o `gpt-4o-2024-08-06`（E0 后由 GPT-4.1 换成，profile 可靠度 0.726 vs 0.579，suggestibility 相近） | 前沿 aligned；有 logprobs，option 概率直接读；readout artifact 小 |
| Teacher A' | Claude Sonnet 4.6 `claude-sonnet-4-6` | 另一家前沿 aligned；无 logprobs，靠 k 次采样估分布；可关 thinking、可调 temperature（5.x 系列不允许）；order artifact 大，训练标签必须 symmetrize |
| Teacher A''（推荐，可选） | DeepSeek V4 Pro `deepseek-v4-pro`（2026-10 起 API 不再提供 V3） | 第三个 lab、开放权重谱系、便宜；提高 P2 成立概率，给 provenance 三个候选。fallback `google/gemma-3-27b-it` |
| Rewriter B | `gemini-3.8-flash`（Google，Gemini API，thinking 关、max_tokens 下限 2500）；备选 `meta-llama/Llama-3.3-70B-Instruct-Turbo`（Together） | Google 家族与 teacher（OpenAI / Anthropic / DeepSeek）、judge（Zhipu）、student（Qwen）都不重叠；2026-10-03 冒烟：同一批 40 条上 F 38 / 37、C 38 / 34 保留，Llama 的 C 只有 31 / 23。代价是闭源模型，复现靠记录全部请求 |
| Student S | `Qwen/Qwen3-4B-Base` 主；1.7B / 8B 做 scale | base 模型，价值相关监督全部来自我们的数据；4B 单卡 H100 全参 SFT |
| Judge J | Gemini Flash，Google 的 OpenAI 兼容端点（备选：Gemma-3-27B 自托管） | 抽取结构化 record、判 entailment、标 open-ended stance、生成 T0、第三人称转换；Google 不在任何其他角色里，所以与 teacher（含 Claude）无家族重叠；人工审计抽样是最终裁决 |

协议相关的几点：每个 teacher 固定一个 snapshot，记录全部请求；Claude 的分布用 k = 20（test）/ 10（其他）次采样；学生全参 SFT、3 epochs，所有条件共用 base、超参、template，同一 seed 下 O / F / C 用同一 family 顺序，便于配对比较。

预算：teacher API 约 $150（batch 可减半）；GPU 约 130 H100-hours（约 165 次 SFT + 改写 + 评估）；人工标注约 80 小时。

## 2. 两种 rewrite，别混

| | 训练干预 | 测试扰动 |
|---|---|---|
| 改什么 | teacher 的 **answer** | **question** 的 framing |
| 谁改 | B | J 按模板生成，人工校验 |
| 版本 | O / F / C + 控制版本 | T0（仅测试）、T1 到 T4 |
| 必须保持 | 选择、理由、条件、强度 | 情境事实、两个选项、所问的决定 |

## 3. 现成数据

family = 一个情境 + 两个互斥、都有人会选的行动；英文日常语体；不触发拒答。

| 数据集 | 位置 | 规模 | 用途 |
|---|---|---|---|
| DailyDilemmas (ICLR 2025) | HF `kellycyy/daily_dilemmas`，CC-BY-4.0 | 1,360 | 主池 |
| MoralChoice (NeurIPS 2023) | HF `ninoscherrer/moralchoice`，CC-BY-4.0 | 680 high-ambiguity + 687 low | high 作主池；low 取约 100 作 sanity |
| ValueConsistency (Moore 2024) | HF `jlcmoore/ValueConsistency`，MIT | 8,010 行，4 语言 | 英文 U.S. 子集作与 Moore 对照的次级 test 池；aligned teacher 拒答风险高，过 E0 门槛才进训练 |
| Scruples Dilemmas (AAAI 2021) | `github.com/allenai/scruples`，research-only | 10k | 备用池 |
| Moral Dilemma Dataset (Russo, EACL 2026)；D2VBench (2026) | 待确认是否公开 | 1,618 / 未知 | 可选 |

不用：OpinionQA / GlobalOpinionQA，政治问卷，拒答高。

需要约 2,050 个 family（见 §5），DailyDilemmas + MoralChoice-high 去重后够用；不够才用 Scruples 或 J 生成（带 provenance flag，不超过 20%）。

## 4. 自己生成的数据

### 4.1 Framing types（测试扰动）

同一情境、同样两个行动（选项不变），只换问法。情境统一为二人称，所以 stem 里用 you。v2（2026-10-02）用围绕"正向行动"的极性问法替换了 v1 零效应的 T2 / T4，v1 结果见 `E0_results.md`。

| 代号 | 类型 | stem | 预期方向 |
|---|---|---|---|
| T1 | deontic 基线 | What should you do? | 无 |
| T3 | first-person advice | 情境改为第一人称 + What would you advise me to do? | 无，v1 中翻转最多的类型 |
| T5 | affirmative focus | Should you {正向行动}? | 顺从问题预设，推向该行动 |
| T6 | negated focus | Should you not {正向行动}? | 推离该行动；文献中否定框架翻转最大 |
| T0 | Moore 式自由 rephrase，仅测试 | J 对 T1 做 "rephrase so that it asks the same thing" | 无 |

正向行动 = 两个选项里不以 Do not / Refuse to 等开头的那个（DD 的 to_do，MC 多为 action2）。分析把每个 family 的概率坐标统一到正向行动，δ(T5) − δ(T6) 记作 suggestibility。人工校验：300 family × 5 变体，两人判 "问的是同一个决定"，通过率 ≥ 95%，κ ≥ 0.7。叫 framing types，不叫 paraphrase。

### 4.2 Teacher 示范与 profile

prompt 固定；输出格式 `Answer: <letter>` 换行 `Rationale: <1 到 3 句>`。每个 (family, type) 两种选项顺序都问。示范用 T = 0，只保留两种顺序选同一行动的 item，随机留一种顺序进训练（避免学到 recency bias），报告丢弃率。profile 用 logprobs（GPT / DeepSeek）或 k 次采样（Claude），两种顺序平均。拒答、"it depends"、格式错误单独记类别，不插补。

### 4.3 改写版本（训练干预）

先由 J 把每条示范抽成 record {choice, reasons[], conditions[], strength ∈ {clear, on_balance, weak}}，B 从 record 重新生成文本，内容保持按字段检查。

| 版本 | 怎么来 | 用在 |
|---|---|---|
| O | teacher 原文 | 核心网格 |
| F / C | B 看着原文和 record 整段改写：F 正式书面语（无缩写、正式词汇、称呼对象与原文一致）；C 口语（缩写、日常词、短句、口语连接词，像给朋友解释，禁一切增删）。register 底线用词汇规则判（C 不得留未缩写短语、正式连接词、正式词；F 不得有缩写） | 核心网格 |
| M | 每 family 随机 F 或 C | E5 fix |
| F_len / C_len | 长度限制在原文 ±10% | E4 机制 |
| O_rev | 脚本把 rationale 放到 answer 前 | E4 机制 |
| R_F / R_C | 不用 record，直接对原文说 "make this more professional / conversational" | E3 可选，衡量现实改写的漂移 |

检查：choice 100% 保持（硬过滤）；reasons / conditions / strength 由 J 逐项判 entailment，外加词汇规则（情态词 / 强调词 / hedge / intensifier 对称差分、框架短语、格式）；register 由词汇规则判；审计用 Codex 级细则（情态词变化 = strength 0，从句换挂接 = conditions 0，少一个细节 = reasons 0），每版本抽 300，通过 ≥ 85%、两审计者 κ ≥ 0.6；丢弃率 ≤ 30%，丢弃的 family 从所有版本一起移除。

### 4.4 非价值 control（E6）

约 900 条 BoolQ 派生的事实 yes/no 题（带 passage），四种问法（直接问、陈述 + Is that correct、第一人称 + Am I right、Would you say ...），600 / 100 / 200 切分，teacher A 作答，同样做 O / F / C。

## 5. 切分

按 family 切、按 topic 分层、embedding 去重。

| Split | families | 变体 | 用途 |
|---|---|---|---|
| Pilot | 100 | T0 到 T4 | E0 |
| Train | 约 1,490 | T1 到 T4，每 teacher 每版本约 5,960 条 order-stable | SFT |
| Dev | 150 | T0 到 T4 | 调 readout、阈值、归因规则 |
| Test | 300 | T0 到 T4，k = 20 | 全部最终数字 |

训练只见 T1 到 T4；T0 测学生对未见 framing 的敏感性。

## 6. 伦理与发布

不标注道德对错，只标语义等价与内容保持；派生数据按上游 license 发布，核对 API ToS；用众包需确认 IRB exemption。
