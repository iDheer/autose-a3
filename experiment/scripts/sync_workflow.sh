#!/usr/bin/env bash
# Copy the workflow and agent code from the fork working copy into workflow/ (submission layout).
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
rm -rf "$ROOT/workflow"; mkdir -p "$ROOT/workflow/.github"
cp -r "$ROOT/_fork/.github/workflows" "$ROOT/workflow/.github/"
cp -r "$ROOT/_fork/.autose" "$ROOT/workflow/.autose"
cp "$ROOT/_fork/ARCHITECTURE.md" "$ROOT/workflow/ARCHITECTURE.md"
find "$ROOT/workflow" -name __pycache__ -type d -prune -exec rm -rf {} +
