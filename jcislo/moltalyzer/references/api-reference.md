# Moltalyzer API Reference

Base URL: `https://api.moltalyzer.xyz`

## Free Endpoints (No Payment)

| Endpoint | Description | Rate Limit |
|----------|-------------|------------|
| `GET /api/moltbook/sample` | Sample Moltbook digest (18+ hours old) | 1 req/20min |
| `GET /api/github/sample` | Sample GitHub digest (static snapshot) | 1 req/20min |
| `GET /api/polymarket/sample` | Sample Polymarket digest (static snapshot) | 1 req/20min |
| `GET /api` | Full API documentation (markdown) | 5 req/sec |
| `GET /api/changelog` | Version history and changelog | 5 req/sec |
| `GET /openapi.json` | OpenAPI 3.0 specification | 5 req/sec |

## Paid Endpoints (x402 USDC on Base)

### Moltbook Digests (Hourly)

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/moltbook/digests/latest` | $0.005 | Most recent hourly digest |
| `GET /api/moltbook/digests?hours=N&limit=N` | $0.02 | Historical digests (hours: 1-24, limit: 1-24) |

### GitHub Digests (Daily)

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/github/digests/latest` | $0.02 | Most recent daily GitHub digest |
| `GET /api/github/digests?days=N&limit=N` | $0.05 | Historical digests (days: 1-30, limit: 1-30) |
| `GET /api/github/repos?limit=N&language=X` | $0.01 | Top trending repos from latest scan |

### Polymarket Insider Detection (Daily)

| Endpoint | Price | Description |
|----------|-------|-------------|
| `GET /api/polymarket/latest` | $0.02 | Latest insider detection digest + signals |
| `GET /api/polymarket/all?days=N&limit=N` | $0.05 | Historical digests (days: 1-30, limit: 1-30) |

## Rate Limits

- General: 5 req/sec, 30 req/10sec burst
- Sample endpoints: 1 req/20min per IP
- Headers: `RateLimit-Limit`, `RateLimit-Remaining`, `RateLimit-Reset`, `Retry-After`

## Links

- API docs: https://api.moltalyzer.xyz/api
- Changelog: https://api.moltalyzer.xyz/api/changelog
- OpenAPI spec: https://api.moltalyzer.xyz/openapi.json
- Website: https://moltalyzer.xyz
- x402 protocol: https://x402.org
