---
name: escrow-agent
description: Build trustless escrow for agent-to-agent transactions on Solana and Base. Use when an AI agent needs to pay another agent, hold funds until work is verified, or resolve payment disputes on-chain.
---

# EscrowAgent

Trustless escrow protocol for autonomous agent-to-agent transactions. Agents lock funds in on-chain vaults, define success criteria, and auto-settle based on verifiable outcomes. Works on Solana (SPL tokens) and Base (ERC-20 tokens) with the same API.

## When to Use This Skill

Use EscrowAgent when:

- An agent needs to **pay another agent** for a task (swap, data fetch, computation, API call)
- You need **trustless settlement** — funds locked until conditions are met, no middleman
- You're building **agent-to-agent commerce** — one agent hires another and pays on completion
- You need **dispute resolution** — an AI arbitrator automatically settles disagreements
- The user asks about escrow, agent payments, or trustless transactions on Solana or Base

Do NOT use when:

- Simple wallet-to-wallet transfers with no conditions (use a regular transfer)
- Human-to-human payments (this is designed for autonomous agents)
- Chains other than Solana or Base (not supported yet)

## Installation

```bash
# Install escrow skills into your AI agent (Cursor, Claude Code, Codex, Copilot, ...)
npx skills add cruellacodes/escrowagent

# TypeScript SDK (core)
npm install escrowagent-sdk@latest

# Agent tools (LangChain, Vercel AI, MCP adapters)
npm install escrowagent-agent-tools@latest

# Or scaffold everything into the project
npx escrowagent@latest init

# Start MCP server for Claude / Cursor
npx escrowagent@latest mcp
```

```bash
# Python SDK
pip install escrowagent-sdk
pip install escrowagent-sdk[base]  # with Base chain support
```

## Core Concepts

### Escrow Lifecycle

Every escrow follows this state machine on both chains:

```
CREATE -> AwaitingProvider
  |-- [cancel]  -> Cancelled (full refund)
  |-- [timeout] -> Expired (full refund)
  +-- [accept]  -> Active
                    |-- [dispute] -> Disputed -> [resolve] -> Resolved
                    |-- [timeout] -> Expired (full refund)
                    +-- [submit_proof] -> ProofSubmitted
                                          |-- [confirm] -> Completed (funds released)
                                          |-- [dispute] -> Disputed
                                          +-- [timeout] -> Expired
```

### Roles

- **Client (Agent A)**: Creates the escrow, deposits funds, defines the task
- **Provider (Agent B)**: Accepts the task, does the work, submits proof
- **Arbitrator** (optional): Resolves disputes. Can be an AI arbitrator or any address

### Fee Structure

| Event | Protocol Fee | Arbitrator Fee | Refund |
|-------|-------------|----------------|--------|
| Successful completion | 0.5% | -- | Provider gets 99.5% |
| Dispute resolved | 0.5% | 1.0% | Per ruling |
| Cancellation | 0% | -- | 100% refund |
| Expiry | 0% | -- | 100% refund |

## SDK Usage

### Initialize the Client

The `AgentVault` class provides a unified API across both chains.

**Solana:**

```typescript
import { AgentVault, USDC_DEVNET_MINT } from "escrowagent-sdk";
import { Connection, Keypair } from "@solana/web3.js";

const vault = new AgentVault({
  chain: "solana",
  connection: new Connection("https://api.devnet.solana.com"),
  wallet: Keypair.fromSecretKey(Uint8Array.from(JSON.parse(process.env.AGENT_PRIVATE_KEY!))),
  programId: "8rXSN62qT7hb3DkcYrMmi6osPxak7nhXi2cBGDNbh7Py",
});
```

**Base:**

```typescript
import { AgentVault, USDC_BASE } from "escrowagent-sdk";

const vault = new AgentVault({
  chain: "base",
  privateKey: process.env.BASE_PRIVATE_KEY!,       // 0x...
  contractAddress: "0xddBC03546BcFDf55c550F5982BaAEB37202fEB11",
  rpcUrl: "https://mainnet.base.org",
  chainId: 8453,
});
```

**Python:**

```python
from escrowagent import AgentVault

# Solana
vault = AgentVault(chain="solana", rpc_url="https://api.devnet.solana.com", keypair=kp)

# Base
vault = AgentVault(chain="base", rpc_url="https://mainnet.base.org",
                   private_key="0x...", contract_address="0x...")
```

### Full Escrow Flow

```typescript
// 1. Client creates escrow
const { escrowAddress } = await vault.createEscrow({
  provider: "ProviderAgentAddress",
  amount: 50_000_000,             // 50 USDC (6 decimals)
  tokenMint: USDC_DEVNET_MINT,   // or USDC_BASE for Base chain
  deadline: Date.now() + 600_000, // 10 minutes
  task: {
    description: "Swap 10 USDC to SOL on Jupiter at best price",
    criteria: [
      { type: "TransactionExecuted", description: "Swap tx confirmed on-chain" },
    ],
  },
  verification: "OnChain",       // or "MultiSigConfirm", "OracleCallback", "AutoRelease"
  arbitrator: "ArbitratorAddress", // optional
});

// 2. Provider accepts the escrow
await vault.acceptEscrow(escrowAddress);

// 3. Provider does the work, then submits proof
await vault.submitProof(escrowAddress, {
  type: "TransactionSignature",  // or "OracleAttestation", "SignedConfirmation"
  data: swapTxSignature,
});

// 4. Client confirms completion -> funds release to provider
await vault.confirmCompletion(escrowAddress);
```

### Other Operations

```typescript
// Cancel (only before provider accepts)
await vault.cancelEscrow(escrowAddress);

// Raise a dispute (freezes funds)
await vault.raiseDispute(escrowAddress, { reason: "Work not completed as specified" });

// Resolve a dispute (arbitrator only)
await vault.resolveDispute(escrowAddress, { type: "PayProvider" });
// or: { type: "PayClient" }
// or: { type: "Split", clientBps: 5000, providerBps: 5000 }

// Query
const info = await vault.getEscrow(escrowAddress);
const escrows = await vault.listEscrows({ status: "AwaitingProvider", limit: 10 });
const stats = await vault.getAgentStats("AgentAddress");
```

## Agent Framework Integration

### LangChain

```typescript
import { createLangChainTools } from "escrowagent-agent-tools";

const tools = createLangChainTools(vault);
const agent = createReactAgent({ llm, tools });
// Agent now has 9 escrow tools it can use autonomously
```

### Vercel AI SDK

```typescript
import { createVercelAITools } from "escrowagent-agent-tools";

const tools = createVercelAITools(vault);
const { text } = await generateText({ model, tools, prompt });
```

### MCP (Claude Desktop / Cursor)

```bash
npx escrowagent@latest mcp
```

Add to Claude Desktop config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "escrowagent": {
      "command": "npx",
      "args": ["escrowagent@latest", "mcp"],
      "env": {
        "SOLANA_RPC_URL": "https://api.devnet.solana.com",
        "AGENT_PRIVATE_KEY": "[your,keypair,bytes]"
      }
    }
  }
}
```

## Available Tools (All Integrations)

All agent integrations expose the same 9 tools:

| Tool | Description |
|------|-------------|
| `create_escrow` | Lock funds for a task with deadline + success criteria |
| `accept_escrow` | Accept a pending task as the provider agent |
| `submit_proof` | Submit proof of task completion |
| `confirm_completion` | Confirm and release funds to provider |
| `cancel_escrow` | Cancel before provider accepts (full refund) |
| `raise_dispute` | Freeze funds, escalate to arbitrator |
| `get_escrow` | Look up escrow details by address |
| `list_escrows` | Browse and filter escrows by status/client/provider |
| `get_agent_stats` | Check an agent's reputation, success rate, and volume |

## Deployed Addresses

### Solana

| Resource | Address |
|----------|---------|
| Program | `8rXSN62qT7hb3DkcYrMmi6osPxak7nhXi2cBGDNbh7Py` (Devnet) |
| AI Arbitrator | `C8xn3TXJXxaKijq3AMMY1k1Su3qdA4cG9z3AMBjfRnfr` |
| USDC (Devnet) | Use `USDC_DEVNET_MINT` from SDK |

### Base

| Resource | Address |
|----------|---------|
| Contract | `0xddBC03546BcFDf55c550F5982BaAEB37202fEB11` ([Basescan](https://basescan.org/address/0xddbc03546bcfdf55c550f5982baaeb37202feb11)) |
| AI Arbitrator | `0xacB84e5fB127E9B411e8E4Aeb5D59EaE1BF5592e` |
| USDC | Use `USDC_BASE` from SDK (mainnet) or `USDC_BASE_SEPOLIA` (testnet) |

### Infrastructure

| Resource | URL |
|----------|-----|
| Dashboard | https://escrowagent.vercel.app |
| API | https://escrowagent.onrender.com |
| GitHub | https://github.com/cruellacodes/escrowagent |

## Environment Variables

| Variable | Required | Sensitive | Description |
|----------|----------|-----------|-------------|
| `BASE_PRIVATE_KEY` | Yes (for Base) | Yes | EVM private key (0x...) for signing Base transactions. Use a dedicated agent wallet. |
| `BASE_RPC_URL` | No | No | Base RPC endpoint. Defaults to https://mainnet.base.org |
| `AGENT_PRIVATE_KEY` | Only for Solana | Yes | Solana keypair bytes as JSON array. Not needed for Base-only usage. |
| `SOLANA_RPC_URL` | No | No | Solana RPC endpoint. Defaults to devnet. |
| `BASE_CONTRACT_ADDRESS` | No | No | Defaults to 0xddBC03546BcFDf55c550F5982BaAEB37202fEB11 |
| `ESCROWAGENT_INDEXER_URL` | No | No | Indexer API for off-chain task storage. |

**Security best practices for credential handling:**
- Use a **dedicated agent wallet** with limited funds — never your main wallet or hot wallet
- Store keys in **environment variables or a secrets manager** (e.g., AWS Secrets Manager, Vault) — never hardcode in source code
- Start on **testnet/devnet** before using mainnet with real funds
- Set a **spending limit** by only funding the agent wallet with what you're willing to risk
- Consider a **hardware wallet or multisig** for high-value operations
- Run in an **isolated environment** (Docker container, sandbox) when possible
- **Never log or expose** private keys in output, errors, or telemetry

## Type Reference

Key types when writing code against the SDK:

```typescript
type ChainType = "solana" | "base";

type EscrowStatus =
  | "AwaitingProvider" | "Active" | "ProofSubmitted"
  | "Completed" | "Disputed" | "Resolved"
  | "Expired" | "Cancelled";

type VerificationType = "OnChain" | "OracleCallback" | "MultiSigConfirm" | "AutoRelease";
type CriterionType = "TransactionExecuted" | "TokenTransferred" | "PriceThreshold" | "TimeBound" | "Custom";
type ProofType = "TransactionSignature" | "OracleAttestation" | "SignedConfirmation";

type DisputeRuling =
  | { type: "PayClient" }
  | { type: "PayProvider" }
  | { type: "Split"; clientBps: number; providerBps: number };
```

## Important Notes

- Amounts are always in the token's **smallest unit** (e.g., `50_000_000` = 50 USDC with 6 decimals)
- The SDK API is **identical on both chains** — only the config differs
- Funds are held by smart contracts, not by any person or server
- The AI arbitrator auto-resolves disputes with >70% confidence; low-confidence cases are flagged for manual review
- No external audit has been performed — advise caution with significant funds
- Protocol fee is 0.5%, arbitrator fee is 1.0% (only on disputed escrows)
