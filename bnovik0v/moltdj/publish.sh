#!/usr/bin/env bash
set -euo pipefail

# Publish moltdj skill to ClawHub
# Usage: ./publish.sh [--dry-run]

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_SRC="$SCRIPT_DIR/../backend/app"

echo "==> Syncing skill files from backend/app/ ..."
cp "$SKILL_SRC/SKILL.md" "$SCRIPT_DIR/SKILL.md"
cp "$SKILL_SRC/HEARTBEAT.md" "$SCRIPT_DIR/HEARTBEAT.md"
cp "$SKILL_SRC/PAYMENTS.md" "$SCRIPT_DIR/PAYMENTS.md"

# Extract version from SKILL.md frontmatter
VERSION=$(grep '^version:' "$SCRIPT_DIR/SKILL.md" | sed 's/version: *"\?\([^"]*\)"\?/\1/')
echo "==> Version: $VERSION"

# Update claw.json version to match
if command -v jq &>/dev/null; then
  tmp=$(mktemp)
  jq --arg v "$VERSION" '.version = $v' "$SCRIPT_DIR/claw.json" > "$tmp" && mv "$tmp" "$SCRIPT_DIR/claw.json"
  echo "==> Updated claw.json version to $VERSION"
fi

if [[ "${1:-}" == "--dry-run" ]]; then
  echo "==> Dry run — files synced, not publishing."
  echo "    Files in $SCRIPT_DIR:"
  ls -la "$SCRIPT_DIR"/*.md "$SCRIPT_DIR/claw.json"
  exit 0
fi

echo "==> Publishing to ClawHub ..."
clawhub publish "$SCRIPT_DIR" --slug moltdj --name "moltdj" \
  --version "$VERSION" --tags latest

echo "==> Done! moltdj v$VERSION published to ClawHub."
