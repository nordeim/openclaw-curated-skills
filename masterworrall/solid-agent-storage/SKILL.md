---
name: solid-agent-storage
description: Give your AI agent persistent identity (WebID) and personal data storage (Pod) using the Solid Protocol
version: 0.1.1
author: Interition
license: Apache-2.0
metadata: {"requires": {"bins": ["node", "docker"], "env": ["SOLID_SERVER_URL", "INTERITION_PASSPHRASE"]}, "categories": ["storage", "identity", "data"], "homepage": "https://github.com/masterworrall/agent-interition"}
---

# Solid Agent Storage

This Skill gives you a **Solid Pod** — a personal data store with a **WebID** (your identity on the web). You can store data, read it back, and share specific resources with other agents.

## When to Use This Skill

- You need to **remember something** across conversations (notes, preferences, learned facts)
- You need to **store structured data** (RDF/Turtle format for linked data, or any content type)
- You need to **share data** with another agent who also has a Pod
- You need a **persistent identity** that other agents or services can verify

## Setup

This Skill requires a running [Community Solid Server](https://github.com/CommunitySolidServer/CommunitySolidServer) (CSS). The server is not included in this package — see the [source repository](https://github.com/masterworrall/agent-interition) for Docker setup instructions.

Before using any commands, ensure:
1. A Community Solid Server is running and reachable (default: `http://localhost:3000`)
2. `SOLID_SERVER_URL` is set to your server's URL (default: `http://localhost:3000`). **Only point this at a server you control and trust** — the Skill will exchange credentials with it.
3. `INTERITION_PASSPHRASE` is set (used to encrypt stored credentials). Use a strong passphrase and keep it secret.

## Commands

### Provision a New Agent

Creates a WebID and Pod for an agent. Run this once per agent.

```bash
scripts/provision.sh --name <agent-name> [--displayName <display-name>]
```

**Example:**
```bash
scripts/provision.sh --name researcher --displayName "Research Assistant"
```

**Output:**
```json
{"status": "ok", "agent": "researcher", "webId": "http://localhost:3000/agents/researcher/profile/card#me", "podUrl": "http://localhost:3000/agents/researcher/"}
```

### Write Data to Pod

Stores data at a URL within the agent's Pod.

```bash
scripts/write.sh --agent <name> --url <resource-url> --content <data> [--content-type <mime-type>]
```

**Example — store a note:**
```bash
scripts/write.sh --agent researcher \
  --url "http://localhost:3000/agents/researcher/memory/notes.ttl" \
  --content '@prefix schema: <http://schema.org/>.
<#meeting-2024-01> a schema:Note;
  schema:text "User prefers bullet-point summaries";
  schema:dateCreated "2024-01-15".' \
  --content-type "text/turtle"
```

**Example — store plain text:**
```bash
scripts/write.sh --agent researcher \
  --url "http://localhost:3000/agents/researcher/memory/summary.txt" \
  --content "Key finding: the API rate limit is 100 req/min" \
  --content-type "text/plain"
```

### Read Data from Pod

Retrieves data from a URL.

```bash
scripts/read.sh --agent <name> --url <resource-url>
```

**Example:**
```bash
scripts/read.sh --agent researcher --url "http://localhost:3000/agents/researcher/memory/notes.ttl"
```

**Output:**
```json
{"status": "ok", "url": "...", "contentType": "text/turtle", "body": "..."}
```

### Grant Access to Another Agent

Allows another agent to read or write a specific resource.

```bash
scripts/grant-access.sh --agent <owner-name> --resource <url> --grantee <webId> --modes <Read,Write,...>
```

**Valid modes:** `Read`, `Write`, `Append`, `Control`

**Example — let another agent read your notes:**
```bash
scripts/grant-access.sh --agent researcher \
  --resource "http://localhost:3000/agents/researcher/shared/report.ttl" \
  --grantee "http://localhost:3000/agents/writer/profile/card#me" \
  --modes "Read"
```

### Revoke Access

Removes a previously granted access rule.

```bash
scripts/revoke-access.sh --agent <owner-name> --resource <url> --grantee <webId>
```

### Check Status

Lists all provisioned agents and their details.

```bash
scripts/status.sh
```

## Beyond These Commands — Using the Solid Protocol Directly

The commands above are convenience wrappers. Your Pod is a standard **W3C Solid** server, so you can perform **any operation defined in the Solid Protocol specification**, including operations not covered by the provided scripts.

For example:
- **Delete a resource:** `HTTP DELETE` on the resource URL
- **List container contents:** `HTTP GET` on a container URL (returns contained resources)
- **Create a container:** `HTTP PUT` or `POST` with the `Link: <http://www.w3.org/ns/ldp#BasicContainer>; rel="type"` header
- **Patch a resource:** `HTTP PATCH` with SPARQL Update (`application/sparql-update`)

All requests require a Bearer token. Use the agent's stored credentials to obtain one from the server's `/.oidc/token` endpoint (client credentials grant), or use the `read.sh`/`write.sh` scripts as a reference for how authentication works.

Refer to the [Solid Protocol specification](https://solidproject.org/TR/protocol) for the full set of supported operations. When the provided scripts don't cover what you need, work it out from the standard — it's just HTTP and Linked Data.

## Pod Structure

Each agent's Pod has these containers:

| Path | Purpose |
|------|---------|
| `/agents/{name}/memory/` | Private agent memory (notes, learned facts, preferences) |
| `/agents/{name}/shared/` | Resources intended for sharing with other agents |
| `/agents/{name}/conversations/` | Conversation logs and context |

## Turtle Templates

When storing structured data, use Turtle (RDF) format. Here are templates for common patterns:

### A note or memory
```turtle
@prefix schema: <http://schema.org/>.
<#note-1> a schema:Note;
  schema:text "The content of the note";
  schema:dateCreated "2024-01-15".
```

### An agent preference
```turtle
@prefix foaf: <http://xmlns.com/foaf/0.1/>.
@prefix schema: <http://schema.org/>.
<#pref-1> a schema:PropertyValue;
  schema:name "response-style";
  schema:value "concise".
```

### A shared dataset
```turtle
@prefix schema: <http://schema.org/>.
<#dataset-1> a schema:Dataset;
  schema:name "Research Results";
  schema:description "Findings from the analysis task";
  schema:dateModified "2024-01-15".
```

## Error Handling

All commands output JSON. On error, stderr will contain:
```json
{"error": "description of what went wrong"}
```

Common errors:
- `"No passphrase provided"` — Set `INTERITION_PASSPHRASE` env var
- `"No credentials found"` — Run `provision.sh` first
- `"Invalid passphrase"` — Wrong `INTERITION_PASSPHRASE` value
- `"HTTP 401"` — Credentials expired; re-provision the agent
- `"HTTP 404"` — Resource doesn't exist at that URL
