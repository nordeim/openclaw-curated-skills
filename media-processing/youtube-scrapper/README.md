# 📺 YouTube Channel Scrapper

[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![Playwright](https://img.shields.io/badge/playwright-v1.40%2B-green.svg)](https://playwright.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful, resilient, and anti-detect YouTube channel metadata scraper. This tool enables automated discovery and deep-scraping of YouTube channels without requiring official API keys or user authentication.

---

## 🚀 Features

- **🔍 Smart Discovery**: Find channels by category and location using advanced Google Search and YouTube discovery techniques.
- **📊 Deep Scraping**: Extract comprehensive metadata, including:
  - Subscriber counts, total views, and video counts.
  - Channel descriptions, joined dates, and verified status.
  - Recent video uploads with thumbnails and metadata.
  - External social links and location info.
- **🛡️ Anti-Detection**: Built-in human-like behavior simulation (random mouse movements, scroll behavior) and custom user-agent rotation to minimize bot detection.
- **🖼️ Media Handling**: Automatic downloading and resizing (JPEG compression) of profile pictures, banners, and video thumbnails.
- **🔄 Robust Orchestration**: State-managed pipeline with auto-resume, failure recovery, and checkpointing for large-scale scraping operations.

---

## 📦 Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/youtube-scrapper.git
   cd youtube-scrapper
   ```

2. **Install dependencies**:
   ```bash
   pip install playwright aiohttp python-dotenv Pillow tqdm
   ```

3. **Setup Playwright**:
   ```bash
   playwright install chromium
   ```

---

## 🛠️ Usage

### 1. Channel Discovery
Find channel handles/URLs based on niche and location. This generates a queue file in `data/queue/`.
```bash
python youtube_channel_discovery.py --categories "tech" --locations "India"
```

### 2. Detailed Scraping
Process a queue file to extract detailed metadata for each channel.
```bash
python youtube_channel_scraper.py --queue data/queue/your_queue_file.json
```

### 3. Full Pipeline (Orchestrator)
Run the entire journey from discovery to completed scrape using a config file.
```bash
python youtube_orchestrator.py --config config/scraper_config.json
```

---

## ⚙️ Configuration

The scraper behavior can be fine-tuned via JSON configuration files in the `config/` directory:

| Setting | Description |
|---------|-------------|
| `max_discovery_retries` | Number of times to retry Google Search results. |
| `max_videos_to_scrape` | Limit for recent video metadata collection per channel. |
| `delay_between_channels` | Random range for sleep time between channel visits. |
| `headless` | Set to `true` for background operation, `false` for visual monitoring. |

---

## 📂 Output Structure

- **`data/output/`**: JSON files for each scraped channel.
- **`thumbnails/`**: Organized folders containing profile pics, banners, and video thumbnails.
- **`data/queue/`**: Checkpoint files for discovery results.
- **`data/progress/`**: Session state files for the orchestrator.




