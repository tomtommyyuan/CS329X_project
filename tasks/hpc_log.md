# HPC 工作日志（HAIC 上的 Claude Code agent 维护）

每个阶段结束追加一段：日期、做了什么、关键数字（表）、异常、下一步。卡住写 `BLOCKED:` 行。Mac 侧只读不改这个文件，回复写在 `tasks/e1_plan.md` / `tasks/e2_plan.md` 的对应位置。

## 状态板

| 项 | 状态 | 备注 |
|---|---|---|
| 环境（README §0） | 未开始 | account / partition / QoS 待核实 |
| gate run（README §1） | 未开始 | 含 vLLM / transformers 一致性、peak_memory_gib ≤ 70、E0.7 |
| SFT 文件 O + R | 未开始 | 在 compute 分配里建 |
| E1 18 run | 未开始 | |
| dev 评估 + 分析 | 未开始 | 冻结点 |
| test 评估 + 分析 | 未开始 | 只跑一次 |
| F / C 改写（Mac 侧） | 进行中 2026-10-04 | 完成后 `data/rewrites_train/` 进仓库，再建 paired O / F / C |

## 日志
