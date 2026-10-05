"""Dev diagnostics for E1 (not decision rules): calibration of teachers / students, and seed-pooled side-taking on
contested cells (two teachers' majority acts differ) with a family-bootstrap 95% CI."""
import sys
from itertools import combinations
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
split = sys.argv[1] if len(sys.argv) > 1 else "dev"
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts(f"data/prompts/{split}_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_{split}_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", split, "qwen3-4b") if M.is_run_id(r.teacher)]
sym = pd.concat([M.sym_table(M.frame_table(trows, prompts)), M.sym_table(M.frame_table(srows, prompts))])
sym = sym[sym.variant.isin(V)].dropna(subset=["p_sym"])
def grp(w):
    if w in TS: return w
    k = M.parse_run_id(w); return f"S[{k.teacher}_{k.version}]"
sym["group"] = sym["teacher"].map(grp)
cal = sym.assign(conf=(sym.p_sym - .5).abs(), extreme=((sym.p_sym < .1) | (sym.p_sym > .9))).groupby("group")[["conf", "extreme"]].mean()
cal["n_cells"] = sym.groupby("group").size()
print("calibration: mean |p_sym - 0.5| and share of cells with p_sym outside [0.1, 0.9] (students: mean over seeds' cells)")
print(cal.round(3).to_string())
W = sym.pivot_table(index=["family_id", "variant"], columns="teacher", values="p_sym")
rng = np.random.default_rng(0)
rows = []
for g in sorted({grp(c) for c in W.columns if c not in TS}):
    runs = [c for c in W.columns if c not in TS and grp(c) == g]
    for a, b in combinations(TS, 2):
        d = W[[a, b] + runs].dropna()
        c = d[(d[a] > .5) != (d[b] > .5)]
        if not len(c): continue
        side = ((c[runs].to_numpy() > .5) == (c[[a]].to_numpy() > .5)).mean(axis=1)   # per cell, share of seeds siding with a
        fam = c.index.get_level_values("family_id").to_numpy(); uf = np.unique(fam)
        per_f = {f: side[fam == f] for f in uf}
        boots = [np.concatenate([per_f[f] for f in rng.choice(uf, len(uf))]).mean() for _ in range(2000)]
        rows.append(dict(students=g, n_seeds=len(runs), pair=f"{a} vs {b}", n_cells=len(c), n_families=len(uf), side_with_first=side.mean(), ci_lo=np.quantile(boots, .025), ci_hi=np.quantile(boots, .975)))
print("\nseed-pooled share of contested cells where the students side with the FIRST teacher of the pair (95% family-bootstrap CI)")
print(pd.DataFrame(rows).round(3).to_string(index=False))
