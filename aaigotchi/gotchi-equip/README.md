# gotchi-equip

**Equip and manage wearables on your Aavegotchi NFTs on Base mainnet.**

Easily customize your gotchis by equipping wearables, changing loadouts, and optimizing trait bonuses - all from the command line.

## 🎮 Features

- ✅ Equip wearables on any gotchi you own
- ✅ Multi-slot batch equipping
- ✅ Unequip all wearables
- ✅ View currently equipped items
- ✅ Secure Bankr integration
- ✅ Gas-efficient operations

## 📦 Installation

```bash
cd /home/ubuntu/.openclaw/workspace/skills/gotchi-equip
npm install
```

## 🚀 Quick Start

### Equip a Wearable

```bash
bash scripts/equip.sh 9638 right-hand=64
```

### Equip Multiple Wearables

```bash
bash scripts/equip.sh 9638 head=90 pet=151 right-hand=64
```

### View Equipped Wearables

```bash
bash scripts/show-equipped.sh 9638
```

### Unequip Everything

```bash
bash scripts/unequip-all.sh 9638
```

## 🎯 Valid Slots

- `body` - Body wearable
- `face` - Face wearable
- `eyes` - Eyes wearable
- `head` - Head wearable
- `left-hand` - Left hand wearable
- `right-hand` - Right hand wearable
- `pet` - Pet slot wearable
- `background` - Background wearable

## 🛠️ How It Works

1. **Build transaction** using `viem` to encode `equipWearables()` call
2. **Submit via Bankr API** for secure transaction signing
3. **Wait for confirmation** on Base mainnet
4. **Display result** with transaction hash and BaseScan link

## 📋 Requirements

- Node.js with `viem` package
- Bankr API key configured
- Aavegotchi NFT ownership
- Wearables in your wallet

## 🔗 Related Skills

- [aavegotchi-baazaar](https://clawhub.ai) - Buy wearables
- [gotchi-finder](https://clawhub.ai) - View gotchi stats
- [aavegotchi-traits](https://clawhub.ai) - Fetch trait data

## 📖 Documentation

See [SKILL.md](SKILL.md) for detailed documentation.

## 📄 License

MIT

## 👻 Author

aaigotchi - First autonomous Aavegotchi AI
