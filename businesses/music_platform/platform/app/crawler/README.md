# Crawler

A polite, domain-limited crawler for allowed data collection use cases.

## Why this crawler

- does not execute JavaScript (helps avoid client-side analytics events)
- supports `robots.txt`
- keeps request delay configurable
- stores outputs in SQLite `.db` for later analysis

## Usage

### Generic mode (domain crawl)

```bash
python businesses/music_platform/platform/app/crawler/crawler.py \
  https://example.com \
  --max-pages 30 \
  --delay-seconds 2.0 \
  --output-dir businesses/music_platform/runtime/crawl/example
```

### Bandoff mode (event and song extraction)

```bash
python businesses/music_platform/platform/app/crawler/crawler.py \
  --mode bandoff \
  http://bandoff.info/event/event_list \
  --max-list-pages 5 \
  --list-paging-mode increment \
  --max-old-event-pages 134 \
  --max-events 200 \
  --delay-seconds 2.0 \
  --output-dir businesses/music_platform/runtime/crawl/bandoff
```

### Bandoff background runner (continuous)

```bash
python businesses/music_platform/platform/app/crawler/run_bandoff_background.py \
  --interval-seconds 60 \
  --max-list-pages 3 \
  --list-paging-mode increment \
  --max-old-event-pages 134 \
  --max-events 120 \
  --exclude-old-events \
  --output-root businesses/music_platform/runtime/crawl/bandoff_background
```

Notes:

- Creates run snapshots under output-root as run_YYYYMMDD_HHMMSSZ_NNNNNN
- Copies latest run artifacts to output-root/latest/
- Writes operational logs to output-root/background_runner.log
- Use --max-runs 0 to run forever (default)

### Bandoff one-shot terminal run

```bash
python businesses/music_platform/platform/app/crawler/run_bandoff_once.py
```

OldEvent pages by explicit page increment:

```bash
python businesses/music_platform/platform/app/crawler/run_bandoff_once.py \
  --include-old-events \
  --list-paging-mode increment \
  --max-old-event-pages 134
```

This creates a timestamped run directory under:

- `businesses/music_platform/runtime/crawl/bandoff_once/`

It uses short-delay, no-browser defaults and writes:

- `crawl.db` for the run
- `merged.db` at the output root, deduplicated across all one-shot runs in that root

### Merge background runs into one DB

```bash
python businesses/music_platform/platform/app/crawler/merge_bandoff_runs.py
```

This creates:

- `businesses/music_platform/runtime/crawl/bandoff_background/merged.db`
- `merged_events` and `merged_songs` tables with one row per unique URL
- `duplicate_events` and `duplicate_songs` tables for overlap inspection

## Output files

- `crawl.db`: SQLite database
  - `pages` table: crawled HTML pages
  - `failures` table: skipped/failed URLs with reason
  - `discovered_event_urls` table: event URLs collected from list pages
  - `events` table: normalized event-level records (info + song counts)
  - `songs` table: normalized song rows with member columns
- `summary.json`: run metadata and counts

## Important notes

- Use only when terms and policy allow crawling.
- Keep a conservative request rate.
- Default behavior is same-domain only.
- Do not use `--ignore-robots` unless explicitly authorized.
