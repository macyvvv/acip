# 038 Runbook Policy

## Conclusion

Repeatable operations must be converted into runbooks so Codex and future approved automation can execute them without Human handholding.

## Runbook Requirements

Each runbook must define:

- objective
- trigger
- inputs
- preconditions
- execution steps
- validation steps
- failure modes
- retry rules
- escalation rules
- done condition
- owner
- Human boundary

## Human Boundary

Runbooks must avoid assigning mechanical work to Human.

Human should appear only where approval, risk acceptance, capital allocation, or emergency stop is required.

## Repository Rule

Repository overrides conversation.
