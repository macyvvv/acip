from __future__ import annotations

from functools import lru_cache
import subprocess
from pathlib import Path


@lru_cache(maxsize=1)
def get_repo_root() -> Path:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True,
            text=True,
            check=True,
        )
        root = Path(result.stdout.strip())
        if root.exists():
            return root
    except Exception:
        pass

    current = Path(__file__).resolve()
    matches: list[Path] = []
    for candidate in current.parents:
        if (
            (candidate / ".git").exists()
            or (candidate / "pyproject.toml").exists()
            or (candidate / "README.md").exists()
        ):
            matches.append(candidate)
    if matches:
        return matches[-1]
    raise RuntimeError(f"Unable to locate repository root from {__file__}")
