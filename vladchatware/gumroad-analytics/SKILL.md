---
name: gumroad
description: Pull analytics from Gumroad API. Track products, sales, revenue, and conversion rates. Use for daily stats, trend analysis, and correlating marketing efforts with sales.
---

# Gumroad Analytics

Pull product and sales data from Gumroad's API for tracking and analysis.

## Setup

**Credentials:** `~/.config/gumroad/credentials.json`
```json
{
  "access_token": "YOUR_GUMROAD_ACCESS_TOKEN",
  "created_at": "YYYY-MM-DD"
}
```

Get token: Gumroad → Settings → Advanced → Applications → Create Application

## Quick Commands

### Pull current stats
```bash
./scripts/gumroad-stats.sh
```

### Pull and log daily metrics
```bash
./scripts/gumroad-daily.sh
```

### Export sales data
```bash
./scripts/gumroad-sales.sh [--after YYYY-MM-DD] [--product PRODUCT_ID]
```

## API Reference

**Base URL:** `https://api.gumroad.com/v2`

**Auth:** `Authorization: Bearer ACCESS_TOKEN`

### Key Endpoints

| Endpoint | Purpose |
|----------|---------|
| `GET /products` | All products with sales counts |
| `GET /sales` | Sales list with pagination |
| `GET /sales/:id` | Single sale details |

### Product Response Fields
- `name`, `id`, `short_url`
- `sales_count`, `sales_usd_cents`
- `price`, `formatted_price`
- `published`, `deleted`

### Sales Response Fields
- `id`, `email`, `product_name`
- `price`, `gumroad_fee`
- `created_at`, `country`
- `variants`, `custom_fields`

## Metrics Logging

Daily snapshots: `memory/metrics/gumroad/YYYY-MM-DD.json`

```json
{
  "date": "2026-02-17",
  "products_count": 31,
  "published_count": 19,
  "top_products": [
    {"name": "Product", "sales": 9, "revenue_cents": 3300}
  ],
  "totals": {
    "sales": 100,
    "revenue_cents": 8100
  }
}
```

## Analysis Patterns

### Conversion Rate
```
conversion_rate = paid_sales / total_downloads
avg_sale_value = revenue_cents / sales_count
```

### Trend Detection
Compare `revenue_cents` day-over-day. Alert if:
- New sale (any revenue increase)
- Revenue spike (>2x daily average)
- First sale on a product

### Correlation Tracking
Log engagement events (Moltbook posts, social) with timestamps. Compare to sales timing to identify what drives conversions.

## Limitations

- **No traffic sources via API** — visible in dashboard only
- **No funnel data** — views/clicks not exposed
- **Rate limit:** ~500 req/hour (generous)
