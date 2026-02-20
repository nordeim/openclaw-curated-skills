# Enterprise Legal Guardrails

Open-source OpenClaw skill for outbound legal/compliance preflight checks.

## Quick install

```bash
git clone https://github.com/lawyered0/enterprise-legal-guardrails.git
cd enterprise-legal-guardrails
```

You can run this directly:

```bash
python3 scripts/check_enterprise_guardrails.py --help
```

Then run against draft text as needed in your own outbound workflows:

```bash
python3 scripts/check_enterprise_guardrails.py \
  --action post \
  --app <app_name> \
  --text "Draft message here"
```

```bash
python3 scripts/check_enterprise_guardrails.py \
  --action comment \
  --file /tmp/draft.txt \
  --json
```

## What it checks
- Legal-conclusion phrasing
- Defamation / reputational risk
- Financial certainty and guarantee claims
- Market manipulation framing
- Coercive or spam-like outreach
- Harassment / abusive language
- Privacy and sensitive data leakage
- HR- or workplace-sensitive allegations

## Generic app filtering

Defaults: check everything outbound.

You can restrict/ignore specific apps at check time using CLI args:

```bash
python3 scripts/check_enterprise_guardrails.py --action comment --app whatsapp --scope include --apps whatsapp,telegram --text "..."
```

Or global env config:

```bash
export ENTERPRISE_LEGAL_GUARDRAILS_OUTBOUND_SCOPE=exclude
export ENTERPRISE_LEGAL_GUARDRAILS_OUTBOUND_APPS=whatsapp,email,moltbook,babylon
export BABYLON_GUARDRAILS_SCOPE=exclude   # legacy alias
export BABYLON_GUARDRAILS_APPS=whatsapp,email,moltbook,babylon
```

## Integration model

This is a generic OpenClaw outbound safety layer. Existing Babylon integration points are optional examples:

- create_post
- create_comment
- send_message

Other outbound skills can adopt the same pattern (`--action`, `--app`, and optional env scope).

Control with env vars (legacy aliases preserved):

```bash
export ENTERPRISE_LEGAL_GUARDRAILS_ENABLED=true
export ENTERPRISE_LEGAL_GUARDRAILS_STRICT=false   # set true to block on REVIEW
export ENTERPRISE_LEGAL_GUARDRAILS_POLICIES=social,antispam,hr,privacy,market,financial,legal
```

## Tuning

You can tune sensitivity without changing rules:

- `ENTERPRISE_LEGAL_GUARDRAILS_REVIEW_THRESHOLD` (default `5`)
- `ENTERPRISE_LEGAL_GUARDRAILS_BLOCK_THRESHOLD` (default `9`)
- Alias: `ELG_*` and `BABYLON_GUARDRAILS_*` equivalents

CLI overrides:
- `--review-threshold <int>`
- `--block-threshold <int>`

## Universal outbound adapter (no-native integration path)

For command-based outbound flows that don't yet call the guardrails directly (e.g., gog
Gmail/website scripts), run your command through:

```bash
python3 scripts/check_enterprise_guardrails.py ... # run checks directly
# or (recommended)
python3 scripts/guard_and_run.py   --app gmail --action message   --text "$DRAFT"   -- gog gmail send --to user@domain.com --subject "Update" --body "$DRAFT"
```

Notes:
- `--action` should match the outbound intent: `message` for email/chat, `post` for public content.
- `--app` sets the app namespace (e.g., `gmail`, `website`, `babylon`, `slack`).

## Exit codes

- `0` PASS/WATCH
- `1` REVIEW
- `2` BLOCK
