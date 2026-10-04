from __future__ import annotations

import json
from pathlib import Path
from typing import Iterable, Iterator, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


def read_jsonl(path: str | Path) -> Iterator[dict]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield json.loads(line)


def write_jsonl(path: str | Path, rows: Iterable[dict | BaseModel], append: bool = False) -> int:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    n = 0
    with open(path, "a" if append else "w", encoding="utf-8") as f:
        for r in rows:
            if isinstance(r, BaseModel):
                r = r.model_dump(mode="json")
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
            n += 1
    return n


def load_models(path: str | Path, cls: Type[T]) -> list[T]:
    return [cls.model_validate(r) for r in read_jsonl(path)]
