# Asset Lifecycle Checklist

## Conclusion

Use this checklist before treating any asset as reusable canonical knowledge.

## Checklist

| ID | Check | Required Evidence | Status |
|---|---|---|---|
| AL-01 | Asset has an ID | `asset_id` exists | To verify |
| AL-02 | Asset has a lifecycle status | `status` exists | To verify |
| AL-03 | Asset type is valid | Knowledge / Content / Media / Operational | To verify |
| AL-04 | Owner is defined | `owner` exists | To verify |
| AL-05 | Source context is recorded | `source_context` exists | To verify |
| AL-06 | Scope is explicit | scope section exists | To verify |
| AL-07 | Out of scope is explicit | out-of-scope section exists | To verify |
| AL-08 | Reuse rules are documented | reuse section exists | To verify |
| AL-09 | Risk notes exist | risk section exists | To verify |
| AL-10 | ROI link exists | value or ROI section exists | To verify |
| AL-11 | Related ADR/WBS are referenced when applicable | metadata or body reference exists | To verify |
| AL-12 | Human approval is recorded before canonical status | PR approval | To verify |

## Definition of Done

An asset may be treated as canonical only when:

1. It is merged into `main`.
2. It passes the canonical asset quality gate.
3. It has valid lifecycle metadata.
4. It does not introduce runtime implementation.
5. It can be reused without relying on chat context.
