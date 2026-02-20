---
name: Aluvia Browser Proxy
description: Launch a proxy-protected headless browser session using Aluvia SDK. Avoid 403 blocks, CAPTCHAs, and rate limits by routing browser traffic through residential proxies. Provides a CDP URL for integration with browser automation tools.
read_when:
  - Browsing websites that block datacenter IPs
  - Avoiding CAPTCHAs and rate limits
  - Scraping or extracting data from protected websites
  - Running browser automation through residential proxies
  - Need a CDP URL for browser tools
metadata: { 'clawdbot': { 'emoji': '🛡️', 'requires': { 'bins': ['node', 'npx'] } } }
allowed-tools: Bash(aluvia-sdk:*)
---

# Aluvia Browser Proxy

## What it does

Aluvia SDK launches a headless Chromium browser routed through residential proxies, making your browser traffic appear as a real user. It returns a CDP (Chrome DevTools Protocol) URL that any browser automation tool can connect to.

## Quick start

```bash
export ALUVIA_API_KEY=your_api_key
aluvia-sdk open https://example.com        # Start proxied browser, get CDP URL
aluvia-sdk close                            # Stop the session
```

## Core workflow

1. Set `ALUVIA_API_KEY` environment variable
2. `aluvia-sdk open <url>` — launches a headless proxied browser, returns JSON with `cdpUrl`
3. Parse the `cdpUrl` from the JSON output and pass it to browser tools (agent-browser, OpenClaw, etc.)
4. `aluvia-sdk close` — stops the session when done

## Installation

```bash
npm install -g @aluvia/sdk
```

Or use directly with npx (no install needed):

```bash
npx aluvia-sdk help
```

## API Key Setup

1. Sign up at [Aluvia Dashboard](https://www.aluvia.io/)
2. Create an API key from the dashboard
3. Set the environment variable:

```bash
export ALUVIA_API_KEY=your_api_key_here
```

The CLI reads the API key from the `ALUVIA_API_KEY` environment variable. It must be set before running any command.

## Commands

### Open a browser session

```bash
aluvia-sdk open <url>
```

Options:

- `--connection-id <id>` — Use an existing account connection
- `--headed` — Show the browser window (default is headless)

Example:

```bash
aluvia-sdk open https://example.com
```

Output (JSON):

```json
{
  "status": "ok",
  "url": "https://example.com",
  "cdpUrl": "http://127.0.0.1:45651",
  "connectionId": 3449,
  "pid": 113282
}
```

### Close the browser session

```bash
aluvia-sdk close
```

Output (JSON):

```json
{
  "status": "ok",
  "message": "Browser session closed.",
  "url": "https://example.com",
  "cdpUrl": "http://127.0.0.1:45651",
  "connectionId": 3449,
  "pid": 113282
}
```

### Help

```bash
aluvia-sdk help
```

Output (plain text):

```
Usage: aluvia-sdk <command> [options]

Commands:
  open <url>    Start a browser session
  close         Stop the running browser session
  help          Show this help message

Options for 'open':
  --connection-id <id>   Use an existing account connection
  --headed               Show the browser window (default: headless)

Environment:
  ALUVIA_API_KEY         Your Aluvia API key (required)
```

## Response Structure

All operational commands (`open`, `close`) return a single JSON line to stdout.

| Field          | Type              | Description                               |
| -------------- | ----------------- | ----------------------------------------- |
| `status`       | `"ok" \| "error"` | Whether the command succeeded             |
| `url`          | `string \| null`  | The URL the browser was opened with       |
| `cdpUrl`       | `string \| null`  | CDP endpoint to connect external tools    |
| `connectionId` | `number \| null`  | Aluvia account connection ID              |
| `pid`          | `number \| null`  | Process ID of the background daemon       |
| `error`        | `string`          | Error message (only when status is error) |
| `message`      | `string`          | Success message (only on close)           |

Parse the output:

```bash
CDP_URL=$(aluvia-sdk open https://example.com | jq -r '.cdpUrl')
```

Only one session can run at a time. If `aluvia-sdk open` is called while a session is already running, it returns:

```json
{
  "status": "error",
  "error": "A browser session is already running.",
  "url": "https://example.com",
  "cdpUrl": "http://127.0.0.1:45651",
  "connectionId": 3449,
  "pid": 113282
}
```

## Create a Connection via API (recommended)

Create a reusable connection to avoid creating a new one on every `open` call. Reusing a connection is recommended — it maintains the same proxy allocation and rules across sessions.

```bash
# Create a new connection
curl -s -X POST https://api.aluvia.io/v1/account/connections \
  -H "Authorization: Bearer $ALUVIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "description": "openclaw agent"
  }'
```

Response:

```json
{
  "data": {
    "connection_id": "3449",
    "proxy_username": "...",
    "proxy_password": "..."
  }
}
```

Then use the `connection_id` when opening a browser session:

```bash
aluvia-sdk open https://target-site.com --connection-id 3449
```

Other useful API calls:

```bash
# List existing connections
curl -s https://api.aluvia.io/v1/account/connections \
  -H "Authorization: Bearer $ALUVIA_API_KEY"

# Update connection
curl -s -X PATCH https://api.aluvia.io/v1/account/connections/3449 \
  -H "Authorization: Bearer $ALUVIA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"description": "openclaw agent (updated)"}'

# Delete a connection
curl -s -X DELETE https://api.aluvia.io/v1/account/connections/3449 \
  -H "Authorization: Bearer $ALUVIA_API_KEY"
```

## Using the CDP URL with agent-browser

Start an Aluvia session, then pass the CDP URL to agent-browser:

```bash
# Start Aluvia proxy browser
CDP_URL=$(aluvia-sdk open https://example.com | jq -r '.cdpUrl')

# Connect agent-browser via CDP
agent-browser --cdp $CDP_URL snapshot -i
agent-browser --cdp $CDP_URL click @e1
agent-browser --cdp $CDP_URL fill @e2 "search query"

# When done
aluvia-sdk close
```

This routes all of agent-browser's traffic through Aluvia's residential proxies, avoiding blocks and CAPTCHAs.

## Using the CDP URL with OpenClaw Browser Tool

Start an Aluvia session and configure OpenClaw to use the CDP URL as a remote profile.

```bash
# Start Aluvia proxy browser
CDP_URL=$(aluvia-sdk open https://example.com | jq -r '.cdpUrl')
```

Add a remote profile in `~/.openclaw/openclaw.json`:

```json
{
  "browser": {
    "profiles": {
      "aluvia": {
        "cdpUrl": "http://127.0.0.1:<port>",
        "color": "#6366F1"
      }
    }
  }
}
```

Replace `<port>` with the port from the `cdpUrl` output. Then use the profile:

```bash
openclaw browser --browser-profile aluvia snapshot
openclaw browser --browser-profile aluvia open https://example.com
```

This works the same way as [Browserless hosted remote CDP](https://docs.openclaw.ai/tools/browser#browserless-hosted-remote-cdp), but routes traffic through Aluvia's residential proxies instead.

The browser session is shared — the tool will see the same pages, cookies, and state as the `aluvia-sdk open` command created.

## Example: Full workflow

```bash
# 1. Set API key
export ALUVIA_API_KEY=your_api_key

# 2. Open a proxied browser session
RESULT=$(aluvia-sdk open https://example.com)
CDP_URL=$(echo $RESULT | jq -r '.cdpUrl')
echo "CDP URL: $CDP_URL"

# 3. Use with agent-browser or any CDP-compatible tool
agent-browser --cdp $CDP_URL snapshot -i
agent-browser --cdp $CDP_URL click @e1

# 4. Close when done
aluvia-sdk close
```

## Example: Reuse an existing connection

```bash
# Open with a specific connection ID (reuses proxy allocation)
aluvia-sdk open https://example.com --connection-id 3449
```

## Example: Headed mode for debugging

```bash
# Launch with a visible browser window
aluvia-sdk open https://example.com --headed
```

## Troubleshooting

- **"ALUVIA_API_KEY environment variable is required"** — Set `export ALUVIA_API_KEY=your_key` before running the command.
- **"A browser session is already running"** — Run `aluvia-sdk close` first, then try again.
- **"Browser session timed out"** — The browser took too long to start. Check the daemon log at `/tmp/aluvia-sdk/cli.log` for details.
- **"Failed to load Playwright"** — Install Playwright: `npm install playwright` and then `npx playwright install chromium`.
- **CDP connection refused** — Make sure the session is still running. Check with `cat /tmp/aluvia-sdk/cli.lock`.
- **Cannot find `aluvia-sdk` command** — Use `npx aluvia-sdk` instead, or install globally with `npm install -g @aluvia/sdk`.

## Notes

- Only one browser session can run at a time per machine.
- The browser runs as a background daemon — closing the terminal does not stop it.
- Always run `aluvia-sdk close` to cleanly shut down the session.
- The CDP URL is a local endpoint (`http://127.0.0.1:<port>`) — it is only accessible from the same machine.
- Session state (cookies, localStorage) persists for the lifetime of the session.
- The `connectionId` can be reused across sessions with `--connection-id` to maintain the same proxy allocation.

## Links

- [Aluvia Website](https://www.aluvia.io/)
- [Aluvia Documentation](https://docs.aluvia.io/)
- [SDK on npm](https://www.npmjs.com/package/@aluvia/sdk)
- [OpenClaw Browser Tool Docs](https://docs.openclaw.ai/tools/browser#browserless-hosted-remote-cdp)
