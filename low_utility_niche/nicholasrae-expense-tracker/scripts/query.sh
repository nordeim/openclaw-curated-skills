#!/usr/bin/env bash
# query.sh — Query the expense ledger with filters
# Usage: query.sh [--from DATE] [--to DATE] [--category CAT] [--vendor VENDOR] [--format summary|detail|json]

set -euo pipefail

# --- Check dependencies ---
if ! command -v jq &>/dev/null; then
  echo "Error: jq is required but not installed. Install with: brew install jq" >&2
  exit 2
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SKILL_DIR="$(dirname "$SCRIPT_DIR")"
LEDGER="${SKILL_DIR}/expenses/ledger.json"

# --- Defaults ---
FROM_DATE=""
TO_DATE=""
CATEGORY=""
VENDOR=""
FORMAT="summary"

# --- Parse args ---
while [[ $# -gt 0 ]]; do
  case "$1" in
    --from)   FROM_DATE="$2"; shift 2 ;;
    --to)     TO_DATE="$2"; shift 2 ;;
    --category) CATEGORY="$2"; shift 2 ;;
    --vendor) VENDOR="$2"; shift 2 ;;
    --format) FORMAT="$2"; shift 2 ;;
    *) echo "Unknown arg: $1" >&2; exit 1 ;;
  esac
done

# --- Check ledger exists ---
if [[ ! -f "$LEDGER" ]]; then
  echo "No ledger found. No expenses recorded yet." >&2
  exit 0
fi

# --- Build jq filter ---
FILTER="."

if [[ -n "$FROM_DATE" ]]; then
  FILTER="$FILTER | map(select(.date >= \"$FROM_DATE\"))"
fi

if [[ -n "$TO_DATE" ]]; then
  FILTER="$FILTER | map(select(.date <= \"$TO_DATE\"))"
fi

if [[ -n "$CATEGORY" ]]; then
  FILTER="$FILTER | map(select(.category == \"$CATEGORY\" or (.category | ascii_downcase) == (\"$CATEGORY\" | ascii_downcase)))"
fi

if [[ -n "$VENDOR" ]]; then
  FILTER="$FILTER | map(select(.vendor | ascii_downcase | contains(\"$VENDOR\" | ascii_downcase)))"
fi

# --- Execute query ---
RESULTS=$(jq "$FILTER" "$LEDGER")
COUNT=$(echo "$RESULTS" | jq 'length')

if [[ "$COUNT" -eq 0 ]]; then
  echo "No expenses found matching your filters."
  exit 0
fi

case "$FORMAT" in
  json)
    echo "$RESULTS" | jq .
    ;;
  detail)
    TOTAL=$(echo "$RESULTS" | jq '[.[].amount] | add')
    echo "=== Expense Detail ==="
    echo ""
    echo "$RESULTS" | jq -r '.[] | "  #\(.id | tostring | . + " " * (4 - length))  \(.date)  \(if .amount < 0 then "-$\(.amount * -1 | tostring | if contains(".") then . else . + ".00" end)" else " $\(.amount | tostring | if contains(".") then . else . + ".00" end)" end | .[0:12] | . + " " * (12 - length))  \(.category | .[0:16] | . + " " * (16 - length))  \(.vendor)\(if .notes != "" then " (\(.notes))" else "" end)"'
    echo ""
    printf "  Total: $%.2f (%d items)\n" "$TOTAL" "$COUNT"
    ;;
  summary|*)
    echo "=== Spending Summary ==="
    if [[ -n "$FROM_DATE" || -n "$TO_DATE" ]]; then
      echo "  Period: ${FROM_DATE:-earliest} to ${TO_DATE:-latest}"
    fi
    if [[ -n "$CATEGORY" ]]; then
      echo "  Category: $CATEGORY"
    fi
    if [[ -n "$VENDOR" ]]; then
      echo "  Vendor: $VENDOR"
    fi
    echo ""
    echo "$RESULTS" | jq -r '
      group_by(.category) |
      map({
        category: .[0].category,
        total: (map(.amount) | add),
        count: length
      }) |
      sort_by(-.total) |
      .[] |
      "  \(.category): $\(.total | tostring | if contains(".") then (split(".") | .[0] + "." + (.[1] + "00")[0:2]) else . + ".00" end) (\(.count) \(if .count == 1 then "item" else "items" end))"
    '
    TOTAL=$(echo "$RESULTS" | jq '[.[].amount] | add')
    echo ""
    printf "  TOTAL: $%.2f (%d items)\n" "$TOTAL" "$COUNT"
    ;;
esac
