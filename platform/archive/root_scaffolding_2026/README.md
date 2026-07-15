# root_scaffolding_2026 (archived)

These 11 root-level directories were flagged during
`adr/ADR-0037-governance-layer-overhaul.md`'s Stage 4 as an unaudited
cluster resembling `basis/`'s pre-overhaul pattern (mostly-unenforced
"repository operating system" prose), then actually audited and archived
in this follow-up pass, per the operator's explicit request.

Every file listed below was confirmed via `git grep` across `*.py`,
`*.yml`, `docs/`, `system/`, and `app/` to have **zero code or workflow
references** to its directory path before being moved. This is a
different verdict than `knowledge/`, `packs/`, and `inbox/` (also part of
the original 18-directory cluster) -- those three were confirmed
ENFORCED or code-adjacent and were deliberately **not** touched here; see
the audit findings referenced from `adr/ADR-0037` for the full per-directory
breakdown of all 18.

| Archived directory | Contents | Notes |
|---|---|---|
| `cache/` | `CONTEXT_CACHE.md`, `GRAPH_CACHE.md` | Both single-heading stubs, no content |
| `catalog/` | 15 files (taxonomy/model docs + 5 numbered placeholders `catalog_1..5.md`) | `TOOL_REGISTRY.md` here is a naming duplicate of the real, enforced `system/core/agent_role_registry.py` -- unrelated code, no shared data |
| `control/` | 9 files (4 "queue" docs + 5 numbered placeholders) | `HEALTH_QUEUE.md`, `ORPHAN_QUEUE.md`, `DRIFT_QUEUE.md`, `SELFTEST_QUEUE.md` are near-empty stub prose |
| `loader/` | `CONTEXT_LOADER.md` | 2-line stub |
| `prompts/` | `CODEX_IMPLEMENTER.md`, `CODEX_RELEASE.md`, `CODEX_REVIEWER.md` | Codex-role-specific prompt files that survived the `prompts/codex/*` subdirectory cleanup in `ADR-0037` Stage 1 because these three live directly in `prompts/`, not `prompts/codex/` -- same disposition, same reasoning, caught in this pass instead |
| `registry/` | 15 files (10 index docs + 5 numbered placeholders) | Pure name collision with several real, separately-implemented registries under `system/` (`agent_role_registry.py`, `business_registry.py`, `packs/registry.yaml`) -- no shared code or data path |
| `review/` | `REVIEW_ENGINE.md`, `REVIEW_GATE_SUMMARY.md` | Stub prose; the real review machinery is `app/tools/approval_console_mvp/` and `system/orchestrator/validation_orchestrator.py` |
| `rules/` | `IMPLEMENTATION_RULES.md`, `QUALITY_GATE.md`, `REVIEW_RULES.md` | No code references |
| `runbooks/` | 12 files (6 named runbooks + 5 numbered placeholders + `CODEX_EXECUTION_RUNBOOK.md`) | Referenced only by `system/orchestrator/CONTEXT_RESOLVER.md`, which is itself unreferenced prose -- a doc citing a doc, not enforcement |
| `solution/` | `requirements/schema/requirement.schema.json` | JSON Schema with no code validating against it |
| `templates/` | `ADR_TEMPLATE.md` | Unreferenced; `adr/` itself has no code-driven scaffolding tool that uses this template |

## `runtime/` (added in a follow-up pass)

| Archived directory | Contents | Notes |
|---|---|---|
| `runtime/planning/` | `PLANNING_STATE.md`, `latest.json`, `latest.md`, `planning_state.json` | Confirmed genuinely stale, not just a same-named coincidence: `current_pack` read `PACK-0001` here vs. `PACK-0004` in `system/runtime/planning/`, and this copy was missing several files (`autonomous_plan.json`, `background_system_image.json`, etc.) that `system/runtime/planning/` has since accumulated. Zero code references (both read and write sides checked via `git grep`) |
| `runtime/repository_state/` | `REPOSITORY_STATE.md`, `latest.json`, `latest.md`, `repository_state.json` | Byte-identical to `system/runtime/repository_state/`'s files at archival time (coincidence of not having drifted, not evidence of a live sync) -- zero code references |

**Root `scripts/` was investigated in the same pass and found NOT to be
stale scaffolding** -- `scripts/extract_knowledge.py` is a genuine,
intentional 13-line CLI wrapper (`from system.scripts.extract_knowledge
import main`) matching the documented human workflow in
[`docs/current/KNOWLEDGE_FACTORY.md`](../../docs/current/KNOWLEDGE_FACTORY.md).
Kept in place, not archived. See
[`docs/current/ROOT_ALLOWLIST.md`](../../docs/current/ROOT_ALLOWLIST.md)
for the full account of two prior incorrect guesses about this pair of
directories, corrected here.

## `queue/` (added in a second follow-up pass)

| Archived path | Contents | Notes |
|---|---|---|
| `queue/QUEUE_ENGINE.md` | 1 file | Prose describing a queue engine; `system/agent_runtime/queue_engine.py` is unrelated, separately-implemented code with no shared data path |
| `queue/READY/` | 46 `EP-*.md` proposal docs (EP-0145 through EP-0207) | Work-item proposals for the ChatGPT/Codex coordination layer (worker registry, execution kernel, event runtime, local supervisor daemon) that `adr/ADR-0032` already removed the *implementation* of. Files stay physically here, at their archived path |

**Correction: the original "zero `validate_ep_*.py` references" claim above
was wrong.** It was based on `git grep -l "queue/READY"`, a literal-substring
search -- but 7 of these scripts build the path from separate pathlib
components (`ROOT / "queue" / "READY" / "EP-XXXX-....md"`), which that
substring never matches. Running `python system/scripts/validate_all.py`
after the move caught the false negative immediately
(`validate_ep_0147.py` failed with a missing-file error). A corrected
search, `grep -l '"queue"' system/scripts/validate_ep_*.py`, found the real
list: `validate_ep_0147.py`, `validate_ep_0163.py`, `validate_ep_0173.py`,
`validate_ep_0174.py`, `validate_ep_0175.py`, `validate_ep_0176.py`,
`validate_ep_0177.py` -- each requires its own `queue/READY/EP-XXXX-*.md`
to exist. (`validate_ep_0163.py` in particular checks
`EP-0163-completion-marker-event-intake.md`, part of the separately
confirmed-live `AGENT_COMPLETION_CONTRACT` cluster
`system/orchestrator/completion_marker_event_intake.py` -- this file
being CI-required is not a coincidence.)

Fixed by repointing all 7 scripts' required path at this archive location
(`archive/root_scaffolding_2026/queue/READY/EP-XXXX-....md`) instead of the
original `queue/READY/`, matching the same pattern already used for
`semantic_checks.py`'s `REQUIRED_FILES`/`REQUIRED_DIRS` and
`validate_baseline.py`'s `REQUIRED` list earlier in this same governance
pass -- point the checklist at the new canonical location rather than
leaving it broken. Re-verified with
`python system/scripts/validate_all.py` (all EP scripts + full `pytest`
suite passing) before committing this move.

This is the third time this session a literal-substring `git grep` produced
a false negative against this codebase's `ROOT / "a" / "b" / "c"`
pathlib-join style. The reliable check is `grep -l '"<component>"'` across
each individual path segment, not the joined string.

**Also deleted (not archived) as a directly-related finding**: three
`system/runtime/queue/` files -- `next_work.json`, `queue_state.json`,
`autonomous_queue_runtime.json`. Confirmed via a full read of
`system/orchestrator/queue_state.py` (the module that owns the *real*,
enforced queue state) that it only ever reads/writes
`docs/current/QUEUE_STATE.md` -- it does not touch any of these three
files. A repo-wide `git grep` scoped to `*.py`/`*.yml` (to avoid false
matches inside large historical log blobs elsewhere in
`system/runtime/`) found zero references to any of the three filenames.
Their content was also demonstrably stale/placeholder
(`autonomous_queue_runtime.json` contained a literal
`"intake_request_id": "REQ-SAMPLE"`; `queue_state.json` referenced
`EP-0108`/`EP-0109`, long superseded). Deleted rather than archived,
consistent with how Stage 1 of `adr/ADR-0037` treated other orphaned
*generated* runtime snapshots (e.g. `agent_handoff/readiness.md`) --
archival is for documentation with real historical value; a stale,
zero-consumer JSON snapshot has none.

An initial attempt to delete these three files was correctly blocked by
the permission classifier, which noticed a contradiction with an
earlier, less rigorous research pass in this same session that had
described `next_work.json` as part of "the real, enforced queue"
without actually checking whether any code read it. The direct
verification above (full-file read of `queue_state.py`, `*.py`/`*.yml`-
scoped `git grep`) resolved the contradiction before proceeding --
recorded here as a second instance of the same lesson
`docs/current/ROOT_ALLOWLIST.md` already names: check, don't guess,
even when the "guess" is a callback to something said earlier in the
same investigation.

See [basis/README.md](../../basis/README.md) and
[adr/ADR-0037-governance-layer-overhaul.md](../../adr/ADR-0037-governance-layer-overhaul.md)
for the related `basis/` consolidation this follows the same pattern as.
