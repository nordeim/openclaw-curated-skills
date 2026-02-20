# Health Sync Setup Reference

Use this file to guide setup behavior in ClawHub.

## Scope And Defaults

- Operate inside `workspace/health-sync`.
- Prefer `health-sync` CLI commands over direct provider API calls.
- You are expected to guide the user through setup.
- Default to user-run setup (recommended) to reduce risk of leaking secrets/tokens.
- Assisted setup is allowed only if the user explicitly asks for it.
- Do not use direct provider `curl` calls unless you are debugging a failed CLI auth flow.

## Standard Bootstrap (Always First)

1. Ensure the CLI is installed:

```bash
npm install -g health-sync
health-sync --help
```

2. Work inside the project directory:

```bash
mkdir -p workspace/health-sync
cd workspace/health-sync
```

3. Initialize config + local storage:

```bash
health-sync init
```

Expected files in this directory:

- `health-sync.toml`
- `health.sqlite`
- `.health-sync.creds` (created when auth tokens are saved)

## Direct Auth Rule (Mandatory)

For OAuth2 providers (`oura`, `withings`, `strava`, `whoop`), be direct and guide the user through this exact pattern:

1. Create/select provider app in the provider portal.
2. Get `client_id` and `client_secret`.
3. Set the exact callback URL in provider portal and `health-sync.toml`.
4. Run `health-sync auth <provider>` from `workspace/health-sync`.
5. Tell user they may see an error page after consent.
6. If an error page appears, they should still copy the full callback URL and send it.
7. Use that callback URL/code with the running `health-sync auth` flow.

For non-OAuth2 providers:

- Hevy: API key only (`[hevy].api_key`), no `auth` command.
- Eight Sleep: not OAuth2; uses account credentials (`email`/`password`) or `access_token`, then `health-sync auth eightsleep`.

## Two Flows After `health-sync init`

### 1) Recommended Flow (Default)

Use this unless the user explicitly asks for hands-on setup help.

1. Guide the user to edit `workspace/health-sync/health-sync.toml`.
2. Explain which fields they need for each enabled provider.
3. Tell them to run `health-sync auth` commands themselves from `workspace/health-sync`.
4. Then run sync/status.

User-run commands:

```bash
cd workspace/health-sync
health-sync auth oura
health-sync auth withings
health-sync auth strava
health-sync auth whoop
health-sync auth eightsleep
health-sync sync
health-sync status
```

Notes:

- Hevy does not use `health-sync auth`; it uses `[hevy].api_key` in `health-sync.toml`.
- `health-sync auth <provider>` scaffolds/enables that provider section in config.

### 2) Non-Recommended Assisted Flow

Use only if the user explicitly asks the agent to guide setup step-by-step.

1. Warn briefly that assisted setup may expose sensitive credentials/tokens.
2. Proceed one provider at a time.
3. For each provider:
   - guide where to get credentials
   - update `health-sync.toml`
   - run `health-sync auth <provider>` when supported
   - confirm success before moving to next provider
4. Avoid direct provider API calls unless debugging a CLI auth error.

Provider order:

1. `oura`
2. `withings`
3. `strava`
4. `whoop`
5. `eightsleep`
6. `hevy`

## Provider Setup Links And Credential Instructions

### Oura (`health-sync auth oura`)

Where the user goes:

- Oura app console: `https://developer.ouraring.com/applications`

How to get credentials:

1. Sign in to Oura developer portal.
2. Create/select an application.
3. Set callback/redirect URI to `http://localhost:8080/callback`.
4. Copy the app `client_id` and `client_secret`.
5. Put them in `[oura]` in `health-sync.toml`.

Config requirements:

- `[oura].client_id`
- `[oura].client_secret`
- `[oura].redirect_uri` (default scaffold: `http://localhost:8080/callback`)

Default OAuth endpoints in scaffold:

- authorize: `https://moi.ouraring.com/oauth/v2/ext/oauth-authorize`
- token: `https://moi.ouraring.com/oauth/v2/ext/oauth-token`

Run:

```bash
health-sync auth oura
```

Direct callback instruction:

- If Oura shows an error page after consent, ask the user to still copy the full callback URL and paste it.

### Withings (`health-sync auth withings`)

Where the user goes:

- Integration guide: `https://developer.withings.com/developer-guide/v3/integration-guide/public-health-data-api/developer-account/create-your-accesses-no-medical-cloud/`
- Developer dashboard: `https://developer.withings.com/dashboard/`

How to get credentials:

1. Sign in/create a Withings developer account.
2. Create/select an app for the public health data API.
3. Set callback/redirect URI to `http://127.0.0.1:8485/callback`.
4. Copy `client_id` and `client_secret`.
5. Put them in `[withings]` in `health-sync.toml`.

Config requirements:

- `[withings].client_id`
- `[withings].client_secret`
- `[withings].redirect_uri` (default scaffold: `http://127.0.0.1:8485/callback`)

Run:

```bash
health-sync auth withings
```

Direct callback instruction:

- If browser flow does not return cleanly, request the full callback URL and feed it back into the running auth flow.

### Strava (`health-sync auth strava`)

Where the user goes:

- Strava API app settings: `https://www.strava.com/settings/api`
- Strava auth docs: `https://developers.strava.com/docs/authentication`

How to get credentials:

1. Create/select a Strava API app.
2. Configure callback settings so your redirect URI matches `http://127.0.0.1:8486/callback`.
3. Copy app `client_id` and `client_secret`.
4. Put them in `[strava]` in `health-sync.toml`.

Config options:

- Option A (recommended): `[strava].client_id`, `[strava].client_secret`, `[strava].redirect_uri`
- Option B: `[strava].access_token` (static token mode)
- Default scaffold redirect: `http://127.0.0.1:8486/callback`

Run:

```bash
health-sync auth strava
```

Direct callback instruction:

- If consent flow does not complete cleanly in browser, ask for the full callback URL and continue auth with it.

### WHOOP (`health-sync auth whoop`)

Where the user goes:

- WHOOP Developer Dashboard: `https://developer-dashboard.whoop.com`
- WHOOP Getting Started: `https://developer.whoop.com/docs/developing/getting-started`
- WHOOP OAuth docs: `https://developer.whoop.com/docs/developing/oauth`

How to get credentials:

1. Create/select a WHOOP app in the Developer Dashboard.
2. Configure redirect URI to `http://127.0.0.1:8487/callback`.
3. Ensure app scopes include the WHOOP datasets needed for sync.
4. Include `offline` scope so the CLI receives refresh tokens.
5. Copy `client_id` and `client_secret`.
6. Put them in `[whoop]` in `health-sync.toml`.

Config requirements:

- `[whoop].client_id`
- `[whoop].client_secret`
- `[whoop].redirect_uri` (default scaffold: `http://127.0.0.1:8487/callback`)
- `[whoop].scopes` should include `offline`

Default WHOOP endpoints in scaffold:

- authorize: `https://api.prod.whoop.com/oauth/oauth2/auth`
- token: `https://api.prod.whoop.com/oauth/oauth2/token`
- API base: `https://api.prod.whoop.com/developer`

Run:

```bash
health-sync auth whoop
```

Direct callback instruction:

- If consent flow does not complete cleanly in browser, ask for the full callback URL and continue auth with it.

### Eight Sleep (`health-sync auth eightsleep`)

Where the user goes:

- Eight Sleep app/web account (no public OAuth app dashboard required for this flow)

How to get credentials:

1. Use account credentials from Eight Sleep app/web login.
2. Put `email` and `password` in `[eightsleep]`.
3. Keep scaffolded `client_id`/`client_secret` defaults unless there is a known upstream change.

Config options:

- Option A (recommended): `[eightsleep].email`, `[eightsleep].password`
- Option B: `[eightsleep].access_token`
- `client_id` and `client_secret` defaults are scaffolded by `health-sync init`

Run:

```bash
health-sync auth eightsleep
```

### Hevy (No `auth` command)

Where the user goes:

- Hevy API docs: `https://api.hevyapp.com/docs/`
- Hevy developer/API key page: `https://hevy.com/settings?developer`

How to get credentials:

1. Open Hevy developer page.
2. Generate/copy API key (Hevy Pro required).
3. Put key in `[hevy].api_key` and set `enabled = true`.

Config requirements:

- `[hevy].api_key`

Run sync after config:

```bash
health-sync sync
```

## Post-Setup Checks

Run from `workspace/health-sync`:

```bash
health-sync providers --verbose
health-sync sync
health-sync status
```

## Safety Notes

- Keep all setup work in `workspace/health-sync`.
- Never commit `health-sync.toml` if it contains secrets.
- Never commit `.health-sync.creds`.
- Prefer guiding the user to run auth locally themselves.
