"""scripts/10b_subsample_sft.py: per-variant counts match the reference, one example set across seeds, source order kept, deterministic."""

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def _write(path: Path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")


def _row(fam, variant, order, teacher):
    return {"prompt_id": f"{fam}.{variant}.o{order}", "family_id": fam, "variant": variant, "order": order,
            "teacher": teacher, "version": "O", "text_prompt": "p", "text_target": " A\nRationale: r", "letter": "A"}


def test_subsample_matches_reference_counts(tmp_path):
    src, ref, out = tmp_path / "k", tmp_path / "c", tmp_path / "kn"
    big = [_row(f"f{i}", v, 1, "t1") for i in range(6) for v in ("T1", "T3", "T5", "T6")]  # 24 rows, 6 per variant
    small = [_row(f"g{i}", v, 1, "t1") for i in range(2) for v in ("T1", "T3", "T5")] + [_row("g9", "T6", 1, "t1")]  # 2/2/2/1
    _write(src / "t1_O_s1.jsonl", big)
    _write(src / "t1_O_s2.jsonl", list(reversed(big)))  # same set, other order
    _write(ref / "t1_O_s1.jsonl", small)
    _write(ref / "t1_O_s2.jsonl", small)
    cmd = [sys.executable, str(ROOT / "scripts/10b_subsample_sft.py"), "--src-dir", str(src), "--ref-dir", str(ref),
           "--out-dir", str(out), "--teachers", "t1", "--seeds", "1,2", "--seed", "7"]
    subprocess.run(cmd, check=True, capture_output=True)
    k1 = [json.loads(l) for l in open(out / "t1_O_s1.jsonl")]
    k2 = [json.loads(l) for l in open(out / "t1_O_s2.jsonl")]
    assert len(k1) == len(k2) == 7
    assert {r["prompt_id"] for r in k1} == {r["prompt_id"] for r in k2}
    counts = {v: sum(r["variant"] == v for r in k1) for v in ("T1", "T3", "T5", "T6")}
    assert counts == {"T1": 2, "T3": 2, "T5": 2, "T6": 1}
    assert [r["prompt_id"] for r in k2] == [r["prompt_id"] for r in reversed(k1)]  # source order preserved
    meta = json.load(open(out / "t1_O_s1.meta.json"))
    assert meta["n_examples"] == 7 and meta["reference_n_examples"] == 7 and meta["source_n_examples"] == 24
    assert (out / "runs.txt").read_text().count("\n") == 2
    # deterministic
    subprocess.run(cmd + ["--overwrite"], check=True, capture_output=True)
    assert [json.loads(l)["prompt_id"] for l in open(out / "t1_O_s1.jsonl")] == [r["prompt_id"] for r in k1]
