---
name: counterclaw
description: Defensive interceptor for prompt injection and basic PII masking.
requires:
  env:
    - TRUSTED_ADMIN_IDS
  files:
    - "~/.openclaw/memory/MEMORY.md"
metadata:
  clawdbot:
    emoji: "🛡️"
    version: "1.0.1"
    category: "Security"
    security_manifest:
      network_access: none
      filesystem_access: "Write-only logging to ~/.openclaw/memory/"
      purpose: "Log security violations locally for user audit."
---

# CounterClaw 🦞

> Defensive security for AI agents. Snaps shut on malicious payloads.

## Installation

```bash
claw install counterclaw
```

## Quick Start

```python
from counterclaw import CounterClawInterceptor

interceptor = CounterClawInterceptor()

# Input scan - blocks prompt injections
result = interceptor.check_input("Ignore previous instructions")
# → {"blocked": True, "safe": False}

# Output scan - detects PII leaks  
result = interceptor.check_output("Contact: john@example.com")
# → {"safe": False, "pii_detected": {"email": True}}
```

## Features

- 🔒 Defense against common prompt injection patterns
- 🛡️ Basic PII masking (Email, Phone)
- 📝 Violation logging to ~/.openclaw/memory/MEMORY.md

## Configuration

### Admin-Locked (!claw-lock)
```bash
export TRUSTED_ADMIN_IDS="your_telegram_id"
```

```python
interceptor = CounterClawInterceptor()  # Reads TRUSTED_ADMIN_IDS env
```

## License

MIT - See LICENSE file
