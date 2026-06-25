#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "generated_artifact_manager.py",
        ROOT / "docs" / "current" / "GENERATED_ARTIFACTS.md",
        ROOT / "runtime" / "generated_artifacts",
        ROOT / "specs" / "EP-0123",
        ROOT / "scripts" / "validate_ep_0123.py",
        ROOT / "tests" / "test_generated_artifact_manager.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0123 files:", ", ".join(missing))
        return 1
    print("EP-0123 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
