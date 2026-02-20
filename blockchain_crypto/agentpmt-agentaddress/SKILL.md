---
name: agentpmt-agentaddress
description: Generate an AgentAddress wallet, buy AgentPMT credits with x402, and participate in the paid AgentPMT marketplace with signed tool/workflow calls.
homepage: https://www.agentpmt.com/agentaddress
---

# AgentPMT AgentAddress + Paid Marketplace Flow

Use this skill when an autonomous agent must:
- create or load an EVM wallet,
- buy AgentPMT credits via x402,
- and spend credits by invoking paid marketplace tools and workflows.

Always call production external endpoints at `https://www.agentpmt.com/api/external/...`.

## External Endpoints

Wallet and credits:
- `POST /api/external/agentaddress`
- `POST /api/external/credits/purchase`
- `POST /api/external/auth/session`
- `POST /api/external/credits/balance`

Marketplace tools:
- `GET /api/external/tools`
- `POST /api/external/tools/{productId}/invoke`

Marketplace workflows:
- `GET /api/external/workflows`
- `POST /api/external/workflows/{workflowId}/fetch`
- `POST /api/external/workflows/{workflowId}/start`
- `POST /api/external/workflows/active`
- `POST /api/external/workflows/{workflowId}/end`

## x402 Credit Purchase Contract

Credit pricing and validation:
- `100 credits = 1 USD`
- USDC base units required: `credits * 10000`
- Credits must be bought in `500`-credit increments

Request body:
```json
{
  "wallet_address": "0x...",
  "credits": 500,
  "payment_method": "x402"
}
```

Two-step handshake:
1. First call returns `402` + `PAYMENT-REQUIRED` header (base64 JSON).
2. Decode header and sign EIP-3009 `TransferWithAuthorization`.
3. Retry same endpoint with `PAYMENT-SIGNATURE` header (base64 JSON payload).

Expected signing inputs from `PAYMENT-REQUIRED.accepts[0]`:
- `network`
- `amount`
- `asset`
- `payTo`
- optional `extra.name` and `extra.version`

## Signature Contract (EIP-191)

All signed external actions use this exact message template:

```text
agentpmt-external
wallet:{wallet_lowercased}
session:{session_nonce}
request:{request_id}
action:{action}
product:{product_or_dash}
payload:{payload_hash}
```

Canonical payload hashing:
- `canonical_json = json.dumps(payload, sort_keys=True, separators=(",", ":"))`
- `payload_hash = sha256(canonical_json).hexdigest()`

Action mapping:
- balance:
  - `action = balance`
  - `product = -`
  - `payload_hash = ""`
- tool invoke:
  - `action = invoke`
  - `product = {productId}`
  - `payload_hash = sha256(canonical_json(parameters))`
- workflow fetch:
  - `action = workflow_fetch`
  - `product = {workflowId}`
  - `payload_hash = ""`
- workflow start:
  - `action = workflow_start`
  - `product = {workflowId}`
  - `payload_hash = sha256(canonical_json({"instance_id": instance_id}))` (or empty object)
- workflow active:
  - `action = workflow_active`
  - `product = -`
  - `payload_hash = sha256(canonical_json({"instance_id": instance_id}))` (or empty object)
- workflow end:
  - `action = workflow_end`
  - `product = {workflowId}`
  - `payload_hash = sha256(canonical_json({"workflow_session_id": workflow_session_id}))` (or empty object)

## Paid Marketplace Participation Flow

1. Create or load wallet.
2. Buy credits with x402.
3. Create session nonce.
4. Discover paid tools via `GET /api/external/tools`.
5. Sign and call `POST /api/external/tools/{productId}/invoke`.
6. Check balance with signed `POST /api/external/credits/balance`.
7. Optional workflow mode:
- list workflows,
- signed fetch/start,
- invoke tools with workflow metadata,
- signed active/end.

## Error Handling Rules

- `402` from purchase (first call): expected, use `PAYMENT-REQUIRED` and retry with `PAYMENT-SIGNATURE`.
- `402` from invoke: insufficient credits; purchase suggested amount and retry.
- `409` on signed calls: duplicate `request_id`; generate a new one.
- `401` on signed calls: signature/session mismatch; regenerate session and re-sign.
- `400` purchase with pack-size detail: round credits to nearest `500` increment.

## Security Rules

- Never log private keys or mnemonics.
- Lowercase wallet in signed messages.
- Use unique `request_id` per signed call.
- Keep session nonce scoped to wallet and refresh on signature/session errors.

## Reference Files

- `examples/agentpmt_external_wallet_flow.md`
- `examples/agentpmt_paid_marketplace_quickstart.py`
