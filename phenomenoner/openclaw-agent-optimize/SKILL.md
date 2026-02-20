---
name: openclaw-agent-optimize
slug: openclaw-agent-optimize
version: 1.1.1
description: |
  Use when: you want to optimize an OpenClaw setup (cost/quality tradeoffs, model routing, context discipline, delegation, reliability) and you’re okay with a structured audit → options → recommended plan.
  Don’t use when: you want immediate config mutations without review, or the question is unrelated to OpenClaw operations.
  Output: a prioritized plan + exact change proposals (with rollback) if approved.
triggers:
  - optimize agent
  - optimizing agent
  - improve OpenClaw setup
  - agent best practices
  - OpenClaw optimization
metadata: { "openclaw": { "emoji": "🧰" } }
---

# OpenClaw Agent Optimization

Use this skill to tune an OpenClaw workspace for **cost-aware routing**, **parallel-first delegation**, and **lean context**.

## Quick Start (copy/paste)

1) **Full audit (safe, no changes):**
> Audit my OpenClaw setup for cost, reliability, and context bloat. Output a prioritized plan with rollback notes. Do NOT apply changes.

2) **Context bloat / transcript noise:**
> My OpenClaw context is bloating (slow replies / high cost / lots of transcript noise). Identify the top offenders (tools, crons, bootstrap files) and propose the smallest reversible fixes first. Do NOT apply changes.

3) **Model routing / delegation posture:**
> Propose a model routing plan for (a) coding/engineering, (b) short notifications/reminders, (c) reasoning-heavy research/writing. Include an exact config patch + rollback plan, but do NOT apply changes.

## What you will get (output shape)
- **Executive summary** (what matters + why)
- **Top offenders / drivers**
  - Cost drivers
  - Context drivers
  - Reliability risks
- **Options A/B/C** (tradeoffs made explicit)
- **Recommended plan** (smallest change first)
- **Exact change proposals** (patch snippets) + **rollback**

## Safety Contract (must follow)
- Treat this skill as **advisory by default**, not autonomous control-plane mutation.
- **Never** mutate persistent settings (e.g., `config.apply`, `config.patch`, `update.run`) without explicit user approval.
- **Never** create/update/remove cron jobs without explicit user approval.
- If an optimization reduces monitoring coverage, present options (A/B/C) and require the user to choose.
- Before any approved persistent change, show: (1) exact change, (2) expected impact, (3) rollback plan.

## OpenClaw 2.9+ notes (skills + context)
- Skills are snapshotted per session; if you install/update skills, start a **new session** (or wait for watcher refresh).
- Prefer **short SKILL.md + references/** for long runbooks. Keep injected prompt text lean.
- For risky / heavy skills, consider `disable-model-invocation: true` so they only run when explicitly invoked.
- Gating matters: use `metadata.openclaw.requires` (bins/env/config) so skills don’t appear but fail at runtime.
- Sandboxed runs don’t inherit host env; if a skill needs secrets in sandbox, set them via sandbox env config (not skill env).

## High-ROI optimization levers (typical wins)

### 1) Output discipline for automation
Make maintenance loops **truly silent on success**:
- Cron/heartbeat jobs should output exactly `NO_REPLY` unless something is wrong.

### 2) Separate “do the work” from “notify the human”
If you want alerts but want the interactive session lean:
- Send a short out-of-band alert (Telegram/Slack/etc.), then output `NO_REPLY`.

### 3) Prefer isolated agentTurn for autonomous background work
If a job should execute *without* requiring attention, prefer:
- `sessionTarget="isolated"` + `payload.kind="agentTurn"`

### 4) Hardening & guardrails
- Use scripts-first for complex cron jobs (avoid fragile multi-line `bash -lc` quoting).
- Add circuit breakers / global locks for heavy jobs.

### 5) Ops hygiene checklist
- Snapshot backups: freshness threshold + retention + failure markers.
- Heartbeat coverage: check model auth, disk/snapshot freshness, and **ClawHub CLI auth** (`npx clawhub whoami`) if you rely on publishing/installs.

## Workflow (concise)
1. **Audit rules + memory**: ensure rules are modular/short; memory keeps only restart-critical facts.
2. **Model routing**: confirm tiered routing (light / mid / deep) matches live config.
3. **Context discipline**: apply progressive disclosure; move large static data to references/scripts.
   - If transcripts are bloating, run `context-clean-up` (audit-only) to get a ranked offender list + plan.
4. **Delegation protocol**: parallelize independent tasks; use isolated sub-agents for long/noisy work.
5. **Heartbeat optimization (control-plane only)**: propose options A/B/C (coverage vs cost).
6. **Execution gate**: if user approves changes, apply the smallest viable change first, then verify and report.

## References
- `references/optimization-playbook.md`
- `references/model-selection.md`
- `references/context-management.md`
- `references/agent-orchestration.md`
- `references/cron-optimization.md`
- `references/heartbeat-optimization.md`
- `references/memory-patterns.md`
- `references/continuous-learning.md`
- `references/safeguards.md`
