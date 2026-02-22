#!/usr/bin/env bash
# build-index.sh — Regenerate skills-index.json and description.md from current structure
BASE="$(cd "$(dirname "$0")" && pwd)"
INDEX="$BASE/skills-index.json"
DESC="$BASE/description.md"
TIMESTAMP=$(date -u +"%Y-%m-%dT%H:%M:%SZ")

echo "Building skill index from $BASE ..."

# Collect all SKILL.md paths
mapfile -t SKILLS < <(find "$BASE" -maxdepth 3 -mindepth 3 -name "SKILL.md" | sort)
TOTAL=${#SKILLS[@]}
CATS=$(find "$BASE" -maxdepth 1 -mindepth 1 -type d ! -name ".git" | wc -l)

echo "  Found $TOTAL skills in $CATS categories"

# Build description.md
> "$DESC"
for skillmd in "${SKILLS[@]}"; do
  rel_path="${skillmd#$BASE/}"
  cat_skill="${rel_path%/SKILL.md}"
  desc_raw=$(grep '^description:' "$skillmd" 2>/dev/null | head -1 | sed 's/^description:[[:space:]]*//')
  echo "${cat_skill}/SKILL.md:description: ${desc_raw}" >> "$DESC"
done
echo "  ✅ description.md written ($TOTAL entries)"

# Build skills-index.json
{
  echo "{"
  echo "  \"version\": \"1.0\","
  echo "  \"generated\": \"$TIMESTAMP\","
  echo "  \"categories\": $CATS,"
  echo "  \"total_skills\": $TOTAL,"
  echo "  \"category_list\": ["
  
  # List categories
  first_cat=true
  for dir in "$BASE"/*/; do
    dirname="$(basename "$dir")"
    [[ "$dirname" == ".git" ]] && continue
    count=$(find "$dir" -maxdepth 1 -mindepth 1 -type d | wc -l)
    if $first_cat; then first_cat=false; else echo ","; fi
    printf '    {"name": "%s", "count": %d}' "$dirname" "$count"
  done
  echo ""
  echo "  ],"
  echo "  \"skills\": ["
  
  first=true
  for skillmd in "${SKILLS[@]}"; do
    rel_path="${skillmd#$BASE/}"
    cat_skill="${rel_path%/SKILL.md}"
    category="${cat_skill%%/*}"
    skill_name="${cat_skill##*/}"
    
    desc_raw=$(grep '^description:' "$skillmd" 2>/dev/null | head -1 | sed 's/^description:[[:space:]]*//')
    # Escape for JSON
    desc_clean=$(echo "$desc_raw" | sed 's/\\/\\\\/g; s/"/\\"/g; s/\t/ /g' | tr '\n' ' ' | head -c 200)
    
    if $first; then first=false; else echo ","; fi
    printf '    {"name": "%s", "category": "%s", "path": "%s", "description": "%s"}' \
      "$skill_name" "$category" "$cat_skill" "$desc_clean"
  done
  echo ""
  echo "  ]"
  echo "}"
} > "$INDEX"

echo "  ✅ skills-index.json written"
echo ""
echo "Done. Index: $TOTAL skills in $CATS categories."
echo "Search with: bash find-skill.sh <keywords>"
