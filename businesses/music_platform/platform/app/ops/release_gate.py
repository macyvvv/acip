#!/usr/bin/env python3
"""A-005/A-006 Release gate evaluation and block decision."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ops_common import read_json, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Evaluate release gate")
    p.add_argument(
        "--quality",
        default="businesses/music_platform/runtime/ops/reports/quality_gate_latest.json",
        help="Quality gate report JSON",
    )
    p.add_argument(
        "--drift",
        default="businesses/music_platform/runtime/ops/reports/drift_latest.json",
        help="Drift report JSON",
    )
    p.add_argument(
        "--sli",
        default="businesses/music_platform/runtime/ops/reports/sli_latest.json",
        help="SLI report JSON",
    )
    p.add_argument(
        "--policy",
        default="businesses/music_platform/platform/app/ops/gate_policy.json",
        help="Gate policy JSON",
    )
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/release_gate_latest.json",
        help="Output gate decision JSON",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    quality = read_json(Path(args.quality))
    drift = read_json(Path(args.drift))
    sli = read_json(Path(args.sli))
    policy = read_json(Path(args.policy))

    reasons: list[str] = []
    decision = "go"

    if policy["rules"]["no_go_if_quality_fail"] and quality.get("status") != "pass":
        reasons.append("quality_gate_failed")
        decision = "no_go"

    if policy["rules"]["no_go_if_drift_red"] and drift.get("overall") == "red":
        reasons.append("drift_red")
        decision = "no_go"

    insufficient_history = bool(
        drift.get("data_sufficiency", {}).get("insufficient_history", False)
    )

    max_fail = float(policy["sli"]["max_failure_rate"])
    max_p95 = float(policy["sli"]["max_p95_latency_seconds"])
    max_critical = int(policy["sli"]["max_critical_incidents"])
    min_runs = int(policy["sli"].get("min_runs_for_enforcement", 1))

    sli_enforceable = int(sli.get("runs_count", 0)) >= min_runs

    sli_breach = (
        float(sli["failure_rate"]) > max_fail
        or float(sli["p95_latency_seconds"]) > max_p95
        or int(sli["critical_incidents"]) > max_critical
    )

    if policy["rules"]["no_go_if_sli_breach"] and sli_enforceable and sli_breach:
        reasons.append("sli_breach")
        decision = "no_go"

    if (
        decision == "go"
        and policy["rules"]["conditional_if_drift_yellow"]
        and drift.get("overall") == "yellow"
    ):
        reasons.append("drift_yellow")
        decision = "conditional"

    if decision == "go" and insufficient_history:
        reasons.append("insufficient_history")
        decision = "conditional"

    if decision == "go" and not sli_enforceable:
        reasons.append("sli_insufficient_runs")
        decision = "conditional"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "decision": decision,
        "reasons": reasons,
        "inputs": {
            "quality": str(Path(args.quality)),
            "drift": str(Path(args.drift)),
            "sli": str(Path(args.sli)),
            "policy": str(Path(args.policy)),
        },
    }
    write_json(Path(args.out), out)
    print(out["decision"])
    return 0 if decision != "no_go" else 3


if __name__ == "__main__":
    raise SystemExit(main())
