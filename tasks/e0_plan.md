# E0 实现计划（给自己）

目标：跑通 [03_experiments.md §1](../docs/03_experiments.md) 的七个 E0 子项。顺序：先做不需要 GPU、不花钱的部分（数据、framings、解析、统计），再接 teacher API，最后接 HAIC 上的 B / J（vLLM，OpenAI 兼容接口）。

## 文件树

```
CS329X_Project/
├── docs/                          01–04 研究文档
├── tasks/e0_plan.md               本文件
├── configs/
│   ├── models.yaml                teacher / rewriter / judge 的 provider、model id、价格、endpoint
│   └── e0.yaml                    pilot 规模、k、temperature、并发、E0 门槛、路径
├── data/
│   ├── raw/                       HF 原始文件（不进 git）
│   ├── families/families.jsonl    统一后的 family + split
│   ├── prompts/                   pilot_prompts.jsonl；t0_texts.jsonl（J 生成）
│   ├── teacher/                   {teacher}_{mode}.jsonl 原始回答
│   ├── rewrites/                  records / rewrites / checks
│   ├── annotation/                人工标注表导出与回收
│   └── cache/llm_cache.sqlite     LLM 调用缓存（不进 git）
├── results/e0/                    表格与 report.md
├── src/vcd/
│   ├── schemas.py                 Family / Prompt / TeacherResponse
│   ├── config.py  io.py  stats.py
│   ├── data/      load_daily_dilemmas, load_moralchoice, load_valueconsistency, normalize, dedup_split, framings
│   ├── llm/       base（请求/响应/重试/并发）, cache, openai_compat（GPT、DeepSeek、vLLM）, anthropic_client, registry
│   ├── teacher/   parse（Answer/Rationale → category/letter/p）, query（demo / profile 两种 mode）, profile（p_sym, r, δ, reliability, 跨 teacher）
│   ├── rewrite/   extract_record（J）, rewrite（B）, check（J + 规则）
│   ├── readout/   logit_vs_sample（E0.7）
│   └── analysis/  e0_answer_rates, e0_profiles, e0_rewrite_stats, annotation_sheets, report
├── scripts/01…09                  每步一个薄 CLI，按编号顺序跑
└── tests/
```

## 步骤与状态

- [x] 环境：`.venv`（py3.12，uv），openai 1.x，anthropic 1.x
- [x] 原始数据到 `data/raw`，字段核对
- [x] 01 families：DD 1,360 + MC 680 high / 687 low + VC 英文 U.S. 原题 210 → `families.jsonl`
- [x] 02 splits：TF-IDF 去重（丢 1）；pilot（DD 60 + MC-high 30 + MC-low 10 + VC probe 20）；dev 150 / test 300 / 其余 train；第三人称情境 → excluded
- [x] 03 framings：T1 / T2 / T4 模板；T3 规则转第一人称（标 `t3_auto`，审核表 `data/annotation/t3_review_pilot.csv`）；T0 需 J（03b）
- [x] 04 teacher 查询：demo + profile；GPT-4.1 全量 pilot 已跑（840 + 840 调用，约 $1）；Claude 4.6 全量在跑（约 $12）；DeepSeek 改用 `deepseek-v4-pro`（API 已无 V3，`deepseek-chat` 别名指向 flash）
- [x] 05 E0.1–E0.4 分析表：`results/e0/e0_summary.md`；GPT-4.1 结果见下
- [x] 06 E0.6 改写审计：三个主 teacher × 300 条 × F / C 完成（B = Together Llama-3.3-70B，J = Together GLM-5.3-Flash）；过滤率 1% 到 9%，choice 100%；见 `docs/E0_results.md` §10
- [ ] 07 E0.7 readout 校验：代码就位，需 vLLM；与学生评估栈一起在 HAIC 做
- [~] 08 人工标注表：v2 framing 等价表（含 T0，500 行）、T3 审核表、第三人称转换抽检表、三份改写审计表（各约 550 行）都在 `data/annotation/v2/`；需两位标注者
- [x] 09 pilot report：`results/e0_v2/report.md`

## 数据事实（决定 loader 怎么写）

- DD：`dilemma_situation` 二人称，末句是 "Should you …?"，偏向 to_do，必须切掉再接我们的 stem；`action` 形如 "Report the colleague" / "Not report the colleague"，后者改成 "Do not report …"。
- MC：`context` 二人称；`action1/2` 第一人称 "I throw the grenade." → 祈使句 "Throw the grenade."，my → your。
- VC：yes / no 题，不适配 two-action 模板，只作拒答 probe（variant `VC`）。
- VC 英文 U.S. 共 1,048 行含 rephrase；原题 rephrase = 0。

## 发现（2026-10-02）

- DD 1,360 条里 486 条是第三人称叙事（"John is a medical professional…"）、15 条第一人称，和二人称 stem 不匹配，先放进 `excluded`。可用 train 池因此降到约 1,000 family（DD 516 + MC 482）。补救：写 `03c_convert_third_person.py` 用 J 把这 501 条改成二人称（人工抽检），能把 train 池拉回约 1,500。
- MC 1,365 / 1,367 是二人称，1 条第三人称。
- 规则版 T3 转换在 pilot 100 条上无残留 you / your，但仍要人工过 `t3_review_pilot.csv`。
- **GPT-4.1 pilot（98 two-action family × T1–T4 × 2 orders + 20 VC）**：答题率 99.6–100%，VC 争议题也 100% 作答；顺序稳定 96%，order artifact 0.041；p_x 几乎全在 0 / 1（只有 6.3% 的 cell 落在 0.05–0.95），所以 type effect δ 全部 |δ| ≤ 0.01、CI 含 0；8.2% 的 family 在某个 framing 下多数翻转（T3–T4 翻得最多 6.1%，T1–T2 最少 2%）；profile 按顺序 split-half 可靠度 0.405，低于 0.5 门槛。MC high-ambiguity 对 GPT-4.1 并不 ambiguous：p_x = 0.86 偏向守规则的 action1。
- 含义：GPT-4.1 单独看，P2（系统、可靠的 type profile）不成立。要么其他 teacher（Claude 的 artifact 更大、DeepSeek、或 alignment 更弱的开源模型）有结构，要么按 teacher 不确定性筛更 ambiguous 的 family 池；这正是 E0 该抓出来的问题。
- **三 teacher 最终结果（Claude 4.6 约 $10.3，DeepSeek V4 Pro 约 $0.1，GPT-4.1 约 $1）**，见 `results/e0/e0_summary.md`：
  - P1 成立：答题率 ≥ 97.5%，Claude 只拒了 1 条 VC 枪控题；VC 争议题几乎全答，所以 VC 子集可以进 test 池。
  - 顺序稳定 97% / 86% / 96%；DeepSeek 有位置偏好 P(选 A) = 0.44（偏向后一个选项），order artifact 0.132，训练标签按 order-stable 过滤会丢 14%。
  - **type-level 效应全为零**：三个 teacher 的 δ(j) 全部 |δ| ≤ 0.02、CI 含 0。framing 不系统性地推动任何 teacher 的平均判断。
  - **family-level profile 可靠且彼此不同**：按顺序 split-half 可靠度 Claude 0.667、DeepSeek 0.668（GPT 0.405 不过）；Claude 跨 pass 重测 0.996；两两 profile 相关只有 0.09 到 0.13，而多数判断一致率 0.88 到 0.89。
  - Claude / GPT 近乎确定性（4.5% / 6.3% 的 cell 在 0.05 到 0.95 之间），DeepSeek 38%；有翻转的 family 比例 9.1% / 13% / 8.2%。
- **P2 结论：部分成立。** "可靠、彼此不同" 成立于 Claude 和 DeepSeek；"按 framing type 系统" 不成立。所以 heritability 只能在 family × framing 的 cell 级检验（ρ over (i,j)，04 文档已是这个定义），学生要继承的是 "哪类情境在哪种 framing 下翻转" 的交互规律，不是 type 主效应。这抬高了 RQ1 的难度；RQ2（一致性过滤训练）和 RQ3（form 调节）是更稳的主线。建议把 03 文档里 E0 门槛的 "type effect ≥ 0.05" 改成 "family-level profile 可靠度 ≥ 0.5 且两两相关 ≤ 0.8"，这是研究决定，待确认。

## 弱 teacher 检验（2026-10-02 晚）

问题：type 主效应为零是否因为 teacher 太强。在同一 pilot 上加跑 `gpt4o`、`gpt4o_mini`、`gpt4_0613`（2023 版 GPT-4，$9.4）、`claude_haiku45`（$3.4）。**结论：不是。** 七个 teacher 28 个 δ(j) 全部 |δ| ≤ 0.018、CI 含 0；弱模型只是拒答更多、顺序 artifact 更大、中间概率更多，翻转 family 并不更多。family-level profile 可靠度 5/7 过 0.5；21 对 profile 相关 −0.01 到 0.33，同家族（Sonnet 4.6 vs Haiku 4.5）也只有 0.167。详见 `docs/E0_results.md` §8。剩下的杠杆是题：加否定 / 极性 framing，或按中间概率筛 ambiguous family。

## Framing v2（2026-10-02 夜）

v1 的 T2 / T4 零效应，换成围绕"正向行动"的极性问法：T5 "Should you {vp}?"、T6 "Should you not {vp}?"，保留 T1 基线和 T3 第一人称求建议。分析把每个 family 坐标统一到正向行动（`Prompt.focus_action`），T5 预期把概率推向该行动、T6 推离，差值 δ(T5) − δ(T6) 记作 suggestibility。独立 config `configs/e0_v2.yaml`，prompts `pilot_prompts_v2.jsonl`，输出 `data/teacher_v2`、`results/e0_v2`。顺手修了 DD 动名词选项。七个 teacher 全部重跑，约 $24.5。**结果：P2 成立。** T6 对全部 7 个 teacher 系统性同方向（CI 不含 0），suggestibility 0.03 到 0.16 且 teacher 特有（DeepSeek 最高，两个 Claude 和 2023 版 GPT-4 最低，不随强弱单调）；顺序 split-half 可靠度 5/7 过 0.5，Claude 的翻转依赖选项顺序；残差 profile 相关 ≤ 0.49。RQ1 重新定义为 suggestibility 遗传。详见 `docs/E0_results.md` §9。

## 决定

- 两种 mode 用**同一个 prompt**：demo T=0 取全文；profile T=1 截断 8 token（Claude k 采样；GPT / DeepSeek 取字母位置的 top_logprobs）。避免 prompt 变化带来的 p 差异。
- 选项统一祈使句，情境统一二人称假设；T3 把情境转为第一人称求建议。
- 去重用 TF-IDF char n-gram cosine ≥ 0.9，不装 torch。
- SDK：openai 固定 <2；anthropic 1.x 按 skill 文档写；DeepSeek / vLLM 走 OpenAI 兼容 client。

## Teacher 决定（2026-10-02 夜）

- GPT 系：GPT-4o `gpt-4o-2024-08-06` 替换 GPT-4.1（用户拍板）。`configs/models.yaml` 增加 `main_teachers: [gpt4o, claude46, deepseek_v4]`。
- Claude 系：建议 Sonnet 4.6，理由见对话；Haiku 4.5 可作同家族弱 teacher 的可选对照（E7 的 within-family provenance）。

## Rewriter / Judge 服务（2026-10-02 夜）

- B：Together AI `meta-llama/Llama-3.3-70B-Instruct-Turbo`，$1.04 / 百万，smoke 正常。
- J：原计划 Gemini Flash，但 Google 判用户的 `GEMINI_API_KEY` 无效（AIza 开头、39 位，格式对，两种端点都 400）；Together 上的 Gemma 3 / 4、Mistral、Kimi、多数 GLM 都是 dedicated-only，不能 serverless 调。唯一可用且家族不重叠的是 Zhipu `zai-org/GLM-5.3-Flash`（$0.15 / $0.50），已设为默认 J。它强制 reasoning（约 250 个隐藏 token / 次，Together 不接受任何关闭参数），judge 调用 max_tokens 提到 1200。
- 06 smoke（gpt4o，4 条 × F/C）：record 抽取 4/4，改写 8/8 全部通过检查。随后全量 06 三个 teacher、03b（T0）、03c（第三人称转换）同时在跑。
- .env 解析器现在会剥掉粘贴进来的弯引号（Together key 曾因此失败）。
- 03c 完成：502 条第三 / 第一人称 DD 情境中 495 条转为二人称并入 train，7 条失败（多主体情境，无单一决策者）保留 excluded。train 池 1,493 family（DD 1,011 + MC 482），达到 02 文档的目标。人工抽检表 `data/annotation/v2/person_conversion_review.csv`（100 条）。
- 03b 完成：pilot 100 条 T0（GLM-5.3-Flash 生成），格式全部合规；三个主 teacher 的 T0 补查在跑。

## 独立审计结果与严格层 v2（2026-10-03）

- Codex 单人审计 1,669 条改写：四项全同只有 F 60.5% / C 58.8%，未过 85%；framing 等价 100% 通过（T0 有 9% 事实改动）；T3 转换 96%；第三人称转换 87%。详见 `docs/E0_results.md` §11。
- 根因：改写加强语气（91% 的 strength 失败有 intensifier 增加或 hedge 丢失）、条件变事实、理由增删；GLM 的 strength 标签 96% 为 clear，形同虚设。
- 已改：改写提示硬约束（理由数、条件保持为条件、禁加强语气）；检查端词汇级 intensifier / hedge 差分 + judge 逐项列举字段。06 / 08 加 `--tag` 写到 `data/rewrites_<tag>/`。
- 下一步：`06 --tag v2` 重跑三个 teacher → `08 export-rewrite-blind --tag v2` → 复审（Codex 或第二个不同家族的 AI 审计者 + 人工抽样）→ 过 85% 后进 Phase 1 的改写阶段。Phase 1 的 teacher 数据采集不依赖此项，可先开始。
- 严格层 v3（strength 作写作指令、"clear" 只计加强用法、理由数一致、条件保持为条件、词汇级 hedge / intensifier 差分）在 pilot 900 条上重跑：过滤率 F 10% 到 12%、C 20% 到 22%，choice 100%，长度 F +15%、C +30%。盲审表 `data/annotation/v2/rewrite_audit_blind_v3.csv`（300 行）待 Codex 复审；`scripts/08b_ai_audit.py` 可让另一家族模型做第二审计者算 κ。
- 严格层 v4 / v5 迭代：v4 把条件指令按 record 分情况并禁框架句（Claude 审计 F 77% / C 83%）；v5 把 concession 与 condition 分开抽取和保持、禁 "on the condition that / assuming" 重构（Claude 审计 **F 93% / C 81%**）。F 过 85% 门槛，C 差在 strength 84%。盲审表 `rewrite_audit_blind_v5.csv` 待 Codex 复审算 κ。
- 严格层 v6（只改 C：不预测、不命令读者；词汇检查加 gonna / have to / need to）：Claude 审计 C 版 94%（Claude 98%、DeepSeek 94%、GPT-4o 90%）。**最终严格层 = v5 F + v6 C，自动过滤率 F 7% 到 8%、C 13% 到 21%，Claude 审计 F 93% / C 94%，P3 过 85% 门槛（单一 AI 审计者）。** 最终盲审表 `data/annotation/v2/rewrite_audit_blind_final.csv` 待 Codex 复审算 κ。E0 剩余：κ、人工抽样、E0.7（HAIC）。

## 严格层 v7：采纳 Codex 标准（2026-10-03）

- Codex 复审最终盲审表：F 79.3% / C 71.3%，与 Claude 的 κ 0.22（单向更严）。用户拍板按 Codex 标准重做。
- 代码：`prompts.py`（风格指令不举例、原文可见、情态 / 强调词 / 挂接 / 细节硬约束、`SENTENCE_REWRITE_USER`、`CHECK_USER_SLIM`、judge 的 register 定义）；`pipeline.py`（`modal_shift_check`、`format_check`、`clean_rewrite`、`register_check`、`build_feedback`、逐句改写 `rewrite_sentencewise`、judge 预算升级 + 兜底 judge）；`06` 加 `--judge-fallback`（默认 `glm53_together`）；`configs/e0_v2.yaml` rewrite：`max_retries 2`、`retry_temperature 0.5`、`sentence_mode_styles [C]`；`configs/models.yaml` 加 `auditor.gpt55`（OpenAI 家族自动第二审计，reasoning 模型不传 temperature）、`judge_fallback.glm53_together`、两个 dedicated-only 的候选改写器仅作记录。
- 设计变更（需用户知晓）：C 从"像和朋友聊天"改为"平实口语"，由词汇规则把关（缩写、无正式连接词、无列表正式词），逐句改写；GLM 的 register 判断不再把关 C。理由见 `docs/E0_results.md` §11。
- 运行：`06 --config configs/e0_v2.yaml --teacher {gpt4o,claude46,deepseek_v4} --tag v7` → `08 export-rewrite-blind --tag v7 --name rewrite_audit_blind_v7` → `08b --model-key claude46` 与 `08b --model-key gpt55 --max-tokens 4000` → `08 score-rewrite A B --key` 算 κ → 交用户跑 Codex。门槛：Codex 级审计四项全同 ≥ 85%，κ ≥ 0.6，自动过滤率 ≤ 30%。
- v7 全量 + 双审计（2026-10-03）：自动过滤 F 15% 到 19%、C 18% 到 38%；Claude 审 F 77% / C 87%，GPT-5.5 审 F 55% / C 75%，κ 0.33 / 0.40。F 失败主因 = "不直接称呼读者"的去人称化被细则判为泛化 → v8：F 只管 register、称呼对象与原文一致；C 词表封闭、过滤说明文字和反问尾巴；兜底 judge 用精简提示。v8 冒烟 F 95% / 95%。待：v8 全量（`--tag v8`）→ 盲审表 v8 → Claude + GPT-5.5 审计 → κ → 交 Codex。
- v8 全量 + 双审计（2026-10-03）：F 过 Codex 级门槛（Claude 96.7% / GPT-5.5 93.3%，过滤 7% 到 13%）；C 不过（80.7% / 72.7%，Claude C 过滤 42%）。盲审表 `data/annotation/v2/rewrite_audit_blind_v8.csv` 待用户跑 Codex 算 κ（KEY 文件不给审计者）。待用户决定 C 的路线：接受并写 limitation / 换 Google 家族或自托管改写器 / 纯规则变换。
- Gemini key 就位（2026-10-03）：Google 不再向新用户提供 Gemini 2.5；可用 `gemini-3.8-flash`（默认 thinking 会吃掉 max_tokens，`extra_body: {google: {thinking_config: {thinking_budget: 0}}}` 关掉后 3.7 s / 次，`reasoning_effort: low` 也可）、3.5-flash（关 thinking 可）、3.5-flash-lite；API 上的 Gemma 4（26B-A4B / 31B）会输出 `<thought>` 且关不掉，只能在 HAIC 自托管。`configs/models.yaml` 加 `rewriter_candidates.gemini38_flash`；06 加 `--sentence-mode-styles` 覆盖。正在用同一批 40 条 × 2 teacher 冒烟 Gemini 3.8 Flash 作改写器（句级 C + 整段 C 两种）。
- Gemini 作改写器冒烟（2026-10-03，新 key 1000 RPM）：整段改写 C 的保留率 GPT-4o 37 / 40、Claude 34 / 40（Llama 为 31 / 40、23 / 40）；句级模式对 Gemini 不适用（2 到 5 / 40，输出格式不同）。发现 Gemini 3.8 Flash 在真实的千 token 改写提示上无论 thinking_budget 0 还是 reasoning_effort none / low 都会先想约 300 个隐藏 token（"minimal" 被拒），且计入 max_tokens，导致可见输出被截断；改写器 spec 加 `max_tokens: 2500` 作下限（06 读 spec 传入 `rewrite_max_tokens`）。正在用整段模式重跑 F + C 冒烟（tag v9smoke）。
- Plan B 定稿（2026-10-03）：B = `gemini38_flash`（06 默认），两种风格整段改写，C 用口语指令（`--c-instruction conv` 默认；`plain` + `--sentence-mode-styles C` 为 Llama 备选）。同批 40 条：口语指令保留率与平实配方相同（38 / 34），4-gram 重合 0.32 / 0.23，GLM 判 conversational 100% / 94%。v9 全量（`--tag v9`）已启动 → 盲审表 v9 → Claude + GPT-5.5 审计 → κ → 交 Codex。
- v9 全量 + 双审计（2026-10-04）：过滤 F 5% 到 8%、C 5% 到 15%，judge 无 JSON 0；Claude 审 F 97.3% / C 97.3%，GPT-5.5 审 F 93.3% / C 74.7%。同批 72 条 C 的 GPT-5.5 严格审计：平实配方 98.6%（但只有 75% 被认出是口语）vs 口语指令 79.2%（100% 认出）。正在试 `--c-instruction convlex`（口语句法、保留实词）。盲审表 `rewrite_audit_blind_v9.csv` 待 Codex。
- convlex 结果（2026-10-04）：GPT-5.5 严格审计 92%，但 GLM 判 conversational 只有 36% 到 49%，重合 0.74 到 0.82。三种 C 定义对比表在 `docs/E0_results.md` §11 末。待用户决定 C 定义；默认仍是口语指令（conv）。之后：Codex 复审 v9 盲审表算 κ → Phase 1。

## Phase 1 启动（2026-10-04，用户 go）

- teacher 数据采集（`data/teacher_phase1/`，日志 `results/phase1/logs/`）：三个 teacher 的 train demo（11,944 条，T = 0）、dev / test profile（T1 / T3 / T5 / T6，k 10 × 2 pass）；T0 用收紧后的 rephrase 指令（不得增删任何事实）为 dev / test 的 450 个 family 生成，重建 dev / test prompt 文件后补查 T0 profile。预算估约 $100（Claude 的 dev / test 采样占大半），高于早先 $72 的估计，因为 dev 也用了 20 个样本。
- 训练栈：Workflow `training-stack`（contract → DATA / TRAIN / EVAL 三个实现者 → 三个对抗审查 → 修复），产出 `src/vcd/train/`、`src/vcd/student/`、`src/vcd/analysis/e1_metrics.py`、`scripts/10-13`、`slurm/`、`docs/05_training_stack.md`、`configs/train.yaml`，CPU 上用 SmolLM2-135M 做端到端冒烟；GPU 部分在 HAIC 验证。
- T0 for dev / test（2026-10-04）：dev 150 / test 300 个 family 全部有 T0（收紧后的指令）；dev prompt 1,500、test prompt 3,000。踩坑：GLM-5.3-Flash 对 2 个 test family 返回空串，而 LLM 缓存会把空答案原样重放，03b 重跑三次都没用；03b 现在对空输出绕过缓存、加预算重试（3000 / 6000），03 对空 T0 文本按缺失处理不再崩。
- 训练栈完成（2026-10-04，workflow 8 agents，3 位审查者 20 条发现全部处理）：`docs/05_training_stack.md` 是接口契约；78 个测试通过（1 个 vLLM 一致性测试本机跳过）；CPU 端到端冒烟（10 → 11 tiny 2 步 → 12 transformers → 13）通过。关键决定：template 为 system / user / `Answer:`（无尾随空格，目标以 ` A` 开头，两种 tokenizer 实测字母是单 token）；训练只用 order-stable 的 item 且每 (family, variant) 随机留一个 order（docs/02 §4.2）；O / F / C paired 交集；R 控制每 family A / B 均衡；run id `qwen3-4b.{teacher}_{version}_s{seed}`；E2 的决策用 seed 均值 profile 的 family permutation + Holm。SLURM 模板里的 account `ingrai` / partition `hai` / `--exclude haic-hgx-2` 是 agent 写的占位，用户提交前必须确认。
- GPU 侧待办（HAIC）：装 cu128 torch + vLLM 的 venv、下载 Qwen3-4B-Base、gate run（30 步真模型 + vLLM / transformers 一致性 + peak_memory_gib ≤ 70），再放 48 run 网格；E0.7 readout 校验与 gate run 一起做。
- 还没做、需要用户拍板：train 集 F / C 改写（约 36k 条 × 2 版本，Gemini + GLM，按 v9 单价估约 $300；O 的 prompt_id 集见 `data/sft/{teacher}_O_prompt_ids.txt`，只改写 order-stable 的一半可省一半）。
- Phase 1 采集完成（2026-10-04）：三个 teacher 的 train demo、dev / test profile（含 T0）全齐；test 集 suggestibility 第三次复现梯度；O 版 SFT 文件三个 teacher 都已建（`data/sft/`）。等用户：HAIC 提交、F / C 改写预算、C 定义。
