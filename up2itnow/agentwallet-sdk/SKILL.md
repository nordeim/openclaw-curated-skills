# Agent Wallet

On-chain spend limits for autonomous AI agents. The crypto wallet agent for Base L2 that enables autonomous payments with human-approved spending controls. Set a budget per token, let your agent transact freely within it — anything over-limit queues for human approval. A wallet for AI that handles gas management and on-chain transactions so your agent can focus on its task.

## When To Use This Skill

- Use when the agent needs to make autonomous payments
- Use when the agent needs a crypto wallet with spending limits
- Use when the user asks about agent financial autonomy
- Use when the agent needs to send ETH or ERC-20 tokens on Base
- Use when the agent needs human-approved spending limits
- Use when building agent-to-agent payment flows
- Use when the agent needs an agent treasury with spending controls
- Use when integrating token bound accounts (ERC-6551) for agent spending

## 🔒 Security Posture

| Metric | Detail |
|--------|--------|
| **Tests** | 129 Solidity · 34 SDK · 104 backend — **267 total** |
| **Security Review** | 2 rounds internal adversarial review (NOT third-party) |
| **Validation** | 8 Validator rounds — 0 fixable issues remaining |
| **Transparency** | KNOWN_ISSUES.md — full disclosure of limitations |
| **License** | MIT — fully open source |

## What It Does

Agent Wallet is a smart contract wallet (ERC-6551 Token Bound Account) designed for AI agents on Base. Instead of giving your agent a private key with unlimited access, you deploy a wallet with enforced constraints:

- **Per-transaction limits** — Max spend per tx, enforced on-chain
- **Daily budget caps** — Rolling period budgets per token
- **Operator permissions** — Grant agents scoped access without sharing keys
- **Approval queue** — Over-limit transactions queue for owner approval (ERC-4337 compatible)
- **Operator epochs** — All operator permissions auto-invalidate on NFT transfer (prevents stale access)
- **Reentrancy guards** — All state-changing functions protected

## Deployed Addresses

| Network | Contract | Address |
|---------|----------|---------|
| **Base Mainnet** | AgentAccountFactoryV2 | `0x700e9Af71731d707F919fa2B4455F27806D248A1` |
| **Base Sepolia** | AgentAccountFactoryV2 | `0x337099749c516B7Db19991625ed12a6c420453Be` |

## SDK Usage

```bash
npm install @agentwallet/sdk
```

```typescript
import { createWallet, agentTransferToken } from '@agentwallet/sdk';

// Connect to an agent's wallet
const wallet = createWallet({
  accountAddress: '0x...',
  chain: 'base',
  walletClient
});

// Agent spends within limits — no approval needed
await agentTransferToken(wallet, {
  token: USDC_ADDRESS,
  to: recipientAddress,
  amount: parseUnits('50', 6)
});

// Set spend limits (owner only)
await wallet.setSpendLimit({
  token: USDC_ADDRESS,
  maxPerTx: parseUnits('100', 6),
  periodLimit: parseUnits('500', 6),
  periodDuration: 86400 // 24 hours
});
```

## Security Model

### On-Chain Enforcements
- **Spend limits** checked in contract — agent code cannot bypass them
- **Operator epoch** invalidates all operators on ownership (NFT) transfer
- **Reentrancy guards** on all mutating functions (both base and 4337 variants)
- **Fixed-window periods** prevent boundary double-spend attacks
- **NFT burn protection** — funds recoverable, clean revert on burned NFT

### What Was Reviewed
Security reviewed internally (2 rounds of AI-assisted adversarial review). No third-party audit has been performed.

- **Round 1:** Standard security review — found and fixed reentrancy vectors, access control gaps
- **Round 2:** Adversarial red-team — found and fixed flash-loan NFT hijack, stale operator persistence, 4337 queue DoS, period boundary double-spend, NFT burn fund lock

Full audit reports:
- [`AUDIT_REPORT.md`](./AUDIT_REPORT.md) — Round 1
- [`AUDIT_REPORT_V2.md`](./AUDIT_REPORT_V2.md) — Round 2 (adversarial)

### Test Results
- **129/129 Solidity tests pass** (Unit, Exploit, Invariant, Factory, Router, 4337, Escrow, Entitlements, CCTP, A2A)
- **34/34 SDK tests pass** (wallet creation, spend limits, operators, transactions, edge cases)
- Exploit tests specifically prove all discovered attack vectors are blocked

## Architecture

```
NFT (ERC-721)
  └── Token Bound Account (ERC-6551)
       ├── Owner: NFT holder (full control)
       ├── Operators: Scoped access (set by owner)
       ├── Spend Limits: Per-token, per-period (on-chain)
       ├── Approval Queue: Over-limit txs (ERC-4337)
       └── Factory: CREATE2 deterministic deploys
```

## Known Issues

See [KNOWN_ISSUES.md](./KNOWN_ISSUES.md) for transparent documentation of limitations and items we're monitoring.

## License

MIT
