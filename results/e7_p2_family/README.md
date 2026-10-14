# 探索性：家族层面的归属规则（2026-10-13，看过 7 候选的 test 结果之后设计，非预注册）

家族分数 = 该家族候选分数（基座未知 s_t）的最大值；margin = 最高家族 − 次高家族；τ 在 dev 负例上按 ≤ 5% 误报定；test 一次。输入是 results/e7_p2*/e7_runs.csv（预注册检测器已算好的分数），没有重新查询任何模型。表见 family_level_attribution.csv。
