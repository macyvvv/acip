#!/usr/bin/env python3
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    commands = [
        [sys.executable, "scripts/specs/validate_ep_contract.py", "specs/EP-0107/ep_contract.yaml"],
    ]
    for command in commands:
        print("$ " + " ".join(command))
        subprocess.check_call(command, cwd=ROOT)

    output_contract = ROOT / "docs" / "current" / "CODEX_OUTPUT_CONTRACT.md"
    if not output_contract.exists():
        print("FAIL: missing docs/current/CODEX_OUTPUT_CONTRACT.md")
        return 1
    text = output_contract.read_text(encoding="utf-8")
    required_fragments = [
        "task_id:",
        "commit_sha:",
        "worktree_clean:",
        "validation_results:",
        "next_action:",
        "rerun_validation_conditions:",
    ]
    missing = [fragment for fragment in required_fragments if fragment not in text]
    if missing:
        print("# EP-0107 Output Contract Validation")
        for fragment in missing:
            print(f"FAIL: missing {fragment}")
        return 1
    print("EP-0107 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
