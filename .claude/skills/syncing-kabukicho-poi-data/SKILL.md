---
name: syncing-kabukicho-poi-data
description: Edits and safely syncs POI JSON data for kabukicho_survival_map (businesses/kabukicho_survival_map/app/data/*.json and its two mirrors), avoiding the DB-first build pipeline's data-loss trap where a plain build.py run silently overwrites a fresh manual JSON edit with stale SQLite content. Use this whenever adding, editing, or fixing an entry in any kabukicho_survival_map POI JSON file -- e.g. fixing a POI's coordinates/tags/gray_zone_note, adding new POIs, removing a duplicate -- before running build.py or committing.
---

# Editing Kabukicho POI data without losing your edit

## The trap

`businesses/kabukicho_survival_map/app/build.py`'s `build()` function, by
default, runs `poi_db_sync.py export-json` **first** -- exporting the SQLite
DB (`businesses/kabukicho_survival_map/app/data/kabukicho_poi.db`) *into* the
JSON files, then copying those JSON files everywhere. If you hand-edit a JSON
file directly and then run `build.py` normally, your edit gets silently
overwritten by whatever stale data is still in the DB, because the DB was
never told about your edit. This has actually happened twice in this
repository's real history already (once with a `gray_zone_note` on
`smoking.json`, once with a `gray_zone_note`/tag fix on `toilet.json`) --
both times the fix looked like it worked (no error, `build.py` printed
`exported: yes`) and the loss was only caught by re-reading the file
afterward.

## The three mirror locations

Every POI JSON file exists in three places that must all be edited (or all
re-synced from one source of truth) together:
- `businesses/kabukicho_survival_map/app/data/<category>.json`
- `platform/system/runtime/data/kabukicho/<category>.json` (this one is
  `DATA_SOURCE` -- the actual source `build.py` reads from)
- `platform/web/public/kabukicho_survival_map/data/<category>.json`
  (deployable bundle copy)

## Correct order of operations

1. **Edit the JSON directly in all three locations** (a small Python script
   looping over the three paths is simplest and least error-prone -- see
   example below). Do not edit only one and expect a later step to
   propagate it; only `build.py`'s copy step does that, and it copies
   *from* `DATA_SOURCE`, so `DATA_SOURCE` must be one of the paths you
   actually edited.

2. **Import your edit into the DB before running build.py**:
   ```
   python3 businesses/kabukicho_survival_map/app/scripts/poi_db_sync.py import-json
   ```
   This pushes the (now-edited) `DATA_SOURCE` JSON *into* the SQLite DB, so
   the DB is no longer stale relative to your edit.

3. **Now run build.py**:
   ```
   python3 businesses/kabukicho_survival_map/app/build.py
   ```
   Its internal `export-json` step is now a no-op relative to your edit
   (DB and JSON already agree), and it proceeds to copy/render normally.

4. **Verify the edit actually survived** -- don't trust step 3's clean exit
   alone:
   ```
   python3 -c "
   import json
   data = json.load(open('businesses/kabukicho_survival_map/app/data/<category>.json'))
   for e in data:
       if '<distinguishing name substring>' in e.get('name', ''):
           print(e)
   "
   ```

5. **Run the full verification suite** before committing:
   ```
   node -c businesses/kabukicho_survival_map/app/app.js
   node businesses/kabukicho_survival_map/app/tests/test_app_logic.js
   PYTHONPATH=platform .venv/bin/python -m pytest -q
   ```

## If you skip straight to build.py without importing first

You will likely need to redo the edit. Recovery is the same as the correct
order above: re-apply the edit to all three JSON mirrors, then
`import-json`, then `build.py` again -- import-json before build.py, always.

## Example: editing script template

```python
import json
for f in [
    'businesses/kabukicho_survival_map/app/data/<category>.json',
    'platform/system/runtime/data/kabukicho/<category>.json',
    'platform/web/public/kabukicho_survival_map/data/<category>.json',
]:
    data = json.load(open(f))
    for e in data:
        if e.get('name') == '<exact POI name>':
            # mutate e here
            pass
    json.dump(data, open(f, 'w'), ensure_ascii=False, indent=2)
    open(f, 'a').write('\n')
```
