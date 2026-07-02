#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def _parse_bool(value: str) -> bool:
    normalized = value.strip().lower()
    if normalized in {"true", "1", "yes"}:
        return True
    if normalized in {"false", "0", "no"}:
        return False
    raise argparse.ArgumentTypeError("execution-enabled must be true or false")


def _format_md(payload: dict[str, object]) -> str:
    return "\n".join(
        [
            "# AUTONOMOUS_EXECUTION_APPROVAL",
            "",
            f"approval_id: {payload.get('approval_id') or ''}",
            f"handoff_id: {payload.get('handoff_id') or ''}",
            f"scope_type: {payload.get('scope_type') or ''}",
            f"scope_id: {payload.get('scope_id') or ''}",
            f"decision_status: {payload.get('decision_status') or ''}",
            f"approved_by: {payload.get('approved_by') or ''}",
            f"approved_at: {payload.get('approved_at') or ''}",
            f"reason: {payload.get('reason') or ''}",
            f"execution_enabled: {str(bool(payload.get('execution_enabled'))).lower()}",
            f"supersedes: {payload.get('supersedes') or ''}",
            "",
        ]
    )


def _validate_required(args: argparse.Namespace) -> None:
    missing = [name for name in ("scope_type", "scope_id", "handoff_id", "decision_status", "approved_by", "reason") if not getattr(args, name)]
    if missing:
        raise ValueError(f"missing required fields: {', '.join(missing)}")
    if args.decision_status not in {"pending", "approved", "rejected"}:
        raise ValueError("decision_status must be one of: pending, approved, rejected")
    if args.decision_status != "approved" and args.execution_enabled:
        raise ValueError("execution_enabled=true is only allowed when decision_status=approved")


def main() -> int:
    parser = argparse.ArgumentParser(description="Set the canonical execution approval artifact.")
    parser.add_argument("--scope-type", required=True)
    parser.add_argument("--scope-id", required=True)
    parser.add_argument("--handoff-id", required=True)
    parser.add_argument("--decision-status", required=True, choices=["pending", "approved", "rejected"])
    parser.add_argument("--execution-enabled", required=True, type=_parse_bool)
    parser.add_argument("--approved-by", required=True)
    parser.add_argument("--reason", required=True)
    parser.add_argument("--approval-id", default="APP-AGENT-HANDOFF-0001")
    parser.add_argument("--supersedes", default=None)
    args = parser.parse_args()

    _validate_required(args)

    payload = {
        "approval_id": args.approval_id,
        "handoff_id": args.handoff_id,
        "scope_type": args.scope_type,
        "scope_id": args.scope_id,
        "decision_status": args.decision_status,
        "approved_by": args.approved_by,
        "approved_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "reason": args.reason,
        "execution_enabled": bool(args.execution_enabled),
        "supersedes": args.supersedes,
    }

    runtime_dir = ROOT / "system" / "runtime" / "agent_handoff"
    runtime_dir.mkdir(parents=True, exist_ok=True)
    approval_path = runtime_dir / "approval.json"
    approval_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (runtime_dir / "approval.md").write_text(_format_md(payload), encoding="utf-8")

    print(f"approval_path={approval_path}")
    print(f"scope_type={payload['scope_type']}")
    print(f"scope_id={payload['scope_id']}")
    print(f"decision_status={payload['decision_status']}")
    print(f"execution_enabled={str(payload['execution_enabled']).lower()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

