---
name: hefestoai-auditor
version: "2.1.0"
description: "AI-powered architectural guardian with Socratic Adaptive Constitution. Runs security audits, detects semantic drift, analyzes complexity, and prevents AI-generated code degradation across 17 languages. Governed by formal ethical principles and multi-model awareness."
metadata:
  {
    "openclaw":
      {
        "emoji": "🔨",
        "requires": { "bins": ["hefesto"] },
        "install":
          [
            {
              "id": "pip",
              "kind": "pip",
              "package": "hefesto-ai",
              "bins": ["hefesto"],
              "label": "Install HefestoAI (pip)"
            }
          ]
      }
  }
---

# HefestoAI Auditor Skill v2.0

AI-powered architectural guardian. Not just a code analyzer — a **security and quality governance system** governed by a Socratic Adaptive Constitution.

## What's New in v2.0

- **Constitución Socrática Adaptativa:** Formal ethical framework governing all bot behavior
- **Semantic Drift Detection:** Identifies when AI-generated code subtly alters logical intent
- **Multi-Model Architecture (Active):** Grok, DeepSeek, Claude, and OpenAI integrated as operational sub-agents
- **Enhanced Security Posture:** Explicit security scope definition and continuous audit principle
- **Optimized Token Management:** Structured outputs and delta-based communication

---

## Quick Start

### Run a full audit

```bash
source /home/user/.hefesto_env 2>/dev/null
hefesto analyze /absolute/path/to/project --severity HIGH --exclude venv,node_modules,.git
```

### Severity levels

```bash
hefesto analyze /path --severity CRITICAL   # Critical only
hefesto analyze /path --severity HIGH        # High + Critical
hefesto analyze /path --severity MEDIUM      # Medium + High + Critical
hefesto analyze /path --severity LOW         # Everything
```

### Output formats

```bash
hefesto analyze /path --output text                          # Terminal (default)
hefesto analyze /path --output json                          # Structured JSON
hefesto analyze /path --output html --save-html report.html  # HTML report
hefesto analyze /path --quiet                                # Summary only
```

### Status and version

```bash
hefesto status
hefesto --version
```

---

## Socratic Adaptive Constitution (Summary)

This skill operates under a formal constitution with 6 chapters:

1. **Fundamental Principles:** Truthfulness, human leadership, continuous audit, beneficence, accountability, privacy
2. **Socratic Adaptive Method (MSA):** 4-phase workflow — Diagnose, Decide (max 2 questions), Execute (minimal impact), Verify
3. **Multi-Model Architecture:** Current Gemini + future DeepSeek/Claude Code/Grok roles
4. **Security:** Shift-left code/config vulnerabilities (not runtime/network)
5. **Operational Rules:** Anti-spam, anti-hallucination, structured responses
6. **Capabilities:** Audit protocol, social publishing, dev tools

Full constitution: see workspace `CLAUDE.md`

---

## What It Detects

### Security Vulnerabilities
- SQL injection and command injection
- Hardcoded secrets (API keys, passwords, tokens)
- Insecure configurations (Dockerfiles, Terraform, YAML)
- Path traversal and XSS risks

### Semantic Drift (AI Code Integrity)
- Logic alterations that preserve syntax but change intent
- Architectural degradation from AI-generated code
- Hidden duplicates and inconsistencies in monorepos

### Code Quality
- Cyclomatic complexity >10 (HIGH) or >20 (CRITICAL)
- Deep nesting (>4 levels)
- Long functions (>50 lines)
- Code smells and anti-patterns

### DevOps Issues
- Dockerfile: missing USER, no HEALTHCHECK, running as root
- Shell: missing `set -euo pipefail`, unquoted variables
- Terraform: missing tags, hardcoded values

### What It Does NOT Detect
- Runtime network attacks (DDoS, port scanning)
- Active intrusions (rootkits, privilege escalation)
- Network traffic monitoring
- For these, use SIEM/IDS/IPS or GCP Security Command Center

---

## Supported Languages (17)

**Code:** Python, TypeScript, JavaScript, Java, Go, Rust, C#
**DevOps/Config:** Dockerfile, Jenkins/Groovy, JSON, Makefile, PowerShell, Shell, SQL, Terraform, TOML, YAML

---

## Interpreting Results

```
📄 <file>:<line>:<col>
├─ Issue: <description>
├─ Function: <name>
├─ Type: <issue_type>
├─ Severity: CRITICAL | HIGH | MEDIUM | LOW
└─ Suggestion: <fix recommendation>
```

### Issue Types
| Type | Severity | Action |
|------|----------|--------|
| `VERY_HIGH_COMPLEXITY` | CRITICAL | Fix immediately |
| `HIGH_COMPLEXITY` | HIGH | Fix in current sprint |
| `DEEP_NESTING` | HIGH | Refactor nesting levels |
| `SQL_INJECTION_RISK` | HIGH | Parameterize queries |
| `HARDCODED_SECRET` | CRITICAL | Remove and rotate |
| `LONG_FUNCTION` | MEDIUM | Split function |

---

## Pro Tips

```bash
# CI/CD gate - fail build on issues
hefesto analyze /path --fail-on HIGH --exclude venv

# Pre-push hook
hefesto install-hook

# Limit output
hefesto analyze /path --max-issues 10

# Exclude specific types
hefesto analyze /path --exclude-types VERY_HIGH_COMPLEXITY,LONG_FUNCTION
```

### Wrapper Script (Recommended)

```bash
#!/bin/bash
source /home/user/.hefesto_env 2>/dev/null
exec hefesto "$@"
```

---

## Multi-Model Architecture (Active)

HefestoAI Auditor is designed to work within a 4-model system:

| Model | Role | Status |
|-------|------|--------|
| **Gemini 2.5 Flash** | Central brain + ethical filter | Active |
| **DeepSeek** | Logical architect (formalization) | Active |
| **Claude Code** | Senior coder (generation + refactoring) | Active |
| **Grok** | Strategist + social sensor (X/Twitter) | Active |
| **OpenAI GPT** | Complementary analyst | Active |

HefestoAI acts as the **external audit layer** — reviewing output from all models for security and quality compliance.

### Multi-Model Commands

```bash
# Query individual models
source ~/.hefesto_env 2>/dev/null
python3 ~/hefesto_tools/multi_model/query_model.py --model grok "Analyze trends"
python3 ~/hefesto_tools/multi_model/query_model.py --model deepseek "Formalize this algorithm"
python3 ~/hefesto_tools/multi_model/query_model.py --model claude "Review this code"

# Run constitutional pipelines
python3 ~/hefesto_tools/multi_model/orchestrate.py --task code-review --input "def foo(): ..."
python3 ~/hefesto_tools/multi_model/orchestrate.py --task full-cycle --input "Design a webhook validator"
python3 ~/hefesto_tools/multi_model/orchestrate.py --task strategy --input "Position vs Devin"
```

---

## Licensing Tiers

| Tier | Price | Key Features |
|------|-------|-------------|
| **FREE** | $0/mo | Static analysis, 17 languages, pre-push hooks |
| **PRO** | $8/mo | ML semantic analysis, REST API, BigQuery, custom rules |
| **OMEGA** | $19/mo | IRIS monitoring, auto-correlation, real-time alerts, team dashboard |

All paid tiers include a **14-day free trial**.

- **PRO**: https://buy.stripe.com/4gM00i6jE6gV3zE4HseAg0b
- **OMEGA**: https://buy.stripe.com/14A9AS23o20Fgmqb5QeAg0c

```bash
export HEFESTO_LICENSE_KEY=<your-key>
hefesto status  # verify tier
```

---

## Important Rules

- **ALWAYS** use absolute paths, never `.` or relative paths
- **ALWAYS** load environment first: `source /home/user/.hefesto_env`
- **ALWAYS** exclude: `--exclude venv,node_modules,.git`
- **REPORT ONLY** what hefesto returns — never invent or add issues

---

## About

Created by **Narapa LLC** (Miami, FL) — Arturo Velasquez (@artvepa)
GitHub: https://github.com/artvepa80/Agents-Hefesto
Support: support@narapallc.com

> "El código limpio es código seguro" 🛡️
