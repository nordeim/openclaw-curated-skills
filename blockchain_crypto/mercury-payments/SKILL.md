---
name: mercury-payments
description: Pay invoices via Mercury Bank API. Use when sending ACH or wire payments through Mercury, creating recipients, querying transactions, or managing payment workflows. Covers recipient lookup/creation, payment execution (ACH and domestic wire), idempotency keys, wire purpose formatting, and transaction querying with date ranges.
---

# Mercury Payments

Pay invoices via the Mercury Bank API.

## Prerequisites
- Mercury API token with write access
- Auth header: `Authorization: Bearer <token>`
- Base URL: `https://api.mercury.com/api/v1`

## Account Discovery
```bash
curl -s -H "Authorization: Bearer $TOKEN" "https://api.mercury.com/api/v1/accounts"
```
Returns all accounts with IDs, names, and last-4 digits.

## Payment Flow

### 1. Get explicit approval
**NEVER send money without explicit approval.** Present: amount, recipient, invoice #, account.

### 2. Check for existing recipient
```bash
curl -s -H "Authorization: Bearer $TOKEN" "https://api.mercury.com/api/v1/recipients" \
  | python3 -c "import sys,json; [print(r['name'],r['id']) for r in json.load(sys.stdin)]"
```

### 3. Create recipient if needed
```bash
curl -s -X POST "https://api.mercury.com/api/v1/recipients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Vendor Name",
    "emails": ["vendor@example.com"],
    "defaultPaymentMethod": "ach",
    "electronicRoutingInfo": {
      "accountNumber": "...",
      "routingNumber": "...",
      "electronicAccountType": "businessChecking",
      "address": { "address1": "...", "city": "...", "region": "...", "postalCode": "...", "country": "US" }
    }
  }'
```

### 4. Send payment

**ACH:**
```bash
curl -s -X POST "https://api.mercury.com/api/v1/account/{accountId}/transactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipientId": "...",
    "amount": 500.00,
    "paymentMethod": "ach",
    "note": "INV-001 - Vendor - Jan 2025",
    "idempotencyKey": "vendor-inv001-jan2025"
  }'
```

**Domestic wire:**
```bash
curl -s -X POST "https://api.mercury.com/api/v1/account/{accountId}/transactions" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "recipientId": "...",
    "amount": 1000.00,
    "paymentMethod": "domesticWire",
    "purpose": {"simple": {"category": "vendor", "additionalInfo": "Invoice INV-001 Service Description"}},
    "note": "INV-001 - Vendor - Jan 2025",
    "idempotencyKey": "vendor-inv001-jan2025"
  }'
```

**Wire `purpose` is required.** Format: `{"simple": {"category": "<cat>", "additionalInfo": "<desc>"}}`

Categories: `employee`, `landlord`, `vendor`, `contractor`, `subsidiary`, `transferToMyExternalAccount`, `familyMemberOrFriend`, `forGoodsOrServices`, `angelInvestment`, `savingsOrInvestments`, `expenses`, `travel`, `other`

### 5. Notify bookkeeper and vendor
After payment, email the bookkeeper and reply to the vendor with payment confirmation and invoice attached.

## Querying Transactions
```bash
# Recent (~30 days default)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.mercury.com/api/v1/account/{accountId}/transactions?limit=500"

# Date range (required to go further back)
curl -s -H "Authorization: Bearer $TOKEN" \
  "https://api.mercury.com/api/v1/account/{accountId}/transactions?start=2025-01-01&end=2025-01-31&limit=500"
```
Without `start`/`end`, the API only returns ~30 days of history.

## Idempotency Keys
Use descriptive keys: `{vendor}-{invoice}-{period}` (e.g., `acme-inv123-jan2025`). Prevents duplicate payments on retry.

## Payment Checklist
- [ ] Payment explicitly approved
- [ ] Invoice PDF downloaded
- [ ] Recipient exists (or created)
- [ ] Payment sent with correct amount, method, and note
- [ ] Bookkeeper notified with invoice attached
- [ ] Vendor notified with invoice attached
