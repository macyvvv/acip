#!/usr/bin/env bash
set -euo pipefail

source .venv/bin/activate

echo "Starting Repository OS work loop..."

while true
do
    echo
    echo "===== Supervisor ====="
    python3 scripts/supervisor/run_local_supervisor.py

    cat runtime/supervisor/latest.md

    if grep -q "supervisor_state: idle" runtime/supervisor/latest.md; then
        echo
        echo "Repository OS is idle."
        break
    fi

    echo
    echo "===== Execute ====="
    APPROVAL_FLAG=true \
        python3 scripts/local_execution/run_codex_adapter.py

    echo
    echo "===== Validation ====="
    python3 scripts/validate_all.py
    python3 -m pytest -q

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