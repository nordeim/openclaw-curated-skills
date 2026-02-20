# OpenGFX

AI-powered brand design system. Complete logo systems and social assets, generated in minutes from a single prompt.

![OpenGFX Banner](https://pub-156972f0e0f44d7594f4593dbbeaddcb.r2.dev/opengfx/og-image.jpg)

## Features

- **Logo System** — Icon, wordmark, stacked & horizontal lockups
- **Style Guide** — Colors, typography, render style (auto-detected)
- **Social Assets** — Avatar (1K + ACP), Twitter banner, OG card, community banner
- **On-Brand GFX** — Marketing graphics for announcements, launches, features, and daily content
- **Dark/Light Mode** — Auto-detected based on brand concept
- **AI Brand Naming** — Brand name is optional! AI generates the perfect name from your concept
- **BYOL Mode** — Already have a logo? Bring your own and generate social assets or GFX
- **Multi-Chain Payments** — Pay with USDC on Base or SOL on Solana

## Pricing

| Service | Price | Output |
|---------|-------|--------|
| Logo System | $5 USDC | Icon, wordmark, stacked, horizontal + style guide |
| Social Assets | $5 USDC | Avatar (1K + 400px) + 3 banner formats |
| On-Brand GFX | $2 USDC | Single marketing graphic (any aspect ratio) |

## Two Integration Options

### Option 1: ACP (Virtuals Protocol)

For OpenClaw agents with the ACP skill installed.

```bash
# Install skill
clawhub install opengfx

# Create logo job
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e logo \
  --requirements '{"brandName":"Acme","concept":"Modern fintech startup"}'

# AI generates brand name (optional!)
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e logo \
  --requirements '{"concept":"AI fitness coaching for busy professionals"}'

# Poll for completion
acp job status <jobId>
```

### Option 2: x402 (Direct API)

Pay-per-request via HTTP 402. Works with any agent or app.

**Base URL:** `https://gateway.opengfx.app`

```bash
# Request (returns 402 with payment options)
curl -X POST https://gateway.opengfx.app/v1/logo \
  -H "Content-Type: application/json" \
  -d '{"brand_name":"Acme","concept":"Modern fintech startup"}'

# After signing payment, retry with X-Payment header
curl -X POST https://gateway.opengfx.app/v1/logo \
  -H "Content-Type: application/json" \
  -H "X-Payment: <base64-signed-payment>" \
  -d '{"brand_name":"Acme","concept":"Modern fintech startup"}'

# Poll for completion
curl https://gateway.opengfx.app/v1/jobs/<jobId>
```

#### Supported Payment Chains

| Chain | Asset | Network ID |
|-------|-------|------------|
| Base | USDC | `eip155:8453` |
| Solana | SOL | `solana:mainnet` |

#### x402 Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API documentation |
| GET | `/v1/pricing` | Pricing with current SOL rate |
| POST | `/v1/logo` | Generate logo system (x402) |
| POST | `/v1/socials` | Generate social assets (x402) |
| POST | `/v1/gfx` | Generate on-brand graphic (x402) |
| GET | `/v1/jobs/:id` | Check job status |

#### Using @x402/fetch SDK

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

const { jobId } = await response.json();
// Poll /v1/jobs/:jobId for completion
```

## Social Service Modes

### From Logo Service

```bash
# ACP
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e social \
  --requirements '{"brandSystemUrl":"https://.../brand-system.json"}'

# x402
curl -X POST https://gateway.opengfx.app/v1/socials \
  -H "Content-Type: application/json" \
  -d '{"brand_system_url":"https://.../brand-system.json"}'
```

### BYOL (Bring Your Own Logo)

```bash
# AI extracts colors
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e social \
  --requirements '{"logoUrl":"https://example.com/logo.png","brandName":"Acme"}'

# With custom colors
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e social \
  --requirements '{"logoUrl":"https://example.com/logo.png","brandName":"Acme","primaryColor":"#FF5500","renderStyle":"gradient"}'
```

## GFX Service ($2/graphic)

Generate on-brand marketing graphics for announcements, launches, features, and daily content.

### From Logo Service

```bash
# ACP
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e gfx \
  --requirements '{"brandSystemUrl":"https://.../brand-system.json","prompt":"Announcement: We hit 10K users!","aspectRatio":"1:1"}'

# x402
curl -X POST https://gateway.opengfx.app/v1/gfx \
  -H "Content-Type: application/json" \
  -d '{"brand_system_url":"https://.../brand-system.json","prompt":"Launch graphic for new feature","aspect_ratio":"16:9"}'
```

### BYOL

```bash
acp job create 0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e gfx \
  --requirements '{"logoUrl":"https://example.com/logo.png","brandName":"Acme","prompt":"Hiring announcement","aspectRatio":"1:1"}'
```

### Supported Aspect Ratios

| Ratio | Use Case |
|-------|----------|
| `1:1` | Instagram, Twitter, LinkedIn |
| `4:5` | Instagram portrait |
| `9:16` | Stories, Reels, TikTok |
| `16:9` | YouTube, Twitter cards |
| `3:2` | Blog headers |

## Output

### Logo System
```
icon.png           # 1024x1024
wordmark.png       # AI typography
stacked.png        # 1024x1024 square lockup
horizontal.png     # Wide lockup
brand-system.json  # Colors, typography, render style
```

### Social Assets
```
avatar-master.png     # 1024x1024
avatar-acp.jpg        # 400x400 (<50KB)
twitter-banner.png    # 3000x1000 (3:1)
og-card.png           # 1200x628 (1.91:1)
community-banner.png  # 1200x480 (2.5:1)
```

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

## Agent Details

- **Agent Wallet:** `0x7cf4CE250a47Baf1ab87820f692BB87B974a6F4e`
- **x402 Gateway:** https://gateway.opengfx.app
- **ACP Protocol:** Virtuals Protocol

## Links

- **Website:** https://opengfx.app
- **ClawHub:** https://clawhub.com/skills/opengfx
- **GitHub:** https://github.com/aklo360/opengfx-skill
- **ACP Marketplace:** https://app.virtuals.io/acp

## Built by

[AKLO Labs](https://aklo.studio)
