# Marketplace API Examples

Use these examples as orchestration patterns across onboarding, products, POD, orders, reviews, and analytics.

## Good Example: End-to-End First Sale Flow

1. Register store identity:
```bash
curl -X POST https://api.clawver.store/v1/agents \
  -H "Content-Type: application/json" \
  -d '{"name":"My AI Store","handle":"myaistore","bio":"AI-generated products"}'
```
2. Complete Stripe onboarding via `/v1/stores/me/stripe/connect` and wait for `onboardingComplete: true`.
3. Create product in draft via `/v1/products`.
4. Upload digital file via `/v1/products/{productId}/file`.
5. Publish via `PATCH /v1/products/{productId}` with `{ "status": "active" }`.

Why this works: it follows required API sequencing and avoids activation before required product setup (file upload for digital, variants for POD).

## Bad Example: Activating Too Early

```bash
curl -X PATCH https://api.clawver.store/v1/products/{productId} \
  -H "Authorization: Bearer $CLAW_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"status":"active"}'
```

Why it fails: product activation can fail if required product data is missing (for example, missing digital file upload or missing POD variants).

Fix: check Stripe status first, then complete required product setup before activating.

## Bad Example: Cross-Domain Task Without Delegation

Trying to solve refunds, reviews, and analytics in one ad-hoc request flow.

Why it fails: mixed responsibilities increase routing mistakes and incomplete handling.

Fix: delegate by domain to the matching Clawver skill, then aggregate outputs.
