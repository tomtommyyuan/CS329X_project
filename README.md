# Value-consistency distillation: E0 pilot

研究文档在 [docs/](docs/)（01 related work，02 模型与数据，03 实验，04 指标）；工程计划与状态在 [tasks/e0_plan.md](tasks/e0_plan.md)。

## 环境

```bash
uv venv .venv --python 3.12 && uv pip install --python .venv/bin/python -e . pytest
.venv/bin/python -m pytest -q
```

API key 填在项目根目录的 `.env`（已 gitignore，模板已建好）：teacher 用 `OPENAI_API_KEY`、`ANTHROPIC_API_KEY`、`DEEPSEEK_API_KEY`；rewriter B 用 `GEMINI_API_KEY`（Gemini 3.8 Flash，需开计费的项目，免费档每分钟 5 次不够用；备选 Llama 走 `TOGETHER_API_KEY`）；judge J 用 `TOGETHER_API_KEY`（GLM-5.3-Flash）；自托管 vLLM 备选用 `VLLM_B_URL` / `VLLM_J_URL`。所有脚本启动时自动读取，shell 里已有的变量优先。

原始数据放在 `data/raw/`（DailyDilemmas、MoralChoice、ValueConsistency 的 HF 文件；见 `scripts/01_build_families.py` 里的路径）。

## E0 步骤

| 步骤 | 命令 | 产出 |
|---|---|---|
| 01 families | `python scripts/01_build_families.py` | `data/families/families.jsonl` |
| 02 splits | `python scripts/02_make_splits.py` | split 字段 + `splits_summary.json` |
| 03 framings | `python scripts/03_build_framings.py --split pilot` | `data/prompts/pilot_prompts.jsonl`，`data/annotation/t3_review_pilot.csv` |
| 03b T0（需 J） | `python scripts/03b_generate_t0.py` 然后重跑 03 | `data/prompts/t0_texts.jsonl` |
| 04 teacher | `python scripts/04_query_teachers.py --teacher gpt4o --mode demo` 和 `--mode profile`；主研究 teacher ∈ gpt4o, claude46, deepseek_v4（见 `configs/models.yaml` 的 `main_teachers`） | `data/teacher/{teacher}_{mode}.jsonl`（可中断续跑，调用有 sqlite 缓存） |
| 05 分析 | `python scripts/05_e0_analysis.py` | `results/e0/*.csv`，`results/e0/e0_summary.md`（含 gate 判定） |
| 06 改写审计（需 B、J） | `python scripts/06_rewrite_pilot.py --config configs/e0_v2.yaml --teacher gpt4o --tag v8`（`--judge-fallback glm53_together` 默认开；`none` 关） | `data/rewrites_<tag>/{teacher}/` |
| 07 readout 校验（需 vLLM） | `python scripts/07_readout_check.py --model-key llama33_70b` | `results/e0/readout_check_*.csv` |
| 08 人工标注 | `python scripts/08_annotation.py export-framing` / `export-rewrite --teacher gpt4o`；填完后 `score-framing A.csv B.csv` | `data/annotation/` |
| 08 盲审表 + AI 审计 | `08_annotation.py export-rewrite-blind --config configs/e0_v2.yaml --tag v8 --name rewrite_audit_blind_v8`；`08b_ai_audit.py --sheet <csv> --model-key claude46`、`--model-key gpt55 --max-tokens 4000`；`08_annotation.py score-single <filled> --key <KEY>`、`score-rewrite A B --key <KEY>` 算 κ | `data/annotation/v2/` |
| 09 报告 | `python scripts/09_report.py` | `results/e0/report.md` |

模型、价格、endpoint 在 `configs/models.yaml`；pilot 规模、k、temperature、E0 门槛在 `configs/e0.yaml`。

## 代码布局

`src/vcd/data`（loader、规范化、去重切分、framings）→ `src/vcd/teacher`（prompt 解析、查询、profile 数学）→ `src/vcd/rewrite`（record 抽取、改写、检查）→ `src/vcd/readout`（logit vs 采样）→ `src/vcd/analysis`（E0 表、标注表、报告）。`src/vcd/llm` 封装 OpenAI 兼容接口与 Anthropic 接口，带缓存、重试、并发限制。
