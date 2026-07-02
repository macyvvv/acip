#!/usr/bin/env python3
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from system.core.agent_issue_bridge import AgentIssueBridge


def main() -> int:
    parser = argparse.ArgumentParser(description="Run one bounded issue-scoped autonomous agent thread.")
    scope_group = parser.add_mutually_exclusive_group(required=True)
    scope_group.add_argument("--issue-number", type=int)
    scope_group.add_argument("--approved-draft-id")
    parser.add_argument("--max-turns", type=int, default=5)
    args = parser.parse_args()
    result = AgentIssueBridge().run(issue_number=args.issue_number, approved_draft_id=args.approved_draft_id, max_turns=args.max_turns)
    print(f"issue_scope={result.issue_scope}")
    print(f"thread_id={result.thread_id}")
    print(f"turns_run={result.thread_result.turns_run}")
    print(f"final_state={result.thread_result.final_state}")
    print(f"stop_reason={result.thread_result.stop_reason}")
    print(f"handoff_path={result.handoff_path or ''}")
    print(f"request_path={result.request_path or ''}")
    print(f"archive_path={result.archive_path or ''}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
