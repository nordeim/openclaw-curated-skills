---
name: agentstead-deploy
description: Deploy OpenClaw agents to AgentStead cloud hosting. Use when a user wants to deploy their agent to the cloud, host an AI assistant on Telegram/Discord, or set up a remote OpenClaw instance. Handles account creation, agent provisioning, channel connection, and billing.
---

# AgentStead Deploy

Deploy an OpenClaw agent to AgentStead's cloud hosting in minutes.

**API Base URL:** `https://agentstead.com/api/v1`

## Quick Deploy Flow

1. Register/login → 2. Create agent → 3. Add channel → 4. Set up billing → 5. Start agent → 6. Verify

## Conversation Guide

Before calling any APIs, gather from the user:

1. **Agent name** — What should the agent be called?
2. **Personality/instructions** — System prompt or personality description
3. **Channel** — Telegram (need bot token from @BotFather) or Discord (need bot token from Discord Developer Portal)
4. **AI plan** — BYOK (bring your own API key, $0) or Platform AI (Pro +$20/mo, Max +$100/mo)
5. **If BYOK** — Which provider and API key? (Anthropic, OpenAI, Google, OpenRouter, xAI, Groq, Mistral, Bedrock, Venice)
6. **Hosting plan** — Starter $9/mo, Pro $19/mo, Business $39/mo, Enterprise $79/mo
7. **Payment method** — Crypto (USDC) or card (Stripe)

## Step-by-Step Workflow

### Step 1: Register

```bash
curl -X POST https://agentstead.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

Response includes `token` — use as `Authorization: Bearer <token>` for all subsequent requests.

If user already has an account, use login instead:

```bash
curl -X POST https://agentstead.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

### Step 2: Create Agent

```bash
curl -X POST https://agentstead.com/api/v1/agents \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyAgent",
    "personality": "You are a helpful assistant...",
    "plan": "starter",
    "aiPlan": "byok",
    "byokProvider": "anthropic",
    "byokApiKey": "sk-ant-..."
  }'
```

For platform AI instead of BYOK:
```json
{
  "name": "MyAgent",
  "personality": "You are a helpful assistant...",
  "plan": "pro",
  "aiPlan": "pro_ai"
}
```

Response includes the agent `id` — save it for subsequent steps.

### Step 3: Add Channel

**Telegram:**
```bash
curl -X POST https://agentstead.com/api/v1/agents/<agent_id>/channels \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "telegram", "botToken": "123456:ABC-DEF..."}'
```

**Discord:**
```bash
curl -X POST https://agentstead.com/api/v1/agents/<agent_id>/channels \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "discord", "botToken": "MTIz..."}'
```

### Step 4: Set Up Billing

**Crypto (USDC):**
```bash
curl -X POST https://agentstead.com/api/v1/billing/crypto/create-invoice \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent_id>", "plan": "starter", "aiPlan": "byok"}'
```

Returns a payment address/URL. Guide user to send USDC.

**Stripe (card):**
```bash
curl -X POST https://agentstead.com/api/v1/billing/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent_id>", "plan": "starter", "aiPlan": "byok"}'
```

Returns a Stripe checkout URL. Send to user to complete payment.

### Step 5: Start Agent

```bash
curl -X POST https://agentstead.com/api/v1/agents/<agent_id>/start \
  -H "Authorization: Bearer <token>"
```

### Step 6: Verify

```bash
curl -X GET https://agentstead.com/api/v1/agents/<agent_id> \
  -H "Authorization: Bearer <token>"
```

Check that `status` is `"RUNNING"`. If not, wait a few seconds and retry.

## Pricing Reference

| Plan | Price |
|------|-------|
| Starter | $9/mo |
| Pro | $19/mo |
| Business | $39/mo |
| Enterprise | $79/mo |

| AI Plan | Price |
|---------|-------|
| BYOK | $0 (bring your own key) |
| Pro AI | +$20/mo |
| Max AI | +$100/mo |

**Supported BYOK Providers:** Anthropic, OpenAI, Google, OpenRouter, xAI, Groq, Mistral, Bedrock, Venice

## Notes

- Telegram bot tokens come from [@BotFather](https://t.me/BotFather)
- Discord bot tokens come from the [Discord Developer Portal](https://discord.com/developers/applications)
- Agents can be stopped with `POST /agents/:id/stop` and restarted anytime
- See `references/api-reference.md` for full API documentation
