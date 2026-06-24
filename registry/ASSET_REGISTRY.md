# Asset Registry

## Conclusion

This file is the initial repository-governed registry for Canonical Assets.

Repository overrides conversation.

## Registry

| asset_id | title | asset_type | lifecycle_status | owner | version | source_path | parent_asset_id | derived_asset_ids | related_adr | related_wbs | quality_gate_status | reuse_status | risk_level | revenue_link | last_reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| REG-0000 | Asset Registry Control | Operational Asset | canonical | Human | 0.1.0 | registry/ASSET_REGISTRY.md |  |  | ADR-0005 | WBS-0003 | pending | reusable | low | TBD | 2026-06-24 |

## Rules

- Every canonical asset should have one registry row.
- Every derivative should reference source asset id.
- Deprecated assets remain listed.
- Registry changes must go through PR review.
