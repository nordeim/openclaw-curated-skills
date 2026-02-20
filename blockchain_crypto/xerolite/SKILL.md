---
name: xerolite
description: "Integrate OpenClaw with Xerolite trading platform. Use when: querying Xerolite API, placing orders, searching contracts, or processing Xerolite webhooks."
metadata: {"openclaw":{"requires":{"bins":["node"]}}}
---

# Xerolite

Xerolite is a TradingView-to-broker (IB) trading platform.  
This skill lets the agent place orders, search contracts, and receive Xerolite webhooks via OpenClaw.

## Setup

### Install

Installs the transform module and configures webhook endpoint:

```bash
bash skills/xerolite/scripts/install.sh
```

### Uninstall

Removes transform module and webhook configuration:

```bash
bash skills/xerolite/scripts/uninstall.sh
```

## Package Structure

```
skills/xerolite/
├── SKILL.md              # This file
├── transforms/
│   └── xerolite.js       # Webhook payload transformer
├── scripts/
│   ├── xerolite.mjs      # CLI (order place, contract search)
│   ├── install.sh        # Setup script
│   └── uninstall.sh      # Removal script
└── references/
    ├── API.md            # REST API guide
    └── WEBHOOKS.md       # Webhook configuration
```

## Capabilities

- Place orders via Xerolite REST API.
- Search contracts via Xerolite REST API.
- Receive `/hooks/xerolite` webhooks and format them as readable notifications.

## Commands

Use these commands from the skill directory (or with `{baseDir}` in other skills).

**Default flag values** (optional; omit to use): `--currency USD`, `--asset-class STOCK`, `--exch SMART`.

### Place order

Required: `--action`, `--qty`, `--symbol`. Optional: `--currency`, `--asset-class`, `--exch`.

```bash
# Minimal (defaults: USD, STOCK, SMART)
node {baseDir}/scripts/xerolite.mjs order place --symbol AAPL --action BUY --qty 10

# Full
node {baseDir}/scripts/xerolite.mjs order place \
  --symbol AAPL \
  --currency USD \
  --asset-class STOCK \
  --exch SMART \
  --action BUY \
  --qty 10
```

JSON sent to `POST /api/internal/agent/order/place-order`:

```json
{
  "name": "Agent",
  "action": "BUY",
  "qty": "10",
  "symbol": "AAPL",
  "currency": "USD",
  "asset_class": "STOCK",
  "exch": "SMART"
}
```

### Search contract

Required: `--symbol`. Optional: `--currency`, `--asset-class`, `--exch`.

```bash
# Minimal (defaults: USD, STOCK, SMART)
node {baseDir}/scripts/xerolite.mjs contract search --symbol AAPL

# Full
node {baseDir}/scripts/xerolite.mjs contract search \
  --symbol AAPL \
  --currency USD \
  --asset-class STOCK \
  --exch SMART
```

JSON sent to `POST /api/internal/agent/contract/search`:

```json
{
  "brokerName": "IBKR",
  "symbol": "AAPL",
  "currency": "USD",
  "xeroAssetClass": "STOCK"
}
```

## Webhooks

After install, OpenClaw listens at `/hooks/xerolite`.

### How It Works

```
Xerolite Event
     ↓
POST /hooks/xerolite (with Bearer token)
     ↓
Transform module formats payload
     ↓
Agent receives formatted notification
     ↓
Delivers to active channel (Telegram, etc.)
```

The transform module (`xerolite.js`) formats incoming payloads into readable notifications with proper structure.

### Xerolite Configuration

Configure Xerolite to send webhooks:
- **URL**: `https://your-openclaw-host:18789/hooks/xerolite`
- **Method**: POST
- **Header**: `Authorization: Bearer <your-hooks-token>`
- **Content-Type**: `application/json`

### Payload Format

The transform handles various payload structures:

```json
{"event": "order.created", "data": {"id": "123", "total": 99.99}}
```

```json
{"message": "Server restarted", "level": "info"}
```

Output example:
```
📥 **Xerolite Notification**

**Event:** order.created
**Data:**
  • id: 123
  • total: 99.99
```

## REST API

For the order and contract search endpoints used by this skill, see [references/API.md](references/API.md).

## Transform Module

The bundled transform (`transforms/xerolite.js`) handles:
- Payload formatting with readable structure
- Event/message/data field extraction
- Automatic delivery to configured channel
- No-rephrase instruction for clean forwarding

To customize the transform, edit `transforms/xerolite.js` before running install.

## Requirements

- Node.js 18+ (for built-in `fetch`)
- OpenClaw hooks enabled (for webhook delivery)
- **CLI only**: Optional `XEROLITE_API_URL` — base URL for Xerolite API. If not set, defaults to `http://localhost` (same machine or local network). No API key in this version; may be added in a future version.

## Troubleshooting

### Webhook not receiving
- Verify `hooks.token` is set in openclaw config
- Check Xerolite sends correct `Authorization: Bearer <token>` header
- Confirm gateway was restarted after install

### 401 Unauthorized
- Token mismatch — check Xerolite uses same token as `hooks.token`

### Transform not working
- Check transform is at `~/.openclaw/hooks/transforms/xerolite.js`
- Re-run `install.sh` to copy fresh transform
- Check gateway logs for errors
