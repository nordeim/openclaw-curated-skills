---
name: sparkle-vpn
description: Control Sparkle VPN - start and stop VPN connections using Mihomo core directly.
---

# Sparkle VPN Control

This skill provides tools to control the Sparkle VPN using Mihomo core directly (no GUI interaction needed).

## Tools

- `sparkle_vpn_start` - Start VPN using Mihomo core with DirectACCESS profile
- `sparkle_vpn_stop` - Stop VPN and kill all related processes

## Implementation

Uses Mihomo core directly:
- Profile: `~/.config/sparkle/profiles/19c48c94cbb.yaml`
- Proxy port: `7890` (HTTP/HTTPS)
- Config dir: `~/.config/sparkle/`

## Usage

Start VPN:
```bash
bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/start-vpn.sh
```

Stop VPN:
```bash
bash /home/admin/.openclaw/workspace/skills/sparkle-vpn/scripts/stop-vpn.sh
```
