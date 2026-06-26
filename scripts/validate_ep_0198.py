#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required = [
        ROOT / "queue" / "READY" / "ep-0198-parking-lot-and-blocked-candidate-handling.md",
        ROOT / "specs" / "EP-0198" / "IMPLEMENTATION_SPEC.md",
        ROOT / "specs" / "EP-0198" / "MANIFEST.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing EP-0198 files:", ", ".join(missing))
        return 1
    print("EP-0198 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
