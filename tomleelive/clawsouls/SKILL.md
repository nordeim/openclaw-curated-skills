---
name: clawsouls
description: Manage AI agent personas (Souls) for OpenClaw. Use when the user wants to install, switch, list, or restore AI personalities/personas. Triggers on requests like "install a soul", "switch persona", "change personality", "list souls", "restore my old soul", "use minimalist", "browse personas", "what souls are available", "publish a soul", or "login to clawsouls".
---

# ClawSouls — AI Persona Manager

Manage Soul packages that define an AI agent's personality, behavior, and identity.

Souls use `owner/name` namespacing (e.g., `clawsouls/surgical-coder`, `TomLeeLive/my-soul`).

## Prerequisites

Ensure `clawsouls` CLI is available:

```bash
npx clawsouls --version
```

If not installed, install globally:

```bash
npm install -g clawsouls
```

Current version: **v0.4.0**

## Commands

### Install a Soul

```bash
npx clawsouls install clawsouls/surgical-coder
npx clawsouls install clawsouls/surgical-coder --force       # overwrite existing
npx clawsouls install clawsouls/surgical-coder@0.1.0         # specific version
```

79+ souls available. Browse all at https://clawsouls.ai

**Official souls** (owner: `clawsouls`):
- **Development:** code-reviewer, coding-tutor, debug-detective, api-architect, ml-engineer, sysadmin-sage, devops-veteran, gamedev-mentor, prompt-engineer, frontend-dev, backend-dev, mobile-dev, cloud-architect, database-admin, qa-engineer
- **Writing & Content:** tech-writer, storyteller, scifi-writer, copywriter, content-creator, journalist, poet, screenwriter, academic-writer
- **Professional:** data-analyst, project-manager, legal-advisor, startup-founder, hr-manager, marketing-strategist, sales-coach, product-manager
- **Education:** math-tutor, philosophy-prof, mentor-coach, science-tutor, history-prof, language-teacher, economics-tutor
- **Creative:** music-producer, ux-designer, chef-master, graphic-designer, video-editor, podcast-host, dungeon-master, game-designer
- **Lifestyle:** personal-assistant, fitness-coach, travel-guide, life-coach, meditation-guide, nutrition-advisor, productivity-guru, financial-planner
- **Science:** research-scientist, data-scientist
- **Security:** security-auditor
- **MBTI:** mbti-intj, mbti-intp, mbti-entj, mbti-entp, mbti-infj, mbti-infp, mbti-enfj, mbti-enfp, mbti-istj, mbti-isfj, mbti-estj, mbti-esfj, mbti-istp, mbti-isfp, mbti-estp, mbti-esfp
- **Special:** surgical-coder, korean-translator
- **General:** brad, minimalist

### Activate a Soul

```bash
npx clawsouls use clawsouls/surgical-coder
```

- Automatically backs up current workspace files (SOUL.md, IDENTITY.md, AGENTS.md, HEARTBEAT.md, STYLE.md, examples/)
- Never overwrites USER.md, MEMORY.md, or TOOLS.md
- Requires gateway restart to take effect

### Restore Previous Soul

```bash
npx clawsouls restore
```

Reverts to the most recent backup created by `use`.

### List Installed Souls

```bash
npx clawsouls list
```

Shows installed souls in `owner/name` format.

### Create a New Soul

```bash
npx clawsouls init my-soul
```

Scaffolds a new soul directory with `soul.json`, SOUL.md, IDENTITY.md, AGENTS.md, HEARTBEAT.md, README.md.

### Validate a Soul

```bash
npx clawsouls validate ./my-soul/
npx clawsouls validate --soulscan ./my-soul/   # with SoulScan security analysis
npx clawsouls check ./my-soul/                 # alias
```

Validates against the spec: schema, required files. Add `--soulscan` for full security & quality analysis with scoring. Also runs automatically before publish.

### SoulScan — Security & Integrity Scanner

```bash
npx clawsouls soulscan              # scan current OpenClaw workspace
npx clawsouls soulscan ./my-soul/   # scan a specific directory
npx clawsouls soulscan --init       # initialize baseline checksums
npx clawsouls soulscan -q           # quiet mode for cron (SOULSCAN_OK / SOULSCAN_ALERT)
npx clawsouls scan                  # alias
```

SoulScan checks active soul files for:
- **Integrity**: SHA-256 checksum comparison — detects tampering since last scan
- **Security**: 53 pattern checks (prompt injection, code execution, XSS, data exfiltration, privilege escalation, social engineering, harmful content, secret detection)
- **Quality**: File structure, content length, schema validation
- **Persona Consistency**: Cross-validates name/tone across SOUL.md, IDENTITY.md, soul.json

**Cron usage** — periodic tamper detection:
```bash
# Run every hour to monitor workspace integrity
npx clawsouls soulscan -q
# Exit code 0 = OK, 1 = alert (tampered or security issue)
```

**First run**: Use `--init` to establish baseline checksums without triggering alerts.

SOULSCAN™ — Score: 0-100, Grades: Verified (90+) / Low Risk (70+) / Medium Risk (40+) / High Risk / Blocked

### Publish a Soul

```bash
export CLAWSOULS_TOKEN=<token>
npx clawsouls publish ./my-soul/
```

Publishes to `username/soul-name` namespace automatically. Requires authentication token. Runs validation automatically before publishing — blocks on failure.

### Login / Get Token

```bash
npx clawsouls login
```

Instructions to get API token: Sign in at https://clawsouls.ai → Dashboard → Generate API Token.

## Workflow

### Installing & Switching Personas

1. **Browse** — Check available souls at https://clawsouls.ai or suggest from the categorized list above
2. **Install** — `npx clawsouls install clawsouls/surgical-coder`
3. **Activate** — `npx clawsouls use clawsouls/surgical-coder`
4. **Restart** — Run `openclaw gateway restart` to apply the new persona
5. **Restore** — If they want to go back, `npx clawsouls restore`

### Publishing a Soul

1. **Login** — `npx clawsouls login` → get token from dashboard
2. **Set token** — `export CLAWSOULS_TOKEN=<token>`
3. **Create** — `npx clawsouls init my-soul` → edit files
4. **Publish** — `npx clawsouls publish ./my-soul/`
5. **Manage** — Dashboard at https://clawsouls.ai/dashboard (delete, view downloads)

## Important Notes

- After `use`, always remind the user to run `openclaw gateway restart`
- The `use` command creates automatic backups — data loss is unlikely
- Souls may include STYLE.md and examples/ for enhanced persona customization
- Published souls appear at `https://clawsouls.ai/souls/owner/name`
- Users can leave reviews (1-5 stars) on any soul they don't own
- For custom registry (local testing), set env: `CLAWSOULS_CDN=/path/to/souls`
- Website available in 5 languages: English, Korean, Japanese, Chinese, Spanish (e.g., `clawsouls.ai/ko/souls/...`)
- Share any soul to your OpenClaw bot: the install command is included in the share text
- **The Soul Thesis** — Read the manifesto: https://clawsouls.ai/en/manifesto
- **Research paper** — "Soul-Driven Interaction Design": https://doi.org/10.5281/zenodo.18661656
- Legal: [Privacy Policy](https://clawsouls.ai/en/privacy) · [Terms of Service](https://clawsouls.ai/en/terms)
