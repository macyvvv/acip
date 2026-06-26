#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "chatgpt_review_intake.py",
        ROOT / "docs" / "current" / "CHATGPT_REVIEW_INTAKE.md",
        ROOT / "runtime" / "handoff" / "latest.json",
        ROOT / "specs" / "EP-0158",
        ROOT / "tests" / "test_chatgpt_review_intake.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing EP-0158 files:", ", ".join(missing))
        return 1
    print("EP-0158 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
