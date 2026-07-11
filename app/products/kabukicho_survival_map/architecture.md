# Architecture

## Shape

Static site, no backend, no build tooling beyond a copy-script:

```
system/runtime/data/kabukicho/*.json   <- canonical data source (6 files)
app/products/kabukicho_survival_map/
  index.html                          <- SEO meta, GA + Google Maps API key placeholders, mounts app.js
  app.js                              <- category config, tag copy, render logic, map + geolocation logic
  style.css                           <- mobile-first styles, top map / bottom list split, bottom nav
  data/*.json                         <- build-time copy of the canonical source
  build.py                            <- copies data + static files to web/public/kabukicho/
web/public/kabukicho/                 <- deployable static bundle (build output)
```

## Data flow

1. Business-agent roles (`market_research`, `scenario_writing`, `doc_creation`) produce research/copy as read-only text artifacts under `system/runtime/business_agents/kabukicho_survival_map/`.
2. A human (or this implementation pass) distills that research into the structured JSON at `system/runtime/data/kabukicho/`.
3. `build.py` copies that data (plus the static HTML/JS/CSS) into `web/public/kabukicho/`, the deployable bundle.
4. In the browser, `app.js` fetches `data/*.json` relative to itself, renders the bottom-nav-filtered POI list (bottom pane), and plots the same filtered set as pins on an embedded Google Map (top pane). No server-side logic anywhere.

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

- **Local testing** (this is what `.env`/`KABUKICHO_GMAPS_API_KEY` is for): set `KABUKICHO_GMAPS_API_KEY=...` in `.env` (gitignored, copy from `.env.example`), then run `build.py`. It reads the key via `system/core/dotenv.py` and writes it into `app/products/kabukicho_survival_map/local.config.js` -- a small, gitignored file, loaded by `index.html` via `<script src="local.config.js">` *before* the `window.KABUKICHO_GMAPS_API_KEY` placeholder, so the `||` fallback in that placeholder preserves the real value. Absent `.env` entry -> `build.py` removes any stale `local.config.js` and the map falls back to the setup notice. This file is **never** written into `web/public/kabukicho/` (that bundle is tracked in git) and never copied there by `build.py`.
- **Production deploy**: needs its own, separate key-injection step tied to whichever host is eventually chosen (not yet decided -- see `requirements.md`'s "Explicitly Out of Scope"). Whatever that step is, it must write the real key into the *deployed*, not the *committed*, `index.html` -- e.g., a deploy-time environment variable substituted by the hosting platform's build step, never a `git commit` of the real key into `web/public/kabukicho/`.

## Extension points

- Adding a POI: append an entry to the relevant `system/runtime/data/kabukicho/*.json` file matching the existing schema, then re-run `build.py`.
- Adding a category: add an entry to `app.js`'s `CATEGORIES` array and a new `TAG_COPY` block, plus a new source JSON file.
- Future UGC/voting/ranking (explicitly out of scope now) would need a backend and is a separate, later architectural decision -- not something to bolt onto this static shape.
