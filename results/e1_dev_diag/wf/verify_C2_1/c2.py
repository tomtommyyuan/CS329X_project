"""EXPLORATORY (dev only, not pre-registered): is the E1 dev failure a small-signal/noise issue or a
failure of students to generalize teacher-specific choices to unseen contested cells?"""
from itertools import combinations
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base_relaxed = [r.model_copy(update={"category": "answer", "teacher": "S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
studs = [r for r in srows if not r.teacher.endswith("base_B_s0")]
sym = pd.concat([M.sym_table(M.frame_table(trows, prompts)), M.sym_table(M.frame_table(studs + base_relaxed, prompts))])
sym = sym[sym.variant.isin(V)].dropna(subset=["p_sym"])
W = sym.pivot_table(index=["family_id", "variant"], columns="teacher", values="p_sym")
runs = [c for c in W.columns if c not in TS and c != "S0_relaxed"]
def tof(c): return M.parse_run_id(c).teacher
rng = np.random.default_rng(0)
def fboot(vals, fam, B=2000):
    uf = np.unique(fam); per = {f: vals[fam == f] for f in uf}
    b = [np.concatenate([per[f] for f in rng.choice(uf, len(uf))]).mean() for _ in range(B)]
    return np.quantile(b, [.025, .975])

print("== 1. Decomposition: agree_own - agree_other == (#contested siding own - #siding other)/N  (per O run)")
rows = []
for r in runs:
    t = tof(r)
    if t not in TS: continue
    for o in TS:
        if o == t: continue
        d = W[[r, t, o]].dropna(); d = d[(d[r] != .5) & (d[t] != .5) & (d[o] != .5)]
        N = len(d); s, a, b = d[r] > .5, d[t] > .5, d[o] > .5
        diff = (s == a).mean() - (s == b).mean()
        c = a != b; nc = int(c.sum()); q = (s[c] == a[c]).mean()
        rows.append(dict(run=r.split(".")[1], other=o, N=N, n_contested=nc, diff=diff, recon=nc * (2 * q - 1) / N, q_side_own=q,
                         diff_if_q09=nc * 0.8 / N, q_needed_for_diff_0p016=0.5 + 0.016 * N / nc / 2))
D = pd.DataFrame(rows); print(D.round(3).to_string(index=False))

print("\n== 2. Differential side-taking on (a,b)-contested cells: share siding with a, by student group; Diff = S[a]-S[b] (family bootstrap CI)")
grpruns = {g: [r for r in runs if tof(r) == g] for g in TS + ["random"]}
out = []
for a, b in combinations(TS, 2):
    d = W[[a, b] + runs + ["S0_relaxed"]].dropna(subset=[a, b] + runs)
    for label, mask in [("all", np.ones(len(d), bool)),
                        ("both_confident(|p-.5|>=.4)", ((d[a] - .5).abs() >= .4) & ((d[b] - .5).abs() >= .4)),
                        ("soft(either |p-.5|<.4)", ~(((d[a] - .5).abs() >= .4) & ((d[b] - .5).abs() >= .4)))]:
        c = d[mask & ((d[a] > .5) != (d[b] > .5))]
        if len(c) < 5: continue
        fam = c.index.get_level_values("family_id").to_numpy()
        sa = {g: ((c[grpruns[g]].to_numpy() > .5) == (c[[a]].to_numpy() > .5)).mean(1) for g in grpruns}
        diff = sa[a] - sa[b]; lo, hi = fboot(diff, fam)
        s0 = c["S0_relaxed"].dropna(); s0side = ((s0 > .5) == (c.loc[s0.index, a] > .5)).mean()
        out.append(dict(pair=f"{a} vs {b}", subset=label, n=len(c), nfam=len(np.unique(fam)),
                        **{f"S[{g}]": sa[g].mean() for g in grpruns}, S0rel=s0side, diff_own=diff.mean(), lo=lo, hi=hi))
print(pd.DataFrame(out).round(3).to_string(index=False))

print("\n== 3. Base-prior pull: on contested cells, share of student choices agreeing with S0_relaxed's side, vs with own teacher")
out = []
for g in TS:
    rs = grpruns[g]
    for o in TS:
        if o == g: continue
        d = W[[g, o, "S0_relaxed"] + rs].dropna()
        c = d[(d[g] > .5) != (d[o] > .5)]
        S = c[rs].to_numpy() > .5
        own = (S == (c[[g]].to_numpy() > .5)).mean(); base = (S == (c[["S0_relaxed"]].to_numpy() > .5)).mean()
        # cells where base sides with own vs with other
        bo = (c["S0_relaxed"] > .5) == (c[g] > .5)
        own_bo = (S[bo.to_numpy()] == (c[bo][[g]].to_numpy() > .5)).mean() if bo.any() else np.nan
        own_bx = (S[~bo.to_numpy()] == (c[~bo][[g]].to_numpy() > .5)).mean() if (~bo).any() else np.nan
        out.append(dict(students=g, other=o, n=len(c), side_own=own, side_S0=base, n_base_with_own=int(bo.sum()), side_own_when_base_agrees=own_bo, side_own_when_base_opposes=own_bx))
print(pd.DataFrame(out).round(3).to_string(index=False))
