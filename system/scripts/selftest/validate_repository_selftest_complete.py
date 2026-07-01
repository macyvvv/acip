#!/usr/bin/env python3
from __future__ import annotations

from importlib import util
from pathlib import Path
import sys

def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
SELFTEST_V2 = ROOT / "system" / "scripts" / "selftest_v2"
if str(SELFTEST_V2) not in sys.path:
    sys.path.insert(0, str(SELFTEST_V2))

MODULE_PATH = SELFTEST_V2 / "validate_semantic_selftest.py"
SPEC = util.spec_from_file_location("system.scripts.selftest_v2.validate_semantic_selftest", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"Unable to load semantic selftest from {MODULE_PATH}")
MODULE = util.module_from_spec(SPEC)
sys.modules[SPEC.name] = MODULE
SPEC.loader.exec_module(MODULE)
main = MODULE.main

if __name__ == "__main__":
    raise SystemExit(main())
