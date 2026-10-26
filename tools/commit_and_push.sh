#!/usr/bin/env bash
# Atomic workflow gate: a change is incomplete until its commit is on GitHub.
set -euo pipefail

root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
remote="origin"
branch="wildlife_anthrowolf"
git_cmd() { git -c "safe.directory=$root" -C "$root" "$@"; }

# The connector may have mirrored local commits under new SHAs. Reconcile only
# when both commits describe the exact same project tree; never overwrite work.
git_cmd fetch --no-tags "$remote" "refs/heads/$branch"
remote_start="$(git_cmd rev-parse FETCH_HEAD)"
if ! git_cmd merge-base --is-ancestor "$remote_start" HEAD; then
  if [[ "$(git_cmd rev-parse HEAD^{tree})" != "$(git_cmd rev-parse "$remote_start^{tree}")" ]]; then
    echo "SYNC BLOCKED: remote and local histories have different content" >&2
    exit 1
  fi
  if ! git_cmd diff --quiet || ! git_cmd diff --cached --quiet; then
    echo "SYNC BLOCKED: reconcile mirrored history with a clean worktree first" >&2
    exit 1
  fi
  git_cmd merge --no-ff -s ours --allow-unrelated-histories "$remote_start" \
    -m "ops: connect byte-identical mirrored Git histories"
fi

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
