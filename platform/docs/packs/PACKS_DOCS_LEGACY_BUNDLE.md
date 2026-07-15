# Packs Docs Legacy Bundle

This file consolidates pack narrative docs that were previously split across many files.

## platform/docs/platform/packs/README_AGENT_ORCHESTRATOR_PACK.md

# ACIP Agent Orchestrator Pack

## Conclusion

This pack adds a repository-governed Agent Orchestrator preparation layer.

## Validation

```bash
python platform/scripts/graph/build_repository_graph.py
python platform/scripts/platform/context/build_agent_context_pack.py
python platform/scripts/orchestrator/build_context_bundle.py
python platform/scripts/orchestrator/build_execution_plan.py
python platform/scripts/orchestrator/validate_orchestration.py
```

## Generated Artifacts

- `orchestrator/context_bundle.json`
- `orchestrator/execution_plan.json`

## Boundary

This pack does not implement runtime execution.

Runtime agent execution, auto posting, platform API mutation, scraping-dependent automation, secret use, and approval bypass remain prohibited until explicit Human approval.

## Human Boundary

Human handles Mission, Approval, Emergency Stop, Risk Acceptance, Capital Allocation, and Runtime Transition Approval.

## platform/docs/platform/packs/README_AGENT_OS.md

# Agent OS README

## Conclusion

Agent OS defines the repository-governed operating boundary for ChatGPT, Codex, validation scripts, GitHub Actions, and future approved automation.

## Responsibilities

| Actor | Responsibility |
|---|---|
| Human | Mission / Approval / Emergency Stop |
| ChatGPT | CSO / Review / Priority / Planning / Delegation |
| Codex | Implementation / Test / Commit |
| Scripts | Deterministic validation |
| GitHub Actions | CI enforcement |
| Future Automation | Approved routine execution |

## Rule

Routine work must not default to Human.

## platform/docs/platform/packs/README_AGENT_OS_PACK.md

# Agent OS Pack

Repository overrides conversation.

Human handles only Mission, Approval, Emergency Stop.

Routine planning, delegation, validation, queue management, and metadata work should be handled by ChatGPT, Codex, scripts, GitHub Actions, or approved future automation.

## platform/docs/platform/packs/README_AGENT_RUNTIME_FOUNDATION_PACK.md

# Agent Runtime Foundation Pack
Run: python platform/scripts/runtime/validate_runtime_foundation.py

## platform/docs/platform/packs/README_ASSET_LIFECYCLE_PACK.md

# ACIP Asset Lifecycle Pack

## Conclusion

This pack extends Canonical Asset Production from definition into lifecycle control.

It does not introduce runtime automation, platform API integration, auto posting, scraping, or a new framework.

## Files

- `platform/basis/011_asset_lifecycle.md`
- `platform/basis/012_asset_repository_conventions.md`
- `platform/adr/ADR-0004-asset-lifecycle-control.md`
- `platform/docs/ASSET_LIFECYCLE_CHECKLIST.md`
- `platform/docs/ASSET_STATUS_MODEL.md`
- `platform/docs/ASSET_INDEX_TEMPLATE.md`
- `platform/docs/ASSET_CHANGELOG_TEMPLATE.md`
- `platform/wbs/WBS-0002-asset-lifecycle-control.md`
- `.github/ISSUE_TEMPLATE/asset_lifecycle.yml`
- `.github/workflows/asset-lifecycle-check.yml`
- `platform/scripts/validate_asset_lifecycle.py`

## Done Condition

1. Add the files to the repository root.
2. Run `python platform/scripts/validate_asset_lifecycle.py`.
3. Open a PR.
4. Confirm GitHub Actions workflow `Asset Lifecycle Check` passes.
5. Human approves and merges to `main`.

## platform/docs/platform/packs/README_ASSET_PRODUCTION_OPERATIONS_PACK.md

# ACIP Asset Production Operations Pack

## Conclusion

This pack adds repeatable production operations for Canonical Asset Production.

## Files

- `platform/basis/015_asset_intake_policy.md`
- `platform/basis/016_asset_production_workflow.md`
- `platform/basis/017_asset_review_cadence.md`
- `platform/basis/018_asset_output_policy.md`
- `platform/adr/ADR-0006-asset-production-operations.md`
- `platform/docs/ASSET_INTAKE_TEMPLATE.md`
- `platform/docs/ASSET_TRIAGE_TEMPLATE.md`
- `platform/docs/ASSET_PRODUCTION_CHECKLIST.md`
- `platform/docs/ASSET_REVIEW_CADENCE_CHECKLIST.md`
- `platform/docs/DERIVED_OUTPUT_TEMPLATE.md`
- `platform/docs/ASSET_PRODUCTION_OPERATIONS_CHECKLIST.md`
- `platform/wbs/WBS-0004-asset-production-operations.md`
- `.github/ISSUE_TEMPLATE/asset_intake.yml`
- `.github/ISSUE_TEMPLATE/asset_review_cadence.yml`
- `.github/workflows/asset-production-operations-check.yml`
- `platform/scripts/validate_asset_production_operations.py`

## Validation

```bash
python platform/scripts/validate_asset_production_operations.py
```

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, and new frameworks remain out of scope.

## platform/docs/platform/packs/README_ASSET_QUALITY_ROI_CLOSURE_PACK.md

# ACIP Asset Quality ROI Closure Pack

## Conclusion

This pack adds quality, ROI, risk, and closure controls for Canonical Asset Production.

## Files

- `platform/basis/019_asset_quality_policy.md`
- `platform/basis/020_asset_roi_policy.md`
- `platform/basis/021_asset_risk_policy.md`
- `platform/basis/022_asset_completion_policy.md`
- `platform/adr/ADR-0007-asset-quality-roi-risk-closure.md`
- `platform/docs/ASSET_QUALITY_SCORECARD.md`
- `platform/docs/ASSET_ROI_CANVAS.md`
- `platform/docs/ASSET_RISK_REVIEW.md`
- `platform/docs/CANONICAL_ASSET_PRODUCTION_CLOSURE_CHECKLIST.md`
- `platform/docs/HUMAN_APPROVAL_RECORD_TEMPLATE.md`
- `platform/wbs/WBS-0005-canonical-asset-production-closure.md`
- `.github/ISSUE_TEMPLATE/asset_quality_review.yml`
- `.github/ISSUE_TEMPLATE/canonical_asset_closure.yml`
- `.github/workflows/canonical-asset-production-closure-check.yml`
- `platform/scripts/validate_canonical_asset_production_closure.py`

## Validation

```bash
python platform/scripts/validate_canonical_asset_production_closure.py
```

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, architecture changes, and new frameworks remain out of scope.

## platform/docs/platform/packs/README_ASSET_REGISTRY_PACK.md

# ACIP Asset Registry Pack

## Conclusion

This pack adds Asset Registry and Traceability control for Canonical Asset Production.

## Files

- `platform/basis/013_asset_registry_policy.md`
- `platform/basis/014_asset_traceability_policy.md`
- `platform/adr/ADR-0005-asset-registry-traceability.md`
- `platform/docs/ASSET_REGISTRY_CHECKLIST.md`
- `platform/docs/ASSET_REGISTRY_TEMPLATE.md`
- `platform/docs/ASSET_TRACEABILITY_MAP_TEMPLATE.md`
- `registry/ASSET_REGISTRY.md`
- `platform/wbs/WBS-0003-asset-registry-traceability.md`
- `.github/ISSUE_TEMPLATE/asset_registry.yml`
- `.github/workflows/asset-registry-check.yml`
- `platform/scripts/validate_asset_registry.py`

## Validation

```bash
python platform/scripts/validate_asset_registry.py
```

## Scope

This pack is governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, and new application frameworks remain out of scope.

## platform/docs/platform/packs/README_AUTOMATION_PACK.md

# ACIP Automation Pack

## Conclusion

This pack adds the minimum files needed to close GitHub foundation automation without starting runtime automation.

## Files

```text
platform/docs/GITHUB_FOUNDATION_CHECKLIST.md
platform/basis/007_automation_scope.md
platform/adr/ADR-0002-foundation-automation.md
platform/scripts/validate_foundation.py
.github/workflows/foundation-check.yml
.github/ISSUE_TEMPLATE/foundation_completion.yml
```

## Apply

Copy these files into the ACIP repository root.

Then run:

```bash
python platform/scripts/validate_foundation.py
```

If validation passes, create a branch and PR.

## Done Condition

- local validation passes
- GitHub Actions validation passes
- Human approves PR
- PR merges into `main`

## Non-goal

This pack does not implement runtime automation, auto posting, platform API integration, or scraping.

## platform/docs/platform/packs/README_AUTONOMOUS_WORKFLOW_CONTROL_PACK.md

# ACIP Autonomous Workflow Control Pack

## Conclusion

This pack adds repository-governed autonomous workflow control without introducing runtime implementation.

## Validation

```bash
python platform/scripts/validate_autonomous_workflow_control.py
```

## Human Boundary

Human handles:

- Mission
- Approval
- Emergency Stop

Routine planning, queue management, validation, retry, PR review preparation, and status reporting should be delegated to ChatGPT, Codex, scripts, GitHub Actions, or future approved automation.

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, architecture changes, and new frameworks remain out of scope.

## platform/docs/platform/packs/README_CANONICAL_ASSET_PACK.md

# ACIP Canonical Asset Production Pack

## Conclusion

This pack defines the minimum repository documents required to execute the current objective: Canonical Asset Production.

It does not introduce runtime agents, posting automation, platform API integration, scraping, or new application frameworks.

## Files

- `platform/basis/008_canonical_asset_definition.md`
- `platform/basis/009_asset_production_policy.md`
- `platform/basis/010_quality_gate.md`
- `platform/adr/ADR-0003-canonical-asset-production.md`
- `platform/docs/CANONICAL_ASSET_PRODUCTION_CHECKLIST.md`
- `platform/docs/CANONICAL_ASSET_TEMPLATE.md`
- `platform/docs/ASSET_REVIEW_TEMPLATE.md`
- `platform/wbs/WBS-0001-canonical-asset-production.md`
- `.github/ISSUE_TEMPLATE/canonical_asset.yml`
- `.github/ISSUE_TEMPLATE/asset_review.yml`
- `platform/scripts/validate_canonical_assets.py`
- `.github/workflows/canonical-asset-check.yml`

## Execution

1. Copy all files into the repository root.
2. Run `python platform/scripts/validate_canonical_assets.py`.
3. Open a PR.
4. Confirm `Canonical Asset Check` passes.
5. Merge only after Human approval.

## Done Condition

The pack is complete when canonical asset documents, templates, WBS, and validation checks exist in the repository and pass CI.

## platform/docs/platform/packs/README_CATALOG_LAYER_PACK.md

# ACIP Catalog Layer Pack

## Conclusion

This pack adds Catalog, Search, Relationship, and Autonomy First governance for Knowledge Factory operations.

## Files

- `platform/basis/023_catalog_policy.md`
- `platform/basis/024_tag_policy.md`
- `platform/basis/025_searchability_policy.md`
- `platform/basis/026_autonomy_first_policy.md`
- `platform/adr/ADR-0008-catalog-and-search-governance.md`
- `platform/adr/ADR-0009-autonomy-first-operating-boundary.md`
- `registry/KNOWLEDGE_INDEX.md`
- `registry/CONTENT_INDEX.md`
- `registry/MEDIA_INDEX.md`
- `registry/OPERATIONAL_INDEX.md`
- `registry/DEPRECATED_INDEX.md`
- `catalog/CATEGORY_TAXONOMY.md`
- `catalog/TAG_STANDARD.md`
- `catalog/NAMING_STANDARD.md`
- `catalog/SEARCH_GUIDELINE.md`
- `catalog/RELATIONSHIP_MODEL.md`
- `platform/docs/CATALOG_ENTRY_TEMPLATE.md`
- `platform/docs/KNOWLEDGE_CARD_TEMPLATE.md`
- `platform/docs/SEARCH_METADATA_TEMPLATE.md`
- `platform/docs/CATALOG_LAYER_CHECKLIST.md`
- `platform/wbs/WBS-0006-catalog-layer.md`
- `.github/ISSUE_TEMPLATE/catalog_update.yml`
- `.github/workflows/catalog-layer-check.yml`
- `platform/scripts/validate_catalog_layer.py`

## Validation

```bash
python platform/scripts/validate_catalog_layer.py
```

## Human Boundary

Human should only handle Mission, Approval, Emergency Stop, risk acceptance, capital allocation, and final strategic judgment.

Routine catalog hygiene, metadata normalization, duplicate detection, checklist execution, and validation should be delegated to ChatGPT, Codex, scripts, GitHub Actions, or future approved automation.

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, architecture changes, and new frameworks remain out of scope.

## platform/docs/platform/packs/README_GOVERNANCE.md

# Governance README

## Conclusion

Governance exists to preserve robustness, maintainability, reproducibility, ROI, and Human boundary clarity.

## Core Rules

- Repository overrides conversation.
- Current Objective must not change without approval.
- Execution First.
- Human handles Mission / Approval / Emergency Stop.
- Runtime implementation remains out of scope until explicitly approved.

## platform/docs/platform/packs/README_KNOWLEDGE_FACTORY.md

# Knowledge Factory README

## Conclusion

Knowledge Factory converts Human mission and reusable knowledge into repository-governed Canonical Assets.

## Components

- Canonical Asset definition
- Asset lifecycle
- Asset registry
- Traceability
- Production operations
- Quality / ROI / Risk
- Catalog / Search / Relationship model

## Rule

Repository overrides conversation.

Human should not perform routine asset hygiene when ChatGPT, Codex, scripts, GitHub Actions, or approved automation can do it.

## platform/docs/platform/packs/README_REPOSITORY_COMPLETE_PACK.md

# ACIP Repository Complete Pack

## Conclusion

This pack consolidates Knowledge Factory, Canonical Asset Production, Catalog Layer, Agent OS Foundation, Autonomous Workflow Control, Execution Contract, Safety Gate, Handoff, and Runtime Readiness governance into one repository update.

## Human Boundary

Human handles:

- Mission
- Approval
- Emergency Stop
- Risk Acceptance
- Capital Allocation
- Runtime Transition Approval

Routine execution, drafting, validation, checklist execution, queue hygiene, registry hygiene, catalog hygiene, PR review preparation, status reporting, and mechanical retries should be delegated to ChatGPT, Codex, scripts, GitHub Actions, or future approved automation.

## Repository Rule

Repository overrides conversation.

## Validation

Run:

```bash
python platform/scripts/validate_all.py
```

Individual validators:

```bash
python platform/scripts/validate_governance.py
python platform/scripts/validate_knowledge_factory.py
python platform/scripts/validate_agent_os_foundation.py
python platform/scripts/validate_runtime_readiness.py
```

## Scope

Governance-only.

Runtime implementation, auto posting, platform API integration, scraping-dependent workflows, external databases, architecture changes, and new frameworks remain out of scope unless explicitly approved.

## platform/docs/platform/packs/README_REPOSITORY_KNOWLEDGE_GRAPH_RUNTIME_INTEGRATION_PACK.md

# ACIP Repository Knowledge Graph Runtime Integration Pack

## Conclusion

This pack prepares ACIP for runtime integration without starting runtime execution.

## Included

- Repository Knowledge Graph policy
- Graph extraction policy
- Agent Context Pack policy
- Runtime Integration Boundary policy
- Agent IO Contract policy
- Runtime Dry Run policy
- ADR-0019
- ADR-0020
- WBS-0013
- graph schemas
- context pack schemas
- runtime specs
- graph extraction scripts
- graph validation scripts
- context pack builder
- runtime dry-run planner
- GitHub Actions workflow

## Validation

```bash
python platform/scripts/validate_repository_knowledge_graph_runtime_integration.py
```

## Boundary

Runtime implementation, platform API integration, auto posting, scraping-dependent automation, secret use, and autonomous external actions remain prohibited until explicit Human approval.

## platform/docs/platform/packs/README_REPOSITORY_OS_V1_BASELINE_PACK.md

# ACIP Repository OS v1 Baseline Pack

## Conclusion

This pack freezes Repository OS v1.0 as the baseline for future Runtime and Agent development.

## Version

`1.0.0-repository-os`

## Validation

```bash
python platform/scripts/validate_repository_os_v1_baseline.py
```

## Generated Artifacts

- `graph/repository_graph_delta.json`
- `graph/context_diff.json`
- `orchestrator/EXECUTION_QUEUE.md`
- `review/REVIEW_GATE_SUMMARY.md`

## Boundary

Runtime execution remains prohibited until explicit Human approval.

## platform/docs/platform/packs/README_REPOSITORY_SELFTEST_COMPLETE_PACK.md

# ACIP Repository Self Test Complete Pack

## Conclusion

This pack replaces the prior Self Test skeleton with implementation-backed repository self-test.

## Included Checks

- Repository Health
- Boundary Validation
- Secret Boundary
- Link Integrity
- Duplicate Detection
- Orphan / Dead Document Detection
- Workflow-Script Consistency
- Current Objective Drift Detection

## Validation

```bash
python platform/scripts/selftest/validate_repository_selftest_complete.py
```

Compatibility:

```bash
python platform/scripts/validate_repository_selftest.py
python platform/scripts/validate_continuous_governance.py
```

## Human Boundary

Human handles Mission, Approval, Emergency Stop, Risk Acceptance, Capital Allocation, and runtime transition approval.

Routine repository inspection should be delegated to scripts, GitHub Actions, Codex, ChatGPT, or approved future automation.

## platform/docs/platform/packs/README_RUNTIME_READINESS.md

# Runtime Readiness README

## Conclusion

Runtime implementation must not begin until Runtime Readiness is approved by Human.

## Required Before Runtime

- Execution Contract
- Safety Gates
- Approval Gates
- Handoff Contracts
- Rollback Plan
- Emergency Stop
- Secret Boundary
- External Action Boundary
- Runtime Scope Approval
- Validation Plan

## Prohibited Before Approval

- runtime agent execution
- auto posting
- platform API integration
- scraping-dependent automation
- autonomous external actions
- approval bypass

## platform/docs/platform/packs/README_RUNTIME_TRANSITION_READINESS_PACK.md

# Runtime Transition Readiness Pack
Validate:
python platform/scripts/validate_repository_knowledge_graph_runtime_integration.py

## platform/docs/platform/packs/README_SELFTEST_IMPORT_FIX_PACK.md

# ACIP SelfTest Import Fix Pack

## Conclusion

This pack fixes the `ImportError: cannot import name 'fail' from 'selftest_common'`.

## Cause

Some existing selftest modules still import `fail`, while the remediation pack renamed the function to `issue`.

## Fix

`selftest_common.py` now exposes `fail()` as a backward-compatible alias to `issue()`.

## Validation

Run:

```bash
python platform/scripts/selftest/validate_repository_selftest_complete.py
```

## platform/docs/platform/packs/README_SELFTEST_REMEDIATION_PACK.md

# ACIP SelfTest Remediation Pack

## Conclusion

This pack remediates the first SelfTest Complete run.

## Primary Fix

The previous self-test was useful because it exposed real repository debt and validator false positives. This pack fixes both categories.

## Validation

```bash
python platform/scripts/selftest/validate_repository_selftest_complete.py
```

## Optional Cleanup

```bash
python platform/scripts/selftest/cleanup_selftest_skeleton.py
```

## Human Boundary

Human should not manually clean duplicate skeleton files. Codex should run the cleanup script and commit the resulting moves when accepted.

## platform/docs/platform/packs/README_SEMANTIC_SELFTEST_V2_PACK.md

# ACIP Repository Semantic SelfTest v2 Pack

## Conclusion

This pack replaces raw lint-style SelfTest behavior with configuration-driven semantic analysis.

## Why

The prior SelfTest correctly found real missing files and boundary risks, but it also produced false positives:

- archived files counted as duplicate canonical ADR/WBS
- explanatory mentions of Current Objective counted as drift
- drafts/templates/reports/indexes counted as orphan documents
- selftest scripts matched their own prohibited keyword constants

## Validation

```bash
python platform/scripts/selftest_v2/validate_semantic_selftest.py
```

Compatibility:

```bash
python platform/scripts/selftest/validate_repository_selftest_complete.py
python platform/scripts/validate_repository_selftest.py
```

## Configuration

`selftest.yml`

## Human Boundary

Human should receive only decision-ready reports. Routine repository inspection should be delegated to SelfTest, Codex, ChatGPT, GitHub Actions, or future approved automation.

