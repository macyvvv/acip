# AUTONOMOUS_CONVERSATION_VERTICAL_SLICE

## Purpose
Run one deterministic ChatGPT ↔ Codex turn, or one bounded thread, using repository-native messages and agent state.

## Scope Boundaries
- No daemon
- No infinite loop
- No GitHub mutation
- No external mutation
- No live Codex execution
- No architecture rewrite

## How to Run One Turn
- `python3 system/scripts/agent/run_agent_turn.py`

## How to Run One Bounded Thread
- `python3 system/scripts/agent/run_agent_thread.py --max-turns 5`

## Sample Fixtures
- `system/runtime/agent_messages/inbox/sample_request_execution.json`
- `system/runtime/agent_messages/inbox/sample_request_review.json`
- `system/runtime/agent_messages/inbox/sample_autonomous_thread.json`

## Expected State Transitions
- `request_execution` → `ready_to_execute` / `executing` / `waiting_for_review`
- `request_review` → `waiting_for_review`
- `approve_plan` → `completed`
- `reject_plan` → `blocked`
- `block` → `blocked`
- `unblock` → `waiting_for_input`
- `terminate_thread` → `terminated`

## Stop Conditions
- `completed`
- `blocked`
- `terminated`
- `max_turns reached`

## What This Does Not Do Yet
- It does not run Codex against live repository issues.
- It does not advance beyond bounded deterministic turns.
- It does not replace the governance or planning system.
