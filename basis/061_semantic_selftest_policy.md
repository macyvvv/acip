# 061 Semantic SelfTest Policy

## Conclusion

Repository Semantic SelfTest v2 must analyze repository structure with configuration-driven semantics rather than raw string matching.

## Purpose

The v1 SelfTest proved useful but generated false positives because it treated archive, draft, template, report, queue, and explanatory text as canonical violations.

v2 separates:

- canonical space
- archive space
- draft space
- template space
- report space
- index space
- declaration syntax
- explanatory text

## Rules

- Repository overrides conversation.
- SelfTest must reduce Human review burden.
- Archive is historical, not canonical.
- Draft is non-canonical until promoted.
- Templates and reports may be unreferenced without being dead.
- Current Objective drift must parse declarations only.
- Runtime implementation remains out of scope unless approved.
