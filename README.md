# OpenClaw Curated Skills

<div align="center">

**791 security-vetted skills for AI agents** — organized into 20 searchable categories with instant discovery tooling.

[![Skills](https://img.shields.io/badge/skills-791-4361ee)](skills-index.json)
[![Categories](https://img.shields.io/badge/categories-20-06d6a0)](.)
[![Security](https://img.shields.io/badge/scanned_by-TrustSkill_v3.1-ef233c)](trustskill/)
[![License](https://img.shields.io/badge/license-MIT-f8f9fa)](LICENSE)

</div>

---

## What Is This?

A curated, security-audited collection of skills for the [OpenClaw](https://openclaw.com) AI agent ecosystem. Each skill is a self-contained folder with a `SKILL.md` manifest that teaches an AI agent *how* to do something — send email, generate images, control smart home devices, search the web, manage tasks, and hundreds more.

This repository solves three problems:

1. **Discovery** — Find the right skill in seconds via `find-skill.sh` or `skills-index.json`
2. **Trust** — Every included skill has been scanned by [TrustSkill v3.1](#-security--trustskill) for malicious code, hardcoded secrets, vulnerable dependencies, and data exfiltration
3. **Organization** — 20 named categories designed around *what the agent is trying to accomplish*, not arbitrary taxonomies

---

## Category Directory

| Category | Skills | What Agents Use It For |
|----------|:------:|------------------------|
| [`agent-core`](agent-core/) | 46 | Task tracking, memory, context recovery, session state, self-improvement |
| [`agent-orchestration`](agent-orchestration/) | 29 | Multi-agent delegation, model routing, spawning, A2A protocols |
| [`browser-automation`](browser-automation/) | 21 | Playwright, Stagehand, headless browsing, form filling, scraping |
| [`business-operations`](business-operations/) | 24 | CRM, Shopify, SaaS, invoicing, real estate, lead generation |
| [`communication-messaging`](communication-messaging/) | 76 | Email, WhatsApp, Telegram, Discord, SMS, Slack, IRC, notifications |
| [`content-publishing`](content-publishing/) | 46 | X/Twitter, LinkedIn, blog writing, SEO, social media, Moltbook |
| [`data-analytics`](data-analytics/) | 32 | Dashboards, CSV/Excel, reporting, business intelligence, KPIs |
| [`developer-tools`](developer-tools/) | 58 | Git, PR review, code security, UI/UX, tmux, scaffolding, accessibility |
| [`devops-cloud`](devops-cloud/) | 39 | Docker, Kubernetes, AWS, CI/CD, SSH, deployment, server monitoring |
| [`finance-markets`](finance-markets/) | 20 | Stock data, investment analysis, accounting, EDINET, J-Quants |
| [`games-entertainment`](games-entertainment/) | 32 | Games, Spotify, Sonos, media players, chess, text adventures |
| [`integrations-connectors`](integrations-connectors/) | 29 | ClawHub, Google Workspace, Microsoft 365, Notion, API connectors |
| [`knowledge-research`](knowledge-research/) | 69 | Deep research, arXiv, news, knowledge graphs, RAG, semantic search |
| [`media-generation`](media-generation/) | 52 | Image gen, video gen, TTS, voice cloning, music, avatar video |
| [`media-processing`](media-processing/) | 52 | Transcription (STT), OCR, FFmpeg, document conversion, QR codes |
| [`productivity-personal`](productivity-personal/) | 72 | Task managers, Pomodoro, calendars, reminders, health, finance |
| [`search-web`](search-web/) | 31 | DuckDuckGo, SearXNG, Tavily, Google, metasearch, Exa |
| [`security-compliance`](security-compliance/) | 24 | Vulnerability scanning, prompt injection defense, content moderation |
| [`smart-home-iot`](smart-home-iot/) | 23 | Smart lights, robots, 3D printers, sensors, home automation |
| [`travel-transport`](travel-transport/) | 24 | Flights, trains, trip planning, bus booking, navigation |

---

## Quick Start

### Find a Skill

```bash
# Search by keyword — returns ranked results
bash find-skill.sh email send

# Filter by category
bash find-skill.sh -c media-generation image

# JSON output for programmatic use
bash find-skill.sh -j -n 5 docker deploy

# Show all matches
bash find-skill.sh -a tts voice
```

### Use a Skill

Each skill folder contains a `SKILL.md` file. This is the skill's API contract — read it to understand:

- **What** the skill does (`description:` field)
- **When** to trigger it (trigger patterns and use cases)
- **How** to invoke it (commands, scripts, API calls)
- **What** it requires (dependencies, API keys, environment variables)

```
media-generation/gemini-image-remix/
├── SKILL.md          ← Read this first
├── scripts/          ← Executable scripts
└── ...
```

---

## Skill Search System

Three complementary ways to discover skills:

| Tool | Format | Best For |
|------|--------|----------|
| `find-skill.sh` | CLI table or JSON | Interactive use, quick lookups |
| `skills-index.json` | Machine-readable JSON | Programmatic access, AI agent parsing |
| `description.md` | Flat text list | `grep`-friendly, human scanning |

### `find-skill.sh` Reference

```
Usage: find-skill.sh [-c category] [-n max] [-j] [-a] <keyword1> [keyword2] ...

Options:
  -c <category>   Filter by category name (prefix match)
  -n <number>     Max results (default: 15)
  -j              Output JSON instead of table
  -a              Show all matches (no limit)
```

Results are ranked by relevance — skill *name* matches score higher than description-only matches.

### Rebuilding the Index

After adding, removing, or moving skills, regenerate the index:

```bash
python3 build-index.py
```

This rebuilds both `skills-index.json` and `description.md` from the current folder structure.

---

## 🔒 Security — TrustSkill

Every skill in this repository has been scanned by **[TrustSkill v3.1](trustskill/)**, an advanced security scanner purpose-built for OpenClaw skills. Skills that fail the security audit are removed.

### What TrustSkill Detects

| Severity | Detects |
|----------|---------|
| 🔴 **HIGH** | Command injection, hardcoded secrets, data exfiltration, destructive `rm -rf`, credential harvesting, backdoors |
| 🟡 **MEDIUM** | Vulnerable dependencies (CVEs via OSV), suspicious network requests, code obfuscation, out-of-bounds file access |
| 🟢 **LOW** | Environment variable access, standard file operations, documentation placeholders |

### How It Works

TrustSkill uses five analysis layers:

1. **Regex scanning** — Fast pattern-based detection of known malicious signatures
2. **AST analysis** — Python abstract syntax tree inspection for structural code risks
3. **Entropy detection** — Shannon entropy to distinguish real secrets from placeholders
4. **Taint analysis** — Tracks data flow from user input to dangerous function sinks
5. **Dependency scanning** — Checks against the OSV (Open Source Vulnerabilities) database

### Scan a New Skill Before Adding

Before adding any new skill to this repository, **you must scan it first**:

```bash
# Navigate to the trustskill directory
cd trustskill/

# Activate the Python environment
source /opt/venv/bin/activate

# Run a deep scan on the new skill
python src/cli.py /path/to/new-skill --mode deep

# For JSON output (CI/CD integration)
python src/cli.py /path/to/new-skill --mode deep --format json

# For a detailed markdown report
python src/cli.py /path/to/new-skill --mode deep --export-for-llm
```

**Decision criteria:**
- **Exit code 0** → No high-risk issues. Safe to include.
- **Exit code 1** → High-risk issues detected. Investigate every finding before inclusion.
- **Any `hardcoded_secret` with confidence > 0.9** → Reject unless proven to be a placeholder.
- **Any `data_exfiltration` or `command_injection` finding** → Reject unless thoroughly justified.

### Batch Scan All Skills

```bash
cd trustskill/
source /opt/venv/bin/activate
python scripts/batch_scan.py /path/to/skills-directory --mode deep
```

---

## Adding a New Skill

1. **Create the skill folder** inside the appropriate category:
   ```
   communication-messaging/my-new-skill/
   └── SKILL.md
   ```

2. **Write the `SKILL.md`** with YAML frontmatter:
   ```yaml
   ---
   name: my-new-skill
   description: One-line description of what this skill does and when to use it.
   ---
   
   # My New Skill
   
   Detailed instructions for the AI agent...
   ```

3. **Security scan** the skill:
   ```bash
   cd trustskill/ && source /opt/venv/bin/activate
   python src/cli.py ../communication-messaging/my-new-skill --mode deep
   ```

4. **Rebuild the index**:
   ```bash
   python3 build-index.py
   ```

5. **Verify discoverability**:
   ```bash
   bash find-skill.sh my-new-skill
   ```

---

## Project Structure

```
openclaw/curated_skills/
├── agent-core/                  # 46 skills — Agent self-management
├── agent-orchestration/         # 29 skills — Multi-agent coordination
├── browser-automation/          # 21 skills — Web automation
├── business-operations/         # 24 skills — Business tools
├── communication-messaging/     # 76 skills — Chat, email, SMS
├── content-publishing/          # 46 skills — Social media, blogs
├── data-analytics/              # 32 skills — Data & reporting
├── developer-tools/             # 58 skills — Dev utilities
├── devops-cloud/                # 39 skills — Infrastructure
├── finance-markets/             # 20 skills — Financial data
├── games-entertainment/         # 32 skills — Games & media players
├── integrations-connectors/     # 29 skills — API connectors
├── knowledge-research/          # 69 skills — Research & knowledge
├── media-generation/            # 52 skills — Create media
├── media-processing/            # 52 skills — Transform media
├── productivity-personal/       # 72 skills — Personal tools
├── search-web/                  # 31 skills — Web search
├── security-compliance/         # 24 skills — Security tools
├── smart-home-iot/              # 23 skills — IoT & smart home
├── travel-transport/            # 24 skills — Travel & transit
│
├── trustskill/                  # 🔒 Security scanner (v3.1)
│
├── find-skill.sh                # Keyword search CLI
├── build-index.py               # Index regenerator
├── skills-index.json            # Machine-readable skill index
├── description.md               # Flat skill listing
└── README.md                    # This file
```

---

## For AI Agents

If you are an AI agent reading this repository, see **[AGENT_GUIDE.md](AGENT_GUIDE.md)** for a structured guide on how to navigate, search, and use skills from this collection.

**Quick agent summary:**
- Read `skills-index.json` for the full searchable index
- Match your task intent against category names first
- Read the `SKILL.md` file inside the matched skill folder
- Follow the instructions in `SKILL.md` to execute the skill

---

## License

MIT License — see [LICENSE](LICENSE) for details.

**TrustSkill** scanner is included under the same MIT license.

---

<div align="center">

*Curated with care. Scanned for safety. Organized for speed.*

</div>
