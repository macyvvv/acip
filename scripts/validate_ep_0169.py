#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0169-event-runtime-cli-entrance.md",
        ROOT / "orchestrator" / "event_runtime_cli.py",
        ROOT / "docs" / "current" / "EVENT_RUNTIME_CLI_ENTRANCE.md",
        ROOT / "specs" / "EP-0169",
        ROOT / "tests" / "test_event_runtime_cli.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0169 files:", ", ".join(missing))
        return 1
    print("EP-0169 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
