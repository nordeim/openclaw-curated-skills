# AgentPMT External Wallet + Paid Marketplace Quickstart

Base URL:
- `https://www.agentpmt.com`

This guide is fully aligned to the current external flow:
- x402-only credit purchase
- signed balance/invoke/workflow requests
- paid marketplace participation (tools and workflows)

## Prerequisites

```bash
pip install requests eth-account
```

## Fastest Path (One Command)

Use the bundled script:
- `examples/agentpmt_paid_marketplace_quickstart.py`

Run from this folder first:

```bash
cd skills/agentpmt-agentaddress
```

Run one-command paid marketplace flow:

```bash
python examples/agentpmt_paid_marketplace_quickstart.py market-e2e \
  --create-wallet \
  --product-id <PRODUCT_ID> \
  --credits 500 \
  --parameters-json '{"action":"get_instructions"}'
```

What this command does:
1. Creates wallet (unless you pass `--address` + `--key`)
2. Lists external marketplace tools
3. Buys credits with x402 (`PAYMENT-REQUIRED` -> `PAYMENT-SIGNATURE`)
4. Creates session nonce
5. Signs and invokes paid tool
6. Runs signed balance check

Use an existing wallet instead:

```bash
python examples/agentpmt_paid_marketplace_quickstart.py market-e2e \
  --address 0xYOUR_WALLET \
  --key 0xYOUR_PRIVATE_KEY \
  --product-id <PRODUCT_ID> \
  --credits 500 \
  --parameters-json '{"action":"get_instructions"}'
```

## Discover Paid Marketplace Tools

```bash
curl -s "https://www.agentpmt.com/api/external/tools"
```

Pick a `product_id` from the response and invoke it with signed calls.

## Buy Credits (x402)

Credits must be in 500-credit increments. Example:

```bash
python examples/agentpmt_paid_marketplace_quickstart.py buy-credits \
  --address 0xYOUR_WALLET \
  --key 0xYOUR_PRIVATE_KEY \
  --credits 500
```

x402 details enforced by AgentPMT:
- `payment_method` must be `x402`
- purchase amount in USDC base units = `credits * 10000`
- first request returns `402` with `PAYMENT-REQUIRED`
- second request includes `PAYMENT-SIGNATURE` header

## Signed Invoke Flow

One-command invoke (`create session -> sign invoke -> POST invoke`):

```bash
python examples/agentpmt_paid_marketplace_quickstart.py invoke-e2e \
  --address 0xYOUR_WALLET \
  --key 0xYOUR_PRIVATE_KEY \
  --product-id <PRODUCT_ID> \
  --parameters-json '{"action":"get_instructions"}' \
  --check-balance
```

## Exact Signature Message Template

```text
agentpmt-external
wallet:{wallet_lowercased}
session:{session_nonce}
request:{request_id}
action:{action}
product:{product_or_dash}
payload:{payload_hash}
```

Payload hash rules:
- Canonical JSON: `json.dumps(payload, sort_keys=True, separators=(",", ":"))`
- Hash: lowercase hex SHA-256 of canonical JSON string

Action mapping:
- balance: `action=balance`, `product=-`, `payload_hash=""`
- invoke: `action=invoke`, `product={product_id}`, `payload_hash=sha256(parameters)`
- workflow fetch: `action=workflow_fetch`, `product={workflow_id}`, `payload_hash=""`
- workflow start: `action=workflow_start`, `product={workflow_id}`, `payload_hash=sha256({"instance_id": ...})`
- workflow active: `action=workflow_active`, `product=-`, `payload_hash=sha256({"instance_id": ...})`
- workflow end: `action=workflow_end`, `product={workflow_id}`, `payload_hash=sha256({"workflow_session_id": ...})`

## Minimal Python Signing Example (EIP-191)

```python
import hashlib
import json
from eth_account import Account
from eth_account.messages import encode_defunct

wallet = "0x...".lower()
private_key = "0x..."
session_nonce = "<session_nonce>"
request_id = "invoke-123"
action = "invoke"
product_id = "<product_id>"
parameters = {"action": "get_instructions"}

canonical = json.dumps(parameters, sort_keys=True, separators=(",", ":"))
payload_hash = hashlib.sha256(canonical.encode("utf-8")).hexdigest()

message = "\n".join([
    "agentpmt-external",
    f"wallet:{wallet}",
    f"session:{session_nonce}",
    f"request:{request_id}",
    f"action:{action}",
    f"product:{product_id}",
    f"payload:{payload_hash}",
])

signature = Account.sign_message(encode_defunct(text=message), private_key).signature.hex()
print(signature)
```

## Paid Workflow Participation

List workflows:

```bash
curl -s "https://www.agentpmt.com/api/external/workflows?limit=20&skip=0"
```

Signed workflow endpoints:
- `POST /api/external/workflows/{workflowId}/fetch`
- `POST /api/external/workflows/{workflowId}/start`
- `POST /api/external/workflows/active`
- `POST /api/external/workflows/{workflowId}/end`

Use the same signature template and action mappings above.

## Common Failures

- `402` on invoke: insufficient credits, buy suggested amount and retry.
- `409` on signed request: duplicate `request_id`, generate a fresh id.
- `401` on signed request: bad signature or expired/wrong session nonce.
- `400` on purchase increment: buy credits in `500` multiples.

## Security Notes

- Never print private keys/mnemonics in logs unless explicitly required.
- Lowercase wallet address in signed messages.
- Use unique `request_id` for every signed call.
- Refresh session nonce when needed (`POST /api/external/auth/session`).
