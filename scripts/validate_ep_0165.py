#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0165-event-runtime-dry-run.md",
        ROOT / "orchestrator" / "event_runtime_dry_run.py",
        ROOT / "docs" / "current" / "EVENT_RUNTIME_DRY_RUN.md",
        ROOT / "runtime" / "event_runtime",
        ROOT / "specs" / "EP-0165",
        ROOT / "tests" / "test_event_runtime_dry_run.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0165 files:", ", ".join(missing))
        return 1
    print("EP-0165 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
