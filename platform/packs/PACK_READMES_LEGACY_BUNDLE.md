# Pack READMEs Legacy Bundle

This file consolidates per-pack README prose. Canonical package metadata remains in each pack.yaml.

## platform/packs/PACK-0001-solution-development/README.md

# PACK-0001 Solution Development Pack

Repository-driven solution development from requirements to runtime handoff.

## platform/packs/PACK-0003-generated-artifact-ssot/README.md

# PACK-0003 Generated Artifact SSOT Pack

Parent issue: #3

## Purpose
Ensure validation is read-only by default and generated artifacts are tracked as repository-managed outputs.

## Child EPs
- EP-0151 Generated Artifact Registry Enforcement
- EP-0152 Validation Read-Only Mode
- EP-0153 Runtime Artifact Write Policy
- EP-0154 Worktree Cleanliness Gate
- EP-0155 Generated Artifact Refresh Command

## Execution Record
- EP-0151 -> commit 3b97372
- EP-0152 -> commit 6624ee4
- EP-0153 -> commit 03b7108
- EP-0154 -> commit 33d06d4
- EP-0155 -> commit 655ce87

## platform/packs/PACK-0004-agent-handshake-protocol/README.md

# PACK-0004 Agent Handshake Protocol

## Canonical Input

- `queue/READY/EP-0156-completion-protocol.md`
- `queue/READY/EP-0157-repository-completion-marker.md`
- `queue/READY/EP-0158-chatgpt-review-intake.md`
- `queue/READY/EP-0159-issue-synchronizer.md`
- `queue/READY/EP-0160-handshake-validation.md`

## Purpose

- Make Codex completion machine readable.
- Make ChatGPT review intake deterministic.
- Keep issue synchronization repository-native.

## Status

- READY

## platform/packs/PACK-0005-event-runtime/README.md

# PACK-0005 Event Runtime

## Canonical Input

- `queue/READY/EP-0161-event-contract.md`
- `queue/READY/EP-0162-issue-event-intake.md`
- `queue/READY/EP-0163-completion-marker-event-intake.md`
- `queue/READY/EP-0164-event-to-queue-resolver.md`
- `queue/READY/EP-0165-event-runtime-dry-run.md`
- `queue/READY/EP-0166-event-runtime-safety-gate.md`

## Purpose

- Detect eligible events deterministically.
- Resolve the next work item or approval hold.
- Keep the event runtime local and safe by default.

## Status

- READY

## platform/packs/PACK-0006-external-trigger-bridge/README.md

# PACK-0006 External Trigger Bridge

## Canonical Input

- `queue/READY/EP-0167-github-actions-event-fixture.md`
- `queue/READY/EP-0168-workflow-dispatch-runtime.md`
- `queue/READY/EP-0169-event-runtime-cli-entrance.md`
- `queue/READY/EP-0170-codex-intake-trigger-contract.md`
- `queue/READY/EP-0171-approval-hold-workflow.md`
- `queue/READY/EP-0172-external-trigger-dry-run-validation.md`

## Purpose

- Bridge GitHub events or workflow dispatch into the repository event runtime.
- Produce Codex intake trigger data or approval-hold decisions.
- Keep the bridge deterministic and safe.

## Status

- READY

## platform/packs/PACK-0007-repository-structure-hygiene/README.md

# PACK-0007 Repository Structure Hygiene

## Canonical Input

- `queue/READY/EP-0173-root-inventory-and-classification.md`
- `queue/READY/EP-0174-target-layout-contract.md`
- `queue/READY/EP-0175-reference-impact-analyzer.md`
- `queue/READY/EP-0176-root-migration-dry-run.md`
- `queue/READY/EP-0177-root-migration-approval-gate.md`
- `queue/READY/EP-0178-root-migration-execution.md`
- `queue/READY/EP-0179-layout-enforcement-gate.md`

## Purpose

- Classify root entries.
- Define a target layout contract.
- Analyze reference impact before any move.
- Keep migration execution blocked until approval.

## Status

- READY

## platform/packs/PACK-0011-local-agent-supervisor-bridge/README.md

# PACK-0011 Local Agent Supervisor Bridge

## Canonical Input

- `queue/READY/EP-0187-local-supervisor-contract.md`
- `queue/READY/EP-0188-work-discovery-loop.md`
- `queue/READY/EP-0189-codex-intake-adapter.md`
- `queue/READY/EP-0190-execution-launch-contract.md`
- `queue/READY/EP-0191-completion-capture-adapter.md`
- `queue/READY/EP-0192-supervisor-safety-gate.md`
- `queue/READY/EP-0193-supervisor-dry-run-validation.md`

## Purpose

- Eliminate Human as the ChatGPT-to-Codex courier after local startup.
- Bridge Planning State, Repository State, and execution intake through repository artifacts.

## Status

- READY

## platform/packs/PACK-0012-work-planner/README.md

# PACK-0012 Work Planner

## Canonical Input

- `queue/READY/EP-0194-work-planner-contract.md`
- `queue/READY/EP-0195-candidate-source-aggregator.md`
- `queue/READY/EP-0196-work-candidate-scoring-model.md`
- `queue/READY/EP-0197-issue-candidate-renderer.md`
- `queue/READY/EP-0198-parking-lot-and-blocked-candidate-handling.md`
- `queue/READY/EP-0199-work-planner-review-gate.md`
- `queue/READY/EP-0200-work-planner-validation.md`

## Purpose

- Produce prioritized next-work candidates from repository projections.
- Keep recommendations deterministic and reviewable.

## Status

- READY

## platform/packs/PACK-0013-repository-os-v2-release/README.md

# PACK-0013 Repository OS v2 Release

## Canonical Input

- Repository Constitution
- Planning State
- Repository State
- Supervisor projection
- Work Planner projection

## Purpose

Freeze Repository OS v2 as the operational baseline before product development begins.

## Status

- READY

## platform/packs/PACK-0014-first-product-launch-platform/system/README.md

# PACK-0014 First Product Launch System

## Canonical Input

- `platform/docs/current/FIRST_POST_LAUNCH_WBS.md`
- `platform/docs/current/BACKGROUND_SYSTEM_IMAGE.md`
- `platform/system/runtime/planning/first_post_launch_wbs.json`
- `platform/system/runtime/planning/background_system_image.json`

## Purpose

Use Repository OS v2 as the operating system for the first production outcome.

## Status

- READY

## platform/packs/PACK-0015-local-execution-adapter/README.md

# PACK-0015 Local Execution Adapter

## Canonical Input

- `queue/READY/EP-0201-execution-request-contract-hardening.md`
- `queue/READY/EP-0202-codex-adapter-contract.md`
- `queue/READY/EP-0203-codex-cli-dry-run-adapter.md`
- `queue/READY/EP-0204-codex-cli-execution-adapter.md`
- `queue/READY/EP-0205-completion-capture-adapter.md`
- `queue/READY/EP-0206-local-execution-safety-gate.md`
- `queue/READY/EP-0207-local-execution-adapter-validation.md`

## Purpose

Bridge supervisor execution requests to safe Codex CLI execution.

## Status

- READY

