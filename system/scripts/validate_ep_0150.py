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
        ROOT / "queue" / "READY" / "EP-0150-human-removal-validation.md",
        ROOT / "orchestrator" / "human_removal_validation.py",
        ROOT / "docs" / "current" / "HUMAN_REMOVAL_VALIDATION.md",
        ROOT / "runtime" / "validation" / "human_removal_validation.json",
        ROOT / "tests" / "test_human_removal_validation.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0150 files:", ", ".join(missing))
        return 1
    print("EP-0150 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
