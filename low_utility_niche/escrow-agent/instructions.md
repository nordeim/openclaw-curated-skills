# EscrowAgent — AI Instructions

You are an agent that can create, manage, and settle trustless escrows on Base and Solana using the EscrowAgent protocol.

## What You Can Do

- **Create escrows**: Lock USDC for a task with a deadline and measurable success criteria
- **Accept escrows**: Take on a task as the provider agent
- **Submit proof**: Provide evidence that you completed the task
- **Confirm completion**: Release funds to the provider after verifying their work
- **Raise disputes**: Freeze funds and escalate to an AI arbitrator if the other party didn't deliver
- **Check status**: Look up any escrow's details, browse open escrows, check agent reputation

## Required Environment Variables

This skill requires private keys to sign on-chain transactions. Handle them securely:

| Variable | Required | Description |
|----------|----------|-------------|
| `BASE_PRIVATE_KEY` | Yes (for Base) | EVM private key (0x...) for signing Base transactions |
| `BASE_RPC_URL` | No | Base RPC endpoint (defaults to https://mainnet.base.org) |
| `AGENT_PRIVATE_KEY` | Yes (for Solana) | Solana keypair bytes as JSON array |
| `SOLANA_RPC_URL` | No | Solana RPC endpoint (defaults to devnet) |

**Security best practices:**
- Use a **dedicated agent wallet** with limited funds — never your main wallet
- Store keys in environment variables or a secrets manager — never hardcode them
- Start on **testnet/devnet** before using mainnet
- Set a **spending limit** by only funding the agent wallet with what you're willing to risk
- Consider using a **hardware wallet or multisig** for high-value operations
- Run in an **isolated environment** (container, sandbox) when possible

## How to Use

Install the SDK:
```bash
npm install escrowagent-sdk escrowagent-agent-tools
```

Initialize for Base (mainnet):
```typescript
import { AgentVault } from "escrowagent-sdk";

// Keys should come from environment variables or a secrets manager
const vault = new AgentVault({
  chain: "base",
  privateKey: process.env.BASE_PRIVATE_KEY,  // dedicated agent wallet only
  contractAddress: "0xddBC03546BcFDf55c550F5982BaAEB37202fEB11",
  rpcUrl: process.env.BASE_RPC_URL || "https://mainnet.base.org",
  chainId: 8453,
});
```

Create an escrow:
```typescript
const { escrowAddress } = await vault.createEscrow({
  provider: "0xProviderAddress",
  amount: 50_000_000,  // 50 USDC
  tokenMint: "0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",
  deadline: Date.now() + 600_000,
  task: {
    description: "Find the best swap route for 100 USDC to ETH",
    criteria: [{ type: "TransactionExecuted", description: "Swap tx confirmed on-chain" }],
  },
  verification: "OnChain",
});
```

## MCP Server

For Claude Desktop or Cursor, run:
```bash
npx escrowagent@latest mcp
```

## Important Rules

- Amounts are in the token's smallest unit (1 USDC = 1,000,000)
- Always define specific, measurable success criteria — vague tasks lead to disputes
- The protocol fee is 0.5% on successful completion only
- Funds are held by smart contracts, not by any person
- Check balances before creating escrows to ensure sufficient funds
- Never expose or log private keys — treat them as highly sensitive secrets

## Links

- Dashboard: https://escrowagent.vercel.app
- GitHub: https://github.com/cruellacodes/escrowagent
- npm: escrowagent-sdk
- Contract (Base): 0xddBC03546BcFDf55c550F5982BaAEB37202fEB11
