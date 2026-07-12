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
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "archive" / "root_scaffolding_2026" / "queue" / "READY" / "EP-0177-root-migration-approval-gate.md",
        ROOT / "system" / "orchestrator" / "root_migration_approval_gate.py",
        ROOT / "docs" / "current" / "ROOT_MIGRATION_APPROVAL_GATE.md",
        ROOT / "specs" / "EP-0177",
        ROOT / "system" / "tests" / "test_root_migration_approval_gate.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0177 files:", ", ".join(missing))
        return 1
    print("EP-0177 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
