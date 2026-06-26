# EP-0144 Agent Handoff Automation Pack

Status: READY
Owner: Codex
Source: ChatGPT
Repository: macyvvv/acip

## Current Objective

Remove Human from ChatGPT-to-Codex handoff.

## Done Condition

ChatGPT can place work into Repository / GitHub Issue / Queue, and Codex can retrieve the next work item from that persistent queue without the Human copying the specification text into Codex.

## Scope

Implement the shortest durable handoff path:

1. Repository queue item format.
2. GitHub Issue intake format.
3. Codex intake reader for queue/READY and optionally GitHub issue metadata.
4. Execution handoff status transitions.
5. Completion report handoff back into repository artifacts.

## Required EPs

### EP-0144 ChatGPT-to-Codex Handoff Queue

Purpose:
- Define repository-native handoff queue format.
- Make `queue/READY/` the durable intake source for Codex.
- Define fields required for Codex to start work.

### EP-0145 Codex Execution Intake

Purpose:
- Add a Codex-side intake script that reads next READY queue item.
- Convert queue item into execution request using existing Execution Request Contract.
- Refuse ambiguous or incomplete items.

### EP-0146 Completion Report Ingestion

Purpose:
- Standardize how Codex writes completion reports back to runtime / journal / output contract.
- Ensure ChatGPT can review completion from repository artifacts, not chat text.

### EP-0147 Handoff State Transitions

Purpose:
- READY -> RUNNING -> REVIEW -> DONE / BLOCKED.
- Persist handoff state in repository artifacts.
- Keep Human only as approval/emergency stop.

### EP-0148 Human Removal Validation

Purpose:
- Validate that a handoff item can be created, read, converted to execution request, and reported without copying spec text through Human.
- This does not require Codex auto-start from the platform, but it must remove Human as message courier.

## Required Implementation Targets

Codex should create or update as needed:

- `contracts/HANDOFF_QUEUE_CONTRACT.md`
- `docs/current/AGENT_HANDOFF_AUTOMATION.md`
- `orchestrator/handoff_queue.py`
- `orchestrator/codex_intake.py`
- `runtime/handoff/`
- `scripts/handoff/read_next_handoff.py`
- `scripts/handoff/validate_handoff_queue.py`
- `scripts/validate_ep_0144.py` through `scripts/validate_ep_0148.py`
- `tests/test_handoff_queue.py`
- `tests/test_codex_intake.py`
- `tests/test_handoff_state_transitions.py`
- `specs/EP-0144/` through `specs/EP-0148/`

## Non-Goals

- Do not rely on Human copying full specs into Codex.
- Do not introduce unsafe auto-push.
- Do not introduce secrets.
- Do not introduce external runtime mutation beyond existing repository/GitHub flow.
- Do not break EP-0100 through EP-0143.

## Validation

Use only:

```bash
python3 scripts/validate_all.py
python3 -m pytest -q
```

## Commit Policy

Commit each EP separately:

- `feat: EP-0144 ChatGPT-to-Codex Handoff Queue`
- `feat: EP-0145 Codex Execution Intake`
- `feat: EP-0146 Completion Report Ingestion`
- `feat: EP-0147 Handoff State Transitions`
- `feat: EP-0148 Human Removal Validation`

## Completion Report Format

For each EP report:

- EP
- Commit SHA
- Validation result
- pytest result
- worktree state
- next action

Pack-level report:

- Whether Codex can read next work item from `queue/READY/` without Human copying the spec text.
- Remaining gap to full Codex auto-start, if any.
