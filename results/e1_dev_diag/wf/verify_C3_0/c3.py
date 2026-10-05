"""EXPLORATORY (dev only, not pre-registered): stress-test claim C3 (base prior explains DeepSeek-nearest)."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r.model_copy(update={"category": "answer", "teacher": "S0"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
studs = [r for r in srows if not r.teacher.endswith("base_B_s0")]
sym_t = M.sym_table(M.frame_table(trows, prompts)); sym_s = M.sym_table(M.frame_table(studs + base, prompts))
sh_t, sh_s = P.framing_shifts(sym_t, V), P.framing_shifts(sym_s, V)
def grp(w):
    if w == "S0": return w
    k = M.parse_run_id(w); return f"S_{k.teacher}"
sh_s["g"] = sh_s.teacher.map(grp)
pooled = sh_s.groupby(["g", "family_id", "variant"])["r"].mean().reset_index().rename(columns={"g": "teacher"})
allsh = pd.concat([sh_t[["teacher","family_id","variant","r"]], pooled])
W = allsh.pivot_table(index=["family_id","variant"], columns="teacher", values="r")
names = TS + ["S0", "S_gpt4o", "S_claude46", "S_deepseek_v4", "S_random"]
fam_ok = W[names].dropna().reset_index().groupby("family_id").size().pipe(lambda s: s[s==4].index)
W = W.loc[W.index.get_level_values(0).isin(fam_ok), names].dropna()
fams = np.array(sorted(fam_ok)); print("common families", len(fams), "cells", len(W))
def corrmat(X): return X.corr()
print("\n[1] Pearson profile corr, raw r (common families)"); print(corrmat(W).round(3).to_string())
# variant-residualized: remove each model's per-variant mean (type main effect)
R = W - W.groupby(level="variant").transform("mean")
print("\n[2] Pearson, variant-main-effect removed"); print(corrmat(R).round(3).to_string())
# variance share of type main effect
for c in names:
    tot = (W[c]**2).sum(); me = (W.groupby(level="variant")[c].transform("mean")**2).sum()
    print(f"  type-main-effect share of r variance  {c:15s} {me/tot:.3f}  sd(r)={W[c].std():.3f}")
# bootstrap
rng = np.random.default_rng(0); B = 5000
fi = {f: W.index.get_locs([f]) for f in fams}
def boot(X, fn):
    out = []
    for _ in range(B):
        idx = np.concatenate([fi[f] for f in rng.choice(fams, len(fams))])
        out.append(fn(X.iloc[idx]))
    return np.array(out)
def c(X,a,b): return np.corrcoef(X[a], X[b])[0,1]
for lab, X in [("raw", W), ("resid", R)]:
    for o in ["gpt4o", "claude46"]:
        d = c(X,"S0","deepseek_v4") - c(X,"S0",o); bs = boot(X, lambda Y: c(Y,"S0","deepseek_v4") - c(Y,"S0",o))
        print(f"[3 {lab}] rho(S0,DS)-rho(S0,{o}) = {d:.3f}  95% CI [{np.quantile(bs,.025):.3f},{np.quantile(bs,.975):.3f}]")
# partial correlations controlling S0
def partial(X, a, b, z):
    ra = X[a] - np.polyval(np.polyfit(X[z], X[a], 1), X[z]); rb = X[b] - np.polyval(np.polyfit(X[z], X[b], 1), X[z])
    return np.corrcoef(ra, rb)[0,1]
for lab, X in [("raw", W), ("resid", R)]:
    print(f"\n[4 {lab}] partial corr(student, teacher | S0)  and delta (own - max other)")
    for s in ["S_gpt4o", "S_claude46", "S_deepseek_v4"]:
        own = s[2:]; pr = {t: partial(X, s, t, "S0") for t in TS}; rr = {t: c(X, s, t) for t in TS}
        oth = max((v,t) for t,v in pr.items() if t != own); othr = max((v,t) for t,v in rr.items() if t != own)
        print(f"  {s:15s} raw " + " ".join(f"{t}={rr[t]:.3f}" for t in TS) + f" d={rr[own]-othr[0]:+.3f}({othr[1]}) | partial " + " ".join(f"{t}={pr[t]:.3f}" for t in TS) + f" d={pr[own]-oth[0]:+.3f}({oth[1]})")
# also partial out DS's similarity to S0 via teacher residualized on S0 only
# multiple regression student ~ S0 + 3 teachers (standardized)
print("\n[5] OLS standardized betas: student_pooled ~ S0 + gpt4o + claude46 + deepseek_v4 (raw r)")
Z = (W - W.mean())/W.std()
for s in ["S_gpt4o", "S_claude46", "S_deepseek_v4"]:
    X = np.column_stack([np.ones(len(Z))] + [Z[k] for k in ["S0"]+TS]); b,*_ = np.linalg.lstsq(X, Z[s], rcond=None)
    X2 = np.column_stack([np.ones(len(Z))] + [Z[k] for k in TS]); b2,*_ = np.linalg.lstsq(X2, Z[s], rcond=None)
    print(f"  {s:15s} with S0: S0={b[1]:.3f} gpt={b[2]:.3f} cl={b[3]:.3f} ds={b[4]:.3f} | without S0: gpt={b2[1]:.3f} cl={b2[2]:.3f} ds={b2[3]:.3f}")
# hub test: teacher-teacher
print("\n[6] teacher hubness: corr with mean of other two teachers (raw / resid)")
for t in TS:
    o=[x for x in TS if x!=t]; print(f"  {t}: raw {np.corrcoef(W[t], W[o].mean(1))[0,1]:.3f}  resid {np.corrcoef(R[t], R[o].mean(1))[0,1]:.3f}")
# graded-ness: share of teacher cells with p_sym in (0.1,0.9) on these families
st = sym_t[sym_t.variant.isin(V) & sym_t.family_id.isin(fams)]
print("\n[7] share teacher p_sym in [0.1,0.9]:", st.groupby("teacher")["p_sym"].apply(lambda x: ((x>=.1)&(x<=.9)).mean()).round(3).to_dict())
# share of r-variance from families with |r|>0.25 (big flips)
for t in names: print(f"  {t:15s} share of sum r^2 from cells |r|>0.25: {(W[t]**2)[W[t].abs()>.25].sum()/(W[t]**2).sum():.3f}; nonzero cells(|r|>.02) {(W[t].abs()>.02).mean():.3f}")
# per-seed: does subtracting S0 flip nearest teacher?
print("\n[8] per-seed partial (raw) delta own-max other | S0")
runs = sorted(sh_s[sh_s.g.str.startswith("S_")].teacher.unique())
for run in runs:
    if "random" in run: continue
    own = M.parse_run_id(run).teacher
    x = sh_s[sh_s.teacher==run].set_index(["family_id","variant"])["r"].reindex(W.index)
    X = W.assign(s=x).dropna()
    pr = {t: partial(X, "s", t, "S0") for t in TS}; rr = {t: c(X,"s",t) for t in TS}
    print(f"  {run:28s} raw d={rr[own]-max(v for t,v in rr.items() if t!=own):+.3f} nearest={max(rr,key=rr.get)} | partial d={pr[own]-max(v for t,v in pr.items() if t!=own):+.3f} nearest={max(pr,key=pr.get)}")
