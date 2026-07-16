#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="${ROOT_DIR:-$(git rev-parse --show-toplevel)}"
TARGETS=(baseline control loader prompts releases rules templates)

for target in "${TARGETS[@]}"; do
	if [[ ! -e "$ROOT_DIR/platform/archive/$target" ]]; then
		echo "Missing archive entry: platform/archive/$target" >&2
		exit 1
	fi
	if [[ -e "$ROOT_DIR/$target" ]]; then
		echo "Unexpected root entry already present: $target" >&2
		exit 1
	fi
done

for target in "${TARGETS[@]}"; do
	printf 'mv %q %q\n' "$ROOT_DIR/platform/archive/$target" "$ROOT_DIR/$target"
done

echo "Reference rollback updates are intentionally not performed by this script."
echo "Post-rollback validation commands:"
echo "python3 platform/system/platform/scripts/validate_all.py"
echo "python3 -m pytest -q"