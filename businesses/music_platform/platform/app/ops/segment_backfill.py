#!/usr/bin/env python3
"""Backfill segment contract columns with deterministic heuristics."""

from __future__ import annotations

import argparse
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


@dataclass(frozen=True)
class Segment:
    actor_role: str
    user_type: str
    journey_stage: str


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Backfill segment columns")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    return p.parse_args()


def safe_parse_iso(ts: str | None) -> datetime | None:
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except Exception:
        return None


def infer_journey_from_event_dt(event_dt: str | None, fetched_at: str | None) -> str:
    e = safe_parse_iso(event_dt)
    f = safe_parse_iso(fetched_at)
    if e is None or f is None:
        return "discover"
    days = (e - f).total_seconds() / 86400.0
    if days > 7:
        return "discover"
    if days > 1:
        return "entry"
    if days >= 0:
        return "build"
    return "review"


def backfill_event_observations(conn: sqlite3.Connection) -> None:
    counts = {
        row[0]: int(row[1])
        for row in conn.execute(
            """
            SELECT organizer, COUNT(DISTINCT event_id)
            FROM event_observations
            WHERE organizer IS NOT NULL AND TRIM(organizer) <> ''
            GROUP BY organizer
            """
        ).fetchall()
    }

    rows = conn.execute(
        """
        SELECT event_obs_id, organizer, event_datetime, fetched_at_utc
        FROM event_observations
        """
    ).fetchall()

    for event_obs_id, organizer, event_datetime, fetched_at_utc in rows:
        organizer_norm = (organizer or "").strip()
        freq = counts.get(organizer_norm, 0)
        user_type = "repeater" if freq >= 2 else "beginner"
        journey = infer_journey_from_event_dt(event_datetime, fetched_at_utc)
        segment_label = f"organizer_{user_type}"

        conn.execute(
            """
            UPDATE event_observations
            SET actor_role = ?, user_type = ?, journey_stage = ?, segment_label = ?
            WHERE event_obs_id = ?
            """,
            ("organizer", user_type, journey, segment_label, event_obs_id),
        )


def primary_participant_token(row: sqlite3.Row) -> str:
    for key in ("vo", "cho", "gt1", "gt2", "ba", "dr", "key_part"):
        val = row[key]
        if val is not None and str(val).strip() != "":
            return str(val).strip()
    return ""


def backfill_song_observations(conn: sqlite3.Connection) -> None:
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        """
        SELECT
            so.song_obs_id,
            so.fetched_at_utc,
            so.vo,
            so.cho,
            so.gt1,
            so.gt2,
            so.ba,
            so.dr,
            so.key_part,
            eo.event_datetime
        FROM song_observations so
        JOIN song_entities se ON se.song_id = so.song_id
        LEFT JOIN event_observations eo
          ON eo.event_id = se.event_id
         AND eo.fetched_at_utc = so.fetched_at_utc
        """
    ).fetchall()

    token_counts: dict[str, int] = {}
    for r in rows:
        token = primary_participant_token(r)
        if token:
            token_counts[token] = token_counts.get(token, 0) + 1

    for r in rows:
        token = primary_participant_token(r)
        freq = token_counts.get(token, 0)
        user_type = "repeater" if freq >= 2 else "beginner"
        journey = infer_journey_from_event_dt(r["event_datetime"], r["fetched_at_utc"])
        segment_label = f"participant_{user_type}"

        conn.execute(
            """
            UPDATE song_observations
            SET actor_role = ?, user_type = ?, journey_stage = ?, segment_label = ?
            WHERE song_obs_id = ?
            """,
            ("participant", user_type, journey, segment_label, r["song_obs_id"]),
        )


def main() -> int:
    args = parse_args()
    db = Path(args.db)

    with sqlite3.connect(str(db)) as conn:
        backfill_event_observations(conn)
        backfill_song_observations(conn)
        conn.commit()

    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
