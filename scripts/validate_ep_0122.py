#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "repository_governor.py",
        ROOT / "docs" / "current" / "REPOSITORY_GOVERNOR.md",
        ROOT / "docs" / "current" / "GOVERNOR_STATE.md",
        ROOT / "runtime" / "governor" / "governor_recommendations.json",
        ROOT / "runtime" / "governor" / "GOVERNOR_RECOMMENDATIONS.md",
        ROOT / "specs" / "EP-0122",
        ROOT / "scripts" / "validate_ep_0122.py",
        ROOT / "tests" / "test_repository_governor.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0122 files:", ", ".join(missing))
        return 1
    print("EP-0122 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
