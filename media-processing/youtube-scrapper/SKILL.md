---
name: youtube-scrapper
description: A skill for discovering and scraping YouTube channels based on categories and locations without requiring API keys or login.
---

# YouTube Scrapper Skill

This skill provides a resilient pipeline for discovering YouTube channels via Google Search and scraping detailed channel metadata (subscribers, views, description, recent videos) using Playwright.

## Capabilities

- **Channel Discovery**: Finds YouTube channels by searching for specific categories and locations (e.g., "India tech influencer").
- **Detailed Scraping**: Extracts channel info including subscriber count, view count, video count, joined date, country, and recent video metadata.
- **Anti-Detection**: Built-in mechanisms to mimic human behavior and bypass basic bot detection.
- **Orchestration**: Seamlessly transitions from discovery to scraping with progress tracking and failure recovery.

## Prerequisites

- **Python 3.8+**
- **Playwright**: Required for browser automation.
- **Dependencies**: `pip install playwright aiohttp python-dotenv Pillow tqdm`
- **Playwright Browsers**: `playwright install chromium`

## Usage

### 1. Simple Discovery
Run the discovery script to find channels and create a queue file:
```bash
python scripts/youtube_channel_discovery.py --categories tech --locations India
```

### 2. Scraping a Queue
Once a queue file is created (in `data/queue/`), run the scraper:
```bash
python scripts/youtube_channel_scraper.py --queue data/queue/your_queue_file.json
```

### 3. Full Orchestration
Run both discovery and scraping in one go:
```bash
python scripts/youtube_orchestrator.py --config resources/scraper_config_ind.json
```

## Configuration

The skill uses JSON configuration files in the `config/` directory to manage regional searches and delays.

## Output

- **Data**: Scraped channel data is saved in `data/output/` as JSON files.
- **Thumbnails**: Downloaded profile pictures, banners, and video thumbnails are saved in `thumbnails/`.
- **Progress**: Orchestration and discovery progress are tracked in `data/progress/`.
