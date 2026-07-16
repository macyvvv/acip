#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    # Prefer the outermost git root in case a nested .git directory exists.
    git_matches: list[Path] = []
    for candidate in current.parents:
        if (candidate / ".git").exists():
            git_matches.append(candidate)
    if git_matches:
        return git_matches[-1]
    for candidate in current.parents:
        if (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT / "platform"))


def main() -> int:
    required_paths = [
        ROOT / "platform" / "docs" / "current" / "ROOT_HYGIENE_REPORT.md",
        ROOT / "platform" / "docs" / "current" / "CODE_QUALITY_BASELINE.md",
        ROOT / "platform" / "docs" / "current" / "REFACTORING_QUEUE.md",
        ROOT / "platform" / "contracts" / "ROOT_HYGIENE_CONTRACT.md",
        ROOT / "platform" / "contracts" / "CODE_QUALITY_CONTRACT.md",
        ROOT / "platform" / "system" / "scripts" / "hygiene" / "audit_repository_root.py",
        ROOT / "platform" / "system" / "scripts" / "hygiene" / "audit_code_quality.py",
        ROOT / "platform" / "docs" / "ep" / "EP_LEGACY_BUNDLE.md",
        ROOT / "platform" / "specs" / "EP-0116",
        ROOT / ".github" / "workflows" / "ep0116-repository-hygiene-code-quality.yml",
        ROOT / "platform" / "system" / "tests" / "test_repository_hygiene.py",
        ROOT / "platform" / "system" / "tests" / "test_code_quality_baseline.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing repository hygiene files:", ", ".join(missing))
        return 1
    print("EP-0116 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
