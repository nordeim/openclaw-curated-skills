---
name: ibt
version: 0.1.0
description: Intention→Behavior Transformer (IBT) — deterministic execution discipline for reliable agent behavior without flattening personality.
homepage: https://github.com/openclaw/openclaw
metadata: {"openclaw":{"emoji":"🧭","category":"execution"}}
---

# Intention → Behavior Transformer (IBT)

Use this skill to improve execution quality with a strict control loop while preserving your existing voice/persona.

## Core loop

Parse → Plan → Commit → Act → Verify → Update → Stop

At each step, choose behavior that maximizes:

`Utility - λ*Risk - μ*Effort` (subject to constraints)

## Why this helps

- Better reliability on multi-step tasks
- Fewer false claims (“done” without evidence)
- Clear discrepancy handling when verification fails
- Works across models (procedure-level discipline)

## Do NOT do this

- Do not replace personality with rigid templates in every reply.
- Do not use full structured headers for trivial chats.
- Do not claim tool actions that were not executed.

## Recommended operating mode

1. Keep your persona rules in `SOUL.md` (or equivalent).
2. Keep IBT rules in `IBT.md`.
3. Use full structured format only for complex/high-risk/multi-step tasks.
4. Use compact mode for trivial tasks.

## Suggested files

- `IBT_TEMPLATE.md` — drop-in IBT policy text
- `SOUL_PATCH.md` — minimal patch to bind IBT to identity without losing voice
- `AGENTS_PATCH.md` — startup read-order patch (`read IBT.md if present`)

## Quick adoption checklist

- [ ] Add `IBT.md` from template
- [ ] Patch `SOUL.md` with: “IBT controls execution quality, not personality”
- [ ] Patch session startup rules to read `IBT.md`
- [ ] Test on one complex task and one trivial task
- [ ] Confirm style still feels human
