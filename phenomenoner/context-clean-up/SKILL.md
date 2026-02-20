---
name: context-clean-up
slug: context-clean-up
version: 1.0.4
license: MIT
description: |
  Use when: you suspect OpenClaw prompt context is bloating (slow replies, high cost, repeated transcript noise) and you want a ranked offender list + a reversible clean-up plan.
  Don’t use when: you want the assistant to apply fixes automatically, or you’re asking for unrelated troubleshooting.
  Output: an audit summary + 3–8 concrete fix steps + rollback notes (no automatic changes).
disable-model-invocation: true
allowed-tools:
  - read
  - exec
  - sessions_list
  - sessions_history
  - session_status
metadata: { "openclaw": { "emoji": "🧹", "requires": { "bins": ["python3"] } } }
---

# Context Clean Up (audit-only)

This skill is a **runbook** to identify *what is bloating your OpenClaw prompt context* and produce a **safe, reversible plan**.

**Important:** This skill is intentionally **audit-only**.
- It will **not** delete files, prune sessions, patch config, or modify cron jobs.
- If you ask for changes, it will propose an exact patch + rollback plan and wait for explicit approval.

## Quick start

- `/context-clean-up` → audit + actionable plan (no changes)

## Common offenders (what usually causes bloat)

Typical high-impact sources (roughly in descending frequency):

1) **Tool result dumps**
- Large `exec` output pasted back into chat
- Big `read` outputs (logs, JSON, lockfiles)
- Web fetches that inject long pages

2) **Automation transcript noise**
- Cron jobs that report “OK” every run
- Heartbeat outputs that are not strictly alert-only

3) **Bootstrap reinjection bloat**
- Overgrown `AGENTS.md` / `MEMORY.md` / `SOUL.md` / `USER.md`
- Large “runbooks” embedded directly in SKILL.md instead of `references/`

4) **Repeated summaries that never get trimmed**
- Summaries that accrete historical detail instead of staying restart-critical

## Negative examples (don’t run this skill)
- “Delete old sessions / prune logs / apply fixes now” → this skill is audit-only.
- “Change my OpenClaw config automatically” → must ask first.
- “Investigate a specific bug in app code” → use repo-specific debugging instead.

## Workflow (audit → plan)

### Step 0 — Determine scope

Find:
- **Workspace dir**: where your OpenClaw workspace / project files live
- **State dir**: where OpenClaw stores runtime state (sessions, memory, etc.)

The state dir is often:
- macOS/Linux: `~/.openclaw`
- Windows: `%USERPROFILE%\.openclaw`

…but it can differ per installation. The audit script supports overrides via `--state-dir` or `OPENCLAW_STATE_DIR`.

If you want a quick sanity check:

```text
# POSIX (macOS/Linux)
echo "WORKDIR=$PWD"; echo "HOME=$HOME"; ls -ld ~/.openclaw

# PowerShell (Windows)
Write-Host "WORKDIR=$PWD"; Write-Host "USERPROFILE=$env:USERPROFILE"; Get-Item "$env:USERPROFILE\.openclaw"
```

### Step 1 — Run the audit script

This script prints a short summary and can write a full JSON report.

```text
# Run the audit script shipped with this skill.
# From the skill folder, run:
python3 scripts/context_cleanup_audit.py --out context-cleanup-audit.json

# If your Python executable is not `python3` (common on Windows):
#   py -3 scripts/context_cleanup_audit.py --out context-cleanup-audit.json

# Optional overrides:
#   --workspace   (defaults to current directory)
#   --state-dir   (defaults to ~/.openclaw or OPENCLAW_STATE_DIR)
python3 scripts/context_cleanup_audit.py --workspace . --state-dir <PATH_TO_OPENCLAW_STATE> --out context-cleanup-audit.json
```

Interpretation cheatsheet:
- Huge `toolResult` entries (exec/read/web_fetch): **transcript bloat**
- Many `System:` / `Cron:` lines: **automation bloat**
- Large bootstrap docs (AGENTS/MEMORY/SOUL/USER): **reinjected rules bloat**

### Step 2 — Produce a fix plan (lowest-risk first)

Create a short plan with:
- Top offenders (largest transcript entries)
- Noisiest recurring jobs (cron/heartbeat)
- Quick wins (reversible)

Use these standard levers:

#### Lever A — Make no-op automation truly silent
Goal: maintenance loops should output exactly `NO_REPLY` unless there is an anomaly.

Pattern: update prompts so the last line forces:
- `Finally output ONLY: NO_REPLY`

#### Lever B — Keep notifications, avoid transcript injection
If you want alerts but want the *interactive* session lean:
- Send out-of-band (Telegram/Slack/etc.)
- Then output `NO_REPLY`

See: `references/out-of-band-delivery.md`

#### Lever C — Keep injected bootstrap files small
- Keep only restart-critical rules in `MEMORY.md`
- Move bulky notes into `references/*.md` or `memory/*.md`

### Step 3 — Verify

After you apply any changes:
- Confirm the next cron/heartbeat runs are silent on success.
- Watch context growth rate (it should flatten).

## Sample report skeleton (what “good output” looks like)

Use this structure when you report the audit (even if you do not write JSON):

```markdown
# Context Clean Up — Audit Report (No Changes)

## Executive Summary
- Symptoms observed:
- Primary bloat drivers:
- Recommended first action:

## Top Offenders
1) <offender> — <why it matters> — <quick fix>
2) <offender> — <why it matters> — <quick fix>

## Automation Noise (Cron/Heartbeat)
- Findings:
- Proposed changes (audit-only):
- Risk/rollback notes:

## Bootstrap Size
- Files contributing most:
- Recommendation:

## Plan (3–8 steps)
1) ...
2) ...

## Rollback Plan
- How to revert each step:

## Verification
- What to check after changes:
```

## References
- `references/out-of-band-delivery.md`
- `references/cron-noise-checklist.md`
