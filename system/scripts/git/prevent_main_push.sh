#!/usr/bin/env bash
set -euo pipefail

branch="$(git branch --show-current 2>/dev/null || true)"
if [[ "$branch" == "main" ]]; then
  echo "Blocked: direct push to main is prohibited. Switch to a feature branch and open a pull request." >&2
  exit 1
fi

echo "Push allowed from branch: ${branch:-unknown}"
