"""EXPLORATORY (dev only, not pre-registered): reliability ceiling for rho, residualized and S0-partialled delta_rho."""
import numpy as np, pandas as pd, itertools
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
from vcd.stats import spearman_brown
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
assert "test" not in "data/prompts/dev_prompts_v2.jsonl"
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base_relaxed = [r.model_copy(update={"category": "answer", "teacher": "S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
ft = M.frame_table(trows, prompts)
sym_t = M.sym_table(ft)
sym_s = M.sym_table(M.frame_table([r for r in srows if not r.teacher.endswith("base_B_s0")] + base_relaxed, prompts))
print("== teacher reliability by order (dev, T1/T3/T5/T6)")
print(P.reliability_by_order(sym_t, V).round(3).to_string(index=False))
try:
    cells = P.cell_estimates(P.align_to_focus(P.responses_to_frame(trows, prompts), M.focus_map(prompts)))
    if "pass_idx" in cells: print(P.reliability_by_pass(cells, V).round(3).to_string(index=False))
except Exception as e: print("pass reliability skipped:", e)
rel_t = P.reliability_by_order(sym_t, V).set_index("teacher")["reliability"]

# student reliabilities
grp = {}
for w in sym_s.teacher.unique():
    if w == "S0_relaxed": continue
    k = M.parse_run_id(w); grp.setdefault(k.teacher, []).append(w)
ro = P.reliability_by_order(sym_s, V).set_index("teacher")
print("\n== student order split-half reliability per run"); print(ro.round(3).to_string())
sh_s = P.framing_shifts(sym_s, V); sh_t = P.framing_shifts(sym_t, V)
def vec(sh, who): return sh[sh.teacher == who].set_index(["family_id", "variant"])["r"]
rows = []
for g, runs in sorted(grp.items()):
    vs = [vec(sh_s, r) for r in runs]
    idx = vs[0].index
    for v in vs[1:]: idx = idx.intersection(v.index)
    cs = [np.corrcoef(a.loc[idx], b.loc[idx])[0, 1] for a, b in itertools.combinations(vs, 2)]
    rbar = float(np.mean(cs)); k = len(runs)
    # pooled order split-half: average p_o1 over seeds and p_o2 over seeds
    s = sym_s[sym_s.teacher.isin(runs)].groupby(["family_id", "variant"])[["p_o1", "p_o2"]].mean().reset_index().assign(teacher=g)
    pr = P.reliability_by_order(s, V)
    rows.append(dict(group=g, k=k, between_seed_r=rbar, seed_pooled_SB=k * rbar / (1 + (k - 1) * rbar),
                     pooled_order_split_half_rel=float(pr.reliability.iloc[0])))
srel = pd.DataFrame(rows).set_index("group"); print("\n== student reliability"); print(srel.round(3).to_string())

# pooled rho, disattenuated
pooled = sh_s[sh_s.teacher != "S0_relaxed"].assign(g=lambda x: x.teacher.map(lambda w: M.parse_run_id(w).teacher)) \
    .groupby(["g", "family_id", "variant"])["r"].mean().reset_index().rename(columns={"g": "teacher"})
# common complete families across the 3 pooled students and 3 teachers
fams = set.intersection(*[set(pooled[pooled.teacher == g].family_id) for g in TS], *[set(sh_t[sh_t.teacher == t].family_id) for t in TS])
fams = sorted(fams); print("\ncommon families", len(fams))
def mat(sh, who): return sh[(sh.teacher == who) & sh.family_id.isin(fams)].set_index(["family_id", "variant"])["r"].sort_index()
out = []
for g in TS:
    s = mat(pooled, g)
    for t in TS:
        tt = mat(sh_t, t); rho = np.corrcoef(s, tt.loc[s.index])[0, 1]
        out.append(dict(student=g, teacher=t, rho=rho, rel_T=rel_t[t], rel_S_order=srel.loc[g, "pooled_order_split_half_rel"], rel_S_seed=srel.loc[g, "seed_pooled_SB"],
                        rho_over_relT=rho / rel_t[t], rho_over_sqrt_relT=rho / np.sqrt(rel_t[t]),
                        rho_disatt_seed=rho / np.sqrt(rel_t[t] * srel.loc[g, "seed_pooled_SB"]),
                        ceiling_seed=np.sqrt(rel_t[t] * srel.loc[g, "seed_pooled_SB"])))
o = pd.DataFrame(out); print("\n== pooled rho, reliability ratios"); print(o.round(3).to_string(index=False))

# residualized (each model's own delta(j) removed) and S0-partialled
def resid(sh): return P.residual_shifts(sh)
pr_res, t_res = resid(pooled[pooled.family_id.isin(fams)]), resid(sh_t[sh_t.family_id.isin(fams)])
s0 = sh_s[sh_s.teacher == "S0_relaxed"]; fams0 = sorted(set(fams) & set(s0.family_id)); print("families with S0_relaxed complete:", len(fams0))
def partial(x, y, z):
    rxy, rxz, ryz = np.corrcoef(x, y)[0, 1], np.corrcoef(x, z)[0, 1], np.corrcoef(y, z)[0, 1]
    return (rxy - rxz * ryz) / np.sqrt((1 - rxz**2) * (1 - ryz**2))
rng = np.random.default_rng(0)
def table(kind, nb=2000):
    res = []
    F = fams0 if kind == "partial_S0" else fams
    def get(sh, who, fs): return sh[(sh.teacher == who) & sh.family_id.isin(fs)].set_index(["family_id", "variant"])["r"].sort_index()
    P_, T_ = (pr_res, t_res) if kind == "residual" else (pooled, sh_t)
    S0 = get(s0, "S0_relaxed", F) if kind == "partial_S0" else None
    def rhos(fs_list):
        idx = pd.MultiIndex.from_tuples([(f, v) for f in fs_list for v in V])
        d = {}
        for g in TS:
            s = get(P_, g, F).reindex(idx).to_numpy()
            for t in TS:
                tt = get(T_, t, F).reindex(idx).to_numpy()
                d[(g, t)] = partial(s, tt, S0.reindex(idx).to_numpy()) if kind == "partial_S0" else np.corrcoef(s, tt)[0, 1]
        return d
    d0 = rhos(F)
    boots = [rhos(list(rng.choice(F, len(F), replace=True))) for _ in range(nb)]
    for g in TS:
        others = [t for t in TS if t != g]
        dr = d0[(g, g)] - max(d0[(g, t)] for t in others)
        bd = np.array([b[(g, g)] - max(b[(g, t)] for t in others) for b in boots])
        res.append(dict(kind=kind, student=g, n_fam=len(F), **{f"rho_{t}": d0[(g, t)] for t in TS}, delta_rho=dr, ci_lo=np.quantile(bd, .025), ci_hi=np.quantile(bd, .975)))
    return pd.DataFrame(res)
print("\n== EXPLORATORY delta_rho variants (seed-pooled students, family bootstrap 2000)")
print(pd.concat([table("raw"), table("residual"), table("partial_S0")]).round(3).to_string(index=False))
