# RB-0006: Emergency Stop

## Objective

Define the Human emergency stop path.

## Trigger

Human issues Emergency Stop or a severe policy/risk violation is detected.

## Steps

1. Stop current execution.
2. Record stop reason.
3. Identify affected files/issues/PRs.
4. Freeze new execution.
5. Prepare recovery options.
6. Wait for Human approval before resuming.

## Human Boundary

Human owns Emergency Stop decision.

## Done Condition

Execution is stopped, reason is recorded, and recovery path is prepared.
