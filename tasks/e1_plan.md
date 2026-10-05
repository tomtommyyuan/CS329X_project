# E1 执行计划：蒸馏基线（HAIC 上执行）

> 协议：[docs/03_experiments.md](../docs/03_experiments.md) §2、§8；指标：[docs/04_eval_metrics.md](../docs/04_eval_metrics.md)；代码契约与命令：[docs/05_training_stack.md](../docs/05_training_stack.md) §9、[slurm/README.md](../slurm/README.md)。执行者：HPC 上的 Claude Code agent（见 [CLAUDE.md](../CLAUDE.md)）。

## 0. 问题与决策规则（2026-10-05 在 dev 上修订并冻结）

| 问 | 学生学到 teacher 的判断了吗？seed noise 多大？ |
|---|---|
| run | 15 个 S_{T,O}（3 teacher × 5 seeds，O 版）+ 3 个随机标签学生 R |
| E1a 训练标签复现 | 每个 run 在**自己的训练 prompt**（SFT 文件的 prompt_id，训练过的那个 order）上 readout（`12 --split train`），argmax 字母 = SFT 目标字母的比例；**门：每个 O run ≥ 0.95** |
| E1b 争议项站队 | 对每对 (own, other) teacher，训练项中两者标签不同的项上，5 seed 合并后学生给 own 字母的比例，family bootstrap 10,000 的 95% CI；**门：对每个 other teacher 下界 > 0.5** |
| E1 判定 | 三个 teacher 的 E1a 与 E1b 都过；没有 `train_responses.jsonl` 时 13 打 `pending (no train readouts)`，其它表照出 |
| 描述性（无门） | dev 上与各 teacher 的 agreement（含 CI）、JSD（标注受 teacher 校准混淆：越极端的 teacher 不一致时罚得越重）、一致性、seed-noise null |
| 控制 | R 学生：E1a ≈ 0.5、agreement ≈ 0.5，一致性"看起来很高"是因为处处 50 / 50，所以一致性永远和 agreement、JSD 一起报 |
| 基座 | S_0 = 未训练的 Qwen3-4B-Base，同样 readout（0.9 门不变），给 malformed 率和"训练前"的参照；它不加门的先验 profile 只作 E2 的协变量（e2_plan §1） |
| 原规则（留档） | 每个 O seed 与自己 teacher 的 dev agreement > 与其他 teacher 的最大值。dev 上 deepseek_v4 5/5、claude46 4/5、gpt4o 2/5 未过；诊断（`results/e1_dev_diag/`）表明训练无误（训练标签复现 98.5–99.5%），未过来自 teacher 在 dev 上共识 83–89% + 基座先验像 DeepSeek，故换成直接看训练项的 E1a / E1b |

## 1. 前置条件（已满足的打勾）

- [x] Phase 1 teacher 数据：`data/teacher_phase1/{teacher}_train_demo.jsonl`、`{teacher}_{dev,test}_profile.jsonl`（含 T0），在 git 里
- [x] 训练文件可重建：`scripts/10_build_sft_data.py`（O 版三 teacher 5,619 / 5,642 / 4,936 条，R 3 seeds）；`data/sft/` 不进 git，在集群上重建
- [x] 代码：99 passed 1 skipped（skip = vLLM 缺席）；CPU 端到端冒烟通过
- [ ] 集群环境（README §0）；account / partition / QoS 已核实
- [ ] gate run 通过（§2）

## 2. 步骤

| # | 做什么 | 命令 / 位置 | 验收 |
|---|---|---|---|
| 0 | 环境 | README §0：uv venv、cu128 torch、`.[train,eval]`、下载 Qwen3-4B-Base 到 `/hai/scratch/$USER/hf` | `torch.cuda.is_available()` 为 True |
| 1 | 单测 + 建训练文件（在 compute 分配里，不在 head node） | `srun … --pty bash` → `python -m pytest -q`；`for t in gpt4o claude46 deepseek_v4; do python scripts/10_build_sft_data.py --teacher $t --versions O --seeds 1,2,3,4,5 --tokenizer Qwen/Qwen3-4B-Base; done`；`python scripts/10_build_sft_data.py --random-label --ref-teacher gpt4o --seeds 1,2,3` | 测试全过；`data/sft/*.meta.json` 的 `n_examples` 与上表一致 |
| 2 | gate run | README §1：30 步真模型 → transformers 与 vLLM 读数一致（max ∣ΔP(A)∣ < 0.01）→ manifest 检查 | `peak_memory_gib ≤ 70`、`precision bf16`、`n_dropped_too_long 0`；不过则 `optimizer: adamw_8bit` 重跑 gate |
| 2b | E0.7 readout 校验（顺带做） | 对 S_0 和 gate run 的学生，200 条 dev prompt：first-token p(A)（12 的输出）vs vLLM 采样 20 次的频率（`vllm serve <checkpoint>` 后 `VLLM_B_URL=http://localhost:8000/v1 python scripts/07_readout_check.py`，或等价脚本） | mean ∣diff∣ < 0.05（`gates.readout_diff_max`）；超了则学生评估改用采样，记入 `tasks/hpc_log.md` |
| 3 | 训练 18 个 run | `sbatch --array=0-4,15-19,30-34,45-47%8 slurm/train.sbatch` | 每个 run 目录有 `train_manifest.json`；失败的重提同一 array 即可（已完成的会跳过） |
| 4 | dev 评估 | `MODEL=Qwen/Qwen3-4B-Base sbatch slurm/eval.sbatch - dev`；每个 run `sbatch slurm/eval.sbatch runs/qwen3-4b/<run> dev` | `eval/dev_responses.jsonl` 1,500 行（含 T0） |
| 5 | dev 分析，冻结 | `python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split dev --out results/e1_dev` | 看 §3 的验收；此后 readout、阈值、决策规则不再改 |
| 6 | test 评估与分析（只跑一次） | 同 4、5，split 换 `test`，输出 `results/e1` | `test_responses.jsonl` 3,000 行 |
| 7 | 清理 | dev + test 都评完的 run：`rm -rf runs/qwen3-4b/<run>/checkpoint`（E2 复用的是 eval 输出，不是权重） | scratch 用量回落 |
| 8 | 提交 | `git add runs/qwen3-4b/*/train_manifest.json runs/qwen3-4b/*/train_log.jsonl runs/qwen3-4b/*/eval results/e1_dev results/e1 tasks/hpc_log.md && git commit && git pull --rebase && git push` | Mac 侧能直接读表 |

## 3. 验收与预期（2026-10-05 修订）

| 检查 | 预期 | 不满足怎么办 |
|---|---|---|
| S_0 与学生的 malformed 率 | 学生 < 5%；S_0 可以高（基座未学格式） | 学生 > 5%：查 template 是否与训练一致（docs/05 §1.3），不是去放宽 readout |
| **E1a**（`e1_train_reproduction.csv`） | 每个 O run accuracy ≥ 0.95（seed-1 诊断：98.5 / 98.5 / 99.5%）；R ≈ 0.5 | < 0.95：查 manifest 的 `data_sha256` 与 SFT 文件、训练 loss；不进 E2 |
| **E1b**（`e1_contested.csv`） | 每对 (own, other) 的 ci_lo > 0.5（seed-1 诊断：own 字母比例 0.90–0.97） | 下界 ≤ 0.5：该 teacher 的学生没学到它特有的判断；不进 E2 |
| teacher agreement（描述） | 学生与自己 teacher ≈ 0.85；R 学生对所有 teacher ≈ 0.5；dev 上 own 不必高于他人（teacher 共识 83–89%，无门） | — |
| student–teacher JSD（描述） | 报但不判；标注校准混淆 | — |
| seed-noise null | 同 (teacher, O) 五个 seed 两两 agreement 之差的 SD，预计 ≤ 0.02 | 大于 0.05：检查 seed 是否真的只改了顺序（manifest 的 data sha256 应相同） |
| 一致性 | 学生的 flip rate、cross-framing JSD 与 teacher 同量级；R 学生"一致"但 agreement 0.5 | — |
| 训练量 | `n_target_tokens` 约 GPT-4o 27 万、Claude 44 万、DeepSeek 22 万 / epoch | 差一个数量级：数据文件错 |

## 4. 预算与时间

18 run × 约 0.5 GPU 小时（3 epochs，5,600 条 × 160 token）+ 评估每 run 约 5 分钟（vLLM，4,500 条 prompt）≈ 11 GPU 小时；并发 8 时约 2 到 3 小时墙钟。checkpoint 每个约 8 GB，评完即删。

## 5. 已知风险

- Claude teacher 的 profile 依赖选项顺序（顺序 split-half 可靠度 0.33，跨 pass 重测 0.99）：E1 的 agreement 用两种顺序平均后的多数行动，不受影响；E2 要把它当 ρ 的上界报。
- DeepSeek 的 T6 顺序不稳定最多（O 版只有 4,936 条）：三个 teacher 的训练量不等，E1 的比较按 teacher 内 seed 配对，不跨 teacher 比绝对值。
- vLLM 与 transformers 在 base 模型上 p_letters 可能差在 logprobs 截断（vLLM 只给 top-20）：gate 的一致性检查就是为此；不一致就统一用 transformers 后端评估。

## 6. Mac 侧回复（2026-10-05，对 hpc_log 的 gate 结果）

| 问题 | 决定 |
|---|---|
| vLLM vs transformers 不一致（max 0.062，bf16 噪声） | 同意：E1 / E2 全部 readout 用 transformers 后端 |
| readout 精度 | **改 fp32**（`configs/train.yaml` 的 `readout.dtype: float32`，已提交；训练不变仍 bf16）。gate 测出 bf16 读数噪声 mean 0.007、单条最大 0.06，fp32 免费去掉，且此时还没做任何 dev 分析，不违反冻结。S_0 的 dev readout 用 fp32 重跑一次（`--overwrite`），学生评估直接用新默认 |
| 2b readout 校验 | 过（k = 200 时差值落在采样噪声地板上），学生评估不改用采样。`scripts/14_readout_check.py` 保留 |
| checkpoint 兼容补丁 `write_legacy_compat` | 同意，保留 |
| 显存 69.3 / 70 GiB | 太贴边。规则：所有 run 必须用同一个 optimizer。若任何一个 run OOM，不要只给那个 run 换 `adamw_8bit`；在 hpc_log 写 `BLOCKED:` 停下，由 Mac 侧决定是否整个网格换 8-bit 重跑 |
| R 在交互分配里顺序训练 | 同意，manifest 已记 job id |
| dev 分析后 | 按原计划停下等确认，再做 test |

## 7. Mac 侧回复 #2（2026-10-05）

对 hpc_log 2026-10-04 / 10-05 两段的三个选项选 **(b)**：在看 test 之前、在 dev 上改 E1 / E2 的量，改完冻结。训练不动、readout 不动、0.9 阈值不动、`configs/train.yaml` 不动。规则见 §0（E1a / E1b）与 e2_plan §1–2（r_0 协变量、P1 / P2 / P3），代码与测试已在仓库（`e1_metrics.py`、`12 --split train`、新 13；`python -m pytest -q` 99 passed 1 skipped）。Mac 侧用现有 dev readout 跑过新 13：`results/e1_dev_revised/summary.md`（E1 pending；E2 在 dev 上 PASS：P1 p 1.3e-6、P2 slope 1.15 p 1.3e-6、P3 2/3 正——dev 是选规则的 split，这个 PASS 由构造保证、只是描述，不要在 hpc_log 里当结果报；只有 test 的 `results/e1` 是确认性的）。本节的 <commit> 指 Mac 侧提交并推送本次修订后的 main HEAD；pull 不到这些文件就先在 hpc_log 写 `BLOCKED:` 等。

HPC agent 按顺序做（都在 compute 分配里）：

| # | 做什么 | 命令 | 验收 |
|---|---|---|---|
| 1 | 更新代码 | `git pull --rebase`；`python -m pytest -q` | 99 passed 1 skipped |
| 2 | 训练 prompt readout（E1a / E1b），18 个 run（15 个 O + 3 个 R；checkpoint 还在） | 每个 run：`python scripts/12_eval_student.py --run-dir runs/qwen3-4b/<run> --split train`（prompt 自动取 manifest 的 `data_path`，`data/sft/` 缺了先按 §2 第 1 步重建；eval.sbatch 把 `dev` 换成 `train` 即可） | 每个 run 有 `eval/train_responses.jsonl`，行数 = manifest `n_examples`（gpt4o / R 5,619、claude46 5,642、deepseek_v4 4,936），`train_readout_summary.json` 的 `sft_sha256` = manifest `data_sha256` |
| 3 | dev 分析，覆盖 | `python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b --split dev --out results/e1_dev --n-perm 10000 --n-boot 10000` | `summary.md` 顶部 Verdicts 表 E1 不再 pending（E1a 每个 O run `passed` True 且 `n_missing` 0；E1b 六对 ci_lo > 0.5）；P1 / P2 / P3 数字与 `results/e1_dev_revised` 一致（枚举是确定性的）；表下那行"dev = rule-selection split"说明 E2 的 dev 判定只是描述 |
| 4 | 冻结 | 在 `tasks/hpc_log.md` 追加一段：日期、E1a / E1b 的数字、一行 `E1 / E2 规则冻结于 <commit>`（<commit> = 第 1 步 pull 后的 main HEAD）；之后不改 13 的默认值 | — |
| 5 | test readout（只跑一次） | S_0：`MODEL=Qwen/Qwen3-4B-Base sbatch slurm/eval.sbatch - test`；每个 run：`sbatch slurm/eval.sbatch runs/qwen3-4b/<run> test`（18 个 run） | 19 个 `eval/test_responses.jsonl`，各 3,000 行（含 T0） |
| 6 | test 分析 | 同 3，`--split test --out results/e1` | `results/e1/summary.md` 的 Verdicts 表就是 E1 / E2 的结论；不再改任何量 |
| 7 | 提交 | `git add runs/qwen3-4b/*/train_manifest.json runs/qwen3-4b/*/eval results/e1_dev results/e1 tasks/hpc_log.md && git commit && git pull --rebase && git push` | Mac 侧写论文表 |
| 8 | 清理 | dev / train / test 都评完的 run：`rm -rf runs/qwen3-4b/<run>/checkpoint` | scratch 回落 |

注意：第 2 步 R run 的 E1a 是描述项（预期 ≈ 0.5），不进判定；`--split train` 不会评另一个 order，所以行数等于 SFT 行数而不是两倍；第 5 步之前不要生成任何 `test_responses.jsonl`；若 E1a 或 E1b 在 dev 上未过，照 e1_plan §3 的"不满足怎么办"写 `BLOCKED:` 停下，不进第 5 步。

## 8. E3 的 paired 网格（2026-10-05，改写已进仓库）

`data/rewrites_train/{teacher}/rewrites.jsonl` 已提交：两种风格都保留的 item GPT-4o 5,132 / Claude 4,682 / DeepSeek 4,668（F 过滤 3% 到 8%、C 4% 到 17%）。E3 要求 O / F / C 用同一组 prompt_id，所以 paired 的 O 也要重训，与 §2 的 O run（全集）分开放在另一个 student 命名空间，互不覆盖。可以和 §7 的 test 步骤并行提交（不同 run 目录），但 §7 第 5 步之前照样不要产生任何 test readout。

| # | 做什么 | 命令 | 验收 |
|---|---|---|---|
| 1 | 建 paired 文件（compute 分配里） | `for t in gpt4o claude46 deepseek_v4; do python scripts/10_build_sft_data.py --teacher $t --versions O,F,C --seeds 1,2,3,4,5 --rewrites-dir data/rewrites_train --out-dir data/sft_paired --tokenizer Qwen/Qwen3-4B-Base; done` | 45 个文件；每个 teacher 的 O / F / C 行数相同、`meta.json` 里 `paired: true`，n_examples 约 5,132 / 4,682 / 4,668；F / C 的 `letter` 与 O 逐行相同 |
| 2 | 训练 45 个 run | `ls data/sft_paired/*.jsonl > paired_runs.txt`；`STUDENT_SHORT=qwen3-4b-paired DATA_LIST=paired_runs.txt sbatch --array=0-44%8 slurm/train.sbatch` | `runs/qwen3-4b-paired/{teacher}_{O,F,C}_s{seed}/train_manifest.json` 45 个；同一 teacher 的三版本 `n_examples` 相同、`data_sha256` 不同 |
| 3 | readout | 每个 run：`--split train`、`--split dev`（`sbatch slurm/eval.sbatch runs/qwen3-4b-paired/<run> dev`），test 只在 §7 第 5 步之后、与 E1 的 test 一起做一次 | 45 × 3 个 responses 文件 |
| 4 | 现有分析 | `python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev --out results/e3_dev_e1tables`（13 按版本出 E1 / E2 表；F / C 版本的 P1 / P2 也在里面） | 表齐 |
| 5 | E3 专用指标 | **等 Mac 侧的 `scripts/15_e3_analysis.py`**（跨学生分歧率、excess teacher drift、homogenization、Δρ 随 form 的配对差、seed 配对 null；docs/04 组 C / D）。不要自己写一版 | — |
| 6 | 提交 / 清理 | 同 §7 第 7、8 步，目录换成 `runs/qwen3-4b-paired` | — |

注意：§2 的 `runs/qwen3-4b/*_O_*` 是 E1 / E2 的全集 O 学生，保留；paired 的 O 学生只用于 E3 的配对比较，两者的差异（全集 vs 交集，约 9% 的 item）顺带是稳健性检查。显存和 §2 一样贴边（Claude 的 F / C 版 rationale 和 O 一样长），OOM 规则见 §6。

## 9. 暂停 test（2026-10-05，Mac 侧）

hpc_log "dev 结果的解读 + 两处更正"是对的：§7 冻结的 P1 / P2 用 15 个 run 做置换，把同一 teacher 的 5 个 seed 当成了独立单位（伪复制）；可交换的单位只有 3 个 teacher，teacher 层面的精确 p 最小 1/6。E1a / E1b 不受影响。**§7 第 1 到 4 步照做（训练 prompt readout、dev 分析、E1 判定），第 5 步 test 等下一个冻结 commit**；§8 的建文件和训练照做。更正后的 E2 规则（原 Δρ 规则保留为 primary；次级统计量用 family 作重抽样单位；剂量反应只作描述）正在改，改完在 e2_plan §2 和这里写明 commit。
