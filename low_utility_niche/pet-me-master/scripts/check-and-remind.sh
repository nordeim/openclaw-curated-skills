#!/bin/bash
set -e

# Check if all gotchis are ready and send reminder if needed
# This script runs every 30 minutes via cron

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$HOME/.openclaw/workspace/skills/pet-me-master/config.json"
STATE_FILE="$HOME/.openclaw/workspace/skills/pet-me-master/reminder-state.json"
REMINDER_FILE="$HOME/.openclaw/workspace/.gotchi-reminder.txt"

# Load config
GOTCHI_IDS=($(jq -r '.gotchiIds[]' "$CONFIG_FILE"))
CONTRACT=$(jq -r '.contractAddress' "$CONFIG_FILE")
RPC_URL=$(jq -r '.rpcUrl' "$CONFIG_FILE")

# Cooldown requirement (12h 1min)
REQUIRED_WAIT=43260

# Check if all gotchis are ready
ALL_READY=true
NOW=$(date +%s)

for GOTCHI_ID in "${GOTCHI_IDS[@]}"; do
  # Get last pet time from blockchain
  DATA=$(cast call "$CONTRACT" "getAavegotchi(uint256)" "$GOTCHI_ID" --rpc-url "$RPC_URL" 2>/dev/null)
  
  if [ -z "$DATA" ]; then
    echo "[$(date)] Failed to query gotchi #$GOTCHI_ID"
    ALL_READY=false
    continue
  fi
  
  # Extract last pet timestamp
  LAST_PET_HEX=${DATA:2498:64}
  LAST_PET_DEC=$((16#$LAST_PET_HEX))
  TIME_SINCE=$((NOW - LAST_PET_DEC))
  
  if [ $TIME_SINCE -lt $REQUIRED_WAIT ]; then
    ALL_READY=false
    break
  fi
done

# Check state file
if [ -f "$STATE_FILE" ]; then
  LAST_REMINDER=$(jq -r '.lastReminder // 0' "$STATE_FILE" 2>/dev/null || echo "0")
  FALLBACK_SCHEDULED=$(jq -r '.fallbackScheduled // false' "$STATE_FILE" 2>/dev/null || echo "false")
else
  LAST_REMINDER=0
  FALLBACK_SCHEDULED=false
  echo '{"lastReminder": 0, "fallbackScheduled": false}' > "$STATE_FILE"
fi

# If all ready and we haven't sent reminder in last 12h
TIME_SINCE_REMINDER=$((NOW - LAST_REMINDER))

if [ "$ALL_READY" = true ] && [ $TIME_SINCE_REMINDER -gt 43200 ] && [ "$FALLBACK_SCHEDULED" = false ]; then
  echo "[$(date)] All gotchis ready! Creating reminder file..."
  
  # Write reminder file for AAI to pick up on next heartbeat
  cat > "$REMINDER_FILE" << EOF
fren, pet your gotchi(s)! 👻

All ${#GOTCHI_IDS[@]} gotchis are ready for petting!

Reply with 'pet all my gotchis' or I'll auto-pet them in 1 hour if you're busy! 🦞
EOF
  
  echo "[$(date)] ✅ Reminder file created"
  
  # Update state: mark reminder sent and schedule fallback
  jq '.lastReminder = '$(date +%s)' | .fallbackScheduled = true' "$STATE_FILE" > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"
  
  # Schedule auto-pet fallback in 1 hour
  echo "bash $SCRIPT_DIR/auto-pet-fallback.sh" | at now + 1 hour 2>/dev/null || {
    # If 'at' not available, use background sleep
    (sleep 3600 && bash "$SCRIPT_DIR/auto-pet-fallback.sh" >> /tmp/auto-pet-fallback.log 2>&1) &
    FALLBACK_PID=$!
    echo "[$(date)] Fallback scheduled via background process (PID $FALLBACK_PID)"
  }
  
  echo "[$(date)] ✅ Fallback scheduled for 1 hour from now"
  
elif [ "$ALL_READY" = false ] && [ "$FALLBACK_SCHEDULED" = true ]; then
  # Reset state if gotchis were already petted
  echo "[$(date)] Gotchis already petted, resetting state"
  echo '{"lastReminder": 0, "fallbackScheduled": false}' > "$STATE_FILE"
  rm -f "$REMINDER_FILE"
fi

exit 0
