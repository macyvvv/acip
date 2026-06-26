# EP-0145 Handoff Payload Normalizer

status: DONE
pack_id: PACK-0002
ep_range: EP-0144..EP-0147
objective: Normalize queue/READY handoff payloads into machine-readable execution intake records.

## Scope

- Read the next queue item from `queue/READY/`.
- Normalize the handoff payload into an execution request record.
- Preserve the repository queue as the source of truth.

## Validation

- `python3 scripts/validate_all.py`
- `python3 -m pytest -q`

