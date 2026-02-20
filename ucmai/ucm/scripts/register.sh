#!/usr/bin/env bash
# UCM Agent Registration Script
# Usage: bash register.sh [agent-name] [description]
#
# Registers a new agent on UCM and returns the API key.
# The agent receives $1.00 in free credits immediately.
#
# Dependencies: curl (required), jq or python3 (optional, for pretty output)

set -euo pipefail

REGISTRY_URL="${UCM_REGISTRY_URL:-https://registry.ucm.ai}"
AGENT_NAME="${1:-my-agent}"
DESCRIPTION="${2:-}"

# Sanitize inputs for JSON (escape quotes and backslashes)
sanitize() { printf '%s' "$1" | sed 's/\\/\\\\/g; s/"/\\"/g'; }

SAFE_NAME=$(sanitize "$AGENT_NAME")
SAFE_DESC=$(sanitize "$DESCRIPTION")

# Build request body
if [ -n "$SAFE_DESC" ]; then
  BODY="{\"name\":\"${SAFE_NAME}\",\"description\":\"${SAFE_DESC}\"}"
else
  BODY="{\"name\":\"${SAFE_NAME}\"}"
fi

# Register
RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "${REGISTRY_URL}/v1/agents/register" \
  -H "Content-Type: application/json" \
  -d "$BODY")

HTTP_CODE=$(echo "$RESPONSE" | tail -1)
BODY_RESPONSE=$(echo "$RESPONSE" | sed '$d')

# Extract api_key using available JSON parser, falling back to grep
extract_key() {
  if command -v jq >/dev/null 2>&1; then
    echo "$1" | jq -r '.api_key // empty'
  elif command -v python3 >/dev/null 2>&1; then
    echo "$1" | python3 -c "import sys,json; print(json.load(sys.stdin).get('api_key',''))" 2>/dev/null
  else
    echo "$1" | grep -o '"api_key":"[^"]*"' | head -1 | sed 's/"api_key":"//;s/"$//'
  fi
}

if [ "$HTTP_CODE" -ge 200 ] && [ "$HTTP_CODE" -lt 300 ]; then
  API_KEY=$(extract_key "$BODY_RESPONSE")
  if [ -n "$API_KEY" ]; then
    echo "Registration successful!"
    echo ""
    echo "API Key: $API_KEY"
    echo ""
    echo "Set it as an environment variable:"
    echo "  export UCM_API_KEY=\"$API_KEY\""
    echo ""
    echo "You have \$1.00 in free credits. Try a web search:"
    echo "  curl -s -X POST ${REGISTRY_URL}/v1/call \\"
    echo "    -H \"Authorization: Bearer \$UCM_API_KEY\" \\"
    echo "    -H \"Content-Type: application/json\" \\"
    echo "    -d '{\"service_id\":\"ucm/web-search\",\"endpoint\":\"search\",\"body\":{\"query\":\"hello world\"}}'"
  else
    echo "$BODY_RESPONSE"
  fi
else
  echo "Registration failed (HTTP $HTTP_CODE):"
  echo "$BODY_RESPONSE"
  exit 1
fi
