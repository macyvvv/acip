# WBS-0008: Autonomous Workflow Control

## Current Phase

Knowledge Factory

## Current Objective

Agent OS Foundation

## Conclusion

This WBS adds autonomous workflow control without introducing runtime implementation.

## Scope

- autonomous workflow policy
- runbook policy
- control plane policy
- failure recovery policy
- status reporting policy
- control plane ADR
- runbooks
- control files
- checklist
- Codex execution prompt
- validation script
- GitHub Actions workflow

## Out of Scope

- runtime implementation
- auto posting
- platform API integration
- scraping-dependent automation
- external database
- new application frameworks

## Work Breakdown

| ID | Task | Owner | Done Condition |
|---|---|---|---|
| WBS-0008-01 | Add policies | Codex | basis files exist |
| WBS-0008-02 | Add ADR | Codex | ADR exists |
| WBS-0008-03 | Add runbooks | Codex | runbooks exist |
| WBS-0008-04 | Add control files | Codex | control files exist |
| WBS-0008-05 | Add validation | Codex | script exits 0 |
| WBS-0008-06 | Add CI | Codex | workflow exists |

## Human Boundary

Human is responsible only for Mission, Approval, and Emergency Stop unless risk acceptance or capital allocation is required.

## Acceptance Criteria

- `python scripts/validate_autonomous_workflow_control.py` passes.
- `Autonomous Workflow Control Check` passes.
- Runtime implementation remains out of scope.
