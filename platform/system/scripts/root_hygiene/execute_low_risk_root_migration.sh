#!/usr/bin/env bash
set -euo pipefail

APPROVAL_FLAG="${APPROVAL_FLAG:-false}"
DRY_RUN="${DRY_RUN:-true}"
ROOT_DIR="${ROOT_DIR:-$(git rev-parse --show-toplevel)}"
TARGETS=(baseline control loader prompts releases rules templates)

if [[ "$APPROVAL_FLAG" != "true" ]]; then
  echo "Human Approval gate required: set APPROVAL_FLAG=true before execution." >&2
  exit 1
fi

if [[ "$DRY_RUN" != "true" ]]; then
  echo "This script defaults to dry-run. Set DRY_RUN=true explicitly for review, then rerun with APPROVAL_FLAG=true to execute." >&2
  exit 1
fi

for target in "${TARGETS[@]}"; do
  if [[ ! -e "$ROOT_DIR/$target" ]]; then
    echo "Missing expected root entry: $target" >&2
    exit 1
  fi
  if [[ -e "$ROOT_DIR/platform/archive/$target" ]]; then
    echo "Unexpected existing archive target: platform/archive/$target" >&2
    exit 1
  fi
done

mkdir -p "$ROOT_DIR/archive"
for target in "${TARGETS[@]}"; do
  printf 'mkdir -p %q\n' "$ROOT_DIR/platform/archive/$target"
  printf 'mv %q %q\n' "$ROOT_DIR/$target" "$ROOT_DIR/platform/archive/$target"
done

echo "Reference updates are intentionally not performed by this script." \
  "Run the documented reference update plan separately after approval."

echo "Post-move validation commands:"
echo "python3 platform/system/platform/scripts/validate_all.py"
echo "python3 -m pytest -q"
