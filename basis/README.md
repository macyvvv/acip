# basis/README

`basis/` is ACIP's policy corpus — the permanent bound-volume record of why
the repository is governed the way it is. Per repository-wide convention
this directory is always kept; this file is the index that makes it
navigable, since nothing else in the repo links into it (confirmed by
`system/scripts/selftest/check_orphans.py` — every file below had zero
inbound markdown references before this index existed).

Numbering note: numbers are not contiguous or unique. 001-025 are referenced
by `docs/packs/README_*.md` but no longer exist in this directory (lost at
some point, not reconstructed here). Several numbers in the 053-060 range
were reused by an early placeholder pass; those stub duplicates have been
moved to [archive/basis_skeleton/](../archive/basis_skeleton/README.md) and
are not listed below. What remains is the current, non-duplicated set.

## Actor boundary (who does what)

- [026_autonomy_first_policy.md](026_autonomy_first_policy.md) — Human owns Mission/Approval/Emergency Stop/Risk/Capital/Runtime Transition; everything else defaults to ChatGPT/Codex/scripts/automation.
- [037_autonomous_workflow_policy.md](037_autonomous_workflow_policy.md) — Autonomous workflows convert Human mission into repo-governed execution; lists actions prohibited until approval (runtime execution, auto-posting, platform API, scraping, approval bypass).
- [042_execution_contract_policy.md](042_execution_contract_policy.md) — Every autonomous/semi-autonomous execution needs an Execution Contract before Codex/automation acts.
- [046_runtime_readiness_boundary.md](046_runtime_readiness_boundary.md) — Runtime implementation is blocked until governance, contracts, safety gates, handoffs, approval gates, rollback, and secret boundaries all exist.
- [073_task_router_policy.md](073_task_router_policy.md) — Routing table of work type -> owner (Human/ChatGPT/Codex/scripts/CI/automation); Human must not receive routine execution work.
- [REPOSITORY_CONVENTIONS.md](REPOSITORY_CONVENTIONS.md) — Repository is SSOT, not conversation; naming conventions (UPPER_SNAKE_CASE docs, lower_snake_case code/dirs).

## Repository health & self-test

- [053_repository_selftest_policy.md](053_repository_selftest_policy.md) — Self-test must mechanically and continuously verify the repository OS; enumerates required checks (health, required files, link integrity, boundary preservation, duplicate/orphan/dead-doc detection, objective drift, prohibited keywords).
- [054_repository_health_policy.md](054_repository_health_policy.md) — Health = minimum operating condition: required dirs/files, executable validation scripts, CI workflows, no committed secrets, no prohibited runtime actions.
- [055_dead_asset_detection_policy.md](055_dead_asset_detection_policy.md) — Defines dead-document signals (no inbound reference, missing title, unreferenced by index/ADR/WBS); dead docs are surfaced for review, not auto-deleted.
- [056_link_integrity_policy.md](056_link_integrity_policy.md) — Repository links (ADR/WBS/policy/runbook/template chains) must stay auditable; broken links and missing validation targets must fail self-test.
- [057_boundary_validation_policy.md](057_boundary_validation_policy.md) — Enumerates the boundaries (Human, Runtime, Secret, External Action, Current Objective) and what constitutes a blocking violation of each.
- [058_drift_detection_policy.md](058_drift_detection_policy.md) — Drift = files/policies/ADRs contradicting the active operating model; must be reported with file path, evidence, and recommended owner.
- [059_duplicate_detection_policy.md](059_duplicate_detection_policy.md) — Duplicate governance docs create ambiguity; signals include identical H1s, repeated ADR/WBS numbers, repeated workflow names. Fails only on canonical ambiguity, otherwise warns.
- [060_continuous_governance_policy.md](060_continuous_governance_policy.md) — CI must run self-test, boundary validation, link integrity, secret scan, and runtime-readiness check on PRs and on demand; CI should reduce, not increase, human review burden.
- [061_semantic_selftest_policy.md](061_semantic_selftest_policy.md) — Self-test v2 must separate canonical/archive/draft/template/report/index space to stop the v1 false positives that flagged archives and templates as violations.
- [063_selftest_v2_boundary_policy.md](063_selftest_v2_boundary_policy.md) — Boundary checks must distinguish prohibited execution from text that merely *describes* the boundary (e.g. "auto posting is prohibited" is a valid mention, not a violation).
- [064_selftest_v2_archive_policy.md](064_selftest_v2_archive_policy.md) — `archive/**` is historical space: may duplicate ADR/WBS numbers, may be unreferenced, but must still be scanned for secrets.

**Known gap:** the checks this section describes (`check_orphans.py`, `check_duplicates.py`, `check_repository_health.py`, and the rest of `system/scripts/selftest/` and `selftest_v2/`) are not invoked by `validate_all.py` or wired into any `.github/workflows/*.yml`. The policy describes continuous governance; nothing currently runs it continuously.

## Knowledge graph & context

- [062_policy_graph_policy.md](062_policy_graph_policy.md) — Repository validation should model policy/ADR/WBS/runbook/contract/workflow relationships as a graph; semantic warnings are advisory unless they hit broken links, duplicate IDs, boundary violations, or missing files.
- [065_repository_knowledge_graph_policy.md](065_repository_knowledge_graph_policy.md) — Maintain a repository knowledge graph so ChatGPT/Codex/agents reason from shared structure; the graph is derived, source files stay canonical.
- [066_graph_extraction_policy.md](066_graph_extraction_policy.md) — Extraction must be deterministic, reproducible, non-mutating, and not require secrets or external calls.
- [067_agent_context_pack_policy.md](067_agent_context_pack_policy.md) — Context packs provide bounded repo context (purpose, actor, phase, objective, allowed/excluded paths, validation command); read-only, no secrets.
- [074_context_resolution_policy.md](074_context_resolution_policy.md) — Context priority order: conventions > current state > architecture > ADR > WBS > graph artifacts > context pack > conversation.
- [078_incremental_graph_policy.md](078_incremental_graph_policy.md) — stub: boilerplate placeholder text only, not authored yet.
- [079_context_diff_policy.md](079_context_diff_policy.md) — stub: boilerplate placeholder text only, not authored yet.
- [082_context_loader_policy.md](082_context_loader_policy.md) — stub: two-line placeholder ("repository overrides conversation", "runtime execution prohibited"), not authored yet.
- [084_graph_cache_policy.md](084_graph_cache_policy.md) — stub: one line ("derived cache only"), not authored yet.

## Runtime transition & agent execution boundary

- [068_runtime_integration_boundary_policy.md](068_runtime_integration_boundary_policy.md) — What's allowed (specs, schemas, context packs, dry-run) vs. prohibited (external mutation, auto-posting, scraping, live execution) before human runtime approval.
- [069_agent_io_contract_policy.md](069_agent_io_contract_policy.md) — Agent IO contracts must declare input source, output target, allowed/prohibited mutations, validation command, rollback path, approval requirement, emergency-stop condition.
- [070_runtime_dry_run_policy.md](070_runtime_dry_run_policy.md) — Dry-run is allowed pre-approval only if it performs no external actions and no mutation; output is advisory.
- [071_runtime_transition_readiness_policy.md](071_runtime_transition_readiness_policy.md) — Runtime transition requires evidence, not optimism: self-test pass, graph generated, context pack generated, dry-run pass, recorded human approval, defined rollback and emergency stop.
- [072_agent_orchestrator_policy.md](072_agent_orchestrator_policy.md) — The orchestrator routes tasks to the correct actor from repository-derived context while preserving the Human and Runtime boundaries.
- [091_agent_runtime_mvp_policy.md](091_agent_runtime_mvp_policy.md) — Agent Runtime MVP may only do local dry-run planning (read repo/graph/context, generate plans/queue items/reviews); no external mutation.
- [092_agent_runtime_task_intake_policy.md](092_agent_runtime_task_intake_policy.md) — Runtime may intake repository-defined tasks for dry-run planning only; no external execution.

## Execution queue & review

- [075_execution_queue_policy.md](075_execution_queue_policy.md) — Queue item schema (task_id, objective, owner, context_bundle, validation_command, status) and status values (ready/executing/blocked/review/done/parked/escalated).
- [076_review_gate_policy.md](076_review_gate_policy.md) — Review gates turn execution output into decision-ready summaries; Human only reviews decisions, not raw output.
- [077_baseline_policy.md](077_baseline_policy.md) — stub: boilerplate placeholder text only, not authored yet.
- [080_execution_queue_automation_policy.md](080_execution_queue_automation_policy.md) — stub: boilerplate placeholder text only, not authored yet.
- [081_review_gate_summary_policy.md](081_review_gate_summary_policy.md) — stub: boilerplate placeholder text only, not authored yet.
- [083_incremental_execution_policy.md](083_incremental_execution_policy.md) — stub: one line ("only changed assets rebuilt"), not authored yet.
- [085_review_engine_policy.md](085_review_engine_policy.md) — stub: one line ("review before runtime"), not authored yet.
- [086_queue_coordination_policy.md](086_queue_coordination_policy.md) — stub: one line ("repository overrides conversation"), not authored yet.
- [087_approval_gate_engine_policy.md](087_approval_gate_engine_policy.md) — stub: one line ("approval required for runtime transition"), not authored yet.
- [088_context_cache_engine_policy.md](088_context_cache_engine_policy.md) — stub: title only, no body.
- [089_replay_engine_policy.md](089_replay_engine_policy.md) — stub: title only, no body.
- [090_audit_engine_policy.md](090_audit_engine_policy.md) — stub: title only, no body.

## Reading this corpus going forward

- Files marked "stub" above are placeholders, not adopted policy — treat their topic as unwritten, not as a real constraint.
- If you're about to write real content for a stub, do it in place (same filename) and update its one-line summary here.
- If you add a new policy, append it to the relevant section above in the same PR — an unlinked `basis/` file is exactly the problem this index exists to fix.
