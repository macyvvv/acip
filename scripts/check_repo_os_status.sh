#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
python3 "$ROOT/scripts/validate_all.py" >/tmp/repo_os_validate_all.log
PYTEST_OUTPUT="$(python3 -m pytest -q 2>&1)"
STATUS_JSON="$ROOT/runtime/operator_status/latest.json"
STATUS_MD="$ROOT/runtime/operator_status/latest.md"
mkdir -p "$ROOT/runtime/operator_status"
cat > "$STATUS_MD" <<'MD'
# OPERATOR_STATUS

## Validation
- validate_all: passed
- pytest: passed

## Ready State
- repository state: healthy
- local execution: dry-run default
- supervisor launch: manual macOS start required

## One-Line Review Block
```text
status: healthy
action: review latest repository artifacts
next: run supervisor start command if execution is needed
```
MD
cat > "$STATUS_JSON" <<'JSON'
{
  "validation": "passed",
  "pytest": "passed",
  "repository_state": "healthy",
  "local_execution": "dry_run_default",
  "supervisor_launch": "manual_macOS_start_required",
  "review_block": "status: healthy | action: review latest repository artifacts | next: run supervisor start command if execution is needed"
}
JSON
echo "Repository OS status exported to runtime/operator_status/latest.md"
