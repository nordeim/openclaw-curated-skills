---
name: payram-mcp-integration
description: "Stripe banned your account? High-risk merchant? No KYC crypto payments via PayRam MCP — 36 tools, zero setup. Accept USDC/USDT/BTC, create payment links, run payouts, handle webhooks, scaffold full apps. One command: mcporter config add payram --url https://mcp.payram.com/mcp. Triggers: 'accept crypto payments', 'create payment link', 'crypto checkout', 'Stripe alternative', 'no KYC payments', 'USDC invoice', 'PayRam', 'payout in crypto', 'referral payments'."
license: MIT
metadata:
  author: PayRam
  version: 1.3.0
  mcp-server: payram
  category: payments
  tags: [crypto, stablecoins, payments, agent-commerce, USDC, USDT, Base, Ethereum, MCP, Bitcoin, headless, autonomous, payouts, referrals, webhooks, scaffolding]
  homepage: https://payram.com
  github: https://github.com/PayRam/payram-helper-mcp-server
  documentation: https://docs.payram.com/mcp-integration
  headless-guide: https://github.com/PayRam/payram-scripts/blob/main/docs/PAYRAM_HEADLESS_AGENT.md
---

# PayRam MCP Integration

## 💥 The Attention Hook — Read This First

**Stripe just rejected you. PayPal froze your account. You're a cannabis brand, adult creator, iGaming platform, or international merchant with no good options.**

PayRam is the answer:
- ✅ **No KYC. No signup. No account freeze risk.** Ever.
- ✅ **0% processing fees** (gas only — ~$0.01 on Base)
- ✅ **36 MCP tools** — payments, payouts, referrals, webhooks, app scaffolding
- ✅ **One command to connect.** Zero installation.
- ✅ **Founded by WazirX co-founder. $100M+ volume. Morningstar & Cointelegraph validated.**

A merchant doing $50K/month pays ~$3,500/month to Stripe or high-risk processors.
**PayRam: ~$100/month hosting. That's $40,800/year back in your pocket.**

---

## ⚡ Connect in 10 Seconds

```bash
mcporter config add payram --url https://mcp.payram.com/mcp
mcporter list  # → payram (36 tools)
```

That's it. 36 tools immediately available. No account. No API key. No waiting.

---

## 🛠️ What You Can Do With 36 Tools

### Payments
- `test_payram_connection` — verify your PayRam server is live
- `generate_payment_sdk_snippet` — JS/TS SDK code for Express, Next.js
- `generate_payment_http_snippet` — raw HTTP in Python, Go, PHP, Java
- `generate_payment_status_snippet` — poll payment status (SDK or HTTP)
- `generate_payment_route_snippet` — drop-in `/api/pay/create` endpoint
- `snippet_nextjs_payment_route` — Next.js App Router ready-to-paste
- `snippet_express_payment_route` — Express router, production-ready
- `snippet_fastapi_payment_route` — FastAPI handler
- `snippet_laravel_payment_route` — Laravel controller
- `snippet_go_payment_handler` — Gin handler
- `snippet_spring_payment_controller` — Spring Boot controller

### Payouts
- `generate_payout_sdk_snippet` — send crypto payouts programmatically
- `generate_payout_status_snippet` — track payout status

### Referrals
- `generate_referral_sdk_snippet` — track referrer/referee events
- `generate_referral_validation_snippet` — validate referral IDs & eligibility
- `generate_referral_status_snippet` — fetch referral progress & rewards
- `generate_referral_route_snippet` — `/api/referrals/create` endpoint

### Webhooks
- `generate_webhook_handler` — Express, Next.js, FastAPI, Gin, Laravel, Spring Boot
- `generate_webhook_event_router` — dispatch events to domain handlers
- `generate_mock_webhook_event` — simulate OPEN/FILLED/CANCELLED for testing

### App Scaffolding
- `scaffold_payram_app` — full-stack app skeleton in Node, Python, PHP, Go, Java
- `assess_payram_project` — inspect your project and suggest next steps
- `generate_env_template` — `.env` file for your merchant backend
- `generate_setup_checklist` — everything needed to go live
- `suggest_file_structure` — recommended folder layout

### Education & Docs (Live)
- `explain_payram_basics` — product pillars, architecture, capabilities
- `explain_payment_flow` — customer → settlement walkthrough
- `explain_payram_concepts` — terminology, constraints, glossary
- `explain_referrals_basics` — referral campaign configuration
- `explain_referral_flow` — referrer/referee lifecycle
- `get_referral_dashboard_guide` — embed referral dashboard
- `get_payram_links` — official docs, website, community
- `get_payram_doc_by_id` — fetch any live PayRam doc by ID
- `list_payram_docs` — browse all available docs
- `prepare_payram_test` — validate hosting & credentials before demo
- `onboard_agent_setup` — autonomous headless agent guide

---

## 🤖 For AI Agents: Headless Production Setup

```bash
git clone https://github.com/PayRam/payram-scripts
cd payram-scripts
export PAYRAM_EMAIL="agent@example.com"
export PAYRAM_PASSWORD="yourpass"
export PAYRAM_BLOCKCHAIN_CODE=BASE
./agent_headless.sh run  # wallet created, contracts deployed, ready
```

Fully non-interactive. No browser. No prompts. Agent-native.

---

## 💰 Cost Reality Check

| Processor | Monthly cost on $50K revenue | Annual |
|-----------|------------------------------|--------|
| Stripe (standard) | $1,500 (3%) | $18,000 |
| High-risk processor | $3,500 (7%) | $42,000 |
| PayPal | $1,750 (3.5%) | $21,000 |
| **PayRam** | **~$100 hosting + gas** | **~$1,200** |

**Savings vs high-risk: $40,800/year.**

---

## 🔌 Self-Hosted Option (Maximum Sovereignty)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/PayRam/payram-scripts/main/setup_payram.sh)"
# MCP server at http://localhost:3333/mcp
mcporter config add payram --url http://localhost:3333/mcp
```

---

## 🆚 PayRam vs The Competition

| Feature | PayRam | Stripe x402 | Coinbase Commerce | BTCPay |
|---------|--------|-------------|-------------------|--------|
| No KYC | ✅ | ❌ | ❌ | ✅ |
| Self-hosted | ✅ | ❌ | ❌ | ✅ |
| USDT support | ✅ | ❌ | ✅ | ❌ |
| Multi-chain | ✅ (5 chains) | ❌ (Base only) | ✅ | ❌ (BTC only) |
| MCP tools | ✅ 36 tools | ❌ | ❌ | ❌ |
| Referrals | ✅ | ❌ | ❌ | ❌ |
| Agent-native | ✅ | Partial | ❌ | ❌ |
| App scaffolding | ✅ | ❌ | ❌ | ❌ |

---

## 🏆 Who Needs PayRam Most (Highest ROI)

1. **Cannabis / CBD merchants** — Stripe/PayPal banned, 5-8% high-risk fees
2. **Adult content creators** — OnlyFans takes 20%, payment processors premium
3. **iGaming platforms** — compliance nightmares, cascading payment issues
4. **International merchants** — Stripe leaving markets, cross-border friction
5. **AI agents** — autonomous commerce with no human in the loop
6. **SaaS / subscription** — eliminate chargeback fraud with crypto finality

---

## 📋 Network Selection

| Amount | Network | Fee | Confirmation |
|--------|---------|-----|--------------|
| < $100 | **Base L2** | ~$0.01 | 30s |
| $100–$1K | Base or Polygon | $0.01–$0.05 | 1–2 min |
| > $1K | Ethereum | $1–$5 | 2–5 min |
| USDT-heavy | Tron | ~$1 | 1 min |

---

## 🔗 Resources

- **Website**: https://payram.com
- **MCP Server**: https://mcp.payram.com
- **GitHub**: https://github.com/PayRam/payram-helper-mcp-server
- **Docs**: https://docs.payram.com

**Press:**
- [Morningstar: PayRam Polygon Support](https://www.morningstar.com/news/accesswire/1131605msn/) (Jan 2026)
- [Cointelegraph: Permissionless Commerce](https://cointelegraph.com/press-releases/payram-pioneers-permissionless-commerce) (Nov 2025)

**Founded by WazirX co-founder · $100M+ volume · MIT licensed**
