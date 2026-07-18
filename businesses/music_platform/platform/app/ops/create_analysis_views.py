#!/usr/bin/env python3
"""A-003 Create analysis-ready views for normalized schema."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create analysis views")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    return p.parse_args()


SQL = """
CREATE VIEW IF NOT EXISTS event_latest_view AS
SELECT eo.*
FROM event_observations eo
JOIN (
  SELECT event_id, MAX(fetched_at_utc) AS max_fetched
  FROM event_observations
  GROUP BY event_id
) m
ON eo.event_id = m.event_id AND eo.fetched_at_utc = m.max_fetched;

CREATE VIEW IF NOT EXISTS song_latest_view AS
SELECT so.*
FROM song_observations so
JOIN (
  SELECT song_id, MAX(fetched_at_utc) AS max_fetched
  FROM song_observations
  GROUP BY song_id
) m
ON so.song_id = m.song_id AND so.fetched_at_utc = m.max_fetched;

CREATE VIEW IF NOT EXISTS event_observation_timeseries_view AS
SELECT
  date(fetched_at_utc) AS d,
  COUNT(*) AS observations,
  COUNT(DISTINCT event_id) AS unique_events
FROM event_observations
GROUP BY date(fetched_at_utc)
ORDER BY d;

CREATE VIEW IF NOT EXISTS song_observation_timeseries_view AS
SELECT
  date(fetched_at_utc) AS d,
  COUNT(*) AS observations,
  COUNT(DISTINCT song_id) AS unique_songs
FROM song_observations
GROUP BY date(fetched_at_utc)
ORDER BY d;
"""


def main() -> int:
    args = parse_args()
    db = Path(args.db)

    with sqlite3.connect(str(db)) as conn:
        conn.executescript(SQL)
        conn.commit()

        checks = {
            "event_latest_view": conn.execute(
                "SELECT COUNT(*) FROM event_latest_view"
            ).fetchone()[0],
            "song_latest_view": conn.execute(
                "SELECT COUNT(*) FROM song_latest_view"
            ).fetchone()[0],
            "event_observation_timeseries_view": conn.execute(
                "SELECT COUNT(*) FROM event_observation_timeseries_view"
            ).fetchone()[0],
            "song_observation_timeseries_view": conn.execute(
                "SELECT COUNT(*) FROM song_observation_timeseries_view"
            ).fetchone()[0],
        }

    for k, v in checks.items():
        print(f"{k}: {v}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
