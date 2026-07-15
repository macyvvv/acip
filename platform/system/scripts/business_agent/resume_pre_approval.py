from __future__ import annotations

import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from system.core.execution_pre_approval_control import resume_pre_approval


def main() -> int:
    was_paused = resume_pre_approval(ROOT)
    print(f"was_paused={str(was_paused).lower()}")
    print("pre_approval_paused=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
