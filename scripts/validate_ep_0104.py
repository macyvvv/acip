#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, "scripts/specs/validate_ep_contract.py"],
        [sys.executable, "scripts/specs/load_active_ep_contract.py"],
    ]
    for command in commands:
        print("$ " + " ".join(command))
        subprocess.check_call(command, cwd=ROOT)
    print("EP-0104 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
