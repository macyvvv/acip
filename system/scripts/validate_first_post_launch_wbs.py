#!/usr/bin/env python3
from __future__ import annotations

import json
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
    required = [
        ROOT / "docs" / "current" / "FIRST_POST_LAUNCH_WBS.md",
        ROOT / "docs" / "current" / "BACKGROUND_SYSTEM_IMAGE.md",
        ROOT / "system" / "runtime" / "planning" / "first_post_launch_wbs.json",
        ROOT / "system" / "runtime" / "planning" / "background_system_image.json",
        ROOT / "system" / "tests" / "test_first_post_launch_wbs.py",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required if not path.exists()]
    if missing:
        print("FAIL: missing first post launch WBS files:", ", ".join(missing))
        return 1
    wbs = json.loads((ROOT / "system" / "runtime" / "planning" / "first_post_launch_wbs.json").read_text(encoding="utf-8"))
    bg = json.loads((ROOT / "system" / "runtime" / "planning" / "background_system_image.json").read_text(encoding="utf-8"))
    required_fields = ["first_post_objective", "target_audience", "value_proposition", "minimum_publishable_scope", "pre_post_checklist", "wbs", "done_condition", "dependency_on_repository_os", "chatgpt_uses_planning_state", "codex_uses_repository_artifacts"]
    if any(field not in wbs for field in required_fields):
        print("FAIL: invalid first post launch WBS payload")
        return 1
    if "components" not in bg or "content_production_flow" not in bg:
        print("FAIL: invalid background system image payload")
        return 1
    print("First post launch WBS validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
