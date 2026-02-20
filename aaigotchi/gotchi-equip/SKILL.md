---
name: gotchi-equip
description: >
  Equip and manage wearables on your Aavegotchi NFTs on Base mainnet.
  Dress up your gotchis, optimize traits, and manage loadouts with ease.
homepage: https://github.com/aaigotchi/gotchi-equip-skill
metadata:
  openclaw:
    requires:
      bins:
        - node
        - jq
        - curl
      env: []
---

# gotchi-equip

**Equip and manage wearables on your Aavegotchi NFTs.**

Easily customize your gotchis by equipping wearables, changing loadouts, and optimizing trait bonuses - all from the command line via Bankr integration.

## Features

- ✅ **Equip wearables** - Dress up your gotchis with purchased wearables
- ✅ **Multi-slot support** - Equip multiple wearables in one transaction
- ✅ **Unequip all** - Strip gotchi naked for trading/selling
- ✅ **View equipped** - See current wearable loadout
- ✅ **Bankr integration** - Secure transaction signing via Bankr API
- ✅ **Gas efficient** - Batch equip/unequip operations

## Requirements

- **Bankr API key** configured at `~/.openclaw/skills/bankr/config.json`
- **Node.js** with `viem` package
- **gotchi-finder** skill (optional, for viewing equipped wearables)

## Installation

```bash
cd /home/ubuntu/.openclaw/workspace/skills/gotchi-equip
npm install
```

## Usage

### Equip Wearables

Equip one or more wearables on your gotchi:

```bash
# Equip single wearable
bash scripts/equip.sh 9638 right-hand=64

# Equip multiple wearables
bash scripts/equip.sh 9638 head=90 pet=151 right-hand=64

# Equip full loadout
bash scripts/equip.sh 9638 body=1 head=90 left-hand=65 right-hand=64 pet=151
```

**Valid slots:**
- `body` - Body wearable
- `face` - Face wearable
- `eyes` - Eyes wearable
- `head` - Head wearable
- `left-hand` - Left hand wearable
- `right-hand` - Right hand wearable
- `pet` - Pet slot wearable
- `background` - Background wearable

### View Equipped Wearables

See what's currently equipped on your gotchi:

```bash
bash scripts/show-equipped.sh 9638
```

Example output:
```
👻 Fetching Equipped Wearables for Gotchi #9638

===================================================================
Gotchi: #9638 "aaigotchi"

🎭 Equipped Wearables:

   Right Hand: Wearable ID 64

===================================================================
```

### Unequip All Wearables

Remove all equipped wearables (useful before trading/selling):

```bash
bash scripts/unequip-all.sh 9638
```

## How It Works

1. **Build transaction** - Uses `viem` to encode `equipWearables()` function call
2. **Submit via Bankr** - Sends transaction to Bankr API for signing
3. **Confirm on-chain** - Waits for transaction confirmation
4. **Return result** - Displays transaction hash and BaseScan link

## Slot Positions

Wearables are stored as a 16-element array:

| Index | Slot | Description |
|-------|------|-------------|
| 0 | body | Body wearable |
| 1 | face | Face wearable |
| 2 | eyes | Eyes wearable |
| 3 | head | Head wearable |
| 4 | left-hand | Left hand wearable |
| 5 | right-hand | Right hand wearable |
| 6 | pet | Pet slot wearable |
| 7 | background | Background wearable |
| 8-15 | (reserved) | Future slots |

## Transaction Safety

- **Simulation** - All transactions are simulated before submission
- **Bankr signing** - Private keys never leave Bankr's secure environment
- **Confirmation wait** - Scripts wait for on-chain confirmation
- **Error handling** - Clear error messages for failed transactions

## Examples

### Equip Common Wizard Staff

```bash
bash scripts/equip.sh 9638 right-hand=64
```

### Dress Up Gotchi

```bash
# Full outfit
bash scripts/equip.sh 9638 \
  head=90 \
  body=1 \
  left-hand=65 \
  right-hand=64 \
  pet=151
```

### Strip for Trading

```bash
# Remove all wearables
bash scripts/unequip-all.sh 9638
```

## Related Skills

- **aavegotchi-baazaar** - Buy wearables from marketplace
- **gotchi-finder** - View gotchi stats and images
- **aavegotchi-traits** - Fetch gotchi trait data

## Chain Configuration

- **Chain:** Base mainnet (8453)
- **Contract:** 0xA99c4B08201F2913Db8D28e71d020c4298F29dBF (Aavegotchi Diamond)
- **Function:** `equipWearables(uint256 _tokenId, uint16[16] _wearablesToEquip)`

## Troubleshooting

**❌ "Bankr config not found"**
- Install and configure the Bankr skill first
- Config location: `~/.openclaw/skills/bankr/config.json`

**❌ "Invalid slot name"**
- Use valid slot names: body, face, eyes, head, left-hand, right-hand, pet, background
- Slots are case-sensitive (use lowercase with hyphens)

**❌ "Transaction failed"**
- Check you own the wearable in your wallet
- Verify wearable ID is correct
- Ensure wearable is compatible with that slot

## License

MIT

## Author

aaigotchi 👻
