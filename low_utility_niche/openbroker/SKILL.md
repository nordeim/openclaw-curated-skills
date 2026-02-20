---
name: openbroker
description: Hyperliquid trading CLI. Execute market orders, limit orders, manage positions, view funding rates, and run trading strategies. Use for any Hyperliquid perp trading task.
license: MIT
compatibility: Requires Node.js 22+, network access to api.hyperliquid.xyz
homepage: https://www.npmjs.com/package/openbroker
metadata: {"author": "monemetrics", "version": "1.0.39", "openclaw": {"requires": {"bins": ["openbroker"], "env": ["HYPERLIQUID_PRIVATE_KEY"]}, "primaryEnv": "HYPERLIQUID_PRIVATE_KEY", "install": [{"id": "node", "kind": "node", "package": "openbroker", "bins": ["openbroker"], "label": "Install openbroker (npm)"}]}}
allowed-tools: Bash(openbroker:*) Bash(npm:*) Read
---

# Open Broker - Hyperliquid Trading CLI

Execute trading operations on Hyperliquid DEX with builder fee support.

## Installation

```bash
npm install -g openbroker
```

## Quick Start

```bash
# 1. Setup (generates wallet, creates config, approves builder fee)
openbroker setup

# 2. Fund your wallet with USDC on Arbitrum, then deposit at https://app.hyperliquid.xyz/

# 3. Start trading
openbroker account
openbroker buy --coin ETH --size 0.1
```

## Command Reference

### Setup
```bash
openbroker setup              # One-command setup (wallet + config + builder approval)
openbroker approve-builder --check  # Check builder fee status (for troubleshooting)
```

The `setup` command handles everything:
1. Generate new wallet or use existing private key
2. Save config to `~/.openbroker/.env`
3. Automatically approve builder fee (required for trading)

### Account Info
```bash
openbroker account            # Balance, equity, margin
openbroker account --orders   # Include open orders
openbroker positions          # Open positions with PnL
openbroker positions --coin ETH  # Specific coin
```

### Funding Rates
```bash
openbroker funding --top 20   # Top 20 by funding rate
openbroker funding --coin ETH # Specific coin
```

### Markets
```bash
openbroker markets --top 30   # Top 30 main perps
openbroker markets --coin BTC # Specific coin
```

### All Markets (Perps + Spot + HIP-3)
```bash
openbroker all-markets                 # Show all markets
openbroker all-markets --type perp     # Main perps only
openbroker all-markets --type hip3     # HIP-3 perps only
openbroker all-markets --type spot     # Spot markets only
openbroker all-markets --top 20        # Top 20 by volume
```

### Search Markets (Find assets across providers)
```bash
openbroker search --query GOLD    # Find all GOLD markets
openbroker search --query BTC     # Find BTC across all providers
openbroker search --query ETH --type perp  # ETH perps only
```

### Spot Markets
```bash
openbroker spot                   # Show all spot markets
openbroker spot --coin PURR       # Show PURR market info
openbroker spot --balances        # Show your spot balances
openbroker spot --top 20          # Top 20 by volume
```

## Trading Commands

### Market Orders (Quick)
```bash
openbroker buy --coin ETH --size 0.1
openbroker sell --coin BTC --size 0.01
openbroker buy --coin SOL --size 5 --slippage 100  # Custom slippage (bps)
```

### Market Orders (Full)
```bash
openbroker market --coin ETH --side buy --size 0.1
openbroker market --coin BTC --side sell --size 0.01 --slippage 100
```

### Limit Orders
```bash
openbroker limit --coin ETH --side buy --size 1 --price 3000
openbroker limit --coin SOL --side sell --size 10 --price 200 --tif ALO
```

### Set TP/SL on Existing Position
```bash
# Set take profit at $40, stop loss at $30
openbroker tpsl --coin HYPE --tp 40 --sl 30

# Set TP at +10% from entry, SL at entry (breakeven)
openbroker tpsl --coin HYPE --tp +10% --sl entry

# Set only stop loss at -5% from entry
openbroker tpsl --coin ETH --sl -5%

# Partial position TP/SL
openbroker tpsl --coin ETH --tp 4000 --sl 3500 --size 0.5
```

### Trigger Orders (Standalone TP/SL)
```bash
# Take profit: sell when price rises to $40
openbroker trigger --coin HYPE --side sell --size 0.5 --trigger 40 --type tp

# Stop loss: sell when price drops to $30
openbroker trigger --coin HYPE --side sell --size 0.5 --trigger 30 --type sl
```

### Cancel Orders
```bash
openbroker cancel --all           # Cancel all orders
openbroker cancel --coin ETH      # Cancel ETH orders only
openbroker cancel --oid 123456    # Cancel specific order
```

## Advanced Execution

### TWAP (Time-Weighted Average Price)
```bash
# Execute 1 ETH buy over 1 hour (auto-calculates slices)
openbroker twap --coin ETH --side buy --size 1 --duration 3600

# Custom intervals with randomization
openbroker twap --coin BTC --side sell --size 0.5 --duration 1800 --intervals 6 --randomize 20
```

### Scale In/Out (Grid Orders)
```bash
# Place 5 buy orders ranging 2% below current price
openbroker scale --coin ETH --side buy --size 1 --levels 5 --range 2

# Scale out with exponential distribution
openbroker scale --coin BTC --side sell --size 0.5 --levels 4 --range 3 --distribution exponential --reduce
```

### Bracket Order (Entry + TP + SL)
```bash
# Long ETH with 3% take profit and 1.5% stop loss
openbroker bracket --coin ETH --side buy --size 0.5 --tp 3 --sl 1.5

# Short with limit entry
openbroker bracket --coin BTC --side sell --size 0.1 --entry limit --price 100000 --tp 5 --sl 2
```

### Chase Order (Follow Price)
```bash
# Chase buy with ALO orders until filled
openbroker chase --coin ETH --side buy --size 0.5 --timeout 300

# Aggressive chase with tight offset
openbroker chase --coin SOL --side buy --size 10 --offset 2 --timeout 60
```

## Trading Strategies

### Funding Arbitrage
```bash
# Collect funding on ETH if rate > 25% annualized
openbroker funding-arb --coin ETH --size 5000 --min-funding 25

# Run for 24 hours, check every 30 minutes
openbroker funding-arb --coin BTC --size 10000 --duration 24 --check 30 --dry
```

### Grid Trading
```bash
# ETH grid from $3000-$4000 with 10 levels, 0.1 ETH per level
openbroker grid --coin ETH --lower 3000 --upper 4000 --grids 10 --size 0.1

# Accumulation grid (buys only)
openbroker grid --coin BTC --lower 90000 --upper 100000 --grids 5 --size 0.01 --mode long
```

### DCA (Dollar Cost Averaging)
```bash
# Buy $100 of ETH every hour for 24 hours
openbroker dca --coin ETH --amount 100 --interval 1h --count 24

# Invest $5000 in BTC over 30 days with daily purchases
openbroker dca --coin BTC --total 5000 --interval 1d --count 30
```

### Market Making Spread
```bash
# Market make ETH with 0.1 size, 10bps spread
openbroker mm-spread --coin ETH --size 0.1 --spread 10

# Tighter spread with position limit
openbroker mm-spread --coin BTC --size 0.01 --spread 5 --max-position 0.1
```

### Maker-Only MM (ALO orders)
```bash
# Market make using ALO (post-only) orders - guarantees maker rebates
openbroker mm-maker --coin HYPE --size 1 --offset 1

# Wider offset for volatile assets
openbroker mm-maker --coin ETH --size 0.1 --offset 2 --max-position 0.5
```

## Order Types

### Limit Orders vs Trigger Orders

**Limit Orders** (`openbroker limit`):
- Execute immediately if price is met
- Rest on the order book until filled or cancelled
- A limit sell BELOW current price fills immediately (taker)
- NOT suitable for stop losses

**Trigger Orders** (`openbroker trigger`, `openbroker tpsl`):
- Stay dormant until trigger price is reached
- Only activate when price hits the trigger level
- Proper way to set stop losses and take profits
- Won't fill prematurely

### When to Use Each

| Scenario | Command |
|----------|---------|
| Buy at specific price below market | `openbroker limit` |
| Sell at specific price above market | `openbroker limit` |
| Stop loss (exit if price drops) | `openbroker trigger --type sl` |
| Take profit (exit at target) | `openbroker trigger --type tp` |
| Add TP/SL to existing position | `openbroker tpsl` |

## Common Arguments

All commands support `--dry` for dry run (preview without executing).

| Argument | Description |
|----------|-------------|
| `--coin` | Asset symbol (ETH, BTC, SOL, HYPE, etc.) |
| `--side` | Order direction: `buy` or `sell` |
| `--size` | Order size in base asset |
| `--price` | Limit price |
| `--dry` | Preview without executing |
| `--help` | Show command help |

### Order Arguments
| Argument | Description |
|----------|-------------|
| `--trigger` | Trigger price (for trigger orders) |
| `--type` | Trigger type: `tp` or `sl` |
| `--slippage` | Slippage tolerance in bps (for market orders) |
| `--tif` | Time in force: GTC, IOC, ALO |
| `--reduce` | Reduce-only order |

### TP/SL Price Formats
| Format | Example | Description |
|--------|---------|-------------|
| Absolute | `--tp 40` | Price of $40 |
| Percentage up | `--tp +10%` | 10% above entry |
| Percentage down | `--sl -5%` | 5% below entry |
| Entry price | `--sl entry` | Breakeven stop |

## Configuration

Config is loaded from (in priority order):
1. Environment variables
2. `.env` in current directory
3. `~/.openbroker/.env` (global config)

Run `openbroker setup` to create the global config interactively.

| Variable | Required | Description |
|----------|----------|-------------|
| `HYPERLIQUID_PRIVATE_KEY` | Yes | Wallet private key (0x...) |
| `HYPERLIQUID_NETWORK` | No | `mainnet` (default) or `testnet` |
| `HYPERLIQUID_ACCOUNT_ADDRESS` | No | For API wallets |

## Risk Warning

- Always use `--dry` first to preview orders
- Start with small sizes on testnet (`HYPERLIQUID_NETWORK=testnet`)
- Monitor positions and liquidation prices
- Use `--reduce` for closing positions only
