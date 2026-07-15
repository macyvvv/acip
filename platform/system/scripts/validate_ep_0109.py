#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")

ROOT = _resolve_repo_root()
def main() -> int:
    commands = [
        [sys.executable, "system/scripts/validate_ep_0108.py"],
    ]
    for command in commands:
        print("$ " + " ".join(command))
        subprocess.check_call(command, cwd=ROOT)

    queue_state = (ROOT / "docs" / "current" / "QUEUE_STATE.md").read_text(encoding="utf-8")
    required = ["active_ep: EP-0108", "next_ep: EP-0109"]
    missing = [item for item in required if item not in queue_state]
    if missing:
        print("FAIL: missing queue state markers:", ", ".join(missing))
        return 1

    print("EP-0109 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
