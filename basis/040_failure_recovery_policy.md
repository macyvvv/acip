# 040 Failure Recovery Policy

## Conclusion

Autonomous workflows must define failure detection, retry, rollback, and escalation before runtime implementation.

## Rules

- Retry only when failure cause is known.
- Do not bypass approval.
- Do not introduce runtime implementation.
- Repository overrides conversation.
