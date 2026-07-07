from __future__ import annotations

from pathlib import Path

import pytest

from system.core.dotenv import load_dotenv


def test_load_dotenv_parses_key_value_pairs(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("SOMIA_TEST_KEY", raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text(
        "\n".join(
            [
                "# a comment",
                "",
                'SOMIA_TEST_KEY="abc123"',
                "SOMIA_TEST_OTHER=plain-value",
            ]
        ),
        encoding="utf-8",
    )
    loaded = load_dotenv(env_path)
    assert loaded == {"SOMIA_TEST_KEY": "abc123", "SOMIA_TEST_OTHER": "plain-value"}
    import os

    assert os.environ["SOMIA_TEST_KEY"] == "abc123"


def test_load_dotenv_missing_file_returns_empty(tmp_path: Path) -> None:
    assert load_dotenv(tmp_path / "does_not_exist.env") == {}


def test_load_dotenv_does_not_override_real_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("SOMIA_TEST_KEY", "from-shell")
    env_path = tmp_path / ".env"
    env_path.write_text("SOMIA_TEST_KEY=from-file\n", encoding="utf-8")
    load_dotenv(env_path)
    import os

    assert os.environ["SOMIA_TEST_KEY"] == "from-shell"


def test_load_dotenv_last_duplicate_key_wins(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    # Regression: appending an updated value below an old/empty placeholder
    # line for the same key must not be shadowed by the earlier line.
    monkeypatch.delenv("SOMIA_TEST_KEY", raising=False)
    env_path = tmp_path / ".env"
    env_path.write_text("SOMIA_TEST_KEY=\nSOMIA_TEST_KEY=real-value\n", encoding="utf-8")
    loaded = load_dotenv(env_path)
    assert loaded["SOMIA_TEST_KEY"] == "real-value"
    import os

    assert os.environ["SOMIA_TEST_KEY"] == "real-value"
