# REPOSITORY_OS_V1_RISK_REGISTER

## Open Risks

1. Root layout remains warn-only.
   - Impact: repository root may accumulate legacy markdown and pack assets until a later migration EP.
   - Status: accepted for v1; monitored by root hygiene validation.

2. Generated artifact churn.
   - Impact: validation and runtime commands create deterministic artifacts that can dirty the worktree.
   - Status: managed by generated artifact tracking, but not yet fully eliminated.

3. Non-destructive validation drift.
   - Impact: validation commands and runtime artifacts can diverge if scripts are edited without updating repository state files.
   - Status: mitigated by validate_all and validation state records.

4. Human approval load.
   - Impact: high-risk or destructive changes still require Human approval and may slow execution.
   - Status: intentional boundary, not a defect.

## Parking Lot

- Root layout migration
- Additional root allowlist enforcement
- Generated artifact cleanup automation
- Multi-worker execution expansion beyond current registry set

