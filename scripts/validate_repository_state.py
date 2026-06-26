#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required = [
        ROOT / "contracts" / "REPOSITORY_STATE_CONTRACT.md",
        ROOT / "docs" / "current" / "REPOSITORY_STATE_PROJECTION.md",
        ROOT / "runtime" / "repository_state" / "latest.json",
        ROOT / "runtime" / "repository_state" / "latest.md",
        ROOT / "orchestrator" / "repository_state_builder.py",
        ROOT / "tests" / "test_repository_state_builder.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing repository state projection files:", ", ".join(missing))
        return 1
    payload = json.loads((ROOT / "runtime" / "repository_state" / "latest.json").read_text(encoding="utf-8"))
    for key in ["active_pack", "active_ep", "latest_completion", "queue_status", "validation_status", "pytest_status", "worktree_state", "approval_required", "pending_review_items", "repository_health", "runtime_health", "next_action", "source_artifacts"]:
        if key not in payload:
            print(f"FAIL: missing field {key}")
            return 1
    print("Repository state projection validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
