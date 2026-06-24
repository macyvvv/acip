# 039 Control Plane Policy

## Conclusion

ACIP requires a lightweight repository control plane before runtime implementation.

## Control Plane Components

- Mission Intake
- Task Queue
- Review Queue
- Retry Queue
- Escalation Queue
- Parking Lot
- Status Report
- Decision Log
- Runbook Index

## Purpose

The control plane exists to coordinate ChatGPT planning, Codex implementation, validation scripts, GitHub Actions, and Human approval.

## Rules

- Repository overrides conversation.
- Control plane state must be explicit in repository files or GitHub issues.
- Human must not maintain control plane state manually when automation or Codex can do it.
- Runtime implementation remains out of scope.
