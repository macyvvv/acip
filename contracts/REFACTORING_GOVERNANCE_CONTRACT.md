# REFACTORING_GOVERNANCE_CONTRACT

Refactoring governance is a pre-execution gate.

## Required Fields

- risk_level
- impact_area
- rollback_requirement
- validation_requirement
- changed_path_allowlist
- destructive_change_policy
- human_approval_required

## Risk Levels

- low
- medium
- high

## Policy

- root moves and code rewrites are separate EPs
- high risk requires Human approval
- migration EPs must cover one logical concern
- destructive changes are prohibited unless explicitly approved
