"""Twitter/X recent-search connector."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable

import tweepy

from .base import BaseConnector
from .utils import since_to_datetime


class TwitterConnector(BaseConnector):
    def __init__(
        self,
        bearer_token: str | None = None,
        *,
        query: str | None = None,
        client: Any | None = None,
    ):
        self.query = query or os.getenv("TWITTER_QUERY", "-is:retweet")
        token = bearer_token or os.getenv("TWITTER_BEARER_TOKEN")
        if client is None and not token:
            raise ValueError("Twitter bearer token not provided")
        self.client = client or tweepy.Client(bearer_token=token, wait_on_rate_limit=True)

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        response = self.client.search_recent_tweets(
            query=self.query,
            start_time=since_to_datetime(since),
            max_results=100,
            tweet_fields=["created_at", "lang", "author_id"],
        )
        for tweet in response.data or []:
            created_at = getattr(tweet, "created_at", None)
            yield {
                "id": str(tweet.id),
                "source": "twitter",
                "text": tweet.text,
                "timestamp": created_at.isoformat() if created_at else None,
                "language": getattr(tweet, "lang", None),
                "author_id": str(tweet.author_id) if getattr(tweet, "author_id", None) else None,
            }
