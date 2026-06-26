#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "docs" / "current" / "VALIDATION_READ_ONLY_MODE.md",
        ROOT / "scripts" / "validate_all.py",
        ROOT / "tests" / "test_validate_all_read_only.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0152 files:", ", ".join(missing))
        return 1
    print("EP-0152 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
