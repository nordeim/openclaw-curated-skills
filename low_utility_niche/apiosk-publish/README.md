# Apiosk Publisher

Publish and manage your own APIs on the Apiosk marketplace. Register your API endpoint, set pricing, and start earning from every request.

## Quick Start

### 1. Register Your API

```bash
./register-api.sh \
  --name "My Weather API" \
  --slug "my-weather-api" \
  --endpoint "https://my-api.com/v1" \
  --price 0.01 \
  --description "Real-time weather data" \
  --wallet "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

### 2. Check Your APIs & Revenue

```bash
./my-apis.sh --wallet "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

### 3. Update Your API

```bash
./update-api.sh \
  --slug "my-weather-api" \
  --price 0.02 \
  --wallet "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"
```

### 4. Test Your API Through the Gateway

```bash
./test-api.sh --slug "my-weather-api"
```

## Requirements

- **Wallet:** You need an Ethereum wallet address (same one used with `apiosk` skill)
- **HTTPS Endpoint:** Your API must be accessible over HTTPS
- **Health Check:** Gateway performs a health check (HEAD/GET request) during registration

## Revenue Split

- **Developer:** 90% (first 100 developers get 95%)
- **Apiosk:** 10% (5% for early adopters)

Earnings accumulate in your developer account and can be withdrawn anytime.

## Features

- ✅ **Auto-approval:** If health check passes, your API goes live immediately
- ✅ **No API keys:** Authentication by wallet address
- ✅ **Flexible pricing:** Set prices between $0.0001 and $10.00 per request
- ✅ **Real-time stats:** Track requests and revenue
- ✅ **Update anytime:** Change endpoint, price, or deactivate

## Security

- All endpoints must use HTTPS
- Wallet ownership verified for all operations
- No plaintext secrets in scripts
- Gateway validates all inputs

## Files

- `register-api.sh` — Register a new API
- `my-apis.sh` — List your APIs and revenue
- `update-api.sh` — Update price/endpoint/status
- `test-api.sh` — Test your API through the gateway
- `SKILL.md` — Full documentation

## Support

- Docs: https://apiosk.com/docs
- Discord: https://discord.gg/apiosk
- Email: hello@apiosk.com
