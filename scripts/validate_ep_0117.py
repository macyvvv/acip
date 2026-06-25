#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "contracts" / "REFACTORING_GOVERNANCE_CONTRACT.md",
        ROOT / "docs" / "current" / "REFACTORING_GOVERNANCE_GATE.md",
        ROOT / "docs" / "current" / "REFACTORING_DECISION_RECORD.md",
        ROOT / "scripts" / "hygiene" / "validate_refactoring_governance.py",
        ROOT / "docs" / "ep" / "README_EP0117_REFACTORING_GOVERNANCE.md",
        ROOT / "specs" / "EP-0117",
        ROOT / ".github" / "workflows" / "ep0117-refactoring-governance.yml",
        ROOT / "tests" / "test_refactoring_governance.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing refactoring governance files:", ", ".join(missing))
        return 1

    from scripts.hygiene.validate_refactoring_governance import validate_refactoring_governance

    validate_refactoring_governance()
    print("EP-0117 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
