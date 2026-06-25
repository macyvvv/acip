#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "human_approval_gate.py",
        ROOT / "docs" / "current" / "HUMAN_APPROVAL_GATE.md",
        ROOT / "runtime" / "approval" / "approval_state.json",
        ROOT / "specs" / "EP-0126",
        ROOT / "scripts" / "validate_ep_0126.py",
        ROOT / "tests" / "test_human_approval_gate.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0126 files:", ", ".join(missing))
        return 1
    print("EP-0126 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
