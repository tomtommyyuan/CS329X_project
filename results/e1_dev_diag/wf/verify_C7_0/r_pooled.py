"""EXPLORATORY (dev): permutation p for seed-pooled R profile vs teachers; source of cross-seed R structure."""
import numpy as np, pandas as pd
from scipy.stats import spearmanr
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
rng = np.random.default_rng(1)
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
R = [f"qwen3-4b.random_R_s{s}" for s in (1, 2, 3)]
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if r.teacher in R]
sym_t = M.sym_table(M.frame_table(trows, prompts)); sym_s = M.sym_table(M.frame_table(srows, prompts))
sh_t = P.framing_shifts(sym_t, V); sh_s = P.framing_shifts(sym_s, V)
pooled = sh_s.groupby(["family_id", "variant"])["r"].mean().reset_index().assign(teacher="Rp")
for t in TS:
    fam = M._complete_families(pd.concat([pooled, sh_t]), ["Rp", t], V)
    X = M._shift_matrix(pooled, "Rp", fam, V); T = M._shift_matrix(sh_t, t, fam, V)
    op = np.corrcoef(X.ravel(), T.ravel())[0, 1]; osp = spearmanr(X.ravel(), T.ravel())[0]
    # null: shuffle families AND independently permute variant columns within family (removes variant main effects too)
    n1, n2 = [], []
    for _ in range(5000):
        Xp = X[rng.permutation(len(fam))]
        n1.append(np.corrcoef(Xp.ravel(), T.ravel())[0, 1]); n2.append(spearmanr(Xp.ravel(), T.ravel())[0])
    n1, n2 = np.array(n1), np.array(n2)
    print(t, len(fam), f"pearson {op:.3f} p_perm {np.mean(np.abs(n1-n1.mean())>=abs(op-n1.mean())):.4f} null mean {n1.mean():.3f};",
          f"spearman {osp:.3f} p_perm {np.mean(np.abs(n2-n2.mean())>=abs(osp-n2.mean())):.4f} null mean {n2.mean():.3f}")
# R variant means vs teacher variant means (spearman inflation from variant main effects?)
print(sh_t.groupby(["teacher", "variant"])["r"].mean().unstack().round(4))
# cross-seed structure: within-family shift sign vs order (p_o1 vs p_o2 letter effects)
s = sym_s[sym_s.variant.isin(V)].copy(); s["d"] = s.p_o1 - s.p_o2
print("order gap p_o1-p_o2 mean by seed:", s.groupby("teacher")["d"].agg(["mean", "std"]).round(4).to_string())
