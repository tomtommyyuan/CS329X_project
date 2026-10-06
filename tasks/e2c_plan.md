# E2c 预注册：争议增强训练池（Contested-Enriched Training Pool）

> 状态：**代码、候选池、T1 prompt 就绪；审查修订已并入，2026-10-05**。筛选结果尚未产生；本文件 §0–§10 连同代码必须在任何筛选文件被打开前提交（§9）。付费筛选未开始，`data/teacher_e2c/` 不存在。上游：[docs/02](../docs/02_models_and_datasets.md) §3–5、[docs/03](../docs/03_experiments.md) §1–3、[e1_plan](e1_plan.md) §0、[e2_plan](e2_plan.md) §1–2（冻结于 456b487）。付费 API 只在 Mac 侧；本阶段不修改 `data/families/families.jsonl` 与 `data/prompts/{pilot,train,dev,test}_prompts_v2.jsonl`。

## 0. 问题

E1 在 dev 上显示：三个 aligned teacher 的训练标签两两一致 93–96%，teacher 特有信号太小，学生与自己 teacher 的 agreement 不高于与其他 teacher（gpt4o 0.856 / 0.856）。E2c 问：**如果训练示范只来自 teacher 彼此不一致（或不确定）的 family，学生能否学到 teacher 特有的判断，并在同一套冻结的 dev / test 上表现为 own > other（E1）与更强的 profile 继承（E2）？** 对照：等量、来源匹配的共识 family 训练集，排除"换了数据源"这一混杂。

按 §3 的争议定义用 `scripts/18_select_contested.py` 复算现有 train（phase-1 T1 demo，`results/e2c/calibration_tier0.md`）：1,469 个有效 family 中 **356 个（24.2%）已是 contested**（DD 24.4%、MC-high 23.9%）。分解（可重叠）：多数行动不同 154、logprob teacher 落入不确定带 242、Claude 两序分裂 74；其中 **113 个只因两序极端翻转**进入不确定带（`flip_only`，§3）。pilot DD 32%、MC-high 23%、MC-low 0/10（E0 期 teacher 数据，仅参考；dev / test 的 teacher 输出不在本文件引用）。所以 E1 的训练集里 3/4 是共识项。

## 1. 候选池：来源与数量

全部**纯规则**转换（无 LLM），复用 `normalize.py`；每条带 `meta.provenance`、`meta.license` 与源 id。Wave 1 固定；Wave 2 = 2a ∪ 2b，成员**现在已钉死**（seed 20261002），只决定是否启用；Wave 3（LLM 改写）只在前两波不足时启用并限额。

| 层 | 来源 | 候选数 | 导出规则 | 人类分歧信号 | 预期 contested rate | 预期产出 |
|---|---|---|---|---|---|---|
| 0 | **现有 train 的 contested family**（phase1 T1 demo 已有，0 次新调用） | 356 | 已是 Family | — | 100%（已筛） | 356 |
| 1a | **MoralChoice-low**（`sanity` split） | 675 | 已是 Family，只改 split | 无；构造上低歧义 | 3–8%（pilot 0/10） | 20–55；兼作选择脚本的低端校准 |
| 1b | **Scruples Anecdotes HYPOTHETICAL（WIBTA）**，规则干净、≤ 300 词 | 1,776 | situation = 正文去 edit / TLDR / AITA 句（含 NTA / YTA / ESH / NAH / "this sub"）→ 一人称→二人称 → `split_trailing_question`；action_x = `normalize_action(action.description)`（先去前导副词），action_y = 加 "Do not "；action 内 we / our → you / your | 社区投票 `label_scores`（中位 8 票）；少数派占比可算 | 35–50% | 620–890 |
| 1c | **Berkeley AITA（ucberkeley-dlab）**：WIBTA 前瞻 221 ∪ 回溯争议帖 727（max(nta, yta) < 0.7 **或** gpt4 ≠ claude，取并）且正文 ≤ 1,500 字符 | 948 | 标题正则 → 去前导副词 → `degerund_first_word` → 肯定 / "Do not " 对；正文清洗 + 一人称→二人称。回溯式先只送 200 条 `1_pilot`，过门才放 527 条 `1_gated`（§10） | `comments_*_agreement` + 2023 LLM 标签 | 35–50%（回溯帖的 rate 部分来自"事后叙述 + 前瞻 stem"的错位，见 §10） | 150–210（Wave 1） |
| 1d | **Moral Stories**（demelin），clean + same_gender_other | Wave 1 600（正 / 负 norm 各 300）；**2a = 其余正向 norm 全部 2,711**；负向 5,264 为 reserve | actor 名→you，代词 / 主谓一致规则；situation = 二人称 situation + intention；x = moral_action、y = immoral_action（`focus_action = x`） | 无（consensus-by-construction） | 6–15% | 36–90（Wave 1）；+160–400（2a） |
| 1e | **ETHICS justice（impartiality）**，每个 habit VP 取 1 条；habit 为 "used to"（习惯已停止，575 条）与状态动词 VP（76 条）**丢弃**；action 去习惯性时间状语（"every year" 等留在 situation） | Wave 1 300；**2b = 1,600**；205 reserve | 正则 "I usually VP but didn't … because R" → "You usually VP. This time, R."；x = VP，y = "Do not VP" | 无（≥ 4/5 标注一致才保留） | 4–10% | 12–30（Wave 1）；+64–160（2b） |
| 3 | **LLM 改写（last resort）**：Scruples HISTORICAL 少数派 ≥ 0.3 与 Berkeley 回溯争议帖 | ≤ 250 条进入训练集 | Gemini（J）只改 situation 为决策前的 ≤ 60 词二人称情境；action 对仍由标题规则导出；校验 `detect_person == second`、无裁决词、J 事实蕴含、人工抽 100 | 同 1b / 1c | 35–50% | ≤ 250 |

不用：Wan Dilemmas_Disagreement（无情境文本）、cnnmon（57 条、无许可）、ETHICS commonsense / desert、AITA 长帖。

**预算与触发**：Wave 1 = 675 + 1,776 + 421 + 600 + 300 = **3,772 family / 7,544 prompt / 22,632 次调用**；预期新 contested 840–1,270 + 层 0 的 356 → 目标 **1,500 contested**（新 ≈ 1,144）。Wave 1 后新 contested < 1,144 → 启用 2a（2,711 × 6 = 16.3k 次）；仍不足 → 2b（1,600 × 6 = 9.6k 次）；仍不足 → 层 3。**不降低争议定义凑数**；最终不足 1,200 则如实缩小训练集并在论文声明。

契约性的代码改动（已实现，`python -m pytest -q` 142 passed 1 skipped）：`schemas.Source` 加四个新源，`Split` 加 `pool_contested | train_contested | train_consensus_control`；loader 在 `src/vcd/data/load_contested_sources.py`（`HARD_FLAGS` 决定哪些转换不入池；`LICENSES` 写入 `meta.license`）；去重 / 泄漏在 `src/vcd/data/contested_pool.py`；§3 规则在 `src/vcd/analysis/contested.py`；脚本 `16_build_contested_pool.py`（建池 + 去重 + 分波 + 人工抽检样本 + 报告）、`17_contested_prompts.py`（任意 family 文件建 prompt；E0 路径 01–09 不动）、`18_select_contested.py`（§3 定义 + 分源报表 + E2c-C / E2c-K 组成 + 层 0 校准）。测试 `tests/test_contested.py`（17 个）。

实际建池结果（`results/e2c/pool_report.md`，2026-10-05 修订后）：

| 来源 | 载入 | 规则干净 | 泄漏丢弃 | 池内重复 | 入池 | Wave 1 | 2a / 2b | reserve |
|---|---|---|---|---|---|---|---|---|
| mc_low | 676 | 676 | 0 | 1 | 675 | 675 | — | — |
| scruples HYPOTHETICAL ≤ 300 词 | 3,195 | 1,782 | 0 | 6 | 1,776 | 1,776 | — | — |
| aita_berkeley（WIBTA 221 + 回溯争议 727）≤ 1,500 字符 | 2,710 | 948 | 0 | 0 | 948 | 221 + `1_pilot` 200 | `1_gated` 527 | — |
| moral_stories（clean 6,700 + same_gender_other 1,878） | 10,986 | 8,578 | 0 | 3 | 8,575 | 600 | 2a 2,711 | 5,264 |
| ethics justice（每 VP 一条） | 2,749 | 2,105 | 0 | 0 | 2,105 | 300 | 2b 1,600 | 205 |
| 合计 | | | 0 | 10 | **14,079** | **3,772 family / 7,544 prompt** | | |

主要丢弃原因：Scruples 正文过长 1,142、状态动词 136、action 缺失 106；Berkeley 正文过长 1,541、状态动词 249、标题不可解析 88；Moral Stories 代词歧义 2,323；ETHICS "used to" 575、状态动词 76。残留（信息性 flag，不丢）：Reddit 正文的 we / our（Scruples 1,136 / 1,776、Berkeley 307 / 421 条 Wave 1 situation 含）、Moral Stories 并列动词一致偶有漏改。

**人工检查（步 B，筛选前必做）**：`scripts/16` 已按 seed 20261002 写出 `data/annotation/e2c_handcheck_{scruples,aita_berkeley,moral_stories,hendrycks_ethics}.csv`（每源 100 条，三列判定：二人称、两行动互斥、情境无裁决），每源三项全过 ≥ 90% 才进步 D；不过的源先修规则再重建（16 → 17），并重做该源抽检。

## 2. 去重与泄漏

| 检查 | 规则 | 结果（2026-10-05） |
|---|---|---|
| 源项不同源 | 新来源与 DD / MC / VC 无共享 item；脚本断言新 family 的 (source, source_id) 不在现有集合内 | 0 冲突 |
| 对全部现有 family | `dedup_split` 同款 TF-IDF char_wb(3,5) 余弦，取**两个空间的最大值**：联合空间（现有 + 池上拟合）与参照空间（只在现有 2,936 条上拟合，池行投影进去；未见 n-gram 丢失只会抬高余弦）。新 situation 对 2,936 个现有 family（所有 split）≥ 0.9 → 丢；[0.7, 0.9) 列出人工看 | 0 丢；1 对审阅（ms_3M81GAB8… ~ dd_36819（pilot），0.700，内容不同） |
| 只对 dev / test | 同上，单独报：最大余弦、≥ 0.7 条数、top-10 | 最大 0.611，0 条 ≥ 0.7；再用的 sanity 行最大 0.593 |
| 行动对 | 新 (x, y) 与现有 (x, y) ≥ 0.9 **且** situation ≥ 0.7 → 丢；对**每一个** situation ≥ 0.7 的现有 family 检查（不只最近邻）。另列出行动对与 dev / test 对 ≥ 0.9 的池行（主题重叠，situation 低则保留） | 0 丢；4 条主题重叠（bk_z4kw98 ~ dd_1862 0.984 / sit 0.180 等），保留 |
| 池内 | situation ≥ 0.9 → 丢后者（在池上拟合）；AITA 两源另按 post_id 与标题 ≥ 0.9 去重 | 5 + 5；含 mc_C_1177 ~ mc_C_347 0.924（两条 sanity 家族，在 families.jsonl 的小语料上低于 0.9） |
| 0.9 阈值的灵敏度 | 对一条 test DD 情境的手工改写探针：去冠词 0.997、句子重排 0.966 被抓；同义替换 0.842、缩写 + 限定词 0.754、截前半 0.739 不被抓 | 只能抓近逐字复制；轻改写靠源项不同源保证（Reddit / Moral Stories / ETHICS MTurk vs GPT-4 生成的 DD、手写 MC），已写入报告 |
| 层 0 | 本来就在 train | — |

## 3. 筛选协议与争议定义

协议（Mac 侧执行付费部分）：每个候选 family 的 **T1**（"What should you do?"）**两种选项顺序**，**demo 模式 T = 0**，三个 teacher（精确命令 §11 D）。GPT-4o / DeepSeek 从 logprobs 给 p_x，Claude 给字母（单次采样）。每 family 6 次调用。

定义（原文，`scripts/18_select_contested.py` 与 `src/vcd/analysis/contested.py` 必须完全照此实现）：**A family is CONTESTED if the symmetrized majority action differs between at least two teachers, or any teacher's symmetrized p (logprob teachers) lies in [0.2, 0.8].**

实现细节（预先写明，不是事后选择）：

| 项 | 规则 |
|---|---|
| symmetrized p | logprob teacher：两序 p_x 的均值；Claude：两序字母→{0, 1} 的均值 ∈ {0, 0.5, 1} |
| majority action | p_sym > 0.5 → x，< 0.5 → y；= 0.5 未定义。Claude 两序不一致（p_sym = 0.5）即定义中 "p ∈ [0.2, 0.8]" 对采样 teacher 的唯一可能取值，记 contested，计数单列 `claude_order_split` |
| 非答 | 任一 teacher 任一顺序 category ≠ answer → 该 family **既不进 contested 也不进 consensus**，按来源报比例 |
| 未筛 | `--families` 中没有 T1 prompt 的 family（后续波）记 `not_screened`，不算非答；非答率只在已筛 family 上算 |
| 重复行 | 同一 (teacher, prompt) 多行 demo（§11 F 向同一文件追加）→ 取**最后一行**，被覆盖行数报 `duplicate_rows` |
| teacher 标签 | demo 文件行的 `teacher` 必须等于 `--demos` 里的键，否则报错停止（`--trust-file-labels` 才改写） |
| 分源报表 | 每来源 / 每波 / 每人类先验：n、not_screened、非答率、contested rate、多数不同 / 不确定带 / Claude 分裂计数、`flip_only`、`contested_excl_flip_only`；两两多数不一致率；p_sym 直方图 |
| **极端翻转子计数** | `band_exact_flip_<teacher>`：logprob teacher 在带内且 \|p_o1 − p_o2\| ≥ 0.9（两序都自信、方向相反；DeepSeek 的 p_x 几乎只取 0 / 1，其带内 196 / 196 全是翻转，gpt4o 12 / 82）。`flip_only`：family 只因这类翻转进入 contested（无多数不同、无 Claude 分裂、无真正居中的 p）。**规则不变**，这是子计数；**预先声明的灵敏度集** = contested − flip_only（层 0：356 − 113 = 243） |
| 校准 | 同一脚本跑现有 train 的 phase1 T1 demo 复现 356 / 1,469：**已复现**（valid 1,469、contested 356、consensus 1,113、non-answer 24；DD 0.244、MC-high 0.239；两两多数不同 gpt4o–claude 0.080、gpt4o–deepseek 0.057、claude–deepseek 0.060）；MC-low 与 ETHICS justice 应低 |
| logprob teacher 的 p_x 缺失 | category = answer 但 p_x 为 None → 用字母指示 0 / 1 代替并计数 `p_x_missing`，不算非答 |

## 4. 目标规模与训练集组成

| 集 | 组成 | family 数 | 用途 |
|---|---|---|---|
| **E2c-C（contested）** | 层 0 的 356 + 新 contested（按来源可用量全取；超出 1,144 时按来源可用量比例抽样，largest remainder，seed 20261002） | 1,500（≈ E1 train 1,493） | 主条件：3 teacher × 5 seed × O = 15 run |
| **E2c-K（consensus 对照）** | 筛选池 **+ 层 0 对应的现有 train 共识 1,113** 中的 consensus family，`18 --consensus-select-out`：**每来源取与 E2c-C 完全相同的条数**（same seed）；某来源不足时取尽，缺口按 C 的来源比例分给其余有余量的来源（largest remainder），全部耗尽才按可用量分给未在 C 中的来源；分配表写进 `screen_report.md` | 1,500 | 对照：15 run。不做则 E2c-C 与 E1 的差混杂"换数据源" |
| 参照 | E1 的 15 个 O run、R 学生、S_0 | 已有 | 不重训 |

训练文件：被选 family 建 T1 / T3 / T5 / T6 两序 prompt（`17 --families … --variants T1,T3,T5,T6 --waves all`），teacher 在 T3 / T5 / T6 跑 demo（T1 复用筛选结果），`10_build_sft_data.py` 不变，`order_policy stable_one`、`order_seed 20261002` 不变。**已知混杂**：contested family 顺序稳定率更低 → E2c-C 的样例数预计少于 E2c-K；且**耦合在 teacher 上**：family 因 DeepSeek 两序翻转入选时，DeepSeek 恰好在该 family 上给不出 `stable_one` 样例，所以 DeepSeek 学生的 n_examples 会最少（层 0：flip_only 113 条中 DeepSeek 翻转占绝大多数）。manifest 的 `n_examples`、`n_target_tokens` 按 teacher 必报；灵敏度：E2c-C 去掉 flip_only 的版本（§3）与 E2c-K 等样例版本（3 seed）可选。

## 5. 冻结不动的

| 项 | 内容 |
|---|---|
| 评估数据 | dev 150 / test 300 family 与 `data/prompts/{dev,test}_prompts_v2.jsonl`（含 T0）；E2c 的学生只在这两套上评 |
| framing 与 template | `framings.py` v2 stems、`vcd.train.data` template 与 `ASSISTANT_PREFIX`、prompt 格式 |
| 训练 | `configs/train.yaml` 全部超参、`stable_one`、`order_seed`、变体 T1 / T3 / T5 / T6 |
| readout | transformers 后端、fp32、0.9 质量门 |
| teacher | 同三个 snapshot，demo T = 0 |
| 规则 | E1a / E1b（e1_plan §0）；E2 primary / secondary **原样**（456b487）；`13_e1_analysis.py` 默认值 |
| 流程 | dev 只作描述；test 每条件只跑一次；看 test 后不改任何量 |

## 6. 预测与决策规则

记 gap_T = 某 teacher 5 seed 的 seed-mean [agree_own − max_other agree_other]（test，symmetrized 多数行动，与 E1 描述项同算法）；seed-pair null = 同 (teacher, 条件) 5 seed 两两 |Δagree| 的分布（E1 dev：SD 0.005–0.008，q95 ≤ 0.022）。

| 判定 | 规则 | 预测 |
|---|---|---|
| **E2c-E1 门** | E2c-C 每个 O run E1a ≥ 0.95；E1b 六对 ci_lo > 0.5；不过则先修训练，不看下面 | 过 |
| **E2c primary（own > other）** | E2c-C 上 ≥ 2/3 teacher：gap_T > seed-pair null q95 **且** family bootstrap 95% CI 下界 > 0 → **PASS**；1/3 PARTIAL；0/3 FAIL | PASS；E1 原 train 的 gap 为 0 / 0.017 / 0.018 |
| **E2c 归因（对照）** | 每 teacher：gap_T(C) − gap_T(K) 的 family bootstrap CI 下界 > 0，≥ 2/3 → 效应归于争议性而非换源 | 成立；E2c-K 的 gap ≈ 0 |
| **E2 primary / secondary（冻结规则）** | 对 E2c-C 的 15 run 照 e2_plan §2 跑 13，如实报 | D(C) > D(E1)；Δρ 方向改善，不预测必过 |
| 灵敏度（预先声明，描述性） | 同上三项在 "E2c-C − flip_only" 子集训练的版本上重算（只在主结果出来后决定是否训练，训练与否都报告该子集的规模） | 方向相同 |
| 描述项 | agreement、JSD、flip rate、suggestibility 各组、S_0 控制行；分源 contested rate；按 teacher 的 n_examples | — |

## 7. 预算

| 项 | 量 | 调用 | 费用（prompt 中位 ≈ 120 token，AITA ≈ 400） |
|---|---|---|---|
| Wave 1 筛选 | 3,772 × 6 | 22.6k | ≈ $30 |
| 1_gated（门过才跑） | 527 × 6 | 3.2k | ≈ $5 |
| Wave 2a / 2b（条件触发） | 2,711 × 6 / 1,600 × 6 | 16.3k / 9.6k | ≈ $14 / $8 |
| 训练示范 T3 / T5 / T6 | ≈ 2,300 新 family（C + K，减去 T1 已有）× 18 | ≈ 41k | ≈ $45–65 |
| 层 3 改写（若启用） | ≤ 400 条 Gemini | ≤ 1k | < $2 |
| GPU | 30 run × ≈ 0.5 h + readout | | ≈ 23 H100-h |
| 人工 | 转换抽检 4 × 100；Berkeley 回溯 rationale 抽检 50 | | ≈ 6 h |

## 8. 步骤

| # | 侧 | 做什么 | 产出 / 验收 | 状态 |
|---|---|---|---|---|
| 1 | Mac | 人工抽检步 B（§1） | 4 个 CSV 填完，每源 ≥ 90% | 样本已生成，**未判** |
| 2 | Mac | 提交本文件 + 全部 E2c 代码 / 池 / prompt / 抽检 CSV（一个 commit），hash 写入 §9 与 hpc_log | 冻结 | **待提交** |
| 3 | Mac | 三 teacher 筛选 Wave 1（§11 D） | `data/teacher_e2c/*_pool_screen.jsonl` | 未跑（付费） |
| 4 | Mac | 18（§11 E）：分源 rate、校准复现 356、Berkeley 门（§10）、按 §1 触发 1_gated / 2a / 2b / 层 3 | `screen_report.md`；contested_selected ≥ 1,500 或记录缺口 | 校准已复现；等步 3 |
| 5 | Mac | E2c-C / E2c-K 文件（步 E 一并产出）；T3 / T5 / T6 demo；`10` 建 `data/sft_e2c/`；提交 family id 列表与 meta | 30 个 SFT 文件 + meta | 等步 4 |
| 6 | HPC | `STUDENT_SHORT=qwen3-4b-e2c` 训练 30 run；readout train / dev；13 `--split dev --out results/e2c_dev`（描述） | E1a / E1b 过 | — |
| 7 | HPC | test readout 一次；13 `--split test --out results/e2c`；E2c gap 与对照 CI（`19_e2c_analysis.py`，第 6 步前写好并测试） | `results/e2c/summary.md` | — |
| 8 | Mac | 论文表：E1 原 train vs E2c-C vs E2c-K | — | — |

## 9. 看筛选结果之前必须写完的

§0–§10 全部，连同 `16 / 17 / 18`、`contested.py`、`contested_pool.py`、`load_contested_sources.py`、测试、`contested_pool.jsonl`、`contested_pool_T1.jsonl`、`data/annotation/e2c_handcheck_*.csv`，先提交；之后才运行步 3。筛选文件产生后，只允许改动的是 1_gated / 2a / 2b / 层 3 的**是否启用**（按 §1、§10 预先写的触发条件）和 `--exclude-waves 1_pilot`（§10），不允许改争议定义、阈值、训练集规模规则、E2c-K 抽样规则或判定规则。冻结 commit：`<待填：步 2 的 hash>`。

## 10. 风险

| 风险 | 处理 |
|---|---|
| 共识型来源 rate 低于预估，新 contested 不足 1,144 | 2a → 2b → 层 3（≤ 250）→ 如实缩小；不改定义 |
| 分布漂移：AITA 口语、长帖、Moral Stories 带 intention 句；dev / test 全是 DD / MC | E2c-K 对照吸收换源效应；长度上限；论文声明 train–test 分布差 |
| **回溯式 AITA 与前瞻式 stem 错位**（727 条 Berkeley 回溯帖叙述已完成的事，"What should you do?" 时序不合） | Scruples 只用 HYPOTHETICAL；Berkeley 回溯帖 200 条 `1_pilot` 门：(a) 三 teacher answer rate ≥ 0.9；(b) rationale 抽检：从 1_pilot 已答 family 中按 seed 20261002 抽 50 条，每条取 gpt4o o1 的 rationale，**遮住 verdict** 后由人判"回答是否针对前瞻行动（而非评判已做的事）"，"评判已做" ≤ 10%。两条都过才放 `1_gated`；**任一不过 → 727 条全部不进 C 与 K**（`18 --exclude-waves 1_pilot`，1_gated 不建 prompt），转层 3。门的结果与判定表写入 `results/e2c/berkeley_gate.md` |
| contested family 顺序不稳 → 样例数少，且耦合在 teacher 上（§4） | `stable_one` 不变；按 teacher 报 n_examples；flip_only 灵敏度集 |
| Reddit 内容触发拒答 / 敏感 | 非答按类别记录并剔除，不插补；分源报非答率 |
| 许可：Scruples research-only、Berkeley CC-BY-NC-4.0、ETHICS MIT、Moral Stories 上游未标（源自 Social Chemistry CC BY-SA 4.0）、MoralChoice CC-BY-4.0 | `meta.license` 逐行；公开发布只给源 id 与我们的转写；论文引 Lourie 2021、Berkeley D-Lab、Emelin 2021、Hendrycks 2021 |
| 规则转换残留（we / our、并列动词一致、Moral Stories 名字所有格） | 步 B 每源 ≥ 90%；flag 进 `needs_review`；`pronoun_ambiguous` 的 Moral Stories 不入池 |
| 选择效应：按 teacher T1 回答选 family，再用同批 teacher 示范训练 | 设计意图（增强分歧），不是泄漏：评估在未被筛选的 dev / test 上；对照组用同一筛选过程 |

## 11. 逐步命令（Mac 侧，仓库根目录，`source .venv/bin/activate`）

| 步 | 命令 | 产出 | 付费 |
|---|---|---|---|
| A 建池（已跑） | `python scripts/16_build_contested_pool.py` | `data/families/contested_pool.jsonl`（14,079）、`results/e2c/pool_report.md`、`data/annotation/e2c_handcheck_*.csv`；读 HF 缓存，离线加 `--no-hf --scruples-files … --berkeley-file … --moral-stories-file … --ethics-files …` | 否 |
| B 人工抽检 | 填 `data/annotation/e2c_handcheck_{source}.csv` 的三个 pass 列（1 / 0）与 note；每源三列均 ≥ 90% | 同文件 | 否 |
| C Wave 1 prompt（已跑） | `python scripts/17_contested_prompts.py` | `data/prompts/contested_pool_T1.jsonl`：3,772 × 2 = 7,544 | 否 |
| D **筛选（付费，22,632 次，≈ $30）** | `for t in gpt4o claude46 deepseek_v4; do python scripts/04_query_teachers.py --teacher $t --mode demo --variants T1 --prompts data/prompts/contested_pool_T1.jsonl --out data/teacher_e2c/${t}_pool_screen.jsonl; done`（可先 `--limit 60` 冒烟；缓存命中免费，可断点续跑） | `data/teacher_e2c/{gpt4o,claude46,deepseek_v4}_pool_screen.jsonl` | **是** |
| D' 校准（已验证，随时可重跑） | `python scripts/18_select_contested.py --tier0-families data/families/families.jsonl --tier0-prompts data/prompts/train_prompts_v2.jsonl --tier0-demos gpt4o=data/teacher_phase1/gpt4o_train_demo.jsonl,claude46=data/teacher_phase1/claude46_train_demo.jsonl,deepseek_v4=data/teacher_phase1/deepseek_v4_train_demo.jsonl --out /tmp/tier0.jsonl --report results/e2c/calibration_tier0.md` | tier0 consensus 1113 / contested 356 / non_answer 24；flip_only 113 | 否 |
| E 选择 + 对照 | `python scripts/18_select_contested.py --families data/families/contested_pool.jsonl --prompts data/prompts/contested_pool_T1.jsonl --demos gpt4o=data/teacher_e2c/gpt4o_pool_screen.jsonl,claude46=data/teacher_e2c/claude46_pool_screen.jsonl,deepseek_v4=data/teacher_e2c/deepseek_v4_pool_screen.jsonl --tier0-families data/families/families.jsonl --tier0-prompts data/prompts/train_prompts_v2.jsonl --tier0-demos gpt4o=data/teacher_phase1/gpt4o_train_demo.jsonl,claude46=data/teacher_phase1/claude46_train_demo.jsonl,deepseek_v4=data/teacher_phase1/deepseek_v4_train_demo.jsonl --target 1500 --seed 20261002 --out data/families/contested_selected.jsonl --consensus-out data/families/contested_consensus_pool.jsonl --consensus-select-out data/families/consensus_control_selected.jsonl --report results/e2c/screen_report.md`；Berkeley 门不过时加 `--exclude-waves 1_pilot` | `contested_selected.jsonl`（E2c-C，split = train_contested，`meta.screen`）、`consensus_control_selected.jsonl`（E2c-K，split = train_consensus_control）、`contested_consensus_pool.jsonl`、`screen_report.md` + `.csv` | 否 |
| F 1_gated / 2a / 2b（按 §1、§10 触发） | `python scripts/17_contested_prompts.py --waves 1_gated --out data/prompts/contested_pool_T1_gated.jsonl`；`--waves 2a --out data/prompts/contested_pool_T1_wave2a.jsonl`；`--waves 2b --out …_wave2b.jsonl`；再跑 D（`--prompts` 换文件，`--out` 同一文件追加）与 E（`--prompts` 传 `cat` 合并后的 prompt 文件） | 同上 | 是 |
| G 训练 prompt | `python scripts/17_contested_prompts.py --families data/families/contested_selected.jsonl --variants T1,T3,T5,T6 --waves all --out data/prompts/e2c_C_prompts.jsonl`；K：`--families data/families/consensus_control_selected.jsonl --out data/prompts/e2c_K_prompts.jsonl` | `data/prompts/e2c_{C,K}_prompts.jsonl` | 否 |
| H T3 / T5 / T6 demo（付费） | `python scripts/04_query_teachers.py --teacher $t --mode demo --variants T3,T5,T6 --prompts data/prompts/e2c_C_prompts.jsonl --out data/teacher_e2c/${t}_e2c_C_demo.jsonl`（K 同理）；T1 行从筛选 / phase1 文件拼入 | `data/teacher_e2c/*_e2c_{C,K}_demo.jsonl` → `10_build_sft_data.py` | **是** |

未决（需 Mac 侧定，不影响冻结）：(1) Moral Stories 的 x 恒为 normative action，`positive_act` 取 x 为 focus，T5 / T6 只围绕 normative 行动问；(2) 2a 实际只有 2,711 条正向 norm（低于原设想的 4,400），不足时才动负向 norm 的 reserve，需另行声明；(3) E2c 不建 T0（dev / test 的 T0 已冻结，训练集不需要）。
