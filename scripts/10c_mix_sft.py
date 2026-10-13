"""Dose-response mixtures (docs/supplemental_experiments.md §3 row 1; C / K / K_n in tasks/e2c_plan.md §4 and §12): for every
teacher and contested share p, mix that teacher's E2c-C (contested) and E2c-K (consensus) SFT files into
data/sft_e2c_mix{25,50}/{teacher}_O_s{seed}.jsonl with EXACTLY the example count of the C file: round(p * n_C) rows from C
and the rest from K, stratified by framing variant so that the per-variant counts equal C's (each variant's quota is
split p : 1 - p between C and K by largest remainder; totals exact). With K_n (p = 0, scripts/10b) and C (p = 1) this
gives the 4-point curve of teacher-specific inheritance vs the share of contested demonstrations (scripts/24).

  python scripts/10c_mix_sft.py --c-dir data/sft_e2c --k-dir data/sft_e2ck --out-root data/sft_e2c_mix --shares 0.25,0.5

Conventions copied from scripts/10b: ONE example set per (teacher, share) shared by all seeds; sampling without
replacement from the lexically sorted prompt_ids of the seed-1 files with numpy default_rng([seed, teacher_index,
round(100 p)]) -- per variant in sorted order, the C draw before the K draw; a {name}.meta.json sidecar with counts and
sha256s; runs.txt per output directory for slurm/train.sbatch DATA_LIST mode. Rounding: round(p * n_C) is half-up;
per variant floor(p * n_v), the remaining units to the largest fractional remainders (ties: sorted variant name).

Row ORDER is the scripts/10 training order (vcd.train.data.order_examples): families in the run seed's permutation
(vcd.train.data.family_permutation over the union of the teacher's C and K families, keyed by the run seed alone as in
scripts/10), inside a family variants T1, T3, T5, T6 then option order. A mixture file is therefore laid out exactly
like a scripts/10 file over the union prompt set, C and K families interleaved; the sources' own orders are NOT
concatenated (that would train on every contested row first) and rows are NOT shuffled individually (scripts/10 keeps a
family's variants adjacent). C and K are disjoint family sets, which the script asserts (prompt_ids and family_ids).
Deterministic: the cluster rebuild reproduces the committed sha256s. No API, no GPU.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
import math
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Mapping, Sequence

import numpy as np

from vcd.train.data import TRAIN_VARIANTS, family_permutation, order_examples

DEFAULT_TEACHERS = ("gpt4o", "claude46", "deepseek_v4")
DEFAULT_SEEDS = (1, 2, 3, 4, 5)
DEFAULT_SHARES = (0.25, 0.5)
DEFAULT_SEED = 20261013


def _read(path: Path) -> list[dict]:
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _ids_sha256(ids: Iterable[str]) -> str:
    """sha256 over the sorted prompt_id set (the scripts/10 `prompt_ids_sha256` convention)."""
    return hashlib.sha256("\n".join(sorted(set(ids))).encode()).hexdigest()


def _variant(row: dict) -> str:
    return row.get("variant") or row["prompt_id"].rsplit(".", 2)[1]


def share_pct(share: float) -> int:
    """The share as an integer percentage (rng key and directory suffix); shares must be whole percentages in [0, 1]."""
    pct = round(share * 100)
    if not 0.0 <= share <= 1.0 or abs(share * 100 - pct) > 1e-9:
        raise SystemExit(f"share {share} must be a whole percentage in [0, 1] (e.g. 0.25, 0.5)")
    return int(pct)


def round_half_up(x: float) -> int:
    return int(math.floor(x + 0.5))


def split_quota(c_counts: Mapping[str, int], share: float) -> dict[str, tuple[int, int]]:
    """Per variant (n_from_C, n_from_K) with n_from_C + n_from_K = C's count and sum(n_from_C) = round_half_up(share * n_C) exactly.

    Largest remainder: floor(share * n_v) per variant, then one more unit to each of the variants with the largest
    fractional remainder (ties broken by the sorted variant name) until the total is met.
    """
    n_c = sum(c_counts.values())
    total_c = round_half_up(share * n_c)
    base = {v: int(math.floor(share * n)) for v, n in c_counts.items()}
    rem = {v: share * n - base[v] for v, n in c_counts.items()}
    short = total_c - sum(base.values())
    if not 0 <= short <= len(c_counts):  # arithmetic guarantee; guards against a broken share
        raise SystemExit(f"quota rounding failed: total {total_c}, floors {sum(base.values())}")
    for v in sorted(c_counts, key=lambda v: (-rem[v], v))[:short]:
        base[v] += 1
    return {v: (base[v], c_counts[v] - base[v]) for v in sorted(c_counts)}


def select_prompt_ids(c_rows: Sequence[dict], k_rows: Sequence[dict], share: float, seed: int, teacher_index: int) -> tuple[list[str], list[str]]:
    """(C prompt_ids, K prompt_ids) of one mixture set: per variant (sorted) draw the quota without replacement from the lexically sorted pools, C first."""
    quota = split_quota(collections.Counter(_variant(r) for r in c_rows), share)
    pools = {"C": collections.defaultdict(set), "K": collections.defaultdict(set)}
    for name, rows in (("C", c_rows), ("K", k_rows)):
        for r in rows:
            pools[name][_variant(r)].add(r["prompt_id"])
    rng = np.random.default_rng([seed, teacher_index, share_pct(share)])
    chosen = {"C": [], "K": []}
    for variant in sorted(quota):
        for name, need in zip(("C", "K"), quota[variant]):
            pool = sorted(pools[name][variant])
            if len(pool) < need:
                raise SystemExit(f"variant {variant}: {name} has {len(pool)} examples, the mixture needs {need}")
            if need == 0:
                continue
            idx = rng.choice(len(pool), size=need, replace=False)
            chosen[name].extend(pool[i] for i in sorted(idx))
    return chosen["C"], chosen["K"]


def mixture_order(rows: Sequence[dict], universe_families: Iterable[str], seed: int, variants: Sequence[str] = TRAIN_VARIANTS) -> list[dict]:
    """scripts/10 training order: families in the seed's permutation of `universe_families`, inside a family variant rank then option order."""
    return order_examples(rows, family_permutation(universe_families, seed), variants)


def _check_same_set(rows: Sequence[dict], ref_ids: set[str], path: Path, teacher: str) -> None:
    if {r["prompt_id"] for r in rows} != ref_ids:
        raise SystemExit(f"{path}: seed files of {teacher} do not share one example set")


def build(c_dir: Path, k_dir: Path, out_root: str, shares: Sequence[float], teachers: Sequence[str], seeds: Sequence[int], seed: int, overwrite: bool) -> list[Path]:
    written_all: list[Path] = []
    for share in shares:
        pct = share_pct(share)
        out_dir = Path(f"{out_root}{pct}")
        out_dir.mkdir(parents=True, exist_ok=True)
        written: list[Path] = []
        for t_index, teacher in enumerate(teachers):
            c_first, k_first = _read(c_dir / f"{teacher}_O_s{seeds[0]}.jsonl"), _read(k_dir / f"{teacher}_O_s{seeds[0]}.jsonl")
            c_ids, k_ids = {r["prompt_id"] for r in c_first}, {r["prompt_id"] for r in k_first}
            c_fams, k_fams = {r["family_id"] for r in c_first}, {r["family_id"] for r in k_first}
            if c_ids & k_ids or c_fams & k_fams:
                raise SystemExit(f"{teacher}: C and K are not disjoint ({len(c_ids & k_ids)} shared prompt_ids, {len(c_fams & k_fams)} shared families)")
            c_counts = collections.Counter(_variant(r) for r in c_first)
            quota = split_quota(c_counts, share)
            chosen_c, chosen_k = select_prompt_ids(c_first, k_first, share, seed, t_index)
            keep_c, keep_k = set(chosen_c), set(chosen_k)
            universe = sorted(c_fams | k_fams)
            for s in seeds:
                c_path, k_path = c_dir / f"{teacher}_O_s{s}.jsonl", k_dir / f"{teacher}_O_s{s}.jsonl"
                c_rows, k_rows = _read(c_path), _read(k_path)
                _check_same_set(c_rows, c_ids, c_path, teacher)
                _check_same_set(k_rows, k_ids, k_path, teacher)
                from_c = [r for r in c_rows if r["prompt_id"] in keep_c]
                from_k = [r for r in k_rows if r["prompt_id"] in keep_k]
                rows = mixture_order(from_c + from_k, universe, s)
                ids = [r["prompt_id"] for r in rows]
                if len(ids) != len(set(ids)) or len(ids) != len(c_first) or collections.Counter(_variant(r) for r in rows) != c_counts:
                    raise SystemExit(f"{teacher} share {share} seed {s}: mixture invariants violated (n {len(ids)} vs {len(c_first)})")
                out = out_dir / f"{teacher}_O_s{s}.jsonl"
                if out.exists() and not overwrite:
                    raise SystemExit(f"{out} exists; pass --overwrite")
                with open(out, "w", encoding="utf-8") as f:
                    for r in rows:
                        f.write(json.dumps(r, ensure_ascii=False) + "\n")
                meta = {
                    "control": "mix",
                    "description": "dose-response mixture: C (contested) rows + K (consensus) rows, size- and variant-matched to C (scripts/10c_mix_sft.py)",
                    "share": share, "share_pct": pct,
                    "teacher": teacher, "version": "O", "seed": s,
                    "n_examples": len(rows), "n_from_C": len(from_c), "n_from_K": len(from_k),
                    "n_families": len({r["family_id"] for r in rows}), "n_families_from_C": len({r["family_id"] for r in from_c}), "n_families_from_K": len({r["family_id"] for r in from_k}),
                    "variant_counts": dict(sorted(collections.Counter(_variant(r) for r in rows).items())),
                    "variant_counts_from_C": {v: q[0] for v, q in quota.items()}, "variant_counts_from_K": {v: q[1] for v, q in quota.items()},
                    "letter_counts": dict(sorted(collections.Counter(r["letter"] for r in rows).items())),
                    "reference": str(c_path), "reference_n_examples": len(c_rows),
                    "source_C": str(c_path), "source_C_sha256": _sha256(c_path), "source_C_n_examples": len(c_rows),
                    "source_K": str(k_path), "source_K_sha256": _sha256(k_path), "source_K_n_examples": len(k_rows),
                    "subsample_seed": seed, "teacher_index": t_index, "rng_key": [seed, t_index, pct],
                    "selected_prompt_ids_sha256": _ids_sha256(ids), "selected_C_prompt_ids_sha256": _ids_sha256(chosen_c), "selected_K_prompt_ids_sha256": _ids_sha256(chosen_k),
                    "prompt_ids_sha256": _ids_sha256(ids),
                    "order": "scripts/10 training order: vcd.train.data.family_permutation(union of the teacher's C and K families, run seed), then variant rank T1,T3,T5,T6, then option order (order_examples)",
                    "n_families_universe": len(universe),
                    "sha256": _sha256(out), "built_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                }
                with open(out.with_suffix(".meta.json"), "w", encoding="utf-8") as f:
                    json.dump(meta, f, indent=2, ensure_ascii=False)
                written.append(out)
                print(f"{out}  n_examples={len(rows)} (C {len(from_c)} + K {len(from_k)}; reference {len(c_rows)})  variants={meta['variant_counts']}  from_C={meta['variant_counts_from_C']}")
        with open(out_dir / "runs.txt", "w") as f:
            for p in sorted(written):
                f.write(f"{p}\n")
        print(f"wrote {len(written)} files + runs.txt to {out_dir}")
        written_all += written
    return written_all


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--c-dir", default="data/sft_e2c", help="E2c-C SFT files (contested; the size and per-variant reference)")
    ap.add_argument("--k-dir", default="data/sft_e2ck", help="E2c-K SFT files (consensus; supplies the 1 - p share)")
    ap.add_argument("--out-root", default="data/sft_e2c_mix", help="output directory prefix; the share in percent is appended (data/sft_e2c_mix25, data/sft_e2c_mix50)")
    ap.add_argument("--shares", default=",".join(map(str, DEFAULT_SHARES)), help="comma list of contested shares p (whole percentages)")
    ap.add_argument("--teachers", default=",".join(DEFAULT_TEACHERS))
    ap.add_argument("--seeds", default=",".join(map(str, DEFAULT_SEEDS)))
    ap.add_argument("--seed", type=int, default=DEFAULT_SEED, help="subsample seed (fixed; not the run seed)")
    ap.add_argument("--overwrite", action="store_true")
    a = ap.parse_args()
    shares = [float(s) for s in a.shares.split(",") if s.strip()]
    build(Path(a.c_dir), Path(a.k_dir), a.out_root, shares, a.teachers.split(","), [int(s) for s in a.seeds.split(",")], a.seed, a.overwrite)


if __name__ == "__main__":
    main()
