# 31Third Skill Integration Guide

## Overview

After deploying your Strategy Executor module and policies via the wizard, configure this skill with environment variables.

## 1. Install the Skill

```bash
openclaw clawhub install 31third-safe-rebalancer
```

## 2. Environment Variables (Required)

| Variable | Description | Source |
| --- | --- | --- |
| `RPC_URL` | RPC URL for the target chain. | User provided |
| `CHAIN_ID` | Chain ID (optional; defaults to `8453`). | User provided |
| `TOT_API_KEY` | 31Third API key for routing/rebalancing. | User provided (`dev@31third.com`) |
| `SAFE_ADDRESS` | Safe wallet address. | Wizard output |
| `EXECUTOR_MODULE_ADDRESS` | Strategy Executor module address. | Wizard output |
| `EXECUTOR_WALLET_PRIVATE_KEY` | Signer private key for execution txs. | User provided |

## 3. Secure Configuration (Recommended)

Use encrypted secrets via OpenClaw:

```bash
openclaw configure --section secrets
```

Then set:

```bash
RPC_URL=<your-rpc-url>
CHAIN_ID=8453
TOT_API_KEY=<your_api_key>
SAFE_ADDRESS=<safe_address>
EXECUTOR_MODULE_ADDRESS=<strategy_executor_address>
EXECUTOR_WALLET_PRIVATE_KEY=<your_agent_private_key>
```

## 4. Policy Verification (Optional)

```bash
node scripts/inspect_policies_advanced.js
```

## 5. Boundary Detection and Safety

- Auto-boundary detection: scans on-chain policies before execution.
- Error decoding: translates revert data into readable policy violations.
