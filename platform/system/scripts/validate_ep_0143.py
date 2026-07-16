#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    matches: list[Path] = []
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            matches.append(candidate)
    if matches:
        return matches[-1]
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT / "platform"))


def main() -> int:
    required_paths = [
        ROOT / "platform" / "docs" / "current" / "REPOSITORY_OS_V1_COMPLETION_REVIEW.md",
        ROOT / "platform" / "docs" / "current" / "REPOSITORY_OS_V1_CAPABILITY_MAP.md",
        ROOT / "platform" / "docs" / "current" / "REPOSITORY_OS_V1_RISK_REGISTER.md",
        ROOT / "platform" / "docs" / "current" / "REPOSITORY_OS_V1_NEXT_PHASE_CRITERIA.md",
        ROOT / "platform" / "system" / "runtime" / "reviews" / "repository_os_v1_completion_review.json",
        ROOT / "platform" / "system" / "scripts" / "validate_ep_0143.py",
        ROOT / "platform" / "system" / "tests" / "test_repository_os_v1_completion_review.py",
        ROOT / "platform" / "specs" / "EP-0143",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0143 files:", ", ".join(missing))
        return 1
    print("EP-0143 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
