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

## Separately flagged, not archived here

While moving these 11 directories, two more root-level entries were
found that were **not** part of the originally-audited 18-directory
cluster and are **not** archived in this pass, since they weren't yet
verified safe: root-level `scripts/` (containing a shorter, differently-
implemented `extract_knowledge.py` than the real `system/scripts/
extract_knowledge.py`) and root-level `runtime/` (containing `planning/`
and `repository_state/` subdirectories that overlap in name, but not
exactly in content, with `system/runtime/planning/` and `system/runtime/
repository_state/`). These look like leftover pre-consolidation
duplicates of the real `system/` tree, not the same "unenforced prose"
pattern as the 11 above -- flagged for a separate, dedicated
investigation before any decision, not silently included here.

See [basis/README.md](../../basis/README.md) and
[adr/ADR-0037-governance-layer-overhaul.md](../../adr/ADR-0037-governance-layer-overhaul.md)
for the related `basis/` consolidation this follows the same pattern as.
