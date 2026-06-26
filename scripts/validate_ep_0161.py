#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0161-event-contract.md",
        ROOT / "orchestrator" / "event_contract.py",
        ROOT / "docs" / "current" / "EVENT_CONTRACT.md",
        ROOT / "specs" / "EP-0161",
        ROOT / "tests" / "test_event_contract.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0161 files:", ", ".join(missing))
        return 1
    print("EP-0161 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
