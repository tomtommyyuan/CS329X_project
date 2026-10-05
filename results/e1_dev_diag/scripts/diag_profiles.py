"""Dev diagnostics (not decision rules): suggestibility delta(T5) - delta(T6) per teacher / student group, and
profile correlations of the untrained base with the 0.9 mass rule RELAXED (every row with p_letters counts)."""
import numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
from vcd.teacher import profile as P
V = ["T1", "T3", "T5", "T6"]; TS = ["gpt4o", "claude46", "deepseek_v4"]
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
base_relaxed = [r.model_copy(update={"category": "answer", "teacher": "S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
sym_t = M.sym_table(M.frame_table(trows, prompts)); sym_s = M.sym_table(M.frame_table([r for r in srows if not r.teacher.endswith("base_B_s0")] + base_relaxed, prompts))
sh_t, sh_s = P.framing_shifts(sym_t, V), P.framing_shifts(sym_s, V)
def grp(w):
    if w in TS or w == "S0_relaxed": return w
    k = M.parse_run_id(w); return f"S[{k.teacher}_{k.version}]"
sh = pd.concat([sh_t, sh_s]); sh["group"] = sh["teacher"].map(grp)
d = sh.groupby(["group", "teacher", "variant"])["r"].mean().unstack()
d["sugg_T5_minus_T6"] = d["T5"] - d["T6"]
g = d.groupby("group")[["T1", "T3", "T5", "T6", "sugg_T5_minus_T6"]].agg(["mean", "std"])
print("framing effects delta(variant) = mean family-demeaned shift r; students: mean (sd) over seeds")
out = pd.DataFrame({c: g[(c, "mean")].round(3).astype(str) + " (" + g[(c, "std")].round(3).fillna(0).astype(str) + ")" for c in ["T1", "T3", "T5", "T6", "sugg_T5_minus_T6"]})
print(out.to_string())
rho = M.profile_rho(sh_s[sh_s.teacher == "S0_relaxed"], sh_t, V)
print("\nS_0 with the 0.9 rule relaxed (diagnostic only): profile correlation with each teacher")
print(rho.round(3).to_string(index=False))
pooled = sh_s[sh_s.teacher != "S0_relaxed"].assign(group=lambda x: x.teacher.map(grp)).groupby(["group", "family_id", "variant"])["r"].mean().reset_index().rename(columns={"group": "teacher"})
print("\nseed-pooled student profiles vs teachers (Pearson, same as pooled_inheritance's rho; families complete for both)")
print(M.profile_rho(pooled, sh_t, V).pivot_table(index="run_id", columns="teacher", values="pearson").round(3).to_string())
