"""configs/train_e2c.yaml (E2c amendment 1) differs from configs/train.yaml in train.num_epochs only."""

from vcd.train.sft import load_train_config


def _flat(d, prefix=""):
    out = {}
    for k, v in d.items():
        key = f"{prefix}{k}"
        if isinstance(v, dict):
            out.update(_flat(v, key + "."))
        else:
            out[key] = v
    return out


def test_e2c_config_changes_only_num_epochs():
    base = _flat(load_train_config("configs/train.yaml"))
    e2c = _flat(load_train_config("configs/train_e2c.yaml"))
    assert set(base) == set(e2c)
    diff = {k for k in base if base[k] != e2c[k] and k != "config_path"}  # the loader records its own path
    assert diff == {"train.num_epochs"}
    assert base["train.num_epochs"] == 3 and e2c["train.num_epochs"] == 5
