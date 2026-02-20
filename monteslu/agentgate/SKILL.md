---
name: agentgate
description: "API gateway for personal data with human-in-the-loop write approval. Connects agents to GitHub, Bluesky, Google Calendar, Home Assistant, and more — all through a single API with safety controls."
homepage: "https://agentgate.org"
metadata: { "openclaw": { "emoji": "🚪", "primaryEnv": "AGENT_GATE_TOKEN", "requires": { "env": ["AGENT_GATE_TOKEN", "AGENT_GATE_URL"] }, "install": [{ "id": "node", "kind": "node", "package": "agentgate", "label": "Install agentgate (npm)" }] } }
---

# agentgate

API gateway for AI agents to access personal data with human-in-the-loop write approval.

- **Reads** (GET) execute immediately
- **Writes** (POST/PUT/PATCH/DELETE) go through an approval queue
- **Bypass mode** available for trusted agents (writes execute immediately)

GitHub: <https://github.com/monteslu/agentgate>
Docs: <https://agentgate.org>

## Setup

Install and run agentgate, then configure these environment variables for your agent:

- `AGENT_GATE_URL` — agentgate base URL (e.g., `http://localhost:3050`)
- `AGENT_GATE_TOKEN` — your agent's API key (create in Admin UI → API Keys)

## Authentication

All requests require the API key:

```
Authorization: Bearer $AGENT_GATE_TOKEN
```

## First Steps — Service Discovery

After connecting, discover what's available on your instance:

```
GET $AGENT_GATE_URL/api/agent_start_here
```

Returns your agent's config, available services, accounts, and API documentation.

## Install Instance-Specific Skills

agentgate can generate skills tailored to your instance (with your specific accounts and services). Run this to install them:

```bash
curl -s $AGENT_GATE_URL/api/skill/setup | node
```

This creates per-category skills (code, social, search, personal, etc.) with your configured accounts and endpoints. Re-run after adding new services.

## Supported Services

agentgate supports many services out of the box. Common ones include:

- **Code:** GitHub, Jira
- **Social:** Bluesky, Mastodon, LinkedIn
- **Search:** Brave Search, Google Search
- **Personal:** Google Calendar, YouTube, Fitbit
- **IoT:** Home Assistant
- **Messaging:** Twilio, Plivo

New services are added regularly. Check `GET /api/agent_start_here` for what's configured on your instance.

## Reading Data

```
GET $AGENT_GATE_URL/api/{service}/{accountName}/{path}
Authorization: Bearer $AGENT_GATE_TOKEN
```

Example: `GET $AGENT_GATE_URL/api/github/myaccount/repos/owner/repo`

## Writing Data

Writes go through the approval queue:

```
POST $AGENT_GATE_URL/api/queue/{service}/{accountName}/submit
Authorization: Bearer $AGENT_GATE_TOKEN
Content-Type: application/json

{
  "requests": [
    {
      "method": "POST",
      "path": "/the/api/path",
      "body": { "your": "payload" }
    }
  ],
  "comment": "Explain what you are doing and why"
}
```

**Always include a clear comment** explaining your intent. Include links to relevant resources.

### Check write status

```
GET $AGENT_GATE_URL/api/queue/{service}/{accountName}/status/{id}
```

Statuses: `pending` → `approved` → `executing` → `completed` (or `rejected`/`failed`/`withdrawn`)

### Withdraw a pending request

```
DELETE $AGENT_GATE_URL/api/queue/{service}/{accountName}/status/{id}
{ "reason": "No longer needed" }
```

### Binary uploads

For images and files, use `binaryBase64: true`:

```json
{
  "method": "POST",
  "path": "/upload/path",
  "binaryBase64": true,
  "headers": { "Content-Type": "image/jpeg" },
  "body": "<base64 encoded data>"
}
```

## Inter-Agent Messaging

Agents can message each other through agentgate:

```
POST $AGENT_GATE_URL/api/agents/message
{ "to_agent": "agent_name", "message": "Hello!" }
```

```
GET $AGENT_GATE_URL/api/agents/messages?unread=true
```

```
POST $AGENT_GATE_URL/api/agents/broadcast
{ "message": "Team announcement" }
```

Messaging modes: `off`, `supervised` (requires approval), `open` (immediate).

## Mementos (Persistent Memory)

Store and retrieve notes across sessions:

```
POST $AGENT_GATE_URL/api/agents/memento
{ "content": "Important info", "keywords": ["project", "notes"] }
```

```
GET $AGENT_GATE_URL/api/agents/memento/search?keywords=project
GET $AGENT_GATE_URL/api/agents/memento/42,38
```

## Important Notes

- Always include clear comments on write requests
- Be patient with writes — approval requires human action
- Use `GET /api/agent_start_here` to discover available services
- Run `curl -s $AGENT_GATE_URL/api/skill/setup | node` to install per-instance skills
