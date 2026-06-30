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
sys.path.insert(0, str(ROOT))


def main() -> int:
    required = [
        ROOT / "docs" / "current" / "REPOSITORY_OS_V2_RELEASE.md",
        ROOT / "docs" / "current" / "REPOSITORY_OS_V2_ARCHITECTURE.md",
        ROOT / "system" / "runtime" / "releases" / "repository_os_v2.json",
        ROOT / "system" / "runtime" / "releases" / "repository_os_v2.md",
        ROOT / "system" / "tests" / "test_repository_os_v2_release.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing repository os v2 release files:", ", ".join(missing))
        return 1
    payload = json.loads((ROOT / "system" / "runtime" / "releases" / "repository_os_v2.json").read_text(encoding="utf-8"))
    if payload.get("status") != "frozen":
        print("FAIL: release is not frozen")
        return 1
    print("Repository OS v2 release validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
