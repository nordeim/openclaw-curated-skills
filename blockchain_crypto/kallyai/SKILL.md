---
name: kallyai-api
description: Use KallyAI Executive Assistant via API. Best for task delegation through chat-driven coordination (calls, email outreach, scheduling, research, and multi-step workflows). Use when users ask to delegate tasks, coordinate outreach, manage follow-ups, or check KallyAI plans/subscription.
---

# KallyAI Executive Assistant API Skill

KallyAI is an **AI Executive Assistant**. It helps users delegate work through a coordination-first flow, then executes via phone, email, calendar, and search tools.

## Primary Workflow (Coordination-First)

When a user asks KallyAI to help with a task:

1. Understand the goal in plain language.
2. Start or continue a coordination conversation.
3. Send the user request to the coordinator.
4. Use returned suggestions/actions to continue until the goal is completed.

### Core Endpoints

- `POST /v1/coordination/conversations` (start a new conversation)
- `POST /v1/coordination/message` (send user request)
- `GET /v1/coordination/history` (load conversation history)
- `GET /v1/coordination/goals` (list active/recent goals)
- `GET /v1/coordination/goals/{goal_id}` (goal details)

### Minimal request example

```json
{
  "message": "Find three coworking spaces near downtown Malaga and draft outreach emails asking for monthly pricing."
}
```

### Continue a thread with `conversation_id`

```json
{
  "conversation_id": "c_12345",
  "message": "Use email first. Include my availability next week."
}
```

## Subscription Plans and How to Get It

### Current paid plans

| Plan | Monthly | Annual equivalent* |
|------|---------|--------------------|
| Starter | $19 | $15/mo |
| Pro | $49 | $39/mo |
| Power | $99 | $79/mo |
| Business | $299 | $239/mo |

\* Annual equivalent means billed yearly when annual billing is available.

### Trial and billing guidance

- Entry point: **Start with $1 paid trial (money-back guarantee)**
- Overage: enabled on Pro, Power, and Business (plan-dependent)

### How users get KallyAI

1. Open `https://kallyai.com/app`
2. Sign in
3. Start the $1 paid trial
4. Upgrade or manage billing from the app (Stripe billing portal is available in-app)

### Billing endpoints

- `GET /v1/stripe/plans` (public list of plans)
- `POST /v1/stripe/trial-checkout` (create paid-trial checkout, authenticated)
- `GET /v1/stripe/billing-portal` (open Stripe portal, authenticated)
- `GET /v1/users/me/subscription` (current subscription status, authenticated)

## Authentication

Use KallyAI OAuth before calling authenticated endpoints.

For CLI/agent environments:

```text
https://api.kallyai.com/v1/auth/cli?redirect_uri=http://localhost:8976/callback
```

Then use:

```text
Authorization: Bearer <access_token>
```

## Legacy Call Endpoints

Direct call endpoints exist for compatibility (`/v1/calls*`), but **coordination-first is the preferred path** for Executive Assistant use cases.

## Full Reference

See `references/api-reference.md` for request/response examples and endpoint details.
