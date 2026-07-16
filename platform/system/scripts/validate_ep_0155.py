#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

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
sys.path.insert(0, str(ROOT / "platform"))


def main() -> int:
    required_paths = [
        ROOT / "platform" / "docs" / "current" / "GENERATED_ARTIFACT_REFRESH_COMMAND.md",
        ROOT / "platform" / "system" / "orchestrator" / "generated_artifact_refresh.py",
        ROOT / "platform" / "system" / "scripts" / "refresh_generated_artifacts.py",
        ROOT / "platform" / "system" / "tests" / "test_generated_artifact_refresh.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0155 files:", ", ".join(missing))
        return 1
    print("EP-0155 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
