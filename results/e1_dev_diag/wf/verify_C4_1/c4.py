"""EXPLORATORY (dev only, not pre-registered): stress tests of the suggestibility-inheritance claim C4."""
import json, numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1","T3","T5","T6"]; TS = ["gpt4o","claude46","deepseek_v4"]
rng = np.random.default_rng(0)
# ---- 1. training-label suggestibility (hard labels in SFT files)
trp = {}
for l in open("data/prompts/train_prompts_v2.jsonl"):
    d = json.loads(l); trp[d["prompt_id"]] = d
print("== 1. training-label suggestibility (SFT O files, focus-aligned hard labels)")
for t in TS:
    for s in [1]:
        rows = [json.loads(l) for l in open(f"data/sft/{t}_O_s{s}.jsonl")]
        df = pd.DataFrame([dict(fam=r["family_id"], var=r["variant"],
              x=float(trp[r["prompt_id"]]["letter_to_action"][r["letter"]] == trp[r["prompt_id"]]["focus_action"])) for r in rows])
        rate = df.groupby("var")["x"].mean()
        w = df.pivot_table(index="fam", columns="var", values="x")
        both = w.dropna(subset=["T5","T6"]); full = w.dropna()
        print(f"{t} s{s}: n={len(df)} rate T5-T6 (all items) = {rate['T5']-rate['T6']:.3f};"
              f" paired T5-T6 (fams with both, n={len(both)}) = {(both.T5-both.T6).mean():.3f};"
              f" complete fams n={len(full)}: {(full.T5-full.T6).mean():.3f}; share fams T5!=T6 {(both.T5!=both.T6).mean():.3f}")
# ---- dev data
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs","dev","qwen3-4b") if M.is_run_id(r.teacher)]
base = [r for r in srows if r.teacher.endswith("base_B_s0")]
stud = [r for r in srows if not r.teacher.endswith("base_B_s0")]
sym_t = M.sym_table(M.frame_table(trows, prompts)); sym_s = M.sym_table(M.frame_table(stud, prompts))
def grp(w):
    if w in TS: return w
    k = M.parse_run_id(w); return f"S[{k.teacher}]"
def wide(sym):
    s = sym[sym.variant.isin(["T5","T6"])].pivot_table(index=["teacher","family_id"], columns="variant", values="p_sym").dropna()
    return s.reset_index()
wt, ws = wide(sym_t), wide(sym_s)
ws["group"] = ws.teacher.map(grp)
famsets = [set(wt[wt.teacher==t].family_id) for t in TS] + [set(ws[ws.teacher==r].family_id) for r in ws.teacher.unique()]
common = sorted(set.intersection(*famsets)); print(f"\n== 2. dev, common families with T5&T6 for all 3 teachers + 18 students: n={len(common)}")
wt = wt[wt.family_id.isin(common)]; ws = ws[ws.family_id.isin(common)]
# seed-pool students per family
wsp = ws.groupby(["group","family_id"])[["T5","T6"]].mean().reset_index().rename(columns={"group":"teacher"})
allw = pd.concat([wt, wsp])
allw["d"] = allw.T5 - allw.T6
allw["dh"] = (allw.T5 > .5).astype(float) - (allw.T6 > .5).astype(float)
allw["sgn"] = np.sign(allw.T5 - allw.T6)
summ = allw.groupby("teacher").agg(sugg_soft=("d","mean"), sugg_hard=("dh","mean"), share_T5gtT6=("sgn", lambda x: (x>0).mean()), share_T5ltT6=("sgn", lambda x:(x<0).mean()), n=("d","size"))
print(summ.round(3).to_string())
# bootstrap over families for pairwise orderings
D = allw.pivot_table(index="family_id", columns="teacher", values="d"); DH = allw.pivot_table(index="family_id", columns="teacher", values="dh")
n = len(D); B = 10000; idx = rng.integers(0, n, (B, n))
def boot(col_a, col_b, X):
    a = X[col_a].to_numpy()[idx].mean(1) - X[col_b].to_numpy()[idx].mean(1)
    return f"{X[col_a].mean()-X[col_b].mean():+.3f} [{np.quantile(a,.025):+.3f},{np.quantile(a,.975):+.3f}] P(>0)={np.mean(a>0):.3f}"
print("\nfamily bootstrap of pairwise differences (soft | hard):")
for a,b in [("deepseek_v4","gpt4o"),("gpt4o","claude46"),("deepseek_v4","claude46")]:
    print(f" teacher {a}-{b}: {boot(a,b,D)} | {boot(a,b,DH)}")
    print(f" student S[{a}]-S[{b}]: {boot('S['+a+']','S['+b+']',D)} | {boot('S['+a+']','S['+b+']',DH)}")
    print(f" student-minus-teacher S[{a}]-{a}: {boot('S['+a+']',a,D)}")
# per-family correlation of student suggestibility with own vs other teachers
print("\nper-family correlation of d=p(T5)-p(T6), seed-pooled student vs teacher (common fams):")
print(D.corr().loc[["S[claude46]","S[deepseek_v4]","S[gpt4o]","S[random]" if "S[random]" in D else "S[random]"], TS].round(3).to_string() if "S[random]" in D else D.corr().loc[[c for c in D if c.startswith("S[")], TS].round(3).to_string())
# ---- 3. base S0 under different mass thresholds
print("\n== 3. base S0 suggestibility vs letter-mass threshold (raw p_x = normalized letter prob)")
for thr in [0.0, 0.3, 0.5, 0.7, 0.9]:
    keep = [r.model_copy(update={"category":"answer"}) for r in base if r.p_letters and (r.usage or {}).get("mass_AB", 0) >= thr]
    sb = M.sym_table(M.frame_table(keep, prompts)); w = wide(sb)
    wc = w[w.family_id.isin(common)]
    print(f" thr {thr}: rows {len(keep)}, fams T5&T6 {len(w)}: sugg {(w.T5-w.T6).mean():.3f}; on common fams n={len(wc)}: {(wc.T5-wc.T6).mean():.3f}")
mass = pd.DataFrame([dict(var=prompts[r.prompt_id].variant, m=(r.usage or {}).get("mass_AB")) for r in base if r.prompt_id in prompts])
print(" S0 mean letter mass by variant:", mass.groupby("var")["m"].mean().round(3).to_dict())
