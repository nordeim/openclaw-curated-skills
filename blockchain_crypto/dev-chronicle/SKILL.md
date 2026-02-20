---
name: dev-chronicle
description: Generate narrative chronicles of developer work from git history, session transcripts, and memory files. Use when the user asks "what did I do today/this week", wants a work summary, daily/weekly chronicle, standup notes, or portfolio narrative. Also triggers on "chronicle", "dev diary", "work story", "recap", or "standup".
---

# DevChronicle — Narrative Engineering Journal

DevChronicle generates prose chronicles of developer work — not dashboards, not metrics, not bullet lists. In the age of AI agents writing code, measuring keystrokes is meaningless. What matters is what you *decided*, what you *killed*, and where you're *going*.

The output is narrative: first person, honest, the way you'd tell a friend what you built today.

## Setup

On first use, check for `{baseDir}/config.json`. If it doesn't exist, create it by asking the user:

```json
{
  "projectDirs": ["~/Projects"],
  "projectDepth": 3,
  "memoryDir": null,
  "sessionsDir": null
}
```

- `projectDirs`: directories to scan for git repos (array, supports `~`)
- `projectDepth`: how deep to search for `.git` folders (default: 3)
- `memoryDir`: path to OpenClaw memory files, or `null` to auto-detect (`<workspace>/memory`)
- `sessionsDir`: path to session transcripts, or `null` to auto-detect (`~/.openclaw/agents/main/sessions`)

## Gathering Data

Run the gather script to collect raw data for a period:

```bash
bash {baseDir}/scripts/gather.sh [YYYY-MM-DD] [days]
```

Examples:
- `bash {baseDir}/scripts/gather.sh` — today only
- `bash {baseDir}/scripts/gather.sh 2026-02-19 7` — week ending Feb 19

The script reads `{baseDir}/config.json` for paths. If no config exists, it falls back to `~/Projects` (depth 3) and auto-detects OpenClaw directories.

After gathering, read the output and generate a chronicle.

### Data Sources (priority order)

1. **Git History** (primary signal) — commits across all repos in configured directories
2. **Memory Files** — `memory/YYYY-MM-DD.md` files contain decisions, context, things worth remembering
3. **Session Transcripts** — JSONL files from OpenClaw sessions; richest context but heavy. Scan metadata line first, only read relevant sessions.
4. **External Tools** (optional) — Trello, Notion, calendar, etc. Enrichment, not primary.

## Generating the Chronicle

### Voice

**Critical**: Read `{baseDir}/references/voice-profile.md` before generating any chronicle. The voice IS the product.

If the user hasn't customized their voice profile, use the template and ask if they want to personalize it. A chronicle without voice is just a changelog.

Core rules (regardless of voice profile):
- **Decisions > tasks.** What got rejected matters as much as what shipped.
- **No corporate speak.** No "leveraged", "synergized", "deliverables".
- **Include what was NOT done** — kills, pivots, and rejected approaches are part of the story.
- **Emotional beats matter** — the satisfaction, frustration, surprise. These are human signals.

### Formats

**Daily Chronicle** (default)
```markdown
# Chronicle — [Date]

[Opening: 1-2 sentences setting the scene — what was the focus]

## [Theme/Project 1]
[Narrative paragraph: what happened, why, key decisions, outcome]

## [Theme/Project 2]
[...]

## Metrics
- Commits: N across M repos
- Projects touched: [list]
- Key decisions: [list]

## Open Threads
[What's unfinished, blocked, or next — if identifiable]
```

**Weekly Chronicle** — roll up daily themes into arcs. Emphasize progress and direction over individual tasks.

**Standup** — telegraphic: yesterday / today / blockers. Minimum viable narrative.

**Portfolio Narrative** — third person, present tense, emphasizes technical decisions and impact. For LinkedIn, CV, case studies.

## Direction/Execution Ratio

When enough data exists (weekly+), calculate and mention:
- **Spec lines vs code lines** — are you building or planning?
- **Commits vs decisions** — activity vs impact
- **Kills** — what got cut and why (kills show taste)
- **Pivots** — direction changes and their reasoning

This is not a KPI. It's a mirror.
