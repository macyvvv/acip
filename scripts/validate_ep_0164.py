#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0164-event-to-queue-resolver.md",
        ROOT / "orchestrator" / "event_to_queue_resolver.py",
        ROOT / "docs" / "current" / "EVENT_TO_QUEUE_RESOLVER.md",
        ROOT / "specs" / "EP-0164",
        ROOT / "tests" / "test_event_to_queue_resolver.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0164 files:", ", ".join(missing))
        return 1
    print("EP-0164 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
