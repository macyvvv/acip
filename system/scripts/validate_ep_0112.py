#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
def main() -> int:
    required_paths = [
        ROOT / "system" / "orchestrator" / "execution_kernel.py",
        ROOT / "docs" / "current" / "EXECUTION_KERNEL.md",
        ROOT / "system" / "scripts" / "validate_ep_0112.py",
        ROOT / "system" / "tests" / "test_execution_kernel.py",
        ROOT / "docs" / "ep" / "README_EP0112_EXECUTION_KERNEL.md",
        ROOT / "specs" / "EP-0112",
        ROOT / ".github" / "workflows" / "ep0112-execution-kernel.yml",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing execution kernel files:", ", ".join(missing))
        return 1
    print("EP-0112 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
