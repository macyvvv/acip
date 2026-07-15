# EP Legacy Bundle

This file consolidates individual EP README documents previously stored as one file per EP.

## platform/docs/ep/README_EP0001.md

# EP-0001 Runtime Capability Suite
One-shot package.

## platform/docs/ep/README_EP0002.md

# EP-0002 Runtime Coordination Suite
Focus: queue, review, approval coordination.

## platform/docs/ep/README_EP0003.md

# EP-0003 Agent Capability Suite

## platform/docs/ep/README_EP0111_VALIDATION_ORCHESTRATOR.md

# EP-0111 Validation Orchestrator

- Purpose: run all EP validation scripts and pytest from one entrypoint.
- Inputs: `platform/scripts/validate_ep_*.py`, repository state, `pytest`.
- Outputs: `runtime/validation/validation_report.json`, `runtime/validation/VALIDATION_REPORT.md`, `platform/docs/current/VALIDATION_STATE.md`.
- Failure mode: non-zero exit when any validation or pytest fails.

## platform/docs/ep/README_EP0116_REPOSITORY_HYGIENE_CODE_QUALITY.md

# EP-0116 Repository Hygiene & Code Quality Baseline

Detection-first hygiene and quality baseline for the repository.

## platform/docs/ep/README_EP0117_REFACTORING_GOVERNANCE.md

# EP-0117 Refactoring Governance Gate

Governance gate for refactoring execution.

## platform/docs/ep/README_EP0118_ROOT_HYGIENE_MIGRATION_1.md

# EP-0118 Root Hygiene Migration 1

Move root-level EP README, MANIFEST, and PACK markdown into responsibility directories.

## platform/docs/ep/README_EP0121_REPOSITORY_LAYOUT_CANONICALIZATION.md

# EP-0121 Repository Layout Canonicalization

Define the canonical repository layout and root allowlist without moving files yet.

## platform/docs/ep/README_EP0123_GENERATED_ARTIFACT_MANAGER.md

# EP-0123 Generated Artifact Manager

Detect generated artifact diffs and classify dirty worktree state.

## platform/docs/ep/README_EP0143_REPOSITORY_OS_V1_COMPLETION_REVIEW.md

# EP-0143 Repository OS v1 Completion Review

Review the repository OS v1 completion state and formalize the remaining risks and next-phase criteria.

## platform/docs/ep/README_EP0147_COMPLETION_REPORT_AUTOMATION.md

# EP-0147 Completion Report Automation

Reflect completion data into output contract, journal, runtime, and validation artifacts.

## platform/docs/ep/README_EP0152_VALIDATION_READ_ONLY_MODE.md

# EP-0152 Validation Read-Only Mode

Make `python3 platform/scripts/validate_all.py` read-only by default.

## platform/docs/ep/README_EP0153_RUNTIME_ARTIFACT_WRITE_POLICY.md

# EP-0153 Runtime Artifact Write Policy

Define the write policy for runtime artifacts and explicit refresh boundaries.

## platform/docs/ep/README_EP0154_WORKTREE_CLEANLINESS_GATE.md

# EP-0154 Worktree Cleanliness Gate

Check whether validation leaves the repository clean by default.

## platform/docs/ep/README_EP0155_GENERATED_ARTIFACT_REFRESH_COMMAND.md

# EP-0155 Generated Artifact Refresh Command

Provide an explicit command for refreshing validation and generated-artifact runtime reports.

