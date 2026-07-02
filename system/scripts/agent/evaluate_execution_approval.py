#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from system.core.agent_execution_approval import evaluate_execution_approval


def main() -> int:
    result = evaluate_execution_approval(ROOT)
    print(f"allow={str(result.allowed).lower()}")
    print(f"reason={result.reason}")
    return 0 if result.allowed else 1


if __name__ == "__main__":
    raise SystemExit(main())
