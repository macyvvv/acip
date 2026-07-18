#!/usr/bin/env python3
"""A-004 Drift monitor v1 using simple PSI on daily counts."""

from __future__ import annotations

import argparse
import math
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from ops_common import read_json, write_json


EPS = 1e-9


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run drift monitor")
    p.add_argument("--db", required=True, help="Path to normalized SQLite DB")
    p.add_argument(
        "--thresholds",
        default="businesses/music_platform/platform/app/ops/drift_thresholds.json",
        help="Path to drift threshold JSON",
    )
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/drift_latest.json",
        help="Output report path",
    )
    p.add_argument(
        "--min-active-days",
        type=int,
        default=7,
        help="Minimum active days required for stable drift evaluation",
    )
    return p.parse_args()


def psi(expected: list[float], actual: list[float]) -> float:
    total = 0.0
    for e, a in zip(expected, actual):
        e2 = max(e, EPS)
        a2 = max(a, EPS)
        total += (a2 - e2) * math.log(a2 / e2)
    return total


def classify(v: float, green_max: float, yellow_max: float) -> str:
    if v <= green_max:
        return "green"
    if v <= yellow_max:
        return "yellow"
    return "red"


def daily_counts(conn: sqlite3.Connection, table: str, days: int, offset_days: int) -> list[float]:
    sql = f"""
    WITH day_series AS (
      SELECT date('now', '-' || n || ' day') AS d
      FROM (
        WITH RECURSIVE r(n) AS (
          SELECT {offset_days}
          UNION ALL
          SELECT n+1 FROM r WHERE n < {offset_days + days - 1}
        )
        SELECT n FROM r
      )
    )
    SELECT d.d, COALESCE(c.cnt, 0) AS cnt
    FROM day_series d
    LEFT JOIN (
      SELECT date(fetched_at_utc) AS d, COUNT(*) AS cnt
      FROM {table}
      GROUP BY date(fetched_at_utc)
    ) c
      ON c.d = d.d
    ORDER BY d.d;
    """
    rows = conn.execute(sql).fetchall()
    counts = [float(r[1]) for r in rows]
    s = sum(counts)
    if s <= 0:
        return [1.0 / len(counts)] * len(counts)
    return [c / s for c in counts]


def active_days(conn: sqlite3.Connection, table: str, days: int, offset_days: int) -> int:
        sql = f"""
        SELECT COUNT(DISTINCT date(fetched_at_utc))
        FROM {table}
        WHERE date(fetched_at_utc) BETWEEN date('now', '-{offset_days + days - 1} day')
            AND date('now', '-{offset_days} day');
        """
        row = conn.execute(sql).fetchone()
        return int(row[0] if row and row[0] is not None else 0)


def main() -> int:
    args = parse_args()
    cfg = read_json(Path(args.thresholds))
    baseline_days = int(cfg["window"]["baseline_days"])
    recent_days = int(cfg["window"]["recent_days"])

    with sqlite3.connect(args.db) as conn:
        ev_recent_active_days = active_days(conn, "event_observations", recent_days, 0)
        so_recent_active_days = active_days(conn, "song_observations", recent_days, 0)
        ev_expected = daily_counts(conn, "event_observations", baseline_days, recent_days)
        ev_actual = daily_counts(conn, "event_observations", recent_days, 0)
        so_expected = daily_counts(conn, "song_observations", baseline_days, recent_days)
        so_actual = daily_counts(conn, "song_observations", recent_days, 0)

    # Normalize dimensions to recent_days for simple v1 PSI.
    # We bucket baseline by aggregating into recent-sized bins.
    def rebucket(vals: list[float], target_bins: int) -> list[float]:
        chunk = max(1, len(vals) // target_bins)
        out: list[float] = []
        for i in range(0, len(vals), chunk):
            out.append(sum(vals[i : i + chunk]))
        while len(out) < target_bins:
            out.append(0.0)
        return out[:target_bins]

    ev_expected_b = rebucket(ev_expected, recent_days)
    so_expected_b = rebucket(so_expected, recent_days)

    ev_psi = psi(ev_expected_b, ev_actual)
    so_psi = psi(so_expected_b, so_actual)

    ev_t = cfg["thresholds"]["event_count_psi"]
    so_t = cfg["thresholds"]["song_count_psi"]

    status_event = classify(ev_psi, float(ev_t["green_max"]), float(ev_t["yellow_max"]))
    status_song = classify(so_psi, float(so_t["green_max"]), float(so_t["yellow_max"]))

    insufficient_history = (
        ev_recent_active_days < args.min_active_days
        or so_recent_active_days < args.min_active_days
    )

    report = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "window": {"baseline_days": baseline_days, "recent_days": recent_days},
        "data_sufficiency": {
            "min_active_days": args.min_active_days,
            "event_recent_active_days": ev_recent_active_days,
            "song_recent_active_days": so_recent_active_days,
            "insufficient_history": insufficient_history,
        },
        "metrics": {
            "event_count_psi": ev_psi,
            "song_count_psi": so_psi,
        },
        "status": {
            "event_count_psi": status_event,
            "song_count_psi": status_song,
        },
    }

    if insufficient_history:
        report["overall"] = "yellow"
        report["notes"] = ["insufficient_history"]
    elif "red" in report["status"].values():
        report["overall"] = "red"
    elif "yellow" in report["status"].values():
        report["overall"] = "yellow"
    else:
        report["overall"] = "green"

    write_json(Path(args.out), report)
    print(report["overall"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
