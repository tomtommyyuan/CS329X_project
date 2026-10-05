"""EXPLORATORY (dev, not pre-registered). Claim C2 check: is the E1 failure a small-signal/noise issue?"""
import numpy as np, pandas as pd
from itertools import combinations
from vcd.analysis import e1_metrics as M
V = ["T1","T3","T5","T6"]; TS = ["gpt4o","claude46","deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs","dev","qwen3-4b") if M.is_run_id(r.teacher)]
base_rel = [r.model_copy(update={"category":"answer","teacher":"S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
srows = [r for r in srows if not r.teacher.endswith("base_B_s0")] + base_rel
sym = pd.concat([M.sym_table(M.frame_table(trows,prompts)), M.sym_table(M.frame_table(srows,prompts))])
sym = sym[sym.variant.isin(V)].dropna(subset=["p_sym"])
W = sym.pivot_table(index=["family_id","variant"], columns="teacher", values="p_sym")
runs = [c for c in W.columns if c not in TS and c!="S0_relaxed"]
def grp(w):
    if w in TS or w=="S0_relaxed": return w
    k=M.parse_run_id(w); return k.teacher
rng = np.random.default_rng(1)
B=5000
# 1) teacher-teacher agreement (ceiling of gap if student == own teacher)
print("== teacher-teacher majority agreement on dev cells (both defined)")
for a,b in combinations(TS,2):
    d=W[[a,b]].dropna(); d=d[(d[a]!=.5)&(d[b]!=.5)]
    print(a,b,len(d), round(((d[a]>.5)==(d[b]>.5)).mean(),3))
# 2) per-run and seed-pooled gap own - other (each other teacher), family bootstrap, cells common to all three teachers
common = W[TS].dropna().index
Wc = W.loc[common]
fam = Wc.index.get_level_values("family_id").to_numpy(); uf=np.unique(fam)
idx_by_f = {f: np.where(fam==f)[0] for f in uf}
boot_idx = [np.concatenate([idx_by_f[f] for f in rng.choice(uf,len(uf))]) for _ in range(B)]
T = {t:(Wc[t].to_numpy()>.5) for t in TS}
print("\n== gap = agree(own) - agree(other) on", len(Wc), "cells,", len(uf), "families; 95% family-bootstrap CI")
rows=[]
for t in TS:
    rr=[r for r in runs if grp(r)==t]
    S=np.stack([(Wc[r].to_numpy()>.5) for r in rr])  # seeds x cells
    for o in TS:
        if o==t: continue
        g_cell = (S==T[t]).mean(0) - (S==T[o]).mean(0)   # seed-pooled per-cell gap
        per_seed = [((S[i]==T[t]).mean()-(S[i]==T[o]).mean()) for i in range(len(rr))]
        bs = np.array([g_cell[ix].mean() for ix in boot_idx])
        contested = T[t]!=T[o]
        ceil = contested.mean()
        side_own = (S[:,contested]==T[t][contested]).mean()
        # student-own vs teacher ceiling fraction
        rows.append(dict(student=t, other=o, n_contested=int(contested.sum()), ceiling_gap=round(ceil,3),
            pooled_gap=round(g_cell.mean(),4), ci=(round(np.quantile(bs,.025),4), round(np.quantile(bs,.975),4)),
            frac_of_ceiling=round(g_cell.mean()/ceil,3), side_own_contested=round(side_own,3),
            per_seed=[round(x,3) for x in per_seed]))
print(pd.DataFrame(rows).to_string(index=False))
# 3) same with S0_relaxed and R as reference: side with each teacher on contested pairs
print("\n== reference: S0_relaxed and R side-taking on contested cells (same common cells where S0 defined)")
for ref in ["S0_relaxed"]+[r for r in runs if grp(r)=="random"]:
    s = Wc[ref]
    for a,b in combinations(TS,2):
        c=(T[a]!=T[b]) & s.notna().to_numpy()
        print(ref, a, "vs", b, int(c.sum()), "side_with_first", round(((s.to_numpy()[c]>.5)==T[a][c]).mean(),3))
# 4) contrast relative to base: for each pair (a,b), student_a side_with_a minus student_b side_with_a on the same contested cells (seed-pooled), family bootstrap
print("\n== differential side-taking: P(side a | S[a]) - P(side a | S[b]) on a-vs-b contested cells (cancels base prior)")
for a,b in combinations(TS,2):
    c = T[a]!=T[b]
    Sa=np.stack([(Wc[r].to_numpy()>.5) for r in runs if grp(r)==a]); Sb=np.stack([(Wc[r].to_numpy()>.5) for r in runs if grp(r)==b])
    pa=(Sa==T[a]).mean(0); pb=(Sb==T[a]).mean(0)
    diff=(pa-pb)
    obs=diff[c].mean()
    bs=np.array([diff[ix][c[ix]].mean() for ix in boot_idx])
    print(a,b,"n",int(c.sum()),"P(side a|S[a])",round(pa[c].mean(),3),"P(side a|S[b])",round(pb[c].mean(),3),"diff",round(obs,3),"CI",np.round(np.quantile(bs,[.025,.975]),3), "agree on contested (S[a] vs S[b] same letter)", round(((Sa.mean(0)>.5)==(Sb.mean(0)>.5))[c].mean(),3))
# 5) student-student agreement across teacher groups (do differently trained students differ at all?)
print("\n== seed-majority student-vs-student agreement, all common cells; and seed-vs-seed within group")
maj={t:(np.stack([(Wc[r].to_numpy()>.5) for r in runs if grp(r)==t]).mean(0)>.5) for t in TS}
for a,b in combinations(TS,2): print("S",a,"S",b, round((maj[a]==maj[b]).mean(),3))
for t in TS:
    rr=[r for r in runs if grp(r)==t]; S=np.stack([(Wc[r].to_numpy()>.5) for r in rr])
    print("within",t, round(np.mean([(S[i]==S[j]).mean() for i,j in combinations(range(len(rr)),2)]),3))
