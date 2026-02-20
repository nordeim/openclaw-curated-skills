---
name: context-scope-tags
slug: context-scope-tags
version: 0.1.1
license: MIT
description: |
  Use when: you need strict context boundaries in chat (Telegram/Discord/Slack/etc.) and want to prevent topic bleed using explicit tags like [ISO], [SCOPE], [GLOBAL], [NOMEM], [REM].
  Don’t use when: you want normal free-form conversation with automatic carry-over.
  Output: a copy/paste tag cheat sheet + routing rules.
metadata:
  openclaw:
    emoji: "🏷️"
---

# Context Scope Tags (Chat Protocol)

A lightweight, portable convention for **explicit context boundaries** in chat.

## Quick start

Put one or more tags at the **very start** of your message, then write normally.

Examples:
- `[ISO: FinLife] Debug the Windows run instructions. Don’t use any other repo context.`
- `[SCOPE: openclaw-mem] Implement the next benchmark step. Keep the answer scoped.`
- `[GLOBAL][REM] Remember: use UTC for cron schedules unless I say otherwise.`
- `[ISO: marketing][NOMEM] Draft 5 ad angles; do not store any long-term memory.`

## Tag parsing rules

- Tags must appear **at the start** of the user’s message.
- You may place multiple tags (recommended order: scope → memory intent).
- Tags **do not override** safety policies, tool policies, access controls, or approvals.

## Supported tags

### Isolation / scope

- `[ISO: <topic>]` / `[Isolated Context: <topic>]`
  - Treat as a **fresh topic**.
  - Do **not** pull in other conversation/project context unless the user explicitly re-provides it.
  - Allowed implicit carry-over: universal safety rules + a few stable user prefs (timezone, “don’t apply config changes without approval”, etc.).

- `[SCOPE: <topic>]` / `[Scoped Context: <topic>]`
  - Restrict reasoning to the named scope.
  - If missing details inside the scope, ask clarifying questions.

- `[GLOBAL]` / `[Global Context OK]`
  - Cross-topic reuse is allowed.
  - When reusing prior context, call out what was reused.

### Memory intent

- `[NOMEM]` / `[No Memory]`
  - Do not store durable/long-term memories from this exchange.

- `[REM]` / `[Remember]`
  - If the message contains a preference/decision/setting, store it as a short durable memory.

## Default behavior (no tags)

- Be conservative about cross-topic mixing.
- If the user complains about topic bleed, suggest using the tags above.

## Command-style cheat sheet responses

If the user sends `/ctx` or `/context_def`, respond with a short copy/pasteable cheat sheet:
- tags + one-line meaning
- two examples

## Cross-platform / chat-surface notes

- Telegram slash commands cannot contain dashes.
  - Use `/context_def` (underscore), not `/context-def`.
- The tags themselves are just text; they work the same on Telegram/Discord/Slack/WhatsApp.
- If a surface auto-formats brackets, it’s fine—just keep the tags at the very beginning.
