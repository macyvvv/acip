from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Callable


REPO_ROOT = Path(__file__).resolve().parents[2]
BUSINESS_ROOT = Path(__file__).resolve().parent
ARTIFACT_ROOT = BUSINESS_ROOT / "artifacts"


def _write(task_id: str, payload: dict[str, Any]) -> Path:
    directory = ARTIFACT_ROOT / task_id
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / "output.json"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path


def _e001a() -> dict[str, Any]:
    registry = REPO_ROOT / "platform/system/core/business_registry.py"
    text = registry.read_text(encoding="utf-8")
    return {
        "task_id": "E-001A",
        "business_id": "cf_gb_relative_system",
        "currently_registered": '"business_id": "cf_gb_relative_system"' in text,
        "registry_path": str(registry.relative_to(REPO_ROOT)),
        "canonical_roots": ["app", "artifacts", "schemas", "templates"],
        "registration_status": "existing" if '"business_id": "cf_gb_relative_system"' in text else "required",
    }


def _e004a() -> dict[str, Any]:
    return {
        "task_id": "E-004A",
        "states": ["ready", "blocked", "running", "succeeded", "failed", "quarantined"],
        "allowed_transitions": {
            "blocked": ["ready", "quarantined"],
            "ready": ["running", "quarantined"],
            "running": ["succeeded", "failed", "quarantined"],
            "failed": ["ready", "quarantined"],
            "succeeded": [],
            "quarantined": ["ready"],
        },
        "atomic_claim": {"required": True, "idempotency_key": "business_id:task_id:manifest_version"},
        "quarantine": {"fail_closed": True, "requires_policy_or_exception_resolution": True},
    }


def _e006a() -> dict[str, Any]:
    decisions = [
        "initial_area", "source_legal_risk", "people_media_scope", "correction_policy",
        "pilot_loss_cap", "architecture", "security_residual_risk", "ai_adoption",
        "gate_2", "gate_3", "public_release", "repeatability", "reinvestment",
        "regional_legal_risk", "regional_release", "phase_transition",
    ]
    return {
        "task_id": "E-006A",
        "decisions": [
            {
                "decision_id": item,
                "normal_path": "policy_engine",
                "policy_owner": "owner" if item in {"initial_area", "pilot_loss_cap", "reinvestment", "phase_transition"} else "ops_policy",
                "fallback": "quarantined",
                "exception": "qualified_counsel" if "legal" in item else "owner_exception",
            }
            for item in decisions
        ],
    }


BUILDERS: dict[str, Callable[[], dict[str, Any]]] = {
    "E-001A": _e001a,
    "E-004A": _e004a,
    "E-006A": _e006a,
}


def _validate(task_id: str) -> None:
    path = ARTIFACT_ROOT / task_id / "output.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("task_id") != task_id:
        raise ValueError("task_id mismatch")
    if task_id == "E-001A":
        if payload.get("registration_status") not in {"existing", "required"}:
            raise ValueError("registration status missing")
        if payload.get("canonical_roots") != ["app", "artifacts", "schemas", "templates"]:
            raise ValueError("canonical roots mismatch")
    elif task_id == "E-004A":
        if not payload.get("atomic_claim", {}).get("required"):
            raise ValueError("atomic claim missing")
        if not payload.get("quarantine", {}).get("fail_closed"):
            raise ValueError("quarantine must fail closed")
        if "succeeded" not in payload.get("states", []):
            raise ValueError("state model incomplete")
    elif task_id == "E-006A":
        decisions = payload.get("decisions", [])
        if len(decisions) != 16:
            raise ValueError("all 16 decisions must be classified")
        if any(not item.get("policy_owner") or item.get("fallback") != "quarantined" for item in decisions):
            raise ValueError("decision owner or fallback missing")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--validate", action="store_true")
    parser.add_argument("task_id", choices=sorted(BUILDERS))
    args = parser.parse_args()
    if args.validate:
        _validate(args.task_id)
        print(f"{args.task_id}: valid")
        return
    path = _write(args.task_id, BUILDERS[args.task_id]())
    print(path.relative_to(REPO_ROOT))


if __name__ == "__main__":
    main()
