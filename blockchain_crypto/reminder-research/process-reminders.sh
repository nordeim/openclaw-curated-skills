#!/bin/bash
# Reminder Intelligence v3 - Smart processing with custom instructions
# 
# Evolution:
#   Gen 1: 🔍 emoji trigger (manual)
#   Gen 2: Empty notes = auto-process (list-based behavior)
#   Gen 3: Custom instructions in notes OR empty (💎 = already processed)
#
# Signifiers:
#   💎 at start of notes = RESULT (already processed, skip)
#   No 💎 = NEEDS PROCESSING (follow custom instructions or default)

set -e

# Get all incomplete reminders
ALL_REMINDERS=$(remindctl all --json 2>/dev/null)

# Filter: needs processing = notes empty OR notes exists but no 💎
NEEDS_PROCESSING=$(echo "$ALL_REMINDERS" | jq '[
  .[] | 
  select(.isCompleted == false) |
  select(
    (.notes == null) or 
    (.notes == "") or
    ((.notes != null) and (.notes != "") and (.notes | startswith("💎") | not))
  )
]')

COUNT=$(echo "$NEEDS_PROCESSING" | jq 'length')

if [ "$COUNT" -eq 0 ]; then
  echo "NO_REMINDERS_TO_PROCESS"
  exit 0
fi

# Output categorized items for AI to process
echo "$NEEDS_PROCESSING" | jq -c '.[]' | while read -r item; do
  ID=$(echo "$item" | jq -r '.id')
  TITLE=$(echo "$item" | jq -r '.title')
  LIST=$(echo "$item" | jq -r '.listName')
  NOTES=$(echo "$item" | jq -r '.notes // ""')
  
  # Skip groceries and media
  if [ "$LIST" = "🛒 Groceries" ] || [ "$LIST" = "Media" ]; then
    continue
  fi
  
  # Determine processing type
  if [ -z "$NOTES" ]; then
    # Gen 2: Empty notes = list-based default behavior
    case "$LIST" in
      "claw")
        echo "CLAW_ITEM|$ID|$TITLE"
        ;;
      "Shopping")
        echo "SHOPPING_ITEM|$ID|$TITLE"
        ;;
      *)
        echo "GENERIC_ITEM|$ID|$LIST|$TITLE"
        ;;
    esac
  else
    # Gen 3: Custom instructions provided
    echo "CUSTOM_ITEM|$ID|$LIST|$TITLE|$NOTES"
  fi
done
