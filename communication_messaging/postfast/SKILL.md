---
name: postfast
description: Schedule and manage social media posts across TikTok, Instagram, Facebook, X (Twitter), YouTube, LinkedIn, Threads, Bluesky, and Pinterest using the PostFast API. Use when the user wants to schedule social media posts, manage social media content, upload media for social posting, list connected social accounts, check scheduled posts, delete scheduled posts, cross-post content to multiple platforms, or automate their social media workflow. PostFast is a SaaS tool — no self-hosting required.
homepage: https://postfa.st
metadata: {"openclaw":{"emoji":"⚡","primaryEnv":"POSTFAST_API_KEY","requires":{"env":["POSTFAST_API_KEY"]}}}
---

# PostFast

Schedule social media posts across 9 platforms from one API. SaaS — no self-hosting needed.

## Setup

1. Sign up at https://app.postfa.st/register
2. Go to Workspace Settings → generate an API key
3. Set the environment variable:
   ```bash
   export POSTFAST_API_KEY="your-api-key"
   ```

Base URL: `https://api.postfa.st`
Auth header: `pf-api-key: $POSTFAST_API_KEY`

## Core Workflow

### 1. List connected accounts

```bash
curl -s -H "pf-api-key: $POSTFAST_API_KEY" https://api.postfa.st/social-media/my-social-accounts
```

Returns array of `{ id, platform, platformUsername, displayName }`. Save the `id` — it's the `socialMediaId` for posting.

### 2. Schedule a text post (no media)

```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "content": "Your post text here",
      "mediaItems": [],
      "scheduledAt": "2025-06-15T10:00:00.000Z",
      "socialMediaId": "ACCOUNT_ID_HERE"
    }],
    "controls": {}
  }'
```

### 3. Schedule a post with media (3-step flow)

**Step A** — Get signed upload URLs:
```bash
curl -X POST https://api.postfa.st/file/get-signed-upload-urls \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{ "contentType": "image/png", "count": 1 }'
```
Returns `[{ "key": "image/uuid.png", "signedUrl": "https://..." }]`.

**Step B** — Upload file to S3:
```bash
curl -X PUT "SIGNED_URL_HERE" \
  -H "Content-Type: image/png" \
  --data-binary @/path/to/file.png
```

**Step C** — Create post with media key:
```bash
curl -X POST https://api.postfa.st/social-posts \
  -H "pf-api-key: $POSTFAST_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "posts": [{
      "content": "Post with image!",
      "mediaItems": [{ "key": "image/uuid.png", "type": "IMAGE", "sortOrder": 0 }],
      "scheduledAt": "2025-06-15T10:00:00.000Z",
      "socialMediaId": "ACCOUNT_ID_HERE"
    }],
    "controls": {}
  }'
```

For video: use `contentType: "video/mp4"`, `type: "VIDEO"`, key prefix `video/`.

### 4. List scheduled posts

```bash
curl -s -H "pf-api-key: $POSTFAST_API_KEY" https://api.postfa.st/social-posts
```

### 5. Delete a scheduled post

```bash
curl -X DELETE -H "pf-api-key: $POSTFAST_API_KEY" https://api.postfa.st/social-posts/POST_ID
```

### 6. Cross-post to multiple platforms

Include multiple entries in the `posts` array, each with a different `socialMediaId`. They share the same `controls` and `mediaItems` keys.

## Platform-Specific Controls

Pass these in the `controls` object. See [references/platform-controls.md](references/platform-controls.md) for full details.

| Platform | Key Controls |
|---|---|
| **TikTok** | `tiktokPrivacy`, `tiktokAllowComments`, `tiktokAllowDuet`, `tiktokAllowStitch`, `tiktokIsDraft`, `tiktokBrandContent`, `tiktokAutoAddMusic` |
| **Instagram** | `instagramPublishType` (TIMELINE/STORY/REEL), `instagramPostToGrid`, `instagramCollaborators` |
| **Facebook** | `facebookContentType` (POST/REEL/STORY) |
| **YouTube** | `youtubeIsShort`, `youtubeTitle`, `youtubePrivacy`, `youtubePlaylistId`, `youtubeTags`, `youtubeMadeForKids` |
| **LinkedIn** | `linkedinAttachmentKey`, `linkedinAttachmentTitle` (for document posts) |
| **X (Twitter)** | `xQuoteTweetUrl` (for quote tweets) |
| **Pinterest** | `pinterestBoardId` (required), `pinterestLink` |
| **Bluesky** | No platform-specific controls — text + images only |
| **Threads** | No platform-specific controls — text + images/video |

## Helper Endpoints

- **Pinterest boards**: `GET /social-media/{id}/pinterest-boards` → returns `[{ boardId, name }]`
- **YouTube playlists**: `GET /social-media/{id}/youtube-playlists` → returns `[{ playlistId, title }]`

## Rate Limits

- 60/min, 150/5min, 300/hour, 2000/day per API key
- Check `X-RateLimit-Remaining-*` headers
- 429 = rate limited, check `Retry-After-*` header

## Media Specs Quick Reference

| Platform | Images | Video | Carousel |
|---|---|---|---|
| TikTok | Carousels only | ≤250MB, MP4/MOV, 3s-10min | 2-35 images |
| Instagram | JPEG/PNG | ≤1GB, 3-90s (Reels) | Up to 10 |
| Facebook | ≤30MB, JPG/PNG | 1 per post | Up to 10 images |
| YouTube | — | Shorts ≤3min, H.264 | — |
| LinkedIn | Up to 9 | ≤10min | Up to 9, or documents (PDF/PPTX/DOCX) |
| X (Twitter) | Up to 4 | — | — |
| Pinterest | 2:3 ratio ideal | Supported | 2-5 images |
| Bluesky | Up to 4 | Not supported | — |
| Threads | Supported | Supported | Up to 10 |

## Tips for the Agent

- Always call `my-social-accounts` first to get valid `socialMediaId` values.
- For media posts, complete the full 3-step upload flow (signed URL → S3 PUT → create post).
- `scheduledAt` must be ISO 8601 UTC and in the future.
- Pinterest always requires `pinterestBoardId` — fetch boards first.
- LinkedIn documents use `linkedinAttachmentKey` instead of `mediaItems`.
- For carousels, include multiple items in `mediaItems` with sequential `sortOrder`.
- TikTok video thumbnails: set `coverTimestamp` (seconds) in `mediaItems`.
