#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required = [
        ROOT / "queue" / "READY" / "ep-0204-codex-cli-execution-adapter.md",
        ROOT / "specs" / "EP-0204" / "IMPLEMENTATION_SPEC.md",
        ROOT / "specs" / "EP-0204" / "MANIFEST.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing EP-0204 files:", ", ".join(missing))
        return 1
    print("EP-0204 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
