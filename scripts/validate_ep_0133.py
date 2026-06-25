#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "execution_journal.py",
        ROOT / "docs" / "current" / "EXECUTION_JOURNAL.md",
        ROOT / "runtime" / "journal" / "execution_journal.jsonl",
        ROOT / "specs" / "EP-0133",
        ROOT / "scripts" / "validate_ep_0133.py",
        ROOT / "tests" / "test_execution_journal.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0133 files:", ", ".join(missing))
        return 1
    print("EP-0133 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
