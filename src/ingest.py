import json
import time
import feedparser
import requests
from typing import List, Dict, Any

from config.settings import SEEDS_FILE, HTTP_TIMEOUT, MAX_RETRIES, BACKOFF_FACTOR
from src.utils import get_logger, parse_published_date

logger = get_logger("Ingest")

def fetch_feed_with_retry(url: str) -> str:
    headers = {"User-Agent": "NewsSentimentMonitor/1.0"}
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=headers, timeout=HTTP_TIMEOUT)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            if attempt == MAX_RETRIES:
                raise
            time.sleep(BACKOFF_FACTOR ** attempt)
    return ""

def fetch_all_feeds() -> List[Dict[str, Any]]:
    if not SEEDS_FILE.exists():
        logger.error(f"Seeds file not found at {SEEDS_FILE}")
        return []

    with open(SEEDS_FILE, "r") as f:
        seeds = json.load(f)

    raw_articles = []
    for feed in seeds.get("rss_feeds", []):
        try:
            logger.info(f"Fetching feed: {feed['name']}")
            content = fetch_feed_with_retry(feed["url"])
            parsed = feedparser.parse(content)

            for entry in parsed.entries:
                raw_articles.append({
                    "url": getattr(entry, "link", ""),
                    "title": getattr(entry, "title", "No Title"),
                    "source": feed["name"],
                    "category": feed.get("category", "General"),
                    "summary": getattr(entry, "summary", getattr(entry, "description", "")),
                    "published_at": parse_published_date(getattr(entry, "published", ""))
                })
        except Exception as e:
            logger.error(f"Failed to ingest feed {feed['name']}: {e}")

    return [a for a in raw_articles if a["url"]]
