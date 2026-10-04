from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[2]
_CURLY_QUOTES = str.maketrans({"“": '"', "”": '"', "‘": "'", "’": "'"})


def load_dotenv(path: str | Path | None = None, override: bool = False) -> dict[str, str]:
    """Read KEY=VALUE lines from .env into os.environ. Shell variables win unless override=True.

    Accepts `export KEY=value`, quoted values and `#` comments; empty values are skipped.
    """
    p = Path(path) if path else PROJECT_ROOT / ".env"
    loaded: dict[str, str] = {}
    if not p.exists():
        return loaded
    for raw in p.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export "):
            line = line[len("export "):]
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip()
        value = value.translate(_CURLY_QUOTES)  # keys pasted from chat / docs often carry smart quotes
        if value[:1] in ("'", '"') and value[-1:] == value[:1] and len(value) >= 2:
            value = value[1:-1]
        elif " #" in value:
            value = value.split(" #", 1)[0].rstrip()
        value = value.strip().strip("'\"")
        if not key or not value:
            continue
        if override or not os.environ.get(key):
            os.environ[key] = value
            loaded[key] = value
    return loaded


def load_yaml(path: str | Path) -> dict[str, Any]:
    with open(resolve(path), encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve(path: str | Path) -> Path:
    """Paths in configs are relative to the project root unless absolute."""
    p = Path(path)
    return p if p.is_absolute() else PROJECT_ROOT / p


def load_e0(path: str | Path = "configs/e0.yaml") -> dict[str, Any]:
    load_dotenv()
    cfg = load_yaml(path)
    cfg["paths"] = {k: resolve(v) for k, v in cfg["paths"].items()}
    return cfg


def load_models_cfg(path: str | Path = "configs/models.yaml") -> dict[str, Any]:
    load_dotenv()
    return load_yaml(path)


def env_or_none(name: str | None) -> str | None:
    return os.environ.get(name) if name else None
