---
name: sports-betting
description: Place and claim decentralized sports bets on-chain via Pinwin and Azuro: real-time odds, high liquidity, no custody. Fetch prematch and live games from the data-feed, pick a selection, then sign and submit. Use when the user wants to bet on sports with Pinwin, browse games, place a bet, or check or redeem winnings.
compatibility: Requires Node, viem and @azuro-org/dictionaries (for human-readable market/selection names). Required env: BETTOR_PRIVATE_KEY (wallet private key; high-sensitivity). Optional env: POLYGON_RPC_URL (Polygon RPC); if unset, use default RPC(s) in references/polygon.md.
homepage: https://github.com/skinnynoizze/pinwin-agent
disable-model-invocation: true
metadata: {"openclaw":{"requires":{"bins":["node"],"env":["BETTOR_PRIVATE_KEY"]},"primaryEnv":"BETTOR_PRIVATE_KEY"}}
---

# Sports betting (Pinwin)

Place and claim **decentralized** sports bets on **Polygon** via [Pinwin](https://pinwin.xyz) and Azuro, with on-chain execution. The agent fetches **prematch and live** games from the data-feed, you pick a selection, then it calls Pinwin, signs (and optionally approves USDT), and submits.

**Invocation:** This skill is **invocation-only**: the assistant will not use it unless you explicitly ask (e.g. “place a bet with Pinwin”) or use the slash command. That avoids accidental bets.

---

## How to use (OpenClaw)

- **Invoke:** Use the slash command **`/sports_betting`** (or **`/skill sports-betting`**) and optionally add your request, e.g. `/sports_betting place 5 USDT on the first Premier League game` or `/sports_betting show my bets`.
- **Versatility:** The assistant should **ask you** for preferences when not specified: how many games to fetch (`first`), order (`turnover` vs `startsAt`), sport/country/league filters, and **which selection you want**. It should **not** suggest or pick a bet unless you explicitly ask for a suggestion (meaningful suggestions would require external data, e.g. news or stats, and could be a separate skill).

---

## When to use

- User wants to **place a bet** on a game (prematch or live): fetch games → choose a selection → call Pinwin `/agent/bet` → approve token if needed → sign EIP-712 → POST signature to returned `apiUrl`.
- User wants to **check bet status** (pending / resolved / won or lost) or **redeem winnings**: query the bets subgraph for the bettor’s bets (see [Check bet status](#check-bet-status-before-redeem)); when a bet has `isRedeemable && !isRedeemed`, call Pinwin `/agent/claim` with those `betIds` → sign and send the returned transaction with viem.

---

## Prerequisites

### Credentials (required env)

- **BETTOR_PRIVATE_KEY** — Wallet private key (hex) for signing bets and claim transactions. High-sensitivity; do not log or expose. Required for placing and claiming. Use a dedicated betting wallet with minimal funds; do not use your primary wallet.

### Optional

- **POLYGON_RPC_URL** — Polygon RPC endpoint. If unset, the agent uses the default RPC(s) in [references/polygon.md](references/polygon.md) (e.g. Pocket Network, PublicNode).

### Other

- **@azuro-org/dictionaries** — required. The subgraph returns only `outcomeId` and odds; this package is the only way to map them to human-readable market and selection names (e.g. "Total Goals", "Over (2.5)"). See [references/dictionaries.md](references/dictionaries.md).
- **Addresses:** relayer, bet token, native gas token (POL), data-feed URL, and bets subgraph URL are in [references/polygon.md](references/polygon.md).
- **Balances:** The agent can use viem to check **POL** (gas) and **USDT** (stake + relayer fee) before placing a bet; if insufficient, inform the user and do not proceed. See [references/viem.md](references/viem.md).

---

## Flow (place a bet)

0. **Optional — check balances:** Use viem to read **POL** (`getBalance(bettor)`) and **USDT** (`balanceOf(bettor)` on bet token). For a **rough pre-check**, ensure USDT ≥ stake and enough POL for gas; the exact USDT required is stake + relayer fee, but **relayerFeeAmount** comes from the decoded Pinwin payload (after calling `/agent/bet`). So either: (a) require USDT ≥ stake (and POL for gas) as a conservative check, or (b) call Pinwin first, decode the payload, then require USDT ≥ stake + payload’s relayerFeeAmount before approving or signing. If insufficient, inform the user and stop. See [references/viem.md](references/viem.md).
1. **Fetch games** – POST a GraphQL query to the Azuro data-feed. URL, query, and variables: [references/subgraph.md](references/subgraph.md). Use `state: "Prematch"` or `"Live"`; get `gameId`, `title`, `startsAt`, `participants`, `conditions` (with `conditionId`, `outcomes` with `outcomeId`, `currentOdds`). Respect user preferences for `first`, `orderBy` / `orderDirection`, and optional filters (sport, country, league); if not specified, ask or use defaults (e.g. `first: 20`, `orderBy: turnover`, `orderDirection: desc`). Use **@azuro-org/dictionaries** to map `outcomeId` to market/selection names; use `getSelectionName({ outcomeId, withPoint: true })` so lines (e.g. Over 2.5) are shown: [references/dictionaries.md](references/dictionaries.md).
2. **Choose selection** – Pick one (or more for combo) `conditionId` + `outcomeId` from an Active condition. Use that outcome’s `currentOdds` for `minOdds`: `minOdds = Math.round(parseFloat(currentOdds) * 1e12)`.
3. **Call Pinwin** – `POST https://api.pinwin.xyz/agent/bet` with JSON body (see [references/api.md](references/api.md)). Response: `{ "encoded": "<base64>" }`. Decode: `payload = JSON.parse(atob(response.encoded))`.
4. **Explain to user (before signing)** – **Display all decoded payload data** (for transparency): amount, selections (with human-readable names from the data-feed and [references/dictionaries.md](references/dictionaries.md)), relayerFeeAmount, apiUrl, environment, and all clientData fields (affiliate, core, expiresAt, chainId, attention, isFeeSponsored, isBetSponsored, isSponsoredBetReturnable). Use paths from [references/api.md](references/api.md): single bet = `signableClientBetData.bet`; combo = `signableClientBetData.bets` and top-level amount/minOdds/nonce. Then **explain in human-readable terms**: stake in USDT, selection/market names, relayer fee, and that this is the bet they are authorising. Do this before approval or signing.
5. **Approval (if needed)** – Check bet token’s `allowance(bettor, relayer)` on Polygon. If &lt; bet amount + relayer fee + 0.2 USDT, sign `approve(relayer, bet amount + relayer fee + 0.2 USDT)` on the bet token. Approval is bounded to this bet plus a small buffer for security; the agent may need to approve again for the next bet. Addresses: [references/polygon.md](references/polygon.md). Steps: [references/viem.md](references/viem.md).
6. **Verify payload vs user intent** – Before signing: (a) Confirm that the decoded payload’s amount matches the user’s requested stake and that the payload’s selections (conditionId/outcomeId or combo bets) match the user’s chosen selection(s). (b) Verify that the payload’s **clientData.core** (from `signableClientBetData` or `apiClientBetData`) equals the documented **claimContract** (ClientCore) for Polygon in [references/polygon.md](references/polygon.md); if not, do not sign and report the mismatch. (c) Use only the **relayer** address from [references/polygon.md](references/polygon.md) for allowance and approve—do not use any relayer from the payload. If amount or selections do not match, do not sign; inform the user that the API payload does not match their request and stop.
7. **Sign and submit** – Use viem `signTypedData` with `payload.domain`, `payload.types`, `primaryType` (see [references/api.md](references/api.md)), and `message: payload.signableClientBetData`. Then POST to `payload.apiUrl` with `environment`, `bettor`, `betOwner`, `clientBetData` (= `payload.apiClientBetData`), `bettorSignature`. The **order id is in the POST response**: use `response.id`. If you get an order id, poll until the order settles (see [references/api.md](references/api.md)): GET `{apiBase}/bet/orders/{orderId}`. Success = response has `txHash`; failure = `state` is `Rejected` or `Canceled` (use `errorMessage`).

---

## Check bet status (before redeem)

To know when a bet is **resolved** and whether it **won** or **lost**, and whether the user can **redeem**, query the **bets subgraph** (different from the data-feed). See [references/bets-subgraph.md](references/bets-subgraph.md).

1. **Query bets** – POST a GraphQL query to the bets subgraph URL (Polygon: in [references/polygon.md](references/polygon.md)). Query `v3Bets` with `where: { bettor: "<bettor address>" }` (address in lowercase). To fetch only bets that can be claimed, add **`isRedeemable: true`** to the where clause (see [references/bets-subgraph.md](references/bets-subgraph.md)). Request at least: `betId`, `status`, `result`, `isRedeemable`, `isRedeemed`, `amount`, `payout`.
2. **Interpret** – **status** = `Accepted` (pending) | `Resolved` (settled) | `Canceled`. When **status === Resolved**, **result** = `Won` or `Lost`. When **isRedeemable === true** and **isRedeemed === false**, the user can claim; collect those bets’ **betId** values for the claim flow.

---

## Flow (claim)

Only for bets that are resolved (or canceled) and have **isRedeemable** true and **isRedeemed** false; get **betIds** from the bets subgraph (see [Check bet status](#check-bet-status-before-redeem)).

1. **Call Pinwin** – `POST https://api.pinwin.xyz/agent/claim` with `betIds` (array of on-chain bet ids) and `chain: "polygon"`. Decode the response `encoded` payload. **Explain to the user in human-readable terms** what they are sending: e.g. claiming winnings for bet IDs X, Y; the transaction will go to the Azuro ClientCore contract on Polygon; no value (ETH/POL) is sent. Display the **full** decoded claim payload (to, chainId, value, and any other keys returned) for transparency.
2. **Verify claim contract** – Ensure `payload.to` (lowercase) equals the documented **claimContract** (ClientCore) for Polygon in [references/polygon.md](references/polygon.md). This is the redeem contract for won/canceled bets, not the Cashout (early-exit) contract. If it does not match, do not send the tx and report the mismatch.
3. **Send tx** – Use viem `sendTransaction` with `{ to: payload.to, data: payload.data, value: 0n, chainId: payload.chainId }`. Wait for receipt. Details: [references/viem.md](references/viem.md).

---

## Example (place a single bet)

After fetching games and choosing one outcome:

```json
POST https://api.pinwin.xyz/agent/bet
{ "amount": 1000000, "minOdds": 1500000000000, "chain": "polygon", "selections": [{ "conditionId": "<from data-feed>", "outcomeId": 21 }] }
```

Decode `response.encoded`, sign `payload.signableClientBetData` with viem `signTypedData`, then POST to `payload.apiUrl` with `clientBetData` and `bettorSignature`.

## Example (claim)

Get **betIds** from the bets subgraph (e.g. query with `isRedeemable: true`). Then:

```json
POST https://api.pinwin.xyz/agent/claim
{ "betIds": [215843], "chain": "polygon" }
```

Decode `response.encoded` → `payload`. Display payload to the user; verify `payload.to` equals the claimContract (ClientCore) in [references/polygon.md](references/polygon.md). Then send tx with viem: `sendTransaction({ to: payload.to, data: payload.data, value: 0n, chainId: payload.chainId })`. Wait for receipt.

---

## Tools

| Step | Tool | Purpose |
|------|------|---------|
| Games | Data-feed subgraph (GraphQL) | Get games, conditions, outcomes, odds |
| Bet status | Bets subgraph (GraphQL) | Get bettor’s bets: status (Accepted/Resolved/Canceled), result (Won/Lost), isRedeemable, betId |
| Names | @azuro-org/dictionaries (required) | Map outcomeId → human-readable market/selection names; only way to get labels from subgraph data. |
| Bet/claim | Pinwin API | Get encoded payload and apiUrl |
| Chain | viem + RPC | getBalance (POL), readContract (allowance, balanceOf USDT), sendTransaction (approve, claim), signTypedData (bet) |

**Required packages:** `npm install viem @azuro-org/dictionaries`. Setup and chain calls: [references/viem.md](references/viem.md). Dictionaries usage: [references/dictionaries.md](references/dictionaries.md).

---

## Errors

- **Pinwin 4xx/5xx:** read `error` or `message` in the response body.
- **Subgraph:** check both HTTP status and `data.errors` in the JSON body (GraphQL can return 200 with `data.errors`).
- **Chain:** tx reverted, insufficient funds — report tx hash.

---

## Reference files

Load these when you need full request/response shapes, queries, or addresses:

- [references/api.md](references/api.md) – Pinwin POST /agent/bet and /agent/claim (request, response, decoded payload).
- [references/subgraph.md](references/subgraph.md) – Data-feed URL, canonical GraphQL query, example variables, filtering, response shape.
- [references/bets-subgraph.md](references/bets-subgraph.md) – Bets subgraph URL, query for bettor’s bets, status/result/isRedeemable, betId for claim.
- [references/dictionaries.md](references/dictionaries.md) – @azuro-org/dictionaries (getMarketName, getSelectionName; use withPoint: true for selection lines).
- [references/polygon.md](references/polygon.md) – Polygon data-feed URL, bets subgraph URL, native gas token (POL), relayer, betToken (USDT), environment.
- [references/viem.md](references/viem.md) – viem install, setup, getBalance (POL), balanceOf (USDT), allowance, approve, signTypedData, claim tx.
