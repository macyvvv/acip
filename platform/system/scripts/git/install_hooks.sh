#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
hooks_dir="${repo_root}/.git/hooks"
mkdir -p "${hooks_dir}"
install -m 0755 "${repo_root}/platform/system/git_hooks/pre-push" "${hooks_dir}/pre-push"
echo "Installed pre-push hook to ${hooks_dir}/pre-push"
