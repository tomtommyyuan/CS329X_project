# E7 预注册：黑盒溯源（Provenance under realistic conditions）

> 状态：**2026-10-08 写于任何溯源结果产生之前**。输入全部已存在（学生的 test / dev readout、teacher 的 test / dev profile），阶段 1 不花 API、不用 GPU。上游：[docs/03](../docs/03_experiments.md) E7 行、[e2c_plan](e2c_plan.md) §6、[e3c_plan](e3c_plan.md) §8、[docs/story.md](../docs/story.md)。

## 0. 问题与立场

RQ4：只看一个学生模型的**行为**，能不能判断它是从哪个 teacher 蒸馏来的；文风改写后还能不能。E2c / E3c 已给出前提：争议示范训出的学生继承 teacher 特有的判断倾向，且该倾向穿过文风改写。E7 把它做成**检测任务**，并尽量模拟真实的检测条件，而不是全知设定下的分类玩具。论文只 claim 信号与条件，不 claim 审计系统（docs/03 E7 行）。

## 1. 真实条件 → 实验中的对应

| 真实检测者（实验室 / 审计方）面对的条件 | 我们怎么模拟 | 不模拟 / 局限 |
|---|---|---|
| 可疑模型只能黑盒查询：开放权重时有 logprob，闭源 API 时只有采样文本 | 两种 readout：(i) 字母概率（现有 fp32 readout）；(ii) **只采样**：按现有概率抽 n 次答案取多数，n ∈ {1, 3, 10}，重复抽样取平均结果 | 不重新推理学生（checkpoint 已删），采样由概率模拟 |
| 手里只有**一个**可疑模型，没有 5 个 seed | 判定单位 = 单个 run；seed 只用来估不确定性 | — |
| 不知道蒸馏用了什么 prompt、什么数据源、什么配方 | 探针 = 冻结 test（DD / MC 来源），与所有训练 family 不相交，与 E2c 的训练来源（Reddit / ETHICS / Moral Stories）不同分布；检测规则对所有网格一套，不按条件调参 | 探针领域仍是道德困境，与训练领域同类 |
| 候选 teacher 是有限集合（几家前沿 API），但可疑模型可能**不来自任何候选** | 开集：候选 = 3 个 teacher；负例 = 共识对照 K / K_n 学生（有蒸馏、无特定 teacher 信号）、随机标签 R、未训练 S_0；必须有"不判定"选项，按负例的 FPR 定阈值 | 阶段 2 才加同家族 / 旧版本候选 |
| 候选 teacher 可以黑盒查询（有 logprob 的给 logprob，没有的采样） | 现有 teacher test / dev profile（GPT-4o / DeepSeek logprob，Claude 采样 20 次） | — |
| 可疑模型的基座可能已知（开放权重、model card）也可能未知 | 两种检测器：**基座已知**（减去 S_0 对各 teacher 的一致率）与**基座未知**（不减） | 只有一个基座（Qwen3-4B），基座先验像 DeepSeek 的影响无法跨基座检验 |
| 阈值和参照只能在别处标定，不能在被测模型上调 | 参照与阈值全部在 **dev** split 上定，test 只跑一次；再做 leave-one-grid-out（在 E1 原集学生上标定，用到 E2c / E3c 等网格） | — |
| 查询预算有限 | 准确率随探针 family 数的曲线（30 / 60 / 100 / 150 / 300，随机子集 × 200 次） | — |
| 检测者会**挑候选 teacher 意见不一致的题**来探 | 探针选择只用 teacher 的答案（不用学生信息）：全部 cell vs teacher 分歧 cell | test 上分歧 cell 只有约 11%（127 / 1,121） |
| 蒸馏方可能改写了 teacher 输出 | **leave-one-style-out**：规则、参照、阈值只用 O 学生定，再去认 E3 / E3c 的 F / C 学生 | — |
| 蒸馏方可能换过 teacher 版本，检测者手里只有现版本 API；或可疑模型混合多个 teacher | 阶段 2：加同家族 / 旧版本候选（GPT-4.1、GPT-4o-mini、GPT-4 0613、Claude Haiku 4.5）做"真 teacher 不在候选集"的替代实验 | 多 teacher 混合学生没有训练，列为未来工作 |
| 词汇层溯源（PoS / n-gram）作 baseline | 学生 checkpoint 已删、不能生成文本，所以词汇 baseline 做在**训练文本**上（teacher 原文 vs F / C 改写稿能否按词汇认出 teacher），说明词汇线索被改写抹掉而行为线索留下 | 与 docs/03 E7 原设计（学生生成文本的 PoS）不同，须披露；要做学生文本版需重训少量学生 |

## 2. 输入

| 项 | 内容 |
|---|---|
| 学生（test 与 dev readout 都齐） | E1 原集 O 15；E1 R 3；E3 paired O / F / C 45；E2c-C 15；K 15；K_n 15；Cnf 15；E3c paired O / F / C 45；S_0 | 共 165 个蒸馏学生 + 3 R + S_0 |
| 真值 | 每个 run 的 teacher（run id）；K / K_n / R / S_0 的真值 = "无特定 teacher" |
| teacher 参照 | `data/teacher_phase1/{t}_{dev,test}_profile.jsonl`，symmetrized 多数行动与 p_sym（同 `e1_metrics.sym_table`） |
| 探针 | `data/prompts/{dev,test}_prompts_v2.jsonl`，T1 / T3 / T5 / T6 两序（T0 只作描述） |

## 3. 检测器（全部预先写定）

| 项 | 定义 |
|---|---|
| 行为指纹 | run 与 teacher t 在 cell 上的多数行动一致率 a_t（`e1_metrics.teacher_agreement`，p_sym = 0.5 的 cell 不计） |
| 分数 | 基座已知：s_t = a_t − a_t(S_0)；基座未知：s_t = a_t − mean_t' a_t'（减去该 run 对所有候选的平均，去掉"整体像谁都像"的成分） |
| 判定 | t* = argmax s_t；margin = s_{t*} − 第二大；margin > τ → 判为 t*，否则"不判定" |
| 阈值 τ | 在 dev 上定：使 dev 负例（K、K_n、R、S_0）被判为任一 teacher 的比例 ≤ 5%（负例 ≥ 20 个时）；同一 τ 用于 test 与所有网格 |
| 采样 readout | 每个 cell 的 p 作 Bernoulli，抽 n 个答案取多数（两序各抽），重复 200 次，报均值与区间 |
| 探针子集 | 全部 cell；teacher 分歧 cell（三家多数行动不全同，用 teacher profile 定，不看学生）；随机 k 个 family |

## 4. 指标与判定规则

| 量 | 定义 | 参照 |
|---|---|---|
| 每 teacher 召回 | 真值为 t 的 run 中被判为 t 的比例，Wilson 95% CI | 随机 1/3 × (1 − 不判定率)；teacher 标签置换 10,000 次 |
| 开集 FPR | 负例被判为任一 teacher 的比例 | 目标 ≤ 5%（dev 标定） |
| AUROC（一对多） | 以 s_t 为分数，"真值 = t" vs 其余（含负例） | 0.5 |
| 总体 | 三 teacher 的平均召回（macro），不判定计为错 | |

**主判定**（test，一次）：在 **E2c-C 的 15 个 O 学生**上，基座已知、字母概率 readout、全部探针：≥ 2/3 的 teacher 召回的 Wilson 下界 > 1/3，且开集 FPR ≤ 10% → **溯源可行（有条件）**；1/3 → 部分；0/3 → 不可行。预测：DeepSeek 可行，Claude 部分，GPT-4o 不可行（E2c 的 gap 0.035 / 0.028 / 0.003 决定了上限）。

**预注册的次级行**（都在 test，各一次，不改规则）：(a) E1 原集 O 学生 → 预测在随机水平（E2 null 的另一种表述）；(b) leave-one-style-out：E3c 的 F / C 学生 → 预测 DeepSeek 仍可行（E3c gap 穿过改写）；E3 的 F / C 学生 → 随机；(c) 基座未知 vs 已知；(d) 采样 readout n = 1 / 3 / 10 vs 概率；(e) 探针数曲线与分歧探针；(f) leave-one-grid-out 标定；(g) Cnf、K_n、3 epoch 归档 run（有 test 的）作描述。

**词汇 baseline**（训练文本）：对每个 teacher 的 O / F / C 训练目标文本做 PoS 3-gram + 字符 n-gram 的 logistic 三分类，leave-one-style-out（O 训练、F / C 测试），报准确率：预测 O 内近 100%，F / C 上大幅下降。与行为溯源的对比是定性的（对象不同），论文须说明。

## 5. 阶段

| 阶段 | 内容 | 代价 |
|---|---|---|
| 1（现在） | `src/vcd/analysis/provenance.py` + `scripts/21_provenance.py` + 测试；dev 标定 → 冻结 hash → test 一次；词汇 baseline 脚本 | 0 API，Mac CPU |
| 2（待批） | 加候选 teacher：GPT-4.1、GPT-4o-mini、GPT-4 0613、Claude Haiku 4.5 的 dev / test profile（`04 --mode profile`）；重算开集与"真 teacher 不在候选集"（如把 GPT-4o 换成 GPT-4.1 作参照） | 估 $60–90 API |
| 3（可选） | 重训 6–9 个学生用于生成，做学生文本的词汇 baseline（docs/03 原设计） | 约 3 GPU 小时 |

## 6. 披露

E7 在看到 E2c / E3c 的 test 结果之后设计；主判定与次级行在任何溯源结果之前写定于此；阈值只在 dev 标定；词汇 baseline 的对象因 checkpoint 已删而改为训练文本。只有一个基座，基座先验（像 DeepSeek）与 teacher 可区分性的交互无法分离，是本实验最大的外部效度限制。

## 7. 结果

### 7.1 词汇 baseline（训练文本；2026-10-08，`results/e7_lexical/`，`scripts/22_lexical_provenance.py`）

**预测落空，如实记录**：§4 预测"O 内近 100%，F / C 上大幅下降"，实际是 O 内 0.94 / 0.90，改写后仍远高于随机。

| 集 | 评估（family 不相交；macro 准确率，随机 1/3） | gpt4o | claude46 | deepseek_v4 | macro |
|---|---|---|---|---|---|
| 原集 | O 内 5 折 | 0.921 | 0.973 | 0.915 | 0.936 |
| 原集 | O 训 → F 测 | 0.910 | 0.972 | 0.757 | 0.880 |
| 原集 | O 训 → C 测 | 0.743 | 0.895 | 0.816 | 0.818 |
| 争议集 | O 内 5 折 | 0.894 | 0.933 | 0.858 | 0.895 |
| 争议集 | O 训 → F 测 | 0.889 | 0.894 | 0.584 | 0.789 |
| 争议集 | O 训 → C 测 | 0.668 | 0.904 | 0.683 | 0.752 |
| 两集 | 只用长度特征（词数、句数、平均词长） | | claude46 0.95 / 0.76 | | 0.74 / 0.68 |

线索是什么（O 模型的 top 词特征）：gpt4o 的论证词汇（"crucial"、"important to"、"might"）与随文风翻转的 "it is" / "it's"；claude46 的长多句结构（标点密度、破折号；长度一项就能认出 0.95）；deepseek_v4 的弯引号 ’、分号与 "trust / harm / , even"。改写器抹掉的是**正字法与 register 标记**（弯引号、分号、缩写形式、部分破折号），留下的是**长度 / 句子结构与论证词汇**。DeepSeek 的 O → F 下降（0.915 → 0.757，争议集 0.858 → 0.584）主要就是弯引号被抹掉。

**对论文的含义**：原来的措辞"词汇线索被改写抹掉、行为线索留下"不成立，应改为"register 改写抹掉表面正字法，但不抹掉长度与词汇语义偏好；示范文本的词汇溯源大体幸存"。行为检测器因此是**互补**的渠道，而非唯一幸存的渠道。要比较两个渠道在**同一批学生**上的表现，需要学生生成的文本（阶段 3，重训少量学生）。

注意事项：按 family 分折（同 family 的两选项内容会泄漏）；"同 prompt" 版本因内容记忆而偏高（原集 O→F 0.931、O→C 0.853），一并报在 CSV 里；PoS 3-gram 因离线无 tagger 未做；争议集三家 prompt 集重叠只有 0.25–0.51，来源构成可能带 teacher 信息；正字法归一化（’→'）和长度匹配的消融可再量化，未做。

