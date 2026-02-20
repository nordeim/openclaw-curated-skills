---
description: Diagnose .env file issues — missing variables, format errors, security risks, and misconfigurations.
---

# Env Doctor

Diagnose and fix .env file issues.

## Instructions

1. **Read files**: Parse `.env` (and `.env.example` if exists)
2. **Detect issues**:

   | Severity | Issue | Example |
   |----------|-------|---------|
   | 🔴 Critical | Secret committed to git | `.env` not in `.gitignore` |
   | 🔴 Critical | Missing required vars | In `.env.example` but not `.env` |
   | 🟡 Warning | Duplicate keys | `DB_HOST` defined twice |
   | 🟡 Warning | Empty values | `API_KEY=` |
   | 🟡 Warning | Spaces around `=` | `DB_HOST = localhost` (won't parse correctly) |
   | 🔵 Info | Extra keys | In `.env` but not `.env.example` |
   | 🔵 Info | Quoted booleans | `DEBUG="true"` (should be `DEBUG=true`) |

3. **Validation checks**:
   - URLs missing protocol (`example.com` → `https://example.com`)
   - Port numbers out of range (0-65535)
   - Unquoted values with spaces
   - Trailing whitespace
   - BOM characters at file start

4. **Cross-reference**: If `.env.example` exists, report missing and extra keys

5. **Git safety check**:
   ```bash
   # Is .env in .gitignore?
   grep -q "^\.env$" .gitignore 2>/dev/null && echo "✅ Protected" || echo "🔴 NOT in .gitignore!"
   # Was .env ever committed?
   git log --all --diff-filter=A -- .env 2>/dev/null
   ```

6. **Report format**:
   ```
   🩺 Env Doctor — .env

   Found 3 issues:

   🔴 CRITICAL: .env not in .gitignore
      Fix: echo ".env" >> .gitignore

   🟡 WARNING: Duplicate key DB_HOST (lines 4, 12)
      Fix: Remove duplicate on line 12

   🔵 INFO: ANALYTICS_KEY in .env but not .env.example
      Fix: Add to .env.example (with empty value)
   ```

## Security

- **Never output actual secret values** — mask as `sk-****...abc`
- Check if `.env` is tracked by git — this is the #1 security risk
- Flag production credentials that appear to be in a development `.env`

## Edge Cases

- **No .env file**: Check cwd; suggest `cp .env.example .env`
- **Multi-line values**: Handle values spanning lines (quoted with `\n`)
- **Variable interpolation**: `${VAR}` references — check if referenced var exists

## Requirements

- No dependencies — text file analysis
- No API keys needed
