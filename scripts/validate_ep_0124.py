#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "repository_state_manager.py",
        ROOT / "docs" / "current" / "REPOSITORY_STATE.md",
        ROOT / "runtime" / "repository_state" / "repository_state.json",
        ROOT / "specs" / "EP-0124",
        ROOT / "scripts" / "validate_ep_0124.py",
        ROOT / "tests" / "test_repository_state_manager.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0124 files:", ", ".join(missing))
        return 1
    print("EP-0124 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
