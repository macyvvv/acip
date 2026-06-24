# 053 Repository Self Test Policy

## Conclusion

Repository Self Test must verify the ACIP Repository Operating System continuously and mechanically.

## Required Checks

- repository health
- required directory existence
- required file existence
- ADR/WBS link integrity
- policy boundary integrity
- Human Boundary preservation
- Runtime Boundary preservation
- Secret Boundary preservation
- External Action Boundary preservation
- duplicate title detection
- orphan document detection
- dead document detection
- Current Objective drift detection
- prohibited keyword detection

## Human Boundary

Human should not manually inspect repository consistency when deterministic scripts can check it.

Human handles Mission, Approval, Emergency Stop, Risk Acceptance, Capital Allocation, and runtime transition approval.

## Repository Rule

Repository overrides conversation.
