#!/usr/bin/env python3
"""Merge bandoff background run databases into one SQLite database.

The script also writes duplicate audit tables so the caller can inspect how
many repeated event URLs and song URLs were collected across runs.
"""

from __future__ import annotations

import argparse
import sqlite3
from collections import defaultdict
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Merge bandoff crawl run databases.")
    parser.add_argument(
        "--source-root",
        default="businesses/music_platform/runtime/crawl/bandoff_background",
        help="Directory containing run_* subdirectories with crawl.db files",
    )
    parser.add_argument(
        "--output-db",
        default="businesses/music_platform/runtime/crawl/bandoff_background/merged.db",
        help="Destination merged SQLite database",
    )
    return parser


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.execute("create table if not exists source_runs(run_dir text primary key, db_path text)")
    conn.execute(
        """
        create table if not exists merged_events (
            event_url text primary key,
            event_slug text,
            fetched_at_utc text,
            complete_count integer,
            waiting_count integer,
            event_info_json text,
            source_db text
        )
        """
    )
    conn.execute(
        """
        create table if not exists merged_songs (
            song_url text primary key,
            event_url text,
            event_slug text,
            source_table text,
            song_title text,
            artist text,
            status text,
            vo text,
            cho text,
            gt1 text,
            gt2 text,
            ba text,
            dr text,
            key_part text,
            fetched_at_utc text,
            source_db text
        )
        """
    )
    conn.execute(
        """
        create table if not exists duplicate_events (
            event_url text,
            count integer,
            first_db text,
            last_db text
        )
        """
    )
    conn.execute(
        """
        create table if not exists duplicate_songs (
            song_url text,
            count integer,
            first_db text,
            last_db text
        )
        """
    )


def merge_runs(source_root: Path, output_db: Path) -> None:
    output_db.parent.mkdir(parents=True, exist_ok=True)
    if output_db.exists():
        output_db.unlink()

    run_dirs = sorted(
        [p for p in source_root.iterdir() if p.is_dir() and p.name.startswith("run_")]
    )

    all_event_rows = []
    all_song_rows = []

    with sqlite3.connect(str(output_db)) as conn:
        ensure_schema(conn)

        for run_dir in run_dirs:
            db_path = run_dir / "crawl.db"
            if not db_path.exists():
                continue
            conn.execute("insert or replace into source_runs values (?, ?)", (run_dir.name, str(db_path)))
            with sqlite3.connect(str(db_path)) as src:
                event_rows = src.execute(
                    "select event_url,event_slug,fetched_at_utc,complete_count,waiting_count,event_info_json from events"
                ).fetchall()
                song_rows = src.execute(
                    "select event_url,event_slug,source_table,song_title,song_url,artist,status,vo,cho,gt1,gt2,ba,dr,key_part,fetched_at_utc from songs"
                ).fetchall()
                all_event_rows.extend([(*row, str(db_path)) for row in event_rows])
                all_song_rows.extend([(*row, str(db_path)) for row in song_rows])

        events_by_url: dict[str, list[tuple]] = defaultdict(list)
        songs_by_url: dict[str, list[tuple]] = defaultdict(list)
        for row in all_event_rows:
            events_by_url[row[0]].append(row)
        for row in all_song_rows:
            songs_by_url[row[4]].append(row)

        for event_url, rows in events_by_url.items():
            if len(rows) > 1:
                conn.execute(
                    "insert into duplicate_events values (?,?,?,?)",
                    (event_url, len(rows), rows[0][6], rows[-1][6]),
                )
            chosen = rows[-1]
            conn.execute(
                """
                insert or replace into merged_events (
                    event_url,event_slug,fetched_at_utc,complete_count,waiting_count,event_info_json,source_db
                ) values (?,?,?,?,?,?,?)
                """,
                chosen,
            )

        for song_url, rows in songs_by_url.items():
            if len(rows) > 1:
                conn.execute(
                    "insert into duplicate_songs values (?,?,?,?)",
                    (song_url, len(rows), rows[0][15], rows[-1][15]),
                )
            chosen = rows[-1]
            conn.execute(
                """
                insert or replace into merged_songs (
                    song_url,event_url,event_slug,source_table,song_title,artist,status,vo,cho,gt1,gt2,ba,dr,key_part,fetched_at_utc,source_db
                ) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                """,
                (
                    chosen[4],
                    chosen[0],
                    chosen[1],
                    chosen[2],
                    chosen[3],
                    chosen[5],
                    chosen[6],
                    chosen[7],
                    chosen[8],
                    chosen[9],
                    chosen[10],
                    chosen[11],
                    chosen[12],
                    chosen[13],
                    chosen[14],
                    chosen[15],
                ),
            )

        conn.commit()


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    source_root = Path(args.source_root)
    output_db = Path(args.output_db)
    merge_runs(source_root, output_db)

    with sqlite3.connect(str(output_db)) as conn:
        print(f"merged db: {output_db}")
        print(f"raw event rows: {conn.execute('select sum(count) from duplicate_events').fetchone()[0] or conn.execute('select count(*) from merged_events').fetchone()[0]}")
        print(f"raw song rows: {conn.execute('select sum(count) from duplicate_songs').fetchone()[0] or conn.execute('select count(*) from merged_songs').fetchone()[0]}")
        print(f"unique event urls: {conn.execute('select count(*) from merged_events').fetchone()[0]}")
        print(f"unique song urls: {conn.execute('select count(*) from merged_songs').fetchone()[0]}")
        print(f"duplicate event urls: {conn.execute('select count(*) from duplicate_events').fetchone()[0]}")
        print(f"duplicate song urls: {conn.execute('select count(*) from duplicate_songs').fetchone()[0]}")
        print(f"merged events rows: {conn.execute('select count(*) from merged_events').fetchone()[0]}")
        print(f"merged songs rows: {conn.execute('select count(*) from merged_songs').fetchone()[0]}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
