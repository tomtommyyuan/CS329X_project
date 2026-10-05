"""EXPLORATORY (dev only, not pre-registered). Shared loader: p_sym matrices (family x variant) for teachers,
student runs, seed-pooled student groups and S0 with the 0.9 mass rule relaxed. Run with cwd = repo root."""
import numpy as np, pandas as pd, pickle, os
from vcd.analysis import e1_metrics as M
OUT = "/hai/scratch/tomyyc/vcd_diag/wf/quant"
TS = ["gpt4o", "claude46", "deepseek_v4"]
V5 = ["T0", "T1", "T3", "T5", "T6"]
GROUPS = {"gpt4o": "S[gpt4o]", "claude46": "S[claude46]", "deepseek_v4": "S[deepseek_v4]", "random": "S[R]"}

def build():
    prompts = M.load_prompts("data/prompts/dev_prompts_v2.jsonl")
    trows = M.load_responses([f"data/teacher_phase1/{t}_dev_profile.jsonl" for t in TS], set(prompts))
    srows = [r for r in M.load_run_responses("runs", "dev", "qwen3-4b") if M.is_run_id(r.teacher)]
    base_relaxed = [r.model_copy(update={"category": "answer", "teacher": "S0_relaxed"}) for r in srows if r.teacher.endswith("base_B_s0") and r.p_letters]
    sym = pd.concat([M.sym_table(trows, prompts), M.sym_table([r for r in srows if not r.teacher.endswith("base_B_s0")] + base_relaxed, prompts)])
    piv = sym.pivot_table(index="family_id", columns=["teacher", "variant"], values="p_sym")
    fams = sorted(piv.index)
    P = {}
    for who in sym["teacher"].unique():
        P[who] = piv[who].reindex(index=fams, columns=V5).to_numpy(float)
    runs = {}
    for who in P:
        if M.is_run_id(who):
            k = M.parse_run_id(who)
            if k.teacher != "base":
                runs.setdefault(GROUPS[k.teacher], []).append(who)
    for g, rs in runs.items():
        P[g] = np.mean(np.stack([P[r] for r in sorted(rs)]), axis=0)  # NaN unless every seed has the cell
    return dict(P=P, fams=fams, runs={g: sorted(v) for g, v in runs.items()})

def load():
    f = f"{OUT}/psym.pkl"
    if not os.path.exists(f):
        pickle.dump(build(), open(f, "wb"))
    return pickle.load(open(f, "rb"))

if __name__ == "__main__":
    d = load(); P = d["P"]
    print(len(d["fams"]), {g: len(v) for g, v in d["runs"].items()})
    seen = [1, 2, 3, 4]
    for w in TS + ["S0_relaxed"] + list(GROUPS.values()):
        print(w, "families complete seen:", int(np.isfinite(P[w][:, seen]).all(1).sum()), "complete V5:", int(np.isfinite(P[w]).all(1).sum()))
    allw = TS + ["S0_relaxed"] + list(GROUPS.values())
    print("complete for all (seen):", int(np.all([np.isfinite(P[w][:, seen]).all(1) for w in allw], 0).sum()),
          "complete for all (V5):", int(np.all([np.isfinite(P[w]).all(1) for w in allw], 0).sum()),
          "complete for 3 teachers+4 groups (seen, no S0):", int(np.all([np.isfinite(P[w][:, seen]).all(1) for w in TS + list(GROUPS.values())], 0).sum()))
