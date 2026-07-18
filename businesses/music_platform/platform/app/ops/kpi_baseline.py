#!/usr/bin/env python3
"""B-001 baseline KPI instrumentation (short-term 3 metrics)."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ops_common import write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate baseline KPI report")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/kpi_baseline_latest.json",
        help="Output report JSON",
    )
    return p.parse_args()


def q1(conn: sqlite3.Connection, sql: str) -> float:
    row = conn.execute(sql).fetchone()
    return float(row[0] if row and row[0] is not None else 0.0)


def main() -> int:
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        # Metric 1: Open event ratio on latest snapshot.
        open_event_ratio = q1(
            conn,
            """
            SELECT 1.0 * SUM(CASE WHEN COALESCE(waiting_count, 0) > 0 THEN 1 ELSE 0 END) / COUNT(*)
            FROM event_latest_view
            """,
        )

        # Metric 2: Average fill ratio on latest snapshot.
        avg_fill_ratio = q1(
            conn,
            """
            SELECT AVG(
              CASE
                WHEN COALESCE(complete_count, 0) + COALESCE(waiting_count, 0) > 0
                THEN 1.0 * COALESCE(complete_count, 0) /
                     (COALESCE(complete_count, 0) + COALESCE(waiting_count, 0))
                ELSE NULL
              END
            )
            FROM event_latest_view
            """,
        )

        # Metric 3: Assignment completeness on latest song snapshot.
        assignment_completeness = q1(
            conn,
            """
            SELECT 1.0 * SUM(
                CASE WHEN
                    COALESCE(NULLIF(TRIM(vo), ''), NULLIF(TRIM(cho), ''), NULLIF(TRIM(gt1), ''),
                             NULLIF(TRIM(gt2), ''), NULLIF(TRIM(ba), ''), NULLIF(TRIM(dr), ''),
                             NULLIF(TRIM(key_part), '')) IS NOT NULL
                THEN 1 ELSE 0 END
            ) / COUNT(*)
            FROM song_latest_view
            """,
        )

        total_events = int(
            conn.execute("SELECT COUNT(*) FROM event_latest_view").fetchone()[0]
        )
        total_songs = int(
            conn.execute("SELECT COUNT(*) FROM song_latest_view").fetchone()[0]
        )

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "metrics": {
            "open_event_ratio": open_event_ratio,
            "avg_fill_ratio": avg_fill_ratio,
            "assignment_completeness": assignment_completeness,
        },
        "coverage": {
            "events_latest_count": total_events,
            "songs_latest_count": total_songs,
        },
    }

    write_json(Path(args.out), out)
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
