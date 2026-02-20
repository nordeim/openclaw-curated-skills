# Security Policy

## Overview

**apiosk-publish** is a skill for publishing APIs on the Apiosk marketplace. It has been designed with security as a top priority.

## Security Level: Benign

This skill is rated **Benign** on the ClawHub security scale.

### What This Means

- ✅ No arbitrary code execution
- ✅ No `curl | bash` patterns
- ✅ All external requests go to verified Apiosk infrastructure
- ✅ No plaintext secrets in scripts
- ✅ No write access outside `~/.apiosk/` directory
- ✅ All dependencies declared (`curl`, `jq`)

## Network Access

This skill communicates **only** with:
- `https://gateway.apiosk.com` — Apiosk gateway API

All communication uses HTTPS exclusively.

## Data Access

- **Reads:** `~/.apiosk/wallet.txt` (your wallet address, same as `apiosk` skill)
- **Writes:** None (skill stores no local data)

## Wallet Security

- Wallet address is read from `~/.apiosk/wallet.txt`
- No private keys are accessed or transmitted
- Wallet address is sent to Apiosk gateway for ownership verification only
- You retain full control of your wallet

## Required Binaries

- `curl` — HTTP requests
- `jq` — JSON parsing

These are standard Unix utilities and are **not** downloaded by this skill.

## API Endpoint Validation

When you register an API:
1. Gateway validates the endpoint URL is HTTPS
2. Performs a health check (HEAD/GET request)
3. Only approves if health check passes
4. Your endpoint URL is stored in the Apiosk database

**Important:** Ensure your API endpoint is secure and doesn't expose sensitive data.

## No Arbitrary Code Execution

- All scripts are simple shell scripts
- No `eval`, `source`, or dynamic code execution
- No external script downloads
- No dependency installations

## Reporting Security Issues

If you discover a security issue:

1. **DO NOT** open a public GitHub issue
2. Email: security@apiosk.com
3. We'll respond within 24 hours
4. Coordinated disclosure after fix

## Updates

This skill may receive security updates. Check the latest version on ClawHub.

---

**Last Updated:** 2026-02-15  
**Version:** 1.0.0
