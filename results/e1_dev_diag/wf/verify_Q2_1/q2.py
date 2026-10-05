"""Exploratory (dev, not pre-registered): recompute S0_relaxed vs teacher profile correlation on various family sets."""
import numpy as np, pandas as pd, itertools
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1","T3","T5","T6"]; TS = ["gpt4o","claude46","deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs","dev","qwen3-4b") if M.is_run_id(r.teacher)]
base = [r for r in srows if r.teacher.endswith("base_B_s0")]
print("base rows", len(base), "with p_letters", sum(1 for r in base if r.p_letters))
base_relaxed = [r.model_copy(update={"category":"answer","teacher":"S0_relaxed"}) for r in base if r.p_letters]
studs = [r for r in srows if not r.teacher.endswith("base_B_s0")]
sym_t = M.sym_table(M.frame_table(trows, prompts))
sym_s = M.sym_table(M.frame_table(studs + base_relaxed, prompts))
sh_t, sh_s = P.framing_shifts(sym_t, V), P.framing_shifts(sym_s, V)
sh = pd.concat([sh_t, sh_s])
def complete(w):
    g = sh[(sh.teacher==w)&sh.variant.isin(V)]
    c = g.groupby("family_id")["variant"].nunique(); return set(c[c==4].index)
runs = sorted(sh_s.teacher.unique())
fam = {w: complete(w) for w in TS + runs}
for w in TS + ["S0_relaxed"]: print(w, len(fam[w]))
trained = [r for r in runs if r != "S0_relaxed"]
print("trained runs", len(trained), "min fam", min(len(fam[r]) for r in trained))
sets = {
 "S0&ds": fam["S0_relaxed"] & fam["deepseek_v4"],
 "S0&allT": fam["S0_relaxed"] & set.intersection(*[fam[t] for t in TS]),
 "allT": set.intersection(*[fam[t] for t in TS]),
 "allT&all15": set.intersection(*[fam[t] for t in TS], *[fam[r] for r in trained if "random" not in r]),
 "allT&all18": set.intersection(*[fam[t] for t in TS], *[fam[r] for r in trained]),
 "allT&all18&S0": set.intersection(*[fam[t] for t in TS], *[fam[r] for r in trained], fam["S0_relaxed"]),
 "allT&all15&S0": set.intersection(*[fam[t] for t in TS], *[fam[r] for r in trained if "random" not in r], fam["S0_relaxed"]),
}
def mat(w, F):
    return sh[(sh.teacher==w)].pivot_table(index="family_id", columns="variant", values="r").reindex(index=sorted(F), columns=V).to_numpy().ravel()
for name, F in sets.items():
    s0 = mat("S0_relaxed", F)
    out = {t: np.corrcoef(s0, mat(t, F))[0,1] for t in TS}
    # partial correlation of S0 with ds controlling for other two teachers
    if name=="S0&ds": print(name,len(F),round(np.corrcoef(s0,mat("deepseek_v4",F))[0,1],4)); continue
    X = np.column_stack([mat("gpt4o",F), mat("claude46",F), np.ones(len(s0))])
    rs = s0 - X@np.linalg.lstsq(X,s0,rcond=None)[0]; d = mat("deepseek_v4",F); rd = d - X@np.linalg.lstsq(X,d,rcond=None)[0]
    print(name, len(F), {k: round(v,4) for k,v in out.items()}, "partial(ds|g,c)=", round(np.corrcoef(rs,rd)[0,1],4))

print("\n--- robustness (exploratory) on 139 families ---")
F = sorted(sets["allT"]); rng = np.random.default_rng(0)
M_ = {w: sh[sh.teacher==w].pivot_table(index="family_id", columns="variant", values="r").reindex(index=F, columns=V).to_numpy() for w in TS+["S0_relaxed"]}
bs = []
for _ in range(5000):
    i = rng.integers(0, len(F), len(F)); a = M_["S0_relaxed"][i].ravel(); b = M_["deepseek_v4"][i].ravel(); bs.append(np.corrcoef(a,b)[0,1])
print("family bootstrap 95% CI S0-ds:", np.round(np.percentile(bs,[2.5,97.5]),3))
dc = {w: M_[w] - M_[w].mean(0, keepdims=True) for w in M_}
print("variant-mean-removed (double-centred) Pearson:", {t: round(np.corrcoef(dc["S0_relaxed"].ravel(), dc[t].ravel())[0,1],3) for t in TS})
for j,v in enumerate(V):
    print(v, {t: round(np.corrcoef(M_["S0_relaxed"][:,j], M_[t][:,j])[0,1],3) for t in TS})
# T5-T6 per family vs rest
sugg = {w: M_[w][:,2]-M_[w][:,3] for w in M_}
print("per-family T5-T6 corr:", {t: round(np.corrcoef(sugg["S0_relaxed"], sugg[t])[0,1],3) for t in TS})
# letter mass of base on these families
pm = pd.DataFrame([dict(fid=prompts[r.prompt_id].family_id, mass=sum(r.p_letters.values()) if isinstance(r.p_letters, dict) else np.nan) for r in base])
print("base letter mass median", pm.mass.median(), "share>=0.9", (pm.mass>=0.9).mean(), "share>=0.5", (pm.mass>=0.5).mean())
