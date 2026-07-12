# ROOT_ALLOWLIST

This list was last reconciled against the pre-consolidation repo layout
(`scripts/`, `orchestrator/`, `workers/`, `runtime/`, `graph/` at root),
which no longer exists -- those all live under `system/` today. Updated to
the actual current root entries below.

Current root entries:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, `VERSION`, `.gitignore`,
  `.env.example`
- `.github/`, `.system/`
- `app/`, `system/`, `web/`, `somia/`
- `basis/`, `adr/`, `wbs/`, `docs/`, `specs/`, `contracts/`, `archive/`
- `baseline/`, `cache/`, `catalog/`, `context/`, `control/`, `inbox/`,
  `knowledge/`, `loader/`, `packs/`, `prompts/`, `queue/`, `registry/`,
  `releases/`, `review/`, `rules/`, `runbooks/`, `solution/`, `templates/`

**Note on the last group above** (`baseline/` through `templates/`): these
are additional "repository operating system" prose directories beyond even
`basis/`'s scope, most of which read as descriptive rather than enforced
(same pattern as most of pre-overhaul `basis/`, see `adr/ADR-0037`). Not
audited or touched by this pass -- flagged here as a real, larger follow-up
candidate for a future governance stage, not silently ignored.

## Policy

This allowlist is report-first (was EP-0121; that EP-numbered tracking
system is itself part of the legacy scaffolding, see `adr/ADR-0037`).
Nothing currently enforces it. A prior audit (2026-07-07) explicitly
considered and declined a full root-directory consolidation migration --
judged as trading a purely cosmetic gain for a large, unscoped file-move
effort, which is itself a form of the process-scaffolding growth this repo
is trying to shed. That decision stands; this file's job is to describe
reality accurately, not to justify a migration.
