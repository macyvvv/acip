# Release Notes

## Unreleased

- Initial real implementation of issue #33's MVP spec: 6-category static mobile web app (smoking areas, toilets, convenience stores, ATMs, coin lockers, lodging/internet cafes -- the last two per an operator request beyond the original 4-category scope).
- Data is a first-draft dataset from `market_research/task-0002`'s web-search-grounded research (12 POIs across 6 categories), explicitly flagged as pending human verification -- coordinates are approximate, not geocoded.
- UI copy (tag templates, disclaimer text, SEO metadata, freshness indicators) sourced from `scenario_writing/task-0001` and `doc_creation/task-0001-seo-copy`.
- Deployment target not yet decided -- `web/public/kabukicho/` is a ready-to-serve static bundle once a host is chosen.
- Superseded `app/products/kabukicho_survival_map_mvp/`'s scope (a markdown-brief generator, never a real app) for this product's actual UGC-ready MVP acceptance criteria; that directory is left untouched, not deleted.
