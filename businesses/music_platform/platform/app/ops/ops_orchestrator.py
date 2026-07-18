#!/usr/bin/env python3
"""A-001/A-006 orchestration entrypoint for daily and weekly ops jobs."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import List

from ops_common import RunMeta, make_run_id, utc_now_iso, write_run_meta


ROOT = Path(__file__).resolve().parents[5]
PY = sys.executable


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run ops jobs")
    p.add_argument("--mode", choices=["daily", "weekly"], required=True)
    p.add_argument(
        "--db",
        default="businesses/music_platform/runtime/crawl/bandoff_research_merged.db",
        help="Normalized DB path",
    )
    return p.parse_args()


def run_cmd(cmd: list[str]) -> int:
    proc = subprocess.run(cmd, cwd=str(ROOT), check=False)
    return int(proc.returncode)


def main() -> int:
    args = parse_args()
    started = utc_now_iso()
    run_id = make_run_id(args.mode)

    runs_dir = ROOT / "businesses/music_platform/runtime/ops/runs"
    runs_dir.mkdir(parents=True, exist_ok=True)

    db = args.db
    steps: List[List[str]] = [
        [PY, "businesses/music_platform/platform/app/ops/create_analysis_views.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/segment_contract_migration.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/segment_backfill.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/quality_gate.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/drift_monitor.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/drift_history_status.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/kpi_baseline.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/segment_readiness.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/segment_effect_report.py", "--db", db],
        [PY, "businesses/music_platform/platform/app/ops/sli_report.py"],
        [PY, "businesses/music_platform/platform/app/ops/release_gate.py"],
        [PY, "businesses/music_platform/platform/app/ops/gate_signoff.py"],
        [PY, "businesses/music_platform/platform/app/ops/instrumentation_audit_foundation.py"],
        [PY, "businesses/music_platform/platform/app/ops/stage_transition_check.py"],
    ]

    # Weekly runs also refresh immutable snapshot for rollback safety.
    if args.mode == "weekly":
        steps.insert(
            0,
            [
                PY,
                "businesses/music_platform/platform/app/ops/snapshot_manager.py",
                "snapshot",
                "--db",
                db,
            ],
        )

    status = "success"
    message = "ok"
    current_step = "start"

    for step in steps:
        current_step = Path(step[1]).name
        rc = run_cmd(step)
        if rc != 0:
            if current_step == "release_gate.py" and rc == 3:
                status = "blocked"
                message = "release_no_go"
                continue
            status = "failed"
            message = f"step_failed:{current_step}:rc={rc}"
            break

    finished = utc_now_iso()
    meta = RunMeta(
        run_id=run_id,
        started_at_utc=started,
        finished_at_utc=finished,
        status=status,
        step=current_step,
        message=message,
    )
    write_run_meta(runs_dir / f"{run_id}.json", meta)

    print(status)
    return 0 if status in {"success", "blocked"} else 4


if __name__ == "__main__":
    raise SystemExit(main())
