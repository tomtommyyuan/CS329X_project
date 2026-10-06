# HPC 工作日志（HAIC 上的 Claude Code agent 维护）

每个阶段结束追加一段：日期、做了什么、关键数字（表）、异常、下一步。卡住写 `BLOCKED:` 行。Mac 侧只读不改这个文件，回复写在 `tasks/e1_plan.md` / `tasks/e2_plan.md` 的对应位置。

## 状态板

| 项 | 状态 | 备注 |
|---|---|---|
| 环境（README §0） | 完成 2026-10-04 | ingrai / hai / QoS ingrai 已核实；训练 venv 重建；83 passed 1 skipped |
| gate run（README §1） | 完成 2026-10-04 | 显存 / 精度 / 丢弃过；一致性因 bf16 噪声未过 → 评估统一 transformers 后端；E0.7 过 |
| SFT 文件 O + R | 完成 2026-10-04 | 18 个文件，n 与计划一致；F / C 未建 |
| E1 18 run | 完成 2026-10-04 | 18 / 18，0 失败；12 个在 array 129420，6 个在交互分配 |
| dev 评估 + 分析 | 完成 2026-10-05 | 冻结规则（456b487）重跑 `results/e1_dev`；E1a / E1b 过；dev 判定仅描述 |
| test 评估 + 分析 | 完成 2026-10-05 | `results/e1`（确认性）：E1 PASS，E2 primary FAIL，E2 secondary fail |
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

### 2026-10-05 dev 结果的解读（探索性，只用 dev）+ 两处更正

用户要求解释结果对论文的意义。我做了一次 25 个 agent 的只读分析：4 个分析视角、对 8 条核心论断各做 1–2 个对抗性核查、对新数字做独立复算、最后综合。全部只用 dev，没有打开任何 test 文件，也没有改仓库代码。结论在 `results/e1_dev_diag/interpretation.md`，完整记录在 `interpretation_record.json`，脚本在 `wf/`。

**更正我前面写过的两点：**

- **grid permutation 的 p < 1e-4 不成立**（上面两段写过）。同一 teacher 的 5 个 seed 几乎是复制品，可交换的单位只有 3 个 teacher，即 3! = 6 种指派。真实指派在 6 种里排第一，精确 p = 1/6，这也是这个设计能给出的最小值。方向保留，p 值不能引用。
- **"suggestibility 有继承、teacher 顺序保持"要降级为有条件成立。** 学生的排序（0.174 > 0.123 > 0.052，两两 CI 不含 0）是稳的，但下面三条决定了它不等于"从 teacher 继承"：
  - dev 上 GPT-4o 与 Claude 两个 teacher 的差 +0.012 [−0.034, 0.057]，本身分不开；
  - DeepSeek 学生 ≈ 基座（0.174 vs 0.168）；
  - R 学生也降到 ≈ 0。

  较稳的表述是：SFT 用训练标签里的 framing–标签关联，替换了基座自带的 suggestibility。

**新的探索性结果（均经独立复算）：**

| 量 | 结果 |
|---|---|
| 学生 × teacher 的 profile 相关矩阵：对角均值减非对角均值（seed 合并，见过的 framing） | +0.090 [0.040, 0.140]，5/5 seed 为正；T0（未见 framing）上 +0.026，p 0.20 |
| 争议 cell 上的相对 side-taking：A 的学生比 B 的学生更常站 A | +0.09 / +0.14 / +0.19，CI 都不含 0（gpt4o–claude 一对的下界 0.003） |
| 控制 S_0（放宽规则）profile 后的 pooled Δρ | gpt4o −0.092 → +0.020，claude −0.111 → −0.022，DeepSeek +0.182 → +0.086，三者 CI 都含 0 |
| 预注册 Δρ 的 family 置换 null 均值 | gpt4o −0.094、claude −0.090、DeepSeek +0.088（置换保留了 teacher 的 T5 / T6 主效应），所以 "Δρ > 0" 这条门槛在三个 teacher 之间不对称 |
| 照现规则跑 test 的通过概率（dev 估计当真值，300 个 family 重抽样） | 只有 DeepSeek 通过 ≈ 0.69；≥ 2/3 通过 ≈ 0.01–0.02，把 dev 估计误差也算进去 ≈ 0.09 |

**另外发现的三个问题，留给 Mac 侧：**

- E1 未过时，S_0 的 Δρ 是 NaN，e2_plan §2 的控制条件实际无法检验。
- scripts/13 在 1/3 通过时打印 "E2 FAIL"，不区分 e2_plan 的"部分成立"和"不成立"。
- docs/E0_results 已经记了 test 侧 teacher 可靠度（Claude 0.329、DeepSeek 0.466），这会触发 E0 的"两个及以上 teacher 可靠度 < 0.5"门槛。该门槛原本是在 pilot 上定的。

这三点我都没改，只记录。

**推荐（详见 interpretation.md）：**

- E2 原规则保留为 primary，失败如实报告。
- 在 dev 上只冻结一个预先声明的次级主统计量，例如上表的对角或交互量（限见过的 framing，family bootstrap 给 CI），并披露全部尝试过的版本；grid permutation 改报 teacher 层面的精确 p。
- 之后 test 只跑一次。
- 受控的剂量实验或第二个基座属于新实验，要另行预注册。

BLOCKED: 仍等 Mac 侧决定（E1 门槛如何解释、是否改用次级统计量、是否加新实验）；test 未评估，checkpoint 保留。

### 2026-10-05 e1_plan §7 第 1–4 步：训练 prompt readout、dev 重跑、冻结

- 第 1 步：`git pull --rebase` 到 456b487，pytest **109 passed, 1 skipped**。
- 第 2 步：18 个 run 的 `--split train` readout（交互分配 129037，同一 `eval.sbatch` 路径，fp32，batch 64）。行数 = manifest `n_examples`（5,642 / 4,936 / 5,619），`sft_sha256` = `data_sha256`，18 / 18 通过。
- 第 3 步：新 13 覆盖 `results/e1_dev`（n_perm = n_boot = 10,000，69 s）。与 Mac 侧 `results/e1_dev_revised` 对比：除 E1a / E1b 两段（那边是 pending）以外 `summary.md` 逐行相同；所有 CSV / JSON 数值差 ≤ 3e-16，枚举与固定 seed 的重抽样是确定性的。

| E1a（门：每个 O run ≥ 0.95） | 训练标签复现 |
|---|---|
| claude46 s1–5 | 0.985–0.988 |
| deepseek_v4 s1–5 | 0.989–0.996 |
| gpt4o s1–5 | 0.983–0.986 |
| random R s1–3（描述，不进判定） | 0.553–0.557 |

| E1b（门：ci_lo > 0.5） | other | 争议项 | 站自己 teacher 的比例 [95% CI] |
|---|---|---|---|
| claude46 | deepseek_v4 / gpt4o | 299 / 357 | 0.930 [0.902, 0.954] / 0.919 [0.892, 0.945] |
| deepseek_v4 | claude46 / gpt4o | 299 / 198 | 0.951 [0.931, 0.968] / 0.918 [0.889, 0.944] |
| gpt4o | claude46 / deepseek_v4 | 357 / 198 | 0.910 [0.883, 0.934] / 0.900 [0.862, 0.933] |

E1a、E1b 都过，**E1 PASS**，进入 test。E2 在 dev 上的判定（primary FAIL、secondary pass）只是描述，不当结果报。

**E1 / E2 规则冻结于 456b487。** 此后不改 13 的默认值、readout、阈值和规则；test 只跑一次。

§8 并行进展：45 个 paired SFT 文件已建（`data/sft_paired/`，5,132 / 4,682 / 4,668，O / F / C 的 prompt 顺序与字母逐行相同，最长 265 token）。训练 array 130120（`STUDENT_SHORT=qwen3-4b-paired DATA_LIST=paired_runs.txt`，`%8`）已开跑，目前无 OOM，peak ≤ 69.7 GiB。

QoS 每人最多 64 个作业，没法给每个 run 单独挂评估作业。所以只挂了 3 个 follower（130129–130131，每个 teacher 一个，`afterany:130120`，脚本在 `/hai/scratch/tomyyc/vcd_diag/eval_paired.sh`），依次跑每个 paired run 的 train 和 dev readout。test readout 只在 `results/e1/summary.md` 已存在时才跑，用来保证"§7 第 5 步之后再做 test"。

### 2026-10-05 e1_plan §7 第 5–6 步：test readout 与确认性分析（只跑一次）

- **第 5 步。** S_0 和 18 个 run 的 test readout 在交互分配 129037 里跑，用同一 `eval.sbatch` 路径，transformers、fp32、batch 64。19 个 `test_responses.jsonl` 各 3,000 行，含 T0。学生 answer 率 ≥ 99.9%；S_0 为 21.3%（0.9 门下）。
- **第 6 步。** `13 --split test --out results/e1`，n_perm = n_boot = 10,000，用时 2 分钟。13、e1_metrics、profile、readout、`configs/train.yaml` 与 456b487 逐字节相同（之后的 fc54a5c 只加了 E3 的代码）。

**确认性结论（`results/e1/summary.md` 的 Verdicts，原样）：**

| 判定 | test 值 | verdict |
|---|---|---|
| E1a | 最低训练标签复现 0.983，最低 answer 率 0.999 | pass |
| E1b | 争议项最低 ci_lo 0.862 | pass |
| **E1** | | **PASS** |
| **E2 primary**（预注册 Δρ） | claude46 −0.155 [−0.307, −0.055]，p_perm 0.973（null 均值 −0.073）；deepseek_v4 +0.127 [0.029, 0.229]，p_perm 0.116（null 均值 +0.082），p_holm 0.348；gpt4o −0.067 [−0.185, 0.054]，p_perm 0.348；0/3 | **FAIL** |
| **E2 secondary**（D 与 D_specific 守门） | D 0.027 [−0.013, 0.070]，p 0.061；D_specific 0.067 [0.011, 0.125]，D_shared −0.040（290 个 family） | **fail**（D 的 CI 含 0、p > 0.05） |

**E0 门槛（docs/03 §1）。** test 侧 teacher 可靠度 claude46 0.329、deepseek_v4 0.466，均 < 0.5，P2 不成立：RQ1 / E2 / E7 降为 exploratory，主线改为 E2b / E3 / E4 / E5，本项目做 E3。

ρ_own / 上限 sqrt(2r / (1 + r))：

| teacher | ρ_own | 上限 | ρ / 上限 |
|---|---|---|---|
| claude46 | 0.085 | 0.704 | 0.12 |
| deepseek_v4 | 0.444 | 0.797 | 0.56 |
| gpt4o | 0.374 | 0.904 | 0.41 |

描述项（无判定）：

| 项 | test |
|---|---|
| mean ΔρPartial（15 run） | −0.014，teacher 层面精确 p 0.333（6 种重标号中排第 2） |
| P3（partial Δρ，Holm） | claude46 −0.104（p_holm 0.927）、deepseek_v4 +0.105（0.242）、gpt4o −0.033（0.489） |
| D，仅 T0（探索） | 0.054 [−0.001, 0.114]，p 0.006 |
| raw D（探索） | 0.033 [−0.003, 0.071]，p 0.099 |
| scale-free D（探索） | 0.057 [0.011, 0.104] |
| S_0 控制 | 最近的 teacher 是 deepseek_v4，ρ 0.380 [0.327, 0.434]，比次近者高 0.100 [0.036, 0.167]：基座训练前就最像 DeepSeek |
| suggestibility s（290 个 family） | 学生 claude 0.026 / deepseek 0.140 / gpt4o 0.108；teacher 0.045 / 0.113 / 0.063；R 0.001；base prior 0.146 |
| s 的两两差 | 学生 deepseek − gpt4o +0.032 [0.017, 0.047]，gpt4o − claude +0.082 [0.067, 0.099]；学生 − 自己 teacher：claude −0.019 [−0.042, 0.004]、deepseek +0.027 [0.002, 0.053]、gpt4o +0.045 [0.022, 0.068]；学生 − base prior：claude −0.120、gpt4o −0.038、deepseek −0.006 [−0.030, 0.019] |
| 剂量反应 slope（s_run 对 s_T） | 1.441（pearson 0.856，顺序保持），teacher 层面精确 p 1/6 |

以上是 E1 / E2 的正式结论，此后不再改任何量。

### 2026-10-05 §7 第 8 步清理 + E3（e1_plan §8 / e3_plan §4）进度与交接

- **E1 清理。** 18 个 E1 run 的 train / dev / test readout 齐全，checkpoint 已删（`runs/qwen3-4b` 现在 107 MB）。
- **paired 训练。** array 130120 的 45 个任务全部 COMPLETED、exit 0，peak 最高 69.91 GiB，没有 OOM，optimizer 统一。45 个 manifest 与 train log 已提交。
- **paired train / dev readout。** follower 130174–130176 在跑（每个 teacher 一个）。
- **E3 阶段 2 检查**（`results/e3_dev` 的 `content_check.csv` / `register_separation.csv`，已提交）：
  - F / C 与 O 的字母一致率 1.0，六项 judge check 全为 1.0；claude46 C 的 `letter_matches_rewrite` 0.9998，是 e3_plan 列出的那 1 条已知项。
  - F–C register 分离三个 teacher 都 pass：LOO 0.921 / 0.927 / 0.907，logistic 0.959 / 0.952 / 0.942，与 e3_plan 的冒烟数字一致。
  - O–F 只有约 0.60 可分（描述项）。

**交接。** 交互分配 129037 约 2026-10-05 18:30 PDT 到期，本 session 随之结束。若下面几步没做完，新 session 从这里接：

1. 确认 130174–130176 都结束：每个 paired run 有 `eval/train_responses.jsonl` 和 `dev_responses.jsonl`；train 的行数 = manifest `n_examples`，dev 为 1,500 行。脚本在 `/hai/scratch/tomyyc/vcd_diag/eval_paired.sh`，跑缺的 run 时用 `sbatch slurm/eval.sbatch runs/qwen3-4b-paired/<run> {train,dev}`。
2. e1_plan §8 第 4 步：`python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev --out results/e3_dev_e1tables`。
3. e3_plan §4 第 2–3 步：`python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split dev --out results/e3_dev` → 在本文件写 13 行 verdict 和一行 `E3 规则冻结于 <HEAD>` → 加 `--frozen-commit <HEAD>` 重出一次 → 提交。
4. e3_plan §4 第 4 步（冻结之后才做）：每个 teacher 一个作业跑 45 个 paired test readout，`sbatch ... /hai/scratch/tomyyc/vcd_diag/test_paired.sh <teacher>`。脚本没找到冻结行就拒绝运行。
5. 第 5–7 步：`15 --split test --out results/e3 --frozen-commit <HEAD>` → 提交 → 删除 paired checkpoint。

### 2026-10-05 E3：paired readout、dev 分析、冻结（e1_plan §8 第 3–4 步，e3_plan §4 第 2–3 步）

- **paired readout。** follower 130174–130176 全部 COMPLETED（约 1 小时），90 个 readout 都 exit 0。45 个 run 的 train readout 行数 = `n_examples`、`sft_sha256` = `data_sha256`；dev 各 1,500 行；全部 fp32。
- **e1_plan §8 第 4 步。** `13 --student qwen3-4b-paired --split dev --out results/e3_dev_e1tables` 已出。
- **e3_plan §4 第 2 步。** `15 --split dev --out results/e3_dev`：run inventory 每个 teacher n_O = n_F = n_C = 5、paired 5 / 5；13 行 verdict 都已出、没有 pending；头部为 "not yet frozen"、"dev = freeze split"。

dev 上的 verdict 只是描述，不当结果报：

| 行 | tier | 各 teacher（claude46 / deepseek_v4 / gpt4o）的 stat | q95 | 过 / TOST | verdict |
|---|---|---|---|---|---|
| 分歧率 F vs C | primary | −0.006 / −0.000 / +0.005 | 0.011 | 0/3 / 0/3 | inconclusive |
| 分歧率 O vs F | secondary | −0.026 / −0.016 / −0.016 | 0.011 | 0/3 / 0/3 | inconclusive |
| 分歧率 O vs C | secondary | −0.006 / +0.002 / +0.003 | 0.011 | 0/3 / 0/3 | inconclusive |
| flip rate F − O | primary | −0.007 / +0.001 / −0.005 | 0.016 | 0/3 / 0/3 | inconclusive |
| 跨 framing JSD F − O | primary | +0.001 / −0.002 / −0.003 | 0.006 | 0/3 / 1/3 | inconclusive |
| agreement F − O | secondary | −0.002 / −0.001 / +0.003 | 0.011 | 0/3 / 0/3 | inconclusive |
| excess drift F − O | primary | +0.001 / +0.001 / −0.001 | 0.005 | 0/3 / 0/3 | inconclusive |
| ΔρPartial F − O | primary | +0.001 / −0.031 / −0.004 | 0.052 | 0/3 / 0/3 | inconclusive |
| flip rate C − O | primary | −0.005 / +0.000 / −0.006 | 0.016 | 0/3 / 0/3 | inconclusive |
| 跨 framing JSD C − O | primary | −0.001 / −0.006* / −0.006 | 0.006 | 1/3 / 1/3 | inconclusive |
| agreement C − O | secondary | −0.004 / +0.000 / +0.005 | 0.011 | 0/3 / 0/3 | inconclusive |
| excess drift C − O | primary | −0.003 / −0.004 / −0.005 | 0.005 | 0/3 / 0/3 | inconclusive |
| ΔρPartial C − O | primary | −0.039 / +0.011 / +0.031 | 0.052 | 0/3 / 0/3 | inconclusive |

注：分歧率 O vs F 三个 teacher 都为负，也就是同 seed 的 F / O 学生比两个不同 seed 的 O 学生更像。原因是同 seed 的一对共享初始化和数据顺序，e3_plan §3 已说明它会让 null 偏保守。只记录，不改。

**E3 规则冻结于 5e98fe3。** 15 和 e3_metrics 自 fc54a5c 起未改；之后不改 15 的默认值和 e3_metrics 的阈值；test 只跑一次。

### 2026-10-05 E3 test readout 进行中（e3_plan §4 第 4 步，冻结 5e98fe3 之后）+ 交接更新

- **e1_plan §8 第 4 步重出。** `results/e3_dev_e1tables` 加了 `--sft-dir data/sft_paired` 后重出。§8 原命令没带这个参数，13 默认用全集 `data/sft/` 当 E1a 目标，O run 因此出现 487 / 960 / 268 条"missing"，判为 fail，F / C 则找不到目标。这是输入错误，不是规则改动。重出后 paired 的 E1a pass（最低 0.981）、E1b pass（最低 ci_lo 0.841）。
- **paired 的 13 表里 E2 secondary D 是 NaN**（0 个 family）：13 只在本 namespace 里找 base run，`runs/qwen3-4b-paired` 下没有。按版本的 D 由 15 的 `joint_D_by_version` 负责（它用 `qwen3-4b.base_B_s0`），所以这里不处理。
- **paired test readout。** 6 / 45 已完成（三个 teacher 的 O s1、O s2，各 3,000 行）。剩下 39 个拆成 15 个互不重叠的作业（每个 ≤ 3 个 run），脚本 `/hai/scratch/tomyyc/vcd_diag/test_runs.sh <run...>`，找不到 E3 冻结行就拒绝运行；作业 id 在 `/hai/scratch/tomyyc/vcd_diag/paired_test_ids.txt`。交互分配上的 `steal_pending.sh` 从队尾取仍在 PD 的作业，先 scancel 再在本地跑它的 run，保证每个 run 只有一个写者。

**交接（若本 session 在交互分配 18:30 到期前没做完）：**

1. 检查 45 个 `runs/qwen3-4b-paired/*/eval/test_responses.jsonl` 是否都在且都是 3,000 行。缺的或行数不对的（删掉坏文件后）用 `sbatch --account=ingrai --partition=hai --gres=gpu:h100:1 -c 8 --mem=64G -t 00:45:00 --exclude=haic-hgx-2 -J vcd-test-paired -o logs/%x-%j.out /hai/scratch/tomyyc/vcd_diag/test_runs.sh <run ...>` 补，先确认没有同一 run 的作业仍在跑。
2. `python scripts/15_e3_analysis.py --runs-dir runs --student qwen3-4b-paired --split test --out results/e3 --frozen-commit 5e98fe3`。Verdicts 表即 E3 的确认性结论，effect / no effect / inconclusive 如实报。
3. 提交 `runs/qwen3-4b-paired/*/eval results/e3 tasks/hpc_log.md`，然后对 dev / train / test 都齐的 paired run 执行 `rm -rf runs/qwen3-4b-paired/<run>/checkpoint`。

### 2026-10-05 E3 test：readout 与确认性分析（e3_plan §4 第 4–5 步，只跑一次）

- **readout。** 45 个 paired run 的 test readout 齐全，各 3,000 行。分工如下，每个 run 只有一个写者：
  - 6 个由最初的三条流完成；
  - 7 个在交互分配上跑，从队列里先 scancel 再接手；
  - 32 个由互不重叠的 sbatch 作业完成。
- **分析。** `15 --split test --out results/e3 --frozen-commit 5e98fe3`。15 和 e3_metrics 与 5e98fe3 逐字节相同；inventory 每个 teacher O / F / C 各 5 个，paired 5 / 5。

**确认性结论（`results/e3/summary.md` 的 Verdicts）：13 行中 12 行 inconclusive、1 行 no effect、0 行 effect。**

| 行 | tier | 过 q95 | TOST 过 | 方向 | verdict |
|---|---|---|---|---|---|
| 分歧率 F vs C | primary | 1/3（deepseek +0.008，2.9 null sd） | 0/3 | + | inconclusive |
| 分歧率 O vs F | secondary | 0/3 | 0/3 | — | inconclusive |
| 分歧率 O vs C | secondary | 1/3（claude +0.007） | 0/3 | + | inconclusive |
| flip rate F − O | primary | 0/3 | 0/3 | — | inconclusive |
| 跨 framing JSD F − O | primary | 0/3 | 2/3（claude、gpt4o） | — | **no effect** |
| agreement F − O | secondary | 0/3 | 0/3 | — | inconclusive |
| excess drift F − O | primary | 0/3 | 0/3 | — | inconclusive |
| ΔρPartial F − O | primary | 2/3（deepseek +0.035、gpt4o −0.034，符号相反） | 0/3 | mixed | inconclusive |
| flip rate C − O | primary | 0/3 | 0/3 | — | inconclusive |
| 跨 framing JSD C − O | primary | 0/3 | 1/3 | — | inconclusive |
| agreement C − O | secondary | 1/3（gpt4o +0.008） | 0/3 | + | inconclusive |
| excess drift C − O | primary | 0/3 | 0/3 | — | inconclusive |
| ΔρPartial C − O | primary | 1/3（deepseek +0.054，5.3 null sd） | 0/3 | + | inconclusive |

以上是 E3 的正式结论，此后不再改任何量。
