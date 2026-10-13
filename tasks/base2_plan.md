# 第二基座预注册：跨学生家族复现 E2c（2026-10-13，写于任何新基座 run 之前）

> 上游：[e2c_plan](e2c_plan.md) §4–§6、§12；[e7_plan](e7_plan.md) §3；[docs/supplemental_experiments.md](../docs/supplemental_experiments.md) §2 行 1。

## 0. 为什么

所有学生都是 Qwen3-4B-Base，而它训练前就最像 DeepSeek（E1：S_0 与 DeepSeek 的 profile 相关最高；E7：未训练的基座被判为 DeepSeek）。最强的结果恰是 DeepSeek 的，所以"DeepSeek 最可继承 / 最可溯源"与"基座先验像 DeepSeek"分不开。换一个预训练家族的基座，若结果仍在，混杂即解；若 DeepSeek 的优势消失、换成别家，也是重要结论。

## 1. 基座

| 候选 | 选择理由 | 注意 |
|---|---|---|
| **`HuggingFaceTB/SmolLM3-3B-Base`（默认）** | 非 gated、Apache-2.0、3.1B 与 Qwen3-4B 同量级、预训练数据与 Qwen 不同；栈的 CPU 冒烟已用 SmolLM2-135M，tokenizer 家族已验证 | 单卡全参配方可直接复用 |
| `meta-llama/Llama-3.2-3B`（备选） | 更常见 | gated：HPC agent 不能持有 HF token，需用户在登录节点自行下载 |

不选 Gemma（与改写器 Gemini 同家族）、不选 ≥ 7B（单卡 fp32 master + AdamW 放不下，改 LoRA 或多卡会改协议）。

## 2. 复现什么

| 条件 | run 数 | 配方 | 数据 |
|---|---|---|---|
| S_0（未训练基座）dev / test readout | — | — | — |
| E2c-C | 15 | `configs/train_smollm3_3b_e2c.yaml`（= train_e2c.yaml 换 student，5 epoch） | `data/sft_e2c`（与 Qwen 完全相同的文本） |
| E2c-K | 15 | 同上 | `data/sft_e2ck` |
| E1 原集 O（可选，若 GPU 允许） | 15 | `configs/train_smollm3_3b.yaml`（3 epoch） | `data/sft` |

学生命名 `smollm3-3b-e2c` / `smollm3-3b-e2ck` /（`smollm3-3b`）。

## 3. 门与阶梯

| 门 | 规则 | 不过时 |
|---|---|---|
| gate run（slurm/README §1） | 30 步冒烟：readout 两后端一致、显存 < 75 GiB、模板首 token 为字母 token | 修环境，不改协议 |
| E1a | 30 个 run 都 ≥ 0.95；E1b 六对 ci_lo > 0.5（C 的 O run） | 该 teacher 的 C 与 K 一起 +2 epoch 重训一次（唯一一级），仍不过如实报告 |

## 4. 冻结的判定（原样复用 e2c_plan §6，`19`）

primary：C 上 ≥ 2/3 teacher gap > seed-pair q95 且 family bootstrap CI > 0；归因：C − K ≥ 2/3。E1 参照行用 Qwen 的 E1（不同基座，只作参照，另注明）或本基座的 E1 O（若训）。**另报 S_0 对三个 teacher 的一致率**：若新基座的先验不再最像 DeepSeek 而 DeepSeek 的 gap 仍最大，则混杂排除；反之如实写。E7 的检测器在新基座的学生上重标定（dev 负例 = 新基座的 K 学生 + S_0）后在 test 跑一次（描述）。

预测（无把握，如实写）：DeepSeek 与 Claude 的 gap 仍 > 0；GPT-4o 仍 ≈ 0；代价（翻转率上升）复现。

## 5. 步骤

| # | 侧 | 做什么 |
|---|---|---|
| 1 | Mac | 配置文件 + 配置差异测试 + `scripts/26_base2_check.py`（tokenizer / 模板 / 字母 token / 长度 / 显存估算）；提交本文件 |
| 2 | HPC | 登录节点下载：`HF_HOME=/hai/scratch/$USER/hf hf download HuggingFaceTB/SmolLM3-3B-Base --exclude "onnx/*"`（5.7 GiB；不加 exclude 会拉 39 GiB 的 ONNX）；compute 分配里 `python scripts/26_base2_check.py --offline --out /hai/scratch/$USER/vcd_diag/base2_check.md` 须 PASS；gate run：`python scripts/11_train_student.py --config configs/train_smollm3_3b_e2c.yaml --data data/sft_e2c/claude46_O_s1.jsonl --out runs/_smoke/smollm3_gate --seed 1 --max-steps 30`（看 peak_memory_gib ≤ 70、n_dropped_too_long 0、n_params ≈ 3.075e9），再 `12 --run-dir runs/_smoke/smollm3_gate --split dev --limit 200 --backend transformers`，然后删 `runs/_smoke`；**S_0 必须带配置**：`MODEL=HuggingFaceTB/SmolLM3-3B-Base EXTRA_ARGS="--config configs/train_smollm3_3b.yaml" sbatch slurm/eval.sbatch - dev`（不带 --config 会写到 runs/qwen3-4b/base_B_s0，绝不可 --overwrite 那里）→ `runs/smollm3-3b/base_B_s0/eval/`，复制到两个新 namespace |
| 3 | HPC | SFT 文本与 tokenizer 无关，直接用集群已有的 `data/sft_e2c`、`data/sft_e2ck`（sha256 对 meta）；训练 C、K 各 15：`STUDENT_SHORT=smollm3-3b-e2c CONFIG=configs/train_smollm3_3b_e2c.yaml DATA_LIST=data/sft_e2c/runs.txt sbatch --array=0-14%8 slurm/train.sbatch`（K 换 e2ck / sft_e2ck）；train readout 带 `--prompts data/prompts/e2c_{C,K}_prompts.jsonl`；dev readout；13 `--student smollm3-3b-e2c --config configs/train_smollm3_3b_e2c.yaml --sft-dir data/sft_e2c --prompts-train data/prompts/e2c_C_prompts.jsonl --out results/base2_dev/C`（K 同理）判门；19 dev `--c-glob "runs/smollm3-3b-e2c/*_O_s*/eval/dev_responses.jsonl" --k-glob "runs/smollm3-3b-e2ck/..." --e1-glob "runs/smollm3-3b/*_O_s*/..."（没训 E1 则留空，E1 行缺失）--out results/base2_dev`；冻结行 |
| 4 | HPC | test readout 一次（含 S_0 的 test）；19 test 同上 `--out results/base2 --frozen-commit <hash>`；13 test；E7 的 21 需先在 `provenance.py` 注册新 namespace（Mac 侧改）后再做；删 checkpoint（每个 5.7 GiB） |

## 6. 披露

在看到 Qwen 上全部结果之后设计；判定规则原样复用；基座选择在任何新基座 run 之前写定。

## 7. 代码侧检查结果（2026-10-13，`scripts/26_base2_check.py`，报告在 Mac 草稿目录）

| 项 | SmolLM3-3B-Base | Qwen3-4B-Base |
|---|---|---|
| " A" / "A" / " B" / "B" 单 token | 是（362 / 32 / 426 / 33），`readout.letter_token_ids` 原样可用 | 是 |
| 模板首个目标 token = 字母 token | 600 条真实 SFT 行全部成立 | 成立 |
| 最长行（prompt + 目标 + EOS） | 570 token < 1024 | 592 |
| eos / pad | eos 128001；pad 缺，栈设 pad = eos | eos = pad |
| 参数量 / 预计峰值显存 | 3.075 B / ≈ 55 GiB（Qwen 69–72） | 4.022 B |
| 每步时间 | ≈ 1.34 s → E2c 760 步 ≈ 17 分钟 | 1.76 s |

注意：集群的 `.venv-vllm`（transformers 4.51）不能加载 `smollm3` 架构，E0.7 式的 vLLM 对照（scripts/14）对本基座不可用；协议 readout 是 fp32 transformers，不受影响。SmolLM3 的 tokenizer 是 Llama-3 式 128k 词表（不是 SmolLM2 的 49k），所以备选 Llama-3.2-3B 的字母 id 几乎相同，下载后用 26 复核即可。

