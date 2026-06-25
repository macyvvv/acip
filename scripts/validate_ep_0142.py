#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "solution_development_runtime.py",
        ROOT / "docs" / "current" / "SOLUTION_DEVELOPMENT_RUNTIME.md",
        ROOT / "runtime" / "solution" / "solution_runtime_state" / "solution_runtime_state.json",
        ROOT / "specs" / "EP-0142",
        ROOT / "scripts" / "validate_ep_0142.py",
        ROOT / "tests" / "test_solution_development_runtime.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0142 files:", ", ".join(missing))
        return 1
    print("EP-0142 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
