#!/usr/bin/env python3
"""Evaluate Stage-2 and Stage-3 transition readiness from ops artifacts."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ops_common import read_json, write_json


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Check stage transition readiness")
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/stage_transition_latest.json",
        help="Output report JSON",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()

    quality = read_json(Path("businesses/music_platform/runtime/ops/reports/quality_gate_latest.json"))
    drift = read_json(Path("businesses/music_platform/runtime/ops/reports/drift_latest.json"))
    gate = read_json(Path("businesses/music_platform/runtime/ops/reports/release_gate_latest.json"))
    signoff = read_json(Path("businesses/music_platform/runtime/ops/reports/gate_signoff_latest.json"))
    foundation = read_json(Path("businesses/music_platform/runtime/ops/reports/instrumentation_foundation_audit_latest.json"))
    seg_ready = read_json(Path("businesses/music_platform/runtime/ops/reports/segment_readiness_latest.json"))
    seg_effect = read_json(Path("businesses/music_platform/runtime/ops/reports/segment_effect_report_latest.json"))
    history = read_json(Path("businesses/music_platform/runtime/ops/reports/drift_history_status_latest.json"))

    stage2_conditions = {
        "quality_pass": quality.get("status") == "pass",
        "gate_not_no_go": gate.get("decision") in {"go", "conditional"},
        "tri_party_signed": bool(signoff.get("signed", False)),
        "foundation_audit_pass": foundation.get("status") == "pass",
        "segment_ready": bool(seg_ready.get("segment_effect_ready", False)),
        "segment_effect_ready": bool(seg_effect.get("segment_effect_ready", False)),
    }

    stage3_conditions = {
        "all_stage2_conditions": all(stage2_conditions.values()),
        "drift_history_ready": bool(history.get("drift_history_ready", False)),
        "gate_is_go": gate.get("decision") == "go",
    }

    stage2_status = "go" if all(stage2_conditions.values()) else "no_go"
    if stage2_status == "go" and gate.get("decision") == "conditional":
        stage2_status = "conditional"

    stage3_status = "go" if all(stage3_conditions.values()) else "conditional"

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "stage2": {
            "status": stage2_status,
            "conditions": stage2_conditions,
        },
        "stage3": {
            "status": stage3_status,
            "conditions": stage3_conditions,
            "blockers": [
                k for k, v in stage3_conditions.items() if not v
            ],
        },
    }

    write_json(Path(args.out), out)
    print(stage3_status)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
