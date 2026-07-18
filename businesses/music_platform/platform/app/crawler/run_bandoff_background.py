#!/usr/bin/env python3
"""Run bandoff extraction in a continuous background loop.

This script repeatedly runs bandoff crawl jobs at a fixed interval and stores
run snapshots under timestamped directories.
"""

from __future__ import annotations

import argparse
import json
import shutil
import time
from datetime import datetime, timezone
from pathlib import Path

from crawler import crawl_bandoff


def utc_now_compact() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def append_log(log_path: Path, message: str) -> None:
    ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"[{ts}] {message}\n")


def copy_latest_artifacts(run_dir: Path, latest_dir: Path) -> None:
    latest_dir.mkdir(parents=True, exist_ok=True)
    src_db = run_dir / "crawl.db"
    src_summary = run_dir / "summary.json"
    if src_db.exists():
        shutil.copy2(src_db, latest_dir / "crawl.db")
    if src_summary.exists():
        shutil.copy2(src_summary, latest_dir / "summary.json")


def cleanup_old_runs(output_root: Path, keep_last: int) -> None:
    if keep_last <= 0:
        return
    run_dirs = sorted([p for p in output_root.iterdir() if p.is_dir() and p.name.startswith("run_")])
    if len(run_dirs) <= keep_last:
        return
    to_remove = run_dirs[: len(run_dirs) - keep_last]
    for old_dir in to_remove:
        shutil.rmtree(old_dir, ignore_errors=True)


def run_loop(args: argparse.Namespace) -> int:
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    latest_dir = output_root / "latest"
    log_path = output_root / "background_runner.log"

    append_log(log_path, "background runner started")

    run_index = 0
    while True:
        run_index += 1
        run_id = utc_now_compact()
        run_dir = output_root / f"run_{run_id}_{run_index:06d}"

        append_log(log_path, f"run {run_index} started: {run_dir}")

        try:
            exit_code = crawl_bandoff(
                start_url=args.start_url,
                output_dir=run_dir,
                delay_seconds=args.delay_seconds,
                timeout=args.timeout,
                user_agent=args.user_agent,
                max_list_pages=args.max_list_pages,
                max_events=args.max_events,
                include_old_events=not args.exclude_old_events,
                max_old_event_pages=args.max_old_event_pages,
                list_paging_mode=args.list_paging_mode,
                respect_robots=not args.ignore_robots,
            )

            if exit_code == 0:
                copy_latest_artifacts(run_dir, latest_dir)
                cleanup_old_runs(output_root, args.keep_last)
                append_log(log_path, f"run {run_index} succeeded")
            else:
                append_log(log_path, f"run {run_index} finished with exit code {exit_code}")
        except Exception as exc:
            append_log(log_path, f"run {run_index} failed with exception: {exc}")

        if args.max_runs > 0 and run_index >= args.max_runs:
            append_log(log_path, f"background runner reached max-runs={args.max_runs}")
            break

        append_log(log_path, f"sleeping {args.interval_seconds} seconds")
        time.sleep(args.interval_seconds)

    append_log(log_path, "background runner stopped")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Run bandoff extraction continuously in the background."
    )
    parser.add_argument(
        "--start-url",
        default="http://bandoff.info/event/event_list",
        help="Bandoff event list URL",
    )
    parser.add_argument(
        "--output-root",
        default="businesses/music_platform/runtime/crawl/bandoff_background",
        help="Root directory for timestamped run outputs",
    )
    parser.add_argument(
        "--interval-seconds",
        type=int,
        default=60,
        help="Wait time between runs",
    )
    parser.add_argument(
        "--max-runs",
        type=int,
        default=0,
        help="Stop after N runs; 0 means run forever",
    )
    parser.add_argument(
        "--keep-last",
        type=int,
        default=20,
        help="Keep only latest N run directories; 0 disables cleanup",
    )

    parser.add_argument(
        "--max-list-pages",
        type=int,
        default=3,
        help="Maximum NewEvent list pages per run",
    )
    parser.add_argument(
        "--max-old-event-pages",
        type=int,
        default=134,
        help="Maximum OldEvent list pages per run when included",
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
        help="Maximum event detail pages per run",
    )
    parser.add_argument(
        "--delay-seconds",
        type=float,
        default=0.5,
        help="Delay between HTTP requests within a run",
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
        help="Exclude links from OldEvent-content",
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

    if args.interval_seconds < 0:
        parser.error("--interval-seconds must be >= 0")
    if args.max_runs < 0:
        parser.error("--max-runs must be >= 0")
    if args.keep_last < 0:
        parser.error("--keep-last must be >= 0")
    if args.max_list_pages <= 0:
        parser.error("--max-list-pages must be > 0")
    if args.max_events <= 0:
        parser.error("--max-events must be > 0")
    if args.max_old_event_pages <= 0:
        parser.error("--max-old-event-pages must be > 0")
    if args.delay_seconds < 0:
        parser.error("--delay-seconds must be >= 0")

    try:
        return run_loop(args)
    except KeyboardInterrupt:
        stop_info = {
            "stopped": "keyboard_interrupt",
            "at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        }
        print(json.dumps(stop_info, ensure_ascii=False, indent=2))
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
