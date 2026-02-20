# Safe Rebalancer Skill (31Third)

A secure, policy-compliant execution skill for AI agents managing Gnosis Safe portfolios. Powered by [31Third](https://31third.com).

This skill enables your agent to execute on-chain trades (swaps, rebalancing) while respecting strict safety policies (allowlists, daily limits, slippage) enforced by the 31Third Strategy Executor module.

## Setup and Deployment

Before using this skill, deploy the Strategy Executor Module and policies to your Safe.
Use the Deployment Wizard: <https://app.31third.com/safe-policy-deployer>

## Features

- Policy enforcement: wraps trades in the 31Third execution layer; invalid trades fail on-chain.
- Portfolio rebalancing: calculate and execute complex rebalancing transactions in a single atomic batch.
- Auto-boundary detection: detects active policy limits (asset universe, slippage).
- Verification tools: includes scripts to audit deployed policies and verify target allocations on-chain.

## Installation

### Via ClawHub (Recommended)

```bash
openclaw clawhub install 31third-safe-rebalancer
```

## Configuration

Set these environment variables in your agent configuration:

| Variable | Description |
| --- | --- |
| `RPC_URL` | Target chain RPC URL (for example Base Mainnet). |
| `CHAIN_ID` | Chain ID (optional, defaults to `8453` for Base). |
| `TOT_API_KEY` | 31Third API key. Request via `dev@31third.com`. |
| `SAFE_ADDRESS` | Address of the Safe holding assets. |
| `EXECUTOR_MODULE_ADDRESS` | Address of the deployed Strategy Executor Module. |
| `EXECUTOR_WALLET_PRIVATE_KEY` | Private key of the agent signer wallet. |

## Usage

### 1. Simple Swap

```bash
node scripts/trade.js --action swap --from 0xUSDC... --to 0xWETH... --amount 1000000 --chain base
```

### 2. Portfolio Rebalance

```bash
node scripts/trade.js --action rebalance --targets '{"0xWETH...": 0.5, "0xUSDC...": 0.5}' --chain-id 8453
```

### 3. Policy Inspection

```bash
node scripts/inspect_policies_advanced.js
```

## Notes

- PDF reports require optional dependency `puppeteer`.
- If `puppeteer` is not installed, HTML report output is generated instead.

## Disclaimer

- This software is provided for infrastructure and automation purposes only.
- It is not financial, investment, legal, or tax advice.
- You are solely responsible for policy configuration, key management, trade decisions, and regulatory compliance.
- Always test in a controlled environment before production use.

## Architecture

- `SKILL.md`: main entry point defining agent capabilities.
- `scripts/`: execution, inspection, and reporting scripts.
- `references/`: SDK and policy references.

## License

MIT
