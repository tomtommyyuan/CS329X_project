"""EXPLORATORY (dev, not pre-registered): is the random-label student R a valid control? C7 verification."""
import json, numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
D = "/hai/scratch/tomyyc/vcd_diag/wf/verify_C7_0"
rng = np.random.default_rng(0)
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
srows = [r for r in srows if not r.teacher.endswith("base_B_s0")]
bf = M.load_responses([f"{D}/bf16/random_R_s{s}.jsonl" for s in (1, 2, 3)], set(prompts))
bf = [r.model_copy(update={"teacher": r.teacher + "_bf16"}) for r in bf]
sym_t = M.sym_table(M.frame_table(trows, prompts))
sym_s = M.sym_table(M.frame_table(srows + bf, prompts))
R = [f"qwen3-4b.random_R_s{s}" for s in (1, 2, 3)]
# 1. raw readout distribution
print("== 1. R raw readout: letter P(A), p_sym deviation from .5")
for r in R:
    rr = [x for x in srows if x.teacher == r]
    pa = np.array([x.p_letters["A"] for x in rr])
    s = sym_s[sym_s.teacher == r]
    print(r, f"P(A) mean {pa.mean():.4f} min {pa.min():.4f} max {pa.max():.4f} share P(A)>.5 {np.mean(pa>.5):.3f};",
          f"|p_sym-.5| mean {np.abs(s.p_sym-.5).mean():.5f} max {np.abs(s.p_sym-.5).max():.5f}; share p_sym>.5 (focus act x) {np.mean(s.p_sym>.5):.3f}; n p_sym==.5 {(s.p_sym==.5).sum()}")
# compare with an O student
for r in ["qwen3-4b.gpt4o_O_s1"]:
    s = sym_s[sym_s.teacher == r]; print(r, f"|p_sym-.5| mean {np.abs(s.p_sym-.5).mean():.4f}")
# 2. agreement with family cluster bootstrap
print("\n== 2. R agreement (seen variants, ties excluded) with 95% family-bootstrap CI")
m = M._pairs(sym_s[sym_s.teacher.isin(R + [x + "_bf16" for x in R])], sym_t, V)
m = m[(m.p_s != .5) & (m.p_t != .5)]
m["agree"] = ((m.p_s > .5) == (m.p_t > .5)).astype(float)
fams = np.array(sorted(m.family_id.unique()))
def boot(g, B=4000):
    by = g.groupby("family_id")["agree"].agg(["sum", "count"]).reindex(fams).fillna(0)
    sm, ct = by["sum"].to_numpy(), by["count"].to_numpy()
    idx = rng.integers(0, len(fams), (B, len(fams)))
    est = sm[idx].sum(1) / ct[idx].sum(1)
    return sm.sum() / ct.sum(), *np.quantile(est, [.025, .975])
rows = []
for (run, t), g in m.groupby(["run_id", "teacher"]):
    a, lo, hi = boot(g); rows.append(dict(run=run, teacher=t, agree=round(a, 3), lo=round(lo, 3), hi=round(hi, 3), n=len(g)))
print(pd.DataFrame(rows).to_string(index=False))
# teacher share of focus act x
print("teacher share p_sym>.5 (seen):", {t: round(float((sym_t[(sym_t.teacher == t) & sym_t.variant.isin(V)].p_sym > .5).mean()), 3) for t in TS})
# agreement predicted if R picked act by letter-position/constant: R share x
# 3. per-seed fp32 vs bf16 majority-act stability
print("\n== 3. bf16 vs fp32: share of cells where R's majority act differs; flip rates")
for r in R + ["qwen3-4b.gpt4o_O_s1"]:
    a = sym_s[sym_s.teacher == r].set_index(["family_id", "variant"]).p_sym
    if r + "_bf16" in set(sym_s.teacher):
        b = sym_s[sym_s.teacher == r + "_bf16"].set_index(["family_id", "variant"]).p_sym.reindex(a.index)
        print(r, f"cells with different majority act fp32 vs bf16: {np.mean((a>.5)!=(b>.5)):.3f}; mean |dp| {np.abs(a-b).mean():.5f}")
c = M.consistency(sym_s[sym_s.teacher.str.contains("random")], V)
print(c[["teacher", "flip_rate", "mean_jsd", "share_uncertain"]].to_string(index=False))
# 4. profile correlation R vs teachers, per seed, with permutation null (shuffle family labels) and fp32 vs bf16
print("\n== 4. R profile correlation with teachers (Pearson over family-demeaned shifts) + permutation p (shuffle families)")
sh_t = P.framing_shifts(sym_t, V); sh_s = P.framing_shifts(sym_s[sym_s.teacher.isin(R + [x + "_bf16" for x in R])], V)
rows = []
for r in sorted(sh_s.teacher.unique()):
    for t in TS:
        fam = M._complete_families(pd.concat([sh_s, sh_t]), [r, t], V)
        X = M._shift_matrix(sh_s, r, fam, V); Tm = M._shift_matrix(sh_t, t, fam, V)
        obs = np.corrcoef(X.ravel(), Tm.ravel())[0, 1]
        null = []
        for _ in range(2000):
            null.append(np.corrcoef(X[rng.permutation(len(fam))].ravel(), Tm.ravel())[0, 1])
        null = np.array(null)
        # family bootstrap CI
        bs = []
        for _ in range(2000):
            i = rng.integers(0, len(fam), len(fam)); bs.append(np.corrcoef(X[i].ravel(), Tm[i].ravel())[0, 1])
        rows.append(dict(run=r, teacher=t, pearson=round(obs, 3), lo=round(np.quantile(bs, .025), 3), hi=round(np.quantile(bs, .975), 3), p_perm2=round(float(np.mean(np.abs(null) >= abs(obs))), 4), n_fam=len(fam), r_sd=float(X.std())))
df = pd.DataFrame(rows); print(df.to_string(index=False))
# seed-pooled R profile vs each teacher
pooled = sh_s[sh_s.teacher.isin(R)].groupby(["family_id", "variant"])["r"].mean().reset_index().assign(teacher="R_pooled")
print(M.profile_rho(pooled, sh_t, V).round(3).to_string(index=False))
# 5. cross-seed R profile correlation (is R profile reproducible structure or noise?)
print("\n== 5. R seed-vs-seed profile correlation (fp32) and fp32 vs bf16 same seed")
mats = {}
fam = M._complete_families(sh_s, R + [x + "_bf16" for x in R], V)
for r in R + [x + "_bf16" for x in R]: mats[r] = M._shift_matrix(sh_s, r, fam, V).ravel()
for i, a in enumerate(R):
    for b in R[i+1:]: print(a, b, round(np.corrcoef(mats[a], mats[b])[0, 1], 3))
    print(a, "fp32 vs bf16", round(np.corrcoef(mats[a], mats[a + "_bf16"])[0, 1], 3))
# 6. R suggestibility and variant means
d = sh_s[sh_s.teacher.isin(R)].groupby(["teacher", "variant"])["r"].mean().unstack()
d["T5-T6"] = d["T5"] - d["T6"]; print("\n== 6. R framing effects (mean r)"); print(d.round(5).to_string())
