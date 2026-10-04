"""Step 10: build the student SFT files data/sft/{teacher}_{version}_s{seed}.jsonl (docs/05_training_stack.md §2).

Typical calls (run on the Mac, then rsync data/sft/ to the cluster; no API, no GPU):
  # O only, 5 seeds, from the Phase 1 train demos
  python scripts/10_build_sft_data.py --teacher gpt4o --versions O --seeds 1,2,3,4,5
  # paired O / F / C once the train-set rewrites exist in data/rewrites_v9/{teacher}/rewrites.jsonl
  python scripts/10_build_sft_data.py --teacher gpt4o --versions O,F,C --seeds 1,2,3,4,5 --rewrites-dir data/rewrites_v9
  # random-label control R (same prompts as gpt4o's O file of the same seed; build that first)
  python scripts/10_build_sft_data.py --random-label --ref-teacher gpt4o --seeds 1,2,3
  # only list the O prompt_ids that need rewriting (rewrite budget), no SFT file written
  python scripts/10_build_sft_data.py --teacher gpt4o --list-prompt-ids
  # smoke test on the pilot data
  python scripts/10_build_sft_data.py --teacher gpt4o --versions O,F,C --seeds 1 \
      --prompts data/prompts/pilot_prompts_v2.jsonl --demos data/teacher_v2/gpt4o_demo.jsonl --out-dir /tmp/sft

Every file gets a sidecar {name}.meta.json with the filter counts, the file sha256 and the prompt_id-set sha256
(the trainer copies them into train_manifest.json). O files of different seeds differ only in row order.

Safety: a version with 0 examples after filtering / pairing aborts the run before anything is written (so a paired
O,F,C build against a train set whose rewrites are missing cannot clobber a good O file with an empty one), and an
existing non-empty output file is never overwritten without --overwrite.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from vcd.config import resolve
from vcd.io import load_models, read_jsonl, write_jsonl
from vcd.schemas import Prompt, TeacherResponse
from vcd.train.data import (
    DEFAULT_ORDER_SEED,
    ORDER_POLICIES,
    RANDOM_TEACHER,
    build_random_examples,
    family_permutation,
    file_sha256,
    load_sft_rows,
    load_train_yaml,
    order_examples,
    pair_versions,
    prompt_ids_sha256,
    select_demo_targets,
    summarize_examples,
    version_examples,
)


def _seeds(text: str | None, default: list[int]) -> list[int]:
    return default if not text else [int(s) for s in text.split(",") if s.strip()]


def _check_writable(out_dir: Path, names: list[str], overwrite: bool) -> None:
    """Refuse to clobber an existing non-empty SFT file unless --overwrite (R control files are built on top of them)."""
    clobber = [out_dir / f"{n}.jsonl" for n in names if (out_dir / f"{n}.jsonl").exists() and (out_dir / f"{n}.jsonl").stat().st_size > 0]
    if clobber and not overwrite:
        sys.exit("refusing to overwrite existing non-empty file(s) without --overwrite: " + ", ".join(map(str, clobber)))


def _write(out_dir: Path, name: str, examples: list[dict], meta: dict, tokenizer) -> None:
    if not examples:
        sys.exit(f"refusing to write {out_dir / name}.jsonl with 0 examples (see the filter counts above)")
    path = out_dir / f"{name}.jsonl"
    write_jsonl(path, examples)
    stats = summarize_examples(examples, tokenizer)
    meta = {**meta, **stats, "prompt_ids_sha256": prompt_ids_sha256(examples), "sha256": file_sha256(path),
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")}
    (out_dir / f"{name}.meta.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\n{path}  n_examples={stats['n_examples']}  families={stats['n_families']}  letters={stats['letter_counts']}")
    print(f"  variants={stats['variant_counts']}  orders={stats['order_counts']}")
    if stats["n_examples"]:
        line = f"  target: mean {stats['mean_target_chars']:.0f} chars / {stats['mean_target_words']:.1f} words (max {stats['max_target_chars']} chars)"
        if "mean_target_tokens" in stats:
            line += f"; tokens: prompt {stats['mean_prompt_tokens']:.1f}, target {stats['mean_target_tokens']:.1f}, max total {stats['max_total_tokens']}, target/epoch {stats['n_target_tokens_per_epoch']:,}"
        print(line)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--config", default="configs/train.yaml", help="YAML with paths.{prompts_train,teacher_dir,rewrites_dir,sft_dir}, data.{variants,order_policy,paired}, seeds, control_seeds")
    ap.add_argument("--teacher", default=None, help="teacher key, e.g. gpt4o / claude46 / deepseek_v4 (required unless --random-label)")
    ap.add_argument("--versions", "--version", default="O", help="comma list from O,F,C to build together (paired by default); 'R' is a synonym for --random-label")
    ap.add_argument("--seeds", default=None, help="comma list; default config `seeds` (O/F/C) or `control_seeds` (R)")
    ap.add_argument("--prompts", default=None, help="Prompt jsonl; default paths.prompts_train")
    ap.add_argument("--demos", default=None, help="TeacherResponse demo jsonl; default {teacher_dir}/{teacher}_train_demo.jsonl")
    ap.add_argument("--rewrites-dir", "--rewrites", default=None, help="dir with {teacher}/rewrites.jsonl; default paths.rewrites_dir")
    ap.add_argument("--out-dir", default=None, help="default paths.sft_dir (data/sft)")
    ap.add_argument("--order-policy", default=None, choices=ORDER_POLICIES, help="stable_one (protocol: order-stable items, one seeded order) | stable_both | both; default config data.order_policy")
    ap.add_argument("--order-seed", type=int, default=DEFAULT_ORDER_SEED, help="seed that picks the kept order per item; fixed, NOT the run seed")
    ap.add_argument("--no-paired", "--unpaired", action="store_true", help="do not intersect prompt_ids across the versions built together")
    ap.add_argument("--random-label", action="store_true", help="build the random-label control R from --ref-teacher's O file of the same seed")
    ap.add_argument("--ref-teacher", default="gpt4o", help="teacher whose O_s{seed}.jsonl supplies R's prompt set and order")
    ap.add_argument("--list-prompt-ids", action="store_true", help="only write {out_dir}/{teacher}_O_prompt_ids.txt (the O set after the order policy) and exit")
    ap.add_argument("--tokenizer", default=None, help="optional HF tokenizer name/path for token statistics, e.g. Qwen/Qwen3-4B-Base (cached locally)")
    ap.add_argument("--overwrite", action="store_true", help="allow replacing an existing non-empty output file")
    args = ap.parse_args()

    cfg = load_train_yaml(args.config)  # no .env: this script calls no API
    paths = cfg["paths"]
    out_dir = resolve(args.out_dir) if args.out_dir else paths["sft_dir"]
    out_dir.mkdir(parents=True, exist_ok=True)
    versions = [v.strip().upper() for v in args.versions.split(",") if v.strip()]
    random_label = args.random_label or versions == ["R"]
    if "R" in versions and not random_label:
        sys.exit("R cannot be built together with O/F/C; call --random-label separately after the reference O files exist")
    tokenizer = None
    if args.tokenizer:
        from transformers import AutoTokenizer  # optional heavy import

        tokenizer = AutoTokenizer.from_pretrained(args.tokenizer)

    if random_label:
        seeds = _seeds(args.seeds, list(cfg.get("control_seeds", [1, 2, 3])))
        _check_writable(out_dir, [f"{RANDOM_TEACHER}_R_s{s}" for s in seeds], args.overwrite)
        for seed in seeds:
            ref = out_dir / f"{args.ref_teacher}_O_s{seed}.jsonl"
            if not ref.exists():
                sys.exit(f"reference O file missing: {ref}  (build --teacher {args.ref_teacher} --versions O --seeds {seed} first)")
            ref_rows = load_sft_rows(ref)
            examples = build_random_examples(ref_rows, seed)
            meta = {"teacher": RANDOM_TEACHER, "version": "R", "seed": seed, "ref_file": str(ref), "ref_sha256": file_sha256(ref),
                    "ref_prompt_ids_sha256": prompt_ids_sha256(ref_rows)}
            _write(out_dir, f"{RANDOM_TEACHER}_R_s{seed}", examples, meta, tokenizer)
        return

    if not args.teacher:
        sys.exit("--teacher is required (or use --random-label)")
    bad = [v for v in versions if v not in ("O", "F", "C")]
    if bad:
        sys.exit(f"unknown versions {bad}; use O, F, C")
    prompts_path = resolve(args.prompts) if args.prompts else paths["prompts_train"]
    demos_path = resolve(args.demos) if args.demos else paths["teacher_dir"] / f"{args.teacher}_train_demo.jsonl"
    rewrites_dir = resolve(args.rewrites_dir) if args.rewrites_dir else paths["rewrites_dir"]
    data_cfg = cfg.get("data", {})
    variants = tuple(data_cfg.get("variants", ["T1", "T3", "T5", "T6"]))
    order_policy = args.order_policy or data_cfg.get("order_policy", "stable_one")
    paired = not args.no_paired and bool(data_cfg.get("paired", True))

    prompts = {p.prompt_id: p for p in load_models(prompts_path, Prompt)}
    demos = load_models(demos_path, TeacherResponse)
    o_targets, counts = select_demo_targets(prompts, demos, variants, order_policy, args.order_seed)
    print(f"prompts {counts['n_prompts_in']} -> variants {variants}: {counts['n_prompts_variant']}; demos {counts['n_demos_in']} "
          f"(unmatched {counts['n_demos_unmatched']}, missing {counts['n_missing_demo']}, non-answer {counts['n_dropped_category']}, "
          f"bad format {counts['n_dropped_format']}); items {counts['n_items_answered']}, order-stable {counts['n_items_stable']} "
          f"(rate {counts['order_stable_rate'] if counts['order_stable_rate'] is None else round(counts['order_stable_rate'], 3)}); "
          f"policy {order_policy} -> {counts['n_selected_O']} O prompts")

    if args.list_prompt_ids:
        path = out_dir / f"{args.teacher}_O_prompt_ids.txt"
        path.write_text("\n".join(sorted(o_targets)) + "\n", encoding="utf-8")
        print(f"wrote {len(o_targets)} prompt_ids to {path}")
        return

    rewrites = None
    if any(v in ("F", "C") for v in versions):
        rpath = rewrites_dir / args.teacher / "rewrites.jsonl"
        if not rpath.exists():
            sys.exit(f"rewrites missing: {rpath}")
        rewrites = list(read_jsonl(rpath))
    by_version: dict[str, list[dict]] = {}
    version_counts: dict[str, dict] = {}
    for v in versions:
        by_version[v], version_counts[v] = version_examples(prompts, o_targets, v, args.teacher, rewrites)
        print(f"version {v}: {len(by_version[v])} examples {version_counts[v] or ''}")
    if paired and len(versions) > 1:
        n_o = len(by_version.get("O", next(iter(by_version.values()))))
        by_version = pair_versions(by_version)
        n_paired = len(next(iter(by_version.values())))
        print(f"paired across {versions}: {n_paired} examples ({n_paired / n_o:.1%} of the {n_o} O prompts)" if n_o else f"paired across {versions}: 0 examples")
    empty = [v for v, exs in by_version.items() if not exs]
    if empty:
        sys.exit(f"version(s) {empty} have 0 examples after filtering/pairing; nothing written. "
                 f"For F / C the train-set rewrites must be in {rewrites_dir}/{args.teacher}/rewrites.jsonl; build --versions O alone meanwhile.")

    seeds = _seeds(args.seeds, list(cfg.get("seeds", [1, 2, 3, 4, 5])))
    _check_writable(out_dir, [f"{args.teacher}_{v}_s{s}" for v in versions for s in seeds], args.overwrite)
    rank_by_seed = {s: family_permutation((p.family_id for p in prompts.values()), s) for s in seeds}
    for v in versions:
        for seed in seeds:
            examples = order_examples(by_version[v], rank_by_seed[seed], variants)
            meta = {**counts, **version_counts[v], "teacher": args.teacher, "version": v, "seed": seed, "paired": paired and len(versions) > 1,
                    "versions_built": versions, "variants": list(variants), "prompts_path": str(prompts_path), "demos_path": str(demos_path),
                    "rewrites_dir": str(rewrites_dir) if v in ("F", "C") else None}
            _write(out_dir, f"{args.teacher}_{v}_s{seed}", examples, meta, tokenizer)


if __name__ == "__main__":
    main()
