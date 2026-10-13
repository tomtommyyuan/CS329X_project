# 剂量反应预注册：继承量随争议示范比例变化（2026-10-13，写于任何混合条件 run 存在之前）

> 上游：[e2c_plan](e2c_plan.md) §4 / §6 / §12（C、K、K_n、gap、5 epoch 配方）、[docs/supplemental_experiments.md](../docs/supplemental_experiments.md) §3 行 1。

## 1. 问题与条件

E2c 只有两个点：共识示范（K / K_n）gap ≈ 0，争议示范（C）gap > 0。本实验把争议示范的比例 p 做成四点曲线：

| p | 条件 | 来源 | 规模 | 配方 |
|---|---|---|---|---|
| 0 | K_n | 已训（`runs/qwen3-4b-e2ckn`） | = C | 5 epoch |
| 0.25 | M25 | `scripts/10c_mix_sft.py`：每 teacher 取 C 的 25% + K 的 75%，按 variant 分层，总数与 C 相同，5 seed 同一集合 | = C | 5 epoch（`configs/train_e2c.yaml`） |
| 0.50 | M50 | 同上，50 / 50 | = C | 5 epoch |
| 1 | C | 已训（`runs/qwen3-4b-e2c`） | — | 5 epoch |

所有条件样例数相同（gpt4o 4,964 / claude46 4,838 / deepseek_v4 2,497），唯一变量是争议示范的比例。**实际构建（2026-10-13，`10c`，seed 20261013）**：M25 从 C 取 1,241 / 1,210 / 624 条、其余来自 K；M50 取 2,482 / 2,419 / 1,249；按 variant 分层、C 与 K 的 item 互不相交、5 seed 同一集合、行序按 `scripts/10` 的 family 置换规则生成。设计说明：混合按 **item** 分层抽样而非按 family，所以混合集覆盖的 family 数多于 C（如 gpt4o M25 2,355 族 vs C 1,451 族），每族样例更少；25% 与 50% 的争议子集是独立抽样、非嵌套（重合约一半）。两点斜率与 family bootstrap CI 已验证等于 E2c 的 C − K_n 归因量。学生命名 `qwen3-4b-e2cmix25` / `qwen3-4b-e2cmix50`。训练 prompt 文件 = C 与 K 的并集（`data/prompts/e2c_CK_prompts.jsonl`，供 train readout 与 13 使用）。

## 2. 门

每个 run 训练标签复现 E1a ≥ 0.95（混合集不要求 E1b）。未过则该条件按与 C 相同的步数（`--max-steps` 780 / 760 / 395）重训一次，仍不过如实报告。

## 3. 冻结的量与判定（`scripts/24_dose_response.py`）

| 项 | 定义 |
|---|---|
| 每 run 的量 | gap_T = agree_own − max_other agree_other（`e2c_metrics`，同 19） |
| 趋势统计量 | 每 teacher：20 个 run（4 个 p × 5 seed）的 gap 对 p 的最小二乘斜率；family bootstrap 2,000 次（四个条件共用同一组 family 重抽）的 95% CI |
| 判定 | ≥ 2/3 teacher 斜率 CI 下界 > 0 → **dose-response supported**；1/3 partial；0/3 not supported |
| 描述 | 四点的 seed 均值与 CI、Spearman；翻转率与 suggestibility 对 p 的斜率（代价曲线） |
| 预测 | DeepSeek、Claude 的斜率 > 0；GPT-4o 平（它没有可继承信号）；代价（翻转率）随 p 单调上升 |

## 4. 步骤

| # | 侧 | 做什么 |
|---|---|---|
| 1 | Mac | `10c` 建 M25 / M50（30 个 jsonl，meta + runs.txt 提交，jsonl 不入库）；`cat` 出 `e2c_CK_prompts.jsonl`；24 在 K_n / C 两端点上冒烟（与 results/e2c_robust/Kn、results/e2c 的 gap 逐项相同）；提交本文件 |
| 2 | HPC | 重建 30 个 jsonl（sha256 对 meta）；S_0 复制到两个新目录；`STUDENT_SHORT=qwen3-4b-e2cmix25 CONFIG=configs/train_e2c.yaml DATA_LIST=data/sft_e2c_mix25/runs.txt sbatch --array=0-14%8 slurm/train.sbatch`（M50 同理）；train readout 带 `--prompts data/prompts/e2c_CK_prompts.jsonl`；dev readout |
| 3 | HPC | 13（`--sft-dir data/sft_e2c_mix25 --prompts-train data/prompts/e2c_CK_prompts.jsonl`）判 E1a；`24 --split dev --out results/dose_dev`（描述）；hpc_log 写冻结行 |
| 4 | HPC | test readout 每 run 一次；`24 --split test --out results/dose --frozen-commit <本文件提交 hash>`；删 checkpoint |

## 5. 披露

在 E2c（含 robustness）的 test 结果之后设计；趋势统计量与判定在任何混合条件 run 之前写定于此。四个条件里两个（K_n、C）的结果已知。
