# Instagram API Agent Skill — SPEC

## Goal

Implement the Instagram Graph API as a **skill that Claude Code / OpenAI Codex agents can invoke directly**. Agents execute individual scripts and interpret JSON results.

## Compatibility

Follows the [Agent Skills](https://agentskills.io) open standard. Both Claude Code and OpenAI Codex support this standard, so a single skill directory works on both platforms.

The project root itself is the skill directory. Symlink this project into `.claude/skills/instagram/` or `.agents/skills/instagram/` and `SKILL.md` at the root becomes the entrypoint.

| Platform | Installation | Notes |
|----------|-------------|-------|
| Claude Code | `ln -s <project-root> ~/.claude/skills/instagram` | Tool access controlled via `allowed-tools` |
| OpenAI Codex | `ln -s <project-root> ~/.agents/skills/instagram` | Additional config in `agents/openai.yaml` |

---

## Directory Structure

```
instagram-api/
├── SKILL.md                      # Skill entrypoint (agent instructions)
├── SPEC.md                       # This document
├── agents/
│   └── openai.yaml               # Codex additional config
├── scripts/
│   ├── _common.js                # Shared module
│   ├── refresh-token.js
│   ├── get-profile.js
│   ├── get-posts.js
│   ├── get-post.js
│   ├── post-image.js
│   ├── post-video.js
│   ├── get-comments.js
│   ├── post-comment.js
│   └── reply-comment.js
├── .env                          # Instagram credentials
└── package.json
```

---

## Script Conventions

### Common Principles

1. **Every script refreshes the token before execution** (internally calls `refreshToken()`).
2. **stdout outputs JSON only**. Human-readable logs go to stderr.
3. **Exit codes**: success `0`, failure `1`.
4. **Error format on stdout**:
   ```json
   { "error": "error message" }
   ```
5. Arguments are passed as command-line args. Complex inputs (captions, etc.) use named arguments like `--caption "text"`.
6. Assumes the project root as the working directory.
7. **All scripts support the `--env <path>` option**.
   - When specified: loads credentials from the given `.env` file and writes refreshed tokens to the same file.
   - When omitted: uses the project root `.env` (default).
   - Example: `node scripts/get-profile.js --env /home/user/.instagram-env`

### `scripts/_common.js` Exports

| Function / Constant | Description |
|---------------------|-------------|
| `config` | appId, appSecret, accessToken, baseUrl (Instagram Graph API v24.0) |
| `apiGet(endpoint, params)` | GET request. Automatically appends access_token |
| `apiPost(endpoint, body)` | POST request. Automatically appends access_token |
| `refreshToken()` | Refresh token + save to `.env` file |
| `getProfile()` | Fetch profile (id, username, name, account_type, media_count) |
| `getMyPosts(limit)` | Fetch post list (id, caption, media_type, timestamp, permalink) |
| `getPost(mediaId)` | Fetch post detail (includes like_count, comments_count) |
| `postImage(url, caption)` | Post URL image (create container → poll → publish) |
| `postLocalImage(path, caption)` | Post local image (HTTP server + cloudflared tunnel) |
| `postCarousel(urls, caption)` | Post URL carousel (child containers → carousel container → publish) |
| `postLocalCarousel(paths, caption)` | Post local carousel |
| `validateVideoFile(filePath)` | Validate video file (existence, format, size). Returns `{ absolutePath, mimeType }` |
| `postVideo(url, caption, options?)` | Post URL video as Reels. options: `coverUrl`, `thumbOffset`, `shareToFeed` |
| `postLocalVideo(path, caption, options?)` | Post local video as Reels (HTTP server + cloudflared tunnel). Also serves local cover image |
| `postVideoCarousel(urls, caption)` | Post URL video carousel |
| `postLocalVideoCarousel(paths, caption)` | Post local video carousel |
| `VIDEO_CONTAINER_TIMEOUT` | 10 minute timeout for video container processing |
| `getComments(mediaId)` | Fetch comments + replies |
| `postComment(mediaId, text)` | Create comment |
| `replyToComment(commentId, text)` | Create reply |
| `startTunnel(port)` | Start cloudflared quick tunnel. Returns public URL |
| `stopTunnel()` | Kill tunnel process |
| `run(fn)` | Script entrypoint wrapper: parse args → load env → refresh token → execute fn → JSON output / error handling |
| `parseArgs()` | Command-line args parser. Returns `{ named, positional }` |
| `loadEnv(envPath?)` | Load specified or default `.env`. Also sets the file path for `refreshToken()` to write to |

### Script Specifications

#### `scripts/refresh-token.js`

Refreshes the token and returns new expiration info.

```
node scripts/refresh-token.js
```

```json
{ "access_token": "IGQ...", "expires_in": 5184000, "expires_in_days": 60 }
```

#### `scripts/get-profile.js`

Fetches the user's profile.

```
node scripts/get-profile.js
```

```json
{
  "id": "12345",
  "username": "myaccount",
  "name": "My Name",
  "account_type": "BUSINESS",
  "media_count": 42,
  "profile_picture_url": "https://..."
}
```

#### `scripts/get-posts.js`

Fetches the user's post list.

```
node scripts/get-posts.js [--limit 10]
```

```json
{
  "data": [
    {
      "id": "17890...",
      "caption": "Post caption",
      "media_type": "IMAGE",
      "media_url": "https://...",
      "timestamp": "2026-02-16T00:00:00+0000",
      "permalink": "https://www.instagram.com/p/..."
    }
  ]
}
```

#### `scripts/get-post.js`

Fetches detail for a specific post.

```
node scripts/get-post.js <media-id>
```

```json
{
  "id": "17890...",
  "caption": "Post caption",
  "media_type": "IMAGE",
  "media_url": "https://...",
  "timestamp": "2026-02-16T00:00:00+0000",
  "permalink": "https://www.instagram.com/p/...",
  "like_count": 10,
  "comments_count": 3
}
```

#### `scripts/post-image.js`

Posts images. Automatically switches to carousel when given 2+ files.
Supports both URLs and local file paths (local files use cloudflared tunnel).

```
# Single image (URL)
node scripts/post-image.js --caption "Caption" https://example.com/photo.jpg

# Single image (local)
node scripts/post-image.js --caption "Caption" ./photos/image.png

# Carousel (multiple local)
node scripts/post-image.js --caption "Caption" ./img1.png ./img2.png ./img3.jpg
```

```json
{ "id": "18158...", "type": "IMAGE" }
```

```json
{ "id": "18068...", "type": "CAROUSEL" }
```

**Detection logic**:
- Starts with `http://` or `https://` → URL. Otherwise → local file path.
- Image count: 1 → single post, 2+ → carousel.
- Mixing URLs and local files is not supported.

#### `scripts/post-video.js`

Posts videos as Reels. Automatically switches to carousel when given 2+ files.
Supports both URLs and local file paths (local files use cloudflared tunnel).

```
# Single video (URL)
node scripts/post-video.js --caption "Caption" https://example.com/video.mp4

# Single video (local)
node scripts/post-video.js --caption "Caption" ./videos/clip.mp4

# With options (single video only)
node scripts/post-video.js --caption "Caption" --cover https://example.com/cover.jpg --thumb-offset 5000 --share-to-feed true https://example.com/video.mp4

# Carousel (multiple URLs)
node scripts/post-video.js --caption "Caption" https://example.com/a.mp4 https://example.com/b.mp4
```

```json
{ "id": "18158...", "type": "REELS" }
```

```json
{ "id": "18068...", "type": "CAROUSEL" }
```

**Detection logic**:
- Starts with `http://` or `https://` → URL. Otherwise → local file path.
- Video count: 1 → Reels post, 2+ → carousel.
- Mixing URLs and local files is not supported.

**Options** (single video only):
- `--cover <url-or-path>`: Cover image URL or local file path.
- `--thumb-offset <ms>`: Thumbnail offset in milliseconds.
- `--share-to-feed <true|false>`: Whether to share the Reel to the main feed.

**Constraints**:
- Supported formats: mp4, mov.
- Maximum file size: 100MB per video.
- Video processing timeout: 10 minutes.

#### `scripts/get-comments.js`

Fetches comments and replies for a specific post.

```
node scripts/get-comments.js <media-id>
```

```json
{
  "data": [
    {
      "id": "17858...",
      "text": "Comment text",
      "username": "commenter",
      "timestamp": "2026-02-16T00:00:00+0000",
      "replies": {
        "data": [
          { "id": "17860...", "text": "Reply", "username": "replier", "timestamp": "..." }
        ]
      }
    }
  ]
}
```

#### `scripts/post-comment.js`

Creates a comment on a post.

```
node scripts/post-comment.js <media-id> --text "Comment text"
```

```json
{ "id": "17858..." }
```

#### `scripts/reply-comment.js`

Creates a reply to a comment.

```
node scripts/reply-comment.js <comment-id> --text "Reply text"
```

```json
{ "id": "17860..." }
```

---

## SKILL.md Specification

`SKILL.md` at the project root is the entrypoint that tells the agent what this skill does and how to use it.

### Frontmatter

```yaml
---
name: instagram
description: >
  Instagram 계정을 관리한다. 프로필 조회, 게시물 목록 확인, 이미지/캐러셀 게시,
  댓글 조회 및 작성이 가능하다. 사용자가 Instagram 관련 작업을 요청할 때 사용한다.
allowed-tools: Bash(node scripts/*)
---
```

- `name`: Skill name. Invocable via `/instagram`.
- `description`: Specific enough for the agent to auto-select when relevant.
- `allowed-tools`: Only allows running Node scripts under `scripts/`.

### Body Content Guide

The SKILL.md body should include:

1. **개요**: 이 스킬이 무엇을 할 수 있는지 한 문단 요약.
2. **사전 조건**: `.env` 파일에 인스타그램 자격 증명이 설정되어 있어야 함. 로컬 이미지 게시 시 `cloudflared` 필요.
3. **사용 가능한 명령**: 각 스크립트의 용도, 호출 형식, 출력 예시.
4. **워크플로우 지침**:
   - 사용자가 `.env` 파일 경로를 명시하면 모든 명령에 `--env <path>`를 붙일 것.
   - 모든 명령은 자동으로 토큰을 갱신하므로 별도 갱신 불필요.
   - 이미지 게시 시 사용자에게 캡션을 확인받을 것.
   - 게시 후 결과 ID와 함께 성공 여부를 보고할 것.
   - 댓글 작성 시 내용을 사용자에게 확인받을 것.
5. **에러 처리**: JSON `error` 필드가 있으면 사용자에게 원인을 설명할 것.

---

## Codex Additional Config

### `agents/openai.yaml`

```yaml
interface:
  display_name: "Instagram"
  short_description: "Instagram 계정 관리 (게시, 댓글, 프로필)"
  brand_color: "#E4405F"

policy:
  allow_implicit_invocation: true
```

---

## Environment Requirements

| Item | Required | Description |
|------|----------|-------------|
| Node.js | Yes | v18+ |
| `.env` file | Yes | `INSTAGRAM_APP_ID`, `INSTAGRAM_APP_SECRET`, `INSTAGRAM_ACCESS_TOKEN` |
| `dotenv` | Yes | Included in `package.json` |
| `cloudflared` | For local image posting | `brew install cloudflared` / `apt-get install cloudflared` |

---

## Implementation Order

### Phase 1: Scripts

1. Create `scripts/` directory
2. Write `scripts/_common.js`
3. Write each script (in the order specified above)
4. Test each script individually

### Phase 2: Skill Definition

5. Write `SKILL.md` at the project root
6. Write `agents/openai.yaml`

### Phase 3: Verification

7. Test `/instagram` invocation in Claude Code
8. Test auto-invocation via natural language ("내 인스타 프로필 보여줘")
9. Test error cases (invalid media ID, nonexistent file, etc.)
