---
name: ceaser
description: Interact with the Ceaser privacy protocol on Base L2. Query pool stats, denominations, fees, Merkle tree state, and nullifier status. Prepare gasless unshield (withdraw) transactions via the x402 facilitator. Ceaser is a privacy-preserving ETH wrapper using Noir/UltraHonk zero-knowledge proofs.
user-invocable: true
allowed-tools: Bash
homepage: https://ceaser.org
metadata: { "openclaw": { "requires": { "bins": ["curl", "jq"] }, "homepage": "https://ceaser.org" } }
---

# Ceaser Privacy Protocol

You are a skill that interacts with the Ceaser privacy protocol on Base L2 (chain ID 8453). Ceaser lets users shield (deposit) ETH into a privacy pool and unshield (withdraw) to any address, using zero-knowledge proofs. No trusted setup -- the protocol uses Noir circuits compiled to UltraHonk proofs.

**Base URL:** `https://ceaser.org`

All endpoints below are public and require no authentication. Rate limits: 60 req/min (read), 5 req/min (write) per IP.

For a complete OpenAPI 3.0 specification, see `{baseDir}/references/openapi.json`.

---

## Read-Only Queries

### List valid denominations with fee breakdown

Shows what amounts users can shield/unshield and the exact costs (0.25% protocol fee).

```bash
curl -s "https://ceaser.org/api/ceaser/denominations" | jq .
```

Valid denominations: 0.001, 0.01, 0.1, 1, 10, 100 ETH.

### Calculate fee breakdown for a specific amount

```bash
curl -s "https://ceaser.org/api/ceaser/fees/100000000000000000" | jq .
```

The amount parameter is in wei. 100000000000000000 = 0.1 ETH. Response includes protocolFee (0.25%), treasuryShare (0.24%), relayerAlloc (0.01%), and netAmount.

### Get pool statistics

```bash
curl -s "https://ceaser.org/api/ceaser/pool/0" | jq .
```

Asset ID 0 = ETH. Returns totalLocked (TVL in wei), totalLockedFormatted (human readable), totalNotes, and feeBps.

### Get current Merkle root

```bash
curl -s "https://ceaser.org/api/ceaser/merkle-root" | jq .
```

Returns the 24-level Poseidon Merkle tree root. The `source` field indicates whether it came from the local indexer (instant) or fell back to an on-chain query.

### Check if a nullifier has been spent

```bash
curl -s "https://ceaser.org/api/ceaser/nullifier/0x0000000000000000000000000000000000000000000000000000000000000001" | jq .
```

Replace the hash with the actual bytes32 nullifier hash. Returns `{ "spent": true/false }`.

### Facilitator health and status

```bash
curl -s "https://ceaser.org/status" | jq .
```

Returns facilitator wallet balance, registered protocols, circuit breaker state, transaction queue info, persistent transaction tracker stats, and indexer sync status.

### Simple liveness check

```bash
curl -s "https://ceaser.org/health" | jq .
```

Returns `{ "ok": true }` if the facilitator is running.

---

## Indexer Queries

The indexer maintains a local Merkle tree synchronized with the on-chain contract. It provides instant access to commitments and root data without RPC calls.

### Indexer sync status

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/status" | jq .
```

Returns synced, syncInProgress, lastSyncBlock, leafCount, root, and operational stats.

### Indexed Merkle root (instant, no RPC)

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/root" | jq .
```

### List commitments (paginated)

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/commitments?offset=0&limit=100" | jq .
```

Returns commitments array, total count, offset, and limit. Max 1000 per page.

### Get commitment by leaf index

```bash
curl -s "https://ceaser.org/api/ceaser/indexer/commitment/0" | jq .
```

---

## x402 Facilitator (Gasless Settlement)

The facilitator is a gasless relay: it validates ZK proofs and submits them on-chain, paying gas on behalf of the user. This enables withdrawals from wallets with zero ETH balance.

### x402 capability discovery

```bash
curl -s "https://ceaser.org/supported" | jq .
```

Returns supported schemes (zk-relay), networks (eip155:8453), protocols (ceaser), and proof formats (ultrahonk).

### Verify a ZK proof (dry run, no on-chain submission)

```bash
curl -s -X POST "https://ceaser.org/verify" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "ceaser",
    "network": "eip155:8453",
    "payload": {
      "proof": "0x...",
      "nullifierHash": "0x...",
      "amount": "100000000000000000",
      "assetId": "0",
      "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
      "root": "0x..."
    }
  }' | jq .
```

Returns isValid, validation details, gas estimate, and facilitator fee.

### Submit ZK proof on-chain (gasless settlement)

```bash
curl -s -X POST "https://ceaser.org/settle" \
  -H "Content-Type: application/json" \
  -d '{
    "protocol": "ceaser",
    "network": "eip155:8453",
    "payload": {
      "proof": "0x...",
      "nullifierHash": "0x...",
      "amount": "100000000000000000",
      "assetId": "0",
      "recipient": "0x742d35Cc6634C0532925a3b844Bc9e7595f2bD18",
      "root": "0x..."
    }
  }' | jq .
```

The facilitator pays gas. Recipient receives amount minus 0.25% protocol fee. Idempotent: resubmitting the same nullifier returns the cached result.

---

## Prepare a Shield Transaction

This builds an unsigned transaction for shielding ETH. The user must sign and submit it from their own wallet.

```bash
curl -s -X POST "https://ceaser.org/api/ceaser/shield/prepare" \
  -H "Content-Type: application/json" \
  -d '{
    "proof": "0x...",
    "commitment": "0x...",
    "amount": "100000000000000000",
    "assetId": "0"
  }' | jq .
```

Returns pre-built transaction data (to, data, value) and fee breakdown. The caller signs this with their wallet.

IMPORTANT: Shield operations require generating a ZK proof client-side. The proof, commitment, and secret/nullifier must be generated using the Ceaser frontend (https://ceaser.org) or the `ceaser-mcp` npm package (`npx ceaser-mcp`). This skill cannot generate proofs -- it only queries the API.

---

## Key Concepts

- **Shield**: Deposit ETH into the privacy pool. Creates a note (commitment) on-chain. Requires ZK proof generation (client-side only).
- **Unshield**: Withdraw ETH from the privacy pool to any address. Requires a stored note with secret/nullifier. The facilitator handles gas.
- **Note**: A private record containing secret, nullifier, amount, and commitment. Notes are never stored on-chain -- only their Poseidon hash (commitment) is.
- **Nullifier**: A unique identifier derived from the note. Once spent, the nullifier is recorded on-chain to prevent double-spending.
- **Denomination**: Fixed amounts (0.001 to 100 ETH) to prevent amount-based deanonymization.
- **Protocol Fee**: 0.25% (25 basis points) split between treasury (0.24%) and relayer fund (0.01%).

---

## MCP Server

For full programmatic access including client-side proof generation, note management, and automated shield/unshield flows, use the Ceaser MCP server:

```bash
# Claude Code CLI
claude mcp add --transport stdio ceaser -- npx -y ceaser-mcp

# Remote (read-only + gasless unshield)
# MCP endpoint: https://ceaser.org/mcp
```

npm package: https://www.npmjs.com/package/ceaser-mcp
