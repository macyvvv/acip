# store_collector

Breadth-first store data pipeline for `cf_gb_relative_system`. Operator-run-
locally only -- **never wired into CI execution**. Stdlib only, no
third-party dependencies (`sqlite3`, `urllib.request`, `html.parser`, all
standard library). See `artifacts/census-pivot-2026-07-21/WBS.md` for the
design decisions this implements and which panel (dataops/devops/
marketingops/ux-research/legalops) made each call.

## Two-step workflow: census, then optional enrichment

**Step 1 -- census** (breadth: what stores exist):

```bash
python census.py <area_id> <area_display_name> candidates/<area>_census.json
```

Inserts a `stores` row per name at `completeness_tier='known'` -- name +
area only, nothing else required. `candidates/*_census.json` is
`[{"name_raw", "existence_confidence", "discovery_note", "store_type"}, ...]`,
compiled by a human/LLM web-search pass using **varied general search
queries**, never by systematically paging through one aggregator site's
full area listing (see `artifacts/S-011/source-register.json`'s
`search-engine-discovery` entry, amended 2026-07-21, for the exact
conditions this must satisfy). There is no search-API credential in this
environment either way, so this step is never fully automated -- only the
DB write is.

`store_type` (`concept_cafe`/`girls_bar`) is optional but should be set
whenever it's already obvious from the query that surfaced the name (a
"ガールズバー" search result already tells you the type) -- omitting a
fact you already have just means backfilling it later via
`update_store_category()`.

**Step 2 -- enrichment** (depth: optional, per store, whenever a verified
official source exists):

```bash
python -c "
import db, enrich_db
with db.open_db() as conn:
    print(enrich_db.enrich_store_from_url(conn, '<store_id>', '<official_url>'))
"
```

or via the older single-store/batch CLIs, which still work standalone and
write to `cache/*.draft.json` as before:

```bash
python collect.py <store_id> <url>
python collect_batch.py candidates/<area>.json   # [{"store_id","url","name_hint"}, ...]
```

`enrich_store_from_url()` requires `store_id` to already have a census row
(raises otherwise -- census always comes before enrichment). It:

1. Checks `artifacts/S-011/source-register.json` before doing anything.
   Refuses (`SourceDenied`) if the URL's domain is on the deny list (the
   named competitor aggregators), or if the `store-official-website` /
   `store-official-sns` category review has expired -- fail-closed, same
   principle as `templates/legal-policy.yaml`. **Never fetch a third-party
   aggregator/listing site.** Only a store's own official website or SNS.
2. Fetches the URL with a standard browser `User-Agent` header (several
   small-business sites 403 the default UA; see
   `artifacts/ueno-pilot-2026-07-21/README.md` for how this was found).
3. Caches the raw response under `cache/<store_id>.html`, logs every
   attempt -- success or failure -- to `cache/fetch_log.jsonl`.
4. Best-effort-extracts a couple of easy fields (page title, meta
   description, phone via a UUID-safe regex -- see the 2026-07-21 commit
   fixing a false-positive match against Strikingly/lit.link page-builder
   UUIDs). Writes `official_url` + a confidently-extracted `phone` into
   `store_enrichment`, and promotes the store's `completeness_tier` from
   `known` to `has_official_source`. Nothing else is auto-written.

## store_type and concept_theme

`stores.store_type` (`concept_cafe`/`girls_bar`/`unknown`) and
`store_enrichment.concept_theme` (free text, e.g. `魔法学園`, `水着`,
`うさぎ`, `くまが働くお店`) are independent of the fetch/enrich pipeline --
set/correct either one at any time, at any tier (including `known`, before
any URL has ever been fetched for that store), with:

```bash
python -c "
import db, enrich_db
with db.open_db() as conn:
    enrich_db.update_store_category(conn, '<store_id>', store_type='girls_bar',
        concept_theme='水着', source_url='<where this was learned>')
"
```

Both arguments are optional (pass whichever you have); `source_url` is
always required, matching the traceability discipline every other write in
this tool follows. Never inferred automatically.

## completeness_tier: known -> has_official_source -> enriched -> verified

`hours`, `pricing_model`, `price_items`, `address`, and `verification_method`
are never set automatically. To reach `enriched`/`verified`, a human (or an
LLM reviewing `cache/<store_id>.html` and the draft's `needs_review` list)
must call `enrich_db.confirm_verified_fields(conn, store_id, address=...,
hours=..., pricing_model=..., price_items=..., verification_method=...,
reliability_score=..., source_url=...)` explicitly -- this represents a
confirmed judgement, not a raw scrape. **Only `verified` counts toward the
Verified Fresh Store Coverage KPI** -- never report a bare row count across
tiers as if it were coverage (see WBS.md's marketingops decision).

## Storage

One shared SQLite `.db` at `data/stores.db` (`area_id` is a column, not a
separate file per area -- see WBS.md section 2 for why). Tables: `areas`,
`stores` (census row), `store_enrichment` (1:1 optional sidecar -- its
*absence* for a store is the "no enrichment yet" state, not a null-filled
row), `store_sns`, `store_change_log` (append-only, mirrors
`schemas/store-artifact.json`'s `change_log`). `data/` is gitignored (see
repo-root `.gitignore`): this is real-run output about real, named
businesses, not source, and stays local until the operator decides
otherwise.

`schemas/store-artifact.json` is the validation contract for the shape a
DB row should satisfy at each tier -- it validates, it does not store; there
is no `data/stores/<id>.json` file format anymore.

## Multi-area scale-out

Adding a new area (Shinjuku, Ikebukuro, Akihabara, ...) needs a new
`candidates/<area>_census.json` and one `census.py <area_id> ...` call --
no code change expected. Census may run wide across many areas in parallel
(cheap, low-risk); treating an area's data as "publishable" stays gated
behind its own verification work, same as OUTCOME_BACKLOG.md's Gate 3/4.

## Why this isn't in `app/`

`app/requirements.lock` declares "no third-party runtime dependencies" as a
promise about the *shipped product skeleton* (packaged by
`app/build_artifact.py`). This tool makes live outbound HTTP requests and
is an internal ops tool, not part of the release artifact -- keeping it in
a sibling `tools/` directory means it can never accidentally get bundled.

## Testing

`tests/` uses only local HTML fixtures, an injected fake fetcher, and
`sqlite3.connect(":memory:")`/`tmp_path` databases -- **no test makes a live
HTTP request or touches `data/stores.db`.** Run with:

```bash
python -m pytest businesses/cf_gb_relative_system/tools/store_collector/tests
```
