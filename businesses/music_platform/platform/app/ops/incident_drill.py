#!/usr/bin/env python3
"""A-009 style mini incident drill for rollback validation."""

from __future__ import annotations

import argparse
import sqlite3
from pathlib import Path

from snapshot_manager import cmd_fallback


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run mini incident drill")
    p.add_argument("--db", required=True, help="Target DB path")
    p.add_argument(
        "--manifest",
        default="businesses/music_platform/runtime/ops/snapshots/rollback_manifest_latest.json",
        help="Rollback manifest path",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    db = Path(args.db)

    # Fault injection: create and drop a temp marker table to simulate a bad deploy step.
    with sqlite3.connect(str(db)) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS _incident_marker (id INTEGER PRIMARY KEY)")
        conn.execute("INSERT INTO _incident_marker DEFAULT VALUES")
        conn.commit()

    rc = cmd_fallback(
        argparse.Namespace(
            manifest=args.manifest,
            db=str(db),
        )
    )

    with sqlite3.connect(str(db)) as conn:
        row = conn.execute("PRAGMA integrity_check").fetchone()
        ok = row and row[0] == "ok"

    if rc == 0 and ok:
        print("incident_drill_pass")
        return 0
    print("incident_drill_fail")
    return 5


if __name__ == "__main__":
    raise SystemExit(main())
