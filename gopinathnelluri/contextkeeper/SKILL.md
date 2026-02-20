---
name: contextkeeper
description: ContextKeeper — Automatic project state tracking and intent routing for AI agents. Maintains situational awareness across sessions by summarizing conversations, tracking active projects, blockers, and decisions.
metadata:
  openclaw:
    requires:
      bins: []
    install: []
---

# ContextKeeper 🔮 v0.1.2

> **Context Preservation & Intent Resolution System for AI Agents**

Solves the "what were we doing?" problem. Maintains active project state, tracks decisions, blockers, and context across conversations so agents can resume work seamlessly.

---

## The Problem

AI agents face context loss:

- **Token limits** → Earlier conversation context drops
- **Session gaps** → "Yesterday we discussed..." becomes unknown
- **Ambiguous references** → "Finish it" — what is "it"?
- **Multiple projects** → Which files/commands belong to which?
- **Re-discovery cost** → Re-asking "what were we doing?"

---

## What ContextKeeper Does

### 1. Auto-Checkpoint Conversations

**Triggers:**
- Every N messages (configurable, default 10)
- On session end
- When project switches
- On explicit: "checkpoint this"

**Captures:**
```yaml
project_id: P002
session_type: active_development
summary: Working on BotCall PWA deployment
decisions: []
blockers: []
files_touched: []
next_steps: []
```

### 2. Working Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/ckpt.sh` | Create checkpoint with git auto-detect | `./ckpt.sh "message"` |
| `scripts/dashboard.sh` | Show projects and status | `./dashboard.sh` |

---

## Quick Start

```bash
# Create checkpoint from git repo
./scripts/ckpt.sh "Fixed the auth issue"

# View dashboard
./scripts/dashboard.sh
```

---

## Script Implementation

**scripts/ckpt.sh:**
- Auto-detects project from git directory
- Captures branch, recent commits, files changed
- Creates JSON checkpoint in ~/.memory/contextkeeper/

**scripts/dashboard.sh:**
- Shows active projects (P001, P002, P003...)
- Lists recent checkpoints
- Displays current session status

---

## File Structure

```
.memory/contextkeeper/
├── checkpoints/
│   ├── 2026-02-18-193000.json
│   └── current-state.json
└── projects/
    ├── P001/
    └── P002/
```

---

## Why Not Just SPIRIT?

| | SPIRIT | ContextKeeper |
|---|---|---|
| Preserves | Identity (who I am) | Situation (what we're doing) |
| Scope | Long-term, cross-system | Session-to-session, real-time |
| Data | SOUL.md, IDENTITY.md | Project state, blockers, intents |
| Metaphor | Birth certificate | Whiteboard, sticky notes |

---

## Version History

| Version | Changes |
|---------|---------|
| v0.1.0 | Initial concept |
| v0.1.1 | Working ckpt.sh + dashboard.sh, git auto-detect |
| v0.1.2 | Fixed skill structure, added documentation |

---

## Development Notes

**For skill contributors:**
- Use `write` tool for major updates to SKILL.md
- Avoid `edit` tool — requires exact whitespace matching
- Test scripts before committing
- Update version in title when publishing

---

**Part of:** [TheOrionAI](https://github.com/TheOrionAI)
