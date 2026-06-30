#!/usr/bin/env python3
from __future__ import annotations

import json
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
    required = [
        ROOT / "docs" / "current" / "REPOSITORY_CONSTITUTION.md",
        ROOT / "contracts" / "REPOSITORY_CONSTITUTION_CONTRACT.md",
        ROOT / "system" / "runtime" / "repository_constitution" / "constitution.json",
        ROOT / "system" / "tests" / "test_repository_constitution.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing repository constitution files:", ", ".join(missing))
        return 1

    payload = json.loads((ROOT / "system" / "runtime" / "repository_constitution" / "constitution.json").read_text(encoding="utf-8"))
    if payload.get("status") != "stable":
        print("FAIL: invalid constitution status")
        return 1
    if len(payload.get("principles", [])) != 10:
        print("FAIL: expected 10 principles")
        return 1
    print("Repository constitution validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
