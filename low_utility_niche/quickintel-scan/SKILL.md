---
name: quickintel-scan
description: "Scan any token for security risks, honeypots, and scams using Quick Intel's contract analysis API. Use when: checking if a token is safe to buy, detecting honeypots, analyzing contract ownership and permissions, finding hidden mint/blacklist functions, or evaluating token risk before trading. Triggers: 'is this token safe', 'scan token', 'check for honeypot', 'audit contract', 'rug pull check', 'token security', 'safe to buy', 'scam check'. Supports 63 chains including Base, Ethereum, Solana, Sui, Tron. Costs $0.03 USDC per scan via x402 payment protocol. Works with any x402-compatible wallet."
---

# Quick Intel Token Security Scanner

## What You Probably Got Wrong

**This is NOT a free API.** Quick Intel uses the x402 payment protocol — you pay $0.03 USDC per scan, no API keys, no subscriptions. Your wallet signs a payment authorization, and the scan executes.

**x402 is not complicated.** You call the endpoint → get a 402 response with payment requirements → sign a payment → retry with the payment header → get your scan results. Most wallet libraries handle this automatically.

**63 chains supported.** Not just EVM — Solana, Sui, Radix, Tron, and Injective are supported too. If you're checking a token, Quick Intel probably supports that chain.

## Overview

| Detail | Value |
|--------|-------|
| **Endpoint** | `POST https://x402.quickintel.io/v1/scan/full` |
| **Cost** | $0.03 USDC (30000 atomic units) |
| **Payment Networks** | Base, Ethereum, Arbitrum, Optimism, Polygon, Avalanche, Unichain, Linea, MegaETH, **Solana** |
| **Payment Token** | USDC (native Circle USDC on each chain) |
| **Protocol** | x402 v2 (HTTP 402 Payment Required) |
| **Idempotency** | Supported via `payment-identifier` extension |

## Supported Chains (63)

| Chain | Chain | Chain | Chain |
|-------|-------|-------|-------|
| eth | arbitrum | bsc | opbnb |
| base | core | linea | pulse |
| zksync | shibarium | maxx | polygon |
| scroll | polygonzkevm | fantom | avalanche |
| bitrock | loop | besc | kava |
| metis | astar | oasis | iotex |
| conflux | canto | energi | velas |
| grove | mantle | lightlink | optimism |
| klaytn | solana | radix | sui |
| injective | manta | zeta | blast |
| zora | inevm | degen | mode |
| viction | nahmii | real | xlayer |
| tron | worldchain | apechain | morph |
| ink | sonic | soneium | abstract |
| berachain | unichain | hyperevm | plasma |
| monad | megaeth | | |

**Note:** Use exact chain names as shown (e.g., `"eth"` not `"ethereum"`, `"bsc"` not `"binance"`).

## Pre-Flight Checks

Before calling the API, verify:

### 1. USDC Balance on a Supported Payment Chain

You need at least $0.03 USDC on any supported payment chain. Base is recommended for EVM (lowest fees), Solana is also supported.

**Check balance (viem):**
```javascript
const balance = await publicClient.readContract({
  address: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913", // USDC on Base
  abi: erc20Abi,
  functionName: "balanceOf",
  args: [walletAddress],
});
const hasEnough = balance >= 30000n; // $0.03 with 6 decimals
```

**Check balance (ethers.js):**
```javascript
const USDC_BASE = "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913";
const balance = await usdcContract.balanceOf(walletAddress);
const hasEnough = balance >= 30000n; // $0.03 with 6 decimals
```

### 2. Valid Token Address

- EVM: 42-character hex address starting with `0x`
- Solana: Base58 encoded address (32-44 characters)

## How x402 Payment Works

x402 is an HTTP-native payment protocol. Here's the complete flow:

### EVM Payment Flow (Base, Ethereum, Arbitrum, etc.)

```
┌─────────────────────────────────────────────────────────────┐
│  1. REQUEST    POST to endpoint with scan parameters        │
│                                                             │
│  2. 402        Server returns "Payment Required"            │
│                PAYMENT-REQUIRED header contains payment info │
│                                                             │
│  3. SIGN       Your wallet signs EIP-3009 authorization     │
│                (transferWithAuthorization for USDC)          │
│                                                             │
│  4. RETRY      Resend request with PAYMENT-SIGNATURE header │
│                Contains base64-encoded signed payment proof  │
│                                                             │
│  5. SETTLE     Server verifies signature, settles on-chain  │
│                                                             │
│  6. RESPONSE   Server returns scan results (200 OK)         │
│                PAYMENT-RESPONSE header contains tx receipt   │
└─────────────────────────────────────────────────────────────┘
```

### Solana (SVM) Payment Flow

```
┌─────────────────────────────────────────────────────────────┐
│  1. REQUEST    POST to endpoint with scan parameters        │
│                                                             │
│  2. 402        Server returns "Payment Required"            │
│                Solana entry includes extra.feePayer address  │
│                                                             │
│  3. BUILD      Build SPL TransferChecked transaction:       │
│                - Set feePayer to gateway's facilitator       │
│                - Transfer USDC to gateway's payTo address    │
│                - Partially sign with your wallet             │
│                                                             │
│  4. RETRY      Resend request with PAYMENT-SIGNATURE header │
│                payload: { transaction: "<base64>" }          │
│                                                             │
│  5. SETTLE     Gateway co-signs as feePayer, submits to     │
│                Solana, confirms transaction                  │
│                                                             │
│  6. RESPONSE   Server returns scan results (200 OK)         │
│                PAYMENT-RESPONSE header contains tx signature │
└─────────────────────────────────────────────────────────────┘
```

### x402 v2 Headers

| Header | Direction | Description |
|--------|-----------|-------------|
| `PAYMENT-REQUIRED` | Response (402) | Base64 JSON with payment requirements and accepted networks |
| `PAYMENT-SIGNATURE` | Request (retry) | Base64 JSON with signed EIP-3009 authorization (EVM) or partially-signed transaction (SVM) |
| `PAYMENT-RESPONSE` | Response (200) | Base64 JSON with settlement tx hash/signature and block number |

**Note:** The legacy `X-PAYMENT` header is also accepted for v1 backward compatibility, but `PAYMENT-SIGNATURE` is preferred.

### Payment-Identifier (Idempotency)

The gateway supports the `payment-identifier` extension. If your agent might retry requests (network failures, timeouts), include a unique payment ID in the payload extensions to avoid paying twice:

```javascript
const paymentPayload = {
  // ... standard payment fields ...
  extensions: {
    'payment-identifier': {
      paymentId: 'pay_' + crypto.randomUUID().replace(/-/g, '')
    }
  }
};
```

If the gateway has already processed a request with the same payment ID, it returns the cached response without charging again. Payment IDs must be 16-128 characters, alphanumeric with hyphens and underscores.

### Discovery Endpoint

Query the gateway's accepted payments and schemas before making calls:

```
GET https://x402.quickintel.io/accepted
```

Returns all routes, supported payment networks, pricing, and input/output schemas for agent integration.

## Wallet Integration Patterns

### Pattern 1: Local EVM Wallet (Private Key)

Using `@x402/fetch` (recommended):

```javascript
import { x402Fetch } from '@x402/fetch';
import { createWallet } from '@x402/evm';

const wallet = createWallet(process.env.PRIVATE_KEY);

const response = await x402Fetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chain: 'base',
    tokenAddress: '0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00'
  }),
  wallet,
  preferredNetwork: 'eip155:8453'
});

const scanResult = await response.json();
```

### Pattern 2: Solana Wallet (SVM)

```javascript
import { createSvmClient } from '@x402/svm/client';
import { toClientSvmSigner } from '@x402/svm';
import { wrapFetchWithPayment } from '@x402/fetch';
import { createKeyPairSignerFromBytes } from '@solana/kit';
import { base58 } from '@scure/base';

// Create Solana signer
const keypair = await createKeyPairSignerFromBytes(
  base58.decode(process.env.SOLANA_PRIVATE_KEY)
);
const signer = toClientSvmSigner(keypair);
const client = createSvmClient({ signer });
const paidFetch = wrapFetchWithPayment(fetch, client);

// Call scan API (x402 payment via Solana USDC)
const response = await paidFetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    chain: 'base',
    tokenAddress: '0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00'
  })
});

const scanResult = await response.json();
```

### Pattern 3: AgentWallet (frames.ag)

AgentWallet handles the entire x402 flow in one call:

```javascript
const response = await fetch('https://frames.ag/api/wallets/{username}/actions/x402/fetch', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${AGENTWALLET_API_TOKEN}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    url: 'https://x402.quickintel.io/v1/scan/full',
    method: 'POST',
    body: {
      chain: 'base',
      tokenAddress: '0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00'
    }
  })
});

const scanResult = await response.json();
```

### Pattern 4: Vincent Wallet (heyvincent.ai)

```javascript
// Vincent handles x402 via its transaction signing API
const paymentAuth = await vincent.signPayment({
  network: 'eip155:8453',
  amount: '30000',
  token: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913',
  recipient: recipientFromHeader
});

// Then retry with the signed payment
const response = await fetch('https://x402.quickintel.io/v1/scan/full', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'PAYMENT-SIGNATURE': paymentAuth.encoded
  },
  body: JSON.stringify({ chain: 'base', tokenAddress: '0x...' })
});
```

### Pattern 5: Any EIP-3009 Compatible Wallet

If your wallet supports signing EIP-712 typed data:

```javascript
// 1. Call endpoint, get 402 response
// 2. Parse PAYMENT-REQUIRED header
// 3. Sign EIP-3009 transferWithAuthorization
const signature = await wallet.signTypedData({
  domain: {
    name: 'USD Coin',
    version: '2',
    chainId: 8453,
    verifyingContract: '0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913'
  },
  types: {
    TransferWithAuthorization: [
      { name: 'from', type: 'address' },
      { name: 'to', type: 'address' },
      { name: 'value', type: 'uint256' },
      { name: 'validAfter', type: 'uint256' },
      { name: 'validBefore', type: 'uint256' },
      { name: 'nonce', type: 'bytes32' }
    ]
  },
  primaryType: 'TransferWithAuthorization',
  message: { from, to, value: 30000n, validAfter: 0, validBefore, nonce }
});
// 4. Retry with PAYMENT-SIGNATURE header (base64-encoded payload)
```

## API Request

```http
POST https://x402.quickintel.io/v1/scan/full
Content-Type: application/json

{
  "chain": "base",
  "tokenAddress": "0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chain` | string | Yes | Lowercase chain name (see supported chains) |
| `tokenAddress` | string | Yes | Token contract address |

## API Response

The scan returns comprehensive security analysis:

```json
{
  "tokenDetails": {
    "tokenName": "Ribbita by Virtuals",
    "tokenSymbol": "TIBBIR",
    "tokenDecimals": 18,
    "tokenSupply": 1000000000,
    "tokenCreatedDate": 1736641803000
  },
  "tokenDynamicDetails": {
    "is_Honeypot": false,
    "buy_Tax": "0.0",
    "sell_Tax": "0.0",
    "transfer_Tax": "0.0",
    "has_Trading_Cooldown": false,
    "liquidity": false
  },
  "isScam": null,
  "isAirdropPhishingScam": false,
  "contractVerified": true,
  "quickiAudit": {
    "contract_Renounced": true,
    "hidden_Owner": false,
    "is_Proxy": false,
    "can_Mint": false,
    "can_Blacklist": false,
    "can_Update_Fees": false,
    "can_Pause_Trading": false,
    "has_Suspicious_Functions": false,
    "has_Scams": false
  }
}
```

### Key Fields to Check

#### Immediate Red Flags (DO NOT BUY)

| Field | Bad Value | Meaning |
|-------|-----------|---------|
| `is_Honeypot` | `true` | Cannot sell — funds trapped |
| `isScam` | `true` | Known scam contract |
| `isAirdropPhishingScam` | `true` | Phishing attempt |
| `has_Scams` | `true` | Contains scam patterns |
| `can_Potentially_Steal_Funds` | `true` | Has theft mechanisms |

#### High Risk Warnings

| Field | Risky Value | Meaning |
|-------|-------------|---------|
| `buy_Tax` / `sell_Tax` | `> 10` | High tax reduces profits |
| `can_Mint` | `true` | Owner can inflate supply |
| `can_Blacklist` | `true` | Owner can block your wallet |
| `can_Pause_Trading` | `true` | Owner can freeze trading |
| `hidden_Owner` | `true` | Ownership obscured |
| `contract_Renounced` | `false` | Owner retains control |

#### Positive Signals

| Field | Good Value | Meaning |
|-------|------------|---------|
| `contract_Renounced` | `true` | No owner control |
| `contractVerified` | `true` | Source code public |
| `is_Launchpad_Contract` | `true` | From known launchpad |
| `can_Mint` | `false` | Fixed supply |
| `can_Blacklist` | `false` | No blocking capability |

### Interpreting Results

**Safe to trade (all must be true):**
- `is_Honeypot` = false
- `isScam` = null or false
- `has_Scams` = false
- `buy_Tax` and `sell_Tax` < 10%
- No `has_Suspicious_Functions`

**Proceed with caution:**
- `contract_Renounced` = false (owner can still act)
- `can_Update_Fees` = true (taxes could increase)
- `is_Proxy` = true (code can change)

**Do not trade:**
- `is_Honeypot` = true
- `isScam` = true
- `can_Potentially_Steal_Funds` = true
- `buy_Tax` or `sell_Tax` > 50%

## Complete Example

```javascript
import { x402Fetch } from '@x402/fetch';
import { createWallet } from '@x402/evm';

async function scanToken(chain, tokenAddress) {
  const wallet = createWallet(process.env.PRIVATE_KEY);

  // Pre-flight: Check USDC balance
  const balance = await checkUSDCBalance(wallet.address);
  if (balance < 30000n) {
    throw new Error('Insufficient USDC on Base. Need at least $0.03');
  }

  // Scan token (x402 payment handled automatically by x402Fetch)
  const response = await x402Fetch('https://x402.quickintel.io/v1/scan/full', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chain, tokenAddress }),
    wallet,
    preferredNetwork: 'eip155:8453'
  });

  if (!response.ok) {
    throw new Error(`Scan failed: ${response.status}`);
  }

  const result = await response.json();

  // Analyze results
  const analysis = {
    token: result.tokenDetails.tokenName,
    symbol: result.tokenDetails.tokenSymbol,
    safe: !result.tokenDynamicDetails.is_Honeypot &&
          !result.isScam &&
          !result.quickiAudit.has_Scams,
    risks: []
  };

  if (result.tokenDynamicDetails.is_Honeypot) {
    analysis.risks.push('HONEYPOT - Cannot sell');
  }
  if (result.quickiAudit.can_Mint) {
    analysis.risks.push('Owner can mint new tokens');
  }
  if (result.quickiAudit.can_Blacklist) {
    analysis.risks.push('Owner can blacklist wallets');
  }
  if (!result.quickiAudit.contract_Renounced) {
    analysis.risks.push('Contract not renounced');
  }
  if (parseFloat(result.tokenDynamicDetails.buy_Tax) > 5) {
    analysis.risks.push(`High buy tax: ${result.tokenDynamicDetails.buy_Tax}%`);
  }
  if (parseFloat(result.tokenDynamicDetails.sell_Tax) > 5) {
    analysis.risks.push(`High sell tax: ${result.tokenDynamicDetails.sell_Tax}%`);
  }

  return analysis;
}

// Usage
const result = await scanToken('base', '0xa4a2e2ca3fbfe21aed83471d28b6f65a233c6e00');
console.log(result);
// {
//   token: "Ribbita by Virtuals",
//   symbol: "TIBBIR",
//   safe: true,
//   risks: ["Contract not renounced"]
// }
```

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| `402 Payment Required` | No payment header | Sign and include PAYMENT-SIGNATURE header |
| `402 Payment verification failed` | Invalid signature or insufficient USDC | Check balance and signature |
| `402 Nonce already used` | Replay detected or retry without payment-identifier | Use payment-identifier for safe retries |
| `400 Invalid Chain` | Unknown chain name | Check supported chains list |
| `400 Invalid Address` | Malformed address | Verify address format |
| `404 Token Not Found` | Token doesn't exist | Check address and chain |
| `500 Scan Failed` | Contract analysis error | Retry or contact support |

## Important Notes

- **Payment is charged regardless of outcome.** Even if the scan returns limited data (unverified contract, new token), you still pay $0.03. Use `payment-identifier` to safely retry without being charged twice.
- **Scan results are point-in-time.** A safe token today could be rugged tomorrow if not renounced.
- **Not financial advice.** Quick Intel provides data, not recommendations.
- **Solana tokens** use different analysis than EVM — some fields may be null.
- **Multi-chain payment:** You can pay on any supported chain — 9 EVM chains (Base, Ethereum, Arbitrum, Optimism, Polygon, Avalanche, Unichain, Linea, MegaETH) plus Solana. The 402 response lists all accepted networks.
- **Solana payment:** Pay with USDC on Solana using the SVM payment flow. The 402 response includes the `extra.feePayer` address needed to build the transaction.

## Cross-Reference

For trading tokens after scanning, see the **tator-trade** skill which provides AI-powered trading with unsigned transactions.

## Resources

- **Quick Intel Docs:** https://docs.quickintel.io
- **x402 Protocol:** https://www.x402.org
- **Gateway Discovery:** https://x402.quickintel.io/accepted
- **Support:** https://t.me/quicki