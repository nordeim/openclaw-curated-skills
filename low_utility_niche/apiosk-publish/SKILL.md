---
name: apiosk-publish
displayName: Apiosk Publisher
version: 1.0.0
category: api
tags: [api, marketplace, monetization, web3]
author: Apiosk
requires:
  bins: [curl, jq]
security:
  level: benign
  no_curl_bash: true
---

# Apiosk Publisher

Publish and manage your own APIs on the Apiosk marketplace. Turn any HTTPS endpoint into a paid API and start earning from every request.

## Overview

**Apiosk Publisher** lets you:
- Register your API endpoint on the Apiosk gateway
- Set your own pricing ($0.0001 - $10.00 per request)
- Earn 90% of every paid request (first 100 devs get 95%)
- Manage your APIs (update pricing, endpoint, deactivate)
- Track requests and revenue in real-time

## Quick Start

### 1. Register Your API

```bash
./register-api.sh \
  --name "My Weather API" \
  --slug "my-weather-api" \
  --endpoint "https://my-api.com/v1" \
  --price 0.01 \
  --description "Real-time weather data for 200+ cities" \
  --category "data" \
  --wallet "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

**What happens:**
1. Gateway validates your endpoint (HTTPS only)
2. Performs a health check (HEAD/GET request)
3. If healthy, your API goes live immediately
4. Returns your gateway URL: `https://gateway.apiosk.com/my-weather-api`

### 2. Check Your APIs & Revenue

```bash
./my-apis.sh --wallet "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

**Output:**
```json
{
  "apis": [
    {
      "id": "uuid",
      "slug": "my-weather-api",
      "name": "My Weather API",
      "endpoint_url": "https://my-api.com/v1",
      "price_usd": 0.01,
      "active": true,
      "verified": true,
      "total_requests": 1523,
      "total_earned_usd": 13.71,
      "pending_withdrawal_usd": 13.71
    }
  ],
  "total_earnings_usd": 13.71
}
```

### 3. Update Your API

```bash
# Update price
./update-api.sh --slug "my-weather-api" --price 0.02 --wallet "0x..."

# Update endpoint
./update-api.sh --slug "my-weather-api" --endpoint "https://new-endpoint.com" --wallet "0x..."

# Deactivate
./update-api.sh --slug "my-weather-api" --active false --wallet "0x..."
```

### 4. Test Your API

```bash
./test-api.sh --slug "my-weather-api"
```

This makes a GET request through the gateway to verify it's working.

## Commands

### `register-api.sh`

Register a new API on the Apiosk marketplace.

**Usage:**
```bash
./register-api.sh [OPTIONS]
```

**Options:**
- `--name NAME` — Human-readable API name (required)
- `--slug SLUG` — URL-safe identifier (lowercase, alphanumeric, hyphens only) (required)
- `--endpoint URL` — Your API base URL (HTTPS required) (required)
- `--price USD` — Price per request in USD (0.0001 - 10.00) (required)
- `--description TEXT` — API description (required)
- `--category CATEGORY` — Category (default: "data")
- `--wallet ADDRESS` — Your Ethereum wallet address (required)

**Example:**
```bash
./register-api.sh \
  --name "Crypto Prices" \
  --slug "crypto-prices" \
  --endpoint "https://my-api.com" \
  --price 0.005 \
  --description "Real-time crypto prices" \
  --wallet "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

**Returns:**
```json
{
  "success": true,
  "api_id": "uuid",
  "slug": "crypto-prices",
  "gateway_url": "https://gateway.apiosk.com/crypto-prices",
  "status": "active",
  "verified": true,
  "health_check_passed": true,
  "message": "API registered and verified. It's live!"
}
```

### `my-apis.sh`

List all your registered APIs and revenue stats.

**Usage:**
```bash
./my-apis.sh --wallet "0x..."
```

**Returns:**
```json
{
  "apis": [...],
  "total_earnings_usd": 42.50
}
```

### `update-api.sh`

Update your API configuration.

**Usage:**
```bash
./update-api.sh --slug SLUG [OPTIONS]
```

**Options:**
- `--slug SLUG` — API slug to update (required)
- `--wallet ADDRESS` — Your wallet address (required)
- `--endpoint URL` — New endpoint URL (optional)
- `--price USD` — New price (optional)
- `--description TEXT` — New description (optional)
- `--active BOOL` — Active status (true/false) (optional)

**Example:**
```bash
./update-api.sh \
  --slug "my-weather-api" \
  --price 0.02 \
  --wallet "0x..."
```

### `test-api.sh`

Test your API through the gateway.

**Usage:**
```bash
./test-api.sh --slug SLUG [--path PATH] [--method METHOD]
```

**Options:**
- `--slug SLUG` — API slug to test (required)
- `--path PATH` — Path to test (default: "/")
- `--method METHOD` — HTTP method (default: "GET")

**Example:**
```bash
./test-api.sh --slug "my-weather-api" --path "/weather/london"
```

## How It Works

### Registration Flow

1. **Submit registration** → Gateway receives your API details
2. **Validation** → Checks slug uniqueness, HTTPS, price range, wallet format
3. **Health check** → Gateway performs HEAD/GET request to your endpoint
4. **Auto-approval** → If healthy, API is immediately active and verified
5. **Gateway URL** → Your API is now accessible at `gateway.apiosk.com/{slug}`

### Payment Flow

When someone calls your API:

1. **Request arrives** → User calls `gateway.apiosk.com/your-api/path`
2. **Payment verification** → Gateway checks x402 payment proof
3. **Proxy request** → Gateway forwards to your endpoint
4. **Revenue split** → 90% to you, 10% to Apiosk (95/5 for first 100 devs)
5. **Balance credit** → Your earnings are credited in real-time

### Revenue Tracking

- Every paid request is logged with commission split
- Revenue accumulates in your developer balance
- Check earnings anytime with `my-apis.sh`
- Withdraw feature coming soon

## Configuration

### Wallet Setup

Your wallet address is read from `~/.apiosk/wallet.txt` (same as `apiosk` skill).

If not set up yet:

```bash
echo "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb" > ~/.apiosk/wallet.txt
```

Or pass `--wallet` to every command.

### Endpoint Requirements

Your API endpoint must:
- ✅ Use HTTPS (HTTP is rejected)
- ✅ Respond to HEAD or GET requests (for health check)
- ✅ Return 2xx status code for health check
- ✅ Be publicly accessible

### Pricing Guidelines

- **Minimum:** $0.0001 per request
- **Maximum:** $10.00 per request
- **Recommended:** $0.001 - $0.05 for most APIs
- **High-value APIs:** $0.10 - $1.00 (AI models, premium data)

## Revenue Model

### Commission Split

| Tier | Developer Share | Apiosk Fee |
|------|----------------|------------|
| First 100 developers | 95% | 5% |
| Standard | 90% | 10% |

*Early adopters get better rates to kickstart the marketplace.*

### Example Earnings

If your API gets **1000 requests/day** at **$0.01/request**:

- **Gross revenue:** $10/day = $300/month
- **Your share (90%):** $9/day = $270/month
- **Apiosk fee (10%):** $1/day = $30/month

## Security

### Network Access

This skill communicates only with:
- `https://gateway.apiosk.com`

### Data Access

- **Reads:** `~/.apiosk/wallet.txt`
- **Writes:** None

### No Secrets

- No private keys accessed
- Wallet address is public information
- All communication over HTTPS

See [SECURITY.md](SECURITY.md) for full details.

## Troubleshooting

### Health Check Failed

**Problem:** Registration succeeds but API is marked inactive.

**Solutions:**
1. Ensure your endpoint returns 2xx status for HEAD/GET `/`
2. Check endpoint is publicly accessible (not localhost)
3. Verify SSL certificate is valid
4. Update endpoint after fixing: `./update-api.sh --slug your-api --endpoint https://...`

### Wallet Ownership Error

**Problem:** "Unauthorized: wallet address does not match API owner"

**Solution:** Ensure you're using the same wallet address that registered the API.

### Slug Already Taken

**Problem:** "API slug 'xyz' already registered"

**Solution:** Choose a different slug. Slugs are globally unique.

### Price Validation Error

**Problem:** "Price must be between 0.0001 and 10.00 USD"

**Solution:** Set a price within the allowed range.

## Examples

### Simple Data API

```bash
./register-api.sh \
  --name "US Zip Codes" \
  --slug "us-zip-codes" \
  --endpoint "https://api.example.com/v1" \
  --price 0.001 \
  --description "Lookup US zip code data" \
  --category "data" \
  --wallet "0x..."
```

### AI Model API

```bash
./register-api.sh \
  --name "Image Classifier" \
  --slug "image-classifier-v2" \
  --endpoint "https://ml.example.com/api" \
  --price 0.10 \
  --description "Classify images with 99% accuracy" \
  --category "ai" \
  --wallet "0x..."
```

### Weather API

```bash
./register-api.sh \
  --name "Global Weather" \
  --slug "global-weather" \
  --endpoint "https://weather.example.com" \
  --price 0.005 \
  --description "Real-time weather for any location" \
  --category "data" \
  --wallet "0x..."
```

## FAQ

### Q: Do I need to modify my existing API?

**A:** No! Just register your endpoint. Apiosk handles payment verification and proxies requests to your API.

### Q: How do I get paid?

**A:** Earnings accumulate in your developer balance. Withdrawal feature coming soon (direct to wallet).

### Q: Can I change my price after registration?

**A:** Yes, anytime with `./update-api.sh --price NEW_PRICE`.

### Q: What if my endpoint goes down?

**A:** Requests will fail. Users see error responses. Deactivate your API during maintenance: `./update-api.sh --active false`.

### Q: Can I register multiple APIs?

**A:** Yes! Register as many as you want with different slugs.

### Q: Is there a listing fee?

**A:** No. Registration is free. We only take commission on paid requests.

### Q: Do I need to run a blockchain node?

**A:** No. Payment settlement happens via Apiosk's x402 facilitator.

## Support

- **Docs:** https://apiosk.com/docs
- **Discord:** https://discord.gg/apiosk
- **Email:** hello@apiosk.com
- **GitHub:** https://github.com/apiosk

## License

MIT

---

Built with ❤️ by the Apiosk team
