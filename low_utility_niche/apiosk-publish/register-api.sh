#!/usr/bin/env bash
set -euo pipefail

# Apiosk Publisher - Register API
# Register a new API on the Apiosk marketplace

GATEWAY_URL="https://gateway.apiosk.com"
WALLET_FILE="$HOME/.apiosk/wallet.txt"

# Default values
NAME=""
SLUG=""
ENDPOINT=""
PRICE=""
DESCRIPTION=""
CATEGORY="data"
WALLET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --name)
      NAME="$2"
      shift 2
      ;;
    --slug)
      SLUG="$2"
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
    --category)
      CATEGORY="$2"
      shift 2
      ;;
    --wallet)
      WALLET="$2"
      shift 2
      ;;
    --help)
      echo "Usage: $0 [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --name NAME              API name (required)"
      echo "  --slug SLUG              URL-safe identifier (required)"
      echo "  --endpoint URL           API base URL (HTTPS required) (required)"
      echo "  --price USD              Price per request (0.0001-10.00) (required)"
      echo "  --description TEXT       API description (required)"
      echo "  --category CATEGORY      Category (default: data)"
      echo "  --wallet ADDRESS         Ethereum wallet address"
      echo "  --help                   Show this help"
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

# Validate required fields
if [[ -z "$NAME" || -z "$SLUG" || -z "$ENDPOINT" || -z "$PRICE" || -z "$DESCRIPTION" ]]; then
  echo "Error: Missing required fields"
  echo "Run '$0 --help' for usage"
  exit 1
fi

# Validate HTTPS
if [[ ! "$ENDPOINT" =~ ^https:// ]]; then
  echo "Error: Endpoint must use HTTPS"
  exit 1
fi

# Validate wallet format
if [[ ! "$WALLET" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
  echo "Error: Invalid wallet address format"
  exit 1
fi

# Build JSON payload
PAYLOAD=$(jq -n \
  --arg name "$NAME" \
  --arg slug "$SLUG" \
  --arg endpoint "$ENDPOINT" \
  --argjson price "$PRICE" \
  --arg description "$DESCRIPTION" \
  --arg category "$CATEGORY" \
  --arg wallet "$WALLET" \
  '{
    name: $name,
    slug: $slug,
    endpoint_url: $endpoint,
    price_usd: $price,
    description: $description,
    category: $category,
    owner_wallet: $wallet
  }')

echo "Registering API..."
echo "  Name: $NAME"
echo "  Slug: $SLUG"
echo "  Endpoint: $ENDPOINT"
echo "  Price: \$$PRICE/request"
echo "  Wallet: $WALLET"
echo ""

# Make request
RESPONSE=$(curl -s -X POST "$GATEWAY_URL/v1/apis/register" \
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
  echo "✅ API registered successfully!"
  echo ""
  echo "Gateway URL: $(echo "$RESPONSE" | jq -r '.gateway_url')"
  echo "Status: $(echo "$RESPONSE" | jq -r '.status')"
  echo "Verified: $(echo "$RESPONSE" | jq -r '.verified')"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
  echo ""
  echo "Other agents can now call your API:"
  echo "  curl $(echo "$RESPONSE" | jq -r '.gateway_url')"
else
  echo "❌ Registration failed"
  echo ""
  echo "$(echo "$RESPONSE" | jq -r '.message')"
  exit 1
fi
