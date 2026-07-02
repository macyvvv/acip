# AUTONOMOUS_EXECUTION_APPROVAL_CONTRACT

## Purpose
Define the explicit human approval artifact required to move an autonomous handoff from handoff-ready to execution-allowed.

## Terms
### Handoff-ready
The repository has produced a bounded autonomous handoff artifact and an execution request artifact, but execution is still blocked until approval exists.

### Execution-ready
The handoff and approval artifacts match, the approval status is `approved`, and execution may proceed through the existing execution flow.

### Who may approve
Only a human operator may set `decision_status: approved`.

Codex and ChatGPT may prepare artifacts, but they may not implicitly approve execution.

## Approval Artifact Shape
Canonical fields:
- `approval_id`
- `handoff_id`
- `scope_type`
- `scope_id`
- `decision_status`
- `approved_by`
- `approved_at`
- `reason`
- `execution_enabled`
- `supersedes`

## Execution Must Remain Blocked When
- approval is missing
- approval is pending
- approval is rejected
- scope_id does not match the handoff
- approval has been superseded
- handoff and approval do not match

## Rejection Semantics
Rejected approvals are terminal for that approval record.
Re-execution requires a new approval artifact with a new `approval_id`.

## Supersede / Update Semantics
- A later approval may supersede an earlier approval by setting `supersedes` to the prior approval id.
- If `supersedes` is present, the prior approval is not authoritative.

## Prohibition
Implicit approval is forbidden.
No runtime component may infer approval from readiness alone.
