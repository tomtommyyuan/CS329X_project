"""Second-base configs (configs/train_smollm3_3b*.yaml) differ from their parents in student_model / student_model_short only.

Protocol: the second student base family (docs/supplemental_experiments.md §2 row 1) runs the SAME frozen recipe as Qwen3-4B;
only the model name and the runs/ namespace change. These tests pin that, and that every student_model_short is a legal run-id
prefix (RUN_ID_RE takes `[^.]+` before the first dot, so a short with a dot such as "llama-3.2-3b" would break the run id).
"""

from pathlib import Path

import pytest

from vcd.train.data import RUN_ID_RE
from vcd.train.sft import load_train_config

ROOT = Path(__file__).resolve().parents[1]
BASE2_MODEL = "HuggingFaceTB/SmolLM3-3B-Base"
BASE2_SHORT = "smollm3-3b"
MODEL_KEYS = {"student_model", "student_model_short"}


def _flat(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flat(v, key + "."))
        else:
            out[key] = v
    return out


def _diff(parent: str, child: str, profile: str = "default") -> tuple[dict, dict, set]:
    a = _flat(load_train_config(parent, profile=profile))
    b = _flat(load_train_config(child, profile=profile))
    assert set(a) == set(b), f"{child} adds or drops keys relative to {parent}: {set(a) ^ set(b)}"
    return a, b, {k for k in a if a[k] != b[k] and k != "config_path"}  # the loader records its own path


@pytest.mark.parametrize("parent,child", [("configs/train.yaml", "configs/train_smollm3_3b.yaml"), ("configs/train_e2c.yaml", "configs/train_smollm3_3b_e2c.yaml")])
def test_base2_config_changes_only_the_model(parent, child):
    a, b, diff = _diff(parent, child)
    assert diff == MODEL_KEYS, f"{child} must differ from {parent} in exactly {MODEL_KEYS}, got {diff}"
    assert a["student_model"] == "Qwen/Qwen3-4B-Base" and a["student_model_short"] == "qwen3-4b"
    assert b["student_model"] == BASE2_MODEL and b["student_model_short"] == BASE2_SHORT
    # the CPU smoke profile is untouched: with `tiny` both files load to the same SmolLM2-135M settings
    _, _, tiny_diff = _diff(parent, child, profile="tiny")
    assert tiny_diff == set(), f"the tiny profile of {child} drifted from {parent}: {tiny_diff}"


def test_base2_e2c_config_is_the_e2c_recipe():
    """train_smollm3_3b_e2c = train.yaml + the E2c 5-epoch amendment + the model swap, nothing else."""
    a, b, diff = _diff("configs/train.yaml", "configs/train_smollm3_3b_e2c.yaml")
    assert diff == MODEL_KEYS | {"train.num_epochs"}
    assert a["train.num_epochs"] == 3 and b["train.num_epochs"] == 5
    # and the two second-base configs differ from each other in num_epochs only
    _, _, diff2 = _diff("configs/train_smollm3_3b.yaml", "configs/train_smollm3_3b_e2c.yaml")
    assert diff2 == {"train.num_epochs"}


@pytest.mark.parametrize("config", sorted(str(p.relative_to(ROOT)) for p in (ROOT / "configs").glob("train*.yaml")))
def test_student_short_is_a_legal_run_id_prefix(config):
    """runs/{short}/{teacher}_{version}_s{seed} must parse as a protocol run id for every training config (docs/05 §3.3)."""
    for profile in ("default", "tiny"):
        short = load_train_config(config, profile=profile)["student_model_short"]
        assert "." not in short and "/" not in short, f"{config} ({profile}): {short!r} is not a legal run-id prefix"
        m = RUN_ID_RE.match(f"{short}.gpt4o_O_s1")
        assert m is not None and m["student"] == short, f"{config} ({profile}): run id {short}.gpt4o_O_s1 does not parse"
