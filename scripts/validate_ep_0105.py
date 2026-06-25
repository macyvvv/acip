#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, "scripts/workers/validate_worker_contracts.py"],
        [sys.executable, "scripts/specs/validate_spec_lifecycle.py"],
        [sys.executable, "scripts/specs/validate_ep_contract.py", "specs/EP-0105/ep_contract.yaml"],
    ]
    for command in commands:
        print("$ " + " ".join(command))
        subprocess.check_call(command, cwd=ROOT)
    print("EP-0105 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
