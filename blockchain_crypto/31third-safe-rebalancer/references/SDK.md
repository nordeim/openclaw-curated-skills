# @31third/sdk Reference (for @31third/safe-rebalancer)

Source snapshot: npm package metadata for `@31third/sdk` version `0.1.0-alpha.4`.

## Install

```bash
npm install @31third/sdk
```

## Core capabilities used by this skill

- Calculate rebalancing plans via 31Third API.
- Execute rebalancing plans on-chain through a deployed Strategy Executor module.
- Deploy/initialize Strategy Executor + policies (separate setup workflow).

## Required runtime inputs

For this skill's execution path (`scripts/trade.js`):

- `RPC_URL`
- `CHAIN_ID` (optional; defaults to `8453`)
- `TOT_API_KEY`
- `SAFE_ADDRESS`
- `EXECUTOR_MODULE_ADDRESS`
- `EXECUTOR_WALLET_PRIVATE_KEY`

Typical chain IDs mentioned by the SDK docs:

- Ethereum: `1`
- Polygon: `137`
- Base: `8453`
- Arbitrum One: `42161`

## Key functions

### `calculateRebalancing({...})`

Used to request a rebalancing plan.

Important inputs:

- `apiBaseUrl` (for example `https://api.31third.com/1.3`)
- `apiKey`
- `chainId`
- `payload`

Common payload fields:

- `wallet`: Safe address
- `signer`: executor/signer address
- `baseEntries`: array of `{ tokenAddress, amount }`
- `targetEntries`: array of `{ tokenAddress, allocation }`
- Optional controls: `maxSlippage`, `maxPriceImpact`, `minTradeValue`, `skipBalanceValidation`, `revertOnError`, `failOnMissingPricePair`, `async`

### `executeRebalancing({...})`

Used to send the on-chain execution transaction.

Important inputs:

- `signer`: ethers wallet/signer
- `strategyExecutor`: deployed module address
- `rebalancing`: output from `calculateRebalancing`

## Policy model (high-level)

SDK documentation describes three primary policy classes applied on-chain before execution:

- Asset universe policy: restrict tradable tokens to an allowlist.
- Static allocation policy: enforce target portfolio weights with trigger/tolerance thresholds.
- Slippage policy: enforce minimum receive thresholds based on feeds.

If policy checks fail, execution reverts with policy-specific errors.

## Notes for this skill

- Keep Safe deployment signer and executor wallet distinct.
- Use a dedicated hot wallet for execution.
- Keep policy boundaries strict before autonomous trading.
- The skill's `scripts/error_decoder.js` maps known policy revert selectors to readable messages.

## Current-status note from SDK docs

The published SDK README indicates Base-first support and includes a Base token/feed set reference. If you run on other chains, verify support and addresses before production use.

## Where to verify latest

- npm package: <https://www.npmjs.com/package/@31third/sdk>
- Installed package README via npm:

```bash
npm view @31third/sdk readme
```
