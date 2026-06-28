#!/usr/bin/env python3
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


def main() -> int:
    required_paths = [
        ROOT / "system" / "orchestrator" / "repository_completion_marker.py",
        ROOT / "docs" / "current" / "REPOSITORY_COMPLETION_MARKER.md",
        ROOT / "system" / "runtime" / "handoff" / "latest.json",
        ROOT / "system" / "runtime" / "handoff" / "completion",
        ROOT / "specs" / "EP-0157",
        ROOT / "system" / "tests" / "test_repository_completion_marker.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0157 files:", ", ".join(missing))
        return 1
    print("EP-0157 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
