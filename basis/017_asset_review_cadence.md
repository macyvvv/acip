# 017 Asset Review Cadence

## Conclusion

Canonical Assets require scheduled review to preserve correctness, usefulness, and ROI connection.

## Review Cadence

| Asset Type | Default Review Cadence |
|---|---|
| Knowledge Asset | 90 days |
| Content Object | 60 days |
| Media Object | 60 days |
| Operational Asset | 30 days |
| Governance Asset | 90 days |
| High Risk Asset | 30 days |

## Review Triggers

Review must occur when:

- source assumptions change
- revenue link changes
- derivative output drifts
- risk profile changes
- new ADR supersedes prior reasoning
- asset has not been reviewed by its cadence
- Human requests review

## Review Outcomes

Allowed outcomes:

- keep
- revise
- restrict reuse
- deprecate
- split
- merge
- escalate to ADR

## Rules

- Repository overrides conversation.
- Review must preserve history.
- Deprecated assets remain discoverable.
- Approval bypass is prohibited.
- Runtime implementation remains out of scope.
