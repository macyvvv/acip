#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0163-completion-marker-event-intake.md",
        ROOT / "orchestrator" / "completion_marker_event_intake.py",
        ROOT / "docs" / "current" / "COMPLETION_MARKER_EVENT_INTAKE.md",
        ROOT / "specs" / "EP-0163",
        ROOT / "tests" / "test_completion_marker_event_intake.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0163 files:", ", ".join(missing))
        return 1
    print("EP-0163 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
