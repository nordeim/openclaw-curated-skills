# Agent2RSS API 调用示例

本文档提供完整的 API 调用示例，包括请求格式和响应示例。

## 配置管理

### 初始化配置

首次使用时，Skill 会自动创建配置文件：

```bash
# 配置文件位置
.claude/skills/agent2rss-client/config.json

# 配置文件结构
{
  "serverUrl": "http://agent2rss.yaotutu.top:8765",  # 服务器地址
  "currentChannelId": "default",                      # 当前使用的频道 ID
  "channels": [
    {
      "id": "default",
      "name": "默认频道",
      "token": "ch_xxx...",
      "postsUrl": "http://agent2rss.yaotutu.top:8765/api/channels/default/posts",
      "rssUrl": "http://agent2rss.yaotutu.top:8765/channels/default/rss.xml"
    }
  ]
}
```

### 验证配置

```bash
# 测试服务器连接
curl http://agent2rss.yaotutu.top:8765/health

# 获取频道列表
curl http://agent2rss.yaotutu.top:8765/api/channels
```

**重要**：所有 API 调用都必须使用 `config.json` 中的 `serverUrl`，不要硬编码 localhost。

## 基础信息

- **默认服务器**: `http://agent2rss.yaotutu.top:8765`（从 config.json 读取）
- **API 基础路径**: `/api`
- **内容类型**: `application/json`
- **认证方式**: `Authorization: Bearer <token>`

## 1. 创建频道

### 请求

```bash
curl -X POST http://agent2rss.yaotutu.top:8765/api/channels \
  -H "Content-Type: application/json" \
  -d '{
    "name": "技术博客",
    "description": "分享技术文章和教程"
  }'
```

### 响应示例

```json
{
  "success": true,
  "channel": {
    "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "name": "技术博客",
    "description": "分享技术文章和教程",
    "token": "ch_4fd9cdce724ffb8d6ec69187b5438ae2",
    "theme": "spring",
    "language": "zh-CN",
    "maxPosts": 100,
    "createdAt": "2026-02-05T10:30:00.000Z"
  },
  "rssUrl": "http://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml"
}
```

### 字段说明

- `id`: 频道唯一标识符（UUID，服务端自动生成）
- `name`: 频道名称
- `description`: 频道描述
- `token`: 频道 Token，用于鉴权（格式：`ch_` + 32位随机字符串）
- `theme`: 主题名称（默认：spring）
- `language`: 语言代码（默认：zh-CN）
- `maxPosts`: 最大文章数（默认：100）
- `rssUrl`: RSS Feed 订阅地址
- `createdAt`: 创建时间（ISO 8601 格式）

## 2. 推送内容到频道（JSON 方式）

### 请求（最简参数 - 仅内容）

```bash
curl -X POST http://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -d '{
    "content": "# 我的标题\n\n这是文章内容"
  }'
```

### 请求（完整参数）

```bash
curl -X POST http://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -d '{
    "content": "# Agent2RSS 使用指南\n\n## 简介\n\nAgent2RSS 是一个将任意内容转换为 RSS Feed 的服务...",
    "title": "如何使用 Agent2RSS",
    "link": "https://example.com/article",
    "contentType": "markdown",
    "author": "Claude",
    "tags": ["教程", "RSS", "技术"],
    "idempotencyKey": "article-2024-01-01-001"
  }'
```

### 响应示例（新创建）

```json
{
  "success": true,
  "message": "Post created successfully in channel \"8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece\"",
  "post": {
    "id": "post_1234567890",
    "title": "如何使用 Agent2RSS",
    "channel": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "pubDate": "2026-02-05T15:30:00.000Z"
  },
  "isNew": true
}
```

### 响应示例（已存在 - 幂等性）

```json
{
  "success": true,
  "message": "Post already exists (idempotency key matched)",
  "post": {
    "id": "post_1234567890",
    "title": "如何使用 Agent2RSS",
    "channel": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "pubDate": "2026-02-05T15:30:00.000Z"
  },
  "isNew": false
}
```

### 字段说明

**必填字段**:
- `content`: 文章内容（支持 Markdown 和 HTML）

**可选字段**:
- `title`: 文章标题（未提供则自动从 Markdown 第一个 # 标题提取）
- `link`: 文章链接（未提供则自动生成内部永久链接）
- `contentType`: 内容类型（`auto`、`markdown`、`html`，默认 `auto`）
- `theme`: 主题名称（覆盖频道默认主题）
- `description`: 文章摘要（未提供则自动生成）
- `author`: 作者名称
- `tags`: 标签（数组或逗号分隔的字符串）
- `idempotencyKey`: 幂等性键（最大 255 字符，防止重复发布）

**请求头**:
- `Content-Type: application/json`（必填）
- `Authorization: Bearer <channel-token>`（必填，使用频道 Token）

**响应字段**:
- `isNew`: 是否为新创建的文章（`true` 表示新创建，`false` 表示已存在）

## 3. 推送内容到频道（文件上传方式）

### 请求

```bash
curl -X POST http://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts/upload \
  -H "Authorization: Bearer ch_4fd9cdce724ffb8d6ec69187b5438ae2" \
  -F "file=@article.md" \
  -F "title=自定义标题" \
  -F "tags=技术,教程" \
  -F "idempotencyKey=article-2024-01-01-001"
```

### 响应示例

```json
{
  "success": true,
  "message": "Post created successfully in channel \"8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece\" from uploaded file \"article.md\"",
  "post": {
    "id": "post_1234567890",
    "title": "自定义标题",
    "channel": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "pubDate": "2026-02-05T15:30:00.000Z"
  },
  "isNew": true
}
```

### 字段说明

**必填字段**:
- `file`: Markdown 文件（扩展名为 .md 或 .markdown）

**可选字段**:
- `title`: 文章标题
- `link`: 文章链接
- `contentType`: 内容类型（`auto`、`markdown`、`html`）
- `theme`: 主题名称
- `description`: 文章摘要
- `author`: 作者名称
- `tags`: 标签（逗号分隔的字符串）
- `idempotencyKey`: 幂等性键

**请求头**:
- `Authorization: Bearer <token>`（必填）
- `Content-Type: multipart/form-data`（自动设置）

## 4. 获取频道列表

### 请求

```bash
curl -X GET http://agent2rss.yaotutu.top:8765/api/channels
```

### 响应示例

```json
{
  "success": true,
  "channels": [
    {
      "id": "default",
      "name": "AI Briefing",
      "description": "Daily news summaries powered by AI",
      "theme": "spring",
      "language": "zh-CN",
      "maxPosts": 100,
      "createdAt": "2026-02-05T10:00:00.000Z"
    },
    {
      "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
      "name": "技术博客",
      "description": "分享技术文章和教程",
      "theme": "github",
      "language": "zh-CN",
      "maxPosts": 100,
      "createdAt": "2026-02-05T10:30:00.000Z"
    }
  ]
}
```

## 5. 获取单个频道信息

### 请求

```bash
curl -X GET http://agent2rss.yaotutu.top:8765/api/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece
```

### 响应示例

```json
{
  "success": true,
  "channel": {
    "id": "8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece",
    "name": "技术博客",
    "description": "分享技术文章和教程",
    "theme": "github",
    "language": "zh-CN",
    "maxPosts": 100,
    "createdAt": "2026-02-05T10:30:00.000Z",
    "updatedAt": "2026-02-05T15:30:00.000Z"
  },
  "rssUrl": "http://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml"
}
```

## 6. 获取 RSS Feed

### 请求

```bash
curl -X GET http://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml
```

### 响应示例

```xml
<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom">
  <channel>
    <title>技术博客</title>
    <description>分享技术文章和教程</description>
    <link>http://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece</link>
    <atom:link href="http://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/rss.xml" rel="self" type="application/rss+xml"/>
    <lastBuildDate>Wed, 05 Feb 2026 15:30:00 GMT</lastBuildDate>

    <item>
      <title>如何使用 Agent2RSS</title>
      <description>详细介绍 Agent2RSS 的使用方法和功能特性</description>
      <link>http://agent2rss.yaotutu.top:8765/channels/8cf83b0d-f856-4f7c-bd1c-4f6ca0338ece/posts/post_1234567890</link>
      <guid>post_1234567890</guid>
      <pubDate>Wed, 05 Feb 2026 15:30:00 GMT</pubDate>
      <author>Claude</author>
      <category>教程</category>
      <category>RSS</category>
      <category>技术</category>
    </item>
  </channel>
</rss>
```

## 错误响应示例

### 401 未授权

```json
{
  "success": false,
  "error": "Authorization header missing or invalid",
  "details": {
    "expected": "Authorization: Bearer <channel-token>",
    "help": "Provide the channel token (ch_xxx)"
  }
}
```

### 400 请求参数错误

```json
{
  "success": false,
  "error": "Missing required field: content",
  "details": {
    "field": "content",
    "issue": "Required field missing",
    "expected": { "content": "string (required)" }
  }
}
```

### 404 频道不存在

```json
{
  "success": false,
  "error": "Channel \"xxx\" not found",
  "details": {
    "channelId": "xxx",
    "help": "Use GET /api/channels to list all available channels"
  }
}
```

### 500 服务器错误

```json
{
  "success": false,
  "error": "Internal server error"
}
```

## 使用技巧

### 1. 推荐使用文件上传（重要）

**强烈推荐**：使用文件上传方式推送 Markdown 内容

```bash
curl -X POST "http://agent2rss.yaotutu.top:8765/api/channels/default/posts/upload" \
  -H "Authorization: Bearer ch_xxx" \
  -F "file=@article.md" \
  -F "idempotencyKey=article-001"
```

**优点**：
- 无需处理 JSON 转义
- 支持所有 Markdown 语法
- 自动提取标题和生成摘要
- 最简单可靠

**不推荐**：直接在 JSON 请求体中放置复杂 Markdown 内容，容易出现转义问题。

### 2. 幂等性防止重复发布

使用 `idempotencyKey` 确保相同内容不会重复发布：

```bash
# 使用文章 URL 作为幂等性键
IDEMPOTENCY_KEY="https://example.com/article-123"

curl -X POST http://agent2rss.yaotutu.top:8765/api/channels/default/posts \
  -H "Authorization: Bearer ch_xxx..." \
  -H "Content-Type: application/json" \
  -d "{\"content\":\"...\",\"idempotencyKey\":\"$IDEMPOTENCY_KEY\"}"
```

### 3. Markdown 内容格式化

推送内容时，可以使用完整的 Markdown 语法：

```markdown
# 一级标题

## 二级标题

**粗体文本** 和 *斜体文本*

- 列表项 1
- 列表项 2

[链接文本](https://example.com)

\`\`\`javascript
// 代码块
console.log('Hello, World!');
\`\`\`
```

### 4. 测试连接

快速测试服务器是否可用：

```bash
curl http://agent2rss.yaotutu.top:8765/health
```

## 注意事项

1. **Token 安全**: 不要在公开场合分享你的频道 Token
2. **认证方式**: 必须使用 `Authorization: Bearer` 格式，不再支持 `x-auth-token`
3. **幂等性键**: 建议使用有意义的键（如文章 URL、文件名等）
4. **字符编码**: 所有内容使用 UTF-8 编码
5. **特殊字符**: JSON 中的特殊字符需要转义（如 `"`, `\`, 换行符等）
6. **标题提取**: 如果不提供 `title`，系统会自动从 Markdown 第一个 # 标题提取
