#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from system.core.agent_turn_runner import run_agent_turn


def main() -> int:
    result = run_agent_turn()
    print(result.summary)
    print(f"processed_message_id={result.processed_message_id or ''}")
    print(f"next_state={result.next_state}")
    print(f"state_path={result.state_path}")
    print(f"outbox_message_path={result.outbox_message_path or ''}")
    print(f"archived_message_path={result.archived_message_path or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
