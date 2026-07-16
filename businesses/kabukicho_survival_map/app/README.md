# kabukicho_survival_map

## Purpose

The real MVP for issue #33 ("Kabukicho Survival Map MVP (UGC-ready)"): a mobile-first, static, list-first web app covering 6 POI categories (smoking areas, toilets, convenience stores, ATMs, coin lockers, lodging/internet cafes -- the last two added per an operator request beyond the original 4-category spec).

This is a from-scratch implementation, separate from `platform/app/products/kabukicho_survival_map_mvp/` (an earlier, much smaller Python markdown-brief generator that never became a real app).

This directory is the business-owned source of truth. `platform/app/products/kabukicho_survival_map` is kept only as a compatibility symlink for older platform references.

## Content pipeline

Content for this product (POI research, tag-evaluation copy, SEO/UI copy, promotion planning) was produced by the multi-business agent platform's `kabukicho_survival_map` business roles (`market_research`, `scenario_writing`, `doc_creation`, `marketing`), running under Level 3a policy pre-approval -- see `platform/docs/current/BUSINESS_AGENT_AUTOMATION_READINESS.md` and `platform/system/runtime/business_agents/kabukicho_survival_map/`. The actual app (HTML/CSS/JS, data schema, build script) is regular code, written directly -- the business-agent roles are read-only and cannot write application code.

## Data

Runtime/distribution source: `platform/system/runtime/data/kabukicho/{smoking,toilet,convenience,atm,coin_locker,lodging}.json`, one array per category, schema per issue #33 section 1 plus this product's additions (`verification_method`, `gray_zone_note`, and lodging's `licensed_as`).

**Current dataset is a first draft pending human verification** -- coordinates are approximate (derived from landmark proximity via web search, not geocoded), and several fields (pricing, hours, gender-separation status) are time-sensitive. See `market_research/task-0002`'s own recommendations before treating this as production-verified data.

## Build

`python3 businesses/kabukicho_survival_map/app/build.py` exports the business-owned DB into runtime JSON, then copies that data into this product's own `data/` (for local serving) and into `platform/web/public/kabukicho_survival_map/` (the deployable static bundle). No bundler, no backend -- per issue #33's "no over-engineering" constraint.

GA4 / AdSense deployment is also build-time driven:

- `KABUKICHO_GA_ID` enables GA4 in the public bundle
- `KABUKICHO_ADSENSE_CLIENT` enables AdSense Auto ads in the public bundle

Both are browser-side public IDs, not server-side secrets. `build.py` injects
them into `platform/web/public/kabukicho_survival_map/index.html` so GitHub
Pages can serve them without relying on a tracked config file.

### DB-first operation

This product now uses a DB-first data flow.

- Canonical editable store: `businesses/kabukicho_survival_map/app/data/kabukicho_poi.db`
- Runtime/distribution JSON: `platform/system/runtime/data/kabukicho/*.json`

Core commands:

- Import runtime JSON into DB:
	- `/Users/ariel/Documents/tools/acip/.venv/bin/python scripts/poi_db_sync.py import-json`
- Export DB back to runtime JSON:
	- `/Users/ariel/Documents/tools/acip/.venv/bin/python scripts/poi_db_sync.py export-json`
- Generate nearby-coordinate report:
	- `/Users/ariel/Documents/tools/acip/.venv/bin/python scripts/poi_db_sync.py check-nearby --threshold-m 40 --hard-m 8 --similar-name-threshold 0.64 --similar-name-radius-m 140`

`build.py` runs `export-json` automatically before copying files.

### Nearby duplicate gate

To block risky coordinate regressions in CI/local validation, run:

- `/Users/ariel/Documents/tools/acip/.venv/bin/python scripts/poi_db_sync.py check-nearby --threshold-m 40 --hard-m 8 --similar-name-threshold 0.64 --similar-name-radius-m 140 --max-hard-duplicates 10`

This fails non-zero when hard duplicates exceed the threshold.

## Entry point

`index.html` (self-contained: `app.js` + `style.css`, fetches `data/*.json` relative to itself).

## Deployment

GitHub Pages target URL is `https://macyvvv.github.io/acip/kabukicho_survival_map/`. Repository-side, the deployable artifact remains `platform/web/public/kabukicho_survival_map/`.

## Testing

- Data schema + build-output consistency: `python -m pytest businesses/kabukicho_survival_map/app/tests/` (part of the full `python -m pytest -q` suite).
- Map/list pure logic (distance calculation, freshness dating, filtering) has no Python equivalent to test against -- `node businesses/kabukicho_survival_map/app/tests/test_app_logic.js` runs a small, framework-free Node test against the relevant functions in `app.js` directly (guarded `module.exports`, no effect on browser behavior). Not part of the Python pytest suite (different runtime); run it manually when touching `app.js`'s map/list/filter logic.
- No automated coverage for the Google Maps rendering path itself (marker creation, info windows, category-switch re-pinning) -- verified manually via Playwright with a stubbed `google.maps` SDK during development; there's no committed harness for this yet.

## Review Focus

- Mobile UX: bottom nav, 1-tap category toggle, top map / bottom nearest-first list, tap-to-Google-Maps -- test on an actual phone-width viewport, not just resized desktop.
- Gray-zone/unofficial disclaimer renders inline on the affected card, not a separate screen. A `gray_zone_note` on an `official`-type entry renders as a plain info note, not the disclaimer banner (see `app.js`'s `renderCard` comment).
- Coordinates for most entries are still approximate (derived from landmark proximity via web search, not geocoded against a mapping API) -- flagged per-entry where known, not yet resolved.
