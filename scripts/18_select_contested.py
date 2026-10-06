"""Step 18 (E2c): apply the contested rule to the T1 screening demos and build the contested training set.

Rule (tasks/e2c_plan.md §3, verbatim): A family is CONTESTED if the symmetrized majority action differs between
at least two teachers, or any teacher's symmetrized p (logprob teachers) lies in [0.2, 0.8]. Claude's two-order
split (p_sym = 0.5) counts as contested (`claude_order_split`); any non-answer excludes the family from both pools.

Inputs: the pool family file, its T1 prompts, and one demo file per teacher (TeacherResponse rows from
scripts/04_query_teachers.py --mode demo --variants T1). Optional tier 0: the existing train families with their
phase-1 demos; their contested families are all included and also serve as the calibration (356 / 1,469 valid).

  python scripts/18_select_contested.py \
      --families data/families/contested_pool.jsonl --prompts data/prompts/contested_pool_T1.jsonl \
      --demos gpt4o=data/teacher_e2c/gpt4o_pool_screen.jsonl,claude46=data/teacher_e2c/claude46_pool_screen.jsonl,deepseek_v4=data/teacher_e2c/deepseek_v4_pool_screen.jsonl \
      --tier0-families data/families/families.jsonl --tier0-prompts data/prompts/train_prompts_v2.jsonl \
      --tier0-demos gpt4o=data/teacher_phase1/gpt4o_train_demo.jsonl,claude46=data/teacher_phase1/claude46_train_demo.jsonl,deepseek_v4=data/teacher_phase1/deepseek_v4_train_demo.jsonl \
      --target 1500 --out data/families/contested_selected.jsonl --report results/e2c/screen_report.md

Outputs: the selected families (split train_contested, meta.screen with verdict / reasons / p_sym / majorities),
optionally the screened consensus families (--consensus-out, the E2c-K sampling pool incl. tier 0), the E2c-K
control set itself (--consensus-select-out: per source EXACTLY the counts of the selected E2c-C set, split
train_consensus_control, same --seed), a per-family CSV, and the report (contested rate per source / wave / human
prior, teacher pairwise disagreement, p_sym histograms, exact-flip sub-tally, not-screened counts).

Pool families without a T1 prompt in --prompts (later waves) get verdict `not_screened`, never `non_answer`.
--exclude-waves drops families of those meta.wave values from BOTH C and K (plan §10: the Berkeley retrospective
pilot on gate failure). Demo rows must carry the teacher key they are passed under (--trust-file-labels relabels).
"""

from __future__ import annotations

import argparse
from collections import Counter
from pathlib import Path
from typing import Optional

import pandas as pd

from vcd.analysis.contested import RATE_COLUMNS, REASONS, classify_all, classify_columns, flip_table, infer_readouts, matched_sample, p_histogram, pairwise_disagreement, rate_table, stratified_sample, symmetrize_t1
from vcd.config import load_models_cfg
from vcd.data.contested_pool import md_table
from vcd.io import load_models, write_jsonl
from vcd.schemas import Family, Prompt, TeacherResponse

DEFAULT_TEACHERS = ["gpt4o", "claude46", "deepseek_v4"]


def _parse_demos(arg: str) -> dict[str, str]:
    out = {}
    for part in arg.split(","):
        if not part:
            continue
        k, v = part.split("=", 1)
        out[k] = v
    return out


def _empty_row(fid: str, verdict: str, teachers: list[str]) -> dict:
    return {"family_id": fid, "verdict": verdict, "reasons": "", "flip_only": False, **{r: False for r in REASONS}, **{f"answered_{t}": False for t in teachers}, **{f"p_x_missing_{t}": 0 for t in teachers}, **{f"band_exact_flip_{t}": False for t in teachers}}


def screen(fams: list[Family], prompts_path: str, demos: dict[str, str], teachers: list[str], models_cfg: Optional[dict], label: str, trust_file_labels: bool = False, variant: str = "T1") -> tuple[pd.DataFrame, Counter]:
    prompts = {p.prompt_id: p for p in load_models(prompts_path, Prompt)}
    rows: list[TeacherResponse] = []
    for t, path in demos.items():
        for r in load_models(path, TeacherResponse):
            if r.teacher != t:
                if not trust_file_labels:
                    raise SystemExit(f"{path}: row {r.prompt_id} is labelled teacher={r.teacher!r} but was passed as {t!r}; fix the --demos mapping or pass --trust-file-labels")
                r = r.model_copy(update={"teacher": t})
            rows.append(r)
    readouts = infer_readouts(rows, models_cfg)
    sym, counts = symmetrize_t1(rows, prompts, readouts, variant=variant)
    if counts.get("duplicate_rows"):
        print(f"WARNING [{label}]: {counts['duplicate_rows']} superseded demo rows (same teacher / prompt appears more than once); the last row counts")
    fam_ids = {f.family_id for f in fams}
    screened_ids = {p.family_id for p in prompts.values() if p.variant == variant} & fam_ids
    missing = sorted(fid for fid in screened_ids if fid not in sym)  # prompted but no demo row from any teacher
    not_screened = sorted(fam_ids - screened_ids)  # no T1 prompt in this prompts file (later waves)
    counts["families_without_any_demo"] = len(missing)
    counts["families_not_screened"] = len(not_screened)
    df = classify_all({k: v for k, v in sym.items() if k in fam_ids}, teachers)
    extra = [_empty_row(m, "non_answer", teachers) for m in missing] + [_empty_row(m, "not_screened", teachers) for m in not_screened]
    if extra:
        df = pd.concat([df, pd.DataFrame(extra, columns=classify_columns(teachers))], ignore_index=True)
    df.insert(0, "set", label)
    counts["readouts"] = str(readouts)
    return df, counts


def _human_prior(f: Family) -> str:
    m = f.meta
    if f.source == "scruples":
        ms = m.get("minority_share")
        return "no_votes" if ms is None else ("minority>=0.3" if ms >= 0.3 else "minority<0.3")
    if f.source == "aita_berkeley":
        return ("prospective" if m.get("prospective") else "retrospective") + ("|human_contested" if m.get("human_contested") else "") + ("|llm_differ" if m.get("llm_differ") else "")
    if f.source == "moral_stories":
        return f"norm_{m.get('norm_polarity')}|{m.get('tier')}"
    if f.source == "hendrycks_ethics":
        return f"consensus_{m.get('consensus_action')}"
    return f"{f.source}:{f.ambiguity}"


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--families", default="data/families/contested_pool.jsonl")
    ap.add_argument("--prompts", default="data/prompts/contested_pool_T1.jsonl")
    ap.add_argument("--demos", default=None, help="teacher=path,... (TeacherResponse jsonl per teacher); omit to run only the tier-0 calibration")
    ap.add_argument("--teachers", default=",".join(DEFAULT_TEACHERS))
    ap.add_argument("--tier0-families", default=None, help="existing families.jsonl: its train split is screened with --tier0-demos")
    ap.add_argument("--tier0-prompts", default=None)
    ap.add_argument("--tier0-demos", default=None, help="teacher=path,... phase-1 train demos")
    ap.add_argument("--target", type=int, default=1500, help="size of the contested training set incl. tier 0")
    ap.add_argument("--seed", type=int, default=20261002)
    ap.add_argument("--out", default="data/families/contested_selected.jsonl")
    ap.add_argument("--consensus-out", default=None, help="write ALL screened consensus families (pool + tier 0; the E2c-K sampling pool) here")
    ap.add_argument("--consensus-select-out", default=None, help="write the E2c-K control set: per source exactly the counts of the selected E2c-C set, split train_consensus_control")
    ap.add_argument("--exclude-waves", default="", help="comma list of meta.wave values excluded from both C and K (plan §10: '1_pilot' when the Berkeley gate fails)")
    ap.add_argument("--trust-file-labels", action="store_true", help="relabel demo rows to the --demos teacher key instead of failing on a mismatch")
    ap.add_argument("--csv", default=None, help="per-family verdict table (default: next to --report)")
    ap.add_argument("--report", default="results/e2c/screen_report.md")
    ap.add_argument("--no-models-cfg", action="store_true", help="infer teacher readouts from the rows instead of configs/models.yaml")
    args = ap.parse_args()
    teachers = [t for t in args.teachers.split(",") if t]
    models_cfg = None if args.no_models_cfg else load_models_cfg()

    pool = load_models(args.families, Family)
    pool_by_id = {f.family_id: f for f in pool}
    excluded_waves = {w for w in args.exclude_waves.split(",") if w}
    if args.demos:
        df_pool, counts_pool = screen(pool, args.prompts, _parse_demos(args.demos), teachers, models_cfg, "pool", args.trust_file_labels)
    else:
        if not args.tier0_families:
            raise SystemExit("nothing to do: give --demos (pool screening) and / or --tier0-families (calibration)")
        df_pool, counts_pool = pd.DataFrame(columns=["set", *classify_columns(teachers)]), Counter({"pool_not_screened": 1})
    frames = [df_pool]
    tier0: list[Family] = []
    tier0_by_id: dict[str, Family] = {}
    counts_t0: Counter = Counter()
    if args.tier0_families:
        if not (args.tier0_prompts and args.tier0_demos):
            raise SystemExit("--tier0-families needs --tier0-prompts and --tier0-demos")
        tier0 = [f for f in load_models(args.tier0_families, Family) if f.split == "train" and f.item_form == "two_action"]
        tier0_by_id = {f.family_id: f for f in tier0}
        df_t0, counts_t0 = screen(tier0, args.tier0_prompts, _parse_demos(args.tier0_demos), teachers, models_cfg, "tier0", args.trust_file_labels)
        frames.append(df_t0)
    df = pd.concat(frames, ignore_index=True)
    fam_of = {**tier0_by_id, **pool_by_id}
    df["source"] = df["family_id"].map(lambda x: fam_of[x].source)
    df["wave"] = df["family_id"].map(lambda x: str(fam_of[x].meta.get("wave", "train")))
    df["prior"] = df["family_id"].map(lambda x: _human_prior(fam_of[x]))
    df["excluded_wave"] = df["wave"].isin(excluded_waves)
    eligible = df[~df["excluded_wave"]]

    # ---- selection ----
    def with_screen(f: Family, row: pd.Series, tier: str) -> Family:
        g = f.model_copy(deep=True)
        g.split = "train_contested"
        g.meta = {**g.meta, "screen": {"verdict": row["verdict"], "reasons": [r for r in REASONS if row[r]], "flip_only": bool(row.get("flip_only", False)), "p_sym": {t: (None if pd.isna(row[f"p_sym_{t}"]) else float(row[f"p_sym_{t}"])) for t in teachers}, "majority": {t: (None if pd.isna(row[f"maj_{t}"]) else row[f"maj_{t}"]) for t in teachers}, "tier": tier}}
        if tier == "tier0":
            g.meta["provenance"] = "existing train family (tier 0), split changed from train"
        return g

    t0_con = eligible[(eligible["set"] == "tier0") & (eligible["verdict"] == "contested")]
    pool_con = eligible[(eligible["set"] == "pool") & (eligible["verdict"] == "contested")]
    selected = [with_screen(tier0_by_id[r.family_id], pd.Series(r._asdict()), "tier0") for r in t0_con.itertuples(index=False)] if len(t0_con) else []
    need = max(0, args.target - len(selected))
    pool_con_fams = [pool_by_id[fid] for fid in pool_con["family_id"]]
    chosen = stratified_sample(pool_con_fams, need, args.seed)
    chosen_ids = {f.family_id for f in chosen}
    rows_by_id = {r.family_id: r for r in pool_con.itertuples(index=False)}
    selected += [with_screen(pool_by_id[fid], pd.Series(rows_by_id[fid]._asdict()), "pool") for fid in sorted(chosen_ids)]
    n = write_jsonl(args.out, selected)
    print(f"selected {n} families (tier0 {len(t0_con)}, new {len(chosen_ids)} of {len(pool_con_fams)} contested) -> {args.out}")
    cons = eligible[eligible["verdict"] == "consensus"]
    cons_fams: list[Family] = []
    for r in cons.itertuples(index=False):
        tier = "tier0" if r.set == "tier0" else "pool"
        g = with_screen(fam_of[r.family_id], pd.Series(r._asdict()), tier)
        g.split = "pool_contested"
        cons_fams.append(g)
    if args.consensus_out:
        print(f"consensus pool (pool + tier 0): {write_jsonl(args.consensus_out, cons_fams)} -> {args.consensus_out}")
    c_counts = Counter(f.source for f in selected)
    k_rows, k_alloc = matched_sample(cons_fams, dict(c_counts), args.seed)
    for g in k_rows:
        g.split = "train_consensus_control"
    if args.consensus_select_out:
        print(f"E2c-K control set: {write_jsonl(args.consensus_select_out, k_rows)} -> {args.consensus_select_out}; per source {k_alloc}")

    # ---- report ----
    csv_path = Path(args.csv) if args.csv else Path(args.report).with_suffix(".csv")
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(csv_path, index=False)
    lines = ["# E2c screening report", "", f"rule: contested = majorities differ between >= 2 teachers OR any logprob teacher p_sym in [0.2, 0.8]; Claude order split = contested; any non-answer -> excluded; families without a T1 prompt in --prompts = not_screened. teachers {teachers}. excluded waves: {sorted(excluded_waves) or 'none'} ({int(df['excluded_wave'].sum())} families kept out of C and K).", ""]
    lines += [f"bookkeeping (pool): {dict(counts_pool)}", ""]
    if args.tier0_families:
        lines += [f"bookkeeping (tier0): {dict(counts_t0)}", ""]
        t0 = df[df["set"] == "tier0"]
        lines += ["## Calibration: existing train (tier 0)", "", f"valid {int((t0['verdict'] != 'non_answer').sum())}, contested {int((t0['verdict'] == 'contested').sum())}, consensus {int((t0['verdict'] == 'consensus').sum())}, non-answer {int((t0['verdict'] == 'non_answer').sum())} (expected 1,469 / 356 / 1,113 / 24)", ""]

    def rt(sub: pd.DataFrame, col: str, name: str) -> list[str]:
        t = rate_table(sub, sub[col], name)
        cols = [name, *RATE_COLUMNS]
        return [md_table(cols, t[cols].values.tolist()), ""]

    lines += ["## Contested rate per set and source", ""] + rt(df, "source", "source")
    for s in sorted(df["set"].unique()):
        lines += [f"### set {s}: by source", ""] + rt(df[df["set"] == s], "source", "source")
    if len(df_pool):
        lines += ["## Per wave (pool)", ""] + rt(df[df["set"] == "pool"], "wave", "wave")
    lines += ["## Per human / construction prior", ""]
    for src, sub in df.groupby("source", sort=True):
        lines += [f"### {src}", ""] + rt(sub, "prior", "prior")
    lines += ["## Teacher pairwise disagreement (defined majorities, both answered)", ""]
    for s in sorted(df["set"].unique()):
        pw = pairwise_disagreement(df[df["set"] == s], teachers)
        lines += [f"set {s}", "", md_table(["pair", "n_families", "n_differ", "rate"], pw.values.tolist()), ""]
    for s_name in sorted(df["set"].unique()):
        d = df[(df["set"] == s_name) & (df["verdict"] != "not_screened")]
        lines += [f"## Non-answer and p_x-missing counts per teacher ({s_name}, screened families only)", "", md_table(["teacher", "families not answered (either order)", "answer rows without p_x"], [[t, int((~d[f"answered_{t}"].astype(bool)).sum()), int(d[f"p_x_missing_{t}"].fillna(0).astype(int).sum())] for t in teachers]), ""]
        lines += [f"## Exact order flips inside the band ({s_name})", "", "band_exact_flip: logprob teacher with p_sym in [0.2, 0.8] and |p_o1 - p_o2| >= 0.9 (both orders confident, opposite). flip_only families are contested through such flips alone; the pre-registered sensitivity set is contested minus flip_only.", "", md_table(["teacher", "answered", "in band", "exact flips", "flip share"], flip_table(d, teachers)), "", f"flip_only families: {int(d['flip_only'].fillna(False).astype(bool).sum())} of {int((d['verdict'] == 'contested').sum())} contested", ""]
        lines += [f"## p_sym distribution ({s_name}, answered families)", ""]
        for t in teachers:
            lines += [f"{t}", "", md_table(["bin", "families"], [[b, c] for b, c in p_histogram(d, t)]), ""]
    lines += ["## Selection", "", md_table(["set", "families"], [["tier0 contested (all)", len(t0_con)], ["pool contested available", len(pool_con_fams)], ["pool contested chosen", len(chosen_ids)], ["target", args.target], ["written (E2c-C)", n], ["flip_only among written", sum(1 for f in selected if f.meta["screen"].get("flip_only"))]]), ""]
    lines += ["E2c-C composition and the matched E2c-K draw (consensus pool incl. tier 0, seed %d):" % args.seed, "", md_table(["source", "C chosen", "K target", "K drawn", "K available"], [[src, c_counts.get(src, 0), k_alloc.get(src, {}).get("target", 0), k_alloc.get(src, {}).get("drawn", 0), k_alloc.get(src, {}).get("available", 0)] for src in sorted(set(c_counts) | set(k_alloc))]), "", f"K written: {len(k_rows)}" + (f" -> {args.consensus_select_out}" if args.consensus_select_out else " (not written; pass --consensus-select-out)"), ""]
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")
    print(f"report -> {args.report}; per-family table -> {csv_path}")
    print(df.groupby(["set", "verdict"]).size())


if __name__ == "__main__":
    main()
