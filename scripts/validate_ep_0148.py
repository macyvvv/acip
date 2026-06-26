#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0148-next-work-resolver.md",
        ROOT / "orchestrator" / "next_work_resolver.py",
        ROOT / "docs" / "current" / "NEXT_WORK_RESOLVER.md",
        ROOT / "runtime" / "queue" / "next_work.json",
        ROOT / "tests" / "test_next_work_resolver.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0148 files:", ", ".join(missing))
        return 1
    print("EP-0148 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
