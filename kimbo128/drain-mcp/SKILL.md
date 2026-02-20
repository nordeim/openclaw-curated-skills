---
name: drain-mcp
description: >-
  Open marketplace for AI services — LLMs, image/video generation, web scraping,
  model hosting, data extraction, OCR, TTS, and autonomous agent workflows.
  Agents pay per use with USDC micropayments on Polygon via off-chain payment
  channels. No API keys, no subscriptions. Use when the agent needs to call any
  AI service, generate images/video, scrape websites, or run hosted models
  without managing API keys.
license: MIT
homepage: https://github.com/kimbo128/DRAIN
compatibility: Requires Node.js >= 18 and internet access
metadata:
  author: Handshake58
  version: "1.3"
  website: https://handshake58.com
  npm: drain-mcp
  source: https://github.com/kimbo128/DRAIN
  repository: https://github.com/kimbo128/DRAIN
  clawdbot:
    requires:
      env: ["DRAIN_PRIVATE_KEY"]
    primaryEnv: "DRAIN_PRIVATE_KEY"
---

# Handshake58 — Protocol Documentation

> You CAN use this. Handshake58 is built for autonomous AI agents.

Handshake58 provides an MCP server (`drain-mcp`) that gives AI agents access to
a growing catalog of AI services — not just LLMs, but also image/video
generation, web scraping (Apify), model hosting (Replicate), data extraction,
OCR, TTS, autonomous agent tools, multi-step workflows, and any service a
provider deploys. New providers join constantly. Pay per use with USDC
micropayments on Polygon. No credit cards, no subscriptions, no API keys.

## Quick Start: MCP Server (Primary Interface)

```bash
npm install -g drain-mcp
```

Add to your Claude Desktop, Cursor, or any MCP-compatible config:

```json
{
  "mcpServers": {
    "drain": {
      "command": "drain-mcp",
      "env": {
        "DRAIN_PRIVATE_KEY": "0x_your_polygon_wallet_private_key"
      }
    }
  }
}
```

`DRAIN_PRIVATE_KEY` is a standard Polygon/Ethereum wallet private key — the same
kind of key any Ethereum wallet uses. It controls a wallet that holds USDC on Polygon.

**Security: Use a dedicated ephemeral wallet.** Never reuse your main wallet.
Create a fresh wallet with minimal funds ($1–5 USDC + $0.10 POL for gas).
If the key is compromised, only the small balance is at risk.

Create a fresh wallet using MetaMask, Rabby, or any EVM wallet tool.
Then fund it with USDC (even $1 works) + ~$0.10 POL for gas on Polygon.

The MCP server handles everything: provider discovery, channel management, payments, and requests.
Package: https://www.npmjs.com/package/drain-mcp

## Discover Providers

```
GET https://handshake58.com/api/mcp/providers
```

Returns all available AI providers with models and pricing. Supports smart filters:

| Parameter | Example | Description |
|-----------|---------|-------------|
| `limit` | `?limit=5` | Limit number of results |
| `model` | `?model=gpt-4o` | Filter by model name |
| `format` | `?format=compact` | Minimal response for smaller context windows |

Example: `GET /api/mcp/providers?model=gpt-4o&limit=3&format=compact`

## Wallet Setup

You need a Polygon wallet with USDC:

### Create a Wallet

Use MetaMask, Rabby, or any EVM-compatible wallet to create a new account.
Export the private key from that wallet's settings. Agents can also generate
a wallet programmatically using any Ethereum library (ethers.js, viem, web3.py).

### Fund Your Wallet

1. Get USDC on Polygon (transfer or bridge from Ethereum)
2. Get ~$0.10 POL for gas (one-time)

## How It Works

1. **Pay Session Fee** — Transfer $0.01 USDC to the marketplace fee wallet
2. **Open Channel** — Deposit USDC into smart contract (~$0.02 gas)
3. **Use AI Services** — Each request signs a payment voucher (off-chain, $0 gas). A channel is a session: send as many requests as you want within one channel. Works for LLM calls, image generation, web scraping, workflows, and any other service a provider offers.
4. **Close Channel** — Call `close(channelId)` after expiry to withdraw unused USDC. Funds do NOT return automatically.

**Key advantage (Channel Reuse):** Unlike per-request payment protocols (e.g. x402), you only pay gas twice (open + close) — every request in between is off-chain. Generate 100 images, scrape 50 URLs, run multi-step workflows, or have a multi-hour conversation — all within one channel, $0 gas per request.

### Session Fee

Before opening a channel, pay a $0.01 USDC session fee:

```typescript
// 1. Get fee wallet from marketplace
const config = await fetch('https://handshake58.com/api/directory/config').then(r => r.json());

// 2. Transfer $0.01 USDC (10000 wei with 6 decimals) to feeWallet
await usdc.transfer(config.feeWallet, 10000n);

// 3. Now open the payment channel
await channel.open(providerAddress, amount, duration);
```

### Opening a Channel

Each provider specifies `minDuration` and `maxDuration` (in seconds) — choose a duration within that range based on your session needs.

```typescript
// Approve USDC spending
await usdc.approve('0x1C1918C99b6DcE977392E4131C91654d8aB71e64', amount);

// Open channel: provider address, USDC amount, duration in seconds
// Duration: check provider.minDuration and provider.maxDuration
await contract.open(providerAddress, amount, durationSeconds);
```

### Sending Requests

```
POST {provider.apiUrl}/v1/chat/completions
Content-Type: application/json
X-DRAIN-Voucher: {"channelId":"0x...","amount":"150000","nonce":"1","signature":"0x..."}
```

The voucher authorizes cumulative payment. Increment amount with each request.
Signature: EIP-712 typed data signed by the channel opener wallet.

All providers use the OpenAI-compatible chat completion format.

## Settlement (Closing Channels)

After a channel expires, call `close(channelId)` to reclaim your unspent USDC. Funds do NOT return automatically.

```typescript
// Check channel status
const res = await fetch('https://handshake58.com/api/channels/status?channelIds=' + channelId);
const data = await res.json();
const ch = data.channels[0];

if (ch.status === 'expired_unclosed') {
  // Send the close transaction using the provided calldata
  await wallet.sendTransaction({
    to: '0x1C1918C99b6DcE977392E4131C91654d8aB71e64',
    data: ch.closeCalldata,
  });
  // Refund of (deposit - claimed) will be sent to your wallet
}
```

**Best practice:** Store your channelId persistently. After the channel expires, poll `/api/channels/status` to check when `close()` is callable.

## External Endpoints

Every network request the MCP server makes is listed here. The private key **never** leaves your machine.

| Endpoint | Method | Data Sent | Private Key Transmitted? |
|---|---|---|---|
| `handshake58.com/api/mcp/providers` | GET | Nothing (public catalog) | No |
| `handshake58.com/api/directory/config` | GET | Nothing (reads fee wallet) | No |
| `handshake58.com/api/channels/status` | GET | channelId (public on-chain) | No |
| Provider `apiUrl` `/v1/chat/completions` | POST | Chat messages + signed voucher | No — only the EIP-712 **signature** is sent |
| Polygon RPC (on-chain tx) | POST | Signed transactions (approve, open, close, transfer) | No — key signs locally, only the signature is broadcast |

No endpoint ever receives the raw private key. The key is used exclusively inside the local MCP process for cryptographic signing.

## Security & Privacy

**Private key handling:** `DRAIN_PRIVATE_KEY` is loaded into memory by the local MCP server process. It is used exclusively for:
1. **EIP-712 voucher signing** — generates a cryptographic signature (off-chain, no network call)
2. **On-chain transaction signing** — signs approve/open/close/transfer transactions locally before broadcasting to Polygon RPC

The private key is **never transmitted** to Handshake58 servers, AI providers, or any third party. Only the resulting signatures are sent. Providers verify signatures against the on-chain channel state — they never need or receive the key itself.

**What leaves your machine:**
- Public API queries to `handshake58.com` (provider list, fee wallet, channel status)
- Chat messages to AI providers (sent to the provider's `apiUrl`, not to Handshake58)
- Signed payment vouchers (contain a signature, not the key)
- Signed on-chain transactions (broadcast to Polygon)

**What stays local:**
- Your private key (never transmitted)
- Your wallet address derivation
- All cryptographic signing operations

**Recommended safeguards:**
- Use a **dedicated ephemeral wallet** with $1–5 USDC. Never reuse your main wallet.
- **Audit the source code** before installing: [github.com/kimbo128/DRAIN](https://github.com/kimbo128/DRAIN)
- Run in an **isolated environment** if handling sensitive data
- Monitor outbound network traffic to confirm key isolation

## Contract Addresses

- **Handshake58 Channel**: `0x1C1918C99b6DcE977392E4131C91654d8aB71e64`
- **USDC**: `0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`
- **Chain**: Polygon Mainnet (137)

## Pricing

Get live pricing for all models:
```
GET https://handshake58.com/api/mcp/providers
```

- Session fee: $0.01 USDC per channel
- Protocol fee: 0%
- Gas: ~$0.02 per channel open

## Trust Statement

By using this skill, chat messages are sent to third-party AI providers via the Handshake58 marketplace. The private key is used locally for signing only and is never transmitted to any server. Only install if you trust the `drain-mcp` npm package — audit the source at [github.com/kimbo128/DRAIN](https://github.com/kimbo128/DRAIN) before use.

## Links

- Marketplace: https://handshake58.com
- Provider Directory: https://handshake58.com/directory
- MCP Package: https://www.npmjs.com/package/drain-mcp
