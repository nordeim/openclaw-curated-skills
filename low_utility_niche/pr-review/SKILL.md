---
name: pr-review
description: Find and fix code issues before publishing a PR. Launches 5 parallel analysis agents for bugs, security, performance, guidelines compliance, and quality. Auto-fixes high-confidence issues directly in your code. Also supports auditing existing code by path. Requires Git.
metadata: {"openclaw": {"requires": {"bins": ["git"]}}}
---

# Pre-Review

Find and fix issues **before** publishing your PR — not after.

Traditional review tools post comments on published PRs, creating a fix-then-update loop. Pre-review inverts this: analyze locally, fix directly, publish clean.

## Usage

```
/pr-review                    # Review changes on current branch vs main/master
/pr-review src/api/ src/auth/ # Audit specific directories
/pr-review **/*.ts            # Audit files matching a pattern
/pr-review --audit            # Audit entire codebase with smart prioritization
```

Two modes, one command:

| Mode | Trigger | Scope | Fix threshold | Best for |
|------|---------|-------|---------------|----------|
| **Diff** | No args, on branch with changes | Changed files only | >= 70 | Before opening a PR |
| **Audit** | Paths, patterns, or `--audit` | Specified files or full codebase | >= 80 (conservative) | Security reviews, codebase health |

## Instructions

Follow these steps precisely.

### Step 1: Detect Mode and Scope

Create a todo list to track progress through all steps.

**No arguments provided:**
- Run `git diff main...HEAD --name-only` (try master if main doesn't exist)
- If changes exist: **Diff mode** — review branch changes only
- If no changes: inform user "No changes found. Use `/pr-review <path>` to audit existing code." and stop

**Paths or patterns provided:**
- Resolve to actual files
- If > 50 files, ask user to narrow scope or confirm
- **Audit mode**

**`--audit` flag:**
- Identify source directories (src/, lib/, app/, etc.)
- Exclude: node_modules, dist, build, vendor, .git, coverage
- Propose scope to user for confirmation
- **Audit mode**

### Step 2: Discover Project Guidelines (Haiku Agent)

Launch a Haiku agent (Task tool, model: haiku) to find and read:
- Root CLAUDE.md and CLAUDE.md files in relevant directories
- .eslintrc, .prettierrc, tsconfig.json, biome.json or similar
- CONTRIBUTING.md, code style guides
- package.json (tech stack context)

Return a summary of guidelines and tech stack.

### Step 3: Build Context

**Diff mode** — Launch a Haiku agent to:
- Run `git diff main...HEAD` (full diff; use master if main doesn't exist)
- Return structured summary: files changed, nature of changes, lines added/removed

**Audit mode** — Launch a Haiku agent to categorize files by risk:

| Priority | Examples |
|----------|---------|
| **High** | Auth, payments, DB queries, API endpoints, input validation, file handlers, crypto |
| **Medium** | Business logic, services, utilities, state management |
| **Low** | Tests (unless requested), config-only, types/interfaces, constants |

Return prioritized file list. Analysis focuses on high and medium priority files.

### Step 4: Parallel Deep Analysis (5 Sonnet Agents)

Launch **5 Sonnet agents in a single message** (Task tool, model: sonnet, subagent_type: general-purpose).

Each agent receives: the guidelines summary from Step 2, the context from Step 3, and instructions to return issues as a structured list with file path, line numbers, severity (critical/important/minor), category, description, suggested fix, and confidence score (0-100).

#### Diff Mode — Agent Assignments

**Agent #1 — Guidelines Compliance:**
Audit changes against project guidelines (CLAUDE.md, eslint, prettier, etc.):
- Naming conventions
- Required and forbidden code patterns
- Documentation requirements
- Anti-patterns specific to the project

**Agent #2 — Bug Scanner:**
Scan changed code for real bugs (not style):
- Logic errors, off-by-one
- Null/undefined handling
- Race conditions, resource leaks
- Error handling gaps
- Async/await mistakes

**Agent #3 — Git History and Regressions:**
Read git blame and log of modified files. Return findings as issues when regressions or problems are detected:
- Regressions (re-introducing previously fixed bugs)
- Breaking changes to stable, long-lived code
- Patterns intentionally established in prior commits being undone
- Changes that contradict context from recent commit history

**Agent #4 — Security and Performance:**
- Injection vulnerabilities (SQL, XSS, command, path traversal)
- Exposed secrets, auth issues, unsafe operations
- N+1 queries, unnecessary loops, memory leaks, API misuse

**Agent #5 — Quality and Tests:**
- Missing or inadequate tests for new functionality
- Dead code introduced
- Duplicated logic that should be extracted
- Inconsistent error handling
- Comments that became stale due to code changes

#### Audit Mode — Agent Assignments

**Agent #1 — Security Audit:**
Deep security scan of target files:
- SQL/NoSQL injection, XSS, command injection, path traversal
- Hardcoded secrets and credentials, weak cryptography
- Authentication bypasses, authorization flaws, SSRF
- Insecure deserialization

**Agent #2 — Bug Detection:**
Scan for bugs and logic errors:
- Null/undefined handling, off-by-one errors
- Race conditions, resource leaks (memory, file handles, connections)
- Infinite loops, unreachable code, dead code paths
- Type coercion issues, async/await mistakes, error swallowing

**Agent #3 — Data Flow Analysis:**
Trace data through the application:
- Unvalidated user input reaching sensitive operations
- Data leaks (logging PII, exposing internals in errors)
- Missing input sanitization at boundaries
- Trust boundary violations

**Agent #4 — Performance and Resources:**
- N+1 query patterns, missing pagination
- Unbounded loops over user-controlled data
- Memory accumulation, blocking operations in async context
- Inefficient algorithms (O(n^2) when O(n) is possible)
- Missing caching for repeated expensive operations

**Agent #5 — Code Quality and Maintainability:**
- Functions exceeding 50 lines, nesting deeper than 4 levels
- High cyclomatic complexity
- Duplicated logic across files
- Inconsistent patterns, outdated idioms
- Critical TODOs and FIXMEs that indicate unfinished work

### Step 5: Deduplication and Scoring (Haiku Agent)

Launch a Haiku agent to process all results from Step 4:

1. **Deduplicate** — remove issues found by multiple agents (same file + same line range = one issue)
2. **Merge** — combine related issues with the same root cause
3. **Re-score** — adjust confidence based on full context:

| Score | Meaning |
|-------|---------|
| 90-100 | Critical bug or vulnerability. Clear evidence. Must fix. |
| 70-89 | Real issue that will cause problems. Should fix. |
| 50-69 | Code smell or potential issue. Needs human judgment. |
| < 50 | Minor, stylistic, or likely false positive. |

**Discard threshold:**
- Diff mode: discard below 70 (you wrote it, context is fresh)
- Audit mode: discard below 50 (report more broadly, fix conservatively)

### Step 6: Auto-Fix

Apply fixes directly in the code for issues meeting the threshold:
- **Diff mode:** fix issues scoring **>= 70**
- **Audit mode:** fix issues scoring **>= 80**

For each fix:
1. Read the file containing the issue
2. Apply the fix using Edit tool
3. Verify the fix preserves surrounding code and intent

Group fixes by file to minimize edits.

**Never auto-fix:**
- Issues requiring architectural changes
- Ambiguous fixes with multiple valid approaches
- Issues in test files (report only)
- Issues below the mode threshold

### Step 7: Report

Generate the report and display to the user.

**Diff mode:**

```
## Pre-Review Complete

### Issues Found and Fixed: X

1. **file:line** - Description
   - Severity: critical/important/minor | Confidence: XX
   - Category: security/bug/performance/quality/guidelines
   - Fix applied: What was changed

### Manual Review Required: Y
(Issues with confidence >= 70 that could not be auto-fixed: requires architectural change, ambiguous fix, or in test file)

1. **file:line** - Description (confidence: XX)
   - Reason: Why it needs manual review
   - Suggested approach: Description

### Files Modified: Z
- path/to/file1.ts
- path/to/file2.ts

### Recommendations
- Tests to run
- Areas needing human judgment
```

**Audit mode:**

```
## Code Audit Report

### Summary
- Files Audited: X | Issues Found: Y | Fixed: Z | Manual Review: W

### Critical Issues (Fixed)
1. **file:line** - Description
   - Category: security/bug/performance
   - Fix applied: What was changed

### Critical Issues (Manual Review Required)
(Confidence >= 80 but requires architectural change, ambiguous fix, or in test file)
1. **file:line** - Description
   - Reason: Why it was not auto-fixed
   - Recommended: Suggested approach

### Important Issues (Confidence 50-79)
1. **file:line** - Description (confidence: XX)

### Security Summary
- Hardcoded credentials: none found (or: X instances found)
- Injection risks: none found (or: X potential risks)
- XSS vulnerabilities: none found (or: X potential)
- Input validation: adequate (or: X gaps found)

### Files Modified
- path/to/file1.ts

### Recommendations
- Priority items for manual review
- Tests to add
```

### Step 8: Next Steps

Offer the user:
- "Run tests to verify fixes?"
- "Review changes with `git diff`?"
- "Commit the fixes?"
- (Audit mode only) "Audit additional directories?"

## Guidelines

**DO:**
- Fix issues directly in the code, not just report them
- Preserve code intent and match existing patterns
- Group related fixes by file to minimize edits
- Be conservative: when unsure, report instead of fix

**DON'T:**
- Break working code with speculative fixes
- Fix pre-existing issues in diff mode — only fix what changed
- Make style-only changes unless required by project guidelines
- Refactor working code that has no actual bugs
- Audit node_modules, vendor, dist, or generated code

## False Positives to Avoid

- Pre-existing issues not introduced by current changes (diff mode)
- Issues a linter or type checker would catch (assume CI handles these)
- Nitpicks a senior engineer would not flag in a real review
- Intentional patterns that look unusual but are correct
- Code outside the scope of current changes (diff mode)
- General quality opinions not grounded in project guidelines
