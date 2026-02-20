---
name: business-account-opening
description: Open a Vivid Business account — extract company data from documents or chat, then generate an onboarding link.
version: 0.1.0

metadata:
  openclaw:
    emoji: "🏦"
    homepage: "https://github.com/vivid-money/vivid-mcp"
    requires:
      env: []
      bins: []
      config: []
---

# Business Account Opening

Help the user open a Vivid Business account using `vivid-mcp`.

## Trigger

User wants to open a business account or start business onboarding.

## Flow

1. Ask for **legal entity type** (GmbH, UG, freelancer, etc.) if not provided.
2. Ask for **country** if not provided. Default: Germany.
3. Call MCP to get required fields and accepted document types.
4. Offer two paths:
   - **Upload documents** — extract and prefill automatically
   - **Manual entry** — collect fields in chat
5. Call `build_onboarding_link` with confirmed data. Return the URL.

## Rules

- Fetch requirements from MCP first. Never hardcode.
- Treat uploaded documents as sensitive — summarize only, don't echo contents.
- Never ask for passwords or API keys.
- On error: ask for missing fields or suggest a different document.
