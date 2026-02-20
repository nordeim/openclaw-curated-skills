#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - Update API
# Update your API configuration

GATEWAY_URL="https://gateway.apiosk.com"
WALLET_FILE="$HOME/.apiosk/wallet.txt"

# Default values
SLUG=""
WALLET=""
ENDPOINT=""
PRICE=""
DESCRIPTION=""
ACTIVE=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --slug)
      SLUG="$2"
      shift 2
      ;;
    --wallet)
      WALLET="$2"
      shift 2
      ;;
    --endpoint)
      ENDPOINT="$2"
      shift 2
      ;;
    --price)
      PRICE="$2"
      shift 2
      ;;
    --description)
      DESCRIPTION="$2"
      shift 2
      ;;
    --active)
      ACTIVE="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 --slug SLUG [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --slug SLUG              API slug to update (required)"
      echo "  --wallet ADDRESS         Ethereum wallet address"
      echo "  --endpoint URL           New endpoint URL (HTTPS required)"
      echo "  --price USD              New price per request (0.0001-10.00)"
      echo "  --description TEXT       New description"
      echo "  --active BOOL            Active status (true/false)"
      echo "  --help                   Show this help"
      exit 0
      ;;
    *)
      echo "Unknown option: $1"
      exit 1
      ;;
  esac
done

# Validate required fields
if [[ -z "$SLUG" ]]; then
  echo "Error: --slug is required"
  echo "Run '$0 --help' for usage"
  exit 1
fi

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

# Validate HTTPS if endpoint provided
if [[ -n "$ENDPOINT" && ! "$ENDPOINT" =~ ^https:// ]]; then
  echo "Error: Endpoint must use HTTPS"
  exit 1
fi

# Build JSON payload (only include fields that were provided)
PAYLOAD_ARGS=("--arg" "wallet" "$WALLET")
JQ_FIELDS="{ owner_wallet: \$wallet"

if [[ -n "$ENDPOINT" ]]; then
  PAYLOAD_ARGS+=("--arg" "endpoint" "$ENDPOINT")
  JQ_FIELDS+=", endpoint_url: \$endpoint"
fi

if [[ -n "$PRICE" ]]; then
  PAYLOAD_ARGS+=("--argjson" "price" "$PRICE")
  JQ_FIELDS+=", price_usd: \$price"
fi

if [[ -n "$DESCRIPTION" ]]; then
  PAYLOAD_ARGS+=("--arg" "description" "$DESCRIPTION")
  JQ_FIELDS+=", description: \$description"
fi

if [[ -n "$ACTIVE" ]]; then
  ACTIVE_BOOL="false"
  if [[ "$ACTIVE" == "true" || "$ACTIVE" == "1" ]]; then
    ACTIVE_BOOL="true"
  fi
  PAYLOAD_ARGS+=("--argjson" "active" "$ACTIVE_BOOL")
  JQ_FIELDS+=", active: \$active"
fi

JQ_FIELDS+=" }"

PAYLOAD=$(jq -n "${PAYLOAD_ARGS[@]}" "$JQ_FIELDS")

echo "Updating API '$SLUG'..."
echo ""

# Make request
RESPONSE=$(curl -s -X POST "$GATEWAY_URL/v1/apis/$SLUG" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD")

# Check if jq can parse response
if ! echo "$RESPONSE" | jq empty 2>/dev/null; then
  echo "Error: Invalid response from gateway"
  echo "$RESPONSE"
  exit 1
fi

# Extract success status
SUCCESS=$(echo "$RESPONSE" | jq -r '.success')

if [[ "$SUCCESS" == "true" ]]; then
  echo "✅ API updated successfully!"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
else
  echo "❌ Update failed"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi
