# 014 Asset Traceability Policy

## Conclusion

Every reusable asset must preserve traceability from source idea to canonical asset to derivative output.

## Traceability Chain

```text
Source Context
↓
Canonical Asset
↓
Content Object
↓
Media Object / Operational Output
↓
Performance / Learning Feedback
↓
Revision Decision
```

## Required Links

Each asset must be able to identify:

- its source context
- its parent asset, if any
- its derived outputs
- related ADRs
- related WBS
- quality review record
- lifecycle status
- revision history

## Reuse Rule

Derived outputs must reference source asset id.

If the source asset changes, derivative outputs must be reviewed for drift.

## Prohibited

- orphan derivative assets
- reuse without source reference
- silent meaning changes
- approval bypass
- deleting historical traceability

## Repository Rule

Repository overrides conversation.

Traceability is official only when recorded in repository files and merged into `main`.
