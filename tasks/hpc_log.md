# HPC 工作日志（HAIC 上的 Claude Code agent 维护）

每个阶段结束追加一段：日期、做了什么、关键数字（表）、异常、下一步。卡住写 `BLOCKED:` 行。Mac 侧只读不改这个文件，回复写在 `tasks/e1_plan.md` / `tasks/e2_plan.md` 的对应位置。

## 状态板

| 项 | 状态 | 备注 |
|---|---|---|
| 环境（README §0） | 完成 2026-10-04 | ingrai / hai / QoS ingrai 已核实；训练 venv 重建；83 passed 1 skipped |
| gate run（README §1） | 完成 2026-10-04 | 显存 / 精度 / 丢弃过；一致性因 bf16 噪声未过 → 评估统一 transformers 后端；E0.7 过 |
| SFT 文件 O + R | 完成 2026-10-04 | 18 个文件，n 与计划一致；F / C 未建 |
| E1 18 run | 完成 2026-10-04 | 18 / 18，0 失败；12 个在 array 129420，6 个在交互分配 |
| dev 评估 + 分析 | 完成 2026-10-04 | `results/e1_dev`；**E1 规则未过**（gpt4o 2/5、claude46 4/5），等 Mac 侧决定 |
| test 评估 + 分析 | 未开始，等确认 | 只跑一次 |
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
- 同样理由再取消 array 任务 32–34（deepseek_v4 O s3–5，取消时仍是 PD），在分配 129037 里训练；集群这时只给 array 约 3 张卡。交互卡上训练与 dev 评估串行，不共用 GPU。

### 2026-10-04 步骤 3–4：E1 网格训练 + dev 评估与分析

训练（18 / 18 完成，0 失败；array 129420 的 12 个在 haic-hgx-1/3/5，R 与 deepseek s3–5 在交互分配 haic-hgx-4）：

| 条件 | run | steps | n_examples | target token / epoch（含 EOS） | peak GiB | 分钟 | final loss | dropped |
|---|---|---|---|---|---|---|---|---|
| gpt4o O | 5 | 528 | 5,619 | 279,029 | 69.36–69.37 | 13.8–15.1 | 0.093–0.134 | 0 |
| claude46 O | 5 | 531 | 5,642 | 447,303 | 69.79–69.91 | 14.6–15.2 | 0.163–0.248 | 0 |
| deepseek_v4 O | 5 | 465 | 4,936 | 221,871 | 69.33–69.41 | 12.2–15.0 | 0.136–0.241 | 0 |
| random R | 3 | 528 | 5,619 | 95,523 | 68.99–69.01 | 15.3–16.0 | 0.039–0.040 | 0 |

全部 bf16、checkpoint bfloat16（每个 7.6 GB，共 136 GB）、带 `checkpoint_legacy_compat`。R 的 loss ≈ ln2 / 16 token：固定 rationale 学会、随机字母学不会，符合预期。

dev readout（transformers 后端，`eval.sbatch` 同一脚本）：19 个文件 × 1,500 行（含 T0）。学生 answer 率 99.9–100%（mass_AB ≈ 1.0）；S_0 answer 25%、malformed 75%（mass_AB 均值 0.875），四个 variant 都可用的 family 只有 5 个。

`13_e1_analysis.py --split dev --out results/e1_dev`（n_perm = n_boot = 10,000，代码版本 36f5e1e）对照 e1_plan §3：

| 检查 | 预期 | dev 结果 | 判定 |
|---|---|---|---|
| malformed | 学生 < 5% | 0–0.1%（S_0 75%） | 过 |
| agreement own | ≥ 0.85 且高于他人 | seed 均值 gpt4o 0.855（DeepSeek 0.855）、claude46 0.846（他人最大 0.829）、deepseek_v4 0.843（0.826） | **未过**：≥ 0.85 只有 gpt4o；"高于他人"见下行 |
| E1 规则（每个 O seed own > other_max） | 全过 | deepseek_v4 5/5；claude46 4/5（s3：0.837 vs gpt4o 0.841）；gpt4o 2/5（s1 平 0.859，s2 / s4 / s5 低 0.002–0.005，都是 DeepSeek） | **未过** |
| R agreement | ≈ 0.5 | 0.43–0.56 | 过 |
| JSD own 最小 | 自己最小 | 只有 deepseek_v4 学生如此；gpt4o 与 claude46 学生都是对 DeepSeek 最小 | 未过（受校准混淆，见诊断 3） |
| seed-noise null | 两两 ∣Δagree∣ 的 SD ≤ 0.02 | SD 0.005–0.008，q95 ≤ 0.022 | 过 |
| 一致性 | 与 teacher 同量级 | flip rate：学生 deepseek 0.08–0.12 / gpt4o 0.06–0.08 / claude 0.04–0.05，teacher 0.107 / 0.052 / 0.073；R flip 0.09–0.20、跨 framing JSD ≈ 0（处处 0.5） | 过 |
| 训练量 | 27 万 / 44 万 / 22 万 | 见上表 | 过 |

E2 在 dev 上（只作参考，判定在 test）：pooled Δρ claude46 −0.110 [−0.259, 0.035]、deepseek_v4 +0.183 [0.056, 0.308]（p_perm 0.020，p_holm 0.061）、gpt4o −0.091 [−0.232, 0.057] → 0/3，E2 FAIL。但 grid permutation（打乱 15 个 run 的 teacher 归属）：观测 mean Δρ −0.005，null 均值 −0.081、SD 0.017，p < 1e-4。也就是说，学生的 profile 比随机指派更接近自己的 teacher，只是所有学生最接近的单个 profile 都是 DeepSeek。

诊断（按 e1_plan §3 "先查数据文件 teacher 字段、训练 loss 曲线"；都不是预注册规则，输出与脚本在 `results/e1_dev_diag/`）：

1. 数据与训练没问题。SFT 文件的 teacher / version 字段全对；loss 正常下降。seed 1 学生在自己的训练 prompt（5,948 条）上复现自己 teacher 的标签：gpt4o 98.5%、claude46 98.5%、deepseek_v4 99.4%（R 51%）；在两 teacher 标签不同的训练项上站自己一边：gpt4o 学生对 Claude 92.4%、对 DeepSeek 89.9%，deepseek 学生对 gpt4o 96.5%、对 Claude 96.3%，claude 学生对 gpt4o 91.3%、对 DeepSeek 92.6%。
2. teacher 特有信号很小。训练标签两两一致 93.3–95.8%（gpt4o–DeepSeek 只有 198 / 4,734 项不同；stable_one 只留顺序稳定的项，多为共识项）；dev 上 teacher 两两 majority 一致 0.83–0.89，有争议的 cell 只有 65–100 个（33–47 个 family）。seed 合并后，在争议 cell 上站自己一边的比例：deepseek 学生 0.63 / 0.63，gpt4o 学生对 Claude 0.66、对 DeepSeek 0.45，claude 学生 0.49 / 0.54，95% family-bootstrap CI 大多含 0.5。
3. JSD 被 teacher 校准混淆：p_sym 落在 [0.1, 0.9] 外的 cell 比例 GPT-4o 0.89、Claude 0.92、DeepSeek 0.64，学生 0.79–0.83。不一致时，越极端的 teacher JSD 罚得越重，所以 "JSD 自己最小" 对所有学生都偏向 DeepSeek。
4. **基座本身像 DeepSeek。** S_0 放宽 0.9 规则后（仅诊断）suggestibility δ(T5) − δ(T6) = 0.166，与 profile 相关：DeepSeek 0.488、GPT-4o 0.283、Claude 0.247。所有学生从一个像 DeepSeek 的先验出发，于是每个学生的 ρ_other_max 都是 DeepSeek，Δρ = ρ_own − max ρ_other 结构上偏向 DeepSeek 学生。
5. **suggestibility 有继承，三 teacher 的顺序保持**：δ(T5) − δ(T6) teacher DeepSeek 0.140 > GPT-4o 0.077 > Claude 0.056；学生 0.168 > 0.121 > 0.051（seed SD ≤ 0.014）；R 0.001。Claude 学生把基座的 0.166 压到 teacher 的水平。

需要 Mac 侧决定（我没改任何规则、阈值或 readout；test 未评估，`test_responses.jsonl` 一个也没有）：

- E1 规则在 dev 未过。按 e1_plan 应"先修训练，不进 E2 / E3"，但诊断 1 说明训练本身没坏，未过来自 teacher 特有信号小 + 基座先验像 DeepSeek。可选：(a) 记为结果，照现规则跑 test；(b) 在看 test 之前、在 dev 上改 E1 / E2 的量（例如以 S_0 profile 为协变量的 partial ρ、争议 cell 上的 agreement、以 grid permutation 为主检验），改完再冻结；(c) 改训练（`order_policy both` 保留争议项、或换基座），需要重训。
- 可选：readout 改 fp32（去掉约 0.007 的 bf16 噪声，代价很小）。
- E2 的冻结点：dev 分析用的 13 / e1_metrics 版本是 36f5e1e。若 Mac 侧确认照现规则进 test，就以此为冻结点；若选 (b)，冻结点是改完后的 commit。

BLOCKED: E1 决策规则在 dev 未过（gpt4o 2/5、claude46 4/5 seed 通过），按 e1_plan 不进 test / E2；训练已核实无误，等 Mac 侧在上面三个选项里决定。checkpoint 全部保留（136 GB）。

### 2026-10-05 dev readout 按 Mac 决定改 fp32 重跑

Mac 侧在 7dc06f6（2026-10-04 23:00）把 `readout.dtype` 改成 float32，早于任何 dev 分析；我在 00e5c77 提交时才 rebase 到它，所以上一段的 dev 数字是 bf16 readout 算的。现已全部改用 fp32 重跑：19 个 dev readout（`OVERWRITE=1`，S_0 用 `EXTRA_ARGS=--overwrite`）、`results/e1_dev`、`results/e1_dev_diag`。bf16 版本只留在 git 历史（00e5c77）。`12_eval_student.py` 的 readout summary 现在记录 `dtype` 与 `batch_size`（加了测试）。

| 量 | bf16（00e5c77） | fp32（现行） |
|---|---|---|
| E1 每 seed 通过 | claude46 4/5、deepseek_v4 5/5、gpt4o 2/5 | 相同，通过 / 未过的 seed 也相同 |
| agree_own seed 均值 gpt4o / claude46 / deepseek_v4 | 0.855 / 0.846 / 0.843 | 0.856 / 0.846 / 0.844 |
| agree_other_max seed 均值 | 0.855 / 0.829 / 0.826 | 0.856 / 0.829 / 0.826 |
| pooled Δρ（p_holm）claude46 / deepseek_v4 / gpt4o | −0.110（0.954）/ 0.183（0.061）/ −0.091（0.954） | −0.111（0.956）/ 0.182（0.063）/ −0.092（0.956） |
| O run 各指标最大变化 | — | agree ≤ 0.004、Δρ ≤ 0.012、flip ≤ 0.007 |
| R run flip rate 最大变化 | — | 0.147（R 处处 p ≈ 0.5，多数行动由精度噪声决定；正是一致性不能单独报的原因） |

诊断在 fp32 下复算，变化 ≤ 0.01：训练标签复现 98.5% / 98.5% / 99.5%；S_0（放宽 0.9）与 DeepSeek 的 profile 相关 0.494；suggestibility 学生 0.168 / 0.121 / 0.051 vs teacher 0.140 / 0.077 / 0.056。上一段的结论与三个待决选项不变。

BLOCKED: 同上一段，E1 决策规则在 dev 未过（fp32 下相同），等 Mac 侧决定；test 未评估。
