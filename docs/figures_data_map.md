# 图表数据地图：给画图 agent 的精确入口（2026-10-25）

> 每张图 / 表用哪个文件、哪些列、怎么过滤。全部数据都在仓库里；没有任何图需要 HPC 或 API。图的结构与措辞见 `docs/paper_narrative.md` §4、§7，数字核对以各 `*_summary.md` / `summary.md` 为准。CSV 都是 pandas 直接可读的扁平表。

## 0. 通用约定

| 项 | 说明 |
|---|---|
| run id | `{student}.{teacher}_{version}_s{seed}`；version O = 原文、F = 正式改写、C = 口语改写、R = 随机标签、B = 未训练基座 |
| 条件 → run 目录 | E1 原集 `runs/qwen3-4b`；E3 paired `runs/qwen3-4b-paired`；E2c-C `runs/qwen3-4b-e2c`；K `…-e2ck`；K_n `…-e2ckn`；Cnf `…-e2cnf`；M25 / M50 `…-e2cmix25` / `…-e2cmix50`；E3c paired `…-e2c-paired`；生成学生 `…-e2c-gen`；第二基座 `runs/smollm3-3b-e2c` / `…-e2ck`、S_0 `runs/smollm3-3b/base_B_s0`；归档 `*-3ep`、`*-5ep`、`*-pilot5`（只做附录） |
| teacher 顺序与配色 | 固定 gpt4o / claude46 / deepseek_v4；候选 teacher 另有 gpt41、gpt4o_mini、gpt4_0613、claude_haiku45 |
| 确认性 vs 描述性 | 目录名无 `_dev` 的是 test（确认性，各只跑一次）；`*_dev` 只作描述；文件名含 `-3ep` / `-5ep` 的是被修订替换的归档版本 |
| CI | 列名 `ci_lo` / `ci_hi` 或 `wilson_lo` / `wilson_hi`；null 阈值列 `null_q95` |

## 1. 正文图表

| 图 / 表 | 文件 | 关键列 / 过滤 | 注意 |
|---|---|---|---|
| 图 1 设计总图 | 手画 | — | 术语按 paper_narrative §8 |
| 表 1 teacher 极性效应与 suggestibility（7 模型） | `results/e0_v2/`（pilot，7 家）；`results/phase1/{dev,test}/`（3 家，dev / test） | 各目录的 `summary.md` 给表；按 teacher 的 δ(T5)、δ(T6)、s = δ(T5) − δ(T6)、顺序 split-half 可靠度 | pilot 与 phase1 的 family 集不同，分开列 |
| 图 2 teacher 标签一致 + 争议率按来源 | 一致矩阵：`results/e2c/decomposition/test/teacher_pairwise.csv`（test cell 级，0.917–0.930）；训练标签一致 93–96% 见 `docs/E1_results.md` §2；争议率：`results/e2c/screen_report.csv` 与 `screen_report.md` 的 "by source" 表 | `contested_rate`、`majority_differ`、`uncertain_band`、`claude_order_split`、`flip_only` 按 `source` | mc_low 0.4%、Moral Stories 10%、Reddit 两源 30–38%、ETHICS 37% |
| 表 2 E1 / E2 | `results/e1/agreement.csv`（run × teacher agreement）、`results/e1/summary.md`（判定行）、`results/e1/e1_table.csv` | `agree_own`、`agree_other_max`；E2 primary / secondary 行 | 规则版本披露在 `tasks/e2_plan.md` §2 |
| **图 3 gap 与翻转率随争议比例** | 曲线：`results/dose/dose_gaps.csv`（share × teacher：`gap`、`ci_lo`、`ci_hi`、`flip_rate`、`s`）、`results/dose/dose_slopes.csv`（斜率与 CI）；第二基座两端点：`results/base2/e2c_gaps.csv`（condition C / K 行）；Qwen 的 C / K / K_n 单独也在 `results/e2c/e2c_gaps.csv`、`results/e2c_robust/Kn/e2c_gaps.csv` | x = share ∈ {0, 0.25, 0.5, 1}；一个面板 gap、一个面板 flip_rate；SmolLM3 只有 p = 0（K）与 p = 1（C）两点，用不同记号 | 判定文字在 `results/dose/dose_summary.md`、`results/base2/e2c_summary.md` |
| 表 3 E2c 判定与 robustness | `results/e2c/e2c_gaps.csv`、`e2c_attribution.csv`、`e2c_verdict.json`；K_n：`results/e2c_robust/Kn/`；Cnf：`results/e2c_robust/Cnf/`；base2：`results/base2/` | `gap`、`ci_lo`、`ci_hi`、`null_q95`、`exceeds_null`、`ci_above_zero`、`passed`；归因 `diff`、`ci_lo`、`ci_hi` | 13 的冻结 E2 行在各目录 `C/summary.md`、`K/summary.md` |
| **图 4 格子结构分解** | `results/e2c/decomposition/test/follow_rates.csv`（condition × version × teacher × category：`follow_own_mean`、`follow_other_max_mean`、`n_cells`）、`follow_by_variant_own_unique.csv`、`cell_structure_counts.csv` | 主面板：category = own_unique，条件 E1 / K / E2c_C / E3c（O、F、C）；x 为 teacher；辅面板：按 variant | 由 `scripts/23_cell_decomposition.py` 生成，描述性；cell 数 34 / 48 / 45 很小 |
| 表 4 E3 vs E3c 的 13 + 1 行 | `results/e3/verdicts.csv`、`results/e3c/verdicts.csv`（13 行：`metric`、`tier`、`n_pass`、`n_tost`、`direction`、`verdict`、`p_row`）；gap 行：`results/e3c/e3c_gap_verdicts.csv`；每 teacher 统计量：`results/e3c/e3c_gap_verdict_teachers.csv`、`results/e3/verdicts.json` | 并排两列 verdict | register 可分性：`results/e3c/register_separation.csv`（`nearest_centroid_loo_acc`、`logistic_cv_acc`、`status`） |
| **图 5 溯源** | 3 候选：`results/e7/e7_metrics.csv`；7 候选：`results/e7_p2/e7_metrics.csv`；探针预算：`results/e7/e7_probe_curve.csv`；采样 readout：`results/e7/e7_sampled.csv` | **必须过滤** `table == "main"`、`readout == "probability"`、`subset == "all"`、`tau_policy == "calibrated"`、`detector == "base_unknown"`（修订 1 后的主检测器；`base_known` 为失败的变体）；列 `grid`、`version`、`teacher`、`recall`、`wilson_lo`、`wilson_hi`、`fpr`、`auroc`；探针曲线列 `budget`、`recall_mean`、`recall_lo`、`recall_hi`、`fpr_mean`（`tau_policy == "calibrated"`）；采样列 `n_draws` | 负例行 `teacher == "none"`，其 `fpr` 为该组误报率；`grid` 的 E3c 有 O / F / C 三个 version |
| 表 5 缺席实验 + 词汇 vs 行为 | 缺席：`results/e7_p2_drop_{gpt4o,claude46,deepseek_v4}/e7_absent.csv`（`view ∈ {candidate, family}`、`target`、`share`、`ci_lo`、`ci_hi`；`grid == "all_core"` 为合并行）；家族层面探索：`results/e7_p2_family/family_level_attribution.csv`；词汇 vs 行为：`results/e7_lexical_students/students_vs_behavioural.csv`（`majority_ngram`、`share_own_ngram`、`decision_unknown`、`margin_unknown`、`lexical_correct_ngram`、`behavioural_correct_unknown`） | 过滤 `detector == "base_unknown"` | 家族层面规则是事后探索，标注 |

## 2. 附录图表

| 图 / 表 | 文件 | 说明 |
|---|---|---|
| 训练曲线 | `runs/*/*/train_log.jsonl`（每 10 步：`step`、`loss`、`lr`、`epoch`、`elapsed_s`）；`train_manifest.json`（`steps`、`wall_time_sec`、`peak_memory_gib`、`n_examples`、`final_loss`） | 214 + 36 个 run；E2c-C vs E1 的 claude46 曲线对比支撑修订 1 |
| 改写保留率与失败原因 | `data/rewrites_train/{t}/rewrites.jsonl`、`data/rewrites_e2c/{t}/rewrites.jsonl`（`version`、`attempt`、`kept`、`checks`）；`results/e3/content_check.csv`、`results/e3c/content_check.csv` | 原集 vs 争议集 |
| 词汇 baseline（训练文本） | `results/e7_lexical/lexical_accuracy.csv`（`set`、`evaluation`、`features`、`teacher`、`acc`、`ci_lo`、`ci_hi`）、`lexical_features.csv`、`lexical_cue_survival.csv` | 用 family 不相交的行 |
| 争议池抽检与转换 | `results/e2c/handcheck_round{1,2,3,4}_report.md`、`results/e2c/pool_report.md` | 四轮通过率 |
| E7 基座迁移与 7 候选细节 | `results/e7_base2_qwentau/`、`results/e7_p2/e7_runs.csv`（每 run 对每候选的 `a__*`、`s_unknown__*`、`decision_unknown`、`margin_unknown`） | 可画每 run 的前两名分数 |
| 全部修订与披露 | `tasks/e2_plan.md` §2、`tasks/e2c_plan.md` §12、`tasks/e3c_plan.md` §7、`tasks/e7_plan.md` §7 | 表格化即可 |

## 3. 不要做的

- 不要用 `*_dev` 或 `-3ep` / `-5ep` 的数字当确认性结果。
- `e7_metrics.csv` 不过滤 `table / readout / subset / tau_policy / detector` 会混入敏感性行。
- 不要把 `base_known` 当主检测器；不要把 K_n、Cnf、家族层面规则写成预注册主结果。
- 画图用数据的 teacher 顺序固定为 gpt4o / claude46 / deepseek_v4，三家配色全文一致。
