#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "docs" / "current" / "WORKTREE_CLEANLINESS_GATE.md",
        ROOT / "orchestrator" / "worktree_cleanliness_gate.py",
        ROOT / "tests" / "test_worktree_cleanliness_gate.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0154 files:", ", ".join(missing))
        return 1
    print("EP-0154 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
