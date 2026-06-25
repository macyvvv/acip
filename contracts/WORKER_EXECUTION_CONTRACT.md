# WORKER_EXECUTION_CONTRACT

## Purpose

Define the repository-native execution contract for workers.

## Human Boundary

Human owns Mission, Approval, Emergency Stop, Risk Acceptance, Capital Allocation, and Runtime Transition Approval.

## Codex Boundary

Codex may implement only explicitly specified repository changes.

Codex must not introduce runtime external execution, platform API mutation, secret use, or approval bypass.

## Worker Boundary

Workers operate from repository contracts, worker profiles, and active specs.

Workers do not rely on conversation state as canonical input.

## Validation

Workers must validate before commit.
