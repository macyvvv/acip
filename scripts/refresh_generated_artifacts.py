#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from orchestrator.generated_artifact_refresh import GeneratedArtifactRefresh


def main() -> int:
    result = GeneratedArtifactRefresh(ROOT).refresh()
    print(f"validation_success={str(result.validation_success).lower()}")
    print(f"generated_artifact_count={result.generated_artifact_count}")
    return 0 if result.validation_success else 1


if __name__ == "__main__":
    raise SystemExit(main())
