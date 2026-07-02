#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from system.core.approved_handoff_execution_bridge import ApprovedHandoffExecutionBridge


def main() -> int:
    result = ApprovedHandoffExecutionBridge(ROOT).run()
    print(f"allow={str(result.allow).lower()}")
    print(f"bridge_status={result.bridge_status}")
    print(f"handoff_id={result.handoff_id or ''}")
    print(f"approval_id={result.approval_id or ''}")
    print(f"scope_type={result.scope_type or ''}")
    print(f"scope_id={result.scope_id or ''}")
    print(f"denied_reason={result.denied_reason or ''}")
    print(f"execution_request_path={result.execution_request_path or ''}")
    return 0 if result.allow else 1


if __name__ == "__main__":
    raise SystemExit(main())
