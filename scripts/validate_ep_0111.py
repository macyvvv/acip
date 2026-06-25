#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    required_paths = [
        ROOT / "orchestrator" / "validation_orchestrator.py",
        ROOT / "scripts" / "validate_all.py",
        ROOT / "docs" / "current" / "VALIDATION_STATE.md",
        ROOT / "runtime" / "validation" / "validation_report.json",
        ROOT / "runtime" / "validation" / "VALIDATION_REPORT.md",
        ROOT / ".github" / "workflows" / "validate-all.yml",
        ROOT / "docs" / "ep" / "README_EP0111_VALIDATION_ORCHESTRATOR.md",
    ]
    missing = [str(path.relative_to(ROOT)) for path in required_paths if not path.exists()]
    if missing:
        print("FAIL: missing validation orchestrator files:", ", ".join(missing))
        return 1

    validation_state = (ROOT / "docs" / "current" / "VALIDATION_STATE.md").read_text(encoding="utf-8")
    required_fields = [
        "last_validation_status:",
        "last_validation_command:",
        "last_validation_report_json:",
        "last_validation_report_md:",
        "validation_owner:",
        "rerun_required_when:",
        "human_rerun_policy:",
        "relation_to_worker_output_contract:",
    ]
    missing_fields = [field for field in required_fields if field not in validation_state]
    if missing_fields:
        print("FAIL: missing validation state fields:", ", ".join(missing_fields))
        return 1
    print("EP-0111 Validation passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
