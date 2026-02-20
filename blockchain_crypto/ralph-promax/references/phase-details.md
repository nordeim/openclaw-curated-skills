# Promax Phase Details (10,000 Iterations)

## Phase 1: Reconnaissance & Attack Surface (1-500)

### 1.1 Platform Sync (1-100)
- Auto-detect stack, infra, CI/CD (deterministic order)
- Git sync verification (local vs remote vs deployed)
- Critical file hash comparison (manifests, lockfiles, Dockerfiles, .env, entrypoints)
- Environment drift detection, symlink verification, hidden file detection

### 1.2 Attack Surface (101-250)
- Endpoint enumeration: public, authenticated, admin, webhook, SSE/WebSocket, file upload/download
- Rate limiting coverage mapping
- Exposed ports audit, Swagger/ReDoc exposure, debug endpoints
- Health check info leakage, static file serving paths

### 1.3 Hidden Systems (251-375)
- Host deep scan: `ps aux`, `ss -tulpn`, `lsof -i`, cron, systemd units
- Docker: networks, volumes, stopped containers, images, disk usage
- SUID/SGID binaries, orphaned files, SSH keys, bash history
- `/etc/passwd`, `/etc/sudoers`, recent logins, failed login attempts

### 1.4 Environment & Docs (376-500)
- .env vs .env.example drift (every variable checked)
- Docker environment: build args, secrets, ConfigMaps, runtime injection
- Documentation vs reality: verify every claim in README/CLAUDE.md/docs
- Attack surface scoring

## Phase 2: OWASP Top 10 Deep Dive (501-1,200)

| Iter | OWASP | Focus |
|------|-------|-------|
| 501-620 | A01 | Broken Access Control (IDOR, CORS, path traversal, function-level) |
| 621-740 | A02 | Cryptographic Failures (algorithms, key mgmt, TLS) |
| 741-900 | A03 | Injection (SQL, Command, XSS, Template, Log) |
| 901-960 | A04 | Insecure Design (missing controls, business logic) |
| 961-1020 | A05 | Security Misconfiguration (debug, errors, headers) |
| 1021-1080 | A06 | Vulnerable Components (dependency audit) |
| 1081-1140 | A07 | Auth Failures (credential stuffing, sessions) |
| 1141-1170 | A08 | Integrity Failures (deserialization, CI/CD) |
| 1171-1185 | A09 | Logging Failures |
| 1186-1200 | A10 | SSRF |

See `attack-patterns.md` for payloads per category.

## Phase 3: Authentication & Secrets (1,201-2,000)

**Pre-check:** Library vs custom crypto.

- **1,201-1,500:** Secret detection — hardcoded keys (regex patterns), git history (`gitleaks`), Docker image layers
- **1,501-1,700:** JWT — algorithm verification, claims audit, storage audit, revocation
- **1,701-1,850:** OAuth 2.0 — PKCE, redirect URI, state, token exchange
- **1,851-1,950:** Admin auth — brute force protection, timing-safe comparison, lockout
- **1,951-2,000:** Secrets management — env var audit, rotation plans, startup validation

## Phase 4: Infrastructure & Network (2,001-2,800)

- **2,001-2,300:** Container security — Dockerfile audit (per-instruction), compose, runtime, image supply chain
- **2,301-2,500:** Network — port exposure, Docker network isolation, firewall rules (UFW/iptables)
- **2,501-2,600:** TLS/SSL — cert validity, chain, ciphers, HSTS, OCSP stapling
- **2,601-2,700:** SSH — sshd_config audit, key management (ED25519/RSA-4096)
- **2,701-2,800:** Database — encrypted connections, minimal privileges, backups, cache/queue security

## Phase 5: Code Quality & Business Logic (2,801-3,600)

**Pre-check:** DB constraints before flagging race conditions.

- **2,801-3,000:** Race conditions — TOCTOU, concurrent access, locking strategies
- **3,001-3,200:** Business logic — workflow bypass, state manipulation, rate limit bypass techniques
- **3,201-3,400:** Error handling — exception security, fail-safe defaults, no info leakage
- **3,401-3,550:** Resource management — connection leaks, memory security, streaming
- **3,551-3,600:** DoS resilience — request limits, ReDoS, JSON bombs, complexity attacks

## Phase 6: Supply Chain & Dependencies (3,601-4,400)

- **3,601-4,000:** Dependency audit — `pip-audit`, `safety`, `npm audit`, per-package analysis (CVE, maintenance, typosquat risk)
- **4,001-4,200:** Third-party API security — keys, webhook signatures, LLM provider audit
- **4,201-4,400:** CI/CD — action pinning (SHA not @latest), secrets management, deployment security

## Phase 7: API Security Deep Dive (4,401-5,200)

- **4,401-4,600:** Auth per endpoint — JWT validation, bypass testing
- **4,601-4,800:** Authorization — BOLA/BFLA testing for every resource/admin endpoint
- **4,801-5,000:** Input validation — per-parameter audit, mass assignment protection
- **5,001-5,100:** Rate limiting matrix — per-endpoint IP/user/burst limits
- **5,101-5,200:** Data exposure — response field audit, sensitive data leakage

## Phase 8: Container & Docker Security (5,201-6,000)

- **5,201-5,500:** Dockerfile deep audit — per-instruction, multi-stage, non-root
- **5,501-5,700:** Docker Compose — resource limits, capabilities, health checks
- **5,701-5,900:** Runtime — seccomp, AppArmor, read-only fs
- **5,901-6,000:** Image supply chain — digests, signatures, Trivy/Grype scanning

## Phase 9: CI/CD Pipeline Security (6,001-6,800)

- **6,001-6,400:** Workflow audit — action pinning, permissions, secret masking
- **6,401-6,600:** CI/CD secrets — scope, rotation, fork PR access
- **6,601-6,800:** Supply chain in CI — lockfile verification, dependency review

## Phase 10: Performance & DoS (6,801-7,600)

- **6,801-7,100:** Database — N+1 queries, missing indexes, unbounded queries
- **7,101-7,400:** Memory — streaming, pagination, connection pools
- **7,401-7,600:** DoS vectors — slow loris, ReDoS, JSON bombs, connection exhaustion

## Phase 11: AI/RAG System Security (7,601-8,400)

- **7,601-7,900:** Prompt injection — instruction override, role hijacking, jailbreak
- **7,901-8,200:** RAG security — document sanitization, cross-user leakage, context overflow
- **8,201-8,400:** LLM output — sanitization, code execution prevention, cost monitoring

## Phase 12: Compliance & Privacy (8,401-9,000)

- **8,401-8,600:** GDPR — data inventory, consent, rights (access, deletion, portability)
- **8,601-8,800:** Data retention — periods, automatic deletion, backup alignment
- **8,801-9,000:** Security docs — incident response plan, runbooks, escalation paths

## Phase 13: Cross-Cutting Attack Chains (9,001-9,400)

- Multi-stage scenarios using findings from all previous phases
- Privilege escalation paths (user→admin, container→host, network→admin, API→DB)
- Chained vulnerability assessment

## Phase 14: Penetration Test Simulation (9,401-9,700)

- Automated: SQLi, XSS, auth bypass, IDOR, CSRF, path traversal, command injection, SSRF, rate limit, DoS
- Manual: authentication bypass, authorization bypass, input validation, business logic

## Phase 15: Final Verification (9,701-9,900)

- Critical/HIGH re-verification (fix implemented? verified? regression?)
- Configuration verification (production configs, secrets, debug, headers, rate limits)
- Defense verification (attacks blocked, proper status codes, events logged, alerts)

## Phase 16: Report & Summary (9,901-10,000)

- Executive summary (score/100, risk level, top risks, immediate actions)
- Security scorecard (13 categories, 0-100 each)
- Memory ingest (all findings, fixes, decisions, recommendations)
- Post-audit action plan: immediate → short-term → medium-term → long-term → continuous monitoring
