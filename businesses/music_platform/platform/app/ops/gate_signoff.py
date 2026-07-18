#!/usr/bin/env python3
"""Tri-party gate signoff record (DevOps/DataOps/MLOps)."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from pathlib import Path

from ops_common import read_json, write_json


REQUIRED_ROLES = ("devops", "dataops", "mlops")


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Create tri-party gate signoff")
    p.add_argument(
        "--gate",
        default="businesses/music_platform/runtime/ops/reports/release_gate_latest.json",
        help="Release gate decision JSON",
    )
    p.add_argument("--devops", default="system-devops", help="DevOps approver")
    p.add_argument("--dataops", default="system-dataops", help="DataOps approver")
    p.add_argument("--mlops", default="system-mlops", help="MLOps approver")
    p.add_argument(
        "--out",
        default="businesses/music_platform/runtime/ops/reports/gate_signoff_latest.json",
        help="Output signoff JSON",
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    gate = read_json(Path(args.gate))

    decision = gate.get("decision", "no_go")
    approvers = {
        "devops": args.devops,
        "dataops": args.dataops,
        "mlops": args.mlops,
    }

    missing_roles = [r for r in REQUIRED_ROLES if not approvers.get(r)]
    signed = len(missing_roles) == 0

    out = {
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "gate_decision": decision,
        "gate_reasons": gate.get("reasons", []),
        "approvers": approvers,
        "missing_roles": missing_roles,
        "signed": signed,
        "promotion_allowed": signed and decision in {"go", "conditional"},
    }

    write_json(Path(args.out), out)
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
