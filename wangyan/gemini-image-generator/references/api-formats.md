# API 格式参考

## OpenAI 兼容格式（默认）

### 请求

```
POST {baseUrl}/chat/completions
Authorization: Bearer {apiKey}

{
  "model": "gemini-2.5-flash-image",
  "messages": [
    {"role": "user", "content": "生成一张蓝天白云的照片"}
  ],
  "max_tokens": 4096
}
```

图片编辑（带输入图片）：

```json
{
  "messages": [{
    "role": "user",
    "content": [
      {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}},
      {"type": "text", "text": "把天空改成夕阳色"}
    ]
  }]
}
```

### 响应格式

脚本自动识别以下四种响应格式：

**格式 A**：message.images 数组（cliproxy 等代理实际使用的格式）
```json
{"choices": [{"message": {
  "content": "描述文本",
  "images": [
    {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
  ]
}}]}
```

**格式 B**：content 数组含 image_url
```json
{"choices": [{"message": {"content": [
  {"type": "text", "text": "..."},
  {"type": "image_url", "image_url": {"url": "data:image/png;base64,..."}}
]}}]}
```

**格式 C**：content 数组含 image 对象
```json
{"choices": [{"message": {"content": [
  {"type": "image", "image": {"base64": "..."}}
]}}]}
```

**格式 D**：DALL-E 风格
```json
{"data": [{"b64_json": "...", "revised_prompt": "..."}]}
```

## Google 原生格式

使用 `google-genai` SDK，通过 `http_options.base_url` 自定义端点。
需要第三方提供商兼容 Google Gemini API 请求/响应结构。
