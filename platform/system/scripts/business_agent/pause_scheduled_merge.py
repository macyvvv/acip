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

from system.core.scheduled_merge_control import pause_scheduled_merge


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze ADR-0040's unattended-merge capability. Does NOT affect "
        "is_scheduled_execution_paused() (ADR-0038, generation) -- a wake will keep "
        "executing and opening PRs, it just won't auto-merge them while this is paused. "
        "Also engaged automatically by the merge circuit breaker after repeated "
        "consecutive merge-gate failures (paused_by='circuit_breaker' in that case)."
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--paused-by", required=True)
    args = parser.parse_args()

    path = pause_scheduled_merge(args.reason, args.paused_by, ROOT)
    print("scheduled_merge_paused=true")
    print(f"sentinel_path={path}")
    print(f"reason={args.reason}")
    print(f"paused_by={args.paused_by}")
    print("next: run resume_scheduled_merge.py when ready to let auto-merge resume")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
