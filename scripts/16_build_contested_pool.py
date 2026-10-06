"""Step 16 (E2c): build the contested candidate pool -> data/families/contested_pool.jsonl + results/e2c/pool_report.md.

Sources (tasks/e2c_plan.md §1), all rule-converted without an LLM:
  mc_low         MoralChoice low-ambiguity families from the `sanity` split of families.jsonl (ids unchanged)
  scruples       Scruples Anecdotes, HYPOTHETICAL (WIBTA) posts, cleaned body <= 300 words
  aita_berkeley  ucberkeley-dlab r/AITA 2022-23: WIBTA posts + human / LLM-contested retrospective posts, <= 1,500 chars
  moral_stories  Moral Stories (clean + same_gender_other tiers)
  ethics_justice ETHICS justice impartiality items, one per habit verb phrase

Leakage (§2): every pool situation is checked against ALL existing families (every split, dev / test included) with
the dedup_split TF-IDF cosine (>= 0.9 drop, [0.7, 0.9) listed for review), plus the action-pair rule, within-pool
dedup, AITA post-id / title dedup and a source-item disjointness assertion. families.jsonl is never modified.

Waves (§1): meta.wave is "1" for everything screened first, "1_pilot" / "1_gated" for the Berkeley retrospective
pilot and its gated remainder, "2a" (Moral Stories positive-norm quota) and "2b" (ETHICS quota) for the pinned
wave 2, and "reserve" for everything beyond those quotas (never screened unless the plan is amended).

Hand check (§1 / §11 B): --handcheck-dir writes a seeded 100-row sample per new source for the human pass.

Example (defaults read the Hugging Face cache; pass --no-hf with explicit files to work offline):
  python scripts/16_build_contested_pool.py
  python scripts/16_build_contested_pool.py --sources mc_low,scruples --out /tmp/pool.jsonl --report /tmp/report.md
"""

from __future__ import annotations

import argparse
import random
from collections import Counter
from pathlib import Path

from vcd.data.contested_pool import NEW_SOURCES, check_leakage, dedup_aita_titles, dedup_within_pool, flag_counts, md_table
from vcd.data.load_contested_sources import (
    HARD_FLAGS,
    is_rule_clean,
    load_aita_berkeley,
    load_ethics_justice,
    load_moral_stories,
    load_scruples,
    moralchoice_low_from_families,
)
from vcd.io import load_models, write_jsonl
from vcd.schemas import Family

ALL_SOURCES = ["mc_low", "scruples", "aita_berkeley", "moral_stories", "ethics_justice"]
HF = {
    "scruples": ("tasksource/scruples", ["train.scruples-anecdotes.jsonl", "dev.scruples-anecdotes.jsonl", "test.scruples-anecdotes.jsonl"]),
    "aita_berkeley": ("ucberkeley-dlab/normative_evaluation_llms_everyday_dilemmas", ["normative_evaluation_everyday_dilemmas_dataset.csv"]),
    "moral_stories": ("demelin/moral_stories", ["data/moral_stories_full.jsonl"]),
    "ethics_justice": ("hendrycks/ethics", ["data/justice/train.csv", "data/justice/test.csv", "data/justice/test_hard.csv"]),
}


def hf_files(source: str) -> list[str]:
    from huggingface_hub import hf_hub_download

    repo, files = HF[source]
    return [hf_hub_download(repo, f, repo_type="dataset") for f in files]


def _split_files(arg: str | None, source: str, no_hf: bool) -> list[str]:
    if arg:
        return [a for a in arg.split(",") if a]
    if no_hf:
        raise SystemExit(f"--no-hf given but no files for {source}")
    return hf_files(source)


def assign_waves(fams: list[Family], args, rng: random.Random) -> None:
    """meta.wave per §1. Stratified quotas use a seeded shuffle within strata so the choice is reproducible."""
    by_src: dict[str, list[Family]] = {}
    for f in fams:
        by_src.setdefault(f.source, []).append(f)
    for f in by_src.get("moralchoice", []) + by_src.get("scruples", []):
        f.meta["wave"] = "1"
    bk = by_src.get("aita_berkeley", [])
    for f in bk:
        f.meta["wave"] = "1" if f.meta.get("prospective") else "1_gated"
    retro = sorted([f for f in bk if not f.meta.get("prospective")], key=lambda f: f.family_id)
    rng.shuffle(retro)
    for f in retro[: args.berkeley_retro_pilot]:
        f.meta["wave"] = "1_pilot"
    ms = by_src.get("moral_stories", [])
    for f in ms:
        f.meta["wave"] = "reserve"
    pos = sorted([f for f in ms if f.meta.get("norm_polarity") == "positive"], key=lambda f: f.family_id)
    neg = sorted([f for f in ms if f.meta.get("norm_polarity") == "negative"], key=lambda f: f.family_id)
    rng.shuffle(pos)
    rng.shuffle(neg)
    half = args.ms_wave1 // 2
    for f in pos[:half] + neg[: args.ms_wave1 - half]:
        f.meta["wave"] = "1"
    for f in pos[half : half + args.ms_wave2]:  # wave 2a: positive-norm Moral Stories, pinned now
        f.meta["wave"] = "2a"
    eth = sorted(by_src.get("hendrycks_ethics", []), key=lambda f: f.family_id)
    rng.shuffle(eth)
    for f in eth:
        f.meta["wave"] = "reserve"
    for f in eth[: args.ethics_wave1]:
        f.meta["wave"] = "1"
    for f in eth[args.ethics_wave1 : args.ethics_wave1 + args.ethics_wave2]:  # wave 2b: ETHICS, pinned now
        f.meta["wave"] = "2b"


def write_handcheck(pool: list[Family], out_dir: Path, n: int, seed: int) -> list[tuple[str, int]]:
    """One CSV per new source: a seeded sample of n rows with empty `pass` / `note` columns for the human."""
    import csv

    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for src in sorted({f.source for f in pool} - {"moralchoice"}):
        rows = sorted([f for f in pool if f.source == src], key=lambda f: f.family_id)
        random.Random(seed).shuffle(rows)
        rows = rows[:n]
        path = out_dir / f"e2c_handcheck_{src}.csv"
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(["family_id", "source", "wave", "situation", "action_x", "action_y", "needs_review", "pass_second_person", "pass_two_exclusive_actions", "pass_no_verdict_in_situation", "note"])
            for f in rows:
                w.writerow([f.family_id, f.source, f.meta.get("wave", ""), f.situation, f.action_x, f.action_y, ";".join(f.needs_review), "", "", "", ""])
        written.append((str(path), len(rows)))
    return written


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--families", default="data/families/families.jsonl", help="existing families (read only)")
    ap.add_argument("--out", default="data/families/contested_pool.jsonl")
    ap.add_argument("--report", default="results/e2c/pool_report.md")
    ap.add_argument("--sources", default=",".join(ALL_SOURCES), help=f"comma list from {ALL_SOURCES}")
    ap.add_argument("--no-hf", action="store_true", help="never touch the Hugging Face hub; every source needs explicit files")
    ap.add_argument("--scruples-files", default=None, help="comma list of scruples anecdotes jsonl files")
    ap.add_argument("--berkeley-file", default=None)
    ap.add_argument("--moral-stories-file", default=None)
    ap.add_argument("--ethics-files", default=None, help="comma list of ETHICS justice csv files")
    ap.add_argument("--scruples-max-words", type=int, default=300)
    ap.add_argument("--berkeley-max-chars", type=int, default=1500)
    ap.add_argument("--berkeley-retro-pilot", type=int, default=200, help="retrospective AITA posts screened first (wave 1_pilot)")
    ap.add_argument("--ms-wave1", type=int, default=600, help="Moral Stories families in wave 1 (half per norm polarity)")
    ap.add_argument("--ethics-wave1", type=int, default=300)
    ap.add_argument("--ms-wave2", type=int, default=4400, help="wave 2a: positive-norm Moral Stories beyond wave 1 (pinned)")
    ap.add_argument("--ethics-wave2", type=int, default=1600, help="wave 2b: ETHICS beyond wave 1 (pinned)")
    ap.add_argument("--handcheck-dir", default="data/annotation", help="where the per-source hand-check CSVs go ('' to skip)")
    ap.add_argument("--handcheck-n", type=int, default=100)
    ap.add_argument("--keep-flagged", action="store_true", help="keep rows with HARD_FLAGS instead of dropping them")
    ap.add_argument("--threshold", type=float, default=0.9, help="situation cosine for leakage and within-pool dedup")
    ap.add_argument("--seed", type=int, default=20261002)
    args = ap.parse_args()
    sources = [s for s in args.sources.split(",") if s]
    unknown = set(sources) - set(ALL_SOURCES)
    if unknown:
        raise SystemExit(f"unknown sources {sorted(unknown)}")
    rng = random.Random(args.seed)

    existing = load_models(args.families, Family)
    loaded: dict[str, list[Family]] = {}
    if "mc_low" in sources:
        loaded["mc_low"] = moralchoice_low_from_families(existing)
    if "scruples" in sources:
        loaded["scruples"] = load_scruples(_split_files(args.scruples_files, "scruples", args.no_hf), max_words=args.scruples_max_words)
    if "aita_berkeley" in sources:
        loaded["aita_berkeley"] = load_aita_berkeley(_split_files(args.berkeley_file, "aita_berkeley", args.no_hf)[0], max_chars=args.berkeley_max_chars)
    if "moral_stories" in sources:
        loaded["moral_stories"] = load_moral_stories(_split_files(args.moral_stories_file, "moral_stories", args.no_hf)[0])
    if "ethics_justice" in sources:
        loaded["ethics_justice"] = load_ethics_justice(_split_files(args.ethics_files, "ethics_justice", args.no_hf))

    # 1. conversion quality: drop rows with hard flags
    pool: list[Family] = []
    stats: dict[str, dict] = {}
    all_flags = flag_counts(f for lst in loaded.values() for f in lst)
    for name, fams in loaded.items():
        clean = [f for f in fams if is_rule_clean(f)] if not args.keep_flagged else list(fams)
        hard = Counter(fl for f in fams if not is_rule_clean(f) for fl in f.needs_review if fl in HARD_FLAGS)
        stats[name] = {"loaded": len(fams), "rule_clean": len(clean), "hard_flags": hard}
        pool += clean

    # 2. leakage against every existing family
    leak = check_leakage(pool, existing, sit_threshold=args.threshold)
    assert not leak.source_item_conflicts, f"new-source items already present in families.jsonl: {leak.source_item_conflicts[:5]}"
    ex_sources = {f.source for f in existing}
    assert not (set(NEW_SOURCES) & ex_sources), "a new source already exists in families.jsonl"
    reused_ok = all(f.split == "sanity" for f in existing if f.family_id in leak.reused)
    assert reused_ok, "re-used families must come from the sanity split only"
    pool = [f for f in pool if f.family_id not in leak.drop]

    # 3. within-pool duplicates, then AITA post-id / title duplicates
    pool, dup_pairs = dedup_within_pool(pool, threshold=args.threshold)
    pool, aita_pairs = dedup_aita_titles(pool, threshold=args.threshold)

    # 4. waves and provenance bookkeeping
    assign_waves(pool, args, rng)
    for f in pool:
        f.split = "pool_contested"
        f.meta.setdefault("provenance", f.source)
        f.meta["leak_max_cosine"] = round(leak.max_sim.get(f.family_id, 0.0), 4)
    n = write_jsonl(args.out, pool)
    print(f"wrote {n} families -> {args.out}")
    handcheck = write_handcheck(pool, Path(args.handcheck_dir), args.handcheck_n, args.seed) if args.handcheck_dir else []

    # 5. report
    by_src = Counter(f.source for f in pool)
    by_wave = Counter((f.source, f.meta["wave"]) for f in pool)
    lines = ["# E2c contested pool report", "", f"existing families checked: {len(existing)} (all splits); pool written: {n} -> `{args.out}`", ""]
    prefix = {"mc_low": "mc_", "scruples": "scr_", "aita_berkeley": "bk_", "moral_stories": "ms_", "ethics_justice": "eth_"}
    src_name = {"mc_low": "moralchoice", "scruples": "scruples", "aita_berkeley": "aita_berkeley", "moral_stories": "moral_stories", "ethics_justice": "hendrycks_ethics"}
    per_source = []
    for name, s in stats.items():
        leak_drops = sum(1 for fid in leak.drop if fid.startswith(prefix[name]))
        pool_dups = sum(1 for a, _, _ in dup_pairs + aita_pairs if a.startswith(prefix[name]))
        per_source.append([name, s["loaded"], s["rule_clean"], leak_drops, pool_dups, by_src.get(src_name[name], 0)])
    lines += ["## Per source", "", md_table(["source", "loaded", "rule-clean", "leak drops", "pool dups", "kept"], per_source), ""]
    lines += ["## Waves", "", md_table(["source", "wave", "families"], [[s, w, c] for (s, w), c in sorted(by_wave.items())]), ""]
    lines += ["## Hard flags (rows dropped before the pool)", "", md_table(["source", "flag", "rows"], [[name, fl, c] for name, s in stats.items() for fl, c in sorted(s["hard_flags"].items())]), ""]
    lines += ["## All review flags among loaded rows (informational flags stay in needs_review)", "", md_table(["source", "flag", "rows"], [[src, fl, c] for src, cnt in sorted(all_flags.items()) for fl, c in cnt.most_common()]), ""]
    lines += ["## Leakage vs existing families (situation cosine, char_wb 3-5 TF-IDF)", "", f"vectorizer fitted on: {leak.fit_corpus}. re-used on purpose (same family_id, sanity split): {len(leak.reused)}; dropped: {len(leak.drop)}; review band [0.7, 0.9): {len(leak.review)}; source-item conflicts: {len(leak.source_item_conflicts)}", "", md_table(["max cosine bin (vs all existing, re-used rows excluded)", "pool rows"], [[b, c] for b, c in leak.sim_histogram()]), ""]
    ev = {k: v for k, v in leak.max_sim_eval.items()}
    if ev:
        top = sorted(ev.items(), key=lambda kv: -kv[1])[:10]
        reused_ev = [v for k, v in ev.items() if k in leak.reused]
        lines += ["### Leakage audit vs dev / test only", "", f"pool rows checked (before within-pool dedup): {len(ev)}; max situation cosine vs any dev / test family: {max(ev.values()):.3f}; rows >= 0.7: {sum(v >= 0.7 for v in ev.values())}; re-used sanity rows max: {max(reused_ev) if reused_ev else 0.0:.3f}", "", md_table(["max cosine bin (vs dev / test)", "pool rows"], [[b, c] for b, c in leak.eval_histogram()]), "", "Top-10 pool rows by cosine to dev / test:", "", md_table(["pool", "max cosine"], [[k, v] for k, v in top]), ""]
        lines += [f"Action pairs matching a dev / test pair at >= 0.9 (topic overlap, kept unless the situation is also >= 0.7): {len(leak.action_review)}", ""]
        if leak.action_review:
            lines += [md_table(["pool", "dev/test", "action cosine", "situation cosine"], [list(r) for r in sorted(leak.action_review, key=lambda r: -r[2])[:50]]), ""]
        lines += ["Sensitivity of the 0.9 cut (hand probes on a test DD situation, 2026-10-05): dropping articles 0.997 and reordering sentences 0.966 are caught; a synonym swap 0.842, contractions + determiners 0.754 and a first-half truncation 0.739 are not (review band only). The check therefore catches near-verbatim copies; light paraphrases rely on the source-item disjointness (Reddit / Moral Stories / ETHICS vs GPT-4-generated DD and hand-written MC).", ""]
    if leak.drop:
        lines += [md_table(["dropped", "reason", "matches", "cosine"], [[fid, r, m, s] for fid, (r, m, s) in sorted(leak.drop.items())]), ""]
    if leak.review:
        lines += ["Review pairs:", "", md_table(["pool", "existing", "cosine"], [[a, b, s] for a, b, s in sorted(leak.review, key=lambda x: -x[2])[:50]]), ""]
    lines += ["## Within-pool duplicates", "", f"situation >= {args.threshold}: {len(dup_pairs)}; AITA post-id / title: {len(aita_pairs)}", ""]
    if dup_pairs or aita_pairs:
        lines += [md_table(["dropped", "kept", "cosine"], [[a, b, s] for a, b, s in (dup_pairs + aita_pairs)[:50]]), ""]
    if handcheck:
        lines += ["## Hand-check samples (seeded, for the human pass of plan §11 B)", "", md_table(["file", "rows"], [[a, b] for a, b in handcheck]), ""]
    lines += ["## Licenses (meta.license)", "", md_table(["source", "license"], [[src, lic] for src, lic in sorted({(f.source, str(f.meta.get("license", ""))) for f in pool})]), ""]
    Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    Path(args.report).write_text("\n".join(lines), encoding="utf-8")
    print(f"report -> {args.report}")
    print("by source:", dict(by_src))
    print("by wave:", {f"{s}/{w}": c for (s, w), c in sorted(by_wave.items())})
    print("leak drops:", len(leak.drop), "| review pairs:", len(leak.review), "| pool dups:", len(dup_pairs), "| aita dups:", len(aita_pairs))


if __name__ == "__main__":
    main()
