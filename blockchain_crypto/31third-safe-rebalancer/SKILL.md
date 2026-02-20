---
name: safe-rebalancer
description: Execute policy-guarded token swaps and portfolio rebalancing for a Safe via 31Third on EVM chains.
homepage: https://31third.com
metadata: {"openclaw":{"skillKey":"31third-safe-rebalancer","homepage":"https://31third.com","requires":{"env":["RPC_URL","CHAIN_ID","TOT_API_KEY","SAFE_ADDRESS","EXECUTOR_MODULE_ADDRESS","EXECUTOR_WALLET_PRIVATE_KEY"],"bins":["node"]},"primaryEnv":"TOT_API_KEY"}}
---

# 31Third Safe Rebalancer

This skill executes on-chain transactions with 31Third infrastructure and policy checks (daily limits, allowlists, slippage) before execution.

## Setup for Agent Owners

Deploy the 31Third execution environment to your Safe first:
Deployment Wizard: <https://app.31third.com/safe-policy-deployer>

1. Get an API key from <https://31third.com>.
2. Deploy Safe policy and Strategy Executor with the wizard.
3. Set environment variables:

```bash
RPC_URL=https://mainnet.base.org
CHAIN_ID=8453
TOT_API_KEY=your_api_key_here
SAFE_ADDRESS=your_safe_address
EXECUTOR_MODULE_ADDRESS=deployed_module_address
EXECUTOR_WALLET_PRIVATE_KEY=agent_hot_wallet_private_key
```

## Capabilities

1. Token swaps (for example USDC -> WETH).
2. Portfolio rebalancing to target weights.
3. Policy checks and inspection.

## Usage

### Simple Swap

```bash
node {baseDir}/scripts/trade.js --action swap --from 0xUSDC... --to 0xWETH... --amount 1000000 --chain base
```

### Portfolio Rebalance

```bash
node {baseDir}/scripts/trade.js --action rebalance --targets '{"0xWETH...": 0.5, "0xUSDC...": 0.5}' --chain-id 8453
```

### Policy Checks

```bash
node {baseDir}/scripts/trade.js --action checkPolicy
node {baseDir}/scripts/inspect_policies_advanced.js
node {baseDir}/scripts/check_target_executor.js
```

## Required Configuration

- `RPC_URL`
- `CHAIN_ID` (optional, defaults to `8453`)
- `TOT_API_KEY`
- `SAFE_ADDRESS`
- `EXECUTOR_MODULE_ADDRESS`
- `EXECUTOR_WALLET_PRIVATE_KEY`

## Disclaimer

- This skill is infrastructure tooling and not financial, investment, legal, or tax advice.
- Operators are fully responsible for policy setup, signer security, execution approvals, and compliance.
- Validate behavior in non-production environments before enabling live trading.

## References

- See `references/SDK.md` for SDK notes.
