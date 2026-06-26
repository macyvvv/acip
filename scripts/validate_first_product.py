#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required = [
        ROOT / "docs" / "current" / "FIRST_PRODUCT_ROADMAP.md",
        ROOT / "docs" / "current" / "FIRST_PRODUCT_WBS.md",
        ROOT / "docs" / "current" / "BACKGROUND_SYSTEM_ARCHITECTURE.md",
        ROOT / "runtime" / "planning" / "first_product.json",
        ROOT / "tests" / "test_first_product.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing first product files:", ", ".join(missing))
        return 1
    payload = json.loads((ROOT / "runtime" / "planning" / "first_product.json").read_text(encoding="utf-8"))
    if payload.get("objective") != "Use Repository OS v2 as the operating system for the first production outcome.":
        print("FAIL: unexpected objective")
        return 1
    print("First product validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
