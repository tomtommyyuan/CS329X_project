# E3 执行计划：Form 调节（HAIC 上执行）

> 协议：[docs/03_experiments.md](../docs/03_experiments.md) §0 E3 行、§5、§8；指标：[docs/04_eval_metrics.md](../docs/04_eval_metrics.md) 组 B / C / D、§3；实现：`src/vcd/analysis/e3_metrics.py`、`scripts/15_e3_analysis.py`（[docs/05](../docs/05_training_stack.md) §6b）；paired 网格的建数据 / 训练 / readout 步骤：[e1_plan §8](e1_plan.md)。执行者：HPC agent（见 [CLAUDE.md](../CLAUDE.md)）。

## 0. 问题

answer 的文风改写（O 原文 → F 正式 / C 口语，内容由 judge 逐项保持）改变学生学到的判断、一致性、继承吗？docs/03 §5 的三阶段：

| 阶段 | 看什么 | 变化的含义 | 实现 |
|---|---|---|---|
| 1 改写前 | teacher profile（E0 / E1 已有） | — | `results/e1*` |
| 2 改写后、训练前 | **实际训练文件** `data/sft_paired/{teacher}_{O,F,C}_s1.jsonl` 的内容检查：字母与 O 逐条相同、judge 六项检查、长度、词汇 register 分离 | 有变化 = 内容漂移，不是 form 效应 | `content_check`、`register_table`、`register_separation` → `content_check.csv`、`register_check.csv`、`register_separation.csv` |
| 3 训练后 | S_{T,F,s} / S_{T,C,s} vs S_{T,O,s}，同 teacher **按 seed 配对** | 第二阶段干净而这里有变化 = 学习结果不随 form 保持 | 下表 1 到 5 |

## 1. 输入

| 文件 | 内容 |
|---|---|
| `runs/qwen3-4b-paired/{teacher}_{O,F,C}_s{1..5}/eval/{dev,test}_responses.jsonl` | 45 个 paired run 的 readout（run id `qwen3-4b-paired.gpt4o_F_s1`）；现在还没有，HPC 在训 |
| `runs/qwen3-4b/base_B_s0/eval/{split}_responses.jsonl` | 未训练基座 S_0；不加门的先验 profile r_0 作偏相关的协变量（e2_plan §1） |
| `data/teacher_phase1/{teacher}_{dev,test}_profile.jsonl`、`data/prompts/{dev,test}_prompts_v2.jsonl` | teacher profile 与 prompt |
| `data/sft_paired/{teacher}_{O,F,C}_s1.jsonl`（gitignore，集群上建）+ `data/rewrites_train/{teacher}/rewrites.jsonl` | 阶段 2 的输入；本机重建：`scripts/10_build_sft_data.py --teacher gpt4o --versions O,F,C --seeds 1 --rewrites-dir data/rewrites_train --out-dir /tmp/sft_paired --tokenizer Qwen/Qwen3-4B-Base` |

## 2. 冻结的量（2026-10-05，在任何 F / C run 存在之前）

单位 = family；每 teacher 的统计量 = 配对差 S_{T,V,s} − S_{T,O,s} 的 seed 均值（V ∈ {F, C}）；CI = family bootstrap 10,000（同 teacher 各 seed 联动重抽）；噪声参照 = **seed-pair null**：同一 teacher 两个 O seed 之间的同一量，跨 teacher 合并（3 × C(5,2) = 30 个值）。

| # | 量 | 定义 | 函数 → 文件 |
|---|---|---|---|
| 1 | 跨学生分歧率 | 同 teacher 同 seed 的 S_{T,F,s} vs S_{T,C,s}（另报 O vs F、O vs C）在 (family, variant) cell 上多数行动不同的比例（p = 0.5 的 cell 不计）；null = O seed a vs O seed b 的分歧率 | `cross_student_disagreement`、`seed_pair_disagreement` → `disagreement.csv`、`seed_pair_null.csv` |
| 2 | Δ 一致性 | flip rate 与 cross-framing JSD 的 V − O，按 seed 配对，按 teacher 给 CI 与方向 | `consistency_delta` → `consistency_delta.csv` |
| 3 | Δ agreement 与 excess teacher drift | agree(S_{T,V,s}, T) − agree(S_{T,O,s}, T)；JSD(S_{T,V,s}, T) − JSD(S_{T,O,s}, T) | `drift_delta` → `drift.csv` |
| 4 | Homogenization index（描述） | 每个版本 V：不同 teacher 的学生两两（同 seed）判断 JSD 与 1 − corr(profile) 的均值，与 V = O 的配对差；靠同质化起效的 fix 会下降 | `homogenization` → `homogenization.csv` |
| 5 | 按 form 的继承 | 每 run 的 ΔρPartial（给定 r_0，同 teacher 所有 run 用同一 family 集）的 V − O 配对差；每版本的 joint partial D 及 CI（描述）；每 (teacher, version) 组的 suggestibility s 及版本差（描述） | `inheritance_by_form`、`joint_D_by_version`、`suggestibility_by_version` → `inheritance_by_form.csv`、`joint_D_by_version.csv`、`suggestibility_by_version.csv` |
| 6 | 阶段 2 内容检查（描述） | 每 teacher / version：条数、与 O 的 prompt 集与字母一致率（必须 100%）、kept attempt 的 choice / reasons / conditions / strength / style / format 通过率、平均 attempt 数、改写日志的保留率、rationale 词数 / 字符数 / target token 数；register：缩写率、正式连接词率、正式词率、平均词长、每句词数、Flesch–Kincaid 代理；F vs C 的 LOO 最近质心与 10 折 logistic 准确率（≥ 0.90 是本计划冻结的门槛，docs/02 §4.3 只给词汇规则与审计 ≥ 85%；附 Wilson 95% CI），O vs F / O vs C 只描述 | `content_check`、`register_table`、`register_separation` |

## 3. 决策规则（docs/03 E3 行原文，冻结）

> 效应在 ≥ 2 / 3 teacher 上超 seed null 95 分位且方向一致；R 有而 F / C 无则归因于隐性内容变化

| 项 | 操作化（`e3_verdict`，2026-10-05 审查后定稿，仍在任何 F / C run 之前） |
|---|---|
| 判定的量（13 行，`verdicts.csv`） | **primary 9 行**：分歧率 F vs C；Δ 一致性（flip、JSD）× {F, C}；excess drift（对自己 teacher 的 JSD）× {F, C}；ΔρPartial 的 V − O × {F, C}。**secondary 4 行**：分歧率 O vs F、O vs C；Δ agreement × {F, C} |
| 每 teacher 统计量 | 差值类：5 个 seed 配对差 S_{T,V,s} − S_{T,O,s} 的均值；分歧率：mean_s dis(S_{T,V,s}, S_{T,W,s}) − 该 teacher 自己 O-O seed 对分歧率的均值（`excess_disagreement`；不中心化会把 teacher 层面的分歧水平混进 pooled null） |
| null 的尺度匹配 | seed-pair null 是**单对**量（O_a − O_b，3 × C(5,2) = 30 个），统计量是 n_seeds 对的均值，二者尺度差 √n_seeds。所以 SD_stat = sqrt(mean(d²) / n_seeds)（分歧率：组内 sd² / n_seeds + O-O 均值的 delete-one-seed jackknife 方差），q95 = t(0.975, df) × SD_stat（分歧率单侧 t(0.95)），df = Σ_T (n_O,T − 1) = 12。假设：seed 噪声近似正态、跨 seed 独立；真实的同 seed F / O 对共享初始化与数据顺序，故 null 偏保守。模拟（iid H0，3 × 5 seed）：每 teacher 超阈率 ≈ 4.7%（分歧率 ≈ 3.8%）；原单对 q95 规则只有 0.3%，`tests/test_e3_metrics.py::test_e3_verdict_calibrated_under_h0` 守着 |
| teacher 过 | \|stat\| > q95（分歧率：excess > q95）；`null_q95_single` / `n_pass_single`（单对 95 分位，老规则）作敏感性列一并报 |
| effect | 过的 teacher ≥ 2（= ceil(2/3 × 3)）且符号相同 → `effect` |
| no effect / inconclusive | 不是 effect 时，≥ 2 个 teacher 过 TOST（family bootstrap 95% CI 与点估计都落在 ± 1 SD_stat 内；等价界 = 1 个 null SD，docs/04 §3；用 95% CI 相当于 TOST α = 0.025，偏保守）→ `no effect`，否则 `inconclusive` |
| pending | 没有配对 run → `pending (no paired runs)`；有配对 run 的 teacher < 3 → `pending (n_teachers k < 3)`（部分网格永不出 effect）；O seed < 2 → pending |
| 一并报 | 效应量 = stat / SD_stat；p 来自 t 参照（可到 1e-6，Holm 跨 3 teacher 有意义）；`p_row` = 每行第二小的 teacher p（"≥ 2/3 过" 刚好成立的水平）、`p_row_holm_primary` = primary 9 行上的 Holm（描述）。q95 规则本身在 H0 下每行误报率 ≈ 3α²/2 ≈ 0.004，13 行 Bonferroni ≤ 0.05，不再另加校正 |
| 描述项 | homogenization（先看 1 − corr，JSD 与多数分歧附 \|p − 0.5\| 校准列）、每版本 D、每版本 s、阶段 2 检查都不判定 |
| 冻结 | dev 上跑一次 `scripts/15 --split dev` 看表齐不齐，`tasks/hpc_log.md` 写冻结行后用 `--frozen-commit <hash>` 重跑一次（summary 头部从 "not yet frozen" 变为 "frozen at commit"）；之后不改默认值；test 只跑一次。"R 有而 F / C 无" 指可选的 R_F / R_C 改写控制（docs/03 E3 行 "可选 9"），Phase 1 不做 |

dev 上现有 O run（`runs/qwen3-4b`，全集 O，非 paired）给出的**单对** seed-pair null 量级（`--n-boot 1000` 冒烟）：flip RMS 0.0138、q95 0.028；JSD q95 0.013；agree_own 0.021；jsd_own 0.013；分歧率均值 0.043、组内 sd 0.009；ΔρPartial q95 0.107（SD 0.036）。换成 5 seed 均值后两侧阈值约为单对 RMS × 2.18 / √5 ≈ 单对 q95 的 0.5 倍。paired 网格的 null 由 15 个 paired O run 重算。

## 4. HPC agent 做什么（e1_plan §8 的 1 到 4 步之后）

所有命令在 compute 分配里跑（CLAUDE.md：不在 head node 上计算），先 `source .venv/bin/activate && export HF_HOME=/hai/scratch/$USER/hf HF_HUB_OFFLINE=1`；默认 tokenizer `Qwen/Qwen3-4B-Base` 要在缓存里，否则加 `--tokenizer none`（脚本会警告并继续，只少 token 计数）。45 run × 300 family、`--n-boot 10000 --n-perm 10000`：约 80 s、1.8 GB RSS。

| # | 做什么 | 命令 | 验收 |
|---|---|---|---|
| 1 | 阶段 2 检查可以先跑（只要 `data/sft_paired` 建好，不需要 run） | `python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev --out results/e3_dev` | `content_check.csv` 每个 F / C 行 `letter_identity_with_O` = 1.0、六项 check 全 1.0；`register_separation.csv` 的 F–C 三行 `status` = pass（本机冒烟 LOO 最近质心 0.921 / 0.927 / 0.907，logistic 0.959 / 0.952 / 0.942，Wilson 下界都 ≥ 0.90）；run 没齐时 Verdicts 全 `pending`。已知且允许：claude46 C 有 1 条 `letter_matches_rewrite` < 1（改写文本以 "Neither option A nor B fits … Answer: A" 开头，judge 的 format 检查放过了这个前言；scripts/10 剥掉前言后字母与 O 一致，训练文件没问题；E0 改写路径不改），summary 会单独列出 |
| 2 | 45 个 run 的 dev readout 齐后，dev 分析 | 同上 | `summary.md`：Run inventory 每 teacher `n_O = n_F = n_C = 5`、`paired_F = paired_C = 5`；Verdicts 13 行无 `pending`（部分网格时是 `pending (n_teachers k < 3)`，正常）；头部 "not yet frozen"、"dev = freeze split" |
| 3 | 冻结 | `tasks/hpc_log.md` 追加一段：日期、13 行 verdict 与各 teacher 的 stat / q95 / TOST、一行 `E3 规则冻结于 <commit>`（<commit> = 当前 main HEAD）；然后 `python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev --out results/e3_dev --frozen-commit <commit>` 重出一次（只改 summary 头部）；之后不改 15 的默认值、不改 `e3_metrics` 的任何阈值 | `results/e3_dev/summary.md` 头部 "frozen at commit <commit>" |
| 4 | test readout（只一次） | 与 e1_plan §7 第 5 步一起：45 个 run 各 `sbatch slurm/eval.sbatch runs/qwen3-4b-paired/<run> test`；S_0 的 test readout 已在 §7 第 5 步 | 45 个 `eval/test_responses.jsonl`，各 3,000 行 |
| 5 | test 分析 | `python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split test --out results/e3 --frozen-commit <commit>` | `results/e3/summary.md` 的 Verdicts 表就是 E3 结论（effect / no effect / inconclusive 如实报）；不再改任何量 |
| 6 | 提交 | `git add runs/qwen3-4b-paired/*/train_manifest.json runs/qwen3-4b-paired/*/eval results/e3_dev results/e3 tasks/hpc_log.md && git commit && git pull --rebase && git push` | Mac 侧写论文表 |
| 7 | 清理 | dev / train / test 都评完的 run：`rm -rf runs/qwen3-4b-paired/<run>/checkpoint` | — |

缺版本时 15 自动降级：缺 F / C → 相关行 `pending (no paired runs)`；只有部分 teacher 有 F / C → `pending (n_teachers k < 3)`；null 与 O 版本的 homogenization / D / s 照出；缺 `--base-run` 的 readout → ΔρPartial 回落为 raw Δρ 并在 summary 注明；缺 `data/sft_paired` → 阶段 2 行 `pending` 并印重建命令。

## 5. 产出与提交

| 文件 | 内容 |
|---|---|
| `results/e3_dev/`、`results/e3/` | docs/05 §6b 的全部 CSV + `summary.md`（Verdicts、seed-pair null、1 到 6 的表、阶段 2 检查） |
| `tasks/hpc_log.md` | 冻结行、dev / test 的 verdict 摘要 |
| 不提交 | `data/sft_paired/`（已 gitignore）、checkpoint |

## 6. Mac 侧回复（2026-10-05）

E3 是预先指定的主线，不是补救：docs/03 §1 的 E0 规则 "≥ 2 个 teacher 的 reliability < 0.5 → P2 不成立：RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5"，而 test 侧 teacher 的顺序 split-half r 为 Claude 0.329、DeepSeek 0.466（docs/E0_results §13，e1_plan §9），3 个 teacher 里 2 个低于 0.5，门槛已触发；本项目做其中的 E3。E2 的结果按 e2_plan §2 如实报为 exploratory / secondary。E3 的判定不依赖 teacher profile 的可靠度：1 到 3 比的是同一 teacher 的学生之间的判断与一致性，5 的 ΔρPartial 配对差与每版本 D 受同一上限 sqrt(2r / (1 + r)) 约束，但差值与 null 在同一尺度上，报时附 e1_plan §9 的上限。

本次交付（Mac 侧）：`e3_metrics.py` 与 `scripts/15`、`tests/test_e3_metrics.py`（17 个测试：合成 O / F / C 学生、iid H0 校准、TOST / pending 分支、合成 SFT / rewrites 树、三个 CLI 冒烟：全网格、只有 O、只有一个 teacher 有 F / C），全套 125 passed 1 skipped；在 `runs/qwen3-4b`（只有 O / R）上冒烟：13 行 verdict 全 `pending (no paired runs)`，null 与阶段 2 检查如 §3、§4 所述。审查后的改动（2026-10-05，仍在任何 F / C run 之前）：null 尺度匹配到 seed 均值（t 参照）、分歧率改为对自己 O-O 水平的 excess、TOST 才能写 no effect、teacher < 3 一律 pending、null 与统计量共用每 teacher 的 family 集、primary / secondary 分层、LOO 分类器去掉标准化泄漏。待 HPC 的 45 个 run。
