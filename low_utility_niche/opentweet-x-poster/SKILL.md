---
name: x-poster
description: Post to X (Twitter) using the OpenTweet API. Create tweets, schedule posts, publish threads, and manage your X content autonomously.
version: 1.0.0
homepage: https://opentweet.io/features/openclaw-twitter-posting
user-invocable: true
metadata: {"openclaw":{"requires":{"env":["OPENTWEET_API_KEY"]},"primaryEnv":"OPENTWEET_API_KEY"}}
---

# OpenTweet X Poster

You can post to X (Twitter) using the OpenTweet REST API. All requests go to `https://opentweet.io` with the user's API key.

## Authentication

Every request needs this header:
```
Authorization: Bearer $OPENTWEET_API_KEY
Content-Type: application/json
```

## Before You Start

ALWAYS verify the connection first:
```
GET https://opentweet.io/api/v1/me
```
This returns subscription status, daily post limits, and post counts. Check `subscription.has_access` is true and `limits.remaining_posts_today` > 0 before scheduling or publishing.

## Available Actions

### Verify connection and check limits
```
GET https://opentweet.io/api/v1/me
```
Returns: `authenticated`, `subscription` (has_access, status, is_trialing), `limits` (can_post, remaining_posts_today, daily_limit), `stats` (total_posts, scheduled_posts, posted_posts, draft_posts).

### Create a tweet
```
POST https://opentweet.io/api/v1/posts
Body: { "text": "Your tweet text" }
```
Optionally add `"scheduled_date": "2026-03-01T10:00:00Z"` to schedule it (requires active subscription, date must be in the future).

### Create a thread
```
POST https://opentweet.io/api/v1/posts
Body: {
  "text": "First tweet of the thread",
  "is_thread": true,
  "thread_tweets": ["Second tweet", "Third tweet"]
}
```

### Bulk create (up to 50 posts)
```
POST https://opentweet.io/api/v1/posts
Body: {
  "posts": [
    { "text": "Tweet 1", "scheduled_date": "2026-03-01T10:00:00Z" },
    { "text": "Tweet 2", "scheduled_date": "2026-03-01T14:00:00Z" }
  ]
}
```

### Schedule a post
```
POST https://opentweet.io/api/v1/posts/{id}/schedule
Body: { "scheduled_date": "2026-03-01T10:00:00Z" }
```
The date must be in the future. Use ISO 8601 format.

### Publish immediately
```
POST https://opentweet.io/api/v1/posts/{id}/publish
```
No body needed. Posts to X right now.

### List posts
```
GET https://opentweet.io/api/v1/posts?status=scheduled&page=1&limit=20
```
Status options: `scheduled`, `posted`, `draft`, `failed`

### Get a post
```
GET https://opentweet.io/api/v1/posts/{id}
```

### Update a post
```
PUT https://opentweet.io/api/v1/posts/{id}
Body: { "text": "Updated text" }
```
Cannot update already-published posts.

### Delete a post
```
DELETE https://opentweet.io/api/v1/posts/{id}
```

## Common Workflows

**First: verify your connection works:**
1. `GET /api/v1/me` — check `authenticated` is true, `subscription.has_access` is true

**Post a tweet right now:**
1. `GET /api/v1/me` — check `limits.can_post` is true
2. Create: `POST /api/v1/posts` with text
3. Publish: `POST /api/v1/posts/{id}/publish`

**Schedule a tweet:**
1. `GET /api/v1/me` — check `limits.remaining_posts_today` > 0
2. Create with date: `POST /api/v1/posts` with text and scheduled_date (done in one step)

**Schedule a week of content:**
1. `GET /api/v1/me` — check remaining limit
2. Bulk create: `POST /api/v1/posts` with `"posts": [...]` array, each with a scheduled_date

## Important Rules
- ALWAYS call GET /api/v1/me before scheduling or publishing to check limits
- Tweet max length: 280 characters (per tweet in a thread)
- Bulk limit: 50 posts per request
- Rate limit: 60 requests/minute, 1,000/day
- Dates must be ISO 8601 and in the future — past dates are rejected
- Active subscription required to schedule or publish (creating drafts is free)
- Including scheduled_date in POST /api/v1/posts requires a subscription
- 403 = no subscription, 429 = rate limit or daily post limit hit
- Check response status codes: 201=created, 200=success, 4xx=client error, 5xx=server error

## Full API docs
For complete documentation: https://opentweet.io/api/v1/docs
