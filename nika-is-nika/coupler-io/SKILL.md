# Coupler.io

Read-only data access via Coupler.io's MCP server.

**Author:** Coupler.io Team
**Homepage:** [coupler.io](https://coupler.io)

## Prerequisites

- [mcporter](https://github.com/openclaw/mcporter) CLI installed and on PATH
- `curl`, `jq`, `openssl` — standard on macOS/Linux; install via your package manager if missing
- Coupler.io account with at least one data flow configured to OpenClaw destination

## Quick Reference

```bash
mcporter call coupler.list-dataflows
mcporter call coupler.get-dataflow dataflowId=<uuid>
mcporter call coupler.get-schema executionId=<exec-id>
mcporter call coupler.get-data executionId=<exec-id> query="SELECT * FROM data LIMIT 10"
```

---

## Connection Setup

> **Endpoint verification:** This skill connects to `auth.coupler.io` (OAuth) and `mcp.coupler.io` (MCP data). These are official Coupler.io endpoints. You can verify them via your Coupler.io account (AI integrations page).

### Automated Setup

Run the setup script — it handles everything automatically (no manual input needed):

```bash
bash CPL/setup.sh
```

The script registers the OAuth client, opens the browser for login, automatically captures the callback code via a local HTTP server on port 8976, exchanges for tokens, and saves config — all hands-free.

Note: OAuth credentials are saved in `coupler-io/oauth-state.json`

### Manual OAuth Flow (First-Time Only)

1. **Register client:**

   ```bash
   curl -X POST https://auth.coupler.io/oauth2/register \
     -H "Content-Type: application/json" \
     -d '{
       "client_name": "OpenClaw",
       "redirect_uris": ["http://127.0.0.1:8976/callback"],
       "grant_types": ["authorization_code"],
       "response_types": ["code"],
       "token_endpoint_auth_method": "none"
     }'
   ```

   Save `client_id` from response.

2. **Generate PKCE:**

   ```bash
   CODE_VERIFIER=$(openssl rand -base64 32 | tr -d '=/+' | cut -c1-43)
   CODE_CHALLENGE=$(echo -n "$CODE_VERIFIER" | openssl dgst -sha256 -binary | base64 | tr -d '=' | tr '+/' '-_')
   ```

3. **Browser auth** — open URL, user logs in:

   ```text
   https://auth.coupler.io/oauth2/authorize?client_id=<client_id>&redirect_uri=http://127.0.0.1:8976/callback&response_type=code&scope=mcp&code_challenge=<code_challenge>&code_challenge_method=S256
   ```

4. **Exchange code** (from callback URL):

   ```bash
   curl -X POST https://auth.coupler.io/oauth2/token \
     -d "grant_type=authorization_code&client_id=<client_id>&code=<auth_code>&redirect_uri=http://127.0.0.1:8976/callback&code_verifier=<code_verifier>"
   ```

5. **Save tokens:**
   - `access_token` → `config/mcporter.json`
   - `refresh_token` → `coupler-io/oauth-state.json` (critical for silent refresh)

6. **Secure token files:**

   ```bash
   chmod 600 config/mcporter.json CPL/oauth-state.json
   ```

   > ⚠️ Token files contain sensitive credentials. Never commit them to version control (already excluded via `.gitignore`). For additional security, consider storing tokens in your system keychain (macOS: `security add-generic-password`).

### mcporter Config

`config/mcporter.json`:

```json
{
  "mcpServers": {
    "coupler": {
      "baseUrl": "https://mcp.coupler.io/mcp",
      "headers": {
        "Authorization": "Bearer <access_token>"
      }
    }
  }
}
```

### OAuth State

`coupler-io/oauth-state.json`:

```json
{
  "authServer": "https://auth.coupler.io",
  "clientId": "<client_id>",
  "refreshToken": "<refresh_token>"
}
```

---

## Token Refresh

Access tokens expire in 2 hours. Refresh silently:

```bash
CLIENT_ID=$(jq -r '.clientId' coupler-io/oauth-state.json)
REFRESH_TOKEN=$(jq -r '.refreshToken' coupler-io/oauth-state.json)
AUTH_SERVER=$(jq -r '.authServer' coupler-io/oauth-state.json)

curl -s -X POST "$AUTH_SERVER/oauth2/token" \
  -d "grant_type=refresh_token&client_id=$CLIENT_ID&refresh_token=$REFRESH_TOKEN"
```

Update `config/mcporter.json` with new `access_token` and `coupler-io/oauth-state.json` with new `refresh_token`.

**When to refresh:** On 401 errors, or proactively before MCP calls if token is near expiry.

---

## MCP Tools

### list-dataflows

List all data flows with OpenClaw destination.

```bash
mcporter call coupler.list-dataflows --output json
```

### get-dataflow

Get flow details including `lastSuccessfulExecutionId`.

```bash
mcporter call coupler.get-dataflow dataflowId=<uuid> --output json
```

### get-schema

Get column definitions. Column names are in `columnName` (e.g., `col_0`, `col_1`).

```bash
mcporter call coupler.get-schema executionId=<exec-id>
```

### get-data

Run SQL on flow data. Table is always `data`.

```bash
mcporter call coupler.get-data executionId=<exec-id> query="SELECT col_0, col_1 FROM data WHERE col_2 > 100 LIMIT 50"
```

**Always sample first** (`LIMIT 5`) to understand structure before larger queries.

---

## Typical Workflow

```bash
# 1. List flows, find ID
mcporter call coupler.list-dataflows --output json | jq '.[] | {name, id}'

# 2. Get execution ID
mcporter call coupler.get-dataflow dataflowId=<id> --output json | jq '.lastSuccessfulExecutionId'

# 3. Check schema
mcporter call coupler.get-schema executionId=<exec-id>

# 4. Query
mcporter call coupler.get-data executionId=<exec-id> query="SELECT * FROM data LIMIT 10"
```

---

## Constraints

- Read-only: cannot modify flows, sources, or data
- Only flows with OpenClaw destination are visible
- Tokens expire in 2 hours (use refresh token)
