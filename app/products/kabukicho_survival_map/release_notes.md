# Release Notes

## Unreleased

- Reworked the layout into a top map / bottom list split, per operator request: the top ~32% of the screen is an embedded Google Map showing pins for the currently selected bottom-nav category; the bottom ~55-65% is the POI list, sorted nearest-first from the user's geolocated position when available (falls back to the original, unsorted order with an inline notice when location access is denied/unavailable). Tapping a list card pans/zooms the map to that POI and opens its info window; tapping a marker does the same in reverse. This reverses this product's original "list-first, no embedded map, no external API dependency" constraint (see `requirements.md`/`architecture.md` for the updated decision) -- it now depends on an operator-configured Google Maps JavaScript API key (`window.KABUKICHO_GMAPS_API_KEY`, same empty-by-default placeholder pattern as the existing GA ID), and gracefully shows a setup notice instead of a blank pane until one is set.
- Initial real implementation of issue #33's MVP spec: 6-category static mobile web app (smoking areas, toilets, convenience stores, ATMs, coin lockers, lodging/internet cafes -- the last two per an operator request beyond the original 4-category scope).
- Data is a first-draft dataset from `market_research/task-0002`'s web-search-grounded research (12 POIs across 6 categories), explicitly flagged as pending human verification -- coordinates are approximate, not geocoded.
- UI copy (tag templates, disclaimer text, SEO metadata, freshness indicators) sourced from `scenario_writing/task-0001` and `doc_creation/task-0001-seo-copy`.
- Deployment target not yet decided -- `web/public/kabukicho/` is a ready-to-serve static bundle once a host is chosen.
- Superseded `app/products/kabukicho_survival_map_mvp/`'s scope (a markdown-brief generator, never a real app) for this product's actual UGC-ready MVP acceptance criteria; that directory is left untouched, not deleted.
