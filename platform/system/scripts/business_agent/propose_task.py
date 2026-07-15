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

from system.core.business_agent_handoff import write_business_agent_handoff
from system.core.business_agent_task_queue import add_task
from system.core.business_registry import get_business
from system.core.agent_role_registry import get_role


def main() -> int:
    parser = argparse.ArgumentParser(description="Propose one business-agent task for one-shot approved execution.")
    parser.add_argument("--business-id", required=True)
    parser.add_argument("--role-id", required=True)
    parser.add_argument("--task-id", required=True)
    parser.add_argument("--title", required=True)
    parser.add_argument("--task-description", default="")
    args = parser.parse_args()

    if get_business(args.business_id, ROOT) is None:
        print(f"Unknown business_id: {args.business_id}")
        return 1
    if get_role(args.role_id, ROOT) is None:
        print(f"Unknown role_id: {args.role_id}")
        return 1

    handoff_path = write_business_agent_handoff(args.business_id, args.role_id, args.task_id, args.task_description, ROOT)
    add_task(args.business_id, args.role_id, args.task_id, args.title, ROOT)

    print(f"handoff_path={handoff_path}")
    print(f"business_id={args.business_id}")
    print(f"role_id={args.role_id}")
    print(f"task_id={args.task_id}")
    print("status=candidate")
    print("next: run the Approval Console to review and approve this scope")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
