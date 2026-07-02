#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from system.core.approved_autonomous_execution import ApprovedAutonomousExecution


def main() -> int:
    result = ApprovedAutonomousExecution(ROOT).run()
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
