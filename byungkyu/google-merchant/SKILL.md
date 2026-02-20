---
name: google-merchant
description: |
  Google Merchant Center API integration with managed OAuth. Manage products, inventories, data sources, promotions, and reports for Google Shopping.
  Use this skill when users want to manage their Merchant Center product catalog, check product status, configure data sources, or analyze shopping performance.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    requires:
      env:
        - MATON_API_KEY
---

# Google Merchant Center

Access the Google Merchant Center API with managed OAuth authentication. Manage products, inventories, promotions, data sources, and reports for Google Shopping.

## Quick Start

```bash
# List products in your Merchant Center account
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-merchant/products/v1/accounts/{accountId}/products')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/google-merchant/{sub-api}/{version}/accounts/{accountId}/{resource}
```

The Merchant API uses a modular sub-API structure. Replace:
- `{sub-api}` with the service: `products`, `accounts`, `datasources`, `reports`, `promotions`, `inventories`, `notifications`, `conversions`, `lfp`
- `{version}` with `v1` (stable) or `v1beta`
- `{accountId}` with your Merchant Center account ID

The gateway proxies requests to `merchantapi.googleapis.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

### Finding Your Merchant Center Account ID

Your Merchant Center account ID is a numeric identifier visible in the Merchant Center UI URL or account settings. It's required for all API calls.

## Connection Management

Manage your Google Merchant OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=google-merchant&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'google-merchant'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "00726960-095e-47e2-92e6-6e9cdf3e40a1",
    "status": "ACTIVE",
    "creation_time": "2026-02-07T06:41:22.751289Z",
    "last_updated_time": "2026-02-07T06:42:29.411979Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "google-merchant",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Google Merchant connections, specify which one to use with the `Maton-Connection` header:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/google-merchant/products/v1/accounts/123456/products')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '00726960-095e-47e2-92e6-6e9cdf3e40a1')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### Sub-API Structure

The Merchant API is organized into sub-APIs, each with its own version:

| Sub-API | Purpose | Stable Version |
|---------|---------|----------------|
| `products` | Product catalog management | v1 |
| `accounts` | Account settings and users | v1 |
| `datasources` | Data source configuration | v1 |
| `reports` | Analytics and reporting | v1 |
| `promotions` | Promotional offers | v1 |
| `inventories` | Local and regional inventory | v1 |
| `notifications` | Webhook subscriptions | v1 |
| `conversions` | Conversion tracking | v1 |
| `lfp` | Local Fulfillment Partnership | v1beta |

### Products

#### List Products

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products
```

Query parameters:
- `pageSize` (integer): Maximum results per page
- `pageToken` (string): Pagination token

#### Get Product

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products/{productId}
```

Product ID format: `contentLanguage~feedLabel~offerId` (e.g., `en~US~sku123`)

#### Insert Product Input

```bash
POST /google-merchant/products/v1/accounts/{accountId}/productInputs:insert?dataSource=accounts/{accountId}/dataSources/{dataSourceId}
Content-Type: application/json

{
  "offerId": "sku123",
  "contentLanguage": "en",
  "feedLabel": "US",
  "attributes": {
    "title": "Product Title",
    "description": "Product description",
    "link": "https://example.com/product",
    "imageLink": "https://example.com/image.jpg",
    "availability": "in_stock",
    "price": {
      "amountMicros": "19990000",
      "currencyCode": "USD"
    },
    "condition": "new"
  }
}
```

#### Delete Product Input

```bash
DELETE /google-merchant/products/v1/accounts/{accountId}/productInputs/{productId}?dataSource=accounts/{accountId}/dataSources/{dataSourceId}
```

### Inventories

#### List Local Inventories

```bash
GET /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/localInventories
```

#### Insert Local Inventory

```bash
POST /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/localInventories:insert
Content-Type: application/json

{
  "storeCode": "store123",
  "availability": "in_stock",
  "quantity": 10,
  "price": {
    "amountMicros": "19990000",
    "currencyCode": "USD"
  }
}
```

#### List Regional Inventories

```bash
GET /google-merchant/inventories/v1/accounts/{accountId}/products/{productId}/regionalInventories
```

### Data Sources

#### List Data Sources

```bash
GET /google-merchant/datasources/v1/accounts/{accountId}/dataSources
```

#### Get Data Source

```bash
GET /google-merchant/datasources/v1/accounts/{accountId}/dataSources/{dataSourceId}
```

#### Create Data Source

```bash
POST /google-merchant/datasources/v1/accounts/{accountId}/dataSources
Content-Type: application/json

{
  "displayName": "API Data Source",
  "primaryProductDataSource": {
    "channel": "ONLINE_PRODUCTS",
    "feedLabel": "US",
    "contentLanguage": "en"
  }
}
```

#### Fetch Data Source (trigger immediate refresh)

```bash
POST /google-merchant/datasources/v1/accounts/{accountId}/dataSources/{dataSourceId}:fetch
```

### Reports

#### Search Reports

```bash
POST /google-merchant/reports/v1/accounts/{accountId}/reports:search
Content-Type: application/json

{
  "query": "SELECT offer_id, title, clicks, impressions FROM product_performance_view WHERE date BETWEEN '2026-01-01' AND '2026-01-31'"
}
```

Available report tables:
- `product_performance_view` - Clicks, impressions, CTR by product
- `product_view` - Current inventory with attributes and issues
- `price_competitiveness_product_view` - Pricing vs competitors
- `price_insights_product_view` - Suggested pricing
- `best_sellers_product_cluster_view` - Best sellers by category
- `competitive_visibility_competitor_view` - Competitor visibility

### Promotions

#### List Promotions

```bash
GET /google-merchant/promotions/v1/accounts/{accountId}/promotions
```

#### Get Promotion

```bash
GET /google-merchant/promotions/v1/accounts/{accountId}/promotions/{promotionId}
```

#### Insert Promotion

```bash
POST /google-merchant/promotions/v1/accounts/{accountId}/promotions:insert
Content-Type: application/json

{
  "promotionId": "promo123",
  "contentLanguage": "en",
  "targetCountry": "US",
  "redemptionChannel": ["ONLINE"],
  "attributes": {
    "longTitle": "20% off all products",
    "promotionEffectiveDates": "2026-02-01T00:00:00Z/2026-02-28T23:59:59Z"
  }
}
```

### Accounts

#### Get Account

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}
```

#### List Sub-accounts

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}:listSubaccounts
```

#### Get Business Info

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/businessInfo
```

#### Get Shipping Settings

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/shippingSettings
```

#### List Users

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/users
```

#### List Programs

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/programs
```

#### List Regions

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/regions
```

#### List Online Return Policies

```bash
GET /google-merchant/accounts/v1/accounts/{accountId}/onlineReturnPolicies
```

### Notifications

#### List Notification Subscriptions

```bash
GET /google-merchant/notifications/v1/accounts/{accountId}/notificationsubscriptions
```

#### Create Notification Subscription

```bash
POST /google-merchant/notifications/v1/accounts/{accountId}/notificationsubscriptions
Content-Type: application/json

{
  "registeredEvent": "PRODUCT_STATUS_CHANGE",
  "callBackUri": "https://example.com/webhook"
}
```

### Conversion Sources

#### List Conversion Sources

```bash
GET /google-merchant/conversions/v1/accounts/{accountId}/conversionSources
```

## Pagination

The API uses token-based pagination:

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products?pageSize=50
```

Response includes `nextPageToken` when more results exist:

```json
{
  "products": [...],
  "nextPageToken": "CAE..."
}
```

Use the token for the next page:

```bash
GET /google-merchant/products/v1/accounts/{accountId}/products?pageSize=50&pageToken=CAE...
```

## Code Examples

### JavaScript

```javascript
const accountId = '123456789';
const response = await fetch(
  `https://gateway.maton.ai/google-merchant/products/v1/accounts/${accountId}/products`,
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

account_id = '123456789'
response = requests.get(
    f'https://gateway.maton.ai/google-merchant/products/v1/accounts/{account_id}/products',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- Product IDs use the format `contentLanguage~feedLabel~offerId` (e.g., `en~US~sku123`)
- Products can only be inserted/updated/deleted in data sources of type `API`
- After inserting/updating a product, it may take several minutes before the processed product appears
- Monetary values use micros (divide by 1,000,000 for actual value)
- The API uses sub-API versioning - prefer `v1` stable over `v1beta`
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Google Merchant connection |
| 401 | Invalid or missing Maton API key, or no access to specified account |
| 403 | Permission denied for the requested operation |
| 404 | Resource not found |
| 429 | Rate limited |
| 4xx/5xx | Passthrough error from Google Merchant API |

### Common Errors

**"The caller does not have access to the accounts"**: The specified account ID is not accessible with your OAuth credentials. Verify you have access to the Merchant Center account.

**"GCP project is not registered"**: The v1 stable API requires GCP project registration. Use v1beta or register your project.

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `google-merchant`. For example:

- Correct: `https://gateway.maton.ai/google-merchant/products/v1/accounts/{accountId}/products`
- Incorrect: `https://gateway.maton.ai/products/v1/accounts/{accountId}/products`

## Resources

- [Merchant API Overview](https://developers.google.com/merchant/api/overview)
- [Merchant API Reference](https://developers.google.com/merchant/api/reference/rest)
- [Products Guide](https://developers.google.com/merchant/api/guides/products/overview)
- [Data Sources Guide](https://developers.google.com/merchant/api/guides/datasources)
- [Reports Guide](https://developers.google.com/merchant/api/guides/reports)
- [Product Data Specification](https://support.google.com/merchants/answer/7052112)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
