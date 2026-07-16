#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    matches: list[Path] = []
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            matches.append(candidate)
    if matches:
        return matches[-1]
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ALLOWED_ROOT_MARKDOWN = {"README.md", "AGENTS.md", "CLAUDE.md"}
EXPECTED_PATHS = [
    ROOT / "platform" / "docs" / "current" / "PROJECT.md",
    ROOT / "platform" / "docs" / "current" / "STATE.md",
    ROOT / "platform" / "docs" / "current" / "ROADMAP.md",
    ROOT / "platform" / "docs" / "CHANGELOG.md",
    ROOT / "platform" / "docs" / "packs" / "README.md",
    ROOT / "platform" / "docs" / "packs" / "PACKS_DOCS_LEGACY_BUNDLE.md",
    ROOT / "platform" / "docs" / "manifests" / "MANIFEST_LEGACY_BUNDLE.md",
]


def main() -> int:
    root_markdown = sorted(path.name for path in ROOT.glob("*.md"))
    unexpected = [name for name in root_markdown if name not in ALLOWED_ROOT_MARKDOWN]
    missing = [str(path.relative_to(ROOT)) for path in EXPECTED_PATHS if not path.is_file()]

    print("EP-0108 Repository Root Hygiene")
    if unexpected:
        print("FAIL: unexpected root markdown files:", ", ".join(unexpected))
    if missing:
        print("FAIL: missing moved documents:", ", ".join(missing))
    if unexpected or missing:
        return 1
    print("EP-0108 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
