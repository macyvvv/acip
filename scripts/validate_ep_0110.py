#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, "scripts/validate_ep_0109.py"],
    ]
    for command in commands:
        print("$ " + " ".join(command))
        subprocess.check_call(command, cwd=ROOT)

    required_paths = [
        ROOT / "orchestrator" / "autonomous_loop.py",
        ROOT / "tests" / "test_autonomous_loop.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing autonomous loop files:", ", ".join(missing))
        return 1
    print("EP-0110 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
