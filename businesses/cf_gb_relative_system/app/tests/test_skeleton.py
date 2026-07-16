from __future__ import annotations

from pathlib import Path


APP_ROOT = Path(__file__).resolve().parents[1]
BUSINESS_ROOT = APP_ROOT.parent


def test_env_example_exists_and_has_no_secret_values() -> None:
    env_example = BUSINESS_ROOT / ".env.example"
    lines = env_example.read_text(encoding="utf-8").splitlines()

    assert env_example.exists()
    assert any(line.startswith("APP_ENV=development") for line in lines)
    assert all("secret" not in line.lower() for line in lines)
    assert all("token=" not in line.lower() for line in lines)


def test_dependency_lock_exists() -> None:
    lockfile = APP_ROOT / "requirements.lock"

    assert lockfile.exists()
    assert "no third-party runtime dependencies" in lockfile.read_text(encoding="utf-8")


def test_pyproject_declares_pytest_collection() -> None:
    pyproject = APP_ROOT / "pyproject.toml"
    text = pyproject.read_text(encoding="utf-8")

    assert pyproject.exists()
    assert 'testpaths = ["tests"]' in text
