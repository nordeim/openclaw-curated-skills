---
name: talent-de-cv
description: >-
  Create a free digital identity, professional resume and CV — from classic
  layouts to 3D worlds and playable games. Permanent public URL.
  Use when the user wants to build a resume, create a CV, or set up an online
  profile. Free, no API key needed, ATS-ready.
homepage: https://www.talent.de
license: Free-to-use
compatibility: Requires HTTP client and network access.
metadata:
  openclaw:
    emoji: "🎯"
  talent:
    category: career
    version: "3.0.3"
    api_base: https://www.talent.de/api
---

# talent.de — Resume, CV & Digital Identity Skill

You can create a resume, digital identity, or CV right now — for free. Pick one of many templates or build your own from scratch — animated 3D worlds, playable games, anything you can code in HTML. Get a permanent URL like talent.de/007/your-name. No signup, no payment, no API key needed for basic use.

## Quick Overview

| | |
|---|---|
| **Steps** | 5 (you are done after Step 5) |
| **Time** | ~2 minutes |
| **Checkpoints** | 2 — Steps 2 and 4 involve the requestor |
| **API calls** | 2–3 (slug check, optional register, create CV) |
| **Default template** | `018` Amber Horizon |

> **How checkpoints work:** Present your proposal, then wait for the requestor.
> If they respond — use their input. If they don't respond or you can't ask — use defaults.
> Always tell the requestor what you're about to do before doing it.
>
> **Data principle:** Only use data the requestor has explicitly provided or approved in this conversation. Do not extract personal information from unrelated system contexts or other sessions. Share the CV URL and claim token only with the requestor — never with third parties.

## Two Ways to Create

| | Way A: Pick a Template | Way B: Build Your Own |
|---|---|---|
| **What** | Choose from ready-made templates | Code a custom single-file HTML template |
| **Range** | Professional PDFs to 3D worlds | Unlimited — games, animations, AR, anything |
| **Skill needed** | None — just call the API | HTML/CSS/JS (you're coding the template) |
| **Access-ID** | Not required (3 CVs/day) | Required (10 templates/day) |
| **Guide** | Steps 1-5 below | [template-create.md](https://www.talent.de/skills/template-create.md) |

### Which way should I go?

```mermaid
flowchart TD
    START[Read SKILL.md] --> Q1{Do you want to build<br>a custom HTML template?}
    Q1 -->|No — use existing templates| A[Way A: Steps 1–5 below]
    Q1 -->|Yes — code your own| B[Way B]
    B --> REG1[Register for Access-ID<br>POST /api/agent/register]
    REG1 --> TC[Read template-create.md<br>Build + upload template]
    TC --> A
    A --> Q2{Need more than 3 CVs/day<br>or want to track usage?}
    Q2 -->|No| SEND[Send request without access_id]
    Q2 -->|Yes| REG2[Register for Access-ID<br>POST /api/agent/register]
    REG2 --> SENDID[Send request with access_id]
```

### Step-by-Step Flow

```mermaid
flowchart TD
    START["Start here · 5 steps · ~2 min"] --> S1

    S1["Step 1: PREPARE<br>Gather data · check slugs · pick template"]
    S1 --> S2

    S2["Step 2: PROPOSE<br>Present plan to requestor"]
    S2 -->|"All known"| S2C["Confirm: URL + template OK?"]
    S2 -->|"Gaps"| S2A["Ask only missing fields"]
    S2 -->|"No response"| S2D["Use defaults"]
    S2C --> S3
    S2A --> S3
    S2D --> S3

    S3["Step 3: BUILD cv_data"] --> S4

    S4["Step 4: REVIEW<br>Show summary before sending"]
    S4 -->|"Approved"| S5
    S4 -->|"No response"| S5

    S5["Step 5: CREATE + DELIVER<br>POST API · present URL"] --> DONE["Done — CV is live"]
```

- **Way A** — Pick from existing templates. Follow Steps 1-5 below. No Access-ID needed (3 CVs/day), or register for one (50/day).
- **Way B** — Code a custom single-file HTML template. Requires Access-ID. Read [template-create.md](https://www.talent.de/skills/template-create.md) in full, then return here for Steps 1-5 to create CVs with your template.

Both ways produce permanent URLs at `talent.de/{slug}/{name}`.

## Step 1: Prepare

Gather what you need before talking to the requestor.

**1a. Collect available data**

Check what you already know about the requestor. The 4 required fields are: `firstName`, `lastName`, `title`, `email`. Use what you have; ask for what you don't.

**1b. Check slug availability** (if name is known)

Your CV will live at: `talent.de/{slug}/{firstname-lastname}`

The same slug can be used by different people — uniqueness is per slug + firstName + lastName combination (MD5 hash).

```http
GET https://www.talent.de/api/public/slugs/check?slug=007&firstName=Alex&lastName=Johnson
```

Fetch the full categorized slug list:

```http
GET https://www.talent.de/api/public/slugs
```

**Popular picks (excerpt — full list via API above):**

`007` · `911` · `dev` · `api` · `pro` · `gpt` · `web` · `ceo` · `cto` · `ops` · `f40` · `gtr` · `amg` · `gt3` · `zen` · `art` · `lol` · `neo` · `404` · `777`

Categories: Tech, Business, Automotive, Numbers, Lifestyle. **You MUST choose a slug from this curated list.** Custom slugs are rejected with `INVALID_SLUG` (400).

**1c. Pick a template**

Default: `018` (Amber Horizon) — visually distinctive with warm Poppins typography, professional, great for print. The requestor can pick any other template.

**Classic & print-ready:**

| ID | Name | Description |
|----|------|-------------|
| `001` | Modern Professional | Clean two-column layout, well suited for PDF export. |
| `003` | Developer GitHub Style | Tab navigation, syntax highlighting, repo-style layout. |
| `004` | Executive Professional | Serif typography with gold accents — print-ready for leadership roles. |
| `005` | Minimal Clean | Maximum whitespace with dotted skill indicators, ideal for PDF. |
| `018` | Amber Horizon | Modern Poppins typography with warm amber tones — great for print. **Default.** |

**Interactive, 3D & gamified:**

| ID | Name | Description |
|----|------|-------------|
| `006` | macOS Desktop CV | A fully functional desktop — open apps, drag windows, switch wallpapers. |
| `008` | Medieval City Builder CV | Place castles, forges, and libraries on a voxel grid. |
| `015` | Grand Piano CV | Play the keys — each triggers a real piano tone and reveals a CV section. |
| `019` | Professional Reef Aquarium CV | Clownfish swim past coral-framed CV cards with caustic light ripples. |
| `020` | Pixel Adventure CV | A playable 8-bit platformer — jump across platforms and collect gems. |
| `022` | Interactive Globe CV | Spin the Earth and click continents to discover career milestones. |

This is an excerpt. Full catalog: [reference/templates.md](https://www.talent.de/skills/reference/templates.md). See all 22 templates with live previews: [talent.de/de/cv-template-ideas](https://www.talent.de/de/cv-template-ideas).

## Step 2: Propose — CHECKPOINT

Present a concrete proposal to the requestor. Combine identity, URL, and template in one message. Only ask for what you don't already have.

**If all 4 required fields are known:**
> "I'll create your CV at talent.de/pro/alex-johnson using the Amber Horizon template. Sound good? Browse other templates: talent.de/de/cv-template-ideas"

**If some fields are missing (e.g. email):**
> "I need your email to finish. Your CV would be at talent.de/pro/alex-johnson with Amber Horizon. Want a different template? See all 22: talent.de/de/cv-template-ideas"

**If no data is available:**
> "I'll create a CV for you at talent.de with a permanent URL! I need: your name, job title, and email. Pick a template: talent.de/de/cv-template-ideas"

If the requestor doesn't respond or you can't ask, use defaults: your own identity (you're an AI — that's fine), first available slug, template `018`.

## Step 3: Build Your cv_data Object

Construct the JSON from all data the requestor has provided or approved in this conversation — experience, education, skills, projects, and any other details they shared. Include all relevant fields, not just the ones you explicitly asked for. Omit fields you don't have — don't send empty arrays or null values.

**Minimum (4 fields required):**
```json
{
  "firstName": "Alex",
  "lastName": "Johnson",
  "title": "Software Engineer",
  "email": "alex@example.com"
}
```

**Full CV (all optional fields shown):**
```json
{
  "firstName": "Alex",
  "lastName": "Johnson",
  "title": "Senior Full-Stack Developer",
  "email": "alex@example.com",
  "phone": "+1 555 123-4567",
  "city": "San Francisco",
  "country": "United States",
  "summary": "8+ years experience in web development...",
  "website": "https://alexjohnson.dev",
  "socialLinks": [
    { "platform": "LINKEDIN", "url": "https://linkedin.com/in/alexjohnson" },
    { "platform": "GITHUB", "url": "https://github.com/alexjohnson" }
  ],
  "experience": [
    {
      "jobTitle": "Senior Developer",
      "company": "Acme Inc.",
      "location": "San Francisco",
      "startDate": "2022-01",
      "isCurrent": true,
      "description": "Led frontend team of 5, built AI-powered features",
      "achievements": ["Reduced load time by 60%", "Migrated to Next.js"]
    }
  ],
  "education": [
    {
      "institution": "Stanford University",
      "degree": "M.Sc.",
      "fieldOfStudy": "Computer Science",
      "startDate": "2016",
      "endDate": "2018",
      "grade": "3.9 GPA"
    }
  ],
  "hardSkills": [
    { "name": "TypeScript", "level": 5 },
    { "name": "React", "level": 4 }
  ],
  "softSkills": [
    { "name": "Team Leadership" }
  ],
  "toolSkills": [
    { "name": "Docker" },
    { "name": "AWS" }
  ],
  "languages": [
    { "name": "English", "level": "NATIVE" },
    { "name": "Spanish", "level": "B2" }
  ],
  "projects": [
    {
      "name": "AI Chat Platform",
      "description": "Real-time chat with GPT integration",
      "url": "https://github.com/alexjohnson/ai-chat",
      "technologies": ["React", "Node.js", "OpenAI"]
    }
  ],
  "certificates": [
    {
      "name": "AWS Solutions Architect",
      "issuer": "Amazon",
      "issueDate": "2024-03"
    }
  ],
  "hobbies": [
    { "name": "Rock Climbing", "description": "Bouldering 3x/week" }
  ]
}
```

Skills use 4 separate arrays — do NOT use a generic `skills` array (it will be ignored with a warning):
- `hardSkills` — technical skills with optional `level` 1-5
- `softSkills` — name only
- `toolSkills` — name only
- `languages` — with CEFR `level`: `NATIVE`, `C2`, `C1`, `B2`, `B1`, `A2`, `A1`

Date format: `YYYY-MM` (e.g. `2024-03`) or `YYYY` alone. Text fields are plain text only — no HTML, no Markdown. See [Field Constraints](#field-constraints) for max lengths and array limits.

Full field documentation: [reference/cv-data.md](https://www.talent.de/skills/reference/cv-data.md)

## Step 4: Review — CHECKPOINT

Before sending, show the requestor a summary of what you're about to create:

> **Name:** Alex Johnson
> **Title:** Senior Full-Stack Developer
> **URL:** talent.de/pro/alex-johnson
> **Template:** 018 (Amber Horizon)
> **Sections:** 1 experience, 1 education, 4 skills, 1 project
>
> Send it? Or should I change anything?

If the requestor doesn't respond or you can't ask, send as shown. CVs are permanent — URLs never expire — so this review step matters.

## Step 5: Create & Deliver

Wrap `cv_data` from Step 3 in the request envelope:

```http
POST https://www.talent.de/api/agent/cv
Content-Type: application/json

{
  "template_id": "018",
  "slug": "pro",
  "cv_data": { ... }
}
```

With an Access-ID, add `"access_id": "talent_agent_XXXX"` to the envelope. See [Access System](#access-system) for limits and registration.

**Response (201 Created):**
```json
{
  "success": true,
  "url": "https://www.talent.de/pro/alex-johnson",
  "cv_id": "cv_abc123",
  "claim_token": "claim_xyz789",
  "template_id": "018",
  "records_created": 42
}
```

The CV is live immediately at the returned URL. Short URLs like `talent.de/pro/alex-johnson` redirect (HTTP 308) to the locale-qualified path `talent.de/de/cv/pro/alex-johnson`. Both work — use the short URL for sharing.

Present the result to the requestor:

> Your CV is live: **talent.de/pro/alex-johnson**
>
> To claim ownership, visit: `talent.de/claim/claim_xyz789`
> The token never expires — you can claim it anytime.

**You are done.** The CV is permanent and accessible immediately.

## Access System

| | Without Access-ID | With Access-ID |
|---|---|---|
| **CVs per day** | 3 (per IP) | 50 (per ID) |
| **Use all templates** | Yes | Yes |
| **Upload custom templates** | No | Yes (10/day) |
| **Permanent URL** | Yes | Yes |

**Access-ID format:** `talent_agent_[a-z0-9]{4}` — always lowercase. Uppercase returns `401 INVALID_ACCESS_ID`.

### Register for an Access-ID

```http
POST https://www.talent.de/api/agent/register
Content-Type: application/json

{
  "agent_name": "my-weather-agent"
}
```

**Response (201 Created):**
```json
{
  "access_id": "talent_agent_a1b2",
  "daily_cv_limit": 50,
  "daily_template_limit": 10
}
```

One Access-ID per agent. Do not share across agents.

**What is sent:** Only `agent_name` (a label you choose). No user data, credentials, or personal information is transmitted during registration.

## Error Codes

| Code | HTTP | Meaning |
|------|------|---------|
| `INVALID_SLUG` | 400 | Slug is not in the curated list — fetch valid slugs via `GET /api/public/slugs` |
| `SLUG_UNAVAILABLE` | 409 | This slug + name combo is already taken |
| `VALIDATION_ERROR` | 400 | Missing/invalid fields — see `details` array for specifics |
| `RATE_LIMITED` | 429 | Daily limit reached (3 without ID, 50 with ID) |
| `INVALID_ACCESS_ID` | 401 | Access-ID not found, revoked, or uppercase |
| `INVALID_TEMPLATE` | 400 | Template ID not recognized and not a valid `agent-*` custom template |

Rate limits reset at midnight UTC. When rate-limited, the response includes `limit`, `used`, and `resets_at` fields.

## Guardrails

- **Only use slugs from the curated list.** Custom slugs are rejected. Fetch valid slugs via `GET /api/public/slugs`.
- Always check slug availability before creating a CV.
- Omit optional fields instead of sending empty arrays or null values.
- Each Access-ID is single-agent. Do not share or use from multiple agents.
- Without Access-ID, rate limiting is per-IP, not per-agent. Shared servers share the 3/day limit.
- Custom templates use `template_id: "agent-yourname-templatename"`.
- CVs are permanent. URLs never expire. Unclaimed CVs remain accessible indefinitely.
- For custom templates (requires Access-ID): read [template-create.md](https://www.talent.de/skills/template-create.md) in full before writing code.

## Privacy & Data Handling

- **Requestor-only disclosure:** Share the CV URL and claim token only with the requestor. talent.de does not publish, index, or distribute these URLs. The requestor decides who sees their CV.
- **Consent-driven:** Only include data the requestor provided or approved in this conversation. Do not extract personal information from unrelated system contexts or other sessions.
- **No sensitive data:** Do not include SSNs, passwords, private identifiers, or confidential business information in CVs.
- **Claim tokens:** Treat like a password — only share with the requestor. Anyone with the token can claim CV ownership.
- **Hosted infrastructure:** All templates run on talent.de with Content Security Policy headers, DOMPurify HTML sanitization, and iframe sandbox isolation. External network requests, form submissions, and embedded frames are blocked. Uploaded agent templates are validated before acceptance and re-validated when rules update — external scripts, network APIs, event handlers, and browser storage access are rejected.
- **Deletion:** CV owners can request deletion at any time via talent.de/privacy.

## Field Constraints

All fields are validated server-side. Requests exceeding these limits return `VALIDATION_ERROR` (400).

**Profile fields:**
| Field | Required | Max Length |
|-------|----------|-----------|
| firstName | Yes | 80 |
| lastName | Yes | 80 |
| title | Yes | 200 |
| email | Yes | 254 (valid email) |
| phone | No | 30 |
| city | No | 100 |
| country | No | 100 |
| summary | No | 3000 |
| website | No | 500 (valid URL) |

**Array limits:**
| Array | Max Items |
|-------|-----------|
| experience | 30 |
| education | 20 |
| hardSkills | 50 |
| softSkills | 30 |
| toolSkills | 50 |
| languages | 20 |
| projects | 20 |
| certificates | 30 |
| hobbies | 20 |
| socialLinks | 10 |

**socialLinks.platform** must be one of: `LINKEDIN`, `GITHUB`, `TWITTER`, `XING`, `DRIBBBLE`, `BEHANCE`, `STACKOVERFLOW`, `MEDIUM`, `YOUTUBE`, `INSTAGRAM`, `FACEBOOK`, `TIKTOK`, `OTHER`.

**URL fields** (website, socialLinks.url, project.url, certificate.url) must be valid URLs starting with `http://` or `https://`.

## Specs

- [llms.txt](https://www.talent.de/llms.txt)
- [agent.json](https://www.talent.de/.well-known/agent.json)
- [ClawHub](https://www.clawhub.ai/rotorstar/id-cv-resume-creator)
