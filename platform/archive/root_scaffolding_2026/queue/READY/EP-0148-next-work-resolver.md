# EP-0148 Next Work Resolver

status: DONE
pack_id: PACK-0002
ep_range: EP-0144..EP-0147
objective: Resolve the next work item deterministically using priority, dependency, and approval requirements.

## Scope

- Inspect queue items in `queue/READY/`.
- Select the next work item without Human decision-making.
- Keep the repository queue as the source of truth.

## Validation

- `python3 system/scripts/validate_all.py`
- `python3 -m pytest -q`

