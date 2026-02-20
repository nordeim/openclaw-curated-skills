# TrustSkill v3.0 🍊

Advanced Security Scanner for OpenClaw Skills

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

## ✨ Features

- 🔍 **Multi-Layer Analysis**: Combines Regex, AST (Abstract Syntax Tree), and deep inspection.
- 🔐 **Secret Detection**: Hybrid entropy and pattern-based discovery of hardcoded API keys and credentials.
- 📦 **Vulnerability Scanning**: Integration with OSV (Open Source Vulnerabilities) database to detect vulnerable dependencies.
- 🌊 **Taint Analysis**: Advanced data flow tracking to detect complex injection vulnerabilities (available in `deep` mode).
- ⚙️ **Flexible Configuration**: YAML-based rule customization, severity overrides, and whitelisting.
- 🎯 **Precision Detection**: Context-aware pattern matching to reduce false positives.
- 🌈 **Rich Output Formats**: Supports Colorized Terminal, JSON, and Markdown.
- 📊 **Real-time Tracking**: Live progress monitoring during scans.

## 🚀 Quick Start

```bash
# Scan a specific skill
python3 src/cli.py /path/to/skill

# Use a custom configuration file
python3 src/cli.py /path/to/skill --config trustskill.yaml

# Deep scan (includes Taint Analysis)
python3 src/cli.py /path/to/skill --mode deep

# Output results as JSON for CI/CD
python3 src/cli.py /path/to/skill --format json
```

## 📦 Installation

Zero external dependencies! Built entirely using the Python Standard Library (YAML support is optional but recommended).

## 🔧 Usage

### Analysis Modes

| Mode | Description | Speed | Accuracy |
|------|-------------|-------|----------|
| `fast` | Regex + Secrets + Dependencies | ⚡ Fast | ⭐⭐⭐ |
| `standard` | Regex + AST + Secrets + Dependencies | ⚡ Balanced | ⭐⭐⭐⭐ |
| `deep` | Full analysis + Taint Analysis | 🐢 Thorough | ⭐⭐⭐⭐⭐ |

**Note:** Secret and Dependency analyzers run in all modes because they provide critical security checks with minimal performance overhead.

### Configuration (`trustskill.yaml`)

You can customize the scanner's behavior without modifying code:

```yaml
version: "3.0"
scanning:
  mode: standard
secret_detection:
  enabled: true
  min_entropy: 4.5
rules:
  custom_patterns:
    - name: "custom_api_key"
      pattern: "X-API-KEY:\\s*(\\w+)"
      severity: HIGH
  severity_overrides:
    network_request: LOW
```

## 🛡️ Security Checks

### High Risk 🔴
- **Tainted Command Injection**: Tracking user input to `eval()`, `exec()`, or `os.system()`.
- **Hardcoded Secrets**: Detection of high-entropy strings and known API key patterns (AWS, GitHub, etc.).
- **Data Exfiltration**: HTTP POST to external servers or suspicious IPs.
- **Destructive Operations**: Recursive file/directory deletion.

### Medium Risk 🟡
- **Vulnerable Dependencies**: Packages with known CVEs detected via OSV integration.
- **Out-of-bounds Access**: Accessing files like `/etc/passwd` or SSH keys.
- **Code Obfuscation**: Base64, ROT13, or packed code.
- **Dynamic Imports**: Use of `__import__` or `importlib` with variables.

### Low Risk 🟢
- **Static Shell Commands**: Commands using only string literals.
- **Standard File Ops**: Regular file read/write within the workspace.

## 🏗️ Architecture

```
src/
├── config/                  # NEW: Configuration system (YAML/JSON)
│   ├── loader.py            # Config loader and inheritance
│   └── validator.py         # Schema validation
├── utils/                   # NEW: Utility modules
│   └── entropy.py           # Shannon entropy calculator
├── analyzers/
│   ├── base.py              # Base analyzer class
│   ├── regex_analyzer.py    # Regex pattern matching
│   ├── ast_analyzer.py      # Python AST analysis
│   ├── secret_analyzer.py   # NEW: Secret detection engine
│   ├── dependency_analyzer.py # NEW: OSV vulnerability scanner
│   └── taint_analyzer.py    # NEW: Data flow tracking (Taint analysis)
└── formatters/
    ├── base.py              # Base formatter class
    ├── text_formatter.py    # Colorized terminal output
    ├── json_formatter.py    # Structured JSON output
    └── markdown_formatter.py # Markdown for LLM/manual review
```

## 🔍 How It Works

1. **Discovery**: Recursively gathers files, respecting `.gitignore` and ignore patterns.
2. **Analysis**:
   - **Regex**: Rapid signature-based scanning.
   - **AST**: Deep structural code analysis.
   - **Entropy**: Mathematical randomness checks for secrets.
   - **Taint**: Data flow tracking from source (input) to sink (danger).
3. **Filtering**: Context-aware logic ignores documentation and example code.
4. **Reporting**: Aggregates findings with confidence scores and risk assessments.

## 🆚 Comparison Matrix

| Feature | v1.x | v2.0 | v3.0 |
|------|------|------|------|
| Regex Analysis | ✅ | ✅ | ✅ |
| AST Analysis | ❌ | ✅ | ✅ |
| Secret Detection | ❌ | ❌ | ✅ |
| Dependency Scanning | ❌ | ❌ | ✅ |
| Taint Analysis | ❌ | ❌ | ✅ |
| YAML Configuration | ❌ | ❌ | ✅ |
| Progress Tracking | ❌ | ✅ | ✅ |
| Confidence Scoring | ❌ | ✅ | ✅ |

## 🤝 Contributing

Contributions are welcome! We follow a strict TDD (Test-Driven Development) methodology.
- Ensure all 218+ tests pass: `python3 -m pytest tests/`
- Maintain 90%+ code coverage.
- Adhere to PEP 8 standards.

## 📄 License

MIT License - See the [LICENSE](LICENSE) file for details.
