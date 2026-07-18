#!/usr/bin/env python3
"""Add segment contract columns required for segment-level analysis."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


REQUIRED_COLUMNS = [
    ("actor_role", "TEXT"),
    ("user_type", "TEXT"),
    ("journey_stage", "TEXT"),
    ("segment_label", "TEXT"),
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Apply segment contract migration")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    return p.parse_args()


def existing_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {str(r[1]) for r in rows}


def add_missing_columns(conn: sqlite3.Connection, table: str) -> None:
    cols = existing_columns(conn, table)
    for col, col_type in REQUIRED_COLUMNS:
        if col not in cols:
            conn.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")


def main() -> int:
    args = parse_args()
    db = Path(args.db)
    with sqlite3.connect(str(db)) as conn:
        add_missing_columns(conn, "event_observations")
        add_missing_columns(conn, "song_observations")
        conn.commit()
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
