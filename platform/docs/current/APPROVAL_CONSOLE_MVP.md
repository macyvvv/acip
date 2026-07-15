# APPROVAL_CONSOLE_MVP

## Purpose

Provide a minimal operator console for one-shot approved autonomous execution.

## Scope

- Show approval-eligible scopes
- Approve exactly one selected scope
- Run one-shot approved autonomous execution
- Display final status and completion marker path

## Exact Workflow

1. Refresh candidate list
2. Select exactly one scope
3. Apply approval artifact update
4. Run approval evaluation
5. If allowed, run one-shot approved autonomous execution
6. Review final result

## Disabled By Design

- Repeated autonomy
- Queue autonomy
- Open-ended autonomy
- Auto-selection of next scope
- Daemon/background operation
- GitHub mutation
- Implicit approval
- Batch processing

## Relation to Baseline

This console operates within the `one_shot_approved_execution_only` baseline and does not expand autonomy beyond one explicitly selected scope.

