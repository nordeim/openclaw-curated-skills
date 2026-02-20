---
name: ralph-promax
description: "Maximum paranoia security audit with 10,000 iterations (~2-5 days) using 8 expert personas. Use when user says 'ralph promax', 'maximum security audit', 'full paranoia audit', 'exhaustive security review', 'security incident deep investigation', or 'maximum paranoia mode'. Covers OWASP, supply chain, API, containers, CI/CD, performance, AI/RAG, compliance."
metadata: { "openclaw": { "emoji": "☠️" }, "author": "dorukardahan", "version": "2.0.0", "category": "security", "tags": ["security", "audit", "exhaustive", "paranoia", "owasp", "supply-chain", "compliance"] }
---

# Ralph Promax — 10,000 Iterations (~2-5 days)

The most exhaustive security audit. 8 expert personas, 16 phases, leave nothing unexamined.

> **Host Safety Warning:** Promax includes system-level reconnaissance (process listing, port scanning, file permissions). Runs with YOUR user's permissions. Do NOT run on production servers without understanding implications.

For detailed resources loaded as needed:
- Severity & triage: `{baseDir}/references/severity-guide.md`
- All 8 expert personas: `{baseDir}/references/personas.md`
- OWASP payloads & checklists: `{baseDir}/references/attack-patterns.md`
- Full phase iteration breakdown: `{baseDir}/references/phase-details.md`

## Instructions

### Execution Engine

YOU MUST follow this loop for EVERY iteration — NO EXCEPTIONS:

1. **STATE**: Read current iteration (start: 1)
2. **PHASE**: Determine phase from iteration number
3. **MIND**: Activate appropriate expert persona
4. **DEPTH**: Apply maximum thoroughness
5. **ACTION**: Perform ONE check — DEEPLY and THOROUGHLY
6. **VERIFY**: Before FAIL — read actual code, check libraries, DB constraints, environment. If inconclusive: `NEEDS_REVIEW`.
7. **EXPLOIT**: Attempt to exploit if vulnerability found
8. **REPORT**: Output iteration result with PoC
9. **SAVE**: Every 100 iterations, update `.ralph-report.md`
10. **INCREMENT**: iteration + 1
11. **CONTINUE**: IF iteration <= 10000 GOTO Step 1
12. **FINAL**: Generate comprehensive report

**Critical rules:**
- ONE check per iteration — DEEP not WIDE
- ALWAYS show `[PROMAX-X/10000]`
- NEVER skip iterations
- CRITICAL findings: STOP and demand immediate attention
- Red Team question for EVERY check
- Apply ALL 8 Minds to complex findings

### Per-Iteration Output

```
╔════════════════════════════════════════════════════════════════════════╗
║ [PROMAX-{N}/10000] Phase {P}: {phase_name}                            ║
║ Mind: {active_expert_persona}                                          ║
║ Depth Level: ████████████ MAXIMUM                                      ║
╠════════════════════════════════════════════════════════════════════════╣
║ Check: {specific_check}                                                ║
║ Target: {file:line / endpoint / system / dependency}                   ║
╠════════════════════════════════════════════════════════════════════════╣
║ Red Team Question: "{attack scenario being tested}"                    ║
╠════════════════════════════════════════════════════════════════════════╣
║ Result: {PASS|FAIL|WARN|SUSPICIOUS|N/A}                                ║
║ Confidence: {VERIFIED|LIKELY|PATTERN_MATCH|NEEDS_REVIEW}               ║
║ Severity: {CRITICAL|HIGH|MEDIUM|LOW|INFO}                              ║
║ CVSS: {score} | Exploitability: {TRIVIAL|MODERATE|DIFFICULT}           ║
╠════════════════════════════════════════════════════════════════════════╣
║ Finding: {detailed description}                                        ║
║ Attack Vector: {how an attacker would exploit}                         ║
║ Proof of Concept: {actual exploit code/steps or "N/A"}                 ║
║ Blast Radius: {what gets compromised}                                  ║
║ Fix: {specific remediation with code}                                  ║
╠════════════════════════════════════════════════════════════════════════╣
║ Progress: [████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░] {N/100}%          ║
║ Phase: {current}/{16} | ETA: ~{days}d {hours}h                          ║
╚════════════════════════════════════════════════════════════════════════╝
```

### The Eight Minds

| Phase | Expert Mind |
|-------|-------------|
| 1 | Cybersecurity Veteran + CI/CD Saboteur |
| 2 | Code Auditor (Pentester) |
| 3 | Cybersecurity Veteran |
| 4 | Container Security Expert |
| 5 | Code Auditor |
| 6 | Dependency Hunter |
| 7 | API Security Specialist |
| 8 | Container Security Expert |
| 9 | CI/CD Saboteur |
| 10 | Performance Engineer |
| 11 | RAG System Architect |
| 12 | Cybersecurity Veteran |
| 13-16 | All 8 Minds |

### Core Philosophy

1. DEFENSE IN DEPTH — one control = zero controls
2. FAIL SECURE — when uncertain, DENY
3. LEAST PRIVILEGE — every permission is an attack vector
4. TRUST NOTHING — verify EVERYTHING
5. ASSUME BREACH — they're already inside
6. THOROUGHNESS IS SURVIVAL

### Phase Structure (10,000 Iterations)

| Phase | Iterations | Focus Area |
|-------|------------|------------|
| 1 | 1-500 | Reconnaissance & Attack Surface |
| 2 | 501-1,200 | OWASP Top 10 Deep Dive |
| 3 | 1,201-2,000 | Authentication & Secrets |
| 4 | 2,001-2,800 | Infrastructure & Network |
| 5 | 2,801-3,600 | Code Quality & Business Logic |
| 6 | 3,601-4,400 | Supply Chain & Dependencies |
| 7 | 4,401-5,200 | API Security Deep Dive |
| 8 | 5,201-6,000 | Container & Docker Security |
| 9 | 6,001-6,800 | CI/CD Pipeline Security |
| 10 | 6,801-7,600 | Performance & DoS Resilience |
| 11 | 7,601-8,400 | AI/RAG System Security |
| 12 | 8,401-9,000 | Compliance & Privacy |
| 13 | 9,001-9,400 | Cross-Cutting Attack Chains |
| 14 | 9,401-9,700 | Penetration Test Simulation |
| 15 | 9,701-9,900 | Final Verification |
| 16 | 9,901-10,000 | Report & Summary |

For detailed per-phase iteration breakdowns, checklists, and attack payloads, consult `{baseDir}/references/phase-details.md` and `{baseDir}/references/attack-patterns.md`.

### Auto-Detect (Iteration 1)

1. `git rev-parse --show-toplevel`, `git remote -v`
2. Stack: `package.json`, `pyproject.toml`, `requirements.txt`, `go.mod`, `Cargo.toml`, `pom.xml`, `build.gradle`, `composer.json`
3. Infra: `Dockerfile`, `docker-compose.yml`, k8s, terraform, serverless
4. Services: enumerate containers/k8s services
5. CI/CD: `.github/workflows`, `.gitlab-ci.yml`, `.circleci`
6. Production URL: env/config/docs/ingress
7. Deployment host: SSH config, deploy scripts

### Report File

On start: rename existing report. Auto-save every 100 iterations.

### Parameters

| Param | Default | Options |
|-------|---------|---------|
| `--iterations` | 10000 | 1-20000 |
| `--focus` | all | recon, owasp, auth, infra, code, supply-chain, api, docker, cicd, perf, rag, compliance, all |
| `--phase` | all | 1-16 |
| `--paranoia` | maximum | standard, high, maximum |
| `--resume` | — | Continue from checkpoint |

### Context Limit Protocol

1. IMMEDIATELY checkpoint to report file
2. Output: `AUDIT CHECKPOINT at iteration {N}. Resume with: /ralph-promax --resume`
3. Include: findings summary, next phase
4. Wait for new session

### When to Use

- Security incident investigation
- Compliance audit preparation
- Maximum paranoia mode
- After `/ralph-ultra` finds concerning patterns
