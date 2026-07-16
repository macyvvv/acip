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
        ROOT / "platform" / "contracts" / "REPOSITORY_LAYOUT_CONTRACT.md",
        ROOT / "platform" / "docs" / "current" / "CANONICAL_REPOSITORY_LAYOUT.md",
        ROOT / "platform" / "docs" / "current" / "ROOT_ALLOWLIST.md",
        ROOT / "platform" / "docs" / "current" / "LAYOUT_MIGRATION_RULES.md",
        ROOT / "platform" / "system" / "scripts" / "hygiene" / "validate_repository_layout.py",
        ROOT / "platform" / "docs" / "ep" / "EP_LEGACY_BUNDLE.md",
        ROOT / "platform" / "specs" / "EP-0121",
        ROOT / "platform" / "system" / "tests" / "test_repository_layout.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0121 files:", ", ".join(missing))
        return 1

    from system.scripts.hygiene.validate_repository_layout import validate_repository_layout

    violations = validate_repository_layout(report_only=True)
    if violations:
        print("WARN: root allowlist violations:", ", ".join(violations))
    else:
        print("EP-0121 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
