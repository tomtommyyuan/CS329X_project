"""Size-matched control K_n (tasks/e2c_plan.md §12, robustness): subsample the E2c-K SFT files of each teacher to the
example count of that teacher's E2c-C files, stratified by framing variant, with ONE example set shared by all seeds
(exactly the structure scripts/10 gives C: same set, seed-specific order). Everything else (rows, targets, file order
within the kept rows) is untouched, so a K_n run differs from the K run only in training-set size.

  python scripts/10b_subsample_sft.py --src-dir data/sft_e2ck --ref-dir data/sft_e2c --out-dir data/sft_e2ckn

Each output file gets a {name}.meta.json sidecar (sha256, counts, the source / reference sha256s, the subsample seed)
and the directory a runs.txt for slurm/train.sbatch DATA_LIST mode. Deterministic: numpy default_rng([seed, teacher
index]) over the prompt_ids sorted lexically, so the cluster rebuild reproduces the committed sha256s.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

DEFAULT_TEACHERS = ("gpt4o", "claude46", "deepseek_v4")
DEFAULT_SEEDS = (1, 2, 3, 4, 5)


def _read(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _variant(row: dict) -> str:
    return row.get("variant") or row["prompt_id"].rsplit(".", 2)[1]


def select_prompt_ids(src_rows: list[dict], ref_rows: list[dict], seed: int, teacher_index: int) -> list[str]:
    """Per variant, draw as many src prompt_ids as the reference has, without replacement, from the lexically sorted ids."""
    ref_counts = collections.Counter(_variant(r) for r in ref_rows)
    by_variant: dict[str, list[str]] = collections.defaultdict(list)
    for r in src_rows:
        by_variant[_variant(r)].append(r["prompt_id"])
    rng = np.random.default_rng([seed, teacher_index])
    chosen: list[str] = []
    for variant in sorted(ref_counts):
        pool = sorted(set(by_variant.get(variant, [])))
        need = ref_counts[variant]
        if len(pool) < need:
            raise SystemExit(f"variant {variant}: source has {len(pool)} examples, reference needs {need}")
        idx = rng.choice(len(pool), size=need, replace=False)
        chosen.extend(pool[i] for i in sorted(idx))
    return chosen


def build(src_dir: Path, ref_dir: Path, out_dir: Path, teachers, seeds, seed: int, overwrite: bool) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    written = []
    for t_index, teacher in enumerate(teachers):
        src_first = src_dir / f"{teacher}_O_s{seeds[0]}.jsonl"
        ref_first = ref_dir / f"{teacher}_O_s{seeds[0]}.jsonl"
        src_rows, ref_rows = _read(src_first), _read(ref_first)
        keep = set(select_prompt_ids(src_rows, ref_rows, seed, t_index))
        keep_sha = hashlib.sha256("\n".join(sorted(keep)).encode()).hexdigest()
        for s in seeds:
            src = src_dir / f"{teacher}_O_s{s}.jsonl"
            rows = _read(src)
            ids = {r["prompt_id"] for r in rows}
            if ids != {r["prompt_id"] for r in src_rows}:
                raise SystemExit(f"{src}: seed files of {teacher} do not share one example set")
            kept = [r for r in rows if r["prompt_id"] in keep]  # source file order = training order
            out = out_dir / f"{teacher}_O_s{s}.jsonl"
            if out.exists() and not overwrite:
                raise SystemExit(f"{out} exists; pass --overwrite")
            with open(out, "w", encoding="utf-8") as f:
                for r in kept:
                    f.write(json.dumps(r, ensure_ascii=False) + "\n")
            meta = {
                "control": "K_n (size-matched consensus control)",
                "teacher": teacher, "version": "O", "seed": s,
                "n_examples": len(kept), "n_families": len({r["family_id"] for r in kept}),
                "variant_counts": dict(sorted(collections.Counter(_variant(r) for r in kept).items())),
                "letter_counts": dict(sorted(collections.Counter(r["letter"] for r in kept).items())),
                "reference": str(ref_dir / f"{teacher}_O_s{s}.jsonl"), "reference_n_examples": len(ref_rows),
                "source": str(src), "source_sha256": _sha256(src), "source_n_examples": len(rows),
                "subsample_seed": seed, "teacher_index": t_index, "selected_prompt_ids_sha256": keep_sha,
                "sha256": _sha256(out), "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            }
            with open(out.with_suffix(".meta.json"), "w", encoding="utf-8") as f:
                json.dump(meta, f, indent=2, ensure_ascii=False)
            written.append(out)
            print(f"{out}  n_examples={len(kept)} (source {len(rows)}, reference {len(ref_rows)})  variants={meta['variant_counts']}")
    with open(out_dir / "runs.txt", "w") as f:
        for p in sorted(written):
            f.write(f"{p}\n")
    print(f"wrote {len(written)} files + runs.txt to {out_dir}")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--src-dir", default="data/sft_e2ck", help="E2c-K SFT files (the larger set)")
    ap.add_argument("--ref-dir", default="data/sft_e2c", help="E2c-C SFT files whose per-variant counts are matched")
    ap.add_argument("--out-dir", default="data/sft_e2ckn")
    ap.add_argument("--teachers", default=",".join(DEFAULT_TEACHERS))
    ap.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    ap.add_argument("--seed", type=int, default=20261007, help="subsample seed (fixed; not the run seed)")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    build(Path(a.src_dir), Path(a.ref_dir), Path(a.out_dir), a.teachers.split(","), [int(s) for s in a.seeds.split(",")], a.seed, a.overwrite)


if __name__ == "__main__":
    main()
