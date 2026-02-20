# PostFast API Reference

Base URL: `https://api.postfa.st`
Auth: `pf-api-key` header with workspace API key.

## Endpoints

### GET /social-media/my-social-accounts

List all connected social media accounts.

**Response:**
```json
[
  {
    "id": "6a87b56e-ba73-4696-a415-3d524f1a92f8",
    "platform": "FACEBOOK",
    "platformUsername": "johndoe",
    "displayName": "John's Page"
  }
]
```

Platform values: `TIKTOK`, `INSTAGRAM`, `FACEBOOK`, `X`, `YOUTUBE`, `LINKEDIN`, `THREADS`, `BLUESKY`, `PINTEREST`

### GET /social-media/:id/pinterest-boards

Get Pinterest boards for a connected account.

**Response:**
```json
[{ "boardId": "1234567890123456789", "name": "My Recipes" }]
```

### GET /social-media/:id/youtube-playlists

Get YouTube playlists for a connected account.

**Response:**
```json
[{ "playlistId": "PLrAXtmErZgOe...", "title": "My Tutorials" }]
```

### POST /file/get-signed-upload-urls

Get pre-signed S3 URLs for media upload.

**Request:**
```json
{ "contentType": "image/png", "count": 1 }
```

Supported content types: `image/png`, `image/jpeg`, `image/jpg`, `image/gif`, `image/webp`, `video/mp4`, `video/quicktime`, `application/pdf`, `application/vnd.openxmlformats-officedocument.wordprocessingml.document`, `application/vnd.openxmlformats-officedocument.presentationml.presentation`

**Response:**
```json
[{ "key": "image/a1b2c3d4-e5f6-7890-1234-567890abcdef.png", "signedUrl": "https://s3..." }]
```

Then PUT the raw file to `signedUrl` with matching `Content-Type` header.

### GET /social-posts

List scheduled posts.

**Response:**
```json
{
  "data": [...],
  "totalCount": 25,
  "pageInfo": { "page": 1, "hasNextPage": true, "perPage": 10 }
}
```

### POST /social-posts

Create/schedule one or more posts.

**Request:**
```json
{
  "posts": [
    {
      "content": "Post text with #hashtags",
      "mediaItems": [
        {
          "key": "image/uuid.png",
          "type": "IMAGE",
          "sortOrder": 0
        }
      ],
      "scheduledAt": "2025-06-15T10:00:00.000Z",
      "socialMediaId": "account-uuid"
    }
  ],
  "controls": {
    "tiktokPrivacy": "PUBLIC",
    "instagramPublishType": "REEL"
  }
}
```

**Post fields:**
- `content` (string, required): Post text/caption
- `mediaItems` (array): Media attachments. Each has `key` (from upload), `type` (`IMAGE`/`VIDEO`), `sortOrder` (int)
- `scheduledAt` (string, required): ISO 8601 UTC datetime, must be in the future
- `socialMediaId` (string, required): Target account ID from `/my-social-accounts`

**mediaItems extra fields:**
- `coverTimestamp` (string): TikTok video thumbnail, seconds (e.g., `"3"`)

**controls**: Platform-specific settings. See platform-controls.md for all options.

**Cross-posting**: Add multiple objects to the `posts` array, each with different `socialMediaId`. The `controls` object applies to all posts in the batch.

**Response:**
```json
{ "postIds": ["uuid-1", "uuid-2"] }
```

One ID per entry in the `posts` array.

### DELETE /social-posts/:id

Delete a scheduled post by ID.

**Response:**
```json
{ "deleted": true }
```

## Error Responses

- `400` — Bad request (missing fields, invalid data)
- `401` — Invalid or missing API key
- `403` — Forbidden (insufficient permissions)
- `404` — Resource not found
- `429` — Rate limit exceeded

## Rate Limits

Per API key (workspace):
- 60 requests/minute
- 150 requests/5 minutes
- 300 requests/hour
- 2,000 requests/day

Response headers: `X-RateLimit-Limit-*`, `X-RateLimit-Remaining-*`, `X-RateLimit-Reset-*`, `Retry-After-*`
