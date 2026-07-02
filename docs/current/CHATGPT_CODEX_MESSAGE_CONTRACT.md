# CHATGPT_CODEX_MESSAGE_CONTRACT

## Objective
Define the minimum repository-native protocol for machine-readable ChatGPT ↔ Codex communication.

## Message Schema
Each message must include:
- `message_id`
- `thread_id`
- `sender`
- `receiver`
- `message_type`
- `related_issue`
- `related_artifacts`
- `objective`
- `requested_action`
- `constraints`
- `status`
- `created_at`
- `responded_at`
- `supersedes`
- `body`

## Allowed Message Types
- `request_clarification`
- `propose_plan`
- `approve_plan`
- `reject_plan`
- `request_execution`
- `report_result`
- `request_review`
- `report_review`
- `block`
- `unblock`
- `terminate_thread`

## Message Status
Message `status` tracks message lifecycle, not repository execution.
Allowed values:
- `draft`
- `sent`
- `received`
- `responded`
- `archived`
- `blocked`
- `terminated`

## Authority Boundaries
### ChatGPT may
- plan
- review
- approve or reject within governance
- request execution
- request clarification

### Codex may
- implement
- validate
- report results
- request clarification
- block when execution is impossible

### Neither may
- silently change governance
- silently change architecture
- loop indefinitely without emitting state
- mutate external systems without explicit policy

## Canonical Runtime Locations
- `system/runtime/agent_messages/inbox/`
- `system/runtime/agent_messages/outbox/`
- `system/runtime/agent_messages/archive/`

## State Model Link
Messages are consumed by `docs/current/AUTONOMOUS_AGENT_STATE_MODEL.md` and the runtime state manager under `system/core/agent_state_manager.py`.
