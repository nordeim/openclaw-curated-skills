---
name: feishu-smart-doc-writer
description: |
  Feishu/Lark Smart Document Writer - 飞书智能文档写入器.
  
  Solves API content limits by auto-chunking long documents and auto-transferring ownership.
  Guides OpenID config on first use.
  
  解决长文档API限制导致的空白问题，自动分块写入，自动转移所有权。
  首次使用自动引导配置OpenID。
---

# Feishu Smart Doc Writer

## Features

- **Auto-chunk writing** - Split long content into chunks to avoid blank documents
- **Auto ownership transfer** - Transfer doc ownership to user automatically
- **First-time guide** - Auto-prompts OpenID configuration on first use

## Tools

- `write_smart` - Create doc with auto-chunk and ownership transfer
- `append_smart` - Append content with auto-chunk
- `transfer_ownership` - Transfer doc ownership
- `configure` - Configure OpenID
- `get_config_status` - Check config status

## Quick Start

1. First use: run `write_smart`, it will guide you to get OpenID
2. Go to Feishu admin console → Permission Management
3. Grant `docs:permission.member:transfer` permission
4. Publish new version
5. Configure OpenID in the skill
6. Done! Future docs auto-transfer ownership
