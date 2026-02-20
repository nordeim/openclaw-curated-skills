# Agent Setup Guide — Sigil Protocol

## Understanding the 3 Addresses

| Address | What It Is | Fund It? |
|---------|-----------|----------|
| **Owner Wallet** | Your personal wallet (MetaMask etc.) that controls the Sigil account | ❌ Only for gas to manage settings |
| **Sigil Smart Account** | On-chain contract that holds funds and executes transactions | ✅ **FUND THIS ONE** |
| **Agent Key** | A signing keypair for API authentication — NOT a wallet | ❌ **NEVER FUND THIS** |

> 💡 The agent key is like a login credential. You don't deposit money into a password.

---

## Quick Setup (5 Steps)

```
1. Deploy   → sigil.codes/onboarding (connect owner wallet, pick chain & strategy)
2. Fund     → Send tokens to your SIGIL ACCOUNT address (0xYourSigilAccount)
3. API Key  → sigil.codes/dashboard/agent-access → generate key (starts with sgil_)
4. Config   → Give your agent: SIGIL_API_KEY + SIGIL_ACCOUNT_ADDRESS
5. Go       → Agent submits transactions via API. Guardian evaluates. Sigil account pays.
```

---

## How Transactions Work

```
Agent builds tx
       ↓
POST /v1/evaluate  (with Bearer token from API key auth)
       ↓
┌─────────────────────────┐
│  Guardian 3-Layer Check  │
│  L1: Policy rules        │
│  L2: Tx simulation       │
│  L3: AI risk scoring     │
└─────────────────────────┘
       ↓
   APPROVE → Guardian co-signs → Sigil account executes (using ITS funds)
   REJECT  → Returns guidance on why + how to fix
   ESCALATE → Needs owner approval
```

**Key point:** The Sigil smart account pays for everything. The agent never touches funds directly.

---

## Common Mistakes

| Mistake | Why It's Wrong |
|---------|---------------|
| ❌ Funding the agent key address | Agent key is for auth only — funds sent there are stuck/wasted |
| ❌ Giving the agent your owner private key | Owner key controls freeze/withdraw/policy — agent should NEVER have it |
| ❌ Agent sending from its own wallet | Transactions must go through Guardian API, not direct on-chain sends |
| ❌ Using agent key private key as a wallet | It's a signing key for API auth, not an EOA to hold funds |

---

## Minimal Code Example

### 1. Authenticate

```bash
# Get a Bearer token using your API key
curl -X POST https://api.sigil.codes/v1/agent/auth/api-key \
  -H "Content-Type: application/json" \
  -d '{"apiKey": "sgil_your_key_here"}'

# Response: { "token": "eyJ..." }
```

### 2. Evaluate a Transaction

```bash
# Submit a transaction for Guardian evaluation
curl -X POST https://api.sigil.codes/v1/evaluate \
  -H "Authorization: Bearer eyJ..." \
  -H "Content-Type: application/json" \
  -d '{
    "userOp": {
      "sender": "0xYourSigilAccount",
      "nonce": "0x0",
      "callData": "0x...",
      "callGasLimit": "200000",
      "verificationGasLimit": "200000",
      "preVerificationGas": "50000",
      "maxFeePerGas": "25000000000",
      "maxPriorityFeePerGas": "1500000000",
      "signature": "0x"
    }
  }'
```

### 3. Check Result

```jsonc
// APPROVED — Guardian co-signed, ready to submit on-chain
{ "verdict": "APPROVE", "guardianSignature": "0x..." }

// REJECTED — Read the guidance field
{ "verdict": "REJECT", "guidance": "Transfer exceeds daily limit of 0.5 AVAX..." }
```

---

## Summary

```
Owner wallet    → manages policies (human only)
Sigil account   → holds funds, executes txs  ← FUND THIS
Agent key       → authenticates API calls     ← DON'T FUND
```
