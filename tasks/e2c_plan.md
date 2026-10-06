# E2c 预注册：争议增强训练池（Contested-Enriched Training Pool）

> 状态：**四源 + mc_low 全部过门：moral_stories 第四轮抽检（seed 20261008，`results/e2c/handcheck_round4_report.md`）二人称 93 / 两行动 99 / 无裁决 100，盲审 25/25。非 MS 四源 Wave 1（1,610 族）+ 2b（1,600 族）筛选完成：新 contested 930 + 层 0 356 = 1,286；moral_stories wave 1（493 族）+ 2a（1,515 族）于 f73f097 之后筛完（rate 10.0%，+199）→ **E2c-C = 1,485、E2c-K = 1,485**（§8 行 4；缺 15，层 3 不启用）；T3 / T5 / T6 示范调用中。分析脚本 `19_e2c_analysis.py` 已于 115027a 提交并在 E1 run 上冒烟复现（2026-10-05）**。本文件 §0–§10 连同代码必须在任何筛选文件被打开前提交（§9）。付费筛选只对已过门的三源 + mc_low 开跑（`data/prompts/contested_pool_T1_wave1_noms.jsonl`，1,610 族 → `data/teacher_e2c/*_pool_screen.jsonl`）；moral_stories wave 1 + 2a 待第四轮（最后一轮）过门后追加（§11 D）。上游：[docs/02](../docs/02_models_and_datasets.md) §3–5、[docs/03](../docs/03_experiments.md) §1–3、[e1_plan](e1_plan.md) §0、[e2_plan](e2_plan.md) §1–2（冻结于 456b487）。付费 API 只在 Mac 侧；本阶段不修改 `data/families/families.jsonl` 与 `data/prompts/{pilot,train,dev,test}_prompts_v2.jsonl`。

## 0. 问题

E1 在 dev 上显示：三个 aligned teacher 的训练标签两两一致 93–96%，teacher 特有信号太小，学生与自己 teacher 的 agreement 不高于与其他 teacher（gpt4o 0.856 / 0.856）。E2c 问：**如果训练示范只来自 teacher 彼此不一致（或不确定）的 family，学生能否学到 teacher 特有的判断，并在同一套冻结的 dev / test 上表现为 own > other（E1）与更强的 profile 继承（E2）？** 对照：等量、来源匹配的共识 family 训练集，排除"换了数据源"这一混杂。

按 §3 的争议定义用 `scripts/18_select_contested.py` 复算现有 train（phase-1 T1 demo，`results/e2c/calibration_tier0.md`）：1,469 个有效 family 中 **356 个（24.2%）已是 contested**（DD 24.4%、MC-high 23.9%）。分解（可重叠）：多数行动不同 154、logprob teacher 落入不确定带 242、Claude 两序分裂 74；其中 **113 个只因两序极端翻转**进入不确定带（`flip_only`，§3）。pilot DD 32%、MC-high 23%、MC-low 0/10（E0 期 teacher 数据，仅参考；dev / test 的 teacher 输出不在本文件引用）。所以 E1 的训练集里 3/4 是共识项。

## 1. 候选池：来源与数量

全部**纯规则**转换（无 LLM），复用 `normalize.py`；每条带 `meta.provenance`、`meta.license` 与源 id。Wave 1 固定；Wave 2 = 2a ∪ 2b，成员**现在已钉死**（seed 20261002），只决定是否启用；Wave 3（LLM 改写）只在前两波不足时启用并限额。

| 层 | 来源 | 候选数 | 导出规则 | 人类分歧信号 | 预期 contested rate | 预期产出 |
|---|---|---|---|---|---|---|
| 0 | **现有 train 的 contested family**（phase1 T1 demo 已有，0 次新调用） | 356 | 已是 Family | — | 100%（已筛） | 356 |
| 1a | **MoralChoice-low**（`sanity` split） | 675 | 已是 Family，只改 split | 无；构造上低歧义 | 3–8%（pilot 0/10） | 20–55；兼作选择脚本的低端校准 |
| 1b | **Scruples Anecdotes HYPOTHETICAL（WIBTA）**，规则干净、≤ 300 词 | 585 | situation = 正文去 edit / TLDR / AITA / meta 句（含 NTA / YTA / ESH / NAH / TA / AH / WAITA / "this post" / "Thanks"）→ 引号外一人称→二人称（大小写不敏感缩写表 + was→were / am→are 一致）→ `split_trailing_question`；**硬性丢弃**：引号外残留 we / our / us、引号内第一人称、首句无先行词（`opens_mid_stream`）、旁观者帖；action_x = `normalize_action(action.description)`（去前导代词 / 副词 / "to"，并列动名词一并还原，首词须为动词原形），action_y = 加 "Do not "（由否定标题造肯定句时去 NPI：anymore / ever / any→some）；action 内 we / our → you / your | 社区投票 `label_scores`（中位 8 票）；少数派占比可算 | 35–50% | 205–290 |
| 1c | **Berkeley AITA（ucberkeley-dlab）**：**只取 WIBTA 前瞻帖**（载入 539，正文 ≤ 1,500 字符）；回溯帖（AITA）整体不入池：第一轮抽检 no-verdict 通过率 62%（1_pilot / 1_gated 联合通过 8/24、8/59），"What should you do?" 对已完成的事不成立，§10 的 Berkeley 门随之作废 | 50 | 标题正则（去标题内引号 / 年龄标签）→ 去前导代词 / 副词 → `degerund_first_word` + 并列动名词 → 肯定 / "Do not " 对；正文清洗 + 一人称→二人称，硬性丢弃规则同 1b | `comments_*_agreement` + 2023 LLM 标签 | 35–50% | 18–25 |
| 1d | **Moral Stories**（demelin），只取 clean 层（`pronoun_same_gender_other` 第二轮起硬性丢弃） | 波次钉死于 seed 20261002（第二轮重建时 Wave 1 600 / 2a 1,827 / reserve 3,609），第四轮重建后**存活 Wave 1 493 / 2a 1,515 / reserve 3,059**（新转干净的 131 条只进 reserve，不重抽） | actor 名→you，代词 / 主谓一致规则；situation = 二人称 situation + intention；x = moral_action、y = immoral_action（`focus_action = x`）；第二轮后的规则：actor 为从句主语时宾语 him / her 不是 actor（"you swipe at him" 保留 him；宾语控制 "ask X to V"、伴随 "with him"、新主语后回退为转换）；限定词 his / her → your（绝不 yours）；he's → you're（been / got / had 前才 you've）；"<Name>'s V-ing" 进行体 → you are；"X's friend <Actor>" 同位语 → "you, X's friend,"；be + V-ing 行动首词 → 原形；并列 VBZ 与 "you" / "You, who" 后 VBZ 原形化；**第四轮规则**（§10）：同字段内任一角色名词（扩充词表 ~460 词）或任何大写非 actor 名字（不限性别词典；the / 大写链 "Kentucky Derby" 除外）之后、以及 actor 非确定主语且 situation / intention 里出现同 / 未知性别他人时，actor 性别代词**硬删不改写**；"X of his" / "<Actor> is a teacher" / "<Actor>, an accountant," / "husband Jeff" 不算他人；单数 their + 关系名词且 actor 为主语 → your；无撇号缩写进缩写表；"<Actor>'s found" → "You have"；状态动词头（is + 非形容词 / 被动、has、lives、feels…）取 so / and 分句为行动，否则丢；they + as a family / together → 硬标；and / then / but 后 VBZ 一律原形（介词短语不算从句）；**硬性丢弃** `plural_refers_to_actor`（they / their 需有生命复数先行词，them 任意复数；VBZ 同形词 needs / wants 不算复数名词）、`pronoun_same_gender_other`、`pronoun_ambiguous`（行内无他人却保留宾语 him）、`possessive_without_noun`（your 后非名词短语、yours 后名词）、`actions_identical`（去括号后 x == y）、`reflexive_residual`、`action_stative_verb` | 无（consensus-by-construction） | 6–15% | 30–75（Wave 1）；+90–225（2a） |
| 1e | **ETHICS justice（impartiality）**，每个 habit VP 取 1 条；habit 为 "used to"（习惯已停止，575 条）、状态动词 VP（含 become，80 条）、VP 含 we / our（147 条）、首词非动词（35 条）**丢弃**；VP 去前导 "to"、截去自带的 ", because" 原因子句、去习惯性时间状语（"every year" 等留在 situation） | Wave 1 300；**2b = 1,600**；48 reserve | 正则 "I usually VP but didn't … because R" → "You usually VP. This time, R."；x = VP，y = "Do not VP" | 无（≥ 4/5 标注一致才保留） | 4–10% | 12–30（Wave 1）；+64–160（2b） |
| 3 | **LLM 改写（last resort）**：Scruples HISTORICAL 少数派 ≥ 0.3、Berkeley 回溯争议帖（727，第一轮后只能走此层）、以及因 we / our 被硬性丢弃的 Reddit 帖 | ≤ 250 条进入训练集 | Gemini（J）只改 situation 为决策前的 ≤ 60 词二人称情境；action 对仍由标题规则导出；校验 `detect_person == second`、无裁决词、J 事实蕴含、人工抽 100 | 同 1b / 1c | 35–50% | ≤ 250 |

不用：Wan Dilemmas_Disagreement（无情境文本）、cnnmon（57 条、无许可）、ETHICS commonsense / desert、AITA 长帖。

**预算与触发**：Wave 1 = 675 + 585 + 50 + 600 + 300 = **2,210 family / 4,420 prompt / 13,260 次调用**；预期新 contested 仅 290–490 + 层 0 的 356 → 远低于目标 **1,500 contested**（新 ≈ 1,144），所以 2a（2,424 × 6 = 14.5k 次，+145–365）与 2b（1,600 × 6 = 9.6k 次，+64–160）**几乎必然触发**，仍不足 → 层 3（≤ 250）。接受池缩小是第一轮抽检后的决定（残留 we / our 的 Reddit 帖不改写、直接丢）。**不降低争议定义凑数**；最终不足 1,200 则如实缩小训练集并在论文声明。

契约性的代码改动（已实现，`python -m pytest -q` 148 passed 1 skipped）：`schemas.Source` 加四个新源，`Split` 加 `pool_contested | train_contested | train_consensus_control`；loader 在 `src/vcd/data/load_contested_sources.py`（`HARD_FLAGS` 决定哪些转换不入池，第一轮抽检后新增 `residual_first_person_plural | quoted_first_person | opens_mid_stream | bystander_post | plural_refers_to_actor`；`LICENSES` 写入 `meta.license`）；去重 / 泄漏在 `src/vcd/data/contested_pool.py`；§3 规则在 `src/vcd/analysis/contested.py`；脚本 `16_build_contested_pool.py`（建池 + 去重 + 分波 + 人工抽检样本 + 报告）、`17_contested_prompts.py`（任意 family 文件建 prompt；E0 路径 01–09 不动）、`18_select_contested.py`（§3 定义 + 分源报表 + E2c-C / E2c-K 组成 + 层 0 校准）。测试 `tests/test_contested.py`（23 个，含第一轮每类失败模式的回归用例）。

实际建池结果（`results/e2c/pool_report.md`，第三轮抽检后按第四轮规则重建，2026-10-05；括号内为第二轮后 / 第一轮后；Moral Stories 以外各源的 family_id、situation、两行动、meta.wave 与 T1 prompt 行与第二轮后逐字节相同，`scripts/16 --pin-waves`（默认读旧池）保证存活族波次不变，只有 `meta.leak_max_cosine` 因 TF-IDF 在新池上重拟合而变动 ≤ 0.0062）：

| 来源 | 载入 | 规则干净 | 泄漏丢弃 | 池内重复 | 入池 | Wave 1 | 2a / 2b | reserve |
|---|---|---|---|---|---|---|---|---|
| mc_low | 676 | 676 | 0 | 1 | 675 | 675 | — | — |
| scruples HYPOTHETICAL ≤ 300 词 | 3,195 | 585（1,782） | 0 | 0 | 585（1,776） | 585 | — | — |
| aita_berkeley（只 WIBTA）≤ 1,500 字符 | 539（2,710） | 50（948） | 0 | 0 | 50（948） | 50 | — | — |
| moral_stories（只 clean） | 10,997（10,989） | 5,069（6,038 / 7,772） | 0 | 2 | 5,067（6,036 / 7,770） | 493（600） | 2a 1,515（1,827） | 3,059（3,609；含新转干净 131） |
| ethics justice（每 VP 一条） | 2,749 | 1,948（2,105） | 0 | 0 | 1,948（2,105） | 300 | 2b 1,600 | 48 |
| 合计 | | | 0 | 3 | **8,325**（9,294 / 11,028） | **2,103 family / 4,206 prompt**（2,210 / 4,420） | | |

新增硬性 flag 的丢弃数（可重叠）：Scruples `residual_first_person_plural` 2,254、`quoted_first_person` 429、`opens_mid_stream` 69、`bystander_post` 14、`action_first_word_not_verb` 11；Berkeley WIBTA `residual_first_person_plural` 446、`quoted_first_person` 71、`opens_mid_stream` 4；Moral Stories `plural_refers_to_actor` 1,236（第二轮后 1,234）、`pronoun_same_gender_other` **5,195**（第二轮 2,141；第四轮起与性别词典无关，并吞并原 `pronoun_ambiguous` 2,324 的角色名词情形）、**第四轮新增** `possessive_without_noun` 151、`pronoun_ambiguous` 10（行内无他人的保留宾语）、`actions_identical` 1、`reflexive_residual` 1、`residual_actor_name` 68、`gender_unknown` 41；ETHICS `residual_first_person_plural` 147、`action_first_word_not_verb` 35、`action_stative_verb` 80（含 become）。原有：Scruples 正文过长 1,133、状态动词 139、action 缺失 106；ETHICS "used to" 575。一人称单数残留（`residual_first_person`）从 109 降到 1。Moral Stories 第三轮判定的 18 条失败行重建后 14 条被硬性丢弃（13 `pronoun_same_gender_other`、1 `pronoun_ambiguous`），4 条文本已修正（"You have found out"、"your coworkers"、状态动词头改取 so 分句、puppy 边界行）；三轮共 229 条通过行中 195 条仍在池内（第一轮 61/71、第二轮 67/76、第三轮 67/82，掉的多为他人代词碰巧保留的行）。

**人工检查（步 B，筛选前必做）**：第一轮（seed 20261002，`data/annotation/e2c_handcheck_round1/`，报告 `results/e2c/handcheck_round1_report.md`）三项联合通过率 scruples 19% / aita_berkeley 20% / moral_stories 71% / hendrycks_ethics 89%，全部未过；主因已按上表改为硬性丢弃或修规则。第二轮（seed 20261006，存档 `data/annotation/e2c_handcheck_round2/`，报告 `results/e2c/handcheck_round2_report.md`）：scruples 95 / 96 / 98、aita_berkeley 100 / 100 / 100（n = 46）、hendrycks_ethics 100 / 100 / 100 **过门**；moral_stories 79 / 96 / 100，**二人称未过**（带 `pronoun_same_gender_other` 的 18 行仅 4 过；其余 82 行 75 过，失败为他人代词被改成 you、无 "you and X" 触发的 they / their）。三列判定：二人称、两行动互斥、情境无裁决；每源三列各 ≥ 90% 才进步 D。第三轮（seed 20261007，存档 `data/annotation/e2c_handcheck_round3/`，报告 `results/e2c/handcheck_round3_report.md`）：moral_stories 83 / 99 / 100，**二人称未过**（17 个失败全在当时 flag 之外：他人由角色名词 / 词典外名字引入后被改成 you 10 行、actor 残留 their / shes / him 5 行等）。第四轮：规则按 §10 修复、池重建（Moral Stories 6,036 → 5,067，波次钉死），`scripts/16`（默认 `--handcheck-sources moral_stories --handcheck-waves 1:50,2a:50 --handcheck-seed 20261008`，排除前三轮 300 个已判 id）写出 `data/annotation/e2c_handcheck_moral_stories.csv` 100 条（wave 1 50 / 2a 50，reserve 不入筛选故不抽，`needs_review` 全空，文本与池逐字节相同），**未判**；三源已判表原位保留。

## 2. 去重与泄漏

| 检查 | 规则 | 结果（2026-10-05） |
|---|---|---|
| 源项不同源 | 新来源与 DD / MC / VC 无共享 item；脚本断言新 family 的 (source, source_id) 不在现有集合内 | 0 冲突 |
| 对全部现有 family | `dedup_split` 同款 TF-IDF char_wb(3,5) 余弦，取**两个空间的最大值**：联合空间（现有 + 池上拟合）与参照空间（只在现有 2,936 条上拟合，池行投影进去；未见 n-gram 丢失只会抬高余弦）。新 situation 对 2,936 个现有 family（所有 split）≥ 0.9 → 丢；[0.7, 0.9) 列出人工看 | 0 丢；1 对审阅（ms_3M81GAB8… ~ dd_36819（pilot），0.700，内容不同） |
| 只对 dev / test | 同上，单独报：最大余弦、≥ 0.7 条数、top-10 | 最大 0.611，0 条 ≥ 0.7；再用的 sanity 行最大 0.593 |
| 行动对 | 新 (x, y) 与现有 (x, y) ≥ 0.9 **且** situation ≥ 0.7 → 丢；对**每一个** situation ≥ 0.7 的现有 family 检查（不只最近邻）。另列出行动对与 dev / test 对 ≥ 0.9 的池行（主题重叠，situation 低则保留） | 0 丢；4 条主题重叠（bk_z4kw98 ~ dd_1862 0.984 / sit 0.180 等），保留 |
| 池内 | situation ≥ 0.9 → 丢后者（在池上拟合）；AITA 两源另按 post_id 与标题 ≥ 0.9 去重 | 3 + 0；含 mc_C_1177 ~ mc_C_347 0.918（两条 sanity 家族，在 families.jsonl 的小语料上低于 0.9）、两对 Moral Stories |
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
| **E2c primary（own > other）** | E2c-C 上 ≥ 2/3 teacher：gap_T > seed-pair null q95 **且** family bootstrap 95% CI 下界 > 0 → **PASS**；1/3 PARTIAL；0/3 FAIL | PASS；E1 原 train 的 gap：dev 0.000 / 0.017 / 0.018，test 0.002 / 0.020 / 0.009（gpt4o / claude46 / deepseek_v4，`19` 在 E1 的 15 个 O run 上复算，与 results/e1* 逐行一致） |
| **E2c 归因（对照）** | 每 teacher：gap_T(C) − gap_T(K) 的 family bootstrap CI 下界 > 0，≥ 2/3 → 效应归于争议性而非换源 | 成立；E2c-K 的 gap ≈ 0 |
| **E2 primary / secondary（冻结规则）** | 对 E2c-C 的 15 run 照 e2_plan §2 跑 13，如实报 | D(C) > D(E1)；Δρ 方向改善，不预测必过 |
| 灵敏度（预先声明，描述性） | 同上三项在 "E2c-C − flip_only" 子集训练的版本上重算（只在主结果出来后决定是否训练，训练与否都报告该子集的规模） | 方向相同 |
| 描述项 | agreement、JSD、flip rate、suggestibility 各组、S_0 控制行；分源 contested rate；按 teacher 的 n_examples | — |

## 7. 预算

| 项 | 量 | 调用 | 费用（prompt 中位 ≈ 120 token，AITA ≈ 400） |
|---|---|---|---|
| Wave 1 筛选 | 2,210 × 6 | 13.3k | ≈ $18 |
| Wave 2a / 2b（条件触发，几乎必然） | 2,424 × 6 / 1,600 × 6 | 14.5k / 9.6k | ≈ $12 / $8 |
| 训练示范 T3 / T5 / T6 | ≈ 2,300 新 family（C + K，减去 T1 已有）× 18 | ≈ 41k | ≈ $45–65 |
| 层 3 改写（若启用） | ≤ 400 条 Gemini | ≤ 1k | < $2 |
| GPU | 30 run × ≈ 0.5 h + readout | | ≈ 23 H100-h |
| 人工 | 转换抽检三轮（第一轮 4 × 100 已判；第二轮 3 × 100 + 46 已判；第三轮 moral_stories 100 已判） | | ≈ 7 h |

## 8. 步骤

| # | 侧 | 做什么 | 产出 / 验收 | 状态 |
|---|---|---|---|---|
| 1 | Mac | 人工抽检步 B（§1） | 4 个 CSV 填完，每源 ≥ 90% | 第一轮未过（19 / 20 / 71 / 89%）；第二轮 scruples / aita_berkeley / ethics 过门，moral_stories 二人称 79% 未过；Moral Stories 规则已修、池已重建（9,294）；第三轮 moral_stories **二人称 83% 仍未过**（99 / 100 / 联合 82；`results/e2c/handcheck_round3_report.md`，25 行盲审复核 25/25 一致）；第四轮规则已修、池已重建（8,325），第四轮 **过门**：二人称 93 / 两行动 99 / 无裁决 100（联合 92；wave 1 / 2a 分别 94 / 92；盲审 25/25；`results/e2c/handcheck_round4_report.md`，残余缺陷类型表在该文件）。四源 + mc_low 全部过门 |
| 2 | Mac | 提交本文件 + 全部 E2c 代码 / 池 / prompt / 抽检 CSV（一个 commit），hash 写入 §9 与 hpc_log | 冻结 | 已提交：0ae135c（池 v2，非 MS 筛选开跑前）→ 5abcb31（第三轮）→ **f73f097（第四轮过门，MS 筛选开跑前）**；`19` 于 115027a |
| 3 | Mac | 三 teacher 筛选 Wave 1（§11 D） | `data/teacher_e2c/*_pool_screen.jsonl` | **已完成**：已过门三源 + mc_low（Wave 1，1,610 族，`contested_pool_T1_wave1_noms.jsonl`）+ 2b（hendrycks 1,600 族，`contested_pool_T1_wave2b.jsonl`），每 teacher 6,420 行；非答 7 + 0。moral_stories wave 1（493 族，`contested_pool_T1_wave1_ms.jsonl`）+ 2a（1,515 族，`contested_pool_T1_wave2a.jsonl`）**已完成**（4,016 条 × 3 teacher，$9.6；每 teacher 10,436 行；MS 非答 15） |
| 4 | Mac | 18（§11 E）：分源 rate、校准复现 356、按 §1 触发 2a / 2b / 层 3 | `screen_report.md`；contested_selected ≥ 1,500 或记录缺口 | 校准复现 356 / 1,113 / 24；分源 rate：scruples 37.5%、aita 30.0%、hendrycks wave 1 36.3% / 2b 36.6%、mc_low 0.4%；新 contested 930（majority_differ 261、uncertain_band 702、claude_order_split 200、flip_only 372）；**合计 1,286**（`results/e2c/screen_report_wave1_2b.md`）。**偏离记录**：2b 在 2a 之前开跑——2a 全部为 moral_stories，被步 B 的门卡住，而 §1 的 2a → 2b 只是按来源可用量排的顺序，成员均已钉死（seed 20261002），不影响选择规则。MS 试筛 6.1% → 实际 10.0%（199 / 1,993；wave 1 48 / 493，2a 156 / 1,505）。**最终 E2c-C = 1,485**（层 0 356 + 新 1,129 = hendrycks 695、scruples 217、moral_stories 199、aita 15、层 0 DD 245 / MC 114；缺 15，未达 1,144 新增故全取不抽样）；**K = 1,485**，按来源精确匹配（consensus 池 5,180）；`results/e2c/screen_report.md`。理由构成：仅 uncertain_band 683、含 majority_differ 510、仅 claude_order_split 138；flip_only 553（灵敏度集 = 932）。**簿记偏离**：hendrycks 的 `meta.wave` 在第三轮重建时被重抽（当时无钉波，RNG 流随 MS 变动），与实际筛选所用 prompt 文件相差 47 族（标 2b 未筛 44、标 reserve 已筛 47、标 wave 1 未筛 3）；筛选覆盖 1,900 / 1,948，选择全取、K 按来源抽，波次标签不参与，结果不受影响 |
| 5 | Mac | E2c-C / E2c-K 文件（步 E 一并产出）；T3 / T5 / T6 demo；`10` 建 `data/sft_e2c/`；提交 family id 列表与 meta | 30 个 SFT 文件 + meta | 管线已就位并 dry run（1,286 + 1,286）：`17` → `17b new-prompts`（只为 pool family 的 T3 / T5 / T6 调用；层 0 四个 variant 与 pool T1 复用已有示范，prompt 文本逐条一致）→ `04` → `17b assemble` → `10 --out-dir data/sft_e2c`（C）/ `data/sft_e2ck`（K）；示范调用中：C 6,774 + K 7,194 条新 prompt × 3 teacher（≈ 4.2 万次） |
| 6 | HPC | 在 compute 分配里用 §11 I 的命令重建 `data/sft_e2c/`、`data/sft_e2ck/`（sha256 对 meta）；C：`STUDENT_SHORT=qwen3-4b-e2c DATA_LIST=data/sft_e2c/runs.txt sbatch --array=0-14%8 slurm/train.sbatch`；K：`STUDENT_SHORT=qwen3-4b-e2ck DATA_LIST=data/sft_e2ck/runs.txt …`（run id 前缀随 STUDENT_SHORT，不与 E1 撞名）；readout train / dev；13 对两个 student 目录各跑 `--split dev`（`--out results/e2c_dev/{C,K}`）；`19 --split dev --out results/e2c_dev`（描述） | E1a / E1b 过 | 等步 5 |
| 7 | HPC | test readout 一次；13 `--split test`（`--out results/e2c/{C,K}`）；`19 --split test --out results/e2c --frozen-commit f73f097`（gap_T、seed-pair null、配对 family bootstrap、C − K 归因；已于 115027a 写好，E1 run 上冒烟复现 results/e1*） | `results/e2c/e2c_summary.md` | 等步 6 |
| 8 | Mac | 论文表：E1 原 train vs E2c-C vs E2c-K | — | — |

## 9. 看筛选结果之前必须写完的

§0–§10 全部，连同 `16 / 17 / 18`、`contested.py`、`contested_pool.py`、`load_contested_sources.py`、测试、`contested_pool.jsonl`、`contested_pool_T1.jsonl`、`data/annotation/e2c_handcheck_*.csv`，先提交；之后才运行步 3。筛选文件产生后，只允许改动的是 2a / 2b / 层 3 的**是否启用**（按 §1 预先写的触发条件），不允许改争议定义、阈值、训练集规模规则、E2c-K 抽样规则或判定规则。冻结 commit：0ae135c（§0–§10 与池 v2，非 moral_stories 筛选开跑前）→ 5abcb31（第三轮状态）→ **f73f097**（第四轮过门、池 8,325，moral_stories 筛选开跑前）；`19` / `e2c_metrics.py` 于 115027a（任何 E2c 学生训练之前）。筛选开跑后发生的改动只有两类，均已记录：Moral Stories 的转换规则与其存活族（非 MS 四源的族与 prompt 逐行 byte-identical，第四轮报告有证明）；2b 先于 2a 启用（§8 行 4）。

## 10. 风险

| 风险 | 处理 |
|---|---|
| 共识型来源 rate 低于预估，新 contested 不足 1,144 | 2a → 2b → 层 3（≤ 250）→ 如实缩小；不改定义。**实际**：Reddit 两源 rate 高（30–38%）但硬性丢弃后只剩 635 族；ETHICS 36.6% 全部用尽（reserve 48）；mc_low 0.4%；2b 先于 2a 启用（2a = moral_stories 未过门）；新 contested 930 + 356 = 1,286，缺 214。moral_stories 第四轮过门 → 筛 wave 1 + 2a；层 3 不启用；最终规模如实报告 |
| 分布漂移：AITA 口语、长帖、Moral Stories 带 intention 句；dev / test 全是 DD / MC | E2c-K 对照吸收换源效应；长度上限；论文声明 train–test 分布差 |
| **回溯式 AITA 与前瞻式 stem 错位**（Berkeley 727 条回溯帖叙述已完成的事及其后果，"What should you do?" 时序不合） | **已兑现**：第一轮抽检 Berkeley 回溯帖 no-verdict 通过率 62%（1_gated 26/59 失败），不再设门；Scruples 只用 HYPOTHETICAL，Berkeley 只用 WIBTA（`load_aita_berkeley(prospective_only=True)`，`scripts/16` 默认），回溯帖只可能经层 3 改写进入 |
| contested family 顺序不稳 → 样例数少，且耦合在 teacher 上（§4） | `stable_one` 不变；按 teacher 报 n_examples；flip_only 灵敏度集 |
| Reddit 内容触发拒答 / 敏感 | 非答按类别记录并剔除，不插补；分源报非答率 |
| 许可：Scruples research-only、Berkeley CC-BY-NC-4.0、ETHICS MIT、Moral Stories 上游未标（源自 Social Chemistry CC BY-SA 4.0）、MoralChoice CC-BY-4.0 | `meta.license` 逐行；公开发布只给源 id 与我们的转写；论文引 Lourie 2021、Berkeley D-Lab、Emelin 2021、Hendrycks 2021 |
| 规则转换残留 | 第一轮抽检后改为硬性丢弃：引号外 we / our / us、引号内第一人称、首句无先行词、旁观者帖、Moral Stories 复数代词指 actor + 他人；行动首词须为动词原形；缩写表大小写不敏感 + was / am 一致；代价是池缩至 11,028（Reddit 两源 635）。步 B 第二轮三源过门；Moral Stories `pronoun_same_gender_other` 第二轮 14/18 不过 → **已改硬性**，并修：actor 为主语时宾语 him / her 不再改成 you、they / their 需有生命复数先行词（VBZ 同形词不算）、his / her 限定词 → your、's → you're、be + V-ing → 原形、并列 / "you" 后 VBZ 原形化、去括号后 x == y 丢弃、反身代词残留丢弃；代价是 Moral Stories 7,770 → 6,036（池 9,294），2a 2,424 → 1,827。第三轮只抽 moral_stories：二人称 83%（75 → 79 → 83）仍不过，17 个失败全在现有 flag 之外（他人由角色名词 / 词典外名字引入后被改成 you 10 行、actor 残留 their / shes / him 5 行等）。**试筛**（2026-10-05，`results/e2c/ms_pilot_report.md`，`data/teacher_e2c/ms_pilot/`）：第三轮判为干净的 82 族过一遍 §11 D 的筛选（492 次，$0.39）→ contested 5 / 82 = 6.1%（wave 1 1/9、2a 2/22、reserve 2/51；majority_differ 4），即 wave 1 + 2a 共 2,427 族预计只产 150–235 条 contested。**处置**：按第三轮复核建议再修一轮（第四轮；判官项 (1) 改为与性别词典无关的硬性丢弃），新 seed 抽 wave 1 50 + 2a 50（排除前三轮 300 个已判 id）；过门则筛 wave 1 + 2a（≈ $18）并入选择；**第四轮仍 < 90% 则 moral_stories 整体不入池，不启用层 3，以 1,286 如实缩小**。**第四轮已修**（2026-10-05，复核项 (1)–(7)）：(1) 同字段内任一角色名词或任何大写非 actor 名字（不依赖性别词典）之后、或 actor 非确定主语且前文字段有同 / 未知性别他人时，actor 性别代词硬删（`pronoun_same_gender_other`，2,141 → 5,195）；(2) 单数 their 只在"their + actor 关系名词、actor 为主语、无复数先行词"时映 your，否则留给 `plural_refers_to_actor`；(3) shes / hes / theyre / youre / im / ive / dont 等无撇号缩写进缩写表（大小写不敏感）；(4) 主语位的 "<Actor>'s found" → "You have"，并后检 your 必接名词短语、yours 不接名词（`possessive_without_noun` 151，硬）；(5) 状态动词头（is + 非形容词或被动、has、lives、feels…）不命令式化，取 so / and 分句的动作动词为行动，无则 `action_stative_verb` 丢；(6) they / their + as a family / together / the two of you 且无复数先行词 → `plural_refers_to_actor`；(7) and / then / but 后 VBZ 一律原形（"after work" 等介词短语不再当从句；并列 "and is / are" → be；"you only has" → have）。代价：Moral Stories 6,036 → 5,067（wave 1 493 / 2a 1,515，钉死波次中存活者），池 9,294 → 8,325；第三轮 18 条失败行 14 丢 4 修，三轮 229 条通过行保留 195（层 3 ≤ 250 条按 Reddit 源 37% 的 rate 至多再得 ≈ 90 条 contested，却把 LLM 改写文本引入训练集并需再一轮抽检，不值） |
| 选择效应：按 teacher T1 回答选 family，再用同批 teacher 示范训练 | 设计意图（增强分歧），不是泄漏：评估在未被筛选的 dev / test 上；对照组用同一筛选过程 |

## 11. 逐步命令（Mac 侧，仓库根目录，`source .venv/bin/activate`）

| 步 | 命令 | 产出 | 付费 |
|---|---|---|---|
| A 建池（已跑，第四轮） | `python scripts/16_build_contested_pool.py`（默认 `--pin-waves auto` 读旧 `--out` 钉住存活族的波次、`--handcheck-sources moral_stories --handcheck-waves 1:50,2a:50 --handcheck-seed 20261008 --handcheck-exclude …round1,…round2,…round3`；`--handcheck-sources all` 会覆盖已判的三源表，勿用；`--pin-waves ''` 才重抽波次；Berkeley 只 WIBTA，`--berkeley-retrospective` 才载入回溯帖） | `data/families/contested_pool.jsonl`（8,325）、`results/e2c/pool_report.md`、`data/annotation/e2c_handcheck_moral_stories.csv`；读 HF 缓存，离线加 `--no-hf --scruples-files … --berkeley-file … --moral-stories-file … --ethics-files …` | 否 |
| B 人工抽检（第四轮，最后一轮） | 只判 `data/annotation/e2c_handcheck_moral_stories.csv`（100 行：wave 1 50 + 2a 50）的三个 pass 列（1 / 0）与 note；三列均 ≥ 90%；前三轮判定表存档于 `data/annotation/e2c_handcheck_round{1,2,3}/`（三个过门源的第二轮表亦原位保留）；不过门则按 §10 弃 moral_stories | 同文件 | 否 |
| C Wave 1 prompt（已跑） | `python scripts/17_contested_prompts.py`（默认 `--waves 1`） | `data/prompts/contested_pool_T1.jsonl`：2,103 × 2 = 4,206（moral_stories 493 / 986，第四轮重建后） | 否 |
| D **筛选（付费，13,260 次，≈ $18）** | `for t in gpt4o claude46 deepseek_v4; do python scripts/04_query_teachers.py --teacher $t --mode demo --variants T1 --prompts data/prompts/contested_pool_T1.jsonl --out data/teacher_e2c/${t}_pool_screen.jsonl; done`（可先 `--limit 60` 冒烟；缓存命中免费，可断点续跑）。第二轮后分两步：先用过滤掉 moral_stories 的 `data/prompts/contested_pool_T1_wave1_noms.jsonl`（1,610 族 / 3,220 条，≈ $13）；moral_stories 第四轮过门后 `python scripts/17_contested_prompts.py --sources moral_stories --out data/prompts/contested_pool_T1_wave1_ms.jsonl`（493 族 / 986 条）再以同一 `--out` 追加，2a 1,515 族同理 | `data/teacher_e2c/{gpt4o,claude46,deepseek_v4}_pool_screen.jsonl` | **是** |
| D' 校准（已验证，随时可重跑） | `python scripts/18_select_contested.py --tier0-families data/families/families.jsonl --tier0-prompts data/prompts/train_prompts_v2.jsonl --tier0-demos gpt4o=data/teacher_phase1/gpt4o_train_demo.jsonl,claude46=data/teacher_phase1/claude46_train_demo.jsonl,deepseek_v4=data/teacher_phase1/deepseek_v4_train_demo.jsonl --out /tmp/tier0.jsonl --report results/e2c/calibration_tier0.md` | tier0 consensus 1113 / contested 356 / non_answer 24；flip_only 113 | 否 |
| E 选择 + 对照 | `cat data/prompts/contested_pool_T1_wave1_noms.jsonl data/prompts/contested_pool_T1_wave2b.jsonl data/prompts/contested_pool_T1_wave1_ms.jsonl data/prompts/contested_pool_T1_wave2a.jsonl > data/prompts/contested_pool_T1_screened.jsonl`；`python scripts/18_select_contested.py --families data/families/contested_pool.jsonl --prompts data/prompts/contested_pool_T1_screened.jsonl --demos gpt4o=data/teacher_e2c/gpt4o_pool_screen.jsonl,claude46=data/teacher_e2c/claude46_pool_screen.jsonl,deepseek_v4=data/teacher_e2c/deepseek_v4_pool_screen.jsonl --tier0-families data/families/families.jsonl --tier0-prompts data/prompts/train_prompts_v2.jsonl --tier0-demos gpt4o=data/teacher_phase1/gpt4o_train_demo.jsonl,claude46=data/teacher_phase1/claude46_train_demo.jsonl,deepseek_v4=data/teacher_phase1/deepseek_v4_train_demo.jsonl --target 1500 --seed 20261002 --out data/families/contested_selected.jsonl --consensus-out data/families/contested_consensus_pool.jsonl --consensus-select-out data/families/consensus_control_selected.jsonl --report results/e2c/screen_report.md` | `contested_selected.jsonl`（E2c-C，split = train_contested，`meta.screen`）、`consensus_control_selected.jsonl`（E2c-K，split = train_consensus_control）、`contested_consensus_pool.jsonl`、`screen_report.md` + `.csv` | 否 |
| F 2a / 2b（按 §1 触发） | `python scripts/17_contested_prompts.py --waves 2a --out data/prompts/contested_pool_T1_wave2a.jsonl`；`--waves 2b --out …_wave2b.jsonl`；再跑 D（`--prompts` 换文件，`--out` 同一文件追加）与 E（`--prompts` 传 `cat` 合并后的 prompt 文件） | 同上 | 是 |
| G 训练 prompt | `python scripts/17_contested_prompts.py --families data/families/contested_selected.jsonl --variants T1,T3,T5,T6 --waves all --out data/prompts/e2c_C_prompts.jsonl`；K：`--families data/families/consensus_control_selected.jsonl --out data/prompts/e2c_K_prompts.jsonl` | `data/prompts/e2c_{C,K}_prompts.jsonl` | 否 |
| H T3 / T5 / T6 demo（付费） | `python scripts/17b_e2c_demo_inputs.py new-prompts --prompts data/prompts/e2c_C_prompts.jsonl --out data/prompts/e2c_C_new_prompts.jsonl`（层 0 family 的四个 variant 与 pool family 的 T1 已有示范，只剩 pool family 的 T3 / T5 / T6）；`python scripts/04_query_teachers.py --teacher $t --mode demo --variants T3,T5,T6 --prompts data/prompts/e2c_C_new_prompts.jsonl --out data/teacher_e2c/${t}_e2c_C_new_demo.jsonl`；`python scripts/17b_e2c_demo_inputs.py assemble --prompts data/prompts/e2c_C_prompts.jsonl --teacher $t --sources data/teacher_phase1/${t}_train_demo.jsonl,data/teacher_e2c/${t}_pool_screen.jsonl,data/teacher_e2c/${t}_e2c_C_new_demo.jsonl --out data/teacher_e2c/${t}_e2c_C_demo.jsonl`（每条 prompt 恰一行，缺则报错）；K 同理 | `data/teacher_e2c/*_e2c_{C,K}_demo.jsonl` | **是**（≈ 3.5 万次，≈ $13） |
| I SFT 文件 | `python scripts/10_build_sft_data.py --teacher $t --versions O --prompts data/prompts/e2c_C_prompts.jsonl --demos data/teacher_e2c/${t}_e2c_C_demo.jsonl --out-dir data/sft_e2c`；K：`--prompts data/prompts/e2c_K_prompts.jsonl --demos data/teacher_e2c/${t}_e2c_K_demo.jsonl --out-dir data/sft_e2ck`；`ls data/sft_e2c/*.jsonl > data/sft_e2c/runs.txt`（K 同理）。`stable_one`、`order_seed` 不变；jsonl 不入库，只提交 `.meta.json`（含 sha256）与 runs.txt，HPC 侧同一命令重建后核对 sha256 | `data/sft_e2c{,k}/{teacher}_O_s{1..5}.jsonl` + meta | 否 |

未决（需 Mac 侧定，不影响冻结）：(1) Moral Stories 的 x 恒为 normative action，`positive_act` 取 x 为 focus，T5 / T6 只围绕 normative 行动问；(2) 2a 第四轮重建后为 1,515 条正向 norm（第二轮后 2,424、原设想 4,400），负向 norm 的 reserve 不动；(3) E2c 不建 T0（dev / test 的 T0 已冻结，训练集不需要）。
