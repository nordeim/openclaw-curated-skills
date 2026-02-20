#!/usr/bin/env bash
# Coupler.io MCP — interactive setup script
# Handles: client registration, PKCE auth, token exchange, secure storage
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
WORKSPACE="$(dirname "$SCRIPT_DIR")"
CONFIG_DIR="$WORKSPACE/config"
OAUTH_STATE="$SCRIPT_DIR/oauth-state.json"
MCPORTER_CONFIG="$CONFIG_DIR/mcporter.json"

AUTH_SERVER="https://auth.coupler.io"
MCP_ENDPOINT="https://mcp.coupler.io/mcp"
REDIRECT_URI="http://127.0.0.1:8976/callback"

# --- Preflight ---
for cmd in curl jq openssl; do
  if ! command -v "$cmd" &>/dev/null; then
    echo "❌ Missing required tool: $cmd"
    exit 1
  fi
done

echo "🔧 Coupler.io MCP Setup"
echo "========================"
echo ""

# --- Step 1: Register OAuth client ---
echo "📝 Step 1: Registering OAuth client..."
REG_RESPONSE=$(curl -s -X POST "$AUTH_SERVER/oauth2/register" \
  -H "Content-Type: application/json" \
  -d '{
    "client_name": "OpenClaw",
    "redirect_uris": ["'"$REDIRECT_URI"'"],
    "grant_types": ["authorization_code"],
    "response_types": ["code"],
    "token_endpoint_auth_method": "none"
  }')

CLIENT_ID=$(echo "$REG_RESPONSE" | jq -r '.client_id // empty')
if [[ -z "$CLIENT_ID" ]]; then
  echo "❌ Client registration failed:"
  echo "$REG_RESPONSE"
  exit 1
fi
echo "   ✅ client_id: $CLIENT_ID"

# --- Step 2: Generate PKCE ---
echo ""
echo "🔑 Step 2: Generating PKCE challenge..."
CODE_VERIFIER=$(openssl rand -base64 32 | tr -d '=/+' | cut -c1-43)
CODE_CHALLENGE=$(echo -n "$CODE_VERIFIER" | openssl dgst -sha256 -binary | base64 | tr -d '=' | tr '+/' '-_')
echo "   ✅ PKCE ready"

# --- Step 3: Browser auth ---
AUTH_URL="${AUTH_SERVER}/oauth2/authorize?client_id=${CLIENT_ID}&redirect_uri=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$REDIRECT_URI'))")&response_type=code&scope=mcp&code_challenge=${CODE_CHALLENGE}&code_challenge_method=S256"

echo ""
echo "🌐 Step 3: Browser authorization"
echo "   Opening browser & listening for callback on port 8976..."
echo ""

# Start a one-shot HTTP server to capture the OAuth callback
AUTH_CODE_FILE=$(mktemp)
python3 -c '
import http.server, urllib.parse, sys, os

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        params = urllib.parse.parse_qs(urllib.parse.urlparse(self.path).query)
        code = params.get("code", [None])[0]
        if code:
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Authorization successful!</h2><p>You can close this tab.</p></body></html>")
            with open(sys.argv[1], "w") as f:
                f.write(code)
        else:
            self.send_response(400)
            self.send_header("Content-Type", "text/html")
            self.end_headers()
            self.wfile.write(b"<html><body><h2>Error: no code received</h2></body></html>")
    def log_message(self, *args): pass

http.server.HTTPServer(("127.0.0.1", 8976), Handler).handle_request()
' "$AUTH_CODE_FILE" &
SERVER_PID=$!

sleep 0.5

# Open browser
if command -v open &>/dev/null; then
  open -a "Google Chrome" "$AUTH_URL"
elif command -v xdg-open &>/dev/null; then
  xdg-open "$AUTH_URL"
else
  echo "   ⚠️  Could not open browser automatically."
  echo "   Open this URL manually:"
  echo "   $AUTH_URL"
fi

echo "   Waiting for you to authorize in the browser..."
wait $SERVER_PID 2>/dev/null

AUTH_CODE=$(cat "$AUTH_CODE_FILE" 2>/dev/null)
rm -f "$AUTH_CODE_FILE"

if [[ -z "$AUTH_CODE" ]]; then
  echo "❌ No authorization code received from callback."
  exit 1
fi
echo "   ✅ Authorization code received"

# --- Step 4: Exchange code for tokens ---
echo ""
echo "🔄 Step 4: Exchanging code for tokens..."
TOKEN_RESPONSE=$(curl -s -X POST "$AUTH_SERVER/oauth2/token" \
  -d "grant_type=authorization_code&client_id=${CLIENT_ID}&code=${AUTH_CODE}&redirect_uri=${REDIRECT_URI}&code_verifier=${CODE_VERIFIER}")

ACCESS_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.access_token // empty')
REFRESH_TOKEN=$(echo "$TOKEN_RESPONSE" | jq -r '.refresh_token // empty')

if [[ -z "$ACCESS_TOKEN" ]]; then
  echo "❌ Token exchange failed:"
  echo "$TOKEN_RESPONSE"
  exit 1
fi
echo "   ✅ Tokens received"

# --- Step 5: Save config ---
echo ""
echo "💾 Step 5: Saving configuration..."

mkdir -p "$CONFIG_DIR"

# mcporter config — merge if exists, create if not
if [[ -f "$MCPORTER_CONFIG" ]]; then
  UPDATED=$(jq --arg token "$ACCESS_TOKEN" --arg url "$MCP_ENDPOINT" \
    '.mcpServers.coupler = {"baseUrl": $url, "headers": {"Authorization": ("Bearer " + $token)}}' \
    "$MCPORTER_CONFIG")
  echo "$UPDATED" > "$MCPORTER_CONFIG"
else
  cat > "$MCPORTER_CONFIG" <<EOF
{
  "mcpServers": {
    "coupler": {
      "baseUrl": "$MCP_ENDPOINT",
      "headers": {
        "Authorization": "Bearer $ACCESS_TOKEN"
      }
    }
  }
}
EOF
fi

# OAuth state
cat > "$OAUTH_STATE" <<EOF
{
  "authServer": "$AUTH_SERVER",
  "clientId": "$CLIENT_ID",
  "refreshToken": "$REFRESH_TOKEN"
}
EOF

# --- Step 6: Secure files ---
chmod 600 "$MCPORTER_CONFIG" "$OAUTH_STATE"

echo "   ✅ config/mcporter.json (access token)"
echo "   ✅ CPL/oauth-state.json (refresh token)"
echo "   ✅ File permissions set to 600"

echo ""
echo "🎉 Setup complete! Test with:"
echo "   mcporter call coupler.list-dataflows"
echo ""
