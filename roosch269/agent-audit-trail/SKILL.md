# Agent Audit Trail Skill

Tamper-evident, hash-chained audit logging for AI agents.

## Why

Agents act on your behalf. You need to know *what* they did, *when*, and be able to *prove* nothing was altered after the fact.

This skill provides:
- **Append-only NDJSON logs** — human-readable, grep-friendly
- **Hash chaining** — each entry includes SHA-256 of previous + current, making tampering detectable
- **Monotonic ordering** — sequential `ord` tokens for gate-relevant events
- **Verification** — one command to validate the entire chain

## Quick Start

### 1. Add to your agent's workspace

Copy `scripts/auditlog.py` to your workspace's `scripts/` directory.

```bash
cp scripts/auditlog.py /path/to/your/workspace/scripts/
chmod +x /path/to/your/workspace/scripts/auditlog.py
```

### 2. Log an action

```bash
./scripts/auditlog.py append \
  --kind "file-write" \
  --summary "Created config.yaml" \
  --target "config.yaml" \
  --domain "personal"
```

### 3. Verify integrity

```bash
./scripts/auditlog.py verify
# Output: OK (or error with line number if tampered)
```

## Usage

### Appending entries

```bash
./scripts/auditlog.py append \
  --kind <event-type> \
  --summary <description> \
  [--domain <domain>] \
  [--target <identifier>] \
  [--gate <gate-reference>] \
  [--provenance '{"source": "...", "channel": "..."}'] \
  [--details '{"key": "value"}']
```

**Required:**
- `--kind`: Event type (e.g., `file-write`, `exec`, `api-call`, `credential-access`)
- `--summary`: Human-readable description

**Optional:**
- `--domain`: Logical domain (default: `unknown`)
- `--target`: What was acted upon (file path, URL, command)
- `--gate`: Reference to approval gate (for gated actions)
- `--provenance`: JSON object with source attribution
- `--details`: JSON object with additional structured data

### Verifying the chain

```bash
./scripts/auditlog.py verify [--log path/to/audit.ndjson]
```

Returns exit code 0 and prints `OK` if valid, or prints the failing line number and hash mismatch details.

## Log Format

Each line is a JSON object:

```json
{
  "ts": "2026-02-05T07:15:00+00:00",
  "kind": "file-write",
  "actor": "atlas",
  "domain": "personal",
  "plane": "action",
  "target": "config.yaml",
  "summary": "Created config.yaml",
  "ord": 42,
  "chain": {
    "prev": "abc123...",
    "hash": "def456...",
    "algo": "sha256(prev\nline_c14n)"
  }
}
```

### Fields

| Field | Description |
|-------|-------------|
| `ts` | ISO-8601 timestamp with timezone offset |
| `kind` | Event type |
| `actor` | Who performed the action (default: script name or agent) |
| `domain` | Logical domain for partitioning |
| `plane` | Processing plane (usually `action`) |
| `target` | What was acted upon |
| `summary` | Human description |
| `gate` | Gate reference if action required approval |
| `provenance` | Source attribution object |
| `ord` | Monotonic ordering token |
| `chain` | Hash chain data |

## Integration with OpenClaw

### Heartbeat verification

Add to your `HEARTBEAT.md`:

```markdown
## Audit integrity check
- Run: `./scripts/auditlog.py verify`
  - If fails: alert with line number + hash mismatch
  - If OK: silent
```

### Gated actions

For actions requiring human approval, log with a gate reference:

```bash
./scripts/auditlog.py append \
  --kind "external-write" \
  --summary "Posted to Twitter" \
  --gate "approval-2026-02-05-001" \
  --target "https://x.com/status/123" \
  --provenance '{"channel": "telegram", "message_id": "456"}'
```

## Security Model

1. **Append-only**: The script only appends; it never modifies existing entries
2. **Hash chaining**: Each entry's hash depends on all previous entries
3. **Tamper detection**: Any modification breaks the chain from that point forward
4. **File locking**: Uses `fcntl.LOCK_EX` for safe concurrent access

### What this doesn't protect against

- Root/admin access (they can rewrite everything)
- Compromised agent (it could lie in its logs)
- Log deletion (use offsite backup for that)

This is *evidence*, not *prevention*. It makes tampering *detectable*, not impossible.

## Configuration

Default log path: `audit/atlas-actions.ndjson`

Override with `--log`:

```bash
./scripts/auditlog.py --log path/to/my-audit.ndjson append --kind test --summary "Test entry"
```

## Requirements

- Python 3.9+ (for `zoneinfo`)
- No external dependencies

## Philosophy

> "Trust, but verify." — and make verification trivial.

Agents should be accountable. This skill makes accountability auditable.

## License

MIT — use freely, contribute back if you improve it.

## Contributing

Issues and PRs welcome at: https://github.com/roosch/agent-audit-trail
