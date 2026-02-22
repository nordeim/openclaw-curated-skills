# Security Scan Report - Deep Analysis

**Generated:** 2026-02-22T07:38:03.156991

---

## Executive Summary

| Metric | Value |
|--------|-------|
| Skills Scanned | 49 |
| Total Files Analyzed | 220 |
| Total Findings | 255 |

### Severity Distribution

| Severity | Count |
|----------|-------|
| 🔴 CRITICAL | 0 |
| 🟠 HIGH | 104 |
| 🟡 MEDIUM | 95 |
| 🟢 LOW | 56 |
| ℹ️ INFO | 0 |

---

## Skills by Risk Level

### 🔴 Critical Risk (9 skills)

- `aliyun-oss-upload`
- `barkpush`
- `bring-shopping-list`
- `enzoldhazam`
- `imap-email`
- `sarvam`
- `variflight-aviation`
- `x-trends`
- `zotero-sholar`

### 🟠 High Risk (0 skills)


### 🟡 Medium Risk (7 skills)

- `banshee-s-last-cry`
- `deepdub-tts`
- `imap-smtp-email`
- `instagram-reels`
- `political-struggle`
- `sparkle-vpn`
- `youtube-shorts`

### 🟢 Low Risk (6 skills)

- `d4-world-boss`
- `localsend`
- `pptx-pdf-font-fix`
- `signal-cli`
- `yoebao-bazi`
- `yoebao-yao`

### ✅ Safe (27 skills)

- `asdasd`
- `bring`
- `case-record-socialwork`
- `cma-email`
- `data-viz`
- `grazy`
- `host-ping-detect`
- `intodns`
- `katok`
- `mfa-word`
- `notectl`
- `pandic-office`
- `printer`
- `probar`
- `say-xiaoai`
- `searxng-local`
- `searxng-metasearch`
- `searxng-self-hosted`
- `tamil-whatsapp`
- `tt`
- `webpage-screenshot`
- `wechat-article-search`
- `whats`
- `whispers-from-the-star-cn`
- `win-mouse-native`
- `winamp`
- `xuezh`

---

## Category Breakdown

| Category | Count | Affected Skills |
|----------|-------|-----------------|
| hardcoded_secret | 92 | bring-shopping-list, imap-email, instagram-reels (+3 more) |
| environment_access | 38 | aliyun-oss-upload, barkpush, bring-shopping-list (+6 more) |
| api_key_usage | 37 | banshee-s-last-cry, deepdub-tts, imap-smtp-email (+6 more) |
| file_operation | 24 | aliyun-oss-upload, barkpush, deepdub-tts (+5 more) |
| json_parsing | 23 | barkpush, instagram-reels, localsend (+3 more) |
| network_request | 13 | barkpush, bring-shopping-list, sarvam (+1 more) |
| data_exfiltration | 9 | barkpush, bring-shopping-list, enzoldhazam (+1 more) |
| shell_command | 9 | d4-world-boss, signal-cli, yoebao-bazi (+1 more) |
| sensitive_file_access | 4 | aliyun-oss-upload, variflight-aviation |
| command_injection | 2 | barkpush |
| file_access_outside_workspace | 1 | barkpush |
| obfuscation | 1 | sarvam |
| vulnerable_dependency | 1 | sarvam |
| suspicious_url | 1 | sparkle-vpn |

---

## Detailed High-Priority Findings

### 🔴 HIGH Severity Issues

- **aliyun-oss-upload** `config.md:53`
  - Category: `sensitive_file_access`
  - Description: Shell config access
  - Confidence: 80.00%

- **aliyun-oss-upload** `config.md:53`
  - Category: `sensitive_file_access`
  - Description: Shell config access
  - Confidence: 80.00%

- **barkpush** `bark_api.py:7`
  - Category: `data_exfiltration`
  - Description: urllib network request
  - Confidence: 80.00%

- **barkpush** `utils.py:12`
  - Category: `command_injection`
  - Description: compile() execution with variable
  - Confidence: 90.00%

- **barkpush** `utils.py:13`
  - Category: `command_injection`
  - Description: compile() execution with variable
  - Confidence: 90.00%

- **barkpush** `architecture.md:185`
  - Category: `data_exfiltration`
  - Description: urllib network request
  - Confidence: 80.00%

- **bring-shopping-list** `SKILL.md:27`
  - Category: `hardcoded_secret`
  - Description: Hardcoded Password
  - Confidence: 85.00%

- **bring-shopping-list** `bring.py:19`
  - Category: `data_exfiltration`
  - Description: HTTP client usage
  - Confidence: 80.00%

- **enzoldhazam** `client.go:27`
  - Category: `data_exfiltration`
  - Description: HTTP client usage
  - Confidence: 80.00%

- **enzoldhazam** `client.go:39`
  - Category: `data_exfiltration`
  - Description: HTTP client usage
  - Confidence: 80.00%

- **imap-email** `package-lock.json:20`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.47)
  - Confidence: 68.32%

- **imap-email** `package-lock.json:33`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.51)
  - Confidence: 68.83%

- **imap-email** `package-lock.json:44`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.37)
  - Confidence: 67.10%

- **imap-email** `package-lock.json:50`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.42)
  - Confidence: 67.81%

- **imap-email** `package-lock.json:59`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.68)
  - Confidence: 71.00%

- **imap-email** `package-lock.json:73`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.44)
  - Confidence: 67.99%

- **imap-email** `package-lock.json:85`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.51)
  - Confidence: 68.83%

- **imap-email** `package-lock.json:100`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.39)
  - Confidence: 67.42%

- **imap-email** `package-lock.json:114`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.36)
  - Confidence: 67.04%

- **imap-email** `package-lock.json:126`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.45)
  - Confidence: 68.19%

- **imap-email** `package-lock.json:135`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.42)
  - Confidence: 67.81%

- **imap-email** `package-lock.json:147`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.56)
  - Confidence: 69.49%

- **imap-email** `package-lock.json:156`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.47)
  - Confidence: 68.43%

- **imap-email** `package-lock.json:172`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.52)
  - Confidence: 68.95%

- **imap-email** `package-lock.json:191`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.43)
  - Confidence: 67.83%

- **imap-email** `package-lock.json:203`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.35)
  - Confidence: 66.86%

- **imap-email** `package-lock.json:215`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.50)
  - Confidence: 68.78%

- **imap-email** `package-lock.json:232`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.36)
  - Confidence: 67.01%

- **imap-email** `package-lock.json:238`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.59)
  - Confidence: 69.85%

- **imap-email** `package-lock.json:244`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.58)
  - Confidence: 69.75%

- **imap-email** `package-lock.json:250`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.53)
  - Confidence: 69.11%

- **imap-email** `package-lock.json:259`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.41)
  - Confidence: 67.63%

- **imap-email** `package-lock.json:265`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.39)
  - Confidence: 67.37%

- **imap-email** `package-lock.json:277`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.52)
  - Confidence: 69.02%

- **imap-email** `package-lock.json:289`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.52)
  - Confidence: 69.00%

- **imap-email** `package-lock.json:295`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.42)
  - Confidence: 67.75%

- **imap-email** `package-lock.json:304`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.55)
  - Confidence: 69.42%

- **imap-email** `package-lock.json:322`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.45)
  - Confidence: 68.14%

- **imap-email** `package-lock.json:338`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.51)
  - Confidence: 68.85%

- **imap-email** `package-lock.json:348`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.53)
  - Confidence: 69.08%

- **imap-email** `package-lock.json:357`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.46)
  - Confidence: 68.26%

- **imap-email** `package-lock.json:370`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.58)
  - Confidence: 69.75%

- **imap-email** `package-lock.json:379`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.51)
  - Confidence: 68.86%

- **imap-email** `package-lock.json:388`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.65)
  - Confidence: 70.64%

- **imap-email** `package-lock.json:397`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.55)
  - Confidence: 69.34%

- **imap-email** `package-lock.json:409`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.41)
  - Confidence: 67.64%

- **imap-email** `package-lock.json:421`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.45)
  - Confidence: 68.11%

- **imap-email** `package-lock.json:427`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.40)
  - Confidence: 67.48%

- **imap-email** `package-lock.json:439`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.37)
  - Confidence: 67.07%

- **imap-email** `package-lock.json:448`
  - Category: `hardcoded_secret`
  - Description: High-entropy string (entropy: 5.44)
  - Confidence: 67.94%

### 🟡 MEDIUM Severity Issues (Top 20)

- **aliyun-oss-upload** `oss-upload.py:21`
  - Category: `environment_access` - Environment variable access

- **banshee-s-last-cry** `ch00_start.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch1a_investigate.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch1b_ambush.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch1c_solo.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch2a_chase.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch2b_suspect.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch2c_attack.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch2d_trap.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch2e_alone.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3a_basement.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3b_death2.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3c_split.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3d_team.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3e_escape.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3f_reveal.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch3g_hero.md:10`
  - Category: `api_key_usage` - AI service API

- **banshee-s-last-cry** `ch4_endings.md:10`
  - Category: `api_key_usage` - AI service API

- **barkpush** `bark_api.py:6`
  - Category: `network_request` - urllib usage

- **barkpush** `bark_api.py:7`
  - Category: `network_request` - urllib usage

---

## Recommendations

1. **Immediate Action Required**: Review skills with HIGH severity findings
2. **Medium Priority**: Investigate MEDIUM severity issues in context
3. **False Positive Review**: Many `hardcoded_secret` findings in `package-lock.json` are likely integrity hashes (safe)
4. **Environment Access**: `dotenv` usage is typically safe for configuration management

---

*Report generated by TrustSkill v3.0*