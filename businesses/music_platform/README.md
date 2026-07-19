# music_platform

Business canonical root placeholder.

## Status

- greenfield business
- no legacy root to migrate

## Planned target layout

- platform/app/
- content/
- runtime/
- platform/docs/

## Canonical Docs

- [User Value Analytics Canon](platform/docs/USER_VALUE_ANALYTICS_CANON.md)
- [Participant Organizer Behavior Model Modernized](platform/docs/PARTICIPANT_ORGANIZER_BEHAVIOR_MODEL_MODERNIZED.md)
- [Implementation and Discovery Roadmap](platform/docs/IMPLEMENTATION_AND_DISCOVERY_ROADMAP.md)
- [Implementation WBS Detailed](platform/docs/IMPLEMENTATION_WBS_DETAILED.md)
- [Sitemap](platform/docs/SITEMAP.md)
- [Site Page Flow](platform/docs/SITE_PAGE_FLOW.mmd)
- [Static Mock Improvement WBS](platform/docs/STATIC_MOCK_IMPROVEMENT_WBS.md)
- [Static Mock User Review Plan](platform/docs/STATIC_MOCK_USER_REVIEW_PLAN.md)
- [Static Mock Execution Report](platform/docs/STATIC_MOCK_EXECUTION_REPORT.md)
- [ADR-0046: Participation and Automated Formation Support](../../platform/adr/ADR-0046-music-platform-participation-and-automated-formation-support.md)
- [Static Site Mock](platform/mockups/static_site/README.md)

Current doc ownership:

- `ADR-0046` is the decision source for participation, song entries, automated formation support, and responsibility boundaries.
- `SITEMAP.md` is the information architecture source.
- `platform/mockups/static_site/` is a static UX-order mock only; it is not the production route, API, auth, or notification implementation.
- `USER_VALUE_ANALYTICS_CANON.md` is the value, analytics, and function backlog source.
- The three behavior model docs are kept separate for reviewability now. If duplication becomes operationally costly, merge them into one `BEHAVIOR_MODEL.md` with Participant, Organizer, Machine, and Platform Super User sections.
