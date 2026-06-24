# Asset Registry Template

## Required Columns

| Field | Required | Description |
|---|---:|---|
| asset_id | Yes | Stable unique asset identifier |
| title | Yes | Stable asset title |
| asset_type | Yes | Knowledge Asset / Content Object / Media Object / Operational Asset |
| lifecycle_status | Yes | intake / draft / review / approved / canonical / reuse / revision / deprecated |
| owner | Yes | Responsible owner |
| version | Yes | Asset version |
| source_path | Yes | Repository path of canonical source |
| parent_asset_id | Conditional | Source parent if derivative |
| derived_asset_ids | No | Known derivatives |
| related_adr | No | Related ADR path or ID |
| related_wbs | No | Related WBS path or ID |
| quality_gate_status | Yes | pending / passed / failed / waived |
| reuse_status | Yes | not_reused / reusable / reused / restricted / deprecated |
| risk_level | Yes | low / medium / high |
| revenue_link | No | Known revenue or ROI link |
| last_reviewed | Yes | YYYY-MM-DD |

## Example Row

| asset_id | title | asset_type | lifecycle_status | owner | version | source_path | parent_asset_id | derived_asset_ids | related_adr | related_wbs | quality_gate_status | reuse_status | risk_level | revenue_link | last_reviewed |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| KA-0001 | Example Knowledge Asset | Knowledge Asset | canonical | Human | 0.1.0 | assets/knowledge/KA-0001.md |  | CO-0001 | ADR-0005 | WBS-0003 | passed | reusable | low | TBD | 2026-06-24 |
