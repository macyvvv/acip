#!/usr/bin/env python3
"""Report segment-effect analysis readiness from current schema."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ops_common import write_json


REQUIRED_SEGMENT_FIELDS = [
    "actor_role",
    "user_type",
    "journey_stage",
    "segment_label",
]

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check segment analysis readiness")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/segment_readiness_latest.json",
        help="Output report path",
    )
    return p.parse_args()


def table_columns(conn: sqlite3.Connection, table: str) -> set[str]:
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    return {r[1] for r in rows}


def main() -> int:
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        event_cols = table_columns(conn, "event_observations")
        song_cols = table_columns(conn, "song_observations")
        available = sorted((event_cols | song_cols) & set(REQUIRED_SEGMENT_FIELDS))
        missing = sorted(set(REQUIRED_SEGMENT_FIELDS) - set(available))

        quality_checks = {
            "event_actor_role_valid": False,
            "event_user_type_valid": False,
            "event_journey_stage_valid": False,
            "event_segment_label_valid": False,
            "song_actor_role_valid": False,
            "song_user_type_valid": False,
            "song_journey_stage_valid": False,
            "song_segment_label_valid": False,
        }

        if len(missing) == 0:
            event_actor_invalid = conn.execute(
                "SELECT COUNT(*) FROM event_observations WHERE actor_role NOT IN ('organizer', 'participant') OR actor_role IS NULL"
            ).fetchone()[0]
            event_user_invalid = conn.execute(
                "SELECT COUNT(*) FROM event_observations WHERE user_type NOT IN ('beginner', 'repeater') OR user_type IS NULL"
            ).fetchone()[0]
            event_stage_invalid = conn.execute(
                "SELECT COUNT(*) FROM event_observations WHERE journey_stage NOT IN ('discover', 'entry', 'build', 'run', 'review') OR journey_stage IS NULL"
            ).fetchone()[0]
            event_label_invalid = conn.execute(
                "SELECT COUNT(*) FROM event_observations WHERE segment_label NOT IN ('organizer_beginner', 'organizer_repeater', 'participant_beginner', 'participant_repeater') OR segment_label IS NULL"
            ).fetchone()[0]

            song_actor_invalid = conn.execute(
                "SELECT COUNT(*) FROM song_observations WHERE actor_role NOT IN ('organizer', 'participant') OR actor_role IS NULL"
            ).fetchone()[0]
            song_user_invalid = conn.execute(
                "SELECT COUNT(*) FROM song_observations WHERE user_type NOT IN ('beginner', 'repeater') OR user_type IS NULL"
            ).fetchone()[0]
            song_stage_invalid = conn.execute(
                "SELECT COUNT(*) FROM song_observations WHERE journey_stage NOT IN ('discover', 'entry', 'build', 'run', 'review') OR journey_stage IS NULL"
            ).fetchone()[0]
            song_label_invalid = conn.execute(
                "SELECT COUNT(*) FROM song_observations WHERE segment_label NOT IN ('organizer_beginner', 'organizer_repeater', 'participant_beginner', 'participant_repeater') OR segment_label IS NULL"
            ).fetchone()[0]

            quality_checks = {
                "event_actor_role_valid": event_actor_invalid == 0,
                "event_user_type_valid": event_user_invalid == 0,
                "event_journey_stage_valid": event_stage_invalid == 0,
                "event_segment_label_valid": event_label_invalid == 0,
                "song_actor_role_valid": song_actor_invalid == 0,
                "song_user_type_valid": song_user_invalid == 0,
                "song_journey_stage_valid": song_stage_invalid == 0,
                "song_segment_label_valid": song_label_invalid == 0,
            }

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "segment_required_fields": REQUIRED_SEGMENT_FIELDS,
        "available_fields": available,
        "missing_fields": missing,
        "quality_checks": quality_checks,
        "segment_effect_ready": len(missing) == 0 and all(quality_checks.values()),
        "next_action": (
            "Add segment annotation columns or derived mapping table before segment effect reporting"
            if missing
            else "Segment effect reporting can be enabled"
        ),
    }

    write_json(Path(args.out), out)
    print("ready" if out["segment_effect_ready"] else "not_ready")
    return 0 if out["segment_effect_ready"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
