# ROOT_ALLOWLIST

Current root entries:

- `README.md`, `AGENTS.md`, `CLAUDE.md`, `VERSION`, `.gitignore`,
  `.env.example`
- `.github/`, `.system/`
- `app/`, `system/`, `web/`, `somia/`, `scripts/`
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

**Root `runtime/` archived, root `scripts/` kept -- follow-up to a
correction this doc itself needed twice.** Stage 4 of `adr/ADR-0037`
originally claimed `scripts/` and `runtime/` "no longer exist -- those all
live under `system/` today," which was wrong (both existed). A follow-up
pass then guessed both were "stale, partially-diverged duplicates" of
their `system/` counterparts without actually checking -- also wrong,
for `scripts/` specifically. Investigating properly this time:

- `scripts/extract_knowledge.py` is a genuine, intentional root-level CLI
  wrapper (`from system.scripts.extract_knowledge import main`) matching
  the documented human workflow in `docs/current/KNOWLEDGE_FACTORY.md`
  ("Run `python scripts/extract_knowledge.py`") -- **not** a stale
  duplicate. The earlier "shorter, differently-implemented" read was
  comparing a 13-line delegating wrapper against the real implementation
  it calls, not two independently-diverged copies. Kept as-is.
- `runtime/planning/` and `runtime/repository_state/` had zero code
  references anywhere (confirmed via `git grep`, both read and write
  sides) and, for `planning/` specifically, contained genuinely stale
  content (`current_pack: PACK-0001` at root vs. `PACK-0004` in
  `system/runtime/planning/`, missing several files `system/runtime/
  planning/` has since accumulated) -- real evidence of a frozen,
  no-longer-updated pre-consolidation snapshot, not just a same-named
  coincidence. Archived to
  [archive/root_scaffolding_2026/runtime/](../../archive/root_scaffolding_2026/README.md).

**Lesson applied going forward**: a plausible-sounding guess about
staleness/duplication is not the same as checking it. Both of this doc's
own errors above were guesses stated as findings; the fix each time was
to actually diff the content and `git grep` for references before writing
a conclusion.

## Policy

This allowlist is report-first (was EP-0121; that EP-numbered tracking
system is itself part of the legacy scaffolding, see `adr/ADR-0037`).
Nothing currently enforces it. A prior audit (2026-07-07) explicitly
considered and declined a full root-directory consolidation migration --
judged as trading a purely cosmetic gain for a large, unscoped file-move
effort, which is itself a form of the process-scaffolding growth this repo
is trying to shed. That decision stands; this file's job is to describe
reality accurately, not to justify a migration.
