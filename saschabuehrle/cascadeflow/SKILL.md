---
name: cascadeflow
description: Set up CascadeFlow as an OpenClaw custom provider with fast, copy-paste steps. Use when users want quick install, preset selection (OpenAI-only, Anthropic-only, mixed), OpenClaw model alias setup, and safe production defaults for cascading with streaming and agent loops.
---

# CascadeFlow: Cost + Latency Reduction | 17+ Domain-Aware Models + OpenClaw-Native Events

Use CascadeFlow as an OpenClaw provider to lower cost and latency via cascading.
Assign up to 17 domain-specific models (for coding, web search, reasoning, and more), including OpenClaw-native event handling, and cascade across them (small model first, verifier when needed).
Keep setup minimal, then verify with one health check and one chat call.

## Fast Start

Or ask your OpenClaw agent to set it up for you as an OpenClaw custom provider with OpenClaw-native events and domain understanding.

1. Install:
```bash
python3 -m venv .venv
source .venv/bin/activate
# Fastest base setup (OpenClaw integration extras)
pip install "cascadeflow[openclaw]"
```

Quick provider variants:

```bash
# Anthropic-only preset users
pip install "cascadeflow[openclaw,anthropic]"

# OpenAI-only preset users
pip install "cascadeflow[openclaw,openai]"

# Mixed preset users (OpenAI + Anthropic + common providers)
pip install "cascadeflow[openclaw,providers]"
```

2. Choose one preset:
- `examples/configs/anthropic-only.yaml`
- `examples/configs/openai-only.yaml`
- `examples/configs/mixed-anthropic-openai.yaml`

3. Add keys in `.env`:
```bash
ANTHROPIC_API_KEY=...
OPENAI_API_KEY=...
```

4. Start server:
```bash
set -a; source .env; set +a
python3 -m cascadeflow.integrations.openclaw.openai_server \
  --host 127.0.0.1 \
  --port 8084 \
  --config examples/configs/anthropic-only.yaml \
  --auth-token local-openclaw-token \
  --stats-auth-token local-stats-token
```

5. Configure OpenClaw provider:
- `baseUrl`: `http://127.0.0.1:8084/v1`
- If server runs elsewhere, users should replace it with their host/IP, e.g.:
  - `http://<server-ip>:8084/v1` or `https://<domain>/v1` (behind proxy/TLS)
- `api`: `openai-completions`
- `model`: `cascadeflow`

6. Add alias and use it:
- Set alias `cflow` for `cascadeflow/cascadeflow` in OpenClaw config.
- Switch with `/model cflow`.
- Treat `/cascade` as optional custom command only if configured in OpenClaw.

## What Users Get

- Cost/latency reduction via cascading.
- Support for cascading while streaming is enabled.
- Support for cascading in multi-step agent loops.
- OpenAI-compatible `/v1/chat/completions` transport for OpenClaw.
- Domain-aware cascading via model presets.

## Safe Defaults

- Bind local: `127.0.0.1`.
- Use auth tokens for API and stats.
- Keep external exposure behind TLS reverse proxy.

## Full Docs

- `references/clawhub_publish_pack.md` for complete config and validation.
- `references/market_positioning.md` for listing copy and positioning.
