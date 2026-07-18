#!/usr/bin/env python3
"""Run one safe bandoff scrape from the terminal.

This is a thin wrapper around the existing bandoff crawler with conservative
defaults: no browser, no JavaScript, robots respected, short delay, and
SQLite output.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from crawler import crawl_bandoff
from merge_bandoff_runs import merge_runs


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Run one safe bandoff scrape.")
    parser.add_argument(
        "--start-url",
        default="http://bandoff.info/event/event_list",
        help="Bandoff event list URL",
    )
    parser.add_argument(
        "--output-root",
        default="businesses/music_platform/runtime/crawl/bandoff_once",
        help="Directory where the run folder will be created",
    )
    parser.add_argument(
        "--max-list-pages",
        type=int,
        default=3,
        help="Maximum NewEvent list pages to traverse",
    )
    parser.add_argument(
        "--max-old-event-pages",
        type=int,
        default=134,
        help="Maximum OldEvent list pages to traverse when included",
    )
    parser.add_argument(
        "--list-paging-mode",
        choices=("increment", "auto"),
        default="increment",
        help="increment=page parameter increment, auto=follow rel=next",
    )
    parser.add_argument(
        "--max-events",
        type=int,
        default=120,
        help="Maximum event detail pages to extract",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.5,
        help="Delay between HTTP requests",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=15.0,
        help="HTTP request timeout",
    )
    parser.add_argument(
        "--user-agent",
        default="acip-music-platform-crawler/0.1 (+respectful crawl)",
        help="User-Agent header",
    )
    parser.add_argument(
        "--exclude-old-events",
        action="store_true",
        default=True,
        help="Exclude links from OldEvent-content (default on)",
    )
    parser.add_argument(
        "--include-old-events",
        action="store_true",
        help="Include links from OldEvent-content",
    )
    parser.add_argument(
        "--ignore-robots",
        action="store_true",
        help="Disable robots check (use only when legally permitted)",
    )
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    if args.max_list_pages <= 0:
        parser.error("--max-list-pages must be > 0")
    if args.max_events <= 0:
        parser.error("--max-events must be > 0")
    if args.max_old_event_pages <= 0:
        parser.error("--max-old-event-pages must be > 0")
    if args.delay_seconds < 0:
        parser.error("--delay-seconds must be >= 0")

    output_root = Path(args.output_root)
    run_dir = output_root / f"run_{utc_now_compact()}"
    include_old_events = args.include_old_events or not args.exclude_old_events

    exit_code = crawl_bandoff(
        start_url=args.start_url,
        output_dir=run_dir,
        delay_seconds=args.delay_seconds,
        timeout=args.timeout,
        user_agent=args.user_agent,
        max_list_pages=args.max_list_pages,
        max_events=args.max_events,
        include_old_events=include_old_events,
        max_old_event_pages=args.max_old_event_pages,
        list_paging_mode=args.list_paging_mode,
        respect_robots=not args.ignore_robots,
    )

    if exit_code == 0:
        merged_db = output_root / "merged.db"
        merge_runs(output_root, merged_db)

        with sqlite3.connect(str(merged_db)) as conn:
            summary = {
                "mode": "bandoff_once",
                "run_database": str(run_dir / "crawl.db"),
                "merged_database": str(merged_db),
                "merged_counts": {
                    "events": conn.execute("select count(*) from merged_events").fetchone()[0],
                    "songs": conn.execute("select count(*) from merged_songs").fetchone()[0],
                    "duplicate_event_urls": conn.execute(
                        "select count(*) from duplicate_events"
                    ).fetchone()[0],
                    "duplicate_song_urls": conn.execute(
                        "select count(*) from duplicate_songs"
                    ).fetchone()[0],
                },
            }
        print(json.dumps(summary, ensure_ascii=False, indent=2))

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
