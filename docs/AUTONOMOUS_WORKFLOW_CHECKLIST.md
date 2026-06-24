# Autonomous Workflow Checklist

## Checklist

| ID | Criterion | Evidence | Status |
|---|---|---|---|
| AW-01 | Autonomous workflow policy exists | `basis/037_autonomous_workflow_policy.md` | To verify |
| AW-02 | Runbook policy exists | `basis/038_runbook_policy.md` | To verify |
| AW-03 | Control plane policy exists | `basis/039_control_plane_policy.md` | To verify |
| AW-04 | Failure recovery policy exists | `basis/040_failure_recovery_policy.md` | To verify |
| AW-05 | Status reporting policy exists | `basis/041_status_reporting_policy.md` | To verify |
| AW-06 | Control plane ADR exists | `adr/ADR-0012-autonomous-workflow-control-plane.md` | To verify |
| AW-07 | Runbooks exist | `runbooks/` | To verify |
| AW-08 | Control files exist | `control/` | To verify |
| AW-09 | Validation exists | `scripts/validate_autonomous_workflow_control.py` | To verify |
| AW-10 | CI exists | `.github/workflows/autonomous-workflow-control-check.yml` | To verify |

## Definition of Done

Autonomous Workflow Control is ready when validation passes and Human remains limited to Mission, Approval, and Emergency Stop.
