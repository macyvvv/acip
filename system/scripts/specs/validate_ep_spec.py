#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
def main() -> int:
    spec_dir = ROOT / "specs" / "EP-0102"
    required = [
        "IMPLEMENTATION_SPEC.md",
        "FILE_CHANGESET.md",
        "ACCEPTANCE_TEST.md",
        "VALIDATION.md",
        "ROLLBACK.md",
        "MANIFEST.md",
        "CODEX_PROMPT.md",
    ]
    missing = [name for name in required if not (spec_dir / name).is_file()]
    if missing:
        print("# Spec Validation")
        for name in missing:
            print(f"FAIL: missing {name}")
        return 1
    print("# Spec Validation")
    print("Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
