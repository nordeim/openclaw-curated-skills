---
description: Scan npm and pip projects for outdated dependencies, security vulnerabilities, and updates.
---

# Dependency Checker

Check for outdated dependencies and security issues in npm and pip projects.

## Instructions

1. **Detect project type**: `package.json` → npm, `requirements.txt`/`pyproject.toml` → pip

2. **Run checks**:
   ```bash
   # npm
   cd /path/to/project
   npm outdated --json 2>/dev/null
   npm audit --json 2>/dev/null

   # pip
   pip list --outdated --format=json 2>/dev/null
   pip-audit 2>/dev/null  # if installed
   ```

3. **Output format**:
   ```
   📦 Dependency Check — my-project

   ## npm (3 outdated of 42 total)
   | Package | Current | Latest | Type |
   |---------|---------|--------|------|
   | express | 4.18.2  | 5.0.1  | ⚠️ Major |
   | lodash  | 4.17.20 | 4.17.21| 🟢 Patch |

   ## 🔒 Security Issues
   | Package | Severity | Issue |
   |---------|----------|-------|
   | lodash <4.17.21 | 🔴 High | Prototype Pollution |

   ## Update Commands
   npm update                          # safe (patch+minor)
   npm install express@latest          # major (review changelog!)
   pip install --upgrade flask requests
   ```

4. **Version classification**:
   - 🟢 Patch (x.y.3→x.y.4): Safe to update
   - 🔵 Minor (x.2.z→x.3.0): Usually safe, check changelog
   - ⚠️ Major (1.x→2.0): Breaking changes likely

## Edge Cases

- **Monorepos**: Check each package directory separately
- **Lock file only**: If no `package.json` in current dir, look for `package-lock.json`
- **Private registries**: May need `.npmrc` configuration
- **Pinned versions**: Flag `==` pins in requirements.txt that prevent updates

## Security

- Never run `npm audit fix --force` without user approval (may introduce breaking changes)
- Review major updates' changelogs before recommending

## Requirements

- `npm` and/or `pip` CLI tools
- No API keys needed
