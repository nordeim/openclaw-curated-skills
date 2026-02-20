---
name: agent2rss-client
description: Agent2RSS 服务客户端，帮助用户管理 RSS 频道和推送内容。触发场景：(1) 用户提到"Agent2RSS"、"RSS 频道"、"推送文章/内容"等关键词，(2) 用户想要创建或管理 RSS 订阅，(3) 用户需要发布内容到 RSS Feed，(4) 用户需要使用幂等性防止重复发布。支持 JSON 和文件上传两种方式推送内容。
---

# Agent2RSS Client Skill

帮助用户通过 Agent2RSS 服务创建和管理 RSS 频道，推送内容到 RSS Feed。

## 核心功能

1. **频道管理** - 创建、查询、更新、删除 RSS 频道
2. **内容推送** - 通过 JSON 或文件上传方式发布文章
3. **幂等性支持** - 使用 idempotencyKey 防止重复发布
4. **RSS 订阅** - 生成标准 RSS Feed 供阅读器订阅

## 配置管理（自动化）

### 首次使用自动初始化流程

**重要**：每次执行任务前，必须先检查并初始化配置。

1. **检查配置文件**：读取 `config.json`
2. **如果不存在**：
   - 使用默认服务器地址：`http://agent2rss.yaotutu.top:8765`（**永远不使用 localhost**）
   - 询问用户频道名称（或使用默认值 "AI Briefing"）
   - 调用 API 创建频道：
     ```bash
     curl -X POST "http://agent2rss.yaotutu.top:8765/api/channels" \
       -H "Content-Type: application/json" \
       -d '{"name":"频道名","description":"AI 生成的内容"}'
     ```
   - 从响应中获取频道 ID 和 Token
   - 创建 config.json 并保存配置：
     ```json
     {
       "serverUrl": "http://agent2rss.yaotutu.top:8765",
       "defaultChannelId": "返回的频道ID",
       "channels": [{
         "id": "返回的频道ID",
         "name": "频道名",
         "token": "返回的Token",
         "postsUrl": "http://agent2rss.yaotutu.top:8765/api/channels/{id}/posts",
         "rssUrl": "http://agent2rss.yaotutu.top:8765/channels/{id}/rss.xml"
       }]
     }
     ```
   - 继续执行推送任务
3. **如果存在**：从 config.json 读取配置，继续执行

### 配置文件结构

```json
{
  "serverUrl": "http://agent2rss.yaotutu.top:8765",
  "defaultChannelId": "default",
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

**关键点**：
- `serverUrl` 是必填项，不能是 localhost（除非用户明确配置）
- 所有 API 调用必须使用 `config.json` 中的 `serverUrl`
- 所有 RSS 地址必须使用 `config.json` 中的 `serverUrl`
- 频道的 `postsUrl` 和 `rssUrl` 必须基于 `serverUrl` 构建

## 认证方式

**标准 Bearer Token 认证**（必需）：

```bash
Authorization: Bearer <channel-token>
```

每个频道有独立的 Token（格式 `ch_xxx...`），创建频道时生成。

## 推荐的推送方式

### ⚠️ 重要：避免 JSON 转义问题

直接在 JSON 请求体中放置 Markdown 内容容易出现转义问题（引号、换行符、反斜杠等）。

**强烈推荐使用文件上传方式**：

### 文件上传（推荐）✅

直接上传 Markdown 文件，无需处理 JSON 转义：

```bash
curl -X POST {serverUrl}/api/channels/{channelId}/posts/upload \
  -H "Authorization: Bearer {token}" \
  -F "file=@article.md" \
  -F "idempotencyKey=article-001"
```

**优点**：
- 无需处理 JSON 转义
- 最简单可靠
- 支持所有 Markdown 语法
- 自动提取标题
- 支持幂等性

**可选字段**：
- `title` - 自定义标题
- `tags` - 标签（逗号分隔）
- `author` - 作者名
- `idempotencyKey` - 防止重复发布

### JSON 方式（仅适合简单内容）

如果内容简单且已正确转义，可以使用 JSON 方式。但对于包含复杂 Markdown 的内容，请使用文件上传。

## 常用操作

### 1. 创建频道

```bash
curl -X POST {serverUrl}/api/channels \
  -H "Content-Type: application/json" \
  -d '{
    "name": "技术博客",
    "description": "分享技术文章"
  }'
```

响应包含频道 ID 和 Token，保存到 `config.json`。

### 2. 推送内容（JSON 方式 - 仅适合简单内容）

⚠️ **警告**：JSON 方式容易出现转义问题，推荐使用文件上传方式（见上方"推荐的推送方式"章节）。

**最简调用**（仅内容，标题自动提取）：

```bash
curl -X POST {postsUrl} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "content": "# 标题\n\n内容..."
  }'
```

**响应示例**：

```json
{
  "success": true,
  "message": "Post created successfully in channel \"xxx\"",
  "post": {
    "id": "xxx",
    "title": "标题",
    "channel": "default",
    "pubDate": "2024-01-01T00:00:00.000Z"
  },
  "isNew": true
}
```

### 3. 幂等性支持

使用 `idempotencyKey` 防止重复发布：

- 相同频道内相同 key 的请求只会创建一次文章
- 响应中 `isNew: true` 表示新创建，`false` 表示已存在
- 适用于 JSON 和文件上传两种方式

**示例**：

```bash
# 第一次请求 - 创建新文章
curl -X POST {postsUrl} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content":"# 测试","idempotencyKey":"key1"}'
# 响应: {"success":true,"isNew":true,...}

# 第二次请求 - 返回已存在的文章
curl -X POST {postsUrl} \
  -H "Authorization: Bearer {token}" \
  -H "Content-Type: application/json" \
  -d '{"content":"# 测试","idempotencyKey":"key1"}'
# 响应: {"success":true,"isNew":false,...}
```

## 工作流程

### 推送单篇文章

1. **检查并初始化配置**：
   - 读取 `config.json`
   - 如果不存在，执行自动初始化流程（创建频道并保存配置）
2. **确定目标频道**：
   - 如果用户明确指定频道（如"发布到技术博客频道"），使用指定的频道
   - 否则使用 `defaultChannelId` 对应的频道
3. **从配置读取数据**：
   - `serverUrl`: 服务器地址
   - `token`: 从 `channels` 数组中找到目标频道的 token
4. 准备 Markdown 文件
5. **使用文件上传方式推送**（推荐）：
   ```bash
   curl -X POST "{config.serverUrl}/api/channels/{targetChannelId}/posts/upload" \
     -H "Authorization: Bearer {targetChannel.token}" \
     -F "file=@article.md" \
     -F "idempotencyKey=unique-key"
   ```
6. 检查响应中的 `isNew` 字段
7. **返回 RSS Feed URL**：`{config.serverUrl}/channels/{targetChannelId}/rss.xml`

### 创建新频道

1. 提示用户提供频道名称和描述
2. **从 `config.json` 读取 `serverUrl`**（如果配置不存在，使用默认值 `http://agent2rss.yaotutu.top:8765`）
3. 调用创建频道 API：
   ```bash
   curl -X POST "{config.serverUrl}/api/channels" \
     -H "Content-Type: application/json" \
     -d '{"name":"频道名","description":"描述"}'
   ```
4. 保存返回的频道 ID 和 Token 到 `config.json`：
   - 添加到 `channels` 数组
   - 构建 `postsUrl` 和 `rssUrl`（基于 `serverUrl`）
5. 可选：更新 `defaultChannelId` 为新频道
6. **提供 RSS Feed URL**：`{config.serverUrl}/channels/{channelId}/rss.xml`

### 查看本地频道列表

1. **读取 config.json**
2. **显示 channels 数组中的所有频道**：
   - 频道 ID
   - 频道名称
   - RSS Feed URL
   - 是否为默认频道（defaultChannelId）
3. 格式化输出供用户查看

### 设置默认频道

1. **读取 config.json**
2. **显示可用频道列表**（从 channels 数组）
3. **让用户选择要设为默认的频道**
4. **更新 config.json 中的 defaultChannelId**
5. **确认设置成功**，提供该频道的 RSS Feed URL

### 更新频道配置

修改频道的名称或描述。

**需要认证**：频道 Token

**可更新字段**（仅限以下两个）：
- `name` - 频道名称
- `description` - 频道描述

**工作流程**：
1. 从 config.json 读取指定频道（或默认频道）的 ID 和 token
2. 提示用户要修改的字段（name 或 description）
3. 调用更新频道 API：
   ```bash
   curl -X PUT "{config.serverUrl}/api/channels/{channelId}" \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{"name":"新名称","description":"新描述"}'
   ```
4. 更新成功后，同步更新本地 config.json 中对应频道的信息

### 删除频道

永久删除一个频道及其所有文章。

**需要认证**：频道 Token

⚠️ **警告**：此操作不可撤销，会删除频道的所有文章。

**工作流程**：
1. 读取 config.json 显示所有频道
2. 让用户选择要删除的频道
3. **显示频道信息并要求用户确认**（防止误删）
4. 从 config.json 读取该频道的 token
5. 调用删除频道 API：
   ```bash
   curl -X DELETE "{config.serverUrl}/api/channels/{channelId}" \
     -H "Authorization: Bearer {token}"
   ```
6. 删除成功后，从 config.json 的 channels 数组中移除该频道
7. 如果删除的是 defaultChannelId：
   - 如果还有其他频道，自动将第一个可用频道设为默认
   - 如果没有其他频道，将 defaultChannelId 设为 null，提示用户创建新频道

## 常用场景

### 场景 1：发布到指定频道

**用户需求**：我有多个频道，想发布内容到特定频道

**操作步骤**：
1. 用户明确表达"发布到 xxx 频道"
2. 从 config.json 的 channels 数组中查找匹配的频道
3. 使用该频道的 token 和 ID 发布内容
4. 如果未指定频道，使用 defaultChannelId

### 场景 2：设置默认频道

**用户需求**：我想把"技术博客"设为默认频道

**操作步骤**：
1. 读取 config.json 显示所有频道
2. 让用户选择要设为默认的频道
3. 更新 defaultChannelId
4. 确认设置成功

### 场景 3：修改频道名称或描述

**用户需求**：我想修改频道的名称

**操作步骤**：
1. 从 config.json 读取指定频道（或默认频道）的 ID 和 token
2. 提示用户输入新的名称或描述
3. 调用 `PUT {serverUrl}/api/channels/{channelId}` 更新
4. 同步更新本地 config.json

### 场景 4：删除不需要的频道

**用户需求**：我创建了一个测试频道，现在想删除它

**操作步骤**：
1. 读取 config.json 显示所有频道
2. 让用户选择要删除的频道
3. 显示频道信息并要求确认
4. 调用 `DELETE {serverUrl}/api/channels/{channelId}` 删除
5. 从 config.json 中移除该频道
6. 如果删除的是默认频道，自动设置新的默认频道

## 错误处理

- **401 Unauthorized**：Token 无效或缺失，检查 `Authorization` 头
- **404 Not Found**：频道不存在，检查频道 ID
- **400 Bad Request**：参数错误，检查必填字段 `content`
- **500 Server Error**：服务器错误，稍后重试

## 参考资料

详细的 API 调用示例和响应格式见 `references/api-examples.md`。

## 注意事项

1. **Token 安全**：不要在公开场合分享频道 Token
2. **内容格式**：支持完整的 Markdown 语法
3. **字符编码**：使用 UTF-8 编码
4. **幂等性键**：建议使用有意义的键（如文章 URL、时间戳等）
5. **认证方式**：必须使用 `Authorization: Bearer` 格式
