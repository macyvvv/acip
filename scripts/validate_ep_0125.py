#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "continuous_improvement_engine.py",
        ROOT / "docs" / "current" / "CONTINUOUS_IMPROVEMENT.md",
        ROOT / "runtime" / "improvement" / "improvement_candidates.json",
        ROOT / "runtime" / "improvement" / "IMPROVEMENT_CANDIDATES.md",
        ROOT / "specs" / "EP-0125",
        ROOT / "scripts" / "validate_ep_0125.py",
        ROOT / "tests" / "test_continuous_improvement_engine.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0125 files:", ", ".join(missing))
        return 1
    print("EP-0125 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
