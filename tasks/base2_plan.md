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
| 2 | HPC | 登录节点下载基座到 HF_HOME（非 gated，不需 token）；gate run；S_0 的 dev / test readout（`MODEL=HuggingFaceTB/SmolLM3-3B-Base`，`--student-short smollm3-3b`） |
| 3 | HPC | 重建 SFT（sha256 对 meta，已提交）；训练 C、K 各 15（`STUDENT_SHORT=smollm3-3b-e2c{,k} CONFIG=configs/train_smollm3_3b_e2c.yaml`）；train / dev readout；13 门；19 dev；冻结行 |
| 4 | HPC | test readout 一次；19 test（`--c-glob`、`--k-glob`、`--e1-glob` 指向新基座或 Qwen 的 E1，注明）；E7 的 21 在新基座上 dev 标定 → test 一次；删 checkpoint |

## 6. 披露

在看到 Qwen 上全部结果之后设计；判定规则原样复用；基座选择在任何新基座 run 之前写定。
