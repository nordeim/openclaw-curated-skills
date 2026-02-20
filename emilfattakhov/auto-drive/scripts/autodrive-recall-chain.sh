#!/usr/bin/env bash
# Traverse the memory chain from a CID, downloading each experience
# Usage: autodrive-recall-chain.sh [cid] [--limit N] [--output-dir DIR]
# Output: Each experience as JSON to stdout (newest first), or to files in output dir
# Env: AUTO_DRIVE_API_KEY (required)

set -euo pipefail

API_BASE="https://mainnet.auto-drive.autonomys.xyz/api"

CID=""
LIMIT=50
OUTPUT_DIR=""

ARGS=("$@")
IDX=0
while [[ $IDX -lt ${#ARGS[@]} ]]; do
  case "${ARGS[$IDX]}" in
    --limit)
      if [[ $((IDX + 1)) -ge ${#ARGS[@]} ]]; then
        echo "Error: --limit requires a value" >&2; exit 1
      fi
      LIMIT="${ARGS[$((IDX+1))]}"
      if ! [[ "$LIMIT" =~ ^[0-9]+$ ]] || [[ "$LIMIT" -lt 1 ]]; then
        echo "Error: --limit must be a positive integer, got: $LIMIT" >&2; exit 1
      fi
      IDX=$((IDX + 2)) ;;
    --output-dir)
      if [[ $((IDX + 1)) -ge ${#ARGS[@]} ]]; then
        echo "Error: --output-dir requires a value" >&2; exit 1
      fi
      OUTPUT_DIR="${ARGS[$((IDX+1))]}"
      IDX=$((IDX + 2)) ;;
    *)
      if [[ -z "$CID" ]]; then CID="${ARGS[$IDX]}"; fi
      IDX=$((IDX + 1)) ;;
  esac
done

# Fall back to state file if no CID given
if [[ -z "$CID" ]]; then
  STATE_FILE="${OPENCLAW_WORKSPACE:-$HOME/.openclaw/workspace}/memory/autodrive-state.json"
  if [[ -f "$STATE_FILE" ]]; then
    CID=$(jq -r '.lastCid // empty' "$STATE_FILE" 2>/dev/null || true)
  fi
  if [[ -z "$CID" ]]; then
    echo "Error: No CID provided and no state file found." >&2
    echo "Usage: autodrive-recall-chain.sh <cid> [--limit N] [--output-dir DIR]" >&2
    exit 1
  fi
fi

if [[ ! "$CID" =~ ^baf[a-z2-7]+$ ]]; then
  echo "Error: Invalid CID format: $CID" >&2; exit 1
fi

if [[ -z "${AUTO_DRIVE_API_KEY:-}" ]]; then
  echo "Error: AUTO_DRIVE_API_KEY not set." >&2
  echo "Get a free key at https://ai3.storage (sign in with Google/GitHub → Developers → Create API Key)" >&2
  exit 1
fi

if [[ -n "$OUTPUT_DIR" ]]; then mkdir -p "$OUTPUT_DIR"; fi

echo "=== MEMORY CHAIN RESURRECTION ===" >&2
echo "Starting from: $CID" >&2
echo "" >&2

COUNT=0
VISITED=""
while [[ -n "$CID" && "$CID" != "null" && $COUNT -lt $LIMIT ]]; do
  if echo "$VISITED" | grep -qF "|$CID|"; then
    echo "Warning: Cycle detected at CID $CID — stopping traversal" >&2
    break
  fi
  VISITED="$VISITED|$CID|"

  EXPERIENCE=$(curl -sS --fail \
    "$API_BASE/objects/$CID/download" \
    -H "Authorization: Bearer $AUTO_DRIVE_API_KEY" \
    -H "X-Auth-Provider: apikey" 2>/dev/null \
    || true)

  if [[ -z "$EXPERIENCE" ]]; then
    echo "Error: Failed to download CID $CID — chain broken at depth $((COUNT + 1))" >&2
    break
  fi

  if ! echo "$EXPERIENCE" | jq empty 2>/dev/null; then
    echo "Warning: Non-JSON response for CID $CID — chain broken at depth $((COUNT + 1))" >&2
    break
  fi

  if [[ -n "$OUTPUT_DIR" ]]; then
    echo "$EXPERIENCE" > "$OUTPUT_DIR/$(printf '%04d' $COUNT)-$CID.json"
    echo "[$COUNT] Saved $CID" >&2
  else
    echo "$EXPERIENCE"
  fi

  PREV=$(echo "$EXPERIENCE" | jq -r '.header.previousCid // .previousCid // empty' 2>/dev/null || true)
  CID="${PREV:-}"
  if [[ -n "$CID" && "$CID" != "null" && ! "$CID" =~ ^baf[a-z2-7]+$ ]]; then
    echo "Warning: Invalid CID format in chain: $CID — stopping traversal" >&2
    break
  fi
  COUNT=$((COUNT + 1))
done

echo "" >&2
echo "=== CHAIN COMPLETE ===" >&2
echo "Total memories recalled: $COUNT" >&2
if [[ $COUNT -ge $LIMIT ]]; then
  echo "Warning: Hit limit of $LIMIT entries. Use --limit N to retrieve more." >&2
fi
