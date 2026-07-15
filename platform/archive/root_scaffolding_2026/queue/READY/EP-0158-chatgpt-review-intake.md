# EP-0158 ChatGPT Review Intake

status: READY
pack_id: PACK-0004
ep_range: EP-0156..EP-0160
objective: Define a single review intake path for ChatGPT.

## Scope

- Default review input is `platform/system/runtime/handoff/latest.json`.
- Define review intake fields and expected decisions.
- Avoid scanning queue or runtime state manually.

## Success Criteria

- ChatGPT can determine next action from the latest completion marker.
