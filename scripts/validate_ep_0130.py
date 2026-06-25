#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "execution_request.py",
        ROOT / "contracts" / "EXECUTION_REQUEST_CONTRACT.md",
        ROOT / "docs" / "current" / "EXECUTION_REQUEST.md",
        ROOT / "runtime" / "request" / "execution_request.json",
        ROOT / "specs" / "EP-0130",
        ROOT / "scripts" / "validate_ep_0130.py",
        ROOT / "tests" / "test_execution_request.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0130 files:", ", ".join(missing))
        return 1
    print("EP-0130 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
