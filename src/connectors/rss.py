"""RSS feed connector."""
import feedparser
from typing import Iterable, Dict, Any
from .base import BaseConnector


class RSSConnector(BaseConnector):
    def __init__(self, feed_urls: list[str]):
        self.feed_urls = feed_urls

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        # Stub
        for url in self.feed_urls:
            parsed = feedparser.parse(url)
            for entry in parsed.entries:
                yield {"title": entry.get("title"), "link": entry.get("link"), "summary": entry.get("summary"), "published": entry.get("published")}
