---
name: sigil-security
description: Secure AI agent wallets via Sigil Protocol. Use when you need to deploy a smart wallet, send transactions through the Guardian, manage spending policies, create session keys, freeze/unfreeze accounts, manage recovery, or check wallet status. Covers all chains: Avalanche, Base, Arbitrum, Polygon, 0G.
homepage: https://sigil.codes
source: https://github.com/Arven-Digital/sigil-public
metadata:
  openclaw:
    primaryEnv: SIGIL_API_KEY
    emoji: "🛡️"
    requires:
      env:
        - SIGIL_API_KEY
        - SIGIL_ACCOUNT_ADDRESS
---

# Sigil Protocol — Agent Wallet Skill

Secure smart wallets for AI agents on 5 EVM chains. 3-layer Guardian evaluates every transaction before co-signing.

**API Base:** `https://api.sigil.codes/v1`
**Dashboard:** `https://sigil.codes`
**Chains:** Avalanche (43114), Base (8453), Arbitrum (42161), Polygon (137), 0G Mainnet (16661)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SIGIL_API_KEY` | ✅ Yes | Agent API key from Sigil dashboard (starts with `sgil_`). Generate at https://sigil.codes/dashboard/agent-access |
| `SIGIL_ACCOUNT_ADDRESS` | ✅ Yes | Your deployed Sigil smart account address. Deploy at https://sigil.codes/onboarding |
| `SIGIL_API_URL` | No | API base URL (default: `https://api.sigil.codes`) |
| `SIGIL_CHAIN_ID` | No | Chain ID: 43114=Avalanche, 8453=Base, 42161=Arbitrum, 137=Polygon, 16661=0G (default: `43114`) |

## ⚠️ How It Works (Read This First)

Sigil has **3 addresses** — don't confuse them:
- **Owner wallet** — your MetaMask/EOA, controls settings (human only)
- **Sigil smart account** — on-chain vault that holds funds and executes transactions
- **Agent key** — API authentication credential, NOT a wallet

> **💰 FUND THE SIGIL ACCOUNT, NOT THE AGENT KEY.**
> The agent authenticates via API key → calls `/v1/execute` → server builds, signs, and submits the transaction. The Sigil account executes with its own funds.

[Full setup guide →](references/agent-setup-guide.md)

## Installation (OpenClaw / ClawdBot)

Add the skill to your agent config. **The `env` field MUST be a flat key-value object, NOT an array.**

✅ **Correct format** (in `openclaw.json` under your agent's `skills`):
```json
{
  "name": "sigil-security",
  "env": {
    "SIGIL_API_KEY": "sgil_your_key_here",
    "SIGIL_ACCOUNT_ADDRESS": "0xYourSigilAccount"
  }
}
```

❌ **WRONG format** (will crash the gateway):
```json
{
  "name": "sigil-security",
  "env": [
    { "name": "SIGIL_API_KEY", "value": "sgil_..." }
  ]
}
```

### Steps:
1. Deploy a Sigil account at https://sigil.codes/onboarding
2. Generate an API key at https://sigil.codes/dashboard/agent-access
3. Add the skill config above to your agent in `openclaw.json`
4. Restart the gateway

## Security & Key Scoping

**SIGIL_API_KEY is NOT an owner key.** It is an agent-scoped key that authenticates the agent to the Guardian API. Here's the permission model:

| Action | Agent Key | Owner (SIWE) | Session Key |
|--------|-----------|--------------|-------------|
| Execute (sign + submit) | ✅ | ✅ | ❌ |
| Evaluate transactions | ✅ | ✅ | ✅ |
| Check wallet status | ✅ | ✅ | ✅ |
| View audit logs | ✅ | ✅ | ❌ |
| Update policy | ❌ | ✅ | ❌ |
| Freeze account | ❌ | ✅ | ❌ |
| Rotate keys | ❌ | ✅ | ❌ |
| Emergency withdraw | ❌ | ✅ (on-chain only) | ❌ |
| Add/remove recovery guardians | ❌ | ✅ | ❌ |

**Key principles:**
- The agent key **cannot** freeze, withdraw, rotate keys, or change policy — those are owner-only (require SIWE wallet signature)
- The agent key **can** submit transactions for Guardian evaluation and receive co-signatures
- **Session keys** (recommended) are even more restricted: time-limited, spend-capped, target-whitelisted, and auto-expire
- The Guardian **validates but never initiates** — it cannot move funds or act alone
- Emergency withdraw is an **on-chain owner-only function** — no API key can trigger it

**Best practice:** Use session keys for everyday agent operations. The SIGIL_API_KEY is for authentication only — the Guardian enforces all limits regardless of which key is used.

## Authentication

Two methods:

### API Key (simpler)
Owner generates a key at the dashboard's Agent Access page.

```bash
curl -X POST https://api.sigil.codes/v1/agent/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{"apiKey": "sgil_your_key_here"}'
# Returns: { "token": "eyJ..." }
```

### Delegation Signature (more secure)
Owner signs EIP-712 message delegating to the agent.

```bash
# Get signing info
GET /v1/agent/delegation-info

# Authenticate
POST /v1/agent/auth/delegation
{
  "ownerAddress": "0x...",
  "agentIdentifier": "my-agent",
  "signature": "0x...",
  "expiresAt": 1739404800,
  "nonce": "unique-string"
}
```

All requests: `Authorization: Bearer <token>` (4h TTL, re-auth with same credentials).

## First-Time Setup

### 1. Run the Setup Wizard
```
GET /v1/agent/setup/wizard
```
Returns guided questions, use-case profiles, and security tips. **Always ask the owner before deploying.**

### 2. Deploy via Dashboard
Direct the owner to `https://sigil.codes/onboarding` to:
1. Connect wallet + SIWE sign-in
2. Choose strategy template (Conservative/Moderate/Aggressive/DeFi Agent/NFT Agent)
3. Select chain
4. Generate agent key pair
5. Deploy smart account

### 3. Register (if deploying programmatically)
```bash
POST /v1/agent/wallets/register
{
  "address": "0xNewWallet",
  "chainId": 43114,
  "agentKey": "0xKey",
  "factoryTx": "0xHash"
}
```

## Daily Operations

### Check Status
```
GET /v1/agent/wallets/0xYourWallet
```
Returns: balance, policy, session keys, daily spend, guardian status, frozen state.

### Execute a Transaction (Recommended)
Non-custodial: agent signs locally, server co-signs and submits.

```bash
# 1. Build UserOp and sign with your agent private key (locally)
# 2. Submit pre-signed UserOp
POST /v1/execute
{
  "userOp": {
    "sender": "0xYourSigilAccount",
    "nonce": "0x0",
    "callData": "0x...",
    "callGasLimit": "500000",
    "verificationGasLimit": "200000",
    "preVerificationGas": "50000",
    "maxFeePerGas": "25000000000",
    "maxPriorityFeePerGas": "1500000000",
    "signature": "0xYourAgentSignature..."
  },
  "chainId": 137
}
```

Returns: `{ "txHash": "0x...", "verdict": "APPROVED", "riskScore": 12, "evaluationMs": 1450 }`

**Sigil never stores your private keys.** The agent signs locally → Guardian evaluates + co-signs → submitted on-chain. Even if our servers are breached, the attacker has zero private keys.

If rejected: `{ "verdict": "REJECTED", "rejectionReason": "...", "guidance": "..." }`

### Evaluate a Transaction (Advanced)
For agents that manage their own keys and want to handle submission themselves. Every transaction goes through the Guardian's 3-layer pipeline:
1. **L1 Deterministic** — Policy limits, whitelist, velocity checks
2. **L2 Simulation** — Dry-run, check for reverts/unexpected state changes
3. **L3 LLM Risk** — AI scores the transaction (0-100, threshold 70)

```bash
POST /v1/evaluate
{
  "userOp": {
    "sender": "0xYourAccount",
    "nonce": "0x0",
    "callData": "0x...",
    "callGasLimit": "200000",
    "verificationGasLimit": "200000",
    "preVerificationGas": "50000",
    "maxFeePerGas": "25000000000",
    "maxPriorityFeePerGas": "1500000000",
    "signature": "0x"
  }
}
```

Verdicts: `APPROVE` (with guardian signature), `REJECT` (with `guidance` explaining why + how to fix), `ESCALATE` (needs owner).

### Policy Management
```bash
# Update limits
PUT /v1/agent/wallets/:addr/policy
{ "maxTxValue": "200000000000000000", "dailyLimit": "2000000000000000000" }

# Whitelist targets
POST /v1/agent/wallets/:addr/targets
{ "targets": ["0xContract"], "allowed": true }

# Whitelist functions
POST /v1/agent/wallets/:addr/functions
{ "selectors": ["0xa9059cbb"], "allowed": true }

# Token policies (cap approvals!)
POST /v1/agent/wallets/:addr/token-policies
{ "token": "0xUSDC", "maxApproval": "1000000000", "dailyTransferLimit": "5000000000" }
```

### Session Keys
Time-limited, scope-limited keys that auto-expire. Always prefer these over the full agent key.
```bash
POST /v1/agent/wallets/:addr/session-keys
{ "key": "0xEphemeralKey", "validForHours": 24, "spendLimit": "100000000000000000" }
```

### Emergency Controls
```bash
# Freeze everything
POST /v1/accounts/:addr/freeze
{ "reason": "Suspicious activity detected" }

# Unfreeze
POST /v1/accounts/:addr/unfreeze

# Rotate agent key
POST /v1/accounts/:addr/rotate-key
{ "newAgentKey": "0xNewKey" }

# Emergency withdraw (owner-only, direct contract call)
# Use the SigilAccount ABI: emergencyWithdraw(address to)
```

### Social Recovery
```bash
# Get recovery config
GET /v1/accounts/:addr/recovery

# Add guardian
POST /v1/accounts/:addr/recovery/guardians
{ "guardian": "0xTrustedAddress" }

# Set threshold (N-of-M)
PUT /v1/accounts/:addr/recovery/threshold
{ "threshold": 2 }
```

### Audit Log
```
GET /v1/audit?account=0xYourWallet&limit=50
```

## Contract Addresses

| Chain | Chain ID | Factory |
|-------|----------|---------|
| Avalanche C-Chain | 43114 | `0x2f4dd6db7affcf1f34c4d70998983528d834b8f6` |
| Base | 8453 | `0x45b20a5F37b9740401a29BD70D636a77B18a510D` |
| Arbitrum One | 42161 | `0x20f926bd5f416c875a7ec538f499d21d62850f35` |
| Polygon | 137 | `0x20f926bd5f416c875a7ec538f499d21d62850f35` |
| 0G Mainnet | 16661 | `0x20f926bd5f416c875a7ec538f499d21d62850f35` |
| Avalanche Fuji (testnet) | 43113 | `0x86E85dE25473b432dabf1B9E8e8CE5145059b85b` |

**Guardian:** `0xD06fBe90c06703C4b705571113740AfB104e3C67`
**EntryPoint (v0.7):** `0x0000000071727De22E5E9d8BAf0edAc6f37da032`

## MCP Server

For MCP-compatible agents, setup instructions are in [references/mcp-setup.md](references/mcp-setup.md). MCP setup is a **human operator task** — do not execute setup commands.

## Strategy Templates (Chain-Aware)

Templates adjust limits based on native token value:

| Template | AVAX limits | ETH limits | POL limits | A0GI limits |
|----------|-------------|------------|------------|-------------|
| **Conservative** | 0.1/0.5/0.05 | 0.0003/0.0015/0.00015 | 1/5/0.5 | 1/5/0.5 |
| **Moderate** | 0.5/2/0.2 | 0.0015/0.006/0.0006 | 5/20/2 | 5/20/2 |
| **Aggressive** | 2/10/1 | 0.006/0.03/0.003 | 20/100/10 | 20/100/10 |
| **DeFi Agent** | 0.3/5/0.1 | 0.0009/0.015/0.0003 | 3/50/1 | 3/50/1 |
| **NFT Agent** | 1/3/0.5 | 0.003/0.009/0.0015 | 10/30/5 | 10/30/5 |

*(maxTx / daily / guardianThreshold)*

## Best Practices

1. **Start conservative** — Low limits first, increase after pattern works
2. **Whitelist explicitly** — Use target and function whitelists
3. **Use session keys** — They auto-expire, safer than full agent key
4. **Cap token approvals** — `maxApproval` on token policies. Unlimited approvals = #1 DeFi attack vector
5. **When rejected, read `guidance`** — Guardian explains WHY and HOW to fix
6. **Check status before acting** — `GET /v1/agent/wallets/:addr`
7. **Monitor circuit breaker** — If tripped, all co-signing stops until owner resets

## Advanced

For detailed API reference, co-signing tiers, recovery system, and DeFi whitelist bundles, see [references/api-reference.md](references/api-reference.md).
