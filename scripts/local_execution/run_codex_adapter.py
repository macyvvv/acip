#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from orchestrator.local_execution_adapter import LocalExecutionAdapter


def main() -> int:
    approval_flag = os.environ.get("APPROVAL_FLAG", "false").lower() == "true"
    adapter = LocalExecutionAdapter(ROOT)
    adapter.run(approval_flag=approval_flag, dry_run=not approval_flag)
    print("Local execution adapter completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
