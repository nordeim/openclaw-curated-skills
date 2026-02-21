# Orange TrustSkill v3.0 Enhancement Plan

## Version Information
- **Current Version**: 2.0.0
- **Target Version**: 3.0.0
- **Enhancement Count**: 4 major features
- **Methodology**: Test-Driven Development (TDD)

---

## Executive Summary

This plan outlines the enhancement of Orange TrustSkill from v2.0 to v3.0, adding 4 major capabilities:
1. Secret Detection Engine (entropy-based + regex)
2. Dependency Vulnerability Scanner (OSV integration)
3. Configuration System (YAML-based custom rules)
4. Enhanced Taint Analysis (data flow tracking)

---

## Enhancement 1: Secret Detection Engine 🔐

### Purpose
Detect hardcoded secrets, API keys, passwords, and tokens in code using a hybrid approach of entropy analysis and regex patterns.

### Technical Design

```
src/
├── analyzers/
│   └── secret_analyzer.py      # NEW: Secret detection analyzer
└── utils/
    └── entropy.py               # NEW: Shannon entropy calculator
```

### Detection Methods

1. **High-Entropy String Detection**
   - Calculate Shannon entropy for strings
   - Flag strings with entropy > 4.5 (configurable)
   - Filter out common false positives (hashes, UUIDs)

2. **Pattern-Based Detection**
   - API Key patterns: `api[_-]?key`, `apikey`
   - Secret patterns: `secret`, `password`, `token`
   - Service-specific: `AWS_`, `GITHUB_`, `OPENAI_`

3. **Context Analysis**
   - Check for assignment operators (`=`, `:`)
   - Verify string length (skip short strings)
   - Filter comments and documentation

### TDD Test Strategy

**RED Phase - Write failing tests:**
```python
def test_detects_high_entropy_api_key():
    content = 'API_KEY = "sk-live-abcdefghijklmnopqrstuvwxyz123456"'
    issues = analyzer.analyze(Path("config.py"), content)
    assert any(i.category == 'hardcoded_secret' for i in issues)

def test_detects_aws_access_key():
    content = 'AWS_ACCESS_KEY_ID = "AKIAIOSFODNN7EXAMPLE"'
    issues = analyzer.analyze(Path("config.py"), content)
    assert any('AWS' in i.description for i in issues)

def test_ignores_low_entropy_strings():
    content = 'name = "hello world"'  # Low entropy
    issues = analyzer.analyze(Path("config.py"), content)
    assert len(issues) == 0
```

**GREEN Phase - Implement:**
- Create `SecretAnalyzer` class inheriting from `BaseAnalyzer`
- Implement `EntropyCalculator` utility
- Add secret patterns to rules.py

**REFACTOR Phase:**
- Optimize entropy calculation
- Add caching for repeated calculations
- Fine-tune entropy thresholds

---

## Enhancement 2: Dependency Vulnerability Scanner 📦

### Purpose
Scan Python imports against the Open Source Vulnerabilities (OSV) database to detect known CVEs in dependencies.

### Technical Design

```
src/
├── analyzers/
│   └── dependency_analyzer.py   # NEW: Dependency vulnerability analyzer
└── utils/
    └── osv_client.py            # NEW: OSV API client
```

### Detection Methods

1. **Import Extraction**
   - Parse Python AST for import statements
   - Extract package names from imports
   - Handle both `import x` and `from x import y`

2. **Version Detection**
   - Try to detect installed version from environment
   - Fallback to requirements.txt parsing
   - Support for pyproject.toml

3. **OSV Database Query**
   - Query OSV API for each dependency
   - Cache results to minimize API calls
   - Batch queries for efficiency

### TDD Test Strategy

**RED Phase - Write failing tests:**
```python
def test_detects_vulnerable_requests_version():
    content = 'import requests  # Version 2.19.1 (vulnerable)'
    issues = analyzer.analyze(Path("app.py"), content)
    assert any(i.category == 'vulnerable_dependency' for i in issues)

def test_caches_osv_results():
    # First call should query API
    # Second call should use cache
    pass

def test_handles_missing_version():
    # Should still work if version can't be determined
    pass
```

**GREEN Phase - Implement:**
- Create `DependencyAnalyzer` class
- Implement `OSVClient` for API communication
- Add version parsing utilities

**REFACTOR Phase:**
- Implement intelligent caching
- Add retry logic for API failures
- Support offline mode with cached database

---

## Enhancement 3: Configuration System ⚙️

### Purpose
Allow users to customize scanning behavior via YAML/JSON configuration files without modifying code.

### Technical Design

```
src/
├── config/
│   ├── __init__.py
│   ├── loader.py                # NEW: Config file loader
│   ├── validator.py             # NEW: Config validation
│   └── default_config.yaml      # NEW: Default configuration
```

### Configuration Options

```yaml
# trustskill.yaml
version: "3.0"

scanning:
  mode: standard  # fast, standard, deep
  max_file_size: 10MB
  follow_symlinks: false
  
rules:
  custom_patterns:
    - name: "custom_api_key"
      pattern: "X-API-KEY:\\s*(\\w+)"
      severity: HIGH
      description: "Custom API key header"
      
  severity_overrides:
    network_request: LOW  # Downgrade from MEDIUM
    
  whitelist:
    files:
      - "test_*.py"
      - "*_test.py"
    patterns:
      - "eval\\(\\s*['\"]1\\+1['\"]\\s*\\)"  # Safe eval example
      
secret_detection:
  enabled: true
  min_entropy: 4.5
  min_length: 20
  
dependency_check:
  enabled: true
  cache_duration: 3600  # seconds
  
output:
  format: text
  color: true
  show_confidence: true
```

### TDD Test Strategy

**RED Phase - Write failing tests:**
```python
def test_loads_yaml_config():
    config = ConfigLoader.load("trustskill.yaml")
    assert config.scanning.mode == "standard"

def test_validates_config_schema():
    with pytest.raises(ConfigValidationError):
        ConfigLoader.load("invalid.yaml")

def test_custom_patterns_applied():
    config = ConfigLoader.load_with_custom_patterns("trustskill.yaml")
    scanner = SkillScanner(config=config)
    # Verify custom patterns are active
```

**GREEN Phase - Implement:**
- Create `Config` dataclass
- Implement `ConfigLoader` with YAML/JSON support
- Add `ConfigValidator` with schema validation

**REFACTOR Phase:**
- Add configuration inheritance (base + user config)
- Implement hot-reload for config files
- Add configuration migration for version updates

---

## Enhancement 4: Enhanced Taint Analysis 🌊

### Purpose
Implement basic data flow tracking (taint analysis) to follow user input from source to sink, reducing false positives and catching complex injection vulnerabilities.

### Technical Design

```
src/
├── analyzers/
│   └── taint_analyzer.py        # NEW: Taint flow analyzer
└── taint/
    ├── __init__.py
    ├── source.py                # NEW: Taint source definitions
    ├── sink.py                  # NEW: Taint sink definitions
    └── tracker.py               # NEW: Taint tracking engine
```

### Taint Model

**Sources** (User Input):
- `input()` function
- `sys.argv`
- `os.environ`
- HTTP request parameters
- File reads

**Sinks** (Dangerous Operations):
- `eval()`, `exec()`
- `os.system()`, `subprocess.*`
- SQL query execution
- `open()` with user-controlled paths

**Sanitizers** (Safe Operations):
- Input validation functions
- Escaping functions
- Type casting

### TDD Test Strategy

**RED Phase - Write failing tests:**
```python
def test_detects_taint_flow_to_eval():
    content = '''
user_input = input("Enter: ")
result = eval(user_input)  # Tainted input to eval
'''
    issues = analyzer.analyze(Path("app.py"), content)
    assert any(i.category == 'tainted_code_execution' for i in issues)

def test_no_issue_when_input_validated():
    content = '''
user_input = input("Enter: ")
if user_input.isdigit():
    result = eval(user_input)  # Validated - should not flag
'''
    issues = analyzer.analyze(Path("app.py"), content)
    assert len(issues) == 0

def test_tracks_taint_through_variable_assignment():
    content = '''
data = input("Enter: ")
processed = data.upper()
result = eval(processed)  # Still tainted
'''
    issues = analyzer.analyze(Path("app.py"), content)
    assert len(issues) > 0
```

**GREEN Phase - Implement:**
- Create `TaintTracker` class
- Implement AST-based flow analysis
- Define sources, sinks, and sanitizers

**REFACTOR Phase:**
- Handle complex control flow (if/else, loops)
- Add interprocedural analysis (function calls)
- Optimize for large codebases

---

## Implementation Phases

### Phase 1: Foundation (Week 1)
- [ ] Create configuration system
- [ ] Update CLI to accept --config flag
- [ ] Add tests for config loading/validation

### Phase 2: Secret Detection (Week 1-2)
- [ ] Implement entropy calculator
- [ ] Create SecretAnalyzer
- [ ] Add comprehensive secret patterns
- [ ] Write tests (RED-GREEN-REFACTOR)

### Phase 3: Dependency Scanning (Week 2-3)
- [ ] Implement OSV client
- [ ] Create DependencyAnalyzer
- [ ] Add caching layer
- [ ] Write tests (RED-GREEN-REFACTOR)

### Phase 4: Taint Analysis (Week 3-4)
- [ ] Design taint model
- [ ] Implement TaintTracker
- [ ] Add sources, sinks, sanitizers
- [ ] Write tests (RED-GREEN-REFACTOR)

### Phase 5: Integration & Polish (Week 4)
- [ ] Integrate all analyzers
- [ ] Update formatters for new issue types
- [ ] Update documentation
- [ ] Final test suite validation

---

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| OSV API rate limiting | Medium | Medium | Implement caching, batch queries |
| High false positive rate in secrets | Medium | High | Tune entropy thresholds, add filters |
| Performance degradation | Low | High | Optimize with caching, lazy loading |
| Breaking changes in v2.0 API | Low | High | Maintain backward compatibility |

---

## Success Criteria

- [ ] All 4 enhancements implemented with TDD
- [ ] Test coverage > 90% for new code
- [ ] Zero breaking changes to v2.0 CLI interface
- [ ] Documentation updated with new features
- [ ] Performance impact < 20% increase in scan time

---

## Version Bump Strategy

```
v2.0.0 -> v3.0.0

Breaking Changes: None
New Features: Secret Detection, Dependency Scanning, Config System, Taint Analysis
Deprecated: None
```
