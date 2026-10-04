# E1 执行计划：蒸馏基线（HAIC 上执行）

> 协议：[docs/03_experiments.md](../docs/03_experiments.md) §2、§8；指标：[docs/04_eval_metrics.md](../docs/04_eval_metrics.md)；代码契约与命令：[docs/05_training_stack.md](../docs/05_training_stack.md) §9、[slurm/README.md](../slurm/README.md)。执行者：HPC 上的 Claude Code agent（见 [CLAUDE.md](../CLAUDE.md)）。

## 0. 问题与决策规则

| 问 | 学生学到 teacher 的判断了吗？seed noise 多大？ |
|---|---|
| run | 15 个 S_{T,O}（3 teacher × 5 seeds，O 版）+ 3 个随机标签学生 R |
| 主指标 | teacher agreement（多数行动一致率）、student–teacher JSD、seed-noise null（同条件 seed 两两之差的分布） |
| 决策规则 | 每个学生与**自己** teacher 的 agreement 必须高于与其他两个 teacher 的；否则先修训练，不进 E2 / E3 |
| 控制 | R 学生：agreement 应接近 50%，一致性"看起来很高"是因为处处 50 / 50，所以一致性永远和 agreement、JSD 一起报 |
| 基座 | S_0 = 未训练的 Qwen3-4B-Base，同样 readout，给 malformed 率和"训练前"的参照 |

## 1. 前置条件（已满足的打勾）

- [x] Phase 1 teacher 数据：`data/teacher_phase1/{teacher}_train_demo.jsonl`、`{teacher}_{dev,test}_profile.jsonl`（含 T0），在 git 里
- [x] 训练文件可重建：`scripts/10_build_sft_data.py`（O 版三 teacher 5,619 / 5,642 / 4,936 条，R 3 seeds）；`data/sft/` 不进 git，在集群上重建
- [x] 代码：78 个测试通过；CPU 端到端冒烟通过
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

## 3. 验收与预期

| 检查 | 预期 | 不满足怎么办 |
|---|---|---|
| S_0 与学生的 malformed 率 | 学生 < 5%；S_0 可以高（基座未学格式） | 学生 > 5%：查 template 是否与训练一致（docs/05 §1.3），不是去放宽 readout |
| teacher agreement | 学生与自己 teacher ≥ 0.85，且高于与其他 teacher；R 学生对所有 teacher ≈ 0.5 | 自己 ≤ 他人：先查数据文件 teacher 字段、训练 loss 曲线，再谈 E2 |
| student–teacher JSD | 自己 teacher 最小 | 同上 |
| seed-noise null | 同 (teacher, O) 五个 seed 两两 agreement 之差的 SD，预计 ≤ 0.02 | 大于 0.05：检查 seed 是否真的只改了顺序（manifest 的 data sha256 应相同） |
| 一致性 | 学生的 flip rate、cross-framing JSD 与 teacher 同量级；R 学生"一致"但 agreement 0.5 | — |
| 训练量 | `n_target_tokens` 约 GPT-4o 27 万、Claude 44 万、DeepSeek 22 万 / epoch | 差一个数量级：数据文件错 |

## 4. 预算与时间

18 run × 约 0.5 GPU 小时（3 epochs，5,600 条 × 160 token）+ 评估每 run 约 5 分钟（vLLM，4,500 条 prompt）≈ 11 GPU 小时；并发 8 时约 2 到 3 小时墙钟。checkpoint 每个约 8 GB，评完即删。

## 5. 已知风险

- Claude teacher 的 profile 依赖选项顺序（顺序 split-half 可靠度 0.33，跨 pass 重测 0.99）：E1 的 agreement 用两种顺序平均后的多数行动，不受影响；E2 要把它当 ρ 的上界报。
- DeepSeek 的 T6 顺序不稳定最多（O 版只有 4,936 条）：三个 teacher 的训练量不等，E1 的比较按 teacher 内 seed 配对，不跨 teacher 比绝对值。
- vLLM 与 transformers 在 base 模型上 p_letters 可能差在 logprobs 截断（vLLM 只给 top-20）：gate 的一致性检查就是为此；不一致就统一用 transformers 后端评估。
