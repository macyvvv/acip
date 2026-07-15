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

from system.core.execution_pre_approval_control import pause_pre_approval


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze Level 3a policy-based execution pre-approval across all businesses/roles. "
        "Does NOT affect is_automation_paused() (task-proposal) or is_publishing_paused() (Level 3c) -- "
        "each kill switch is independent. No manual override exists -- paused means every pre-approval "
        "check denies, full stop."
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--paused-by", required=True)
    args = parser.parse_args()

    path = pause_pre_approval(args.reason, args.paused_by, ROOT)
    print(f"pre_approval_paused=true")
    print(f"sentinel_path={path}")
    print(f"reason={args.reason}")
    print(f"paused_by={args.paused_by}")
    print("next: run resume_pre_approval.py when ready to let policy-based pre-approval resume")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
