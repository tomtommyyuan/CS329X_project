"""EXPLORATORY (dev/train only): unfiltered teacher train-demo suggestibility vs SFT-filtered; S0 per-family d correlations."""
import json, numpy as np, pandas as pd
from vcd.analysis import e1_metrics as M
TS = ["gpt4o","claude46","deepseek_v4"]
trp = {json.loads(l)["prompt_id"]: json.loads(l) for l in open("data/prompts/train_prompts_v2.jsonl")}
for t in TS:
    rows=[json.loads(l) for l in open(f"data/teacher_phase1/{t}_train_demo.jsonl")]
    df=pd.DataFrame([dict(pid=r["prompt_id"],fam=trp[r["prompt_id"]]["family_id"],var=trp[r["prompt_id"]]["variant"],
        x=float(r.get("choice_action")==trp[r["prompt_id"]]["focus_action"])) for r in rows if r.get("category")=="answer" and r["prompt_id"] in trp])
    # choice_action in raw coordinates; focus alignment: x=1 if chosen == focus
    rate=df.groupby("var")["x"].mean(); w=df.groupby(["fam","var"])["x"].mean().unstack(); b=w.dropna(subset=["T5","T6"])
    print(f"{t}: answered rows {len(df)}; unfiltered marginal T5-T6 {rate['T5']-rate['T6']:.3f}; paired fam-level {(b.T5-b.T6).mean():.3f} (n={len(b)}); rows per var {df['var'].value_counts().to_dict()}")
prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
base=[r.model_copy(update={"category":"answer"}) for r in M.load_run_responses("runs","dev","qwen3-4b") if r.teacher.endswith("base_B_s0") and r.p_letters]
sym=pd.concat([M.sym_table(M.frame_table(trows,prompts)),M.sym_table(M.frame_table(base,prompts))])
w=sym[sym.variant.isin(["T5","T6"])].pivot_table(index=["family_id"],columns=["teacher","variant"],values="p_sym")
D=pd.DataFrame({t:w[(t,"T5")]-w[(t,"T6")] for t in w.columns.get_level_values(0).unique()}).dropna()
print("per-family d corr, S0 relaxed vs teachers (n=%d):"%len(D)); print(D.corr().round(3).to_string())
