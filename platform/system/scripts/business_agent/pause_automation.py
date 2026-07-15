from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _resolve_repo_root() -> Path:
    current = Path(__file__).resolve()
    for candidate in current.parents:
        if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
            return candidate
    raise RuntimeError(f"Unable to locate repository root from {__file__}")


ROOT = _resolve_repo_root()
sys.path.insert(0, str(ROOT))

from system.core.business_agent_automation_control import pause_automation


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze automatic next-task proposal (Level 1/2 auto-trigger) across all businesses. "
        "Does NOT block manual propose_task.py / set_execution_approval.py / run_approved_autonomous_execution.py."
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--paused-by", required=True)
    args = parser.parse_args()

    path = pause_automation(args.reason, args.paused_by, ROOT)
    print(f"automation_paused=true")
    print(f"sentinel_path={path}")
    print(f"reason={args.reason}")
    print(f"paused_by={args.paused_by}")
    print("next: run resume_automation.py when ready to let auto-trigger resume proposing tasks")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
