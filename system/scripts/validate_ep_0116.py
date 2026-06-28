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
        ROOT / "docs" / "current" / "ROOT_HYGIENE_REPORT.md",
        ROOT / "docs" / "current" / "CODE_QUALITY_BASELINE.md",
        ROOT / "docs" / "current" / "REFACTORING_QUEUE.md",
        ROOT / "contracts" / "ROOT_HYGIENE_CONTRACT.md",
        ROOT / "contracts" / "CODE_QUALITY_CONTRACT.md",
        ROOT / "scripts" / "hygiene" / "audit_repository_root.py",
        ROOT / "scripts" / "hygiene" / "audit_code_quality.py",
        ROOT / "docs" / "ep" / "README_EP0116_REPOSITORY_HYGIENE_CODE_QUALITY.md",
        ROOT / "specs" / "EP-0116",
        ROOT / ".github" / "workflows" / "ep0116-repository-hygiene-code-quality.yml",
        ROOT / "tests" / "test_repository_hygiene.py",
        ROOT / "tests" / "test_code_quality_baseline.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing repository hygiene files:", ", ".join(missing))
        return 1
    print("EP-0116 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
