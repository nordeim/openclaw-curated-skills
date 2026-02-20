---
name: ogment
description: Access business integrations (SaaS, APIs, data) securely through Ogment. Use when the user asks to query, create, update, or manage data in external systems like Salesforce, Notion, Slack, databases, or any connected service.
metadata: {"openclaw":{"emoji":"🦞","requires":{"bins":["ogment"]},"install":[{"id":"npm","kind":"node","package":"ogment","bins":["ogment"],"label":"Install Ogment CLI (npm)"}]}}
---

# Ogment

Ogment gives you secure access to business integrations — SaaS tools, internal APIs, and data — through a single CLI. Credentials never leave Ogment. You get scoped, revocable tokens with per-tool permissions and human approval flows.

## Setup (one-time)

If `ogment` is not installed or any command fails with "not logged in":

1. Install: `npm install -g ogment`
2. Ask the user to run `ogment login` in their terminal (opens browser for OAuth — zero arguments needed)
3. Login is a one-time step. After authenticating, all servers and tools are available automatically.

## Commands

**Discover servers:**
```bash
ogment servers --json
```
Returns all available servers across all organizations.

**Inspect a server's tools:**
```bash
ogment servers <server-path> --json
```
Returns the full list of tools with names, descriptions, and input schemas.

**Call a tool:**
```bash
ogment call <server-path> <tool-name> '<json-args>'
```
Returns JSON. Arguments must be a single JSON string. Omit args for tools that take no parameters.

## Workflow

Follow these steps in order:

1. Run `ogment servers --json` to discover available servers
2. Pick the server relevant to the user's request
3. Run `ogment servers <path> --json` to see that server's tools
4. Call the appropriate tool with `ogment call <server> <tool> '<args>'`
5. Parse the JSON response and present results to the user
6. If the user needs a different integration, go back to step 1

## Examples

```bash
# Discover all servers
ogment servers --json

# Inspect tools on a server
ogment servers salesforce --json

# Query data
ogment call salesforce query_accounts '{"limit":5}'
ogment call notion search '{"query":"Q1 roadmap"}'
ogment call data-warehouse run_query '{"sql":"SELECT * FROM orders LIMIT 10"}'

# Create records
ogment call salesforce create_record '{"type":"Contact","fields":{"Name":"Jane Doe","Email":"jane@example.com"}}'

# Health check (no args)
ogment call my-api get__health
```

## Handling Errors

- **"not logged in"** — ask the user to run `ogment login` in their terminal
- **"server not found"** — run `ogment servers --json` to see available servers
- **approval link returned** — the tool requires human approval. Show the approval URL to the user and ask them to approve. Then retry the same tool call.
- **401 / authentication error** — the token may be expired. Ask the user to run `ogment logout` then `ogment login`

## Important

- Always use `--json` when discovering servers and tools
- `ogment call` returns JSON by default — no `--json` flag needed
- Arguments to `ogment call` must be a single JSON string
- Do not store or log tokens — Ogment handles all credentials server-side
- Each tool call is authenticated, permission-checked, and logged by Ogment
