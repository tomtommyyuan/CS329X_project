# CLAUDE.md

研究项目：value-consistency distillation。teacher（GPT-4o / Claude Sonnet 4.6 / DeepSeek V4）回答两选项道德困境，学生（Qwen3-4B-Base）在 teacher 回答的三种版本 O / F / C（原文 / 正式改写 / 口语改写）上 SFT，测学生是否继承 teacher 对问法极性的顺从（suggestibility）、文风改写是否改变继承。目标 ACL / EMNLP main。

## 文档地图（先读再动手）

| 文件 | 内容 |
|---|---|
| `docs/01_related_work.md` … `docs/04_eval_metrics.md` | 研究设计、模型与数据、实验表 E0 到 E8、指标。中文 |
| `docs/05_training_stack.md` | 训练 / 评估代码契约：template、SFT 文件格式、readout、E1 / E2 指标、SLURM、如何跑 |
| `docs/E0_results.md` | E0 pilot 与 Phase 1 teacher 数据的全部结果和决定 |
| `docs/E1_results.md` | E1 / E2 / E3 的确认性结果（test 已跑，不再改） |
| `tasks/e0_plan.md`、`tasks/e1_plan.md`、`tasks/e2_plan.md`、`tasks/e3_plan.md` | 已完成阶段的计划与状态 |
| `tasks/e2c_plan.md` | **当前阶段** E2c（争议增强训练池）的预注册：§4 训练集、§6 冻结判定规则、§8 行 6–7 HPC 步骤、§11 行 I 建 SFT 的命令 |
| `slurm/README.md` | 集群上的一次性安装、gate run、48 run 网格、恢复 |
| `tasks/hpc_log.md` | HPC agent 的工作日志（见下） |

代码在 `src/vcd/`（Python 3.12，包名 `vcd`），脚本 `scripts/01` 到 `19`，测试 `tests/`（`python -m pytest -q`，当前 168 passed 1 skipped，skip 是 vLLM 缺席时的后端对照）。代码、注释、commit 英文；文档中文，简洁，能用表就用表，LLM 能从要点推出的细节不写。

## 两个角色

- **Mac 侧（API 与数据）**：teacher 查询、改写、审计、数据文件、分析与论文表。所有付费 API 调用只在这里发生，密钥在 Mac 的 `.env`（gitignore）。
- **HPC 侧（GPU）**：HAIC 上的 Claude Code agent，只做 GPU 任务：建训练文件、训练学生、评估、跑分析脚本、把结果提交回仓库。**集群上没有也不需要任何 API 密钥**；不要向任何人索取密钥，不要调用 OpenAI / Anthropic / Google / Together / DeepSeek 的 API。

## 永不（对两个角色都成立）

- 不让 family 跨 train / dev / test；不动 `data/prompts/`、`data/families/`、`data/teacher_phase1/`、`data/teacher_e2c/`、`data/rewrites_train/`（输入数据）。E2c 的 `data/teacher_e2c/*_e2c_{C,K}_demo.jsonl` 与 `data/sft_e2c*/*.jsonl` 在本地用已提交的输入重建（`17b assemble`、`10`），不提交；jsonl 的 sha256 必须与已提交的 `.meta.json` 一致。
- 不改协议性常量：`configs/train.yaml` 的超参、`src/vcd/train/data.py` 的 template 与 `ASSISTANT_PREFIX`、`src/vcd/data/framings.py` 的 stems、readout 的 0.9 质量阈值、E2 / E2c 的决策规则（e2_plan §2、e2c_plan §6）与 `scripts/13`、`scripts/19` 的默认值。要改先在 `tasks/hpc_log.md` 或 `tasks/e0_plan.md` 写明理由，等 Mac 侧确认。
- 不在看了 test 结果之后再选 readout、阈值或规则；dev 冻结，test 只跑一次（`tasks/e2_plan.md` §2）。
- 不把拒答 / malformed 当 50 / 50 插补；不单独报一致性（必须与 agreement、JSD 同报）。
- 不提交模型权重、`data/sft/`、`logs/`、密钥（`.gitignore` 已配）；不 force-push。
- 不在 head node 上计算（pytest、建数据都进 compute 分配）；同一 run 目录不并行提交两个作业。
- 不改 E0 的代码路径（`src/vcd/teacher/`、`src/vcd/rewrite/`、`scripts/01` 到 `09`）。

## HPC agent 的工作流

1. `git pull --rebase` 到最新 main；读 `tasks/hpc_log.md` 的最后两段（前任 agent 的约定与现状），再读当前阶段的计划（E2c：`tasks/e2c_plan.md` §4–§6、§8 行 6–7、§11 行 I；E1 / E2 / E3 已全部完成）。
2. 环境与 gate run 按 `slurm/README.md` §0 到 §1；`train.sbatch` / `eval.sbatch` 里的 `--account=ingrai`、`--partition=hai`、`--exclude=haic-hgx-2` 是占位，先用 `sacctmgr show user $USER withassoc format=user,account%20,qos%30` 核实再提交。
3. 在 compute 分配里建训练文件（`scripts/10_build_sft_data.py`）。E2c：先 `scripts/17b_e2c_demo_inputs.py assemble`（每 teacher 两个条件，必须 11880 / 11880、missing 0），再按 e2c_plan §11 行 I 建 `data/sft_e2c/`（C）与 `data/sft_e2ck/`（K），核对 30 个 sha256。
4. 训练、评估、分析、清理、提交，按当前阶段计划的表走（E2c：e2c_plan §8 行 6–7；C 用 `STUDENT_SHORT=qwen3-4b-e2c`，K 用 `qwen3-4b-e2ck`，run id 前缀随之变化，不与 E1 撞名；robustness 轮见 e2c_plan §12 追加表：K_n → `qwen3-4b-e2ckn`，Cnf → `qwen3-4b-e2cnf`，都用 `CONFIG=configs/train_e2c.yaml`）。
5. 每个阶段结束在 `tasks/hpc_log.md` 追加一段（日期、做了什么、关键数字、异常、下一步），卡住时写一行以 `BLOCKED:` 开头的说明，然后提交推送；Mac 侧会读这个文件。
6. 提交只包含：`runs/<student>/*/train_manifest.json`、`train_log.jsonl`、`eval/`（student 目录 `qwen3-4b`、`qwen3-4b-paired`、`qwen3-4b-e2c`、`qwen3-4b-e2ck`、robustness 轮的 `qwen3-4b-e2ckn`、`qwen3-4b-e2cnf`，归档的 `*-3ep`、`*-pilot5`）、`results/e1*`、`results/e3*`、`results/e2c*`、`tasks/hpc_log.md`、以及你确实改了的代码和测试。先 `git pull --rebase` 再 `push`；冲突只会出现在 markdown，保留双方内容。

## 代码改动的规矩

- 修 bug 可以直接改，但要加或改测试，并在 compute 分配里跑 `python -m pytest -q` 全过；在 `tasks/hpc_log.md` 记一行。
- 新功能放 `src/vcd/` 下对应子包，带 docstring 与类型标注；脚本用 argparse，`--help` 要能让合作者直接用。
- 不引入新的重型依赖；vLLM 是 `.[eval]` 可选依赖，transformers 后端是它的替代。
- 报告结果用表，不用图；数字放表里，不写进句子。

## 常用命令

```bash
source .venv/bin/activate && export HF_HOME=/hai/scratch/$USER/hf HF_HUB_OFFLINE=1
python -m pytest -q                                                        # compute 分配里
sbatch --array=0-4,15-19,30-34,45-47%8 slurm/train.sbatch                  # E1：O + R 的 18 个 run（已完成）
STUDENT_SHORT=qwen3-4b-e2c  DATA_LIST=data/sft_e2c/runs.txt  sbatch --array=0-14%8 slurm/train.sbatch   # E2c-C 15 run
STUDENT_SHORT=qwen3-4b-e2ck DATA_LIST=data/sft_e2ck/runs.txt sbatch --array=0-14%8 slurm/train.sbatch   # E2c-K 15 run
sbatch slurm/eval.sbatch runs/qwen3-4b/gpt4o_O_s1 dev                      # 评估一个 run
python scripts/13_e1_analysis.py --runs-dir runs --student qwen3-4b-e2c --split dev --sft-dir data/sft_e2c --out results/e2c_dev/C   # K：qwen3-4b-e2ck / data/sft_e2ck / results/e2c_dev/K
python scripts/19_e2c_analysis.py --split dev --out results/e2c_dev                                                         # test：--split test --out results/e2c --frozen-commit f73f097
squeue --me -o "%.9i %.4t %.60j %.12b"; sacct -S today -X --name=vcd-train --format=JobID,State,ExitCode,Elapsed
```
