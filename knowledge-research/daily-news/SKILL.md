---
name: daily-news
version: 1.0.1
description: Fetch top news from Baidu, Google, and other sources daily.
metadata:
  openclaw:
    requires:
      bins: ["python"]
      env: ["PYTHONIOENCODING=utf-8"]
    command-dispatch: tool
    command-tool: exec
    command-arg-mode: raw
---

# Daily News Skill

Fetch the daily top news headlines from multiple sources (Baidu Hot Search, Google Trends).

## Version History

### v1.0.1 (2026-02-22)
- **Security Fix**: Updated `requests>=2.32.0` to resolve PYSEC-2018-28 (SSL certificate bypass vulnerability)
- Added explicit SSL verification (`verify=True`) in all HTTP requests
- Improved error handling and type hints
- Pinned all dependencies to secure versions

### v1.0.0
- Initial release

## Instructions

To get the daily news summary:

```bash
python "{baseDir}/daily_news.py"
```

The script outputs news in Chinese format with current Beijing time.

## Setup

Install required packages:

```bash
pip install -r "{baseDir}/requirements.txt"
```

## Security

This skill uses:
- **requests>=2.32.0** - Secure HTTP client with SSL verification
- **Explicit SSL verification** - All requests enforce certificate validation
- **Timeout protection** - 10 second timeout prevents hanging

## Sources

1. **Baidu Hot Search** - Top trending topics from China
2. **Google Trends** - Daily search trends (US)

## Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| requests | >=2.32.0 | HTTP client |
| beautifulsoup4 | >=4.12.0 | HTML parsing |
| feedparser | >=6.0.0 | RSS parsing |
