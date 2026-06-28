#!/usr/bin/env python3
from pathlib import Path
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
V2 = ROOT / "scripts" / "selftest_v2"
if str(V2) not in sys.path:
    sys.path.insert(0, str(V2))

from validate_semantic_selftest import main

if __name__ == "__main__":
    raise SystemExit(main())
