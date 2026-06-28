# WORKER_ROUTING

## Purpose

Route tasks to the correct worker profile.

## Routing Rule

- Codex: implementation tasks
- ChatGPT: specification and review tasks
- Human: approval and escalation tasks

## Boundary

Routing must not execute work or change repository state.
