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
        ROOT / "docs" / "current" / "GOVERNOR_STATE.md",
        ROOT / "docs" / "current" / "GOVERNOR_RECOMMENDATION_SSOT.md",
        ROOT / "system" / "runtime" / "governor" / "governor_recommendations.json",
        ROOT / "system" / "runtime" / "governor" / "GOVERNOR_RECOMMENDATIONS.md",
        ROOT / "system" / "orchestrator" / "repository_governor.py",
        ROOT / "specs" / "EP-0129",
        ROOT / "system" / "scripts" / "validate_ep_0129.py",
        ROOT / "system" / "tests" / "test_repository_governor.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0129 files:", ", ".join(missing))
        return 1
    print("EP-0129 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
