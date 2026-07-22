"""Reddit connector using PRAW."""

from __future__ import annotations

import os
from datetime import datetime, timezone
from typing import Any, Dict, Iterable

import praw

from .base import BaseConnector
from .utils import since_to_datetime


class RedditConnector(BaseConnector):
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str | None = None,
        *,
        subreddit: str | None = None,
        client: Any | None = None,
    ):
        self.subreddit = subreddit or os.getenv("REDDIT_SUBREDDIT", "all")
        if client is not None:
            self.reddit = client
            return

        client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        if not client_id or not client_secret:
            raise ValueError("Reddit credentials missing")
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent or os.getenv("REDDIT_USER_AGENT", "osint-enricher/0.2"),
        )

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        cutoff = since_to_datetime(since).timestamp()
        for submission in self.reddit.subreddit(self.subreddit).new(limit=100):
            if submission.created_utc < cutoff:
                break
            text = "\n\n".join(part for part in (submission.title, submission.selftext) if part)
            yield {
                "id": str(submission.id),
                "source": "reddit",
                "text": text,
                "timestamp": datetime.fromtimestamp(submission.created_utc, timezone.utc).isoformat(),
                "url": submission.url,
                "subreddit": str(submission.subreddit),
                "score": submission.score,
            }
