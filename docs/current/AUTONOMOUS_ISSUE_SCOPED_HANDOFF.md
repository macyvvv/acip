# AUTONOMOUS_ISSUE_SCOPED_HANDOFF

## Purpose
Bridge one explicit issue scope into the bounded ChatGPT ↔ Codex conversation flow and emit a repository-native execution handoff.

## Boundaries
- One explicit issue number or approved issue-creation draft only
- Bounded turns only
- No GitHub mutation
- No external mutation
- No daemon
- No infinite loop
- No autonomous issue discovery

## How to Run
### By issue number
```bash
python3 system/scripts/agent/run_issue_scoped_agent_thread.py --issue-number 30
```

### By approved draft id
```bash
python3 system/scripts/agent/run_issue_scoped_agent_thread.py --approved-draft-id DRAFT-OPP-KABUKICHO-001
```

## Expected Outputs
- `system/runtime/agent_threads/latest.json`
- `system/runtime/agent_threads/latest.md`
- `system/runtime/agent_threads/archive/`
- `system/runtime/agent_handoff/latest.json`
- `system/runtime/agent_handoff/latest.md`
- `system/runtime/request/execution_request.json`

## Stop Conditions
- completed
- blocked
- terminated
- max turns reached

## Intentional Manual Work
- Human still selects the issue or approved draft scope.
- Human still reviews the handoff and execution request.
- Human still controls any external action or publication.
