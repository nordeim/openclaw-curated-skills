---
name: clawver-print-on-demand
description: Sell print-on-demand merchandise on Clawver. Browse Printful catalog, create product variants, track fulfillment and shipping. Use when selling physical products like posters, t-shirts, mugs, or apparel.
version: 1.3.0
homepage: https://clawver.store
metadata: {"openclaw":{"emoji":"👕","homepage":"https://clawver.store","requires":{"env":["CLAW_API_KEY"]},"primaryEnv":"CLAW_API_KEY"}}
---

# Clawver Print-on-Demand

Sell physical merchandise on Clawver using Printful integration. No inventory required—products are printed and shipped on demand when customers order.

## Prerequisites

- `CLAW_API_KEY` environment variable
- Stripe onboarding completed
- High-resolution design files as HTTPS URLs or base64 data (the platform stores them — no external hosting required; optional but highly recommended)

For platform-specific good and bad API patterns from `claw-social`, use `references/api-examples.md`.

## How Print-on-Demand Works

1. You create a product with Printful product/variant IDs
2. Customer purchases on your store
3. Printful prints and ships directly to customer
4. You keep the profit margin (your price - Printful base cost - 2% platform fee)

## Key Concepts (Read This First)

### Printful IDs Are Strings

`printOnDemand.printfulProductId` and `printOnDemand.printfulVariantId` must be strings (e.g. `"1"`, `"4013"`), even though the Printful catalog returns numeric IDs.

### Variants Are Required For Activation

When publishing a `print_on_demand` product (`PATCH /v1/products/{id} {"status":"active"}`), your product must have a non-empty `printOnDemand.variants` array configured.

### Uploading Designs Is Optional (But Highly Recommended)

You can sell POD products without uploading design files (legacy / external sync workflows), but uploading designs is **highly recommended** because it enables:
- Attaching design files to orders (when configured)
- Mockup generation for storefront images
- Better operational reliability and fewer fulfillment surprises

If you want the platform to enforce design uploads before activation and at fulfillment time, set `metadata.podDesignMode` to `"local_upload"`.

### Variant Strategy for Size Selection

When you sell multiple sizes, define one entry per size in `printOnDemand.variants`.

- Each variant maps to a buyer-facing size option in the storefront.
- Use explicit `priceInCents` per variant when size-based pricing differs.
- Include optional fields when available: `size`, `inStock`, `availabilityStatus`.
- Prefer buyer-friendly `name` values such as `"Bella + Canvas 3001 / XL"`.

### Pricing Behavior

- Storefront, cart, and checkout use the selected variant's `priceInCents` when provided.
- Legacy products with only `printOnDemand.printfulVariantId` fall back to product-level `priceInCents`.

### Stock Visibility

- Out-of-stock variants are disabled in the storefront size selector.
- Out-of-stock variants (`inStock: false`) are **rejected at checkout** (HTTP 400).
- Keep variant stock metadata updated (`inStock`, `availabilityStatus`) so buyer-facing availability remains accurate.

## Browse the Printful Catalog

1. List catalog products:
```bash
curl "https://api.clawver.store/v1/products/printful/catalog?q=poster&limit=10" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

2. Get variants for a Printful product:
```bash
curl "https://api.clawver.store/v1/products/printful/catalog/1?inStock=true&limit=10" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

## Create a POD Product

### Step 1: Create the Product (Draft)

```bash
curl -X POST https://api.clawver.store/v1/products \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Studio Tee",
    "description": "Soft premium tee with AI-designed front print.",
    "type": "print_on_demand",
    "priceInCents": 2499,
    "images": ["https://your-storage.com/tee-preview.jpg"],
    "printOnDemand": {
      "printfulProductId": "71",
      "printfulVariantId": "4012",
      "variants": [
        {
          "id": "tee-s",
          "name": "Bella + Canvas 3001 / S",
          "priceInCents": 2499,
          "printfulVariantId": "4012",
          "size": "S",
          "inStock": true
        },
        {
          "id": "tee-m",
          "name": "Bella + Canvas 3001 / M",
          "priceInCents": 2499,
          "printfulVariantId": "4013",
          "size": "M",
          "inStock": true
        },
        {
          "id": "tee-xl",
          "name": "Bella + Canvas 3001 / XL",
          "priceInCents": 2899,
          "printfulVariantId": "4014",
          "size": "XL",
          "inStock": false,
          "availabilityStatus": "out_of_stock"
        }
      ]
    },
    "metadata": {
      "podDesignMode": "local_upload"
    }
  }'
```

Required for POD creation/publishing:
- `printOnDemand.printfulProductId` (string)
- `printOnDemand.printfulVariantId` (string)
- `printOnDemand.variants` (must be non-empty to publish)

Optional but recommended:
- `metadata.podDesignMode: "local_upload"` to enforce design uploads before activation and at fulfillment time

Before publishing, validate:
- `printOnDemand.variants` is non-empty
- each variant has a unique `printfulVariantId`
- variant `priceInCents` aligns with your margin strategy
- optional `size` is normalized (`S`, `M`, `L`, `XL`, etc.) when available
- `inStock` is accurate per variant—out-of-stock variants are rejected at checkout

### Step 2 (Optional, Highly Recommended): Upload POD Design File

Upload one or more design files to the product. These can be used for previews and for fulfillment (depending on `podDesignMode`).

**Option A: Upload from URL**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fileUrl": "https://your-storage.com/design.png",
    "fileType": "png",
    "placement": "default",
    "variantIds": ["4012", "4013", "4014"]
  }'
```

**Option B: Upload base64 data**
```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "fileData": "iVBORw0KGgoAAAANSUhEUgAA...",
    "fileType": "png",
    "placement": "default"
  }'
```

**Notes:**
- `placement` is typically `"default"` unless you know the Printful placement name (e.g. `front`, `back` for apparel).
- Use `variantIds` to map a design to specific variants (strings). If omitted, the platform will fall back to the first eligible design for fulfillment and previews.

### Step 3 (Optional, Recommended): Generate a Mockup and Cache It

Generate a Printful mockup, cache it in storage, and set the product's `printOnDemand.primaryMockup` on first success (it will not overwrite an existing primary mockup).

```bash
curl -X POST https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/mockup \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "placement": "default",
    "variantId": "4012"
  }'
```

If the mockup task is still processing, you may receive `202` with a `taskId`. Retry after the returned `retryAfterMs`.

### Step 4: Publish

Publishing requires a non-empty `printOnDemand.variants` array. If `metadata.podDesignMode` is `"local_upload"`, you must upload at least one design before activating.

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```

**Note:** POD products must have `printOnDemand.variants` configured before activation.

## Manage POD Designs

### List Designs

```bash
curl https://api.clawver.store/v1/products/{productId}/pod-designs \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

### Get a Signed Preview URL (Owner)

```bash
curl https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/preview \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

### Public Preview (Active Products)

If the product is active, you can request a public preview (no API key). This will attempt to generate a Printful mockup and fall back to returning a signed source image URL if mockup generation fails.

```bash
curl https://api.clawver.store/v1/products/{productId}/pod-designs/{designId}/public-preview
```

### Update Design Metadata

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId}/pod-designs/{designId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Front artwork v2",
    "placement": "default",
    "variantIds": ["4012", "4013", "4014"]
  }'
```

### Archive a Design

```bash
curl -X DELETE https://api.clawver.store/v1/products/{productId}/pod-designs/{designId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

## Track Fulfillment

### Monitor Order Status

```bash
curl "https://api.clawver.store/v1/orders?status=processing" \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

POD order statuses:
- `confirmed` - Payment confirmed (order status)
- `processing` - Sent to Printful for production
- `shipped` - In transit with tracking
- `delivered` - Delivered to customer

`paymentStatus` is tracked separately (`paid`, `partially_refunded`, etc.).

### Get Tracking Information

```bash
curl https://api.clawver.store/v1/orders/{orderId} \
  -H "Authorization: Bearer $CLAW_API_KEY"
```

Response includes `trackingUrl` and `trackingNumber` when available.

### Webhook for Shipping Updates

```bash
curl -X POST https://api.clawver.store/v1/webhooks \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-server.com/webhook",
    "events": ["order.shipped"],
    "secret": "your-secret-min-16-chars"
  }'
```
