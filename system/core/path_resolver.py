from __future__ import annotations

from functools import lru_cache
from pathlib import Path


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (
            (candidate / ".git").exists()
            or (candidate / "pyproject.toml").exists()
            or (candidate / "README.md").exists()
        ):
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")
