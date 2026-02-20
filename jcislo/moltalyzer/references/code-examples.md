# Moltalyzer Code Examples

## TypeScript Setup

```typescript
import { x402Client, wrapFetchWithPayment } from "@x402/fetch";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const key = process.env.EVM_PRIVATE_KEY
  || process.env.PRIVATE_KEY
  || process.env.BLOCKRUN_WALLET_KEY
  || process.env.WALLET_PRIVATE_KEY;

const signer = privateKeyToAccount(key as `0x${string}`);
const client = new x402Client();
registerExactEvmScheme(client, { signer });
const fetchWithPayment = wrapFetchWithPayment(fetch, client);
```

## Fetch Moltbook Digest

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/moltbook/digests/latest");
const { data } = await res.json();
console.log(data.title);            // "Agent Mesh Steals the Spotlight"
console.log(data.emergingNarratives); // ["decentralized identity", ...]
console.log(data.hotDiscussions);     // [{ topic, sentiment, description }]
```

## Fetch GitHub Digest

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/github/digests/latest");
const { data } = await res.json();
console.log(data.notableProjects);  // [{ name, stars, language, description }]
console.log(data.emergingTools);    // ["CamoFox: anti-detection browser MCP server"]
```

## Fetch Polymarket Signals

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/polymarket/latest");
const { data: { digest, signals } } = await res.json();
console.log(`${digest.totalSignals} signals (${digest.highConfidence} high confidence)`);
const highConf = signals.filter(s => s.confidence === "high");
```

## Free Samples (No Payment Required)

Test with plain `fetch` — no x402 setup needed:

```typescript
// Moltbook sample (18+ hours old, rate limited to 1/20min)
const moltbook = await fetch("https://api.moltalyzer.xyz/api/moltbook/sample");

// GitHub sample (static snapshot)
const github = await fetch("https://api.moltalyzer.xyz/api/github/sample");

// Polymarket sample (static snapshot)
const polymarket = await fetch("https://api.moltalyzer.xyz/api/polymarket/sample");
```

## Error Handling

```typescript
const res = await fetchWithPayment("https://api.moltalyzer.xyz/api/moltbook/digests/latest");

if (res.status === 402) {
  // Payment failed — check wallet has USDC on Base Mainnet
  // The response body contains pricing and setup instructions
  const info = await res.json();
  console.error("Payment required:", info.price, info.network);
}

if (res.status === 429) {
  // Rate limited — respect Retry-After header
  const retryAfter = res.headers.get("Retry-After");
  console.error(`Rate limited. Retry after ${retryAfter} seconds.`);
}

if (res.status === 404) {
  // No data available yet (e.g., no digests generated)
}
```

## Rate Limit Headers

All responses include:
- `RateLimit-Limit` — max requests per window
- `RateLimit-Remaining` — remaining requests
- `RateLimit-Reset` — seconds until window resets
- `Retry-After` — seconds to wait (only on 429)
