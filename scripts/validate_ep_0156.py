#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "contracts" / "AGENT_COMPLETION_CONTRACT.md",
        ROOT / "orchestrator" / "completion_protocol.py",
        ROOT / "docs" / "current" / "COMPLETION_PROTOCOL.md",
        ROOT / "specs" / "EP-0156",
        ROOT / "tests" / "test_completion_protocol.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0156 files:", ", ".join(missing))
        return 1
    print("EP-0156 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
