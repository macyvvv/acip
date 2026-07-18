#!/usr/bin/env python3
"""B-002 foundation instrumentation completeness audit."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ops_common import read_json, write_json


REQUIRED_REPORTS = {
    "quality_gate": "businesses/music_platform/runtime/ops/reports/quality_gate_latest.json",
    "drift": "businesses/music_platform/runtime/ops/reports/drift_latest.json",
    "kpi_baseline": "businesses/music_platform/runtime/ops/reports/kpi_baseline_latest.json",
    "sli": "businesses/music_platform/runtime/ops/reports/sli_latest.json",
    "release_gate": "businesses/music_platform/runtime/ops/reports/release_gate_latest.json",
    "gate_signoff": "businesses/music_platform/runtime/ops/reports/gate_signoff_latest.json",
    "segment_readiness": "businesses/music_platform/runtime/ops/reports/segment_readiness_latest.json",
    "segment_effect_report": "businesses/music_platform/runtime/ops/reports/segment_effect_report_latest.json",
}


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Audit foundation instrumentation coverage")
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/instrumentation_foundation_audit_latest.json",
        help="Output audit report JSON",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    coverage = {}
    for k, rel_path in REQUIRED_REPORTS.items():
        p = Path(rel_path)
        coverage[k] = p.exists()

    # Validate signature quality when file exists.
    signoff_ok = False
    signoff_path = Path(REQUIRED_REPORTS["gate_signoff"])
    if signoff_path.exists():
        signoff = read_json(signoff_path)
        signoff_ok = bool(signoff.get("signed", False))

    segment_ready = False
    segment_effect_ready = False
    segment_readiness_path = Path(REQUIRED_REPORTS["segment_readiness"])
    if segment_readiness_path.exists():
        segment_ready = bool(read_json(segment_readiness_path).get("segment_effect_ready", False))

    segment_effect_path = Path(REQUIRED_REPORTS["segment_effect_report"])
    if segment_effect_path.exists():
        segment_effect_ready = bool(read_json(segment_effect_path).get("segment_effect_ready", False))

    status = "pass" if all(coverage.values()) and signoff_ok and segment_ready and segment_effect_ready else "fail"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "foundation_reports": coverage,
        "coverage_ratio": sum(1 for v in coverage.values() if v) / len(coverage),
        "tri_party_signoff_valid": signoff_ok,
        "segment_readiness_valid": segment_ready,
        "segment_effect_report_valid": segment_effect_ready,
        "status": status,
        "scope": "foundation_only",
    }

    write_json(Path(args.out), out)
    print(out["status"])
    return 0 if out["status"] == "pass" else 7


if __name__ == "__main__":
    raise SystemExit(main())
