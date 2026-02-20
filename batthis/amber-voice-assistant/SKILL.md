---
name: amber-voice-assistant
description: "The most complete phone skill for OpenClaw. Production-ready, low-latency AI calls — inbound & outbound, multilingual, live dashboard, brain-in-the-loop."
homepage: https://github.com/batthis/amber-openclaw-voice-agent
metadata: {"openclaw":{"emoji":"☎️","requires":{"env":["TWILIO_ACCOUNT_SID","TWILIO_AUTH_TOKEN","TWILIO_CALLER_ID","OPENAI_API_KEY","OPENAI_PROJECT_ID","OPENAI_WEBHOOK_SECRET","PUBLIC_BASE_URL"],"optionalEnv":["OPENCLAW_GATEWAY_URL","OPENCLAW_GATEWAY_TOKEN","BRIDGE_API_TOKEN","TWILIO_WEBHOOK_STRICT","VOICE_PROVIDER","VOICE_WEBHOOK_SECRET"],"anyBins":["node","ical-query"]},"primaryEnv":"OPENAI_API_KEY"}}
---

# Amber — Phone-Capable Voice Agent

## Overview

Amber is a **voice sub-agent for OpenClaw** — it gives your OpenClaw deployment phone capabilities via a production-ready Twilio + OpenAI Realtime SIP bridge (`runtime/`) and a call log dashboard (`dashboard/`). Amber is not a standalone voice agent; it operates as an extension of your OpenClaw instance, delegating complex decisions (calendar lookups, contact resolution, approval workflows) back to OpenClaw mid-call via the `ask_openclaw` tool.

Amber handles inbound call screening, outbound calls, appointment booking, live OpenClaw knowledge lookups, and full call history visualization.

### What's included

- **Runtime bridge** (`runtime/`) — a complete Node.js server that connects Twilio phone calls to OpenAI Realtime with OpenClaw brain-in-the-loop
- **Call log dashboard** (`dashboard/`) — a real-time web UI showing call history, transcripts, captured messages, call summaries, and follow-up tracking with search and filtering
- **Setup & validation scripts** — preflight checks, env templates, quickstart runner
- **Architecture docs & troubleshooting** — call flow diagrams, common failure runbooks
- **Safety guardrails** — approval patterns for outbound calls, payment escalation, consent boundaries

## Why Amber vs. Other Voice Skills

Most voice skills on ClawHub route calls through a managed service (Bland AI, VAPI, Pamela). Amber takes a different approach: you own the stack, and your OpenClaw brain stays connected throughout the entire call.

**What Amber has that other phone skills don't:**

- **Live call dashboard** — Real-time web UI with full transcripts, call history, captured messages, follow-up tracking, and search/filter. No other phone skill on ClawHub includes this.
- **OpenClaw brain-in-the-loop** — The `ask_openclaw` tool delegates complex decisions back to your OpenClaw instance mid-call: calendar lookups, contact resolution, approval workflows — without hanging up.
- **Inbound + outbound in one agent** — Handle incoming call screening and place outbound calls with the same config and the same agent.
- **Multilingual auto-detection** — Amber detects the caller's language automatically and responds in kind. Supports Arabic, Spanish, French, and more via OpenAI Realtime. No configuration required.
- **Natural conversation feel** — VAD tuning and verbal fillers keep conversations flowing with no dead air during lookups or processing.
- **Provider-swappable architecture** — Twilio by default, swap to Telnyx or any supported carrier via `VOICE_PROVIDER`. No lock-in.
- **Production security hardening** — Webhook signature validation, authenticated control endpoints, prompt injection defenses, and a startup check that fails loudly if secrets are missing in production.
- **Full call history + follow-up tracking** — Every call is logged with transcript, summary, intent, and caller info. The dashboard surfaces unresolved follow-ups automatically.
- **Fully configurable** — Assistant name, operator info, org name, calendar integration, and screening style all set via env vars. Launch in minutes: `npm install`, configure `.env`, `npm start`.
- Operator safety guardrails for approvals/escalation/payment handling

## How tool calling works (`ask_openclaw`)

Amber isn't just a voice bot reading a script — she can consult your OpenClaw instance mid-call to answer questions she doesn't know from her instructions alone.

### The flow

```
Caller asks a question
        ↓
Amber (OpenAI Realtime) decides she needs more info
        ↓
Amber says "One moment, let me check on that for you"
        ↓
Amber calls the `ask_openclaw` tool with a short question
        ↓
Bridge sends the question to your OpenClaw gateway
  (via POST /v1/chat/completions on localhost)
        ↓
OpenClaw checks calendar, contacts, memory, etc.
        ↓
Response comes back → Amber speaks the answer to the caller
```

### Example

> **Caller:** "Is Abe free on Thursday?"
> **Amber:** "Let me check on that for you..."
> *(Amber calls ask_openclaw: "Is Abe available Thursday evening?")*
> *(OpenClaw checks calendar, responds: "Thursday evening is clear.")*
> **Amber:** "Yes, Thursday evening works! Shall I set something up?"

### Configuration

The bridge connects to your OpenClaw gateway at `OPENCLAW_GATEWAY_URL` (default: `http://127.0.0.1:18789`) using `OPENCLAW_GATEWAY_TOKEN` for auth. It sends questions as chat completions with:

- A system prompt providing call context (who's calling, the objective, recent transcript)
- The voice agent's question as the user message

Your OpenClaw instance handles the rest — calendar lookups, contact resolution, memory search, or whatever tools you have configured.

### When does Amber use it?

- Caller asks something not in the system prompt (schedule, availability, preferences)
- Caller requests information about the operator
- Outbound calls where Amber needs to verify details mid-conversation
- Any question where the answer requires your personal data/context

### Verbal fillers

To avoid dead air while waiting for OpenClaw to respond, Amber automatically says natural filler phrases like "One moment, let me check on that" before making the tool call. VAD (Voice Activity Detection) is tuned to avoid cutting off the caller during these pauses.

## Runtime environment variables

### Required

| Variable | Description |
|----------|-------------|
| `TWILIO_ACCOUNT_SID` | Your Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Your Twilio auth token (used for API calls and optional webhook validation) |
| `TWILIO_CALLER_ID` | Your Twilio phone number in E.164 format (e.g., `+14165551234`) |
| `OPENAI_API_KEY` | Your OpenAI API key |
| `OPENAI_PROJECT_ID` | Your OpenAI project ID (for Realtime SIP) |
| `OPENAI_WEBHOOK_SECRET` | Your OpenAI webhook secret (for signature verification) |
| `PUBLIC_BASE_URL` | The public URL where your bridge is hosted (e.g., `https://your-domain.com`) |

### Optional

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENCLAW_GATEWAY_URL` | `http://127.0.0.1:18789` | URL of your OpenClaw gateway for `ask_openclaw` tool |
| `OPENCLAW_GATEWAY_TOKEN` | *(empty)* | Bearer token for authenticating to your OpenClaw gateway |
| `BRIDGE_API_TOKEN` | *(empty)* | If set, require `Authorization: Bearer <token>` for `/call/outbound` and `/openclaw/ask`. If not set, these endpoints are localhost-only. |
| `VOICE_PROVIDER` | `twilio` | Telephony provider. Currently supported: `twilio` (production-ready), `telnyx` (stub — not yet implemented). Swap providers with zero code changes. |
| `VOICE_WEBHOOK_SECRET` | *(falls back to `TWILIO_AUTH_TOKEN`)* | Webhook validation secret for non-Twilio providers. **Required in production when `VOICE_PROVIDER` is not `twilio`** — the bridge will refuse to start with a fatal error if this is unset in `NODE_ENV=production`. For Twilio deployments, falls back to `TWILIO_AUTH_TOKEN` (which is already required). |
| `TWILIO_WEBHOOK_STRICT` | `true` | If `"false"`, log a warning on invalid Twilio signatures but still process the request (dev convenience only). Default is `true` — invalid signatures are rejected. Only set to `"false"` in local dev. |
| `ASSISTANT_NAME` | `Amber` | Name of your voice assistant |
| `OPERATOR_NAME` | `your operator` | Name of the person the assistant represents |
| `OPERATOR_PHONE` | *(empty)* | Operator's phone number (used in fallback responses) |
| `OPERATOR_EMAIL` | *(empty)* | Operator's email (used in fallback responses) |
| `ORG_NAME` | *(empty)* | Organization name (included in greetings) |
| `DEFAULT_CALENDAR` | *(empty)* | Default calendar name for bookings (e.g., `Abe`) |
| `OPENAI_VOICE` | `alloy` | OpenAI TTS voice (`alloy`, `echo`, `fable`, `onyx`, `nova`, `shimmer`) |
| `GENZ_CALLER_NUMBERS` | *(empty)* | Comma-separated list of E.164 numbers that should get Gen Z-style screening |
| `OUTBOUND_MAP_PATH` | `<cwd>/data/bridge-outbound-map.json` | Path for storing outbound call metadata |

### Security notes

- **`BRIDGE_API_TOKEN`**: Protects control endpoints (`/call/outbound`, `/openclaw/ask`) from unauthorized access. If not set, these endpoints only accept requests from localhost. **Highly recommended** if your bridge is internet-accessible.
- **`VOICE_PROVIDER`**: Selects the telephony carrier adapter. Amber uses a provider adapter pattern — the carrier layer (phone numbers, PSTN routing) is decoupled from the AI pipeline. Set to `twilio` (default) for production use. Setting `telnyx` will throw `not implemented` errors until the Telnyx adapter is filled in (`runtime/src/providers/telnyx.ts`). Future providers can be added without touching any core logic.
- **`TWILIO_WEBHOOK_STRICT`**: Defaults to `true` — invalid Twilio webhook signatures are rejected. Only set `TWILIO_WEBHOOK_STRICT=false` in local dev when you do not have valid Twilio credentials configured. Do not disable in production.

## ⚠️ Production security checklist

Before exposing Amber to the public internet, verify all of the following:

| # | Check | Risk if skipped |
|---|-------|-----------------|
| 1 | **Set `BRIDGE_API_TOKEN`** | `/call/outbound` and `/openclaw/ask` default to localhost-only. If your bridge is internet-accessible without a token, anyone can trigger outbound calls or query your OpenClaw instance. |
| 2 | **Set `VOICE_WEBHOOK_SECRET`** (or ensure `TWILIO_AUTH_TOKEN` is set) | For non-Twilio providers: the bridge **refuses to start** with a fatal error in `NODE_ENV=production` if this is unset. For Twilio: falls back to `TWILIO_AUTH_TOKEN`. If the fallback is also missing, webhook validation is skipped and spoofed requests will be accepted. |
| 3 | **Do not disable `TWILIO_WEBHOOK_STRICT`** | Defaults to `true` — invalid Twilio signatures are rejected. Only set `TWILIO_WEBHOOK_STRICT=false` in local dev. Disabling in production allows spoofed Twilio webhook requests. |
| 4 | **Secure the dashboard** | `dashboard/` exposes call transcripts and caller metadata. Serve it behind authentication or restrict to localhost only. |
| 5 | **Do not commit `dashboard/data/`** | Runtime call logs contain caller names and phone numbers. These are excluded from git and the published skill package by design — keep them that way. |

## External dependencies

### `ical-query` (optional)
`ical-query` is a macOS Swift CLI that reads Apple Calendar via EventKit — it is **not** a third-party package. It is referenced in `AGENT.md` for live calendar availability checks during call handling. It is only needed if you want Amber to check your local Apple Calendar mid-call.

- **Source:** Companion tool shipped with OpenClaw (`/usr/local/bin/ical-query`) — installed automatically by OpenClaw on macOS.
- **Not required:** If `ical-query` is absent, Amber will still function normally; calendar-check instructions in `AGENT.md` will not execute.
- **Platform:** macOS only (EventKit). Not available on Linux/Windows; omit those AGENT.md instructions if deploying on non-Apple hosts.

### `ical-query` argument safety

`ical-query` is invoked by the OpenClaw agent (not by the bridge runtime directly). To prevent RCE via malicious argument injection, `AGENT.md` enforces strict argument constraints:

- **Allowed subcommands only:** `today`, `tomorrow`, `week`, `range`, `calendars` — no others.
- **`range` date arguments:** must match `YYYY-MM-DD` exactly — the agent must validate against `/^\d{4}-\d{2}-\d{2}$/` before using a date as an argument.
- **No caller-provided input in arguments:** free-form caller speech, names, or any user input must never be interpolated into `ical-query` arguments.
- The bridge runtime itself does not shell out to `ical-query` — OpenClaw's own sandboxed tool executor handles it. This defense-in-depth rule constrains both the agent's reasoning and the tool sandbox.

See the "Calendar" section in `AGENT.md` for the full argument safety rules.

### `SUMMARY_JSON` structured output
`AGENT.md` instructs Amber to emit a silent `SUMMARY_JSON` token as the **final line** of a call session when a message is taken. This is **not** an exfiltration mechanism — it is consumed exclusively by OpenClaw's own SIP webhook handler (`/openai/webhook`) to extract caller name, callback number, and message for storage in the local call log and optional OpenClaw notification.

- **Who reads it:** The `runtime/src/index.ts` webhook handler — running on your own host.
- **Where it goes:** Written to `runtime/data/` (local disk only) and optionally forwarded to your OpenClaw gateway via `ask_openclaw` (your own instance, configured by you).
- **Never transmitted externally:** No third-party service receives this output. The bridge has no analytics, telemetry, or external data forwarding.
- **Scope is caller-provided data only:** name, callback number, and message — no system data, credentials, or environment variables.

## Call log data and privacy

The call log dashboard (`dashboard/`) stores transcripts and caller metadata in `dashboard/data/`. This directory is **excluded from the published skill package and git history** — it contains runtime-generated data local to your deployment.

- `dashboard/data/calls.json` and `dashboard/data/calls.js` are written at runtime and listed in `.gitignore`.
- The published skill includes only `dashboard/data/sample.*` files (anonymized, non-real data) for UI development/demo purposes.
- **Recommendation:** If your bridge is internet-accessible, set `BRIDGE_API_TOKEN` and serve the dashboard behind authentication or localhost-only.

## Webhook architecture

The bridge exposes two webhook endpoints — make sure you point each service to the right one:

| Endpoint | Source | Purpose | Signature verification |
|----------|--------|---------|----------------------|
| `/twilio/inbound` | Twilio | Incoming phone calls → generates TwiML to bridge to OpenAI SIP | None (Twilio-facing) |
| `/twilio/status` | Twilio | Call status callbacks (ringing, answered, completed) | None |
| `/openai/webhook` | OpenAI Realtime | Incoming SIP call events from OpenAI | ✅ `openai-signature` HMAC-SHA256 |
| `/call/outbound` | Your app/OpenClaw | Trigger an outbound call | Internal (localhost only) |

**Common setup mistake:** If you point Twilio's voice webhook at `/openai/webhook` instead of `/twilio/inbound`, calls will fail because Twilio doesn't send the `openai-signature` header that endpoint expects.

## Personalization requirements

Before deploying, users must personalize:
- assistant name/voice and greeting text,
- own Twilio number and account credentials,
- own OpenAI project + webhook secret,
- own OpenClaw gateway/session endpoint,
- own call safety policy (approval, escalation, payment handling).

Do not reuse example values from another operator.

## 5-minute quickstart

### Option A: Runtime bridge (recommended)

1. `cd runtime && npm install`
2. Copy `../references/env.example` to `runtime/.env` and fill in your values.
3. `npm run build && npm start`
4. Point your Twilio voice webhook to `https://<your-domain>/twilio/inbound`
5. Call your Twilio number — your voice assistant answers!

### Option B: Validation-only (existing setup)

1. Copy `references/env.example` to your own `.env` and replace placeholders.
2. Export required variables (`TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_CALLER_ID`, `OPENAI_API_KEY`, `OPENAI_PROJECT_ID`, `OPENAI_WEBHOOK_SECRET`, `PUBLIC_BASE_URL`).
3. Run quick setup:
   `scripts/setup_quickstart.sh`
4. If preflight passes, run one inbound and one outbound smoke test.
5. Only then move to production usage.

## Safe defaults

- Require explicit approval before outbound calls.
- If payment/deposit is requested, stop and escalate to the human operator.
- Keep greeting short and clear.
- Use timeout + graceful fallback when `ask_openclaw` is slow/unavailable.

## Workflow

1. **Confirm scope for V1**
   - Include only stable behavior: call flow, bridge behavior, fallback behavior, and setup steps.
   - Exclude machine-specific secrets and private paths.

2. **Document architecture + limits**
   - Read `references/architecture.md`.
   - Keep claims realistic (latency varies; memory lookups are best-effort).

3. **Run release checklist**
   - Read `references/release-checklist.md`.
   - Validate config placeholders, safety guardrails, and failure handling.

4. **Smoke-check runtime assumptions**
   - Run `scripts/validate_voice_env.sh` on the target host.
   - Fix missing env/config before publishing.

5. **Publish**
   - Publish to ClawHub (example):  
     `clawhub publish <skill-folder> --slug amber-voice-assistant --name "Amber Voice Assistant" --version 1.0.0 --tags latest --changelog "Initial public release"`
   - Optional: run your local skill validator/packager before publishing.

6. **Ship updates**
   - Publish new semver versions (`1.0.1`, `1.1.0`, `2.0.0`) with changelogs.
   - Keep `latest` on the recommended version.

## Call log dashboard

The built-in dashboard provides a real-time web UI for browsing your call history.

### Setup

1. `cd dashboard`
2. Optionally create `contacts.json` from `contacts.example.json` for caller name resolution
3. Process logs: `TWILIO_CALLER_ID=+1... node process_logs.js`
4. Serve: `node scripts/serve.js` → open `http://localhost:8080`

### Features

- Timeline view of all inbound/outbound calls
- Full transcript display per call
- Captured message extraction (name, callback number, message)
- AI-generated call summaries (intent, outcome, next steps)
- Search by name, number, transcript content, or call SID
- Follow-up flagging with local persistence
- Auto-refresh when new data is available
- Filter by direction, transcript availability, messages captured

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `TWILIO_CALLER_ID` | *(required)* | Your Twilio number — used to detect call direction |
| `ASSISTANT_NAME` | `Amber` | Name shown for the voice agent in call logs |
| `OPERATOR_NAME` | `the operator` | Name used in call summaries (e.g. "message passed to...") |
| `CONTACTS_FILE` | `./contacts.json` | Optional phone→name mapping file |
| `LOGS_DIR` | `../runtime/logs` | Directory containing call log files |
| `OUTPUT_DIR` | `./data` | Where processed JSON is written |
| `BRIDGE_OUTBOUND_MAP` | `<LOGS_DIR>/bridge-outbound-map.json` | Path to bridge outbound map (resolves To numbers & objectives) |

See `dashboard/README.md` for full documentation.

## Troubleshooting (common)

- **"Missing env vars"** → re-check `.env` values and re-run `scripts/validate_voice_env.sh`.
- **"Call connects but assistant is silent"** → verify TTS model setting and provider auth.
- **"ask_openclaw timeout"** → verify gateway URL/token and increase timeout conservatively.
- **"Webhook unreachable"** → verify tunnel/domain and Twilio webhook target.

## Guardrails for public release

- Never publish secrets, tokens, phone numbers, webhook URLs with credentials, or personal data.
- Include explicit safety rules for outbound calls, payments, and escalation.
- Mark V1 as beta if conversational quality/latency tuning is ongoing.

## Support & Contributing

Found a bug? Have a feature request? Want to contribute?

- **Issues & feature requests:** [GitHub Issues](https://github.com/batthis/amber-openclaw-voice-agent/issues)
- **Source code:** [github.com/batthis/amber-openclaw-voice-agent](https://github.com/batthis/amber-openclaw-voice-agent)
- **Pull requests welcome** — fork the repo, make your changes, and submit a PR.

## Resources

- **Runtime bridge:** `runtime/` (full source + README)
- **Call log dashboard:** `dashboard/` (web UI + log processor)
- Architecture and behavior notes: `references/architecture.md`
- Release gate: `references/release-checklist.md`
- Env template: `references/env.example`
- Quick setup runner: `scripts/setup_quickstart.sh`
- Env/config validator: `scripts/validate_voice_env.sh`
