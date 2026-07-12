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

from system.core.scheduled_execution_control import pause_scheduled_execution


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze the Level 3b unattended scheduler (run_scheduled_execution.py). "
        "Does NOT affect is_automation_paused() (task-proposal), is_pre_approval_paused() "
        "(Level 3a policy-claim), or is_publishing_paused() (Level 3c) -- each kill switch "
        "is independent. No manual override exists -- paused means the scheduler attempts "
        "nothing at all this wake, full stop."
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--paused-by", required=True)
    args = parser.parse_args()

    path = pause_scheduled_execution(args.reason, args.paused_by, ROOT)
    print("scheduled_execution_paused=true")
    print(f"sentinel_path={path}")
    print(f"reason={args.reason}")
    print(f"paused_by={args.paused_by}")
    print("next: run resume_scheduled_execution.py when ready to let the scheduler resume")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
