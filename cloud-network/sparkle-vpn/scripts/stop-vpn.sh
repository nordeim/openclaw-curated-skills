#!/bin/bash
# Sparkle VPN Stop Script

echo "Stopping Sparkle VPN..."

# Kill mihomo processes
pkill -f "mihomo.*19c48c94cbb" 2>/dev/null || true
pkill -x mihomo 2>/dev/null || true

# Also kill Sparkle GUI if running
pkill -x sparkle 2>/dev/null || true

sleep 1

# Verify stopped
if pgrep -x mihomo > /dev/null || pgrep -x sparkle > /dev/null; then
    echo "Force killing remaining processes..."
    pkill -9 -x mihomo 2>/dev/null || true
    pkill -9 -x sparkle 2>/dev/null || true
fi

echo "VPN stopped"

# Show current IP (should be original)
IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "unknown")
echo "Current IP: $IP"
