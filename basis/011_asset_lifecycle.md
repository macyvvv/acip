# 011 Asset Lifecycle

## Conclusion

A Canonical Asset must move through a controlled lifecycle so that ACIP can preserve source meaning, reuse assets safely, and avoid uncontrolled drift.

## Lifecycle

```text
Intake → Draft → Review → Approved → Canonical → Reuse → Revision → Deprecated
```

## Status Definitions

| Status | Meaning | Repository Condition |
|---|---|---|
| Intake | Candidate asset exists but is not yet structured | Issue or draft document exists |
| Draft | Asset is being written in canonical format | Branch or PR exists |
| Review | Asset is ready for quality review | PR has review request |
| Approved | Human approval has been given | Approval is recorded in PR |
| Canonical | Asset is merged into `main` | Merged repository content exists |
| Reuse | Asset is used to derive channel or operational outputs | Derivative references canonical source |
| Revision | Asset needs controlled update | New Issue / PR / ADR when required |
| Deprecated | Asset should no longer be reused as current guidance | Deprecation note exists |

## Lifecycle Rules

- Repository overrides conversation.
- No asset is canonical before merge into `main`.
- Reuse must reference the canonical source path.
- Revision must preserve version history.
- Deprecation must not delete historical reasoning.
- Approval bypass is prohibited.
- Runtime implementation remains out of scope.

## Required Metadata

Each Canonical Asset should record:

- asset id
- title
- asset type
- lifecycle status
- owner
- version
- source path
- related ADRs
- related WBS
- reuse permissions
- risk notes

## Done Condition

Asset lifecycle control is complete when lifecycle statuses, repository conventions, review checklist, and validation automation exist and pass in CI.
