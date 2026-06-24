# 016 Asset Production Workflow

## Conclusion

Canonical Asset Production follows a controlled workflow from intake to canonical merge and reuse.

## Workflow

```text
Intake
↓
Triage
↓
Draft
↓
Quality Gate
↓
Human Approval
↓
Merge to main
↓
Registry Update
↓
Reuse Planning
↓
Review Cadence
```

## Workflow Rules

- Repository overrides conversation.
- No asset is canonical before merge into `main`.
- Quality Gate must be completed before Human Approval.
- Registry must be updated when an asset becomes canonical.
- Derived outputs must reference source asset id.
- Runtime implementation remains out of scope.
- Approval bypass is prohibited.

## Role Responsibilities

| Step | Human | ChatGPT | Codex |
|---|---|---|---|
| Intake | A | R | C |
| Triage | A | R | C |
| Draft | A | R | C |
| Quality Gate | A | R | C |
| Human Approval | A/R | C | I |
| Merge | A | C | R |
| Registry Update | A | C | R |
| Reuse Planning | A | R | C |

## Done Condition

The workflow is ready when intake, triage, drafting, quality gate, approval, registry update, and reuse planning all have repository-governed templates.
