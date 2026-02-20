# Agent Audit Trail 🔐

**Tamper-evident, hash-chained audit logging for AI agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![OpenClaw](https://img.shields.io/badge/OpenClaw-skill-orange.svg)](https://github.com/openclaw/openclaw)

---

## The Problem

AI agents act autonomously. They write files, execute commands, call APIs, and make decisions. But how do you know what actually happened? How do you prove the record wasn't altered?

## The Solution

A simple, zero-dependency audit log with cryptographic integrity:

- **Append-only NDJSON** — Human-readable, grep-friendly
- **SHA-256 hash chaining** — Each entry links to all previous entries
- **Tamper detection** — Any modification breaks the chain
- **One-command verification** — Instantly validate the entire history

## Quick Start

```bash
# Clone or copy the script
curl -O https://raw.githubusercontent.com/roosch/agent-audit-trail/main/scripts/auditlog.py
chmod +x auditlog.py

# Log an action
./auditlog.py append --kind "file-write" --summary "Created config.yaml"

# Verify integrity
./auditlog.py verify
# Output: OK (1 entries verified)
```

## Example Output

```json
{"actor":"agent","domain":"personal","kind":"file-write","ord":1,"plane":"action","summary":"Created config.yaml","target":"config.yaml","ts":"2026-02-05T07:15:00+00:00","chain":{"algo":"sha256(prev\\nline_c14n)","hash":"a1b2c3...","prev":"000000..."}}
```

## Usage

### Append an entry

```bash
./auditlog.py append \
  --kind "exec" \
  --summary "Ran database backup" \
  --target "pg_dump production" \
  --domain "ops" \
  --gate "approval-123" \
  --provenance '{"channel": "slack", "user": "admin"}' \
  --details '{"duration_ms": 4500}'
```

### Verify the chain

```bash
./auditlog.py verify
```

Returns exit code 0 if valid, 1 if tampered, with details about which line failed.

### Configuration

| Environment Variable | Default | Description |
|---------------------|---------|-------------|
| `AUDIT_LOG_PATH` | `audit/agent-actions.ndjson` | Log file location |
| `AUDIT_LOG_TZ` | `UTC` | Timezone for timestamps |
| `AUDIT_LOG_ACTOR` | `agent` | Default actor name |

Or use CLI flags: `--log`, `--tz`, `--actor`

## OpenClaw Integration

Add to your `HEARTBEAT.md` for automatic integrity checks:

```markdown
## Audit integrity check
- Run: `./scripts/auditlog.py verify`
  - If fails: alert with line number
  - If OK: silent
```

See [SKILL.md](SKILL.md) for full OpenClaw skill documentation.

## How It Works

```
Entry N-1                    Entry N
┌─────────────────┐         ┌─────────────────┐
│ ts, kind, ...   │         │ ts, kind, ...   │
│ chain.hash: H1  │───┬────▶│ chain.prev: H1  │
└─────────────────┘   │     │ chain.hash: H2  │
                      │     └─────────────────┘
                      │            │
                      └────────────┴──▶ H2 = sha256(H1 + "\n" + canonical(entry))
```

Tampering with any entry changes its hash, which breaks the chain for all subsequent entries.

## Security Model

**What this provides:**
- Evidence of what happened
- Detection of post-hoc tampering
- Chronological ordering guarantees

**What this doesn't provide:**
- Prevention of malicious logging (a compromised agent can lie)
- Protection against log deletion (use offsite backups)
- Root-level security (admins can rewrite everything)

This is *audit*, not *access control*. It makes tampering detectable, not impossible.

## Requirements

- Python 3.9+ (for `zoneinfo`; falls back to UTC on older versions)
- No external dependencies

## Contributing

Issues and PRs welcome! Please:
- Keep it simple (no new dependencies)
- Maintain backward compatibility with existing logs
- Add tests for new features

## License

MIT — Use freely, contribute back if you improve it.

---

Built with 🔐 by [Roosch](https://github.com/roosch) and [Atlas](https://github.com/roosch/agent-audit-trail)
