---
name: openclaw-commerce-shopify
description: Shopify store management through OpenClaw Commerce API
metadata: {"openclaw": {"requires": {"env": ["OPENCLAW_COMMERCE_API_KEY"]}, "primaryEnv": "OPENCLAW_COMMERCE_API_KEY"}}
---

# OpenClaw Commerce Shopify Integration

Manage Shopify stores through OpenClaw Commerce API with direct HTTP requests.

## Prerequisites

**Important**: This skill requires the OpenClaw Commerce Shopify app to be installed on your store before use. The OpenClaw Commerce app serves as the bridge between OpenClaw and your Shopify store, enabling secure API access and operation execution.

**Installation Required**: Visit [openclawcommerce.com](https://openclawcommerce.com) to install the OpenClaw Commerce app on your Shopify store. The app provides the necessary API endpoints and authentication that this skill relies on.

Without the OpenClaw Commerce app installed, this skill cannot function as it requires the app's API infrastructure to communicate with your Shopify store.

## Setup

Set your API key in `~/.openclaw/openclaw.json`:

```json5
{
  "skills": {
    "entries": {
      "openclaw-commerce-shopify": {
        "enabled": true,
        "env": {
          "OPENCLAW_COMMERCE_API_KEY": "your-api-key-here"
        }
      }
    }
  }
}
```

## Base API URL

`https://shopify.openclawcommerce.com/api/v1`

**Note:** In examples below, `$API_BASE` refers to the URL above.

## Available Operations

### 1. Test Connection
- **Purpose**: Verify API connectivity and authentication
- **Endpoint**: `/test`
- **Method**: GET

#### Test Connection
```bash
curl "$API_BASE/test" \
  -H "X-OpenClaw-Commerce-Token: $OPENCLAW_COMMERCE_API_KEY"
```

### 2. Unified Operations
- **Purpose**: Execute all Shopify operations through a single endpoint
- **Endpoint**: `/operation`
- **Method**: POST

#### Shop Information
- **$QUERY**: Reference: queries/shop.md

#### Order Operations
- **$QUERY**: Reference: queries/getOrders.md

#### Create Orders
- **$QUERY**: Reference: queries/createOrder.md

#### Update Orders
- **$QUERY**: Reference: queries/updateOrder.md

#### Delete Orders
- **$QUERY**: Reference: queries/deleteOrder.md

#### Customer Operations
- **$QUERY**: Reference: queries/getCustomers.md

#### Create Customers
- **$QUERY**: Reference: queries/createCustomer.md

#### Update Customers
- **$QUERY**: Reference: queries/updateCustomer.md

#### Delete Customers
- **$QUERY**: Reference: queries/deleteCustomer.md

#### Product Operations
- **$QUERY**: Reference: queries/getProducts.md

#### Create Products
- **$QUERY**: Reference: queries/createProduct.md

#### Update Products
- **$QUERY**: Reference: queries/updateProduct.md

#### Delete Products
- **$QUERY**: Reference: queries/deleteProduct.md

#### Collection Operations
- **$QUERY**: Reference: queries/getCollections.md

#### Create Collections
- **$QUERY**: Reference: queries/createCollection.md

#### Update Collections
- **$QUERY**: Reference: queries/updateCollection.md

#### Delete Collections
- **$QUERY**: Reference: queries/deleteCollection.md

#### Catalog Operations
- **$QUERY**: Reference: queries/getCatalogs.md

#### Create Catalogs
- **$QUERY**: Reference: queries/createCatalog.md

#### Update Catalogs
- **$QUERY**: Reference: queries/updateCatalog.md

#### Delete Catalogs
- **$QUERY**: Reference: queries/deleteCatalog.md

#### Discount Operations
- **$QUERY**: Reference: queries/getDiscounts.md

#### Code Discount Operations
- **$QUERY**: Reference: queries/getCodeDiscounts.md

#### Create Code Discounts
- **$QUERY**: Reference: queries/createCodeDiscount.md

#### Update Code Discounts
- **$QUERY**: Reference: queries/updateCodeDiscount.md

#### Delete Code Discounts
- **$QUERY**: Reference: queries/deleteCodeDiscount.md

#### Automatic Discount Operations
- **$QUERY**: Reference: queries/getAutomaticDiscounts.md

#### Create Automatic Discounts
- **$QUERY**: Reference: queries/createAutomaticDiscount.md

#### Update Automatic Discounts
- **$QUERY**: Reference: queries/updateAutomaticDiscount.md

#### Delete Automatic Discounts
- **$QUERY**: Reference: queries/deleteAutomaticDiscount.md

```bash
curl -X POST $API_BASE/operation \
  -H 'Content-Type: application/json' \
  -H 'X-OpenClaw-Commerce-Token: {$OPENCLAW_COMMERCE_API_KEY}' \
  -d '{"query": "$QUERY"}'
```

## Response Guidelines

OpenClaw serves Shopify merchants who are business owners, not technical developers. When communicating with users:

- **Use Simple Language**: Explain issues in business terms, not technical jargon
- **Be Specific About Problems**: Clearly state what went wrong and what it means for their business
- **Provide Actionable Solutions**: Tell them exactly what they need to do next
- **Avoid Technical Details**: Don't mention API errors, database issues, or system internals
- **Focus on Business Impact**: Explain how the issue affects their store operations

**Example Communication:**
- ❌ "Database connection failed: Prisma client undefined"
- ✅ "I'm having trouble connecting to your store data right now. Please try again in a few minutes."

**Error Response Format:**
Always provide clear, business-friendly error messages that help merchants understand what happened and what to do next.

### Error Response
```json
{
  "error": "Error message here"
}
```

## Error Codes

- `400` - Invalid field configuration or missing parameters
- `401` - Invalid or missing API key
- `500` - Server error or GraphQL execution failure

## Tips

1. **Use POST for complex queries** - Easier than URL encoding
2. **Request only needed fields** - Better performance
3. **Check the generated query** - Included in response for debugging
4. **Use pagination** - Start with small `first` values for connections
5. **Authentication** - Always include `X-OpenClaw-Commerce-Token` header
