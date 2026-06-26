#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "repository_completion_marker.py",
        ROOT / "docs" / "current" / "REPOSITORY_COMPLETION_MARKER.md",
        ROOT / "runtime" / "handoff" / "latest.json",
        ROOT / "runtime" / "handoff" / "completion",
        ROOT / "specs" / "EP-0157",
        ROOT / "tests" / "test_repository_completion_marker.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0157 files:", ", ".join(missing))
        return 1
    print("EP-0157 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
