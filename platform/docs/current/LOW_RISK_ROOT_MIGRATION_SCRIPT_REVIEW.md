# LOW_RISK_ROOT_MIGRATION_SCRIPT_REVIEW

## Human Approval Gate

- The migration scripts are review-only artifacts until Human Approval is granted.
- The execution script requires `APPROVAL_FLAG=true`.
- The execution script is dry-run by default and does not move files unless approval and execution mode are explicitly set.

## Low-Risk Candidates

- baseline
- control
- loader
- prompts
- releases
- rules
- templates

## Safety

- Scripts fail if unexpected archive targets already exist.
- Scripts do not touch medium-risk or high-risk candidates.
- Scripts do not update references automatically.
- Scripts are idempotent in the sense that they abort safely when state is not as expected.
