# Agent Runtime MVP Specification

## Objective

Implement a dry-run Runtime Agent cycle using Repository as SSOT.

## Cycle

1. Load repository graph and agent context pack.
2. Build runtime context.
3. Build runtime plan.
4. Build queue item.
5. Build review summary.
6. Build approval gate.
7. Generate dry-run report.

## Boundary

No external action is allowed.
