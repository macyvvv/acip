#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "queue" / "READY" / "EP-0172-external-trigger-dry-run-validation.md",
        ROOT / "orchestrator" / "external_trigger_dry_run_validation.py",
        ROOT / "docs" / "current" / "EXTERNAL_TRIGGER_DRY_RUN_VALIDATION.md",
        ROOT / "specs" / "EP-0172",
        ROOT / "tests" / "test_external_trigger_dry_run_validation.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0172 files:", ", ".join(missing))
        return 1
    print("EP-0172 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
