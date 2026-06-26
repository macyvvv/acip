#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0173-root-inventory-and-classification.md",
        ROOT / "orchestrator" / "root_inventory.py",
        ROOT / "docs" / "current" / "ROOT_INVENTORY_AND_CLASSIFICATION.md",
        ROOT / "specs" / "EP-0173",
        ROOT / "tests" / "test_root_inventory.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0173 files:", ", ".join(missing))
        return 1
    print("EP-0173 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
