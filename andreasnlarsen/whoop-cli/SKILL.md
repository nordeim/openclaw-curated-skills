---
name: whoop-cli
description: Companion skill for @andreasnlarsen/whoop-cli: agent-friendly WHOOP access via stable CLI JSON (day briefs, health flags, trends, exports) without raw API plumbing.
metadata:
  openclaw:
    requires:
      bins:
        - whoop
      env:
        - WHOOP_CLIENT_ID
        - WHOOP_CLIENT_SECRET
        - WHOOP_REDIRECT_URI
    primaryEnv: WHOOP_CLIENT_SECRET
    homepage: https://github.com/andreasnlarsen/whoop-cli
    install:
      - kind: node
        package: "@andreasnlarsen/whoop-cli@0.1.3"
        bins:
          - whoop
        label: Install whoop-cli from npm
---

# whoop-cli

Use the installed `whoop` command.

## Security + credential handling (required)

- Never ask users to paste client secrets/tokens into chat.
- For first-time auth, the user should run login **locally on their own shell**.
- Prefer read-only operational commands in agent flows (`summary`, `day-brief`, `health`, `trend`, `sync pull`).
- Do not run `whoop auth login` unless the user explicitly asks for login help.
- Tokens are stored locally at `~/.whoop-cli/profiles/<profile>.json` by the CLI.

## Install / bootstrap

If `whoop` is missing:

```bash
npm install -g @andreasnlarsen/whoop-cli@0.1.3
```

Optional OpenClaw skill install from package bundle:

```bash
whoop openclaw install-skill --force
```

## Core checks

1. `whoop auth status --json`
2. If unauthenticated, ask the user to run local login:
   - `whoop auth login --client-id ... --client-secret ... --redirect-uri ...`
3. Validate:
   - `whoop day-brief --json --pretty`

## Useful commands

- Daily:
  - `whoop summary --json --pretty`
  - `whoop day-brief --json --pretty`
  - `whoop strain-plan --json --pretty`
  - `whoop health flags --days 7 --json --pretty`
- Trends:
  - `whoop sleep trend --days 30 --json --pretty`
  - `whoop workout trend --days 14 --json --pretty`
- Export:
  - `whoop sync pull --start YYYY-MM-DD --end YYYY-MM-DD --out ./whoop.jsonl --json --pretty`

## Safety

- Never print client secrets or raw tokens.
- Keep API errors concise and actionable.
- Treat this integration as unofficial/non-affiliated.
