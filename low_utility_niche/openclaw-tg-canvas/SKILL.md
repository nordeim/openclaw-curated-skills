---
name: tg-canvas
description: "Telegram Mini App Canvas. Renders agent-generated content (HTML, markdown) in a Telegram Mini App. Authenticated via Telegram initData — only approved users can view. Push content with `tg-canvas push` or via the /push API."
homepage: https://github.com/clvv/openclaw-tg-canvas
kind: server
metadata:
  {
    "openclaw": {
      "emoji": "🖼️",
      "kind": "server",
      "requires": {
        "bins": ["node", "cloudflared"],
        "env": ["BOT_TOKEN", "ALLOWED_USER_IDS", "JWT_SECRET", "MINIAPP_URL"]
      },
      "install": [
        {
          "id": "npm",
          "kind": "npm",
          "label": "Install dependencies (npm install)"
        }
      ]
    }
  }
---

**This is a server skill.** It includes a Node.js HTTP/WebSocket server (`server.js`), a CLI (`bin/tg-canvas.js`), and a Telegram Mini App frontend (`miniapp/`). It is not instruction-only.

Telegram Mini App Canvas renders agent-generated HTML or markdown inside a Telegram Mini App, with access limited to approved user IDs and authenticated via Telegram `initData` verification. It exposes a local push endpoint and a CLI command so agents can update the live canvas without manual UI steps.

## Prerequisites

- Node.js 18+ (tested with Node 18/20/22)
- `cloudflared` for HTTPS tunnel (required by Telegram Mini Apps)
- Telegram bot token

## Setup

1. Configure environment variables (see **Configuration** below) in your shell or a `.env` file.
2. Run the bot setup script to configure the menu button:
   ```bash
   BOT_TOKEN=... MINIAPP_URL=https://xxxx.trycloudflare.com node scripts/setup-bot.js
   ```
3. Start the server:
   ```bash
   node server.js
   ```
4. Start a Cloudflare tunnel to expose the Mini App over HTTPS:
   ```bash
   cloudflared tunnel --url http://localhost:3721
   ```

## Pushing Content from the Agent

- CLI:
  ```bash
  tg-canvas push --html "<h1>Hello</h1>"
  tg-canvas push --markdown "# Hello"
  tg-canvas push --a2ui @./a2ui.json
  ```
- HTTP API:
  ```bash
  curl -X POST http://127.0.0.1:3721/push \
    -H 'Content-Type: application/json' \
    -d '{"html":"<h1>Hello</h1>"}'
  ```

## Security

**What the Cloudflare tunnel exposes publicly:**

| Endpoint | Public? | Auth |
| --- | --- | --- |
| `GET /` | ✅ | None (serves static Mini App HTML) |
| `POST /auth` | ✅ | Telegram `initData` HMAC-SHA256 verification + `ALLOWED_USER_IDS` check |
| `GET /state` | ✅ | JWT required |
| `GET /ws` | ✅ | JWT required (WebSocket upgrade) |
| `POST /push` | ❌ loopback-only | Enforced at socket level (`127.0.0.1` / `::1` only); optional `PUSH_TOKEN` |
| `POST /clear` | ❌ loopback-only | Same as above |
| `GET /health` | ❌ loopback-only | Same as above |

**Loopback enforcement** for `/push`, `/clear`, and `/health` is done at the TCP socket level (`req.socket.remoteAddress`), not via headers — so it cannot be spoofed via `X-Forwarded-For` or similar.

**Recommendations:**
- Set `PUSH_TOKEN` in your `.env` for defense-in-depth even though `/push` is already loopback-restricted.
- Use a strong random `JWT_SECRET` (32+ bytes).
- Keep `BOT_TOKEN` and `JWT_SECRET` secret; rotate if compromised.
- The Cloudflare tunnel exposes the Mini App publicly — the `ALLOWED_USER_IDS` check in `/auth` is the primary access control gate for the canvas.

## Commands

- `tg-canvas push` — push HTML/markdown/text/A2UI
- `tg-canvas clear` — clear the canvas
- `tg-canvas health` — check server health

## Configuration

| Variable | Required | Description |
| --- | --- | --- |
| `BOT_TOKEN` | Yes | Telegram bot token used for API calls and auth verification. |
| `ALLOWED_USER_IDS` | Yes | Comma-separated Telegram user IDs allowed to view the Mini App. |
| `JWT_SECRET` | Yes | Secret used to sign session tokens. Use a long random value (32+ bytes). |
| `PORT` | No | Server port (default: `3721`). |
| `MINIAPP_URL` | Yes (for bot setup) | HTTPS URL of the Mini App (Cloudflare tunnel or nginx). |
| `PUSH_TOKEN` | Recommended | Shared secret for `/push` and CLI. Sent via `X-Push-Token` header. |
| `TG_CANVAS_URL` | No | Base URL for the CLI (default: `http://127.0.0.1:3721`). |
