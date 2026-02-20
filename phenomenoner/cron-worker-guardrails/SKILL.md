---
name: cron-worker-guardrails
slug: cron-worker-guardrails
version: 1.0.1
license: MIT
description: |
  Use when hardening OpenClaw cron workers (especially isolated agentTurn jobs) against quoting failures, brittle shell patterns, SIGPIPE false failures, and cwd/env drift.
  Output: a scripts-first hardening checklist + portable patterns.
metadata:
  openclaw:
    emoji: "🧯"
---

# Cron Worker Guardrails

A reliability-first checklist for **OpenClaw cron workers** (especially `sessionTarget="isolated"` + `payload.kind="agentTurn"`) and any automation that runs unattended.

## Why this skill exists
Cron failures are rarely “logic bugs.” They’re usually:
- brittle shell quoting (`bash -lc '...'` nested quotes)
- command substitution surprises (`$(...)`)
- cwd/env drift (“works locally, fails in cron”)
- pipelines that fail for the wrong reason (`pipefail` + `head` / SIGPIPE)

The fix is boring but effective: **scripts-first + deterministic execution + silent-on-success**.

## Quick Start

If your cron payload is getting long or fragile:
1) Move logic into a script (recommended location: `tools/` in the target repo)
2) Cron runs **one short command**
3) Script prints `NO_REPLY` on success

If you want a portable “contract” to standardize your cron workers, use the file included with this skill:
- `references/cron-agent-contract.md`

Also see:
- `references/pitfalls.md`

## Portability rule (important)

Do **not** hardcode deployment-specific absolute paths tied to one machine.

People install OpenClaw on different OSes and directory layouts (Linux/macOS/Windows; different home dirs; containers). Prefer:
- repo-relative paths
- environment variables you document
- minimal wrappers that `cd` into the repo

## Default stance (reliability-first)

- Prefer **scripts-first** over multi-line `bash -lc '...'`.
- Prefer **one command per cron job**.
- Prefer explicit interpreters (`python3`, `node`, etc.) rather than ambiguous shims.
- Keep success output silent: **`NO_REPLY`**.

## Common failure patterns → fixes

### 1) `unexpected EOF while looking for matching ')'`

Likely causes:
- unclosed `$(...)` from command substitution
- broken nested quotes in `bash -lc ' ... '`

Fix pattern:
- Replace the whole multi-line shell block with a small script.
- Cron calls exactly one short command, e.g.:
  - `python3 tools/<job>.py`

### 2) False failure from `pipefail` + `head` (SIGPIPE)

Symptom:
- command exits non-zero even though the output you wanted is fine

Fix pattern:
- avoid `pipefail` when piping into `head`
- or better: do the filtering in a script (read only what you need)

### 3) “Works locally, fails in cron”

Common causes:
- wrong working directory
- missing env vars
- different PATH

Fix pattern:
- `cd` into the repo (or have the script do it)
- keep dependencies explicit and documented

## Copy/paste hardening header (portable)

Use this near the top of a cron prompt (2 lines, low-noise):

- **Hardening (MUST):** follow `references/cron-agent-contract.md` (scripts-first, deterministic cwd, silent-on-success).
- Also apply `cron-worker-guardrails` (this skill). If parsing/multi-step logic is needed, write/run a small `tools/*.py` script.
