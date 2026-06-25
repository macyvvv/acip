#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def main() -> int:
    required = [
        ROOT / "specs" / "active" / "README.md",
        ROOT / "specs" / "completed" / "README.md",
        ROOT / "specs" / "archived" / "README.md",
    ]
    failures = [path.relative_to(ROOT).as_posix() for path in required if not path.exists()]
    if failures:
        print("# Spec Lifecycle Validation")
        for failure in failures:
            print(f"FAIL: {failure}")
        return 1
    print("# Spec Lifecycle Validation")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
