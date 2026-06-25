#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "contracts" / "REPOSITORY_LAYOUT_CONTRACT.md",
        ROOT / "docs" / "current" / "CANONICAL_REPOSITORY_LAYOUT.md",
        ROOT / "docs" / "current" / "ROOT_ALLOWLIST.md",
        ROOT / "docs" / "current" / "LAYOUT_MIGRATION_RULES.md",
        ROOT / "scripts" / "hygiene" / "validate_repository_layout.py",
        ROOT / "docs" / "ep" / "README_EP0121_REPOSITORY_LAYOUT_CANONICALIZATION.md",
        ROOT / "specs" / "EP-0121",
        ROOT / "tests" / "test_repository_layout.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0121 files:", ", ".join(missing))
        return 1

    from scripts.hygiene.validate_repository_layout import validate_repository_layout

    violations = validate_repository_layout(report_only=True)
    if violations:
        print("WARN: root allowlist violations:", ", ".join(violations))
    else:
        print("EP-0121 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
