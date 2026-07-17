#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

# business_agent_execution_adapter.py's DEFAULT_CLI_TIMEOUT_SECONDS=60 is too
# short for real generation work -- run_scheduled_execution.py already learned
# this the hard way (see its own comment) and sets this env var before
# invoking the same adapter. This script is the other real caller of
# ApprovedAutonomousExecution.run() (manual/interactive use), so it needs the
# same default. setdefault, not assignment, so an operator's own explicit env
# var (e.g. for a manual dry-run) is never silently overridden.
os.environ.setdefault("CLAUDE_EXECUTION_TIMEOUT_SECONDS", "240")

from system.core.approved_autonomous_execution import ApprovedAutonomousExecution


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one approved autonomous execution.")
    parser.add_argument("--business-id", default=None)
    parser.add_argument("--role-id", default=None)
    parser.add_argument("--task-id", default=None)
    args = parser.parse_args()
    if bool(args.business_id) != bool(args.role_id) or bool(args.business_id) != bool(args.task_id):
        parser.error("--business-id/--role-id/--task-id must be given together, or not at all")

    result = ApprovedAutonomousExecution(ROOT).run(business_id=args.business_id, role_id=args.role_id, task_id=args.task_id)
    print(f"allow={str(result.allow).lower()}")
    print(f"handoff_id={result.handoff_id or ''}")
    print(f"approval_id={result.approval_id or ''}")
    print(f"scope_type={result.scope_type or ''}")
    print(f"scope_id={result.scope_id or ''}")
    print(f"execution_triggered={str(result.execution_triggered).lower()}")
    print(f"execution_mode={result.execution_mode}")
    print(f"execution_result_status={result.execution_result_status}")
    print(f"completion_marker_path={result.completion_marker_path or ''}")
    print(f"request_path={result.request_path or ''}")
    print(f"stopped_reason={result.stopped_reason}")
    print(f"authorization_source={result.authorization_source}")
    print(f"policy_id={result.policy_id or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
