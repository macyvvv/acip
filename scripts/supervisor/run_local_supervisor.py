#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from orchestrator.local_supervisor import LocalSupervisor


def main() -> int:
    supervisor = LocalSupervisor(ROOT)
    supervisor.run(execution_flag=False)
    print("Local supervisor dry-run completed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
