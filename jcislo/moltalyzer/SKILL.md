---
name: moltalyzer
version: 1.4.0
description: >-
  Fetch trending topics, sentiment, and narratives from Moltbook (hourly),
  discover hot new GitHub repos and emerging tools (daily), or find Polymarket
  prediction markets with insider-knowledge signals (daily). Use when you need
  community analysis, trending repos, language trends, or market intelligence.
  x402 micropayments, no API key needed.
homepage: https://moltalyzer.xyz
metadata:
  openclaw:
    emoji: "🔭"
    requires:
      env: ["EVM_PRIVATE_KEY"]
      bins: ["node"]
    primaryEnv: "EVM_PRIVATE_KEY"
    install:
      - id: npm
        kind: command
        command: "npm install @x402/fetch @x402/evm viem"
        bins: ["node"]
        label: "Install x402 payment client"
---

# Moltalyzer — AI Intelligence Feeds

Three data feeds from `https://api.moltalyzer.xyz`:

1. **Moltbook** (hourly) — trending topics, sentiment, emerging/fading narratives, hot discussions
2. **GitHub** (daily) — trending new repos, emerging tools, language trends, notable projects
3. **Polymarket** (daily) — markets where insiders may have advance knowledge, with confidence levels

## Try Free First

No setup needed. Test with plain `fetch`:

```typescript
const res = await fetch("https://api.moltalyzer.xyz/api/moltbook/sample");
const { data } = await res.json();
// data.emergingNarratives, data.hotDiscussions, data.fullDigest, etc.
```

All three feeds have free samples: `/api/moltbook/sample`, `/api/github/sample`, `/api/polymarket/sample` (rate limited to 1 req/20min each).

## Paid Endpoints

Payments are automatic via x402 — no API keys or accounts. Even $1 USDC covers 200 requests.

| Feed | Endpoint | Price |
|------|----------|-------|
| Moltbook | `GET /api/moltbook/digests/latest` | $0.005 |
| Moltbook | `GET /api/moltbook/digests?hours=N` | $0.02 |
| GitHub | `GET /api/github/digests/latest` | $0.02 |
| GitHub | `GET /api/github/digests?days=N` | $0.05 |
| GitHub | `GET /api/github/repos?limit=N` | $0.01 |
| Polymarket | `GET /api/polymarket/latest` | $0.02 |
| Polymarket | `GET /api/polymarket/all?days=N` | $0.05 |

### Quick Start (Paid)

```typescript
import { x402Client, wrapFetchWithPayment } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const signer = privateKeyToAccount(process.env.EVM_PRIVATE_KEY as `0x${string}`);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const fetchWithPayment = wrapFetchWithPayment(fetch, client);

const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/moltbook/digests/latest");
const { data } = await res.json();
```

Also supported env vars: `PRIVATE_KEY`, `BLOCKRUN_WALLET_KEY`, `WALLET_PRIVATE_KEY`.

## Error Handling

- **402** — Payment failed. Check wallet has USDC on Base Mainnet. Response body has pricing details.
- **429** — Rate limited. Respect `Retry-After` header (seconds to wait).
- **404** — No data available yet (e.g., service just started, no digests generated).

## Reference Docs

For full response schemas, see `{baseDir}/references/response-formats.md`.
For more code examples and error handling patterns, see `{baseDir}/references/code-examples.md`.
For complete endpoint tables and rate limits, see `{baseDir}/references/api-reference.md`.
