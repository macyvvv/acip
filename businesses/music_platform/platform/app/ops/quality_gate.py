#!/usr/bin/env python3
"""A-002 Data quality gate for normalized bandoff DB."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ops_common import read_json, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run data quality gate checks")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    p.add_argument(
        "--thresholds",
        default="businesses/music_platform/platform/app/ops/quality_thresholds.json",
        help="Path to quality threshold JSON",
    )
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/quality_gate_latest.json",
        help="Output report path",
    )
    return p.parse_args()


def q1(conn: sqlite3.Connection, sql: str) -> float:
    row = conn.execute(sql).fetchone()
    return float(row[0] if row and row[0] is not None else 0.0)


def main() -> int:
    args = parse_args()
    db = Path(args.db)
    thresholds = read_json(Path(args.thresholds))

    with sqlite3.connect(str(db)) as conn:
        metrics = {
            "null_event_url_rate": q1(
                conn,
                "SELECT 1.0 * SUM(CASE WHEN event_url IS NULL OR TRIM(event_url)='' THEN 1 ELSE 0 END) / COUNT(*) FROM events",
            ),
            "null_organizer_rate": q1(
                conn,
                "SELECT 1.0 * SUM(CASE WHEN organizer IS NULL OR TRIM(organizer)='' THEN 1 ELSE 0 END) / COUNT(*) FROM event_observations",
            ),
            "duplicate_event_observation_rate": q1(
                conn,
                "SELECT 1.0 * COUNT(*) / (SELECT COUNT(*) FROM event_observations) FROM (SELECT event_id, fetched_at_utc, COUNT(*) c FROM event_observations GROUP BY event_id, fetched_at_utc HAVING c > 1)",
            ),
            "null_song_title_rate": q1(
                conn,
                "SELECT 1.0 * SUM(CASE WHEN song_title IS NULL OR TRIM(song_title)='' THEN 1 ELSE 0 END) / COUNT(*) FROM song_observations",
            ),
            "null_artist_rate": q1(
                conn,
                "SELECT 1.0 * SUM(CASE WHEN artist IS NULL OR TRIM(artist)='' THEN 1 ELSE 0 END) / COUNT(*) FROM song_observations",
            ),
            "duplicate_song_observation_rate": q1(
                conn,
                "SELECT 1.0 * COUNT(*) / (SELECT COUNT(*) FROM song_observations) FROM (SELECT song_id, fetched_at_utc, COUNT(*) c FROM song_observations GROUP BY song_id, fetched_at_utc HAVING c > 1)",
            ),
            "orphan_song_entity_rate": q1(
                conn,
                "SELECT 1.0 * SUM(CASE WHEN e.event_id IS NULL THEN 1 ELSE 0 END) / COUNT(*) FROM song_entities s LEFT JOIN events e ON e.event_id=s.event_id",
            ),
            "latest_observation_age_days": q1(
                conn,
                "SELECT julianday('now') - julianday(MAX(fetched_at_utc)) FROM event_observations",
            ),
        }

    checks = {
        "events.max_null_event_url_rate": metrics["null_event_url_rate"]
        <= float(thresholds["events"]["max_null_event_url_rate"]),
        "events.max_null_organizer_rate": metrics["null_organizer_rate"]
        <= float(thresholds["events"]["max_null_organizer_rate"]),
        "events.max_duplicate_event_observation_rate": metrics[
            "duplicate_event_observation_rate"
        ]
        <= float(thresholds["events"]["max_duplicate_event_observation_rate"]),
        "songs.max_null_song_title_rate": metrics["null_song_title_rate"]
        <= float(thresholds["songs"]["max_null_song_title_rate"]),
        "songs.max_null_artist_rate": metrics["null_artist_rate"]
        <= float(thresholds["songs"]["max_null_artist_rate"]),
        "songs.max_duplicate_song_observation_rate": metrics[
            "duplicate_song_observation_rate"
        ]
        <= float(thresholds["songs"]["max_duplicate_song_observation_rate"]),
        "songs.max_orphan_song_entity_rate": metrics["orphan_song_entity_rate"]
        <= float(thresholds["songs"]["max_orphan_song_entity_rate"]),
        "freshness.max_latest_observation_age_days": metrics[
            "latest_observation_age_days"
        ]
        <= float(thresholds["freshness"]["max_latest_observation_age_days"]),
    }

    status = "pass" if all(checks.values()) else "fail"
    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "db": str(db),
        "status": status,
        "metrics": metrics,
        "checks": checks,
        "failed_checks": [k for k, v in checks.items() if not v],
    }
    write_json(Path(args.out), out)
    print(out["status"])
    return 0 if status == "pass" else 2


if __name__ == "__main__":
    raise SystemExit(main())
