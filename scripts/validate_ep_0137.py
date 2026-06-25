#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "solution" / "requirements" / "schema" / "requirement.schema.json",
        ROOT / "orchestrator" / "requirement_intake.py",
        ROOT / "docs" / "current" / "REQUIREMENT_INTAKE.md",
        ROOT / "runtime" / "solution" / "requirements",
        ROOT / "specs" / "EP-0137",
        ROOT / "scripts" / "validate_ep_0137.py",
        ROOT / "tests" / "test_requirement_intake.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0137 files:", ", ".join(missing))
        return 1
    print("EP-0137 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
