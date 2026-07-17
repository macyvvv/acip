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

from system.core.publishing_control import pause_publishing


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Freeze the publishing scheduler (platform/system/scripts/publishing/run_scheduled_publish.py) "
        "across all businesses/platforms. No manual override exists -- paused means zero posts, full stop."
    )
    parser.add_argument("--reason", required=True)
    parser.add_argument("--paused-by", required=True)
    args = parser.parse_args()

    path = pause_publishing(args.reason, args.paused_by, ROOT)
    print(f"publishing_paused=true")
    print(f"sentinel_path={path}")
    print(f"reason={args.reason}")
    print(f"paused_by={args.paused_by}")
    print("next: run resume_publishing.py when ready to let scheduled publishing resume")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
