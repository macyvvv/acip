#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "docs" / "current" / "WORKER_OUTPUT_CONTRACT.md",
        ROOT / "docs" / "current" / "WORKER_OUTPUT_SEMANTICS.md",
        ROOT / "orchestrator" / "output_semantics.py",
        ROOT / "specs" / "EP-0120",
        ROOT / "scripts" / "validate_ep_0120.py",
        ROOT / "tests" / "test_output_semantics.py",
        ROOT / "docs" / "ep" / "README_EP0120_WORKER_OUTPUT_SEMANTICS.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0120 files:", ", ".join(missing))
        return 1
    print("EP-0120 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
