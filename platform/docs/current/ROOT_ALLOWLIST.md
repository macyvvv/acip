# ROOT_ALLOWLIST

Current root entries (target policy):

- Canonical containers: `platform/`, `businesses/`
- Minimal config/meta: `README.md`, `AGENTS.md`, `CLAUDE.md`, `VERSION`, `.gitignore`, `.env`, `.env.example`, `.github/`, `.git/`, `.claude/`, `requirements-dev.txt`, `netlify.toml`, `selftest.yml`
- Compatibility symlinks may temporarily remain during migration until all references are updated.

Local machine artifacts (ignored by layout validation): `.DS_Store`, `.pytest_cache/`, `.venv/`.

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

**`queue/` also archived.** 46 `EP-*.md` proposal docs under
`queue/READY/` plus `queue/QUEUE_ENGINE.md` archived to
[archive/root_scaffolding_2026/queue/](../../archive/root_scaffolding_2026/README.md).
An initial "zero `validate_ep_*.py` references" check was wrong -- a
literal-substring `git grep` missed 7 scripts that build the required
path from separate pathlib components. `validate_all.py` caught the break
immediately; fixed by repointing those 7 scripts at the archived path
(same pattern as the `semantic_checks.py`/`validate_baseline.py` fixes
above). See the archive README for the full account -- this is the third
instance this session of that same literal-substring grep gotcha.
Three related `system/runtime/queue/` files (`next_work.json`,
`queue_state.json`, `autonomous_queue_runtime.json`) were deleted, not
archived -- confirmed dead via a full read of
`system/orchestrator/queue_state.py` (only reads/writes
`docs/current/QUEUE_STATE.md`) and stale/placeholder content
(`"intake_request_id": "REQ-SAMPLE"`, references to `EP-0108`/`EP-0109`).
See the archive README for why this correctly triggered a
permission-classifier pause first (a contradiction with an earlier,
less rigorous claim in the same session) before being resolved with
direct evidence.

## Policy

This allowlist is report-first (was EP-0121; that EP-numbered tracking
system is itself part of the legacy scaffolding, see `adr/ADR-0037`).
Nothing currently enforces it. A prior audit (2026-07-07) explicitly
considered and declined a full root-directory consolidation migration --
judged as trading a purely cosmetic gain for a large, unscoped file-move
effort, which is itself a form of the process-scaffolding growth this repo
is trying to shed. That decision stands; this file's job is to describe
reality accurately, not to justify a migration.
