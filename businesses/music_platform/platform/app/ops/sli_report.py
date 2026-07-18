#!/usr/bin/env python3
"""Generate v1 SLI report from execution metadata."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from ops_common import write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Generate SLI report")
    p.add_argument(
        "--runs-dir",
        default="businesses/music_platform/runtime/ops/runs",
        help="Directory of run metadata JSON files",
    )
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/sli_latest.json",
        help="Output SLI report JSON",
    )
    p.add_argument(
        "--min-runs",
        type=int,
        default=3,
        help="Minimum run count required for strict SLI enforcement",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    runs_dir = Path(args.runs_dir)
    files = sorted(runs_dir.glob("*.json"))

    total = 0
    failed = 0
    durations = []
    for f in files[-200:]:
        with f.open("r", encoding="utf-8") as fp:
            d = json.load(fp)
        st = d.get("status")
        # Blocked runs are policy stops, not execution failures.
        if st not in {"success", "failed"}:
            continue
        total += 1
        if st == "failed":
            failed += 1
        try:
            st = datetime.fromisoformat(d["started_at_utc"].replace("Z", "+00:00"))
            ed = datetime.fromisoformat(d["finished_at_utc"].replace("Z", "+00:00"))
            durations.append((ed - st).total_seconds())
        except Exception:
            continue

    failure_rate = (failed / total) if total else 0.0
    durations_sorted = sorted(durations)
    if durations_sorted:
        idx = min(len(durations_sorted) - 1, int(0.95 * (len(durations_sorted) - 1)))
        p95_latency = float(durations_sorted[idx])
    else:
        p95_latency = 0.0

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "runs_count": total,
        "sli_enforceable": total >= int(args.min_runs),
        "failure_rate": failure_rate,
        "p95_latency_seconds": p95_latency,
        "critical_incidents": 0,
    }
    write_json(Path(args.out), out)
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
