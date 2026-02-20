#!/bin/bash

ROOM_STATE_FILE="$HOME/.openclaw/payid/room_state.txt"

if [ -f "$ROOM_STATE_FILE" ]; then
    rm -f "$ROOM_STATE_FILE"
    echo '{"success": true, "message": "Room state cleared"}'
else
    echo '{"success": true, "message": "No room state to clear"}'
fi
