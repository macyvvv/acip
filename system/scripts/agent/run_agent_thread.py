#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from system.core.agent_thread_runner import run_agent_thread


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one bounded autonomous agent thread.")
    parser.add_argument("--max-turns", type=int, default=5)
    args = parser.parse_args()
    result = run_agent_thread(max_turns=args.max_turns)
    print(f"thread_id={result.thread_id or ''}")
    print(f"turns_run={result.turns_run}")
    print(f"final_state={result.final_state}")
    print(f"stop_reason={result.stop_reason}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
