# Cron Agent Contract (Portable)

This file is a **portable contract** you can use for any OpenClaw cron worker (especially `sessionTarget="isolated"` + `payload.kind="agentTurn"`).

The goal: make scheduled jobs **reliable**, **low-noise**, and **safe-by-default**.

## 0) Core principles

1) **Scripts-first**
- If the job is more than a single short command, write a small script and have cron run **one command**.

2) **Deterministic working directory**
- Cron environments often start in an unexpected CWD.
- Always `cd` to the repo/work dir (or have the script do it).

3) **No destructive actions without explicit approval**
- Cron jobs must not delete data, patch persistent config, or mutate control-plane settings unless explicitly authorized.

4) **Silent on success**
- Default output should be exactly `NO_REPLY`.
- Only emit a short alert when something is wrong.

## 1) Payload design rules

- Keep the cron payload message **short**.
- Avoid multi-line shell with nested quotes.
- Avoid command substitution (`$(...)`), heredocs (`<<EOF`), and complex pipelines.

If you need parsing, branching, JSON, or retries → **use a script**.

## 2) Portable path rules (don’t hardcode `/root/...`)

People install OpenClaw on different OSes and with different home/workspace locations.

- **Do not hardcode absolute paths** tied to your machine.
- Prefer:
  - paths relative to the repo (best)
  - `$HOME` / `%USERPROFILE%` only when you truly need user-home paths
  - a config/env variable you document (e.g., `FINLIFE_DB_URL`, `WORKDIR`, etc.)

If you must use an absolute path, make it a **single well-known variable** and document it.

## 3) Recommended execution patterns

### Pattern A — One command calling a script (best)

- Put the logic in: `tools/<job_name>.py` (or `scripts/<job_name>.py`) inside the repo.
- Cron runs:

```bash
python3 tools/<job_name>.py
```

Your script should:
- validate inputs
- `chdir` to the correct directory if needed
- run subprocess calls with argv arrays (no shell)
- print `NO_REPLY` on success

### Pattern B — Minimal shell wrapper (only if needed)

```bash
bash -lc 'cd /path/to/repo && python3 tools/<job_name>.py'
```

Keep it short. If quoting gets tricky, you already crossed the line → move logic into the script.

## 4) Output contract

- **Success:** output exactly `NO_REPLY`
- **Failure:** <= 6 bullets:
  - what failed
  - where (file/command)
  - next action

## 5) Verification checklist

After changes, confirm:
- the job runs end-to-end without human intervention
- reruns are idempotent (no duplicated writes unless intended)
- success runs are silent
- failures are actionable and short
