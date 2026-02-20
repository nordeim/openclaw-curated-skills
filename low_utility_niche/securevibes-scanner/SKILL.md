---
name: securevibes-scanner
description: Run AI-powered application security scans on codebases. Use when asked to scan code for security vulnerabilities, generate threat models, review code for security issues, validate findings, suggest fixes, or verify remediations. Triggers on security scan, threat model, security review, vulnerability assessment, code audit, or AppSec-related requests targeting a project or repository.
env:
  - name: ANTHROPIC_API_KEY
    required: true
    description: Anthropic API key for Claude-powered analysis
  - name: SECUREVIBES_MAX_TURNS
    required: false
    description: Max Claude conversation turns per subagent phase (default 50)
dependencies:
  - name: securevibes
    type: pip
    version: ">=0.3.0"
    url: https://pypi.org/project/securevibes/
    repository: https://github.com/anshumanbh/securevibes
links:
  homepage: https://securevibes.ai
  repository: https://github.com/anshumanbh/securevibes
  pypi: https://pypi.org/project/securevibes/
author: anshumanbh
---

# SecureVibes Scanner

AI-native security platform that detects vulnerabilities using Claude AI. Multi-subagent pipeline: assessment → threat modeling → code review → report generation → optional DAST.

## Prerequisites

1. Install the CLI:
   ```bash
   pip install securevibes
   ```
2. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY=your-key-here
   ```

## Security Notes

- **Always use the `scripts/scan.sh` wrapper** — it validates paths and rejects shell metacharacters before invoking `securevibes`.
- **Never interpolate unsanitized user input into shell commands.** The wrapper uses `realpath` to resolve paths safely and rejects any path containing `;`, `|`, `&`, `$`, backticks, or other metacharacters.
- **Scan targets must be local directories.** Clone remote repos to a known safe location first, then pass the resolved path to the wrapper.
- **DAST scans make network requests** to the `--target-url` you provide. Only use against apps you own or have permission to test.

## Execution Model

**Scans take 10-30 minutes across 4 phases.** Run them as background jobs (cron or subagent), not inline.

### Running a Scan

1. **Clone the target repo** to a local directory
2. **Run the wrapper script:**
   ```bash
   bash scripts/scan.sh /path/to/repo --force --debug
   ```
3. **Results appear in** `/path/to/repo/.securevibes/`

### Background Execution (Recommended)

For OpenClaw users, schedule scans as cron jobs:
- Use `sessionTarget: "isolated"` with `payload.kind: "agentTurn"`
- Set `payload.timeoutSeconds: 2700` (45 minutes) to allow all phases to complete
- Use `delivery.mode: "announce"` to get notified when done

The agentTurn message should instruct the subagent to:
1. `cd` into the repo and `git pull` for latest code
2. Clean previous `.securevibes/` artifacts
3. Run `securevibes scan . --force` via the wrapper script
4. Read and summarize the results from `.securevibes/scan_report.md`

Where to store results, how to diff against previous runs, and notification routing are left to your agent's configuration.

## Commands Reference

### Scan
```bash
securevibes scan <path> [options]
```

| Option | Description |
|--------|-------------|
| `-f, --format` | `markdown` (default), `json`, `text`, `table` |
| `-o, --output` | Custom output path |
| `-s, --severity` | Filter: `critical`, `high`, `medium`, `low` |
| `-m, --model` | Claude model (e.g., `sonnet`, `haiku` for cheaper/faster) |
| `--subagent` | Run one phase only: `assessment`, `threat-modeling`, `code-review`, `report-generator`, `dast` |
| `--resume-from` | Resume from a specific phase onwards |
| `--dast` | Enable dynamic testing (requires `--target-url`) |
| `--target-url` | URL for DAST (e.g., `http://localhost:3000`) |
| `--force` | Skip prompts, overwrite existing artifacts |
| `--quiet` | Minimal output |
| `--debug` | Verbose diagnostics |

### Report
```bash
securevibes report <path>
```
Display a previously saved scan report.

## Mapping Requests to Scan Args

| User Says | Scan Args |
|-----------|-----------|
| "Scan this for security issues" | `--force` |
| "Quick security check" | `-m haiku --force` |
| "Threat model this project" | `--subagent threat-modeling --force` |
| "Just review the code" | `--subagent code-review --force` |
| "Show only critical/high findings" | `-s high --force` |
| "Full audit with DAST" | `--dast --target-url <url> --force` |
| "Output as JSON" | `-f json -o results.json --force` |
| "Resume from code review" | `--resume-from code-review --force` |
| "Show last scan results" | Use `securevibes report <path>` (no cron needed) |

## Subagent Pipeline

Runs sequentially. Each phase builds on the previous:

1. **assessment** → Architecture & attack surface mapping → `.securevibes/SECURITY.md`
2. **threat-modeling** → STRIDE-based threat analysis → `.securevibes/THREAT_MODEL.json`
3. **code-review** → Line-by-line vulnerability detection → `.securevibes/VULNERABILITIES.json`
4. **report-generator** → Consolidated findings report → `.securevibes/scan_report.md`
5. **dast** (optional) → Dynamic validation against running app

## Presenting Results

After a scan completes:
1. Read `.securevibes/scan_report.md` (or `.securevibes/scan_results.json` for structured data)
2. Summarize: total findings by severity (Critical > High > Medium > Low)
3. Highlight top 3 most critical with file locations and remediation
4. Offer next steps: run DAST, fix specific issues, re-scan after changes

## Links

- **Website**: https://securevibes.ai
- **PyPI**: https://pypi.org/project/securevibes/
- **GitHub**: https://github.com/anshumanbh/securevibes
