import os

from vcd.config import load_dotenv


def test_load_dotenv_parsing(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text(
        "# comment\n"
        "VCD_TEST_A=plain\n"
        "export VCD_TEST_B='quoted value'\n"
        'VCD_TEST_C="dq" \n'
        "VCD_TEST_D=   \n"            # empty -> skipped
        "VCD_TEST_E=with # trailing comment\n"
        "VCD_TEST_F=keep=equals\n"
        "VCD_TEST_G=“smart-quoted-key”\n",
        encoding="utf-8",
    )
    for k in ("VCD_TEST_A", "VCD_TEST_B", "VCD_TEST_C", "VCD_TEST_D", "VCD_TEST_E", "VCD_TEST_F", "VCD_TEST_G"):
        monkeypatch.delenv(k, raising=False)
    monkeypatch.setenv("VCD_TEST_A", "from-shell")
    loaded = load_dotenv(env)
    assert os.environ["VCD_TEST_A"] == "from-shell"  # shell wins
    assert os.environ["VCD_TEST_B"] == "quoted value"
    assert os.environ["VCD_TEST_C"] == "dq"
    assert "VCD_TEST_D" not in os.environ
    assert os.environ["VCD_TEST_E"] == "with"
    assert os.environ["VCD_TEST_F"] == "keep=equals"
    assert os.environ["VCD_TEST_G"] == "smart-quoted-key"
    assert set(loaded) == {"VCD_TEST_B", "VCD_TEST_C", "VCD_TEST_E", "VCD_TEST_F", "VCD_TEST_G"}
    assert load_dotenv(tmp_path / "missing.env") == {}
