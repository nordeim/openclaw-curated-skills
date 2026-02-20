---
name: deepread-agent-setup
title: DeepRead OCR — Agent Self-Signup
description: Zero-friction agent signup for production OCR. Your AI agent gets its own API key in seconds via device authorization — no dashboard, no copy/paste. 97%+ accuracy with multi-model consensus and human-in-the-loop review. 2,000 free pages/month.
disable-model-invocation: true
metadata:
  {"openclaw":{"homepage":"https://www.deepread.tech"}}
---

# **DeepRead OCR — Zero-Friction Agent Setup**

DeepRead is an AI-native OCR platform that turns documents into high-accuracy data in minutes. Your agent signs up and gets its own API key automatically — no dashboard, no copy/paste.

Using a multi-pass pipeline (`PDF → Convert → Rotate Correction → OCR → Multi-Model Validation → Extract`), DeepRead achieves 97%+ accuracy and flags only uncertain fields for Human-in-the-Loop review — reducing manual work from 100% to 5-10%. Zero prompt engineering required.

&nbsp;

# **Core Features**

- Agent Self-Signup — your agent gets an API key via device authorization (RFC 8628), you just click Approve
- Text Extraction — convert PDFs and images to clean markdown
- Structured Data — extract JSON fields with confidence scores
- HIL Interface — uncertain fields are flagged (`hil_flag`) so only exceptions need manual review
- Multi-Model Consensus — cross-validation between models for reliability
- Blueprints — optimized reusable schemas with 20-30% accuracy improvement
- Free Tier — 2,000 pages/month (no credit card required)

&nbsp;

# **Agent Self-Signup**

Your agent gets its own API key automatically. No dashboard, no copy/paste. You just click "Approve" once in the browser. This uses secure device authorization (RFC 8628) — the same pattern used by GitHub CLI, Slack, and VS Code.

&nbsp;

Step 1 — Agent requests a device code (no auth needed):

```bash
curl -X POST https://api.deepread.tech/v1/agent/device/code \
  -H "Content-Type: application/json" \
  -d '{"agent_name": "My Agent"}'
```

Response:

```json
{
  "device_code": "a7f3c9d2e1b8...",
  "user_code": "HXKP-3MNV",
  "verification_uri": "https://www.deepread.tech/activate",
  "verification_uri_complete": "https://www.deepread.tech/activate?code=HXKP-3MNV",
  "expires_in": 900,
  "interval": 5
}
```

&nbsp;

Step 2 — Agent opens `verification_uri_complete` in the browser. You log in (or sign up — free, no credit card), see the agent name, and click Approve.

&nbsp;

Step 3 — Agent polls for the API key every 5 seconds:

```bash
curl -X POST https://api.deepread.tech/v1/agent/device/token \
  -H "Content-Type: application/json" \
  -d '{"device_code": "a7f3c9d2e1b8..."}'
```

&nbsp;

| **error** | **api_key** | **Meaning** |
|:--|:--|:--|
| `"authorization_pending"` | `null` | User hasn't approved yet — keep polling |
| `null` | `"sk_live_..."` | User approved — save the key |
| `"access_denied"` | `null` | User denied — stop polling |
| `"expired_token"` | `null` | Code expired (15 min) — start over |

&nbsp;

Step 4 — Agent saves the key. Done — ready to process documents.

&nbsp;

# **Manual Setup (Fallback)**

If you prefer to skip the agent flow, get a key from the dashboard and set it manually:

```bash
# 1. Get your key at https://www.deepread.tech/dashboard/?utm_source=clawdhub
# 2. Set it
export DEEPREAD_API_KEY="sk_live_your_key_here"
```

&nbsp;

# **Supported Platforms**

DeepRead skills work across all major AI coding agents.
After installing, use `/setup` (agent signup + first document) and `/api` (full API reference).

&nbsp;

| **Platform** | **Install** | **Skills** |
|:--|:--|:--|
| Claude Code | `npx skills add deepread-tech/skills` | `/setup`, `/api` |
| Cursor | Copy `.cursor/rules/` from [skills repo](https://github.com/deepread-tech/skills) | Auto-invoked rules |
| Windsurf | Copy `.windsurf/rules/` from [skills repo](https://github.com/deepread-tech/skills) | Auto-invoked rules |
| ClawHub | `clawhub add DeepRead001/deepread-agent-setup` | `/setup`, `/api` |
| MCP agents | Use device flow endpoints directly | Full API access |

&nbsp;

# **Quick Example**

Once you have an API key (via agent self-signup or manual), process any document:

```bash
curl -X POST https://api.deepread.tech/v1/process \
  -H "X-API-Key: $DEEPREAD_API_KEY" \
  -F "file=@invoice.pdf" \
  -F 'schema={
    "type": "object",
    "properties": {
      "vendor": {"type": "string", "description": "Vendor name"},
      "total": {"type": "number", "description": "Total amount"},
      "date": {"type": "string", "description": "Invoice date"}
    }
  }'
```

&nbsp;

Processing is async (takes 2-5 minutes). You get a job ID immediately:

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "queued"
}
```

Then get results via webhook (recommended) or polling `GET /v1/jobs/{id}`. Final response:

```json
{
  "status": "completed",
  "result": {
    "data": {
      "vendor": {"value": "Acme Corp", "hil_flag": false},
      "total": {"value": 1250.00, "hil_flag": false},
      "date": {"value": "2024-10-??", "hil_flag": true, "reason": "Partially obscured"}
    }
  },
  "preview_url": "https://preview.deepread.tech/abc1234"
}
```

- `hil_flag: false` — confident extraction, auto-process
- `hil_flag: true` — uncertain, route to human review (typically only 5-10% of fields)

&nbsp;

# **API Overview**

| **Endpoint** | **What it does** |
|:--|:--|
| `POST /v1/agent/device/code` | Start agent self-signup |
| `POST /v1/agent/device/token` | Poll for API key |
| `POST /v1/process` | Process a document (PDF, JPG, PNG) |
| `GET /v1/jobs/{id}` | Check job status |
| `GET /v1/blueprints` | List optimized schemas |
| `POST /v1/optimize` | Create a new blueprint |
| `GET /v1/preview/{token}` | Public preview link (no auth) |

&nbsp;

Base URL: `https://api.deepread.tech`

Auth: `X-API-Key: sk_live_...` header

&nbsp;

For complete API documentation with all examples, webhooks, blueprints, schema templates, and best practices, see the full API skill: [deepread-ocr](https://clawhub.ai/DeepRead001/deepread-ocr)

&nbsp;

# **Pricing**

| **Tier** | **Pages/month** | **Rate limit** | **Price** |
|:--|:--|:--|:--|
| Free | 2,000 | 10 req/min | $0 (no credit card) |
| Pro | 50,000 | 100 req/min | $99/mo |
| Scale | Custom | Custom | [Contact us](mailto:hello@deepread.tech) |

&nbsp;

# **Links**

- Skills Repo: https://github.com/deepread-tech/skills
- Dashboard: https://www.deepread.tech/dashboard
- Docs: https://www.deepread.tech/docs
- Full API Skill: https://clawhub.ai/DeepRead001/deepread-ocr
- Issues: https://github.com/deepread-tech/deep-read-service/issues
- Email: hello@deepread.tech

---

Ready to start? Run `/setup` and your agent handles the rest.
