"""Cell-structure decomposition of inheritance (docs/paper_narrative.md figure 4; vcd.analysis.decomposition).

  python scripts/23_cell_decomposition.py --split test --out results/e2c/decomposition/test

Classifies every test cell by the three teachers' majority actions (all agree / exactly one dissents) and reports, per
student condition x teacher, how often the students follow their own teacher on the cells where only that teacher holds
its answer (`own_unique`), where it shares the answer with one other teacher, and where all agree. Also the by-framing
breakdown on own-unique cells and the teachers' pairwise agreement. Descriptive; reads only committed readouts.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import vcd.analysis.e1_metrics as M  # noqa: E402
from vcd.analysis.decomposition import cell_structure, follow_rates, majority_frame, seed_mean, teacher_pairwise  # noqa: E402

DEFAULT_STUDENTS = ("E1=qwen3-4b,E2c_C=qwen3-4b-e2c,K=qwen3-4b-e2ck,K_n=qwen3-4b-e2ckn,Cnf=qwen3-4b-e2cnf,"
                    "E3c=qwen3-4b-e2c-paired,base2_C=smollm3-3b-e2c,base2_K=smollm3-3b-e2ck")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--split", default="test", choices=["dev", "test"])
    ap.add_argument("--runs-dir", default="runs")
    ap.add_argument("--students", default=DEFAULT_STUDENTS, help="label=namespace,... (namespaces under --runs-dir)")
    ap.add_argument("--teachers", default="gpt4o,claude46,deepseek_v4")
    ap.add_argument("--teacher-dir", default="data/teacher_phase1")
    ap.add_argument("--prompts", default=None, help="default data/prompts/{split}_prompts_v2.jsonl")
    ap.add_argument("--variants", default="T1,T3,T5,T6")
    ap.add_argument("--out", default=None, help="default results/e2c/decomposition/{split}")
    a = ap.parse_args()
    teachers = a.teachers.split(",")
    variants = a.variants.split(",")
    out = Path(a.out or f"results/e2c/decomposition/{a.split}")
    out.mkdir(parents=True, exist_ok=True)
    prompts = M.load_prompts(a.prompts or f"data/prompts/{a.split}_prompts_v2.jsonl")
    fm = M.focus_map(prompts)

    tsym = M.sym_table(M.load_responses([f"{a.teacher_dir}/{t}_{a.split}_profile.jsonl" for t in teachers]), prompts, fm)
    structure = cell_structure(majority_frame(tsym, variants), teachers)
    structure.to_csv(out / "cell_structure.csv", index=False)
    counts = structure["structure"].value_counts().rename_axis("structure").reset_index(name="n_cells")
    counts.to_csv(out / "cell_structure_counts.csv", index=False)
    pairwise = teacher_pairwise(structure, teachers)
    pairwise.to_csv(out / "teacher_pairwise.csv", index=False)

    per_run, per_run_var = [], []
    for item in a.students.split(","):
        label, ns = item.split("=")
        rows = M.load_run_responses(a.runs_dir, a.split, ns)
        if not rows:
            print(f"[23] {label}: no {a.split} readouts under {a.runs_dir}/{ns}, skipped")
            continue
        s = majority_frame(M.sym_table(rows, prompts, fm), variants)
        for run_id, g in s.groupby("teacher"):
            if not M.is_run_id(run_id):
                continue
            key = M.parse_run_id(run_id)
            if key.version not in ("O", "F", "C") or key.teacher not in teachers:
                continue
            base = {"condition": label, "version": key.version, "teacher": key.teacher, "run_id": f"{ns}.{key.teacher}_{key.version}_s{key.seed}"}
            fr = follow_rates(g, structure, teachers, key.teacher)
            per_run.append(fr.assign(**base))
            fv = follow_rates(g, structure, teachers, key.teacher, by=("variant",))
            per_run_var.append(fv[fv["category"] == "own_unique"].assign(**base))
    runs = pd.concat(per_run, ignore_index=True)
    runs.to_csv(out / "follow_rates_runs.csv", index=False)
    summary = seed_mean(runs, ["condition", "version", "teacher", "category"])
    summary.to_csv(out / "follow_rates.csv", index=False)
    byvar = seed_mean(pd.concat(per_run_var, ignore_index=True), ["condition", "version", "teacher", "variant"])
    byvar.to_csv(out / "follow_by_variant_own_unique.csv", index=False)

    lines = [f"# 格子结构分解（{a.split}；描述性）", "",
             f"teacher 两两一致率：" + "；".join(f"{r.a} vs {r.b} {r.agreement:.3f}" for r in pairwise.itertuples()) + f"（{len(structure)} 个三家都有多数行动的 cell）", "",
             "| 结构 | cell 数 |", "|---|---|", *[f"| {r.structure} | {r.n_cells} |" for r in counts.itertuples()], "",
             "## 学生在自己 teacher 唱独角的 cell 上的跟随率（seed 均值；follow_other_max = 跟随别家中最高者）", "",
             "| 条件 | 版本 | teacher | cell 数 | follow_own | follow_other_max | n_runs |", "|---|---|---|---|---|---|---|"]
    ou = summary[summary["category"] == "own_unique"]
    for r in ou.itertuples():
        lines.append(f"| {r.condition} | {r.version} | {r.teacher} | {int(r.n_cells)} | {r.follow_own_mean:.3f} | {r.follow_other_max_mean:.3f} | {int(r.n_runs)} |")
    (out / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out} ({len(runs)} run x category rows; {len(structure)} cells)")


if __name__ == "__main__":
    main()
