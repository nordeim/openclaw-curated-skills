#!/usr/bin/env bash
# move-skills.sh — Migrate all skills from old categories into 20 new categories
# Reads skill-mapping.tsv and executes the moves.
set -euo pipefail

BASE="$(cd "$(dirname "$0")" && pwd)"
TSV="$BASE/skill-mapping.tsv"
LOG="$BASE/move-log.txt"

if [[ ! -f "$TSV" ]]; then
  echo "ERROR: $TSV not found. Run generate-mapping.sh first."
  exit 1
fi

# Record pre-move count
PRE=$(find "$BASE" -maxdepth 3 -name "SKILL.md" | wc -l)
echo "Pre-move SKILL.md count: $PRE"
echo "Pre-move SKILL.md count: $PRE" > "$LOG"

# Create the 20 new category directories
NEW_CATS=(
  agent-core
  agent-orchestration
  browser-automation
  business-operations
  communication-messaging
  content-publishing
  data-analytics
  developer-tools
  devops-cloud
  finance-markets
  games-entertainment
  integrations-connectors
  knowledge-research
  media-generation
  media-processing
  productivity-personal
  search-web
  security-compliance
  smart-home-iot
  travel-transport
)

for cat in "${NEW_CATS[@]}"; do
  mkdir -p "$BASE/$cat"
done
echo "Created ${#NEW_CATS[@]} category directories."

# Process mapping
MOVED=0
SKIPPED=0
ERRORS=0

while IFS=$'\t' read -r old_path new_cat; do
  # Skip comments and header
  [[ "$old_path" == "#"* ]] && continue
  [[ -z "$old_path" || -z "$new_cat" ]] && continue

  skill_name="${old_path##*/}"
  old_dir="$BASE/$old_path"
  new_dir="$BASE/$new_cat/$skill_name"

  # If already in correct location, skip
  if [[ "$old_path" == "$new_cat/$skill_name" ]]; then
    ((SKIPPED++))
    continue
  fi

  # Check source exists
  if [[ ! -d "$old_dir" ]]; then
    echo "WARN: Source not found: $old_dir" | tee -a "$LOG"
    ((ERRORS++))
    continue
  fi

  # Check for name collision
  if [[ -d "$new_dir" ]]; then
    echo "WARN: Target exists, skipping: $new_dir" | tee -a "$LOG"
    ((SKIPPED++))
    continue
  fi

  # Move
  mv "$old_dir" "$new_dir"
  echo "MOVED: $old_path -> $new_cat/$skill_name" >> "$LOG"
  ((MOVED++))

done < "$TSV"

echo ""
echo "=== Move Summary ==="
echo "Moved: $MOVED"
echo "Skipped (already in place): $SKIPPED"
echo "Errors/Warnings: $ERRORS"
echo "" >> "$LOG"
echo "Moved: $MOVED | Skipped: $SKIPPED | Errors: $ERRORS" >> "$LOG"

# Remove empty old directories
echo ""
echo "Cleaning empty old directories..."
REMOVED=0
for dir in "$BASE"/*/; do
  dirname="$(basename "$dir")"
  # Skip new categories, .git, and trustskill
  skip=false
  for cat in "${NEW_CATS[@]}"; do
    [[ "$dirname" == "$cat" ]] && skip=true && break
  done
  [[ "$dirname" == ".git" ]] && skip=true
  
  if ! $skip; then
    # Check if directory is empty (no subdirs)
    subdirs=$(find "$dir" -maxdepth 1 -mindepth 1 -type d 2>/dev/null | wc -l)
    if [[ "$subdirs" -eq 0 ]]; then
      echo "  Removing empty: $dirname/"
      rm -rf "$dir"
      ((REMOVED++))
    else
      echo "  Keeping non-empty: $dirname/ ($subdirs subdirs remain)"
    fi
  fi
done
echo "Removed $REMOVED empty directories."

# Post-move count
POST=$(find "$BASE" -maxdepth 2 -name "SKILL.md" | wc -l)
echo ""
echo "Post-move SKILL.md count: $POST"
echo "Post-move SKILL.md count: $POST" >> "$LOG"

if [[ "$PRE" -eq "$POST" ]]; then
  echo "✅ INTEGRITY CHECK PASSED: $PRE == $POST"
else
  echo "❌ INTEGRITY CHECK FAILED: $PRE != $POST (diff: $((PRE - POST)))"
fi

# Count categories
CATS=$(find "$BASE" -maxdepth 1 -mindepth 1 -type d ! -name ".git" | wc -l)
echo "Final category count: $CATS"
echo ""
echo "Done. Run build-index.sh to regenerate the search index."
