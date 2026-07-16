# Architecture

## Shape

Static site, no backend, no build tooling beyond a copy-script:

```text
businesses/kabukicho_survival_map/app/         <- business-owned product source of truth
platform/system/runtime/data/kabukicho/*.json  <- runtime/distribution JSON (6 files)
platform/app/products/kabukicho_survival_map/  <- compatibility symlink to businesses/.../app
  index.html                          <- SEO meta, GA + Google Maps API key placeholders, mounts app.js
  app.js                              <- category config, tag copy, render logic, map + geolocation logic
  style.css                           <- mobile-first styles, top map / bottom list split, bottom nav
  data/*.json                         <- build-time local copy of runtime JSON
  build.py                            <- exports runtime JSON + copies bundle files
platform/web/public/kabukicho/                 <- deployable static bundle (build output)
```

## Data flow

1. Business-agent roles (`market_research`, `scenario_writing`, `doc_creation`) produce research/copy as read-only text artifacts under `platform/system/runtime/business_agents/kabukicho_survival_map/`.
2. A human maintains the business-owned SQLite store at `businesses/kabukicho_survival_map/app/data/kabukicho_poi.db`, with `scripts/poi_db_sync.py` exporting the runtime JSON at `platform/system/runtime/data/kabukicho/`.
3. `build.py` exports that runtime JSON, then copies it (plus the static HTML/JS/CSS) into `platform/web/public/kabukicho/`, the deployable bundle.
4. In the browser, `app.js` fetches `data/*.json` relative to itself, renders the bottom-nav-filtered POI list (bottom pane), and plots the same filtered set as pins on an embedded Google Map (top pane). No server-side logic anywhere.

## Commercial / Monetization surfaces

This product is not purely informational; it is intended to support revenue through
affiliate links, partner placements, and sponsored modules.

The layout must therefore reserve explicit monetization surfaces rather than relying
on late, ad-hoc insertion.

Current intended surfaces:

- `#monetization-slot-primary`
  - location: high-visibility slot in the left control stack
  - purpose: sponsored lodging / lockers / late-night utility placements
- `#monetization-slot-secondary`
  - location: after the main results list, before FAQ
  - purpose: related partner offers, editorial commerce, affiliate recommendations

Design constraints:

- sponsored content must remain visually distinct from organic survival-map results
- monetization must not break the map/list task flow
- monetization blocks should degrade safely when empty
- ad/sponsor placement must not replace SEO-rendered POI content as the primary page body

## Analytics / GA4 integration direction

The current GA placeholder in `index.html` is only a bootstrap point.

Operationally, this product needs GA4-oriented event instrumentation for:

- mode selection
- category selection
- tag filter selection
- list-card click
- Google Maps external-link click
- geolocation granted / denied
- monetization slot impression
- monetization slot click

The implementation should preserve clear event boundaries so later GA4 wiring does
not require redesigning the DOM structure.

## Why no framework/bundler

Issue #33 explicitly constrains this to "no over-engineering," "no backend." A ~500-line vanilla JS file reading small static JSON arrays and driving the Google Maps JS SDK doesn't need React/Vue/webpack -- introducing one would be the exact premature abstraction this repo's own ADR-0032 already flags as a standing risk.

## Map pane (operator-requested, 2026-07-11 -- reverses the original "no embedded map / no API dependency" decision)

- `index.html` declares `window.KABUKICHO_GMAPS_API_KEY` as an empty-by-default placeholder, identical in spirit to the existing `KABUKICHO_GA_ID` pattern: never hardcoded, safe to ship absent, and the feature it gates degrades gracefully (a setup notice in the map pane) rather than failing silently or throwing.
- `app.js`'s `loadGoogleMaps()` only injects the `https://maps.googleapis.com/maps/api/js` script tag when a real key is present, using the `callback=initKabukichoMap` pattern so map init happens once the SDK is actually ready. `window.gm_authFailure` and the script's `onerror` both route to the same `showMapNotice()` fallback, so an invalid key or a network failure degrade the same way an absent key does.
- Markers use the classic `google.maps.Marker` API (not `AdvancedMarkerElement`), which needs no extra `libraries=` query param -- appropriate for a handful of static pins per category, not a reason to add SDK surface area.
- The map always shows exactly the POIs of the currently active bottom-nav category (re-plotted and bounds-refit on every category switch) plus, once geolocation succeeds, a distinct "current location" marker -- never all six categories' pins at once.
- List <-> map sync is one lightweight layer on top of the existing render functions: tapping a `.poi-card` (outside its "位置情報を見る" link) calls `focusMarker()`, which pans/zooms the map and opens that POI's `InfoWindow`; tapping a marker opens the same `InfoWindow` directly. Neither direction touches `state.data` or the JSON schema.
- Distance sorting (`sortedByDistance()`, plain haversine, no library) is intentionally independent of whether the map/SDK ever loads -- `requestUserLocation()` is called once at startup, not from inside `initKabukichoMap()`, so the "nearest first" list ordering works even with no API key configured at all.

## Operational note: this map pane needs a real, billed Google Cloud API key

Nothing in this repo can provision that key. An operator must: create/select a Google Cloud project, enable the "Maps JavaScript API", create an API key, restrict it by HTTP referrer to this site's real deploy domain(s) (and, for local testing, `http://localhost:*`), and set the key via one of the two paths below. Until that happens, the map pane shows a setup notice -- this is expected, not a bug.

**Important, and different from this repo's other `.env` secrets (`OPENAI_API_KEY` etc.)**: a Google Maps *JavaScript* API key is not a server-side secret -- it must ship inside client-side JS that runs in every visitor's browser, so once the site is actually deployed, anyone can read it via view-source or the network tab. `.env` only keeps it out of *git history*; the real protection against abuse is the HTTP referrer restriction on the key itself in Google Cloud Console, not secrecy. Both paths below assume that restriction is set.

- **Local testing** (this is what `.env`/`KABUKICHO_GMAPS_API_KEY` is for): set `KABUKICHO_GMAPS_API_KEY=...` in `.env` (gitignored, copy from `.env.example`), then run `build.py`. It reads the key via `platform/system/core/dotenv.py` and writes it into `businesses/kabukicho_survival_map/app/local.config.js` -- a small, gitignored file, loaded by `index.html` via `<script src="local.config.js">` *before* the `window.KABUKICHO_GMAPS_API_KEY` placeholder, so the `||` fallback in that placeholder preserves the real value. `build.py` also writes the same key into `platform/web/public/kabukicho/local.config.js` as part of the deploy artifact, so the public bundle can show the live map when the key is present.
- **Production deploy**: the deploy artifact may include the browser-side Google Maps key, but the key itself must still be referrer-restricted in Google Cloud Console. If a host-specific injection step is used later, it should overwrite the public bundle's `local.config.js` or equivalent at build/deploy time, never rely on a server-side secret at runtime.

## SEO/AIO (search + AI-answer-engine visibility), 2026-07-13

Hosting is explicitly gated on having a distribution strategy (see
`requirements.md`'s deploy section and issue #36); this is that strategy's
technical half. Driven by research into how AI answer engines (ChatGPT,
Perplexity, Google AI Overviews) and traditional search actually crawl and
cite hyperlocal guide content:

- **The core problem this app had**: `app.js` fetches `data/*.json` and
  renders the POI list entirely client-side. Most AI crawlers (and a
  meaningful share of traditional ones) do not execute JavaScript, so the
  raw HTML previously shipped with an empty `<main id="poi-list">` --
  effectively invisible to anything that doesn't run JS.
- **Fix**: `build.py` now pre-renders every category's full POI list (all
  six categories, not just the default one -- a crawler only gets one page
  load) as static HTML directly into `index.html` at build time
  (`_render_poi_static_html`), via marker substitution (`<!-- SSG:* -->`
  comments in the `index.html` template -- do not hand-edit those blocks,
  they're regenerated every build). `app.js`'s `renderList()` fully
  replaces `#poi-list`'s `innerHTML` on `DOMContentLoaded` regardless, so a
  JS-capable browser only ever sees the static content for an instant
  (progressive enhancement, not a UX change).
- **Structured data**: `build.py` also generates a JSON-LD `<script>` block
  (an `ItemList` of `Place` items, one per POI, plus a `FAQPage`) into
  `<head>`. Deliberately `Place`, not `LocalBusiness` -- `LocalBusiness`
  assumes business-identity semantics (`openingHours`, `priceRange`) that
  don't fit a public toilet or an outdoor smoking spot; `additionalType`
  carries the category label instead. Per Google's own 2026 AI-optimization
  guidance, structured data is not required for AI Overviews specifically,
  but it's still useful for ordinary Search (rich-result eligibility,
  entity clarity) -- and ordinary Search indexing/eligibility is a
  documented prerequisite for AI Overview surfacing.
- **FAQ section**: a small, hand-curated (not keyword-stuffed) set of real
  questions in `build.py`'s `FAQ_ITEMS`, rendered as visible `<details>`/
  `<summary>` content in a `#faq-section` -- deliberately a sibling of
  `#poi-list`, not inside it, so `renderList()` never wipes it out; it's
  meant to persist for real visitors, not just crawlers. Google retired the
  visual FAQ rich-result SERP snippet in 2026-05, but `FAQPage` markup is
  still parsed, and Q&A-formatted content remains one of the easier
  patterns for LLMs to extract/quote regardless of the SERP feature's
  status -- so this is kept for the content-extraction value, not for a
  rich-result appearance that no longer exists.
- **Sponsored placement constraint**: monetization blocks must not interrupt
  the pre-rendered POI corpus before the primary informational body is established.
  Ads/sponsored modules can be present near controls or after result clusters, but
  the page should still read as a genuine hyperlocal utility page to crawlers and
  users first.
- **`llms.txt`**: deliberately not implemented. Research found no major AI
  platform officially requires or reliably uses it, and Google's own
  AI-optimization guidance explicitly advises against relying on it. Low
  cost but unproven benefit -- revisit only if that changes.
- **`robots.txt`**: always generated (domain-independent), explicitly
  `Allow`-ing standard crawlers plus AI bots that respect robots.txt
  (`GPTBot`, `OAI-SearchBot`, `ClaudeBot`, `PerplexityBot`,
  `Google-Extended`, `CCBot`) -- some hosts/CDNs block AI bots by default,
  so an explicit `Allow` is safer than an assumed absence of `Disallow`.
- **`sitemap.xml` / canonical tag**: both need a real, absolute deploy URL,
  which doesn't exist yet -- `build.py` skips generating them (rather than
  writing a placeholder domain that would mislead crawlers) until
  `KABUKICHO_SITE_URL` is set in `.env` (see `.env.example`), printing a
  reminder each time it's absent. Set it once a host is chosen and re-run
  `build.py`.
- **Competitive note**: research surfaced several existing smoking-area/
  facility finders (smoking-map.jp, share-map.net, Doko?, "Japan Smoking
  Area", CLUB JT's search) -- none combine all six of this app's categories
  or are Kabukicho-specific, and several have real, documented weaknesses
  (Japanese-only UI, 1.0-star ratings, no in-app search, region-locking).
  That gap is this product's actual differentiation; nothing here changes
  because of it, but it's why the SEO/AIO investment is worth making rather
  than assuming the niche is already saturated.

## Extension points

- Adding or editing a POI: update `businesses/kabukicho_survival_map/app/data/kabukicho_poi.db` through the `scripts/poi_db_sync.py` workflow, then re-run `build.py`.
- Adding a category: add an entry to `app.js`'s `CATEGORIES` array and a new `TAG_COPY` block, plus a new source JSON file.
- Future UGC/voting/ranking (explicitly out of scope now) would need a backend and is a separate, later architectural decision -- not something to bolt onto this static shape.
