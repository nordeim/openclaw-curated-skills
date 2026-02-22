#!/usr/bin/env bash
# find-skill.sh — Fast keyword search for OpenClaw skills
# Usage: find-skill.sh [-c category] [-n max] [-j] [-a] <keyword1> [keyword2] ...
BASE="$(cd "$(dirname "$0")" && pwd)"
INDEX="$BASE/skills-index.json"

# Defaults
MAX_RESULTS=15
CATEGORY_FILTER=""
JSON_OUTPUT=false
SHOW_ALL=false

# Parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    -c) CATEGORY_FILTER="$2"; shift 2 ;;
    -n) MAX_RESULTS="$2"; shift 2 ;;
    -j) JSON_OUTPUT=true; shift ;;
    -a) SHOW_ALL=true; shift ;;
    -*) echo "Unknown option: $1"; exit 1 ;;
    *) break ;;
  esac
done

if [[ $# -eq 0 ]]; then
  echo "Usage: find-skill.sh [-c category] [-n max] [-j] [-a] <keyword1> [keyword2] ..."
  echo ""
  echo "Categories:"
  find "$BASE" -maxdepth 1 -mindepth 1 -type d ! -name ".git" -printf "  %f\n" 2>/dev/null | sort
  exit 0
fi

KEYWORDS=("$@")

# Check if jq is available
if command -v jq &>/dev/null && [[ -f "$INDEX" ]]; then
  # Use jq for precise JSON search
  
  # Build jq filter from keywords
  JQ_FILTER='.skills[] | '
  
  # Category filter
  if [[ -n "$CATEGORY_FILTER" ]]; then
    JQ_FILTER+=".category | test(\"$CATEGORY_FILTER\"; \"i\") | select(.) | input | "
  fi
  
  # Build scoring: count keyword matches in name + description + category
  SCORE_EXPR="0"
  for kw in "${KEYWORDS[@]}"; do
    kw_escaped=$(echo "$kw" | sed 's/[.[\]*+?^${}()|/\\&/g')
    SCORE_EXPR+=" + (if (.name | ascii_downcase | test(\"${kw_escaped}\"; \"i\")) then 5 else 0 end)"
    SCORE_EXPR+=" + (if (.description | ascii_downcase | test(\"${kw_escaped}\"; \"i\")) then 1 else 0 end)"
    SCORE_EXPR+=" + (if (.category | ascii_downcase | test(\"${kw_escaped}\"; \"i\")) then 2 else 0 end)"
  done
  
  # Build the complete jq query
  if [[ -n "$CATEGORY_FILTER" ]]; then
    CAT_FILTER="| select(.category | test(\"$CATEGORY_FILTER\"; \"i\"))"
  else
    CAT_FILTER=""
  fi
  
  RESULTS=$(jq -r "[.skills[] ${CAT_FILTER} | . + {score: ($SCORE_EXPR)} | select(.score > 0)] | sort_by(-.score)" "$INDEX")
  
  TOTAL=$(echo "$RESULTS" | jq 'length')
  
  if [[ "$TOTAL" -eq 0 ]]; then
    echo "No skills found matching: ${KEYWORDS[*]}"
    exit 0
  fi
  
  if $JSON_OUTPUT; then
    if $SHOW_ALL; then
      echo "$RESULTS"
    else
      echo "$RESULTS" | jq ".[:$MAX_RESULTS]"
    fi
  else
    echo ""
    printf "  %-24s %-30s %s\n" "CATEGORY" "SKILL" "DESCRIPTION"
    printf "  %-24s %-30s %s\n" "────────────────────────" "──────────────────────────────" "──────────────────────────────────────────────"
    
    LIMIT=$MAX_RESULTS
    $SHOW_ALL && LIMIT=$TOTAL
    
    echo "$RESULTS" | jq -r ".[:$LIMIT][] | \"\(.category)\t\(.name)\t\(.description[:80])\"" | while IFS=$'\t' read -r cat name desc; do
      printf "  %-24s %-30s %s\n" "$cat" "$name" "$desc"
    done
    
    echo ""
    if ! $SHOW_ALL && [[ $TOTAL -gt $MAX_RESULTS ]]; then
      echo "  Showing $MAX_RESULTS of $TOTAL matches. Use -a for all or -n <num> for more."
    else
      echo "  $TOTAL match(es) found."
    fi
    echo ""
  fi
else
  # Fallback: grep-based search on SKILL.md files directly
  echo "Note: Install jq for better search. Falling back to grep."
  echo ""
  
  PATTERN=$(IFS='|'; echo "${KEYWORDS[*]}")
  
  if [[ -n "$CATEGORY_FILTER" ]]; then
    SEARCH_PATH="$BASE/$CATEGORY_FILTER"
  else
    SEARCH_PATH="$BASE"
  fi
  
  grep -ril "$PATTERN" "$SEARCH_PATH"/*/SKILL.md 2>/dev/null | head -"$MAX_RESULTS" | while IFS= read -r f; do
    rel="${f#$BASE/}"
    cat_skill="${rel%/SKILL.md}"
    category="${cat_skill%%/*}"
    skill="${cat_skill##*/}"
    desc=$(grep '^description:' "$f" 2>/dev/null | head -1 | sed 's/^description:[[:space:]]*//' | head -c 80)
    printf "  %-24s %-30s %s\n" "$category" "$skill" "$desc"
  done
  echo ""
fi
