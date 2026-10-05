# HPC 工作日志（HAIC 上的 Claude Code agent 维护）

每个阶段结束追加一段：日期、做了什么、关键数字（表）、异常、下一步。卡住写 `BLOCKED:` 行。Mac 侧只读不改这个文件，回复写在 `tasks/e1_plan.md` / `tasks/e2_plan.md` 的对应位置。

## 状态板

| 项 | 状态 | 备注 |
|---|---|---|
| 环境（README §0） | 完成 2026-10-04 | ingrai / hai / QoS ingrai 已核实；训练 venv 重建；83 passed 1 skipped |
| gate run（README §1） | 完成 2026-10-04 | 显存 / 精度 / 丢弃过；一致性因 bf16 噪声未过 → 评估统一 transformers 后端；E0.7 过 |
| SFT 文件 O + R | 完成 2026-10-04 | 18 个文件，n 与计划一致；F / C 未建 |
| E1 18 run | 未开始 | |
| dev 评估 + 分析 | 未开始 | 冻结点 |
| test 评估 + 分析 | 未开始 | 只跑一次 |
| F / C 改写（Mac 侧） | 进行中 2026-10-04 | 完成后 `data/rewrites_train/` 进仓库，再建 paired O / F / C |

## 日志

### 2026-10-04 步骤 0：环境核实

在交互分配 129037（`hai-interactive`，haic-hgx-4，1 × H100 80GB）里做。

| 项 | 结果 |
|---|---|
| `nvidia-smi` | driver 550.54.14，CUDA 12.4 |
| `.venv` | torch 2.6.0+cu124（`torch.version.cuda` 12.4），transformers 5.18.0，`cuda.is_available()` True |
| `.venv-vllm` | vllm 0.8.5.post1、torch 2.6.0、xformers 0.0.29.post2、transformers 5.18.0，能 import（真模型加载在 gate 里验） |
| `sacctmgr` | account `ingrai`，QoS `ingrai`（每人 ≤ 32 GPU、32 个运行作业），不需要 `--qos` |
| partition `hai` | QoS `hai` 无限制，7 天上限，节点 haic-hgx-[1-5] H100 + haic-hgx-8 B200；`--gres=gpu:h100:1` 自动避开 B200（cu124 驱不动） |
| `--exclude=haic-hgx-2` | 保留：2026-08 笔记里的 NFS 黑洞节点，未重测（目前它 8 卡全被占，排除几乎无代价） |
| pytest | **83 passed, 1 skipped**（跳过的是 vLLM 一致性单测：训练 venv 不装 vLLM，真模型一致性在 gate 里做） |

异常与处理：

- 训练 `.venv`（指向 `/hai/scratch/tomyyc/.venv` 的软链）被装过 `.[train,eval]`：无版本约束的 vllm 0.30.0 拉进 torch 2.11 一套（torchvision 0.28、torchaudio 2.11、CUDA 13 库），之后 torch 被强制降回 2.6.0，`import transformers` 的模型类报 `operator torchvision::nms does not exist`，readout / sft 测试 11 个失败。按 README §0 重建：先装 torch 2.6.0+cu124，再 `-e ".[train]" pytest lemminflect`；旧 venv 移到 `/hai/scratch/tomyyc/.venv-broken-20261004`（确认无用后可删）。`eval.sbatch` 头注释里 "`.[train,eval]` 装进 `.venv`" 的说法改掉，README §0 改成先 torch 后 extras。
- `test_normalize_action_degerund` 依赖可选包 `lemminflect`（没有它，朴素回退把 Continuing 变成 Continu）。E0 代码不动，venv 里装上即过。
- `test_smoke_train_tiny` 断言 `peak_memory_gib is None`、`optimizer_fused is False`，只在 CPU 上成立；GPU 节点上 tiny 也在 CUDA 上训（3.29 GiB、fused）。测试改成按设备断言（CPU / GPU 两种都验过）。代码未改。
- sbatch 的 `--account` / `--partition` / `--exclude` 核实值与占位相同，只改注释为"2026-10-04 已核实"。

下一步：建 O + R 的 SFT 文件（步骤 1）。

### 2026-10-04 步骤 1：SFT 文件 O + R

在分配 129037 里跑 `10_build_sft_data.py`（O：三 teacher × seeds 1–5；R：`--random-label --ref-teacher gpt4o --seeds 1,2,3`；都加 `--tokenizer Qwen/Qwen3-4B-Base` 出 token 统计）。F / C 未建（改写还在 Mac 上跑）。

| 文件 | n_examples | families | order-stable 率 | A / B | target token / epoch | 最长样例 token |
|---|---|---|---|---|---|---|
| gpt4o_O_s{1..5} | 5,619 | 1,481 | 0.946 | 2,850 / 2,769 | 273,410 | 230 |
| claude46_O_s{1..5} | 5,642 | 1,489 | 0.947 | 2,830 / 2,812 | 441,661 | 300 |
| deepseek_v4_O_s{1..5} | 4,936 | 1,428 | 0.827 | 2,484 / 2,452 | 216,935 | 230 |
| random_R_s{1,2,3} | 5,619 | 1,481 | — | 约 2,810 / 2,810 | 89,904 | 187 |

- n 与计划一致（5,619 / 5,642 / 4,936）；target token 与 e1_plan §3 的 27 万 / 44 万 / 22 万一致；最长 300 token，远低于 `max_seq_len` 1024，预计 `n_dropped_too_long` 为 0。
- 同一 teacher 的 5 个 seed：`prompt_ids_sha256` 相同，文件 `sha256` 各不相同（只差行序）。注：e1_plan §3 "manifest 的 data sha256 应相同" 实际应看 prompt-id 集，文件 sha256 本来就随 seed 变。
- R 的 `ref_sha256` 等于同 seed 的 gpt4o_O 文件，prompt-id 集相同。

下一步：gate run（步骤 2）。

### 2026-10-04 步骤 2：gate run + 2b readout 校验

30 步真模型（`gpt4o_O_s1`，`--max-steps 30`，分配 129037）。全部数字在 `results/e1_gate/gate_summary.json`。

| 检查 | 结果 | 判定 |
|---|---|---|
| `peak_memory_gib` | 69.27；Claude 最长 96 条（232–301 token）3 步压力测试 69.5 | 过（≤ 70），不换 adamw_8bit |
| `precision` / `checkpoint_dtype` | bf16 / bfloat16（7.6 GB） | 过 |
| `n_dropped_too_long` | 0 | 过 |
| `steps_per_epoch` | 176（5,619 / 32） | 过 |
| 速度 | 1.59 s/step，加载约 45 s → 整 run（528 步）约 16 分钟 | — |
| loss | 0.91 → 0.78（30 步） | — |
| vLLM vs transformers（200 条 dev） | max ∣ΔP(A)∣ 0.062，mean 0.0055，p95 0.047，3 个 argmax 翻转；mass_AB 差 ≤ 0.002 | **未过**（阈值 0.01） |
| transformers bf16 vs fp32 | max 0.062，mean 0.0069 | 说明上一行是 bf16 噪声 |
| vLLM bf16 vs transformers fp32 | max 0.050，mean 0.0065 | 两后端离 fp32 一样远 |
| transformers bf16 batch 32 vs 64 | 0.0 | 确定、与 batch 无关 |
| S_0 vLLM vs transformers | max 0.062，mean 0.010；answer 率 0.33 vs 0.28（mass_AB 在 0.9 边界附近） | 同上 |

一致性未过的处理（e1_plan §5 的既定办法）：**E1 / E2 的全部 readout（S_0 和学生，dev 和 test）统一用 transformers 后端**（全词表 softmax，无 top-20 截断，与 batch 无关），dtype 仍是协议的 bf16。`eval.sbatch` 默认 `BACKEND=transformers`，在 `.venv` 里跑；vLLM 只用于 2b 的采样。可选（需 Mac 侧决定，不阻塞）：readout 改 fp32 可去掉约 0.007 的平均 bf16 噪声，代价很小；我没改。

2b readout 校验（`scripts/14_readout_check.py`，新增；first-token p(A) 取 transformers readout，vLLM 采样 T = 1、8 token、`parse_answer`）：

| 模型 | k | mean ∣diff∣ | 纯采样噪声的期望 ∣diff∣ | Pearson | 样本含字母 | 判定（< 0.05） |
|---|---|---|---|---|---|---|
| gate 学生 | 20 | 0.031 | 0.037 | 0.995 | 99.5% | 过 |
| S_0 | 20 | 0.070 | 0.069 | 0.977 | 86.5% | 名义未过 |
| gate 学生 | 200 | 0.011 | 0.012 | 0.999 | 99.8% | 过 |
| S_0 | 200 | 0.020 | 0.021 | 0.997 | 91.7% | 过 |

S_0 在 k = 20 时的 0.070 等于二项采样噪声本身（基座的 p(A) 不极端，20 个样本分辨不了）；k = 200 时两模型的差都落在噪声地板上。结论：first-token readout 与采样一致，学生评估**不**改用采样。

修的问题：

- `.venv-vllm` 的 transformers 5.18 让 vLLM 0.8.5 加载失败（`all_special_tokens_extended`）：pin `transformers==4.51.3`（vLLM 0.8.5 对应版本，支持 Qwen3）。两 venv 对 4,500 条 dev + test prompt 的 token id 逐条相同。
- **checkpoint 兼容性（bug，已修 + 测试）**：transformers 5 存的 `config.json` 只有 `rope_parameters`、没有 `rope_theta`，transformers 4.51 / vLLM 0.8.5 会静默回落到 rope_theta = 10000（Qwen3 是 1e6），`tokenizer_config.json` 的 list 型 `extra_special_tokens` 让 4.51 直接报错。`sft.py` 存盘后调用新函数 `write_legacy_compat` 补上 4.x 写法（不覆盖已有键，幂等；manifest 记 `checkpoint_legacy_compat`）。补丁前后 transformers readout 逐位相同（max ∣ΔP(A)∣ 0.0）。测试：`test_write_legacy_compat` + smoke 断言。
- 新增 `src/vcd/student/readout_check.py`（纯函数）+ `tests/test_readout_check.py`；pytest **87 passed, 1 skipped**。

下一步：提交 E1 的 18 个 run（步骤 3）。

### 2026-10-04 步骤 3 开始：E1 网格提交

- `sbatch --array=0-4,15-19,30-34,45-47%8 slurm/train.sbatch` → 作业 129420（`hai` 里优先级第 3，预计 23:32 开始）。
- 为不让交互分配的 H100 空等：取消 array 任务 45–47（R s1–3，`scancel 129420_45 129420_46 129420_47`，先取消再开跑，避免同一 run 目录两个写者），在分配 129037 里用同一脚本 `bash slurm/train.sbatch random R {1,2,3}` 顺序训练。结果与 array 等价（同代码、同数据顺序、同 seed）；manifest 的 `slurm_job_id` 是 129037。
- S_0 dev readout（transformers）：1,500 行，answer 25% / malformed 75%，mean mass_AB 0.875；完整 family（四个 variant 两种顺序都过 0.9）只有 5 个，S_0 作为参照很薄（协议所致，不放宽阈值）。
- 修 `scripts/13_e1_analysis.py`：只有 S_0、还没有 O run 时 `summary_md` 两处崩溃（空 pooled 表无 `teacher` 列；`core` 无 `delta_rho` 列）。加了 `test_analysis_script_cli_base_only`；pytest 88 passed 1 skipped。
