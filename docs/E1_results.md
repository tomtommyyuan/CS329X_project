# E1 / E2 / E3 结果（2026-10-05）

> 确认性结果只有两份：`results/e1/`（E1 / E2，test）与 `results/e3/`（E3，test），各只跑一次。`results/e1_dev/`、`results/e3_dev/` 是选规则的 split，数字只作描述。过程见 `tasks/hpc_log.md`，规则见 `tasks/e1_plan.md` §0、`tasks/e2_plan.md` §1–2、`tasks/e3_plan.md` §2–3。

## 0. 一句话结论

| 实验 | 结论 | 判定 |
|---|---|---|
| E1 蒸馏基线 | 学生学会了 teacher 的训练标签（复现 ≥ 0.983）并在争议项上站自己 teacher（≥ 0.900） | **PASS** |
| E2 heritability | 预注册 Δρ 0 / 3 teacher 过；次级 D 0.027 [−0.013, 0.070]，CI 含 0。基座训练前就最像 DeepSeek；学生的 suggestibility 排序 DeepSeek > GPT-4o > Claude 稳，但与 teacher 的差不像继承 | **FAIL / fail**；E0 可靠度门槛在 test 触发，RQ1 降为 exploratory |
| E3 form 调节 | 13 行判定 0 effect、1 no effect、12 inconclusive；无一行达到 ≥ 2 / 3 teacher 同号超 q95；单 teacher 超阈见于 4 行但方向不一致 | 未检出 form 效应（12 / 13 inconclusive，不是证明无效应） |

## 1. 设置

| 项 | 值 | 来源 |
|---|---|---|
| 学生 | `Qwen/Qwen3-4B-Base`，4.02 B 参数，全参 SFT | `train_manifest.json` |
| 训练 | bf16，lr 1e-5 cosine，warmup 0.03，3 epoch，有效 batch 32（4 × 8 累积），max_seq_len 1024，loss 只在 assistant，adamw_torch fused，gradient checkpointing，sdpa；1 × H100 80 GB | 同上 |
| readout | first-token p(A) / p(B)，transformers 后端 fp32，两字母质量 ≥ 0.9 才计答；两种选项顺序平均（symmetrized） | `tasks/e1_plan.md` §6、`results/e1_gate/` |
| 训练数据 | O 全集：GPT-4o 5,619 / Claude 5,642 / DeepSeek 4,936 条；paired O / F / C 交集：5,132 / 4,682 / 4,668；R 随机标签 5,619 | `tasks/hpc_log.md` 步骤 1、§8 |
| 评估数据 | dev 150 family、test 300 family × (T0, T1, T3, T5, T6) × 2 顺序 = 1,500 / 3,000 prompt；训练 prompt readout = SFT 行数 | `tasks/hpc_log.md` |
| run 数 | E1 / E2：15 O + 3 R + S_0；E3：45 paired（3 teacher × O / F / C × 5 seed）；共 63 个训练 run | `runs/qwen3-4b*/` |
| GPU 用量 | 训练合计 13.8 GPU 小时（63 run，每 run 11.0–16.0 分钟），峰值显存 68.99–69.91 GiB，0 OOM；readout 待补（估算：paired train / dev readout 3 个 follower × 约 1 小时，`tasks/hpc_log.md` 3e8e654，未计 test readout） | manifest `wall_time_sec`；`tasks/hpc_log.md` |

Gate run（`results/e1_gate/gate_summary.json`，30 步，200 条 dev）：

| 检查 | 结果 | 处理 |
|---|---|---|
| vLLM bf16 vs transformers bf16，max ∣ΔP(A)∣ | 0.062（阈 0.01），mean 0.0055 | 全部 readout 改 transformers |
| transformers bf16 vs fp32 | max 0.062，mean 0.0069 | 上一行是 bf16 噪声；readout 改 fp32（7dc06f6，早于任何 dev 分析） |
| first-token vs 采样频率，k = 200 | 学生 mean ∣diff∣ 0.011（噪声地板 0.012）；S_0 0.020（0.021） | 不改用采样 |
| 显存 / 精度 / 丢弃 | 69.27 GiB / bf16 / 0 | 过，optimizer 全网格统一 |

## 2. E1 蒸馏基线

训练事实（`runs/qwen3-4b*/**/train_manifest.json`）：

| 条件 | run | steps | n_examples | target token / epoch | 峰值 GiB | 分钟 | final loss |
|---|---|---|---|---|---|---|---|
| gpt4o O | 5 | 528 | 5,619 | 279,029 | 69.36–69.37 | 13.8–15.1 | 0.093–0.134 |
| claude46 O | 5 | 531 | 5,642 | 447,303 | 69.79–69.91 | 14.6–15.2 | 0.163–0.248 |
| deepseek_v4 O | 5 | 465 | 4,936 | 221,871 | 69.33–69.41 | 12.2–15.0 | 0.136–0.241 |
| random R | 3 | 528 | 5,619 | 95,523 | 68.99–69.01 | 15.3–16.0 | 0.039–0.040 |
| paired gpt4o O / F / C | 15 | 483 | 5,132 | 253,140 / 254,965 / 261,664 | 69.32–69.43 | 12.1–14.4 | 0.066–0.119 / 0.102–0.205 / 0.162–0.307 |
| paired claude46 O / F / C | 15 | 441 | 4,682 | 367,448 / 369,317 / 376,087 | 69.63–69.68 | 11.9–15.0 | 0.154–0.250 / 0.165–0.323 / 0.328–0.470 |
| paired deepseek_v4 O / F / C | 15 | 438 | 4,668 | 208,353 / 212,042 / 222,217 | 69.38–69.41 | 11.0–13.0 | 0.200–0.281 / 0.290–0.380 / 0.395–0.532 |

R 的 loss ≈ ln 2 / 16 token：固定 rationale 学会、随机字母学不会。同一 teacher 内 final loss O < F < C，改写文本对基座更难拟合，但 E1a 在 paired 上仍 ≥ 0.981。

E1a 训练标签复现与 E1b 争议项站队（`results/e1/e1_train_reproduction.csv`、`results/e1/e1_contested.csv`；训练 prompt 上评，dev / test 相同）：

| teacher | E1a 复现（5 seed，门 ≥ 0.95） | answer 率 | E1b vs claude46 | E1b vs deepseek_v4 | E1b vs gpt4o | 判定 |
|---|---|---|---|---|---|---|
| claude46 | 0.985–0.988 | ≥ 0.999 | — | 0.930 [0.902, 0.954]（299 项） | 0.919 [0.892, 0.945]（357 项） | pass |
| deepseek_v4 | 0.989–0.996 | 1.000 | 0.951 [0.931, 0.968]（299 项） | — | 0.918 [0.889, 0.944]（198 项） | pass |
| gpt4o | 0.983–0.986 | 1.000 | 0.910 [0.883, 0.934]（357 项） | 0.900 [0.862, 0.933]（198 项） | — | pass |
| random R（描述） | 0.553–0.557 | 1.000 | — | — | — | — |

E1b 门：family bootstrap 95% CI 下界 > 0.5；最低 0.862。**E1 PASS**。

未见 family 上的 agreement（描述项，seed 均值；`results/e1_dev/summary.md`、`results/e1/summary.md`）：

| 学生 | split | agree own | agree other max（谁） | JSD own | flip rate | 原规则 own > other_max 过的 seed |
|---|---|---|---|---|---|---|
| gpt4o O | dev | 0.856 | 0.856（deepseek） | 0.093 | 0.074 | 2 / 5 |
| claude46 O | dev | 0.846 | 0.829 | 0.114 | 0.047 | 4 / 5 |
| deepseek_v4 O | dev | 0.844 | 0.826 | 0.083 | 0.102 | 5 / 5 |
| random R | dev | — | 0.497 | — | 0.041 | — |
| gpt4o O | test | 0.857 | 0.855（seed 间 claude / deepseek 交替） | 0.094 | 0.069 | 3 / 5 |
| claude46 O | test | 0.882 | 0.862 | 0.101 | 0.026 | 5 / 5 |
| deepseek_v4 O | test | 0.857 | 0.848 | 0.080 | 0.082 | 5 / 5 |
| random R | test | — | 0.459 | — | 0.055 | — |
| S_0 | test | — | 0.830（8 个完整 family） | — | 0.188 | — |

原规则（每个 O seed 的 own agreement > 其他 teacher 最大值）为什么在 dev 上失败（`results/e1_dev_diag/`、`tasks/hpc_log.md` 2026-10-04 诊断）：

| 原因 | 数字 |
|---|---|
| 训练标签几乎共识 | 三 teacher 两两一致 93.3–95.8%；gpt4o 与 DeepSeek 只有 198 / 4,734 项不同 |
| dev 上 teacher 共识高、争议 cell 少 | teacher 两两多数一致 0.83–0.89；争议 cell 65–100 个（33–47 个 family） |
| 争议项上对未见题泛化弱 | 训练项上站自己 teacher 0.90–0.97，未见争议 cell 上只有 0.45–0.66 |
| 基座先验像 DeepSeek | S_0（不加门）profile 与 DeepSeek ρ 0.533，与 GPT-4o 0.277，Claude 0.245（dev，139 family）；非 DeepSeek 学生的 ρ_other_max 都是 DeepSeek（10 / 10 run；agreement 的 other_max 则是 claude ↔ gpt4o 互为最近） |
| JSD 被校准混淆 | p 落在 [0.1, 0.9] 外的 cell：GPT-4o 0.89、Claude 0.92、DeepSeek 0.64；R 学生对 DeepSeek 的 JSD 也最小（fp32 seed 均值 0.196 vs gpt4o 0.275 / claude 0.288，`results/e1_dev/summary.md`） |
| 不是 seed 噪声 | gpt4o 学生 own − DeepSeek 五个 seed：0 / −0.003 / +0.008 / −0.003 / −0.002（fp32，`results/e1_dev/summary.md`），差距 ≤ 0.008 且 test 上 3 / 5；interpretation.md 原写"五个 seed 全负（−0.003 到 −0.014）"与现表不符，以表为准 |

因此改为直接看训练项的 E1a / E1b（版本见 §5）。

## 3. E2 heritability（`results/e1/`，test，290 个公共 family，n_perm = n_boot = 10,000）

预注册 primary：seed-mean profile 的 Δρ = ρ(own) − max ρ(other)，family permutation + Holm（`inheritance_pooled.csv`）：

| teacher | ρ_own | 上限 sqrt(2r / (1 + r)) | ρ / 上限 | ρ_other_max（谁） | Δρ [95% CI] | null 均值 | p_perm | p_holm | 过 |
|---|---|---|---|---|---|---|---|---|---|
| claude46 | 0.085 | 0.704 | 0.12 | 0.240（deepseek） | −0.155 [−0.307, −0.055] | −0.073 | 0.973 | 0.973 | 否 |
| deepseek_v4 | 0.444 | 0.797 | 0.56 | 0.317（gpt4o） | +0.127 [0.029, 0.229] | +0.082 | 0.116 | 0.348 | 否 |
| gpt4o | 0.374 | 0.904 | 0.41 | 0.440（deepseek） | −0.067 [−0.185, 0.054] | −0.082 | 0.348 | 0.696 | 否 |

0 / 3 → **FAIL**。置换 null 不以 0 为中心（置换保留各 profile 的 variant 主效应），DeepSeek 的 Δρ 有 0.082 来自 null 均值。

次级 D 与分解（`e2_secondary_D.json`；规则：D 的 CI 不含 0 且 p < 0.05，且 D_specific 的 CI 下界 > 0）：

| 量 | test | dev（`results/e1_dev`，139 family） | 性质 |
|---|---|---|---|
| D（partial 给定 r_0，见过的 framing） | 0.027 [−0.013, 0.070]，p 0.061（null 0.004 ± 0.015） | 0.101 [0.041, 0.164]，p 1.0e-4 | 判定量 → **fail** |
| D_specific / D_shared | 0.067 [0.011, 0.125]，p 0.004 / −0.040 | 0.140 [0.065, 0.226] / −0.039 | 守门项（过），但 D 本身不过 |
| D_scalefree | 0.057 [0.011, 0.104] | 0.118 [0.055, 0.183] | 探索 |
| raw D（不控制 r_0） | 0.033 [−0.003, 0.071]，p 0.099 | 0.090 [0.040, 0.142] | 探索 |
| D，仅 T0（未见问法） | 0.054 [−0.001, 0.114]，p 0.006（288 family） | 0.027 [−0.035, 0.092]，p 0.15 | 探索 |
| mean ΔρPartial（15 run） | −0.014，teacher 层面精确 p 0.333 | +0.026，p 0.167 | 描述 |
| P3 ΔρPartial（Holm p） | claude −0.104（0.927）、deepseek +0.105（0.242）、gpt4o −0.033（0.489） | −0.022 / +0.086 / +0.020，均不显著 | 描述 |

partial ρ 矩阵（行 = seed 合并学生，列 = teacher；`results/e1/summary.md`）：

| 学生 | claude46 | deepseek_v4 | gpt4o | 行 contrast | contrast_specific |
|---|---|---|---|---|---|
| claude46 学生 | **0.055** | 0.150 | 0.158 | −0.099 | 0.114 |
| deepseek_v4 学生 | 0.131 | **0.322** | 0.216 | +0.148 | 0.071 |
| gpt4o 学生 | 0.184 | 0.317 | **0.283** | +0.033 | 0.016 |
| 列上限 | 0.704 | 0.797 | 0.904 | | |

Suggestibility s = δ(T5) − δ(T6)（描述；`suggestibility_groups.csv`、`suggestibility_group_pairs.csv`）：

| 组 | s [95% CI] | 学生 − 自己 teacher | 学生 − base prior |
|---|---|---|---|
| claude46 学生（5） / teacher | 0.026 [0.018, 0.034] / 0.045 [0.024, 0.067] | −0.019 [−0.042, 0.004] | −0.120 [−0.134, −0.107] |
| deepseek_v4 学生（5） / teacher | 0.140 [0.116, 0.166] / 0.113 [0.096, 0.131] | +0.027 [0.002, 0.053] | −0.006 [−0.030, 0.019] |
| gpt4o 学生（5） / teacher | 0.108 [0.089, 0.129] / 0.063 [0.045, 0.084] | +0.045 [0.022, 0.068] | −0.038 [−0.057, −0.017] |
| R 学生（3） | 0.0008 [0.0007, 0.0009] | — | −0.145 |
| base prior S_0（不加门） | 0.146 [0.133, 0.159] | — | — |

学生两两差：deepseek − gpt4o +0.032 [0.017, 0.047]，gpt4o − claude +0.082 [0.067, 0.099]；剂量反应 slope 1.441（Pearson 0.856），teacher 层面精确 p 1/6。排序保持，但 DeepSeek 学生 ≈ 基座、GPT-4o 学生高于自己 teacher、R 降到 0：更稳的说法（描述 / 假设，`results/e1/summary.md` 标为 statement under test，非判定）是 SFT 用训练标签里的 framing–标签关联替换了基座自带的 suggestibility。

S_0 控制与可靠度上限（`base_control.csv`、`results/e1/summary.md` Reliability ceilings）：

| 项 | claude46 | deepseek_v4 | gpt4o |
|---|---|---|---|
| S_0（不加门）与 teacher 的 ρ [CI] | 0.118 [0.035, 0.198] | **0.380 [0.327, 0.434]**，领先次近 0.100 [0.036, 0.167] | 0.280 [0.213, 0.344] |
| teacher 顺序 split-half r（test） | 0.329 | 0.466 | 0.691 |
| ρ 上限 sqrt(2r / (1 + r)) | 0.704 | 0.797 | 0.904 |
| E0 门槛（r < 0.5） | 触发 | 触发 | — |

S_0 控制"Δρ ≈ 0"不成立：基座训练前就系统性最像 DeepSeek。2 / 3 teacher 的 r < 0.5 → docs/03 §1 原文"RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5"，本项目做 E3。

## 4. E3 form 调节（`results/e3/`，test，45 paired run，冻结 5e98fe3）

阶段 2：实际训练文件的内容与 register 检查（`content_check.csv`、`register_check.csv`、`register_separation.csv`）：

| teacher | 版本 | 条数 | 与 O 字母一致 | judge 六项（choice / reasons / conditions / strength / style / format） | 改写保留率 | 平均词数 | target token | 缩写率 | 正式词率 | FK 等级 | F–C 可分（LOO / logistic） |
|---|---|---|---|---|---|---|---|---|---|---|---|
| gpt4o | O / F / C | 5,132 | 1.0 / 1.0 | — / 全 1.0 / 全 1.0 | — / 0.954 / 0.935 | 37.9 / 38.3 / 38.9 | 48.3 / 48.7 / 50.0 | 0.005 / 0.0002 / 0.034 | 0.050 / 0.055 / 0.012 | 14.0 / 14.7 / 10.4 | 0.921 / 0.959 pass |
| claude46 | O / F / C | 4,682 | 1.0 / 1.0 | — / 全 1.0 / 全 1.0 | — / 0.932 / 0.856 | 62.3 / 62.5 / 64.1 | 77.5 / 77.9 / 79.3 | 0.003 / 0.0004 / 0.022 | 0.028 / 0.034 / 0.006 | 14.4 / 15.2 / 10.8 | 0.927 / 0.952 pass |
| deepseek_v4 | O / F / C | 4,668 | 1.0 / 1.0 | — / 全 1.0 / 全 1.0 | — / 0.972 / 0.960 | 33.2 / 33.9 / 35.6 | 43.6 / 44.4 / 46.6 | 0.0001 / 0.0001 / 0.032 | 0.031 / 0.040 / 0.007 | 14.5 / 15.8 / 10.8 | 0.907 / 0.942 pass |

O–F 只有约 0.59–0.61 可分（O 本来就是正式语体），O–C 0.86–0.92；claude46 C 有 1 条 `letter_matches_rewrite` 前言泄漏，字母本身与 O 一致。内容无漂移，长度几乎不变：阶段 3 的任何差只能归 form。

阶段 3：13 行判定（`verdicts.csv`；每 teacher 统计量 = 5 个 seed 配对差 V − O 的均值，分歧率为对自己 O–O 水平的 excess；q95 = t(0.975, 12) × SD_stat，分歧率单侧 t(0.95, 12) 且只算 excess > q95；effect 需 ≥ 2 / 3 teacher 同号超 q95；no effect 需 ≥ 2 / 3 过 TOST）：

| 行 | tier | claude46 | deepseek_v4 | gpt4o | q95 | 超 q95 | TOST | verdict |
|---|---|---|---|---|---|---|---|---|
| 分歧率 F vs C（excess） | primary | +0.005 | +0.008 * | +0.004 | 0.006 | 1 / 3 | 0 / 3 | inconclusive |
| 分歧率 O vs F | secondary | −0.010 | −0.008 | −0.017 | 0.006 | 0 / 3 | 0 / 3 | inconclusive |
| 分歧率 O vs C | secondary | +0.007 * | +0.005 | +0.006 | 0.006 | 1 / 3 | 0 / 3 | inconclusive |
| flip rate F − O | primary | −0.000 | −0.002 | +0.002 | 0.007 | 0 / 3 | 0 / 3 | inconclusive |
| 跨 framing JSD F − O | primary | −0.0003 | +0.001 | −0.0004 | 0.005 | 0 / 3 | 2 / 3 | **no effect** |
| agreement F − O | secondary | +0.004 | +0.000 | −0.003 | 0.008 | 0 / 3 | 0 / 3 | inconclusive |
| excess drift（JSD to own）F − O | primary | −0.002 | −0.002 | +0.002 | 0.005 | 0 / 3 | 0 / 3 | inconclusive |
| ΔρPartial F − O | primary | +0.003 | +0.035 * | −0.034 * | 0.022 | 2 / 3，异号 | 0 / 3 | inconclusive |
| flip rate C − O | primary | 0.000 | +0.005 | −0.003 | 0.007 | 0 / 3 | 0 / 3 | inconclusive |
| 跨 framing JSD C − O | primary | −0.0003 | −0.002 | −0.003 | 0.005 | 0 / 3 | 1 / 3 | inconclusive |
| agreement C − O | secondary | −0.004 | −0.002 | +0.008 * | 0.008 | 1 / 3 | 0 / 3 | inconclusive |
| excess drift C − O | primary | +0.001 | −0.002 | −0.004 | 0.005 | 0 / 3 | 0 / 3 | inconclusive |
| ΔρPartial C − O | primary | −0.021 | +0.054 * | +0.010 | 0.022 | 1 / 3 | 0 / 3 | inconclusive |

\* = ∣stat∣ > q95（分歧率：excess > q95，负 excess 不计超）。单 teacher 超阈见于 4 行（分歧率 F vs C deepseek 2.9 null SD、O vs C claude 2.1、agreement C − O gpt4o 2.2、ΔρPartial F − O deepseek +3.4 与 gpt4o −3.3、C − O deepseek 5.3），均未凑成 2 / 3 同号。单个超阈最大的是 deepseek ΔρPartial C − O（5.3 个 null SD，Holm p 5.2e-4），但另两个 teacher 不跟。分歧率 O vs F 三 teacher 全负：同 seed 的 F / O 学生比两个不同 seed 的 O 学生更像（共享初始化与数据顺序，null 偏保守，e3_plan §3 已声明）。

Seed-pair null 的量级（`seed_pair_null_summary.csv`，同一 teacher 两个 O seed 的单对差，30 对）与绝对水平：

| 量 | 单对 mean | 单对 sd | 单对 q95 | 统计量 q95（5 seed 均值） | O 学生的绝对水平 |
|---|---|---|---|---|---|
| flip rate | 0.006 | 0.004 | 0.012 | 0.007 | claude 0.028 / deepseek 0.084 / gpt4o 0.066 |
| 跨 framing JSD | 0.004 | 0.004 | 0.011 | 0.005 | 0.006 / 0.039 / 0.023 |
| agree own | 0.007 | 0.004 | 0.015 | 0.008 | 0.869 / 0.854 / 0.861 |
| JSD own | 0.005 | 0.003 | 0.010 | 0.005 | 0.101 / 0.081 / 0.092 |
| O–O 分歧率 | 0.045 | 0.008 | 0.056 | 0.006（excess） | F–C 分歧率 0.041 / 0.056 / 0.055 |
| ΔρPartial | 0.020 | 0.011 | 0.036 | 0.022 | −0.076 / +0.116 / −0.035 |

描述项（`joint_D_by_version.csv`、`suggestibility_by_version.csv`、`homogenization.csv`）：

| 量 | O | F | C |
|---|---|---|---|
| joint partial D [CI]，p | 0.038 [−0.006, 0.083]，0.021 | 0.050 [0.002, 0.098]，0.004 | 0.055 [0.001, 0.113]，0.003 |
| D_specific [CI] | 0.077 [0.017, 0.137] | 0.096 [0.028, 0.164] | 0.098 [0.028, 0.170] |
| s：claude / deepseek / gpt4o 学生 | 0.015 / 0.143 / 0.105 | 0.013 / 0.146 / 0.107 | 0.011 / 0.142 / 0.103 |
| homogenization 1 − corr（跨 teacher 学生） | 0.524 [0.471, 0.581] | 0.541（vs O +0.016 [−0.006, 0.039]） | 0.537（+0.013 [−0.025, 0.052]） |

解读：13 行无一达到 effect 判定（≥ 2 / 3 teacher 同号超 q95）；9 行三 teacher 全在 q95 内，4 行有单 teacher 超阈但方向不一致或仅 1 / 3；一项（跨 framing JSD F − O）达到等价；F / C 各版本的 D 与 s 和 O 几乎相同，homogenization 不降。两个 D 按 E2 规则 "pass" 是在 paired 交集学生上的描述项，与 E2 的确认性 fail 不冲突（paired O 的 D 0.038 同样 fail）。E3 没有看到"文风改写破坏继承"或"文风改写同质化学生"的证据；12 / 13 inconclusive 意味着这是未检出，不是证明无效应。

## 5. 规则修订与披露

| # | 规则 | 内容 | 在 dev 上看过 | 状态 / commit |
|---|---|---|---|---|
| E1 原 | 每个 O seed 的 own agreement > other max | dev：deepseek 5/5、claude 4/5、gpt4o 2/5，未过 | 是 | 留档，不是判定（d06f6d5 → 换）|
| E1 现 | E1a 训练标签复现 ≥ 0.95 + E1b 争议项 own 下界 > 0.5 | dev 诊断 seed 1 后定（98.5 / 98.5 / 99.5%） | 是 | 冻结 456b487 |
| E2 v1 | 预注册 Δρ > 0 且 Holm p < 0.05，≥ 2/3 teacher | dev 0/3 | 是 | **仍是 primary**，test FAIL（d06f6d5） |
| E2 v2 | P3：partial Δρ（给定 r_0）+ Holm | dev 2/3 为正、无一显著 | 是 | 描述项 |
| E2 v3 | P1 / P2：15 个 run 重指派 teacher 的置换（756,756 种），mean ΔρPartial 与剂量 slope | dev p 1.3e-6 | 是 | **同日撤回**（c2c9d96 → 1989ddc）：同 teacher 的 seed 近复制，伪复制；可交换单位只有 3 个 teacher，精确 p 下限 1/6，dev 两者都恰为 1/6 |
| E2 v4 | 次级 D（family bootstrap + 残差 family 置换），单独判定 | dev D 0.101；同族交互量在 e1_dev_diag 算过 15 个变体 | 是 | 冻结前审查发现对"共享残差 × 行尺度不等"不免疫（模拟误拒约 28%），被 v5 取代 |
| E2 v5 | D 同上 + D_specific 的 CI 下界 > 0 守门 | dev D_specific 0.140 | 是 | **冻结 456b487**；test fail |
| E3 | docs/03 E3 行原文 → `e3_metrics` 操作化（尺度匹配的 seed-pair null、excess 分歧率、TOST、teacher < 3 一律 pending） | 规则在任何 F / C run 之前写定（fc54a5c）；dev 13 行全 inconclusive 后未改 | 是，未改 | **冻结 5e98fe3**；15 与 e3_metrics 自 fc54a5c 起未改 |
| readout | vLLM → transformers 后端；bf16 → fp32 | gate 阶段，早于任何 dev 分析 | 否 | d8b61fc、7dc06f6；bf16 → fp32 后 dev 判定逐 seed 相同 |

伪复制错误的更正（`tasks/hpc_log.md` 2026-10-05、`results/e1_dev_diag/interpretation.md`）：hpc_log 曾写 "grid permutation p < 1e-4，学生比随机指派更像自己 teacher"，撤回为 teacher 层面精确 p = 1/6（真实指派在 6 种里排第一，也是该设计的下限）；"suggestibility 有继承、顺序保持" 降级为有条件成立（dev 上 GPT-4o 与 Claude 两个 teacher 的差分不开：hpc_log 原文 +0.012 [−0.034, 0.057]，现 fp32 CSV +0.016 [−0.028, 0.062]（`results/e1_dev/suggestibility_group_pairs.csv`）；DeepSeek 学生 ≈ 基座；R 也降到 0）。另有一处输入错误：`results/e3_dev_e1tables` 第一次未带 `--sft-dir data/sft_paired`，E1a 误判 fail，重出后 pass（最低 0.981），非规则改动。论文必须列出以上全部版本。

## 6. 对论文的含义

| 项 | 表述 |
|---|---|
| F1（不一致会遗传） | **不能当头条**。预注册 Δρ 0/3；唯一为正的 DeepSeek 恰是基座最像的 teacher，null 均值已 +0.082；次级 D 从 dev 0.101 缩到 test 0.027，CI 含 0。如实报为未通过的预注册假设 + E0 可靠度门槛触发 |
| F2（teacher 特有信号能传多少、被什么挡住） | 跨家族全量 SFT 后，学生的 framing 敏感性主要由基座先验（S_0 与 DeepSeek ρ 0.380）和训练标签的 framing–标签关联决定；teacher 特有的逐题结构只有小幅、相对的传递：D_specific 0.067 [0.011, 0.125]、矩阵对角仅 DeepSeek 行为最大；T0 上 D 0.054 [−0.001, 0.114]。E1 说明这不是训练失败：标签复现 ≥ 0.983、争议项站队 ≥ 0.900，但 teacher 标签两两一致 93–96%，可传的信号本来就少 |
| F3（继承指标的系统性偏差） | Δρ 的置换 null 随 teacher 偏移（−0.082 到 +0.082）；基座先验让 Δρ / agreement / JSD 偏向同一个 teacher；JSD 偏向校准更温和的 teacher（R 学生对 DeepSeek JSD 最小）；按 run 置换是伪复制；R 的零基准不是 0；split-half r 不是 ρ 的上界（上限 sqrt(2r / (1 + r))）。对 provenance / 蒸馏归属类工作都有警示 |
| E3 的表述 | 内容逐项保持（字母 100% 一致、judge 六项 1.0、词数变化 ≤ 7.2%）而 register 真实分开（F–C 可分 ≥ 0.907）时，F / C 学生与 O 学生在判断、一致性、与 teacher 的距离、继承上没有一行达到 effect 判定（统计量 q95 0.005–0.022；单 teacher 超阈 4 行，方向不一致），一项等价成立；没有"文风破坏继承"的证据，也没有"同质化"的证据。注意 inconclusive 占 12/13：等价界 = 1 个 null SD 很严，这是"未检出"而非"证明无效应" |
| 审稿人会攻击 | (1) teacher 太像，null 反映数据不是蒸馏；(2) 只有一个基座，又碰巧像 DeepSeek；(3) S_0 参照靠放宽 0.9 门（test 上 answer 率 21.3%）；(4) 事后改指标（D 族算过 15 个变体，必须全披露）；(5) 3 个 teacher 的精确 p 下限 1/6；(6) 只有 first-token readout；(7) E3 的 inconclusive 多，power 不足以给窄等价界；(8) Claude teacher 的 r 0.33 使其学生的 ρ 上限只有 0.70 |
| 下一步 | **E2c 争议富集**：从 14,079 个 family 的 contested pool 筛 teacher 意见不同的题重训，检验"有信号时信号能传"（第一轮转换人工抽检门未过：四源三项联合 19% / 20% / 71% / 89%，先修规则转换）；**第二基座**（不同家族），看 DeepSeek 偏向是否跟基座走；**consensus 对照**学生（只用三 teacher 一致项训练），teacher 特有继承定义为相对它的偏移；受控剂量（chimeric T5 / T6 回答按比例取自 DeepSeek）；合规 S_0 参照（few-shot 格式提示或采样）。均为新实验，另行预注册 |

## 7. 过程记录

| 日期 | commit | 事件 | 花费 |
|---|---|---|---|
| 10-04 | d06f6d5 | E1 / E2 计划与原预注册规则进仓库 | — |
| 10-04 | eef6719、8ba8340 | HAIC 环境核实（torch 2.6.0+cu124、H100）；O + R 共 18 个 SFT 文件 | — |
| 10-04 | d8b61fc、36f5e1e | gate run：vLLM 一致性未过 → transformers；E0.7 readout 校验过；18 run 网格提交（array 129420） | gate 109 s |
| 10-04 | 7dc06f6 | Mac 侧：readout 改 fp32（早于 dev 分析），optimizer 统一规则 | — |
| 10-04 | 00e5c77 | 18 / 18 训练完成，0 失败；dev 评估；E1 原规则未过，诊断，BLOCKED | 训练 4.4 GPU 小时 |
| 10-05 | 1ac4e92 | dev readout 以 fp32 重跑，判定逐 seed 不变 | — |
| 10-05 | f8cdc21 | 25-agent dev 解读；更正 grid permutation p 与 suggestibility 论断 | — |
| 10-05 | a6741c2、aa8d7e0 | 训练集 F / C 改写进仓库（三 teacher 14,482 项 paired） | Gemini 改写 待补 |
| 10-05 | c2c9d96 → 1989ddc → 456b487 | 修订 E1 / E2 规则；P1 / P2 撤回；v5 冻结 | — |
| 10-05 | 6eb6075 | 18 run 训练 prompt readout；dev 以冻结版 13 重出；**E1 / E2 冻结于 456b487** | — |
| 10-05 | 0c91f89 | test readout（S_0 + 18 run）；`results/e1`：E1 PASS、E2 primary FAIL、secondary fail | — |
| 10-05 | fc54a5c、5e98fe3 | E3 分析栈（125 tests）；45 paired run 训练完成（array 130120，0 OOM）；阶段 2 检查；E1 checkpoint 清理 | 训练 9.4 GPU 小时 |
| 10-05 | 3e8e654 | paired train / dev readout（follower 约 1 小时 × 3）；dev 13 行 verdict；**E3 冻结于 5e98fe3** | — |
| 10-05 | 5c870be、b50ea55 | paired test readout 45 个；`results/e3`：12 inconclusive、1 no effect、0 effect | — |
| 10-05 | bc7b3bb | paired checkpoint 清理，scratch 回到 2.1 TB；HPC 任务全部完成 | 训练合计 13.8 GPU 小时 |
| 10-05 | 1dfa9b9 | E2c contested pool v1（14,079 family），第一轮人工抽检门未过 | — |

Phase 1 teacher 采集与改写的 API 费用 待补（E0 累计约 $50 见 `docs/E0_results.md` §9）。
