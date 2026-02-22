# Reorganize OpenClaw Skills into 20 Optimized Categories

## Problem Statement

The current skills directory contains **~790 skill folders** spread across **38 category sub-folders** with severe problems:

1. **Fragmentation** — Related skills split across multiple overlapping categories:
   - Media: `ai-media-generation/`, `media-content/`, `media-processing/`, `media-entertainment/`
   - Productivity: `productivity/`, `productivity-tools/`, `productivity-automation/`, `productivity-task-management/`
   - Communication: `communication/`, `communication-email/`
   - Developer: `developer-tools/`, `development-system-tools/`, `development-workflows/`, `system-developer-tools/`
   - Business: `business-data-integration/`, `business-integration/`
   - Data: `data-analytics/`, `data-integration/`

2. **Naming inconsistency** — Hyphens vs underscores (`media-content/` vs `media_content/`), vague names.

3. **No search infrastructure** — An AI agent must enumerate ~38 directories to find a relevant skill.

## Goal

Consolidate all skills into **exactly 20** well-named category folders with:
- Names optimized for AI agent fuzzy search
- A skill index (`skills-index.json`) for instant lookup
- A search script (`find-skill.sh`) for keyword matching

---

## User Review Required

> [!IMPORTANT]
> The 20 proposed categories below represent my analysis of ~790 skill descriptions. Please review whether the taxonomy meets your mental model. I can adjust category boundaries before execution.

> [!WARNING]
> The move operation will restructure all skill folders. A full backup via git should be confirmed before execution. The existing `REORGANIZATION_MANIFEST.md`, `clean-up.sh`, `pre-clean.sh`, and `todo.txt` will be archived.

---

## Proposed 20-Category Taxonomy

After analyzing every skill description, I grouped them by **primary agent use-case** — what scenario triggers the agent to reach for that skill. Each category name uses a consistent `kebab-case` convention and starts with the broadest intent keyword.

| # | Category Folder | Agent Trigger / Use-Case | Skill Count (≈) |
|---|-----------------|--------------------------|------------------|
| 1 | `agent-core` | Agent self-management: task tracking, memory, context recovery, self-improvement, guardrails, deterministic behavior | ~30 |
| 2 | `agent-orchestration` | Multi-agent coordination: delegation, model routing, spawning, supervision, A2A protocols | ~25 |
| 3 | `search-web` | Web searching: DuckDuckGo, SearXNG, Tavily, Exa, Brave, Google, metasearch | ~25 |
| 4 | `browser-automation` | Browser control: Playwright, Stagehand, headless browsing, form filling, scraping | ~20 |
| 5 | `communication-messaging` | Chat, email, SMS, WhatsApp, Telegram, Signal, Discord, IRC, Slack, notifications | ~60 |
| 6 | `media-generation` | Creating media: image gen, video gen, TTS, voice cloning, music gen, avatar video | ~45 |
| 7 | `media-processing` | Transforming media: transcription (STT), OCR, video editing, audio processing, document conversion, QR codes | ~45 |
| 8 | `content-publishing` | Publishing & social: Twitter/X posting, LinkedIn, Instagram, blog writing, SEO, content marketing, Moltbook | ~40 |
| 9 | `data-analytics` | Data analysis: dashboards, reporting, CSV/Excel, revenue tracking, business intelligence | ~20 |
| 10 | `knowledge-research` | Research & knowledge: deep research, arXiv, PubMed, knowledge graphs, RAG, semantic search, news aggregation | ~40 |
| 11 | `productivity-personal` | Personal productivity: task managers, Pomodoro, calendars, reminders, note-taking, health tracking, finance tracking | ~60 |
| 12 | `business-operations` | Business tools: CRM, Salesforce, Shopify, SaaS, invoicing, e-commerce, GoHighLevel, real estate | ~35 |
| 13 | `devops-cloud` | DevOps & cloud: Docker, Kubernetes, Railway, AWS, CI/CD, server monitoring, SSH, DNS, deployment | ~35 |
| 14 | `developer-tools` | Coding tools: Git workflows, PR review, code security, linting, UI/UX libraries, IDEs, tmux, project scaffolding | ~40 |
| 15 | `integrations-connectors` | API connectors: ClawHub/ClawdHub installers, Google Workspace, Microsoft 365, Notion, Airtable, Composio | ~40 |
| 16 | `smart-home-iot` | Physical devices: smart lights, robots, 3D printers, sensors, Chromecast, Sonos, smart home control | ~25 |
| 17 | `finance-markets` | Financial data: stock prices, J-Quants, EDINET, investment analysis, accounting, e-invoicing | ~15 |
| 18 | `travel-transport` | Travel & transport: flights, trains, trip planning, bus booking, ride-hailing, navigation | ~20 |
| 19 | `games-entertainment` | Games & fun: text adventures, chess, battle arenas, digital pets, Spotify, media players | ~30 |
| 20 | `security-compliance` | Security: vulnerability scanning, prompt injection defense, content moderation, compliance, MFA, guardrails | ~20 |

### Design Rationale

1. **Agent trigger naming**: Each folder name answers "What is the agent trying to do?" — e.g., an agent searching the web looks in `search-web/`, not a vague `web-communication-tools/`.

2. **Balanced sizes**: Target ~20-60 skills per category to avoid both tiny one-skill categories and massive 200+ buckets.

3. **No duplication of scope**: Skills belong to exactly one category based on their **primary** function.

4. **Searchable names**: The folder names are plain English keywords that any AI agent would naturally match against when seeking a skill (e.g., "I need to send an email" → `communication-messaging/`).

5. **Separation of Generate vs Process**: Media is split into `media-generation` (creating new content) and `media-processing` (transforming existing content) because the agent's intent is fundamentally different.

6. **Security isolated**: Security skills get their own category because agents must find them for compliance checks, regardless of what domain they're working in.

---

## Proposed Changes

### Phase 1: Pre-Execution Setup

#### [NEW] [skills-index.json](file:///home/project/openclaw/curated_skills/skills-index.json)

A machine-readable JSON index of all skills with their category, name, and description snippet. Generated by a build script.

```json
{
  "version": "1.0",
  "generated": "2026-02-23T06:30:00+08:00",
  "categories": 20,
  "total_skills": 790,
  "skills": [
    {
      "name": "gmail-client",
      "category": "communication-messaging",
      "path": "communication-messaging/gmail-client",
      "description": "Read and send emails via Gmail...",
      "keywords": ["email", "gmail", "send", "read"]
    }
  ]
}
```

#### [NEW] [find-skill.sh](file:///home/project/openclaw/curated_skills/find-skill.sh)

A fast keyword search script that searches the skill index and returns matches ranked by relevance. Works with `grep`, `jq`, or pure `bash`.

#### [NEW] [build-index.sh](file:///home/project/openclaw/curated_skills/build-index.sh)

Regenerates `skills-index.json` and `description.md` by scanning all `*/*/SKILL.md` files. Should be run after any skill reorganization.

#### [NEW] [move-skills.sh](file:///home/project/openclaw/curated_skills/move-skills.sh)

The migration script that:
1. Creates the 20 new category directories
2. Moves every skill folder from its current location to the correct new category
3. Removes empty old category directories
4. Generates the fresh index and description files

---

### Phase 2: Category Creation & Skill Migration

For each of the 38 existing category folders, every skill sub-folder will be moved into one of the 20 new categories. The move script will:

1. Read a mapping file (`skill-mapping.tsv`) that maps `old-category/skill-name` → `new-category`
2. Execute `mv old-category/skill-name new-category/skill-name`
3. Remove empty old directories with `rmdir`

The mapping will be generated by analyzing each skill's description against the category definitions above.

---

### Phase 3: Quick Search System

Three complementary discovery mechanisms:

| Tool | Purpose | User |
|------|---------|------|
| `find-skill.sh <keywords>` | CLI keyword search, returns top matches with paths | AI agent or human |
| `skills-index.json` | Machine-readable full index | AI agent (JSON parse) |
| `description.md` | Human-readable flat list | Human review |

The `find-skill.sh` script will:
- Accept one or more keywords as arguments
- Search skill names and descriptions (case-insensitive)
- Return results ranked by number of keyword matches
- Show: category, skill name, description snippet

---

### Phase 4: Cleanup

#### [DELETE] Old empty category directories (after move)
All 38 original directories will be removed if empty after migration.

#### [MODIFY] [description.md](file:///home/project/openclaw/curated_skills/description.md)
Regenerated from the new structure via `build-index.sh`.

#### Archive files
- `REORGANIZATION_MANIFEST.md` → archived (superseded)
- `clean-up.sh`, `pre-clean.sh`, `todo.txt` → archived

---

## Verification Plan

### Automated Verification (via script)

1. **Skill count integrity**: Compare `find . -maxdepth 2 -name "SKILL.md" | wc -l` before and after — must be identical.

2. **No orphaned skills**: `find . -maxdepth 1 -type d` should show exactly 20 category dirs plus `.git` and any root files.

3. **Index completeness**: `jq '.total_skills' skills-index.json` must match the SKILL.md count.

4. **Empty directory check**: `find . -maxdepth 1 -type d -empty` should return nothing.

Run verification:
```bash
# From /home/project/openclaw/curated_skills/
# Pre-move count
PRE=$(find . -maxdepth 2 -name "SKILL.md" | wc -l)
echo "Pre-move skill count: $PRE"

# Execute move
bash move-skills.sh

# Post-move count
POST=$(find . -maxdepth 2 -name "SKILL.md" | wc -l)
echo "Post-move skill count: $POST"

# Verify
[ "$PRE" -eq "$POST" ] && echo "✅ Count match" || echo "❌ MISMATCH: $PRE vs $POST"

# Check no old dirs remain
OLD_DIRS=$(find . -maxdepth 1 -type d | grep -vE '^\.$|\.git' | wc -l)
echo "Category dirs: $OLD_DIRS (should be 20)"

# Check index
jq '.total_skills' skills-index.json
```

### Manual Verification

1. Run `bash find-skill.sh email send` and confirm it returns skills like `gmail-client`, `send-email`, `himalaya`, etc.
2. Run `bash find-skill.sh docker deploy` and confirm it returns relevant DevOps skills.
3. Spot-check 5-10 skill paths to confirm `SKILL.md` files are intact and in correct categories.
