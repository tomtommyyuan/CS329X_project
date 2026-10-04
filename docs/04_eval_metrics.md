# 评估指标

> 其余文档：[01 Related work](01_related_work.md)、[02 模型与数据](02_models_and_datasets.md)、[03 实验](03_experiments.md)。

## 0. 记号

i = family；j ∈ {T0..T4} = framing；o = 选项顺序；p_M(X ∣ i, j, o) = 模型 M 选行动 X 的概率。p_M(i, j) = 两种顺序平均（symmetrized）；p̄_M(i) = 该 family 跨 framing 的均值；**framing shift** r_M(i, j) = p_M(i, j) − p̄_M(i)；**type effect** δ_M(j) = mean_i r_M(i, j)；r_M 全体 = **sensitivity profile**。JSD 为二元分布的 Jensen–Shannon（base 2）；D_DD 为 Moore 的到 JS centroid 的平均 JSD。

## 1. Readout 与回答类别

概率来源：开源学生读 `Answer:` 后两个选项字母的 logit 并归一化；GPT / DeepSeek 用 first-token logprobs；Claude 用 k 次采样频率（test k = 20）。全部两种顺序平均，未平均值只用于 artifact 分析。

类别：answer（两字母质量 ≥ 0.9 或可解析）、refusal、insufficient、malformed（> 5% 触发检查）。family 只有全部变体都是 answer 才进一致性 / profile 指标，排除比例按模型报告。拒答**永不**插补为 50/50。

## 2. 指标

| 组 | 指标 | 定义 | 防什么坑 |
|---|---|---|---|
| A 数据有效性 (E0) | 拒答 / insufficient / malformed 率 | 按 teacher、type、来源 | 池子 teacher 不答 |
| | order-stability；order artifact | 两顺序同行动的比例；mean abs(p(o1) − p(o2)) | 学到 recency bias；artifact 混进 framing 效应 |
| | δ_T(j) 与 CI；profile reliability | family bootstrap；split-half 与两次采样的相关 | 把噪声当 profile |
| | teacher distinctness | corr(r_T, r_T') | 太像则无法检验继承与归因 |
| | framing 等价、内容保持、style 可区分、丢弃率 | 人工 κ；choice / reasons / conditions / strength 的 entailment；分类器 | 换了问题；隐性改内容；只在容易的 item 上宣布安全 |
| B 一致性 | flip rate | 每 family 变体对中多数行动不同的比例（5 变体 10 对），再跨 family 平均 | 只看类别翻转 |
| | cross-framing JSD | 变体两两 JSD 的均值 | 不过 0.5 的漂移 |
| | D_DD | Moore 指标，在 T0 子集报 | 与 anchor 对照 |
| | 见过 vs 未见 framing | T1 到 T4 内部 vs T0 对 T1 | 分开继承的敏感性与对新措辞的反应 |
| C 判断与漂移 | teacher agreement；student–teacher JSD | 多数行动一致率；mean JSD | 蒸馏是否成立；agreement 掩盖置信差 |
| | 跨学生分歧率 | S_{T,F} vs S_{T,C} 同 seed 同 prompt 多数行动不同的比例 | style 改变学到的判断 |
| | excess teacher drift | JSD(S_{T,V}, T) − JSD(S_{T,O}, T)，按 seed 配对 | 把普通蒸馏损失算到 rewriter 头上 |
| | homogenization index | S_{A,V} 与 S_{A',V} 的判断 JSD 与 1 − corr(profile)，对比 V = O | fix 靠同质化起效 |
| | **seed-noise null** | 同 (teacher, version) 的 seed 两两之差的分布 | 把训练噪声当效应 |
| D 继承 (E2 / E3 / E8) | ρ(s, T) | r_s 与 r_T 在 test (i, j) 上的 Pearson 与 Spearman | |
| | **Δρ** | ρ(own) − max ρ(other)，每 seed | 学生像所有 teacher 一样像 |
| | 按 type 的 Δρ；δ 向量相关 | 后者只有 4 到 5 个点，描述性 | 单一 type 驱动 |
| | Δρ 随 form 的变化 | Δρ(S_{T,F / C}) − Δρ(S_{T,O})，配对 | |
| | 共享成分 | r_s 对 r_own 与 r_other 联合回归的 R² | teacher 共有的 profile 成分 |
| E Provenance (E7) | 最近 teacher 准确率 + Wilson CI；margin；leave-one-style-out；PoS / n-gram baseline | 单位 = checkpoint | 小 n；近似打平；detector 认 rewriter 习惯 |
| F 稳健性 (E6) | readout stability；order / label 效应大小；MC 与 open-ended 一致（J + 人工 κ）；value vs factual 对比 | | 效应活在 readout 里；MC 不代表生成行为；value 特有还是通用 |
| G 机制 (E4) | rationale 长度；决策 token 占比；S_0 perplexity；控制后效应存活；cell 级相关 | 训练文件 / test | H2、H3 的操作化；cell 少只作描述 |

解读护栏：Δρ > 0 出现在**未见** family 上不可能是记忆题与答案，只能来自 framing type 与判断之间学到的规律，这是 "继承 disposition" 的含义。

## 3. 统计

单位：一致性、agreement、漂移按 family；provenance 按 checkpoint；null 按 seed 对。核心 cell 5 seeds（最少 3），seed 跨版本配对。family bootstrap 10,000 给 CI；Δρ 用 permutation；E3 / E5 用配对 seed 对 null；每实验内 Holm 校正；效应量以 null SD 为单位。null claim 用 TOST，等价界 = 1 个 null SD，没过 TOST 的 "无效应" 写成 inconclusive。E0 后用 pilot 方差模拟，确认 5 seeds × 300 family 对 Δρ = 0.1 和 1 个 null SD 的一致性差有 power ≥ 0.8，不足则加 seed 或 test。
