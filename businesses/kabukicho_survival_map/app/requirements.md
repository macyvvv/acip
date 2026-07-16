# Requirements

Source: GitHub issue #33 (PRODUCT-0003: Kabukicho Survival Map MVP, UGC-ready), plus two operator-requested category additions (coin lockers, lodging incl. internet cafes).

## Functional Requirements

- 6 POI categories: smoking areas, toilets, convenience stores, ATMs, coin lockers, lodging/internet cafes.
- Each POI: name, lat/lng, description, category, tags (array), last_updated, reliability_score (1-5), source_type (official/observed/inferred), type (official/unofficial).
- Mobile-first, bottom navigation, 1-tap category toggle.
- Top ~32% of the viewport is an embedded Google Map, pinned with the POIs of the currently selected bottom-nav category; re-pins and re-fits bounds on category switch. **(Operator-requested change, 2026-07-11 -- supersedes the original "list-first, no embedded map" requirement below.)**
- Bottom ~55-65% of the viewport is the POI list, sorted nearest-first using the browser's geolocation API when granted; falls back to the original unsorted order plus an inline notice when location access is unavailable or denied.
- Tapping a list card pans/zooms the map to that POI and opens its info window; tapping a marker opens the same info window. The card's "位置情報を見る" link still also opens Google Maps as an external link (unchanged).
- Tag-based evaluation only (no free-form rating).
- Unofficial/gray-zone locations clearly labeled with a disclaimer banner.
- Freshness indicators (recently updated / may be outdated).
- SEO title + meta description.
- Google Analytics placeholder, ID injected via config, never hardcoded.
- GA4-oriented event surfaces must exist for mode/category/filter/card/map/ad interactions.
- Google Maps JavaScript API key placeholder (`window.KABUKICHO_GMAPS_API_KEY`), injected via config, never hardcoded -- same pattern as the GA ID. Empty by default; the map pane shows a setup notice instead of silently staying blank until an operator sets a real, referrer-restricted key.
- SEO/AIO: full POI list pre-rendered as static HTML at build time (not client-side-only), JSON-LD structured data (`ItemList`/`Place` + `FAQPage`), a visible FAQ section, and `robots.txt` explicitly allowing standard + AI answer-engine crawlers. See `architecture.md`'s "SEO/AIO" section. `sitemap.xml`/canonical tag activate once `KABUKICHO_SITE_URL` is set.
- The layout must reserve explicit sponsored / affiliate placement areas without blocking the primary utility flow.
- Sponsored / affiliate modules must be visually differentiated from organic POI results.

## Non-Functional Requirements

- No backend, no authentication.
- Static JSON-based data, no runtime data fetching beyond the local `data/*.json` files.
- Fast rendering, no blocking assets.
- No over-engineering: no bundler, no framework -- plain HTML/CSS/JS plus a small Python copy-script for the build step. The map uses the classic `google.maps.Marker` (not `AdvancedMarkerElement`) specifically to avoid an extra `libraries=marker` script param for what is a handful of static pins.
- Monetization placement must degrade gracefully when empty; the page layout should not collapse or leave broken gaps.

## Superseded requirement (kept for history)

The original spec (below) explicitly ruled out an embedded map and any external API dependency. The operator explicitly requested reversing this on 2026-07-11 ("画面の上半分はgooglemapを表示して...ピンを立てる。下半分は...現在地の最寄りから情報を...示していく") -- this is a deliberate, requested architecture change, not drift:

- ~~List-first (no embedded map).~~
- ~~Tap a POI opens Google Maps (external link only -- no map embedding).~~
- ~~No external API dependency (Google Maps is an outbound link only, not an embed/API call).~~

## Explicitly Out of Scope (per issue #33's "Future" section)

- User submission (UGC), voting, ranking, real-time updates.
- Deployment target selection (separate, later decision) -- explicitly gated on having a distribution strategy first (operator, 2026-07-13: "出しても人に見られる見込みがないならやれません"). The SEO/AIO work above is that strategy's technical half; the remaining piece is distribution/promotion channels, not more implementation.
