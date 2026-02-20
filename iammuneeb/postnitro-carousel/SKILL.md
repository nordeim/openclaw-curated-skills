---
name: postnitro-carousel
description: >
  Generate professional social media carousel posts using the PostNitro.ai Embed API.
  Supports AI-powered content generation and manual content import for LinkedIn, Instagram,
  TikTok, and X (Twitter) carousels. Use this skill whenever the user wants to create a
  carousel, social media post, slide deck for social media, multi-slide content, or
  mentions PostNitro. Also trigger when the user asks to turn text, articles, blog posts,
  or topics into carousel posts, or wants to automate social media content creation.
  Outputs PNG images or PDF files. Requires a PostNitro API key.
metadata:
  openclaw:
    emoji: "🎠"
    requires:
      envs:
        - POSTNITRO_API_KEY
        - POSTNITRO_TEMPLATE_ID
        - POSTNITRO_BRAND_ID
        - POSTNITRO_PRESET_ID
---

# PostNitro Carousel Generator

Create stunning social media carousel posts via the PostNitro.ai Embed API. Supports two workflows: **AI-powered generation** (provide a topic and let AI create content) and **content import** (provide your own slide content with full control).

## Prerequisites

The user must set the following environment variables:

1. `POSTNITRO_API_KEY` — Obtained from PostNitro.ai account settings under "Embed".
2. `POSTNITRO_TEMPLATE_ID` — The ID of a carousel template from their PostNitro account.
3. `POSTNITRO_BRAND_ID` — The ID of a brand profile from their PostNitro account.
4. `POSTNITRO_PRESET_ID` — (Required for AI generation) An AI preset ID configured in their PostNitro account.

If the user doesn't have these, direct them to https://postnitro.ai to sign up (free plan available with 5 credits/month).

## API Reference

**Base URL**: `https://embed-api.postnitro.ai`

**Authentication**: All requests require the header `embed-api-key: $POSTNITRO_API_KEY`.

**Content-Type**: Always `application/json`.

### Workflow Overview

All carousel creation is asynchronous:

1. **Initiate** — Call `/post/initiate/generate` or `/post/initiate/import` → receive an `embedPostId`
2. **Poll Status** — Call `/post/request-status` with the `embedPostId` until status is complete
3. **Get Output** — Call `/post/output` with the `embedPostId` to download the result

### Endpoint 1: AI-Powered Generation

`POST /post/initiate/generate`

Use when the user provides a topic, article URL, or text and wants AI to create carousel content.

```json
{
  "postType": "CAROUSEL",
  "templateId": "<template-id>",
  "brandId": "<brand-id>",
  "presetId": "<ai-preset-id>",
  "responseType": "PNG",
  "aiGeneration": {
    "type": "<generation-type>",
    "context": "<topic, text, or article URL>",
    "instructions": "<optional style/tone instructions>"
  }
}
```

**`aiGeneration.type` values:**
- `"text"` — Generate from user-provided text
- `"article"` — Generate from an article URL or long-form content
- `"topic"` — Generate from a topic description

**`responseType` values:**
- `"PNG"` — Individual images per slide (best for social media posting)
- `"PDF"` — Single PDF document with all slides

**Credit cost**: 2 credits per slide (AI generation).

### Endpoint 2: Content Import

`POST /post/initiate/import`

Use when the user provides their own slide content (headings, descriptions, images).

```json
{
  "postType": "CAROUSEL",
  "templateId": "<template-id>",
  "brandId": "<brand-id>",
  "requestorId": "<optional-tracking-id>",
  "responseType": "PNG",
  "slides": [
    {
      "type": "starting_slide",
      "heading": "Title Text",
      "sub_heading": "Subtitle Text",
      "description": "Description text",
      "cta_button": "Call to Action",
      "image": "https://example.com/image.jpg",
      "background_image": "https://example.com/bg.jpg"
    },
    {
      "type": "body_slide",
      "heading": "Slide Heading",
      "description": "Slide body text",
      "image": "https://example.com/image.jpg"
    },
    {
      "type": "ending_slide",
      "heading": "Final Slide Title",
      "sub_heading": "Closing Subtitle",
      "description": "Closing message",
      "cta_button": "Take Action",
      "image": "https://example.com/logo.png",
      "background_image": "https://example.com/bg.jpg"
    }
  ]
}
```

**Slide types:**
- `"starting_slide"` — First slide (title/intro). Supports: `heading`, `sub_heading`, `description`, `cta_button`, `image`, `background_image`.
- `"body_slide"` — Middle content slides. Supports: `heading`, `description`, `image`.
- `"ending_slide"` — Last slide (CTA/closing). Supports: `heading`, `sub_heading`, `description`, `cta_button`, `image`, `background_image`.

All slide fields are optional. Use `image` for foreground images and `background_image` for slide backgrounds. Image values must be publicly accessible URLs.

**Credit cost**: 1 credit per slide (user-provided content).

### Endpoint 3: Check Request Status

`POST /post/request-status`

```json
{
  "embedPostId": "<post-id-from-initiate-response>"
}
```

Poll this endpoint every 3–5 seconds until the response indicates the post is ready.

### Endpoint 4: Get Output

`POST /post/output`

```json
{
  "embedPostId": "<post-id-from-initiate-response>"
}
```

Returns the generated carousel. For PNG `responseType`, returns an array of image URLs/blobs (one per slide). For PDF, returns a single document.

## Step-by-Step Usage

### Creating an AI-Generated Carousel

1. Confirm the user has set `POSTNITRO_API_KEY`, `POSTNITRO_TEMPLATE_ID`, `POSTNITRO_BRAND_ID`, and `POSTNITRO_PRESET_ID`.
2. Ask the user for their topic/content and any style preferences.
3. Send the generate request:
   ```bash
   curl -X POST 'https://embed-api.postnitro.ai/post/initiate/generate' \
     -H 'Content-Type: application/json' \
     -H "embed-api-key: $POSTNITRO_API_KEY" \
     -d '{
       "postType": "CAROUSEL",
       "templateId": "'"$POSTNITRO_TEMPLATE_ID"'",
       "brandId": "'"$POSTNITRO_BRAND_ID"'",
       "presetId": "'"$POSTNITRO_PRESET_ID"'",
       "responseType": "PNG",
       "aiGeneration": {
         "type": "topic",
         "context": "User topic here",
         "instructions": "User style instructions here"
       }
     }'
   ```
4. Extract the `embedPostId` from the response.
5. Poll status until complete:
   ```bash
   curl -X POST 'https://embed-api.postnitro.ai/post/request-status' \
     -H 'Content-Type: application/json' \
     -H "embed-api-key: $POSTNITRO_API_KEY" \
     -d '{"embedPostId": "'"$EMBED_POST_ID"'"}'
   ```
6. Retrieve the output:
   ```bash
   curl -X POST 'https://embed-api.postnitro.ai/post/output' \
     -H 'Content-Type: application/json' \
     -H "embed-api-key: $POSTNITRO_API_KEY" \
     -d '{"embedPostId": "'"$EMBED_POST_ID"'"}'
   ```

### Creating a Carousel from User Content

1. Confirm the user has set `POSTNITRO_API_KEY`, `POSTNITRO_TEMPLATE_ID`, and `POSTNITRO_BRAND_ID`.
2. Gather slide content from the user (or generate it based on context).
3. Structure slides using the `starting_slide` → `body_slide`(s) → `ending_slide` pattern.
4. Send the import request and follow the same poll → output flow as above.

## Content Strategy Tips

When helping users craft carousel content:

- **LinkedIn**: Professional tone, actionable insights, 6–10 slides, end with a clear CTA.
- **Instagram**: Visual-first, concise text, 5–8 slides, storytelling arc.
- **TikTok**: Trendy, punchy, 4–7 slides, hook on slide 1.
- **X (Twitter)**: Data-driven, 3–6 slides, provocative opening.

## Error Handling

- If the API returns an authentication error, verify `POSTNITRO_API_KEY` is correct and the account is active.
- If credits are exhausted, inform the user. Free plan: 5 credits/month. Paid plan: 250+ credits/month.
- If the status poll indicates failure, retry the initiation once before reporting the error.
- All endpoints are rate-limited per API key — space requests appropriately.

## Pricing Quick Reference

| Plan    | Price      | Credits/Month | Notes                          |
|---------|------------|---------------|--------------------------------|
| Free    | $0/month   | 5             | Default when API key generated |
| Monthly | $10/month  | 250+          | Scalable multiplier (1–100)    |

- 1 credit = 1 slide (user content import)
- AI generation = 2 credits per slide

## Links

- Documentation: https://postnitro.ai/docs/embed/api
- Get API Key: https://postnitro.ai/app/embed
- Postman Collection: https://www.postman.com/postnitro/postnitro-embed-apis/overview
- Support: support@postnitro.ai
