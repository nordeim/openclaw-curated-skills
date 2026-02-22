---
name: health-sync
description: Analyze synced health data across Oura, Withings, Hevy, Strava, WHOOP, and Eight Sleep.
read_when:
  - User asks for health-sync setup, auth, sync, or provider status
  - User asks about sleep, recovery, training, activity, your health, or cross-provider trends
---

# Health Sync Analysis Skill

## Purpose

This skill is dedicated to analyzing the user's health data across available providers:

- Oura
- Withings
- Hevy
- Strava
- WHOOP
- Eight Sleep

The main goal is to help the user understand trends, compare signals across providers, and find useful insights from their synced data.

## Scope

Use this skill when the user asks questions such as:

- How did I sleep last night?
- How was my last workout?
- How did my resting heart rate change during the year?
- What trends are you seeing in my recovery, sleep, and training?
- What useful insights or next steps should I focus on?

## Setup Handling

For initial setup or auth onboarding, consult:

- `references/setup.md`

Do not duplicate setup instructions here. This skill should defer setup details to the setup reference.

## Schema Handling

To understand data schemas and query correctly, read the provider reference files:

- `references/oura.md`
- `references/withings.md`
- `references/hevy.md`
- `references/strava.md`
- `references/whoop.md`
- `references/eightsleep.md`

## Freshness Rule (Mandatory)

Before any analysis, always run:

```bash
health-sync sync
```

If sync fails, report the failure clearly and continue analysis only if the user explicitly asks to proceed with potentially stale data.

## Analysis Workflow

1. Run `health-sync sync` first.
2. Identify the user question and which provider/resource(s) are relevant.
3. Read the provider schema reference before forming SQL.
4. Query `records`, `sync_state`, and `sync_runs` as needed.
5. Produce a clear, user-friendly answer with concrete numbers and dates.
6. Highlight meaningful patterns and offer practical guidance.
7. When data quality or coverage is limited, say so explicitly.

## Output Style

- Be concise, clear, and practical.
- Focus on useful interpretation, not just raw data dumps.
- Connect metrics to actionable insights (sleep, recovery, training, consistency, etc.).
- Ask follow-up questions only when necessary to improve analysis quality.
