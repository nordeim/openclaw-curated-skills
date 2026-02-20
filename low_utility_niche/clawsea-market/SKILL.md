---
name: clawsea-market
description: "Non-custodial automation skill for ClawSea (Base-only NFT marketplace). Use when an agent/bot needs to browse ClawSea data (trending collections, collection items, listings, buy-now sets), and/or autonomously list, buy, and cancel Seaport orders on Base using the bot's own wallet. Triggers on: make my bot trade; autonomous listing/buying; buy floor; list my NFT; cancel listing; poll listings; Seaport order signing; ClawSea API."
---

# ClawSea NFT Marketplace — Built for humans. Optimized for agents.

Enable an agent to use **ClawSea** autonomously:
- Read marketplace data from `https://clawsea.io/api/*`
- Create/cancel listings and buy NFTs on **Base mainnet** using the agent’s **own wallet** (non-custodial)

## Required environment variables

- `CLAWSEA_BASE_URL` (optional)
  - Default: `https://clawsea.io`
  - Use to point bots at staging.

- `BASE_RPC_URL` (required for onchain actions)
  - Base RPC endpoint used for reads + broadcasting txs.

- `BOT_WALLET_PRIVATE_KEY` (required for autonomous trading)
  - The bot wallet private key used to sign messages and transactions.
  - Never commit. Store as a secret.

## Core workflows

### 1) Browse / discover

All endpoints are **GET** unless noted. Prefer the “cells” endpoint for browsing.

**Endpoints (safe defaults):**

- Trending collections (recommended):
  - `GET /api/explore/cells`

- Trending raw (ranking feed):
  - `GET /api/explore/trending`

- Collection items (pagination):
  - `GET /api/collection/nfts?contract=0x...`

- NFT listings:
  - `GET /api/orders?contract=0x...&tokenId=...`

- Buy-now (listed) tokens in a collection (sorted):
  - `GET /api/orders/listed?contract=0x...`

**Optional query params (clamped server-side):**

- `/api/explore/cells`
  - `limit` (default 20)

- `/api/explore/trending`
  - `limit` (default 20)

- `/api/collection/nfts`
  - `pageKey` (optional)
  - `pageSize` (default 24)

- `/api/orders/listed`
  - `sort=price|newest` (default `price`)
  - `offset` (default 0)
  - `limit` (default 48)

**Fair-use guidance (important):**

- Cache responses briefly and avoid aggressive polling.
- If you receive HTTP `429`, back off and retry later.

### 2) List an NFT (Seaport)

High-level steps:
1. Ensure the bot owns the NFT and is on Base.
2. Approve the **OpenSea conduit** for the NFT contract (one-time).
3. Build fixed-price Seaport order parameters (Base Seaport + conduitKey).
4. Sign EIP-712 typed data with the bot wallet.
5. Publish offchain order to ClawSea:
   - `POST /api/orders` (stores orderComponents + signature + priceEth)

### 3) Buy an NFT (Seaport fulfill)

High-level steps:
1. Fetch the target order from `/api/orders`.
2. (Recommended) simulate `Seaport.validate` and `fulfillOrder` (eth_call) before spending gas.
3. Submit `fulfillOrder` onchain with `value`.
4. Best-effort mark filled:
   - `POST /api/orders/fulfill` (offchain status update)

### 4) Cancel a listing

Two layers:
- **Onchain** cancel (canonical): call Seaport `cancel([OrderComponents])`.
- **Offchain** hide (ClawSea UI): `POST /api/orders/cancel { id }`.

## Bundled resources

- `references/endpoints.md` - ClawSea HTTP endpoints and common response shapes
- `references/seaport-base.md` - Base Seaport + OpenSea conduit details
- `scripts/clawsea_bot_skeleton.mjs` - minimal Node skeleton (read-only + wiring for onchain)

Read the references before implementing autonomous buy/list logic.
