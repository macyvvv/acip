# Architecture

## Shape

Static site, no backend, no build tooling beyond a copy-script:

```
system/runtime/data/kabukicho/*.json   <- canonical data source (6 files)
app/products/kabukicho_survival_map/
  index.html                          <- SEO meta, GA placeholder, mounts app.js
  app.js                              <- category config, tag copy, render logic
  style.css                           <- mobile-first styles, bottom nav
  data/*.json                         <- build-time copy of the canonical source
  build.py                            <- copies data + static files to web/public/kabukicho/
web/public/kabukicho/                 <- deployable static bundle (build output)
```

## Data flow

1. Business-agent roles (`market_research`, `scenario_writing`, `doc_creation`) produce research/copy as read-only text artifacts under `system/runtime/business_agents/kabukicho_survival_map/`.
2. A human (or this implementation pass) distills that research into the structured JSON at `system/runtime/data/kabukicho/`.
3. `build.py` copies that data (plus the static HTML/JS/CSS) into `web/public/kabukicho/`, the deployable bundle.
4. In the browser, `app.js` fetches `data/*.json` relative to itself and renders category-filtered POI lists client-side. No server-side logic anywhere.

## Why no framework/bundler

Issue #33 explicitly constrains this to "no over-engineering," "no backend," "no API dependency." A ~200-line vanilla JS file reading small static JSON arrays doesn't need React/Vue/webpack -- introducing one would be the exact premature abstraction this repo's own ADR-0032 already flags as a standing risk.

## Extension points

- Adding a POI: append an entry to the relevant `system/runtime/data/kabukicho/*.json` file matching the existing schema, then re-run `build.py`.
- Adding a category: add an entry to `app.js`'s `CATEGORIES` array and a new `TAG_COPY` block, plus a new source JSON file.
- Future UGC/voting/ranking (explicitly out of scope now) would need a backend and is a separate, later architectural decision -- not something to bolt onto this static shape.
