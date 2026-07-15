# basis_corpus_2026 (archived)

These 43 files were the bulk of `platform/basis/`'s original policy corpus, archived
in one pass as part of a full governance-layer review
(`platform/adr/ADR-0037-governance-layer-overhaul.md`). The review found that almost
all of them were pure prose describing intended policy with no enforcing
code behind them, several restated the identical concern in separate,
independently-drifting copies, and roughly a third were explicitly
unauthored stub placeholders per `platform/basis/README.md`'s own index.

The current, compact replacement is [`platform/basis/CORE_PRINCIPLES.md`](../../platform/basis/CORE_PRINCIPLES.md)
— 9 principles, each one traced to either something genuinely enforced by
real code today or something genuinely durable. Two files stayed standalone
in `platform/basis/` rather than being folded in or archived:
[`057_boundary_validation_policy.md`](../../platform/basis/057_boundary_validation_policy.md)
(maps to real, distinct enforcement) and
[`REPOSITORY_CONVENTIONS.md`](../../platform/basis/REPOSITORY_CONVENTIONS.md)
(actively used naming reference).

Kept here for history per this repo's own established convention (see
`AGENTS.md`/`platform/.platform/system/*`, kept as historical record rather than deleted) and
per the prior archival precedent this follows,
[`archive/basis_skeleton/`](../basis_skeleton/README.md). Archive space may
duplicate numbers/titles and is excluded from canonical duplicate/orphan
checks (this was itself the subject of one of the archived files,
`064_selftest_v2_archive_policy.md`).

## Actor boundary — grouped under `CORE_PRINCIPLES.md` §4 (human approval gate) and §2 (human-in-the-loop)

| Archived file | What it covered | Where the real content lives now |
|---|---|---|
| `026_autonomy_first_policy.md` | Human owns Mission/Approval/Emergency Stop/Risk/Capital/Runtime Transition; everything else defaults to automation | `CLAUDE.md`'s "Human keeps: strategy, approval, capital allocation" + `CORE_PRINCIPLES.md` §4 |
| `042_execution_contract_policy.md` | Every autonomous/semi-autonomous execution needs an Execution Contract before automation acts | `CORE_PRINCIPLES.md` §2/§3 — approval is explicit, never inferred |
| `073_task_router_policy.md` | Routing table of work type → owner (Human/ChatGPT/Codex/platform/scripts/CI) | Superseded outright — there is no multi-actor routing anymore; `CLAUDE.md`'s "Operating model" describes the current single-agent-plus-human shape |
| `074_context_resolution_policy.md` | Context priority order: conventions > current state > architecture > ADR > WBS > graph > context pack > conversation | Superseded by `platform/docs/current/STATE.md`'s "Repository Priority" chain (updated in the same overhaul, Stage 4), which drops the never-built graph/context-pack layers |

## Repository health & self-test — grouped under `CORE_PRINCIPLES.md` §7 (avoid duplication) and real CI

| Archived file | What it covered | Where the real content lives now |
|---|---|---|
| `053_repository_selftest_policy.md` | Self-test must mechanically verify the repository OS | `platform/system/platform/scripts/selftest_v2/*`, wired into `.github/workflows/repository-semantic-selftest-v2.yml` (live) |
| `054_repository_health_policy.md` | Health = required dirs/files, executable validators, CI, no committed secrets | `python platform/system/platform/scripts/validate_all.py` + CI workflows (live) |
| `055_dead_asset_detection_policy.md` | Dead-document signals (no inbound reference, missing title) | `semantic_checks.py`'s orphan detection (live) |
| `056_link_integrity_policy.md` | Repository links must stay auditable | Not currently wired as a dedicated check; aspirational |
| `058_drift_detection_policy.md` | Drift = files/policies contradicting the active operating model, must be reported | Not currently wired as a dedicated check; aspirational — this review (`ADR-0037`) is itself an instance of manually catching drift `058` describes |
| `059_duplicate_detection_policy.md` | Duplicate governance docs create ambiguity | `semantic_checks.py`'s duplicate detection (live) |
| `060_continuous_governance_policy.md` | CI must run self-test/boundary/link/secret/runtime-readiness checks on PRs | Governance Stage 2 of this same overhaul actually cleaned up CI to match this intent — see `.github/workflows/` |
| `061_semantic_selftest_policy.md` | Self-test v2 must separate canonical/archive/draft/template/report/index space | `selftest_v2/` itself, which this file described before it was built |
| `063_selftest_v2_boundary_policy.md` | Boundary checks must distinguish prohibited execution from text merely describing the boundary | Implemented directly in `semantic_checks.py` |
| `064_selftest_v2_archive_policy.md` | `archive/**` is historical space: may duplicate numbers, may be unreferenced, still scanned for secrets | This very archive follows that policy; the policy's principle is now just an implicit repo convention rather than a standalone file |

## Knowledge graph & context — never built beyond stubs; archived without a live replacement

| Archived file | Status |
|---|---|
| `062_policy_graph_policy.md` | Aspirational — no dedicated graph-build code exists |
| `065_repository_knowledge_graph_policy.md` | Aspirational — the "knowledge graph" concept was largely removed by the earlier ADR-0032 cleanup |
| `066_graph_extraction_policy.md` | Aspirational, never built |
| `067_agent_context_pack_policy.md` | Aspirational — the actual `platform/context/CHATGPT_CONTEXT_PACK.md`/`CODEX_CONTEXT_PACK.md` stub docs it described were deleted in Stage 1 of this same overhaul |
| `078_incremental_graph_policy.md` | Confirmed stub — boilerplate placeholder, never authored |
| `079_context_diff_policy.md` | Confirmed stub — boilerplate placeholder, never authored |
| `082_context_loader_policy.md` | Confirmed stub — two-line placeholder, never authored |
| `084_graph_cache_policy.md` | Confirmed stub — one line, never authored |

## Runtime transition & agent execution boundary — grouped under `CORE_PRINCIPLES.md` §2

| Archived file | What it covered | Where the real content lives now |
|---|---|---|
| `037_autonomous_workflow_policy.md` | "Prohibited Until Approval" list (one of 5 near-identical copies) | `CORE_PRINCIPLES.md` §2 — merged into one principle |
| `046_runtime_readiness_boundary.md` | Same list, second copy | `CORE_PRINCIPLES.md` §2 |
| `068_runtime_integration_boundary_policy.md` | Same list, third copy | `CORE_PRINCIPLES.md` §2 |
| `070_runtime_dry_run_policy.md` | Same list, fourth copy ("Dry Run Must Not...") | `CORE_PRINCIPLES.md` §2 |
| `072_agent_orchestrator_policy.md` | Same list, fifth copy ("Runtime Boundary") | `CORE_PRINCIPLES.md` §2 |
| `069_agent_io_contract_policy.md` | Agent IO contracts must declare input/output/mutations/validation/rollback/approval | Aspirational, never built as a standalone contract format — Level 3a/3c's real code covers the load-bearing parts (approval, caps, kill switches) |
| `071_runtime_transition_readiness_policy.md` | Runtime transition requires evidence: self-test pass, dry-run pass, recorded approval, rollback, emergency stop | Aspirational; the real, live equivalent is `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md`'s Level 0-3c readiness criteria |
| `091_agent_runtime_mvp_policy.md` | Agent Runtime MVP: local dry-run planning only, no external mutation | Superseded — the "Agent Runtime" concept this described was mostly removed by the earlier ADR-0032 cleanup |
| `092_agent_runtime_task_intake_policy.md` | Runtime may intake repo-defined tasks for dry-run planning only | Same cluster as `091`, same disposition |

## Execution queue & review — mix of aspirational and superseded-by-real-implementation

| Archived file | What it covered | Where the real content lives now |
|---|---|---|
| `075_execution_queue_policy.md` | Queue item schema (task_id, objective, owner, context_bundle, validation_command, status) | Superseded by the real, live business-agent task queue (`platform/system/core/business_agent_task_queue.py` and friends) — different, simpler shape than this schema described |
| `076_review_gate_policy.md` | Review gates turn execution output into decision-ready summaries | Superseded by `platform/app/tools/approval_console_mvp/` — the real, live implementation |
| `077_baseline_policy.md` | Confirmed stub — boilerplate placeholder | Never authored |
| `080_execution_queue_automation_policy.md` | Confirmed stub — boilerplate placeholder | Never authored |
| `081_review_gate_summary_policy.md` | Confirmed stub — boilerplate placeholder | Never authored |
| `083_incremental_execution_policy.md` | Confirmed stub — one line ("only changed assets rebuilt") | Never authored |
| `085_review_engine_policy.md` | Confirmed stub — one line ("review before runtime") | Never authored |
| `086_queue_coordination_policy.md` | Confirmed stub — one line ("repository overrides conversation") | Never authored |
| `087_approval_gate_engine_policy.md` | Confirmed stub — one line ("approval required for runtime transition") | Never authored |
| `088_context_cache_engine_policy.md` | Confirmed stub — title only | Never authored |
| `089_replay_engine_policy.md` | Confirmed stub — title only | Never authored |
| `090_audit_engine_policy.md` | Confirmed stub — title only | Never authored |

See [platform/basis/README.md](../../platform/basis/README.md) for the current index.
