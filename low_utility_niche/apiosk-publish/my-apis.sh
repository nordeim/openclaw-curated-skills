#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - My APIs
# List your registered APIs and revenue stats

GATEWAY_URL="https://gateway.apiosk.com"
WALLET_FILE="$HOME/.apiosk/wallet.txt"

WALLET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --wallet)
      WALLET="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --wallet ADDRESS    Ethereum wallet address"
      echo "  --help              Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Get wallet from file if not provided
if [[ -z "$WALLET" ]]; then
  if [[ -f "$WALLET_FILE" ]]; then
    WALLET=$(cat "$WALLET_FILE")
  else
    echo "Error: Wallet not found. Set up wallet:"
    echo "  echo \"0xYourAddress\" > $WALLET_FILE"
    echo "Or pass --wallet flag"
    exit 1
  fi
fi

# Validate wallet format
if [[ ! "$WALLET" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
  echo "Error: Invalid wallet address format"
  exit 1
fi

echo "Fetching your APIs..."
echo ""

# Make request
RESPONSE=$(curl -s "$GATEWAY_URL/v1/apis/mine?wallet=$WALLET")

# Check if jq can parse response
if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
  echo "Error: Invalid response from gateway"
  echo "$RESPONSE"
  exit 1
fi

# Count APIs
API_COUNT=$(echo "$RESPONSE" | jq '.apis | length')
TOTAL_EARNINGS=$(echo "$RESPONSE" | jq -r '.total_earnings_usd')

if [[ "$API_COUNT" -eq 0 ]]; then
  echo "No APIs registered yet."
  echo ""
  echo "Register your first API:"
  echo "  ./register-api.sh --help"
  exit 0
fi

echo "📊 Your APIs ($API_COUNT total)"
echo "💰 Total Earnings: \$$TOTAL_EARNINGS USD"
echo ""

# Display each API
echo "$RESPONSE" | jq -r '.apis[] | 
  "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n" +
  "🔹 \(.name) (\(.slug))\n" +
  "   Gateway: https://gateway.apiosk.com/\(.slug)\n" +
  "   Endpoint: \(.endpoint_url)\n" +
  "   Price: $\(.price_usd)/request\n" +
  "   Status: " + (if .active then "✅ Active" else "⏸  Inactive" end) + 
  " | " + (if .verified then "✓ Verified" else "⚠ Unverified" end) + "\n" +
  "   Requests: \(.total_requests)\n" +
  "   Earned: $\(.total_earned_usd) USD\n" +
  "   Pending: $\(.pending_withdrawal_usd) USD\n"'

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Update an API: ./update-api.sh --slug SLUG --help"
