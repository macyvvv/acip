# Runtime Dry Run Plan

## Objective

Simulate runtime agent coordination without external actions.

## Dry Run Steps

1. Load repository graph.
2. Load context pack.
3. Select a WBS.
4. Produce a non-mutating plan.
5. Validate boundaries.
6. Produce report.

## Prohibited

- external API calls
- repository mutation
- auto posting
- secret use
- approval bypass
