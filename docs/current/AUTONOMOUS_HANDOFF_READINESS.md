# AUTONOMOUS_HANDOFF_READINESS

## Summary
Bounded issue-scoped autonomous handoff is operational. Full autonomous execution is not enabled.

## Verified Capability
- An approved issue-creation draft or explicit issue scope can seed a bounded autonomous thread.
- The thread updates repository-native agent runtime artifacts.
- The thread can emit an execution handoff artifact.
- The thread can emit `system/runtime/request/execution_request.json`.
- When human review is still required, the safe stop state is `waiting_for_review` or `idle`.

## Capability Levels
### Level 0
- Message contract only.

### Level 1
- Bounded autonomous turn/thread execution.

### Level 2
- Issue-scoped autonomous handoff generation.

### Level 3
- Human-approved execution wiring.

### Level 4
- Full autonomous execution.
- Not enabled.

## Verified Example
- Approved draft: `DRAFT-OPP-KABUKICHO-001`
- Command:
```bash
python3 system/scripts/agent/run_issue_scoped_agent_thread.py --approved-draft-id DRAFT-OPP-KABUKICHO-001
```
- Final state: `waiting_for_review`
- Stop reason: `idle`
- Handoff path: `system/runtime/agent_handoff/latest.json`
- Request path: `system/runtime/request/execution_request.json`

## Release Gates Before Next Stage
Before enabling any future stage, all of the following must be true:
- review semantics are defined
- explicit human approval semantics are defined
- live execution wiring is bounded
- rollback and kill switch are defined
- no uncontrolled issue selection exists
- no external mutation exists

## Forbidden Now
- Full autonomous execution
- GitHub mutation
- Automatic wiring into `run_until_idle`
- Daemonization
- Open-ended loops
