# SKILL.md Update Plan - v3.0 Alignment

## Current State Analysis

### Version Mismatch
| Field | Current | Should Be |
|-------|---------|-----------|
| version | 1.1.0 | 3.0.0 |

### Missing Features Documentation
- Secret Detection (entropy-based + pattern matching)
- Dependency Vulnerability Scanning (OSV integration)
- Taint Analysis (data flow tracking)
- YAML/JSON Configuration system

### Inaccurate Mode Descriptions
| Mode | Current Description | Actual Behavior |
|------|---------------------|-----------------|
| fast | "Pattern matching only" | Regex + Secrets + Dependencies |
| deep | "+ LLM review" | + Taint Analysis (no LLM) |

### Outdated Usage Examples
- Uses `scripts/scan_skill.py` (legacy)
- Should use `src/cli.py` (current)

### Missing Detection Categories
- Hardcoded Secrets (API keys, passwords, tokens)
- Vulnerable Dependencies (CVE detection)
- Tainted Data Flow (user input to dangerous functions)

---

## Update Plan

### 1. Front Matter Updates
- Update `version: 1.1.0` → `version: 3.0.0`
- Expand description to include all v3.0 features

### 2. Features List Updates
Add to the bullet list:
- Secret Detection (high-entropy strings, API keys)
- Dependency Vulnerability Scanning (known CVEs)
- Taint Analysis (data flow tracking in deep mode)
- Configuration System (YAML/JSON custom rules)

### 3. Scanning Modes Section
Update descriptions:
- **fast**: Regex + Secrets + Dependencies (quickest)
- **standard**: + AST analysis (default, recommended)
- **deep**: + Taint Analysis (most thorough)

### 4. Usage Examples
Update all paths:
- `scripts/scan_skill.py` → `src/cli.py`

Add new examples:
- Using configuration file
- Different output formats

### 5. Detection Categories Updates

#### High Risk (add new items)
- Hardcoded Secrets (API keys, passwords, tokens via entropy analysis)
- Tainted Command Injection (tracking user input to dangerous functions)

#### Medium Risk (add new items)
- Vulnerable Dependencies (packages with known CVEs)

### 6. New Section: Configuration
Add section explaining YAML configuration

### 7. New Section: What v3.0 Adds
Brief comparison or feature highlights

---

## Implementation Checklist

- [ ] Update front matter version and description
- [ ] Update features list with v3.0 capabilities
- [ ] Fix scanning modes descriptions
- [ ] Update all usage examples to use `src/cli.py`
- [ ] Update detection categories
- [ ] Add configuration section
- [ ] Verify all examples work
