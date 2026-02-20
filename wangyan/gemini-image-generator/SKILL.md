---
name: gemini-image-generator
description: >
  使用 Gemini 模型生成或编辑图片，支持自定义第三方 API 端点（baseUrl）和密钥。
  默认 OpenAI 兼容格式，也支持 Google 原生格式。
  触发场景：文生图、图片编辑、图片合成、绘画请求、生成插画/照片/海报、
  AI 画图、根据描述生成图像等。
---

# Gemini Image Gen

使用脚本生成或编辑图片，支持第三方 API 端点。

## 安装

将技能目录复制到以下任一位置：

- 工作区技能目录：`{workspace}/skills/gemini-image-generator/`
- 全局技能目录：通过 `skills.load.extraDirs` 指定的目录

前置依赖：`uv`（Python 包管理器）。脚本依赖（`httpx`、`pillow`、`google-genai`）由 `uv run` 自动安装。

```shell
curl -LsSf https://astral.sh/uv/install.sh | sh
```

在 `~/.openclaw/openclaw.json` 中添加配置：

```json
{
  "skills": {
    "entries": {
      "gemini-image-generator": {
        "enabled": true,
        "apiKey": "your-api-key",
        "env": {
          "GEMINI_API_KEY": "your-api-key",
          "GEMINI_BASE_URL": "https://your-provider.com/v1",
          "GEMINI_MODEL": "gemini-3-pro-image-preview",
          "GEMINI_API_FORMAT": "openai",
          "GEMINI_TIMEOUT": "300",
          "GEMINI_OUTPUT_DIR": "images"
        }
      }
    }
  }
}
```

`env` 中的环境变量会自动注入到 agent 运行环境中。

## 生成图片

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "图片描述" --filename "output.png"
```

## 编辑图片（单图）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "编辑指令" --filename "edited.png" -i "/path/input.png" --resolution 2K
```

## 合成多张图片（最多 14 张）

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "合成指令" --filename "composed.png" -i img1.png -i img2.png -i img3.png
```

## 指定自定义端点

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "描述" --filename "output.png" \
  --base-url "https://example.com/v1" --api-key "sk-xxx" --model "gemini-2.5-flash-image"
```

## 使用 Google 原生格式

```bash
uv run {baseDir}/scripts/generate_image.py --prompt "描述" --filename "output.png" --api-format google
```

## 配置

优先级：命令行参数 > 环境变量（由 `skills.entries.gemini-image-generator.env` 注入）

| 参数 | 环境变量 | 说明 |
|------|---------|------|
| `--api-key` / `-k` | `GEMINI_API_KEY` | API 密钥（必填） |
| `--base-url` / `-b` | `GEMINI_BASE_URL` | API 端点 URL（必填） |
| `--model` / `-m` | `GEMINI_MODEL` | 模型名称（默认 `gemini-3-pro-image-preview`） |
| `--api-format` | `GEMINI_API_FORMAT` | `openai`（默认）或 `google` |
| `--timeout` / `-t` | `GEMINI_TIMEOUT` | 超时秒数（默认 300） |
| `--resolution` / `-r` | `GEMINI_RESOLUTION` | `1K`（默认）、`2K`、`4K` |
| — | `GEMINI_OUTPUT_DIR` | 输出目录（默认 `images`） |

其他可选参数：

- `--input-image` / `-i`：输入图片路径（可重复，最多 14 张）
- `--quality`：`standard`（默认）或 `hd`
- `--style`：`natural`（默认）或 `vivid`
- `--verbose` / `-v`：输出详细调试信息

## 注意事项

- 文件名使用时间戳格式：`yyyy-mm-dd-hh-mm-ss-name.png`
- 脚本输出 `MEDIA:` 行供 OpenClaw 自动附件到聊天
- 不要回读图片内容，只报告保存路径
- 编辑模式下未指定分辨率时，自动根据输入图片尺寸推断
- 内置 429 限流和超时自动重试（最多 3 次）
- API 响应格式详见 [references/api-formats.md](references/api-formats.md)
