#!/usr/bin/env python3
"""
Daily News Skill - Fetch top news from Baidu, Google Trends, and other sources.

Security: Uses requests>=2.32.0 with explicit SSL verification.
Version: 1.0.1
"""

import sys
import requests
from bs4 import BeautifulSoup
import feedparser
import datetime
import logging
from typing import List, Optional

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

sys.stdout.reconfigure(encoding="utf-8")

DEFAULT_TIMEOUT = 10
MAX_RETRIES = 2
MAX_ITEMS_PER_SOURCE = 5
MAX_TOTAL_ITEMS = 10


def fetch_url(
    url: str, headers: Optional[dict] = None, timeout: int = DEFAULT_TIMEOUT
) -> Optional[requests.Response]:
    """
    Fetch URL with explicit SSL verification and timeout.

    Security: verify=True ensures SSL certificate validation.
    """
    default_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    headers = headers or default_headers

    try:
        response = requests.get(url, headers=headers, timeout=timeout, verify=True)
        response.raise_for_status()
        return response
    except requests.exceptions.SSLError as e:
        logging.error(f"SSL verification failed for {url}: {e}")
        return None
    except requests.exceptions.RequestException as e:
        logging.error(f"Request failed for {url}: {e}")
        return None


def get_baidu_hot() -> List[str]:
    """Fetch top trending topics from Baidu Hot Search."""
    url = "https://top.baidu.com/board?tab=realtime"

    response = fetch_url(url)
    if not response:
        return []

    try:
        soup = BeautifulSoup(response.text, "html.parser")
        hot_items = []

        titles = soup.find_all(class_="c-single-text-ellipsis")
        for title in titles:
            text = title.get_text().strip()
            if text and text not in hot_items:
                hot_items.append(text)
                if len(hot_items) >= MAX_ITEMS_PER_SOURCE:
                    break

        return hot_items
    except Exception as e:
        logging.error(f"Error parsing Baidu response: {e}")
        return []


def get_google_trends() -> List[str]:
    """Fetch top trending topics from Google Trends RSS."""
    url = "https://trends.google.com/trends/trendingsearches/daily/rss?geo=US"

    try:
        feed = feedparser.parse(url)
        hot_items = []
        for entry in feed.entries:
            hot_items.append(entry.title)
            if len(hot_items) >= MAX_ITEMS_PER_SOURCE:
                break
        return hot_items
    except Exception as e:
        logging.error(f"Error fetching Google Trends: {e}")
        return []


def get_daily_news() -> str:
    """
    Aggregate trending news from multiple sources.

    Returns formatted string with current time and top 10 unique keywords.
    """
    now = datetime.datetime.now()
    current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")

    baidu_hot = get_baidu_hot()
    google_hot = get_google_trends()

    all_hot = []
    if baidu_hot:
        all_hot.extend(baidu_hot)
    if google_hot:
        all_hot.extend(google_hot)

    final_hot = []
    seen = set()
    for item in all_hot:
        if item not in seen:
            final_hot.append(item)
            seen.add(item)
            if len(final_hot) >= MAX_TOTAL_ITEMS:
                break

    greeting = f"现在是北京时间 {current_time_str}，今日热搜榜单如下："
    news_list = "\n".join(f"{i}. {item}" for i, item in enumerate(final_hot, 1))

    return f"{greeting}\n{news_list}"


if __name__ == "__main__":
    print(get_daily_news())
