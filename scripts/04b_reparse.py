"""Re-parse stored teacher responses after a parser change (category / letter / choice_action / p_x).
Raw text and logprob-derived p_letters are kept; only the derived fields are recomputed.
  python scripts/04b_reparse.py            # all files in data/teacher
"""

from __future__ import annotations

import argparse
from collections import Counter

from vcd.config import load_e0
from vcd.io import load_models, write_jsonl
from vcd.schemas import Prompt, TeacherResponse
from vcd.teacher.parse import p_x_from_letters, parse_answer


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/e0.yaml")
    ap.add_argument("--drop-orphans", action="store_true", help="drop rows whose prompt_id is not in the current prompts file")
    args = ap.parse_args()
    cfg = load_e0(args.config)
    prompts = {p.prompt_id: p for p in load_models(cfg["paths"]["prompts"], Prompt)}
    for path in sorted(cfg["paths"]["teacher_dir"].glob("*.jsonl")):
        rows = load_models(path, TeacherResponse)
        changed = Counter()
        kept = []
        for r in rows:
            p = prompts.get(r.prompt_id)
            if p is None:  # orphan from an earlier prompt set: leave untouched or drop
                changed["orphan"] += 1
                if not args.drop_orphans:
                    kept.append(r)
                continue
            cat, letter = parse_answer(r.raw)
            choice = p.letter_to_action.get(letter) if letter else None
            p_x = p_x_from_letters(r.p_letters, p.letter_to_action) if r.p_letters else r.p_x
            if (cat, letter, choice) != (r.category, r.letter, r.choice_action):
                changed[f"{r.category}->{cat}"] += 1
            r.category, r.letter, r.choice_action, r.p_x = cat, letter, choice, p_x
            kept.append(r)
        write_jsonl(path, kept)
        print(f"{path.name}: {len(rows)} -> {len(kept)} rows, changes: {dict(changed) or 'none'}")


if __name__ == "__main__":
    main()
