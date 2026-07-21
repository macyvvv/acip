# Census-first store data pivot — WBS

## 1. Why this document exists

The operator corrected the direction of `tools/store_collector/`: it was
built depth-first (require a verified official source before recording
anything). The actual priority is breadth-first -- enumerate what stores
merely *exist* in an area (name + rough existence, uneven info density is
fine), with official-source verification applied as optional enrichment
later, unevenly, per store. Scope starts at Ueno station but is explicitly
meant to scale the same way across Shinjuku, Ikebukuro, Akihabara, every
Yamanote line station, and eventually every major Tokyo nightlife-district
station. Storage moves from per-store JSON drafts to a shared SQLite `.db`
(matching `businesses/kabukicho_survival_map/app/data/kabukicho_poi.db`'s
precedent).

Produced from a parallel panel (dataops, devops, marketingops, ux-research,
legalops) consulted 2026-07-21; each role's full assessment is preserved in
this session's transcript. This document is the synthesis, and is what
`tools/store_collector/`'s next implementation pass follows.

## 2. Key decisions

| Topic | Decision | Owner |
|---|---|---|
| Storage | One shared `businesses/cf_gb_relative_system/tools/store_collector/data/stores.db`, `area_id` as a column (not one .db per area) | dataops/devops |
| Data shape | `stores` (census row, cheap, required-at-discovery) separate from `store_enrichment` (1:1 optional sidecar, absent = "no data yet", not null-filled) | dataops |
| Tooling | New `census.py` (name-only ingestion) + new `db.py` (schema/connection), `collect.py`/`collect_batch.py` adapted to write enrichment into the DB against an already-censused `store_id` | devops |
| Status model | 4-tier: `known` → `has_official_source` → `enriched` → `verified`. Only `verified` counts toward Verified Fresh Store Coverage's numerator | marketingops |
| Area sequencing | Census may run wide across many areas in parallel (cheap, low-risk); "publish/index-eligible" claims stay gated per-area (OUTCOME_BACKLOG's Gate 3/4) | marketingops |
| Schema | `schemas/store-artifact.json` evolves in place: add `completeness_tier`; `verification_method`/`reliability_score`/`hours`/`pricing_model`/`price_items` become conditionally required (only when tier != `known`) | ux-research |
| Legal | Name-only census at scale stays within the discovery-lead allowance **only if** sourced via varied general web search, never by systematically paging one aggregator's full area listing; no per-source dominance; nothing beyond the name copied from a listing; area-granularity only, no address/hours/price until independently verified | legalops |
| Legal register | Amend `search-engine-discovery`'s `downstream_use`/`conditions` in `artifacts/S-011/source-register.json` to explicitly cover census persistence (was previously scoped to "URL discovery only"). The 4 deny entries are unaffected. Still DRAFT -- Human/counsel sign-off (S-012C) unchanged | legalops |
| CI | Unchanged: operator-run-locally only, tests use `sqlite3.connect(":memory:")`/`tmp_path`, no live network in CI | devops |

## 3. Task register

| ID | Work | Owner | Depends | Deliverable |
|---|---|---|---|---|
| CP-01 | Amend `artifacts/S-011/source-register.json`'s `search-engine-discovery` entry per legalops's conditions | legalops | -- | updated entry, still DRAFT |
| CP-02 | Evolve `schemas/store-artifact.json`: add `completeness_tier` enum, conditional-required logic, split `last_confirmed_at` into `first_seen_at`/`last_verified_at` | ux-research/dataops | -- | updated schema + tests |
| CP-03 | `tools/store_collector/db.py`: `connect_db()`, `ensure_schema()` (idempotent `CREATE TABLE IF NOT EXISTS`, stdlib `sqlite3`, no ORM) | devops/dataops | -- | db.py + test_db.py |
| CP-04 | `tools/store_collector/census.py`: ingest a per-area name-list JSON, insert `stores` rows (dedupe by `slug(name+area)`), tier=`known` | devops/dataops | CP-03 | census.py + test_census.py |
| CP-05 | Adapt `collect.py`/`collect_batch.py`: look up an already-censused `store_id`, write `store_enrichment`/`store_sns`/`store_change_log` rows instead of only `cache/*.draft.json`; still never auto-set `verification_method` | devops/dataops | CP-03, CP-04 | updated collect.py/collect_batch.py + tests |
| CP-06 | Re-source Ueno candidates as a name-list (`candidates/ueno.json` reshaped), run `census.py`, run enrichment for the 4 already-verified stores | (this session) | CP-01, CP-02, CP-04, CP-05 | populated `data/stores.db` (local, gitignored) |
| CP-07 | Update `tools/store_collector/README.md` for the new two-step (census → enrichment) workflow and multi-area usage | devops | CP-04, CP-05 | updated README |

## 4. Explicitly deferred (not this pass)

- Public-facing UI/display of `completeness_tier` (no UI exists yet; ux-research's finding is a data-layer requirement only, so a future UI isn't blocked).
- KPI dashboard/report changes (marketingops's G-CENSUS-01/03/04) -- real reporting infra doesn't exist yet in Phase -1.
- Actual expansion beyond Ueno (Shinjuku/Ikebukuro/Akihabara/...) -- this pass proves the pattern on Ueno only; each new area is just a new `areas` row + a new `candidates/<area>.json`, no code change expected.
- Gate 1/2 formal area selection and Human/counsel legal sign-off (S-012C) remain outstanding, same as before this pivot.
