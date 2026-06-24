# 040 Failure Recovery Policy

## Conclusion

Autonomous workflows must define failure detection, retry, rollback, and escalation before runtime implementation.

## Failure Classes

- missing file
- failed validation
- failed CI
- unclear requirement
- scope drift
- policy violation
- runtime boundary violation
- approval gap
- repository conflict
- duplicate asset
- outdated asset

## Recovery Rules

- Prefer deterministic validation over judgment.
- Retry only when failure cause is known.
- Escalate when Human approval, risk acceptance, or emergency stop is needed.
- Do not bypass approval.
- Do not introduce runtime implementation.
- Repository overrides conversation.

## Done Condition

Failure recovery is ready when failure classes, retry rules, rollback rules, and escalation records exist.
