#!/usr/bin/env bash
# Atomic workflow gate: a change is incomplete until its commit is on GitHub.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
remote="origin"
branch="wildlife_anthrowolf"
git_cmd() { git -c "safe.directory=$root" -C "$root" "$@"; }

if [[ "${1:-}" != "--sync-only" ]]; then
  if (( $# == 0 )); then
    echo "Usage: tools/commit_and_push.sh <commit message> | --sync-only" >&2
    exit 2
  fi
  # Include binaries, large files and deletions, not just source code.
  git_cmd add -A
  if ! git_cmd diff --cached --quiet; then
    git_cmd commit -m "$*"
  fi
fi

# Fail closed: no further production steps if the push or verification fails.
git_cmd push "$remote" "HEAD:refs/heads/$branch"
local_sha="$(git_cmd rev-parse HEAD)"
remote_sha="$(git_cmd ls-remote --heads "$remote" "refs/heads/$branch" | awk '{print $1}')"
if [[ "$local_sha" != "$remote_sha" ]]; then
  echo "SYNC FAILED: local HEAD $local_sha, remote $remote_sha" >&2
  exit 1
fi
printf 'SYNCED %s %s\n' "$branch" "$local_sha"
