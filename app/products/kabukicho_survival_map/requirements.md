# Requirements

Source: GitHub issue #33 (PRODUCT-0003: Kabukicho Survival Map MVP, UGC-ready), plus two operator-requested category additions (coin lockers, lodging incl. internet cafes).

## Functional Requirements

- 6 POI categories: smoking areas, toilets, convenience stores, ATMs, coin lockers, lodging/internet cafes.
- Each POI: name, lat/lng, description, category, tags (array), last_updated, reliability_score (1-5), source_type (official/observed/inferred), type (official/unofficial).
- Mobile-first, bottom navigation, 1-tap category toggle, list-first (no embedded map).
- Tap a POI opens Google Maps (external link only -- no map embedding).
- Tag-based evaluation only (no free-form rating).
- Unofficial/gray-zone locations clearly labeled with a disclaimer banner.
- Freshness indicators (recently updated / may be outdated).
- SEO title + meta description.
- Google Analytics placeholder, ID injected via config, never hardcoded.

## Non-Functional Requirements

- No backend, no authentication, no external API dependency (Google Maps is an outbound link only, not an embed/API call).
- Static JSON-based data, no runtime data fetching beyond the local `data/*.json` files.
- Fast rendering, no blocking assets.
- No over-engineering: no bundler, no framework -- plain HTML/CSS/JS plus a small Python copy-script for the build step.

## Explicitly Out of Scope (per issue #33's "Future" section)

- User submission (UGC), voting, ranking, real-time updates, embedded map rendering.
- Deployment target selection (separate, later decision).
