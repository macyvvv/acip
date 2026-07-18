#!/usr/bin/env python3
"""Generate segment-level effect difference report."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

from ops_common import write_json


REQUIRED_SEGMENTS = [
    "participant_beginner",
    "participant_repeater",
    "organizer_beginner",
    "organizer_repeater",
]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate segment effect report")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/segment_effect_report_latest.json",
        help="Output report path",
    )
    return p.parse_args()


def qrows(conn: sqlite3.Connection, sql: str) -> List[Tuple[Any, ...]]:
    return [tuple(r) for r in conn.execute(sql).fetchall()]


def main() -> int:
    args = parse_args()
    with sqlite3.connect(args.db) as conn:
        organizer_rows = qrows(
            conn,
            """
            SELECT
                            eo.segment_label,
              COUNT(*) AS events,
              AVG(CASE
                                        WHEN COALESCE(eo.complete_count, 0) + COALESCE(eo.waiting_count, 0) > 0
                                        THEN 1.0 * COALESCE(eo.complete_count, 0) /
                                                 (COALESCE(eo.complete_count, 0) + COALESCE(eo.waiting_count, 0))
                    ELSE NULL
                  END) AS avg_fill_ratio,
                            AVG(CASE WHEN COALESCE(eo.waiting_count, 0) > 0 THEN 1.0 ELSE 0.0 END) AS open_event_ratio
                        FROM event_observations eo
                        JOIN (
                            SELECT event_id, MAX(fetched_at_utc) AS max_fetched
                            FROM event_observations
                            GROUP BY event_id
                        ) m
                            ON m.event_id = eo.event_id AND m.max_fetched = eo.fetched_at_utc
                        WHERE eo.segment_label IN ('organizer_beginner', 'organizer_repeater')
                        GROUP BY eo.segment_label
            """,
        )

        participant_rows = qrows(
            conn,
            """
            SELECT
                            so.segment_label,
              COUNT(*) AS songs,
              AVG(CASE WHEN COALESCE(NULLIF(TRIM(vo), ''), NULLIF(TRIM(cho), ''),
                                     NULLIF(TRIM(gt1), ''), NULLIF(TRIM(gt2), ''),
                                     NULLIF(TRIM(ba), ''), NULLIF(TRIM(dr), ''),
                                     NULLIF(TRIM(key_part), '')) IS NOT NULL
                       THEN 1.0 ELSE 0.0 END) AS assignment_completeness
                        FROM song_observations so
                        JOIN (
                            SELECT song_id, MAX(fetched_at_utc) AS max_fetched
                            FROM song_observations
                            GROUP BY song_id
                        ) m
                            ON m.song_id = so.song_id AND m.max_fetched = so.fetched_at_utc
                        WHERE so.segment_label IN ('participant_beginner', 'participant_repeater')
                        GROUP BY so.segment_label
            """,
        )

    organizer_metrics: Dict[str, Dict[str, float]] = {
        r[0]: {
            "events": int(r[1]),
            "avg_fill_ratio": float(r[2]) if r[2] is not None else 0.0,
            "open_event_ratio": float(r[3]) if r[3] is not None else 0.0,
        }
        for r in organizer_rows
    }
    participant_metrics: Dict[str, Dict[str, float]] = {
        r[0]: {
            "songs": int(r[1]),
            "assignment_completeness": float(r[2]) if r[2] is not None else 0.0,
        }
        for r in participant_rows
    }

    present = set(organizer_metrics.keys()) | set(participant_metrics.keys())
    missing = [s for s in REQUIRED_SEGMENTS if s not in present]

    out: Dict[str, Any] = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "required_segments": REQUIRED_SEGMENTS,
        "missing_segments": missing,
        "segment_effect_ready": len(missing) == 0,
        "organizer_metrics": organizer_metrics,
        "participant_metrics": participant_metrics,
    }

    write_json(Path(args.out), out)
    print("ready" if out["segment_effect_ready"] else "not_ready")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
