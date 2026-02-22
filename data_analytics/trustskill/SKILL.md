---
name: trustskill
version: 3.1.0
description: TrustSkill v3.1 - Advanced security scanner for OpenClaw skills with 99% false positive reduction. Detects malicious code, hardcoded secrets, vulnerable dependencies, tainted data flows, backdoors, credential theft, privacy file access, command injection, file system risks, network exfiltration, and sensitive data leaks. Features entropy-based secret detection, OSV vulnerability database integration, taint analysis, smart data flow detection, context-aware documentation scanning, and flexible YAML configuration.
---

# TrustSkill v3.1 - Advanced Skill Security Scanner

A comprehensive security scanner for OpenClaw skills that detects:
- **Malicious code and backdoors**
- **Hardcoded secrets** (API keys, passwords, tokens via entropy analysis)
- **Vulnerable dependencies** (known CVEs via OSV database)
- **Tainted data flows** (user input to dangerous functions)
- **Credential theft** (SSH keys, passwords, API keys)
- **Privacy file access** (Memory files, configs)
- **Command injection** (eval, exec, os.system)
- **Data uploads** (suspicious POST/PUT requests)
- **File system risks** (destructive operations)
- **Network security issues**

## What's New in v3.1

### 🔒 NPM Integrity Hash Whitelist
Automatically recognizes and skips npm/pnpm/yarn integrity hashes (`sha512-xxx`) in lock files, eliminating 99% of false positive HIGH findings from `package-lock.json`, `yarn.lock`, and `pnpm-lock.yaml`.

### 📊 Smart Data Flow Detection
Distinguishes between **data uploads** (HIGH risk) and **data downloads** (MEDIUM risk):
- `requests.post()`, `requests.put()` → `data_upload` (HIGH)
- `urllib.request.urlretrieve()`, `requests.get(stream=True)` → `data_download` (MEDIUM)

### 📝 Context-Aware Documentation Scanning
Recognizes placeholder patterns and documentation examples:
- Placeholder patterns: `your_api_key_here`, `sk-...`, `<API_KEY>`, `${VARIABLE}`
- i18n patterns: 配置, 设置, 示例, 请将, 填入
- Markdown code blocks in documentation files

### 🌐 Enhanced Whitelist System
Built-in whitelists for known safe patterns:
- Lock files: `package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`, `composer.lock`, `poetry.lock`, `Cargo.lock`
- Documentation files: `SKILL.md`, `README.md`, `AGENTS.md`, `CHANGELOG.md`
- Testing utilities: `test_*.py`, `conftest.py`, `with_server.py`

## What's New in v3.0

- 🔐 **Secret Detection Engine**: Hybrid entropy + pattern-based detection for AWS, GitHub, OpenAI, and generic API keys
- 📦 **Dependency Vulnerability Scanner**: Checks against OSV (Open Source Vulnerabilities) database
- 🌊 **Taint Analysis**: Tracks data flow from user input to dangerous functions (deep mode)
- ⚙️ **Configuration System**: YAML/JSON-based custom rules, severity overrides, and whitelisting

## Prerequisites

**Source the venv environment first before running the python scripts:**
```bash
source /opt/venv/bin/activate && pip -V
# pip 26.0.1 from /opt/venv/lib/python3.12/site-packages/pip (python 3.12)
```

## Quick Start

Scan a skill directory:
```bash
python src/cli.py /path/to/skill-folder
```

## Scanning Modes

| Mode | Description | Speed | Accuracy | Use Case |
|------|-------------|-------|----------|----------|
| **fast** | Regex + Secrets + Dependencies | ⚡ Fast | ⭐⭐⭐ | Quick initial scan |
| **standard** | Regex + AST + Secrets + Dependencies | ⚡ Balanced | ⭐⭐⭐⭐ | Default, recommended |
| **deep** | Full analysis + Taint Analysis | 🐢 Thorough | ⭐⭐⭐⭐⭐ | Comprehensive audit |

**Note:** Secret and Dependency analyzers run in all modes because they provide critical security checks with minimal performance overhead.

## Usage Examples

### Basic scan
```bash
python src/cli.py ~/.openclaw/skills/some-skill
```

### Deep scan with JSON output
```bash
python src/cli.py ~/.openclaw/skills/some-skill --mode deep --format json
```

### Export for manual review
```bash
python src/cli.py ~/.openclaw/skills/some-skill --export-for-llm
```

### Use custom configuration
```bash
python src/cli.py ~/.openclaw/skills/some-skill --config trustskill.yaml
```

### Batch scan multiple skills
```bash
for skill in ~/.openclaw/skills/*/; do
  echo "Scanning: $skill"
  python src/cli.py "$skill" --mode deep --format json > "results/$(basename $skill).json"
done
```

---

## Comprehensive Skill Scanning Guidance

### Pre-Scan Checklist

Before scanning a skill, verify:

- [ ] **Skill source is known** - Where did this skill come from? (official repo, trusted source, unknown)
- [ ] **Virtual environment is active** - Run `source /opt/venv/bin/activate`
- [ ] **Scan mode is appropriate** - Use `deep` for untrusted skills, `standard` for quick checks
- [ ] **Output format is set** - Use `json` for automation, `text` for manual review

### Step-by-Step Scanning Workflow

#### Phase 1: Initial Assessment

```bash
# Step 1: Quick scan to identify obvious issues
python src/cli.py /path/to/skill --mode fast

# Step 2: If any HIGH issues found, proceed to deep scan
python src/cli.py /path/to/skill --mode deep --format json > scan_result.json
```

#### Phase 2: Detailed Analysis

```bash
# Step 3: Export markdown report for thorough review
python src/cli.py /path/to/skill --mode deep --export-for-llm > scan_report.md

# Step 4: Review specific file types manually
find /path/to/skill -name "*.py" -exec grep -l "eval\|exec\|os.system" {} \;
```

#### Phase 3: Validation

```bash
# Step 5: Check for actual malicious patterns
grep -r "base64.b64decode" /path/to/skill --include="*.py"
grep -r "requests.post" /path/to/skill --include="*.py"
grep -r "subprocess.*shell=True" /path/to/skill --include="*.py"
```

### Result Interpretation Guide

#### Severity Levels

| Level | Icon | Meaning | Action |
|-------|------|---------|--------|
| **HIGH** | 🔴 | Confirmed security risk | **Stop and investigate immediately** |
| **MEDIUM** | 🟡 | Potential risk requiring review | Investigate before proceeding |
| **LOW** | 🟢 | Informational, low risk | Document and proceed with caution |

#### Finding Categories

| Category | Risk | Description | Typical Action |
|----------|------|-------------|----------------|
| `command_injection` | HIGH | User input to dangerous functions | **Critical** - Review code flow |
| `data_upload` | HIGH | POST/PUT to external servers | Investigate destination and data |
| `hardcoded_secret` | HIGH | Real API keys/passwords found | Remove and rotate credentials |
| `data_download` | MEDIUM | File downloads from internet | Verify source is legitimate |
| `api_key_usage` | MEDIUM | API key references (docs) | Usually safe if placeholder |
| `network_request` | MEDIUM | HTTP requests | Verify endpoints are legitimate |
| `vulnerable_dependency` | MEDIUM | CVE in dependencies | Update to patched version |
| `environment_access` | LOW | Reading env variables | Normal for configuration |
| `file_operation` | LOW | Standard file I/O | Verify paths are safe |

### Validation Techniques

#### 1. Verify Hardcoded Secrets
```bash
# Check if the "secret" is actually a placeholder
grep -B2 -A2 "your_api_key" /path/to/skill/SKILL.md

# Real secrets are usually in code files, not documentation
grep -r "api_key\s*=\s*['\"]sk-" /path/to/skill --include="*.py"
```

#### 2. Verify Network Requests
```bash
# Check what data is being sent
grep -B5 -A5 "requests.post" /path/to/skill/scripts/*.py

# Verify the destination URL
grep -r "https://" /path/to/skill --include="*.py" | grep -v "example.com"
```

#### 3. Verify Command Injection
```bash
# Check if user input reaches dangerous functions
grep -B10 "eval\|exec\|os.system" /path/to/skill/scripts/*.py
```

### Red Flags Requiring Immediate Action

🚨 **STOP IMMEDIATELY** if you find:

1. **Data Exfiltration Patterns**
   - Sending files to unknown servers
   - POST requests with system information
   - Uploading `.ssh`, `.env`, or credential files

2. **Backdoor Patterns**
   - Hidden network listeners
   - Encoded/obfuscated malicious code
   - Scheduled tasks creating persistence

3. **Destructive Operations**
   - `rm -rf /` or equivalent
   - `shutil.rmtree` on user directories
   - Mass file deletion patterns

4. **Credential Harvesting**
   - Reading `/etc/passwd`, `/etc/shadow`
   - Accessing browser credential stores
   - Extracting SSH private keys

**Action:** Delete the skill immediately and report to security team.

---

## What It Detects

### High Risk 🔴
- **Tainted Command Injection**: User input flowing to `eval()`, `exec()`, or `os.system()`
- **Hardcoded Secrets**: Real API keys, passwords, tokens (not placeholders)
- **Data Upload**: HTTP POST/PUT to external servers with sensitive data
- **Destructive Operations**: Recursive file/directory deletion (`rm -rf`, `shutil.rmtree`)
- **Credential Harvesting**: Password/key extraction attempts

### Medium Risk 🟡
- **Data Download**: File downloads from internet (verify source legitimacy)
- **Vulnerable Dependencies**: Packages with known CVEs (via OSV database)
- **Out-of-bounds File Access**: Accessing `/etc/passwd`, SSH keys, or sensitive configs
- **Code Obfuscation**: Base64, ROT13, or packed code (may be legitimate)
- **Dynamic Imports**: Use of `__import__` or `importlib` with variables
- **Network Requests**: HTTP calls to unknown domains

### Low Risk 🟢
- **Static Shell Commands**: Commands using only string literals
- **Standard File Operations**: Regular file read/write within the workspace
- **Environment Access**: Reading environment variables (normal for config)
- **Documentation References**: API key placeholders in SKILL.md, README.md

## When to Use This Skill

1. **Before installing untrusted skills** - Always scan skills from unknown sources
2. **Periodic audits** - Regular security checks of installed skills
3. **Pre-execution validation** - Before running skill scripts that modify system
4. **Publishing validation** - Before publishing skills to ClawHub
5. **CI/CD integration** - Use `--format json` for automated security gates

## Security Patterns

See [security_patterns.md](references/security_patterns.md) for detailed patterns and detection rules.

## Whitelist System

TrustSkill v3.1+ includes comprehensive whitelists for known safe patterns:

### Lock Files (Automatically Skipped)
Files containing integrity hashes that are safe by design:
- `package-lock.json` - npm lock file
- `yarn.lock` - Yarn lock file
- `pnpm-lock.yaml` - pnpm lock file
- `composer.lock` - PHP Composer lock file
- `poetry.lock` - Python Poetry lock file
- `Cargo.lock` - Rust Cargo lock file
- `Gemfile.lock` - Ruby Bundler lock file

### Documentation Files
Files where placeholder references are expected:
- `SKILL.md`, `README.md`, `AGENTS.md`, `CHANGELOG.md`, `LICENSE`

### Testing Utility Files
Files where `shell=True` is expected for legitimate testing:
- `test_*.py`, `*_test.py`, `conftest.py`
- `with_server.py`, `test_server.py`, `test_helpers.py`

### Placeholder Patterns
Automatically recognized as safe documentation examples:
- `your_api_key_here`, `your_secret_here`, `your_token_here`
- `sk-...`, `sk_...` (truncated examples)
- `<API_KEY>`, `<YOUR_TOKEN>`, `<SECRET>`
- `${VARIABLE}`, `{{VARIABLE}}` (template patterns)
- i18n patterns: 配置, 设置, 示例, 请将, 填入

### Custom Whitelist
Add custom whitelist patterns via YAML configuration:

```yaml
rules:
  whitelist:
    files:
      - "test_*.py"
      - "my_server.py"
    patterns:
      - "eval\\(\\s*['\"]1\\+1['\"]\\s*\\)"
```

## Best Practices for Interpreting Results

### Understanding Confidence Scores

| Score Range | Interpretation |
|-------------|----------------|
| 0.9 - 1.0 | Very high confidence - likely a real issue |
| 0.7 - 0.9 | High confidence - investigate thoroughly |
| 0.5 - 0.7 | Medium confidence - review context |
| < 0.5 | Low confidence - may be false positive |

### Common False Positive Patterns

1. **Integrity Hashes in Lock Files** (v3.1+ handles automatically)
   ```
   "integrity": "sha512-P33hHGdldxGabLFjPPpaTxVolMrzrcegejx..."
   ```
   → These are SRI hashes, not secrets

2. **Documentation Placeholders** (v3.1+ handles automatically)
   ```
   export API_KEY="your_api_key_here"
   ```
   → This is documentation, not a real secret

3. **Environment Variable References**
   ```
   API_KEY = os.environ.get("MY_API_KEY")
   ```
   → This reads from environment, not hardcoded

### When to Escalate

Escalate to security review if:

1. Multiple HIGH findings in the same skill
2. Findings involve external network communication
3. Code appears intentionally obfuscated
4. Files accessed outside workspace without clear reason
5. Pattern suggests credential exfiltration

## Response to Findings

### Critical (Stop immediately)
- Confirmed backdoor or data exfiltration
- Hardcoded production credentials
- System-level destructive operations
- **Action:** Delete skill, report to security, rotate any exposed credentials

### High Risk (Manual review required)
- Suspicious network requests
- Tainted data reaching dangerous functions
- Command injection patterns
- **Action:** Full code review, understand intent, proceed only if confident

### Medium Risk (Investigate before proceeding)
- Unknown network endpoints
- Dependency vulnerabilities
- File access outside workspace
- **Action:** Verify legitimacy, document findings, proceed with caution

### Low Risk (Document and proceed)
- Environment variable access
- Standard file operations
- Documentation placeholders
- **Action:** Note findings, proceed normally

## Comparison with Previous Versions

| Feature | v1.x | v2.0 | v3.0 | v3.1 |
|---------|------|------|------|------|
| Regex Analysis | ✅ | ✅ | ✅ | ✅ |
| AST Analysis | ❌ | ✅ | ✅ | ✅ |
| Secret Detection | ❌ | ❌ | ✅ | ✅ |
| Dependency Scanning | ❌ | ❌ | ✅ | ✅ |
| Taint Analysis | ❌ | ❌ | ✅ | ✅ |
| YAML Configuration | ❌ | ❌ | ✅ | ✅ |
| Progress Tracking | ❌ | ✅ | ✅ | ✅ |
| Confidence Scoring | ❌ | ✅ | ✅ | ✅ |
| Lock File Whitelist | ❌ | ❌ | ❌ | ✅ |
| Smart Data Flow | ❌ | ❌ | ❌ | ✅ |
| Context-Aware Docs | ❌ | ❌ | ❌ | ✅ |
| i18n Placeholder Support | ❌ | ❌ | ❌ | ✅ |
| False Positive Reduction | ~50% | ~70% | ~85% | **~99%** |

## Output Formats

- **text** (default): Colorized terminal output with progress bar
- **json**: Machine-readable JSON for CI/CD integration
- **markdown**: Formatted report for LLM review or documentation

## Exit Codes

- `0`: No high-risk issues found
- `1`: High-risk issues detected (useful for CI/CD pipelines)

## License

MIT License - See the [LICENSE](LICENSE) file for details.
