"""RSS and Atom feed connector."""

from __future__ import annotations

import calendar
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import feedparser

from .base import BaseConnector
from .utils import since_to_datetime


class RSSConnector(BaseConnector):
    def __init__(self, feed_urls: list[str]):
        if not feed_urls:
            raise ValueError("At least one RSS feed URL is required")
        self.feed_urls = feed_urls

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        cutoff = since_to_datetime(since)
        for url in self.feed_urls:
            parsed = feedparser.parse(url)
            if getattr(parsed, "bozo", False) and not parsed.entries:
                raise ValueError(f"Could not parse RSS feed: {url}")
            for entry in parsed.entries:
                published_struct = entry.get("published_parsed") or entry.get("updated_parsed")
                published = None
                if published_struct:
                    published = datetime.fromtimestamp(
                        calendar.timegm(published_struct), timezone.utc
                    )
                    if published < cutoff:
                        continue
                yield {
                    "id": entry.get("id") or entry.get("link"),
                    "source": "rss",
                    "source_url": url,
                    "text": entry.get("summary") or entry.get("title") or "",
                    "title": entry.get("title"),
                    "url": entry.get("link"),
                    "timestamp": published.isoformat() if published else None,
                }
