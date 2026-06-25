#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "specification_generator.py",
        ROOT / "docs" / "current" / "SPECIFICATION_GENERATOR.md",
        ROOT / "runtime" / "solution" / "specifications" / "specification.json",
        ROOT / "specs" / "EP-0139",
        ROOT / "scripts" / "validate_ep_0139.py",
        ROOT / "tests" / "test_specification_generator.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0139 files:", ", ".join(missing))
        return 1
    print("EP-0139 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
