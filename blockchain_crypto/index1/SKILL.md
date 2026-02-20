---
name: index1
description: AI-native project knowledge base. BM25 + vector hybrid search via MCP Server.
version: 2.0.1
license: Apache-2.0
author: gladego
tags: [mcp, knowledge-base, semantic-search, bm25, rag, code-search]
---

# index1

AI-native project knowledge base with BM25 + vector hybrid search. Provides 5 MCP tools for intelligent code/doc search.

## What it does

- **Hybrid search**: BM25 full-text + vector semantic search with RRF fusion
- **Structure-aware chunking**: Markdown, Python, Rust, JavaScript, plain text
- **MCP Server**: 5 tools (`docs_search`, `docs_get`, `docs_status`, `docs_reindex`, `docs_config`)
- **CJK optimized**: Chinese/Japanese/Korean query detection with dynamic weight tuning
- **Graceful degradation**: Works without Ollama (BM25-only mode)

## Install

```bash
# Recommended
pipx install index1

# Or via pip
pip install index1

# Or via npm (auto-installs Python package)
npx index1@latest
```

Verify:

```bash
index1 --version
index1 doctor        # Check environment
```

## Setup MCP

Create `.mcp.json` in your project root:

```json
{
  "mcpServers": {
    "index1": {
      "type": "stdio",
      "command": "index1",
      "args": ["serve"]
    }
  }
}
```

> If `index1` is not in PATH, use the full path from `which index1`.

## Add Search Rules

Add to your project's `.claude/CLAUDE.md`:

```markdown
## Search Strategy

This project has index1 MCP Server configured (docs_search + 4 other tools). When searching code:

1. Known identifiers (function/class/file names) -> Grep/Glob directly (4ms)
2. Exploratory questions ("how does XX work") -> docs_search first, then Grep for details
3. CJK query for English code -> must use docs_search (Grep can't cross languages)
4. High-frequency keywords (50+ expected matches) -> prefer docs_search (saves 90%+ context)
```

**Impact**:

```
Without rules: Grep "search" -> 881 lines -> 35,895 tokens
With rules:    docs_search  -> 5 summaries -> 460 tokens (97% savings)
```

## Index Your Project

```bash
index1 index ./src ./docs    # Index source and docs
index1 status                # Check index stats
index1 search "your query"   # Test search
```

## Optional: Vector Search

For semantic/cross-language search, install Ollama:

```bash
curl -fsSL https://ollama.com/install.sh | sh
ollama pull nomic-embed-text           # Standard, 270MB
# or
ollama pull bge-m3                     # Best for CJK, 1.2GB

index1 doctor                          # Verify setup
```

Without Ollama, BM25 full-text search works perfectly (~60-80ms latency).

## Optional: Chinese Support

```bash
pip install index1[chinese]
index1 doctor    # Check 6 shows CJK status
```

## Web UI

```bash
index1 web                   # Start Web UI on port 6888
index1 web --port 8080       # Custom port
```

## MCP Tools Reference

| Tool | Description |
|------|-------------|
| `docs_search` | Hybrid BM25 + vector search, returns ranked results |
| `docs_get` | Get full content of a chunk by ID |
| `docs_status` | Index statistics (doc count, chunk count, collections) |
| `docs_reindex` | Rebuild index for a path or collection |
| `docs_config` | View or modify configuration |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tools not showing | Check `.mcp.json` format and `index1` path |
| AI doesn't use docs_search | Add search rules to CLAUDE.md (step 2) |
| `command not found` | Use full path from `which index1` |
| Chinese search returns 0 | `pip install index1[chinese]` |
| No vector search | Install Ollama + pull model |
