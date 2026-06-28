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

from system.orchestrator.generated_artifact_refresh import GeneratedArtifactRefresh


def main() -> int:
    result = GeneratedArtifactRefresh(ROOT).refresh()
    print(f"validation_success={str(result.validation_success).lower()}")
    print(f"generated_artifact_count={result.generated_artifact_count}")
    return 0 if result.validation_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
