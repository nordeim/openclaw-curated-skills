#!/bin/bash
# Sparkle VPN Start Script - Using Mihomo Core directly

set -e

echo "Starting Sparkle VPN (Mihomo core)..."

# Check if already running
if pgrep -f "mihomo.*19c48c94cbb" > /dev/null; then
    echo "VPN is already running"
    exit 0
fi

# Kill any existing mihomo processes
pkill mihomo 2>/dev/null || true
sleep 1

# Start mihomo core directly with the DirectACCESS profile
nohup /opt/sparkle/resources/sidecar/mihomo \
    -f ~/.config/sparkle/profiles/19c48c94cbb.yaml \
    -d ~/.config/sparkle/ \
    > /tmp/mihomo.log 2>&1 &

sleep 2

# Verify it's running
if pgrep -f "mihomo.*19c48c94cbb" > /dev/null; then
    echo "VPN started successfully on port 7890"
    # Test connection
    export https_proxy=http://127.0.0.1:7890
    IP=$(curl -s --max-time 5 https://ipinfo.io/ip 2>/dev/null || echo "unknown")
    echo "Current IP: $IP"
else
    echo "ERROR: Failed to start VPN"
    exit 1
fi
