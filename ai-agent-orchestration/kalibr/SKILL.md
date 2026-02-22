---
name: kalibr
description: Autonomous execution path routing for OpenClaw agents. Reads real-time telemetry and routes to the optimal model + tool + parameter combination — so your agent navigates around failures, degradations, and cost spikes autonomously.
homepage: https://github.com/kalibr-ai/openclaw-kalibr
metadata:
  clawdbot:
    emoji: "⚡"
    requires:
      env: ["KALIBR_API_KEY"]
      bins: ["node"]
    primaryEnv: "KALIBR_API_KEY"
    install:
      - id: npm
        kind: node
        package: "@kalibr/openclaw"
        label: Install Kalibr OpenClaw plugin (npm)
---

# Kalibr — Autonomous Execution Path Routing for OpenClaw Agents

Kalibr hooks into your OpenClaw agent's runtime, reads live telemetry, and routes to the optimal execution path (model + tool + parameters) — preventing failures, degradations, and cost spikes before they impact users.

## Installation
```bash
openclaw plugins install @kalibr/openclaw
openclaw config set plugins.entries.kalibr.config.apiKey "your-kalibr-api-key"
openclaw config set plugins.entries.kalibr.config.enableRouting true
openclaw gateway restart
```

Get your API key: https://dashboard.kalibr.systems

## Two Modes

**Telemetry mode** (enableRouting: false) — instruments every LLM call with zero behavior changes. Full visibility into success rates, latency, cost, and failure patterns across providers.

**Routing mode** (enableRouting: true) — everything in telemetry mode, plus autonomous rerouting to the optimal model + tool + parameter combination. Uses Thompson Sampling + Wilson scoring. Detects provider degradation via 10% canary traffic and reroutes before users are affected.

## OpenClaw Hooks

- before_model_resolve — execution path override (primary hook)
- before_prompt_build — context injection
- before_agent_start — legacy fallback

## Reliability

Agents running in production with Kalibr see near 100% success rates even during provider incidents and degradations.

## Resources

- Docs: https://kalibr.systems/docs
- Dashboard: https://dashboard.kalibr.systems
- GitHub: https://github.com/kalibr-ai/openclaw-kalibr
- npm: https://www.npmjs.com/package/@kalibr/openclaw
- Python SDK: https://github.com/kalibr-ai/kalibr-sdk-python
- SKILL.md: https://kalibr.systems/skill.md