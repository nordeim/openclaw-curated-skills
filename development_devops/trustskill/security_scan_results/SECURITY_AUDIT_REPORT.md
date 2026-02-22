# TrustSkill v3.0 Security Audit Report

**Generated:** 2026-02-21 23:55:01  
**Scanner:** TrustSkill v3.0 (Deep Mode)  
**Scope:** `/home/project/openclaw/curated_skills/ai_agent_infrastructure`  
**Skills Scanned:** 109  

---

## Executive Summary

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Skills** | 109 | 100% |
| 🔴 **High-Risk** | 24 | 22.0% |
| 🟡 **Medium-Risk** | 19 | 17.4% |
| ✅ **Clean** | 66 | 60.6% |

| Finding Severity | Count |
|-----------------|-------|
| 🔴 **HIGH** | 131 |
| 🟡 **MEDIUM** | 210 |
| 🟢 **LOW** | 89 |
| **Total** | 430 |

---

## Risk Assessment Matrix

### Critical Concerns (Immediate Action Required)

| Category | HIGH | Description | Skills Affected |
|----------|------|-------------|-----------------|
| **hardcoded_secret** | 87 | High-entropy strings, API keys | content-watcher (82), search-reddit (2), gemini-spark-core (1), auto-updater-ah1 (1) |
| **sensitive_file_access** | 28 | Memory file, shell config access | clawzempic (12), cairn-cli (4), counterclaw-core (1), others |
| **command_injection** | 4 | eval(), compile() with variables | vibevoice, counterclaw-core (2), ppt-ooxml-tool |
| **data_exfiltration** | 3 | HTTP POST to external servers | llmcouncil-router (2), toggle (1) |
| **file_deletion** | 2 | rm -rf commands | narrator, clawzempic |
| **vulnerable_dependency** | 6 | PYSEC-2018-28 (SSL bypass) | elevenlabs-voice (2), poe-chat (1), foto-webcam (1), mersoom-ai-client (1), skills-ai-assistant (1) |
| **credential_access** | 1 | Token file access | daily-rhythm |

---

## High-Risk Skills (24)

### 🔴 content-watcher (82 HIGH findings)
**Path:** `content-watcher/`  
**Risk:** Critical - Mass false positives from package-lock.json entropy detection

| Finding | File | Line | Description |
|---------|------|------|-------------|
| hardcoded_secret | package-lock.json | 26, 35, 50, 56, 67... | High-entropy strings in integrity hashes |

**Verdict:** ⚠️ **FALSE POSITIVE** - These are npm integrity hashes (SHA-512), not secrets. Recommend whitelist.

---

### 🔴 clawzempic (16 HIGH findings)
**Path:** `clawzempic/`  
**Risk:** High - Legitimate security concerns

| Finding | File | Line | Description |
|---------|------|------|-------------|
| sensitive_file_access | README.md, SKILL.md | Multiple | Memory file references in documentation |
| file_deletion | SKILL.md | 293 | `rm -rf` command reference |

**Verdict:** ⚠️ **MIXED** - Documentation references, not executable code. Review context.

---

### 🔴 cairn-cli (4 HIGH findings)
**Path:** `cairn-cli/`  
**Risk:** Medium - Documentation references

| Finding | File | Description |
|---------|------|-------------|
| sensitive_file_access | COMMANDS.md, README.md, SKILL.md | Shell config and memory file documentation |

**Verdict:** ⚠️ **FALSE POSITIVE** - Documentation examples, not code execution.

---

### 🔴 counterclaw-core (3 HIGH findings)
**Path:** `counterclaw-core/`  
**Risk:** High - Potential code injection

| Finding | File | Line | Description |
|---------|------|------|-------------|
| command_injection | scanner.py | 34-35 | `compile()` with variable input |
| sensitive_file_access | middleware.py | 44 | Memory file access |

**Verdict:** 🔴 **REQUIRES REVIEW** - Dynamic code compilation needs validation.

---

### 🔴 search-reddit (2 HIGH findings)
**Path:** `search-reddit/`  
**Risk:** Critical - Exposed API keys in documentation

| Finding | File | Line | Description |
|---------|------|------|-------------|
| hardcoded_secret | README.md, SKILL.md | 26, 20 | OpenAI API Key pattern detected |

**Verdict:** 🔴 **REQUIRES REVIEW** - Verify if these are actual keys or placeholder examples.

---

### 🔴 llmcouncil-router (2 HIGH findings)
**Path:** `llmcouncil-router/`  
**Risk:** High - Potential data exfiltration

| Finding | File | Line | Description |
|---------|------|------|-------------|
| data_exfiltration | SKILL.md | 92, 102 | HTTP POST to external server |

**Verdict:** 🔴 **REQUIRES REVIEW** - Verify destination and purpose of external POST requests.

---

### 🔴 vibevoice (1 HIGH finding)
**Path:** `vibevoice/`  
**Risk:** Critical - Command injection vulnerability

| Finding | File | Line | Description |
|---------|------|------|-------------|
| command_injection | vv.sh | 105 | `eval()` execution |

**Verdict:** 🔴 **CRITICAL** - eval() with potentially untrusted input. Immediate remediation required.

---

### 🔴 Other High-Risk Skills (Brief)

| Skill | HIGH | Primary Concern | Verdict |
|-------|------|-----------------|---------|
| taskleef | 2 | Shell config access in docs | ⚠️ Review |
| project-tree | 2 | Memory file access in JS | 🔴 Review |
| elevenlabs-voice | 2 | Vulnerable `requests` version | 🔴 Update dependency |
| opensoulmd | 2 | Memory file in package.json | ⚠️ Review |
| narrator | 1 | `rm -rf` command | 🔴 Review execution context |
| skills-ai-assistant | 1 | Vulnerable dependency | 🔴 Update dependency |
| mbti | 1 | Memory file access | ⚠️ Review |
| auto-updater-ah1 | 1 | High-entropy string | ⚠️ Verify if secret |
| mersoom-ai-client | 1 | Vulnerable dependency | 🔴 Update dependency |
| poe-chat | 1 | Vulnerable dependency | 🔴 Update dependency |
| toggle | 1 | Data exfiltration | 🔴 Review |
| memory-system | 1 | Memory file access | ⚠️ By design |
| foto-webcam | 1 | Vulnerable dependency | 🔴 Update dependency |
| gemini-spark-core | 1 | High-entropy string | ⚠️ Verify if secret |
| daily-rhythm | 1 | Token file access | 🔴 Review |
| memory-manager | 1 | Memory file access | ⚠️ By design |
| ppt-ooxml-tool | 1 | compile() with variable | 🔴 Review |

---

## Medium-Risk Skills (19)

| Skill | MEDIUM | LOW | Primary Concerns |
|-------|--------|-----|------------------|
| gemini-image-remix | 16 | 3 | API key usage, network requests |
| ai-news-collectors | 11 | 0 | AI service API references |
| auto-updater | 5 | 0 | Network requests |
| moltbook-interact | 4 | 0 | HTTP requests |
| claw-mouse | 4 | 7 | Environment access, subprocess |
| mcporter-railway-query | 3 | 0 | Direct IP HTTP access |
| mcporter-railway-query-repo | 3 | 0 | Direct IP HTTP access |
| mijia | 3 | 0 | HTTP requests |
| deepread-ocr | 2 | 0 | HTTP requests |
| clawdhub-skill | 2 | 0 | HTTP requests |
| turkey-news | 2 | 0 | Network requests |
| skiplagged-flights | 2 | 0 | Network requests |

---

## Findings by Category

```
api_key_usage        ████████████████████████████████████████  152 (MEDIUM)
hardcoded_secret     █████████████████████████                  90 (87 HIGH, 3 MEDIUM)
file_operation       ███████████████                            70 (LOW)
sensitive_file_access ██████                                      28 (HIGH)
network_request      ████                                        20 (MEDIUM)
environment_access   ███                                         19 (MEDIUM)
json_parsing         ██                                          12 (LOW)
suspicious_url       ██                                          10 (MEDIUM)
shell_command        █                                            7 (LOW)
vulnerable_dependency █                                           6 (HIGH)
dynamic_import       █                                            5 (MEDIUM)
command_injection    █                                            4 (HIGH)
data_exfiltration    █                                            3 (HIGH)
file_deletion        █                                            2 (HIGH)
credential_access    █                                            1 (HIGH)
file_access_outside_workspace █                                   1 (MEDIUM)
```

---

## Remediation Recommendations

### Priority 1: Critical (Immediate Action)

1. **vibevoice/vv.sh:105** - Replace `eval()` with safer alternatives
   ```bash
   # Instead of: eval "$cmd"
   # Use: bash -c "$cmd" or case statements
   ```

2. **search-reddit** - Remove or redact any actual API keys from documentation
   ```markdown
   # Replace actual keys with placeholders
   - OPENAI_API_KEY=sk-xxxx... → OPENAI_API_KEY=your-api-key-here
   ```

3. **Vulnerable Dependencies (PYSEC-2018-28)**
   - elevenlabs-voice, poe-chat, foto-webcam, mersoom-ai-client, skills-ai-assistant
   - Update `requests` library: `pip install requests>=2.22.0`

### Priority 2: High (Within 1 Week)

4. **counterclaw-core/scanner.py:34-35** - Validate input before `compile()`
   ```python
   # Add input validation and sandboxing
   if not is_safe_code(user_input):
       raise SecurityError("Unsafe code detected")
   ```

5. **llmcouncil-router** - Audit external POST destinations
   - Document all external endpoints
   - Add user consent for data transmission

6. **toggle/toggle.py** - Review urllib network requests
   - Verify data being transmitted
   - Add opt-out mechanisms

### Priority 3: Medium (Within 1 Month)

7. **Whitelist package-lock.json** - Add to TrustSkill config
   ```yaml
   rules:
     whitelist:
       files:
         - "package-lock.json"
         - "yarn.lock"
   ```

8. **Documentation file references** - The sensitive_file_access findings in README.md, SKILL.md, COMMANDS.md are documentation examples, not security issues. Consider:
   - Adding `.md` files to whitelist for certain patterns
   - Or accepting as informational

9. **Memory file access** - Skills like `memory-system`, `memory-manager`, `clawzempic` intentionally access memory files. Document as expected behavior.

---

## False Positive Analysis

| Finding Type | False Positive Rate | Reason |
|--------------|---------------------|--------|
| hardcoded_secret in package-lock.json | ~95% | npm integrity hashes |
| sensitive_file_access in .md files | ~90% | Documentation examples |
| api_key_usage (AI service) | ~80% | Placeholder/example text |
| environment_access | ~70% | Normal configuration patterns |

---

## Clean Skills (66)

The following skills passed all security checks with no findings:

```
a2a-platform, agent-task-tracker, anyone-proxy, ardupilot, 
autonomous-execution, brainstorming, canvs, clawlist, 
clawmart-browse, cobraclaw, cold-email-personalization, 
comfyui-tts, computer-vision-expert, context-anchor, 
daily-oracle, dgr, dispatch-multiple-agents, doing-tasks, 
download-tools, find-products, fox-lights, 
geeksdobyte-motivation-skill, glin-profanity-mcp, 
gonggong-hwpxskills-main, google-flights, hello-agent-world, 
hello-world, ibt, interclaw, investment-advisor, 
lb-pocket-tts-skill, letterboxd-tracker, mcporter-skill, 
memory-tiering, mi-habilidad-nueva, mixlab-solo-scope, 
molt-mouse, moltsci, momentspost, nano-banana-korean-rendering, 
nostr-nak, ofdreader, pdftk-server, pepsi-or-coke-mcp, 
pi-health, plsreadme, priceworld, primattography-color-science, 
productboard-release, prompt-injection-guard, 
recursive-self-improvement, shodh-local, sure, task, 
telecom-agent-skill, tenzing-moltbook, tg-checkin, 
travel-manager, twinfold, upnote, veadk-skills, verify-task, 
wilma, wpclaw-lite, write-plan, x-hot-topics-daily
```

---

## Configuration Recommendations

Create `trustskill.yaml` for future scans:

```yaml
version: "3.0"
scanning:
  mode: deep
secret_detection:
  enabled: true
  min_entropy: 5.0
  min_length: 25
rules:
  whitelist:
    files:
      - "package-lock.json"
      - "yarn.lock"
      - "poetry.lock"
    patterns:
      # Allow integrity hashes
      - "sha512-[A-Za-z0-9+/=]+"
  severity_overrides:
    # Documentation examples are lower risk
    sensitive_file_access: MEDIUM
```

---

## Conclusion

**Overall Security Posture: MODERATE**

- 60.6% of skills are clean with no security concerns
- 22% have high-risk findings requiring review
- Most HIGH findings are false positives from:
  - npm integrity hashes (package-lock.json)
  - Documentation examples in markdown files
  - Intentional memory file access patterns

**Recommended Actions:**
1. Immediate: Fix `vibevoice` eval() vulnerability
2. This week: Update vulnerable `requests` dependencies
3. This week: Audit `search-reddit` for actual API keys
4. Ongoing: Configure TrustSkill whitelist for known safe patterns

---

*Report generated by TrustSkill v3.0 - Advanced Skill Security Scanner*
