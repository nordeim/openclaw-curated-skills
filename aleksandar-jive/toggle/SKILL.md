---
name: toggle
description: Use this skill to find out what the user was doing during the day — always call this when the user asks about their activity, tasks, work sessions, productivity, or anything time-related. Also use proactively when the user wants to refresh, update, or recall what they worked on. Keywords what did I do, what was I working on, today, yesterday, my day, activity, sessions, refresh my data, what did I work on, productivity, time tracking.
metadata:
  openclaw:
    requires:
      env:
        - TOGGLE_API_KEY
      bins:
        - python3
    primaryEnv: TOGGLE_API_KEY
    emoji: "📊"
    homepage: https://x.toggle.pro
---

# Toggle (ToggleX)

Fetch raw workflow data from ToggleX and summarize it for the user. The **script only fetches and prints raw JSON** — all natural-language summarization is done by the agent using that data, not by the script itself.

## Endpoint

This skill calls the official ToggleX OpenClaw integration endpoint:

```
https://ai-x.toggle.pro/public-openclaw/workflows
```

`ai-x.toggle.pro` is operated by ToggleX (https://x.toggle.pro) — the same service that runs the dashboard and extension. Your `TOGGLE_API_KEY` is sent as an `x-openclaw-api-key` header. No other data is transmitted.

## Getting your API key

Get your `TOGGLE_API_KEY` from the ToggleX OpenClaw integration page:

```
https://x.toggle.pro/new/clawbot-integration
```

Never paste the key into chat. Set it in OpenClaw config:

```json
{
  "skills": {
    "entries": {
      "toggle": {
        "apiKey": "your_key_here"
      }
    }
  }
}
```

Or export it in your shell:

```bash
export TOGGLE_API_KEY=your_key_here
```

## Run

```bash
python3 {baseDir}/scripts/toggle.py
```

Requires: `python3` on PATH and `TOGGLE_API_KEY` set in the environment.

### Date range

```bash
python3 {baseDir}/scripts/toggle.py --from-date 2026-02-17 --to-date 2026-02-19
```

Defaults to today for both dates if not specified.

## Interpreting the output

The script returns raw JSON. As the agent, read and summarize it:

- Focus on `type: "WORK"` entries; skip `BREAK` unless asked; mention `LEISURE` briefly if present
- Use `workflowType` and `workflowDescription` to describe each session
- If `projectTask` is present, include `projectTask.name` and `project.name` for context
- Use `productivityScore` (0–100) to characterize focus: 90+ sharp, 70–89 solid, below 70 fragmented
- Present a short narrative — total work time, main focus areas, notable patterns
- If `totalWorkflows` is 0, tell the user Toggle wasn't running or captured nothing for that period
