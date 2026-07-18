#!/usr/bin/env python3
"""Track drift-history sufficiency progress for gate enforcement."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ops_common import write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Report drift history sufficiency status")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    p.add_argument(
        "--required-active-days",
        type=int,
        default=7,
        help="Required active days for stable drift evaluation",
    )
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/drift_history_status_latest.json",
        help="Output report JSON",
    )
    return p.parse_args()


def active_days(conn: sqlite3.Connection, table: str) -> int:
    row = conn.execute(
        f"SELECT COUNT(DISTINCT date(fetched_at_utc)) FROM {table}"
    ).fetchone()
    return int(row[0] if row and row[0] is not None else 0)


def main() -> int:
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        event_days = active_days(conn, "event_observations")
        song_days = active_days(conn, "song_observations")

    min_days = min(event_days, song_days)
    remaining = max(0, int(args.required_active_days) - min_days)

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "required_active_days": int(args.required_active_days),
        "event_active_days": event_days,
        "song_active_days": song_days,
        "min_active_days": min_days,
        "remaining_days_for_stable_drift": remaining,
        "drift_history_ready": remaining == 0,
    }
    write_json(Path(args.out), out)
    print("ready" if out["drift_history_ready"] else "not_ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
