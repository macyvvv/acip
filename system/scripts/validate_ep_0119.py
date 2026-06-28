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
        ROOT / "orchestrator" / "review_output_integration.py",
        ROOT / "docs" / "current" / "REVIEW_OUTPUT_INTEGRATION.md",
        ROOT / "docs" / "current" / "WORKER_OUTPUT_CONTRACT.md",
        ROOT / "docs" / "ep" / "README_EP0119_REVIEW_OUTPUT_INTEGRATION.md",
        ROOT / "specs" / "EP-0119",
        ROOT / "scripts" / "validate_ep_0119.py",
        ROOT / "tests" / "test_review_output_integration.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0119 files:", ", ".join(missing))
        return 1
    print("EP-0119 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
