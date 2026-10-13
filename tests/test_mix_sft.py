"""scripts/10c_mix_sft.py: exact size and per-variant match with C, round(p n_C) rows from C, one set across seeds, C / K disjoint,
scripts/10 family order, deterministic, meta sidecar and runs.txt."""

import hashlib
import importlib.util
import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest

from vcd.train.data import family_permutation, order_examples

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/10c_mix_sft.py"
V = ("T1", "T3", "T5", "T6")


def _load():
    spec = importlib.util.spec_from_file_location("mix_sft", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _write(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _row(fam, variant, order, teacher):
    return {"prompt_id": f"{fam}.{variant}.o{order}", "family_id": fam, "variant": variant, "order": order,
            "teacher": teacher, "version": "O", "text_prompt": "p", "text_target": " A\nRationale: r", "letter": "A"}


def _rows(path: Path):
    return [json.loads(l) for l in open(path)]


def _ordered(rows, seed, fams):
    """scripts/10 order over the family universe `fams` (what the builder promises)."""
    return [r["prompt_id"] for r in order_examples(rows, family_permutation(fams, seed), V)]


def _tree(tmp_path: Path):
    """C: 8 families with unequal variant coverage (T1 8, T3 6, T5 7, T6 5 = 26 rows); K: 20 families x 4 variants = 80 rows.
    Seed-2 files hold the same sets in a different (reversed) order."""
    c, k = tmp_path / "c", tmp_path / "k"
    cov = {"T1": range(8), "T3": range(6), "T5": range(7), "T6": range(5)}
    c_rows = [_row(f"c{i:02d}", v, 1 + i % 2, "t1") for i in range(8) for v in V if i in cov[v]]
    k_rows = [_row(f"k{i:02d}", v, 1 + (i + 1) % 2, "t1") for i in range(20) for v in V]
    _write(c / "t1_O_s1.jsonl", c_rows)
    _write(c / "t1_O_s2.jsonl", list(reversed(c_rows)))
    _write(k / "t1_O_s1.jsonl", k_rows)
    _write(k / "t1_O_s2.jsonl", list(reversed(k_rows)))
    return c, k, c_rows, k_rows


def _cli(c, k, out_root, *extra):
    return subprocess.run([sys.executable, str(SCRIPT), "--c-dir", str(c), "--k-dir", str(k), "--out-root", str(out_root), "--shares", "0.25,0.5",
                           "--teachers", "t1", "--seeds", "1,2", "--seed", "7", *extra], cwd=ROOT, capture_output=True, text=True)


def test_split_quota_largest_remainder_and_half_up():
    m = _load()
    # 26 rows: p = .25 -> 6.5 -> 7 (half-up); floors 2,1,1,1 = 5, two more units to the largest remainders T5 (.75) then T3 (.5)
    assert m.split_quota({"T1": 8, "T3": 6, "T5": 7, "T6": 5}, 0.25) == {"T1": (2, 6), "T3": (2, 4), "T5": (2, 5), "T6": (1, 4)}
    # p = .5 -> 13; floors 4,3,3,2 = 12; remainders T3 .0, T5 .5, T6 .5, T1 .0 -> tie T5 / T6 broken by name -> T5
    assert m.split_quota({"T1": 8, "T3": 6, "T5": 7, "T6": 5}, 0.5) == {"T1": (4, 4), "T3": (3, 3), "T5": (4, 3), "T6": (2, 3)}
    # the real C counts: totals are round_half_up(p n_C) and every variant is within one unit of p n_v
    for counts in ({"T1": 1223, "T3": 1248, "T5": 1253, "T6": 1240}, {"T1": 1168, "T3": 1236, "T5": 1233, "T6": 1201}, {"T1": 600, "T3": 705, "T5": 613, "T6": 579}):
        for p in (0.25, 0.5):
            q = m.split_quota(counts, p)
            assert sum(a for a, _ in q.values()) == m.round_half_up(p * sum(counts.values()))
            assert all(a + b == counts[v] and abs(a - p * counts[v]) < 1 for v, (a, b) in q.items())
    assert m.split_quota({"T1": 1223, "T3": 1248, "T5": 1253, "T6": 1240}, 0.25) == {"T1": (306, 917), "T3": (312, 936), "T5": (313, 940), "T6": (310, 930)}
    assert m.round_half_up(1248.5) == 1249 and m.round_half_up(1209.5) == 1210 and m.round_half_up(624.25) == 624
    assert m.share_pct(0.25) == 25 and m.share_pct(0.5) == 50
    with pytest.raises(SystemExit):
        m.share_pct(0.333)


def test_select_prompt_ids_deterministic_and_stratified():
    m = _load()
    c_rows = [_row(f"c{i}", v, 1, "t") for i in range(8) for v in V]
    k_rows = [_row(f"k{i}", v, 1, "t") for i in range(20) for v in V]
    cc, kk = m.select_prompt_ids(c_rows, k_rows, 0.25, 7, 0)
    assert len(cc) == 8 and len(kk) == 24 and len(set(cc)) == 8 and len(set(kk)) == 24
    assert Counter(p.split(".")[1] for p in cc) == {v: 2 for v in V} and Counter(p.split(".")[1] for p in kk) == {v: 6 for v in V}
    assert all(p.startswith("c") for p in cc) and all(p.startswith("k") for p in kk)
    assert (cc, kk) == m.select_prompt_ids(c_rows, k_rows, 0.25, 7, 0)
    assert (cc, kk) != m.select_prompt_ids(c_rows, k_rows, 0.25, 8, 0) and (cc, kk) != m.select_prompt_ids(c_rows, k_rows, 0.25, 7, 1)
    assert cc != m.select_prompt_ids(c_rows, k_rows, 0.5, 7, 0)[0][: len(cc)] or True  # a different share is a different rng stream (no containment promised)
    with pytest.raises(SystemExit):  # K pool too small for a variant
        m.select_prompt_ids(c_rows, [r for r in k_rows if r["variant"] != "T6"], 0.25, 7, 0)


def test_cli_builds_size_matched_mixtures(tmp_path):
    c, k, c_rows, k_rows = _tree(tmp_path)
    out_root = tmp_path / "mix"
    res = _cli(c, k, out_root)
    assert res.returncode == 0, res.stderr
    c_ids, k_ids = {r["prompt_id"] for r in c_rows}, {r["prompt_id"] for r in k_rows}
    c_counts = Counter(r["variant"] for r in c_rows)
    fams = sorted({r["family_id"] for r in c_rows} | {r["family_id"] for r in k_rows})
    expect_from_c = {25: 7, 50: 13}
    for pct in (25, 50):
        d = Path(f"{out_root}{pct}")
        s1, s2 = _rows(d / "t1_O_s1.jsonl"), _rows(d / "t1_O_s2.jsonl")
        ids1 = [r["prompt_id"] for r in s1]
        assert len(s1) == len(s2) == len(c_rows) == 26 and len(set(ids1)) == 26  # exact size, no duplicate
        assert set(ids1) == {r["prompt_id"] for r in s2}  # one set for every seed
        assert Counter(r["variant"] for r in s1) == c_counts  # per-variant counts equal C's
        n_c = sum(p in c_ids for p in ids1)
        assert n_c == expect_from_c[pct] and all(p in c_ids or p in k_ids for p in ids1)
        # scripts/10 order: family permutation of the C u K universe keyed by the run seed, variants T1,T3,T5,T6 then option order
        assert ids1 == _ordered(s1, 1, fams) and [r["prompt_id"] for r in s2] == _ordered(s2, 2, fams) and ids1 != [r["prompt_id"] for r in s2]
        fam_seq = [r["family_id"] for r in s1]
        assert len(set(fam_seq)) == 1 + sum(fam_seq[i] != fam_seq[i - 1] for i in range(1, len(fam_seq)))  # each family contiguous
        meta = json.load(open(d / "t1_O_s1.meta.json"))
        assert meta["control"] == "mix" and meta["share"] == pct / 100 and meta["share_pct"] == pct
        assert meta["n_examples"] == 26 and meta["n_from_C"] == expect_from_c[pct] and meta["n_from_K"] == 26 - expect_from_c[pct]
        assert meta["variant_counts"] == dict(c_counts) and sum(meta["variant_counts_from_C"].values()) == expect_from_c[pct]
        assert {v: meta["variant_counts_from_C"][v] + meta["variant_counts_from_K"][v] for v in V} == dict(c_counts)
        assert meta["source_C"].endswith("c/t1_O_s1.jsonl") and meta["source_K"].endswith("k/t1_O_s1.jsonl")
        assert meta["source_C_sha256"] == hashlib.sha256((c / "t1_O_s1.jsonl").read_bytes()).hexdigest()
        assert meta["sha256"] == hashlib.sha256((d / "t1_O_s1.jsonl").read_bytes()).hexdigest()
        assert meta["selected_prompt_ids_sha256"] == hashlib.sha256("\n".join(sorted(ids1)).encode()).hexdigest() == meta["prompt_ids_sha256"]
        assert meta["subsample_seed"] == 7 and meta["rng_key"] == [7, 0, pct] and meta["n_families_universe"] == 28
        assert json.load(open(d / "t1_O_s2.meta.json"))["selected_prompt_ids_sha256"] == meta["selected_prompt_ids_sha256"]
        assert (d / "runs.txt").read_text().splitlines() == [str(d / "t1_O_s1.jsonl"), str(d / "t1_O_s2.jsonl")]
    # the two shares draw different sets (independent rng streams), both deterministic
    a = json.load(open(f"{out_root}25/t1_O_s1.meta.json"))["selected_prompt_ids_sha256"]
    b = json.load(open(f"{out_root}50/t1_O_s1.meta.json"))["selected_prompt_ids_sha256"]
    assert a != b
    before = {pct: (Path(f"{out_root}{pct}") / "t1_O_s1.jsonl").read_bytes() for pct in (25, 50)}
    assert _cli(c, k, out_root).returncode != 0  # refuses to overwrite
    assert _cli(c, k, out_root, "--overwrite").returncode == 0
    assert all((Path(f"{out_root}{pct}") / "t1_O_s1.jsonl").read_bytes() == before[pct] for pct in (25, 50))  # byte-identical rebuild
    other = _cli(c, k, tmp_path / "other", "--seed", "8")
    assert other.returncode == 0 and (tmp_path / "other25" / "t1_O_s1.jsonl").read_bytes() != before[25]


def test_cli_rejects_overlap_and_set_mismatch(tmp_path):
    c, k, c_rows, k_rows = _tree(tmp_path)
    _write(k / "t1_O_s1.jsonl", k_rows + [c_rows[0]])  # a C family inside K
    _write(k / "t1_O_s2.jsonl", list(reversed(k_rows + [c_rows[0]])))
    res = _cli(c, k, tmp_path / "mix")
    assert res.returncode != 0 and "not disjoint" in res.stderr
    c, k, c_rows, k_rows = _tree(tmp_path / "b")
    _write(c / "t1_O_s2.jsonl", c_rows[:-1])  # seed files of C disagree
    res = _cli(c, k, tmp_path / "b" / "mix")
    assert res.returncode != 0 and "do not share one example set" in res.stderr
