#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "docs" / "current" / "REPOSITORY_OS_V1_COMPLETION_REVIEW.md",
        ROOT / "docs" / "current" / "REPOSITORY_OS_V1_CAPABILITY_MAP.md",
        ROOT / "docs" / "current" / "REPOSITORY_OS_V1_RISK_REGISTER.md",
        ROOT / "docs" / "current" / "REPOSITORY_OS_V1_NEXT_PHASE_CRITERIA.md",
        ROOT / "runtime" / "reviews" / "repository_os_v1_completion_review.json",
        ROOT / "scripts" / "validate_ep_0143.py",
        ROOT / "tests" / "test_repository_os_v1_completion_review.py",
        ROOT / "specs" / "EP-0143",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0143 files:", ", ".join(missing))
        return 1
    print("EP-0143 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
