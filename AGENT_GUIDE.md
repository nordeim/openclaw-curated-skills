# Agent Guide — OpenClaw Curated Skills

> **Audience:** This document is for AI agents operating within the OpenClaw ecosystem.
> It explains what this repository contains, how it is organized, and how to find and use the right skill for any task.

---

## What This Repository Is

This is a collection of **791 skills** — self-contained instruction sets that extend your capabilities. Each skill is a folder containing a `SKILL.md` file that tells you:

- What the skill does
- When and why to use it
- How to invoke it (commands, scripts, API calls, environment variables)
- What dependencies or credentials are required

**You do not need to read all 791 skills.** Use the search system described below to find only what you need.

---

## How Skills Are Organized

Skills are grouped into **20 categories** named by intent — what you, the agent, are trying to accomplish:

```
agent-core/               — Your own task tracking, memory, context management
agent-orchestration/       — Delegating to other agents, model routing
browser-automation/        — Controlling web browsers programmatically
business-operations/       — CRM, e-commerce, SaaS, invoicing
communication-messaging/   — Sending/receiving email, chat, SMS, notifications
content-publishing/        — Posting to social media, blogs, SEO
data-analytics/            — Dashboards, reports, CSV/Excel processing
developer-tools/           — Git, code review, UI/UX, accessibility
devops-cloud/              — Docker, Kubernetes, deployment, CI/CD
finance-markets/           — Stock data, accounting, investment analysis
games-entertainment/       — Games, music players, media playback
integrations-connectors/   — API connectors, ClawHub, Google Workspace
knowledge-research/        — Deep research, arXiv, news, knowledge graphs
media-generation/          — Creating images, video, speech (TTS), music
media-processing/          — Transcribing audio, OCR, video editing, format conversion
productivity-personal/     — Calendars, reminders, note-taking, health tracking
search-web/                — Web search engines (DuckDuckGo, SearXNG, Tavily, etc.)
security-compliance/       — Vulnerability scanning, content moderation
smart-home-iot/            — Smart devices, robots, sensors, home automation
travel-transport/          — Flights, trains, trip planning, navigation
```

---

## How to Find the Right Skill

### Method 1: Category Browsing (fastest for clear intent)

If you know **what you need to do**, map your intent directly to a category name:

| Your intent | Look in |
|-------------|---------|
| "Send an email" | `communication-messaging/` |
| "Generate an image" | `media-generation/` |
| "Search the web" | `search-web/` |
| "Deploy a container" | `devops-cloud/` |
| "Transcribe audio" | `media-processing/` |
| "Track a task" | `agent-core/` or `productivity-personal/` |
| "Delegate to another model" | `agent-orchestration/` |
| "Control a smart light" | `smart-home-iot/` |
| "Find flight prices" | `travel-transport/` |
| "Scan for vulnerabilities" | `security-compliance/` |

Then list the category directory and read the `SKILL.md` of the best match.

### Method 2: Keyword Search via `find-skill.sh`

Run from the repository root:

```bash
bash find-skill.sh <keyword1> [keyword2] ...
```

**Examples:**

```bash
bash find-skill.sh email send          # Find email-sending skills
bash find-skill.sh -c media-generation image   # Image skills in media-generation only
bash find-skill.sh -j docker deploy    # JSON output for programmatic parsing
bash find-skill.sh -n 5 tts            # Top 5 text-to-speech skills
```

Results arrive ranked by relevance. Name matches score higher than description-only matches.

### Method 3: Parse `skills-index.json` (best for programmatic access)

The file `skills-index.json` at the repository root contains every skill as a JSON object:

```json
{
  "name": "gmail-client",
  "category": "communication-messaging",
  "path": "communication-messaging/gmail-client",
  "description": "Read and send emails via Gmail..."
}
```

You can parse this file to:
- Search by substring match on `name` or `description`
- Filter by `category`
- Build your own ranking logic

### Method 4: Grep `description.md` (simplest fallback)

The file `description.md` is a flat text file with one line per skill:

```
communication-messaging/gmail-client/SKILL.md:description: Read and send emails via Gmail...
```

Use `grep` for quick substring matching:

```bash
grep -i "email" description.md
```

---

## How to Use a Skill

Once you've identified a skill, follow this process:

### Step 1: Read the SKILL.md

```bash
cat <category>/<skill-name>/SKILL.md
```

The `SKILL.md` contains everything you need:
- **`description:`** — One-line summary (in YAML frontmatter)
- **Prerequisites** — Dependencies, API keys, environment setup
- **Usage** — Exact commands, scripts, or API calls to execute
- **Trigger patterns** — When this skill should be activated

### Step 2: Check Prerequisites

Many skills require:
- **API keys** — Set as environment variables (e.g., `OPENAI_API_KEY`)
- **CLI tools** — Installed via `pip install`, `npm install`, or `brew install`
- **Runtime** — Python 3.10+, Node.js 18+, or specific frameworks
- **Credentials** — OAuth tokens, login credentials stored in config files

If dependencies are missing, the `SKILL.md` will specify how to install them.

### Step 3: Execute

Follow the exact instructions in the skill's `SKILL.md`. Most skills provide:
- Shell commands to run directly
- Python/Node.js scripts with arguments
- API endpoints to call
- MCP server configurations

### Step 4: Handle Results

Skill outputs vary — some return JSON, some produce files, some print to stdout. The `SKILL.md` documents what to expect.

---

## Decision Framework

When multiple skills match your intent, use this precedence:

1. **Name match** — A skill whose name directly matches your task (e.g., `gmail-client` for Gmail)
2. **Category match** — A skill in the most relevant category
3. **Description specificity** — The skill whose description most closely matches your specific use case
4. **Fewer dependencies** — Prefer skills with simpler setup when capabilities are equivalent

---

## Security: Verifying New Skills

All skills in this repository have been scanned by **TrustSkill v3.1** (located in `trustskill/`). If you encounter a skill from an external source or need to add one:

```bash
cd trustskill/
source /opt/venv/bin/activate
python src/cli.py /path/to/skill --mode deep
```

**Interpretation:**
- **Exit code 0** → Safe. No high-risk findings.
- **Exit code 1** → High-risk issues detected. Do NOT use without human review.

**Immediate rejection criteria:**
- `data_exfiltration` findings (sending data to unknown servers)
- `command_injection` findings (user input reaching `eval`/`exec`)
- `hardcoded_secret` with confidence > 0.9 (real credentials, not placeholders)

---

## What NOT to Do

1. **Do not iterate over all 791 skills** — Use the search system instead
2. **Do not assume a skill's category is its only use case** — Read the `SKILL.md`
3. **Do not execute scripts from unscanned skills** — Always TrustSkill-scan first
4. **Do not hardcode skill paths** — Categories may be restructured; use `find-skill.sh` or `skills-index.json`
5. **Do not modify `skills-index.json` manually** — Use `python3 build-index.py` to regenerate

---

## Quick Reference Card

| Action | Command |
|--------|---------|
| Find a skill | `bash find-skill.sh <keywords>` |
| List all categories | `ls -d */` |
| Read a skill's docs | `cat <category>/<skill>/SKILL.md` |
| Search (JSON output) | `bash find-skill.sh -j <keywords>` |
| Rebuild index | `python3 build-index.py` |
| Scan a new skill | `cd trustskill/ && python src/cli.py /path/to/skill --mode deep` |
| Count all skills | `jq '.total_skills' skills-index.json` |
| List one category | `ls <category>/` |

---

*This guide is maintained alongside the skill collection. Last updated: 2026-02-23.*
