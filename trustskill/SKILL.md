---
name: trustskill
version: 3.0.0
description: TrustSkill v3.0 - Advanced security scanner for OpenClaw skills. Detects malicious code, hardcoded secrets, vulnerable dependencies, tainted data flows, backdoors, credential theft, privacy file access, command injection, file system risks, network exfiltration, and sensitive data leaks. Features entropy-based secret detection, OSV vulnerability database integration, taint analysis, and flexible YAML configuration.
---

# TrustSkill v3.0 - Advanced Skill Security Scanner

A comprehensive security scanner for OpenClaw skills that detects:
- **Malicious code and backdoors**
- **Hardcoded secrets** (API keys, passwords, tokens via entropy analysis)
- **Vulnerable dependencies** (known CVEs via OSV database)
- **Tainted data flows** (user input to dangerous functions)
- **Credential theft** (SSH keys, passwords, API keys)
- **Privacy file access** (Memory files, configs)
- **Command injection** (eval, exec, os.system)
- **Data exfiltration** (suspicious network requests)
- **File system risks** (destructive operations)
- **Network security issues**

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

| Mode | Description | Speed | Accuracy |
|------|-------------|-------|----------|
| **fast** | Regex + Secrets + Dependencies | ⚡ Fast | ⭐⭐⭐ |
| **standard** | Regex + AST + Secrets + Dependencies | ⚡ Balanced | ⭐⭐⭐⭐ |
| **deep** | Full analysis + Taint Analysis | 🐢 Thorough | ⭐⭐⭐⭐⭐ |

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

## Configuration

Create a `trustskill.yaml` file to customize scanning behavior:

```yaml
version: "3.0"
scanning:
  mode: standard
secret_detection:
  enabled: true
  min_entropy: 4.5
  min_length: 20
rules:
  custom_patterns:
    - name: "custom_api_key"
      pattern: "X-API-KEY:\s*(\w+)"
      severity: HIGH
      description: "Custom API key header"
  severity_overrides:
    network_request: LOW
  whitelist:
    files:
      - "test_*.py"
    patterns:
      - "eval\(\s*['\"]1\+1['\"]\s*\)"
```

## What It Detects

### High Risk 🔴
- **Tainted Command Injection**: User input flowing to `eval()`, `exec()`, or `os.system()`
- **Hardcoded Secrets**: High-entropy strings and known API key patterns (AWS, GitHub, OpenAI, etc.)
- **Data Exfiltration**: HTTP POST to external servers or suspicious IPs
- **Destructive Operations**: Recursive file/directory deletion (`rm -rf`, `shutil.rmtree`)
- **Credential Harvesting**: Password/key extraction attempts

### Medium Risk 🟡
- **Vulnerable Dependencies**: Packages with known CVEs (via OSV database)
- **Out-of-bounds File Access**: Accessing `/etc/passwd`, SSH keys, or sensitive configs
- **Code Obfuscation**: Base64, ROT13, or packed code
- **Dynamic Imports**: Use of `__import__` or `importlib` with variables
- **Network Requests**: HTTP calls to unknown domains

### Low Risk 🟢
- **Static Shell Commands**: Commands using only string literals
- **Standard File Operations**: Regular file read/write within the workspace
- **Environment Access**: Reading environment variables

## When to Use This Skill

1. **Before installing untrusted skills** - Always scan skills from unknown sources
2. **Periodic audits** - Regular security checks of installed skills
3. **Pre-execution validation** - Before running skill scripts that modify system
4. **Publishing validation** - Before publishing skills to ClawHub
5. **CI/CD integration** - Use `--format json` for automated security gates

## Security Patterns

See [security_patterns.md](references/security_patterns.md) for detailed patterns and detection rules.

## Whitelist System

TrustSkill v3.0+ includes a built-in whitelist for known safe patterns to reduce false positives:

### Documentation Files
Files like `SKILL.md`, `README.md`, `AGENTS.md` can reference memory/config files in documentation context without triggering security alerts.

### Testing Utility Files
Files like `with_server.py`, `test_*.py`, `conftest.py` can use `subprocess.Popen(shell=True)` for legitimate server orchestration and testing purposes.

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

## Response to Findings

### Critical (Stop immediately)
- Confirmed backdoor or data exfiltration
- Hardcoded production credentials
- System-level destructive operations

### High Risk (Manual review required)
- Suspicious network requests
- Tainted data reaching dangerous functions
- Command injection patterns
- Report to user and await confirmation

### Medium/Low Risk (Proceed with caution)
- Document findings
- Inform user of potential risks
- Proceed if user confirms

## Comparison with Previous Versions

| Feature | v1.x | v2.0 | v3.0 |
|---------|------|------|------|
| Regex Analysis | ✅ | ✅ | ✅ |
| AST Analysis | ❌ | ✅ | ✅ |
| Secret Detection | ❌ | ❌ | ✅ |
| Dependency Scanning | ❌ | ❌ | ✅ |
| Taint Analysis | ❌ | ❌ | ✅ |
| YAML Configuration | ❌ | ❌ | ✅ |
| Progress Tracking | ❌ | ✅ | ✅ |
| Confidence Scoring | ❌ | ✅ | ✅ |

## Output Formats

- **text** (default): Colorized terminal output with progress bar
- **json**: Machine-readable JSON for CI/CD integration
- **markdown**: Formatted report for LLM review or documentation

## Exit Codes

- `0`: No high-risk issues found
- `1`: High-risk issues detected (useful for CI/CD pipelines)

## License

MIT License - See the [LICENSE](LICENSE) file for details.
