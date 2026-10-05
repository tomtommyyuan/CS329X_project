"""EXPLORATORY (dev, not pre-registered): verify claim C4 on suggestibility delta(T5)-delta(T6)."""
import json, numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
rng = np.random.default_rng(0); NB = 10000
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base = [r for r in srows if r.teacher.endswith("base_B_s0")]
def relaxed(minmass, name):
    return [r.model_copy(update={"category": "answer", "teacher": name}) for r in base if r.p_letters and (r.usage or {}).get("mass_AB", 0) >= minmass]
stud = [r for r in srows if not r.teacher.endswith("base_B_s0")]
extra = relaxed(0.0, "S0_relaxed") + relaxed(0.5, "S0_mass50") + relaxed(0.9, "S0_mass90")
print("S0 mass_AB quantiles:", np.quantile([(r.usage or {}).get("mass_AB", np.nan) for r in base], [.1,.25,.5,.75,.9]).round(3))
sym = pd.concat([M.sym_table(M.frame_table(trows, prompts)), M.sym_table(M.frame_table(stud + extra, prompts))])
sym = sym[sym.variant.isin(["T5", "T6"])].pivot_table(index=["teacher", "family_id"], columns="variant", values="p_sym").dropna().reset_index()
sym["d"] = sym["T5"] - sym["T6"]   # = delta(T5)-delta(T6) per family (demeaning cancels)
def grp(w):
    if w in TS or w.startswith("S0"): return w
    k = M.parse_run_id(w); return f"S[{k.teacher}]"
sym["group"] = sym.teacher.map(grp)
# seed-pooled per-family d for student groups
fam = sym.groupby(["group", "family_id"])["d"].mean().unstack(0)
print("\nn families with T5&T6 per group:\n", fam.notna().sum().to_string())
groups = ["claude46", "gpt4o", "deepseek_v4", "S[claude46]", "S[gpt4o]", "S[deepseek_v4]", "S[random]", "S0_relaxed", "S0_mass50", "S0_mass90"]
groups = [g for g in groups if g in fam]
print("\nmean d over each group's own families (T5/T6 both present; note: original diag requires all 4 variants):")
print(fam[groups].mean().round(3).to_string())
core = ["claude46", "gpt4o", "deepseek_v4", "S[claude46]", "S[gpt4o]", "S[deepseek_v4]", "S0_relaxed"]
common = fam[core].dropna()
print(f"\ncommon family set (teachers, pooled students, S0_relaxed): n={len(common)}")
X = common.values; n = len(X)
idx = rng.integers(0, n, (NB, n))
B = X[idx].mean(1)  # NB x groups
obs = X.mean(0)
def ci(v): return np.quantile(v, [.025, .975]).round(3)
for j, g in enumerate(core): print(f"  {g:16s} {obs[j]:.3f}  95%CI {ci(B[:, j])}")
c = {g: j for j, g in enumerate(core)}
pairs = [("gpt4o", "claude46"), ("deepseek_v4", "gpt4o"), ("deepseek_v4", "claude46"),
         ("S[gpt4o]", "S[claude46]"), ("S[deepseek_v4]", "S[gpt4o]"), ("S[deepseek_v4]", "S[claude46]"),
         ("S[claude46]", "claude46"), ("S[gpt4o]", "gpt4o"), ("S[deepseek_v4]", "deepseek_v4"),
         ("S0_relaxed", "S[claude46]"), ("S0_relaxed", "S[deepseek_v4]")]
print("\npairwise differences (family bootstrap, paired):")
for a, b in pairs:
    dv = B[:, c[a]] - B[:, c[b]]
    print(f"  {a:16s} - {b:14s} {obs[c[a]]-obs[c[b]]:+.3f}  CI {ci(dv)}  P(boot<=0)={np.mean(dv<=0):.4f}")
# ordering preserved in bootstrap
tord = np.argsort(-B[:, [c["deepseek_v4"], c["gpt4o"], c["claude46"]]], 1)
sord = np.argsort(-B[:, [c["S[deepseek_v4]"], c["S[gpt4o]"], c["S[claude46]"]]], 1)
print("\nbootstrap P(teacher order D>G>C):", np.mean((tord == [0,1,2]).all(1)).round(3),
      " P(student order D>G>C):", np.mean((sord == [0,1,2]).all(1)).round(3),
      " P(student order == teacher order in same resample):", np.mean((tord == sord).all(1)).round(3))
# family-level inheritance: correlate per-family student d with each teacher d
print("\nfamily-level Pearson of per-family d (student pooled vs teacher), common set:")
for s in ["S[claude46]", "S[gpt4o]", "S[deepseek_v4]", "S0_relaxed"]:
    print(f"  {s:16s}", {t: round(np.corrcoef(common[s], common[t])[0, 1], 3) for t in TS})
# per-seed values on common families
print("\nper-seed d on common families:")
ps = sym[sym.family_id.isin(common.index)].groupby(["teacher"])["d"].agg(["mean", "count"])
print(ps.round(3).to_string())
# S0 strict (0.9 rule) cells
s0s = M.sym_table(M.frame_table(base, prompts))
s0s = s0s[s0s.variant.isin(["T5", "T6"])].pivot_table(index="family_id", columns="variant", values="p_sym").dropna()
print(f"\nS0 strict 0.9 rule: families with T5&T6 = {len(s0s)}, mean d = {(s0s.T5 - s0s.T6).mean() if len(s0s) else float('nan'):.3f}")
# training-label suggestibility per teacher (train families, hard labels, order-stable items)
tp = {}
for line in open("data/prompts/train_prompts_v2.jsonl"):
    p = json.loads(line); tp[p["prompt_id"]] = p
print("\ntraining-label suggestibility (s1 files): act-rate(T5) - act-rate(T6) on families having both")
for t in TS + ["random_R"]:
    rows = []
    for line in open(f"data/sft/{t}_O_s1.jsonl"):
        e = json.loads(line); p = tp[e["prompt_id"]]
        act = p["letter_to_action"][e["letter"]] == p["focus_action"]
        rows.append((e["family_id"], e["variant"], act))
    df = pd.DataFrame(rows, columns=["f", "v", "act"]).groupby(["f", "v"]).act.mean().unstack()
    both = df[["T5", "T6"]].dropna()
    dd = (both.T5 - both.T6).values; bi = rng.integers(0, len(dd), (NB, len(dd)))
    print(f"  {t:12s} n_fam={len(both)}  act T5={both.T5.mean():.3f} T6={both.T6.mean():.3f} diff={dd.mean():.3f} CI {ci(dd[bi].mean(1))}"
          f"  act rate T1={df['T1'].mean():.3f} T3={df['T3'].mean():.3f}")
