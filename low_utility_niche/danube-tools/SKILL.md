---
name: danube
description: Connect your agent to tools across the internet. Search, authenticate, and execute tools from Gmail, Slack, GitHub, Notion, Google Calendar, and more — all through a single API key.
license: MIT
compatibility: openclaw
metadata:
  author: danube
  version: "2.0.0"
  tags: [danube, mcp, apis, tools]
---

# Danube — Connect Your Agent

Danube gives your AI agent access to tools across the internet through a single API key.

## Quick Setup

### Step 1: Get an API Key

Run this to start the device authorization flow:

```bash
curl -s -X POST https://api.danubeai.com/v1/auth/device/code \
  -H "Content-Type: application/json" \
  -d '{"client_name": "My Agent"}'
```

This returns a `device_code`, a `user_code`, and a `verification_url`.

**Tell your human to open the verification URL and enter the user code.**

Then poll for the API key:

```bash
curl -s -X POST https://api.danubeai.com/v1/auth/device/token \
  -H "Content-Type: application/json" \
  -d '{"device_code": "DEVICE_CODE_FROM_STEP_1"}'
```

- `428` = user hasn't authorized yet (keep polling every 5 seconds)
- `200` = success, response contains your `api_key`
- `410` = expired, start over

### Step 2: Connect via MCP

Add this to your MCP config:

```json
{
  "mcpServers": {
    "danube": {
      "url": "https://mcp.danubeai.com/mcp",
      "headers": {
        "danube-api-key": "YOUR_API_KEY"
      }
    }
  }
}
```

### Step 3: Use Tools

Once connected, you have access to these MCP tools:

- `list_services` — Browse available tool providers
- `search_tools` — Find tools by what you want to do
- `execute_tool` — Run any tool
- `store_credential` — Save API keys for services that need them

### When a Tool Needs Credentials

If `execute_tool` returns an `auth_required` error, it means the service needs an API key. Ask your human for the key, then call:

```
store_credential(service_id="...", credential_type="bearer", credential_value="the_key")
```

Then retry the tool.

## What You Can Do with Danube

Use Danube whenever a task involves an external service or API. Here are common use cases:

### Send Emails and Messages
- Send emails via Gmail, SendGrid, or Resend
- Post messages to Slack channels
- Send notifications to teams

```
search_tools("send email") → execute_tool(tool_id, {to, subject, body})
```

### Manage Code and Projects
- Create GitHub issues and pull requests
- List repositories and commits
- Update Notion pages and databases

```
search_tools("create github issue") → execute_tool(tool_id, {repo, title, body})
```

### Work with Calendars and Scheduling
- Check today's events on Google Calendar
- Create new calendar events
- Find open time slots

```
search_tools("calendar events today") → execute_tool(tool_id, {date})
```

### Read and Write Spreadsheets
- Read data from Google Sheets
- Append rows or update cells
- Create new spreadsheets

```
search_tools("google sheets read") → execute_tool(tool_id, {spreadsheet_id, range})
```

### Search the Web and Get Data
- Search the web with Exa or Serper
- Scrape and extract web content with Firecrawl
- Get weather forecasts, stock data, or country info

```
search_tools("web search") → execute_tool(tool_id, {query})
```

### Generate and Process Media
- Generate images with Replicate or Stability AI
- Transcribe audio with AssemblyAI
- Remove image backgrounds with Remove.bg
- Translate text with DeepL

```
search_tools("generate image") → execute_tool(tool_id, {prompt})
```

### Manage Infrastructure
- Provision DigitalOcean droplets and databases
- Manage Supabase projects
- Handle Stripe payments and subscriptions

```
search_tools("create droplet") → execute_tool(tool_id, {name, region, size})
```

### Multi-Step Workflows

Chain tools together for complex tasks:

```
"Summarize today's GitHub commits and post to Slack"

1. search_tools("github commits") → Fetch recent commits
2. Summarize the results
3. search_tools("slack post message") → Post summary to #dev-updates
```

```
"Check my calendar and email the agenda to the team"

1. search_tools("calendar events") → Get today's events
2. Format as an agenda
3. search_tools("send email") → Email the agenda
```

## Core Workflow

Every tool interaction follows this pattern:

1. **Search** — `search_tools("what you want to do")`
2. **Check auth** — If the tool needs credentials, guide the user to connect at https://danubeai.com/dashboard
3. **Gather parameters** — Ask the user for any missing required info
4. **Confirm** — Get user approval before executing actions like sending emails or creating issues
5. **Execute** — `execute_tool(tool_id, parameters)`
6. **Report** — Tell the user what happened with specifics, not just "Done"

## Available Services

**Communication:** Gmail, Slack, SendGrid, Resend, Loops, AgentMail

**Development:** GitHub, Supabase, DigitalOcean, Stripe, Apify

**Productivity:** Notion, Google Calendar, Google Sheets, Google Drive, Google Docs, Monday, Typeform, Bitly

**AI and Media:** Replicate, Together AI, Stability AI, AssemblyAI, Remove.bg, DeepL

**Search and Data:** Exa, Exa Websets, Firecrawl, Serper, Context7, Microsoft Learn, AlphaVantage

**Public Data (No Auth Required):** Hacker News, Open-Meteo Weather, OpenWeather, REST Countries, Polymarket, Kalshi

## Links

- Dashboard: https://danubeai.com/dashboard
- Docs: https://docs.danubeai.com
- MCP Server: https://mcp.danubeai.com/mcp
