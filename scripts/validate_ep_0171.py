#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0171-approval-hold-workflow.md",
        ROOT / "orchestrator" / "approval_hold_workflow.py",
        ROOT / "docs" / "current" / "APPROVAL_HOLD_WORKFLOW.md",
        ROOT / "specs" / "EP-0171",
        ROOT / "tests" / "test_approval_hold_workflow.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0171 files:", ", ".join(missing))
        return 1
    print("EP-0171 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
