#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

ROOT="$(SCRIPT_DIR="$SCRIPT_DIR" python3 - <<'PY'
import os
from pathlib import Path

current = Path(os.environ["SCRIPT_DIR"]).resolve()
for candidate in (current, *current.parents):
    if (candidate / ".git").exists() or (candidate / "pyproject.toml").exists() or (candidate / "README.md").exists():
        print(candidate)
        raise SystemExit(0)
raise SystemExit(1)
PY
PY
)"

cd "$ROOT"

if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
fi

echo "Starting Repository OS work loop..."

while true
do
    echo
    echo "===== Supervisor ====="
    python3 system/scripts/supervisor/run_local_supervisor.py

    cat runtime/supervisor/latest.md

    if grep -q "supervisor_state: idle" runtime/supervisor/latest.md; then
        echo
        echo "Repository OS is idle."
        break
    fi

    echo
    echo "===== Execute ====="
    APPROVAL_FLAG=true \
        python3 system/scripts/local_execution/run_codex_adapter.py

    echo
    echo "===== Validation ====="
    python3 system/scripts/validate_all.py
    python3 -m pytest -q

    echo
    echo "===== Public Site ====="
    python3 system/scripts/build_public_site.py

    if ! git diff --quiet -- public || ! git diff --cached --quiet -- public; then
        git add public
        if ! git diff --cached --quiet -- public; then
            git commit -m "feat: automated github pages publishing pipeline"
        fi
    fi

    if python3 - <<'PY'
import json
from pathlib import Path
path = Path("runtime/local_execution/latest.json")
if path.exists():
    data = json.loads(path.read_text(encoding="utf-8"))
    raise SystemExit(0 if data.get("failure_reason") == "missing_deliverables" else 1)
raise SystemExit(1)
PY
    then
        echo
        echo "Local execution reported missing deliverables; stopping without commit."
        break
    fi

    echo
    echo "===== Git ====="

    git status

    if ! git diff --quiet || ! git diff --cached --quiet; then
        echo "Repository changed."
        echo "Commit / Push is currently expected to be performed by Codex if implemented."
    fi

    echo
    echo "Loop complete."
done

echo
echo "All available work items completed."
