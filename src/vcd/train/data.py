"""SFT data for the student: the plain-text template and the O / F / C / R training-file builders.

Contract: docs/05_training_stack.md §1 (template, row format), §2 (filters, ordering, random-label control).
Everything here is pure and deterministic; file I/O lives in scripts/10_build_sft_data.py except for
`load_sft_rows`, which the trainer uses to read a finished file.

Template boundary (verified on the SmolLM2 and Qwen3 tokenizers): the prompt ends with "Answer:" and the
target starts with " X", so tok(prompt + target) == tok(prompt) + tok(target) and the first target token is
exactly the letter token that the readout reads after the same prompt.
"""

from __future__ import annotations

import copy
import hashlib
import re
import zlib
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable, Mapping, Optional, Sequence

import numpy as np

from vcd.config import load_yaml, resolve
from vcd.io import read_jsonl
from vcd.schemas import Prompt, TeacherResponse
from vcd.teacher.parse import parse_answer

ASSISTANT_PREFIX = "Answer:"  # no trailing space; the target supplies " X" (docs/05 §1.3)
RANDOM_RATIONALE = "This option is the more reasonable choice in this situation."
RANDOM_TEACHER = "random"
TRAIN_VARIANTS: tuple[str, ...] = ("T1", "T3", "T5", "T6")
VERSIONS: tuple[str, ...] = ("O", "F", "C", "R")
ORDER_POLICIES: tuple[str, ...] = ("stable_one", "stable_both", "both")
DEFAULT_ORDER_SEED = 20261002  # fixed, independent of the run seed, so every seed shares one prompt_id set

SFT_FIELDS: tuple[str, ...] = ("prompt_id", "family_id", "variant", "order", "teacher", "version", "text_prompt", "text_target", "letter")

# Run naming (docs/05 §3.3), shared by the trainer, the readout script and the analysis so they cannot drift.
# run dir name = "{teacher}_{version}_s{seed}"; run id = "{student_short}.{run dir name}"; version B = untrained base.
# The teacher group must start with a letter, so throwaway dirs such as "_smoke_gpt4o_O_s1" are NOT protocol runs.
RUN_NAME_RE = re.compile(r"^(?P<teacher>[a-z][a-z0-9_]*)_(?P<version>[OFCRB])_s(?P<seed>\d+)$")
RUN_ID_RE = re.compile(r"^(?P<student>[^.]+)\.(?P<teacher>[a-z][a-z0-9_]*)_(?P<version>[OFCRB])_s(?P<seed>\d+)$")

_RATIONALE_RE = re.compile(r"rationale\s*[:：]", re.IGNORECASE)


# --------------------------------------------------------------------------- config


def load_train_yaml(path: str | Path = "configs/train.yaml", profile: Optional[str] = None) -> dict:
    """Read configs/train.yaml and resolve its `paths` section; optionally overlay a profile block (e.g. `tiny`).

    Unlike vcd.config.load_e0 this never touches .env: the training stack calls no API and must not carry keys.
    With `profile`, the keys of cfg[profile] overwrite the top level (nested dicts merged key by key); every
    profile block (currently only `tiny`) is removed from the result and `profile` / `config_path` are recorded.
    """
    cfg = load_yaml(path)
    cfg["paths"] = {k: resolve(v) for k, v in cfg.get("paths", {}).items()}
    blocks = {k: cfg.pop(k) for k in ("tiny",) if isinstance(cfg.get(k), dict)}
    if profile not in (None, "default"):
        if profile not in blocks:
            raise ValueError(f"unknown profile {profile!r}; expected one of {['default', *blocks]}")
        _merge_into(cfg, blocks[profile])
    cfg["profile"] = profile or "default"
    cfg["config_path"] = str(path)
    return cfg


def _merge_into(base: dict, override: dict) -> None:
    for k, v in override.items():
        if isinstance(v, dict) and isinstance(base.get(k), dict):
            _merge_into(base[k], v)
        else:
            base[k] = copy.deepcopy(v)


# --------------------------------------------------------------------------- template


def render_prompt(system: str, user: str) -> str:
    """System line, blank line, user text, blank line, assistant prefix. Used verbatim in training and readout."""
    return f"{system}\n\n{user}\n\n{ASSISTANT_PREFIX}"


def render_target(letter: str, rationale: str) -> str:
    """Canonical assistant completion AFTER the prefix: ' A\\nRationale: ...' (leading space, no trailing whitespace)."""
    return f" {letter}\nRationale: {rationale.strip()}"


def canonical_target(raw: Optional[str]) -> Optional[str]:
    """Teacher demo or rewrite text -> render_target(letter, rationale); None without a letter or a 'Rationale:' line.

    The letter comes from `parse_answer` (category must be "answer"); the rationale is everything after the
    first "Rationale:" (case-insensitive), stripped. Teacher noise such as "Answer: B  \\n" is thereby removed.
    """
    if not raw:
        return None
    category, letter = parse_answer(raw)
    if category != "answer" or letter is None:
        return None
    m = _RATIONALE_RE.search(raw)
    if m is None:
        return None
    rationale = raw[m.end():].strip()
    if not rationale:
        return None
    return render_target(letter, rationale)


def target_letter(text_target: str) -> str:
    """The letter a canonical target starts with (" B\\nRationale: ..." -> "B")."""
    return text_target[1]


# --------------------------------------------------------------------------- deterministic choices


def item_order_choice(family_id: str, variant: str, order_seed: int = DEFAULT_ORDER_SEED) -> int:
    """Which option order (1 or 2) of an order-stable (family, variant) item enters training. Run-seed independent."""
    rng = np.random.default_rng([order_seed, zlib.crc32(f"{family_id}.{variant}".encode())])
    return 1 + int(rng.integers(2))


def family_permutation(family_ids: Iterable[str], seed: int) -> dict[str, int]:
    """family_id -> rank in the seed's permutation of the sorted family list. Same for every teacher and version."""
    families = sorted(set(family_ids))
    perm = np.random.default_rng(seed).permutation(len(families))
    return {families[i]: int(rank) for rank, i in enumerate(perm)}


def order_examples(examples: Sequence[dict], family_rank: Mapping[str, int], variants: Sequence[str] = TRAIN_VARIANTS) -> list[dict]:
    """Training order: families by `family_rank`, inside a family by variant order then option order 1, 2."""
    variant_rank = {v: i for i, v in enumerate(variants)}
    return sorted(examples, key=lambda e: (family_rank[e["family_id"]], variant_rank.get(e["variant"], len(variant_rank)), e["order"]))


# --------------------------------------------------------------------------- demo selection (O)


def select_demo_targets(
    prompts: Mapping[str, Prompt],
    demos: Iterable[TeacherResponse],
    variants: Sequence[str] = TRAIN_VARIANTS,
    order_policy: str = "stable_one",
    order_seed: int = DEFAULT_ORDER_SEED,
) -> tuple[dict[str, str], dict]:
    """Apply the variant / category / order filters of docs/05 §2 steps 1-3 to teacher demos.

    Returns (prompt_id -> canonical O target, counts). Order policies:
      stable_one  keep a (family, variant) only if both orders answer with the same action, then keep the one
                  order chosen by `item_order_choice` (protocol default, docs/02 §4.2);
      stable_both same stability filter, keep both orders;
      both        no stability filter, keep every answered prompt.
    """
    if order_policy not in ORDER_POLICIES:
        raise ValueError(f"order_policy must be one of {ORDER_POLICIES}, got {order_policy!r}")
    variants = tuple(variants)
    prompts_v = {pid: p for pid, p in prompts.items() if p.variant in variants}
    counts: dict = {"n_prompts_in": len(prompts), "n_prompts_variant": len(prompts_v), "n_demos_in": 0, "n_demos_unmatched": 0,
                    "n_demos_duplicate": 0, "n_dropped_category": 0, "n_dropped_format": 0}
    target_by_pid: dict[str, str] = {}
    seen: set[str] = set()
    for d in demos:
        counts["n_demos_in"] += 1
        p = prompts_v.get(d.prompt_id)
        if p is None:
            counts["n_demos_unmatched"] += 1
            continue
        if d.prompt_id in seen:
            counts["n_demos_duplicate"] += 1  # keep the first row for a prompt
            continue
        seen.add(d.prompt_id)
        if d.category != "answer":
            counts["n_dropped_category"] += 1
            continue
        target = canonical_target(d.raw)
        if target is None:
            counts["n_dropped_format"] += 1
            continue
        target_by_pid[d.prompt_id] = target
    counts["n_missing_demo"] = len(prompts_v) - len(seen)  # prompts with no demo row at all

    # order policy on (family, variant) items
    items: dict[tuple[str, str], dict[int, str]] = defaultdict(dict)  # (family, variant) -> order -> prompt_id
    for pid in target_by_pid:
        p = prompts_v[pid]
        items[(p.family_id, p.variant)][p.order] = pid
    n_stable = n_unstable = 0
    kept: dict[str, str] = {}
    for (fid, var), by_order in items.items():
        actions = {o: prompts_v[pid].letter_to_action[target_letter(target_by_pid[pid])] for o, pid in by_order.items()}
        stable = len(by_order) == 2 and len(set(actions.values())) == 1
        n_stable += stable
        n_unstable += not stable
        if order_policy == "both":
            kept.update({pid: target_by_pid[pid] for pid in by_order.values()})
        elif stable and order_policy == "stable_both":
            kept.update({pid: target_by_pid[pid] for pid in by_order.values()})
        elif stable:  # stable_one
            pid = by_order[item_order_choice(fid, var, order_seed)]
            kept[pid] = target_by_pid[pid]
    counts.update(
        n_items_answered=len(items),
        n_items_stable=n_stable,
        n_dropped_order_unstable=0 if order_policy == "both" else n_unstable,
        order_stable_rate=(n_stable / len(items)) if items else None,
        order_policy=order_policy,
        order_seed=order_seed,
        n_selected_O=len(kept),
    )
    return kept, counts


def kept_rewrites(rows: Iterable[dict], version: str) -> dict[str, str]:
    """prompt_id -> `text` of the last kept attempt for `version` ("F" or "C") in a rewrites.jsonl."""
    best: dict[str, tuple[int, str]] = {}
    for r in rows:
        if r.get("version") != version or not r.get("kept"):
            continue
        attempt = int(r.get("attempt", 0))
        if r["prompt_id"] not in best or attempt >= best[r["prompt_id"]][0]:
            best[r["prompt_id"]] = (attempt, r["text"])
    return {pid: text for pid, (_, text) in best.items()}


# --------------------------------------------------------------------------- examples


def make_example(p: Prompt, teacher: str, version: str, text_target: str) -> dict:
    """One SFT row (docs/05 §1.2) for prompt `p`."""
    return {
        "prompt_id": p.prompt_id,
        "family_id": p.family_id,
        "variant": p.variant,
        "order": p.order,
        "teacher": teacher,
        "version": version,
        "text_prompt": render_prompt(p.system, p.user),
        "text_target": text_target,
        "letter": target_letter(text_target),
    }


def version_examples(
    prompts: Mapping[str, Prompt],
    o_targets: Mapping[str, str],
    version: str,
    teacher: str,
    rewrites: Optional[Iterable[dict]] = None,
) -> tuple[list[dict], dict]:
    """Unordered examples for one version from the selected O targets (docs/05 §2 step 4 for F / C).

    O uses the teacher text; F / C use the last kept rewrite whose letter equals O's. Returns (examples, counts).
    """
    counts: dict = {}
    if version == "O":
        examples = [make_example(prompts[pid], teacher, "O", t) for pid, t in o_targets.items()]
        return examples, counts
    if version not in ("F", "C"):
        raise ValueError(f"version_examples builds O, F or C, not {version!r}; use build_random_examples for R")
    if rewrites is None:
        raise ValueError(f"version {version} needs rewrites")
    rewritten = kept_rewrites(rewrites, version)
    examples = []
    counts.update(n_dropped_no_rewrite=0, n_dropped_rewrite_format=0, n_dropped_choice_mismatch=0)
    for pid, o_target in o_targets.items():
        text = rewritten.get(pid)
        if text is None:
            counts["n_dropped_no_rewrite"] += 1
            continue
        target = canonical_target(text)
        if target is None:
            counts["n_dropped_rewrite_format"] += 1
            continue
        if target_letter(target) != target_letter(o_target):
            counts["n_dropped_choice_mismatch"] += 1
            continue
        examples.append(make_example(prompts[pid], teacher, version, target))
    return examples, counts


def pair_versions(by_version: Mapping[str, Sequence[dict]]) -> dict[str, list[dict]]:
    """Restrict every version to the intersection of prompt_ids (docs/05 §2 step 5); relative order is kept."""
    shared: Optional[set[str]] = None
    for exs in by_version.values():
        ids = {e["prompt_id"] for e in exs}
        shared = ids if shared is None else shared & ids
    shared = shared or set()
    return {v: [e for e in exs if e["prompt_id"] in shared] for v, exs in by_version.items()}


def build_sft_examples(
    prompts: Sequence[Prompt] | Mapping[str, Prompt],
    demos: Iterable[TeacherResponse],
    rewrites: Optional[Iterable[dict]] = None,
    version: str = "O",
    teacher: str = "gpt4o",
    seed: int = 1,
    variants: Sequence[str] = TRAIN_VARIANTS,
    order_policy: str = "stable_one",
    order_seed: int = DEFAULT_ORDER_SEED,
) -> tuple[list[dict], dict]:
    """One-shot builder for a single (teacher, version, seed): filters, F / C mapping and seed ordering.

    Not paired across versions; the script pairs O / F / C built together via `pair_versions`.
    Returns (examples in training order, counts).
    """
    prompt_map = prompts if isinstance(prompts, Mapping) else {p.prompt_id: p for p in prompts}
    o_targets, counts = select_demo_targets(prompt_map, demos, variants, order_policy, order_seed)
    examples, more = version_examples(prompt_map, o_targets, version, teacher, rewrites)
    counts.update(more)
    rank = family_permutation((p.family_id for p in prompt_map.values()), seed)
    ordered = order_examples(examples, rank, variants)
    counts.update(seed=seed, n_examples=len(ordered), n_families=len({e["family_id"] for e in ordered}))
    return ordered, counts


def build_random_examples(ref_examples: Sequence[dict], seed: int, rationale: str = RANDOM_RATIONALE) -> list[dict]:
    """Random-label control R (docs/05 §2): same prompts and order as the reference O file, balanced letters per family.

    In a family with k examples, floor(k/2) get A and floor(k/2) get B; an odd extra letter and the assignment
    to prompts come from default_rng([seed, crc32(family_id)]). The rationale is a fixed content-free sentence.
    """
    by_family: dict[str, list[dict]] = defaultdict(list)
    for e in ref_examples:
        by_family[e["family_id"]].append(e)
    letter_of: dict[str, str] = {}
    for fid, exs in by_family.items():
        rng = np.random.default_rng([seed, zlib.crc32(fid.encode())])
        k = len(exs)
        letters = ["A"] * (k // 2) + ["B"] * (k // 2)
        if k % 2:
            letters.append("AB"[int(rng.integers(2))])
        letters = [letters[i] for i in rng.permutation(k)]
        for e, letter in zip(exs, letters):
            letter_of[e["prompt_id"]] = letter
    out = []
    for e in ref_examples:
        letter = letter_of[e["prompt_id"]]
        out.append({**{k: e[k] for k in ("prompt_id", "family_id", "variant", "order", "text_prompt")},
                    "teacher": RANDOM_TEACHER, "version": "R", "text_target": render_target(letter, rationale), "letter": letter})
    return out


# --------------------------------------------------------------------------- validation, hashing, stats


def validate_sft_row(row: Mapping, where: str = "") -> None:
    """Raise ValueError unless `row` is a well-formed SFT row at the template boundary."""
    missing = [k for k in SFT_FIELDS if k not in row]
    if missing:
        raise ValueError(f"{where}missing fields {missing}")
    if row["version"] not in VERSIONS:
        raise ValueError(f"{where}version must be one of {VERSIONS}, got {row['version']!r}")
    if row["order"] not in (1, 2):
        raise ValueError(f"{where}order must be 1 or 2")
    tp, tt = row["text_prompt"], row["text_target"]
    if not tp.endswith(ASSISTANT_PREFIX):
        raise ValueError(f"{where}text_prompt must end with {ASSISTANT_PREFIX!r}")
    if len(tt) < 2 or tt[0] != " " or tt[1] not in ("A", "B") or tt[1] != row["letter"]:
        raise ValueError(f"{where}text_target must start with ' ' + letter {row.get('letter')!r}, got {tt[:4]!r}")
    if tt != tt.rstrip():
        raise ValueError(f"{where}text_target has trailing whitespace")


def load_sft_rows(path: str | Path) -> list[dict]:
    """Read a data/sft/*.jsonl file in file order and validate every row (the trainer's entry point)."""
    rows = []
    for i, row in enumerate(read_jsonl(path), start=1):
        validate_sft_row(row, where=f"{path}:{i}: ")
        rows.append(row)
    return rows


def prompt_ids_sha256(examples: Iterable[Mapping]) -> str:
    """sha256 over the sorted prompt_id set: equal across seeds and across paired versions."""
    ids = sorted({e["prompt_id"] for e in examples})
    return hashlib.sha256("\n".join(ids).encode()).hexdigest()


def file_sha256(path: str | Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def summarize_examples(examples: Sequence[Mapping], tokenizer=None) -> dict:
    """Size statistics for the console and the sidecar: counts, target length in chars / words (and tokens with a tokenizer)."""
    n = len(examples)
    out: dict = {
        "n_examples": n,
        "n_families": len({e["family_id"] for e in examples}),
        "variant_counts": dict(sorted(Counter(e["variant"] for e in examples).items())),
        "order_counts": dict(sorted(Counter(e["order"] for e in examples).items())),
        "letter_counts": dict(sorted(Counter(e["letter"] for e in examples).items())),
    }
    if n:
        tgt_chars = np.array([len(e["text_target"]) for e in examples])
        tgt_words = np.array([len(e["text_target"].split()) for e in examples])
        out.update(mean_target_chars=float(tgt_chars.mean()), max_target_chars=int(tgt_chars.max()),
                   mean_target_words=float(tgt_words.mean()), mean_prompt_chars=float(np.mean([len(e["text_prompt"]) for e in examples])))
    if tokenizer is not None and n:
        tp = [len(tokenizer(e["text_prompt"], add_special_tokens=False)["input_ids"]) for e in examples]
        tt = [len(tokenizer(e["text_target"], add_special_tokens=False)["input_ids"]) for e in examples]
        out.update(tokenizer=getattr(tokenizer, "name_or_path", str(tokenizer)), mean_prompt_tokens=float(np.mean(tp)),
                   mean_target_tokens=float(np.mean(tt)), max_total_tokens=int(max(a + b for a, b in zip(tp, tt))),
                   n_target_tokens_per_epoch=int(sum(tt)), n_total_tokens_per_epoch=int(sum(tp) + sum(tt)))
    return out
