# AUTONOMOUS_AGENT_STATE_MODEL

## Objective
Define the minimum deterministic state model for repository-native ChatGPT ↔ Codex collaboration.

## Runtime State
Canonical runtime files:
- `system/runtime/agent_state/latest.json`
- `system/runtime/agent_state/latest.md`

## State Machine
Allowed states:
- `idle`
- `waiting_for_input`
- `ready_to_execute`
- `executing`
- `waiting_for_review`
- `blocked`
- `completed`
- `terminated`

## Transition Rules
- `idle` → `waiting_for_input`, `ready_to_execute`, `blocked`, `terminated`
- `waiting_for_input` → `ready_to_execute`, `blocked`, `terminated`
- `ready_to_execute` → `executing`, `blocked`, `terminated`
- `executing` → `waiting_for_review`, `blocked`, `completed`, `terminated`
- `waiting_for_review` → `completed`, `blocked`, `terminated`
- `blocked` → `waiting_for_input`, `terminated`
- `completed` → `idle`, `terminated`
- `terminated` has no outbound transitions

## State Fields
The canonical state record stores:
- `state`
- `thread_id`
- `message_id`
- `message_type`
- `sender`
- `receiver`
- `related_issue`
- `pending_messages`
- `updated_at`
- `transition_reason`

## Boundary Rules
ChatGPT and Codex must only act through explicit state transitions and emitted messages.

They may not:
- silently change governance
- silently change architecture
- mutate external systems without explicit policy
- continue a blocked thread without a state emission

## Operational Meaning
- `idle`: no active collaboration
- `waiting_for_input`: one side is awaiting clarification or review
- `ready_to_execute`: a valid execution request exists
- `executing`: Codex is actively working
- `waiting_for_review`: execution is complete and awaiting review
- `blocked`: execution cannot proceed without an explicit resolution
- `completed`: the thread reached a terminal success condition
- `terminated`: the thread was intentionally closed
