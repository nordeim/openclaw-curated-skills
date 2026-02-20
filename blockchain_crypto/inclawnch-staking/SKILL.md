---
name: inclawnch-staking
description: >
  Stake and unstake INCLAWNCH tokens in the UBI pool on Base. Query treasury stats, wallet
  positions, APY estimates, and top stakers. Toggle auto-compounding. No API key needed.
  Use when: (1) user wants to stake INCLAWNCH, (2) checking staking positions or rewards,
  (3) unstaking tokens, (4) enabling auto-compound, (5) comparing staking yields.
version: 1.0.0
metadata:
  openclaw:
    emoji: "🌱"
    homepage: "https://inclawbate.com/skills"
    requires:
      bins: ["curl"]
---

# INCLAWNCH UBI Staking — Stake, Unstake, and Query for AI Agents

Full access to the Inclawbate Universal Basic Income staking system on Base. Stake INCLAWNCH tokens, unstake anytime, toggle auto-compounding, and query treasury stats, wallet positions, and the top stakers leaderboard.

No API key. No auth. Public and open.

## Quick Start

```bash
# Get treasury stats + top stakers
curl "https://inclawbate.com/api/inclawbate/staking"

# Get a specific wallet's staking position
curl "https://inclawbate.com/api/inclawbate/staking?wallet=0x91b5c0d07859cfeafeb67d9694121cd741f049bd"

# Stake tokens (after sending ERC20 transfer on Base)
curl -X POST "https://inclawbate.com/api/inclawbate/ubi" \
  -H "Content-Type: application/json" \
  -d '{"action":"fund","tx_hash":"0x...","wallet_address":"0x..."}'

# Unstake all tokens
curl -X POST "https://inclawbate.com/api/inclawbate/ubi" \
  -H "Content-Type: application/json" \
  -d '{"action":"unstake","wallet_address":"0x...","token":"clawnch"}'

# Toggle auto-compounding
curl -X POST "https://inclawbate.com/api/inclawbate/ubi" \
  -H "Content-Type: application/json" \
  -d '{"action":"toggle-auto-stake","wallet_address":"0x..."}'

# Read the machine-readable skill spec
curl "https://inclawbate.com/api/inclawbate/skill/staking"
```

## Write Capabilities

### Stake INCLAWNCH

Two-step process: transfer tokens on-chain, then register the stake via API.

**Step 1:** Transfer INCLAWNCH to the deposit wallet on Base:
```
Token contract: 0xa1F72459dfA10BAD200Ac160eCd78C6b77a747be
Deposit wallet: 0xa4d6f012003fe6ad2774a874c8c98ee69d17f286
Function: transfer(address to, uint256 amount)
Chain: Base
```

**Step 2:** Register the stake:
```bash
curl -X POST "https://inclawbate.com/api/inclawbate/ubi" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "fund",
    "tx_hash": "0x<64-hex-char-tx-hash>",
    "wallet_address": "0xYourWallet"
  }'
```

The API verifies the on-chain transfer (correct token, correct recipient, amount > 0) and records the stake. Stakers begin earning UBI distributions immediately.

### Unstake INCLAWNCH

No lock period. Request anytime — tokens returned to your wallet within 24 hours (instantly if the unstake wallet has sufficient balance).

```bash
curl -X POST "https://inclawbate.com/api/inclawbate/ubi" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "unstake",
    "wallet_address": "0xYourWallet",
    "token": "clawnch"
  }'
```

### Toggle Auto-Compound

When enabled, daily UBI reward distributions are automatically re-staked instead of sent to your wallet — compounding your position over time.

```bash
curl -X POST "https://inclawbate.com/api/inclawbate/ubi" \
  -H "Content-Type: application/json" \
  -d '{
    "action": "toggle-auto-stake",
    "wallet_address": "0xYourWallet"
  }'
```

## Read Capabilities

### Get Treasury Stats (no params)

Returns the full UBI treasury overview plus top 20 stakers leaderboard.

```bash
curl "https://inclawbate.com/api/inclawbate/staking"
```

**Treasury fields:**

| Field | Description |
|-------|-------------|
| `total_stakers` | Number of unique staking wallets |
| `total_staked` | Total INCLAWNCH staked |
| `tvl_usd` | Total value locked in USD |
| `weekly_distribution_rate` | INCLAWNCH distributed per week |
| `daily_distribution_rate` | INCLAWNCH distributed per day |
| `total_distributed` | All-time INCLAWNCH distributed |
| `total_distributed_usd` | All-time USD value distributed |
| `distribution_count` | Number of distributions executed |
| `estimated_apy` | Current estimated staking APY % |
| `wallet_cap_pct` | Max % any single wallet receives per distribution |
| `last_distribution_at` | Timestamp of most recent distribution |

**Top stakers fields:**

| Field | Description |
|-------|-------------|
| `x_handle` | Staker's X/Twitter handle |
| `x_name` | Display name |
| `total_staked` | Total INCLAWNCH staked |
| `staked_usd` | USD value of stake |
| `stake_count` | Number of individual stake transactions |
| `staking_since` | Earliest stake timestamp |

### Get Wallet Position (`?wallet=0x...`)

Returns everything above plus the wallet's specific staking position.

```bash
curl "https://inclawbate.com/api/inclawbate/staking?wallet=0xYourWallet"
```

**Wallet position fields:**

| Field | Description |
|-------|-------------|
| `total_staked` | Wallet's total INCLAWNCH staked |
| `staked_usd` | USD value of wallet's stake |
| `share_pct` | Wallet's share of the total pool (%) |
| `estimated_daily_reward` | Estimated INCLAWNCH received per day |
| `estimated_weekly_reward` | Estimated INCLAWNCH received per week |
| `auto_stake_enabled` | Whether rewards auto-compound |
| `total_rewards_received` | All-time INCLAWNCH rewards earned |
| `give_back_target` | Where overflow rewards go (null/philanthropy/reinvest/split) |
| `active_stakes` | Array of individual stake records |
| `pending_unstakes` | Array of pending withdrawal requests |

## How UBI Staking Works

1. **Stake** — Transfer INCLAWNCH to the deposit wallet on Base, then register via API with the tx hash.
2. **Earn** — Treasury yield from LP fees is distributed daily at 6am EST, proportional to your stake.
3. **Compound** — Enable auto-stake to reinvest rewards automatically.
4. **Unstake** — No lock period. Request anytime, tokens returned within 24 hours.
5. **Give back** — Optionally redirect a portion of rewards to philanthropy orgs via Kingdom.

## Token Info

| Detail | Value |
|--------|-------|
| Token | INCLAWNCH |
| Chain | Base |
| Contract | `0xa1F72459dfA10BAD200Ac160eCd78C6b77a747be` |
| Staking Contract | `0x206C97D4Ecf053561Bd2C714335aAef0eC1105e6` |
| Deposit Wallet | `0xa4d6f012003fe6ad2774a874c8c98ee69d17f286` |
| BaseScan | https://basescan.org/token/0xa1F72459dfA10BAD200Ac160eCd78C6b77a747be |

## Links

- **Skill Spec (JSON):** https://inclawbate.com/api/inclawbate/skill/staking
- **Read Endpoint:** https://inclawbate.com/api/inclawbate/staking
- **Write Endpoint:** https://inclawbate.com/api/inclawbate/ubi
- **UBI Dashboard:** https://inclawbate.com/ubi
- **Skills Directory:** https://inclawbate.com/skills
- **Homepage:** https://inclawbate.com
