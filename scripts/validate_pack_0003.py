#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "docs" / "current" / "ISSUE_PARENT_CHILD_EXECUTION.md",
        ROOT / "docs" / "current" / "PACK_0003_EXECUTION_RECORD.md",
        ROOT / "runtime" / "handoff" / "completion" / "latest.json",
        ROOT / "packs" / "PACK-0003-generated-artifact-ssot" / "README.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing PACK-0003 files:", ", ".join(missing))
        return 1
    print("PACK-0003 validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
