# ADR-0012: Autonomous Workflow Control Plane

## Status

Proposed

## Context

Agent OS defines capabilities, delegation, context, and queue concepts. The next step is a repository-governed control plane that turns those concepts into repeatable autonomous workflows without implementing runtime agents yet.

## Decision

Adopt an Autonomous Workflow Control Plane.

This includes:

- autonomous workflow policy
- runbook policy
- control plane policy
- failure recovery policy
- status reporting policy
- runbooks
- queue files
- status templates
- validation script
- GitHub Actions workflow

## Human Boundary Decision

Human should receive mission, approval, and emergency stop responsibilities only.

Routine execution and validation must be delegated to ChatGPT, Codex, scripts, GitHub Actions, or future approved automation.

## Alternatives Considered

### Move directly to runtime agents

Rejected because runtime implementation remains out of scope.

### Continue manual orchestration through chat

Rejected because chat is not canonical and creates Human burden.

### Use GitHub issues only

Rejected because issues are useful but insufficient without runbooks and control-plane conventions.

## Consequences

- Autonomous execution paths become explicit.
- Human workload decreases.
- Runtime implementation remains delayed until approved.
- Repository governance becomes more complex but more scalable.
