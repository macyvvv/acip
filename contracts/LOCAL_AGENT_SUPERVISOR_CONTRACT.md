# LOCAL_AGENT_SUPERVISOR_CONTRACT

The local supervisor is a deterministic bridge between Planning State, Repository State, and execution intake.

## Authoritative Inputs

- system/runtime/planning/latest.json
- system/runtime/repository_state/latest.json
- system/runtime/handoff/latest.json
- system/runtime/handoff/completion/latest.json
- system/runtime/event_system/runtime/
- queue/

## Required Fields

- planning_status
- repository_status
- next_eligible_work_item
- codex_intake_payload
- execution_mode
- approval_required
- safety_gate
- source_artifacts
