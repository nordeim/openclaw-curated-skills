---
name: monet-ai
description: |
  Monet AI - AI content generation API for video, image and music.
  Supports Sora, Wan, Hailuo, Kling, Veo, GPT-4o, Flux, Imagen, Suno and more.
metadata:
  openclaw:
    requires:
      env:
        - MONET_API_KEY  # Required: API key from monet.vision
      bins: []
    install:
      - id: node
        kind: npm
        package: monet-ai
        label: Install monet-ai SDK (npm)
---

# Monet AI Skill

AI content generation API for AI agents.

## When to Use

Use this skill when:
- You need to generate video content (Sora, Wan, Hailuo, Kling, Veo)
- You need to generate images (GPT-4o, Flux, Imagen, Ideogram)
- You need to generate music (Suno, Udio)
- You want to integrate AI generation capabilities into your agent workflow

## Installation

```bash
npm install monet-ai
```

## Getting API Key

1. Visit https://monet.vision to register an account
2. After login, go to https://monet.vision/skills/keys to create an API Key
3. Configure the API Key in environment variables or code

If you don't have an API Key, ask your owner to apply at monet.vision.

## Quick Start

```typescript
import { MonetAI } from "monet-ai";

const monet = new MonetAI({ 
  apiKey: process.env.MONET_API_KEY! 
});

// Create a video generation task
const task = await monet.createTask({
  type: "video",
  input: {
    model: "sora-2",
    prompt: "A cat running in the park",
    duration: 5,
    aspect_ratio: "16:9"
  }
});

// Poll for result
while (task.status === "pending" || task.status === "processing") {
  await new Promise(r => setTimeout(r, 3000));
  task = await monet.getTask(task.id);
}

console.log("Result:", task.outputs);
```

## Supported Models

### Video Generation

#### Sora (OpenAI)

**sora-2**
```typescript
{
  model: "sora-2",
  prompt: string,                // Required
  images?: string[],             // Optional
  duration?: 10 | 15,           // Optional, default: 10
  aspect_ratio?: "16:9" | "9:16"
}
```

**sora-2-pro**
```typescript
{
  model: "sora-2-pro",
  prompt: string,
  images?: string[],
  duration?: 15 | 25,           // Optional, default: 15
  aspect_ratio?: "16:9" | "9:16"
}
```

#### Veo (Google)

**veo-3-1-fast**, **veo-3-1**
```typescript
{
  model: "veo-3-1-fast" | "veo-3-1",
  prompt: string,
  images?: string[],
  aspect_ratio?: "16:9" | "9:16"
}
```

**veo-3-fast**, **veo-3**
```typescript
{
  model: "veo-3-fast" | "veo-3",
  prompt: string,
  images?: string[],
  negative_prompt?: string
}
```

#### Wan

**wan-2-6**
```typescript
{
  model: "wan-2-6",
  prompt: string,
  images?: string[],
  duration?: 5 | 10 | 15,
  resolution?: "720p" | "1080p",
  aspect_ratio?: "16:9" | "9:16" | "4:3" | "3:4" | "1:1",
  shot_type?: "single" | "multi"
}
```

**wan-2-5**
```typescript
{
  model: "wan-2-5",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "720p" | "1080p",
  aspect_ratio?: "16:9" | "9:16" | "4:3" | "3:4" | "1:1"
}
```

**wan-2-2-flash**
```typescript
{
  model: "wan-2-2-flash",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "720p" | "1080p",
  negative_prompt?: string
}
```

**wan-2-2**
```typescript
{
  model: "wan-2-2",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "1080p",
  aspect_ratio?: "16:9" | "9:16" | "4:3" | "3:4" | "1:1",
  negative_prompt?: string
}
```

#### Kling

**kling-2-6**
```typescript
{
  model: "kling-2-6",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  generate_audio?: boolean
}
```

**kling-2-5**
```typescript
{
  model: "kling-2-5",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  negative_prompt?: string
}
```

**kling-v2-1-master**, **kling-v2-1**, **kling-v2**
```typescript
{
  model: "kling-v2-1-master" | "kling-v2-1" | "kling-v2",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  aspect_ratio?: "1:1" | "16:9" | "9:16",
  strength?: number,            // 0-1
  negative_prompt?: string
}
```

#### Hailuo

**hailuo-2-3**, **hailuo-2-3-fast**
```typescript
{
  model: "hailuo-2-3" | "hailuo-2-3-fast",
  prompt: string,
  images?: string[],
  duration?: 6 | 10,
  resolution?: "768p" | "1080p"
}
```

**hailuo-02**
```typescript
{
  model: "hailuo-02",
  prompt: string,
  images?: string[],
  duration?: 6 | 10,
  resolution?: "768p" | "1080p"
}
```

**hailuo-01-live2d**, **hailuo-01**
```typescript
{
  model: "hailuo-01-live2d" | "hailuo-01",
  prompt: string,
  images?: string[]
}
```

#### Doubao Seedance

**doubao-seedance-1-5-pro**
```typescript
{
  model: "doubao-seedance-1-5-pro",
  prompt: string,
  images?: string[],
  duration?: number,
  resolution?: "480p" | "720p",
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16" | "21:9",
  generate_audio?: boolean
}
```

**doubao-seedance-1-0-pro-fast**
```typescript
{
  model: "doubao-seedance-1-0-pro-fast",
  prompt: string,
  images?: string[],
  duration?: number,
  resolution?: "720p" | "1080p",
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16" | "21:9"
}
```

**doubao-seedance-1-0-pro**
```typescript
{
  model: "doubao-seedance-1-0-pro",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "1080p",
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16"
}
```

**doubao-seedance-1-0-lite**
```typescript
{
  model: "doubao-seedance-1-0-lite",
  prompt: string,
  images?: string[],
  duration?: 5 | 10,
  resolution?: "480p" | "720p" | "1080p"
}
```

#### Special Features

**kling-motion-control**
```typescript
{
  model: "kling-motion-control",
  prompt: string,                // Required
  images: string[],              // Required: min 1
  videos: string[],              // Required: min 1
  resolution?: "720p" | "1080p"
}
```

**runway-act-two**
```typescript
{
  model: "runway-act-two",
  images: string[],              // Required: min 1
  videos: string[],              // Required: min 1
  aspect_ratio?: "1:1" | "4:3" | "16:9" | "3:4" | "9:16" | "21:9"
}
```

**wan-animate-mix**, **wan-animate-mix-pro**
```typescript
{
  model: "wan-animate-mix" | "wan-animate-mix-pro",
  videos: string[],              // Required
  images: string[]               // Required
}
```

**wan-animate-move**, **wan-animate-move-pro**
```typescript
{
  model: "wan-animate-move" | "wan-animate-move-pro",
  videos: string[],              // Required
  images: string[]               // Required
}
```

---

### Image Generation

#### GPT (OpenAI)

**gpt-4o**
```typescript
{
  model: "gpt-4o",
  prompt: string,
  images?: string[],
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

**gpt-image-1-5**
```typescript
{
  model: "gpt-image-1-5",
  prompt: string,
  images?: string[],             // max 10
  aspect_ratio?: "1:1" | "3:2" | "2:3",
  quality?: "auto" | "low" | "medium" | "high"
}
```

#### Nano Banana

**nano-banana-1**
```typescript
{
  model: "nano-banana-1",
  prompt: string,
  images?: string[],             // max 5
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "16:9" | "9:16"
}
```

**nano-banana-2**
```typescript
{
  model: "nano-banana-2",
  prompt: string,
  images?: string[],             // max 14
  aspect_ratio?: "1:1" | "2:3" | "3:2" | "4:3" | "3:4" | "4:5" | "5:4" | "16:9" | "9:16" | "21:9",
  resolution?: "1K" | "2K" | "4K"
}
```

#### Wan

**wan-i-2-6**
```typescript
{
  model: "wan-i-2-6",
  prompt: string,
  images?: string[],             // max 4
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16" | "21:9"
}
```

**wan-2-5**
```typescript
{
  model: "wan-2-5",
  prompt: string,
  images?: string[],             // max 2
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16" | "21:9"
}
```

#### Flux

**flux-2-dev**
```typescript
{
  model: "flux-2-dev",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16"
}
```

**flux-kontext-pro**, **flux-kontext-max**
```typescript
{
  model: "flux-kontext-pro" | "flux-kontext-max",
  prompt: string,
  images?: string[],
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

**flux-1-schnell**
```typescript
{
  model: "flux-1-schnell",
  prompt: string
}
```

#### Imagen (Google)

**imagen-3-0**, **imagen-4-0**
```typescript
{
  model: "imagen-3-0" | "imagen-4-0",
  prompt: string,
  aspect_ratio?: "1:1" | "3:4" | "4:3" | "9:16" | "16:9",
  style?: string
}
```

#### Ideogram

**ideogram-v2**, **ideogram-v3**
```typescript
{
  model: "ideogram-v2" | "ideogram-v3",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string
}
```

#### Others

**seedream-4-0**
```typescript
{
  model: "seedream-4-0",
  prompt: string,
  images?: string[],             // max 10
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16"
}
```

**stability-1-0**
```typescript
{
  model: "stability-1-0",
  prompt: string,
  aspect_ratio?: "1:1" | "4:3" | "3:2" | "16:9" | "3:4" | "2:3" | "9:16",
  style?: string,
  negative_prompt?: string
}
```

---

### Music Generation

**suno-3.5**, **udio-v1-6**
```typescript
{
  model: "suno-3.5" | "udio-v1-6",
  prompt: string                 // Required: music description
}
```

---

## API Methods

### createTask(options)
Create an async task. Returns immediately with task ID.

```typescript
const task = await monet.createTask({
  type: "video",
  input: { model: "sora-2", prompt: "A cat" },
  idempotency_key: "unique-key"  // Required - must be a unique value (e.g., UUID)
});
```

> ⚠️ **Important**: `idempotency_key` is **required**. Use a unique value (e.g., UUID) to prevent duplicate task creation if the request is retried.

### createTaskStream(options)
Create a task with SSE streaming. Returns ReadableStream.

```typescript
const stream = await monet.createTaskStream({
  type: "video", 
  input: { model: "sora-2", prompt: "A cat" }
});
```

### getTask(taskId)
Get task status and result.

```typescript
const task = await monet.getTask("task_id");
```

### listTasks(options)
List tasks with pagination.

```typescript
const list = await monet.listTasks({ page: 1, pageSize: 20 });
```

## Configuration

```typescript
const monet = new MonetAI({
  apiKey: "monet_xxx",    // Required: API key from monet.vision
  timeout: 60000          // Optional: timeout in ms
});
```

## Environment Variables

```bash
MONET_API_KEY=monet_xxx
```

## curl Examples

### Create Task

```bash
curl -X POST https://monet.vision/api/v1/tasks/async \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer monet_xxx" \
  -d '{
    "type": "video",
    "input": {
      "model": "sora-2",
      "prompt": "A cat running"
    }
  }'
```

### Get Task

```bash
curl https://monet.vision/api/v1/tasks/task_id \
  -H "Authorization: Bearer monet_xxx"
```

### List Tasks

```bash
curl "https://monet.vision/api/v1/tasks/list?page=1" \
  -H "Authorization: Bearer monet_xxx"
```
