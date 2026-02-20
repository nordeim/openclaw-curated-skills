---
name: opengfx
description: AI brand design system — logo systems, style guides, social assets, and on-brand marketing graphics via ACP or x402.
version: 1.4.0
homepage: https://opengfx.app
source: https://github.com/aklo360/opengfx-skill
author: AKLO Labs <aklo@aklo.studio>
---

# Skill: opengfx

## Description
AI brand design system — generates complete logo systems, style guides, social assets, and on-brand marketing graphics in minutes. **Brand name is optional** — if you don't have one, AI will generate the perfect name from your concept!

**Pricing:**
- Logo System: $5
- Social Assets: $5
- On-Brand GFX: $2

**This is a SERVICE skill** — it documents how to use an external paid API. No code execution, no local files modified, no credentials requested.

---

## Two Integration Options

| Method | Protocol | Best For |
|--------|----------|----------|
| **ACP** | Virtuals Protocol | OpenClaw agents with ACP skill |
| **x402** | HTTP 402 | Any agent/app with crypto wallet |

Both methods support the same services at the same price ($5 USDC or equivalent).

---

## Requirements

**For ACP integration:**
- An ACP-compatible agent/wallet (e.g., OpenClaw with ACP skill installed)
- USDC on Base chain for payments ($5 per service)

**For x402 integration:**
- Any HTTP client
- Wallet for payment signing (Base USDC or Solana SOL)
- Use `@x402/fetch` SDK or manual payment flow

**This skill does NOT:**
- Install any binaries
- Request or store private keys
- Execute any code on your system

---

## Privacy & Data

- **What you send:** Concept description (required), brand name (optional), tagline (optional)
- **What happens:** The service generates logo system (icon, wordmark, lockups), analyzes style, creates social assets
- **Data retention:** Assets stored on Cloudflare R2 for 30 days, then deleted. Contact aklo@aklo.studio for early deletion.
- **Recommendation:** Only submit brand names/concepts you own or have rights to use. Do not submit confidential or trademarked content.

---

## Option 1: ACP Integration (Virtuals Protocol)

### Agent Details

- **Agent Wallet:** `0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e`
- **Protocol:** ACP (Agent Commerce Protocol)
- **Marketplace:** https://app.virtuals.io/acp

### Create Logo Job (with name)

```bash
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e logo \
  --requirements '{"brandName":"Acme","concept":"Modern fintech startup, bold and trustworthy","tagline":"Banking for Everyone"}'
```

### Create Logo Job (AI names the brand)

```bash
# Just provide concept — AI will generate the perfect brand name!
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e logo \
  --requirements '{"concept":"AI-powered fitness coaching app for busy professionals"}'
```

### Poll Job Status

```bash
acp job status <jobId>
```

### Create Social Assets (from Logo Service)

```bash
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e social \
  --requirements '{"brandSystemUrl":"https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/brand-system.json"}'
```

### Create Social Assets (BYOL — Bring Your Own Logo)

```bash
# AI extracts colors from your logo
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e social \
  --requirements '{"logoUrl":"https://example.com/my-logo.png","brandName":"My Brand"}'

# Or specify colors manually
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e social \
  --requirements '{"logoUrl":"https://example.com/my-logo.png","brandName":"My Brand","primaryColor":"#FF5500","secondaryColor":"#333333","renderStyle":"gradient"}'
```

### Create On-Brand GFX (from Logo Service)

```bash
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e gfx \
  --requirements '{"brandSystemUrl":"https://pub-xxx.r2.dev/acme/brand-system.json","prompt":"Announcement graphic: We just hit 10,000 users! Celebratory vibe.","aspectRatio":"1:1"}'
```

### Create On-Brand GFX (BYOL)

```bash
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e gfx \
  --requirements '{"logoUrl":"https://example.com/logo.png","brandName":"Acme","prompt":"Launch graphic for new mobile app","aspectRatio":"16:9"}'
```

---

## Option 2: x402 Integration (Direct API)

### Base URL

```
https://gateway.opengfx.app
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/health` | Health check |
| GET | `/v1/pricing` | Pricing with current SOL rate |
| POST | `/v1/logo` | Generate logo system (x402 payment) |
| POST | `/v1/socials` | Generate social assets (x402 payment) |
| POST | `/v1/gfx` | Generate on-brand marketing graphic (x402 payment) |
| GET | `/v1/jobs/:id` | Check job status |
| GET | `/v1/jobs` | List jobs (filter by wallet) |

### Supported Payment Chains

| Chain | Asset | Network |
|-------|-------|---------|
| Base | USDC | `eip155:8453` |
| Solana | SOL | `solana:mainnet` |

### Payment Wallets

- **Base (USDC):** `0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e`
- **Solana (SOL):** Check `/v1/pricing` for current wallet

### x402 Payment Flow

1. **Request service** → POST `/v1/logo` or `/v1/socials` with JSON body
2. **Receive 402** → Response includes payment options (Base USDC or Solana SOL)
3. **Sign payment** → Use wallet to sign the payment authorization
4. **Retry with payment** → Same request with `X-Payment` header containing signed payment
5. **Receive job ID** → Response includes `jobId` and `pollUrl`
6. **Poll for completion** → GET `/v1/jobs/:jobId` until `status: "completed"`
7. **Get assets** → Response contains CDN URLs for all generated assets

### Example: Logo Request

```bash
# Step 1: Initial request (returns 402)
curl -X POST https://gateway.opengfx.app/v1/logo \
  -H "Content-Type: application/json" \
  -d '{"brand_name":"Acme","concept":"Modern fintech startup"}'

# Step 2: After signing payment, retry with X-Payment header
curl -X POST https://gateway.opengfx.app/v1/logo \
  -H "Content-Type: application/json" \
  -H "X-Payment: <base64-encoded-signed-payment>" \
  -d '{"brand_name":"Acme","concept":"Modern fintech startup"}'

# Step 3: Poll for completion
curl https://gateway.opengfx.app/v1/jobs/<jobId>
```

### Using @x402/fetch SDK

```typescript
import { wrapFetch } from '@x402/fetch';

const x402Fetch = wrapFetch(fetch, wallet);

const response = await x402Fetch('https://gateway.opengfx.app/v1/logo', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    brand_name: 'Acme',
    concept: 'Modern fintech startup'
  })
});

const { jobId, pollUrl } = await response.json();

// Poll for completion
let job;
do {
  await new Promise(r => setTimeout(r, 5000));
  job = await fetch(pollUrl).then(r => r.json());
} while (job.status === 'processing');

console.log(job.logo); // CDN URLs
```

---

## Pricing

| Service | Price | Output |
|---------|-------|--------|
| Logo System | $5 | Icon, wordmark, stacked, horizontal + brand-system.json |
| Social Assets | $5 | Avatar (1K + ACP) + Twitter banner + OG card + Community banner |
| On-Brand GFX | $2 | Single marketing graphic (any aspect ratio) |

---

## Input Options

### Logo Service

| Field | Required | Description |
|-------|----------|-------------|
| `concept` | ✅ | Brand concept, vibe, industry, style direction |
| `brandName` / `brand_name` | ❌ | Brand name (AI generates if not provided) |
| `tagline` | ❌ | Optional tagline/slogan |

### Social Service (Mode 1: From Logo Service)

| Field | Required | Description |
|-------|----------|-------------|
| `brandSystemUrl` / `brand_system_url` | ✅ | URL to brand-system.json from logo service |

### Social Service (Mode 2: BYOL)

| Field | Required | Description |
|-------|----------|-------------|
| `logoUrl` / `logo_url` | ✅ | URL to your existing logo image |
| `brandName` / `brand_name` | ✅ | Brand name |
| `tagline` | ❌ | Optional tagline |
| `primaryColor` / `primary_color` | ❌ | Primary color hex (auto-extracted if not provided) |
| `secondaryColor` / `secondary_color` | ❌ | Secondary color hex |
| `backgroundColor` / `background_color` | ❌ | Background color hex |
| `renderStyle` / `render_style` | ❌ | flat, gradient, glass, chrome, gold, neon, 3d |

### GFX Service (Mode 1: From Logo Service)

| Field | Required | Description |
|-------|----------|-------------|
| `brandSystemUrl` / `brand_system_url` | ✅ | URL to brand-system.json from logo service |
| `prompt` | ✅ | What graphic to generate (be specific about purpose, mood, text) |
| `aspectRatio` / `aspect_ratio` | ❌ | Output ratio: 1:1, 4:5, 16:9, 9:16, etc. (default: 1:1) |

### GFX Service (Mode 2: BYOL)

| Field | Required | Description |
|-------|----------|-------------|
| `logoUrl` / `logo_url` | ✅ | URL to your existing logo image |
| `brandName` / `brand_name` | ✅ | Brand name |
| `prompt` | ✅ | What graphic to generate |
| `aspectRatio` / `aspect_ratio` | ❌ | Output ratio (default: 1:1) |
| `primaryColor` / `primary_color` | ❌ | Primary color hex (auto-extracted if not provided) |
| `secondaryColor` / `secondary_color` | ❌ | Secondary color hex |
| `renderStyle` / `render_style` | ❌ | flat, gradient, glass, chrome, gold, neon, 3d |

### GFX Aspect Ratios

| Ratio | Pixels | Use Case |
|-------|--------|----------|
| `1:1` | 1024×1024 | Instagram, Twitter, LinkedIn posts |
| `4:5` | 1024×1280 | Instagram feed (portrait) |
| `9:16` | 1024×1820 | Stories, Reels, TikTok |
| `16:9` | 1820×1024 | YouTube thumbnails, Twitter cards |
| `3:2` | 1536×1024 | Blog headers |
| `2:3` | 1024×1536 | Pinterest |

---

## Output

### Logo System Response

```json
{
  "jobId": "abc-123",
  "status": "completed",
  "brandName": "Acme",
  "logo": {
    "icon": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/icon.png",
    "wordmark": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/wordmark.png",
    "stacked": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/stacked.png",
    "horizontal": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/horizontal.png",
    "brandSystem": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/brand-system.json"
  }
}
```

### Social Assets Response

```json
{
  "jobId": "def-456",
  "status": "completed",
  "brandName": "Acme",
  "socials": {
    "avatarMaster": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/avatar-master.png",
    "avatarAcp": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/avatar-acp.jpg",
    "twitterBanner": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/twitter-banner.png",
    "ogCard": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/og-card.png",
    "communityBanner": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/community-banner.png"
  }
}
```

### GFX Response

```json
{
  "jobId": "gfx-789",
  "status": "completed",
  "brandName": "Acme",
  "gfx": {
    "url": "https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/acme/gfx/gfx-789.png",
    "width": 1024,
    "height": 1024,
    "aspectRatio": "1:1"
  }
}
```

---

## Vendor Information

- **Service:** OpenGFX
- **Provider:** AKLO Labs
- **Website:** https://opengfx.app
- **GitHub:** https://github.com/aklo360/opengfx-skill
- **Support:** aklo@aklo.studio
- **Agent Wallet:** `0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e`
- **x402 Gateway:** https://gateway.opengfx.app
- **ACP Marketplace:** https://app.virtuals.io/acp
- **ClawHub:** https://clawhub.com/skills/opengfx

---

## Best Practices

- **Be specific about your concept** — include industry, vibe, target audience
- **Include color preferences** if you have them (e.g., "blue and gold tones")
- **Mention style direction** — "minimal", "playful", "corporate", "tech", "organic"
- **Dark vs Light** — AI auto-detects, but you can hint ("dark mode aesthetic" or "bright and friendly")
- **Test first** — Use a low-value test job to verify behavior before production use
- **x402 vs ACP** — Use x402 for direct integration; use ACP if you're already in the Virtuals ecosystem
