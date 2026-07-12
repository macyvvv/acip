# kabukicho_survival_map

## Purpose

The real MVP for issue #33 ("Kabukicho Survival Map MVP (UGC-ready)"): a mobile-first, static, list-first web app covering 6 POI categories (smoking areas, toilets, convenience stores, ATMs, coin lockers, lodging/internet cafes -- the last two added per an operator request beyond the original 4-category spec).

This is a from-scratch implementation, separate from `app/products/kabukicho_survival_map_mvp/` (an earlier, much smaller Python markdown-brief generator that never became a real app).

## Content pipeline

Content for this product (POI research, tag-evaluation copy, SEO/UI copy, promotion planning) was produced by the multi-business agent platform's `kabukicho_survival_map` business roles (`market_research`, `scenario_writing`, `doc_creation`, `marketing`), running under Level 3a policy pre-approval -- see `docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md` and `system/runtime/business_agents/kabukicho_survival_map/`. The actual app (HTML/CSS/JS, data schema, build script) is regular code, written directly -- the business-agent roles are read-only and cannot write application code.

## Data

Canonical source: `system/runtime/data/kabukicho/{smoking,toilet,convenience,atm,coin_locker,lodging}.json`, one array per category, schema per issue #33 section 1 plus this product's additions (`verification_method`, `gray_zone_note`, and lodging's `licensed_as`).

**Current dataset is a first draft pending human verification** -- coordinates are approximate (derived from landmark proximity via web search, not geocoded), and several fields (pricing, hours, gender-separation status) are time-sensitive. See `market_research/task-0002`'s own recommendations before treating this as production-verified data.

## Build

`python3 app/products/kabukicho_survival_map/build.py` copies the canonical data into this product's own `data/` (for local serving) and into `web/public/kabukicho/` (the deployable static bundle). No bundler, no backend -- per issue #33's "no over-engineering" constraint.

## Entry point

`index.html` (self-contained: `app.js` + `style.css`, fetches `data/*.json` relative to itself).

## Deployment

**Not yet decided** -- explicitly out of scope for this build (a separate, later decision per the operator). `web/public/kabukicho/` is a ready-to-serve static bundle; any static host works once chosen.

## Testing

- Data schema + build-output consistency: `python -m pytest app/products/kabukicho_survival_map/tests/` (part of the full `python -m pytest -q` suite).
- Map/list pure logic (distance calculation, freshness dating, filtering) has no Python equivalent to test against -- `node app/products/kabukicho_survival_map/tests/test_app_logic.js` runs a small, framework-free Node test against the relevant functions in `app.js` directly (guarded `module.exports`, no effect on browser behavior). Not part of the Python pytest suite (different runtime); run it manually when touching `app.js`'s map/list/filter logic.
- No automated coverage for the Google Maps rendering path itself (marker creation, info windows, category-switch re-pinning) -- verified manually via Playwright with a stubbed `google.maps` SDK during development; there's no committed harness for this yet.

## Review Focus

- Mobile UX: bottom nav, 1-tap category toggle, top map / bottom nearest-first list, tap-to-Google-Maps -- test on an actual phone-width viewport, not just resized desktop.
- Gray-zone/unofficial disclaimer renders inline on the affected card, not a separate screen. A `gray_zone_note` on an `official`-type entry renders as a plain info note, not the disclaimer banner (see `app.js`'s `renderCard` comment).
- Coordinates for most entries are still approximate (derived from landmark proximity via web search, not geocoded against a mapping API) -- flagged per-entry where known, not yet resolved.
