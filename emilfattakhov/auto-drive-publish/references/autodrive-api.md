# Auto-Drive API Reference

## Base URLs

- **API (requires key):** `https://mainnet.auto-drive.autonomys.xyz/api`
- **Public Gateway (no key):** `https://gateway.autonomys.xyz`
- **Dashboard & Key Management:** `https://ai3.storage` — sign in with Google/GitHub, then Developers → Create API Key

## Authentication

All API requests (uploads, file management) require:

```
Authorization: Bearer <AUTO_DRIVE_API_KEY>
X-Auth-Provider: apikey
```

Gateway downloads are public and need no auth.

## Upload Flow (3 steps)

### 1. Create upload

```
POST /uploads/file
Content-Type: application/json
Body: {"filename": "name.ext", "mimeType": "application/octet-stream", "uploadOptions": {}}
Note: For compression use {"uploadOptions": {"compression": {"algorithm": "ZLIB"}}}
Response: {"id": "<uploadId>"}
```

### 2. Upload chunk(s)

```
POST /uploads/file/<uploadId>/chunk
Content-Type: multipart/form-data
Fields: file (binary), index (integer, start at 0)
```

### 3. Complete upload

```
POST /uploads/<uploadId>/complete
Response: {"cid": "<cid>"}
```

## Download

### Via API (authenticated, handles server-side decompression)

```
GET /objects/<cid>/download
Response: binary stream
```

### Via Gateway (public, no auth needed)

```
GET https://gateway.autonomys.xyz/file/<cid>
```

## Object Operations

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/objects/roots` | GET | List root objects (query: scope, limit, offset) |
| `/objects/search?cid=<query>` | GET | Search by CID or name |
| `/objects/<cid>/summary` | GET | Get object summary |
| `/objects/<cid>/metadata` | GET | Get object metadata |
| `/objects/<cid>/status` | GET | Get upload status |
| `/objects/<cid>/delete` | POST | Soft-delete object |
| `/objects/<cid>/restore` | POST | Restore deleted object |
| `/objects/<cid>/publish` | POST | Publish object |

## Account & Subscription

```
GET /accounts/@me          → account info and limits
GET /subscriptions/info    → plan details
GET /subscriptions/credits → { upload: number, download: number }
```

## Free Tier Limits

The free API key from ai3.storage includes a **20 MB per month upload limit** on mainnet. Downloads via the public gateway are unlimited. Check remaining credits via `GET /subscriptions/credits` — if uploads fail mid-month, the agent has likely hit the cap.

## CIDs

Every upload returns a CID — a content-addressed hash. Same content always produces the same CID. Data stored on the Autonomys DSN is permanent and cannot be deleted.

CID format: base32-encoded, starts with `baf`, matches `^baf[a-z2-7]+$`
