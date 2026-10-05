# HPC 工作日志（HAIC 上的 Claude Code agent 维护）

每个阶段结束追加一段：日期、做了什么、关键数字（表）、异常、下一步。卡住写 `BLOCKED:` 行。Mac 侧只读不改这个文件，回复写在 `tasks/e1_plan.md` / `tasks/e2_plan.md` 的对应位置。

## 状态板

| 项 | 状态 | 备注 |
|---|---|---|
| 环境（README §0） | 完成 2026-10-04 | ingrai / hai / QoS ingrai 已核实；训练 venv 重建；83 passed 1 skipped |
| gate run（README §1） | 未开始 | 含 vLLM / transformers 一致性、peak_memory_gib ≤ 70、E0.7 |
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
