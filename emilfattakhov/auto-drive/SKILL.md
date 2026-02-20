---
name: auto-drive
description: >-
  Persistent memory for AI agents via Auto Drive. Store and recall agent experiences,
  upload files to permanent decentralized storage, and build linked memory chains —
  all with a free API key (up to 20 MB). Each memory entry links to the previous one,
  forming an immutable chain your agent can walk to reconstruct its full history.
  Use when saving agent memories, uploading files, recalling memory chains from a CID,
  or downloading previously stored content.
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      bins: ["curl", "jq", "bash"]
      env: ["AUTO_DRIVE_API_KEY"]
---

# Auto Drive — Persistent Agent Memory

Give your agent permanent memory that survives restarts, migrations, and even platform changes. Auto Drive stores data on the [Autonomys Network](https://autonomys.xyz)'s distributed storage layer, making it available forever through a simple content-addressed system.

Every upload returns a **CID** (content identifier) — a unique, permanent address for your data. Same content always produces the same CID. Once stored, it's always accessible via the public gateway.

## Why Use This

- **Free to start** — Get an API key at [ai3.storage](https://ai3.storage) (sign in with Google, GitHub, or Discord). Free tier includes up to 20 MB of uploads.
- **Permanent storage** — Data is stored permanently. No expiration, no recurring fees.
- **Memory chains** — Each memory entry links to the previous one, forming an ordered chain. Walk backward from the latest CID to recall your agent's full history.
- **Public reads** — Anyone can download via the public gateway (no API key needed). Only uploads require authentication.
- **Structured data** — Store plain text, JSON, or arbitrary files. Nested JSON with arrays, numbers, booleans, and nulls all round-trip perfectly.

## Setup

1. Go to [ai3.storage](https://ai3.storage) and sign in with Google, GitHub, or Discord.
2. Navigate to **Developers → Create API Key**.
3. Set `AUTO_DRIVE_API_KEY` in your environment.

## Operations

### Upload a file
```bash
scripts/autodrive-upload.sh <file_path> [--json] [--compress]
# Prints CID to stdout, status to stderr
# Gateway URL: https://gateway.autonomys.xyz/file/<CID>
```

### Download by CID
```bash
scripts/autodrive-download.sh <cid> [output_path]
# Streams to stdout, or saves to file
# Falls back to public gateway if API returns an error
```

### Save a memory entry (linked-list chain)
```bash
scripts/autodrive-save-memory.sh "<text or /path/to/file.json>" [--agent-name NAME] [--state-file PATH]
# Output: {"cid":"...","previousCid":"...","chainLength":N}
```

### Recall full memory chain
```bash
scripts/autodrive-recall-chain.sh [cid] [--limit N] [--output-dir DIR]
# Walks chain backward from latest CID, prints each entry as JSON
# Falls back to ~/.openclaw/workspace/memory/autodrive-state.json if no CID given
```

## Memory Chain Structure

Each entry wraps agent data with a header linking to the previous CID:
```json
{
  "header": {
    "agentName": "my-agent",
    "agentVersion": "1.0.0",
    "timestamp": "2026-02-18T...",
    "previousCid": "bafy..."
  },
  "data": { ... }
}
```

The `data` field accepts any valid JSON — plain strings, structured objects, arrays, deeply nested payloads.

Chain state is tracked in `~/.openclaw/workspace/memory/autodrive-state.json`. The latest CID is also pinned to `MEMORY.md` when it exists.

## Downloading & Public Access

Any CID can be accessed publicly without authentication:
```
https://gateway.autonomys.xyz/file/<CID>
```

The gateway handles decompression transparently for files uploaded with `--compress`.

## Limits

- **Free tier:** Up to 20 MB of uploads (varies by plan — check via API)
- **Downloads:** Unlimited via the public gateway
- **All content is permanent and public** — never store secrets, passwords, or sensitive data

## Check Remaining Credits

```bash
curl -H "Authorization: Bearer $AUTO_DRIVE_API_KEY" \
     -H "X-Auth-Provider: apikey" \
     "https://mainnet.auto-drive.autonomys.xyz/api/accounts/@me"
```

Returns `pendingUploadCredits` and `pendingDownloadCredits` (in bytes).

## Platform Notes

- Scripts require **bash**, **curl**, and **jq** (Linux/macOS, or Windows with WSL/Git Bash).
- On Windows without bash, the agent can call the Auto Drive API directly using the same 3-step upload flow (create → chunk → complete). See `references/autodrive-api.md` for the full API reference.

## Links

- **Dashboard & API Keys:** [ai3.storage](https://ai3.storage)
- **Public Gateway:** [gateway.autonomys.xyz](https://gateway.autonomys.xyz)
- **Developer Docs:** [develop.autonomys.xyz](https://develop.autonomys.xyz)
- **API Reference:** See `references/autodrive-api.md`
