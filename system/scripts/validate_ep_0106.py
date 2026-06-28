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
        [sys.executable, "system/scripts/specs/validate_ep_contract.py", "specs/EP-0106/ep_contract.yaml"],
        [sys.executable, "system/scripts/specs/validate_spec_lifecycle.py"],
    ]
    for command in commands:
        print("$ " + " ".join(command))
        subprocess.check_call(command, cwd=ROOT)
    print("EP-0106 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
