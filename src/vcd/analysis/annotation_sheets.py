"""Human annotation sheets: export CSVs for E0.5 (framing equivalence) and E0.6 (rewrite audit),
score two annotators' filled sheets (pass rate, Cohen's kappa)."""

from __future__ import annotations

import csv
import random
from collections import defaultdict
from pathlib import Path

import pandas as pd

from vcd.schemas import Family, Prompt
from vcd.stats import cohen_kappa

_FRAMING_FIELDS = ["family_id", "variant", "question_text", "option_x", "option_y", "same_decision(1/0)", "fact_added_or_removed(1/0)", "comment"]
_REWRITE_FIELDS = ["prompt_id", "teacher", "version", "original_answer", "rewrite", "same_choice(1/0)", "same_reasons(1/0)", "same_conditions(1/0)", "same_strength(1/0)", "register(F/C)", "comment"]


def export_framing_sheet(prompts: list[Prompt], families: dict[str, Family], out_csv: Path) -> int:
    """One row per family x variant (order 1 only); the T1 row is the reference the others are compared to."""
    rows = []
    for p in prompts:
        if p.order != 1 or p.variant == "VC":
            continue
        f = families[p.family_id]
        body = p.user.split("\n\nOptions:")[0]
        parts = p.user.split("\n\n")  # body, options, [stem], format instruction
        question_text = body if p.variant == "T0" else body + "\n\n" + parts[-2]
        rows.append({"family_id": p.family_id, "variant": p.variant, "question_text": question_text, "option_x": f.action_x, "option_y": f.action_y,
                     "same_decision(1/0)": "", "fact_added_or_removed(1/0)": "", "comment": ""})
    rows.sort(key=lambda r: (r["family_id"], r["variant"]))
    _write(out_csv, _FRAMING_FIELDS, rows)
    return len(rows)


def export_rewrite_sheet(rewrites: pd.DataFrame, records: pd.DataFrame, n_per_version: int, out_csv: Path, seed: int) -> int:
    """Sample kept rewrites per version; show the original teacher answer next to the rewrite."""
    src = records.set_index("prompt_id")["source_text"].to_dict()
    kept = rewrites[rewrites["kept"]]
    parts = [g.sample(n=min(n_per_version, len(g)), random_state=seed) for _, g in kept.groupby("version")]
    sample = pd.concat(parts) if parts else kept.iloc[0:0]
    rows = [{"prompt_id": r.prompt_id, "teacher": r.teacher, "version": r.version, "original_answer": src.get(r.prompt_id, ""), "rewrite": r.text,
             "same_choice(1/0)": "", "same_reasons(1/0)": "", "same_conditions(1/0)": "", "same_strength(1/0)": "", "register(F/C)": "", "comment": ""}
            for r in sample.itertuples()]
    _write(out_csv, _REWRITE_FIELDS, rows)
    return len(rows)


def score_framing(csv_a: Path, csv_b: Path) -> pd.DataFrame:
    a, b = _read(csv_a), _read(csv_b)
    keys = sorted(set(a) & set(b))
    by_variant: dict[str, dict[str, list]] = defaultdict(lambda: {"a": [], "b": []})
    for k in keys:
        v = a[k]["variant"]
        by_variant[v]["a"].append(_bit(a[k]["same_decision(1/0)"]))
        by_variant[v]["b"].append(_bit(b[k]["same_decision(1/0)"]))
    out = []
    for v, d in sorted(by_variant.items()):
        both = [x == 1 and y == 1 for x, y in zip(d["a"], d["b"])]
        out.append({"variant": v, "n": len(both), "pass_rate_both": sum(both) / len(both) if both else float("nan"), "kappa": cohen_kappa(d["a"], d["b"]) if both else float("nan")})
    return pd.DataFrame(out)


_BLIND_FIELDS = ["item_id", "original_answer", "rewrite", "same_choice(1/0)", "same_reasons(1/0)", "same_conditions(1/0)", "same_strength(1/0)", "register(F/C)", "comment"]


def export_blind_rewrite_sheet(per_teacher: dict[str, tuple[pd.DataFrame, pd.DataFrame]], n_per_cell: int, out_csv: Path, key_csv: Path, seed: int) -> int:
    """One shared sheet across teachers: n_per_cell kept rewrites per (teacher, version), shuffled, with
    teacher and version hidden. The key file maps item_id -> prompt_id, teacher, version for scoring."""
    rng = random.Random(seed)
    rows: list[dict] = []
    for teacher, (rewrites, records) in per_teacher.items():
        src = records.set_index("prompt_id")["source_text"].to_dict()
        kept = rewrites[rewrites["kept"]]
        for version, g in kept.groupby("version"):
            g = g.drop_duplicates("prompt_id")
            sample = g.sample(n=min(n_per_cell, len(g)), random_state=seed)
            for r in sample.itertuples():
                rows.append({"prompt_id": r.prompt_id, "teacher": teacher, "version": version, "original_answer": src.get(r.prompt_id, ""), "rewrite": r.text})
    rng.shuffle(rows)
    for i, r in enumerate(rows, 1):
        r["item_id"] = f"R{i:04d}"
    _write(out_csv, _BLIND_FIELDS, [{**{k: "" for k in _BLIND_FIELDS}, "item_id": r["item_id"], "original_answer": r["original_answer"], "rewrite": r["rewrite"]} for r in rows])
    _write(key_csv, ["item_id", "prompt_id", "teacher", "version"], [{k: r[k] for k in ("item_id", "prompt_id", "teacher", "version")} for r in rows])
    return len(rows)


def score_rewrite(csv_a: Path, csv_b: Path, key_csv: Path | None = None) -> pd.DataFrame:
    a, b = _read(csv_a), _read(csv_b)
    if key_csv is not None:  # blind sheet: attach version / teacher from the key
        key = _read(key_csv)
        for d in (a, b):
            for k, row in d.items():
                row.update({f: key.get(k, {}).get(f, "") for f in ("version", "teacher", "prompt_id")})
    keys = sorted(set(a) & set(b))
    fields = ["same_choice(1/0)", "same_reasons(1/0)", "same_conditions(1/0)", "same_strength(1/0)"]
    out = []
    for version in sorted({a[k]["version"] for k in keys}):
        ks = [k for k in keys if a[k]["version"] == version]
        pa = [all(_bit(a[k][f]) == 1 for f in fields) for k in ks]
        pb = [all(_bit(b[k][f]) == 1 for f in fields) for k in ks]
        reg_a = [a[k]["register(F/C)"].strip().upper() == version for k in ks]
        reg_b = [b[k]["register(F/C)"].strip().upper() == version for k in ks]
        out.append({"version": version, "n": len(ks), "pass_rate_both": sum(x and y for x, y in zip(pa, pb)) / len(ks) if ks else float("nan"),
                    "kappa_pass": cohen_kappa(pa, pb) if ks else float("nan"), "style_recognized_both": sum(x and y for x, y in zip(reg_a, reg_b)) / len(ks) if ks else float("nan")})
    return pd.DataFrame(out)


def _bit(s: str) -> int:
    return 1 if str(s).strip() in ("1", "1.0", "yes", "y", "true") else 0


def _key(row: dict) -> str:
    return row.get("item_id") or row.get("prompt_id") or f"{row['family_id']}|{row['variant']}"


def _read(path: Path) -> dict[str, dict]:
    with open(path, newline="", encoding="utf-8") as fh:
        return {_key(r): r for r in csv.DictReader(fh)}


def _write(path: Path, fields: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
