# Clawlett

Secure token swaps and Trenches trading on **Base Mainnet**, powered by Safe + Zodiac Roles.

Swap engine: **CoW Protocol** (MEV-protected batch auctions).
Token creation & bonding curve trading: **Trenches** (via AgentKeyFactoryV3).

> **Network: Base Mainnet (Chain ID: 8453)**

## Overview

This skill enables autonomous token swaps and Trenches token creation/trading through a Gnosis Safe. The agent operates through Zodiac Roles which restricts operations to:
- Swapping tokens via CoW Protocol (MEV-protected)
- Creating tokens on Trenches bonding curves
- Buying and selling tokens on Trenches bonding curves
- Approving tokens for CoW Vault Relayer
- Presigning CoW orders via ZodiacHelpers delegatecall
- Wrapping ETH to WETH and unwrapping WETH to ETH via ZodiacHelpers
- Sending swapped tokens only back to the Safe (no draining)

## Capabilities

| Action | Autonomous | Notes |
|--------|------------|-------|
| Check balances | ✅ | ETH and any ERC20 on Base Mainnet |
| Get swap quote | ✅ | Via CoW Protocol |
| Swap tokens | ✅ | Any pair with liquidity |
| Wrap/Unwrap ETH | ✅ | ETH ↔ WETH via ZodiacHelpers |
| Approve tokens | ✅ | Only for CoW Vault Relayer |
| Create token (Trenches) | ✅ | Via AgentKeyFactoryV3 bonding curve |
| Buy tokens (Trenches) | ✅ | Buy with ETH on bonding curve |
| Sell tokens (Trenches) | ✅ | Sell for ETH on bonding curve |
| Token info | ✅ | Fetch token details from Trenches API |
| Token discovery | ✅ | Trending, new, top volume, gainers, losers |
| Transfer funds | ❌ | Blocked by Roles |

## Agent Name (CNS)

Each agent can optionally register a **unique name** via the Clawlett Name Service (CNS). This name is the agent's app-wide identifier — no two agents can share the same name. The name is minted as an NFT on Base.

Pass `--name` during initialization to register a CNS name. If omitted, CNS registration is skipped. Once registered, it cannot be changed.

## Token Safety

### Verified Tokens

Protected tokens can ONLY resolve to verified Base Mainnet addresses:

| Token | Verified Address |
|-------|--------------------|
| ETH | Native ETH (`0x0000000000000000000000000000000000000000`) |
| WETH | `0x4200000000000000000000000000000000000006` |
| USDC | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| USDT | `0xfde4C96c8593536E31F229EA8f37b2ADa2699bb2` |
| DAI | `0x50c5725949A6F0c72E6C4a641F24049A917DB0Cb` |
| USDS | `0x820C137fa70C8691f0e44Dc420a5e53c168921Dc` |
| AERO | `0x940181a94A35A4569E4529A3CDfB74e38FD98631` |
| cbBTC | `0xcbB7C0000aB88B473b1f5aFd9ef808440eed33Bf` |
| VIRTUAL | `0x0b3e328455c4059EEb9e3f84b5543F74E24e7E1b` |
| DEGEN | `0x4ed4E862860beD51a9570b96d89aF5E1B0Efefed` |
| BRETT | `0x532f27101965dd16442E59d40670FaF5eBB142E4` |
| TOSHI | `0xAC1Bd2486aAf3B5C0fc3Fd868558b082a531B2B4` |
| WELL | `0xA88594D404727625A9437C3f886C7643872296AE` |
| BID | `0xa1832f7f4e534ae557f9b5ab76de54b1873e498b` |

If a scam token impersonates these symbols, the agent will detect and warn.

### Unverified Token Search

Tokens not in the verified list are searched via DexScreener (Base pairs). Search results include:
- Contract address (on-chain verified)
- 24h trading volume and liquidity
- DEX where the token trades

**Agent behavior for unverified tokens:**
- Always display the warning with contract address, volume, and liquidity
- Ask the user to confirm before proceeding with the swap
- Never silently swap an unverified token

## Setup

1. Owner provides their wallet address (and optionally an **agent name**)
2. Agent generates keypair → **Owner sends 0.001 ETH on Base Mainnet** to agent for gas
3. Agent deploys Safe on Base Mainnet (owner as sole owner)
4. Agent registers with backend and optionally mints CNS name on-chain (if `--name` provided)
5. Agent deploys Zodiac Roles with swap permissions
6. Agent removes itself as Safe owner (keeps Roles access)
7. **Owner funds Safe on Base Mainnet** with tokens to trade

## Usage

### Initialize
```
Initialize my wallet with owner 0x123...
Initialize my wallet with owner 0x123... and name MYAGENT
```

### Check Balance
```
What's my balance?
How much USDC do I have?
```

### Swap Tokens
```
Swap 0.1 ETH for USDC
Swap 100 USDC for ETH
Exchange 50 DAI to AERO
```

CoW Protocol swaps are MEV-protected. ETH is automatically wrapped to WETH when needed (CoW requires ERC20s). Wrapping is bundled into the swap transaction.

### Wrap/Unwrap ETH
```
Wrap 0.5 ETH to WETH
Unwrap 0.5 WETH to ETH
```

Wrapping and unwrapping is done via ZodiacHelpers delegatecall. When swapping from ETH via CoW, wrapping is handled automatically as part of the swap transaction.

### Trenches Trading

Trenches enables token creation and bonding curve trading on Base. Tokens are created via the AgentKeyFactoryV3 contract and traded on Uniswap V3-style bonding curves.

All on-chain operations go through ZodiacHelpers wrapper functions (`createViaFactory`, `tradeViaFactory`) which validate the factory address and forward calls with explicit `ethValue` (since `msg.value` doesn't work in delegatecall).

```
Create a token called "My Token" with symbol MTK
Create a token paired with BID (default base token)
Create a token with anti-bot disabled and an initial buy
Buy 0.01 ETH worth of MTK on Trenches
Sell all my MTK tokens
What's trending on Trenches?
Show me the top gainers
Get info on MTK token
```

**IMPORTANT — Token creation parameter collection:**
When a user asks to create a token, the agent MUST collect ALL of the following parameters before executing. If the user's request is missing any of these, ask them to provide the missing values. Do NOT use defaults silently — always confirm each parameter with the user.

| Parameter | Required | Description |
|-----------|----------|-------------|
| Name | **Yes** | The token name (e.g., "My Token") |
| Symbol | **Yes** | The token ticker symbol (e.g., MTK) |
| Description | **Yes** | A description of the token |
| Image | **Yes** | Path to a token image file (PNG/JPEG/WEBP, max 4MB) |
| Base token | No | `BID` (default) or `ETH` — which token to pair with |
| Anti-bot protection | No | ON by default (10-minute sniper protection). Ask user if they want it enabled or disabled |
| Initial buy | No | Amount of ETH to buy immediately after creation (only works with anti-bot OFF) |
| Twitter | No | Twitter/X handle for the token |
| Website | No | Website URL for the token |
| Team allocation | No | SSL team positions that the team can claim after the price moves beyond a given position |

The agent should present the user with a summary of all parameters (including defaults) and ask for confirmation before executing the creation.

**Token creation defaults:**
- Base token: BID (use `--base-token ETH` for ETH pairing)
- Anti-bot protection: ON (10-minute sniper protection window)
- Initial buy is blocked when anti-bot is enabled (agent can't buy during protection window)
- Use `--no-antibot` to disable protection and allow initial buy
- Use `--image` to attach a custom token image (PNG/JPEG/WEBP, max 4MB)

**Image upload flow:**
- Images are uploaded to `/api/skill/image` before token creation
- The returned `imageUrl` is passed to the token creation API
- If image upload fails, the token creation will fail (image is required)

**Anti-bot protection and buying:**
- The agent cannot buy any token that has anti-bot protection currently active (within the 10-minute window after creation)
- This applies to all tokens, not just ones the agent created
- Both the client and backend enforce this — the backend will refuse to issue a swap signature for protected tokens
- Wait for the protection window to expire before buying

The agent will:
1. Upload token image via `/api/skill/image` (returns `imageUrl`)
2. Get creation signature from `/api/skill/token/create` (includes `imageUrl`)
3. **Display token details for confirmation**
4. Execute via Safe + Roles (ZodiacHelpers delegatecall)
5. **After creation, share the token page URL:** `https://trenches.bid/tokens/[address]`

The agent will:
1. Resolve token symbols (with scam protection)
2. Get quote from CoW Protocol
3. **Display swap details for confirmation:**
   - Token symbols (e.g., ETH → USDC)
   - Token addresses (verified Base Mainnet contracts)
   - Input amount (what you're selling)
   - Output amount (estimated amount you'll receive)
   - Fee breakdown
   - ETH wrap amount (if applicable)
4. Ask for explicit user confirmation
5. Execute via Safe + Roles

## Scripts

| Script | Description |
|--------|-------------|
| `initialize.js` | Deploy Safe + Roles, register CNS name |
| `swap.js` | Swap tokens via CoW Protocol (MEV-protected) |
| `balance.js` | Check ETH and token balances |
| `trenches.js` | Create tokens and trade on Trenches bonding curves |

### Examples

```bash
# Initialize (name is optional, registers on CNS if provided)
node scripts/initialize.js --owner 0x123...
node scripts/initialize.js --owner 0x123... --name MYAGENT

# Check balance
node scripts/balance.js
node scripts/balance.js --token USDC

# Swap tokens (CoW Protocol, MEV-protected)
node scripts/swap.js --from ETH --to USDC --amount 0.1
node scripts/swap.js --from USDC --to WETH --amount 100 --execute
node scripts/swap.js --from USDC --to DAI --amount 50 --execute --timeout 600

# With custom slippage (0-0.5 range, e.g., 0.05 = 5%)
node scripts/swap.js --from ETH --to USDC --amount 0.1 --slippage 0.03 --execute

# Trenches: Create a token (BID base token by default, anti-bot ON)
node scripts/trenches.js create --name "My Token" --symbol MTK --description "A cool token"
node scripts/trenches.js create --name "My Token" --symbol MTK --description "desc" --base-token ETH
node scripts/trenches.js create --name "My Token" --symbol MTK --description "desc" --no-antibot --initial-buy 0.01
node scripts/trenches.js create --name "My Token" --symbol MTK --description "desc" --image ./logo.png

# Trenches: Buy/sell tokens
node scripts/trenches.js buy --token MTK --amount 0.01
node scripts/trenches.js sell --token MTK --amount 1000
node scripts/trenches.js sell --token MTK --all

# Trenches: Token info and discovery
node scripts/trenches.js info MTK
node scripts/trenches.js trending
node scripts/trenches.js trending --window 1h --limit 5
node scripts/trenches.js new
node scripts/trenches.js top-volume
node scripts/trenches.js gainers
node scripts/trenches.js losers
```

## Configuration

Scripts read from `config/wallet.json` (configured for Base Mainnet):

```json
{
  "chainId": 8453,
  "owner": "0x...",
  "agent": "0x...",
  "safe": "0x...",
  "roles": "0x...",
  "roleKey": "0x...",
  "name": "MYAGENT",
  "cnsTokenId": 1
}
```

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BASE_RPC_URL` | `https://mainnet.base.org` | Base Mainnet RPC endpoint |
| `WALLET_CONFIG_DIR` | `config` | Config directory |
| `TRENCHES_API_URL` | `https://trenches.bid` | Trenches API endpoint |

## Contracts (Base Mainnet)

| Contract | Address | Description |
|----------|---------|-------------|
| Safe Singleton | `0x3E5c63644E683549055b9Be8653de26E0B4CD36E` | Safe L2 impl |
| CoW Settlement | `0x9008D19f58AAbD9eD0D60971565AA8510560ab41` | CoW Protocol settlement |
| CoW Vault Relayer | `0xC92E8bdf79f0507f65a392b0ab4667716BFE0110` | CoW token allowance target |
| ZodiacHelpers | `0xb34a6210013977FC7D6082287e03915a66249799` | Approvals, CoW presign, WETH wrap/unwrap, Trenches factory wrappers via delegatecall |
| AgentKeyFactoryV3 | `0x2EA0010c18fa7239CAD047eb2596F8d8B7Cf2988` | Trenches token creation and bonding curve trading |
| Safe Factory | `0xa6B71E26C5e0845f74c812102Ca7114b6a896AB2` | Safe deployer |
| Roles Singleton | `0x9646fDAD06d3e24444381f44362a3B0eB343D337` | Zodiac Roles |
| Module Factory | `0x000000000000aDdB49795b0f9bA5BC298cDda236` | Module deployer |
| CNS | `0x299319e0BC8d67e11AD8b17D4d5002033874De3a` | Clawlett Name Service (unique agent names) |

## Updating

When the user says **"update to latest"**, follow this procedure:

1. `git fetch --tags origin` in the clawlett repo
2. Read current version from `scripts/package.json`
3. Identify the latest git tag (e.g., `git tag -l --sort=-v:refname | head -1`)
4. Read **[MIGRATION_GUIDE.md](./MIGRATION_GUIDE.md)** for the migration path between current and latest version
5. Show the user: current version, new version, summary of changes, and whether on-chain steps are required
6. **ASK the user: "Do you want to proceed with this update?"** — do NOT proceed without explicit confirmation
7. If confirmed: `git checkout <tag>`, then walk through each migration step with the user

Some updates are code-only (just checkout the new tag). Others require on-chain transactions signed by the Safe owner (e.g., updating Roles permissions for a new ZodiacHelpers contract). The migration guide specifies which.

## Security Model

1. **Safe holds all funds** - Agent wallet only has gas
2. **Zodiac Roles restricts operations**:
   - Can only interact with ZodiacHelpers
   - ZodiacHelpers scoped with `allowTarget` (Send + DelegateCall)
   - Can only approve tokens for CoW Vault Relayer
3. **No transfer/withdraw** - Agent cannot move funds out
4. **Scam protection** - Common tokens resolve to verified addresses only
5. **MEV protection** - CoW Protocol batches orders, preventing sandwich attacks and other MEV extraction
