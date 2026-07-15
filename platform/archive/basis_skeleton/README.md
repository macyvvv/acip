# basis_skeleton (archived)

These 7 files were an early placeholder pass through `platform/basis/` — a title plus a
single boilerplate line ("Human: Mission/Approval/Emergency Stop"), created
before the fuller policy at the same or a neighboring number was written.
Each one is fully superseded by a later, substantive file still living in
`platform/basis/`:

| Archived stub | Superseded by (at the time, 2026-07-07) | Where that content lives now (2026-07-12) |
|---|---|---|
| `053_repository_health_policy.md` | `platform/basis/054_repository_health_policy.md` | `platform/basis/CORE_PRINCIPLES.md` (see `platform/archive/basis_corpus_2026/README.md`) |
| `054_dead_asset_policy.md` | `platform/basis/055_dead_asset_detection_policy.md` | `platform/basis/CORE_PRINCIPLES.md` §7 |
| `055_orphan_asset_policy.md` | `platform/basis/055_dead_asset_detection_policy.md` ("Dead Document Signals" covers orphan detection) | `platform/basis/CORE_PRINCIPLES.md` §7 |
| `056_drift_detection_policy.md` | `platform/basis/058_drift_detection_policy.md` | archived, aspirational (never wired into a dedicated check) |
| `058_link_integrity_policy.md` | `platform/basis/056_link_integrity_policy.md` | archived, aspirational |
| `059_continuous_governance_policy.md` | `platform/basis/060_continuous_governance_policy.md` | `platform/basis/CORE_PRINCIPLES.md` §7 + real CI (`.github/workflows/`) |
| `060_selftest_policy.md` | `platform/basis/053_repository_selftest_policy.md` | `platform/system/platform/scripts/selftest_v2/` (live) |

The "superseded by" files in the middle column were themselves archived to
[platform/archive/basis_corpus_2026/](../basis_corpus_2026/README.md) by a later,
much larger consolidation pass (`platform/adr/ADR-0037-governance-layer-overhaul.md`)
-- kept here as a historical record of the first archival step, with the
third column added to point at where the real content actually lives today.

Kept for history (archive space may duplicate numbers/titles and is
excluded from canonical duplicate/orphan checks). See
[platform/basis/README.md](../../platform/basis/README.md) for the current index.
