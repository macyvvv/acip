# ROOT_ALLOWLIST

Current root entries:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, `VERSION`, `.gitignore`,
  `.env.example`
- `.github/`, `.system/`
- `app/`, `system/`, `web/`, `somia/`
- `basis/`, `adr/`, `wbs/`, `docs/`, `specs/`, `contracts/`, `archive/`
- `baseline/`, `context/`, `inbox/`, `knowledge/`, `packs/`, `queue/`,
  `releases/`

**11 of the directories previously listed here** (`cache/`, `catalog/`,
`control/`, `loader/`, `prompts/`, `registry/`, `review/`, `rules/`,
`runbooks/`, `solution/`, `templates/`) were audited and archived to
[archive/root_scaffolding_2026/](../../archive/root_scaffolding_2026/README.md)
-- confirmed zero code/workflow references, same "unenforced prose"
pattern as most of pre-overhaul `basis/` (see `adr/ADR-0037`). `knowledge/`
and `packs/` were confirmed live/enforced in the same audit and kept.
`inbox/`, `baseline/`, `releases/` were confirmed to have real code
pointed at them (or, for `baseline/`/`releases/`, an orphaned checker that
nothing calls) but not enforced in CI -- kept as-is, not archived, pending
a closer look.

**Correction to this doc's own prior claim**: an earlier revision of this
file (Stage 4 of `adr/ADR-0037`) asserted that the pre-consolidation
`scripts/` and `runtime/` root directories "no longer exist -- those all
live under `system/` today." That was wrong -- both still exist at root,
discovered while archiving the 11 directories above. Their contents look
like stale, partially-diverged duplicates of `system/scripts/` and
`system/runtime/` (e.g. root `scripts/extract_knowledge.py` is a shorter,
differently-implemented version of `system/scripts/extract_knowledge.py`;
root `runtime/planning/` and `runtime/repository_state/` overlap in name
but not exactly in content with their `system/runtime/` counterparts).
Not archived or otherwise touched yet -- flagged for a dedicated
investigation (confirm nothing reads from the root paths before deciding
whether to archive or delete), not assumed safe just because they look
similar to already-archived scaffolding.

## Policy

This allowlist is report-first (was EP-0121; that EP-numbered tracking
system is itself part of the legacy scaffolding, see `adr/ADR-0037`).
Nothing currently enforces it. A prior audit (2026-07-07) explicitly
considered and declined a full root-directory consolidation migration --
judged as trading a purely cosmetic gain for a large, unscoped file-move
effort, which is itself a form of the process-scaffolding growth this repo
is trying to shed. That decision stands; this file's job is to describe
reality accurately, not to justify a migration.
