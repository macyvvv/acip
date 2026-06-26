# EP-0144 Agent Handoff Automation Pack

status: READY
pack_id: PACK-0002
ep_range: EP-0144..EP-0147
objective: Remove Human from ChatGPT-to-Codex handoff by making the repository queue item the durable source of truth.

## Pack Scope

- Make `queue/READY/` the canonical handoff input for Codex.
- Avoid dependence on Human copying the full specification text.
- Keep handoff machine readable and repository-driven.

## Initial EP Sequence

- EP-0144: Agent Handoff Queue Reader
- EP-0145: Handoff Payload Normalizer
- EP-0146: Queue-to-Execution Bridge
- EP-0147: Handoff Validation and Completion Marker

## Validation

- `python3 scripts/validate_all.py`
- `python3 -m pytest -q`

## Human Boundary

- Human may approve or reject the pack.
- Human should not copy the full specification text into Codex once queue reading is working.

## Success Criteria

- Codex can retrieve the next work item from `queue/READY/` without Human copying the specification text.
- The queue item remains the durable source for execution handoff.
- The handoff format is deterministic and repository-native.

