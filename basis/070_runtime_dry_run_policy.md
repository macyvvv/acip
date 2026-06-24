# 070 Runtime Dry Run Policy

## Conclusion

Runtime dry-run is allowed before runtime approval only if it performs no external actions and no repository mutation without explicit command.

## Dry Run May

- read repository files
- build graph artifacts
- generate reports
- simulate task planning
- validate contracts
- produce next-action recommendations

## Dry Run Must Not

- call external APIs
- post content
- mutate platform state
- use secrets
- bypass approval

## Rule

Dry-run output is advisory until Human approval.
