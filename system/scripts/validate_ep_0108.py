#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
import sys


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
ALLOWED_ROOT_MARKDOWN = {"README.md", "AGENTS.md"}
EXPECTED_PATHS = [
    ROOT / "docs" / "current" / "PROJECT.md",
    ROOT / "docs" / "current" / "STATE.md",
    ROOT / "docs" / "current" / "ROADMAP.md",
    ROOT / "docs" / "CHANGELOG.md",
    ROOT / "docs" / "packs" / "README_REPOSITORY_COMPLETE_PACK.md",
    ROOT / "docs" / "packs" / "README_AGENT_OS.md",
    ROOT / "docs" / "packs" / "README_RUNTIME_READINESS.md",
    ROOT / "docs" / "packs" / "README_GOVERNANCE.md",
    ROOT / "docs" / "packs" / "README_KNOWLEDGE_FACTORY.md",
    ROOT / "docs" / "manifests" / "MANIFEST.md",
    ROOT / "docs" / "manifests" / "MANIFEST_EP0100.md",
    ROOT / "docs" / "manifests" / "MANIFEST_EP0100_1.md",
    ROOT / "docs" / "manifests" / "MANIFEST_EP0100_2.md",
    ROOT / "docs" / "manifests" / "MANIFEST_EP0101.md",
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
