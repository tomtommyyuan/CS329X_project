"""E0.1-E0.4: answer rates, order stability, framing-type profiles, reliability, teacher distinctness.

Reads every data/teacher/*_demo.jsonl and *_profile.jsonl, writes CSV tables and a gate summary.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from vcd.io import load_models
from vcd.schemas import Family, Prompt, TeacherResponse
from vcd.teacher import profile as P


def load_inputs(cfg: dict, teacher_dir: Path | None = None) -> tuple[dict[str, Prompt], pd.DataFrame, pd.DataFrame]:
    prompts = {p.prompt_id: p for p in load_models(cfg["paths"]["prompts"], Prompt)}
    fams = load_models(cfg["paths"]["families"], Family)
    fam_df = pd.DataFrame(
        [dict(family_id=f.family_id, source=f.source, item_form=f.item_form, ambiguity=f.ambiguity, controversial=f.controversial, topic_group=f.topic_group, split=f.split) for f in fams]
    )
    rows: list[TeacherResponse] = []
    for path in sorted((teacher_dir or cfg["paths"]["teacher_dir"]).glob("*.jsonl")):
        rows += [r for r in load_models(path, TeacherResponse) if r.prompt_id in prompts]
    df = P.responses_to_frame(rows, prompts) if rows else pd.DataFrame()
    return prompts, fam_df, df


def run(cfg: dict, out_dir: Path | None = None) -> dict[str, pd.DataFrame]:
    out_dir = out_dir or cfg["paths"]["results"]
    out_dir.mkdir(parents=True, exist_ok=True)
    prompts, fam_df, df = load_inputs(cfg)
    if df.empty:
        raise SystemExit("no teacher responses found; run scripts/04_query_teachers.py first")
    df = df.merge(fam_df[["family_id", "source", "item_form", "controversial"]], on="family_id", how="left")
    variants = list(cfg["variants_profile"])
    tables: dict[str, pd.DataFrame] = {}
    # v2 framings foreground a positive act; align each family's coordinates to it (p = P(positive act))
    focus_by_family = {p.family_id: p.focus_action for p in prompts.values() if p.focus_action}
    if focus_by_family:
        df = P.align_to_focus(df, focus_by_family)

    # E0.1 answer rates (demo mode)
    demo = df[df["mode"] == "demo"]
    if not demo.empty:
        t = demo.groupby(["teacher", "source", "variant"])["category"].value_counts(normalize=True).unstack(fill_value=0.0)
        t["n"] = demo.groupby(["teacher", "source", "variant"]).size()
        tables["answer_rates"] = t.reset_index()
        t2 = demo.groupby(["teacher", "source"])["category"].value_counts(normalize=True).unstack(fill_value=0.0)
        t2["n"] = demo.groupby(["teacher", "source"]).size()
        tables["answer_rates_by_source"] = t2.reset_index()
        vc = demo[demo["source"] == "valueconsistency"]
        if not vc.empty:
            t3 = vc.groupby(["teacher", "controversial"])["category"].value_counts(normalize=True).unstack(fill_value=0.0)
            t3["n"] = vc.groupby(["teacher", "controversial"]).size()
            tables["answer_rates_vc_by_controversial"] = t3.reset_index()
        # E0.2 order stability on two_action families
        tables["order_stability"] = P.order_stability(demo[demo["item_form"] == "two_action"])

    # E0.3 profiles (profile mode, two_action families)
    prof = df[(df["mode"] == "profile") & (df["item_form"] == "two_action")]
    if not prof.empty:
        cells = P.cell_estimates(prof)
        sym = P.symmetrize(cells)
        shifts = P.framing_shifts(sym, variants)
        tables["cells"] = cells
        tables["symmetrized"] = sym
        tables["shifts"] = shifts
        tables["type_effects"] = P.type_effects(shifts, seed=int(cfg["seed"]))
        sv = sym[sym["variant"].isin(variants)].copy()
        # P(choose the option lettered A): order 1 has A = x, order 2 has A = y
        sv["p_choose_A"] = (sv["p_o1"] + (1.0 - sv["p_o2"])) / 2.0
        art = sv.groupby("teacher").agg(order_artifact_mean=("order_gap", "mean"), p_choose_A=("p_choose_A", "mean"), n_cells=("order_gap", "count")).reset_index()
        tables["order_artifact"] = art
        rel_o = P.reliability_by_order(sym, variants)
        rel_p = P.reliability_by_pass(cells, variants)
        tables["reliability"] = rel_o.merge(rel_p, on="teacher", how="outer", suffixes=("_order", "_pass"))
        tables["cross_teacher"] = P.cross_teacher(shifts)
        tables["teacher_consistency"] = P.teacher_consistency(sym, variants)
        tables["pairwise_flip_rates"] = P.pairwise_flip_rates(sym, variants)
        tables["flip_overlap"] = P.flip_overlap(sym, variants)
        if "T0" in sym["variant"].values:
            t0 = sym[sym["variant"].isin(["T0", "T1"])].pivot_table(index=["teacher", "family_id"], columns="variant", values="p_sym").dropna()
            t0["abs_diff_T0_T1"] = (t0["T0"] - t0["T1"]).abs()
            tables["t0_vs_t1"] = t0.groupby("teacher")["abs_diff_T0_T1"].agg(["mean", "count"]).reset_index()

    for name, t in tables.items():
        t.to_csv(out_dir / f"{name}.csv", index=False)
    (out_dir / "e0_summary.md").write_text(gate_report(tables, cfg["gates"]), encoding="utf-8")
    return tables


def _fmt(x) -> str:
    return "nan" if x is None or (isinstance(x, float) and np.isnan(x)) else f"{x:.3f}"


def gate_report(tables: dict[str, pd.DataFrame], gates: dict) -> str:
    lines = ["# E0 summary (auto-generated)", ""]
    if "answer_rates_by_source" in tables:
        t = tables["answer_rates_by_source"]
        lines += ["## E0.1 answer rates by teacher x source (demo, T=0)", "", "| teacher | source | answer | refusal | insufficient | malformed | n | gate |", "|---|---|---|---|---|---|---|---|"]
        for _, r in t.iterrows():
            non = float(r.get("refusal", 0.0)) + float(r.get("insufficient", 0.0))
            gate = "HARD FAIL" if non > gates["refusal_hard"] else ("warn" if non > gates["refusal_max"] else "ok")
            lines.append(f"| {r['teacher']} | {r['source']} | {_fmt(r.get('answer', 0.0))} | {_fmt(r.get('refusal', 0.0))} | {_fmt(r.get('insufficient', 0.0))} | {_fmt(r.get('malformed', 0.0))} | {int(r['n'])} | {gate} |")
        lines.append("")
    if "order_stability" in tables:
        lines += ["## E0.2 order stability (demo, two_action)", "", "| teacher | items | both answered | stable rate | gate |", "|---|---|---|---|---|"]
        for _, r in tables["order_stability"].iterrows():
            gate = "ok" if r["order_stable_rate"] >= gates["order_stable_min"] else "FAIL"
            lines.append(f"| {r['teacher']} | {int(r['n_items'])} | {int(r['n_both_answered'])} | {_fmt(r['order_stable_rate'])} | {gate} |")
        lines.append("")
    if "type_effects" in tables:
        lines += ["## E0.3 type effects delta(j) with 95% bootstrap CI", "", "| teacher | variant | delta | CI | n families | systematic |", "|---|---|---|---|---|---|"]
        for _, r in tables["type_effects"].iterrows():
            sysm = "yes" if (abs(r["delta"]) >= gates["type_effect_min"] and (r["ci_lo"] > 0 or r["ci_hi"] < 0)) else "no"
            lines.append(f"| {r['teacher']} | {r['variant']} | {_fmt(r['delta'])} | [{_fmt(r['ci_lo'])}, {_fmt(r['ci_hi'])}] | {int(r['n_families'])} | {sysm} |")
        lines.append("")
    if "type_effects" in tables:
        te = tables["type_effects"].pivot_table(index="teacher", columns="variant", values="delta")
        if "T5" in te.columns and "T6" in te.columns:
            lines += ["## Suggestibility: delta(T5 'Should you do it?') minus delta(T6 'Should you not do it?'), in positive-act coordinates", ""]
            for teacher, row in te.iterrows():
                lines.append(f"- {teacher}: {_fmt(row['T5'] - row['T6'])} (T5 {_fmt(row['T5'])}, T6 {_fmt(row['T6'])})")
            lines.append("")
    if "teacher_consistency" in tables:
        lines += ["## Teacher consistency across profile framings (profile mode, symmetrized)", "", "| teacher | families | uncertain cells (0.05<p<0.95) | pairwise flip rate | families with any flip | mean cross-framing JSD |", "|---|---|---|---|---|---|"]
        for _, r in tables["teacher_consistency"].iterrows():
            lines.append(f"| {r['teacher']} | {int(r['n_families'])} | {_fmt(r['share_uncertain'])} | {_fmt(r['flip_rate'])} | {_fmt(r['family_flip_share'])} | {_fmt(r['mean_jsd'])} |")
        lines.append("")
    if "order_artifact" in tables:
        lines += ["## Order artifact: mean |p(order1) - p(order2)| and position bias P(choose A)", ""]
        for _, r in tables["order_artifact"].iterrows():
            lines.append(f"- {r['teacher']}: artifact {_fmt(r['order_artifact_mean'])}, P(choose A) = {_fmt(r.get('p_choose_A', np.nan))} over {int(r['n_cells'])} cells")
        lines.append("")
    if "reliability" in tables:
        lines += ["## E0.3 profile reliability", "", "| teacher | split-half by order (SB-corrected) | test-retest across passes | gate |", "|---|---|---|---|"]
        for _, r in tables["reliability"].iterrows():
            rel = r.get("reliability", np.nan)
            gate = "ok" if (not np.isnan(rel) and rel >= gates["reliability_min"]) else "FAIL/na"
            lines.append(f"| {r['teacher']} | {_fmt(rel)} (n={int(r.get('n_cells_order', 0) or 0)}) | {_fmt(r.get('r_retest', np.nan))} | {gate} |")
        lines.append("")
    if "cross_teacher" in tables:
        lines += ["## E0.4 teacher distinctness", "", "residual = profile after removing each teacher's own type effects delta(j); the raw correlation includes the direction shared by all teachers.", "", "| A | B | cells | profile Pearson | residual Pearson | profile Spearman | majority agreement | gate |", "|---|---|---|---|---|---|---|---|"]
        for _, r in tables["cross_teacher"].iterrows():
            pr = r["profile_pearson"]
            gate = "HARD FAIL" if pr > gates["teacher_corr_hard"] else ("warn" if pr > gates["teacher_corr_max"] else "ok")
            lines.append(f"| {r['teacher_a']} | {r['teacher_b']} | {int(r['n_cells'])} | {_fmt(pr)} | {_fmt(r.get('residual_pearson', np.nan))} | {_fmt(r['profile_spearman'])} | {_fmt(r['majority_agreement'])} | {gate} |")
        lines.append("")
    if "pairwise_flip_rates" in tables and not tables["pairwise_flip_rates"].empty:
        pf = tables["pairwise_flip_rates"].pivot_table(index="teacher", columns="pair", values="flip_rate")
        lines += ["## Pairwise framing flip rates (share of families whose majority action differs)", "", "| teacher | " + " | ".join(pf.columns) + " |", "|---|" + "---|" * len(pf.columns)]
        for teacher, row in pf.iterrows():
            lines.append(f"| {teacher} | " + " | ".join(_fmt(v) for v in row.values) + " |")
        lines.append("")
    if "flip_overlap" in tables and not tables["flip_overlap"].empty:
        lines += ["## Do teachers flip on the same families? (Jaccard of flipping-family sets)", "", "| A | B | flips A | flips B | shared | Jaccard |", "|---|---|---|---|---|---|"]
        for _, r in tables["flip_overlap"].iterrows():
            lines.append(f"| {r['teacher_a']} | {r['teacher_b']} | {int(r['n_flip_a'])} | {int(r['n_flip_b'])} | {int(r['shared'])} | {_fmt(r['jaccard'])} |")
        lines.append("")
    if "t0_vs_t1" in tables:
        lines += ["## T0 (free rephrase) vs T1: mean |p_T0 - p_T1|", ""]
        for _, r in tables["t0_vs_t1"].iterrows():
            lines.append(f"- {r['teacher']}: {_fmt(r['mean'])} over {int(r['count'])} families")
        lines.append("")
    return "\n".join(lines)
