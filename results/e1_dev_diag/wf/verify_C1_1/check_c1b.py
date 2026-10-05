"""EXPLORATORY (dev only, not pre-registered). Fix NaN handling of check_c1 §5; then ask whether held-out
errors on teacher-unanimous dev cells look like a bug (random / systematic position) or like the base prior
(S_0 read out with the 0.9 mass rule RELAXED, diagnostic only)."""
import glob
import numpy as np, pandas as pd
from vcd.io import read_jsonl
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P

T = ("gpt4o", "claude46", "deepseek_v4")
SEEN = ["T1", "T3", "T5", "T6"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
dev = {r["prompt_id"]: r for r in read_jsonl("data/prompts/dev_prompts_v2.jsonl")}
sym_t = M.sym_table(M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in T]), prompts)
sresp = M.load_run_responses("runs", "dev", "qwen3-4b")
sym_s = M.sym_table(sresp, prompts)

st = sym_t[sym_t.variant.isin(SEEN)].dropna(subset=["p_sym"])
wide = st.pivot_table(index=["family_id", "variant"], columns="teacher", values="p_sym")
stab = st.assign(stable=((st.p_o1 > .5) == (st.p_o2 > .5)).astype(float)).pivot_table(index=["family_id", "variant"], columns="teacher", values="stable")
complete = wide.dropna().index
maj = wide.loc[complete] > 0.5
unan = maj.all(axis=1) | (~maj).all(axis=1)

# S_0 relaxed: p_x from normalised p_letters for every row, ignoring the mass rule
b0 = [r for r in read_jsonl("runs/qwen3-4b/base_B_s0/eval/dev_responses.jsonl")]
rows = []
for r in b0:
    p = dev[r["prompt_id"]]
    pl = r["p_letters"]
    xl = [k for k, v in p["letter_to_action"].items() if v == "x"][0]
    rows.append(dict(family_id=p["family_id"], variant=p["variant"], order=p["order"], p_x=pl[xl] / (pl["A"] + pl["B"])))
b = pd.DataFrame(rows)
focus = M.focus_map(prompts)
flip = b.family_id.map(focus) == "y"
b.loc[flip, "p_x"] = 1 - b.loc[flip, "p_x"]
b0sym = b.groupby(["family_id", "variant"]).p_x.mean()

ss = sym_s[sym_s.variant.isin(SEEN)].dropna(subset=["p_sym"])
ss = ss[ss.teacher.str.contains("_O_")].copy()
ss["own"] = ss.teacher.str.extract(r"qwen3-4b\.(.+)_O_s\d")[0]
out = []
for own in T:
    g = ss[ss.own == own].set_index(["family_id", "variant"])
    g = g[g.index.isin(complete)]
    for name, idx in [("complete_cells", complete), ("own_order_stable", stab.index[stab[own] == 1].intersection(complete)),
                      ("own_order_unstable", stab.index[stab[own] == 0].intersection(complete)),
                      ("unanimous", unan.index[unan]), ("split", unan.index[~unan])]:
        gg = g[g.index.isin(idx)]
        row = dict(student=own, subset=name, n_cells=len(idx))
        for t in T:
            row[f"agree_{t}"] = round(float(((gg.p_sym > .5).to_numpy() == maj.loc[gg.index, t].to_numpy()).mean()), 3)
        row["agree_S0relaxed"] = round(float(((gg.p_sym > .5).to_numpy() == (b0sym.reindex(gg.index) > .5).to_numpy()).mean()), 3)
        out.append(row)
r = pd.DataFrame(out)
print("Agreement on cells where all three teachers have p_sym (seed-pooled, seen variants):")
print(r.to_string(index=False))

print("\nUnanimous cells: student errors (student majority != consensus). Do errors side with S_0 (relaxed)?")
u = unan.index[unan]
cons = maj.loc[u, "gpt4o"]
s0 = (b0sym.reindex(u) > .5)
print("S_0 relaxed agrees with consensus on unanimous cells:", round(float((s0 == cons).mean()), 3), "n", len(u))
for own in T:
    g = ss[ss.own == own].set_index(["family_id", "variant"])
    g = g[g.index.isin(u)]
    smaj = (g.p_sym > .5).to_numpy()
    c = cons.loc[g.index].to_numpy()
    s0g = s0.loc[g.index].to_numpy()
    err = smaj != c
    print(f"{own}: error rate {err.mean():.3f}; P(S_0 disagrees with consensus | student error) = {(s0g != c)[err].mean():.3f}; "
          f"P(S_0 disagrees | student correct) = {(s0g != c)[~err].mean():.3f}")
    gv = g.reset_index()
    gv["err"] = err
    print("   error rate by variant:", gv.groupby("variant").err.mean().round(3).to_dict())
    # positional sanity: student order consistency on dev
s_or = sym_s[sym_s.teacher.str.contains("_O_") & sym_s.variant.isin(SEEN)].dropna(subset=["p_o1", "p_o2"])
print("\nstudent order-majority agreement (o1 vs o2) mean:", round(float(((s_or.p_o1 > .5) == (s_or.p_o2 > .5)).mean()), 3))
print("teacher order-majority agreement:", st.groupby("teacher").apply(lambda g: round(float(((g.p_o1 > .5) == (g.p_o2 > .5)).mean()), 3)).to_dict())
